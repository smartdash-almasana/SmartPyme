from __future__ import annotations

from uuid import UUID, uuid4

import pytest

from app.services.smartgraph_integration_contract import (
    SmartGraphEntityResolutionInput,
    build_entity_resolution_input,
)


ZERO_UUID = UUID("00000000-0000-0000-0000-000000000000")


def test_build_input_valid() -> None:
    tenant_id = uuid4()
    payload = build_entity_resolution_input(
        tenant_id=tenant_id,
        node_type="PRODUCTO",
        canonical_key="  Producto A  ",
        label="  Producto A  ",
        alias=" Mercadería ",
    )

    assert isinstance(payload, SmartGraphEntityResolutionInput)
    assert payload.tenant_id == tenant_id
    assert payload.node_type == "PRODUCTO"
    assert payload.canonical_key == "  Producto A  "
    assert payload.label == "  Producto A  "
    assert payload.alias == " Mercadería "


def test_build_input_rejects_zero_uuid() -> None:
    with pytest.raises(ValueError, match="tenant_id"):
        build_entity_resolution_input(
            tenant_id=ZERO_UUID,
            node_type="PRODUCTO",
            canonical_key="producto_a",
            label="Producto A",
        )


def test_build_input_rejects_blank_canonical_key() -> None:
    with pytest.raises(ValueError, match="canonical_key"):
        build_entity_resolution_input(
            tenant_id=uuid4(),
            node_type="PRODUCTO",
            canonical_key="   ",
            label="Producto A",
        )


def test_build_input_rejects_blank_label() -> None:
    with pytest.raises(ValueError, match="label"):
        build_entity_resolution_input(
            tenant_id=uuid4(),
            node_type="PRODUCTO",
            canonical_key="producto_a",
            label="   ",
        )


def test_build_input_alias_is_optional() -> None:
    payload = build_entity_resolution_input(
        tenant_id=uuid4(),
        node_type="PRODUCTO",
        canonical_key="producto_a",
        label="Producto A",
    )
    assert payload.alias is None


def test_no_normalization_occurs_in_contract() -> None:
    payload = build_entity_resolution_input(
        tenant_id=uuid4(),
        node_type="PRODUCTO",
        canonical_key="  STOCK   Crítico  ",
        label="  Label  ",
        alias=" Mercadería ",
    )
    assert payload.canonical_key == "  STOCK   Crítico  "
    assert payload.alias == " Mercadería "
