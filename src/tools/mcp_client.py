"""Stdio Model Context Protocol client and dynamic tool integration."""
from __future__ import annotations

import asyncio
import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from src.config import PROJECT_ROOT
from src.tools.base import BaseTool, ToolResult


class McpServerConfig(BaseModel):
    command: str
    args: List[str] = Field(default_factory=list)
    env: Dict[str, str] = Field(default_factory=dict)
    enabled: bool = True
    timeout_seconds: float = 15.0


class McpConnection:
    """Small sequential JSON-RPC client for an MCP server over stdio."""
    def __init__(self, name: str, config: McpServerConfig, cwd: Path) -> None:
        self.name, self.config, self.cwd = name, config, cwd
        self.process: Optional[asyncio.subprocess.Process] = None
        self._request_id = 0
        self._lock = asyncio.Lock()

    async def start(self) -> None:
        if self.process and self.process.returncode is None:
            return
        self.process = await asyncio.create_subprocess_exec(
            self.config.command, *self.config.args, cwd=str(self.cwd),
            env={**os.environ, **self.config.env}, stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        )
        await self.request("initialize", {
            "protocolVersion": "2024-11-05", "capabilities": {},
            "clientInfo": {"name": "llmCli", "version": "0.1.0"},
        })
        await self.notify("notifications/initialized")

    async def notify(self, method: str) -> None:
        if not self.process or not self.process.stdin:
            raise RuntimeError("Servidor MCP não está em execução")
        self.process.stdin.write((json.dumps({"jsonrpc": "2.0", "method": method}) + "\n").encode())
        await self.process.stdin.drain()

    async def request(self, method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        async with self._lock:
            if not self.process or not self.process.stdin or not self.process.stdout:
                raise RuntimeError("Servidor MCP não está em execução")
            self._request_id += 1
            request_id = self._request_id
            payload: Dict[str, Any] = {"jsonrpc": "2.0", "id": request_id, "method": method}
            if params is not None:
                payload["params"] = params
            self.process.stdin.write((json.dumps(payload) + "\n").encode())
            await self.process.stdin.drain()
            while True:
                raw = await asyncio.wait_for(self.process.stdout.readline(), self.config.timeout_seconds)
                if not raw:
                    raise RuntimeError("Servidor MCP encerrou a conexão")
                response = json.loads(raw.decode("utf-8"))
                if response.get("id") != request_id:
                    continue
                if "error" in response:
                    raise RuntimeError(str(response["error"]))
                return response.get("result", {})

    async def close(self) -> None:
        if self.process and self.process.returncode is None:
            self.process.terminate()
            try:
                await asyncio.wait_for(self.process.wait(), 3)
            except asyncio.TimeoutError:
                self.process.kill()
                await self.process.wait()
        self.process = None


class McpTool(BaseTool):
    def __init__(self, server_name: str, tool_name: str, description: str, parameters: Dict[str, Any], runner: Any) -> None:
        self.server_name, self.tool_name = server_name, tool_name
        self.tool_description, self.parameters_schema, self.runner = description, parameters, runner

    @property
    def name(self) -> str:
        server = re.sub(r"[^a-zA-Z0-9_]", "_", self.server_name)
        tool = re.sub(r"[^a-zA-Z0-9_]", "_", self.tool_name)
        return f"mcp_{server}_{tool}"

    @property
    def description(self) -> str:
        return f"[MCP: {self.server_name}] {self.tool_description}"

    async def execute(self, **kwargs: Any) -> ToolResult:
        try:
            output = await self.runner(self.server_name, self.tool_name, kwargs)
            return ToolResult(tool_call_id="", name=self.name, success=True, output=output)
        except Exception as exc:
            return ToolResult(tool_call_id="", name=self.name, success=False, output=f"Erro MCP: {exc}")


class McpManager:
    def __init__(self, project_root: Optional[Path] = None) -> None:
        self.project_root = project_root or PROJECT_ROOT
        self.servers: Dict[str, McpServerConfig] = {}
        self.tools: Dict[str, McpTool] = {}
        self.connections: Dict[str, McpConnection] = {}
        self.load_config()

    def get_config_paths(self) -> List[Path]:
        return [self.project_root / "mcp_servers.json", self.project_root / ".mcp.json"]

    def load_config(self) -> None:
        self.servers.clear()
        for path in self.get_config_paths():
            if not path.exists():
                continue
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                for name, config in data.get("mcpServers", data.get("servers", {})).items():
                    if isinstance(config, dict):
                        self.servers[name] = McpServerConfig(**config)
            except (OSError, json.JSONDecodeError, ValueError) as exc:
                print(f"[MCP] Erro ao carregar {path}: {exc}")

    def add_server(self, name: str, command: str, args: Optional[List[str]] = None, env: Optional[Dict[str, str]] = None) -> None:
        self.servers[name] = McpServerConfig(command=command, args=args or [], env=env or {})
        self.save_config()

    def save_config(self, target_path: Optional[Path] = None) -> Path:
        target = target_path or self.project_root / "mcp_servers.json"
        target.write_text(json.dumps({"mcpServers": {name: cfg.model_dump() for name, cfg in self.servers.items()}}, indent=2), encoding="utf-8")
        return target

    async def discover_tools(self) -> List[str]:
        errors: List[str] = []
        for name, config in self.servers.items():
            if not config.enabled:
                continue
            try:
                connection = self.connections.get(name)
                if connection is None:
                    connection = McpConnection(name, config, self.project_root)
                    self.connections[name] = connection
                await connection.start()
                response = await connection.request("tools/list")
                for definition in response.get("tools", []):
                    tool_name = definition.get("name")
                    if not isinstance(tool_name, str) or not tool_name:
                        continue
                    tool = McpTool(name, tool_name, str(definition.get("description", "Ferramenta MCP")), definition.get("inputSchema", {"type": "object", "properties": {}}), self.call_tool)
                    self.tools[tool.name] = tool
            except (OSError, RuntimeError, asyncio.TimeoutError, json.JSONDecodeError) as exc:
                errors.append(f"{name}: {exc}")
        return errors

    async def call_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any]) -> str:
        connection = self.connections.get(server_name)
        if connection is None:
            raise RuntimeError(f"Servidor MCP indisponível: {server_name}")
        response = await connection.request("tools/call", {"name": tool_name, "arguments": arguments})
        content = response.get("content", response)
        return content if isinstance(content, str) else json.dumps(content, ensure_ascii=False)

    def register_tools_to_agent(self, agent: Any) -> int:
        for tool in self.tools.values():
            agent.tools[tool.name] = tool
        return len(self.tools)

    async def close(self) -> None:
        await asyncio.gather(*(connection.close() for connection in self.connections.values()))
        self.connections.clear()
