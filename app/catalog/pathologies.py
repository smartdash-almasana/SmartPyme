# ruff: noqa: I001

from __future__ import annotations

from app.contracts.pathology_contract import PathologyDefinition, PathologySeverity


PATHOLOGY_CATALOG: dict[str, PathologyDefinition] = {
    "margen_bruto_negativo": PathologyDefinition(
        pathology_id="margen_bruto_negativo",
        formula_id="margen_bruto",
        description="Detecta margen bruto negativo sobre ventas y costos declarados.",
        severity=PathologySeverity.HIGH,
        suggested_action=(
            "Revisar costos de materia prima o ajustar precios de venta."
        ),
    ),
    "trampa_producto_ads_negativo": PathologyDefinition(
        pathology_id="trampa_producto_ads_negativo",
        formula_id="margen_real_estimado",
        description=(
            "Detecta productos cuya rentabilidad real queda destruida por "
            "inversión publicitaria."
        ),
        severity=PathologySeverity.HIGH,
        suggested_action=(
            "Pausar campañas de Mercado Ads para el SKU afectado y revisar "
            "estructura de costos."
        ),
    ),
    "venta_bajo_costo": PathologyDefinition(
        pathology_id="venta_bajo_costo",
        formula_id="ganancia_bruta",
        description="Detecta ventas donde el costo supera al ingreso bruto.",
        severity=PathologySeverity.HIGH,
        suggested_action=(
            "Bloquear reposición del producto hasta corregir precio, costo o "
            "descuentos aplicados."
        ),
    ),
    "falla_precision_int64": PathologyDefinition(
        pathology_id="falla_precision_int64",
        formula_id="integridad_identificador",
        description=(
            "Detecta identificadores largos degradados por herramientas "
            "intermedias como planillas."
        ),
        severity=PathologySeverity.HIGH,
        suggested_action=(
            "Forzar tratamiento de identificadores como texto y reprocesar la "
            "fuente original."
        ),
    ),
    "limbo_liquidaciones_ml": PathologyDefinition(
        pathology_id="limbo_liquidaciones_ml",
        formula_id="conciliacion_liquidaciones",
        description=(
            "Detecta ventas o liquidaciones sin conciliación clara entre "
            "operación, cobro y cuenta destino."
        ),
        severity=PathologySeverity.HIGH,
        suggested_action=(
            "Conciliar liquidaciones pendientes contra órdenes, pagos y "
            "movimientos bancarios."
        ),
    ),
    "clasificacion_iva_lesiva": PathologyDefinition(
        pathology_id="clasificacion_iva_lesiva",
        formula_id="impacto_impositivo_estimado",
        description=(
            "Detecta clasificación fiscal potencialmente perjudicial para la PyME."
        ),
        severity=PathologySeverity.MEDIUM,
        suggested_action=(
            "Revisar clasificación de IVA con contador y corregir reglas de "
            "imputación."
        ),
    ),
}


PATHOLOGY_METADATA: dict[str, dict] = {
    "margen_bruto_negativo": {
        "category": "rentabilidad",
        "impact_capital_time": "Pérdida directa por cada unidad vendida.",
        "requires_formula": True,
    },
    "trampa_producto_ads_negativo": {
        "category": "ads_rentabilidad",
        "impact_capital_time": (
            "Descapitalización por inversión publicitaria sobre productos "
            "sin margen real."
        ),
        "requires_formula": True,
    },
    "venta_bajo_costo": {
        "category": "pricing",
        "impact_capital_time": (
            "Pérdida operacional directa por precio menor al costo."
        ),
        "requires_formula": True,
    },
    "falla_precision_int64": {
        "category": "integridad_datos",
        "impact_capital_time": (
            "Riesgo de trazabilidad por corrupción de identificadores críticos."
        ),
        "requires_formula": False,
    },
    "limbo_liquidaciones_ml": {
        "category": "conciliacion",
        "impact_capital_time": (
            "Capital no localizado o mal imputado en el flujo de cobros."
        ),
        "requires_formula": True,
    },
    "clasificacion_iva_lesiva": {
        "category": "impuestos",
        "impact_capital_time": (
            "Riesgo de sobrepago, deuda fiscal o decisión contable lesiva."
        ),
        "requires_formula": True,
    },
}


def get_pathology_definition(pathology_id: str) -> PathologyDefinition | None:
    return PATHOLOGY_CATALOG.get(pathology_id)


def list_pathology_definitions() -> list[PathologyDefinition]:
    return list(PATHOLOGY_CATALOG.values())


def get_pathology_metadata(pathology_id: str) -> dict:
    return dict(PATHOLOGY_METADATA.get(pathology_id, {}))
