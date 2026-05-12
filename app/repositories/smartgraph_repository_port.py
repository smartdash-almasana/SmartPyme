"""Repository port for SmartGraph persistence.

This module defines the storage boundary for SmartGraph without binding the
clinical-operational core to a concrete database implementation.

Rules:
- no LLM writes directly to SmartGraph persistence;
- every operation is tenant-scoped;
- inferred or hypothesis claims must remain distinguishable from validated facts;
- implementations must fail closed on empty tenant_id.
"""

from __future__ import annotations

from typing import Any, Literal, Protocol, runtime_checkable
from uuid import UUID

from app.contracts.smartgraph_contracts import SmartGraphClaim, SmartGraphEdge, SmartGraphNode


SmartGraphNodeType = Literal[
    "TENANT",
    "EMPRESA",
    "RECEPTION_RECORD",
    "EVIDENCE",
    "DOCUMENTO",
    "CLIENTE",
    "PROVEEDOR",
    "PRODUCTO",
    "FAMILIA_DE_ARTICULOS",
    "CUENTA_BANCARIA",
    "MOVIMIENTO",
    "PROCESO",
    "EVENTO",
    "VARIABLE",
    "FORMULA",
    "PATOLOGIA",
    "SINTOMA",
    "PRACTICE",
    "TREATMENT",
    "MICROSERVICE",
    "OPERATIONAL_CASE",
    "FINDING",
    "PREGUNTA_CLINICA",
]

SmartGraphEdgeType = Literal[
    "EXTRACTED_FROM",
    "EVIDENCE_OF",
    "CONFIRMADO_POR",
    "OBSERVADO_EN",
    "SOPORTA_HALLAZGO",
    "INFERIDO_DESDE",
    "INDICATES",
    "ACTIVA_PATOLOGIA",
    "REQUIRES_EVIDENCE",
    "REQUIRES_VARIABLE",
    "SE_CALCULA_CON",
    "SUGIERE_TRATAMIENTO",
    "REQUIERE_REVISION_HUMANA",
    "CAUSES",
    "AFFECTS",
    "DEPENDS_ON",
    "CONTRADICTS",
    "EMPEORA",
    "MEJORA",
    "DERIVA_EN",
]

SmartGraphClaimType = Literal[
    "EXTRACTED",
    "INFERRED",
    "AMBIGUOUS",
    "HYPOTHESIS",
    "VALIDATED",
]

SmartGraphRecordStatus = Literal[
    "ACTIVE",
    "INACTIVE",
    "DEPRECATED",
    "ARCHIVED",
    "REJECTED",
]

SmartGraphClaimStatus = Literal[
    "CANDIDATE",
    "ACTIVE",
    "SUPPORTED",
    "REJECTED",
    "DEPRECATED",
    "BLOCKED",
]

SmartGraphNodeRecord = SmartGraphNode | dict[str, Any]
SmartGraphEdgeRecord = SmartGraphEdge | dict[str, Any]
SmartGraphClaimRecord = SmartGraphClaim | dict[str, Any]


