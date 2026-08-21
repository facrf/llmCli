"""Unit tests for Architect Mode (Combining Planner and Fast Editor models)."""
import pytest
from src.config import Config, get_config
from src.core.agent import Agent
from src.ui.repl import ReplSession


def test_architect_mode_config():
    cfg = Config()
    assert cfg.architect_mode is False
    assert cfg.architect_model != ""

    cfg.architect_mode = True
    cfg.architect_model = "anthropic/claude-3-7-sonnet-20250219"
    assert cfg.architect_mode is True
    assert cfg.architect_model == "anthropic/claude-3-7-sonnet-20250219"


@pytest.mark.asyncio
async def test_slash_architect_toggle():
    agent = Agent()
    repl = ReplSession(agent=agent)

    # Ativar modo arquiteto sem argumento
    initial_mode = agent.config.architect_mode
    assert await repl.handle_slash_command("/architect") is True
    assert agent.config.architect_mode != initial_mode

    # Definir modelo de arquiteto específico
    assert await repl.handle_slash_command("/architect gpt/gpt-4o") is True
    assert agent.config.architect_mode is True
    assert agent.config.architect_model == "gpt/gpt-4o"

    # Atalho /arch off
    assert await repl.handle_slash_command("/arch off") is True
    assert agent.config.architect_mode is False

    # Atalho /arch com modelo
    assert await repl.handle_slash_command("/arch gemini/gemini-2.5-pro") is True
    assert agent.config.architect_mode is True
    assert agent.config.architect_model == "gemini/gemini-2.5-pro"


@pytest.mark.asyncio
async def test_architect_editor_mock_pipeline():
    from src.providers.base import LLMProvider, StreamChunk
    from src.core.session import Session

    class MockArchProvider(LLMProvider):
        def __init__(self):
            super().__init__("mock-arch")
        async def chat_stream(self, messages, tools=None, temperature=0.2, max_tokens=4096):
            yield StreamChunk(delta_content="Plano do Arquiteto: modifique test_patch_sample.txt para retornar 42.", is_done=True)
        async def check_health(self):
            return True, "OK"

    class MockEditProvider(LLMProvider):
        def __init__(self):
            super().__init__("mock-edit")
        async def chat_stream(self, messages, tools=None, temperature=0.2, max_tokens=4096):
            patch = (
                "Arquivo: tests/test_patch_sample.txt\n"
                "<<<<<<< SEARCH\n"
                "def somar(a, b):\n"
                "    return a - b\n"
                "=======\n"
                "def somar(a, b):\n"
                "    return 42\n"
                ">>>>>>>\n"
            )
            yield StreamChunk(delta_content=patch, is_done=True)
        async def check_health(self):
            return True, "OK"

    session = Session()
    agent = Agent(session=session, architect_provider=MockArchProvider())
    agent.provider = MockEditProvider()
    agent.config.architect_mode = True
    agent.config.yolo_mode = True

    target_file = agent.config.project_root / "tests/test_patch_sample.txt"
    target_file.write_text("def somar(a, b):\n    return a - b\n", encoding="utf-8")

    res = await agent.run_prompt("Faça a função somar retornar 42")
    assert target_file.exists()
    assert "return 42" in target_file.read_text(encoding="utf-8")

