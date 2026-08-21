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
