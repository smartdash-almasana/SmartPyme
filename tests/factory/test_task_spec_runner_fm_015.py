from pathlib import Path

from factory.core.task_spec import TaskSpec, TaskSpecStatus
from factory.core.task_spec_runner import CommandResult, TaskSpecRunner
from factory.core.task_spec_store import TaskSpecStore


def _task(task_id="FM_015"):
    return TaskSpec(
        task_id=task_id,
        title="Crear TaskSpecRunner",
        objective="Ejecutar TaskSpec con validación y evidencia",
        allowed_paths=["factory/core", "tests/factory"],
        forbidden_paths=["app"],
        acceptance_criteria=["runner cierra done o blocked"],
        validation_commands=["pytest fake"],
    )


def _ok_runner(command: str) -> CommandResult:
    return CommandResult(command=command, exit_code=0, stdout="ok", stderr="")


def _fail_runner(command: str) -> CommandResult:
    return CommandResult(command=command, exit_code=1, stdout="", stderr="failed")


def test_runner_run_next_done_generates_evidence(tmp_path):
    store = TaskSpecStore(tmp_path / "taskspecs")
    store.enqueue(_task())
    runner = TaskSpecRunner(
        store,
        evidence_dir=tmp_path / "evidence",
        changed_paths_provider=lambda task: [
            "factory/core/task_spec_runner.py",
            "tests/factory/test_task_spec_runner_fm_015.py",
        ],
        command_runner=_ok_runner,
    )

    result = runner.run_next()
    task = store.get("FM_015")

    assert result.status == TaskSpecStatus.DONE
    assert result.task_id == "FM_015"
    assert result.blocking_reason is None
    assert len(result.evidence_paths) == 2
    assert all(Path(path).exists() for path in result.evidence_paths)
    assert task is not None
    assert task.status == TaskSpecStatus.DONE
    assert task.evidence_paths == result.evidence_paths


def test_runner_blocks_when_validation_command_fails(tmp_path):
    store = TaskSpecStore(tmp_path / "taskspecs")
    store.enqueue(_task())
    runner = TaskSpecRunner(
        store,
        evidence_dir=tmp_path / "evidence",
        changed_paths_provider=lambda task: ["factory/core/task_spec_runner.py"],
        command_runner=_fail_runner,
    )

    result = runner.run_task("FM_015")
    task = store.get("FM_015")

    assert result.status == TaskSpecStatus.BLOCKED
    assert result.blocking_reason == "VALIDATION_COMMAND_FAILED: pytest fake"
    assert result.command_results[0].exit_code == 1
    assert task is not None
    assert task.status == TaskSpecStatus.BLOCKED
    assert task.blocking_reason == "VALIDATION_COMMAND_FAILED: pytest fake"


def test_runner_blocks_when_changed_path_is_forbidden(tmp_path):
    store = TaskSpecStore(tmp_path / "taskspecs")
    store.enqueue(_task())
    runner = TaskSpecRunner(
        store,
        evidence_dir=tmp_path / "evidence",
        changed_paths_provider=lambda task: ["app/services/runtime.py"],
        command_runner=_ok_runner,
    )

    result = runner.run_task("FM_015")
    task = store.get("FM_015")

    assert result.status == TaskSpecStatus.BLOCKED
    assert result.blocking_reason == "PATH_VALIDATION_FAILED"
    assert "FORBIDDEN_PATH_MODIFIED: app/services/runtime.py" in result.path_errors
    assert task is not None
    assert task.status == TaskSpecStatus.BLOCKED


def test_runner_run_next_idle_when_no_pending_task(tmp_path):
    store = TaskSpecStore(tmp_path / "taskspecs")
    runner = TaskSpecRunner(store, evidence_dir=tmp_path / "evidence")

    result = runner.run_next()

    assert result.status == TaskSpecStatus.PENDING
    assert result.task_id is None
    assert result.blocking_reason == "NO_PENDING_TASK"


def test_runner_run_task_missing_returns_blocked_result(tmp_path):
    store = TaskSpecStore(tmp_path / "taskspecs")
    runner = TaskSpecRunner(store, evidence_dir=tmp_path / "evidence")

    result = runner.run_task("missing")

    assert result.status == TaskSpecStatus.BLOCKED
    assert result.task_id == "missing"
    assert result.blocking_reason == "TASK_NOT_FOUND"


def test_runner_rejects_non_pending_task_without_mutating_terminal_state(tmp_path):
    store = TaskSpecStore(tmp_path / "taskspecs")
    store.enqueue(_task())
    store.mark_in_progress("FM_015")
    store.mark_done("FM_015", evidence_paths=["factory/evidence/FM_015/report.txt"])
    runner = TaskSpecRunner(store, evidence_dir=tmp_path / "evidence")

    result = runner.run_task("FM_015")
    task = store.get("FM_015")

    assert result.status == TaskSpecStatus.BLOCKED
    assert result.blocking_reason == "Only pending TaskSpec can move to in_progress"
    assert task is not None
    assert task.status == TaskSpecStatus.DONE
