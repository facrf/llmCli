"""Terminal and shell execution tool with safety timeouts."""
from __future__ import annotations

import asyncio
import os
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

    async def execute(self, command: str, timeout_seconds: Optional[int] = None, **kwargs: Any) -> ToolResult:
        config = get_config()
        timeout = timeout_seconds or config.security.command_timeout_seconds

        # Proibir comandos claramente perigosos se não for intencional
        cmd_stripped = command.strip()
        if cmd_stripped.startswith("rm -rf /") or cmd_stripped.startswith("mkfs") or ":(){ :|:& };:" in cmd_stripped:
            return ToolResult(tool_call_id="", name=self.name, success=False, output="Comando bloqueado por segurança (risco crítico ao sistema).")

        try:
            process = await asyncio.create_subprocess_shell(
                command,
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
