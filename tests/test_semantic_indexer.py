"""Unit tests for semantic codebase indexer and BM25 search."""
import pytest
from src.context.semantic_indexer import SemanticIndexer, SemanticSearchTool


def test_semantic_indexer_and_search(tmp_path):
    # Criar arquivos de código de teste
    calc_file = tmp_path / "calc.py"
    calc_file.write_text(
        "class Calculator:\n    def somar_numeros(self, a, b):\n        return a + b\n\n    def subtrair_numeros(self, a, b):\n        return a - b\n",
        encoding="utf-8"
    )

    auth_file = tmp_path / "auth.py"
    auth_file.write_text(
        "def authenticate_user(username, password):\n    # Verifica credenciais\n    return username == 'admin'\n",
        encoding="utf-8"
    )

    indexer = SemanticIndexer(project_root=tmp_path)
    count = indexer.index_codebase()
    assert count >= 3

    # Busca por 'somar'
    results_calc = indexer.search("somar numeros", top_k=2)
    assert len(results_calc) > 0
    assert "somar" in results_calc[0].chunk.content or "Calculator" in results_calc[0].chunk.content

    # Busca por 'authenticate'
    results_auth = indexer.search("authenticate user admin", top_k=1)
    assert len(results_auth) > 0
    assert "authenticate_user" in results_auth[0].chunk.content


@pytest.mark.asyncio
async def test_semantic_search_tool(tmp_path):
    calc_file = tmp_path / "utils.py"
    calc_file.write_text("def format_currency_brl(value):\n    return f'R$ {value:.2f}'\n", encoding="utf-8")

    indexer = SemanticIndexer(project_root=tmp_path)
    indexer.index_codebase()

    tool = SemanticSearchTool(indexer=indexer)
    res = await tool.execute(query="format currency brl")
    assert res.success is True
    assert "format_currency_brl" in res.output
