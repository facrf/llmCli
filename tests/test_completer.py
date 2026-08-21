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


def test_resolve_slash_command():
    from src.ui.completer import resolve_slash_command

    # Correspondência exata
    cmd, matches = resolve_slash_command("/exit")
    assert cmd == "/exit"
    assert matches == []

    # Prefixo único
    cmd, matches = resolve_slash_command("/ex")
    assert cmd == "/exit"
    assert matches == []

    cmd, matches = resolve_slash_command("/exi")
    assert cmd == "/exit"

    cmd, matches = resolve_slash_command("/yo")
    assert cmd == "/yolo"

    cmd, matches = resolve_slash_command("/cle")
    assert cmd == "/clear"

    cmd, matches = resolve_slash_command("/und")
    assert cmd == "/undo"

    # Ambíguo
    cmd, matches = resolve_slash_command("/m")
    assert cmd is None
    assert "/model" in matches and "/models" in matches

    # Ambíguo resolvido com argumento
    cmd, matches = resolve_slash_command("/mod", has_arg=True)
    assert cmd == "/model"

    # Desconhecido
    cmd, matches = resolve_slash_command("/comando_inexistente")
    assert cmd is None
    assert matches == []

