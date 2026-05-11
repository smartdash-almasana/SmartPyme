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
    assert "STOCK_NEGATIVO" in types
    assert "MOVIMIENTO_INCONSISTENTE" in types
    assert len(types) == 3


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
