"""
Tests de integración: CuratedEvidenceRecord promovido desde BEM → diagnóstico operacional.

Valida el flujo completo sin llamadas reales a BEM:
  BemCuratedEvidenceAdapter.build_curated_evidence_from_bem_response(...)
  → CuratedEvidenceRepositoryBackend.create(...)
  → BasicOperationalDiagnosticService.build_report(...)
  → hallazgos accionables

Sin mocks. Sin side effects. Fail-closed. Determinístico.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from app.repositories.curated_evidence_repository import CuratedEvidenceRepositoryBackend
from app.services.basic_operational_diagnostic_service import BasicOperationalDiagnosticService
from app.services.bem_curated_evidence_adapter import BemCuratedEvidenceAdapter


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_FIXED_NOW = datetime(2026, 5, 10, 12, 0, 0, tzinfo=timezone.utc)


def _adapter() -> BemCuratedEvidenceAdapter:
    return BemCuratedEvidenceAdapter(now_provider=lambda: _FIXED_NOW)


def _bem_response(
    call_reference_id: str = "ref-bem-001",
    precio_venta: float = 10.0,
    costo_unitario: float = 80.0,
    cantidad: int = 5,
    producto: str = "Mouse Gamer RGB",
) -> dict:
    """Fixture de response_payload real de BEM con estructura outputs[0].transformedContent."""
    return {
        "callReferenceID": call_reference_id,
        "callID": "call-bem-abc",
        "avgConfidence": 0.91,
        "inputType": "excel",
        "outputs": [
            {
                "transformedContent": {
                    "precio_venta": precio_venta,
                    "costo_unitario": costo_unitario,
                    "cantidad": cantidad,
                    "producto": producto,
                    "source_name": "ventas_demo.xlsx",
                    "source_type": "excel",
                }
            }
        ],
    }


def _promote_and_diagnose(
    tenant_id: str,
    response_payload: dict,
    repo: CuratedEvidenceRepositoryBackend,
    run_id: str = "run-001",
) -> dict:
    """Flujo completo: BEM response → CuratedEvidenceRecord → diagnóstico."""
    record = _adapter().build_curated_evidence_from_bem_response(
        tenant_id=tenant_id,
        response_payload=response_payload,
        run_id=run_id,
    )
    repo.create(record)
    service = BasicOperationalDiagnosticService(repository=repo)
    return service.build_report(tenant_id)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def repo(tmp_path: Path) -> CuratedEvidenceRepositoryBackend:
    return CuratedEvidenceRepositoryBackend(db_path=tmp_path / "diag_bem.db")


# ---------------------------------------------------------------------------
# Tests: flujo BEM → diagnóstico
# ---------------------------------------------------------------------------


def test_bem_curated_evidence_alimenta_diagnostico(
    repo: CuratedEvidenceRepositoryBackend,
) -> None:
    """CuratedEvidenceRecord promovido desde BEM aparece en el diagnóstico."""
    report = _promote_and_diagnose(
        tenant_id="tenant-bem",
        response_payload=_bem_response(),
        repo=repo,
    )

    assert report["tenant_id"] == "tenant-bem"
    assert report["evidence_count"] == 1
    assert isinstance(report["findings"], list)


def test_venta_bajo_costo_desde_bem_produce_hallazgo(
    repo: CuratedEvidenceRepositoryBackend,
) -> None:
    """precio_venta < costo_unitario en payload BEM produce VENTA_BAJO_COSTO HIGH."""
    report = _promote_and_diagnose(
        tenant_id="tenant-bem",
        response_payload=_bem_response(precio_venta=10.0, costo_unitario=80.0),
        repo=repo,
    )

    types = [f["finding_type"] for f in report["findings"]]
    assert "VENTA_BAJO_COSTO" in types

    finding = next(f for f in report["findings"] if f["finding_type"] == "VENTA_BAJO_COSTO")
    assert finding["severity"] == "HIGH"
    assert "10.0" in finding["message"]
    assert "80.0" in finding["message"]


def test_venta_normal_desde_bem_no_produce_hallazgo(
    repo: CuratedEvidenceRepositoryBackend,
) -> None:
    """precio_venta > costo_unitario no produce hallazgo."""
    report = _promote_and_diagnose(
        tenant_id="tenant-bem",
        response_payload=_bem_response(precio_venta=150.0, costo_unitario=80.0),
        repo=repo,
    )

    types = [f["finding_type"] for f in report["findings"]]
    assert "VENTA_BAJO_COSTO" not in types


def test_evidence_id_desde_callReferenceID_en_hallazgo(
    repo: CuratedEvidenceRepositoryBackend,
) -> None:
    """evidence_id en el hallazgo coincide con callReferenceID del response_payload."""
    report = _promote_and_diagnose(
        tenant_id="tenant-bem",
        response_payload=_bem_response(call_reference_id="ref-especifico-001"),
        repo=repo,
    )

    finding = next(
        (f for f in report["findings"] if f["finding_type"] == "VENTA_BAJO_COSTO"), None
    )
    assert finding is not None
    assert finding["evidence_id"] == "ref-especifico-001"


def test_evidence_id_fallback_run_id_en_hallazgo(
    repo: CuratedEvidenceRepositoryBackend,
) -> None:
    """Si no hay callReferenceID ni callID, evidence_id usa bem-run-{run_id}."""
    response = _bem_response()
    del response["callReferenceID"]
    del response["callID"]

    report = _promote_and_diagnose(
        tenant_id="tenant-bem",
        response_payload=response,
        repo=repo,
        run_id="run-fallback-42",
    )

    finding = next(
        (f for f in report["findings"] if f["finding_type"] == "VENTA_BAJO_COSTO"), None
    )
    assert finding is not None
    assert finding["evidence_id"] == "bem-run-run-fallback-42"


def test_tenant_isolation_diagnostico_bem(
    repo: CuratedEvidenceRepositoryBackend,
) -> None:
    """Evidencia de tenant-a no aparece en diagnóstico de tenant-b."""
    _promote_and_diagnose(
        tenant_id="tenant-a",
        response_payload=_bem_response(
            call_reference_id="ref-a-001",
            precio_venta=10.0,
            costo_unitario=80.0,
        ),
        repo=repo,
        run_id="run-a",
    )

    service = BasicOperationalDiagnosticService(repository=repo)
    report_b = service.build_report("tenant-b")

    assert report_b["evidence_count"] == 0
    assert report_b["findings"] == []


def test_sin_evidencia_diagnostico_vacio(
    repo: CuratedEvidenceRepositoryBackend,
) -> None:
    """Sin evidencia curada, el diagnóstico retorna findings vacío — no inventa hallazgos."""
    service = BasicOperationalDiagnosticService(repository=repo)
    report = service.build_report("tenant-sin-datos")

    assert report["findings"] == []
    assert report["evidence_count"] == 0
    assert report["tenant_id"] == "tenant-sin-datos"


def test_evidencia_insuficiente_no_inventa_diagnostico(
    repo: CuratedEvidenceRepositoryBackend,
) -> None:
    """Payload con campos no relevantes no produce hallazgos falsos."""
    response = _bem_response()
    # Sobreescribir transformedContent con campos no relevantes para las reglas
    response["outputs"][0]["transformedContent"] = {
        "producto": "Widget",
        "descripcion": "sin datos numericos relevantes",
        "source_name": "doc.xlsx",
        "source_type": "excel",
    }

    report = _promote_and_diagnose(
        tenant_id="tenant-bem",
        response_payload=response,
        repo=repo,
    )

    assert report["findings"] == []
    assert report["evidence_count"] == 1


def test_multiples_evidencias_bem_acumulan_hallazgos(
    repo: CuratedEvidenceRepositoryBackend,
) -> None:
    """Múltiples CuratedEvidenceRecord desde BEM acumulan hallazgos correctamente."""
    # Primer record: venta bajo costo
    record1 = _adapter().build_curated_evidence_from_bem_response(
        tenant_id="tenant-multi",
        response_payload=_bem_response(
            call_reference_id="ref-multi-001",
            precio_venta=10.0,
            costo_unitario=80.0,
        ),
        run_id="run-1",
    )
    repo.create(record1)

    # Segundo record: venta normal (sin hallazgo)
    record2 = _adapter().build_curated_evidence_from_bem_response(
        tenant_id="tenant-multi",
        response_payload=_bem_response(
            call_reference_id="ref-multi-002",
            precio_venta=150.0,
            costo_unitario=80.0,
        ),
        run_id="run-2",
    )
    repo.create(record2)

    service = BasicOperationalDiagnosticService(repository=repo)
    report = service.build_report("tenant-multi")

    assert report["evidence_count"] == 2
    types = [f["finding_type"] for f in report["findings"]]
    assert types.count("VENTA_BAJO_COSTO") == 1
    # Solo el primer record produce hallazgo
    finding = next(f for f in report["findings"] if f["finding_type"] == "VENTA_BAJO_COSTO")
    assert finding["evidence_id"] == "ref-multi-001"
