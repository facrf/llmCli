"""Tests for REPL autocomplete."""
from prompt_toolkit.document import Document
from src.ui.completer import CliCompleter


def test_completer_slash_commands():
    completer = CliCompleter()
    doc = Document("/yo")
    completions = list(completer.get_completions(doc, None))
    assert any(c.text == "/yolo" for c in completions)

    doc_model = Document("/mod")
    completions_model = list(completer.get_completions(doc_model, None))
    assert any(c.text == "/model" for c in completions_model)


def test_completer_model_suggestions():
    completer = CliCompleter()
    doc = Document("/model llama")
    completions = list(completer.get_completions(doc, None))
    assert any("llamacpp" in c.text for c in completions)


def test_completer_file_suggestions():
    completer = CliCompleter()
    doc = Document("/add src/")
    completions = list(completer.get_completions(doc, None))
    assert any("src/main.py" in c.text or "src/config.py" in c.text for c in completions)
