from __future__ import annotations

from enum import Enum
from typing import Protocol

from pydantic import BaseModel, Field

from app.contracts.graph_contract import (
    BaseGraphNode,
    HypothesisNode,
    NodeStatus,
    TensionStatus,
)
from app.core.clarification_gate import ClarificationService, ClarificationTicket
from app.core.graph_resolution import evaluar_tension

try:
    from prefect import flow as _prefect_flow
    from prefect import task as _prefect_task
except Exception:  # pragma: no cover
    _prefect_flow = None
    _prefect_task = None


def _identity_decorator(func):
    return func


task = _prefect_task if _prefect_task is not None else _identity_decorator
flow = _prefect_flow if _prefect_flow is not None else _identity_decorator


class GraphJobStatus(str, Enum):
    COMPLETED = "COMPLETED"
    PAUSED_FOR_CLARIFICATION = "PAUSED_FOR_CLARIFICATION"
    FAILED = "FAILED"


class GraphJobResult(BaseModel):
    cliente_id: str
    root_node_id: str
    status: GraphJobStatus
    evaluated_node_ids: list[str] = Field(default_factory=list)
    clarification_ticket_id: str | None = Field(default=None)
    reason: str | None = Field(default=None)


class GraphJobRepositoryProtocol(Protocol):
    def get_graph_node(self, node_id: str) -> BaseGraphNode | None: ...

    def list_dependent_nodes(self, root_node_id: str) -> list[BaseGraphNode]: ...

    def save_graph_node(self, node: BaseGraphNode) -> None: ...


@task
def evaluar_nodo_task_like(node: BaseGraphNode, policy_threshold: float) -> TensionStatus:
    return evaluar_tension(node, policy_threshold)


@task
def gestionar_bloqueo_task_like(
    clarification_service: ClarificationService,
    blocked_node: HypothesisNode,
    question: str,
) -> ClarificationTicket:
    return clarification_service.solicitar_clarificacion(
        blocked_node=blocked_node,
        question=question,
    )


@flow
def procesar_subgrafo(
    cliente_id: str,
    nodo_raiz_id: str,
    graph_repo: GraphJobRepositoryProtocol,
    clarification_service: ClarificationService,
    policy_threshold: float = 0.1,
) -> GraphJobResult:
    root_node = graph_repo.get_graph_node(nodo_raiz_id)
    if root_node is None:
        raise ValueError("nodo raiz no existe")
    if root_node.cliente_id != cliente_id:
        raise ValueError("cliente_id mismatch")

    evaluated_ids: list[str] = [root_node.node_id]
    root_tension = evaluar_nodo_task_like(root_node, policy_threshold)
    if root_tension == TensionStatus.BLOCKING:
        root_node.status = NodeStatus.AWAITING_CLARIFICATION
        graph_repo.save_graph_node(root_node)
        if not isinstance(root_node, HypothesisNode):
            raise ValueError("blocked root node must be HypothesisNode for clarification")
        ticket = gestionar_bloqueo_task_like(
            clarification_service,
            root_node,
            "Se requiere clarificacion para continuar el procesamiento del subgrafo.",
        )
        return GraphJobResult(
            cliente_id=cliente_id,
            root_node_id=nodo_raiz_id,
            status=GraphJobStatus.PAUSED_FOR_CLARIFICATION,
            evaluated_node_ids=evaluated_ids,
            clarification_ticket_id=ticket.ticket_id,
            reason="root node is blocking",
        )

    dependent_nodes = graph_repo.list_dependent_nodes(nodo_raiz_id)
    for node in dependent_nodes:
        if node.cliente_id != cliente_id:
            raise ValueError("cliente_id mismatch")
        evaluated_ids.append(node.node_id)
        tension_status = evaluar_nodo_task_like(node, policy_threshold)
        graph_repo.save_graph_node(node)
        if tension_status == TensionStatus.BLOCKING:
            node.status = NodeStatus.AWAITING_CLARIFICATION
            graph_repo.save_graph_node(node)
            if not isinstance(node, HypothesisNode):
                raise ValueError("blocked dependent node must be HypothesisNode for clarification")
            ticket = gestionar_bloqueo_task_like(
                clarification_service,
                node,
                "Se requiere clarificacion para un nodo dependiente bloqueado.",
            )
            return GraphJobResult(
                cliente_id=cliente_id,
                root_node_id=nodo_raiz_id,
                status=GraphJobStatus.PAUSED_FOR_CLARIFICATION,
                evaluated_node_ids=evaluated_ids,
                clarification_ticket_id=ticket.ticket_id,
                reason=f"dependent node {node.node_id} is blocking",
            )

    return GraphJobResult(
        cliente_id=cliente_id,
        root_node_id=nodo_raiz_id,
        status=GraphJobStatus.COMPLETED,
        evaluated_node_ids=evaluated_ids,
        clarification_ticket_id=None,
        reason=None,
    )
