from __future__ import annotations

import re
import unicodedata
from typing import Any
from uuid import UUID

from app.repositories.smartgraph_repository_port import (
    SmartGraphRepositoryPort,
)
from app.services.smartgraph_integration_contract import SmartGraphEntityResolutionInput


class SmartGraphEntityResolutionService:
    def __init__(self, repository: SmartGraphRepositoryPort) -> None:
        self.repository = repository

    def normalize_alias(self, value: str) -> str:
        if not isinstance(value, str):
            raise ValueError("value must be a string")

        normalized = value.strip().lower()
        normalized = "".join(
            ch
            for ch in unicodedata.normalize("NFKD", normalized)
            if not unicodedata.combining(ch)
        )
        normalized = re.sub(r"\s+", " ", normalized)
        return normalized

    def resolve_or_create_entity(
        self,
        entity_input: SmartGraphEntityResolutionInput,
    ) -> dict[str, Any]:
        tenant_id = entity_input.tenant_id
        node_type = entity_input.node_type
        canonical_key = entity_input.canonical_key
        label = entity_input.label
        alias = entity_input.alias

        self._ensure_tenant_id(tenant_id)

        canonical_key_normalized = self.normalize_alias(canonical_key)
        if not canonical_key_normalized:
            raise ValueError("canonical_key must not be blank")

        label_clean = label.strip() if isinstance(label, str) else ""
        if not label_clean:
            raise ValueError("label must not be blank")

        node = self.repository.get_node_by_canonical_key(
            tenant_id=tenant_id,
            node_type=node_type,
            canonical_key=canonical_key_normalized,
        )
        if node is None:
            node = self.repository.create_node(
                tenant_id=tenant_id,
                node_type=node_type,
                canonical_key=canonical_key_normalized,
                label=label_clean,
            )

        self._maybe_add_alias(
            tenant_id=tenant_id,
            node_id=node["id"],
            alias=alias,
            canonical_key_normalized=canonical_key_normalized,
        )
        return node

    def _maybe_add_alias(
        self,
        *,
        tenant_id: UUID,
        node_id: UUID,
        alias: str | None,
        canonical_key_normalized: str,
    ) -> None:
        if alias is None:
            return

        alias_clean = alias.strip()
        if not alias_clean:
            return

        alias_normalized = self.normalize_alias(alias_clean)
        if not alias_normalized or alias_normalized == canonical_key_normalized:
            return

        matches = self.repository.find_nodes_by_alias(
            tenant_id=tenant_id,
            alias_normalized=alias_normalized,
        )
        if any(match["id"] == node_id for match in matches):
            return

        self.repository.add_alias(
            tenant_id=tenant_id,
            node_id=node_id,
            alias=alias_clean,
            alias_normalized=alias_normalized,
        )

    @staticmethod
    def _ensure_tenant_id(tenant_id: UUID) -> None:
        if not isinstance(tenant_id, UUID):
            raise ValueError("tenant_id must be a UUID")
        if tenant_id.int == 0:
            raise ValueError("tenant_id must not be empty")
