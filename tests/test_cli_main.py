"""Tests for CLI arguments parsing and entrypoints."""
from src.main import parse_arguments


def test_parse_arguments_defaults():
    args = parse_arguments([])
    assert args.prompt == []
    assert args.model is None
    assert args.yolo is False
    assert args.file == []
    assert args.models is False


def test_parse_arguments_custom_flags():
    args = parse_arguments(["-m", "llamacpp/default", "-y", "-f", "src/main.py", "Refatore", "o", "código"])
    assert args.model == "llamacpp/default"
    assert args.yolo is True
    assert args.file == ["src/main.py"]
    assert args.prompt == ["Refatore", "o", "código"]


def test_print_banner():
    from src.ui.console import print_banner
    # Deve rodar sem erro tanto com yolo=False quanto yolo=True
    print_banner(active_model="llamacpp/default", yolo_mode=False)
    print_banner(active_model="gemini/gemini-2.5-flash", yolo_mode=True)


