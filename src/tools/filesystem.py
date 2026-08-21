"""Filesystem tools with workspace security boundaries."""
from __future__ import annotations

import fnmatch
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional
from src.config import get_config
from src.tools.base import BaseTool, ToolResult


def _resolve_safe_path(target_path: str | Path) -> Path:
    config = get_config()
    target = Path(target_path)
    if not target.is_absolute():
        resolved = (config.project_root / target).resolve()
    else:
        resolved = target.resolve()

    if not config.is_path_safe(resolved):
        raise PermissionError(
            f"Acesso negado: O caminho '{target_path}' está fora da raiz permitida do workspace ({config.project_root})."
        )
    return resolved


class ReadFileTool(BaseTool):
    name = "read_file"
    description = "Lê o conteúdo de um arquivo de texto, opcionalmente entre um intervalo de linhas (1-indexed)."
    parameters_schema = {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Caminho relativo ou absoluto do arquivo no workspace."},
            "start_line": {"type": "integer", "description": "Linha inicial para leitura (1-indexed, opcional)."},
            "end_line": {"type": "integer", "description": "Linha final para leitura (inclusive, opcional)."}
        },
        "required": ["path"]
    }

    async def execute(self, path: str, start_line: Optional[int] = None, end_line: Optional[int] = None, **kwargs: Any) -> ToolResult:
        try:
            safe_path = _resolve_safe_path(path)
            if not safe_path.exists():
                return ToolResult(tool_call_id="", name=self.name, success=False, output=f"Arquivo não encontrado: {path}")
            if not safe_path.is_file():
                return ToolResult(tool_call_id="", name=self.name, success=False, output=f"O caminho não é um arquivo: {path}")

            with open(safe_path, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()

            total_lines = len(lines)
            s = (start_line or 1) - 1
            e = end_line or total_lines
            s = max(0, min(s, total_lines))
            e = max(s, min(e, total_lines))

            selected = lines[s:e]
            numbered = [f"{s + i + 1:4d} | {line}" for i, line in enumerate(selected)]
            content = "".join(numbered)
            header = f"--- Arquivo: {path} (Linhas {s + 1}-{e} de {total_lines}) ---\n"
            return ToolResult(tool_call_id="", name=self.name, success=True, output=header + content)
        except Exception as err:
            return ToolResult(tool_call_id="", name=self.name, success=False, output=f"Erro ao ler arquivo: {err}")


class WriteFileTool(BaseTool):
    name = "write_file"
    description = "Escreve ou substitui o conteúdo completo de um arquivo dentro do workspace."
    parameters_schema = {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Caminho do arquivo a ser criado ou substituído."},
            "content": {"type": "string", "description": "Conteúdo textual completo do arquivo."}
        },
        "required": ["path", "content"]
    }

    async def execute(self, path: str, content: str, **kwargs: Any) -> ToolResult:
        try:
            safe_path = _resolve_safe_path(path)
            safe_path.parent.mkdir(parents=True, exist_ok=True)
            with open(safe_path, "w", encoding="utf-8") as f:
                f.write(content)
            return ToolResult(tool_call_id="", name=self.name, success=True, output=f"Arquivo gravado com sucesso: {path} ({len(content)} caracteres)")
        except Exception as err:
            return ToolResult(tool_call_id="", name=self.name, success=False, output=f"Erro ao gravar arquivo: {err}")


class ListDirTool(BaseTool):
    name = "list_dir"
    description = "Lista diretórios e arquivos de um caminho do workspace."
    parameters_schema = {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Caminho do diretório (padrão: '.').", "default": "."},
            "max_depth": {"type": "integer", "description": "Profundidade máxima de listagem (padrão: 2).", "default": 2}
        },
        "required": []
    }

    async def execute(self, path: str = ".", max_depth: int = 2, **kwargs: Any) -> ToolResult:
        try:
            safe_path = _resolve_safe_path(path)
            if not safe_path.exists() or not safe_path.is_dir():
                return ToolResult(tool_call_id="", name=self.name, success=False, output=f"Diretório inválido: {path}")

            results: List[str] = []
            root_depth = len(safe_path.parts)

            for root, dirs, files in os.walk(safe_path):
                cur_depth = len(Path(root).parts) - root_depth
                if cur_depth >= max_depth:
                    dirs.clear()
                    continue

                # Filtrar diretórios ignorados comuns
                dirs[:] = [d for d in dirs if d not in (".git", "__pycache__", "node_modules", ".venv", "env", ".cache")]

                rel_root = Path(root).relative_to(safe_path)
                indent = "  " * cur_depth
                if str(rel_root) != ".":
                    results.append(f"{indent}📁 {rel_root.name}/")
                    indent += "  "

                for f in sorted(files):
                    results.append(f"{indent}📄 {f}")

            out = "\n".join(results) or "(diretório vazio)"
            return ToolResult(tool_call_id="", name=self.name, success=True, output=f"Conteúdo de '{path}':\n{out}")
        except Exception as err:
            return ToolResult(tool_call_id="", name=self.name, success=False, output=f"Erro ao listar diretório: {err}")


