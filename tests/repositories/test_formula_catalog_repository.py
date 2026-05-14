from __future__ import annotations

import pytest

from app.contracts.formula_catalog import FormulaCatalogEntry, TenantFormulaOverride
from app.repositories.formula_catalog_repository import FormulaCatalogRepository


def test_formula_catalog_repository_saves_and_loads_formula(tmp_path) -> None:
    repo = FormulaCatalogRepository(tmp_path / "formula_catalog.db")
    formula = FormulaCatalogEntry(
        formula_id="rotacion_stock",
        name="Rotación de stock",
        description="Calcula rotación por producto.",
        required_inputs=["ventas_por_producto", "stock_actual", "periodo"],
        accepted_sources=["excel_ventas", "excel_stock"],
        assumptions=["mismo período"],
        unit="ratio",
        period="mensual",
        when_not_to_use="No usar con períodos incompatibles.",
        confidence=0.91,
        allows_tenant_override=True,
        metadata={"domain": "stock"},
    )

    repo.save_formula(formula)
    loaded = repo.get_formula("rotacion_stock")

    assert loaded is not None
    assert loaded.formula_id == "rotacion_stock"
    assert loaded.required_inputs == ["ventas_por_producto", "stock_actual", "periodo"]
    assert loaded.metadata == {"domain": "stock"}


def test_formula_catalog_repository_upserts_formula(tmp_path) -> None:
    repo = FormulaCatalogRepository(tmp_path / "formula_catalog.db")
    repo.save_formula(
        FormulaCatalogEntry(
            formula_id="margen_unitario",
            name="Margen unitario",
            description="Versión inicial.",
            required_inputs=["precio", "costo"],
        )
    )
    repo.save_formula(
        FormulaCatalogEntry(
            formula_id="margen_unitario",
            name="Margen unitario actualizado",
            description="Versión actualizada.",
            required_inputs=["precio_neto", "costo_total_unitario"],
        )
    )

    loaded = repo.get_formula("margen_unitario")

    assert loaded is not None
    assert loaded.name == "Margen unitario actualizado"
    assert loaded.required_inputs == ["precio_neto", "costo_total_unitario"]


def test_formula_catalog_repository_isolates_tenant_overrides(tmp_path) -> None:
    repo = FormulaCatalogRepository(tmp_path / "formula_catalog.db")
    repo.save_override(
        TenantFormulaOverride(
            cliente_id="CLIENT_A",
            formula_id="margen_unitario",
            override_id="override-a",
            overridden_inputs=["precio_neto", "costo_total_unitario"],
            approved_by="owner-a",
            reason="Regla de CLIENT_A.",
        )
    )
    repo.save_override(
        TenantFormulaOverride(
            cliente_id="CLIENT_B",
            formula_id="margen_unitario",
            override_id="override-b",
            overridden_inputs=["precio_lista", "costo_directo"],
            approved_by="owner-b",
            reason="Regla de CLIENT_B.",
        )
    )

    client_a_overrides = repo.list_overrides(cliente_id="CLIENT_A")

    assert len(client_a_overrides) == 1
    assert client_a_overrides[0].cliente_id == "CLIENT_A"
    assert client_a_overrides[0].override_id == "override-a"


def test_formula_catalog_repository_requires_cliente_for_overrides(tmp_path) -> None:
    repo = FormulaCatalogRepository(tmp_path / "formula_catalog.db")

    with pytest.raises(ValueError, match="cliente_id is required"):
        repo.list_overrides(cliente_id=" ")
