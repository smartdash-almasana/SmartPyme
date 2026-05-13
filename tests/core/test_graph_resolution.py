from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

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
    TensionStatus,
    ValidityWindow,
)
from app.core.graph_resolution import (
    bloquear_dependientes,
    crear_truth_conflict,
    evaluar_tension,
    propagar_certeza,
    puede_estabilizar,
    requiere_clarificacion,
)


def _base(node_id: str) -> dict:
    return {
        "cliente_id": "tenant-1",
        "node_id": node_id,
        "certainty": 0.8,
        "status": NodeStatus.PENDIENTE,
    }


def _window() -> ValidityWindow:
    now = datetime.now(UTC)
    return ValidityWindow(valid_from=now, valid_until=now + timedelta(days=2))


def test_tension_ok_without_tensions():
    node = SignalNode(**_base("s1"))
    assert evaluar_tension(node, 0.5) == TensionStatus.OK


def test_tension_alert_by_score_gt_zero():
    node = SignalNode(
        **_base("s1"),
        tensions=[Tension(kind=TensionKind.DOCUMENTAL, score=0.1, threshold=1.0)],
    )
    assert evaluar_tension(node, 0.5) == TensionStatus.ALERT


def test_tension_blocking_by_score_gt_threshold():
    node = SignalNode(
        **_base("s1"),
        tensions=[Tension(kind=TensionKind.FUENTE, score=0.9, threshold=1.0)],
    )
    assert evaluar_tension(node, 0.5) == TensionStatus.BLOCKING


def test_tension_blocking_by_status_blocking():
    node = SignalNode(
        **_base("s1"),
        tensions=[
            Tension(
                kind=TensionKind.OPERACIONAL,
                score=0.1,
                threshold=1.0,
                status=TensionStatus.BLOCKING,
            )
        ],
    )
    assert evaluar_tension(node, 0.5) == TensionStatus.BLOCKING


def test_error_on_negative_threshold():
    node = SignalNode(**_base("s1"))
    with pytest.raises(ValueError, match="policy_threshold"):
        evaluar_tension(node, -0.1)


def test_propagar_certeza_uses_minimum():
    p1 = SignalNode(cliente_id="tenant-1", node_id="p1", certainty=0.9, status=NodeStatus.PENDIENTE)
    p2 = SignalNode(cliente_id="tenant-1", node_id="p2", certainty=0.4, status=NodeStatus.PENDIENTE)
    assert propagar_certeza([p1, p2]) == pytest.approx(0.4)


def test_propagar_certeza_applies_degradation_factor():
    p1 = SignalNode(cliente_id="tenant-1", node_id="p1", certainty=0.9, status=NodeStatus.PENDIENTE)
    p2 = SignalNode(cliente_id="tenant-1", node_id="p2", certainty=0.5, status=NodeStatus.PENDIENTE)
    assert propagar_certeza([p1, p2], degradation_factor=0.5) == pytest.approx(0.25)


def test_error_when_parents_empty():
    with pytest.raises(ValueError, match="parent_nodes"):
        propagar_certeza([])


def test_bloquear_dependientes_does_not_mutate_input():
    root = SignalNode(**_base("root"))
    child = SignalNode(**_base("child"), dependencies=["root"])
    graph = {"root": root, "child": child}

    result = bloquear_dependientes(graph, "root")

    assert graph["child"].status == NodeStatus.PENDIENTE
    assert result["child"].status == NodeStatus.BLOCKED_BY_PARENT


def test_bloquear_dependientes_blocks_descendants_recursively():
    root = SignalNode(**_base("root"))
    child = SignalNode(**_base("child"), dependencies=["root"])
    grandchild = SignalNode(**_base("grandchild"), dependencies=["child"])
    graph = {"root": root, "child": child, "grandchild": grandchild}

    result = bloquear_dependientes(graph, "root")

    assert result["root"].status == NodeStatus.PENDIENTE
    assert result["child"].status == NodeStatus.BLOCKED_BY_PARENT
    assert result["grandchild"].status == NodeStatus.BLOCKED_BY_PARENT


def test_requiere_clarificacion_true_by_blocking():
    node = SignalNode(
        **_base("s1"),
        tensions=[Tension(kind=TensionKind.DOCUMENTAL, score=0.9, threshold=0.9)],
    )
    assert requiere_clarificacion(node, 0.5) is True


def test_puede_estabilizar_true_with_fact_node():
    hypothesis = HypothesisNode(**_base("h1"), supporting_node_ids=["s1"])
    fact = FactNode(**_base("f1"), source_of_truth=SourceOfTruth(evidence_ids=["ev-1"]))
    assert puede_estabilizar(hypothesis, evidence_nodes=[fact]) is True


def test_puede_estabilizar_true_with_human_input_node():
    hypothesis = HypothesisNode(**_base("h1"), supporting_node_ids=["s1"])
    human_input = HumanInputNode(**_base("hi1"), input_text="Owner confirms")
    assert puede_estabilizar(hypothesis, human_input=human_input) is True


def test_puede_estabilizar_false_without_evidence_or_human_input():
    hypothesis = HypothesisNode(**_base("h1"), supporting_node_ids=["s1"])
    assert puede_estabilizar(hypothesis) is False


def test_crear_truth_conflict_valid():
    fact = FactNode(**_base("f1"), source_of_truth=SourceOfTruth(evidence_ids=["ev-1"]))
    operational_truth = OperationalTruthNode(
        **_base("ot1"),
        validity_window=_window(),
        human_input_id="human-1",
    )

    conflict = crear_truth_conflict(
        fact=fact,
        operational_truth=operational_truth,
        conflict_kind=TensionKind.DOCUMENTAL,
        explanation="Document mismatch",
    )

    assert conflict.cliente_id == "tenant-1"
    assert conflict.fact_node_id == "f1"
    assert conflict.operational_truth_node_id == "ot1"
    assert conflict.conflict_kind == "documental"


def test_crear_truth_conflict_fails_when_cliente_id_differs():
    fact = FactNode(
        cliente_id="tenant-1",
        node_id="f1",
        certainty=0.8,
        source_of_truth=SourceOfTruth(evidence_ids=["ev-1"]),
    )
    operational_truth = OperationalTruthNode(
        cliente_id="tenant-2",
        node_id="ot1",
        certainty=0.8,
        validity_window=_window(),
        human_input_id="human-1",
    )

    with pytest.raises(ValueError, match="cliente_id mismatch"):
        crear_truth_conflict(
            fact=fact,
            operational_truth=operational_truth,
            conflict_kind=TensionKind.DOCUMENTAL,
            explanation="Mismatch",
        )
