from __future__ import annotations

import pytest

from app.contracts.graph_contract import (
    HypothesisNode,
    NodeStatus,
    SourceOfTruth,
    Tension,
    TensionKind,
    TensionStatus,
)
from app.core.clarification_gate import (
    ClarificationService,
    ClarificationStatus,
    ClarificationTicket,
)
from app.core.graph_resolution import evaluar_tension
from app.core.graph_jobs import (
    GraphJobStatus,
    evaluar_nodo_task_like,
    procesar_subgrafo,
)


class InMemoryGraphRepo:
    def __init__(self) -> None:
        self.nodes: dict[str, HypothesisNode] = {}
        self.saved_ids: list[str] = []

    def get_graph_node(self, node_id: str):
        return self.nodes.get(node_id)

    def list_dependent_nodes(self, root_node_id: str):
        return [node for node in self.nodes.values() if root_node_id in node.dependencies]

    def save_graph_node(self, node):
        self.nodes[node.node_id] = node
        self.saved_ids.append(node.node_id)


class InMemoryClarificationRepo:
    def __init__(self) -> None:
        self.tickets: dict[str, ClarificationTicket] = {}
        self.saved_nodes: dict[str, object] = {}
        self.saved_conflicts: list[object] = []

    def save_clarification_ticket(self, ticket: ClarificationTicket) -> None:
        self.tickets[ticket.ticket_id] = ticket

    def get_clarification_ticket(self, ticket_id: str) -> ClarificationTicket | None:
        return self.tickets.get(ticket_id)

    def save_graph_node(self, node: object) -> None:
        self.saved_nodes[getattr(node, "node_id")] = node

    def save_truth_conflict(self, conflict) -> None:
        self.saved_conflicts.append(conflict)

    def mark_clarification_resolved(self, ticket_id: str, status: ClarificationStatus) -> None:
        ticket = self.tickets.get(ticket_id)
        if ticket:
            ticket.status = status


def _hypothesis(
    node_id: str,
    cliente_id: str = "tenant-1",
    tensions: list[Tension] | None = None,
    dependencies: list[str] | None = None,
) -> HypothesisNode:
    return HypothesisNode(
        cliente_id=cliente_id,
        node_id=node_id,
        certainty=0.7,
        status=NodeStatus.PENDIENTE,
        tensions=tensions or [],
        dependencies=dependencies or [],
        supporting_node_ids=["support-1"],
        source_of_truth=SourceOfTruth(),
    )


def _blocking_tension() -> Tension:
    return Tension(
        kind=TensionKind.DOCUMENTAL,
        score=0.9,
        threshold=0.1,
        status=TensionStatus.BLOCKING,
    )


def _alert_tension() -> Tension:
    return Tension(
        kind=TensionKind.OPERACIONAL,
        score=0.05,
        threshold=0.5,
        status=TensionStatus.ALERT,
    )


def _service() -> ClarificationService:
    return ClarificationService(InMemoryClarificationRepo())


def test_root_sin_tension_completed():
    repo = InMemoryGraphRepo()
    root = _hypothesis("root")
    repo.nodes[root.node_id] = root

    result = procesar_subgrafo("tenant-1", "root", repo, _service())

    assert result.status == GraphJobStatus.COMPLETED


def test_root_blocking_paused_for_clarification():
    repo = InMemoryGraphRepo()
    root = _hypothesis("root", tensions=[_blocking_tension()])
    repo.nodes[root.node_id] = root

    result = procesar_subgrafo("tenant-1", "root", repo, _service())

    assert result.status == GraphJobStatus.PAUSED_FOR_CLARIFICATION
    assert result.clarification_ticket_id is not None


def test_root_blocking_guarda_status_awaiting_clarification():
    repo = InMemoryGraphRepo()
    root = _hypothesis("root", tensions=[_blocking_tension()])
    repo.nodes[root.node_id] = root

    procesar_subgrafo("tenant-1", "root", repo, _service())

    assert repo.nodes["root"].status == NodeStatus.AWAITING_CLARIFICATION


def test_dependiente_blocking_pausa():
    repo = InMemoryGraphRepo()
    root = _hypothesis("root", tensions=[])
    child = _hypothesis("child", tensions=[_blocking_tension()], dependencies=["root"])
    repo.nodes[root.node_id] = root
    repo.nodes[child.node_id] = child

    result = procesar_subgrafo("tenant-1", "root", repo, _service())

    assert result.status == GraphJobStatus.PAUSED_FOR_CLARIFICATION
    assert repo.nodes["child"].status == NodeStatus.AWAITING_CLARIFICATION


def test_cliente_id_mismatch_falla():
    repo = InMemoryGraphRepo()
    root = _hypothesis("root", cliente_id="tenant-A")
    repo.nodes[root.node_id] = root

    with pytest.raises(ValueError, match="cliente_id mismatch"):
        procesar_subgrafo("tenant-B", "root", repo, _service())


def test_nodo_raiz_inexistente_falla():
    repo = InMemoryGraphRepo()

    with pytest.raises(ValueError, match="nodo raiz no existe"):
        procesar_subgrafo("tenant-1", "missing", repo, _service())


def test_no_se_crea_ticket_si_no_hay_blocking():
    repo = InMemoryGraphRepo()
    root = _hypothesis("root")
    child = _hypothesis("child", tensions=[_alert_tension()], dependencies=["root"])
    repo.nodes[root.node_id] = root
    repo.nodes[child.node_id] = child

    result = procesar_subgrafo("tenant-1", "root", repo, _service())

    assert result.status == GraphJobStatus.COMPLETED
    assert result.clarification_ticket_id is None


def test_se_crea_ticket_con_question_no_vacia():
    repo = InMemoryGraphRepo()
    clarification_repo = InMemoryClarificationRepo()
    service = ClarificationService(clarification_repo)
    root = _hypothesis("root", tensions=[_blocking_tension()])
    repo.nodes[root.node_id] = root

    result = procesar_subgrafo("tenant-1", "root", repo, service)
    ticket = clarification_repo.get_clarification_ticket(result.clarification_ticket_id or "")

    assert ticket is not None
    assert ticket.question.strip() != ""


def test_evaluated_node_ids_contiene_nodos_evaluados():
    repo = InMemoryGraphRepo()
    root = _hypothesis("root")
    child = _hypothesis("child", dependencies=["root"])
    repo.nodes[root.node_id] = root
    repo.nodes[child.node_id] = child

    result = procesar_subgrafo("tenant-1", "root", repo, _service())

    assert "root" in result.evaluated_node_ids
    assert "child" in result.evaluated_node_ids


def test_no_mutar_logica_de_graph_resolution():
    node = _hypothesis("node-1", tensions=[_alert_tension()])

    assert evaluar_nodo_task_like(node, 0.1) == evaluar_tension(node, 0.1)
