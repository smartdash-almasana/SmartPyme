import json
from pathlib import Path

import pytest

from app.services.formula_catalog_service import FormulaCatalogService


def test_formula_catalog_service_loads_default_catalog():
    service = FormulaCatalogService()

    assert service.catalog.catalog_id == "formulas_smartpyme_v0"
    assert service.catalog.version == "0.1"
    assert len(service.list_items()) == 95
    assert "finanzas" in service.list_domains()
    assert "stock" in service.list_domains()


def test_formula_catalog_service_gets_formula_by_id():
    service = FormulaCatalogService()

    item = service.get_item("FORM_011")

    assert item is not None
    assert item.nombre == "Margen Bruto por Producto"
    assert item.dominio == "finanzas"
    assert "precio_venta_unitario" in item.datos_minimos_a_pedir
    assert "REN_001" in item.patologias_asociadas
    assert item.variables_requeridas[0].nombre == "precio_venta"


def test_formula_catalog_service_lists_by_domain_and_pathology():
    service = FormulaCatalogService()

    finance_items = service.list_by_domain("finanzas")
    ren_001_items = service.list_by_pathology("REN_001")

    assert {item.id for item in finance_items} >= {"FORM_001", "FORM_011", "FORM_076"}
    assert "FORM_011" in {item.id for item in ren_001_items}
    assert service.list_by_domain("dominio_inexistente") == []
    assert service.list_by_pathology("PAT_INEXISTENTE") == []


def test_formula_catalog_service_lists_by_criticality():
    service = FormulaCatalogService()

    high_criticality_items = service.list_by_criticality("alta")

    assert "FORM_001" in {item.id for item in high_criticality_items}
    assert service.list_by_criticality("inexistente") == []


def test_formula_catalog_service_returns_empty_tuples_for_unknown_item():
    service = FormulaCatalogService()

    assert service.get_item("NO_EXISTE") is None
    assert service.get_minimum_data("NO_EXISTE") == ()
    assert service.get_pathologies("NO_EXISTE") == ()


def test_formula_catalog_service_rejects_invalid_catalog(tmp_path: Path):
    catalog_path = tmp_path / "invalid_formula_catalog.json"
    catalog_path.write_text(
        json.dumps(
            {
                "catalog_id": "invalid",
                "version": "0.1",
                "description": "invalid catalog",
                "criteria": "invalid criteria",
                "items": [
                    {
                        "id": "FORM_BAD",
                        "nombre": "bad_formula",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Formula catalog item missing required fields"):
        FormulaCatalogService(catalog_path)
