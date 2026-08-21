"""Tests for conversation sessions and YOLO mode handling."""
import pytest
from src.config import get_config
from src.core.session import Session
from src.context.file_tracker import FileTracker
from src.core.agent import Agent


def test_session_message_flow():
    tracker = FileTracker()
    session = Session(file_tracker=tracker)

    session.add_user_message("Crie um arquivo teste.py")
    session.add_assistant_message("Criando arquivo...")

    full_msgs = session.get_full_messages()
    assert len(full_msgs) == 3
    assert full_msgs[0].role == "system"
    assert full_msgs[1].role == "user"
    assert full_msgs[2].role == "assistant"


def test_yolo_mode_toggle():
    config = get_config()
    initial = config.yolo_mode
    config.yolo_mode = not initial
    assert config.yolo_mode != initial
    config.yolo_mode = initial  # Restaurar


def test_session_custom_system_prompt():
    session = Session()
    session.set_custom_system_prompt("Você é um especialista em Python.")
    sys_msg = session.build_system_message()
    assert sys_msg.content == "Você é um especialista em Python."

    session.reset_system_prompt()
    sys_msg_default = session.build_system_message()
    assert "llmCli" in sys_msg_default.content


def test_session_compact_history():
    session = Session()
    session.add_user_message("Passo 1")
    session.add_assistant_message("Resposta 1")
    session.add_user_message("Passo 2")
    session.add_assistant_message("Resposta 2")

    assert len(session.messages) == 4
    session.compact_history("Resumo dos passos 1 e 2", keep_last_n=2)
    assert len(session.messages) == 3
    assert "RESUMO DO CONTEXTO ANTERIOR" in session.messages[0].content
    assert session.messages[1].content == "Passo 2"
    assert session.messages[2].content == "Resposta 2"

