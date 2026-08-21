"""Tests for filesystem and terminal tools."""
import pytest
from pathlib import Path
from src.tools.filesystem import ReadFileTool, WriteFileTool, ListDirTool, FindFilesTool, GrepSearchTool
from src.tools.terminal import RunCommandTool
from src.config import get_config


@pytest.mark.asyncio
async def test_read_and_write_file_sandbox(tmp_path):
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
async def test_run_command():
    cmd_tool = RunCommandTool()
    res = await cmd_tool.execute(command="echo 'llmCli teste'")
    assert res.success is True
    assert "llmCli teste" in res.output
