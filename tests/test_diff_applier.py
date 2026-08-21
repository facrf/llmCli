"""Tests for diff applier and Search/Replace block parser."""
import pytest
from src.core.diff_applier import (
    extract_search_replace_blocks,
    fuzzy_find_and_replace
)


def test_extract_search_replace_blocks():
    text = """
Aqui está a alteração:

Arquivo: src/sample.py
<<<<<<< SEARCH
def old_func():
    return 1
=======
def new_func():
    return 2
>>>>>>>
    """
    blocks = extract_search_replace_blocks(text)
    assert len(blocks) == 1
    assert blocks[0].file_path == "src/sample.py"
    assert "def old_func():" in blocks[0].search_content
    assert "def new_func():" in blocks[0].replace_content


def test_fuzzy_find_and_replace_exact():
    original = "line 1\nline 2\nline 3\n"
    search = "line 2\n"
    replace = "line 2 modified\n"
    ok, result = fuzzy_find_and_replace(original, search, replace)
    assert ok is True
    assert result == "line 1\nline 2 modified\nline 3\n"


def test_fuzzy_find_and_replace_whitespace_tolerance():
    original = "def foo():   \n    x = 1   \n"
    search = "def foo():\n    x = 1\n"
    replace = "def foo():\n    x = 2\n"
    ok, result = fuzzy_find_and_replace(original, search, replace)
    assert ok is True
    assert "x = 2" in result
