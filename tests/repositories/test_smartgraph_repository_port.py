from __future__ import annotations

from datetime import UTC, datetime
from typing import get_type_hints
from uuid import UUID, uuid4

from app.contracts.smartgraph_contracts import SmartGraphClaim, SmartGraphEdge, SmartGraphNode
from app.repositories.smartgraph_repository_port import (
    SmartGraphClaimRecord,
    SmartGraphEdgeRecord,
    SmartGraphNodeRecord,
    SmartGraphRepositoryPort,
)


def test_port_record_aliases_include_contract_models_and_dicts() -> None:
    node_value = SmartGraphNode(
        tenant_id="tenant-a",
        node_type="PRODUCTO",
        canonical_key="prod-001",
        label="Producto 001",
    )
    edge_value = SmartGraphEdge(
        tenant_id="tenant-a",
        edge_type="INDICATES",
        claim_type="HYPOTHESIS",
    )
    claim_value = SmartGraphClaim(
        tenant_id="tenant-a",
        claim_type="INFERRED",
        claim_status="CANDIDATE",
    )

    def _accept_node(_: SmartGraphNodeRecord) -> bool:
        return True

    def _accept_edge(_: SmartGraphEdgeRecord) -> bool:
        return True

    def _accept_claim(_: SmartGraphClaimRecord) -> bool:
        return True

    assert _accept_node(node_value)
    assert _accept_node({"tenant_id": "tenant-a", "node_type": "PRODUCTO"})
    assert _accept_edge(edge_value)
    assert _accept_edge({"tenant_id": "tenant-a", "edge_type": "INDICATES"})
    assert _accept_claim(claim_value)
    assert _accept_claim({"tenant_id": "tenant-a", "claim_type": "INFERRED"})


def test_port_create_methods_expose_boundary_types() -> None:
    hints_create_node = get_type_hints(SmartGraphRepositoryPort.create_node)
    hints_create_edge = get_type_hints(SmartGraphRepositoryPort.create_edge)
    hints_create_claim = get_type_hints(SmartGraphRepositoryPort.create_claim)

    assert hints_create_node["return"] == SmartGraphNodeRecord
    assert hints_create_edge["return"] == SmartGraphEdgeRecord
    assert hints_create_claim["return"] == SmartGraphClaimRecord


class _DummyPort:
    def create_node(self, *, tenant_id: UUID, node_type, canonical_key, label, description=None, source_table=None, source_id=None, confidence=None, metadata=None):
        return {
            "tenant_id": str(tenant_id),
            "node_type": node_type,
            "canonical_key": canonical_key,
            "label": label,
        }

    def get_node(self, *, tenant_id: UUID, node_id: UUID):
        return None

    def get_node_by_canonical_key(self, *, tenant_id: UUID, node_type, canonical_key):
        return None

    def list_nodes(self, *, tenant_id: UUID, node_type=None, status="ACTIVE", limit=100, offset=0):
        return []

    def create_edge(self, *, tenant_id: UUID, from_node_id: UUID, to_node_id: UUID, edge_type, claim_type, confidence=None, evidence_ids=None, source_table=None, source_id=None, metadata=None):
        return {
            "tenant_id": str(tenant_id),
            "edge_type": edge_type,
            "claim_type": claim_type,
        }

    def get_edge(self, *, tenant_id: UUID, edge_id: UUID):
        return None

    def list_edges_for_node(self, *, tenant_id: UUID, node_id: UUID, direction="BOTH", edge_type=None, claim_type=None, status="ACTIVE", limit=100, offset=0):
        return []

    def add_alias(self, *, tenant_id: UUID, node_id: UUID, alias: str, alias_normalized: str, language=None, source_table=None, source_id=None, confidence=None, metadata=None):
        return {"tenant_id": str(tenant_id), "alias": alias}

    def find_nodes_by_alias(self, *, tenant_id: UUID, alias_normalized: str, status="ACTIVE", limit=20):
        return []

    def create_claim(self, *, tenant_id: UUID, claim_type, claim_status, statement: str, subject_node_id=None, object_node_id=None, edge_id=None, confidence=None, evidence_ids=None, requires_human_review=False, metadata=None):
        return {
            "tenant_id": str(tenant_id),
            "claim_type": claim_type,
            "claim_status": claim_status,
            "statement": statement,
        }

    def get_claim(self, *, tenant_id: UUID, claim_id: UUID):
        return None

    def list_claims(self, *, tenant_id: UUID, claim_type=None, claim_status=None, requires_human_review=None, limit=100, offset=0):
        return []

    def update_claim_status(self, *, tenant_id: UUID, claim_id: UUID, claim_status, reviewed_by=None, review_decision=None):
        return {"tenant_id": str(tenant_id), "claim_status": claim_status}

    def get_activation_subgraph(self, *, tenant_id: UUID, seed_node_ids, edge_types=None, claim_types=None, depth=1, limit=200):
        return {"tenant_id": str(tenant_id), "nodes": [], "edges": []}

    def export_graph_json(self, *, tenant_id: UUID, node_types=None, edge_types=None, include_claims=True, include_aliases=True):
        return {"tenant_id": str(tenant_id), "nodes": [], "edges": [], "claims": [], "aliases": []}


def test_runtime_protocol_compatibility_kept_for_dict_adapters() -> None:
    adapter = _DummyPort()
    assert isinstance(adapter, SmartGraphRepositoryPort)
    tenant_id = uuid4()
    node = adapter.create_node(
        tenant_id=tenant_id,
        node_type="PRODUCTO",
        canonical_key="prod-001",
        label="Producto 001",
    )
    assert node["tenant_id"] == str(tenant_id)
    edge = adapter.create_edge(
        tenant_id=tenant_id,
        from_node_id=uuid4(),
        to_node_id=uuid4(),
        edge_type="INDICATES",
        claim_type="HYPOTHESIS",
        confidence=0.5,
        evidence_ids=[],
        source_table=None,
        source_id=None,
        metadata={"at": datetime.now(UTC).isoformat()},
    )
    assert edge["claim_type"] == "HYPOTHESIS"
