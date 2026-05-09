"""In-memory implementation of the SmartGraph repository port.

This adapter is intentionally deterministic and side-effect free outside its
own process memory. It is meant for tests, local spikes, and contract validation
before introducing a Supabase implementation.
"""

from __future__ import annotations

from collections import deque
from datetime import UTC, datetime
from typing import Any, Literal
from uuid import UUID, uuid4

from app.repositories.smartgraph_repository_port import (
    SmartGraphClaimStatus,
    SmartGraphClaimType,
    SmartGraphEdgeType,
    SmartGraphNodeType,
    SmartGraphRecordStatus,
    SmartGraphRepositoryPort,
)


class InMemorySmartGraphRepository(SmartGraphRepositoryPort):
    """In-memory SmartGraph repository with tenant-scoped fail-closed access."""

    def __init__(self) -> None:
        self._nodes: dict[UUID, dict[str, Any]] = {}
        self._edges: dict[UUID, dict[str, Any]] = {}
        self._aliases: dict[UUID, dict[str, Any]] = {}
        self._claims: dict[UUID, dict[str, Any]] = {}

    # ------------------------------------------------------------------
    # Nodes
    # ------------------------------------------------------------------

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
    ) -> dict[str, Any]:
        self._ensure_tenant_id(tenant_id)
        self._ensure_not_blank(canonical_key, "canonical_key")
        self._ensure_not_blank(label, "label")
        self._ensure_confidence(confidence)

        existing = self.get_node_by_canonical_key(
            tenant_id=tenant_id,
            node_type=node_type,
            canonical_key=canonical_key,
        )
        if existing is not None:
            raise ValueError(
                "SmartGraph node already exists for "
                f"tenant_id={tenant_id}, node_type={node_type}, canonical_key={canonical_key}"
            )

        now = self._now()
        record = {
            "id": uuid4(),
            "tenant_id": tenant_id,
            "node_type": node_type,
            "canonical_key": canonical_key,
            "label": label,
            "description": description,
            "source_table": source_table,
            "source_id": source_id,
            "status": "ACTIVE",
            "confidence": confidence,
            "metadata": dict(metadata or {}),
            "created_at": now,
            "updated_at": now,
        }
        self._nodes[record["id"]] = record
        return self._copy(record)

    def get_node(self, *, tenant_id: UUID, node_id: UUID) -> dict[str, Any] | None:
        self._ensure_tenant_id(tenant_id)
        record = self._nodes.get(node_id)
        if record is None or record["tenant_id"] != tenant_id:
            return None
        return self._copy(record)

    def get_node_by_canonical_key(
        self,
        *,
        tenant_id: UUID,
        node_type: SmartGraphNodeType,
        canonical_key: str,
    ) -> dict[str, Any] | None:
        self._ensure_tenant_id(tenant_id)
        self._ensure_not_blank(canonical_key, "canonical_key")
        for record in self._nodes.values():
            if (
                record["tenant_id"] == tenant_id
                and record["node_type"] == node_type
                and record["canonical_key"] == canonical_key
            ):
                return self._copy(record)
        return None

    def list_nodes(
        self,
        *,
        tenant_id: UUID,
        node_type: SmartGraphNodeType | None = None,
        status: SmartGraphRecordStatus | None = "ACTIVE",
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        self._ensure_tenant_id(tenant_id)
        self._ensure_pagination(limit, offset)
        records = [
            record
            for record in self._nodes.values()
            if record["tenant_id"] == tenant_id
            and (node_type is None or record["node_type"] == node_type)
            and (status is None or record["status"] == status)
        ]
        records = self._stable_page(records, limit=limit, offset=offset)
        return [self._copy(record) for record in records]

    # ------------------------------------------------------------------
    # Edges
    # ------------------------------------------------------------------

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
    ) -> dict[str, Any]:
        self._ensure_tenant_id(tenant_id)
        self._ensure_confidence(confidence)
        if from_node_id == to_node_id:
            raise ValueError("SmartGraph self-edges are not allowed")

        from_node = self._nodes.get(from_node_id)
        to_node = self._nodes.get(to_node_id)
        if from_node is None or from_node["tenant_id"] != tenant_id:
            raise ValueError("from_node_id does not exist for tenant")
        if to_node is None or to_node["tenant_id"] != tenant_id:
            raise ValueError("to_node_id does not exist for tenant")

        now = self._now()
        record = {
            "id": uuid4(),
            "tenant_id": tenant_id,
            "from_node_id": from_node_id,
            "to_node_id": to_node_id,
            "edge_type": edge_type,
            "claim_type": claim_type,
            "confidence": confidence,
            "valid_from": None,
            "valid_until": None,
            "observed_at": None,
            "source_table": source_table,
            "source_id": source_id,
            "evidence_ids": list(evidence_ids or []),
            "status": "ACTIVE",
            "metadata": dict(metadata or {}),
            "created_at": now,
            "updated_at": now,
        }
        self._edges[record["id"]] = record
        return self._copy(record)

    def get_edge(self, *, tenant_id: UUID, edge_id: UUID) -> dict[str, Any] | None:
        self._ensure_tenant_id(tenant_id)
        record = self._edges.get(edge_id)
        if record is None or record["tenant_id"] != tenant_id:
            return None
        return self._copy(record)

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
    ) -> list[dict[str, Any]]:
        self._ensure_tenant_id(tenant_id)
        self._ensure_direction(direction)
        self._ensure_pagination(limit, offset)
        if self.get_node(tenant_id=tenant_id, node_id=node_id) is None:
            return []

        records = []
        for record in self._edges.values():
            if record["tenant_id"] != tenant_id:
                continue
            if edge_type is not None and record["edge_type"] != edge_type:
                continue
            if claim_type is not None and record["claim_type"] != claim_type:
                continue
            if status is not None and record["status"] != status:
                continue
            if direction in ("OUT", "BOTH") and record["from_node_id"] == node_id:
                records.append(record)
                continue
            if direction in ("IN", "BOTH") and record["to_node_id"] == node_id:
                records.append(record)

        records = self._stable_page(records, limit=limit, offset=offset)
        return [self._copy(record) for record in records]

    # ------------------------------------------------------------------
    # Aliases
    # ------------------------------------------------------------------

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
        self._ensure_tenant_id(tenant_id)
        self._ensure_not_blank(alias, "alias")
        self._ensure_not_blank(alias_normalized, "alias_normalized")
        self._ensure_confidence(confidence)
        if self.get_node(tenant_id=tenant_id, node_id=node_id) is None:
            raise ValueError("node_id does not exist for tenant")

        for record in self._aliases.values():
            if (
                record["tenant_id"] == tenant_id
                and record["node_id"] == node_id
                and record["alias_normalized"] == alias_normalized
            ):
                raise ValueError("SmartGraph alias already exists for tenant/node")

        now = self._now()
        record = {
            "id": uuid4(),
            "tenant_id": tenant_id,
            "node_id": node_id,
            "alias": alias,
            "alias_normalized": alias_normalized,
            "language": language,
            "source_table": source_table,
            "source_id": source_id,
            "confidence": confidence,
            "status": "ACTIVE",
            "metadata": dict(metadata or {}),
            "created_at": now,
            "updated_at": now,
        }
        self._aliases[record["id"]] = record
        return self._copy(record)

    def find_nodes_by_alias(
        self,
        *,
        tenant_id: UUID,
        alias_normalized: str,
        status: SmartGraphRecordStatus | None = "ACTIVE",
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        self._ensure_tenant_id(tenant_id)
        self._ensure_not_blank(alias_normalized, "alias_normalized")
        self._ensure_pagination(limit, 0)

        node_ids = []
        for alias_record in self._aliases.values():
            if (
                alias_record["tenant_id"] == tenant_id
                and alias_record["alias_normalized"] == alias_normalized
                and (status is None or alias_record["status"] == status)
            ):
                node_ids.append(alias_record["node_id"])

        nodes = []
        for node_id in node_ids:
            node = self.get_node(tenant_id=tenant_id, node_id=node_id)
            if node is not None and (status is None or node["status"] == status):
                nodes.append(node)

        return self._stable_page(nodes, limit=limit, offset=0)

    # ------------------------------------------------------------------
    # Claims
    # ------------------------------------------------------------------

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
    ) -> dict[str, Any]:
        self._ensure_tenant_id(tenant_id)
        self._ensure_not_blank(statement, "statement")
        self._ensure_confidence(confidence)
        self._ensure_optional_node_for_tenant(tenant_id, subject_node_id, "subject_node_id")
        self._ensure_optional_node_for_tenant(tenant_id, object_node_id, "object_node_id")
        self._ensure_optional_edge_for_tenant(tenant_id, edge_id, "edge_id")
        self._ensure_supported_claim_is_validated(
            claim_type=claim_type,
            claim_status=claim_status,
            evidence_ids=list(evidence_ids or []),
            requires_human_review=requires_human_review,
        )

        now = self._now()
        record = {
            "id": uuid4(),
            "tenant_id": tenant_id,
            "claim_type": claim_type,
            "claim_status": claim_status,
            "subject_node_id": subject_node_id,
            "object_node_id": object_node_id,
            "edge_id": edge_id,
            "statement": statement,
            "confidence": confidence,
            "evidence_ids": list(evidence_ids or []),
            "requires_human_review": requires_human_review,
            "reviewed_by": None,
            "reviewed_at": None,
            "review_decision": None,
            "valid_from": None,
            "valid_until": None,
            "observed_at": None,
            "metadata": dict(metadata or {}),
            "created_at": now,
            "updated_at": now,
        }
        self._claims[record["id"]] = record
        return self._copy(record)

    def get_claim(self, *, tenant_id: UUID, claim_id: UUID) -> dict[str, Any] | None:
        self._ensure_tenant_id(tenant_id)
        record = self._claims.get(claim_id)
        if record is None or record["tenant_id"] != tenant_id:
            return None
        return self._copy(record)

    def list_claims(
        self,
        *,
        tenant_id: UUID,
        claim_type: SmartGraphClaimType | None = None,
        claim_status: SmartGraphClaimStatus | None = None,
        requires_human_review: bool | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        self._ensure_tenant_id(tenant_id)
        self._ensure_pagination(limit, offset)
        records = [
            record
            for record in self._claims.values()
            if record["tenant_id"] == tenant_id
            and (claim_type is None or record["claim_type"] == claim_type)
            and (claim_status is None or record["claim_status"] == claim_status)
            and (
                requires_human_review is None
                or record["requires_human_review"] == requires_human_review
            )
        ]
        records = self._stable_page(records, limit=limit, offset=offset)
        return [self._copy(record) for record in records]

    def update_claim_status(
        self,
        *,
        tenant_id: UUID,
        claim_id: UUID,
        claim_status: SmartGraphClaimStatus,
        reviewed_by: str | None = None,
        review_decision: str | None = None,
    ) -> dict[str, Any]:
        self._ensure_tenant_id(tenant_id)
        record = self._claims.get(claim_id)
        if record is None or record["tenant_id"] != tenant_id:
            raise ValueError("claim_id does not exist for tenant")

        self._ensure_supported_claim_is_validated(
            claim_type=record["claim_type"],
            claim_status=claim_status,
            evidence_ids=record["evidence_ids"],
            requires_human_review=record["requires_human_review"],
            reviewed_by=reviewed_by,
            review_decision=review_decision,
        )

        record["claim_status"] = claim_status
        record["reviewed_by"] = reviewed_by
        record["review_decision"] = review_decision
        record["reviewed_at"] = self._now() if reviewed_by or review_decision else None
        record["updated_at"] = self._now()
        return self._copy(record)

    # ------------------------------------------------------------------
    # Activation / export
    # ------------------------------------------------------------------

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
        self._ensure_tenant_id(tenant_id)
        if depth < 0:
            raise ValueError("depth must be >= 0")
        self._ensure_pagination(limit, 0)

        allowed_edge_types = set(edge_types or [])
        allowed_claim_types = set(claim_types or [])
        visited_nodes: set[UUID] = set()
        collected_edges: dict[UUID, dict[str, Any]] = {}
        queue: deque[tuple[UUID, int]] = deque()

        for seed_node_id in seed_node_ids:
            if self.get_node(tenant_id=tenant_id, node_id=seed_node_id) is not None:
                queue.append((seed_node_id, 0))
                visited_nodes.add(seed_node_id)

        while queue and len(visited_nodes) < limit:
            node_id, current_depth = queue.popleft()
            if current_depth >= depth:
                continue

            connected_edges = self.list_edges_for_node(
                tenant_id=tenant_id,
                node_id=node_id,
                direction="BOTH",
                status="ACTIVE",
                limit=limit,
            )
            for edge in connected_edges:
                if allowed_edge_types and edge["edge_type"] not in allowed_edge_types:
                    continue
                if allowed_claim_types and edge["claim_type"] not in allowed_claim_types:
                    continue
                collected_edges[edge["id"]] = edge
                for next_node_id in (edge["from_node_id"], edge["to_node_id"]):
                    if next_node_id not in visited_nodes and len(visited_nodes) < limit:
                        visited_nodes.add(next_node_id)
                        queue.append((next_node_id, current_depth + 1))

        nodes = [
            node
            for node_id in visited_nodes
            if (node := self.get_node(tenant_id=tenant_id, node_id=node_id)) is not None
        ]
        return {
            "tenant_id": tenant_id,
            "seed_node_ids": list(seed_node_ids),
            "depth": depth,
            "nodes": self._stable_records(nodes),
            "edges": self._stable_records(list(collected_edges.values())),
        }

    def export_graph_json(
        self,
        *,
        tenant_id: UUID,
        node_types: list[SmartGraphNodeType] | None = None,
        edge_types: list[SmartGraphEdgeType] | None = None,
        include_claims: bool = True,
        include_aliases: bool = True,
    ) -> dict[str, Any]:
        self._ensure_tenant_id(tenant_id)
        allowed_node_types = set(node_types or [])
        allowed_edge_types = set(edge_types or [])

        nodes = [
            self._copy(record)
            for record in self._nodes.values()
            if record["tenant_id"] == tenant_id
            and (not allowed_node_types or record["node_type"] in allowed_node_types)
        ]
        node_ids = {record["id"] for record in nodes}
        edges = [
            self._copy(record)
            for record in self._edges.values()
            if record["tenant_id"] == tenant_id
            and record["from_node_id"] in node_ids
            and record["to_node_id"] in node_ids
            and (not allowed_edge_types or record["edge_type"] in allowed_edge_types)
        ]
        aliases = [
            self._copy(record)
            for record in self._aliases.values()
            if include_aliases
            and record["tenant_id"] == tenant_id
            and record["node_id"] in node_ids
        ]
        claims = [
            self._copy(record)
            for record in self._claims.values()
            if include_claims and record["tenant_id"] == tenant_id
        ]
        return {
            "tenant_id": tenant_id,
            "nodes": self._stable_records(nodes),
            "edges": self._stable_records(edges),
            "aliases": self._stable_records(aliases),
            "claims": self._stable_records(claims),
        }

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _now() -> datetime:
        return datetime.now(UTC)

    @staticmethod
    def _copy(record: dict[str, Any]) -> dict[str, Any]:
        copied = dict(record)
        for key, value in list(copied.items()):
            if isinstance(value, dict):
                copied[key] = dict(value)
            elif isinstance(value, list):
                copied[key] = list(value)
        return copied

    @staticmethod
    def _ensure_tenant_id(tenant_id: UUID) -> None:
        if not isinstance(tenant_id, UUID):
            raise ValueError("tenant_id must be a UUID")
        if tenant_id.int == 0:
            raise ValueError("tenant_id must not be empty")

    @staticmethod
    def _ensure_not_blank(value: str, field_name: str) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field_name} must not be blank")

    @staticmethod
    def _ensure_confidence(confidence: float | None) -> None:
        if confidence is None:
            return
        if confidence < 0 or confidence > 1:
            raise ValueError("confidence must be between 0 and 1")

    @staticmethod
    def _ensure_pagination(limit: int, offset: int) -> None:
        if limit < 1:
            raise ValueError("limit must be >= 1")
        if offset < 0:
            raise ValueError("offset must be >= 0")

    @staticmethod
    def _ensure_direction(direction: str) -> None:
        if direction not in {"OUT", "IN", "BOTH"}:
            raise ValueError("direction must be OUT, IN, or BOTH")

    def _ensure_optional_node_for_tenant(
        self,
        tenant_id: UUID,
        node_id: UUID | None,
        field_name: str,
    ) -> None:
        if node_id is not None and self.get_node(tenant_id=tenant_id, node_id=node_id) is None:
            raise ValueError(f"{field_name} does not exist for tenant")

    def _ensure_optional_edge_for_tenant(
        self,
        tenant_id: UUID,
        edge_id: UUID | None,
        field_name: str,
    ) -> None:
        if edge_id is not None and self.get_edge(tenant_id=tenant_id, edge_id=edge_id) is None:
            raise ValueError(f"{field_name} does not exist for tenant")

    @staticmethod
    def _ensure_supported_claim_is_validated(
        *,
        claim_type: SmartGraphClaimType,
        claim_status: SmartGraphClaimStatus,
        evidence_ids: list[UUID],
        requires_human_review: bool,
        reviewed_by: str | None = None,
        review_decision: str | None = None,
    ) -> None:
        if claim_status != "SUPPORTED":
            return
        if claim_type in {"INFERRED", "AMBIGUOUS", "HYPOTHESIS"}:
            has_evidence = bool(evidence_ids)
            has_human_review = bool(reviewed_by and review_decision)
            if not has_evidence and not has_human_review:
                raise ValueError(
                    "inferred, ambiguous, or hypothesis claims cannot become "
                    "SUPPORTED without evidence or human review"
                )
        if requires_human_review and not (reviewed_by and review_decision):
            raise ValueError("claim requires human review before SUPPORTED")

    @staticmethod
    def _stable_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return sorted(records, key=lambda item: str(item["id"]))

    def _stable_page(
        self,
        records: list[dict[str, Any]],
        *,
        limit: int,
        offset: int,
    ) -> list[dict[str, Any]]:
        return self._stable_records(records)[offset : offset + limit]
