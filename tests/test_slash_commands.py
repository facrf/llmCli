"""Tests for all interactive slash commands."""
import pytest
from src.core.agent import Agent
from src.core.session import Session
from src.ui.repl import ReplSession


@pytest.mark.asyncio
async def test_slash_yolo_toggle():
    agent = Agent()
    repl = ReplSession(agent=agent)

    initial_mode = agent.config.yolo_mode
    cont = await repl.handle_slash_command("/yolo")
    assert cont is True
    assert agent.config.yolo_mode != initial_mode

    # Alternar de volta
    await repl.handle_slash_command("/yolo")
    assert agent.config.yolo_mode == initial_mode


@pytest.mark.asyncio
async def test_slash_model_switch():
    agent = Agent()
    repl = ReplSession(agent=agent)

    cont = await repl.handle_slash_command("/model llamacpp/default")
    assert cont is True
    assert agent.config.active_model == "llamacpp/default"


@pytest.mark.asyncio
async def test_slash_add_drop_files():
    agent = Agent()
    repl = ReplSession(agent=agent)

    test_path = "src/config.py"
    await repl.handle_slash_command(f"/add {test_path}")
    assert test_path in agent.session.file_tracker.tracked_files

    await repl.handle_slash_command(f"/drop {test_path}")
    assert test_path not in agent.session.file_tracker.tracked_files


@pytest.mark.asyncio
async def test_slash_clear_and_reset():
    agent = Agent()
    repl = ReplSession(agent=agent)

    agent.session.add_user_message("Teste")
    agent.session.file_tracker.add_file("src/config.py")

    assert len(agent.session.messages) == 1
    assert len(agent.session.file_tracker.tracked_files) == 1

    # Clear limpa mensagens mas mantém arquivos
    await repl.handle_slash_command("/clear")
    assert len(agent.session.messages) == 0
    assert len(agent.session.file_tracker.tracked_files) == 1

    # Reset limpa ambos
    await repl.handle_slash_command("/reset")
    assert len(agent.session.messages) == 0
    assert len(agent.session.file_tracker.tracked_files) == 0


@pytest.mark.asyncio
async def test_slash_run_command():
    agent = Agent()
    repl = ReplSession(agent=agent)
    cont = await repl.handle_slash_command("/run echo 'slash_test'")
    assert cont is True


@pytest.mark.asyncio
async def test_slash_tokens_and_help():
    agent = Agent()
    repl = ReplSession(agent=agent)
    assert await repl.handle_slash_command("/tokens") is True
    assert await repl.handle_slash_command("/help") is True
    assert await repl.handle_slash_command("/files") is True
    assert await repl.handle_slash_command("/diff") is True


@pytest.mark.asyncio
async def test_slash_exit():
    agent = Agent()
    repl = ReplSession(agent=agent)
    assert await repl.handle_slash_command("/exit") is False
    assert await repl.handle_slash_command("/quit") is False
