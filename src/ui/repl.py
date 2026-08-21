"""Interactive REPL loop with prompt_toolkit, slash command dispatcher, and rich UI."""
from __future__ import annotations

import asyncio
import os
from pathlib import Path
from prompt_toolkit import PromptSession
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.history import FileHistory, InMemoryHistory
from prompt_toolkit.styles import Style
from src.config import get_config, get_preferences
from src.core.agent import Agent
from src.core.exporter import SessionExporter
from src.core.todo_manager import TodoManager
from src.i18n import SUPPORTED_LANGUAGES, get_active_language, set_active_language, t
from src.providers.registry import ProviderRegistry
from src.providers.scanner import HostScanner
from src.tools.git_ops import create_user_commit, get_git_diff, get_raw_git_diff, undo_last_checkpoint
from src.ui.completer import CliCompleter, resolve_slash_command
from src.ui.console import ask_user_confirmation, console, print_banner, print_diff, print_scan_results, print_status_table
from rich.panel import Panel
from rich.syntax import Syntax


prompt_style = Style.from_dict({
    "prompt.name": "ansicyan bold",
    "prompt.model": "ansiyellow",
    "prompt.yolo_on": "ansired bold",
    "prompt.yolo_off": "ansigreen",
    "prompt.arch": "ansimagenta bold",
    "prompt.arrow": "ansicyan bold"
})


