"""Tests for filesystem and terminal tools."""

import pytest

from src.config import get_config
from src.tools.filesystem import (
    FindFilesTool,
    GrepSearchTool,
    ListDirTool,
    ReadFileTool,
    WriteFileTool,
)
from src.tools.terminal import RunCommandTool


@pytest.mark.asyncio
async def test_read_and_write_file_sandbox():
    config = get_config()
    write_tool = WriteFileTool()
    read_tool = ReadFileTool()

    test_file = "tests/test_scratch.txt"
    res_write = await write_tool.execute(path=test_file, content="Linha 1\nLinha 2\nLinha 3\n")
    assert res_write.success is True

    res_read = await read_tool.execute(path=test_file, start_line=2, end_line=3)
    assert res_read.success is True
    assert "Linha 2" in res_read.output

    # Limpeza
    target = config.project_root / test_file
    if target.exists():
        target.unlink()


@pytest.mark.asyncio
async def test_security_sandbox_violation():
    read_tool = ReadFileTool()
    res = await read_tool.execute(path="/etc/passwd")
    assert res.success is False
    assert "fora da raiz permitida" in res.output or "negado" in res.output


@pytest.mark.asyncio
async def test_list_dir_tool():
    tool = ListDirTool()
    res = await tool.execute(path="src", max_depth=2)
    assert res.success is True
    assert "main.py" in res.output or "config.py" in res.output


@pytest.mark.asyncio
async def test_grep_search_tool():
    tool = GrepSearchTool()
    res = await tool.execute(query="class Config", path="src")
    assert res.success is True
    assert "config.py" in res.output


@pytest.mark.asyncio
async def test_find_files_tool():
    tool = FindFilesTool()
    res = await tool.execute(pattern="*.py", path="src")
    assert res.success is True
    assert "src/main.py" in res.output


@pytest.mark.asyncio
async def test_run_command_safe_and_blocked():
    cmd_tool = RunCommandTool()
    res = await cmd_tool.execute(command="echo 'llmCli teste'")
    assert res.success is True
    assert "llmCli teste" in res.output

    # Comando perigoso bloqueado
    res_blocked = await cmd_tool.execute(command="rm -rf /")
    assert res_blocked.success is False
    assert "bloqueado por segurança" in res_blocked.output


@pytest.mark.asyncio
async def test_run_command_does_not_invoke_a_shell():
    cmd_tool = RunCommandTool()
    res = await cmd_tool.execute(command="echo 'ok; touch escaped.txt'")
    assert res.success is True
    assert "ok; touch escaped.txt" in res.output
    assert not (get_config().project_root / "escaped.txt").exists()


@pytest.mark.asyncio
async def test_run_command_blocks_workspace_escape_and_dynamic_code():
    cmd_tool = RunCommandTool()
    escaped = await cmd_tool.execute(command="cat /etc/passwd")
    assert escaped.success is False
    assert "bloqueado por segurança" in escaped.output

    dynamic_code = await cmd_tool.execute(command="python3 -c 'print(1)'")
    assert dynamic_code.success is False
    assert "bloqueado por segurança" in dynamic_code.output

    for command in (
        "git -C=/etc status",
        "git -C /etc status",
        "git -C/etc status",
        "cat --output=/etc/passwd",
        "cat --output=../outside.txt",
        "find . -exec echo test ;",
    ):
        result = await cmd_tool.execute(command=command)
        assert result.success is False
        assert "bloqueado por segurança" in result.output
