"""Terminal output formatting, rich styling, diff views, and user confirmation prompts."""
from __future__ import annotations

import sys
from typing import Optional
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text

console = Console()


def print_banner(active_model: str, yolo_mode: bool) -> None:
    yolo_badge = "[bold red]⚡ YOLO: ON[/bold red]" if yolo_mode else "[bold green]🛡️ YOLO: OFF[/bold green]"
    title = f"[bold cyan]llmCli[/bold cyan] - Assistente IA de Código Híbrido (Local & Nuvem)"
    subtitle = f"Modelo Ativo: [bold yellow]{active_model}[/bold yellow] | Modo: {yolo_badge}"
    
    body = (
        f"{title}\n{subtitle}\n\n"
        "[dim]Suporte nativo a llama.cpp (porta 8080), Ollama, LM Studio, vLLM, Gemini, OpenAI, Anthropic e DeepSeek.[/dim]\n"
        "[dim]Digite [bold]/help[/bold] para ver comandos ou [bold]/yolo[/bold] para alternar o modo autônomo.[/dim]"
    )
    console.print(Panel(body, border_style="cyan", padding=(1, 2)))


def print_diff(diff_text: str, filename: str = "") -> None:
    if not diff_text.strip():
        return
    syntax = Syntax(diff_text, "diff", theme="monokai", line_numbers=False)
    title = f"Modificações: {filename}" if filename else "Diff Proposto"
    console.print(Panel(syntax, title=title, border_style="yellow"))


def print_tool_execution(tool_name: str, args_summary: str, is_yolo: bool = False) -> None:
    badge = "[bold red][YOLO AUTO][/bold red]" if is_yolo else "[bold cyan][FERRAMENTA][/bold cyan]"
    console.print(f"\n{badge} Executando [bold yellow]{tool_name}[/bold yellow]({args_summary})...")


def print_tool_result(tool_name: str, success: bool, output: str) -> None:
    style = "bold green" if success else "bold red"
    icon = "✓" if success else "✗"
    console.print(f"[{style}]{icon} {tool_name}:[/{style}]")
    if len(output.splitlines()) > 10:
        lines = output.splitlines()
        preview = "\n".join(lines[:10]) + f"\n... (+ {len(lines) - 10} linhas ocultas)"
        console.print(Panel(preview, border_style="dim"))
    else:
        console.print(Panel(output, border_style="dim"))


def ask_user_confirmation(prompt_text: str) -> str:
    """Solicita confirmação do usuário no modo padrão. Retorna: 'y' (sim), 'n' (não), 'yolo' (ativar yolo), 'abort' (cancelar tarefa)."""
    console.print(f"\n[bold yellow]❓ {prompt_text}[/bold yellow]")
    console.print("[dim]([s]im / [N]ão / [y]olo para liberar tudo / [c]ancelar)[/dim] ", end="")
    try:
        choice = input().strip().lower()
        if choice in ("s", "sim", "y", "yes"):
            return "yes"
        elif choice in ("yolo", "yolo!"):
            return "yolo"
        elif choice in ("c", "cancel", "abort"):
            return "abort"
        else:
            return "no"
    except (KeyboardInterrupt, EOFError):
        return "abort"


def print_status_table(status_list: list) -> None:
    table = Table(title="Status dos Provedores de LLM", border_style="cyan")
    table.add_column("Provedor", style="bold")
    table.add_column("Endpoint / Origem", style="dim")
    table.add_column("Status", justify="center")
    table.add_column("Detalhes", style="italic")
    table.add_column("Exemplo de Uso", style="yellow")

    for item in status_list:
        status = item["status"]
        if status in ("ONLINE", "CONFIGURADO"):
            status_styled = f"[bold green]{status}[/bold green]"
        elif status == "SEM CHAVE":
            status_styled = f"[bold yellow]{status}[/bold yellow]"
        else:
            status_styled = f"[bold red]{status}[/bold red]"

        models_extra = f" ({len(item.get('models', []))} modelos)" if item.get("models") else ""
        table.add_row(
            item["provider"],
            item["endpoint"],
            status_styled,
            item["detail"] + models_extra,
            item["example"]
        )

    console.print(table)


def print_scan_results(host: str, services: list) -> None:
    if not services:
        console.print(f"\n[bold yellow]Nenhum servidor de LLM ativo encontrado no host '{host}'.[/bold yellow]")
        console.print("[dim]Certifique-se de que o servidor (Ollama na porta 11434 ou llama.cpp na porta 8080) está rodando e acessível na rede.[/dim]\n")
        return

    table = Table(title=f"Serviços e Modelos Detectados em {host}", border_style="green")
    table.add_column("Serviço / Servidor", style="bold cyan")
    table.add_column("Endpoint", style="dim")
    table.add_column("Modelos Disponíveis", style="yellow")
    table.add_column("Comando para Usar", style="bold green")

    for s in services:
        models_text = ", ".join(s.models) if s.models else "(modelo padrão ativo)"
        cmd_example = f"/model {s.provider_type}/{s.models[0]}" if s.models else f"/model {s.provider_type}/default"
        table.add_row(
            s.service_name,
            s.base_url,
            models_text,
            cmd_example
        )

    console.print(table)
