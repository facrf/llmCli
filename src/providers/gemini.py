"""Google Gemini native API provider with streaming and function calling."""
from __future__ import annotations

import json
import os
from typing import Any, AsyncGenerator, Dict, List, Optional, Tuple
import httpx
from src.providers.base import ChatMessage, LLMProvider, StreamChunk
from src.tools.base import ToolCall, ToolDefinition


class GeminiProvider(LLMProvider):
    def __init__(
        self,
        model_name: str = "gemini-2.5-flash",
        api_key: Optional[str] = None,
        **kwargs: Any
    ) -> None:
        super().__init__(model_name, **kwargs)
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "")
        # Normalizar nome do modelo caso contenha prefixo
        if self.model_name.startswith("gemini/"):
            self.model_name = self.model_name.replace("gemini/", "", 1)

    def _convert_contents(self, messages: List[ChatMessage]) -> Tuple[Optional[Dict[str, Any]], List[Dict[str, Any]]]:
        system_instruction: Optional[Dict[str, Any]] = None
        contents: List[Dict[str, Any]] = []

        for msg in messages:
            if msg.role == "system":
                system_instruction = {
                    "parts": [{"text": msg.content}]
                }
            elif msg.role == "user":
                contents.append({
                    "role": "user",
                    "parts": [{"text": msg.content}]
                })
            elif msg.role == "assistant":
                parts: List[Dict[str, Any]] = []
                if msg.content:
                    parts.append({"text": msg.content})
                if msg.tool_calls:
                    for tc in msg.tool_calls:
                        parts.append({
                            "functionCall": {
                                "name": tc.name,
                                "args": tc.arguments if isinstance(tc.arguments, dict) else {}
                            }
                        })
                contents.append({"role": "model", "parts": parts or [{"text": ""}]})
            elif msg.role == "tool":
                contents.append({
                    "role": "user",
                    "parts": [{
                        "functionResponse": {
                            "name": msg.name or "tool_call",
                            "response": {"output": msg.content}
                        }
                    }]
                })

        return system_instruction, contents

    def _convert_tools(self, tools: List[ToolDefinition]) -> List[Dict[str, Any]]:
        declarations = []
        for t in tools:
            declarations.append({
                "name": t.name,
                "description": t.description,
                "parameters": t.parameters
            })
        return [{"functionDeclarations": declarations}]

    async def chat_stream(
        self,
        messages: List[ChatMessage],
        tools: Optional[List[ToolDefinition]] = None,
        temperature: float = 0.2,
        max_tokens: int = 4096,
    ) -> AsyncGenerator[StreamChunk, None]:
        if not self.api_key:
            yield StreamChunk(is_done=True, error="Chave GEMINI_API_KEY não configurada no arquivo .env.")
            return

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:streamGenerateContent?alt=sse&key={self.api_key}"

        system_instruction, contents = self._convert_contents(messages)

        payload: Dict[str, Any] = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens
            }
        }

        if system_instruction:
            payload["systemInstruction"] = system_instruction

        if tools:
            payload["tools"] = self._convert_tools(tools)

        accumulated_tool_calls: List[ToolCall] = []

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                async with client.stream("POST", url, json=payload) as response:
                    if response.status_code != 200:
                        err_text = await response.aread()
                        yield StreamChunk(is_done=True, error=f"HTTP {response.status_code} Gemini API: {err_text.decode('utf-8', errors='replace')}")
                        return

                    async for line in response.aiter_lines():
                        line = line.strip()
                        if not line or not line.startswith("data: "):
                            continue

                        raw_json = line[6:]
                        try:
                            data = json.loads(raw_json)
                            candidates = data.get("candidates", [])
                            if not candidates:
                                continue
                            cand = candidates[0]
                            content = cand.get("content", {})
                            parts = content.get("parts", [])

                            for part in parts:
                                if "text" in part:
                                    yield StreamChunk(delta_content=part["text"])
                                elif "functionCall" in part:
                                    fc = part["functionCall"]
                                    accumulated_tool_calls.append(
                                        ToolCall(
                                            id=f"gemini_call_{len(accumulated_tool_calls)}",
                                            name=fc.get("name", ""),
                                            arguments=fc.get("args", {})
                                        )
                                    )

                        except json.JSONDecodeError:
                            continue

            if accumulated_tool_calls:
                yield StreamChunk(tool_calls=accumulated_tool_calls, is_done=True)
            else:
                yield StreamChunk(is_done=True)

        except Exception as exc:
            yield StreamChunk(is_done=True, error=f"Erro na requisição Gemini: {exc}")

    async def check_health(self) -> Tuple[bool, str]:
        if not self.api_key:
            return False, "GEMINI_API_KEY ausente no .env"
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}?key={self.api_key}"
                res = await client.get(url)
                if res.status_code == 200:
                    return True, "API Google Gemini conectada"
                return False, f"HTTP {res.status_code}"
        except Exception as e:
            return False, str(e)
