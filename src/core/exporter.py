"""Session Exporter for llmCli to Markdown and HTML documentation."""
from __future__ import annotations

import datetime
import html
from pathlib import Path
from typing import Optional

from src.config import PROJECT_ROOT, get_config
from src.core.session import Session


class SessionExporter:
    def __init__(self, session: Session, project_root: Optional[Path] = None) -> None:
        self.session = session
        self.project_root = project_root or PROJECT_ROOT
        self.config = get_config()

    def export_markdown(self, target_path: Optional[Path] = None) -> Path:
        now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        dest = target_path or (self.project_root / f"session_export_{now}.md")

        p_tok, c_tok, tot_tok = self.session.get_cumulative_tokens()
        tracked = list(self.session.file_tracker.tracked_files)

        lines = [
            f"# 📄 Relatório de Sessão llmCli",
            f"- **Data/Hora:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"- **Modelo Ativo:** `{self.config.active_model}`",
            f"- **Modo YOLO:** `{'Ativado' if self.config.yolo_mode else 'Desativado'}`",
            f"- **Modo Arquiteto:** `{'Ativado (' + self.config.architect_model + ')' if self.config.architect_mode else 'Desativado'}`",
            f"- **Tokens Acumulados:** ~{tot_tok} tokens (~{p_tok} prompt + ~{c_tok} completion)",
            f"- **Arquivos no Contexto ({len(tracked)}):** {', '.join(f'`{f}`' for f in tracked) if tracked else 'Nenhum'}",
            "",
            "---",
            "",
            "## 💬 Histórico da Conversa",
            ""
        ]

        for i, msg in enumerate(self.session.messages, 1):
            role = msg.role.upper()
            if role == "USER":
                lines.append(f"### 👤 Usuário\n\n{msg.content}\n")
            elif role == "ASSISTANT":
                lines.append(f"### 🤖 Assistente ({self.config.active_model})\n\n{msg.content}\n")
            elif role == "TOOL":
                lines.append(f"#### 🛠️ Ferramenta: `{msg.name or 'tool'}`\n\n```text\n{msg.content}\n```\n")
            elif role == "SYSTEM":
                lines.append(f"#### ⚙️ Sistema\n\n{msg.content}\n")

        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text("\n".join(lines), encoding="utf-8")
        return dest

    def export_html(self, target_path: Optional[Path] = None) -> Path:
        now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        dest = target_path or (self.project_root / f"session_export_{now}.html")

        p_tok, c_tok, tot_tok = self.session.get_cumulative_tokens()
        tracked = list(self.session.file_tracker.tracked_files)

        messages_html = []
        for msg in self.session.messages:
            role = msg.role.lower()
            escaped = html.escape(msg.content or "").replace("\n", "<br>")
            if role == "user":
                badge = '<span class="badge user">👤 Usuário</span>'
                cls = "msg-user"
            elif role == "assistant":
                badge = f'<span class="badge assistant">🤖 Assistente ({self.config.active_model})</span>'
                cls = "msg-assistant"
            elif role == "tool":
                badge = f'<span class="badge tool">🛠️ Ferramenta: {msg.name or "tool"}</span>'
                cls = "msg-tool"
            else:
                badge = '<span class="badge system">⚙️ Sistema</span>'
                cls = "msg-system"

            messages_html.append(f"""
            <div class="message {cls}">
                <div class="msg-header">{badge}</div>
                <div class="msg-body">{escaped}</div>
            </div>
            """)

        html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>llmCli - Relatório de Sessão</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 2rem; line-height: 1.6; }}
        .container {{ max-width: 900px; margin: 0 auto; }}
        .header {{ background: #1e293b; padding: 1.5rem; border-radius: 8px; margin-bottom: 2rem; border-left: 4px solid #38bdf8; }}
        .header h1 {{ margin: 0 0 1rem 0; color: #38bdf8; font-size: 1.8rem; }}
        .meta-item {{ margin: 0.3rem 0; color: #94a3b8; }}
        .meta-item strong {{ color: #e2e8f0; }}
        .message {{ margin-bottom: 1.5rem; padding: 1rem 1.2rem; border-radius: 8px; }}
        .msg-user {{ background: #1e293b; border-left: 4px solid #22c55e; }}
        .msg-assistant {{ background: #1e293b; border-left: 4px solid #38bdf8; }}
        .msg-tool {{ background: #1e293b; border-left: 4px solid #eab308; font-family: monospace; font-size: 0.9rem; }}
        .msg-system {{ background: #1e293b; border-left: 4px solid #94a3b8; font-size: 0.9rem; }}
        .msg-header {{ margin-bottom: 0.6rem; font-weight: bold; }}
        .badge {{ padding: 0.2rem 0.6rem; border-radius: 4px; font-size: 0.85rem; }}
        .badge.user {{ background: #15803d; color: #fff; }}
        .badge.assistant {{ background: #0369a1; color: #fff; }}
        .badge.tool {{ background: #854d0e; color: #fff; }}
        .badge.system {{ background: #475569; color: #fff; }}
        .msg-body {{ white-space: pre-wrap; word-break: break-word; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📄 llmCli - Relatório de Sessão</h1>
            <div class="meta-item"><strong>Data:</strong> {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
            <div class="meta-item"><strong>Modelo Ativo:</strong> {self.config.active_model}</div>
            <div class="meta-item"><strong>Tokens Acumulados:</strong> ~{tot_tok} (~{p_tok} prompt + ~{c_tok} completion)</div>
            <div class="meta-item"><strong>Arquivos no Contexto:</strong> {', '.join(tracked) if tracked else 'Nenhum'}</div>
        </div>
        <div class="chat-flow">
            {''.join(messages_html)}
        </div>
    </div>
</body>
</html>
"""
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(html_content, encoding="utf-8")
        return dest
