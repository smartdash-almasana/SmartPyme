from app.adapters.telegram_adapter import TelegramAdapter
from app.services.identity_service import IdentityService


def _update(user_id: int, text: str) -> dict:
    return {
        "message": {
            "from": {"id": user_id},
            "text": text,
        }
    }


def test_new_user_status_is_rejected(tmp_path):
    identity = IdentityService(tmp_path / "identity.db")
    adapter = TelegramAdapter(identity_service=identity)

    result = adapter.handle_update(_update(42, "/status"))

    assert result["status"] == "unauthorized"
    assert result["telegram_user_id"] == "42"
    assert "Cuenta no vinculada" in result["message"]


def test_user_can_link_with_valid_token(tmp_path):
    identity = IdentityService(tmp_path / "identity.db")
    identity.create_onboarding_token("123456", "pyme_A")
    adapter = TelegramAdapter(identity_service=identity)

    result = adapter.handle_update(_update(42, "/vincular 123456"))

    assert result["status"] == "linked"
    assert result["cliente_id"] == "pyme_A"
    assert identity.get_cliente_id_for_telegram_user(42) == "pyme_A"


def test_linked_user_status_returns_owner_status(tmp_path):
    identity = IdentityService(tmp_path / "identity.db")
    identity.create_onboarding_token("123456", "pyme_A")
    identity.link_telegram_user(42, "123456")

    def fake_owner_status(cliente_id: str) -> dict:
        return {
            "cliente_id": cliente_id,
            "jobs_count": 1,
            "findings_count": 2,
            "formula_results_count": 3,
            "pathology_findings_count": 4,
            "messages": ["ok"],
        }

    adapter = TelegramAdapter(identity_service=identity, owner_status_provider=fake_owner_status)

    result = adapter.handle_update(_update(42, "/status"))

    assert result["status"] == "ok"
    assert result["cliente_id"] == "pyme_A"
    assert result["data"]["jobs_count"] == 1
    assert "patologías=4" in result["message"]


def test_missing_user_id_is_security_error(tmp_path):
    adapter = TelegramAdapter(identity_service=IdentityService(tmp_path / "identity.db"))

    result = adapter.handle_update({"message": {"text": "/status"}})

    assert result["status"] == "security_error"
