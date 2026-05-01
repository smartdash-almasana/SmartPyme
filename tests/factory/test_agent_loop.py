import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.factory.agent_loop.models import AgentLoopContext
from app.factory.agent_loop.service import run_agent_loop
from app.orchestrator.router.models import RoutingDecision


def test_agent_loop_created_needs_echo_completes_full_flow():
    context = AgentLoopContext(
        current_state="CREATED",
        flags={"needs_echo": True},
        payload={"message": "hola"},
        last_output={},
        executed_skills=[],
    )

    result = run_agent_loop(context)

    assert result.status == "done"
    assert result.executed_skills == ["echo_skill", "wrap_echo_skill"]
    assert result.final_state == "AFTER_WRAP"
    assert result.final_output == {"final_message": "wrapped: hola"}
    assert result.error_code is None
    assert result.error_message is None


def test_agent_loop_unknown_route_blocks_immediately():
    context = AgentLoopContext(
        current_state="UNKNOWN",
        flags={},
        payload={},
        last_output={},
        executed_skills=[],
    )

    result = run_agent_loop(context)

    assert result.status == "blocked"
    assert result.executed_skills == []
    assert result.error_code == "NO_ROUTE_FOUND"


def test_agent_loop_skill_execution_error_blocks_immediately():
    context = AgentLoopContext(
        current_state="CREATED",
        flags={"needs_echo": True},
        payload={"message": 123},
        last_output={},
        executed_skills=[],
    )

    result = run_agent_loop(context)

    assert result.status == "blocked"
    assert result.executed_skills == []
    assert result.error_code == "INPUT_SCHEMA_INVALID"


def test_agent_loop_executed_skills_preserves_order():
    context = AgentLoopContext(
        current_state="CREATED",
        flags={"needs_echo": True},
        payload={"message": "hola"},
        last_output={},
        executed_skills=[],
    )

    result = run_agent_loop(context)

    assert result.executed_skills == ["echo_skill", "wrap_echo_skill"]


def test_agent_loop_final_output_equals_last_successful_output():
    context = AgentLoopContext(
        current_state="CREATED",
        flags={"needs_echo": True},
        payload={"message": "hola"},
        last_output={},
        executed_skills=[],
    )

    result = run_agent_loop(context)

    assert result.status == "done"
    assert result.final_output == {"final_message": "wrapped: hola"}


def test_agent_loop_max_steps_safeguard_works(monkeypatch):
    import app.factory.agent_loop.service as loop_service

    def always_route_echo(_):
        return RoutingDecision(
            status="ok",
            next_skill_id="echo_skill",
            reason="forced",
            error_code=None,
        )

    def always_ok_run_skill(*_args, **_kwargs):
        return {
            "status": "ok",
            "skill_id": "echo_skill",
            "output": {"message": "hola"},
            "error_code": None,
            "error_message": None,
        }

    monkeypatch.setattr(loop_service, "decide_next_skill", always_route_echo)
    monkeypatch.setattr(loop_service, "run_skill", always_ok_run_skill)

    context = AgentLoopContext(
        current_state="CREATED",
        flags={"needs_echo": True},
        payload={"message": "hola"},
        last_output={},
        executed_skills=[],
    )

    result = run_agent_loop(context)

    assert result.status == "blocked"
    assert result.error_code == "MAX_STEPS_EXCEEDED"
    assert len(result.executed_skills) == 10
