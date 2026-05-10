from __future__ import annotations

import pytest

from app.services.bem_mcp_submit_adapter import BemMcpSubmitAdapter


class _FakeMcpClient:
    def __init__(self, result: dict) -> None:
        self.result = result
        self.last_tool_name: str | None = None
        self.last_kwargs: dict | None = None

    def call_tool(self, tool_name: str, **kwargs):
        self.last_tool_name = tool_name
        self.last_kwargs = kwargs
        return self.result


def test_payload_and_workflow_reach_mcp_intact():
    fake = _FakeMcpClient({"status": "COMPLETED", "response_payload": {"ok": True}})
    adapter = BemMcpSubmitAdapter(fake)
    payload = {"x": 1, "nested": {"y": "z"}}

    result = adapter.submit_payload("wf-1", payload, tenant_id="tenant-a")

    assert result == {"ok": True}
    assert fake.last_tool_name == "bem_submit_workflow"
    assert fake.last_kwargs == {
        "tenant_id": "tenant-a",
        "workflow_id": "wf-1",
        "payload": payload,
    }


def test_call_reference_id_forwarded():
    fake = _FakeMcpClient({"status": "COMPLETED", "response_payload": {"ok": True}})
    adapter = BemMcpSubmitAdapter(fake)

    adapter.submit_payload(
        "wf-1",
        {"x": 1},
        tenant_id="tenant-a",
        call_reference_id="ref-1",
    )

    assert fake.last_kwargs is not None
    assert fake.last_kwargs["call_reference_id"] == "ref-1"


def test_mcp_error_maps_to_runtime_error():
    fake = _FakeMcpClient(
        {"status": "REJECTED", "error_type": "BEM_UPSTREAM_ERROR", "reason": "timeout"}
    )
    adapter = BemMcpSubmitAdapter(fake)

    with pytest.raises(RuntimeError, match="BEM_UPSTREAM_ERROR: timeout"):
        adapter.submit_payload("wf-1", {"x": 1}, tenant_id="tenant-a")
