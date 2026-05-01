import pytest

from factory.core.task_spec_templates import (
    build_task_spec_from_template,
    get_task_spec_template,
    list_template_names,
)


def test_list_template_names_contains_required_templates():
    assert list_template_names() == [
        "audit_only",
        "code_change",
        "docs_change",
        "refactor",
        "test_fix",
    ]


def test_build_code_change_template_creates_taskspec():
    task = build_task_spec_from_template(
        "code_change",
        "Crear módulo de cola",
        task_id="FM_022_CODE",
        metadata={"owner": "superowner"},
    )

    assert task.task_id == "FM_022_CODE"
    assert task.title == "Code change: Crear módulo de cola"
    assert task.objective == "Crear módulo de cola"
    assert task.allowed_paths == ["factory", "tests/factory"]
    assert "app" in task.forbidden_paths
    assert task.metadata["template"] == "code_change"
    assert task.metadata["owner"] == "superowner"
    assert task.validation_commands == ["PYTHONPATH=. pytest tests/factory"]


def test_docs_change_allows_docs_without_app_runtime():
    task = build_task_spec_from_template(
        "docs_change",
        "Actualizar documentación",
        task_id="FM_022_DOCS",
    )

    assert "docs" in task.allowed_paths
    assert "app" in task.forbidden_paths
    assert task.metadata["template"] == "docs_change"


def test_audit_only_sets_read_only_metadata():
    task = build_task_spec_from_template("audit_only", "Auditar frontera", task_id="FM_022_AUDIT")

    assert task.metadata["template"] == "audit_only"
    assert task.metadata["mode"] == "read_only_audit"
    assert "docs" in task.allowed_paths


def test_refactor_has_boundary_validation_command():
    task = build_task_spec_from_template(
        "refactor",
        "Reducir duplicación",
        task_id="FM_022_REFACTOR",
    )

    assert any(
        "test_factory_boundary_no_app_imports_fm_012.py" in command
        for command in task.validation_commands
    )
    assert "app" in task.forbidden_paths


def test_test_fix_template_keeps_scope_in_factory_tests():
    task = build_task_spec_from_template("test_fix", "Corregir test runner", task_id="FM_022_TEST")

    assert task.allowed_paths == ["tests/factory", "factory"]
    assert task.metadata["template"] == "test_fix"


def test_unknown_template_raises_clear_error():
    with pytest.raises(ValueError, match="Unknown TaskSpec template"):
        get_task_spec_template("unknown")


def test_blank_objective_is_rejected():
    with pytest.raises(ValueError, match="objective is required"):
        build_task_spec_from_template("code_change", "   ")


def test_task_id_factory_can_be_injected():
    task = build_task_spec_from_template(
        "code_change",
        "Objetivo",
        task_id_factory=lambda template_name: f"custom-{template_name}",
    )

    assert task.task_id == "custom-code_change"
