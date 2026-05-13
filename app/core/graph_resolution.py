from __future__ import annotations

from collections import deque
from typing import Iterable

from app.contracts.graph_contract import (
    BaseGraphNode,
    FactNode,
    HumanInputNode,
    HypothesisNode,
    NodeStatus,
    OperationalTruthNode,
    TensionKind,
    TensionStatus,
    TruthConflict,
)

SmartGraphNode = BaseGraphNode


def _status_value(status: object) -> str:
    return status.value if hasattr(status, "value") else str(status)


def evaluar_tension(node: SmartGraphNode, policy_threshold: float) -> TensionStatus:
    if policy_threshold < 0:
        raise ValueError("policy_threshold must be >= 0")

    tensions = list(getattr(node, "tensions", []) or [])
    for tension in tensions:
        if _status_value(tension.status).lower() == TensionStatus.BLOCKING.value:
            return TensionStatus.BLOCKING

    for tension in tensions:
        if tension.score > policy_threshold:
            return TensionStatus.BLOCKING

    for tension in tensions:
        if _status_value(tension.status).lower() == TensionStatus.ALERT.value:
            return TensionStatus.ALERT

    for tension in tensions:
        if tension.score > 0:
            return TensionStatus.ALERT

    return TensionStatus.OK


def propagar_certeza(parent_nodes: Iterable[SmartGraphNode], degradation_factor: float = 1.0) -> float:
    parent_nodes = list(parent_nodes)
    if not parent_nodes:
        raise ValueError("parent_nodes must not be empty")
    if degradation_factor < 0 or degradation_factor > 1:
        raise ValueError("degradation_factor must be between 0 and 1")
    return min(parent.certainty for parent in parent_nodes) * degradation_factor


def bloquear_dependientes(
    graph: dict[str, SmartGraphNode], root_node_id: str
) -> dict[str, SmartGraphNode]:
    if root_node_id not in graph:
        raise ValueError("root_node_id not found in graph")

    cloned_graph = {node_id: node.model_copy(deep=True) for node_id, node in graph.items()}
    queue: deque[str] = deque([root_node_id])
    visited: set[str] = {root_node_id}

    while queue:
        current = queue.popleft()
        for candidate_id, candidate in cloned_graph.items():
            if candidate_id in visited:
                continue
            dependencies = getattr(candidate, "dependencies", []) or []
            if current in dependencies:
                candidate.status = NodeStatus.BLOCKED_BY_PARENT
                visited.add(candidate_id)
                queue.append(candidate_id)

    return cloned_graph


def requiere_clarificacion(node: SmartGraphNode, policy_threshold: float) -> bool:
    if evaluar_tension(node, policy_threshold) == TensionStatus.BLOCKING:
        return True
    return node.status in (NodeStatus.AMBIGUOUS, NodeStatus.AWAITING_CLARIFICATION)


def puede_estabilizar(
    hypothesis_node: HypothesisNode,
    evidence_nodes: Iterable[SmartGraphNode] | None = None,
    human_input: HumanInputNode | None = None,
) -> bool:
    if not isinstance(hypothesis_node, HypothesisNode):
        raise ValueError("hypothesis_node must be HypothesisNode")

    if evidence_nodes:
        if any(isinstance(node, FactNode) for node in evidence_nodes):
            return True

    if isinstance(human_input, HumanInputNode):
        return True

    return False


def crear_truth_conflict(
    fact: FactNode,
    operational_truth: OperationalTruthNode,
    conflict_kind: TensionKind,
    explanation: str,
) -> TruthConflict:
    if not isinstance(fact, FactNode):
        raise ValueError("fact must be FactNode")
    if not isinstance(operational_truth, OperationalTruthNode):
        raise ValueError("operational_truth must be OperationalTruthNode")
    if not isinstance(conflict_kind, TensionKind):
        raise ValueError("conflict_kind must be TensionKind")
    if not isinstance(explanation, str) or not explanation.strip():
        raise ValueError("explanation is required")
    if fact.cliente_id != operational_truth.cliente_id:
        raise ValueError("cliente_id mismatch between fact and operational_truth")

    return TruthConflict(
        cliente_id=fact.cliente_id,
        fact_node_id=fact.node_id,
        operational_truth_node_id=operational_truth.node_id,
        conflict_kind=conflict_kind.value,
        explanation=explanation.strip(),
        status=TensionStatus.BLOCKING,
    )
