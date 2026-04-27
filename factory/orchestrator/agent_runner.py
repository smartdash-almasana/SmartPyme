from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class AgentResult:
    status: str
    content: str
    data: dict[str, Any]


class MockAgentRunner:
    """Deterministic test runner for Hermes loop.

    This runner does not call external APIs. It exists only to validate state
    transitions and evidence persistence before connecting Hermes/Vertex.
    """

    def __init__(self, auditor_verdict: str = "VALIDADO") -> None:
        self.auditor_verdict = auditor_verdict

    def run_builder(self, hallazgo_text: str) -> AgentResult:
        return AgentResult(
            status="submitted",
            content="VEREDICTO_BUILDER: submitted\nEVIDENCE: mock builder executed deterministically.\n",
            data={"status": "submitted"},
        )

    def run_auditor(self, hallazgo_text: str, builder_report: str) -> AgentResult:
        verdict = self.auditor_verdict
        return AgentResult(
            status="validated" if verdict == "VALIDADO" else "rejected",
            content=f"VEREDICTO_AUDITOR: {verdict}\nEVIDENCIA: mock auditor reviewed builder report.\n",
            data={"verdict": verdict},
        )
