"""Base classes and schemas for agent tools."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional
from pydantic import BaseModel


class ToolParam(BaseModel):
    name: str
    type: str
    description: str
    required: bool = True
    enum: Optional[List[str]] = None


class ToolDefinition(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any]


@dataclass
class ToolCall:
    id: str
    name: str
    arguments: Dict[str, Any]


@dataclass
class ToolResult:
    tool_call_id: str
    name: str
    success: bool
    output: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_message_text(self) -> str:
        status = "SUCESSO" if self.success else "ERRO"
        return f"[{status}] Ferramenta '{self.name}':\n{self.output}"


class BaseTool:
    """Interface base para ferramentas executáveis."""
    name: str = ""
    description: str = ""
    parameters_schema: Dict[str, Any] = {}

    def get_definition(self) -> ToolDefinition:
        return ToolDefinition(
            name=self.name,
            description=self.description,
            parameters=self.parameters_schema
        )

    async def execute(self, **kwargs: Any) -> ToolResult:
        raise NotImplementedError
