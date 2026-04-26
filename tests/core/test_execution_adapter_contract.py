import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.contracts.execution_adapter_contract import (
    ExecutionAdapter,
    ExecutionAdapterResult,
)
from app.contracts.action_contract import ActionProposal


# ── minimal concrete adapter for testing ─────────────────────────────────────

class _MockAdapter(ExecutionAdapter):
    """Minimal concrete adapter that always returns 'executed'."""

    def __init__(self, status: str = "executed", message: str = "OK") -> None:
        self._status = status
        self._message = message

    @property
    def adapter_id(self) -> str:
        return "mock"

    def execute(self, proposal: Any) -> ExecutionAdapterResult:
        return ExecutionAdapterResult(
            adapter_id=self.adapter_id,
            action_id=proposal.action_id,
            status=self._status,
            message=self._message,
        )


def _proposal(action_id: str = "act-1") -> ActionProposal:
    return ActionProposal(
        action_id=action_id,
        source_id="src-1",
        source_type="finding",
        title="T",
        description="D",
        recommended_action="R",
        status="approved",
    )


# ── ExecutionAdapterResult ────────────────────────────────────────────────────

def test_execution_adapter_result_is_dataclass():
    from dataclasses import fields
    field_names = {f.name for f in fields(ExecutionAdapterResult)}
    assert {"adapter_id", "action_id", "status", "message", "traceable_origin"}.issubset(field_names)


def test_execution_adapter_result_is_frozen():
    result = ExecutionAdapterResult(
        adapter_id="mock", action_id="act-1",
        status="executed", message="OK",
    )
    try:
        object.__setattr__(result, "status", "failed")
        assert False, "Should have raised FrozenInstanceError"
    except Exception:
        pass


def test_execution_adapter_result_traceable_origin_defaults_to_empty_dict():
    result = ExecutionAdapterResult(
        adapter_id="mock", action_id="act-1",
        status="executed", message="OK",
    )
    assert result.traceable_origin == {}


def test_execution_adapter_result_valid_statuses():
    for status in ("executed", "blocked", "failed"):
        r = ExecutionAdapterResult(
            adapter_id="mock", action_id="act-1",
            status=status, message="msg",
        )
        assert r.status == status


# ── ExecutionAdapter ABC ──────────────────────────────────────────────────────

def test_execution_adapter_is_abstract():
    import inspect
    assert inspect.isabstract(ExecutionAdapter)


def test_execution_adapter_concrete_subclass_works():
    adapter = _MockAdapter()
    assert adapter.adapter_id == "mock"


def test_execution_adapter_execute_returns_adapter_result():
    adapter = _MockAdapter()
    result = adapter.execute(_proposal())
    assert isinstance(result, ExecutionAdapterResult)


def test_execution_adapter_execute_result_contains_action_id():
    adapter = _MockAdapter()
    result = adapter.execute(_proposal("act-xyz"))
    assert result.action_id == "act-xyz"


def test_execution_adapter_execute_result_contains_adapter_id():
    adapter = _MockAdapter()
    result = adapter.execute(_proposal())
    assert result.adapter_id == "mock"


# ── adapter_id property ───────────────────────────────────────────────────────

def test_execution_adapter_subclass_must_implement_adapter_id():
    class _Incomplete(ExecutionAdapter):
        def execute(self, proposal: Any) -> ExecutionAdapterResult:
            return ExecutionAdapterResult(
                adapter_id="x", action_id="y", status="executed", message="ok"
            )

    try:
        _Incomplete()
        assert False, "Should have raised TypeError for missing adapter_id"
    except TypeError:
        pass