@runtime_checkable
class SmartGraphRepositoryPort(Protocol):
    """Persistence boundary for SmartGraph node/edge/alias/claim records."""

    # ---------------------------------------------------------------------
    # Nodes
    # ---------------------------------------------------------------------

    def create_node(
        self,
        *,
        tenant_id: UUID,
        node_type: SmartGraphNodeType,
        canonical_key: str,
        label: str,
        description: str | None = None,
        source_table: str | None = None,
        source_id: UUID | None = None,
        confidence: float | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> SmartGraphNodeRecord:
        """Create a tenant-scoped canonical SmartGraph node."""
        ...

    def get_node(
        self,
        *,
        tenant_id: UUID,
        node_id: UUID,
    ) -> SmartGraphNodeRecord | None:
        """Return a node by id, scoped by tenant."""
        ...

    def get_node_by_canonical_key(
        self,
        *,
        tenant_id: UUID,
        node_type: SmartGraphNodeType,
        canonical_key: str,
    ) -> SmartGraphNodeRecord | None:
        """Return a canonical node for a tenant/type/key tuple."""
        ...

    def list_nodes(
        self,
        *,
        tenant_id: UUID,
        node_type: SmartGraphNodeType | None = None,
        status: SmartGraphRecordStatus | None = "ACTIVE",
        limit: int = 100,
        offset: int = 0,
    ) -> list[SmartGraphNodeRecord]:
        """List tenant-scoped nodes with optional type/status filters."""
        ...

    # ---------------------------------------------------------------------
    # Edges
    # ---------------------------------------------------------------------

    def create_edge(
        self,
        *,
        tenant_id: UUID,
        from_node_id: UUID,
        to_node_id: UUID,
        edge_type: SmartGraphEdgeType,
        claim_type: SmartGraphClaimType,
        confidence: float | None = None,
        evidence_ids: list[UUID] | None = None,
        source_table: str | None = None,
        source_id: UUID | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> SmartGraphEdgeRecord:
        """Create a typed relationship between two tenant-scoped nodes."""
        ...

    def get_edge(
        self,
        *,
        tenant_id: UUID,
        edge_id: UUID,
    ) -> SmartGraphEdgeRecord | None:
        """Return an edge by id, scoped by tenant."""
        ...

    def list_edges_for_node(
        self,
        *,
        tenant_id: UUID,
        node_id: UUID,
        direction: Literal["OUT", "IN", "BOTH"] = "BOTH",
        edge_type: SmartGraphEdgeType | None = None,
        claim_type: SmartGraphClaimType | None = None,
        status: SmartGraphRecordStatus | None = "ACTIVE",
        limit: int = 100,
        offset: int = 0,
    ) -> list[SmartGraphEdgeRecord]:
        """List edges connected to a node."""
        ...

    # ---------------------------------------------------------------------
    # Aliases / canonical entity resolution
    # ---------------------------------------------------------------------

    def add_alias(
        self,
        *,
        tenant_id: UUID,
        node_id: UUID,
        alias: str,
        alias_normalized: str,
        language: str | None = None,
        source_table: str | None = None,
        source_id: UUID | None = None,
        confidence: float | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Attach an alias to a canonical node."""
        ...

    def find_nodes_by_alias(
        self,
        *,
        tenant_id: UUID,
        alias_normalized: str,
        status: SmartGraphRecordStatus | None = "ACTIVE",
        limit: int = 20,
    ) -> list[SmartGraphNodeRecord]:
        """Find canonical nodes matching a normalized alias."""
        ...

    # ---------------------------------------------------------------------
    # Claims
    # ---------------------------------------------------------------------

    def create_claim(
        self,
        *,
        tenant_id: UUID,
        claim_type: SmartGraphClaimType,
        claim_status: SmartGraphClaimStatus,
        statement: str,
        subject_node_id: UUID | None = None,
        object_node_id: UUID | None = None,
        edge_id: UUID | None = None,
        confidence: float | None = None,
        evidence_ids: list[UUID] | None = None,
        requires_human_review: bool = False,
        metadata: dict[str, Any] | None = None,
    ) -> SmartGraphClaimRecord:
        """Create an explicit SmartGraph claim with its epistemic status."""
        ...

    def get_claim(
        self,
        *,
        tenant_id: UUID,
        claim_id: UUID,
    ) -> SmartGraphClaimRecord | None:
        """Return a claim by id, scoped by tenant."""
        ...

    def list_claims(
        self,
        *,
        tenant_id: UUID,
        claim_type: SmartGraphClaimType | None = None,
        claim_status: SmartGraphClaimStatus | None = None,
        requires_human_review: bool | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[SmartGraphClaimRecord]:
        """List tenant-scoped claims."""
        ...

    def update_claim_status(
        self,
        *,
        tenant_id: UUID,
        claim_id: UUID,
        claim_status: SmartGraphClaimStatus,
        reviewed_by: str | None = None,
        review_decision: str | None = None,
    ) -> SmartGraphClaimRecord:
        """Update claim lifecycle status under deterministic or human review."""
        ...

    # ---------------------------------------------------------------------
    # Activation / export
    # ---------------------------------------------------------------------

    def get_activation_subgraph(
        self,
        *,
        tenant_id: UUID,
        seed_node_ids: list[UUID],
        edge_types: list[SmartGraphEdgeType] | None = None,
        claim_types: list[SmartGraphClaimType] | None = None,
        depth: int = 1,
        limit: int = 200,
    ) -> dict[str, Any]:
        """Return a bounded subgraph for clinical-operational activation."""
        ...

    def export_graph_json(
        self,
        *,
        tenant_id: UUID,
        node_types: list[SmartGraphNodeType] | None = None,
        edge_types: list[SmartGraphEdgeType] | None = None,
        include_claims: bool = True,
        include_aliases: bool = True,
    ) -> dict[str, Any]:
        """Export a tenant graph representation for visualization or analysis."""
        ...
