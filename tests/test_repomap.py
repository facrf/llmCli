"""Tests for repository tree mapping."""
from src.context.repomap import build_repo_map


def test_build_repo_map_contains_core_files():
    tree = build_repo_map()
    assert "src/" in tree
    assert "main.py" in tree
    assert "config.py" in tree
    assert "📁 .git" not in tree
    assert "__pycache__" not in tree

