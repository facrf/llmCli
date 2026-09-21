"""A constrained project-test tool for the multi-agent tester role."""
from __future__ import annotations

import asyncio
from typing import Any

from src.config import get_config
from src.tools.base import BaseTool, ToolResult


class RunProjectTestsTool(BaseTool):
    """Runs pytest without accepting arbitrary shell input or arguments."""

    name = "run_project_tests"
    description = "Executa a suíte pytest do projeto com parâmetros seguros e predefinidos."
    parameters_schema = {"type": "object", "properties": {}, "required": []}
    MAX_OUTPUT_CHARS = 20_000

    async def execute(self, **kwargs: Any) -> ToolResult:
        config = get_config()
        venv_pytest = config.project_root / ".venv" / "bin" / "pytest"
        executable = str(venv_pytest) if venv_pytest.exists() else "pytest"
        try:
            process = await asyncio.create_subprocess_exec(
                executable,
                "-q",
                cwd=str(config.project_root),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), timeout=config.security.command_timeout_seconds
            )
        except asyncio.TimeoutError:
            process.kill()
            await process.wait()
            return ToolResult("", self.name, False, "Testes excederam o tempo limite configurado.")
        except OSError as exc:
            return ToolResult("", self.name, False, f"Não foi possível iniciar pytest: {exc}")

        output = "\n".join(
            part for part in (
                stdout.decode("utf-8", errors="replace").strip(),
                stderr.decode("utf-8", errors="replace").strip(),
            ) if part
        )
        if len(output) > self.MAX_OUTPUT_CHARS:
            output = output[:self.MAX_OUTPUT_CHARS] + "\n... [saída truncada]"
        return ToolResult(
            "", self.name, process.returncode == 0, output or "pytest terminou sem saída.",
            {"exit_code": process.returncode},
        )
