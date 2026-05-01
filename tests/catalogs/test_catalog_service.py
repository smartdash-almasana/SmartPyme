import json
from pathlib import Path

import pytest

from app.services.catalog_service import CatalogService


def test_catalog_service_loads_default_pathology_catalog():
    service = CatalogService()

    assert service.catalog.catalog_id == "patologias_pyme_v0"
    assert service.catalog.version == "0.1"
    assert len(service.list_items()) >= 1
    assert "liquidez" in service.list_domains()


def test_catalog_service_gets_pathology_by_id():
    service = CatalogService()

    item = service.get_item("LIQ_001")

    assert item is not None
    assert item.domain == "liquidez"
    assert item.name == "descalce_ventas_cobranzas"
    assert "total_ventas_periodo" in item.minimum_data
    assert "Flujo de fondos proyectado" in item.associated_formulas


def test_catalog_service_lists_items_by_domain():
    service = CatalogService()

    liquidity_items = service.list_by_domain("liquidez")

    assert {item.id for item in liquidity_items} >= {"LIQ_001", "LIQ_002"}
    assert service.list_by_domain("dominio_inexistente") == []


def test_catalog_service_returns_empty_tuples_for_unknown_item():
    service = CatalogService()

    assert service.get_item("NO_EXISTE") is None
    assert service.get_minimum_data("NO_EXISTE") == ()
    assert service.get_associated_formulas("NO_EXISTE") == ()


def test_catalog_service_rejects_invalid_catalog(tmp_path: Path):
    catalog_path = tmp_path / "invalid_catalog.json"
    catalog_path.write_text(
        json.dumps(
            {
                "catalog_id": "invalid",
                "version": "0.1",
                "description": "invalid catalog",
                "criteria": "invalid criteria",
                "items": [
                    {
                        "id": "BAD_001",
                        "domain": "liquidez",
                        "name": "bad_item",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Catalog item missing required fields"):
        CatalogService(catalog_path)
