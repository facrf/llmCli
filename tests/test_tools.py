"""Tests for filesystem and terminal tools."""
import pytest
from pathlib import Path
from src.tools.filesystem import ReadFileTool, WriteFileTool, ListDirTool, FindFilesTool, GrepSearchTool
from src.tools.terminal import RunCommandTool
from src.config import get_config


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