class GrepSearchTool(BaseTool):
    name = "grep_search"
    description = "Busca ocorrências de texto ou regex dentro dos arquivos do projeto."
    parameters_schema = {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Termo ou padrão regex de busca."},
            "path": {"type": "string", "description": "Diretório ou arquivo alvo (padrão: '.').", "default": "."},
            "case_sensitive": {"type": "boolean", "description": "Se a busca diferencia maiúsculas de minúsculas.", "default": False}
        },
        "required": ["query"]
    }

    async def execute(self, query: str, path: str = ".", case_sensitive: bool = False, **kwargs: Any) -> ToolResult:
        try:
            safe_path = _resolve_safe_path(path)
            flags = 0 if case_sensitive else re.IGNORECASE
            pattern = re.compile(query, flags)

            matches: List[str] = []
            files_to_search: List[Path] = []

            if safe_path.is_file():
                files_to_search.append(safe_path)
            else:
                for root, dirs, files in os.walk(safe_path):
                    dirs[:] = [d for d in dirs if d not in (".git", "__pycache__", "node_modules", ".venv", "env", ".cache")]
                    for f in files:
                        p = Path(root) / f
                        files_to_search.append(p)

            for file_path in files_to_search[:200]:
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        for line_idx, line in enumerate(f, 1):
                            if pattern.search(line):
                                rel = file_path.relative_to(get_config().project_root)
                                matches.append(f"{rel}:{line_idx}: {line.strip()}")
                                if len(matches) >= 50:
                                    break
                except Exception:
                    continue
                if len(matches) >= 50:
                    break

            if not matches:
                return ToolResult(tool_call_id="", name=self.name, success=True, output=f"Nenhuma ocorrência encontrada para '{query}'.")

            summary = "\n".join(matches)
            if len(matches) >= 50:
                summary += "\n... (limite de 50 resultados atingido)"
            return ToolResult(tool_call_id="", name=self.name, success=True, output=summary)
        except Exception as err:
            return ToolResult(tool_call_id="", name=self.name, success=False, output=f"Erro na busca: {err}")


class FindFilesTool(BaseTool):
    name = "find_files"
    description = "Encontra arquivos pelo nome ou padrão glob (ex: '*.py', 'test_*')."
    parameters_schema = {
        "type": "object",
        "properties": {
            "pattern": {"type": "string", "description": "Padrão de busca (ex: '*.ts', '*agent*')."},
            "path": {"type": "string", "description": "Diretório de início (padrão: '.').", "default": "."}
        },
        "required": ["pattern"]
    }

    async def execute(self, pattern: str, path: str = ".", **kwargs: Any) -> ToolResult:
        try:
            safe_path = _resolve_safe_path(path)
            matches: List[str] = []

            for root, dirs, files in os.walk(safe_path):
                dirs[:] = [d for d in dirs if d not in (".git", "__pycache__", "node_modules", ".venv", "env", ".cache")]
                for filename in files:
                    if fnmatch.fnmatch(filename, pattern):
                        full = Path(root) / filename
                        rel = full.relative_to(get_config().project_root)
                        matches.append(str(rel))
                        if len(matches) >= 50:
                            break
                if len(matches) >= 50:
                    break

            if not matches:
                return ToolResult(tool_call_id="", name=self.name, success=True, output=f"Nenhum arquivo encontrado com padrão '{pattern}'.")

            return ToolResult(tool_call_id="", name=self.name, success=True, output="\n".join(matches))
        except Exception as err:
            return ToolResult(tool_call_id="", name=self.name, success=False, output=f"Erro ao buscar arquivos: {err}")
