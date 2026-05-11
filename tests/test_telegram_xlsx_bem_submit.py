from app.adapters.telegram_adapter import TelegramAdapter
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


def _linked_identity(tmp_path):
    identity = IdentityService(tmp_path / "identity.db")
    identity.create_onboarding_token("token-1", "pyme_A")
    identity.link_telegram_user(42, "token-1")
    return identity


def test_xlsx_happy_path_submits_to_bem_and_sends_controlled_message(tmp_path):
    sent_messages = []
    submit_calls = []

    adapter = TelegramAdapter(
        identity_service=_linked_identity(tmp_path),
        factory_task_enqueuer=lambda task_id, objective: {"status": "queued", "task_id": task_id},
        telegram_get_file=lambda file_id: {"file_path": f"docs/{file_id}.xlsx"},
        telegram_download_file=lambda file_path: b"xlsx-bytes",
        bem_xlsx_submitter=lambda tenant_id, file_name, file_bytes, file_id: (
            submit_calls.append(
                {
                    "tenant_id": tenant_id,
                    "file_name": file_name,
                    "file_bytes": file_bytes,
                    "file_id": file_id,
                }
            )
            or {"call": {"id": "bem-call-1"}, "outputs": []}
        ),
        telegram_send_message=lambda chat_id, text: sent_messages.append(
            {"chat_id": str(chat_id), "text": text}
        ),
    )

    result = adapter.handle_update(_xlsx_update(42, "xlsx-1"))

    assert result["status"] == "queued"
    assert result["bem"]["status"] == "ok"
    assert submit_calls[0]["tenant_id"] == "pyme_A"
    assert submit_calls[0]["file_name"] == "ventas.xlsx"
    assert submit_calls[0]["file_id"] == "xlsx-1"
    assert sent_messages[0]["chat_id"] == "42"
    assert sent_messages[0]["text"] == "Archivo recibido y procesado por BEM"


def test_xlsx_fail_download_returns_controlled_error_and_keeps_intake(tmp_path):
    sent_messages = []

    adapter = TelegramAdapter(
        identity_service=_linked_identity(tmp_path),
        factory_task_enqueuer=lambda task_id, objective: {"status": "queued", "task_id": task_id},
        telegram_get_file=lambda file_id: {"file_path": f"docs/{file_id}.xlsx"},
        telegram_download_file=lambda file_path: (_ for _ in ()).throw(RuntimeError("download failed")),
        telegram_send_message=lambda chat_id, text: sent_messages.append(
            {"chat_id": str(chat_id), "text": text}
        ),
    )

    result = adapter.handle_update(_xlsx_update(42, "xlsx-2"))

    assert result["status"] == "queued"
    assert result["bem"]["status"] == "error"
    assert "download failed" in result["bem"]["reason"]
    assert sent_messages[0]["text"] == "Error controlado al procesar XLSX con BEM. Intentá nuevamente."


def test_xlsx_fail_bem_returns_controlled_error_and_keeps_intake(tmp_path):
    sent_messages = []

    adapter = TelegramAdapter(
        identity_service=_linked_identity(tmp_path),
        factory_task_enqueuer=lambda task_id, objective: {"status": "queued", "task_id": task_id},
        telegram_get_file=lambda file_id: {"file_path": f"docs/{file_id}.xlsx"},
        telegram_download_file=lambda file_path: b"xlsx-bytes",
        bem_xlsx_submitter=lambda tenant_id, file_name, file_bytes, file_id: (_ for _ in ()).throw(
            RuntimeError("bem unavailable")
        ),
        telegram_send_message=lambda chat_id, text: sent_messages.append(
            {"chat_id": str(chat_id), "text": text}
        ),
    )

    result = adapter.handle_update(_xlsx_update(42, "xlsx-3"))

    assert result["status"] == "queued"
    assert result["bem"]["status"] == "error"
    assert "bem unavailable" in result["bem"]["reason"]
    assert sent_messages[0]["text"] == "Error controlado al procesar XLSX con BEM. Intentá nuevamente."
