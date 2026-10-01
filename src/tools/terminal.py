"""Terminal and shell execution tool with safety timeouts."""
from __future__ import annotations

import asyncio
import os
import shlex
from pathlib import Path
from typing import Any, Optional

from src.config import get_config
from src.tools.base import BaseTool, ToolResult


class RunCommandTool(BaseTool):
    name = "run_command"
    description = "Executa um comando shell no terminal dentro da raiz do workspace."
    parameters_schema = {
        "type": "object",
        "properties": {
            "command": {"type": "string", "description": "Comando de terminal a ser executado."},
            "timeout_seconds": {"type": "integer", "description": "Tempo limite em segundos (padrão: 60).", "default": 60}
        },
        "required": ["command"]
    }

    # Commands are intentionally limited to common project-development tools.  This
    # is not a replacement for an OS sandbox, but avoids giving an LLM a general
    # purpose shell with access to the user's machine.
    SAFE_EXECUTABLES = {
        "cargo", "cat", "echo", "find", "git", "go", "head", "java", "ls",
        "make", "mypy", "node", "npm", "npx", "php", "pytest", "python",
        "python3", "rg", "ruff", "sed", "tail",
    }
    FORBIDDEN_ARGUMENTS = {
        "-c", "-C", "--command", "--global", "--prefix", "--work-tree", "--git-dir",
        "-exec", "-execdir", "-ok", "-okdir", "--pre",
    }

    def _parse_safe_command(self, command: str) -> tuple[Optional[list[str]], Optional[str]]:
        try:
            args = shlex.split(command, posix=True)
        except ValueError as err:
            return None, f"Comando inválido: {err}"

        if not args:
            return None, "Comando vazio."
        if args[0] not in self.SAFE_EXECUTABLES:
            return None, f"Executável não permitido: {args[0]}."
        if any(
            arg.split("=", 1)[0] in self.FORBIDDEN_ARGUMENTS or arg.startswith("-C/")
            for arg in args[1:]
        ):
            return None, "Argumento não permitido por segurança."

        root = get_config().project_root.resolve()
        for arg in args[1:]:
            # Opções como --output=/path também carregam caminhos após '='.
            path_arg = arg.split("=", 1)[-1] if "=" in arg else arg
            # Reject paths that can escape the workspace. Absolute paths within it
            # remain valid, which is useful for tools that require an explicit path.
            if path_arg.startswith("/"):
                try:
                    Path(path_arg).resolve().relative_to(root)
                except ValueError:
                    return None, f"Caminho fora do workspace não permitido: {arg}"
            elif path_arg == ".." or path_arg.startswith("../") or "/../" in path_arg:
                return None, f"Caminho que sai do workspace não permitido: {arg}"
        return args, None

    async def execute(self, command: str, timeout_seconds: Optional[int] = None, **kwargs: Any) -> ToolResult:
        config = get_config()
        timeout = timeout_seconds or config.security.command_timeout_seconds
        args, error = self._parse_safe_command(command)
        if error:
            return ToolResult(tool_call_id="", name=self.name, success=False, output=f"Comando bloqueado por segurança: {error}")

        try:
            process = await asyncio.create_subprocess_exec(
                *args,
                cwd=str(config.project_root),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=os.environ.copy()
            )

            try:
                stdout_bytes, stderr_bytes = await asyncio.wait_for(process.communicate(), timeout=timeout)
                stdout = stdout_bytes.decode("utf-8", errors="replace").strip()
                stderr = stderr_bytes.decode("utf-8", errors="replace").strip()
                returncode = process.returncode

                output_parts = []
                if stdout:
                    output_parts.append(f"[STDOUT]\n{stdout}")
                if stderr:
                    output_parts.append(f"[STDERR]\n{stderr}")
                if not output_parts:
                    output_parts.append("(sem saída de texto)")

                output_str = f"Código de saída: {returncode}\n" + "\n\n".join(output_parts)
                success = (returncode == 0)
                return ToolResult(tool_call_id="", name=self.name, success=success, output=output_str, metadata={"exit_code": returncode})

            except asyncio.TimeoutError:
                try:
                    process.kill()
                    await process.wait()
                except Exception:
                    pass
                return ToolResult(
                    tool_call_id="",
                    name=self.name,
                    success=False,
                    output=f"Comando abortado: excedeu o tempo limite de {timeout}s."
                )

        except Exception as err:
            return ToolResult(tool_call_id="", name=self.name, success=False, output=f"Falha ao executar comando: {err}")
