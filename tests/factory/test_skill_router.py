import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.factory.router.models import RouterContext
from app.factory.router.service import decide_next_skill


def test_created_with_needs_echo_routes_to_echo_skill():
    context = RouterContext(current_state="CREATED", flags={"needs_echo": True}, last_output={})

    decision = decide_next_skill(context)

    assert decision.status == "ok"
    assert decision.next_skill_id == "echo_skill"
    assert decision.error_code is None


def test_after_echo_with_echoed_message_routes_to_wrap_echo_skill():
    context = RouterContext(
        current_state="AFTER_ECHO",
        flags={},
        last_output={"echoed_message": "hola"},
    )

    decision = decide_next_skill(context)

    assert decision.status == "ok"
    assert decision.next_skill_id == "wrap_echo_skill"
    assert decision.error_code is None


def test_after_wrap_returns_done_with_no_next_skill():
    context = RouterContext(current_state="AFTER_WRAP", flags={}, last_output={})

    decision = decide_next_skill(context)

    assert decision.status == "done"
    assert decision.next_skill_id is None
    assert decision.error_code is None


def test_unknown_state_returns_blocked_with_no_route_found():
    context = RouterContext(current_state="UNKNOWN", flags={}, last_output={})

    decision = decide_next_skill(context)

    assert decision.status == "blocked"
    assert decision.next_skill_id is None
    assert decision.error_code == "NO_ROUTE_FOUND"


def test_missing_required_flag_returns_blocked():
    context = RouterContext(current_state="CREATED", flags={}, last_output={})

    decision = decide_next_skill(context)

    assert decision.status == "blocked"
    assert decision.next_skill_id is None
    assert decision.error_code == "NO_ROUTE_FOUND"


def test_after_echo_without_echoed_message_returns_blocked():
    context = RouterContext(current_state="AFTER_ECHO", flags={}, last_output={})

    decision = decide_next_skill(context)

    assert decision.status == "blocked"
    assert decision.next_skill_id is None
    assert decision.error_code == "NO_ROUTE_FOUND"
