from factory.control.telegram_handler import (
    create_callback_token,
    load_allowed_user_ids,
    resolve_callback_token,
    validate_update,
)


def test_allowlist_and_dedup(tmp_path):
    allowlist = tmp_path / "allowlist.yaml"
    allowlist.write_text(
        (
            "owner:\n"
            "  user_id: 123\n"
            "  role: owner\n"
            "  enabled: true\n"
            "moderators: []\n"
            "auditors: []\n"
        ),
        encoding="utf-8",
    )
    db = tmp_path / "telegram.db"
    assert load_allowed_user_ids(allowlist) == [123]
    update = {
        "update_id": 1,
        "message": {
            "from": {"id": 123},
            "text": "/estado",
            "chat": {"id": 999},
        },
    }
    assert validate_update(update, db_path=db, allowlist_path=allowlist)["status"] == "ok"
    assert (
        validate_update(update, db_path=db, allowlist_path=allowlist)["code"]
        == "DUPLICATE_UPDATE"
    )


def test_callback_token_under_64_bytes(tmp_path):
    db = tmp_path / "telegram.db"
    token = create_callback_token("cycle-1", "APPROVE", db_path=db)
    assert len(token.encode("utf-8")) <= 64
    assert resolve_callback_token(token, db_path=db)["action"] == "APPROVE"
