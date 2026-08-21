"""Interactive autocomplete for prompt_toolkit REPL (commands & workspace files)."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable, List, Optional
from prompt_toolkit.completion import CompleteEvent, Completer, Completion
from prompt_toolkit.document import Document
from src.config import get_config

SLASH_COMMANDS = [
    ("/yolo", "Alterna o modo YOLO (execução autônoma total sem pedir confirmação)"),
    ("/model", "Troca o modelo de LLM ativo (ex: /model llamacpp/default, /model gemini/gemini-2.5-flash)"),
    ("/models", "Lista todos os provedores e modelos locais/nuvem disponíveis"),
    ("/scan", "Escaneia um IP/host e detecta automaticamente todos os modelos e servidores de LLM ativos (ex: /scan 192.168.0.11)"),
    ("/host", "Conecta e define o IP/host padrão para Ollama e llama.cpp (ex: /host 192.168.0.11)"),
    ("/discover", "Escaneia e autodetecta modelos e servidores de LLM ativos no host"),
    ("/add", "Adiciona arquivo(s) ao contexto ativo da IA (ex: /add src/main.py)"),
    ("/drop", "Remove arquivo(s) do contexto da IA"),
    ("/files", "Lista arquivos atualmente carregados no contexto"),
    ("/diff", "Exibe as alterações git atuais não commitadas"),
    ("/commit", "Gera mensagem semântica via IA e cria commit Git (ex: /commit ou /commit feat: novo modulo)"),
    ("/review", "Analisa e faz Code Review das modificações Git pendentes"),
    ("/undo", "Reverte o último checkpoint / modificação realizada"),
    ("/run", "Executa um comando de terminal diretamente"),
    ("/test", "Executa a suíte de testes (pytest) com diagnóstico"),
    ("/clear", "Limpa o histórico da conversa atual"),
    ("/reset", "Limpa histórico e remove todos os arquivos do contexto"),
    ("/compact", "Compacta o histórico da conversa gerando um resumo consolidado"),
    ("/temp", "Exibe ou altera a temperatura do modelo (ex: /temp 0.2)"),
    ("/system", "Exibe, altera ou redefine o system prompt da sessão (ex: /system reset)"),
    ("/paste", "Inicia modo de entrada multilinha para colar blocos de código"),
    ("/tokens", "Exibe estimativa de tokens do contexto atual"),
    ("/help", "Exibe o menu de ajuda e documentação"),
    ("/exit", "Encerra o llmCli"),
    ("/quit", "Encerra o llmCli"),
    ("/q", "Encerra o llmCli")
]

KNOWN_SLASH_COMMANDS = [cmd for cmd, _ in SLASH_COMMANDS]


def resolve_slash_command(command: str, has_arg: bool = False) -> tuple[Optional[str], List[str]]:
    """Resolve um comando slash parcial ou exato para seu comando canônico.
    
    Retorna uma tupla (resolved_command, candidate_matches):
    - Se encontrar correspondência exata ou única correspondência por prefixo, retorna (resolved_command, []).
    - Se for ambíguo (múltiplas opções), retorna (None, candidate_matches).
    - Se for desconhecido (nenhuma opção), retorna (None, []).
    """
    cmd_clean = command.strip().lower()
    if not cmd_clean.startswith("/"):
        return None, []

    # 1. Correspondência Exata
    if cmd_clean in KNOWN_SLASH_COMMANDS:
        return cmd_clean, []

    # 2. Busca por prefixo
    matches = [c for c in KNOWN_SLASH_COMMANDS if c.startswith(cmd_clean)]
    
    # Se houver apenas 1 comando correspondente, completa automaticamente
    if len(matches) == 1:
        return matches[0], []

    # Caso especial: se o usuário passou argumento e as opções forem /model e /models,
    # /model é o único que aceita argumentos
    if has_arg and set(matches) == {"/model", "/models"}:
        return "/model", []

    return None, matches


class CliCompleter(Completer):
    def get_completions(self, document: Document, complete_event: CompleteEvent) -> Iterable[Completion]:
        text_before_cursor = document.text_before_cursor
        config = get_config()

        # Completar comandos slash
        if text_before_cursor.startswith("/"):
            parts = text_before_cursor.split(" ", 1)
            cmd_part = parts[0]

            if len(parts) == 1:
                for cmd, desc in SLASH_COMMANDS:
                    if cmd.startswith(cmd_part):
                        yield Completion(cmd, start_position=-len(cmd_part), display=cmd, display_meta=desc)
                return

            # Completar caminhos de arquivo para /add e /drop
            if cmd_part in ("/add", "/drop"):
                arg_part = parts[1]
                for file_compl in self._complete_files(arg_part, config.project_root):
                    yield file_compl
                return

            # Sugestão de modelos para /model
            if cmd_part == "/model":
                model_arg = parts[1]
                model_suggestions = [
                    "llamacpp/default",
                    "llamacpp/qwen2.5-coder",
                    "ollama/qwen2.5-coder:latest",
                    "ollama/deepseek-r1:latest",
                    "gemini/gemini-2.5-flash",
                    "gemini/gemini-2.5-pro",
                    "gpt/codex",
                    "gpt/gpt-4o",
                    "gpt/gpt-4o-mini",
                    "openai/gpt-4o",
                    "openai/gpt-4o-mini",
                    "openai/o1",
                    "openai/o3-mini",
                    "openai/codex",
                    "anthropic/claude-3-7-sonnet-20250219",
                    "deepseek/deepseek-chat",
                    "groq/llama-3.3-70b-versatile",
                    "openrouter/anthropic/claude-3.5-sonnet"
                ]
                for m in model_suggestions:
                    if m.startswith(model_arg):
                        yield Completion(m, start_position=-len(model_arg), display=m, display_meta="Modelo")
                return

    def _complete_files(self, prefix: str, root_dir: Path) -> Iterable[Completion]:
        target_dir = root_dir
        sub_prefix = prefix

        if "/" in prefix:
            parent_rel, sub_prefix = prefix.rsplit("/", 1)
            target_dir = (root_dir / parent_rel).resolve()

        if target_dir.exists() and target_dir.is_dir():
            try:
                for entry in sorted(os.listdir(target_dir)):
                    if entry.startswith(".") or entry in ("__pycache__", "node_modules", ".venv"):
                        continue
                    if entry.lower().startswith(sub_prefix.lower()):
                        full_entry = target_dir / entry
                        rel = str(full_entry.relative_to(root_dir))
                        is_dir = full_entry.is_dir()
                        display_val = f"{rel}/" if is_dir else rel
                        insert_val = f"{rel}/" if is_dir else rel
                        yield Completion(
                            insert_val,
                            start_position=-len(prefix),
                            display=display_val,
                            display_meta="pasta" if is_dir else "arquivo"
                        )
            except Exception:
                pass
