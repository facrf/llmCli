"""Sequential, supervised coordinator for specialized llmCli agents."""
from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Awaitable, Callable, Dict, List, Optional

if TYPE_CHECKING:
    from src.core.agent import Agent


@dataclass
class AgentReport:
    role: str
    status: str
    summary: str
    affected_files: List[str] = field(default_factory=list)


@dataclass
class MultiAgentRun:
    objective: str
    reports: List[AgentReport] = field(default_factory=list)

    @property
    def plan(self) -> str:
        return next((report.summary for report in self.reports if report.role == "architect"), "")


RoleRunner = Callable[[str, str, Optional[str]], Awaitable[str]]


class MultiAgentCoordinator:
    """Runs a safe sequential team; only the implementer can modify files."""

    READ_ONLY_ROLES = ("researcher", "architect", "tester", "reviewer")

    def __init__(self, agent: "Agent", role_runner: Optional[RoleRunner] = None) -> None:
        self.agent = agent
        self._role_runner = role_runner or self._run_read_only_role

    def role_model(self, role: str) -> Optional[str]:
        role_config = self.agent.config.multi_agent.roles.get(role)
        return role_config.model if role_config and role_config.model else None

    def role_limits(self, role: str) -> tuple[int, int]:
        role_config = self.agent.config.multi_agent.roles.get(role)
        if role_config is None:
            return 4, 120
        return role_config.max_iterations, role_config.timeout_seconds

    async def _run_read_only_role(self, role: str, prompt: str, model: Optional[str]) -> str:
        return await self.agent.run_role_prompt(role, prompt, model)

    async def run(self, objective: str, apply_changes: bool = False) -> MultiAgentRun:
        run = MultiAgentRun(objective=objective)
        research_report = await self._delegate(
            "researcher",
            f"Objetivo: {objective}\nInvestigue o repositório e liste evidências, arquivos relevantes e riscos. Não proponha alterações.",
            self.role_model("researcher"),
        )
        self._record(run, research_report)
        research = research_report.summary

        plan_report = await self._delegate(
            "architect",
            f"Objetivo: {objective}\n\nEvidências do pesquisador:\n{research}\n\nCrie um plano de implementação verificável, com arquivos e testes afetados. Não altere arquivos.",
            self.role_model("architect") or self.agent.config.architect_model,
        )
        self._record(run, plan_report)
        plan = plan_report.summary

        if not apply_changes:
            return run

        implementation_report = await self._implement(
            objective, plan
        )
        self._record(run, implementation_report)
        implementation = implementation_report.summary

        tests_report = await self._delegate(
            "tester",
            f"Objetivo: {objective}\nPlano: {plan}\nImplementação: {implementation}\nAvalie quais testes e verificações devem ser executados; não modifique arquivos.",
            self.role_model("tester"),
        )
        self._record(run, tests_report)

        review_report = await self._delegate(
            "reviewer",
            f"Objetivo: {objective}\nPlano: {plan}\nImplementação: {implementation}\nFaça uma revisão de riscos e critérios de aceite; não modifique arquivos.",
            self.role_model("reviewer"),
        )
        self._record(run, review_report)
        return run

    async def _delegate(self, role: str, prompt: str, model: Optional[str]) -> AgentReport:
        try:
            _, timeout_seconds = self.role_limits(role)
            summary = await asyncio.wait_for(
                self._role_runner(role, prompt, model), timeout=timeout_seconds
            )
            return AgentReport(role, "complete", summary)
        except asyncio.TimeoutError:
            return AgentReport(role, "failed", f"Agente {role} excedeu o limite de tempo.")
        except Exception as exc:
            return AgentReport(role, "failed", f"Falha do agente {role}: {exc}")

    async def _implement(self, objective: str, plan: str) -> AgentReport:
        try:
            summary = await self.agent.run_prompt(
                f"Você é o implementador. Execute este plano para o objetivo '{objective}':\n\n{plan}"
            )
            return AgentReport("implementer", "complete", summary)
        except Exception as exc:
            return AgentReport("implementer", "failed", f"Falha do implementador: {exc}")

    def _record(self, run: MultiAgentRun, report: AgentReport) -> None:
        run.reports.append(report)
        session = getattr(self.agent, "session", None)
        if session is not None:
            session.add_assistant_message(
                f"[MULTIAGENT:{report.role}:{report.status}]\n{report.summary}"
            )

    def status(self) -> Dict[str, str]:
        roles = ("researcher", "architect", "implementer", "tester", "reviewer")
        return {role: self.role_model(role) or self.agent.config.active_model for role in roles}
