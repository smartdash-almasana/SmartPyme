from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from app.repositories.smartgraph_repository_port import SmartGraphNodeType


@dataclass(frozen=True)
class SmartGraphEntityResolutionInput:
    tenant_id: UUID
    node_type: SmartGraphNodeType
    canonical_key: str
    label: str
    alias: str | None = None


def build_entity_resolution_input(
    *,
    tenant_id: UUID,
    node_type: SmartGraphNodeType,
    canonical_key: str,
    label: str,
    alias: str | None = None,
) -> SmartGraphEntityResolutionInput:
    if not isinstance(tenant_id, UUID):
        raise ValueError("tenant_id must be a UUID")
    if tenant_id.int == 0:
        raise ValueError("tenant_id must not be empty")
    if not isinstance(canonical_key, str) or not canonical_key.strip():
        raise ValueError("canonical_key must not be blank")
    if not isinstance(label, str) or not label.strip():
        raise ValueError("label must not be blank")
    if alias is not None and not isinstance(alias, str):
        raise ValueError("alias must be a string when provided")

    return SmartGraphEntityResolutionInput(
        tenant_id=tenant_id,
        node_type=node_type,
        canonical_key=canonical_key,
        label=label,
        alias=alias,
    )
