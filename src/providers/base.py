"""Base classes and interfaces for all LLM providers (Local & Cloud)."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, AsyncGenerator, Dict, List, Optional
from src.tools.base import ToolCall, ToolDefinition


@dataclass
class ChatMessage:
    role: str  # 'system', 'user', 'assistant', 'tool'
    content: str
    tool_calls: Optional[List[ToolCall]] = None
    tool_call_id: Optional[str] = None
    name: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {
            "role": self.role,
            "content": self.content
        }
        if self.tool_calls:
            data["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.name,
                        "arguments": tc.arguments if isinstance(tc.arguments, str) else str(tc.arguments)
                    }
                }
                for tc in self.tool_calls
            ]
        if self.tool_call_id:
            data["tool_call_id"] = self.tool_call_id
        if self.name:
            data["name"] = self.name
        return data


@dataclass
class StreamChunk:
    delta_content: str = ""
    tool_calls: Optional[List[ToolCall]] = None
    is_done: bool = False
    finish_reason: Optional[str] = None
    error: Optional[str] = None


class LLMProvider(ABC):
    """Classe base para adaptadores de provedores de LLM."""

    def __init__(self, model_name: str, **kwargs: Any) -> None:
        self.model_name = model_name
        self.extra_config = kwargs

    @abstractmethod
    async def chat_stream(
        self,
        messages: List[ChatMessage],
        tools: Optional[List[ToolDefinition]] = None,
        temperature: float = 0.2,
        max_tokens: int = 4096,
    ) -> AsyncGenerator[StreamChunk, None]:
        """Gera tokens e chamadas de ferramentas em tempo real (streaming)."""
        yield StreamChunk(is_done=True)

    @abstractmethod
    async def check_health(self) -> Tuple[bool, str]:
        """Verifica se o provedor / servidor está acessível."""
        return True, "OK"

    async def list_available_models(self) -> List[str]:
        """Lista modelos disponíveis no provedor (se suportado)."""
        return [self.model_name]
