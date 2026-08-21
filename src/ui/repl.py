"""Interactive REPL loop with prompt_toolkit, slash command dispatcher, and rich UI."""
from __future__ import annotations

import asyncio
import os
from pathlib import Path
from prompt_toolkit import PromptSession
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.history import FileHistory, InMemoryHistory
from prompt_toolkit.styles import Style
from src.config import get_config
from src.core.agent import Agent
from src.providers.registry import ProviderRegistry
from src.providers.scanner import HostScanner
from src.tools.git_ops import create_user_commit, get_git_diff, get_raw_git_diff, undo_last_checkpoint
from src.ui.completer import CliCompleter, resolve_slash_command
from src.ui.console import ask_user_confirmation, console, print_banner, print_diff, print_scan_results, print_status_table



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
        
        # Histórico persistente em ~/.llmcli_history
        history_path = Path.home() / ".llmcli_history"
        try:
            history = FileHistory(str(history_path))
        except Exception:
            history = InMemoryHistory()

        self.prompt_session: PromptSession = PromptSession(
            history=history,
            completer=CliCompleter(),
            style=prompt_style,
            complete_while_typing=True
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
        raw_command = parts[0].lower()
        arg = parts[1].strip() if len(parts) > 1 else ""

        # Resolver comando (autocompletar caso o comando seja parcial e unico)
        command, matches = resolve_slash_command(raw_command, has_arg=bool(arg))

        if not command:
            if matches:
                console.print(f"[yellow]Comando ambíguo '{raw_command}'. Opções possíveis: {', '.join(matches)}[/yellow]")
            else:
                console.print(f"[red]Comando desconhecido: '{raw_command}'. Digite /help para ver os comandos disponíveis.[/red]")
            return True

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

        elif command in ("/scan", "/host", "/discover"):
            target_host = arg or "127.0.0.1"
            console.print(f"[dim]Escaneando host [bold yellow]{target_host}[/bold yellow] em busca de servidores e modelos de LLM...[/dim]")
            scanner = HostScanner(target_host)
            services = await scanner.scan()
            print_scan_results(target_host, services)

            # Se encontrou serviços, atualizar endpoints locais automaticamente
            if services:
                for s in services:
                    if s.provider_type == "ollama":
                        self.config.local_endpoints.ollama = s.base_url
                    elif s.provider_type == "llamacpp":
                        self.config.local_endpoints.llamacpp = s.base_url

                # Se o comando foi /host ou o usuário pediu para conectar, ativar o primeiro modelo encontrado
                if command == "/host" or (len(services) == 1 and services[0].models):
                    chosen_service = services[0]
                    model_to_use = chosen_service.models[0] if chosen_service.models else "default"
                    full_model_name = f"{chosen_service.provider_type}/{model_to_use}"
                    self.agent.set_model(full_model_name)
                    console.print(f"[bold green]✓ Conectado com sucesso! Modelo ativo alterado para:[/bold green] [bold yellow]{full_model_name}[/bold yellow]")
                else:
                    console.print("[dim]Use [bold]/model <provedor>/<modelo>[/bold] para ativar um dos modelos encontrados acima.[/dim]")


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

        elif command == "/commit":
            if not arg:
                raw_diff = await get_raw_git_diff()
                if not raw_diff:
                    console.print("[yellow]Nenhuma alteração Git não commitada encontrada para gerar commit.[/yellow]")
                else:
                    console.print("[dim]Analisando alterações Git e gerando mensagem de commit semântica...[/dim]")
                    prompt = (
                        "Gere uma mensagem de commit curta, concisa e semântica no padrão Conventional Commits (ex: feat: ..., fix: ..., refactor: ...) "
                        "para as seguintes alterações Git. Responda APENAS com a mensagem de commit de uma linha (ou poucas linhas), sem explicações adicionais:\n\n"
                        f"```diff\n{raw_diff[:3000]}\n```"
                    )
                    proposed_msg = (await self.agent.run_prompt(prompt)).strip()
                    if proposed_msg.startswith("```"):
                        lines = [l for l in proposed_msg.splitlines() if not l.startswith("```")]
                        proposed_msg = lines[0] if lines else proposed_msg
                    proposed_msg = proposed_msg.strip("`'\"\n ")
                    console.print(f"\n[bold green]Mensagem sugerida:[/bold green] [bold yellow]{proposed_msg}[/bold yellow]")
                    if not self.config.yolo_mode:
                        choice = ask_user_confirmation("Deseja criar o commit com esta mensagem?")
                        if choice not in ("yes", "yolo"):
                            console.print("[dim]Commit cancelado.[/dim]")
                            return True
                        if choice == "yolo":
                            self.config.yolo_mode = True
                    ok, msg = await create_user_commit(proposed_msg)
                    style = "green" if ok else "red"
                    console.print(f"[{style}]{msg}[/{style}]")
            else:
                ok, msg = await create_user_commit(arg)
                style = "green" if ok else "red"
                console.print(f"[{style}]{msg}[/{style}]")

        elif command == "/review":
            raw_diff = await get_raw_git_diff()
            if not raw_diff:
                console.print("[yellow]Nenhuma alteração Git detectada para Code Review.[/yellow]")
            else:
                console.print("[dim]Executando Code Review nas alterações Git pendentes...[/dim]")
                review_prompt = (
                    "Faça um Code Review técnico detalhado e construtivo das alterações Git abaixo.\n"
                    "Avalie:\n"
                    "1. 🐛 Possíveis bugs, regressões ou edge cases não tratados\n"
                    "2. 🔒 Segurança e integridade de dados\n"
                    "3. ⚡ Otimizações de desempenho e boas práticas de código\n"
                    "4. 💡 Sugestões de melhoria\n\n"
                    f"```diff\n{raw_diff[:5000]}\n```"
                )
                await self.agent.run_prompt(review_prompt)

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

        elif command == "/test":
            test_cmd = f"pytest {arg}".strip() if arg else "pytest"
            console.print(f"[dim]Executando suíte de testes: [bold yellow]{test_cmd}[/bold yellow]...[/dim]")
            res = await self.agent.tools["run_command"].execute(command=test_cmd)
            console.print(res.output)
            if not res.success:
                console.print("\n[bold red]✗ Falha detectada nos testes.[/bold red]")
                should_fix = self.config.yolo_mode
                if not self.config.yolo_mode:
                    choice = ask_user_confirmation("Deseja que a IA analise o erro e tente corrigir o código?")
                    if choice in ("yes", "yolo"):
                        if choice == "yolo":
                            self.config.yolo_mode = True
                        should_fix = True
                if should_fix:
                    await self.agent.run_prompt(
                        f"Os testes falharam ao executar `{test_cmd}` com a seguinte saída:\n```\n{res.output[-2000:]}\n```\n"
                        "Por favor, analise a stack trace e corrija o código para fazer os testes passarem."
                    )

        elif command == "/clear":
            self.agent.session.clear_history()
            console.print("[green]Histórico da conversa limpo com sucesso.[/green]")

        elif command == "/reset":
            self.agent.session.clear_history()
            self.agent.session.file_tracker.clear()
            console.print("[green]Sessão reiniciada (histórico e arquivos de contexto limpos).[/green]")

        elif command == "/compact":
            if not self.agent.session.messages:
                console.print("[dim]Histórico da conversa está vazio, nada a compactar.[/dim]")
            else:
                console.print("[dim]Compactando histórico da conversa com resumo consolidado...[/dim]")
                history_text = "\n".join(f"{m.role}: {m.content[:200]}" for m in self.agent.session.messages)
                compact_prompt = (
                    "Resuma de forma concisa o histórico da conversa a seguir, preservando todas as decisões técnicas importantes, arquivos modificados e requisitos acordados:\n\n"
                    f"{history_text[:4000]}"
                )
                summary = await self.agent.run_prompt(compact_prompt)
                self.agent.session.compact_history(summary)
                tokens = self.agent.session.estimate_tokens()
                console.print(f"[bold green]✓ Histórico compactado com sucesso![/bold green] Estimativa atual: [bold cyan]~{tokens} tokens[/bold cyan]")

        elif command in ("/temp", "/temperature"):
            if not arg:
                console.print(f"Temperatura atual: [bold yellow]{self.config.temperature}[/bold yellow] (padrão: 0.2)")
                console.print("[dim]Use '/temp <valor>' (ex: /temp 0.0 para determinístico, /temp 0.7 para criativo)[/dim]")
            else:
                try:
                    val = float(arg)
                    if not (0.0 <= val <= 2.0):
                        console.print("[red]Temperatura deve estar entre 0.0 e 2.0.[/red]")
                    else:
                        self.config.temperature = val
                        console.print(f"[bold green]✓ Temperatura alterada para:[/bold green] [bold yellow]{val}[/bold yellow]")
                except ValueError:
                    console.print("[red]Valor de temperatura inválido. Use um número float (ex: /temp 0.2).[/red]")

        elif command == "/system":
            if not arg:
                current = self.agent.session.custom_system_prompt or "(Padrão oficial do llmCli)"
                console.print(f"[bold cyan]System Prompt Ativo:[/bold cyan]\n{current}")
                console.print("[dim]Use '/system <texto>' para alterar ou '/system reset' para voltar ao padrão.[/dim]")
            elif arg.lower() == "reset":
                self.agent.session.reset_system_prompt()
                console.print("[green]System prompt redefinido para o padrão com sucesso.[/green]")
            else:
                self.agent.session.set_custom_system_prompt(arg)
                console.print("[bold green]✓ System prompt personalizado configurado para esta sessão.[/bold green]")

        elif command == "/paste":
            console.print("[bold cyan]📋 Modo Multilinha ativado.[/bold cyan] [dim]Digite ou cole seu código/texto. Digite ':done' em uma linha para enviar ou ':cancel' para abortar.[/dim]")
            lines = []
            while True:
                line = await self.prompt_session.prompt_async("... ")
                if line.strip() == ":done":
                    break
                elif line.strip() == ":cancel":
                    console.print("[dim]Modo multilinha cancelado.[/dim]")
                    return True
                lines.append(line)
            full_text = "\n".join(lines).strip()
            if full_text:
                await self.agent.run_prompt(full_text)

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
  [bold yellow]/scan <ip/host>[/bold yellow]   - Escaneia o IP e detecta automaticamente servidores e modelos ativos
  [bold yellow]/host <ip/host>[/bold yellow]   - Conecta ao host e define como servidor local ativo (ex: /host 192.168.0.11)
  [bold yellow]/model <nome>[/bold yellow]     - Troca o modelo de LLM (ex: /model llamacpp/default, /model gemini/gemini-2.5-flash)
  [bold yellow]/models[/bold yellow]           - Exibe lista e status de todos os provedores locais e na nuvem

  [bold yellow]/add <caminho>[/bold yellow]    - Adiciona arquivo ou diretório ao contexto da IA
  [bold yellow]/drop <caminho>[/bold yellow]   - Remove arquivo do contexto
  [bold yellow]/files[/bold yellow]            - Lista arquivos carregados no contexto atual
  [bold yellow]/diff[/bold yellow]             - Exibe alterações Git não commitadas
  [bold yellow]/commit [msg][/bold yellow]      - Gera commit semântico via IA ou cria commit direto
  [bold yellow]/review[/bold yellow]           - Executa Code Review das alterações Git pendentes
  [bold yellow]/undo[/bold yellow]             - Reverte a última modificação ou commit gerado pela IA
  [bold yellow]/test [args][/bold yellow]      - Roda testes (pytest) e sugere correção automática se falhar
  [bold yellow]/run <comando>[/bold yellow]   - Executa comando no terminal da raiz do projeto

  [bold yellow]/paste[/bold yellow]            - Inicia modo multilinha para colar blocos de código
  [bold yellow]/compact[/bold yellow]          - Compacta o histórico da conversa gerando resumo consolidado
  [bold yellow]/temp [valor][/bold yellow]     - Exibe ou altera a temperatura do modelo (ex: /temp 0.2)
  [bold yellow]/system [txt][/bold yellow]     - Exibe, altera ou redefine o system prompt (ex: /system reset)
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
