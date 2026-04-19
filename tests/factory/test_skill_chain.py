import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.factory.chain.models import ChainStep
from app.factory.chain.service import run_skill_chain


def test_skill_chain_success_two_steps_echo_then_wrap():
    steps = [
        ChainStep(step_id="step-1", skill_id="echo_skill"),
        ChainStep(step_id="step-2", skill_id="wrap_echo_skill"),
    ]

    result = run_skill_chain(steps, initial_payload={"message": "hola"})

    assert result.status == "ok"
    assert result.completed_steps == ["step-1", "step-2"]
    assert result.failed_step_id is None
    assert result.error_code is None
    assert result.error_message is None


def test_skill_chain_empty_returns_error():
    result = run_skill_chain([], initial_payload={"message": "hola"})

    assert result.status == "error"
    assert result.completed_steps == []
    assert result.final_output is None
    assert result.failed_step_id is None
    assert result.error_code == "CHAIN_EMPTY"


def test_skill_chain_blocks_on_unknown_skill_in_second_step():
    steps = [
        ChainStep(step_id="step-1", skill_id="echo_skill"),
        ChainStep(step_id="step-2", skill_id="unknown_skill"),
    ]

    result = run_skill_chain(steps, initial_payload={"message": "hola"})

    assert result.status == "blocked"
    assert result.completed_steps == ["step-1"]
    assert result.final_output is None
    assert result.failed_step_id == "step-2"
    assert result.error_code == "SKILL_NOT_FOUND"


def test_skill_chain_blocks_when_second_step_receives_invalid_payload():
    steps = [
        ChainStep(step_id="step-1", skill_id="wrap_echo_skill"),
        ChainStep(step_id="step-2", skill_id="wrap_echo_skill"),
    ]

    result = run_skill_chain(steps, initial_payload={"echoed_message": "hola"})

    assert result.status == "blocked"
    assert result.completed_steps == ["step-1"]
    assert result.final_output is None
    assert result.failed_step_id == "step-2"
    assert result.error_code == "INPUT_SCHEMA_INVALID"


def test_completed_steps_only_include_successful_steps_before_failure():
    steps = [
        ChainStep(step_id="step-1", skill_id="echo_skill"),
        ChainStep(step_id="step-2", skill_id="unknown_skill"),
        ChainStep(step_id="step-3", skill_id="wrap_echo_skill"),
    ]

    result = run_skill_chain(steps, initial_payload={"message": "hola"})

    assert result.status == "blocked"
    assert result.completed_steps == ["step-1"]
    assert result.failed_step_id == "step-2"


def test_final_output_equals_last_step_output_on_success():
    steps = [
        ChainStep(step_id="step-1", skill_id="echo_skill"),
        ChainStep(step_id="step-2", skill_id="wrap_echo_skill"),
    ]

    result = run_skill_chain(steps, initial_payload={"message": "hola"})

    assert result.status == "ok"
    assert result.final_output == {"final_message": "wrapped: hola"}
