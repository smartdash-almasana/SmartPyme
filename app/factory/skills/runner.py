from typing import Any

from app.factory.skills.executors import get_executor
from app.factory.skills.registry import SkillDisabledError, SkillNotFoundError, SkillRegistry
from app.factory.skills.validators import validate_schema


def _error_result(skill_id: str, error_code: str, error_message: str) -> dict[str, Any]:
    return {
        "status": "error",
        "skill_id": skill_id,
        "output": None,
        "error_code": error_code,
        "error_message": error_message,
    }


def run_skill(
    skill_id: str,
    payload: dict[str, Any],
    registry: SkillRegistry | None = None,
) -> dict[str, Any]:
    active_registry = registry or SkillRegistry.load_builtin()

    try:
        skill = active_registry.get_skill(skill_id)
    except SkillNotFoundError as exc:
        return _error_result(skill_id, "SKILL_NOT_FOUND", str(exc))
    except SkillDisabledError as exc:
        return _error_result(skill_id, "SKILL_DISABLED", str(exc))

    valid_input, input_error = validate_schema(payload, skill.input_schema, path="input")
    if not valid_input:
        return _error_result(
            skill_id,
            "INPUT_SCHEMA_INVALID",
            input_error or "input schema invalid",
        )

    try:
        executor = get_executor(skill.executor_ref)
        output = executor(payload)
    except Exception as exc:
        return _error_result(skill_id, "EXECUTOR_ERROR", str(exc))

    valid_output, output_error = validate_schema(output, skill.output_schema, path="output")
    if not valid_output:
        return _error_result(
            skill_id,
            "OUTPUT_SCHEMA_INVALID",
            output_error or "output schema invalid",
        )

    return {
        "status": "ok",
        "skill_id": skill_id,
        "output": output,
        "error_code": None,
        "error_message": None,
    }
