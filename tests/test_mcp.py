"""Unit tests for MCP (Model Context Protocol) integration."""
import sys
from pathlib import Path

import pytest

from src.core.agent import Agent
from src.tools.mcp_client import McpManager, McpServerConfig, McpTool


def test_mcp_config_save_and_load(tmp_path):
    mgr = McpManager(project_root=tmp_path)
    assert len(mgr.servers) == 0

    mgr.add_server("sqlite", command="uvx", args=["mcp-server-sqlite", "db.sqlite"])
    assert "sqlite" in mgr.servers
    assert mgr.servers["sqlite"].command == "uvx"

    # Recarregar
    mgr2 = McpManager(project_root=tmp_path)
    assert "sqlite" in mgr2.servers
    assert mgr2.servers["sqlite"].args == ["mcp-server-sqlite", "db.sqlite"]


@pytest.mark.asyncio
async def test_mcp_tool_execution():
    async def runner(server_name, tool_name, arguments):
        return f"{server_name}:{tool_name}:{arguments['sql']}"

    tool = McpTool(
        server_name="test_server",
        tool_name="query",
        description="Query database",
        parameters={"type": "object", "properties": {"sql": {"type": "string"}}},
        runner=runner,
    )
    assert tool.name == "mcp_test_server_query"
    res = await tool.execute(sql="SELECT 1;")
    assert res.success is True
    assert "SELECT 1" in res.output


def test_mcp_register_tools_to_agent(tmp_path):
    mgr = McpManager(project_root=tmp_path)
    async def runner(*args):
        return "ok"

    tool = McpTool("db", "select", "Select rows", {}, runner)
    mgr.tools["mcp_db_select"] = tool

    agent = Agent()
    count = mgr.register_tools_to_agent(agent)
    assert count == 1
    assert "mcp_db_select" in agent.tools


@pytest.mark.asyncio
async def test_mcp_stdio_discovery_and_tool_call():
    project_root = Path(__file__).resolve().parents[1]
    fixture = project_root / "tests" / "fixtures" / "mcp_stdio_server.py"
    manager = McpManager(project_root=project_root)
    manager.servers = {
        "fixture": McpServerConfig(command=sys.executable, args=[str(fixture)], timeout_seconds=3)
    }
    try:
        errors = await manager.discover_tools()
        assert errors == []
        result = await manager.tools["mcp_fixture_echo"].execute(value="hello MCP")
        assert result.success is True
        assert "hello MCP" in result.output
    finally:
        await manager.close()
