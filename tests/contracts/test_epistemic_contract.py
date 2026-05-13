from __future__ import annotations

import pytest

from app.contracts.epistemic_contract import (
    EpistemicReadinessState,
    EpistemicRegion,
    MathFunctionSpec,
    UnknownEntity,
    UnknownSourceRequired,
)


def test_unknown_entity_requires_non_empty_name() -> None:
    with pytest.raises(ValueError, match="unknown name is required"):
        UnknownEntity(
            name=" ",
            description="Ventas por producto del período analizado.",
            source_required=UnknownSourceRequired.DOCUMENT,
        )


def test_unknown_entity_accepts_blocked_functions_and_formats() -> None:
    unknown = UnknownEntity(
        name="ventas_por_producto",
        description="Sin ventas por producto no se puede calcular rotación ni distinguir mix.",
        source_required=UnknownSourceRequired.DOCUMENT,
        blocks_functions=["rotacion_stock"],
        accepted_formats=["xlsx", "csv", "manual_table"],
    )

    assert unknown.name == "ventas_por_producto"
    assert unknown.source_required == UnknownSourceRequired.DOCUMENT
    assert unknown.blocks_functions == ["rotacion_stock"]


def test_math_function_spec_rejects_duplicate_inputs() -> None:
    with pytest.raises(ValueError, match="required_inputs cannot contain duplicates"):
        MathFunctionSpec(
            function_name="rotacion_stock",
            required_inputs=["ventas_por_producto", "ventas_por_producto"],
            output_entity="rotacion",
        )


def test_math_function_spec_declares_deterministic_inputs_and_output() -> None:
    spec = MathFunctionSpec(
        function_name="rotacion_stock",
        required_inputs=["ventas_por_producto", "stock_actual"],
        output_entity="rotacion",
        risk_level="LOW",
        reversible=True,
    )

    assert spec.required_inputs == ["ventas_por_producto", "stock_actual"]
    assert spec.output_entity == "rotacion"


def test_epistemic_readiness_requires_next_observable_when_unknowns_exist() -> None:
    unknown = UnknownEntity(
        name="ventas_por_producto",
        description="Requerido para calcular rotación.",
        source_required=UnknownSourceRequired.DOCUMENT,
    )

    with pytest.raises(ValueError, match="next_required_observable is required"):
        EpistemicReadinessState(
            cliente_id="C1",
            region=EpistemicRegion.STATE_EVIDENCE_PARTIAL,
            critical_unknowns=[unknown],
            collapse_reason="Evidencia parcial con incógnita crítica.",
        )


def test_epistemic_readiness_state_models_next_piece_request() -> None:
    unknown = UnknownEntity(
        name="ventas_por_producto",
        description="Sin ventas por producto no se puede calcular rotación.",
        source_required=UnknownSourceRequired.DOCUMENT,
        blocks_functions=["rotacion_stock"],
        accepted_formats=["xlsx", "csv"],
    )

    state = EpistemicReadinessState(
        cliente_id="C1",
        region=EpistemicRegion.STATE_EVIDENCE_PARTIAL,
        present_observables=["stock_actual"],
        critical_unknowns=[unknown],
        blocked_functions=["rotacion_stock"],
        enabled_functions=["abrir_caso_exploratorio"],
        allowed_transitions=["ASK_NEXT_OBSERVABLE", "OPEN_CASE"],
        forbidden_transitions=["CREATE_JOB", "EXECUTE_TOOL"],
        next_required_observable="ventas_por_producto",
        next_action_prompt="Para avanzar necesito ventas por producto del período analizado.",
        collapse_reason="Hay stock actual, pero falta ventas por producto para calcular rotación.",
    )

    assert state.region == EpistemicRegion.STATE_EVIDENCE_PARTIAL
    assert state.next_required_observable == "ventas_por_producto"
    assert "CREATE_JOB" in state.forbidden_transitions
