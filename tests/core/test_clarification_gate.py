from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from app.contracts.graph_contract import (
    FactNode,
    HumanInputNode,
    HypothesisNode,
    NodeStatus,
    SourceOfTruth,
    TruthConflict,
    ValidityWindow,
)
from app.core.clarification_gate import (
    ClarificationService,
    ClarificationStatus,
    ClarificationTicket,
)


class InMemoryGraphRepository:
    def __init__(self) -> None:
        self.tickets: dict[str, ClarificationTicket] = {}
        self.nodes: dict[str, object] = {}
        self.truth_conflicts: list[TruthConflict] = []

    def save_clarification_ticket(self, ticket: ClarificationTicket) -> None:
        self.tickets[ticket.ticket_id] = ticket

    def get_clarification_ticket(self, ticket_id: str) -> ClarificationTicket | None:
        return self.tickets.get(ticket_id)

    def save_graph_node(self, node: object) -> None:
        node_id = getattr(node, "node_id", None)
        if not isinstance(node_id, str):
            raise ValueError("node_id is required")
        self.nodes[node_id] = node

    def save_truth_conflict(self, conflict: TruthConflict) -> None:
        self.truth_conflicts.append(conflict)

    def mark_clarification_resolved(self, ticket_id: str, status: ClarificationStatus) -> None:
        ticket = self.tickets.get(ticket_id)
        if ticket is None:
            raise ValueError("ticket not found")
        ticket.status = status


def _hypothesis(cliente_id: str = "tenant-1", node_id: str = "hyp-1") -> HypothesisNode:
    return HypothesisNode(
        cliente_id=cliente_id,
        node_id=node_id,
        certainty=0.6,
        status=NodeStatus.AWAITING_CLARIFICATION,
        supporting_node_ids=["s1"],
    )


def _human_input(cliente_id: str = "tenant-1", node_id: str = "human-1") -> HumanInputNode:
    return HumanInputNode(
        cliente_id=cliente_id,
        node_id=node_id,
        certainty=0.8,
        status=NodeStatus.CONFIRMADO,
        input_text="Owner confirms",
    )


def _fact(cliente_id: str = "tenant-1", node_id: str = "fact-1") -> FactNode:
    return FactNode(
        cliente_id=cliente_id,
        node_id=node_id,
        certainty=0.9,
        status=NodeStatus.CONFIRMADO,
        source_of_truth=SourceOfTruth(evidence_ids=["ev-1"]),
    )


def test_crear_ticket_valido():
    repo = InMemoryGraphRepository()
    service = ClarificationService(repo)

    ticket = service.solicitar_clarificacion(_hypothesis(), "Please clarify margin change")

    assert ticket.status == ClarificationStatus.OPEN
    assert repo.get_clarification_ticket(ticket.ticket_id) is not None


def test_error_si_blocked_node_no_es_hypothesis():
    repo = InMemoryGraphRepository()
    service = ClarificationService(repo)

    with pytest.raises(ValueError, match="HypothesisNode"):
        service.solicitar_clarificacion(_fact(), "question")


def test_error_si_question_vacia():
    repo = InMemoryGraphRepository()
    service = ClarificationService(repo)

    with pytest.raises(ValueError, match="question"):
        service.solicitar_clarificacion(_hypothesis(), "   ")


def test_resolver_via_input_humano_crea_operational_truth_node():
    repo = InMemoryGraphRepository()
    service = ClarificationService(repo)
    ticket = service.solicitar_clarificacion(_hypothesis(), "question")

    result = service.resolver_via_input_humano(ticket.ticket_id, _human_input())

    assert result.operational_truth_node is not None
    assert result.status == ClarificationStatus.RESOLVED_BY_HUMAN_INPUT
    assert result.requires_recompute is False


def test_resolver_via_input_humano_crea_truth_conflict_si_fact_node_id_existe():
    repo = InMemoryGraphRepository()
    service = ClarificationService(repo)
    ticket = service.solicitar_clarificacion(
        _hypothesis(),
        "question",
        fact_node_id="fact-legacy-1",
    )

    result = service.resolver_via_input_humano(ticket.ticket_id, _human_input())

    assert result.truth_conflict is not None
    assert len(repo.truth_conflicts) == 1
    assert repo.truth_conflicts[0].fact_node_id == "fact-legacy-1"


def test_error_si_ticket_no_existe():
    repo = InMemoryGraphRepository()
    service = ClarificationService(repo)

    with pytest.raises(ValueError, match="not found"):
        service.resolver_via_input_humano("missing", _human_input())


def test_error_si_ticket_no_esta_open():
    repo = InMemoryGraphRepository()
    service = ClarificationService(repo)
    ticket = service.solicitar_clarificacion(_hypothesis(), "question")
    repo.mark_clarification_resolved(ticket.ticket_id, ClarificationStatus.REJECTED)

    with pytest.raises(ValueError, match="not OPEN"):
        service.resolver_via_input_humano(ticket.ticket_id, _human_input())


def test_error_si_cliente_id_no_coincide():
    repo = InMemoryGraphRepository()
    service = ClarificationService(repo)
    ticket = service.solicitar_clarificacion(_hypothesis(cliente_id="tenant-1"), "question")

    with pytest.raises(ValueError, match="cliente_id mismatch"):
        service.resolver_via_input_humano(ticket.ticket_id, _human_input(cliente_id="tenant-2"))


def test_resolver_via_nueva_evidencia_guarda_fact_node():
    repo = InMemoryGraphRepository()
    service = ClarificationService(repo)
    ticket = service.solicitar_clarificacion(_hypothesis(), "question")
    fact = _fact(node_id="fact-new-1")

    result = service.resolver_via_nueva_evidencia(ticket.ticket_id, [fact])

    assert "fact-new-1" in repo.nodes
    assert result.new_evidence_node_ids == ["fact-new-1"]


def test_resolver_via_nueva_evidencia_requires_recompute_true():
    repo = InMemoryGraphRepository()
    service = ClarificationService(repo)
    ticket = service.solicitar_clarificacion(_hypothesis(), "question")

    result = service.resolver_via_nueva_evidencia(ticket.ticket_id, [_fact()])

    assert result.requires_recompute is True
    assert result.status == ClarificationStatus.READY_FOR_RECOMPUTE


def test_resolver_via_nueva_evidencia_no_crea_operational_truth_node():
    repo = InMemoryGraphRepository()
    service = ClarificationService(repo)
    ticket = service.solicitar_clarificacion(_hypothesis(), "question")

    result = service.resolver_via_nueva_evidencia(ticket.ticket_id, [_fact()])

    assert result.operational_truth_node is None
    assert result.truth_conflict is None


def test_error_si_nueva_evidencia_vacia():
    repo = InMemoryGraphRepository()
    service = ClarificationService(repo)
    ticket = service.solicitar_clarificacion(_hypothesis(), "question")

    with pytest.raises(ValueError, match="must not be empty"):
        service.resolver_via_nueva_evidencia(ticket.ticket_id, [])


def test_error_si_nueva_evidencia_tiene_cliente_id_distinto():
    repo = InMemoryGraphRepository()
    service = ClarificationService(repo)
    ticket = service.solicitar_clarificacion(_hypothesis(cliente_id="tenant-1"), "question")
    fact_wrong_tenant = _fact(cliente_id="tenant-2")

    with pytest.raises(ValueError, match="cliente_id mismatch"):
        service.resolver_via_nueva_evidencia(ticket.ticket_id, [fact_wrong_tenant])
