
"""
E2E HTTP: POST /webhook/telegram + XLSX → BEM mock → CuratedEvidence → 200 OK.

Flujo cubierto:
  FastAPI TestClient.post("/webhook/telegram")
  → dependency_overrides(get_telegram_adapter)
  → TelegramAdapter.handle_update(update_xlsx)
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
  → respuesta HTTP 200 con bem.findings_count >= 1

Sin Supabase. Sin SmartGraph. Sin Telegram real. Sin BEM real.
Fail-closed. Determinístico.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.adapters.telegram_adapter import TelegramAdapter
from app.api.telegram_webhook_router import get_telegram_adapter
from app.main import app
from app.repositories.curated_evidence_repository import CuratedEvidenceRepositoryBackend
from app.services.basic_operational_diagnostic_service import BasicOperationalDiagnosticService
from app.services.document_intake_service import DocumentIntakeService
from app.services.identity_service import IdentityService

# --------------------------------------------------------------------------
# Constantes del escenario
# --------------------------------------------------------------------------

_CLIENTE_ID = "pyme-e2e-ts018"
_TELEGRAM_USER_ID = 43
_FILE_ID = "file-xlsx-e2e-002"
_FILE_NAME = "ventas_router.xlsx"


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------


def _linked_identity(tmp_path: Path) -> IdentityService:
    identity = IdentityService(tmp_path / "identity_ts018.db")
    identity.create_onboarding_token("token-e2e-018", _CLIENTE_ID)
    result = identity.link_telegram_user(_TELEGRAM_USER_ID, "token-e2e-018")
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
        "callID": "call-e2e-ts018",
        "avgConfidence": 0.95,
        "inputType": "excel",
        "outputs": [
            {
                "transformedContent": {
                    "precio_venta": 10.0,
                    "costo_unitario": 80.0,
                    "cantidad": 5,
                    "producto": "Producto Test E2E Router",
                    "source_name": _FILE_NAME,
                    "source_type": "excel",
                }
            }
        ],
    }


def _fake_enqueuer(task_id: str, objective: str, **_kwargs: Any) -> dict[str, Any]:
    return {"task_id": task_id, "status": "queued", "objective": objective}


# --------------------------------------------------------------------------
# Fixture principal
# --------------------------------------------------------------------------


@pytest.fixture
def repo(tmp_path: Path) -> CuratedEvidenceRepositoryBackend:
    return CuratedEvidenceRepositoryBackend(db_path=tmp_path / "curated_e2e_ts018.db")


# --------------------------------------------------------------------------
# Test E2E principal
# --------------------------------------------------------------------------


def test_telegram_xlsx_router_produces_diagnostic_findings(
    tmp_path: Path,
    repo: CuratedEvidenceRepositoryBackend,
) -> None:
    """
    Flujo E2E HTTP: POST /webhook/telegram con XLSX → hallazgo VENTA_BAJO_COSTO.

    Verifica:
    1. Respuesta HTTP 200 OK.
    2. JSON de respuesta contiene status=ok y un resultado anidado.
    3. Resultado anidado contiene bem.findings_count >= 1.
    4. El repositorio de evidencia curada (repo) persiste 1 registro.
    5. El payload del registro contiene los datos correctos del BEM.
    6. El servicio de diagnóstico sobre el repo encuentra VENTA_BAJO_COSTO.
    7. Se envió un mensaje de vuelta al usuario con el hallazgo.
    """
    identity = _linked_identity(tmp_path)
    sent_messages: list[tuple[Any, str]] = []

    def get_overridden_adapter() -> TelegramAdapter:
        return TelegramAdapter(
            identity_service=identity,
            document_intake_service=DocumentIntakeService(
                tmp_path / "evidence_candidates_ts018.db"
            ),
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

    app.dependency_overrides[get_telegram_adapter] = get_overridden_adapter

    client = TestClient(app)
    response = client.post("/webhook/telegram", json=_xlsx_update())

    # 1. Verificar respuesta HTTP
    assert response.status_code == 200, f"Código de estado inesperado: {response.text}"
    
    # 2. Verificar estructura de la respuesta
    data = response.json()
    assert data.get("status") == "ok", "El status principal no es 'ok'"
    result = data.get("result")
    assert result is not None, "Falta el objeto 'result' en la respuesta"

    # 3. Verificar hallazgos en la respuesta
    bem = result.get("bem", {})
    assert bem.get("status") == "ok", f"bem.status inesperado: {bem}"
    assert bem.get("findings_count", 0) >= 1, (
        f"findings_count esperado >= 1, obtenido: {bem.get('findings_count')}"
    )

    # 4. Verificar persistencia en el repositorio
    records = repo.list_by_tenant(_CLIENTE_ID)
    assert len(records) == 1, f"Esperado 1 registro en repo, encontrado: {len(records)}"

    # 5. Verificar contenido del payload persistido
    payload = records[0].payload
    assert payload.get("precio_venta") == 10.0, f"precio_venta incorrecto: {payload}"
    assert payload.get("costo_unitario") == 80.0, f"costo_unitario incorrecto: {payload}"

    # 6. Verificar diagnóstico sobre el repo
    service = BasicOperationalDiagnosticService(repository=repo)
    report = service.build_report(_CLIENTE_ID)
    finding_types = {f["finding_type"] for f in report["findings"]}
    assert "VENTA_BAJO_COSTO" in finding_types, (
        f"VENTA_BAJO_COSTO no encontrado en hallazgos: {finding_types}"
    )
    
    # 7. Verificar mensaje enviado
    assert len(sent_messages) >= 1, "No se envió ningún mensaje al usuario"
    combined_text = " ".join(text for _, text in sent_messages)
    assert "VENTA_BAJO_COSTO" in combined_text, (
        f"VENTA_BAJO_COSTO no encontrado en mensajes enviados: {combined_text!r}"
    )

    # Limpiar override
    app.dependency_overrides.clear()
