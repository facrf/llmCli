"""Unit tests for MCP (Model Context Protocol) integration."""
import json
import pytest
from src.tools.mcp_client import McpManager, McpTool, McpServerConfig
from src.core.agent import Agent


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
    tool = McpTool(
        server_name="test_server",
        tool_name="query",
        description="Query database",
        parameters={"type": "object", "properties": {"sql": {"type": "string"}}}
    )
    assert tool.name == "mcp_test_server_query"
    res = await tool.execute(sql="SELECT 1;")
    assert res.success is True
    assert "mcp_test_server_query" in res.output


def test_mcp_register_tools_to_agent(tmp_path):
    mgr = McpManager(project_root=tmp_path)
    tool = McpTool("db", "select", "Select rows", {})
    mgr.tools["mcp_db_select"] = tool

    agent = Agent()
    count = mgr.register_tools_to_agent(agent)
    assert count == 1
    assert "mcp_db_select" in agent.tools
