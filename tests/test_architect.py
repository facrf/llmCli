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
