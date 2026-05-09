"""Adapter Supabase para SmartGraph — SmartPyme.

Implementa SmartGraphRepositoryPort usando un cliente Supabase inyectable.

Reglas:
    - cliente_id es OBLIGATORIO. Fail-closed si está vacío.
    - Todas las operaciones filtran por tenant_id/cliente_id.
    - No permite escritura directa del LLM.
    - No modifica repositorios SQLite legacy.
    - No hace dual-write.
    - Conserva claim_type, confidence, evidence_ids y metadata como datos estructurados.
    - INFERRED / AMBIGUOUS / HYPOTHESIS no pasan a SUPPORTED sin evidencia o revisión humana.

Tablas Supabase esperadas:
    smartgraph_nodes
    smartgraph_edges
    smartgraph_aliases
    smartgraph_claims
"""
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal
from uuid import UUID

from app.repositories.persistence_provider import validate_supabase_env
from app.repositories.smartgraph_repository_port import (
    SmartGraphClaimStatus,
    SmartGraphClaimType,
    SmartGraphEdgeType,
    SmartGraphNodeType,
    SmartGraphRecordStatus,
    SmartGraphRepositoryPort,
)

_NODES_TABLE = "smartgraph_nodes"
_EDGES_TABLE = "smartgraph_edges"
_ALIASES_TABLE = "smartgraph_aliases"
_CLAIMS_TABLE = "smartgraph_claims"


