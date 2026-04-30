import pytest

from factory.core.task_spec import (
    TaskSpec,
    TaskSpecStatus,
    read_task_spec,
    task_spec_from_dict,
    validate_changed_paths,
    write_task_spec,
)


def _task(**overrides):
    data = {
        "task_id": "FM_013",
        "title": "Crear contrato TaskSpec",
        "objective": "Definir contrato soberano de tareas dev",
        "allowed_paths": ["factory/core", "tests/factory"],
        "forbidden_paths": ["app", "data"],
        "acceptance_criteria": ["TaskSpec valida campos obligatorios"],
        "validation_commands": ["PYTHONPATH=. pytest tests/factory/test_task_spec_contract_fm_013.py"],
        "metadata": {"owner": "superowner"},
    }
    data.update(overrides)
    return TaskSpec(**data)


def test_task_spec_serializes_and_roundtrips(tmp_path):
    task = _task()
    path = tmp_path / "FM_013.json"

    written = write_task_spec(task, path)
    loaded = read_task_spec(written)

    assert loaded.task_id == "FM_013"
    assert loaded.status == TaskSpecStatus.PENDING
    assert loaded.allowed_paths == ["factory/core", "tests/factory"]
    assert loaded.metadata["owner"] == "superowner"


def test_task_spec_from_dict_coerces_status():
    task = task_spec_from_dict(
        {
            "task_id": "FM_014",
            "title": "Store",
            "objective": "Crear store",
            "allowed_paths": ["factory/core"],
            "forbidden_paths": ["app"],
            "acceptance_criteria": ["store creado"],
            "validation_commands": ["pytest"],
            "status": "in_progress",
        }
    )

    assert task.status == TaskSpecStatus.IN_PROGRESS


def test_task_spec_requires_core_fields():
    with pytest.raises(ValueError, match="task_id is required"):
        _task(task_id="")

    with pytest.raises(ValueError, match="allowed_paths must not be empty"):
        _task(allowed_paths=[])

    with pytest.raises(ValueError, match="validation_commands must not be empty"):
        _task(validation_commands=[])


def test_done_requires_evidence_paths():
    with pytest.raises(ValueError, match="evidence_paths is required"):
        _task(status=TaskSpecStatus.DONE)

    done = _task(status=TaskSpecStatus.DONE, evidence_paths=["factory/evidence/FM_013/report.txt"])

    assert done.status == TaskSpecStatus.DONE


def test_blocked_requires_blocking_reason():
    with pytest.raises(ValueError, match="blocking_reason is required"):
        _task(status=TaskSpecStatus.BLOCKED)

    blocked = _task(status=TaskSpecStatus.BLOCKED, blocking_reason="TEST_FAILED")

    assert blocked.status == TaskSpecStatus.BLOCKED


def test_with_status_preserves_contract_and_sets_terminal_fields():
    task = _task()

    done = task.with_status(
        TaskSpecStatus.DONE,
        evidence_paths=["factory/evidence/FM_013/report.txt"],
    )
    blocked = task.with_status(
        "blocked",
        blocking_reason="VALIDATION_FAILED",
    )

    assert done.status == TaskSpecStatus.DONE
    assert done.evidence_paths == ["factory/evidence/FM_013/report.txt"]
    assert blocked.status == TaskSpecStatus.BLOCKED
    assert blocked.blocking_reason == "VALIDATION_FAILED"


def test_validate_changed_paths_allows_only_allowed_paths():
    task = _task()

    result = validate_changed_paths(
        task,
        [
            "factory/core/task_spec.py",
            "tests/factory/test_task_spec_contract_fm_013.py",
        ],
    )

    assert result.valid is True
    assert result.errors == []


def test_validate_changed_paths_blocks_forbidden_and_unlisted_paths():
    task = _task()

    result = validate_changed_paths(
        task,
        [
            "app/services/runtime.py",
            "README.md",
        ],
    )

    assert result.valid is False
    assert "FORBIDDEN_PATH_MODIFIED: app/services/runtime.py" in result.errors
    assert "PATH_NOT_ALLOWED: app/services/runtime.py" in result.errors
    assert "PATH_NOT_ALLOWED: README.md" in result.errors
