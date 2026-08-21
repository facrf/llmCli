"""Lightweight repository mapper and directory tree generator."""
from __future__ import annotations

import os
from pathlib import Path
from typing import List
from src.config import get_config


def build_repo_map(max_files: int = 100) -> str:
    """Gera um mapa conciso da árvore do projeto para guiar a LLM."""
    config = get_config()
    root = config.project_root
    lines: List[str] = [f"Estrutura do Projeto ({root.name}):"]

    ignored_dirs = {".git", "__pycache__", "node_modules", ".venv", "env", ".cache", "dist", "build"}
    count = 0

    for current_dir, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in ignored_dirs and not d.startswith(".")]
        rel_dir = Path(current_dir).relative_to(root)
        depth = len(rel_dir.parts)

        if depth > 4:
            dirs.clear()
            continue

        indent = "  " * depth
        if str(rel_dir) != ".":
            lines.append(f"{indent}📁 {rel_dir.name}/")
            indent += "  "

        for f in sorted(files):
            if f.startswith(".") and f not in (".env.example", ".gitignore"):
                continue
            lines.append(f"{indent}📄 {f}")
            count += 1
            if count >= max_files:
                lines.append(f"{indent}... (árvore truncada para brevidade)")
                return "\n".join(lines)

    return "\n".join(lines)
