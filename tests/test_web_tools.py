"""Unit tests for web search and URL reader tools."""
import pytest

from src.tools.web_tools import ReadUrlTool, WebSearchTool


@pytest.mark.asyncio
async def test_read_url_tool_invalid():
    tool = ReadUrlTool()
    # URL inválida/inexistente deve tratar o erro graciosamente
    res = await tool.execute(url="http://invalid-non-existent-domain-12345.local")
    assert res.success is False
    assert "Falha" in res.output or "Erro" in res.output or "bloqueado" in res.output


@pytest.mark.asyncio
async def test_read_url_tool_blocks_private_destinations():
    tool = ReadUrlTool()
    res = await tool.execute(url="http://127.0.0.1:8080/private")
    assert res.success is False
    assert "bloqueado" in res.output


@pytest.mark.asyncio
async def test_web_search_tool_structure():
    tool = WebSearchTool()
    assert tool.name == "web_search"
    assert "query" in tool.parameters["properties"]
    definition = tool.get_definition()
    assert definition.name == "web_search"
    assert "query" in definition.parameters["properties"]


@pytest.mark.asyncio
async def test_read_url_tool_structure():
    tool = ReadUrlTool()
    assert tool.name == "read_url"
    assert "url" in tool.parameters["properties"]
    definition = tool.get_definition()
    assert definition.name == "read_url"
    assert "url" in definition.parameters["properties"]
