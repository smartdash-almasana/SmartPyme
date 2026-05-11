"""
Tests: BemSubmitService → CuratedEvidenceRepositoryBackend (integración post-run).

Valida:
- COMPLETED persiste run Y curated evidence cuando el repo está inyectado.
- Sin repo inyectado, comportamiento actual queda igual (sin curated evidence).
- Adapter failure produce error controlado (no silencioso).
- tenant_id preservado en curated evidence.
- response_payload queda persistido en el run.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from app.repositories.bem_run_repository import BemRunRepository
from app.repositories.curated_evidence_repository import CuratedEvidenceRepositoryBackend
from app.services.bem_submit_service import BemSubmitService


# ---------------------------------------------------------------------------
# Fake BEM client que devuelve un response_payload con estructura real de BEM
# ---------------------------------------------------------------------------


class _FakeBemClientBemResponse:
    """Devuelve un response_payload con estructura outputs[0].transformedContent."""

    def __init__(self, call_reference_id: str = "ref-001") -> None:
        self._call_reference_id = call_reference_id

    def submit_payload(self, workflow_id: str, payload: dict) -> dict:
        return {
            "callReferenceID": self._call_reference_id,
            "callID": "call-abc",
            "avgConfidence": 0.92,
            "inputType": "excel",
            "workflow_id": workflow_id,
            "outputs": [
                {
                    "transformedContent": {
                        "precio_venta": 10.0,
                        "costo_unitario": 80.0,
                        "cantidad": 3,
                        "producto": "Widget",
                        "source_name": "ventas.xlsx",
                        "source_type": "excel",
                    }
                }
            ],
        }


class _FakeBemClientFlatResponse:
    """Devuelve un response_payload plano (sin outputs) — simula BEM legacy."""

    def submit_payload(self, workflow_id: str, payload: dict) -> dict:
        return {"provider_run_id": "bem-1", "accepted": True}


class _FakeBemClientFail:
    def submit_payload(self, workflow_id: str, payload: dict) -> dict:
        raise RuntimeError("bem unavailable")


def _now_factory():
    values = [
        datetime(2026, 5, 10, 12, 0, 0, tzinfo=timezone.utc),
        datetime(2026, 5, 10, 12, 1, 0, tzinfo=timezone.utc),
        datetime(2026, 5, 10, 12, 2, 0, tzinfo=timezone.utc),
        datetime(2026, 5, 10, 12, 3, 0, tzinfo=timezone.utc),
    ]

    def _p() -> datetime:
        return values.pop(0) if values else datetime(2026, 5, 10, 12, 3, 0, tzinfo=timezone.utc)

    return _p


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_completed_persiste_run_y_curated_evidence(tmp_path: Path) -> None:
    """Cuando el repo está inyectado, COMPLETED persiste run Y curated evidence."""
    run_repo = BemRunRepository(tmp_path / "runs.db")
    curated_repo = CuratedEvidenceRepositoryBackend(tmp_path / "curated.db")

    service = BemSubmitService(
        bem_client=_FakeBemClientBemResponse(),
        bem_run_repository=run_repo,
        curated_evidence_repository=curated_repo,
        now_provider=_now_factory(),
        run_id_provider=lambda: "run-001",
    )

    run = service.submit("tenant-a", "wf-1", {"x": 1})

    # Run queda COMPLETED
    assert run.status == "COMPLETED"
    assert run.run_id == "run-001"

    # Curated evidence fue persistida
    records = curated_repo.list_by_tenant("tenant-a")
    assert len(records) == 1
    record = records[0]
    assert record.tenant_id == "tenant-a"
    assert record.evidence_id == "ref-001"
    assert record.payload["precio_venta"] == 10.0
    assert record.payload["costo_unitario"] == 80.0


def test_sin_curated_repo_comportamiento_actual_igual(tmp_path: Path) -> None:
    """Sin repo inyectado, submit funciona igual que antes — sin curated evidence."""
    run_repo = BemRunRepository(tmp_path / "runs.db")

    service = BemSubmitService(
        bem_client=_FakeBemClientBemResponse(),
        bem_run_repository=run_repo,
        # curated_evidence_repository NO inyectado
        now_provider=_now_factory(),
        run_id_provider=lambda: "run-002",
    )

    run = service.submit("tenant-a", "wf-1", {"x": 1})

    assert run.status == "COMPLETED"
    assert run.run_id == "run-002"
    # No hay curated repo — no hay error, no hay side effect


def test_adapter_failure_produce_error_controlado(tmp_path: Path) -> None:
    """Si el adapter falla (response_payload sin outputs), el error se propaga — no silencioso."""
    run_repo = BemRunRepository(tmp_path / "runs.db")
    curated_repo = CuratedEvidenceRepositoryBackend(tmp_path / "curated.db")

    service = BemSubmitService(
        bem_client=_FakeBemClientFlatResponse(),  # devuelve payload sin outputs
        bem_run_repository=run_repo,
        curated_evidence_repository=curated_repo,
        now_provider=_now_factory(),
        run_id_provider=lambda: "run-003",
    )

    with pytest.raises(ValueError, match="outputs"):
        service.submit("tenant-a", "wf-1", {"x": 1})

    # El run quedó COMPLETED en el repositorio (BEM respondió OK)
    run = run_repo.get_by_run_id("tenant-a", "run-003")
    assert run is not None
    assert run.status == "COMPLETED"

    # Pero curated evidence NO fue persistida (el adapter falló antes del create)
    records = curated_repo.list_by_tenant("tenant-a")
    assert len(records) == 0


def test_tenant_id_preservado_en_curated_evidence(tmp_path: Path) -> None:
    """tenant_id del submit queda en el CuratedEvidenceRecord."""
    run_repo = BemRunRepository(tmp_path / "runs.db")
    curated_repo = CuratedEvidenceRepositoryBackend(tmp_path / "curated.db")

    service = BemSubmitService(
        bem_client=_FakeBemClientBemResponse(call_reference_id="ref-tenant-test"),
        bem_run_repository=run_repo,
        curated_evidence_repository=curated_repo,
        now_provider=_now_factory(),
        run_id_provider=lambda: "run-004",
    )

    service.submit("tenant-xyz", "wf-1", {"x": 1})

    records = curated_repo.list_by_tenant("tenant-xyz")
    assert len(records) == 1
    assert records[0].tenant_id == "tenant-xyz"

    # Tenant isolation: otro tenant no ve el registro
    assert curated_repo.list_by_tenant("tenant-other") == []


def test_response_payload_persistido_en_run(tmp_path: Path) -> None:
    """response_payload de BEM queda persistido en el BemRunRecord."""
    run_repo = BemRunRepository(tmp_path / "runs.db")
    curated_repo = CuratedEvidenceRepositoryBackend(tmp_path / "curated.db")

    service = BemSubmitService(
        bem_client=_FakeBemClientBemResponse(call_reference_id="ref-rp"),
        bem_run_repository=run_repo,
        curated_evidence_repository=curated_repo,
        now_provider=_now_factory(),
        run_id_provider=lambda: "run-005",
    )

    run = service.submit("tenant-a", "wf-1", {"x": 1})

    assert run.response_payload is not None
    assert run.response_payload["callReferenceID"] == "ref-rp"
    assert "outputs" in run.response_payload


def test_evidence_id_fallback_a_run_id_cuando_no_hay_callReferenceID(tmp_path: Path) -> None:
    """Si BEM no devuelve callReferenceID ni callID, evidence_id usa bem-run-{run_id}."""

    class _FakeBemClientNoRef:
        def submit_payload(self, workflow_id: str, payload: dict) -> dict:
            return {
                # sin callReferenceID ni callID
                "outputs": [
                    {
                        "transformedContent": {
                            "precio_venta": 5.0,
                            "source_name": "doc.xlsx",
                            "source_type": "excel",
                        }
                    }
                ],
            }

    run_repo = BemRunRepository(tmp_path / "runs.db")
    curated_repo = CuratedEvidenceRepositoryBackend(tmp_path / "curated.db")

    service = BemSubmitService(
        bem_client=_FakeBemClientNoRef(),
        bem_run_repository=run_repo,
        curated_evidence_repository=curated_repo,
        now_provider=_now_factory(),
        run_id_provider=lambda: "run-fallback",
    )

    service.submit("tenant-a", "wf-1", {"x": 1})

    records = curated_repo.list_by_tenant("tenant-a")
    assert len(records) == 1
    assert records[0].evidence_id == "bem-run-run-fallback"


def test_bem_client_failure_no_persiste_curated_evidence(tmp_path: Path) -> None:
    """Si BEM falla, el run queda FAILED y no se intenta persistir curated evidence."""
    run_repo = BemRunRepository(tmp_path / "runs.db")
    curated_repo = CuratedEvidenceRepositoryBackend(tmp_path / "curated.db")

    service = BemSubmitService(
        bem_client=_FakeBemClientFail(),
        bem_run_repository=run_repo,
        curated_evidence_repository=curated_repo,
        now_provider=_now_factory(),
        run_id_provider=lambda: "run-fail",
    )

    with pytest.raises(RuntimeError, match="bem unavailable"):
        service.submit("tenant-a", "wf-1", {"x": 1})

    run = run_repo.get_by_run_id("tenant-a", "run-fail")
    assert run is not None
    assert run.status == "FAILED"

    assert curated_repo.list_by_tenant("tenant-a") == []
