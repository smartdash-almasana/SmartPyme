from factory.adapters.telegram_superowner_adapter import TelegramSuperownerAdapter
from factory.core.task_spec_store import TaskSpecStore


def _update(user_id: int, text: str) -> dict:
    return {"message": {"from": {"id": user_id}, "text": text}}


def test_templates_command_lists_available_templates(tmp_path):
    adapter = TelegramSuperownerAdapter(
        superowner_telegram_user_id=111,
        store=TaskSpecStore(tmp_path / "taskspecs"),
    )

    response = adapter.handle_update(_update(111, "/templates"))

    assert response["status"] == "ok"
    assert response["templates"] == [
        "audit_only",
        "code_change",
        "docs_change",
        "refactor",
        "test_fix",
    ]
    assert "code_change" in response["message"]


def test_enqueue_template_creates_taskspec_from_named_template(tmp_path):
    store = TaskSpecStore(tmp_path / "taskspecs")
    adapter = TelegramSuperownerAdapter(superowner_telegram_user_id=111, store=store)

    response = adapter.handle_update(
        _update(111, "/enqueue_template docs_change Documentar comandos de factoría")
    )

    assert response["status"] == "queued"
    assert response["task"]["task_type"] == "taskspec_template"
    assert response["task"]["template"] == "docs_change"

    task_id = response["task"]["task_id"]
    task = store.get(task_id)
    assert task is not None
    assert task.metadata["template"] == "docs_change"
    assert task.metadata["origin"] == "telegram_superowner"
    assert task.metadata["telegram_user_id"] == "111"
    assert task.objective == "Documentar comandos de factoría"
    assert "docs" in task.allowed_paths
    assert "app" in task.forbidden_paths


def test_enqueue_dev_keeps_backward_compatibility_via_code_change_template(tmp_path):
    store = TaskSpecStore(tmp_path / "taskspecs")
    adapter = TelegramSuperownerAdapter(superowner_telegram_user_id=111, store=store)

    response = adapter.handle_update(_update(111, "/enqueue_dev Crear módulo runner"))

    assert response["status"] == "queued"
    assert response["task"]["template"] == "code_change"

    task = store.get(response["task"]["task_id"])
    assert task is not None
    assert task.metadata["template"] == "code_change"
    assert task.objective == "Crear módulo runner"


def test_enqueue_template_rejects_unknown_template(tmp_path):
    adapter = TelegramSuperownerAdapter(
        superowner_telegram_user_id=111,
        store=TaskSpecStore(tmp_path / "taskspecs"),
    )

    response = adapter.handle_update(_update(111, "/enqueue_template unknown Hacer algo"))

    assert response["status"] == "invalid_template"
    assert response["template"] == "unknown"
    assert "Unknown TaskSpec template" in response["message"]


def test_enqueue_template_rejects_invalid_format(tmp_path):
    adapter = TelegramSuperownerAdapter(
        superowner_telegram_user_id=111,
        store=TaskSpecStore(tmp_path / "taskspecs"),
    )

    missing_objective = adapter.handle_update(_update(111, "/enqueue_template code_change"))
    missing_template = adapter.handle_update(_update(111, "/enqueue_template"))

    assert missing_objective["status"] == "invalid_command"
    assert missing_template["status"] == "unsupported_command"


def test_enqueue_template_rejects_non_superowner(tmp_path):
    store = TaskSpecStore(tmp_path / "taskspecs")
    adapter = TelegramSuperownerAdapter(superowner_telegram_user_id=111, store=store)

    response = adapter.handle_update(_update(999, "/enqueue_template code_change Crear algo"))

    assert response["status"] == "unauthorized"
    assert store.counts()["pending"] == 0
