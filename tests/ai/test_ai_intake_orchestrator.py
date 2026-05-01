from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.ai.orchestrators.ai_intake_orchestrator import AIIntakeOrchestrator
from app.ai.schemas.owner_message_interpretation import OwnerMessageInterpretation
from app.ai.schemas.soft_interpretation_result import SoftInterpretationResult


class _ConsumerReturning:
    def __init__(self, result):
        self.result = result

    def consume(self, message: str):
        return self.result


class _ConsumerRaising:
    def consume(self, message: str):
        raise RuntimeError("consumer failed")


def test_orchestrator_returns_ok_result_from_consumer():
    interpretation = OwnerMessageInterpretation(intent="consultar_ventas", confidence=0.8)
    expected = SoftInterpretationResult.ok(
        raw_message="Revisame ventas",
        interpretation=interpretation,
    )
    orchestrator = AIIntakeOrchestrator(consumer=_ConsumerReturning(expected))

    result = orchestrator.interpret_owner_message("Revisame ventas")

    assert result == expected
    assert result.status == "ok"


def test_orchestrator_returns_empty_for_empty_message_without_calling_consumer():
    orchestrator = AIIntakeOrchestrator(
        consumer=_ConsumerReturning(
            SoftInterpretationResult.ok(
                raw_message="should not run",
                interpretation=OwnerMessageInterpretation(intent="should_not_run"),
            )
        )
    )

    result = orchestrator.interpret_owner_message("   ")

    assert result == SoftInterpretationResult.empty(raw_message="   ")


def test_orchestrator_returns_failed_when_consumer_raises():
    orchestrator = AIIntakeOrchestrator(consumer=_ConsumerRaising())

    result = orchestrator.interpret_owner_message("Revisame ventas")

    assert result.status == "failed"
    assert result.interpretation == OwnerMessageInterpretation()
    assert result.errors == ["orchestrator_exception"]


def test_orchestrator_returns_failed_when_consumer_returns_invalid_output():
    orchestrator = AIIntakeOrchestrator(consumer=_ConsumerReturning({"status": "ok"}))

    result = orchestrator.interpret_owner_message("Revisame ventas")

    assert result.status == "failed"
    assert result.interpretation == OwnerMessageInterpretation()
    assert result.errors == ["invalid_orchestrator_output"]


def test_orchestrator_preserves_failed_result_from_consumer():
    expected = SoftInterpretationResult.failed(
        raw_message="Revisame ventas",
        errors=["consumer_exception"],
    )
    orchestrator = AIIntakeOrchestrator(consumer=_ConsumerReturning(expected))

    result = orchestrator.interpret_owner_message("Revisame ventas")

    assert result == expected
    assert result.status == "failed"
    assert result.errors == ["consumer_exception"]
