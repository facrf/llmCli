"""Universal OpenAI-compatible API provider (OpenAI, LM Studio, vLLM, DeepSeek, Groq, OpenRouter)."""
from __future__ import annotations

import json
from typing import Any, AsyncGenerator, Dict, List, Optional, Tuple
import httpx
from src.providers.base import ChatMessage, LLMProvider, StreamChunk
from src.tools.base import ToolCall, ToolDefinition


class OpenAICompatibleProvider(LLMProvider):
    def __init__(
        self,
        model_name: str,
        base_url: str = "https://api.openai.com/v1",
        api_key: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: float = 120.0,
        **kwargs: Any
    ) -> None:
        super().__init__(model_name, **kwargs)
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key or "sk-dummy"
        self.headers = headers or {}
        self.timeout = timeout

    def _build_headers(self) -> Dict[str, str]:
        hdrs = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            **self.headers
        }
        return hdrs

    def _convert_messages(self, messages: List[ChatMessage]) -> List[Dict[str, Any]]:
        converted: List[Dict[str, Any]] = []
        for msg in messages:
            item: Dict[str, Any] = {"role": msg.role, "content": msg.content}
            if msg.role == "assistant" and msg.tool_calls:
                item["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.name,
                            "arguments": json.dumps(tc.arguments) if isinstance(tc.arguments, dict) else str(tc.arguments)
                        }
                    }
                    for tc in msg.tool_calls
                ]
            if msg.role == "tool":
                item["tool_call_id"] = msg.tool_call_id or "call_default"
                if msg.name:
                    item["name"] = msg.name
            converted.append(item)
        return converted

    def _convert_tools(self, tools: List[ToolDefinition]) -> List[Dict[str, Any]]:
        return [
            {
                "type": "function",
                "function": {
                    "name": t.name,
                    "description": t.description,
                    "parameters": t.parameters
                }
            }
            for t in tools
        ]

    async def chat_stream(
        self,
        messages: List[ChatMessage],
        tools: Optional[List[ToolDefinition]] = None,
        temperature: float = 0.2,
        max_tokens: int = 4096,
    ) -> AsyncGenerator[StreamChunk, None]:
        url = f"{self.base_url}/chat/completions"
        payload: Dict[str, Any] = {
            "model": self.model_name,
            "messages": self._convert_messages(messages),
            "stream": True,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        if tools:
            payload["tools"] = self._convert_tools(tools)
            payload["tool_choice"] = "auto"

        headers = self._build_headers()

        tool_calls_accumulator: Dict[int, Dict[str, Any]] = {}

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                async with client.stream("POST", url, headers=headers, json=payload) as response:
                    if response.status_code != 200:
                        err_text = await response.aread()
                        yield StreamChunk(is_done=True, error=f"HTTP {response.status_code}: {err_text.decode('utf-8', errors='replace')}")
                        return

                    async for line in response.aiter_lines():
                        line = line.strip()
                        if not line or line.startswith(":") or line == "data: [DONE]":
                            continue

                        if line.startswith("data: "):
                            raw_json = line[6:]
                            try:
                                data = json.loads(raw_json)
                                choices = data.get("choices", [])
                                if not choices:
                                    continue
                                choice = choices[0]
                                delta = choice.get("delta", {})
                                finish_reason = choice.get("finish_reason")

                                content_delta = delta.get("content") or ""

                                # Acumular tool calls do delta
                                if "tool_calls" in delta and delta["tool_calls"]:
                                    for tc_chunk in delta["tool_calls"]:
                                        idx = tc_chunk.get("index", 0)
                                        if idx not in tool_calls_accumulator:
                                            tool_calls_accumulator[idx] = {
                                                "id": tc_chunk.get("id", f"call_{idx}"),
                                                "name": "",
                                                "arguments_str": ""
                                            }
                                        if tc_chunk.get("id"):
                                            tool_calls_accumulator[idx]["id"] = tc_chunk["id"]
                                        func = tc_chunk.get("function", {})
                                        if func.get("name"):
                                            tool_calls_accumulator[idx]["name"] += func["name"]
                                        if func.get("arguments"):
                                            tool_calls_accumulator[idx]["arguments_str"] += func["arguments"]

                                yield StreamChunk(
                                    delta_content=content_delta,
                                    is_done=bool(finish_reason),
                                    finish_reason=finish_reason
                                )
                            except json.JSONDecodeError:
                                continue

            # Montar tool calls finais acumulados
            if tool_calls_accumulator:
                final_calls: List[ToolCall] = []
                for _, item in tool_calls_accumulator.items():
                    args_obj: Dict[str, Any] = {}
                    try:
                        args_obj = json.loads(item["arguments_str"]) if item["arguments_str"] else {}
                    except Exception:
                        args_obj = {"raw_arguments": item["arguments_str"]}

                    final_calls.append(
                        ToolCall(
                            id=item["id"],
                            name=item["name"],
                            arguments=args_obj
                        )
                    )
                yield StreamChunk(tool_calls=final_calls, is_done=True)

        except Exception as exc:
            yield StreamChunk(is_done=True, error=f"Erro de conexão com provedor ({url}): {exc}")

    async def check_health(self) -> Tuple[bool, str]:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                url = f"{self.base_url}/models"
                res = await client.get(url, headers=self._build_headers())
                if res.status_code in (200, 401, 403):
                    return True, "Acessível"
                return False, f"HTTP {res.status_code}"
        except Exception as e:
            return False, str(e)
