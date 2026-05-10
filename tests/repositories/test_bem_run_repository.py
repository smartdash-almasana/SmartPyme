from __future__ import annotations

import pytest

from app.contracts.bem_runs import BemRunRecord
from app.repositories.bem_run_repository import BemRunRepository


def _record(
    *,
    tenant_id: str = "tenant-a",
    run_id: str = "run-1",
    workflow_id: str = "wf-1",
    status: str = "SUBMITTED",
    request_payload: dict | None = None,
) -> BemRunRecord:
    if request_payload is None:
        request_payload = {"amount": 123}
    return BemRunRecord(
        tenant_id=tenant_id,
        run_id=run_id,
        workflow_id=workflow_id,
        status=status,
        request_payload=request_payload,
        response_payload=None,
        created_at="2026-05-10T12:00:00+00:00",
        updated_at=None,
        error_message=None,
    )


def test_create_valido(tmp_path):
    repo = BemRunRepository(tmp_path / "bem_runs.db")
    repo.create(_record())
    assert repo.get_by_run_id("tenant-a", "run-1") is not None


def test_get_valido(tmp_path):
    repo = BemRunRepository(tmp_path / "bem_runs.db")
    repo.create(_record())
    run = repo.get_by_run_id("tenant-a", "run-1")
    assert run is not None
    assert run.workflow_id == "wf-1"
    assert run.status == "SUBMITTED"


def test_list_tenant(tmp_path):
    repo = BemRunRepository(tmp_path / "bem_runs.db")
    repo.create(_record(run_id="run-1"))
    repo.create(_record(run_id="run-2"))
    runs = repo.list_by_tenant("tenant-a")
    assert len(runs) == 2
    assert {item.run_id for item in runs} == {"run-1", "run-2"}


def test_tenant_isolation(tmp_path):
    repo = BemRunRepository(tmp_path / "bem_runs.db")
    repo.create(_record(tenant_id="tenant-a", run_id="shared-run"))
    repo.create(_record(tenant_id="tenant-b", run_id="shared-run"))
    assert repo.get_by_run_id("tenant-a", "shared-run") is not None
    assert repo.get_by_run_id("tenant-b", "shared-run") is not None
    assert len(repo.list_by_tenant("tenant-a")) == 1
    assert len(repo.list_by_tenant("tenant-b")) == 1


def test_mark_completed(tmp_path):
    repo = BemRunRepository(tmp_path / "bem_runs.db")
    repo.create(_record())
    repo.mark_completed(
        "tenant-a",
        "run-1",
        {"accepted": True, "provider_run_id": "bem-1"},
        "2026-05-10T12:05:00+00:00",
    )
    run = repo.get_by_run_id("tenant-a", "run-1")
    assert run is not None
    assert run.status == "COMPLETED"
    assert run.response_payload == {"accepted": True, "provider_run_id": "bem-1"}
    assert run.updated_at == "2026-05-10T12:05:00+00:00"
    assert run.error_message is None


def test_mark_failed(tmp_path):
    repo = BemRunRepository(tmp_path / "bem_runs.db")
    repo.create(_record())
    repo.mark_failed("tenant-a", "run-1", "timeout", "2026-05-10T12:06:00+00:00")
    run = repo.get_by_run_id("tenant-a", "run-1")
    assert run is not None
    assert run.status == "FAILED"
    assert run.error_message == "timeout"
    assert run.updated_at == "2026-05-10T12:06:00+00:00"


def test_tenant_vacio():
    with pytest.raises(ValueError, match="tenant_id"):
        _record(tenant_id="")


def test_run_id_vacio():
    with pytest.raises(ValueError, match="run_id"):
        _record(run_id="")


def test_workflow_id_vacio():
    with pytest.raises(ValueError, match="workflow_id"):
        _record(workflow_id="")


def test_request_payload_vacio():
    with pytest.raises(ValueError, match="request_payload"):
        _record(request_payload={})
