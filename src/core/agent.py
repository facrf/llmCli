"""Main autonomous agent loop with hybrid function calling and search/replace support."""
from __future__ import annotations

import asyncio
from typing import Any, Callable, Dict, List, Optional
from rich.console import Console
from src.config import get_config
from src.core.diff_applier import apply_search_replace_block, extract_search_replace_blocks, extract_json_tool_calls

from src.core.session import Session
from src.providers.base import LLMProvider, StreamChunk
from src.providers.registry import ProviderRegistry
from src.tools.base import BaseTool, ToolCall, ToolDefinition, ToolResult
from src.tools.filesystem import FindFilesTool, GrepSearchTool, ListDirTool, ReadFileTool, WriteFileTool
from src.tools.git_ops import create_checkpoint_commit
from src.tools.terminal import RunCommandTool
from src.ui.console import ask_user_confirmation, console, print_diff, print_tool_execution, print_tool_result


class Agent:
    def __init__(self, session: Optional[Session] = None) -> None:
        self.config = get_config()
        self.session = session or Session()
        self.provider: LLMProvider = ProviderRegistry.create_provider()
        
        # Registrar ferramentas disponíveis
        self.tools: Dict[str, BaseTool] = {
            "read_file": ReadFileTool(),
            "write_file": WriteFileTool(),
            "list_dir": ListDirTool(),
            "grep_search": GrepSearchTool(),
            "find_files": FindFilesTool(),
            "run_command": RunCommandTool()
        }

    def set_model(self, model_name: str) -> None:
        self.config.active_model = model_name
        self.provider = ProviderRegistry.create_provider(model_name)

    def get_tool_definitions(self) -> List[ToolDefinition]:
        return [tool.get_definition() for tool in self.tools.values()]

    async def execute_tool_with_permission(self, tool_name: str, kwargs: Dict[str, Any], tool_call_id: str = "") -> ToolResult:
        tool = self.tools.get(tool_name)
        if not tool:
            return ToolResult(tool_call_id=tool_call_id, name=tool_name, success=False, output=f"Ferramenta desconhecida: {tool_name}")

        args_str = ", ".join(f"{k}={repr(v)[:50]}" for k, v in kwargs.items())

        # Se não estiver no modo YOLO, solicitar permissão para ações que alteram estado
        if not self.config.yolo_mode and tool_name in ("write_file", "run_command"):
            confirm_msg = f"Deseja executar a ferramenta '{tool_name}' com os argumentos: {args_str}?"
            choice = ask_user_confirmation(confirm_msg)
            if choice == "abort":
                return ToolResult(tool_call_id=tool_call_id, name=tool_name, success=False, output="Ação cancelada pelo usuário.")
            elif choice == "no":
                return ToolResult(tool_call_id=tool_call_id, name=tool_name, success=False, output="Ação rejeitada pelo usuário.")
            elif choice == "yolo":
                self.config.yolo_mode = True
                console.print("[bold red]⚡ Modo YOLO ativado para esta sessão![/bold red]")

        print_tool_execution(tool_name, args_str, is_yolo=self.config.yolo_mode)
        result = await tool.execute(**kwargs)
        result.tool_call_id = tool_call_id

        # Se modificou arquivo, criar checkpoint de git
        if tool_name == "write_file" and result.success:
            commit_hash = await create_checkpoint_commit(f"write_file em {kwargs.get('path')}")
            if commit_hash:
                result.output += f"\n[Git Checkpoint: {commit_hash}]"

        print_tool_result(tool_name, result.success, result.output)
        return result

    async def run_prompt(self, user_prompt: str, max_iterations: int = 8) -> str:
        """Executa um prompt do usuário através do loop de raciocínio e execução de ferramentas."""
        self.session.add_user_message(user_prompt)

        iteration = 0
        final_assistant_text = ""

        while iteration < max_iterations:
            iteration += 1
            messages = self.session.get_full_messages()
            tools_defs = self.get_tool_definitions()

            console.print(f"\n[dim]Pensando com [bold cyan]{self.config.active_model}[/bold cyan]...[/dim]")

            stream_text = ""
            collected_tool_calls: List[ToolCall] = []
            has_error = False

            try:
                async for chunk in self.provider.chat_stream(
                    messages=messages,
                    tools=tools_defs,
                    temperature=self.config.temperature,
                    max_tokens=self.config.max_tokens
                ):
                    if chunk.error:
                        console.print(f"\n[bold red]Erro da LLM:[/bold red] {chunk.error}")
                        has_error = True
                        break

                    if chunk.delta_content:
                        console.print(chunk.delta_content, end="")
                        stream_text += chunk.delta_content

                    if chunk.tool_calls:
                        collected_tool_calls.extend(chunk.tool_calls)

            except Exception as e:
                console.print(f"\n[bold red]Exceção no stream:[/bold red] {e}")
                has_error = True

            console.print()  # Quebra de linha final

            if has_error:
                backup_model = ProviderRegistry.find_backup_model(self.config.active_model)
                if backup_model:
                    console.print(f"[dim]💡 Dica: Provedor alternativo disponível: [bold green]{backup_model}[/bold green]. Use [bold]/model {backup_model}[/bold] para alternar.[/dim]\n")
                break

            final_assistant_text = stream_text

            # 1. Verificar se há blocos SEARCH/REPLACE no texto gerado (para modelos locais ou sem function calling)
            search_replace_blocks = extract_search_replace_blocks(stream_text)

            # Executar blocos de modificação se houver
            sr_applied = False
            for block in search_replace_blocks:
                sr_applied = True
                if not self.config.yolo_mode:
                    choice = ask_user_confirmation(f"Aplicar modificação no arquivo '{block.file_path}'?")
                    if choice == "abort":
                        break
                    elif choice == "yolo":
                        self.config.yolo_mode = True
                        console.print("[bold red]⚡ Modo YOLO ativado![/bold red]")
                    elif choice == "no":
                        continue

                ok, msg, diff = apply_search_replace_block(block)
                if diff:
                    print_diff(diff, block.file_path)
                print_tool_result("diff_applier", ok, msg)

                if ok:
                    await create_checkpoint_commit(f"patch em {block.file_path}")

            # 2. Extrair e mesclar tool calls de blocos JSON no texto (modelos locais)
            parsed_json_calls = extract_json_tool_calls(stream_text)
            if parsed_json_calls:
                collected_tool_calls.extend(parsed_json_calls)

            # 3. Executar tool calls se houver
            if collected_tool_calls:
                self.session.add_assistant_message(stream_text, tool_calls=collected_tool_calls)


                for tc in collected_tool_calls:
                    res = await self.execute_tool_with_permission(
                        tool_name=tc.name,
                        kwargs=tc.arguments,
                        tool_call_id=tc.id
                    )
                    self.session.add_tool_result(
                        tool_call_id=tc.id,
                        name=tc.name,
                        output=res.output
                    )

                # Continuar o loop para a LLM processar a saída das ferramentas
                continue

            # Se não houver chamadas de ferramentas e nem blocos a aplicar, finaliza o turno
            self.session.add_assistant_message(stream_text)
            break

        return final_assistant_text
