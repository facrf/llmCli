"""Tests for provider registry and model resolvers."""
import pytest
from src.providers.registry import ProviderRegistry
from src.providers.llamacpp import LlamaCppProvider
from src.providers.ollama import OllamaProvider
from src.providers.gemini import GeminiProvider
from src.providers.anthropic import AnthropicProvider
from src.providers.openai_compatible import OpenAICompatibleProvider
from src.providers.base import ChatMessage
from src.tools.base import ToolDefinition


def test_provider_resolution():
    p_llama = ProviderRegistry.create_provider("llamacpp/default")
    assert isinstance(p_llama, LlamaCppProvider)

    p_ollama = ProviderRegistry.create_provider("ollama/qwen2.5-coder:7b")
    assert isinstance(p_ollama, OllamaProvider)

    p_gemini = ProviderRegistry.create_provider("gemini/gemini-2.5-flash")
    assert isinstance(p_gemini, GeminiProvider)

    p_claude = ProviderRegistry.create_provider("anthropic/claude-3-7-sonnet-20250219")
    assert isinstance(p_claude, AnthropicProvider)

    p_openai = ProviderRegistry.create_provider("openai/gpt-4o")
    assert isinstance(p_openai, OpenAICompatibleProvider)


def test_gemini_message_conversion():
    provider = GeminiProvider(model_name="gemini-2.5-flash", api_key="dummy_key")
    messages = [
        ChatMessage(role="system", content="Você é um assistente."),
        ChatMessage(role="user", content="Olá mundo!"),
        ChatMessage(role="assistant", content="Olá!")
    ]
    sys_inst, contents = provider._convert_contents(messages)
    assert sys_inst is not None
    assert sys_inst["parts"][0]["text"] == "Você é um assistente."
    assert len(contents) == 2
    assert contents[0]["role"] == "user"
    assert contents[1]["role"] == "model"


def test_anthropic_message_conversion():
    provider = AnthropicProvider(model_name="claude-3-7-sonnet-20250219", api_key="dummy_key")
    messages = [
        ChatMessage(role="system", content="System instruction."),
        ChatMessage(role="user", content="User prompt.")
    ]
    sys_prompt, converted = provider._convert_messages(messages)
    assert sys_prompt == "System instruction."
    assert len(converted) == 1
    assert converted[0]["role"] == "user"
    assert converted[0]["content"] == "User prompt."


def test_openai_tool_conversion():
    provider = OpenAICompatibleProvider(model_name="gpt-4o", api_key="dummy_key")
    tools = [
        ToolDefinition(
            name="read_file",
            description="Reads a file",
            parameters={"type": "object", "properties": {"path": {"type": "string"}}}
        )
    ]
    converted_tools = provider._convert_tools(tools)
    assert len(converted_tools) == 1
    assert converted_tools[0]["type"] == "function"
    assert converted_tools[0]["function"]["name"] == "read_file"
