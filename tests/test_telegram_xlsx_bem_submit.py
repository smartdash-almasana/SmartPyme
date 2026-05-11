from app.adapters.telegram_adapter import TelegramAdapter
from app.repositories.curated_evidence_repository import CuratedEvidenceRepositoryBackend
from app.services.basic_operational_diagnostic_service import BasicOperationalDiagnosticService
from app.services.identity_service import IdentityService


def _xlsx_update(user_id: int, file_id: str = "xlsx-file-1") -> dict:
    return {
        "message": {
            "from": {"id": user_id},
            "document": {
                "file_id": file_id,
                "file_name": "ventas.xlsx",
                "mime_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            },
        }
    }


def _linked_identity(tmp_path, cliente_id: str = "pyme_A"):
    identity = IdentityService(tmp_path / "identity.db")
    identity.create_onboarding_token("token-1", cliente_id)
    identity.link_telegram_user(42, "token-1")
    return identity


def test_xlsx_happy_path_end_to_end_builds_findings_and_sends_message(tmp_path):
    sent_messages = []
    repository = CuratedEvidenceRepositoryBackend(tmp_path / "curated.db")
    diagnostic = BasicOperationalDiagnosticService(repository=repository)

    adapter = TelegramAdapter(
        identity_service=_linked_identity(tmp_path),
        factory_task_enqueuer=lambda task_id, objective: {"status": "queued", "task_id": task_id},
        telegram_get_file=lambda file_id: {"file_path": f"docs/{file_id}.xlsx"},
        telegram_download_file=lambda file_path: b"xlsx-bytes",
        bem_xlsx_submitter=lambda tenant_id, file_name, file_bytes, file_id: {
            "call": {
                "callReferenceID": f"telegram-xlsx:{tenant_id}:{file_id}",
                "outputs": [
                    {
                        "transformedContent": {
                            "precio_venta": 80,
                            "costo_unitario": 100,
                            "source_name": "ventas.xlsx",
                            "source_type": "excel",
                        }
                    }
                ],
            }
        },
        curated_evidence_repository=repository,
        diagnostic_service=diagnostic,
        telegram_send_message=lambda chat_id, text: sent_messages.append(text),
    )

    result = adapter.handle_update(_xlsx_update(42, "xlsx-1"))

    assert result["status"] == "queued"
    assert result["bem"]["status"] == "ok"
    assert result["bem"]["findings_count"] >= 1
    assert "Hallazgos detectados:" in sent_messages[0]
    assert "VENTA_BAJO_COSTO (1)" in sent_messages[0]


def test_xlsx_no_findings_sends_no_findings_message(tmp_path):
    sent_messages = []
    repository = CuratedEvidenceRepositoryBackend(tmp_path / "curated.db")
    diagnostic = BasicOperationalDiagnosticService(repository=repository)

    adapter = TelegramAdapter(
        identity_service=_linked_identity(tmp_path),
        factory_task_enqueuer=lambda task_id, objective: {"status": "queued", "task_id": task_id},
        telegram_get_file=lambda file_id: {"file_path": f"docs/{file_id}.xlsx"},
        telegram_download_file=lambda file_path: b"xlsx-bytes",
        bem_xlsx_submitter=lambda tenant_id, file_name, file_bytes, file_id: {
            "call": {
                "callReferenceID": f"telegram-xlsx:{tenant_id}:{file_id}",
                "outputs": [
                    {
                        "transformedContent": {
                            "precio_venta": 120,
                            "costo_unitario": 100,
                            "source_name": "ventas.xlsx",
                            "source_type": "excel",
                        }
                    }
                ],
            }
        },
        curated_evidence_repository=repository,
        diagnostic_service=diagnostic,
        telegram_send_message=lambda chat_id, text: sent_messages.append(text),
    )

    result = adapter.handle_update(_xlsx_update(42, "xlsx-2"))

    assert result["status"] == "queued"
    assert result["bem"]["status"] == "ok"
    assert result["bem"]["findings_count"] == 0
    assert sent_messages[0] == "Archivo procesado. No se detectaron hallazgos operacionales."


def test_xlsx_bem_without_transformed_content_fails_closed(tmp_path):
    sent_messages = []
    repository = CuratedEvidenceRepositoryBackend(tmp_path / "curated.db")
    diagnostic = BasicOperationalDiagnosticService(repository=repository)

    adapter = TelegramAdapter(
        identity_service=_linked_identity(tmp_path),
        factory_task_enqueuer=lambda task_id, objective: {"status": "queued", "task_id": task_id},
        telegram_get_file=lambda file_id: {"file_path": f"docs/{file_id}.xlsx"},
        telegram_download_file=lambda file_path: b"xlsx-bytes",
        bem_xlsx_submitter=lambda tenant_id, file_name, file_bytes, file_id: {
            "call": {"callReferenceID": "abc", "outputs": [{}]}
        },
        curated_evidence_repository=repository,
        diagnostic_service=diagnostic,
        telegram_send_message=lambda chat_id, text: sent_messages.append(text),
    )

    result = adapter.handle_update(_xlsx_update(42, "xlsx-3"))

    assert result["status"] == "queued"
    assert result["bem"]["status"] == "error"
    assert "transformedContent" in result["bem"]["reason"]
    assert sent_messages[0] == "Error controlado al procesar XLSX con BEM. Intentá nuevamente."


def test_xlsx_tenant_invalid_fails_closed(tmp_path):
    class InvalidTenantIdentity:
        def get_cliente_id_for_telegram_user(self, user_id):
            return "   "

        def link_telegram_user(self, user_id, token):
            return {"status": "invalid"}

    adapter = TelegramAdapter(
        identity_service=InvalidTenantIdentity(),
        factory_task_enqueuer=lambda task_id, objective: {"status": "queued", "task_id": task_id},
    )

    result = adapter.handle_update(_xlsx_update(42, "xlsx-4"))

    assert result["status"] == "security_error"
    assert "tenant_id inválido" in result["message"]
