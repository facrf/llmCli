"""Automated unit test generator module for llmCli."""
from __future__ import annotations

from pathlib import Path
from typing import Optional, Any
from src.config import PROJECT_ROOT, get_config


def get_test_prompt_for_file(target_file: Path, project_root: Optional[Path] = None) -> str:
    """Gera um prompt especializado para a IA escrever testes unitários completos com pytest."""
    root = project_root or PROJECT_ROOT
    try:
        content = target_file.read_text(encoding="utf-8")
    except Exception as e:
        content = f"# Erro ao ler arquivo: {e}"

    rel_path = str(target_file.relative_to(root)) if target_file.is_relative_to(root) else str(target_file)
    test_file_name = f"tests/test_{target_file.stem}.py"

    return f"""Escreva uma suíte completa de testes unitários com pytest para o arquivo `{rel_path}`.

Requisitos:
1. Crie ou atualize o arquivo `{test_file_name}` usando a ferramenta `write_file` ou blocos SEARCH/REPLACE.
2. Cubra todos os caminhos principais (happy path), casos limites (edge cases) e tratamento de erros/exceções.
3. Utilize fixtures de teste do pytest, mocks (unittest.mock) e `@pytest.mark.asyncio` onde aplicável.
4. Mantenha o código limpo, modular e de execução rápida.

Código do arquivo `{rel_path}`:
```python
{content}
```
"""
