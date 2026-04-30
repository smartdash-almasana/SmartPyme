import pytest

from factory.core.task_spec import TaskSpec, TaskSpecStatus
from factory.core.task_spec_store import TaskSpecStore


def _task(task_id="FM_014"):
    return TaskSpec(
        task_id=task_id,
        title="Crear TaskSpecStore",
        objective="Persistir TaskSpec por estados",
        allowed_paths=["factory/core", "tests/factory"],
        forbidden_paths=["app"],
        acceptance_criteria=["store persiste estados"],
        validation_commands=["PYTHONPATH=. pytest tests/factory/test_task_spec_store_fm_014.py"],
    )


def test_store_enqueue_and_get_pending_task(tmp_path):
    store = TaskSpecStore(tmp_path / "taskspecs")

    path = store.enqueue(_task())
    loaded = store.get("FM_014")

    assert path.endswith("pending/FM_014.json")
    assert loaded is not None
    assert loaded.task_id == "FM_014"
    assert loaded.status == TaskSpecStatus.PENDING


def test_store_rejects_duplicate_task_id_across_states(tmp_path):
    store = TaskSpecStore(tmp_path / "taskspecs")
    store.enqueue(_task())
    store.mark_in_progress("FM_014")

    with pytest.raises(ValueError, match="TaskSpec already exists"):
        store.enqueue(_task())


def test_store_state_transitions_pending_to_in_progress_to_done(tmp_path):
    store = TaskSpecStore(tmp_path / "taskspecs")
    store.enqueue(_task())

    in_progress = store.mark_in_progress("FM_014")
    done = store.mark_done("FM_014", evidence_paths=["factory/evidence/FM_014/report.txt"])

    assert in_progress.status == TaskSpecStatus.IN_PROGRESS
    assert done.status == TaskSpecStatus.DONE
    assert done.evidence_paths == ["factory/evidence/FM_014/report.txt"]
    assert store.get("FM_014").status == TaskSpecStatus.DONE
    assert store.counts() == {"pending": 0, "in_progress": 0, "done": 1, "blocked": 0}


def test_store_blocks_pending_task(tmp_path):
    store = TaskSpecStore(tmp_path / "taskspecs")
    store.enqueue(_task())

    blocked = store.mark_blocked("FM_014", "NO_BUILDER_AVAILABLE")

    assert blocked.status == TaskSpecStatus.BLOCKED
    assert blocked.blocking_reason == "NO_BUILDER_AVAILABLE"
    assert store.counts()["blocked"] == 1


def test_store_blocks_in_progress_task(tmp_path):
    store = TaskSpecStore(tmp_path / "taskspecs")
    store.enqueue(_task())
    store.mark_in_progress("FM_014")

    blocked = store.mark_blocked("FM_014", "VALIDATION_FAILED")

    assert blocked.status == TaskSpecStatus.BLOCKED
    assert blocked.blocking_reason == "VALIDATION_FAILED"


def test_store_rejects_invalid_transitions(tmp_path):
    store = TaskSpecStore(tmp_path / "taskspecs")
    store.enqueue(_task())

    with pytest.raises(ValueError, match="Only in_progress TaskSpec can move to done"):
        store.mark_done("FM_014", evidence_paths=["factory/evidence/FM_014/report.txt"])

    store.mark_in_progress("FM_014")
    store.mark_done("FM_014", evidence_paths=["factory/evidence/FM_014/report.txt"])

    with pytest.raises(ValueError, match="Only pending or in_progress TaskSpec can move to blocked"):
        store.mark_blocked("FM_014", "TOO_LATE")


def test_store_next_pending_returns_sorted_first_task(tmp_path):
    store = TaskSpecStore(tmp_path / "taskspecs")
    store.enqueue(_task("FM_014_B"))
    store.enqueue(_task("FM_014_A"))

    next_task = store.next_pending()

    assert next_task is not None
    assert next_task.task_id == "FM_014_A"


def test_store_list_by_status_and_all(tmp_path):
    store = TaskSpecStore(tmp_path / "taskspecs")
    store.enqueue(_task("FM_014_A"))
    store.enqueue(_task("FM_014_B"))
    store.mark_in_progress("FM_014_A")

    pending = store.list(TaskSpecStatus.PENDING)
    in_progress = store.list("in_progress")
    all_tasks = store.list()

    assert [task.task_id for task in pending] == ["FM_014_B"]
    assert [task.task_id for task in in_progress] == ["FM_014_A"]
    assert [task.task_id for task in all_tasks] == ["FM_014_A", "FM_014_B"]


def test_store_missing_task_raises_file_not_found(tmp_path):
    store = TaskSpecStore(tmp_path / "taskspecs")

    with pytest.raises(FileNotFoundError, match="TaskSpec not found"):
        store.mark_in_progress("missing")
