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

    # Troca direta por nome
    cont = await repl.handle_slash_command("/model llamacpp/default")
    assert cont is True
    assert agent.config.active_model == "llamacpp/default"

    # Troca por número ID (ex: 8 = gemini/gemini-2.5-flash)
    await repl.handle_slash_command("/model 8")
    assert agent.config.active_model == "gemini/gemini-2.5-flash"

    # Troca por número ID (ex: 11 = openai/gpt-4o)
    await repl.handle_slash_command("/model 11")
    assert agent.config.active_model == "openai/gpt-4o"


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
    assert await repl.handle_slash_command("/q") is False


@pytest.mark.asyncio
async def test_slash_partial_command_autocomplete():
    agent = Agent()
    repl = ReplSession(agent=agent)

    # /exi ou /qui deve resolver para /exit / /quit e encerrar (retornar False)
    assert await repl.handle_slash_command("/exi") is False
    assert await repl.handle_slash_command("/qui") is False

    # /yo deve resolver para /yolo e alternar modo
    initial_mode = agent.config.yolo_mode
    assert await repl.handle_slash_command("/yo") is True
    assert agent.config.yolo_mode != initial_mode

    # /tok deve resolver para /tokens
    assert await repl.handle_slash_command("/tok") is True

    # /ad deve resolver para /add
    test_path = "src/config.py"
    assert await repl.handle_slash_command(f"/ad {test_path}") is True
    assert test_path in agent.session.file_tracker.tracked_files

    # Comando ambiguo como /m (/model vs /models) nao quebra
    assert await repl.handle_slash_command("/m") is True

    # Comando desconhecido nao quebra
    assert await repl.handle_slash_command("/desconhecido") is True


@pytest.mark.asyncio
async def test_slash_temp_and_system():
    agent = Agent()
    repl = ReplSession(agent=agent)

    # /temp
    assert await repl.handle_slash_command("/temp") is True
    assert await repl.handle_slash_command("/temp 0.7") is True
    assert agent.config.temperature == 0.7
    assert await repl.handle_slash_command("/temp 5.0") is True  # Fora do range, nao quebra

    # /system
    assert await repl.handle_slash_command("/system") is True
    assert await repl.handle_slash_command("/system Seja conciso.") is True
    assert agent.session.custom_system_prompt == "Seja conciso."
    assert await repl.handle_slash_command("/system reset") is True
    assert agent.session.custom_system_prompt is None


@pytest.mark.asyncio
async def test_slash_compact_and_review():
    agent = Agent()
    repl = ReplSession(agent=agent)

    # /compact em sessao vazia
    assert await repl.handle_slash_command("/compact") is True

    # /review
    assert await repl.handle_slash_command("/review") is True

    # /test
    assert await repl.handle_slash_command("/test tests/test_soma.py") is True


@pytest.mark.asyncio
async def test_slash_reset_options():
    agent = Agent()
    repl = ReplSession(agent=agent)

    # Configurar preferências
    await repl.handle_slash_command("/yolo")
    await repl.handle_slash_command("/temp 0.8")

    # /reset simples
    assert await repl.handle_slash_command("/reset") is True

    # /reset prefs
    assert await repl.handle_slash_command("/reset prefs") is True
    assert agent.config.yolo_mode is False
    assert agent.config.temperature == 0.2

    # /reset all
    assert await repl.handle_slash_command("/reset all") is True



