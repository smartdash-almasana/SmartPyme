"""
Motor operacional soberano MVP — diagnóstico básico determinístico.

Lee evidencia persistida de un tenant y aplica reglas explícitas para
generar hallazgos accionables.

Sin IA. Sin LLM. Sin embeddings. Sin graph. Sin heurísticas mágicas.
Solo reglas explícitas. Fail-closed. Deterministic.
"""
from __future__ import annotations

from typing import Any

from app.contracts.bem_payloads import CuratedEvidenceRecord
from app.repositories.curated_evidence_repository import CuratedEvidenceRepositoryBackend


# ---------------------------------------------------------------------------
# Constantes de severidad
# ---------------------------------------------------------------------------

SEVERITY_LOW = "LOW"
SEVERITY_MEDIUM = "MEDIUM"
SEVERITY_HIGH = "HIGH"


# ---------------------------------------------------------------------------
# Helpers de validación de campos numéricos
# ---------------------------------------------------------------------------


def _to_number(value: Any) -> float | None:
    """Convierte a float si es int o float; retorna None en cualquier otro caso."""
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


# ---------------------------------------------------------------------------
# Reglas de hallazgo
# ---------------------------------------------------------------------------


def _check_venta_bajo_costo(
    payload: dict[str, Any],
    evidence_id: str,
) -> dict[str, str] | None:
    """
    VENTA_BAJO_COSTO: precio_venta < costo_unitario

    Severity: HIGH — vender por debajo del costo destruye margen.
    """
    precio = _to_number(payload.get("precio_venta"))
    costo = _to_number(payload.get("costo_unitario"))

    if precio is None or costo is None:
        return None
    if precio < costo:
        return {
            "finding_type": "VENTA_BAJO_COSTO",
            "severity": SEVERITY_HIGH,
            "message": (
                f"precio_venta ({precio}) es menor que costo_unitario ({costo}). "
                "Se está vendiendo por debajo del costo."
            ),
            "evidence_id": evidence_id,
        }
    return None


def _check_margen_critico(
    payload: dict[str, Any],
    evidence_id: str,
) -> dict[str, str] | None:
    """
    MARGEN_CRITICO: precio_venta > costo_unitario y margen < 5%.

    Severity: HIGH — margen positivo pero insuficiente para absorber gastos,
    descuentos o variaciones de costo.
    """
    precio = _to_number(payload.get("precio_venta"))
    costo = _to_number(payload.get("costo_unitario"))

    if precio is None or costo is None:
        return None
    if precio <= 0 or precio <= costo:
        return None

    margen = (precio - costo) / precio
    if margen < 0.05:
        return {
            "finding_type": "MARGEN_CRITICO",
            "severity": SEVERITY_HIGH,
            "message": (
                f"margen ({margen:.2%}) es menor al umbral crítico de 5%. "
                "La venta tiene margen positivo pero insuficiente."
            ),
            "evidence_id": evidence_id,
        }
    return None


def _check_costo_cero_sospechoso(
    payload: dict[str, Any],
    evidence_id: str,
) -> dict[str, str] | None:
    """
    COSTO_CERO_SOSPECHOSO: costo_unitario == 0 y precio_venta > 0.

    Severity: MEDIUM — puede indicar costo faltante, error de importación o
    producto sin costeo cargado.
    """
    precio = _to_number(payload.get("precio_venta"))
    costo = _to_number(payload.get("costo_unitario"))

    if precio is None or costo is None:
        return None
    if costo == 0 and precio > 0:
        return {
            "finding_type": "COSTO_CERO_SOSPECHOSO",
            "severity": SEVERITY_MEDIUM,
            "message": (
                f"costo_unitario ({costo}) es 0 con precio_venta ({precio}) positivo. "
                "Puede faltar el costo o existir un error de importación."
            ),
            "evidence_id": evidence_id,
        }
    return None


