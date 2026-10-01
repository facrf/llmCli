"""Tests for autonomous Agent reasoning loop using mock LLM providers."""
from typing import AsyncGenerator, List, Optional

import pytest

from src.core.agent import Agent
from src.core.multi_agent import MultiAgentCoordinator
from src.core.session import Session
from src.providers.base import ChatMessage, LLMProvider, StreamChunk
from src.tools.base import ToolCall, ToolDefinition
from src.tools.mcp_client import McpTool


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


@pytest.mark.asyncio
async def test_read_only_role_can_read_but_cannot_write(monkeypatch):
    agent = Agent(session=Session())
    blocked_target = agent.config.project_root / "tests" / "role_blocked.txt"

    class RoleProvider(LLMProvider):
        def __init__(self):
            super().__init__("role-mock")
            self.turn = 0

        async def chat_stream(self, messages, tools=None, temperature=0.2, max_tokens=4096):
            if self.turn == 0:
                self.turn += 1
                assert tools and all(tool.name != "write_file" for tool in tools)
                yield StreamChunk(
                    tool_calls=[
                        ToolCall("read", "read_file", {"path": "src/config.py"}),
                        ToolCall("blocked", "write_file", {"path": "tests/role_blocked.txt", "content": "x"}),
                    ],
                    is_done=True,
                )
            else:
                yield StreamChunk(delta_content="Análise concluída.", is_done=True)

        async def check_health(self):
            return True, "OK"

    provider = RoleProvider()
    monkeypatch.setattr("src.core.agent.ProviderRegistry.create_provider", lambda *_: provider)

    response = await agent.run_role_prompt("researcher", "Analise a configuração")
    assert response == "Análise concluída."
    assert not blocked_target.exists()


@pytest.mark.asyncio
async def test_tester_role_receives_only_the_constrained_test_tool(monkeypatch):
    agent = Agent(session=Session())

    class TesterProvider(LLMProvider):
        def __init__(self):
            super().__init__("tester-mock")

        async def chat_stream(self, messages, tools=None, temperature=0.2, max_tokens=4096):
            tool_names = {tool.name for tool in tools}
            assert "run_project_tests" in tool_names
            assert "run_command" not in tool_names
            assert "write_file" not in tool_names
            yield StreamChunk(delta_content="Testes analisados.", is_done=True)

        async def check_health(self):
            return True, "OK"

    monkeypatch.setattr(
        "src.core.agent.ProviderRegistry.create_provider", lambda *_: TesterProvider()
    )
    response = await agent.run_role_prompt("tester", "Valide a suíte")
    assert response == "Testes analisados."


@pytest.mark.asyncio
async def test_mcp_tool_requires_confirmation(monkeypatch):
    agent = Agent(session=Session())
    monkeypatch.setattr(agent.config, "yolo_mode", False)
    calls = []

    async def runner(server_name, tool_name, arguments):
        calls.append((server_name, tool_name, arguments))
        return "executado"

    tool = McpTool("db", "delete", "Delete rows", {}, runner)
    agent.tools[tool.name] = tool
    monkeypatch.setattr("src.core.agent.ask_user_confirmation", lambda _: "no")

    result = await agent.execute_tool_with_permission(tool.name, {"query": "DELETE FROM data"})
    assert result.success is False
    assert calls == []


@pytest.mark.asyncio
async def test_provider_error_marks_role_failed(monkeypatch):
    agent = Agent(session=Session())

    class ErrorProvider(MockStreamProvider):
        def __init__(self):
            super().__init__([StreamChunk(is_done=True, error="provider unavailable")])

    monkeypatch.setattr("src.core.agent.ProviderRegistry.create_provider", lambda *_: ErrorProvider())
    coordinator = MultiAgentCoordinator(agent)

    report = await coordinator._delegate("researcher", "Analise o projeto", None)
    assert report.status == "failed"
    assert "provider unavailable" in report.summary


@pytest.mark.asyncio
@pytest.mark.parametrize("editor_loop", [False, True])
async def test_abort_patch_stops_remaining_tool_calls(monkeypatch, editor_loop):
    agent = Agent(session=Session())
    monkeypatch.setattr(agent.config, "yolo_mode", False)
    monkeypatch.setattr("src.core.agent.ask_user_confirmation", lambda _: "abort")
    target = agent.config.project_root / "tests" / "aborted_patch.txt"
    assert not target.exists()

    response = (
        "Arquivo: tests/aborted_patch.txt\n"
        "<<<<<<< SEARCH\n=======\nconteúdo\n>>>>>>> REPLACE\n"
    )
    tool_call = ToolCall("write", "write_file", {"path": "tests/aborted_patch.txt", "content": "tool"})
    agent.provider = MockStreamProvider([StreamChunk(delta_content=response, tool_calls=[tool_call])])

    if editor_loop:
        await agent._run_editor_loop()
    else:
        await agent.run_prompt("Crie o arquivo")

    assert not target.exists()
    assert all(message.role != "tool" for message in agent.session.messages)
