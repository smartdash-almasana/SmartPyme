from app.adapters.telegram_adapter import TelegramAdapter
from app.services.identity_service import IdentityService


def _document_update(user_id: int, file_name: str, file_id: str = "file1") -> dict:
    return {
        "message": {
            "from": {"id": user_id},
            "document": {
                "file_id": file_id,
                "file_name": file_name,
                "mime_type": "application/octet-stream",
            },
        }
    }


def _linked_identity(tmp_path):
    identity = IdentityService(tmp_path / "identity.db")
    identity.create_onboarding_token("123456", "pyme_A")
    identity.link_telegram_user(42, "123456")
    return identity


def test_unlinked_user_document_is_rejected(tmp_path):
    adapter = TelegramAdapter(identity_service=IdentityService(tmp_path / "identity.db"))

    result = adapter.handle_update(_document_update(42, "factura.pdf"))

    assert result["status"] == "unauthorized"


def test_linked_user_allowed_document_is_queued(tmp_path):
    calls = []

    def fake_enqueue(task_id: str, objective: str) -> dict:
        calls.append({"task_id": task_id, "objective": objective})
        return {"status": "queued", "task_id": task_id}

    adapter = TelegramAdapter(
        identity_service=_linked_identity(tmp_path),
        factory_task_enqueuer=fake_enqueue,
    )

    result = adapter.handle_update(_document_update(42, "factura.pdf", file_id="abc"))

    assert result["status"] == "queued"
    assert result["cliente_id"] == "pyme_A"
    assert result["document"]["file_name"] == "factura.pdf"
    assert calls[0]["task_id"] == "telegram:pyme_A:abc"


def test_linked_user_xlsx_document_is_queued(tmp_path):
    adapter = TelegramAdapter(
        identity_service=_linked_identity(tmp_path),
        factory_task_enqueuer=lambda task_id, objective: {"status": "queued", "task_id": task_id},
    )

    result = adapter.handle_update(_document_update(42, "ventas.xlsx", file_id="xlsx1"))

    assert result["status"] == "queued"
    assert result["task"]["task_id"] == "telegram:pyme_A:xlsx1"


def test_unsupported_document_extension_is_rejected(tmp_path):
    adapter = TelegramAdapter(identity_service=_linked_identity(tmp_path))

    result = adapter.handle_update(_document_update(42, "malware.exe", file_id="bad"))

    assert result["status"] == "unsupported_document"
    assert "Formato no soportado" in result["message"]
