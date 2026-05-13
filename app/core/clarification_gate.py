from __future__ import annotations

from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import Protocol
from uuid import uuid4

from pydantic import BaseModel, Field, model_validator

from app.contracts.graph_contract import (
    FactNode,
    HumanInputNode,
    HypothesisNode,
    NodeStatus,
    OperationalTruthNode,
    TensionStatus,
    TruthConflict,
    ValidityWindow,
)


def _require_non_empty(value: str, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} is required")


class ClarificationStatus(str, Enum):
    OPEN = "OPEN"
    RESOLVED_BY_HUMAN_INPUT = "RESOLVED_BY_HUMAN_INPUT"
    RESOLVED_BY_NEW_EVIDENCE = "RESOLVED_BY_NEW_EVIDENCE"
    READY_FOR_RECOMPUTE = "READY_FOR_RECOMPUTE"
    REJECTED = "REJECTED"


class ClarificationResolutionKind(str, Enum):
    HUMAN_INPUT = "HUMAN_INPUT"
    NEW_EVIDENCE = "NEW_EVIDENCE"


class ClarificationTicket(BaseModel):
    ticket_id: str
    cliente_id: str
    blocked_node_id: str
    question: str
    status: ClarificationStatus
    fact_node_id: str | None = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @model_validator(mode="after")
    def _validate(self) -> ClarificationTicket:
        _require_non_empty(self.ticket_id, "ticket_id")
        _require_non_empty(self.cliente_id, "cliente_id")
        _require_non_empty(self.blocked_node_id, "blocked_node_id")
        _require_non_empty(self.question, "question")
        if self.fact_node_id is not None:
            _require_non_empty(self.fact_node_id, "fact_node_id")
        return self


class ClarificationResult(BaseModel):
    ticket_id: str
    cliente_id: str
    status: ClarificationStatus
    resolution_kind: ClarificationResolutionKind
    operational_truth_node: OperationalTruthNode | None = Field(default=None)
    truth_conflict: TruthConflict | None = Field(default=None)
    new_evidence_node_ids: list[str] = Field(default_factory=list)
    requires_recompute: bool


class GraphRepositoryProtocol(Protocol):
    def save_clarification_ticket(self, ticket: ClarificationTicket) -> None: ...

    def get_clarification_ticket(self, ticket_id: str) -> ClarificationTicket | None: ...

    def save_graph_node(self, node: object) -> None: ...

    def save_truth_conflict(self, conflict: TruthConflict) -> None: ...

    def mark_clarification_resolved(self, ticket_id: str, status: ClarificationStatus) -> None: ...


class ClarificationService:
    def __init__(self, repository: GraphRepositoryProtocol) -> None:
        self.repository = repository

    def solicitar_clarificacion(
        self,
        blocked_node: HypothesisNode,
        question: str,
        fact_node_id: str | None = None,
    ) -> ClarificationTicket:
        if not isinstance(blocked_node, HypothesisNode):
            raise ValueError("blocked_node must be HypothesisNode")
        _require_non_empty(question, "question")
        if fact_node_id is not None:
            _require_non_empty(fact_node_id, "fact_node_id")

        ticket = ClarificationTicket(
            ticket_id=f"clarif-{uuid4().hex}",
            cliente_id=blocked_node.cliente_id,
            blocked_node_id=blocked_node.node_id,
            question=question.strip(),
            status=ClarificationStatus.OPEN,
            fact_node_id=fact_node_id,
        )
        self.repository.save_clarification_ticket(ticket)
        return ticket

    def resolver_via_input_humano(
        self, ticket_id: str, input_node: HumanInputNode
    ) -> ClarificationResult:
        _require_non_empty(ticket_id, "ticket_id")
        if not isinstance(input_node, HumanInputNode):
            raise ValueError("input_node must be HumanInputNode")

        ticket = self.repository.get_clarification_ticket(ticket_id)
        if ticket is None:
            raise ValueError("clarification ticket not found")
        if ticket.status != ClarificationStatus.OPEN:
            raise ValueError("clarification ticket is not OPEN")
        if ticket.cliente_id != input_node.cliente_id:
            raise ValueError("cliente_id mismatch between ticket and input_node")

        now = datetime.now(UTC)
        operational_truth = OperationalTruthNode(
            cliente_id=ticket.cliente_id,
            node_id=f"op-truth-{uuid4().hex}",
            certainty=input_node.certainty,
            status=NodeStatus.CONFIRMADO,
            validity_window=ValidityWindow(
                valid_from=now,
                valid_until=now + timedelta(days=30),
            ),
            human_input_id=input_node.node_id,
        )
        self.repository.save_graph_node(operational_truth)

        truth_conflict: TruthConflict | None = None
        if ticket.fact_node_id:
            truth_conflict = TruthConflict(
                cliente_id=ticket.cliente_id,
                fact_node_id=ticket.fact_node_id,
                operational_truth_node_id=operational_truth.node_id,
                conflict_kind="operacional",
                explanation=f"Human input resolution for ticket {ticket.ticket_id}",
                status=TensionStatus.BLOCKING,
            )
            self.repository.save_truth_conflict(truth_conflict)

        self.repository.mark_clarification_resolved(
            ticket.ticket_id, ClarificationStatus.RESOLVED_BY_HUMAN_INPUT
        )

        return ClarificationResult(
            ticket_id=ticket.ticket_id,
            cliente_id=ticket.cliente_id,
            status=ClarificationStatus.RESOLVED_BY_HUMAN_INPUT,
            resolution_kind=ClarificationResolutionKind.HUMAN_INPUT,
            operational_truth_node=operational_truth,
            truth_conflict=truth_conflict,
            new_evidence_node_ids=[],
            requires_recompute=False,
        )

    def resolver_via_nueva_evidencia(
        self, ticket_id: str, nuevos_fact_nodes: list[FactNode]
    ) -> ClarificationResult:
        _require_non_empty(ticket_id, "ticket_id")
        ticket = self.repository.get_clarification_ticket(ticket_id)
        if ticket is None:
            raise ValueError("clarification ticket not found")
        if ticket.status != ClarificationStatus.OPEN:
            raise ValueError("clarification ticket is not OPEN")
        if not nuevos_fact_nodes:
            raise ValueError("nuevos_fact_nodes must not be empty")

        for node in nuevos_fact_nodes:
            if not isinstance(node, FactNode):
                raise ValueError("all nuevos_fact_nodes must be FactNode")
            if node.cliente_id != ticket.cliente_id:
                raise ValueError("cliente_id mismatch between ticket and fact node")
            self.repository.save_graph_node(node)

        resolved_status = ClarificationStatus.READY_FOR_RECOMPUTE
        self.repository.mark_clarification_resolved(ticket.ticket_id, resolved_status)

        return ClarificationResult(
            ticket_id=ticket.ticket_id,
            cliente_id=ticket.cliente_id,
            status=resolved_status,
            resolution_kind=ClarificationResolutionKind.NEW_EVIDENCE,
            operational_truth_node=None,
            truth_conflict=None,
            new_evidence_node_ids=[node.node_id for node in nuevos_fact_nodes],
            requires_recompute=True,
        )
