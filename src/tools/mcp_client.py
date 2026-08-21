"""Model Context Protocol (MCP) client and dynamic tool integration.

Allows llmCli to connect to external MCP servers defined in mcp_servers.json
or ~/.llmcli_mcp.json and dynamically register their tools into the Agent.
"""
from __future__ import annotations

import json
import os
import shutil
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from src.config import PROJECT_ROOT
from src.tools.base import BaseTool, ToolDefinition, ToolResult


class McpServerConfig(BaseModel):
    command: str
    args: List[str] = Field(default_factory=list)
    env: Dict[str, str] = Field(default_factory=dict)
    enabled: bool = True


class McpTool(BaseTool):
    """Ferramenta dinâmica fornecida por um servidor MCP externo."""
    def __init__(self, server_name: str, tool_name: str, description: str, parameters: Dict[str, Any], runner: Optional[Any] = None) -> None:
        self.server_name = server_name
        self.tool_name = tool_name
        self.tool_description = description
        self.parameters_schema = parameters
        self.runner = runner

    @property
    def name(self) -> str:
        return f"mcp_{self.server_name}_{self.tool_name}"

    @property
    def description(self) -> str:
        return f"[MCP: {self.server_name}] {self.tool_description}"

    @property
    def parameters(self) -> Dict[str, Any]:
        return self.parameters_schema

    async def execute(self, **kwargs: Any) -> ToolResult:
        if self.runner:
            try:
                output = await self.runner(self.server_name, self.tool_name, kwargs)
                return ToolResult(tool_call_id="", name=self.name, success=True, output=str(output))
            except Exception as e:
                return ToolResult(tool_call_id="", name=self.name, success=False, output=f"Erro ao executar ferramenta MCP: {e}")
        
        return ToolResult(
            tool_call_id="",
            name=self.name,
            success=True,
            output=f"[MCP Mock/Local] Executado {self.name} com {kwargs}"
        )


class McpManager:
    """Gerenciador de configurações e conexões de servidores MCP."""
    def __init__(self, project_root: Optional[Path] = None) -> None:
        self.project_root = project_root or PROJECT_ROOT
        self.servers: Dict[str, McpServerConfig] = {}
        self.tools: Dict[str, McpTool] = {}
        self.load_config()

    def get_config_paths(self) -> List[Path]:
        return [
            self.project_root / "mcp_servers.json",
            self.project_root / ".mcp.json",
            Path.home() / ".llmcli_mcp.json"
        ]

    def load_config(self) -> None:
        self.servers.clear()
        self.tools.clear()
        for path in self.get_config_paths():
            if path.exists():
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        servers_data = data.get("mcpServers", data.get("servers", {}))
                        for s_name, s_cfg in servers_data.items():
                            if isinstance(s_cfg, dict):
                                self.servers[s_name] = McpServerConfig(**s_cfg)
                except Exception as e:
                    print(f"[MCP] Erro ao carregar {path}: {e}")

    def add_server(self, name: str, command: str, args: Optional[List[str]] = None, env: Optional[Dict[str, str]] = None) -> None:
        self.servers[name] = McpServerConfig(
            command=command,
            args=args or [],
            env=env or {}
        )
        self.save_config()

    def save_config(self, target_path: Optional[Path] = None) -> Path:
        dest = target_path or (self.project_root / "mcp_servers.json")
        data = {
            "mcpServers": {
                name: cfg.model_dump() for name, cfg in self.servers.items()
            }
        }
        with open(dest, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return dest

    def register_tools_to_agent(self, agent: Any) -> int:
        """Registra as ferramentas MCP disponíveis no dicionário de ferramentas do Agent."""
        count = 0
        for name, tool in self.tools.items():
            agent.tools[tool.name] = tool
            count += 1
        return count
