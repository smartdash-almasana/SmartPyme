from pathlib import Path

from app.adapters.telegram_adapter import TelegramAdapter
from factory.adapters.app_bridge.agent_loop.multiagent_task_loop import load_task
from app.agents.business_task_executor import AUDIT_VENTA_BAJO_COSTO
from app.services.identity_service import IdentityService


def _update(user_id: int, text: str) -> dict:
    return {
        "message": {
            "from": {"id": user_id},
            "text": text,
        }
    }


def _linked_identity(
    tmp_path: Path, user_id: int = 111, cliente_id: str = "pyme_A"
) -> IdentityService:
    identity = IdentityService(tmp_path / "identity.db")
    identity.create_onboarding_token("token-a", cliente_id)
    result = identity.link_telegram_user(user_id, "token-a")
    assert result["status"] == "linked"
    return identity


def test_telegram_audit_venta_bajo_costo_enqueues_business_task(tmp_path):
    tasks_dir = tmp_path / "tasks"
    identity = _linked_identity(tmp_path)

    def enqueuer(task_id, objective, task_type=None, payload=None):
        from app.mcp.tools.factory_control_tool import enqueue_factory_task

        return enqueue_factory_task(
            task_id=task_id,
            objective=objective,
            tasks_dir=tasks_dir,
            task_type=task_type,
            payload=payload,
        )

    adapter = TelegramAdapter(
        identity_service=identity,
        factory_task_enqueuer=enqueuer,
    )

    response = adapter.handle_update(_update(111, "/auditar_venta_bajo_costo 1000 1200"))

    assert response["status"] == "queued"
    assert response["cliente_id"] == "pyme_A"
    assert response["payload"]["cliente_id"] == "pyme_A"
    assert response["payload"]["ventas"] == 1000.0
    assert response["payload"]["costos"] == 1200.0
    assert response["task"]["task_type"] == AUDIT_VENTA_BAJO_COSTO

    task_id = response["task"]["task_id"]
    task = load_task(task_id, tasks_dir)
    assert task is not None
    assert task.status == "pending"
    assert task.task_type == AUDIT_VENTA_BAJO_COSTO
    assert task.payload["cliente_id"] == "pyme_A"
    assert task.payload["ventas"] == 1000.0
    assert task.payload["costos"] == 1200.0
    assert task.payload["source_refs"] == ["telegram:111:/auditar_venta_bajo_costo"]


def test_telegram_audit_venta_bajo_costo_rejects_unlinked_user(tmp_path):
    tasks_dir = tmp_path / "tasks"
    identity = IdentityService(tmp_path / "identity.db")
    calls = []

    def enqueuer(*args, **kwargs):
        calls.append((args, kwargs))
        raise AssertionError("unlinked user must not enqueue tasks")

    adapter = TelegramAdapter(
        identity_service=identity,
        factory_task_enqueuer=enqueuer,
    )

    response = adapter.handle_update(_update(999, "/auditar_venta_bajo_costo 1000 1200"))

    assert response["status"] == "unauthorized"
    assert calls == []
    assert not tasks_dir.exists()


def test_telegram_audit_venta_bajo_costo_rejects_invalid_input(tmp_path):
    tasks_dir = tmp_path / "tasks"
    identity = _linked_identity(tmp_path)
    calls = []

    def enqueuer(*args, **kwargs):
        calls.append((args, kwargs))
        raise AssertionError("invalid input must not enqueue tasks")

    adapter = TelegramAdapter(
        identity_service=identity,
        factory_task_enqueuer=enqueuer,
    )

    response = adapter.handle_update(_update(111, "/auditar_venta_bajo_costo mil 1200"))

    assert response["status"] == "invalid_command"
    assert response["cliente_id"] == "pyme_A"
    assert calls == []
    assert not tasks_dir.exists()
