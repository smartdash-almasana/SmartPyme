import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.orchestrator.skills.models import SkillSpec
from app.orchestrator.skills.registry import SkillRegistry
from app.orchestrator.skills.runner import run_skill


def test_registry_loads_builtin_skill():
    registry = SkillRegistry.load_builtin()

    skills = registry.list_skills()
    assert len(skills) >= 1
    assert any(skill.skill_id == "echo_skill" for skill in skills)


def test_run_skill_success_with_valid_payload():
    result = run_skill("echo_skill", {"message": "hola"})

    assert result == {
        "status": "ok",
        "skill_id": "echo_skill",
        "output": {"echoed_message": "hola"},
        "error_code": None,
        "error_message": None,
    }


def test_run_skill_fails_when_skill_not_found():
    result = run_skill("unknown_skill", {"message": "hola"})

    assert result["status"] == "error"
    assert result["skill_id"] == "unknown_skill"
    assert result["output"] is None
    assert result["error_code"] == "SKILL_NOT_FOUND"


def test_run_skill_fails_when_input_schema_invalid():
    result = run_skill("echo_skill", {"message": 123})

    assert result["status"] == "error"
    assert result["skill_id"] == "echo_skill"
    assert result["output"] is None
    assert result["error_code"] == "INPUT_SCHEMA_INVALID"


def test_run_skill_fails_when_executor_output_schema_invalid():
    registry = SkillRegistry.load_builtin()
    broken = SkillSpec(
        skill_id="broken_echo_skill",
        name="Echo roto",
        version="1.0.0",
        input_schema={
            "type": "object",
            "required": ["message"],
            "properties": {"message": {"type": "string"}},
        },
        output_schema={
            "type": "object",
            "required": ["echoed_message"],
            "properties": {"echoed_message": {"type": "string"}},
        },
        validator_ref=None,
        executor_ref="builtin.invalid_output",
        accuracy_score=1.0,
        enabled=True,
    )
    registry.set_skill(broken)

    result = run_skill("broken_echo_skill", {"message": "hola"}, registry=registry)

    assert result["status"] == "error"
    assert result["skill_id"] == "broken_echo_skill"
    assert result["output"] is None
    assert result["error_code"] == "OUTPUT_SCHEMA_INVALID"


def test_run_skill_fails_when_skill_disabled():
    registry = SkillRegistry.load_builtin()
    disabled = SkillSpec(
        skill_id="disabled_echo_skill",
        name="Echo deshabilitado",
        version="1.0.0",
        input_schema={
            "type": "object",
            "required": ["message"],
            "properties": {"message": {"type": "string"}},
        },
        output_schema={
            "type": "object",
            "required": ["echoed_message"],
            "properties": {"echoed_message": {"type": "string"}},
        },
        validator_ref=None,
        executor_ref="builtin.echo",
        accuracy_score=1.0,
        enabled=False,
    )
    registry.set_skill(disabled)

    result = run_skill("disabled_echo_skill", {"message": "hola"}, registry=registry)

    assert result["status"] == "error"
    assert result["skill_id"] == "disabled_echo_skill"
    assert result["output"] is None
    assert result["error_code"] == "SKILL_DISABLED"
