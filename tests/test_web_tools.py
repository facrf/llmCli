"""Unit tests for web search and URL reader tools."""
import pytest
from src.tools.web_tools import WebSearchTool, ReadUrlTool


@pytest.mark.asyncio
async def test_read_url_tool_invalid():
    tool = ReadUrlTool()
    # URL inválida/inexistente deve tratar o erro graciosamente
    res = await tool.execute(url="http://invalid-non-existent-domain-12345.local")
    assert res.success is False
    assert "Falha" in res.output or "Erro" in res.output


@pytest.mark.asyncio
async def test_web_search_tool_structure():
    tool = WebSearchTool()
    assert tool.name == "web_search"
    assert "query" in tool.parameters["properties"]
