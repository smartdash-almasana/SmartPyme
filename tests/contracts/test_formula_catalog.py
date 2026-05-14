from __future__ import annotations

import pytest

from app.contracts.formula_catalog import FormulaCatalogEntry, TenantFormulaOverride


def test_formula_catalog_entry_rejects_duplicate_inputs() -> None:
    with pytest.raises(ValueError, match="required_inputs cannot contain duplicates"):
        FormulaCatalogEntry(
            formula_id="rotacion_stock",
            name="Rotación de stock",
            description="Calcula rotación por producto.",
            required_inputs=["ventas_por_producto", "ventas_por_producto"],
        )


def test_formula_catalog_entry_declares_required_inputs_and_limits() -> None:
    formula = FormulaCatalogEntry(
        formula_id="rotacion_stock",
        name="Rotación de stock",
        description="Calcula rotación por producto en un período.",
        required_inputs=["ventas_por_producto", "stock_actual", "periodo"],
        accepted_sources=["excel_ventas", "excel_stock"],
        assumptions=["ventas y stock pertenecen al mismo período"],
        unit="ratio",
        period="mensual",
        when_not_to_use="No usar si ventas y stock pertenecen a períodos distintos.",
        confidence=0.95,
        allows_tenant_override=True,
    )

    assert formula.formula_id == "rotacion_stock"
    assert formula.required_inputs == ["ventas_por_producto", "stock_actual", "periodo"]
    assert formula.allows_tenant_override is True


def test_tenant_formula_override_requires_owner_reason() -> None:
    with pytest.raises(ValueError, match="reason is required"):
        TenantFormulaOverride(
            cliente_id="C1",
            formula_id="margen_unitario",
            override_id="override-1",
            approved_by="owner",
            reason=" ",
        )


def test_tenant_formula_override_declares_tenant_specific_inputs() -> None:
    override = TenantFormulaOverride(
        cliente_id="C1",
        formula_id="margen_unitario",
        override_id="override-1",
        overridden_inputs=["precio_neto", "costo_total_unitario"],
        assumptions=["el costo logístico se incluye como costo directo"],
        approved_by="owner",
        reason="La PyME calcula margen incluyendo logística en costo directo.",
    )

    assert override.cliente_id == "C1"
    assert override.overridden_inputs == ["precio_neto", "costo_total_unitario"]
