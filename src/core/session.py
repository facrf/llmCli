"""Conversation session, system prompt builder, and message history management."""
from __future__ import annotations

from typing import List, Optional
from src.config import get_config
from src.context.file_tracker import FileTracker
from src.context.repomap import build_repo_map
from src.providers.base import ChatMessage


SYSTEM_PROMPT_TEMPLATE = """Você é o assistente oficial de desenvolvimento llmCli, operando diretamente no terminal do desenvolvedor.
Você ajuda a criar, refatorar, depurar e manter código neste projeto com máxima precisão e autonomia.

=== REGRAS FUNDAMENTAIS E SEGURANÇA ===
1. ISOLAMENTO DE DIRETÓRIO: Você opera estritamente dentro da raiz do projeto: {project_root}
   Nunca tente acessar, ler, gravar ou executar comandos fora deste diretório.
2. PRESERVAÇÃO DE CÓDIGO: Ao modificar arquivos existentes, preserve a formatação, comentários relevantes e evite remover código sem motivo.
3. SEGURANÇA: Nunca exponha segredos ou credenciais. Sugira o uso de variáveis no .env.

=== ESTRATÉGIAS DE EDIÇÃO DE ARQUIVOS ===
Você pode usar as ferramentas fornecidas (Function Calling) OU gerar blocos SEARCH/REPLACE no estilo Aider:

Exemplo de bloco SEARCH/REPLACE:
Arquivo: caminho/do/arquivo.py
<<<<<<< SEARCH
código exato existente
=======
código modificado
>>>>>>>

Para criar um novo arquivo completo, você pode usar a ferramenta `write_file` ou fornecer o SEARCH vazio:
Arquivo: novo_arquivo.py
<<<<<<< SEARCH
=======
conteúdo completo do novo arquivo
>>>>>>>

=== ESTRUTURA ATUAL DO PROJETO ===
{repo_map}

{files_context}
"""


class Session:
    def __init__(self, file_tracker: Optional[FileTracker] = None) -> None:
        self.config = get_config()
        self.file_tracker = file_tracker or FileTracker()
        self.messages: List[ChatMessage] = []
        self.custom_system_prompt: Optional[str] = None

    def set_custom_system_prompt(self, prompt: str) -> None:
        """Define um prompt de sistema personalizado para a sessão atual."""
        self.custom_system_prompt = prompt.strip()

    def reset_system_prompt(self) -> None:
        """Restaura o prompt de sistema para o padrão."""
        self.custom_system_prompt = None

    def build_system_message(self) -> ChatMessage:
        if self.custom_system_prompt:
            return ChatMessage(role="system", content=self.custom_system_prompt)

        repo_map = build_repo_map(max_files=60)
        files_context = self.file_tracker.get_context_text()
        prompt_text = SYSTEM_PROMPT_TEMPLATE.format(
            project_root=str(self.config.project_root),
            repo_map=repo_map,
            files_context=files_context
        )
        return ChatMessage(role="system", content=prompt_text)

    def compact_history(self, summary_text: str, keep_last_n: int = 2) -> None:
        """Compacta mensagens anteriores substituindo-as por um resumo consolidado."""
        if not self.messages:
            return
        recent_messages = self.messages[-keep_last_n:] if len(self.messages) > keep_last_n else []
        summary_msg = ChatMessage(
            role="system",
            content=f"=== RESUMO DO CONTEXTO ANTERIOR ===\n{summary_text.strip()}\n===================================="
        )
        self.messages = [summary_msg] + recent_messages

    def get_full_messages(self) -> List[ChatMessage]:
        """Retorna as mensagens da conversa iniciando pelo prompt de sistema atualizado."""
        return [self.build_system_message()] + self.messages

    def add_user_message(self, text: str) -> None:
        self.messages.append(ChatMessage(role="user", content=text))

    def add_assistant_message(self, text: str, tool_calls: Optional[list] = None) -> None:
        self.messages.append(ChatMessage(role="assistant", content=text, tool_calls=tool_calls))

    def add_tool_result(self, tool_call_id: str, name: str, output: str) -> None:
        self.messages.append(ChatMessage(role="tool", content=output, tool_call_id=tool_call_id, name=name))

    def clear_history(self) -> None:
        self.messages.clear()

    def estimate_tokens(self) -> int:
        """Estima o número total de tokens no contexto atual (~4 chars por token)."""
        all_msgs = self.get_full_messages()
        total_chars = sum(len(m.content) for m in all_msgs)
        return max(1, total_chars // 4)
