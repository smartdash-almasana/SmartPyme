from app.services.identity_service import IdentityService


def test_create_token_and_link_telegram_user(tmp_path):
    service = IdentityService(tmp_path / "identity.db")
    service.create_onboarding_token("123456", "pyme_A")

    result = service.link_telegram_user(telegram_user_id=42, token="123456")

    assert result["status"] == "linked"
    assert result["telegram_user_id"] == "42"
    assert result["cliente_id"] == "pyme_A"
    assert service.get_cliente_id_for_telegram_user(42) == "pyme_A"
    assert service.is_authorized(42) is True


def test_invalid_token_does_not_authorize_user(tmp_path):
    service = IdentityService(tmp_path / "identity.db")

    result = service.link_telegram_user(telegram_user_id=42, token="missing")

    assert result["status"] == "invalid_token"
    assert result["cliente_id"] is None
    assert service.is_authorized(42) is False


def test_token_cannot_be_reused(tmp_path):
    service = IdentityService(tmp_path / "identity.db")
    service.create_onboarding_token("123456", "pyme_A")

    first = service.link_telegram_user(telegram_user_id=42, token="123456")
    second = service.link_telegram_user(telegram_user_id=99, token="123456")

    assert first["status"] == "linked"
    assert second["status"] == "invalid_token"
    assert service.get_cliente_id_for_telegram_user(99) is None


def test_existing_user_can_be_relinked_with_new_token(tmp_path):
    service = IdentityService(tmp_path / "identity.db")
    service.create_onboarding_token("111111", "pyme_A")
    service.create_onboarding_token("222222", "pyme_B")

    service.link_telegram_user(telegram_user_id=42, token="111111")
    service.link_telegram_user(telegram_user_id=42, token="222222")

    assert service.get_cliente_id_for_telegram_user(42) == "pyme_B"
