from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.ai.consumers.owner_message_soft_interpretation_consumer import (
    OwnerMessageSoftInterpretationConsumer,
)
from app.ai.schemas.owner_message_interpretation import OwnerMessageInterpretation
from app.ai.schemas.soft_interpretation_result import SoftInterpretationResult


class _AdapterReturning:
    def __init__(self, result):
        self.result = result

    def interpret_result(self, message: str):
        return self.result


class _AdapterRaising:
    def interpret_result(self, message: str):
        raise RuntimeError("adapter failed")


def test_consumer_returns_ok_result_from_adapter():
    interpretation = OwnerMessageInterpretation(intent="consultar_ventas", confidence=0.8)
    expected = SoftInterpretationResult.ok(
        raw_message="Revisame ventas",
        interpretation=interpretation,
    )
    consumer = OwnerMessageSoftInterpretationConsumer(adapter=_AdapterReturning(expected))

    result = consumer.consume("Revisame ventas")

    assert result == expected
    assert result.status == "ok"


def test_consumer_returns_empty_for_empty_message_without_calling_adapter():
    consumer = OwnerMessageSoftInterpretationConsumer(
        adapter=_AdapterReturning(
            SoftInterpretationResult.ok(
                raw_message="should not run",
                interpretation=OwnerMessageInterpretation(intent="should_not_run"),
            )
        )
    )

    result = consumer.consume("   ")

    assert result == SoftInterpretationResult.empty(raw_message="   ")


def test_consumer_returns_failed_when_adapter_raises():
    consumer = OwnerMessageSoftInterpretationConsumer(adapter=_AdapterRaising())

    result = consumer.consume("Revisame ventas")

    assert result.status == "failed"
    assert result.interpretation == OwnerMessageInterpretation()
    assert result.errors == ["consumer_exception"]


def test_consumer_returns_failed_when_adapter_returns_invalid_output():
    consumer = OwnerMessageSoftInterpretationConsumer(adapter=_AdapterReturning({"status": "ok"}))

    result = consumer.consume("Revisame ventas")

    assert result.status == "failed"
    assert result.interpretation == OwnerMessageInterpretation()
    assert result.errors == ["invalid_consumer_output"]


def test_consumer_preserves_failed_result_from_adapter():
    expected = SoftInterpretationResult.failed(
        raw_message="Revisame ventas",
        errors=["interpreter_exception"],
    )
    consumer = OwnerMessageSoftInterpretationConsumer(adapter=_AdapterReturning(expected))

    result = consumer.consume("Revisame ventas")

    assert result == expected
    assert result.status == "failed"
    assert result.errors == ["interpreter_exception"]
