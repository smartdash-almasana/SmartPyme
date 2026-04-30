from pathlib import Path

from app.adapters.factory_superowner_telegram_adapter import FactorySuperownerTelegramAdapter
from app.mcp.tools.factory_control_tool import enqueue_factory_task


def _update(user_id: int, text: str) -> dict:
    return {"message": {"from": {"id": user_id}, "text": text}}


def test_superowner_telegram_rejects_non_superowner(tmp_path):
    adapter = FactorySuperownerTelegramAdapter(
        superowner_telegram_user_id=111,
        tasks_dir=tmp_path / "tasks",
        evidence_dir=tmp_path / "evidence",
    )

    response = adapter.handle_update(_update(999, "/status_factory"))

    assert response["status"] == "unauthorized"
    assert response["telegram_user_id"] == "999"


def test_superowner_telegram_status_and_pending_tasks(tmp_path):
    tasks_dir = tmp_path / "tasks"
    adapter = FactorySuperownerTelegramAdapter(
        superowner_telegram_user_id=111,
        tasks_dir=tasks_dir,
        evidence_dir=tmp_path / "evidence",
    )
    enqueue_factory_task(
        task_id="dev_task_1",
        objective="Implementar tarea dev 1",
        tasks_dir=tasks_dir,
        task_type="dev_task",
        payload={"origin": "test"},
    )

    status = adapter.handle_update(_update(111, "/status_factory"))
    pending = adapter.handle_update(_update(111, "/tasks_pending"))

    assert status["status"] == "ok"
    assert status["counts"]["pending"] == 1
    assert status["next_pending_task_id"] == "dev_task_1"
    assert pending["status"] == "ok"
    assert pending["pending_count"] == 1
    assert pending["pending_tasks"][0]["task_id"] == "dev_task_1"


def test_superowner_telegram_enqueue_dev_and_task_status(tmp_path):
    tasks_dir = tmp_path / "tasks"
    adapter = FactorySuperownerTelegramAdapter(
        superowner_telegram_user_id=111,
        tasks_dir=tasks_dir,
        evidence_dir=tmp_path / "evidence",
    )

    queued = adapter.handle_update(_update(111, "/enqueue_dev Crear contrato TaskSpec real"))

    assert queued["status"] == "queued"
    assert queued["task"]["task_type"] == "dev_task"

    task_id = queued["task"]["task_id"]
    status = adapter.handle_update(_update(111, f"/task {task_id}"))

    assert status["status"] == "pending"
    assert status["task"]["task_id"] == task_id
    assert status["task"]["objective"] == "Crear contrato TaskSpec real"
    assert status["task"]["payload"]["origin"] == "telegram_superowner"


def test_superowner_telegram_run_one_executes_pending_dev_task(tmp_path):
    tasks_dir = tmp_path / "tasks"
    evidence_dir = tmp_path / "evidence"
    adapter = FactorySuperownerTelegramAdapter(
        superowner_telegram_user_id=111,
        tasks_dir=tasks_dir,
        evidence_dir=evidence_dir,
    )
    enqueue_factory_task(
        task_id="dev_task_1",
        objective="Implementar tarea dev 1",
        tasks_dir=tasks_dir,
        task_type="dev_task",
        payload={"origin": "test"},
    )

    run = adapter.handle_update(_update(111, "/run_one"))
    status = adapter.handle_update(_update(111, "/task dev_task_1"))

    assert run["status"] == "done"
    assert run["result"]["task_id"] == "dev_task_1"
    assert Path(run["result"]["report_path"]).exists()
    assert status["status"] == "done"
    assert status["task"]["audit"]["status"] == "passed"


def test_superowner_telegram_run_one_idle_when_no_pending_tasks(tmp_path):
    adapter = FactorySuperownerTelegramAdapter(
        superowner_telegram_user_id=111,
        tasks_dir=tmp_path / "tasks",
        evidence_dir=tmp_path / "evidence",
    )

    run = adapter.handle_update(_update(111, "/run_one"))

    assert run["status"] == "idle"
    assert run["result"]["reason"] == "NO_PENDING_TASK"
