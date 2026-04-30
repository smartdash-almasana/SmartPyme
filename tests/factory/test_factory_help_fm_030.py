from factory.adapters.telegram_superowner_adapter import TelegramSuperownerAdapter
from factory.core.factory_help import build_factory_help_payload, format_factory_help_message
from factory.core.task_spec_store import TaskSpecStore


def _update(user_id: int, text: str) -> dict:
    return {"message": {"from": {"id": user_id}, "text": text}}


def test_build_factory_help_payload_lists_core_commands():
    payload = build_factory_help_payload()
    commands = [item["command"] for item in payload["commands"]]

    assert payload["commands_count"] == len(payload["commands"])
    assert "/factory_help" in commands
    assert "/factory_health" in commands
    assert "/run_one" in commands
    assert "/run_batch <n>" in commands
    assert "/failed_paths" in commands
    assert "/diff <task_id>" in commands
    assert payload["recommended_flow"][0] == "/factory_health"


def test_format_factory_help_message_is_compact_and_actionable():
    payload = build_factory_help_payload()
    message = format_factory_help_message(payload)

    assert "Factory help" in message
    assert "Flujo recomendado" in message
    assert "/factory_health" in message
    assert "/run_one" in message


def test_telegram_factory_help_returns_help_payload(tmp_path):
    adapter = TelegramSuperownerAdapter(
        superowner_telegram_user_id=111,
        store=TaskSpecStore(tmp_path / "taskspecs"),
    )

    response = adapter.handle_update(_update(111, "/factory_help"))

    commands = [item["command"] for item in response["help"]["commands"]]
    assert response["status"] == "ok"
    assert response["help"]["commands_count"] == len(response["help"]["commands"])
    assert "/factory_help" in commands
    assert "/factory_health" in commands
    assert "/failed_paths" in commands
    assert "Factory help" in response["message"]


def test_telegram_factory_help_rejects_non_superowner(tmp_path):
    adapter = TelegramSuperownerAdapter(
        superowner_telegram_user_id=111,
        store=TaskSpecStore(tmp_path / "taskspecs"),
    )

    response = adapter.handle_update(_update(999, "/factory_help"))

    assert response["status"] == "unauthorized"
