from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError

from app.contracts.graph_contract import (
    FactNode,
    HumanInputNode,
    HypothesisNode,
    NodeStatus,
    OperationalTruthNode,
    SignalNode,
    SourceOfTruth,
    Tension,
    TensionKind,
    TruthConflict,
    ValidityWindow,
)


def _base_kwargs() -> dict:
    return {
        "cliente_id": "tenant-1",
        "node_id": "node-1",
        "status": NodeStatus.PENDIENTE,
        "certainty": 0.7,
    }


def _window() -> ValidityWindow:
    now = datetime.now(UTC)
    return ValidityWindow(valid_from=now, valid_until=now + timedelta(days=7))


def test_fact_node_valid_with_evidence_id():
    node = FactNode(
        **_base_kwargs(),
        source_of_truth=SourceOfTruth(evidence_ids=["ev-1"]),
    )
    assert node.source_of_truth.evidence_ids == ["ev-1"]


def test_signal_node_valid_with_formula_id():
    node = SignalNode(
        **_base_kwargs(),
        source_of_truth=SourceOfTruth(formula_id="formula-1"),
    )
    assert node.source_of_truth.formula_id == "formula-1"


def test_hypothesis_node_valid():
    node = HypothesisNode(
        **_base_kwargs(),
        supporting_node_ids=["signal-1"],
    )
    assert node.supporting_node_ids == ["signal-1"]


def test_human_input_node_valid():
    node = HumanInputNode(
        **_base_kwargs(),
        input_text="Owner says margin dropped last week",
    )
    assert node.input_text


def test_operational_truth_node_valid_with_human_input_and_window():
    node = OperationalTruthNode(
        **_base_kwargs(),
        validity_window=_window(),
        human_input_id="human-1",
    )
    assert node.human_input_id == "human-1"


def test_truth_conflict_valid():
    conflict = TruthConflict(
        cliente_id="tenant-1",
        fact_node_id="fact-1",
        operational_truth_node_id="op-1",
        conflict_kind="documental_vs_operacional",
        explanation="Mismatch between accounting fact and owner operational truth",
    )
    assert conflict.conflict_kind == "documental_vs_operacional"


def test_error_on_empty_cliente_id():
    with pytest.raises(ValidationError, match="cliente_id"):
        FactNode(
            cliente_id="",
            node_id="node-1",
            certainty=0.8,
            source_of_truth=SourceOfTruth(evidence_ids=["ev-1"]),
        )


def test_error_on_certainty_out_of_range():
    with pytest.raises(ValidationError, match="certainty"):
        SignalNode(
            cliente_id="tenant-1",
            node_id="node-1",
            certainty=1.2,
        )


def test_error_on_negative_tension():
    with pytest.raises(ValidationError, match="score"):
        Tension(kind=TensionKind.DOCUMENTAL, score=-0.1, threshold=0.0)


def test_error_if_fact_node_only_has_human_input_id():
    with pytest.raises(ValidationError, match="FactNode requires evidence_ids or formula_id"):
        FactNode(
            **_base_kwargs(),
            source_of_truth=SourceOfTruth(human_input_id="human-1"),
        )


def test_error_if_operational_truth_node_has_no_validity_window():
    with pytest.raises(ValidationError, match="validity_window"):
        OperationalTruthNode(
            **_base_kwargs(),
            human_input_id="human-1",
        )


def test_error_if_operational_truth_node_has_no_human_input_or_policy():
    with pytest.raises(ValidationError, match="OperationalTruthNode requires human_input_id or policy_id"):
        OperationalTruthNode(
            **_base_kwargs(),
            validity_window=_window(),
        )


def test_error_if_truth_conflict_has_empty_ids():
    with pytest.raises(ValidationError, match="fact_node_id"):
        TruthConflict(
            cliente_id="tenant-1",
            fact_node_id="",
            operational_truth_node_id="",
            conflict_kind="kind",
            explanation="text",
        )
