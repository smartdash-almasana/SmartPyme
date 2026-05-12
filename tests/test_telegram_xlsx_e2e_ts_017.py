"""
E2E mínimo: Telegram + XLSX → BEM mock → CuratedEvidence → Diagnóstico → Respuesta.

Flujo cubierto:
  TelegramAdapter.handle_update(update_xlsx)
  → _handle_document
  → DocumentIntakeService.register_telegram_document_candidate  (real, SQLite tmp)
  → _submit_xlsx_to_bem
      → telegram_get_file          (mock)
      → telegram_download_file     (mock)
      → bem_xlsx_submitter         (mock — retorna BEM response con VENTA_BAJO_COSTO)
      → BemCuratedEvidenceAdapter  (real)
      → CuratedEvidenceRepositoryBackend.create  (real, SQLite tmp)
      → BasicOperationalDiagnosticService.build_report  (real)
      → telegram_send_message      (mock — captura mensajes)
  → respuesta dict con bem.findings_count >= 1

Sin Supabase. Sin SmartGraph. Sin Telegram real. Sin BEM real.
Fail-closed. Determinístico.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from app.adapters.telegram_adapter import TelegramAdapter
from app.repositories.curated_evidence_repository import CuratedEvidenceRepositoryBackend
from app.services.basic_operational_diagnostic_service import BasicOperationalDiagnosticService
from app.services.document_intake_service import DocumentIntakeService
from app.services.identity_service import IdentityService


# ---------------------------------------------------------------------------
# Constantes del escenario
# ---------------------------------------------------------------------------

_CLIENTE_ID = "pyme-e2e-ts017"
_TELEGRAM_USER_ID = 42
_FILE_ID = "file-xlsx-e2e-001"
_FILE_NAME = "ventas.xlsx"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _linked_identity(tmp_path: Path) -> IdentityService:
    identity = IdentityService(tmp_path / "identity.db")
    identity.create_onboarding_token("token-e2e-017", _CLIENTE_ID)
    result = identity.link_telegram_user(_TELEGRAM_USER_ID, "token-e2e-017")
    assert result["status"] == "linked", f"setup falló: {result}"
    return identity


def _xlsx_update() -> dict[str, Any]:
    """Payload mínimo de update Telegram con documento XLSX."""
    return {
        "message": {
            "from": {"id": _TELEGRAM_USER_ID},
            "document": {
                "file_id": _FILE_ID,
                "file_name": _FILE_NAME,
                "mime_type": (
                    "application/vnd.openxmlformats-officedocument"
                    ".spreadsheetml.sheet"
                ),
            },
        }
    }


def _bem_response_venta_bajo_costo() -> dict[str, Any]:
    """
    BEM response mínimo con estructura real outputs[0].transformedContent.
    precio_venta (10) < costo_unitario (80) → garantiza VENTA_BAJO_COSTO.
    """
    return {
        "callReferenceID": f"telegram-xlsx:{_CLIENTE_ID}:{_FILE_ID}",
        "callID": "call-e2e-ts017",
        "avgConfidence": 0.95,
        "inputType": "excel",
        "outputs": [
            {
                "transformedContent": {
                    "precio_venta": 10.0,
                    "costo_unitario": 80.0,
                    "cantidad": 5,
                    "producto": "Producto Test E2E",
                    "source_name": _FILE_NAME,
                    "source_type": "excel",
                }
            }
        ],
    }


def _fake_enqueuer(task_id: str, objective: str, **_kwargs: Any) -> dict[str, Any]:
    return {"task_id": task_id, "status": "queued", "objective": objective}


# ---------------------------------------------------------------------------
# Fixture principal
# ---------------------------------------------------------------------------


@pytest.fixture()
def repo(tmp_path: Path) -> CuratedEvidenceRepositoryBackend:
    return CuratedEvidenceRepositoryBackend(db_path=tmp_path / "curated_e2e.db")


# ---------------------------------------------------------------------------
# Test E2E principal
# ---------------------------------------------------------------------------


def test_telegram_xlsx_webhook_produces_diagnostic_findings(
    tmp_path: Path,
    repo: CuratedEvidenceRepositoryBackend,
) -> None:
    """
    Flujo completo Telegram XLSX → hallazgo VENTA_BAJO_COSTO en respuesta y en repo.

    Verifica:
    1. result["status"] existe y es "queued"
    2. result["cliente_id"] == _CLIENTE_ID
    3. result["bem"]["status"] == "ok"
    4. result["bem"]["findings_count"] >= 1
    5. repo persistió exactamente 1 registro de evidencia curada
    6. payload del registro contiene precio_venta y costo_unitario correctos
    7. diagnóstico sobre el repo contiene VENTA_BAJO_COSTO
    8. mensaje enviado al usuario contiene "VENTA_BAJO_COSTO"
    """
    identity = _linked_identity(tmp_path)
    sent_messages: list[tuple[Any, str]] = []

    adapter = TelegramAdapter(
        identity_service=identity,
        document_intake_service=DocumentIntakeService(tmp_path / "evidence_candidates.db"),
        factory_task_enqueuer=_fake_enqueuer,
        # --- mocks de red Telegram ---
        telegram_get_file=lambda file_id: {"file_path": "documents/fake_e2e.xlsx"},
        telegram_download_file=lambda file_path: b"PK\x03\x04fake-xlsx-content",
        telegram_send_message=lambda chat_id, text: sent_messages.append((chat_id, text)),
        # --- mock BEM: retorna response determinístico con venta bajo costo ---
        bem_xlsx_submitter=lambda tenant_id, file_name, file_bytes, file_id: (
            _bem_response_venta_bajo_costo()
        ),
        # --- repositorio real SQLite en tmp ---
        curated_evidence_repository=repo,
        # --- servicio de diagnóstico real sobre el mismo repo ---
        diagnostic_service=BasicOperationalDiagnosticService(repository=repo),
    )

    result = adapter.handle_update(_xlsx_update())

    # 1. status existe
    assert "status" in result, f"falta 'status' en result: {result}"

    # 2. status es "queued" (documento procesado)
    assert result["status"] == "queued", f"status inesperado: {result['status']}"

    # 3. cliente_id correcto
    assert result["cliente_id"] == _CLIENTE_ID, (
        f"cliente_id incorrecto: {result.get('cliente_id')}"
    )

    # 4. BEM status ok
    bem = result.get("bem", {})
    assert bem.get("status") == "ok", f"bem.status inesperado: {bem}"

    # 5. findings_count >= 1
    assert bem.get("findings_count", 0) >= 1, (
        f"findings_count esperado >= 1, obtenido: {bem.get('findings_count')}"
    )

    # 6. repo persistió exactamente 1 registro
    records = repo.list_by_tenant(_CLIENTE_ID)
    assert len(records) == 1, f"esperado 1 registro en repo, encontrado: {len(records)}"

    # 7. payload del registro tiene los valores correctos
    payload = records[0].payload
    assert payload.get("precio_venta") == 10.0, f"precio_venta incorrecto: {payload}"
    assert payload.get("costo_unitario") == 80.0, f"costo_unitario incorrecto: {payload}"

    # 8. diagnóstico sobre el repo contiene VENTA_BAJO_COSTO
    service = BasicOperationalDiagnosticService(repository=repo)
    report = service.build_report(_CLIENTE_ID)
    finding_types = {f["finding_type"] for f in report["findings"]}
    assert "VENTA_BAJO_COSTO" in finding_types, (
        f"VENTA_BAJO_COSTO no encontrado en hallazgos: {finding_types}"
    )

    # 9. mensaje enviado al usuario contiene VENTA_BAJO_COSTO
    assert len(sent_messages) >= 1, "no se envió ningún mensaje al usuario"
    combined_text = " ".join(text for _, text in sent_messages)
    assert "VENTA_BAJO_COSTO" in combined_text, (
        f"VENTA_BAJO_COSTO no encontrado en mensajes enviados: {combined_text!r}"
    )


# ---------------------------------------------------------------------------
# Test de aislamiento: usuario no vinculado no genera evidencia
# ---------------------------------------------------------------------------


def test_unlinked_user_xlsx_does_not_persist_evidence(
    tmp_path: Path,
    repo: CuratedEvidenceRepositoryBackend,
) -> None:
    """
    Usuario no vinculado → respuesta unauthorized → repo vacío.
    Garantiza que el flujo BEM no se activa sin autenticación.
    """
    identity = IdentityService(tmp_path / "identity_unlinked.db")
    # No se vincula ningún usuario

    adapter = TelegramAdapter(
        identity_service=identity,
        document_intake_service=DocumentIntakeService(tmp_path / "evidence_unlinked.db"),
        factory_task_enqueuer=_fake_enqueuer,
        curated_evidence_repository=repo,
        diagnostic_service=BasicOperationalDiagnosticService(repository=repo),
    )

    result = adapter.handle_update(_xlsx_update())

    assert result["status"] == "unauthorized"
    assert repo.list_by_tenant(_CLIENTE_ID) == []
