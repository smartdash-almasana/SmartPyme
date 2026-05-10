"""
FM-010 — TelegramSuperownerAdapter sobre runtime TaskSpec.

Valida que el adapter Telegram controla la factoría usando TaskSpec/TaskSpecStore/TaskSpecRunner.
Los tests que usan runner inyectan stubs determinísticos para evitar comandos reales.
"""

from pathlib import Path

from factory.adapters.telegram_superowner_adapter import TelegramSuperownerAdapter as FactorySuperownerTelegramAdapter
from factory.core.task_spec import TaskSpec, TaskSpecStatus
from factory.core.task_spec_runner import CommandResult, TaskSpecRunner
from factory.core.task_spec_store import TaskSpecStore


def _update(user_id: int, text: str) -> dict:
    return {"message": {"from": {"id": user_id}, "text": text}}


def _stub_command_runner(command: str) -> CommandResult:
    """Simula ejecución exitosa de cualquier comando de validación."""
    return CommandResult(command=command, exit_code=0, stdout="ok", stderr="")


def _stub_changed_paths_provider(task: TaskSpec) -> list[str]:
    """Devuelve un path dentro del allowed_paths del task para que la validación pase."""
    if task.allowed_paths:
        return [f"{task.allowed_paths[0]}/stub_file.py"]
    return []


def _make_adapter(tmp_path: Path) -> FactorySuperownerTelegramAdapter:
    """Construye adapter con runner stub para tests determinísticos."""
    tasks_dir = tmp_path / "tasks"
    evidence_dir = tmp_path / "evidence"
    store = TaskSpecStore(tasks_dir)
    runner = TaskSpecRunner(
        store=store,
        evidence_dir=evidence_dir,
        command_runner=_stub_command_runner,
        changed_paths_provider=_stub_changed_paths_provider,
    )
    return FactorySuperownerTelegramAdapter(
        superowner_telegram_user_id=111,
        tasks_dir=tasks_dir,
        evidence_dir=evidence_dir,
        store=store,
        runner=runner,
    )


def _enqueue_task_spec(store: TaskSpecStore, task_id: str, objective: str) -> TaskSpec:
    """Encola un TaskSpec mínimo válido directamente en el store."""
    task = TaskSpec(
        task_id=task_id,
        title=objective[:80],
        objective=objective,
        allowed_paths=["factory"],
        forbidden_paths=["app"],
        acceptance_criteria=["El task se ejecuta correctamente."],
        validation_commands=["echo ok"],
        metadata={"origin": "test", "task_type": "dev_task"},
    )
    store.enqueue(task)
    return task


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_superowner_telegram_rejects_non_superowner(tmp_path):
    """Usuarios no autorizados son rechazados."""
    adapter = FactorySuperownerTelegramAdapter(
        superowner_telegram_user_id=111,
        tasks_dir=tmp_path / "tasks",
        evidence_dir=tmp_path / "evidence",
    )

    response = adapter.handle_update(_update(999, "/status_factory"))

    assert response["status"] == "unauthorized"
    assert response["telegram_user_id"] == "999"


def test_superowner_telegram_status_and_pending_tasks(tmp_path):
    """Status y tasks_pending reflejan el estado del TaskSpecStore."""
    adapter = _make_adapter(tmp_path)
    _enqueue_task_spec(adapter.store, "dev_task_1", "Implementar tarea dev 1")

    status = adapter.handle_update(_update(111, "/status_factory"))
    pending = adapter.handle_update(_update(111, "/tasks_pending"))

    assert status["status"] == "ok"
    assert status["counts"]["pending"] == 1
    assert status["next_pending_task_id"] == "dev_task_1"
    assert pending["status"] == "ok"
    assert pending["pending_count"] == 1
    assert pending["pending_tasks"][0]["task_id"] == "dev_task_1"


def test_superowner_telegram_enqueue_dev_and_task_status(tmp_path):
    """enqueue_dev crea un TaskSpec via template y /task devuelve su estado."""
    adapter = _make_adapter(tmp_path)

    queued = adapter.handle_update(_update(111, "/enqueue_dev Crear contrato TaskSpec real"))

    assert queued["status"] == "queued"
    # El adapter usa template code_change vía /enqueue_dev → task_type es "taskspec_template"
    assert "task_id" in queued["task"]

    task_id = queued["task"]["task_id"]
    task_status = adapter.handle_update(_update(111, f"/task {task_id}"))

    assert task_status["status"] == TaskSpecStatus.PENDING.value
    assert task_status["task"]["task_id"] == task_id
    assert task_status["task"]["objective"] == "Crear contrato TaskSpec real"


def test_superowner_telegram_run_one_executes_pending_dev_task(tmp_path):
    """run_one ejecuta la tarea pendiente y devuelve DONE con evidencia."""
    adapter = _make_adapter(tmp_path)
    _enqueue_task_spec(adapter.store, "dev_task_1", "Implementar tarea dev 1")

    run = adapter.handle_update(_update(111, "/run_one"))
    task_status = adapter.handle_update(_update(111, "/task dev_task_1"))

    assert run["status"] == TaskSpecStatus.DONE.value
    assert run["result"]["task_id"] == "dev_task_1"
    assert len(run["result"]["evidence_paths"]) > 0
    assert all(Path(p).exists() for p in run["result"]["evidence_paths"])
    assert task_status["status"] == TaskSpecStatus.DONE.value


def test_superowner_telegram_run_one_idle_when_no_pending_tasks(tmp_path):
    """run_one devuelve idle cuando no hay tareas pendientes."""
    adapter = FactorySuperownerTelegramAdapter(
        superowner_telegram_user_id=111,
        tasks_dir=tmp_path / "tasks",
        evidence_dir=tmp_path / "evidence",
    )

    run = adapter.handle_update(_update(111, "/run_one"))

    assert run["status"] == "idle"
    assert run["result"]["reason"] == "NO_PENDING_TASK"
