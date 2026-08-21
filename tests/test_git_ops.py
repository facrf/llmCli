"""Tests for Git operations, diffs, and checkpoints."""
import pytest
from src.tools.git_ops import is_git_repo, get_git_diff, get_git_status


@pytest.mark.asyncio
async def test_git_repo_detection():
    assert await is_git_repo() is True


@pytest.mark.asyncio
async def test_get_git_diff():
    diff = await get_git_diff()
    assert isinstance(diff, str)


@pytest.mark.asyncio
async def test_get_git_status():
    status = await get_git_status()
    assert isinstance(status, str)
