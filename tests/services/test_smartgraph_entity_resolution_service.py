from __future__ import annotations

from dataclasses import FrozenInstanceError
from uuid import UUID, uuid4

import pytest

from app.repositories.in_memory_smartgraph_repository import InMemorySmartGraphRepository
from app.services.smartgraph_integration_contract import (
    SmartGraphEntityResolutionInput,
    build_entity_resolution_input,
)
from app.services.smartgraph_entity_resolution_service import SmartGraphEntityResolutionService


@pytest.fixture
def tenant_id() -> UUID:
    return uuid4()


@pytest.fixture
def other_tenant_id() -> UUID:
    return uuid4()


@pytest.fixture
def repo() -> InMemorySmartGraphRepository:
    return InMemorySmartGraphRepository()


@pytest.fixture
def service(repo: InMemorySmartGraphRepository) -> SmartGraphEntityResolutionService:
    return SmartGraphEntityResolutionService(repo)


def test_normalize_alias_removes_accents(service: SmartGraphEntityResolutionService) -> None:
    assert service.normalize_alias(" Mercadería ") == "mercaderia"


def test_normalize_alias_collapses_internal_whitespace(service: SmartGraphEntityResolutionService) -> None:
    assert service.normalize_alias("STOCK   Crítico") == "stock critico"


def test_resolve_existing_entity(service: SmartGraphEntityResolutionService, tenant_id: UUID) -> None:
    created = service.resolve_or_create_entity(build_entity_resolution_input(
        tenant_id=tenant_id,
        node_type="PRODUCTO",
        canonical_key="producto_a",
        label="Producto A",
    ))

    resolved = service.resolve_or_create_entity(build_entity_resolution_input(
        tenant_id=tenant_id,
        node_type="PRODUCTO",
        canonical_key="  PRODUCTO_A ",
        label="Otro label",
    ))

    assert resolved["id"] == created["id"]


def test_create_canonical_node(service: SmartGraphEntityResolutionService, tenant_id: UUID) -> None:
    node = service.resolve_or_create_entity(build_entity_resolution_input(
        tenant_id=tenant_id,
        node_type="PRODUCTO",
        canonical_key="  Producto A  ",
        label="Producto A",
    ))

    assert node["canonical_key"] == "producto a"
    assert node["label"] == "Producto A"


def test_add_alias(
    service: SmartGraphEntityResolutionService,
    repo: InMemorySmartGraphRepository,
    tenant_id: UUID,
) -> None:
    node = service.resolve_or_create_entity(build_entity_resolution_input(
        tenant_id=tenant_id,
        node_type="PRODUCTO",
        canonical_key="producto a",
        label="Producto A",
        alias="Mercadería",
    ))

    matches = repo.find_nodes_by_alias(tenant_id=tenant_id, alias_normalized="mercaderia")
    assert [item["id"] for item in matches] == [node["id"]]


def test_no_duplicate_alias(
    service: SmartGraphEntityResolutionService,
    repo: InMemorySmartGraphRepository,
    tenant_id: UUID,
) -> None:
    node = service.resolve_or_create_entity(build_entity_resolution_input(
        tenant_id=tenant_id,
        node_type="PRODUCTO",
        canonical_key="producto a",
        label="Producto A",
        alias="Mercadería",
    ))
    service.resolve_or_create_entity(build_entity_resolution_input(
        tenant_id=tenant_id,
        node_type="PRODUCTO",
        canonical_key="producto a",
        label="Producto A",
        alias="  mercaderia  ",
    ))

    matches = repo.find_nodes_by_alias(tenant_id=tenant_id, alias_normalized="mercaderia")
    assert [item["id"] for item in matches] == [node["id"]]


def test_tenant_isolation(
    service: SmartGraphEntityResolutionService,
    tenant_id: UUID,
    other_tenant_id: UUID,
) -> None:
    node_a = service.resolve_or_create_entity(build_entity_resolution_input(
        tenant_id=tenant_id,
        node_type="PRODUCTO",
        canonical_key="producto a",
        label="Producto A",
    ))
    node_b = service.resolve_or_create_entity(build_entity_resolution_input(
        tenant_id=other_tenant_id,
        node_type="PRODUCTO",
        canonical_key="producto a",
        label="Producto A",
    ))

    assert node_a["id"] != node_b["id"]
    assert node_a["tenant_id"] != node_b["tenant_id"]


def test_service_accepts_valid_input_object(
    service: SmartGraphEntityResolutionService,
    tenant_id: UUID,
) -> None:
    entity_input = build_entity_resolution_input(
        tenant_id=tenant_id,
        node_type="PRODUCTO",
        canonical_key="producto_a",
        label="Producto A",
    )
    node = service.resolve_or_create_entity(entity_input)
    assert node["tenant_id"] == tenant_id


def test_service_rejects_raw_kwargs(service: SmartGraphEntityResolutionService, tenant_id: UUID) -> None:
    with pytest.raises(TypeError):
        service.resolve_or_create_entity(  # type: ignore[call-arg]
            tenant_id=tenant_id,
            node_type="PRODUCTO",
            canonical_key="producto_a",
            label="Producto A",
        )


def test_input_is_immutable(tenant_id: UUID) -> None:
    entity_input = build_entity_resolution_input(
        tenant_id=tenant_id,
        node_type="PRODUCTO",
        canonical_key="producto_a",
        label="Producto A",
    )
    with pytest.raises(FrozenInstanceError):
        entity_input.label = "Mutado"  # type: ignore[misc]


def test_consumer_builds_input_via_builder(
    service: SmartGraphEntityResolutionService,
    tenant_id: UUID,
) -> None:
    entity_input = build_entity_resolution_input(
        tenant_id=tenant_id,
        node_type="PRODUCTO",
        canonical_key="producto_a",
        label="Producto A",
        alias="Mercadería",
    )
    assert isinstance(entity_input, SmartGraphEntityResolutionInput)
    node = service.resolve_or_create_entity(entity_input)
    assert node["canonical_key"] == "producto_a"
