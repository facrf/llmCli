"""Tests for the sequential multi-agent coordinator."""
import pytest

from src.core.multi_agent import MultiAgentCoordinator


class FakeConfig:
    class MultiAgent:
        roles = {}

    multi_agent = MultiAgent()
    architect_model = "architect-model"
    active_model = "editor-model"


class FakeAgent:
    config = FakeConfig()

    def __init__(self):
        self.implemented = []

    async def run_role_prompt(self, role, prompt, model):
        return f"{role}:{model or 'default'}"

    async def run_prompt(self, prompt):
        self.implemented.append(prompt)
        return "implementation complete"


@pytest.mark.asyncio
async def test_sequential_planning_stops_before_changes():
    agent = FakeAgent()
    coordinator = MultiAgentCoordinator(agent)

    run = await coordinator.run("Adicionar autenticação")

    assert [report.role for report in run.reports] == ["researcher", "architect"]
    assert "architect:architect-model" in run.plan
    assert agent.implemented == []


@pytest.mark.asyncio
async def test_implementation_runs_only_after_explicit_request():
    agent = FakeAgent()
    coordinator = MultiAgentCoordinator(agent)

    run = await coordinator.run("Adicionar autenticação", apply_changes=True)

    assert [report.role for report in run.reports] == [
        "researcher", "architect", "implementer", "tester", "reviewer"
    ]
    assert len(agent.implemented) == 1
    assert "Adicionar autenticação" in agent.implemented[0]


@pytest.mark.asyncio
async def test_role_failure_is_recorded_without_aborting_pipeline():
    agent = FakeAgent()

    async def failing_runner(role, prompt, model):
        if role == "researcher":
            raise RuntimeError("provider unavailable")
        return f"{role}:ok"

    coordinator = MultiAgentCoordinator(agent, role_runner=failing_runner)
    run = await coordinator.run("Analisar falha")

    assert run.reports[0].status == "failed"
    assert "provider unavailable" in run.reports[0].summary
    assert run.reports[1].role == "architect"
    assert run.reports[1].status == "complete"
