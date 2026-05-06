"""Tests del runner LangGraph mínimo de factory_v2."""

import pytest

from factory_v2.contracts import GraphState, TaskSpecV2
from factory_v2.langgraph_runner import run_with_langgraph
from factory_v2.sandbox import FakeSandboxAdapter


pytest.importorskip("langgraph")


def test_run_with_langgraph_executes_deterministic_graph():
    """run_with_langgraph envuelve run_graph sin reemplazarlo ni usar agentes reales."""
    state = run_with_langgraph(
        TaskSpecV2(
            task_id="test_langgraph_runner",
            objective="validar runner LangGraph mínimo",
        ),
        sandbox_adapter=FakeSandboxAdapter(),
    )

    assert isinstance(state, GraphState)
    assert state.halted is False
    assert state.audit_result is not None
    assert state.audit_result.status.value == "PASS"
    assert state.implement_result is not None
    assert state.implement_result.status.value == "PASS"
    assert state.sandbox_result is not None
    assert state.sandbox_result.status.value == "PASS"
    assert state.review_result is not None
    assert state.review_result.status.value == "PASS"
