from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.ai.adapters.owner_message_interpreter_adapter import LocalOwnerMessageInterpreterAdapter
from app.ai.schemas.owner_message_interpretation import OwnerMessageInterpretation


def test_adapter_returns_valid_interpretation_from_injected_interpreter():
    expected = OwnerMessageInterpretation(
        intent="consultar_stock",
        entities=["stock"],
        variables=["cantidad"],
        evidence=["excel de inventario"],
        doubts=["deposito no especificado"],
        confidence=0.7,
    )

    adapter = LocalOwnerMessageInterpreterAdapter(interpreter=lambda message: expected)

    result = adapter.interpret("Revisame el stock del Excel")

    assert result == expected


def test_adapter_returns_empty_interpretation_when_interpreter_returns_none():
    adapter = LocalOwnerMessageInterpreterAdapter(interpreter=lambda message: None)

    result = adapter.interpret("Revisame ventas")

    assert result == LocalOwnerMessageInterpreterAdapter.empty()


def test_adapter_returns_empty_interpretation_when_interpreter_raises():
    def failing_interpreter(message: str):
        raise RuntimeError("soft interpreter failed")

    adapter = LocalOwnerMessageInterpreterAdapter(interpreter=failing_interpreter)

    result = adapter.interpret("Revisame ventas")

    assert result == LocalOwnerMessageInterpreterAdapter.empty()


def test_adapter_returns_empty_interpretation_for_empty_message():
    adapter = LocalOwnerMessageInterpreterAdapter(
        interpreter=lambda message: OwnerMessageInterpretation(intent="should_not_run")
    )

    result = adapter.interpret("   ")

    assert result == LocalOwnerMessageInterpreterAdapter.empty()


def test_adapter_rejects_non_validated_raw_output():
    adapter = LocalOwnerMessageInterpreterAdapter(interpreter=lambda message: {"intent": "raw"})

    result = adapter.interpret("Revisame ventas")

    assert result == LocalOwnerMessageInterpreterAdapter.empty()
