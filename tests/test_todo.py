"""Unit tests for TODO task planner and checklist."""
import pytest
from src.core.todo_manager import TodoManager


def test_todo_manager_crud():
    mgr = TodoManager()
    assert len(mgr.items) == 0

    item1 = mgr.add_item("Criar módulo de autenticação")
    item2 = mgr.add_item("Adicionar testes unitários")
    assert len(mgr.items) == 2
    assert item1.id == 1
    assert item2.id == 2
    assert item1.done is False

    # Check
    assert mgr.check_item(1) is True
    assert mgr.items[0].done is True

    # Toggle
    mgr.toggle_item(1)
    assert mgr.items[0].done is False

    # Format
    fmt = mgr.format_checklist()
    assert "Criar módulo de autenticação" in fmt

    # Clear
    mgr.clear()
    assert len(mgr.items) == 0


def test_todo_manager_parse_plan():
    mgr = TodoManager()
    plan_text = """
    Aqui está o plano:
    - [ ] 1. Configurar banco de dados
    - [x] 2. Criar modelos SQLAlchemy
    - [ ] 3. Implementar rotas FastAPI
    """
    added = mgr.parse_plan(plan_text)
    assert added == 3
    assert mgr.items[0].done is False
    assert mgr.items[1].done is True
    assert "FastAPI" in mgr.items[2].text
