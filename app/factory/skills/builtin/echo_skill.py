from app.factory.skills.models import SkillSpec


def get_builtin_skills() -> list[SkillSpec]:
    echo_input_schema = {
        "type": "object",
        "required": ["message"],
        "properties": {
            "message": {"type": "string"},
        },
    }
    echo_output_schema = {
        "type": "object",
        "required": ["echoed_message"],
        "properties": {
            "echoed_message": {"type": "string"},
        },
    }

    return [
        SkillSpec(
            skill_id="echo_skill",
            name="Eco mínimo",
            version="1.0.0",
            input_schema=echo_input_schema,
            output_schema=echo_output_schema,
            validator_ref=None,
            executor_ref="builtin.echo",
            accuracy_score=1.0,
            enabled=True,
        )
    ]
