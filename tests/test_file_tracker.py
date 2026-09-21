"""Tests for FileTracker and context building."""
from src.config import get_config
from src.context.file_tracker import FileTracker


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


def test_file_tracker_does_not_add_secret_files():
    config = get_config()
    secret_file = config.project_root / "tests" / ".env"
    secret_file.write_text("API_KEY=never-send-this", encoding="utf-8")
    try:
        tracker = FileTracker()
        ok, message = tracker.add_file("tests/.env")
        assert ok is False
        assert "protegido" in message
        assert "never-send-this" not in tracker.get_context_text()
    finally:
        secret_file.unlink(missing_ok=True)