def _check_venta_sin_stock(
    payload: dict[str, Any],
    evidence_id: str,
) -> dict[str, str] | None:
    """
    VENTA_SIN_STOCK: cantidad == 0 y existe venta valorizada.

    Severity: HIGH — venta registrada sin unidades asociadas requiere revisión
    inmediata de stock, facturación o integración de inventario.
    """
    cantidad = _to_number(payload.get("cantidad"))
    precio = _to_number(payload.get("precio_venta"))
    monto = _to_number(payload.get("monto_total"))

    if cantidad is None:
        return None
    if cantidad == 0 and ((precio is not None and precio > 0) or (monto is not None and monto > 0)):
        return {
            "finding_type": "VENTA_SIN_STOCK",
            "severity": SEVERITY_HIGH,
            "message": (
                "cantidad es 0 pero existe una venta valorizada. "
                "Puede haber venta sin stock, error de carga o integración incompleta."
            ),
            "evidence_id": evidence_id,
        }
    return None


def _check_stock_negativo(
    payload: dict[str, Any],
    evidence_id: str,
) -> dict[str, str] | None:
    """
    STOCK_NEGATIVO: stock_actual < 0

    Severity: MEDIUM — indica error de registro o descubierto operativo.
    """
    stock = _to_number(payload.get("stock_actual"))

    if stock is None:
        return None
    if stock < 0:
        return {
            "finding_type": "STOCK_NEGATIVO",
            "severity": SEVERITY_MEDIUM,
            "message": (
                f"stock_actual ({stock}) es negativo. "
                "Posible error de registro o descubierto operativo."
            ),
            "evidence_id": evidence_id,
        }
    return None


def _check_movimiento_inconsistente(
    payload: dict[str, Any],
    evidence_id: str,
) -> dict[str, str] | None:
    """
    MOVIMIENTO_INCONSISTENTE: cantidad == 0 y monto_total > 0

    Severity: MEDIUM — movimiento con monto pero sin cantidad es inconsistente.
    """
    cantidad = _to_number(payload.get("cantidad"))
    monto = _to_number(payload.get("monto_total"))

    if cantidad is None or monto is None:
        return None
    if cantidad == 0 and monto > 0:
        return {
            "finding_type": "MOVIMIENTO_INCONSISTENTE",
            "severity": SEVERITY_MEDIUM,
            "message": (
                f"cantidad es 0 pero monto_total ({monto}) es mayor que 0. "
                "El movimiento es inconsistente."
            ),
            "evidence_id": evidence_id,
        }
    return None


# ---------------------------------------------------------------------------
# Reglas registradas — orden determinístico
# ---------------------------------------------------------------------------

_RULES = [
    _check_venta_bajo_costo,
    _check_margen_critico,
    _check_costo_cero_sospechoso,
    _check_venta_sin_stock,
    _check_stock_negativo,
    _check_movimiento_inconsistente,
]


# ---------------------------------------------------------------------------
# Servicio
# ---------------------------------------------------------------------------


def _require_non_empty(value: str, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} es obligatorio y no puede estar vacío")


def _apply_rules(record: CuratedEvidenceRecord) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    for rule in _RULES:
        result = rule(record.payload, record.evidence_id)
        if result is not None:
            findings.append(result)
    return findings


class BasicOperationalDiagnosticService:
    """
    Servicio de diagnóstico operacional básico MVP.

    Lee evidencia persistida de un tenant y aplica reglas determinísticas
    para detectar síntomas operacionales accionables.

    Parámetros
    ----------
    repository:
        Instancia de CuratedEvidenceRepositoryBackend.
    """

    def __init__(self, repository: CuratedEvidenceRepositoryBackend) -> None:
        self._repository = repository

    def build_report(self, tenant_id: str) -> dict[str, Any]:
        """
        Genera el reporte de diagnóstico para el tenant indicado.

        Retorna:
            {
                "tenant_id": str,
                "findings": list[dict],
                "evidence_count": int,
            }

        Falla si tenant_id está vacío (fail-closed).
        Retorna findings vacío si el tenant no tiene evidencia.
        """
        _require_non_empty(tenant_id, "tenant_id")

        records = self._repository.list_by_tenant(tenant_id=tenant_id)

        findings: list[dict[str, str]] = []
        for record in records:
            findings.extend(_apply_rules(record))

        return {
            "tenant_id": tenant_id,
            "findings": findings,
            "evidence_count": len(records),
        }
