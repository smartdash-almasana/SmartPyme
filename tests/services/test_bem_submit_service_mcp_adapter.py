from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from app.repositories.bem_run_repository import BemRunRepository
from app.services.bem_mcp_submit_adapter import BemMcpSubmitAdapter
from app.services.bem_submit_service import BemSubmitService


class _FakeMcpClient:
    def __init__(self, result: dict) -> None:
        self.result = result
        self.last_kwargs: dict | None = None

    def call_tool(self, tool_name: str, **kwargs):
        self.last_kwargs = kwargs
        return self.result


def _now_provider_factory():
    values = [
        datetime(2026, 5, 10, 12, 0, 0, tzinfo=timezone.utc),
        datetime(2026, 5, 10, 12, 1, 0, tzinfo=timezone.utc),
    ]

    def _provider() -> datetime:
        if values:
            return values.pop(0)
        return datetime(2026, 5, 10, 12, 1, 0, tzinfo=timezone.utc)

    return _provider


def test_mcp_adapter_response_persists_completed_run(tmp_path: Path):
    mcp = _FakeMcpClient({"status": "COMPLETED", "response_payload": {"provider_run_id": "mcp-1"}})
    adapter = BemMcpSubmitAdapter(mcp)
    repo = BemRunRepository(tmp_path / "bem_runs.db")
    service = BemSubmitService(
        bem_client=adapter,
        bem_run_repository=repo,
        now_provider=_now_provider_factory(),
        run_id_provider=lambda: "run-mcp-1",
    )

    run = service.submit("tenant-mcp", "wf-mcp", {"x": 1})

    assert run.tenant_id == "tenant-mcp"
    assert run.status == "COMPLETED"
    assert run.response_payload == {"provider_run_id": "mcp-1"}
    assert mcp.last_kwargs is not None
    assert mcp.last_kwargs["tenant_id"] == "tenant-mcp"
    assert mcp.last_kwargs["workflow_id"] == "wf-mcp"


def test_mcp_adapter_error_persists_failed_run(tmp_path: Path):
    mcp = _FakeMcpClient(
        {"status": "REJECTED", "error_type": "BEM_UPSTREAM_ERROR", "reason": "mcp-down"}
    )
    adapter = BemMcpSubmitAdapter(mcp)
    repo = BemRunRepository(tmp_path / "bem_runs.db")
    service = BemSubmitService(
        bem_client=adapter,
        bem_run_repository=repo,
        now_provider=_now_provider_factory(),
        run_id_provider=lambda: "run-mcp-fail",
    )

    with pytest.raises(RuntimeError, match="BEM_UPSTREAM_ERROR: mcp-down"):
        service.submit("tenant-mcp", "wf-mcp", {"x": 1})

    run = repo.get_by_run_id("tenant-mcp", "run-mcp-fail")
    assert run is not None
    assert run.status == "FAILED"
