"""Dedicated llama.cpp server provider."""
from __future__ import annotations

import json
from typing import Any, AsyncGenerator, Dict, List, Optional, Tuple
import httpx
from src.providers.base import ChatMessage, LLMProvider, StreamChunk
from src.providers.openai_compatible import OpenAICompatibleProvider
from src.tools.base import ToolCall, ToolDefinition


class LlamaCppProvider(LLMProvider):
    """Adaptador dedicado para servidores llama.cpp (porta padrão 8080)."""

    def __init__(
        self,
        model_name: str = "default",
        base_url: str = "http://localhost:8080",
        api_key: Optional[str] = None,
        **kwargs: Any
    ) -> None:
        super().__init__(model_name, **kwargs)
        self.base_url = base_url.rstrip("/")
        # O llama.cpp server expõe a API padrão /v1/chat/completions
        self.compat_provider = OpenAICompatibleProvider(
            model_name=model_name,
            base_url=f"{self.base_url}/v1" if not self.base_url.endswith("/v1") else self.base_url,
            api_key=api_key or "sk-llamacpp",
            **kwargs
        )

    async def chat_stream(
        self,
        messages: List[ChatMessage],
        tools: Optional[List[ToolDefinition]] = None,
        temperature: float = 0.2,
        max_tokens: int = 4096,
    ) -> AsyncGenerator[StreamChunk, None]:
        async for chunk in self.compat_provider.chat_stream(
            messages=messages,
            tools=tools,
            temperature=temperature,
            max_tokens=max_tokens
        ):
            yield chunk

    async def check_health(self) -> Tuple[bool, str]:
        """Verifica os endpoints de saúde e propriedades do llama.cpp."""
        try:
            async with httpx.AsyncClient(timeout=4.0) as client:
                # 1. Tentar endpoint /health do llama.cpp
                health_url = f"{self.base_url}/health"
                try:
                    res = await client.get(health_url)
                    if res.status_code == 200:
                        data = res.json()
                        status = data.get("status", "ok")
                        return True, f"Servidor llama.cpp ativo ({status})"
                except Exception:
                    pass

                # 2. Tentar endpoint /props
                try:
                    props_url = f"{self.base_url}/props"
                    res = await client.get(props_url)
                    if res.status_code == 200:
                        props = res.json()
                        default_gen = props.get("default_generation_settings", {})
                        ctx_size = default_gen.get("n_ctx", "desconhecido")
                        return True, f"Servidor llama.cpp ativo (Contexto: {ctx_size} tokens)"
                except Exception:
                    pass

                # 3. Tentar endpoint /v1/models
                models_url = f"{self.base_url}/v1/models"
                res = await client.get(models_url)
                if res.status_code == 200:
                    return True, "Servidor llama.cpp ativo (API /v1/models OK)"

                return False, f"Servidor llama.cpp respondeu HTTP {res.status_code}"
        except Exception as exc:
            return False, f"Servidor llama.cpp inacessível em {self.base_url}: {exc}"

    async def list_available_models(self) -> List[str]:
        try:
            async with httpx.AsyncClient(timeout=4.0) as client:
                res = await client.get(f"{self.base_url}/v1/models")
                if res.status_code == 200:
                    data = res.json()
                    models = [m.get("id") for m in data.get("data", []) if m.get("id")]
                    if models:
                        return models
        except Exception:
            pass
        return [self.model_name]
