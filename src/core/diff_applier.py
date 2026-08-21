"""Search & Replace block parser and diff applier (Aider-style & AST-safe)."""
from __future__ import annotations

import difflib
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple
from src.config import get_config


@dataclass
class SearchReplaceBlock:
    file_path: str
    search_content: str
    replace_content: str


SEARCH_REPLACE_PATTERN = re.compile(
    r"(?:(?:\*{3}|```+)(?:[a-zA-Z0-9_\-\.]+)?\s*)?"
    r"(?:(?:File|Arquivo):\s*`?([^\n`\r]+)`?\n)?"
    r"<<<<<<<\s*SEARCH\n"
    r"(.*?)"
    r"=======\n"
    r"(.*?)"
    r">>>>>>>\s*(?:REPLACE)?",
    re.DOTALL
)


def extract_search_replace_blocks(text: str, default_filepath: Optional[str] = None) -> List[SearchReplaceBlock]:
    """Extrai blocos SEARCH/REPLACE do texto da resposta da LLM."""
    blocks: List[SearchReplaceBlock] = []

    # Procurar primeiro cabeçalhos explícitos de arquivo antes dos blocos
    file_header_pattern = re.compile(r"^(?:(?:[#*`\s]*)(?:File|Arquivo|Path):\s*`?([^\n`\r]+)`?|([a-zA-Z0-9_\-/\\]+\.[a-zA-Z0-9]+))\s*$", re.MULTILINE)

    for match in SEARCH_REPLACE_PATTERN.finditer(text):
        header_path = match.group(1)
        search_block = match.group(2)
        replace_block = match.group(3)

        target_file = header_path or default_filepath
        if not target_file:
            # Tentar encontrar menção de arquivo logo antes do bloco
            start_pos = match.start()
            preceding_text = text[max(0, start_pos - 200):start_pos]
            headers = list(file_header_pattern.finditer(preceding_text))
            if headers:
                target_file = headers[-1].group(1) or headers[-1].group(2)

        if target_file:
            blocks.append(
                SearchReplaceBlock(
                    file_path=target_file.strip(),
                    search_content=search_block,
                    replace_content=replace_block
                )
            )

    return blocks


def fuzzy_find_and_replace(original_text: str, search: str, replace: str) -> Tuple[bool, str]:
    """Tenta substituir o trecho exato ou com correspondência tolerante a espaços/quebras de linha."""
    # 1. Correspondência exata
    if search in original_text:
        return True, original_text.replace(search, replace, 1)

    # 2. Correspondência sem espaços no fim das linhas
    def strip_trailing_lines(t: str) -> str:
        return "\n".join(l.rstrip() for l in t.splitlines())

    stripped_orig = strip_trailing_lines(original_text)
    stripped_search = strip_trailing_lines(search)

    if stripped_search in stripped_orig:
        # Reconstruir linhas
        orig_lines = original_text.splitlines(keepends=True)
        search_lines = [l.rstrip() for l in search.splitlines()]
        search_len = len(search_lines)

        for i in range(len(orig_lines) - search_len + 1):
            chunk = [l.rstrip() for l in orig_lines[i:i + search_len]]
            if chunk == search_lines:
                before = "".join(orig_lines[:i])
                after = "".join(orig_lines[i + search_len:])
                return True, before + replace + after

    # 3. Correspondência de similaridade difflib se o bloco for único
    orig_lines = original_text.splitlines()
    search_lines = search.splitlines()
    if not search_lines or len(orig_lines) < len(search_lines):
        return False, original_text

    search_len = len(search_lines)
    best_ratio = 0.0
    best_idx = -1

    for i in range(len(orig_lines) - search_len + 1):
        window = orig_lines[i:i + search_len]
        ratio = difflib.SequenceMatcher(None, [l.strip() for l in window], [l.strip() for l in search_lines]).ratio()
        if ratio > best_ratio and ratio > 0.85:
            best_ratio = ratio
            best_idx = i

    if best_idx != -1:
        before_lines = orig_lines[:best_idx]
        after_lines = orig_lines[best_idx + search_len:]
        new_content = "\n".join(before_lines + [replace] + after_lines)
        if original_text.endswith("\n") and not new_content.endswith("\n"):
            new_content += "\n"
        return True, new_content

    return False, original_text


def apply_search_replace_block(block: SearchReplaceBlock) -> Tuple[bool, str, str]:
    """Aplica o bloco de modificação ao arquivo alvo. Retorna (sucesso, mensagem, unified_diff)."""
    config = get_config()
    target_path = (config.project_root / block.file_path).resolve()

    if not config.is_path_safe(target_path):
        return False, f"Caminho inseguro fora do workspace: {block.file_path}", ""

    if not target_path.exists():
        # Se for um arquivo novo e o SEARCH estiver vazio, cria o arquivo
        if not block.search_content.strip():
            target_path.parent.mkdir(parents=True, exist_ok=True)
            with open(target_path, "w", encoding="utf-8") as f:
                f.write(block.replace_content)
            diff = f"+ {block.replace_content}"
            return True, f"Arquivo criado: {block.file_path}", diff
        return False, f"Arquivo não encontrado para modificação: {block.file_path}", ""

    with open(target_path, "r", encoding="utf-8", errors="replace") as f:
        original_content = f.read()

    success, updated_content = fuzzy_find_and_replace(original_content, block.search_content, block.replace_content)
    if not success:
        return False, f"Não foi possível localizar o trecho SEARCH no arquivo '{block.file_path}'.", ""

    # Gerar diff unificado para exibição limpa
    diff_lines = list(difflib.unified_diff(
        original_content.splitlines(keepends=True),
        updated_content.splitlines(keepends=True),
        fromfile=f"a/{block.file_path}",
        tofile=f"b/{block.file_path}"
    ))
    diff_str = "".join(diff_lines)

    # Gravar arquivo atualizado
    with open(target_path, "w", encoding="utf-8") as f:
        f.write(updated_content)

    return True, f"Modificação aplicada com sucesso em '{block.file_path}'.", diff_str
