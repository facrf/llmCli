"""Anthropic Claude native API provider."""
from __future__ import annotations

import json
import os
from typing import Any, AsyncGenerator, Dict, List, Optional, Tuple
import httpx
from src.providers.base import ChatMessage, LLMProvider, StreamChunk
from src.tools.base import ToolCall, ToolDefinition


class AnthropicProvider(LLMProvider):
    def __init__(
        self,
        model_name: str = "claude-3-7-sonnet-20250219",
        api_key: Optional[str] = None,
        **kwargs: Any
    ) -> None:
        super().__init__(model_name, **kwargs)
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY", "")
        if self.model_name.startswith("anthropic/"):
            self.model_name = self.model_name.replace("anthropic/", "", 1)

    def _convert_messages(self, messages: List[ChatMessage]) -> Tuple[str, List[Dict[str, Any]]]:
        system_prompt = ""
        converted: List[Dict[str, Any]] = []

        for msg in messages:
            if msg.role == "system":
                system_prompt += msg.content + "\n"
            elif msg.role == "tool":
                tool_block = {
                    "type": "tool_result",
                    "tool_use_id": msg.tool_call_id or "tool_call_id",
                    "content": msg.content
                }
                if converted and converted[-1]["role"] == "user":
                    if isinstance(converted[-1]["content"], list):
                        converted[-1]["content"].append(tool_block)
                    else:
                        converted[-1]["content"] = [
                            {"type": "text", "text": str(converted[-1]["content"])},
                            tool_block
                        ]
                else:
                    converted.append({
                        "role": "user",
                        "content": [tool_block]
                    })
            elif msg.role == "assistant":
                content_blocks = []
                if msg.content:
                    content_blocks.append({"type": "text", "text": msg.content})
                if msg.tool_calls:
                    for tc in msg.tool_calls:
                        content_blocks.append({
                            "type": "tool_use",
                            "id": tc.id,
                            "name": tc.name,
                            "input": tc.arguments if isinstance(tc.arguments, dict) else {}
                        })
                converted.append({"role": "assistant", "content": content_blocks or [{"type": "text", "text": ""}]})
            else:
                if converted and converted[-1]["role"] == "user":
                    if isinstance(converted[-1]["content"], str):
                        converted[-1]["content"] += "\n" + msg.content
                    elif isinstance(converted[-1]["content"], list):
                        converted[-1]["content"].append({"type": "text", "text": msg.content})
                else:
                    converted.append({"role": "user", "content": msg.content})

        return system_prompt.strip(), converted

    def _convert_tools(self, tools: List[ToolDefinition]) -> List[Dict[str, Any]]:
        return [
            {
                "name": t.name,
                "description": t.description,
                "input_schema": t.parameters
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
        if not self.api_key:
            yield StreamChunk(is_done=True, error="Chave ANTHROPIC_API_KEY não configurada no arquivo .env.")
            return

        url = "https://api.anthropic.com/v1/messages"
        system_prompt, formatted_messages = self._convert_messages(messages)

        payload: Dict[str, Any] = {
            "model": self.model_name,
            "messages": formatted_messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": True
        }

        if system_prompt:
            payload["system"] = system_prompt

        if tools:
            payload["tools"] = self._convert_tools(tools)

        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }

        tool_calls: List[ToolCall] = []
        current_tool: Optional[Dict[str, Any]] = None

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                async with client.stream("POST", url, headers=headers, json=payload) as response:
                    if response.status_code != 200:
                        err_text = await response.aread()
                        yield StreamChunk(is_done=True, error=f"HTTP {response.status_code} Anthropic: {err_text.decode('utf-8', errors='replace')}")
                        return

                    async for line in response.aiter_lines():
                        line = line.strip()
                        if not line or not line.startswith("data: "):
                            continue

                        raw_json = line[6:]
                        try:
                            event = json.loads(raw_json)
                            event_type = event.get("type")

                            if event_type == "content_block_start":
                                block = event.get("content_block", {})
                                if block.get("type") == "tool_use":
                                    current_tool = {
                                        "id": block.get("id", ""),
                                        "name": block.get("name", ""),
                                        "input_json": ""
                                    }
                            elif event_type == "content_block_delta":
                                delta = event.get("delta", {})
                                if delta.get("type") == "text_delta":
                                    yield StreamChunk(delta_content=delta.get("text", ""))
                                elif delta.get("type") == "input_json_delta":
                                    if current_tool:
                                        current_tool["input_json"] += delta.get("partial_json", "")
                            elif event_type == "content_block_stop":
                                if current_tool:
                                    args = {}
                                    try:
                                        args = json.loads(current_tool["input_json"]) if current_tool["input_json"] else {}
                                    except Exception:
                                        pass
                                    tool_calls.append(ToolCall(
                                        id=current_tool["id"],
                                        name=current_tool["name"],
                                        arguments=args
                                    ))
                                    current_tool = None
                            elif event_type == "message_stop":
                                if tool_calls:
                                    yield StreamChunk(tool_calls=tool_calls, is_done=True)
                                else:
                                    yield StreamChunk(is_done=True)

                        except json.JSONDecodeError:
                            continue

        except Exception as exc:
            yield StreamChunk(is_done=True, error=f"Erro na conexão Anthropic: {exc}")

    async def check_health(self) -> Tuple[bool, str]:
        if not self.api_key:
            return False, "ANTHROPIC_API_KEY ausente no .env"
        return True, "API Anthropic configurada"
