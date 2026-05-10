"""
FM-011 — Decoupling test: factory core y adapter Telegram operan sobre TaskSpec.

Valida que:
- factory/core guarda y ejecuta TaskSpec (sin comandos reales).
- factory/tools encola, consulta estado y ejecuta vía TaskSpec.
- TelegramSuperownerAdapter controla la factoría de punta a punta.
- El shim de compatibilidad FactorySuperownerTelegramAdapter sigue funcionando.

El runner se inyecta con command_runner y changed_paths_provider stub para
evitar ejecución de comandos reales en el entorno de test.
"""

from pathlib import Path

from factory.adapters.telegram_superowner_adapter import TelegramSuperownerAdapter
from factory.core.task_spec import TaskSpec, TaskSpecStatus
from factory.core.task_spec_runner import CommandResult, TaskSpecRunner
from factory.core.task_spec_store import TaskSpecStore


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _update(user_id: int, text: str) -> dict:
    return {"message": {"from": {"id": user_id}, "text": text}}


def _stub_command_runner(command: str) -> CommandResult:
    """Simula ejecución exitosa de cualquier comando de validación."""
    return CommandResult(command=command, exit_code=0, stdout="ok", stderr="")


def _stub_changed_paths_provider(task: TaskSpec) -> list[str]:
    """Devuelve paths dentro del allowed_paths del task para que la validación pase."""
    if task.allowed_paths:
        # Devolver un path dentro del primer allowed_path
        return [f"{task.allowed_paths[0]}/stub_file.py"]
    return []


def _make_adapter(tmp_path: Path) -> TelegramSuperownerAdapter:
    """Construye un adapter con runner stub para tests determinísticos."""
    tasks_dir = tmp_path / "tasks"
    evidence_dir = tmp_path / "evidence"
    store = TaskSpecStore(tasks_dir)
    runner = TaskSpecRunner(
        store=store,
        evidence_dir=evidence_dir,
        command_runner=_stub_command_runner,
        changed_paths_provider=_stub_changed_paths_provider,
    )
    return TelegramSuperownerAdapter(
        superowner_telegram_user_id=111,
        tasks_dir=tasks_dir,
        evidence_dir=evidence_dir,
        store=store,
        runner=runner,
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_decoupled_factory_core_saves_and_runs_task(tmp_path):
    """TaskSpecStore + TaskSpecRunner operan sin comandos reales."""
    tasks_dir = tmp_path / "tasks"
    evidence_dir = tmp_path / "evidence"
    store = TaskSpecStore(tasks_dir)
    runner = TaskSpecRunner(
        store=store,
        evidence_dir=evidence_dir,
        command_runner=_stub_command_runner,
        changed_paths_provider=_stub_changed_paths_provider,
    )

    task = TaskSpec(
        task_id="fm_task_1",
        title="Verificar core desacoplado",
        objective="Verificar core desacoplado",
        allowed_paths=["factory"],
        forbidden_paths=["app"],
        acceptance_criteria=["El core opera sin app imports."],
        validation_commands=["echo ok"],
    )
    store.enqueue(task)

    result = runner.run_next()

    assert result.task_id == "fm_task_1"
    assert result.status == TaskSpecStatus.DONE
    assert len(result.evidence_paths) > 0
    assert all(Path(p).exists() for p in result.evidence_paths)


def test_decoupled_factory_tools_enqueue_status_and_run(tmp_path):
    """TaskSpecStore encola, consulta estado y ejecuta correctamente."""
    tasks_dir = tmp_path / "tasks"
    evidence_dir = tmp_path / "evidence"
    store = TaskSpecStore(tasks_dir)
    runner = TaskSpecRunner(
        store=store,
        evidence_dir=evidence_dir,
        command_runner=_stub_command_runner,
        changed_paths_provider=_stub_changed_paths_provider,
    )

    task = TaskSpec(
        task_id="fm_task_2",
        title="Probar tools desacoplados",
        objective="Probar tools desacoplados",
        allowed_paths=["factory"],
        forbidden_paths=["app"],
        acceptance_criteria=["El store y runner operan correctamente."],
        validation_commands=["echo ok"],
    )
    store.enqueue(task)

    counts_before = store.counts()
    result = runner.run_next()
    counts_after = store.counts()
    done_task = store.get("fm_task_2")

    assert counts_before["pending"] == 1
    assert result.status == TaskSpecStatus.DONE
    assert result.task_id == "fm_task_2"
    assert counts_after["done"] == 1
    assert counts_after["pending"] == 0
    assert done_task is not None
    assert done_task.status == TaskSpecStatus.DONE


def test_decoupled_telegram_superowner_adapter_controls_factory(tmp_path):
    """TelegramSuperownerAdapter controla la factoría de punta a punta via TaskSpec."""
    adapter = _make_adapter(tmp_path)

    # 1. Encolar tarea vía /enqueue_dev
    queued = adapter.handle_update(_update(111, "/enqueue_dev Crear runner desacoplado"))
    assert queued["status"] == "queued"
    assert "task" in queued

    # 2. Consultar estado: debe haber 1 tarea pendiente
    status = adapter.handle_update(_update(111, "/status_factory"))
    assert status["status"] == "ok"
    assert status["counts"]["pending"] == 1

    # 3. Ejecutar /run_one: debe completar con DONE
    run = adapter.handle_update(_update(111, "/run_one"))
    assert run["status"] == TaskSpecStatus.DONE.value
    assert run["result"]["task_id"] is not None
    assert len(run["result"]["evidence_paths"]) > 0

    # 4. Estado post-ejecución: 0 pendientes, 1 done
    status_after = adapter.handle_update(_update(111, "/status_factory"))
    assert status_after["counts"]["pending"] == 0
    assert status_after["counts"]["done"] == 1


def test_app_superowner_adapter_shim_preserves_compatibility(tmp_path):
    """El shim FactorySuperownerTelegramAdapter mantiene compatibilidad."""
    from factory.adapters.telegram_superowner_adapter import (
        FactorySuperownerTelegramAdapter,
    )

    store = TaskSpecStore(tmp_path / "tasks")
    runner = TaskSpecRunner(
        store=store,
        evidence_dir=tmp_path / "evidence",
        command_runner=_stub_command_runner,
        changed_paths_provider=_stub_changed_paths_provider,
    )
    adapter = FactorySuperownerTelegramAdapter(
        superowner_telegram_user_id=111,
        tasks_dir=tmp_path / "tasks",
        evidence_dir=tmp_path / "evidence",
        store=store,
        runner=runner,
    )

    response = adapter.handle_update(_update(111, "/status_factory"))

    assert response["status"] == "ok"
    assert response["counts"]["pending"] == 0
