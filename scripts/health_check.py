#!/usr/bin/env python3
"""Script de diagnóstico rápido para testar conectividade com LLMs locais e nuvem."""
import asyncio
import sys
from pathlib import Path

# Garantir que a pasta raiz esteja no sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.providers.registry import ProviderRegistry
from src.ui.console import console, print_status_table


async def main():
    console.print("\n[bold cyan]=== Diagnóstico de Conectividade llmCli ===[/bold cyan]\n")
    console.print("[dim]Testando conexões com llama.cpp, Ollama, LM Studio e credenciais na nuvem...[/dim]\n")
    
    status_list = await ProviderRegistry.get_status_overview()
    print_status_table(status_list)
    
    online_locals = [s for s in status_list if "Local" in s["provider"] and s["status"] == "ONLINE"]
    configured_cloud = [s for s in status_list if "Nuvem" in s["provider"] and s["status"] == "CONFIGURADO"]
    
    console.print(f"\n[bold]Resumo:[/bold]")
    console.print(f"  • Provedores locais online: [bold green]{len(online_locals)}[/bold green]")
    console.print(f"  • Provedores na nuvem configurados: [bold green]{len(configured_cloud)}[/bold green]")
    
    if not online_locals and not configured_cloud:
        console.print("\n[yellow]Dica: Para começar, suba o llama.cpp local na porta 8080 ou adicione suas chaves no .env![/yellow]")


if __name__ == "__main__":
    asyncio.run(main())
