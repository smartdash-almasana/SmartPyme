from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable
from uuid import uuid4

from factory.core.task_spec import TaskSpec

TaskIdFactory = Callable[[str], str]


@dataclass(frozen=True)
class TaskSpecTemplate:
    name: str
    title_prefix: str
    allowed_paths: list[str]
    forbidden_paths: list[str]
    acceptance_criteria: list[str]
    validation_commands: list[str]
    metadata: dict = field(default_factory=dict)

    def build(
        self,
        objective: str,
        *,
        task_id: str | None = None,
        task_id_factory: TaskIdFactory | None = None,
        metadata: dict | None = None,
    ) -> TaskSpec:
        normalized_objective = _require_objective(objective)
        resolved_task_id = task_id or (task_id_factory or default_task_id_factory)(self.name)
        merged_metadata = dict(self.metadata)
        merged_metadata.update(metadata or {})
        merged_metadata["template"] = self.name
        return TaskSpec(
            task_id=resolved_task_id,
            title=f"{self.title_prefix}: {_title_from_objective(normalized_objective)}",
            objective=normalized_objective,
            allowed_paths=list(self.allowed_paths),
            forbidden_paths=list(self.forbidden_paths),
            acceptance_criteria=list(self.acceptance_criteria),
            validation_commands=list(self.validation_commands),
            metadata=merged_metadata,
        )


TEMPLATES: dict[str, TaskSpecTemplate] = {
    "code_change": TaskSpecTemplate(
        name="code_change",
        title_prefix="Code change",
        allowed_paths=["factory", "tests/factory"],
        forbidden_paths=["app", "data", ".git"],
        acceptance_criteria=[
            "El cambio queda limitado a factory/* y tests/factory/*.",
            "Los tests relevantes pasan.",
            "Se genera evidencia verificable.",
        ],
        validation_commands=[
            "PYTHONPATH=. pytest tests/factory"
        ],
    ),
    "docs_change": TaskSpecTemplate(
        name="docs_change",
        title_prefix="Docs change",
        allowed_paths=["docs", "factory", "tests/factory"],
        forbidden_paths=["app", "data", ".git"],
        acceptance_criteria=[
            "La documentación se actualiza sin tocar runtime app/*.",
            "La evidencia referencia los archivos documentales modificados.",
        ],
        validation_commands=[
            "PYTHONPATH=. pytest tests/factory/test_factory_boundary_no_app_imports_fm_012.py"
        ],
    ),
    "test_fix": TaskSpecTemplate(
        name="test_fix",
        title_prefix="Test fix",
        allowed_paths=["tests/factory", "factory"],
        forbidden_paths=["app", "data", ".git"],
        acceptance_criteria=[
            "El test fallido queda reproducido y corregido.",
            "No se relajan asserts sin justificación en evidencia.",
            "La suite factory relevante queda verde.",
        ],
        validation_commands=[
            "PYTHONPATH=. pytest tests/factory"
        ],
    ),
    "refactor": TaskSpecTemplate(
        name="refactor",
        title_prefix="Refactor",
        allowed_paths=["factory", "tests/factory"],
        forbidden_paths=["app", "data", ".git"],
        acceptance_criteria=[
            "El comportamiento externo se preserva.",
            "Los tests existentes siguen verdes.",
            "El refactor mantiene el desacople factory/* -> no app/*.",
        ],
        validation_commands=[
            "PYTHONPATH=. pytest tests/factory",
            "PYTHONPATH=. pytest tests/factory/test_factory_boundary_no_app_imports_fm_012.py",
        ],
    ),
    "audit_only": TaskSpecTemplate(
        name="audit_only",
        title_prefix="Audit only",
        allowed_paths=["factory", "tests/factory", "docs"],
        forbidden_paths=["app", "data", ".git"],
        acceptance_criteria=[
            "No se modifican archivos productivos.",
            "El resultado queda expresado como evidencia de auditoría.",
            "Toda conclusión incluye estado VALIDADO o NO_VALIDADO.",
        ],
        validation_commands=[
            "PYTHONPATH=. pytest tests/factory/test_factory_boundary_no_app_imports_fm_012.py"
        ],
        metadata={"mode": "read_only_audit"},
    ),
}


def list_template_names() -> list[str]:
    return sorted(TEMPLATES.keys())


def get_task_spec_template(name: str) -> TaskSpecTemplate:
    try:
        return TEMPLATES[name]
    except KeyError as exc:
        raise ValueError(f"Unknown TaskSpec template: {name}") from exc


def build_task_spec_from_template(
    template_name: str,
    objective: str,
    *,
    task_id: str | None = None,
    task_id_factory: TaskIdFactory | None = None,
    metadata: dict | None = None,
) -> TaskSpec:
    return get_task_spec_template(template_name).build(
        objective,
        task_id=task_id,
        task_id_factory=task_id_factory,
        metadata=metadata,
    )


def default_task_id_factory(template_name: str) -> str:
    return f"{template_name}-{uuid4()}"


def _require_objective(objective: str) -> str:
    if not isinstance(objective, str) or not objective.strip():
        raise ValueError("objective is required")
    return objective.strip()


def _title_from_objective(objective: str) -> str:
    return objective.split("\n", maxsplit=1)[0][:80]
