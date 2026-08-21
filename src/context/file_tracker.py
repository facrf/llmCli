"""Manages active files loaded into the LLM context."""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from src.config import get_config


class FileTracker:
    def __init__(self) -> None:
        self.tracked_files: Set[str] = set()

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
                if child.is_file() and not any(part in child.parts for part in (".git", "__pycache__", "node_modules", ".venv")):
                    rel = str(child.relative_to(config.project_root))
                    self.tracked_files.add(rel)
                    added_count += 1
            return True, f"{added_count} arquivos do diretório '{file_path}' adicionados ao contexto."

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

        for rel_path in sorted(self.tracked_files):
            full_path = config.project_root / rel_path
            if not full_path.exists() or not full_path.is_file():
                continue

            try:
                with open(full_path, "r", encoding="utf-8", errors="replace") as f:
                    lines = f.readlines()
                numbered = [f"{i + 1:4d} | {line}" for i, line in enumerate(lines)]
                content = "".join(numbered)
                blocks.append(f"\n--- Início de '{rel_path}' ---\n{content}\n--- Fim de '{rel_path}' ---")
            except Exception as e:
                blocks.append(f"\n--- Erro ao ler '{rel_path}': {e} ---")

        blocks.append("===================================")
        return "\n".join(blocks)
