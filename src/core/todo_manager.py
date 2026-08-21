"""Interactive Checklist and Task Planner (TODO Manager) for llmCli."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class TodoItem:
    id: int
    text: str
    done: bool = False


class TodoManager:
    def __init__(self) -> None:
        self.items: List[TodoItem] = []
        self._next_id: int = 1

    def add_item(self, text: str) -> TodoItem:
        clean_text = text.strip()
        item = TodoItem(id=self._next_id, text=clean_text, done=False)
        self._next_id += 1
        self.items.append(item)
        return item

    def check_item(self, item_id: int) -> bool:
        for item in self.items:
            if item.id == item_id:
                item.done = True
                return True
        return False

    def uncheck_item(self, item_id: int) -> bool:
        for item in self.items:
            if item.id == item_id:
                item.done = False
                return True
        return False

    def toggle_item(self, item_id: int) -> Optional[bool]:
        for item in self.items:
            if item.id == item_id:
                item.done = not item.done
                return item.done
        return None

    def remove_item(self, item_id: int) -> bool:
        initial_len = len(self.items)
        self.items = [item for item in self.items if item.id != item_id]
        return len(self.items) < initial_len

    def clear(self) -> None:
        self.items.clear()
        self._next_id = 1

    def parse_plan(self, plan_text: str) -> int:
        """Extrai itens de tarefas a partir de um texto de plano gerado pela IA."""
        count = 0
        for line in plan_text.splitlines():
            line = line.strip()
            # Padrão: - [ ] tarefa ou 1. [ ] tarefa ou - tarefa
            m_box = re.match(r"^[-*]\s*\[([ xX])\]\s*(.+)$", line)
            if m_box:
                is_done = m_box.group(1).lower() == "x"
                item_text = m_box.group(2).strip()
                item = self.add_item(item_text)
                item.done = is_done
                count += 1
                continue

            m_num = re.match(r"^\d+[\.\)]\s*(.+)$", line)
            if m_num:
                item_text = m_num.group(1).strip()
                self.add_item(item_text)
                count += 1
                continue

            m_bullet = re.match(r"^[-*]\s+(.+)$", line)
            if m_bullet and len(line) > 5 and not line.startswith("---"):
                item_text = m_bullet.group(1).strip()
                self.add_item(item_text)
                count += 1

        return count

    def format_checklist(self) -> str:
        if not self.items:
            return "Nenhuma tarefa na lista. Use '/todo add <tarefa>' ou '/plan <objetivo>' para adicionar."

        completed = sum(1 for i in self.items if i.done)
        total = len(self.items)
        progress = f"Progresso: {completed}/{total} concluídas"

        lines = [f"[bold cyan]📋 Checklist de Tarefas ({progress}):[/bold cyan]"]
        for item in self.items:
            box = "[bold green][✓][/bold green]" if item.done else "[bold yellow][ ][/bold yellow]"
            style = "strike dim" if item.done else "bold white"
            lines.append(f"  {box} [cyan]#{item.id}[/cyan] [{style}]{item.text}[/{style}]")

        return "\n".join(lines)
