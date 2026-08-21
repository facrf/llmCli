"""Interactive REPL loop with prompt_toolkit, slash command dispatcher, and rich UI."""
from __future__ import annotations

import asyncio
from prompt_toolkit import PromptSession
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.styles import Style
from src.config import get_config
from src.core.agent import Agent
from src.providers.registry import ProviderRegistry
from src.tools.git_ops import get_git_diff, undo_last_checkpoint
from src.ui.completer import CliCompleter
from src.ui.console import console, print_banner, print_diff, print_status_table


prompt_style = Style.from_dict({
    "prompt.name": "ansicyan bold",
    "prompt.model": "ansiyellow",
    "prompt.yolo_on": "ansired bold",
    "prompt.yolo_off": "ansigreen",
    "prompt.arrow": "ansicyan bold"
})


class ReplSession:
    def __init__(self, agent: Agent) -> None:
        self.agent = agent
        self.config = get_config()
        self.prompt_session: PromptSession = PromptSession(
            history=InMemoryHistory(),
            completer=CliCompleter(),
            style=prompt_style
        )

    def _get_prompt_html(self) -> HTML:
        model = self.config.active_model.split("/")[-1]
        if self.config.yolo_mode:
            yolo_tag = '<style class="prompt.yolo_on">⚡ YOLO: ON</style>'
        else:
            yolo_tag = '<style class="prompt.yolo_off">🛡️ YOLO: OFF</style>'

        files_count = len(self.agent.session.file_tracker.tracked_files)
        files_tag = f"files:{files_count}" if files_count > 0 else ""

        info_parts = [model, yolo_tag]
        if files_tag:
            info_parts.append(files_tag)

        info_str = " | ".join(info_parts)
        return HTML(f'<style class="prompt.name">llmCli</style> [{info_str}] <style class="prompt.arrow">❯</style> ')

    async def handle_slash_command(self, cmd_line: str) -> bool:
        """Processa comandos iniciados com '/'. Retorna True para continuar o loop ou False para sair."""
        parts = cmd_line.strip().split(maxsplit=1)
        command = parts[0].lower()
        arg = parts[1].strip() if len(parts) > 1 else ""

        if command in ("/exit", "/quit", "/q"):
            console.print("[cyan]Encerrando llmCli. Até logo![/cyan]")
            return False

        elif command == "/yolo":
            self.config.yolo_mode = not self.config.yolo_mode
            if self.config.yolo_mode:
                console.print("[bold red]⚡ MODO YOLO ATIVADO: Execuções automáticas de comandos e edições sem confirmação![/bold red]")
            else:
                console.print("[bold green]🛡️ MODO YOLO DESATIVADO: Confirmação manual exigida para ações destrutivas.[/bold green]")

        elif command == "/model":
            if not arg:
                console.print(f"Modelo atual: [bold yellow]{self.config.active_model}[/bold yellow]")
                console.print("[dim]Use '/model <nome>' para alterar (ex: /model llamacpp/default, /model gemini/gemini-2.5-flash)[/dim]")
            else:
                self.agent.set_model(arg)
                console.print(f"[bold green]✓ Modelo ativo alterado para:[/bold green] [bold yellow]{arg}[/bold yellow]")

        elif command == "/models":
            console.print("[dim]Verificando status de conectividade dos provedores...[/dim]")
            status = await ProviderRegistry.get_status_overview()
            print_status_table(status)

        elif command == "/add":
            if not arg:
                console.print("[yellow]Especifique o arquivo ou diretório: /add <caminho>[/yellow]")
            else:
                ok, msg = self.agent.session.file_tracker.add_file(arg)
                style = "green" if ok else "red"
                console.print(f"[{style}]{msg}[/{style}]")

        elif command == "/drop":
            if not arg:
                console.print("[yellow]Especifique o arquivo a remover: /drop <caminho>[/yellow]")
            else:
                if self.agent.session.file_tracker.remove_file(arg):
                    console.print(f"[green]Arquivo '{arg}' removido do contexto.[/green]")
                else:
                    console.print(f"[red]Arquivo '{arg}' não constava no contexto.[/red]")

        elif command == "/files":
            files = self.agent.session.file_tracker.list_files()
            if not files:
                console.print("[dim]Nenhum arquivo adicionado ao contexto no momento. Use /add <arquivo> para incluir.[/dim]")
            else:
                console.print(f"[bold cyan]Arquivos no Contexto ({len(files)}):[/bold cyan]")
                for f in files:
                    console.print(f"  📄 [yellow]{f}[/yellow]")

        elif command == "/diff":
            diff_text = await get_git_diff()
            print_diff(diff_text, "Modificações Git Pendentes")

        elif command == "/undo":
            ok, msg = await undo_last_checkpoint()
            style = "green" if ok else "red"
            console.print(f"[{style}]{msg}[/{style}]")

        elif command == "/run":
            if not arg:
                console.print("[yellow]Especifique o comando a executar: /run <comando>[/yellow]")
            else:
                res = await self.agent.tools["run_command"].execute(command=arg)
                console.print(res.output)

        elif command == "/clear":
            self.agent.session.clear_history()
            console.print("[green]Histórico da conversa limpo com sucesso.[/green]")

        elif command == "/reset":
            self.agent.session.clear_history()
            self.agent.session.file_tracker.clear()
            console.print("[green]Sessão reiniciada (histórico e arquivos de contexto limpos).[/green]")

        elif command == "/tokens":
            tokens = self.agent.session.estimate_tokens()
            console.print(f"Estimativa atual de contexto: [bold cyan]~{tokens} tokens[/bold cyan]")

        elif command == "/help":
            self._print_help()

        else:
            console.print(f"[red]Comando desconhecido: '{command}'. Digite /help para ver os comandos disponíveis.[/red]")

        return True

    def _print_help(self) -> None:
        console.print("""
[bold cyan]Comandos Disponíveis no llmCli:[/bold cyan]
  [bold yellow]/yolo[/bold yellow]             - Alterna o modo YOLO (execução autônoma total sem pedir confirmação)
  [bold yellow]/model <nome>[/bold yellow]     - Troca o modelo de LLM (ex: /model llamacpp/default, /model gemini/gemini-2.5-flash)
  [bold yellow]/models[/bold yellow]           - Exibe lista e status de todos os provedores locais e na nuvem
  [bold yellow]/add <caminho>[/bold yellow]    - Adiciona arquivo ou diretório ao contexto da IA
  [bold yellow]/drop <caminho>[/bold yellow]   - Remove arquivo do contexto
  [bold yellow]/files[/bold yellow]            - Lista arquivos carregados no contexto atual
  [bold yellow]/diff[/bold yellow]             - Exibe alterações Git não commitadas
  [bold yellow]/undo[/bold yellow]             - Reverte a última modificação ou commit gerado pela IA
  [bold yellow]/run <comando>[/bold yellow]   - Executa comando no terminal da raiz do projeto
  [bold yellow]/clear[/bold yellow]            - Limpa o histórico de mensagens da conversa
  [bold yellow]/reset[/bold yellow]            - Limpa o histórico e esvazia o contexto de arquivos
  [bold yellow]/tokens[/bold yellow]           - Exibe estimativa de tokens do contexto
  [bold yellow]/help[/bold yellow]             - Mostra este menu de ajuda
  [bold yellow]/exit, /quit[/bold yellow]      - Sai do programa
        """)

    async def start(self) -> None:
        print_banner(self.config.active_model, self.config.yolo_mode)

        while True:
            try:
                user_input = await self.prompt_session.prompt_async(self._get_prompt_html())
                user_input = user_input.strip()

                if not user_input:
                    continue

                if user_input.startswith("/"):
                    should_continue = await self.handle_slash_command(user_input)
                    if not should_continue:
                        break
                    continue

                # Processar prompt na IA
                await self.agent.run_prompt(user_input)

            except (KeyboardInterrupt, asyncio.CancelledError):
                console.print("\n[dim](Pressione /exit para sair ou Ctrl+D)[/dim]")
                continue
            except EOFError:
                console.print("\n[cyan]Até logo![/cyan]")
                break
