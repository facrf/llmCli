"""Manages active files loaded into the LLM context."""
from __future__ import annotations

import fnmatch
from pathlib import Path
from typing import List, Set, Tuple

from src.config import get_config


class FileTracker:
    MAX_FILES = 100
    MAX_FILE_BYTES = 256 * 1024
    MAX_CONTEXT_CHARS = 200_000
    PROTECTED_NAMES = {".env", "credentials.json", "token.json"}
    PROTECTED_SUFFIXES = (".env", ".pem", ".key", ".cert", ".pfx")

    def __init__(self) -> None:
        self.tracked_files: Set[str] = set()

    def _is_excluded(self, path: Path, config_root: Path) -> bool:
        relative = path.relative_to(config_root)
        ignored_parts = {
            ".git", "__pycache__", "node_modules", ".venv", "env", ".cache", "secrets"
        }
        if any(part in ignored_parts for part in relative.parts):
            return True
        name = path.name.lower()
        if name in self.PROTECTED_NAMES or name.endswith(self.PROTECTED_SUFFIXES):
            return True
        ignore_file = config_root / ".gitignore"
        if ignore_file.exists():
            lines = ignore_file.read_text(encoding="utf-8", errors="ignore").splitlines()
            patterns = [
                line.strip().rstrip("/")
                for line in lines
                if line.strip() and not line.lstrip().startswith("#") and not line.startswith("!")
            ]
            rel_text = relative.as_posix()
            if any(
                fnmatch.fnmatch(rel_text, pattern) or fnmatch.fnmatch(name, pattern)
                for pattern in patterns
            ):
                return True
        return False

    def _can_track(self, path: Path, config_root: Path) -> bool:
        return (
            not self._is_excluded(path, config_root)
            and path.stat().st_size <= self.MAX_FILE_BYTES
        )

    def add_file(self, file_path: str | Path) -> Tuple[bool, str]:
        config = get_config()
        p = Path(file_path)
        if not p.is_absolute():
            resolved = (config.project_root / p).resolve()
        else:
            resolved = p.resolve()

        if not config.is_path_safe(resolved):
            return False, f"Caminho fora do workspace permitido: {file_path}"

        if not resolved.exists():
            return False, f"Arquivo não encontrado: {file_path}"

        if resolved.is_dir():
            # Adicionar todos os arquivos do diretório (não ignorados)
            added_count = 0
            for child in resolved.rglob("*"):
                if len(self.tracked_files) >= self.MAX_FILES:
                    break
                if child.is_file() and self._can_track(child, config.project_root):
                    rel = str(child.relative_to(config.project_root))
                    self.tracked_files.add(rel)
                    added_count += 1
            return True, (
                f"{added_count} arquivos do diretório '{file_path}' adicionados ao contexto."
            )

        if not self._can_track(resolved, config.project_root):
            return False, "Arquivo protegido, ignorado pelo Git ou maior que o limite de contexto."
        if len(self.tracked_files) >= self.MAX_FILES:
            return False, f"Limite de {self.MAX_FILES} arquivos no contexto atingido."
        rel_path = str(resolved.relative_to(config.project_root))
        self.tracked_files.add(rel_path)
        return True, f"Arquivo '{rel_path}' adicionado ao contexto."

    def remove_file(self, file_path: str) -> bool:
        if file_path in self.tracked_files:
            self.tracked_files.remove(file_path)
            return True
        return False

    def clear(self) -> None:
        self.tracked_files.clear()

    def list_files(self) -> List[str]:
        return sorted(list(self.tracked_files))

    def get_context_text(self) -> str:
        """Gera o bloco formatado com os arquivos rastreados para inclusão no prompt."""
        if not self.tracked_files:
            return ""

        config = get_config()
        blocks: List[str] = ["=== ARQUIVOS ATIVOS NO CONTEXTO ==="]

        context_chars = 0
        for rel_path in sorted(self.tracked_files):
            full_path = config.project_root / rel_path
            if not full_path.exists() or not full_path.is_file():
                continue

            try:
                with open(full_path, "r", encoding="utf-8", errors="replace") as f:
                    lines = f.readlines()
                numbered = [f"{i + 1:4d} | {line}" for i, line in enumerate(lines)]
                content = "".join(numbered)
                if context_chars + len(content) > self.MAX_CONTEXT_CHARS:
                    blocks.append("\n--- Contexto truncado por limite de tamanho ---")
                    break
                blocks.append(
                    f"\n--- Início de '{rel_path}' ---\n{content}\n--- Fim de '{rel_path}' ---"
                )
                context_chars += len(content)
            except Exception as e:
                blocks.append(f"\n--- Erro ao ler '{rel_path}': {e} ---")

        blocks.append("===================================")
        return "\n".join(blocks)
