"""
Tests determinísticos para BasicOperationalDiagnosticService.

Cada test usa un SQLite temporal aislado.
Sin mocks. Sin side effects. Fail-closed.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from app.contracts.bem_payloads import (
    BemSourceMetadata,
    CuratedEvidenceRecord,
    EvidenceKind,
)
from app.repositories.curated_evidence_repository import CuratedEvidenceRepositoryBackend
from app.services.basic_operational_diagnostic_service import (
    BasicOperationalDiagnosticService,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def repo(tmp_path: Path) -> CuratedEvidenceRepositoryBackend:
    return CuratedEvidenceRepositoryBackend(db_path=tmp_path / "diag.db")


@pytest.fixture()
def service(repo: CuratedEvidenceRepositoryBackend) -> BasicOperationalDiagnosticService:
    return BasicOperationalDiagnosticService(repository=repo)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_SOURCE = BemSourceMetadata(source_name="archivo.xlsx", source_type="excel")


def _insert(
    repo: CuratedEvidenceRepositoryBackend,
    evidence_id: str,
    payload: dict,
    tenant_id: str = "tenant-1",
) -> None:
    repo.create(
        CuratedEvidenceRecord(
            tenant_id=tenant_id,
            evidence_id=evidence_id,
            kind=EvidenceKind.EXCEL,
            payload=payload,
            source_metadata=_SOURCE,
            received_at="2024-01-15T10:00:00+00:00",
        )
    )


def _finding_types(report: dict) -> list[str]:
    return [f["finding_type"] for f in report["findings"]]


# ---------------------------------------------------------------------------
# Tenant sin evidencia
# ---------------------------------------------------------------------------


def test_report_empty_when_no_evidence(
    service: BasicOperationalDiagnosticService,
) -> None:
    report = service.build_report("tenant-sin-datos")

    assert report["tenant_id"] == "tenant-sin-datos"
    assert report["findings"] == []
    assert report["evidence_count"] == 0


# ---------------------------------------------------------------------------
# VENTA_BAJO_COSTO
# ---------------------------------------------------------------------------


def test_venta_bajo_costo_detected(
    repo: CuratedEvidenceRepositoryBackend,
    service: BasicOperationalDiagnosticService,
) -> None:
    _insert(repo, "ev-001", {"precio_venta": 50.0, "costo_unitario": 80.0})

    report = service.build_report("tenant-1")

    assert "VENTA_BAJO_COSTO" in _finding_types(report)


def test_venta_bajo_costo_severity_high(
    repo: CuratedEvidenceRepositoryBackend,
    service: BasicOperationalDiagnosticService,
) -> None:
    _insert(repo, "ev-001", {"precio_venta": 10.0, "costo_unitario": 20.0})

    report = service.build_report("tenant-1")
    finding = next(f for f in report["findings"] if f["finding_type"] == "VENTA_BAJO_COSTO")

    assert finding["severity"] == "HIGH"
    assert finding["evidence_id"] == "ev-001"


def test_venta_bajo_costo_not_triggered_when_equal(
    repo: CuratedEvidenceRepositoryBackend,
    service: BasicOperationalDiagnosticService,
) -> None:
    _insert(repo, "ev-001", {"precio_venta": 100.0, "costo_unitario": 100.0})

    report = service.build_report("tenant-1")

    assert "VENTA_BAJO_COSTO" not in _finding_types(report)


def test_venta_bajo_costo_not_triggered_when_above(
    repo: CuratedEvidenceRepositoryBackend,
    service: BasicOperationalDiagnosticService,
) -> None:
    _insert(repo, "ev-001", {"precio_venta": 150.0, "costo_unitario": 100.0})

    report = service.build_report("tenant-1")

    assert "VENTA_BAJO_COSTO" not in _finding_types(report)


# ---------------------------------------------------------------------------
# MARGEN_CRITICO
# ---------------------------------------------------------------------------


def test_margen_critico_detected(
    repo: CuratedEvidenceRepositoryBackend,
    service: BasicOperationalDiagnosticService,
) -> None:
    _insert(repo, "ev-001", {"precio_venta": 100.0, "costo_unitario": 96.0})

    report = service.build_report("tenant-1")

    assert "MARGEN_CRITICO" in _finding_types(report)


def test_margen_critico_severity_high(
    repo: CuratedEvidenceRepositoryBackend,
    service: BasicOperationalDiagnosticService,
) -> None:
    _insert(repo, "ev-001", {"precio_venta": 100.0, "costo_unitario": 96.0})

    report = service.build_report("tenant-1")
    finding = next(f for f in report["findings"] if f["finding_type"] == "MARGEN_CRITICO")

    assert finding["severity"] == "HIGH"
    assert finding["evidence_id"] == "ev-001"


def test_margen_critico_not_triggered_when_margin_ok(
    repo: CuratedEvidenceRepositoryBackend,
    service: BasicOperationalDiagnosticService,
) -> None:
    _insert(repo, "ev-001", {"precio_venta": 100.0, "costo_unitario": 80.0})

    report = service.build_report("tenant-1")

    assert "MARGEN_CRITICO" not in _finding_types(report)


# ---------------------------------------------------------------------------
# STOCK_NEGATIVO
# ---------------------------------------------------------------------------


def test_stock_negativo_detected(
    repo: CuratedEvidenceRepositoryBackend,
    service: BasicOperationalDiagnosticService,
) -> None:
    _insert(repo, "ev-001", {"stock_actual": -5})

    report = service.build_report("tenant-1")

    assert "STOCK_NEGATIVO" in _finding_types(report)


def test_stock_negativo_severity_medium(
    repo: CuratedEvidenceRepositoryBackend,
    service: BasicOperationalDiagnosticService,
) -> None:
    _insert(repo, "ev-001", {"stock_actual": -1})

    report = service.build_report("tenant-1")
    finding = next(f for f in report["findings"] if f["finding_type"] == "STOCK_NEGATIVO")

    assert finding["severity"] == "MEDIUM"
    assert finding["evidence_id"] == "ev-001"


def test_stock_negativo_not_triggered_when_zero(
    repo: CuratedEvidenceRepositoryBackend,
    service: BasicOperationalDiagnosticService,
) -> None:
    _insert(repo, "ev-001", {"stock_actual": 0})

    report = service.build_report("tenant-1")

    assert "STOCK_NEGATIVO" not in _finding_types(report)


def test_stock_negativo_not_triggered_when_positive(
    repo: CuratedEvidenceRepositoryBackend,
    service: BasicOperationalDiagnosticService,
) -> None:
    _insert(repo, "ev-001", {"stock_actual": 100})

    report = service.build_report("tenant-1")

    assert "STOCK_NEGATIVO" not in _finding_types(report)


# ---------------------------------------------------------------------------
# MOVIMIENTO_INCONSISTENTE
# ---------------------------------------------------------------------------


def test_movimiento_inconsistente_detected(
    repo: CuratedEvidenceRepositoryBackend,
    service: BasicOperationalDiagnosticService,
) -> None:
    _insert(repo, "ev-001", {"cantidad": 0, "monto_total": 500.0})

    report = service.build_report("tenant-1")

    assert "MOVIMIENTO_INCONSISTENTE" in _finding_types(report)


def test_movimiento_inconsistente_severity_medium(
    repo: CuratedEvidenceRepositoryBackend,
    service: BasicOperationalDiagnosticService,
) -> None:
    _insert(repo, "ev-001", {"cantidad": 0, "monto_total": 1.0})

    report = service.build_report("tenant-1")
    finding = next(
        f for f in report["findings"] if f["finding_type"] == "MOVIMIENTO_INCONSISTENTE"
    )

    assert finding["severity"] == "MEDIUM"
    assert finding["evidence_id"] == "ev-001"


def test_movimiento_inconsistente_not_triggered_when_cantidad_nonzero(
    repo: CuratedEvidenceRepositoryBackend,
    service: BasicOperationalDiagnosticService,
) -> None:
    _insert(repo, "ev-001", {"cantidad": 5, "monto_total": 500.0})

    report = service.build_report("tenant-1")

    assert "MOVIMIENTO_INCONSISTENTE" not in _finding_types(report)


def test_movimiento_inconsistente_not_triggered_when_monto_zero(
    repo: CuratedEvidenceRepositoryBackend,
    service: BasicOperationalDiagnosticService,
) -> None:
    _insert(repo, "ev-001", {"cantidad": 0, "monto_total": 0.0})

    report = service.build_report("tenant-1")

    assert "MOVIMIENTO_INCONSISTENTE" not in _finding_types(report)


# ---------------------------------------------------------------------------
# Múltiples findings en un mismo registro
# ---------------------------------------------------------------------------


def test_multiple_findings_from_single_record(
    repo: CuratedEvidenceRepositoryBackend,
    service: BasicOperationalDiagnosticService,
) -> None:
    _insert(
        repo,
        "ev-001",
        {
            "precio_venta": 10.0,
            "costo_unitario": 50.0,
            "stock_actual": -3,
            "cantidad": 0,
            "monto_total": 200.0,
        },
    )

    report = service.build_report("tenant-1")
    types = _finding_types(report)

    assert "VENTA_BAJO_COSTO" in types
    assert "VENTA_SIN_STOCK" in types
    assert "STOCK_NEGATIVO" in types
    assert "MOVIMIENTO_INCONSISTENTE" in types
    assert len(types) == 4


def test_multiple_findings_from_multiple_records(
    repo: CuratedEvidenceRepositoryBackend,
    service: BasicOperationalDiagnosticService,
) -> None:
    _insert(repo, "ev-001", {"precio_venta": 5.0, "costo_unitario": 20.0})
    _insert(repo, "ev-002", {"stock_actual": -10})

    report = service.build_report("tenant-1")
    types = _finding_types(report)

    assert "VENTA_BAJO_COSTO" in types
    assert "STOCK_NEGATIVO" in types
    assert report["evidence_count"] == 2


# ---------------------------------------------------------------------------
# Tenant isolation
# ---------------------------------------------------------------------------


def test_tenant_isolation_findings(
    repo: CuratedEvidenceRepositoryBackend,
    service: BasicOperationalDiagnosticService,
) -> None:
    _insert(repo, "ev-001", {"precio_venta": 1.0, "costo_unitario": 100.0}, tenant_id="tenant-a")
    _insert(repo, "ev-002", {"stock_actual": 50}, tenant_id="tenant-b")

    report_a = service.build_report("tenant-a")
    report_b = service.build_report("tenant-b")

    assert "VENTA_BAJO_COSTO" in _finding_types(report_a)
    assert "VENTA_BAJO_COSTO" not in _finding_types(report_b)

    assert "STOCK_NEGATIVO" not in _finding_types(report_a)
    assert "STOCK_NEGATIVO" not in _finding_types(report_b)


def test_tenant_isolation_evidence_count(
    repo: CuratedEvidenceRepositoryBackend,
    service: BasicOperationalDiagnosticService,
) -> None:
    _insert(repo, "ev-001", {"x": 1}, tenant_id="tenant-a")
    _insert(repo, "ev-002", {"x": 2}, tenant_id="tenant-a")
    _insert(repo, "ev-003", {"x": 3}, tenant_id="tenant-b")

    assert service.build_report("tenant-a")["evidence_count"] == 2
    assert service.build_report("tenant-b")["evidence_count"] == 1


# ---------------------------------------------------------------------------
# Payload parcial (campos faltantes → no finding)
# ---------------------------------------------------------------------------


def test_partial_payload_no_false_positives(
    repo: CuratedEvidenceRepositoryBackend,
    service: BasicOperationalDiagnosticService,
) -> None:
    # Solo tiene precio_venta, sin costo_unitario → no puede evaluar VENTA_BAJO_COSTO
    _insert(repo, "ev-001", {"precio_venta": 10.0})

    report = service.build_report("tenant-1")

    assert report["findings"] == []


def test_partial_payload_stock_only(
    repo: CuratedEvidenceRepositoryBackend,
    service: BasicOperationalDiagnosticService,
) -> None:
    # Solo tiene stock_actual positivo → sin findings
    _insert(repo, "ev-001", {"stock_actual": 10})

    report = service.build_report("tenant-1")

    assert report["findings"] == []


# ---------------------------------------------------------------------------
# Payload vacío (sin campos relevantes → sin findings)
# ---------------------------------------------------------------------------


def test_empty_relevant_fields_no_findings(
    repo: CuratedEvidenceRepositoryBackend,
    service: BasicOperationalDiagnosticService,
) -> None:
    _insert(repo, "ev-001", {"descripcion": "producto sin datos numericos"})

    report = service.build_report("tenant-1")

    assert report["findings"] == []
    assert report["evidence_count"] == 1


# ---------------------------------------------------------------------------
# Estructura del reporte
# ---------------------------------------------------------------------------


def test_report_structure(
    repo: CuratedEvidenceRepositoryBackend,
    service: BasicOperationalDiagnosticService,
) -> None:
    _insert(repo, "ev-001", {"precio_venta": 1.0, "costo_unitario": 10.0})

    report = service.build_report("tenant-1")

    assert set(report.keys()) == {"tenant_id", "findings", "evidence_count"}
    assert report["tenant_id"] == "tenant-1"
    assert isinstance(report["findings"], list)
    assert isinstance(report["evidence_count"], int)


def test_finding_structure(
    repo: CuratedEvidenceRepositoryBackend,
    service: BasicOperationalDiagnosticService,
) -> None:
    _insert(repo, "ev-001", {"precio_venta": 1.0, "costo_unitario": 10.0})

    report = service.build_report("tenant-1")
    finding = report["findings"][0]

    assert set(finding.keys()) == {"finding_type", "severity", "message", "evidence_id"}


# ---------------------------------------------------------------------------
# Fail-closed: tenant_id vacío
# ---------------------------------------------------------------------------


def test_build_report_fails_on_empty_tenant_id(
    service: BasicOperationalDiagnosticService,
) -> None:
    with pytest.raises(ValueError, match="tenant_id"):
        service.build_report("")


def test_build_report_fails_on_blank_tenant_id(
    service: BasicOperationalDiagnosticService,
) -> None:
    with pytest.raises(ValueError, match="tenant_id"):
        service.build_report("   ")


# ---------------------------------------------------------------------------
# RENTABILIDAD_NULA
# ---------------------------------------------------------------------------


def test_rentabilidad_nula_detected(
    repo: CuratedEvidenceRepositoryBackend,
    service: BasicOperationalDiagnosticService,
) -> None:
    """Detecta producto donde precio_venta == costo_unitario (margen 0)."""
    _insert(repo, "ev-001", {"precio_venta": 100.0, "costo_unitario": 100.0})

    report = service.build_report("tenant-1")

    assert "RENTABILIDAD_NULA" in _finding_types(report)
    finding = next(f for f in report["findings"] if f["finding_type"] == "RENTABILIDAD_NULA")
    assert finding["severity"] == "HIGH"
    assert finding["evidence_id"] == "ev-001"
    assert "100.0" in finding["message"]
    assert "Margen absoluto: 0" in finding["message"]


def test_rentabilidad_nula_not_triggered_when_venta_mayor(
    repo: CuratedEvidenceRepositoryBackend,
    service: BasicOperationalDiagnosticService,
) -> None:
    """No dispara cuando precio_venta > costo_unitario."""
    _insert(repo, "ev-001", {"precio_venta": 120.0, "costo_unitario": 100.0})

    report = service.build_report("tenant-1")

    assert "RENTABILIDAD_NULA" not in _finding_types(report)


def test_rentabilidad_nula_not_triggered_with_incomplete_data(
    repo: CuratedEvidenceRepositoryBackend,
    service: BasicOperationalDiagnosticService,
) -> None:
    """No rompe con datos incompletos (falta costo_unitario)."""
    _insert(repo, "ev-001", {"precio_venta": 100.0})

    report = service.build_report("tenant-1")

    assert "RENTABILIDAD_NULA" not in _finding_types(report)


def test_rentabilidad_nula_coexists_with_other_rules(
    repo: CuratedEvidenceRepositoryBackend,
    service: BasicOperationalDiagnosticService,
) -> None:
    """RENTABILIDAD_NULA convive con otras reglas sin interferencia."""
    # Registro con rentabilidad nula
    _insert(repo, "ev-001", {"precio_venta": 50.0, "costo_unitario": 50.0})
    # Registro con stock negativo (regla distinta)
    _insert(repo, "ev-002", {"stock_actual": -3})

    report = service.build_report("tenant-1")
    types = _finding_types(report)

    assert "RENTABILIDAD_NULA" in types
    assert "STOCK_NEGATIVO" in types
    assert report["evidence_count"] == 2


# ---------------------------------------------------------------------------
# STOCK_INMOVILIZADO
# ---------------------------------------------------------------------------


def test_stock_inmovilizado_detected(
    repo: CuratedEvidenceRepositoryBackend,
    service: BasicOperationalDiagnosticService,
) -> None:
    """Dispara con stock positivo y ventas_periodo == 0."""
    _insert(repo, "ev-001", {"stock_actual": 50.0, "ventas_periodo": 0})

    report = service.build_report("tenant-1")

    assert "STOCK_INMOVILIZADO" in _finding_types(report)
    finding = next(f for f in report["findings"] if f["finding_type"] == "STOCK_INMOVILIZADO")
    assert finding["severity"] == "MEDIUM"
    assert finding["evidence_id"] == "ev-001"
    assert "50.0" in finding["message"]
    assert "ventas_periodo" in finding["message"]


def test_stock_inmovilizado_not_triggered_when_hay_ventas(
    repo: CuratedEvidenceRepositoryBackend,
    service: BasicOperationalDiagnosticService,
) -> None:
    """No dispara si hubo ventas en el período."""
    _insert(repo, "ev-001", {"stock_actual": 50.0, "ventas_periodo": 10.0})

    report = service.build_report("tenant-1")

    assert "STOCK_INMOVILIZADO" not in _finding_types(report)


def test_stock_inmovilizado_not_triggered_when_stock_cero(
    repo: CuratedEvidenceRepositoryBackend,
    service: BasicOperationalDiagnosticService,
) -> None:
    """No dispara si stock_actual == 0 (no hay capital inmovilizado)."""
    _insert(repo, "ev-001", {"stock_actual": 0, "ventas_periodo": 0})

    report = service.build_report("tenant-1")

    assert "STOCK_INMOVILIZADO" not in _finding_types(report)


def test_stock_inmovilizado_fail_closed_with_incomplete_data(
    repo: CuratedEvidenceRepositoryBackend,
    service: BasicOperationalDiagnosticService,
) -> None:
    """Fail-closed: no dispara si falta alguno de los dos campos."""
    # Solo stock_actual, sin ventas_periodo
    _insert(repo, "ev-001", {"stock_actual": 100.0})
    # Solo ventas_periodo, sin stock_actual
    _insert(repo, "ev-002", {"ventas_periodo": 0})

    report = service.build_report("tenant-1")

    assert "STOCK_INMOVILIZADO" not in _finding_types(report)


# ---------------------------------------------------------------------------
# PRECIO_DESACTUALIZADO
# ---------------------------------------------------------------------------


def test_precio_desactualizado_detected(
    repo: CuratedEvidenceRepositoryBackend,
    service: BasicOperationalDiagnosticService,
) -> None:
    """Dispara cuando costo_actual > precio_venta."""
    _insert(repo, "ev-001", {"precio_venta": 80.0, "costo_actual": 100.0})

    report = service.build_report("tenant-1")

    assert "PRECIO_DESACTUALIZADO" in _finding_types(report)
    finding = next(f for f in report["findings"] if f["finding_type"] == "PRECIO_DESACTUALIZADO")
    assert finding["severity"] == "HIGH"
    assert finding["evidence_id"] == "ev-001"
    assert "100.0" in finding["message"]
    assert "80.0" in finding["message"]
    assert "20.00" in finding["message"]


def test_precio_desactualizado_not_triggered_when_precio_mayor(
    repo: CuratedEvidenceRepositoryBackend,
    service: BasicOperationalDiagnosticService,
) -> None:
    """No dispara cuando precio_venta > costo_actual."""
    _insert(repo, "ev-001", {"precio_venta": 120.0, "costo_actual": 100.0})

    report = service.build_report("tenant-1")

    assert "PRECIO_DESACTUALIZADO" not in _finding_types(report)


def test_precio_desactualizado_not_triggered_when_iguales(
    repo: CuratedEvidenceRepositoryBackend,
    service: BasicOperationalDiagnosticService,
) -> None:
    """No dispara cuando precio_venta == costo_actual."""
    _insert(repo, "ev-001", {"precio_venta": 100.0, "costo_actual": 100.0})

    report = service.build_report("tenant-1")

    assert "PRECIO_DESACTUALIZADO" not in _finding_types(report)


def test_precio_desactualizado_fail_closed_with_incomplete_data(
    repo: CuratedEvidenceRepositoryBackend,
    service: BasicOperationalDiagnosticService,
) -> None:
    """Fail-closed: no dispara si falta alguno de los dos campos."""
    # Solo precio_venta, sin costo_actual
    _insert(repo, "ev-001", {"precio_venta": 80.0})
    # Solo costo_actual, sin precio_venta
    _insert(repo, "ev-002", {"costo_actual": 100.0})

    report = service.build_report("tenant-1")

    assert "PRECIO_DESACTUALIZADO" not in _finding_types(report)


# ---------------------------------------------------------------------------
# INVENTARIO_FANTASMA
# ---------------------------------------------------------------------------


def test_inventario_fantasma_detected(
    repo: CuratedEvidenceRepositoryBackend,
    service: BasicOperationalDiagnosticService,
) -> None:
    """Dispara con stock positivo y cero compras/ventas en el período."""
    _insert(repo, "ev-001", {"stock_actual": 30.0, "compras_periodo": 0, "ventas_periodo": 0})

    report = service.build_report("tenant-1")

    assert "INVENTARIO_FANTASMA" in _finding_types(report)
    finding = next(f for f in report["findings"] if f["finding_type"] == "INVENTARIO_FANTASMA")
    assert finding["severity"] == "MEDIUM"
    assert finding["evidence_id"] == "ev-001"
    assert "30.0" in finding["message"]
    assert "compras_periodo" in finding["message"]
    assert "ventas_periodo" in finding["message"]


def test_inventario_fantasma_not_triggered_when_hay_ventas(
    repo: CuratedEvidenceRepositoryBackend,
    service: BasicOperationalDiagnosticService,
) -> None:
    """No dispara si hubo ventas en el período."""
    _insert(repo, "ev-001", {"stock_actual": 30.0, "compras_periodo": 0, "ventas_periodo": 5.0})

    report = service.build_report("tenant-1")

    assert "INVENTARIO_FANTASMA" not in _finding_types(report)


def test_inventario_fantasma_not_triggered_when_hay_compras(
    repo: CuratedEvidenceRepositoryBackend,
    service: BasicOperationalDiagnosticService,
) -> None:
    """No dispara si hubo compras en el período."""
    _insert(repo, "ev-001", {"stock_actual": 30.0, "compras_periodo": 10.0, "ventas_periodo": 0})

    report = service.build_report("tenant-1")

    assert "INVENTARIO_FANTASMA" not in _finding_types(report)


def test_inventario_fantasma_not_triggered_when_stock_cero(
    repo: CuratedEvidenceRepositoryBackend,
    service: BasicOperationalDiagnosticService,
) -> None:
    """No dispara si stock_actual == 0."""
    _insert(repo, "ev-001", {"stock_actual": 0, "compras_periodo": 0, "ventas_periodo": 0})

    report = service.build_report("tenant-1")

    assert "INVENTARIO_FANTASMA" not in _finding_types(report)


def test_inventario_fantasma_fail_closed_with_incomplete_data(
    repo: CuratedEvidenceRepositoryBackend,
    service: BasicOperationalDiagnosticService,
) -> None:
    """Fail-closed: no dispara si falta alguno de los tres campos."""
    # Falta compras_periodo
    _insert(repo, "ev-001", {"stock_actual": 30.0, "ventas_periodo": 0})
    # Falta ventas_periodo
    _insert(repo, "ev-002", {"stock_actual": 30.0, "compras_periodo": 0})
    # Falta stock_actual
    _insert(repo, "ev-003", {"compras_periodo": 0, "ventas_periodo": 0})

    report = service.build_report("tenant-1")

    assert "INVENTARIO_FANTASMA" not in _finding_types(report)


# ---------------------------------------------------------------------------
# DUPLICADO_OPERACIONAL
# ---------------------------------------------------------------------------


def test_duplicado_operacional_detected(
    repo: CuratedEvidenceRepositoryBackend,
    service: BasicOperationalDiagnosticService,
) -> None:
    """Detecta duplicado exacto: misma referencia, monto y fecha."""
    _insert(repo, "ev-001", {"referencia": "FAC-001", "monto": 500.0, "fecha": "2024-01-15"})
    _insert(repo, "ev-002", {"referencia": "FAC-001", "monto": 500.0, "fecha": "2024-01-15"})

    report = service.build_report("tenant-1")

    assert "DUPLICADO_OPERACIONAL" in _finding_types(report)
    finding = next(f for f in report["findings"] if f["finding_type"] == "DUPLICADO_OPERACIONAL")
    assert finding["severity"] == "HIGH"
    assert finding["referencia"] == "FAC-001"
    assert finding["cantidad_detectada"] == "2"


def test_duplicado_operacional_not_triggered_with_distinct_referencia(
    repo: CuratedEvidenceRepositoryBackend,
    service: BasicOperationalDiagnosticService,
) -> None:
    """No dispara si las referencias son distintas."""
    _insert(repo, "ev-001", {"referencia": "FAC-001", "monto": 500.0, "fecha": "2024-01-15"})
    _insert(repo, "ev-002", {"referencia": "FAC-002", "monto": 500.0, "fecha": "2024-01-15"})

    report = service.build_report("tenant-1")

    assert "DUPLICADO_OPERACIONAL" not in _finding_types(report)


def test_duplicado_operacional_not_triggered_with_distinct_fecha(
    repo: CuratedEvidenceRepositoryBackend,
    service: BasicOperationalDiagnosticService,
) -> None:
    """No dispara si las fechas son distintas."""
    _insert(repo, "ev-001", {"referencia": "FAC-001", "monto": 500.0, "fecha": "2024-01-15"})
    _insert(repo, "ev-002", {"referencia": "FAC-001", "monto": 500.0, "fecha": "2024-01-16"})

    report = service.build_report("tenant-1")

    assert "DUPLICADO_OPERACIONAL" not in _finding_types(report)


def test_duplicado_operacional_not_triggered_with_distinct_monto(
    repo: CuratedEvidenceRepositoryBackend,
    service: BasicOperationalDiagnosticService,
) -> None:
    """No dispara si los montos son distintos."""
    _insert(repo, "ev-001", {"referencia": "FAC-001", "monto": 500.0, "fecha": "2024-01-15"})
    _insert(repo, "ev-002", {"referencia": "FAC-001", "monto": 600.0, "fecha": "2024-01-15"})

    report = service.build_report("tenant-1")

    assert "DUPLICADO_OPERACIONAL" not in _finding_types(report)


def test_duplicado_operacional_fail_closed_with_incomplete_data(
    repo: CuratedEvidenceRepositoryBackend,
    service: BasicOperationalDiagnosticService,
) -> None:
    """Fail-closed: registros con campos faltantes son ignorados."""
    # Sin fecha
    _insert(repo, "ev-001", {"referencia": "FAC-001", "monto": 500.0})
    # Sin monto
    _insert(repo, "ev-002", {"referencia": "FAC-001", "fecha": "2024-01-15"})
    # Sin referencia
    _insert(repo, "ev-003", {"monto": 500.0, "fecha": "2024-01-15"})

    report = service.build_report("tenant-1")

    assert "DUPLICADO_OPERACIONAL" not in _finding_types(report)
