from pathlib import Path

from factory.adapters.telegram_superowner_adapter import TelegramSuperownerAdapter
from factory.core.queue_runner import run_one_queued_task
from factory.core.task_loop import MultiagentTask, load_task, save_task
from factory.tools.factory_control import (
    enqueue_factory_task,
    get_factory_task_status,
    run_factory_once,
)


def _update(user_id: int, text: str) -> dict:
    return {"message": {"from": {"id": user_id}, "text": text}}


def test_decoupled_factory_core_saves_and_runs_task(tmp_path):
    tasks_dir = tmp_path / "tasks"
    evidence_dir = tmp_path / "evidence"
    save_task(
        MultiagentTask(task_id="fm_task_1", objective="Verificar core desacoplado"),
        tasks_dir,
    )

    result = run_one_queued_task(tasks_dir, evidence_dir)
    task = load_task("fm_task_1", tasks_dir)

    assert result["status"] == "done"
    assert result["task_id"] == "fm_task_1"
    assert task is not None
    assert task.status == "done"
    assert Path(result["report_path"]).exists()


def test_decoupled_factory_tools_enqueue_status_and_run(tmp_path):
    tasks_dir = tmp_path / "tasks"
    evidence_dir = tmp_path / "evidence"

    queued = enqueue_factory_task(
        task_id="fm_task_2",
        objective="Probar tools desacoplados",
        tasks_dir=tasks_dir,
        task_type="dev_task",
        payload={"origin": "fm_011_test"},
    )
    before = get_factory_task_status("fm_task_2", tasks_dir=tasks_dir)
    run = run_factory_once(tasks_dir=tasks_dir, evidence_dir=evidence_dir)
    after = get_factory_task_status("fm_task_2", tasks_dir=tasks_dir)

    assert queued["status"] == "queued"
    assert before["status"] == "pending"
    assert before["task_type"] == "dev_task"
    assert run["status"] == "done"
    assert after["status"] == "done"
    assert after["audit"]["status"] == "passed"


def test_decoupled_telegram_superowner_adapter_controls_factory(tmp_path):
    tasks_dir = tmp_path / "tasks"
    evidence_dir = tmp_path / "evidence"
    adapter = TelegramSuperownerAdapter(
        superowner_telegram_user_id=111,
        tasks_dir=tasks_dir,
        evidence_dir=evidence_dir,
    )

    queued = adapter.handle_update(_update(111, "/enqueue_dev Crear runner desacoplado"))
    status = adapter.handle_update(_update(111, "/status_factory"))
    run = adapter.handle_update(_update(111, "/run_one"))

    assert queued["status"] == "queued"
    assert status["counts"]["pending"] == 1
    assert run["status"] == "done"
    assert Path(run["result"]["report_path"]).exists()


def test_app_superowner_adapter_shim_preserves_compatibility(tmp_path):
    from app.adapters.factory_superowner_telegram_adapter import (
        FactorySuperownerTelegramAdapter,
    )

    adapter = FactorySuperownerTelegramAdapter(
        superowner_telegram_user_id=111,
        tasks_dir=tmp_path / "tasks",
        evidence_dir=tmp_path / "evidence",
    )

    response = adapter.handle_update(_update(111, "/status_factory"))

    assert response["status"] == "ok"
    assert response["counts"]["pending"] == 0
