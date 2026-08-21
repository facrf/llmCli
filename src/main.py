"""Main CLI entrypoint for llmCli."""
from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path
from typing import List, Optional

# Garantir que a raiz do projeto esteja no sys.path para execucoes diretas
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src import __version__
from src.config import get_config
from src.core.agent import Agent
from src.core.session import Session
from src.providers.registry import ProviderRegistry
from src.providers.scanner import HostScanner
from src.ui.console import console, print_scan_results, print_status_table
from src.ui.repl import ReplSession


def parse_arguments(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="llm-cli",
        description="llmCli: Assistente IA de Código Híbrido (Local: llama.cpp/Ollama/LM Studio | Nuvem: Gemini/OpenAI/Claude/DeepSeek)"
    )
    parser.add_argument("prompt", nargs="*", help="Prompt para execução direta (não-interativa).")
    parser.add_argument("-m", "--model", help="Modelo de LLM a ser utilizado (ex: llamacpp/default, gemini/gemini-2.5-flash, openai/gpt-4o).")
    parser.add_argument("-y", "--yolo", action="store_true", help="Ativa o modo YOLO (execução autônoma total sem pedir confirmação).")
    parser.add_argument("-f", "--file", action="append", default=[], help="Adiciona arquivo(s) ao contexto inicial.")
    parser.add_argument("--scan", metavar="IP", help="Escaneia um IP/host e detecta automaticamente todos os modelos e servidores de LLM ativos.")
    parser.add_argument("--host", metavar="IP", help="Conecta ao IP/host informado e configura como endpoint padrão para Ollama e llama.cpp.")
    parser.add_argument("--models", action="store_true", help="Verifica e lista todos os provedores e modelos disponíveis.")
    parser.add_argument("-v", "--version", action="version", version=f"llmCli v{__version__}")
    return parser.parse_args(argv)


async def async_main() -> int:
    args = parse_arguments()
    config = get_config()

    # Escanear IP e sair se passado --scan
    if args.scan:
        console.print(f"[dim]Escaneando host [bold yellow]{args.scan}[/bold yellow] em busca de modelos de LLM...[/dim]")
        scanner = HostScanner(args.scan)
        services = await scanner.scan()
        print_scan_results(args.scan, services)
        return 0

    # Configurar host se passado --host
    if args.host:
        console.print(f"[dim]Conectando ao host [bold yellow]{args.host}[/bold yellow] e detectando modelos...[/dim]")
        scanner = HostScanner(args.host)
        services = await scanner.scan()
        print_scan_results(args.host, services)
        for s in services:
            if s.provider_type == "ollama":
                config.local_endpoints.ollama = s.base_url
            elif s.provider_type == "llamacpp":
                config.local_endpoints.llamacpp = s.base_url
        if services and not args.model:
            chosen = services[0]
            m_name = chosen.models[0] if chosen.models else "default"
            config.active_model = f"{chosen.provider_type}/{m_name}"
            console.print(f"[bold green]✓ Modelo ativo configurado automaticamente para:[/bold green] [bold yellow]{config.active_model}[/bold yellow]\n")

    # Sobrescrever configurações via argumentos CLI
    if args.model:
        config.active_model = args.model
    if args.yolo:
        config.yolo_mode = True


    # Listar modelos e sair se solicitado
    if args.models:
        console.print("[dim]Verificando provedores locais e em nuvem...[/dim]")
        status = await ProviderRegistry.get_status_overview()
        print_status_table(status)
        return 0

    session = Session()

    # Adicionar arquivos passados via flag -f
    for file_path in args.file:
        ok, msg = session.file_tracker.add_file(file_path)
        if not ok:
            console.print(f"[yellow]Aviso:[/yellow] {msg}")

    agent = Agent(session=session)

    # Modo não interativo (One-shot) se foi passado um prompt na linha de comando
    if args.prompt:
        full_prompt = " ".join(args.prompt).strip()
        await agent.run_prompt(full_prompt)
        return 0

    # Modo Interativo (REPL)
    repl = ReplSession(agent=agent)
    await repl.start()
    return 0


def cli_entrypoint() -> None:
    try:
        sys.exit(asyncio.run(async_main()))
    except KeyboardInterrupt:
        console.print("\n[dim]Operação interrompida.[/dim]")
        sys.exit(130)


if __name__ == "__main__":
    cli_entrypoint()
