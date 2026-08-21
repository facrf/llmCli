"""Tests for autonomous Agent reasoning loop using mock LLM providers."""
import pytest
from typing import AsyncGenerator, List, Optional
from src.core.agent import Agent
from src.core.session import Session
from src.providers.base import ChatMessage, LLMProvider, StreamChunk
from src.tools.base import ToolCall, ToolDefinition


class MockStreamProvider(LLMProvider):
    def __init__(self, response_chunks: List[StreamChunk], **kwargs):
        super().__init__("mock-model", **kwargs)
        self.response_chunks = response_chunks

    async def chat_stream(
        self,
        messages: List[ChatMessage],
        tools: Optional[List[ToolDefinition]] = None,
        temperature: float = 0.2,
        max_tokens: int = 4096,
    ) -> AsyncGenerator[StreamChunk, None]:
        for chunk in self.response_chunks:
            yield chunk

    async def check_health(self):
        return True, "Mock OK"


@pytest.mark.asyncio
async def test_agent_text_response():
    session = Session()
    agent = Agent(session=session)
    agent.provider = MockStreamProvider([
        StreamChunk(delta_content="Olá, "),
        StreamChunk(delta_content="eu sou a IA!"),
        StreamChunk(is_done=True)
    ])

    response = await agent.run_prompt("Diga olá")
    assert "Olá, eu sou a IA!" in response
    assert len(session.messages) == 2  # user + assistant


@pytest.mark.asyncio
async def test_agent_autonomous_tool_execution_yolo():
    session = Session()
    agent = Agent(session=session)
    agent.config.yolo_mode = True

    # 1. Primeiro stream pede a ferramenta write_file
    # 2. Segundo stream processa o resultado e dá a resposta final
    tool_call = ToolCall(
        id="call_123",
        name="write_file",
        arguments={"path": "tests/test_mock_output.txt", "content": "mock content"}
    )

    class MultiTurnMockProvider(LLMProvider):
        def __init__(self):
            super().__init__("mock-multi")
            self.turn = 0

        async def chat_stream(self, messages, tools=None, temperature=0.2, max_tokens=4096):
            if self.turn == 0:
                self.turn += 1
                yield StreamChunk(delta_content="Vou criar o arquivo.", tool_calls=[tool_call], is_done=True)
            else:
                yield StreamChunk(delta_content="Arquivo criado com sucesso!", is_done=True)

        async def check_health(self):
            return True, "Mock OK"

    agent.provider = MultiTurnMockProvider()
    response = await agent.run_prompt("Crie o arquivo de teste")
    assert "Arquivo criado" in response

    # Verificar que o arquivo foi de fato criado no workspace
    target = agent.config.project_root / "tests/test_mock_output.txt"
    assert target.exists()
    assert target.read_text(encoding="utf-8") == "mock content"

    # Limpeza
    target.unlink()


@pytest.mark.asyncio
async def test_agent_search_replace_block_parsing():
    session = Session()
    agent = Agent(session=session)
    agent.config.yolo_mode = True

    target_file = agent.config.project_root / "tests/test_patch_sample.txt"
    target_file.write_text("def somar(a, b):\n    return a - b\n", encoding="utf-8")

    diff_response = """
Vou corrigir a função:
Arquivo: tests/test_patch_sample.txt
<<<<<<< SEARCH
def somar(a, b):
    return a - b
=======
def somar(a, b):
    return a + b
>>>>>>>
Pronto, corrigido!
"""

    agent.provider = MockStreamProvider([
        StreamChunk(delta_content=diff_response),
        StreamChunk(is_done=True)
    ])

    await agent.run_prompt("Corrija a função somar")

    updated_content = target_file.read_text(encoding="utf-8")
    assert "return a + b" in updated_content

    # Limpeza
    target_file.unlink()
