"""Dedicated Ollama provider supporting local models & model listing."""
from __future__ import annotations

import json
from typing import Any, AsyncGenerator, Dict, List, Optional, Tuple
import httpx
from src.providers.base import ChatMessage, LLMProvider, StreamChunk
from src.providers.openai_compatible import OpenAICompatibleProvider
from src.tools.base import ToolCall, ToolDefinition


class OllamaProvider(LLMProvider):
    def __init__(
        self,
        model_name: str = "qwen2.5-coder:latest",
        base_url: str = "http://localhost:11434",
        **kwargs: Any
    ) -> None:
        super().__init__(model_name, **kwargs)
        self.base_url = base_url.rstrip("/")
        self.compat = OpenAICompatibleProvider(
            model_name=model_name,
            base_url=f"{self.base_url}/v1",
            api_key="ollama",
            **kwargs
        )

    async def chat_stream(
        self,
        messages: List[ChatMessage],
        tools: Optional[List[ToolDefinition]] = None,
        temperature: float = 0.2,
        max_tokens: int = 4096,
    ) -> AsyncGenerator[StreamChunk, None]:
        async for chunk in self.compat.chat_stream(
            messages=messages,
            tools=tools,
            temperature=temperature,
            max_tokens=max_tokens
        ):
            yield chunk

    async def check_health(self) -> Tuple[bool, str]:
        try:
            async with httpx.AsyncClient(timeout=4.0) as client:
                res = await client.get(f"{self.base_url}/api/version")
                if res.status_code == 200:
                    ver = res.json().get("version", "")
                    return True, f"Ollama ativo (versão {ver})"
                return False, f"HTTP {res.status_code}"
        except Exception as e:
            return False, f"Ollama inacessível em {self.base_url}: {e}"

    async def list_available_models(self) -> List[str]:
        try:
            async with httpx.AsyncClient(timeout=4.0) as client:
                res = await client.get(f"{self.base_url}/api/tags")
                if res.status_code == 200:
                    data = res.json()
                    return [m.get("name") for m in data.get("models", []) if m.get("name")]
        except Exception:
            pass
        return [self.model_name]
