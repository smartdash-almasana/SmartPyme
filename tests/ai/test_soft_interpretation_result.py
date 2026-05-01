from __future__ import annotations

import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.ai.schemas.owner_message_interpretation import OwnerMessageInterpretation
from app.ai.schemas.soft_interpretation_result import SoftInterpretationResult


def test_ok_result_wraps_valid_interpretation():
    interpretation = OwnerMessageInterpretation(intent="consultar_stock", confidence=0.9)

    result = SoftInterpretationResult.ok(
        raw_message="Revisame stock",
        interpretation=interpretation,
    )

    assert result.raw_message == "Revisame stock"
    assert result.interpretation == interpretation
    assert result.status == "ok"
    assert result.source == "local_adapter"
    assert result.errors == []


def test_empty_result_uses_empty_valid_interpretation():
    result = SoftInterpretationResult.empty(raw_message="   ")

    assert result.raw_message == "   "
    assert result.interpretation == OwnerMessageInterpretation()
    assert result.status == "empty"
    assert result.source == "local_adapter"
    assert result.errors == []


def test_failed_result_uses_empty_interpretation_and_errors():
    result = SoftInterpretationResult.failed(
        raw_message="Revisame ventas",
        errors=["interpreter_failed"],
    )

    assert result.raw_message == "Revisame ventas"
    assert result.interpretation == OwnerMessageInterpretation()
    assert result.status == "failed"
    assert result.source == "local_adapter"
    assert result.errors == ["interpreter_failed"]


def test_invalid_status_is_rejected():
    with pytest.raises(ValidationError):
        SoftInterpretationResult(
            raw_message="x",
            interpretation=OwnerMessageInterpretation(),
            status="decided",
            source="local_adapter",
            errors=[],
        )


def test_invalid_source_is_rejected():
    with pytest.raises(ValidationError):
        SoftInterpretationResult(
            raw_message="x",
            interpretation=OwnerMessageInterpretation(),
            status="ok",
            source="pipeline",
            errors=[],
        )