class ReplSession:
    def __init__(self, agent: Agent) -> None:
        self.agent = agent
        self.config = get_config()
        self.todo_manager = TodoManager()
        
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

        info_parts = [model]

        if self.config.architect_mode:
            arch_short = self.config.architect_model.split("/")[-1]
            info_parts.append(f'<style class="prompt.arch">🏛️ ARCH: {arch_short}</style>')

        info_parts.append(yolo_tag)

        files_count = len(self.agent.session.file_tracker.tracked_files)
        if files_count > 0:
            info_parts.append(f"files:{files_count}")

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
            prefs = get_preferences()
            prefs.set_model_pref(self.config.active_model, "yolo_mode", self.config.yolo_mode)
            prefs.set_global_pref("yolo_mode", self.config.yolo_mode)
            if self.config.yolo_mode:
                console.print(f"[bold red]⚡ MODO YOLO ATIVADO para [yellow]{self.config.active_model}[/yellow] (preferência salva)![/bold red]")
            else:
                console.print(f"[bold green]🛡️ MODO YOLO DESATIVADO para [yellow]{self.config.active_model}[/yellow] (preferência salva).[/bold green]")

        elif command in ("/architect", "/arch"):
            prefs = get_preferences()
            if not arg:
                self.config.architect_mode = not self.config.architect_mode
                prefs.set_global_pref("architect_mode", self.config.architect_mode)
                if self.config.architect_mode:
                    console.print(f"[bold magenta]🏛️ MODO ARQUITETO ATIVADO:[/bold magenta] Arquiteto: [bold yellow]{self.config.architect_model}[/bold yellow] | Editor: [bold cyan]{self.config.active_model}[/bold cyan]")
                else:
                    console.print("[bold green]🛡️ MODO ARQUITETO DESATIVADO: Usando modelo único padrão.[/bold green]")
            elif arg.lower() in ("off", "disable", "desativar", "false"):
                self.config.architect_mode = False
                prefs.set_global_pref("architect_mode", False)
                console.print("[bold green]🛡️ MODO ARQUITETO DESATIVADO.[/bold green]")
            else:
                self.config.architect_mode = True
                self.config.architect_model = arg
                prefs.set_global_pref("architect_mode", True)
                prefs.set_global_pref("architect_model", arg)
                console.print(f"[bold magenta]🏛️ MODO ARQUITETO ATIVADO:[/bold magenta] Arquiteto: [bold yellow]{arg}[/bold yellow] | Editor: [bold cyan]{self.config.active_model}[/bold cyan]")

        elif command in ("/lang", "/language"):
            prefs = get_preferences()
            if not arg:
                current_code = get_active_language()
                info = SUPPORTED_LANGUAGES.get(current_code, {"name": current_code, "flag": "🌐"})
                console.print(f"[bold cyan]{t('lang_current', flag=info['flag'], name=info['name'], code=current_code)}[/bold cyan]")
                console.print("\n[dim]Idiomas suportados / Supported languages:[/dim]")
                for code, item in SUPPORTED_LANGUAGES.items():
                    current_marker = " [bold green]✓[/bold green]" if code == current_code else ""
                    console.print(f"  {item['flag']} [bold yellow]{code}[/bold yellow] - {item['name']}{current_marker}")
                console.print("  🌐 [bold yellow]auto[/bold yellow] - Detecção automática (SO / OS locale)")
                console.print("\n[dim]Use '/lang <código>' (ex: /lang en, /lang pt, /lang es, /lang de, /lang fr, /lang zh, /lang ru, /lang hi, /lang auto)[/dim]")
            else:
                resolved = set_active_language(arg)
                prefs.set_global_pref("language", resolved)
                self.config.language = resolved
                info = SUPPORTED_LANGUAGES.get(resolved, {"name": resolved, "flag": "🌐"})
                console.print(f"[bold green]{t('lang_changed', flag=info['flag'], name=info['name'], code=resolved)}[/bold green]")

        elif command == "/model":
            if not arg:
                console.print(f"Modelo atual: [bold yellow]{self.config.active_model}[/bold yellow] (Temp: {self.config.temperature})")
                console.print("[dim]Use '/model <nome>' para alterar (ex: /model llamacpp/default, /model gemini/gemini-2.5-flash, /model gpt/codex)[/dim]")
            else:
                self.agent.set_model(arg)
                yolo_desc = "[bold red]⚡ YOLO: ON[/bold red]" if self.config.yolo_mode else "[bold green]🛡️ YOLO: OFF[/bold green]"
                console.print(f"[bold green]✓ Modelo ativo alterado para:[/bold green] [bold yellow]{arg}[/bold yellow] [dim]({yolo_desc} | Temp: {self.config.temperature})[/dim]")

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
            if arg.lower() in ("prefs", "preferences", "config"):
                get_preferences().reset()
                self.config.yolo_mode = False
                self.config.temperature = 0.2
                console.print("[bold green]✓ Todas as preferências salvas (globais e por LLM) foram redefinidas para o padrão.[/bold green]")
            elif arg.lower() == "all":
                self.agent.session.clear_history()
                self.agent.session.file_tracker.clear()
                get_preferences().reset()
                self.config.yolo_mode = False
                self.config.temperature = 0.2
                console.print("[bold green]✓ Sessão e preferências de usuário totalmente reiniciadas para o padrão.[/bold green]")
            else:
                self.agent.session.clear_history()
                self.agent.session.file_tracker.clear()
                console.print("[green]Sessão reiniciada (histórico e arquivos limpos).[/green] [dim](Use '/reset prefs' para redefinir preferências salvas do usuário)[/dim]")

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
                console.print(f"Temperatura atual para [yellow]{self.config.active_model}[/yellow]: [bold yellow]{self.config.temperature}[/bold yellow] (padrão: 0.2)")
                console.print("[dim]Use '/temp <valor>' (ex: /temp 0.0 para determinístico, /temp 0.7 para criativo)[/dim]")
            else:
                try:
                    val = float(arg)
                    if not (0.0 <= val <= 2.0):
                        console.print("[red]Temperatura deve estar entre 0.0 e 2.0.[/red]")
                    else:
                        self.config.temperature = val
                        prefs = get_preferences()
                        prefs.set_model_pref(self.config.active_model, "temperature", val)
                        prefs.set_global_pref("temperature", val)
                        console.print(f"[bold green]✓ Temperatura para [yellow]{self.config.active_model}[/yellow] alterada para:[/bold green] [bold yellow]{val}[/bold yellow] (preferência salva)")
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

        elif command == "/index":
            console.print("[dim]Indexando base de código para busca semântica...[/dim]")
            count = self.agent.indexer.index_codebase()
            console.print(f"[bold green]✓ Base de código indexada com sucesso:[/bold green] [bold yellow]{count}[/bold yellow] blocos de código mapeados.")

        elif command == "/search":
            if not arg:
                console.print("[dim]Use '/search <termo/conceito/função>' para buscar trechos no código indexado.[/dim]")
            else:
                results = self.agent.indexer.search(arg, top_k=5)
                if not results:
                    console.print(f"[yellow]Nenhum resultado relevante encontrado para:[/yellow] '{arg}'")
                else:
                    console.print(f"[bold cyan]Resultados da busca semântica para '{arg}':[/bold cyan]")
                    for r in results:
                        lang = "python" if r.chunk.file_path.endswith(".py") else "text"
                        console.print(Panel(
                            Syntax(r.chunk.content, lang, line_numbers=True, start_line=r.chunk.start_line),
                            title=f"{r.chunk.file_path} | {r.chunk.symbol_type}: {r.chunk.symbol_name} (Score: {r.score:.2f})",
                            border_style="cyan"
                        ))

        elif command == "/web":
            if not arg:
                console.print("[dim]Use '/web <pesquisa>' para pesquisar na web via DuckDuckGo/Tavily.[/dim]")
            else:
                tool = self.agent.tools.get("web_search")
                if tool:
                    console.print(f"[dim]Pesquisando na web: '{arg}'...[/dim]")
                    res = await tool.execute(query=arg)
                    console.print(res.output)

        elif command in ("/gentest", "/gentests", "/test-for"):
            if not arg:
                console.print("[dim]Use '/gentest <caminho_do_arquivo>' para gerar testes unitários automáticos com pytest (ex: /gentest src/config.py).[/dim]")
            else:
                target = (self.config.project_root / arg).resolve()
                if not target.exists():
                    console.print(f"[red]Arquivo '{arg}' não encontrado.[/red]")
                else:
                    from src.tools.test_generator import get_test_prompt_for_file
                    prompt = get_test_prompt_for_file(target, self.config.project_root)
                    console.print(f"[bold cyan]Gerando testes unitários completos com pytest para [yellow]{arg}[/yellow]...[/bold cyan]")
                    await self.agent.run_prompt(prompt)

        elif command == "/todo":
            if not arg:
                console.print(self.todo_manager.format_checklist())
            elif arg.startswith("add "):
                item = self.todo_manager.add_item(arg[4:])
                console.print(f"[green]✓ Tarefa #{item.id} adicionada:[/green] {item.text}")
            elif arg.startswith("check ") or arg.startswith("done "):
                try:
                    tid = int(arg.split()[1])
                    if self.todo_manager.check_item(tid):
                        console.print(f"[bold green]✓ Tarefa #{tid} marcada como concluída![/bold green]")
                    else:
                        console.print(f"[red]Tarefa #{tid} não encontrada.[/red]")
                except Exception:
                    console.print("[red]Uso: /todo check <id>[/red]")
            elif arg == "clear":
                self.todo_manager.clear()
                console.print("[green]✓ Lista de tarefas limpa com sucesso.[/green]")
            else:
                console.print("[dim]Uso: /todo, /todo add <tarefa>, /todo check <id>, /todo clear[/dim]")

        elif command == "/plan":
            if not arg:
                console.print("[dim]Use '/plan <objetivo>' para planejar uma feature e gerar tarefas automáticas no /todo.[/dim]")
            else:
                plan_prompt = f"Crie um plano técnico detalhado passo a passo com checklist `- [ ]` para implementar o seguinte objetivo no projeto:\n\n{arg}"
                resp = await self.agent.run_prompt(plan_prompt)
                added = self.todo_manager.parse_plan(resp)
                if added > 0:
                    console.print(f"\n[bold green]✓ {added} tarefas extraídas automaticamente para o checklist /todo![/bold green]")

        elif command == "/export":
            exporter = SessionExporter(self.agent.session, self.config.project_root)
            fmt = "md"
            target_path = None
            if arg:
                parts_exp = arg.split(maxsplit=1)
                first_token = parts_exp[0].lower()
                if first_token in ("html", "htm"):
                    fmt = "html"
                    if len(parts_exp) > 1:
                        target_path = Path(parts_exp[1])
                elif first_token in ("md", "markdown"):
                    fmt = "md"
                    if len(parts_exp) > 1:
                        target_path = Path(parts_exp[1])
                else:
                    target_path = Path(arg)
                    if str(target_path).endswith(".html"):
                        fmt = "html"

            if fmt == "html":
                out_path = exporter.export_html(target_path)
            else:
                out_path = exporter.export_markdown(target_path)
            console.print(f"[bold green]✓ Sessão exportada com sucesso em:[/bold green] [bold yellow]{out_path}[/bold yellow]")

        elif command == "/mcp":
            servers = self.agent.mcp_manager.servers
            if not servers:
                console.print("[dim]Nenhum servidor MCP configurado. Crie um arquivo [bold]mcp_servers.json[/bold] ou [bold]~/.llmcli_mcp.json[/bold].[/dim]")
            else:
                console.print(f"[bold cyan]Servidores MCP Configurados ({len(servers)}):[/bold cyan]")
                for s_name, s_cfg in servers.items():
                    console.print(f"  🔌 [bold yellow]{s_name}[/bold yellow]: comando='{s_cfg.command}' args={s_cfg.args}")
                mcp_tools = [k for k in self.agent.tools if k.startswith("mcp_")]
                console.print(f"[dim]Ferramentas MCP dinâmicas ativas: {len(mcp_tools)}[/dim]")

        elif command == "/tokens":
            tokens = self.agent.session.estimate_tokens()
            p_tok, c_tok, tot_tok = self.agent.session.get_cumulative_tokens()
            console.print(f"Estimativa atual de contexto: [bold cyan]~{tokens} tokens[/bold cyan]")
            console.print(f"Tokens acumulados nesta sessão: [bold yellow]~{tot_tok} tokens[/bold yellow] (~{p_tok} prompt + ~{c_tok} completion)")

        elif command == "/help":
            self._print_help()

        else:
            console.print(f"[red]Comando desconhecido: '{command}'. Digite /help para ver os comandos disponíveis.[/red]")

        return True

    def _print_help(self) -> None:
        console.print("""
[bold cyan]Comandos Disponíveis no llmCli:[/bold cyan]
  [bold yellow]/yolo[/bold yellow]             - Alterna o modo YOLO (salva preferência por LLM e global)
  [bold yellow]/architect [mod][/bold yellow]  - Alterna Modo Arquiteto (planejador forte + editor rápido)
  [bold yellow]/lang [código][/bold yellow]    - Altera o idioma do sistema (pt, en, es, de, fr, zh, ru, hi, auto)
  [bold yellow]/scan <ip/host>[/bold yellow]   - Escaneia o IP e detecta automaticamente servidores e modelos ativos
  [bold yellow]/host <ip/host>[/bold yellow]   - Conecta ao host e define como servidor local ativo (ex: /host 192.168.0.11)
  [bold yellow]/model <nome>[/bold yellow]     - Troca o modelo de LLM (carrega preferências salvas daquele modelo)
  [bold yellow]/models[/bold yellow]           - Exibe lista e status de todos os provedores locais e na nuvem
  [bold yellow]/mcp[/bold yellow]              - Lista servidores MCP e ferramentas externas ativas

  [bold yellow]/add <caminho>[/bold yellow]    - Adiciona arquivo ou diretório ao contexto da IA
  [bold yellow]/drop <caminho>[/bold yellow]   - Remove arquivo do contexto
  [bold yellow]/files[/bold yellow]            - Lista arquivos carregados no contexto atual
  [bold yellow]/index[/bold yellow]            - Indexa a base de código para busca semântica local
  [bold yellow]/search <termo>[/bold yellow]  - Realiza busca semântica/RAG no código indexado
  [bold yellow]/web <termo>[/bold yellow]     - Pesquisa na web (DuckDuckGo/Tavily) e traz respostas atualizadas

  [bold yellow]/diff[/bold yellow]             - Exibe alterações Git não commitadas
  [bold yellow]/commit [msg][/bold yellow]      - Gera commit semântico via IA ou cria commit direto
  [bold yellow]/review[/bold yellow]           - Executa Code Review das alterações Git pendentes
  [bold yellow]/undo[/bold yellow]             - Reverte a última modificação ou commit gerado pela IA
  [bold yellow]/test [args][/bold yellow]      - Roda testes (pytest) e sugere correção automática se falhar
  [bold yellow]/gentest <arq>[/bold yellow]    - Gera suíte completa de testes unitários com pytest para o arquivo
  [bold yellow]/run <comando>[/bold yellow]   - Executa comando no terminal da raiz do projeto

  [bold yellow]/plan <objetivo>[/bold yellow] - Cria plano estruturado e gera tarefas automáticas no /todo
  [bold yellow]/todo [add|check][/bold yellow] - Gerencia checklist interativo de tarefas da sessão
  [bold yellow]/export [md|html][/bold yellow] - Exporta relatório completo da sessão em Markdown ou HTML
  [bold yellow]/paste[/bold yellow]            - Inicia modo multilinha para colar blocos de código
  [bold yellow]/compact[/bold yellow]          - Compacta o histórico da conversa gerando resumo consolidado
  [bold yellow]/temp [valor][/bold yellow]     - Exibe ou altera a temperatura (salva por LLM e global)
  [bold yellow]/system [txt][/bold yellow]     - Exibe, altera ou redefine o system prompt (ex: /system reset)
  [bold yellow]/clear[/bold yellow]            - Limpa o histórico de mensagens da conversa
  [bold yellow]/reset [prefs|all][/bold yellow] - Limpa sessão ou redefine preferências salvas do usuário
  [bold yellow]/tokens[/bold yellow]           - Exibe estimativa de tokens do contexto e da sessão
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
