import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.orchestrator.multiagent.models import DirectorRequest
from app.orchestrator.multiagent.service import run_multiagent_flow


def test_multiagent_valid_request_runs_full_flow_and_finishes_done():
    request = DirectorRequest(
        objetivo="Responder eco envuelto",
        payload_inicial={"message": "hola"},
        flags={"needs_echo": True},
    )

    result = run_multiagent_flow(request)

    assert result["status"] == "done"
    assert result["plan_status"] == "ok"
    assert result["final_state"] == "AFTER_WRAP"


def test_multiagent_empty_objetivo_blocks_in_director_before_execution():
    request = DirectorRequest(
        objetivo="   ",
        payload_inicial={"message": "hola"},
        flags={"needs_echo": True},
    )

    result = run_multiagent_flow(request)

    assert result["status"] == "blocked"
    assert result["plan_status"] == "blocked"
    assert result["executed_skills"] == []
    assert result["error_code"] == "OBJETIVO_INVALIDO"


def test_multiagent_blocked_plan_never_reaches_execution(monkeypatch):
    import app.orchestrator.multiagent.service as multiagent_service

    def fail_if_called(*_args, **_kwargs):
        raise AssertionError("execute_plan no debe llamarse con plan bloqueado")

    monkeypatch.setattr(multiagent_service, "execute_plan", fail_if_called)

    request = DirectorRequest(
        objetivo="",
        payload_inicial={},
        flags={},
    )
    result = run_multiagent_flow(request)

    assert result["status"] == "blocked"
    assert result["error_code"] == "OBJETIVO_INVALIDO"


def test_multiagent_executed_skills_preserves_order_from_loop():
    request = DirectorRequest(
        objetivo="Orden de skills",
        payload_inicial={"message": "hola"},
        flags={"needs_echo": True},
    )

    result = run_multiagent_flow(request)

    assert result["status"] == "done"
    assert result["executed_skills"] == ["echo_skill", "wrap_echo_skill"]


def test_multiagent_final_output_equals_loop_final_output():
    request = DirectorRequest(
        objetivo="Output final",
        payload_inicial={"message": "hola"},
        flags={"needs_echo": True},
    )

    result = run_multiagent_flow(request)

    assert result["status"] == "done"
    assert result["final_output"] == {"final_message": "wrapped: hola"}


def test_multiagent_propagates_loop_errors_through_facade():
    request = DirectorRequest(
        objetivo="Debe fallar por schema",
        payload_inicial={"message": 123},
        flags={"needs_echo": True},
    )

    result = run_multiagent_flow(request)

    assert result["status"] == "blocked"
    assert result["plan_status"] == "ok"
    assert result["error_code"] == "INPUT_SCHEMA_INVALID"