class SupabaseSmartGraphRepository(SmartGraphRepositoryPort):
    """Adapter Supabase para SmartGraph.

    Args:
        cliente_id: Identificador del tenant. Obligatorio. Fail-closed si vacío.
        supabase_client: Cliente Supabase inyectable. Si es None, se valida
            el entorno y se construye el cliente real.
    """

    def __init__(self, cliente_id: str, supabase_client: Any | None = None) -> None:
        if not cliente_id or not cliente_id.strip():
            raise ValueError("cliente_id is required")
        self.cliente_id = cliente_id

        if supabase_client is None:
            validate_supabase_env()
            self._client = self._build_real_client()
        else:
            self._client = supabase_client

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
        self._ensure_tenant_match(tenant_id)
        self._ensure_not_blank(canonical_key, "canonical_key")
        self._ensure_not_blank(label, "label")
        self._ensure_confidence(confidence)

        row = {
            "tenant_id": str(tenant_id),
            "node_type": node_type,
            "canonical_key": canonical_key,
            "label": label,
            "description": description,
            "source_table": source_table,
            "source_id": str(source_id) if source_id else None,
            "status": "ACTIVE",
            "confidence": confidence,
            "metadata": dict(metadata or {}),
        }
        rows = self._insert(_NODES_TABLE, row)
        return self._normalize_node(rows[0])

    def get_node(self, *, tenant_id: UUID, node_id: UUID) -> dict[str, Any] | None:
        self._ensure_tenant_match(tenant_id)
        rows = (
            self._client.table(_NODES_TABLE)
            .select("*")
            .eq("tenant_id", str(tenant_id))
            .eq("id", str(node_id))
            .execute()
            .data
        )
        if not rows:
            return None
        return self._normalize_node(rows[0])

    def get_node_by_canonical_key(
        self,
        *,
        tenant_id: UUID,
        node_type: SmartGraphNodeType,
        canonical_key: str,
    ) -> dict[str, Any] | None:
        self._ensure_tenant_match(tenant_id)
        self._ensure_not_blank(canonical_key, "canonical_key")
        rows = (
            self._client.table(_NODES_TABLE)
            .select("*")
            .eq("tenant_id", str(tenant_id))
            .eq("node_type", node_type)
            .eq("canonical_key", canonical_key)
            .execute()
            .data
        )
        if not rows:
            return None
        return self._normalize_node(rows[0])

    def list_nodes(
        self,
        *,
        tenant_id: UUID,
        node_type: SmartGraphNodeType | None = None,
        status: SmartGraphRecordStatus | None = "ACTIVE",
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        self._ensure_tenant_match(tenant_id)
        self._ensure_pagination(limit, offset)
        query = self._client.table(_NODES_TABLE).select("*").eq("tenant_id", str(tenant_id))
        if node_type is not None:
            query = query.eq("node_type", node_type)
        if status is not None:
            query = query.eq("status", status)
        rows = query.range(offset, offset + limit - 1).execute().data
        return [self._normalize_node(row) for row in rows]

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
        self._ensure_tenant_match(tenant_id)
        self._ensure_confidence(confidence)
        if from_node_id == to_node_id:
            raise ValueError("SmartGraph self-edges are not allowed")
        self._ensure_node_exists(tenant_id=tenant_id, node_id=from_node_id, field_name="from_node_id")
        self._ensure_node_exists(tenant_id=tenant_id, node_id=to_node_id, field_name="to_node_id")

        row = {
            "tenant_id": str(tenant_id),
            "from_node_id": str(from_node_id),
            "to_node_id": str(to_node_id),
            "edge_type": edge_type,
            "claim_type": claim_type,
            "confidence": confidence,
            "valid_from": None,
            "valid_until": None,
            "observed_at": None,
            "source_table": source_table,
            "source_id": str(source_id) if source_id else None,
            "evidence_ids": [str(item) for item in evidence_ids or []],
            "status": "ACTIVE",
            "metadata": dict(metadata or {}),
        }
        rows = self._insert(_EDGES_TABLE, row)
        return self._normalize_edge(rows[0])

    def get_edge(self, *, tenant_id: UUID, edge_id: UUID) -> dict[str, Any] | None:
        self._ensure_tenant_match(tenant_id)
        rows = (
            self._client.table(_EDGES_TABLE)
            .select("*")
            .eq("tenant_id", str(tenant_id))
            .eq("id", str(edge_id))
            .execute()
            .data
        )
        if not rows:
            return None
        return self._normalize_edge(rows[0])

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
        self._ensure_tenant_match(tenant_id)
        self._ensure_direction(direction)
        self._ensure_pagination(limit, offset)
        self._ensure_node_exists(tenant_id=tenant_id, node_id=node_id, field_name="node_id")

        if direction == "OUT":
            rows = self._query_edges(
                tenant_id=tenant_id,
                from_node_id=node_id,
                edge_type=edge_type,
                claim_type=claim_type,
                status=status,
                limit=limit,
                offset=offset,
            )
        elif direction == "IN":
            rows = self._query_edges(
                tenant_id=tenant_id,
                to_node_id=node_id,
                edge_type=edge_type,
                claim_type=claim_type,
                status=status,
                limit=limit,
                offset=offset,
            )
        else:
            outbound = self._query_edges(
                tenant_id=tenant_id,
                from_node_id=node_id,
                edge_type=edge_type,
                claim_type=claim_type,
                status=status,
                limit=limit + offset,
                offset=0,
            )
            inbound = self._query_edges(
                tenant_id=tenant_id,
                to_node_id=node_id,
                edge_type=edge_type,
                claim_type=claim_type,
                status=status,
                limit=limit + offset,
                offset=0,
            )
            dedup = {row["id"]: row for row in [*outbound, *inbound]}
            rows = self._stable_rows(list(dedup.values()))[offset : offset + limit]

        return [self._normalize_edge(row) for row in rows]

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
        self._ensure_tenant_match(tenant_id)
        self._ensure_node_exists(tenant_id=tenant_id, node_id=node_id, field_name="node_id")
        self._ensure_not_blank(alias, "alias")
        self._ensure_not_blank(alias_normalized, "alias_normalized")
        self._ensure_confidence(confidence)

        row = {
            "tenant_id": str(tenant_id),
            "node_id": str(node_id),
            "alias": alias,
            "alias_normalized": alias_normalized,
            "language": language,
            "source_table": source_table,
            "source_id": str(source_id) if source_id else None,
            "confidence": confidence,
            "status": "ACTIVE",
            "metadata": dict(metadata or {}),
        }
        rows = self._insert(_ALIASES_TABLE, row)
        return self._normalize_alias(rows[0])

    def find_nodes_by_alias(
        self,
        *,
        tenant_id: UUID,
        alias_normalized: str,
        status: SmartGraphRecordStatus | None = "ACTIVE",
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        self._ensure_tenant_match(tenant_id)
        self._ensure_not_blank(alias_normalized, "alias_normalized")
        self._ensure_pagination(limit, 0)

        query = (
            self._client.table(_ALIASES_TABLE)
            .select("*")
            .eq("tenant_id", str(tenant_id))
            .eq("alias_normalized", alias_normalized)
        )
        if status is not None:
            query = query.eq("status", status)
        aliases = query.range(0, limit - 1).execute().data

        nodes: list[dict[str, Any]] = []
        for alias in aliases:
            node = self.get_node(tenant_id=tenant_id, node_id=UUID(alias["node_id"]))
            if node is not None and (status is None or node["status"] == status):
                nodes.append(node)
        return self._stable_rows(nodes)[:limit]

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
        self._ensure_tenant_match(tenant_id)
        self._ensure_not_blank(statement, "statement")
        self._ensure_confidence(confidence)
        self._ensure_optional_node_exists(tenant_id, subject_node_id, "subject_node_id")
        self._ensure_optional_node_exists(tenant_id, object_node_id, "object_node_id")
        self._ensure_optional_edge_exists(tenant_id, edge_id, "edge_id")
        self._ensure_supported_claim_is_validated(
            claim_type=claim_type,
            claim_status=claim_status,
            evidence_ids=list(evidence_ids or []),
            requires_human_review=requires_human_review,
        )

        row = {
            "tenant_id": str(tenant_id),
            "claim_type": claim_type,
            "claim_status": claim_status,
            "subject_node_id": str(subject_node_id) if subject_node_id else None,
            "object_node_id": str(object_node_id) if object_node_id else None,
            "edge_id": str(edge_id) if edge_id else None,
            "statement": statement,
            "confidence": confidence,
            "evidence_ids": [str(item) for item in evidence_ids or []],
            "requires_human_review": requires_human_review,
            "reviewed_by": None,
            "reviewed_at": None,
            "review_decision": None,
            "valid_from": None,
            "valid_until": None,
            "observed_at": None,
            "metadata": dict(metadata or {}),
        }
        rows = self._insert(_CLAIMS_TABLE, row)
        return self._normalize_claim(rows[0])

    def get_claim(self, *, tenant_id: UUID, claim_id: UUID) -> dict[str, Any] | None:
        self._ensure_tenant_match(tenant_id)
        rows = (
            self._client.table(_CLAIMS_TABLE)
            .select("*")
            .eq("tenant_id", str(tenant_id))
            .eq("id", str(claim_id))
            .execute()
            .data
        )
        if not rows:
            return None
        return self._normalize_claim(rows[0])

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
        self._ensure_tenant_match(tenant_id)
        self._ensure_pagination(limit, offset)
        query = self._client.table(_CLAIMS_TABLE).select("*").eq("tenant_id", str(tenant_id))
        if claim_type is not None:
            query = query.eq("claim_type", claim_type)
        if claim_status is not None:
            query = query.eq("claim_status", claim_status)
        if requires_human_review is not None:
            query = query.eq("requires_human_review", requires_human_review)
        rows = query.range(offset, offset + limit - 1).execute().data
        return [self._normalize_claim(row) for row in rows]

    def update_claim_status(
        self,
        *,
        tenant_id: UUID,
        claim_id: UUID,
        claim_status: SmartGraphClaimStatus,
        reviewed_by: str | None = None,
        review_decision: str | None = None,
    ) -> dict[str, Any]:
        self._ensure_tenant_match(tenant_id)
        current = self.get_claim(tenant_id=tenant_id, claim_id=claim_id)
        if current is None:
            raise ValueError("claim_id does not exist for tenant")

        self._ensure_supported_claim_is_validated(
            claim_type=current["claim_type"],
            claim_status=claim_status,
            evidence_ids=current["evidence_ids"],
            requires_human_review=current["requires_human_review"],
            reviewed_by=reviewed_by,
            review_decision=review_decision,
        )

        patch = {
            "claim_status": claim_status,
            "reviewed_by": reviewed_by,
            "review_decision": review_decision,
            "reviewed_at": self._now_iso() if reviewed_by or review_decision else None,
            "updated_at": self._now_iso(),
        }
        rows = (
            self._client.table(_CLAIMS_TABLE)
            .update(patch)
            .eq("tenant_id", str(tenant_id))
            .eq("id", str(claim_id))
            .execute()
            .data
        )
        if not rows:
            raise ValueError("claim_id does not exist for tenant")
        return self._normalize_claim(rows[0])

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
        self._ensure_tenant_match(tenant_id)
        if depth < 0:
            raise ValueError("depth must be >= 0")
        self._ensure_pagination(limit, 0)

        allowed_edge_types = set(edge_types or [])
        allowed_claim_types = set(claim_types or [])
        visited: set[UUID] = set()
        frontier = [node_id for node_id in seed_node_ids if self.get_node(tenant_id=tenant_id, node_id=node_id)]
        visited.update(frontier)
        collected_edges: dict[UUID, dict[str, Any]] = {}

        for _ in range(depth):
            next_frontier: list[UUID] = []
            for node_id in frontier:
                edges = self.list_edges_for_node(
                    tenant_id=tenant_id,
                    node_id=node_id,
                    direction="BOTH",
                    status="ACTIVE",
                    limit=limit,
                )
                for edge in edges:
                    if allowed_edge_types and edge["edge_type"] not in allowed_edge_types:
                        continue
                    if allowed_claim_types and edge["claim_type"] not in allowed_claim_types:
                        continue
                    collected_edges[edge["id"]] = edge
                    for candidate_id in (edge["from_node_id"], edge["to_node_id"]):
                        if candidate_id not in visited and len(visited) < limit:
                            visited.add(candidate_id)
                            next_frontier.append(candidate_id)
            frontier = next_frontier
            if not frontier or len(visited) >= limit:
                break

        nodes = [
            node
            for node_id in visited
            if (node := self.get_node(tenant_id=tenant_id, node_id=node_id)) is not None
        ]
        return {
            "tenant_id": tenant_id,
            "seed_node_ids": list(seed_node_ids),
            "depth": depth,
            "nodes": self._stable_rows(nodes),
            "edges": self._stable_rows(list(collected_edges.values())),
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
        self._ensure_tenant_match(tenant_id)
        nodes = self.list_nodes(tenant_id=tenant_id, status=None, limit=10000)
        if node_types:
            allowed_node_types = set(node_types)
            nodes = [node for node in nodes if node["node_type"] in allowed_node_types]
        node_ids = {node["id"] for node in nodes}

        raw_edges = self._client.table(_EDGES_TABLE).select("*").eq("tenant_id", str(tenant_id)).execute().data
        edges = [
            self._normalize_edge(row)
            for row in raw_edges
            if UUID(row["from_node_id"]) in node_ids and UUID(row["to_node_id"]) in node_ids
        ]
        if edge_types:
            allowed_edge_types = set(edge_types)
            edges = [edge for edge in edges if edge["edge_type"] in allowed_edge_types]

        aliases: list[dict[str, Any]] = []
        if include_aliases:
            raw_aliases = self._client.table(_ALIASES_TABLE).select("*").eq("tenant_id", str(tenant_id)).execute().data
            aliases = [
                self._normalize_alias(row)
                for row in raw_aliases
                if UUID(row["node_id"]) in node_ids
            ]

        claims: list[dict[str, Any]] = []
        if include_claims:
            raw_claims = self._client.table(_CLAIMS_TABLE).select("*").eq("tenant_id", str(tenant_id)).execute().data
            claims = [self._normalize_claim(row) for row in raw_claims]

        return {
            "tenant_id": tenant_id,
            "nodes": self._stable_rows(nodes),
            "edges": self._stable_rows(edges),
            "aliases": self._stable_rows(aliases),
            "claims": self._stable_rows(claims),
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _insert(self, table_name: str, row: dict[str, Any]) -> list[dict[str, Any]]:
        rows = self._client.table(table_name).insert(row).execute().data
        if not rows:
            raise RuntimeError(f"Supabase insert returned no data for table={table_name}")
        return rows

    def _query_edges(
        self,
        *,
        tenant_id: UUID,
        from_node_id: UUID | None = None,
        to_node_id: UUID | None = None,
        edge_type: SmartGraphEdgeType | None = None,
        claim_type: SmartGraphClaimType | None = None,
        status: SmartGraphRecordStatus | None = "ACTIVE",
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        query = self._client.table(_EDGES_TABLE).select("*").eq("tenant_id", str(tenant_id))
        if from_node_id is not None:
            query = query.eq("from_node_id", str(from_node_id))
        if to_node_id is not None:
            query = query.eq("to_node_id", str(to_node_id))
        if edge_type is not None:
            query = query.eq("edge_type", edge_type)
        if claim_type is not None:
            query = query.eq("claim_type", claim_type)
        if status is not None:
            query = query.eq("status", status)
        return query.range(offset, offset + limit - 1).execute().data

    def _ensure_tenant_match(self, tenant_id: UUID) -> None:
        if not isinstance(tenant_id, UUID):
            raise ValueError("tenant_id must be a UUID")
        if str(tenant_id) != self.cliente_id:
            raise ValueError(f"cliente_id mismatch: repo={self.cliente_id!r}, tenant_id={str(tenant_id)!r}")

    def _ensure_node_exists(self, *, tenant_id: UUID, node_id: UUID, field_name: str) -> None:
        if self.get_node(tenant_id=tenant_id, node_id=node_id) is None:
            raise ValueError(f"{field_name} does not exist for tenant")

    def _ensure_optional_node_exists(
        self,
        tenant_id: UUID,
        node_id: UUID | None,
        field_name: str,
    ) -> None:
        if node_id is not None:
            self._ensure_node_exists(tenant_id=tenant_id, node_id=node_id, field_name=field_name)

    def _ensure_optional_edge_exists(
        self,
        tenant_id: UUID,
        edge_id: UUID | None,
        field_name: str,
    ) -> None:
        if edge_id is not None and self.get_edge(tenant_id=tenant_id, edge_id=edge_id) is None:
            raise ValueError(f"{field_name} does not exist for tenant")

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
    def _uuid_or_none(value: Any) -> UUID | None:
        if value is None:
            return None
        if isinstance(value, UUID):
            return value
        return UUID(str(value))

    @classmethod
    def _uuid_list(cls, values: Any) -> list[UUID]:
        return [UUID(str(item)) for item in values or []]

    @classmethod
    def _normalize_node(cls, row: dict[str, Any]) -> dict[str, Any]:
        normalized = dict(row)
        normalized["id"] = UUID(str(row["id"]))
        normalized["tenant_id"] = UUID(str(row["tenant_id"]))
        normalized["source_id"] = cls._uuid_or_none(row.get("source_id"))
        normalized["metadata"] = dict(row.get("metadata") or {})
        return normalized

    @classmethod
    def _normalize_edge(cls, row: dict[str, Any]) -> dict[str, Any]:
        normalized = dict(row)
        normalized["id"] = UUID(str(row["id"]))
        normalized["tenant_id"] = UUID(str(row["tenant_id"]))
        normalized["from_node_id"] = UUID(str(row["from_node_id"]))
        normalized["to_node_id"] = UUID(str(row["to_node_id"]))
        normalized["source_id"] = cls._uuid_or_none(row.get("source_id"))
        normalized["evidence_ids"] = cls._uuid_list(row.get("evidence_ids"))
        normalized["metadata"] = dict(row.get("metadata") or {})
        return normalized

    @classmethod
    def _normalize_alias(cls, row: dict[str, Any]) -> dict[str, Any]:
        normalized = dict(row)
        normalized["id"] = UUID(str(row["id"]))
        normalized["tenant_id"] = UUID(str(row["tenant_id"]))
        normalized["node_id"] = UUID(str(row["node_id"]))
        normalized["source_id"] = cls._uuid_or_none(row.get("source_id"))
        normalized["metadata"] = dict(row.get("metadata") or {})
        return normalized

    @classmethod
    def _normalize_claim(cls, row: dict[str, Any]) -> dict[str, Any]:
        normalized = dict(row)
        normalized["id"] = UUID(str(row["id"]))
        normalized["tenant_id"] = UUID(str(row["tenant_id"]))
        normalized["subject_node_id"] = cls._uuid_or_none(row.get("subject_node_id"))
        normalized["object_node_id"] = cls._uuid_or_none(row.get("object_node_id"))
        normalized["edge_id"] = cls._uuid_or_none(row.get("edge_id"))
        normalized["evidence_ids"] = cls._uuid_list(row.get("evidence_ids"))
        normalized["metadata"] = dict(row.get("metadata") or {})
        return normalized

    @staticmethod
    def _stable_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return sorted(rows, key=lambda item: str(item["id"]))

    @staticmethod
    def _now_iso() -> str:
        return datetime.now(UTC).isoformat()

    @staticmethod
    def _build_real_client() -> Any:
        import os

        try:
            from supabase import create_client  # type: ignore[import]
        except ImportError as exc:
            raise ImportError(
                "BLOCKED_MISSING_DEPENDENCY: la librería 'supabase' no está instalada. "
                "Instalar con: pip install supabase"
            ) from exc

        url = os.environ["SMARTPYME_SUPABASE_URL"]
        key = os.environ["SMARTPYME_SUPABASE_KEY"]
        return create_client(url, key)
