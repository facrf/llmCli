"""Tests for FileTracker and context building."""
from src.context.file_tracker import FileTracker
from src.config import get_config


def test_file_tracker_single_file():
    tracker = FileTracker()
    ok, msg = tracker.add_file("src/config.py")
    assert ok is True
    assert "src/config.py" in tracker.list_files()

    context = tracker.get_context_text()
    assert "src/config.py" in context
    assert "class Config" in context

    tracker.remove_file("src/config.py")
    assert "src/config.py" not in tracker.list_files()
    assert tracker.get_context_text() == ""


def test_file_tracker_directory_recursion():
    tracker = FileTracker()
    ok, msg = tracker.add_file("src/tools")
    assert ok is True
    files = tracker.list_files()
    assert any("filesystem.py" in f for f in files)
    assert any("terminal.py" in f for f in files)


def test_file_tracker_security_boundary():
    tracker = FileTracker()
    ok, msg = tracker.add_file("/etc/passwd")
    assert ok is False
    assert "fora do workspace" in msg
