from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from app.repositories.bem_run_repository import BemRunRepository
from app.services.bem_submit_service import BemSubmitService


class _FakeBemClientOk:
    def __init__(self) -> None:
        self.last_workflow_id: str | None = None
        self.last_payload: dict | None = None

    def submit_payload(self, workflow_id: str, payload: dict):
        self.last_workflow_id = workflow_id
        self.last_payload = payload
        return {"provider_run_id": "bem-1", "accepted": True}


class _FakeBemClientFail:
    def submit_payload(self, workflow_id: str, payload: dict):
        raise RuntimeError("bem unavailable")


def _now_provider_factory():
    values = [
        datetime(2026, 5, 10, 12, 0, 0, tzinfo=timezone.utc),
        datetime(2026, 5, 10, 12, 1, 0, tzinfo=timezone.utc),
        datetime(2026, 5, 10, 12, 2, 0, tzinfo=timezone.utc),
    ]

    def _provider() -> datetime:
        if values:
            return values.pop(0)
        return datetime(2026, 5, 10, 12, 2, 0, tzinfo=timezone.utc)

    return _provider


def test_submit_exitoso_crea_run_completed(tmp_path: Path):
    repo = BemRunRepository(tmp_path / "bem_runs.db")
    client = _FakeBemClientOk()
    service = BemSubmitService(
        bem_client=client,
        bem_run_repository=repo,
        now_provider=_now_provider_factory(),
        run_id_provider=lambda: "run-det-1",
    )

    run = service.submit("tenant-a", "wf-1", {"tenant_id": "tenant-a", "payload": {"x": 1}})

    assert run.status == "COMPLETED"
    assert run.run_id == "run-det-1"
    assert run.workflow_id == "wf-1"


def test_response_payload_persistido(tmp_path: Path):
    repo = BemRunRepository(tmp_path / "bem_runs.db")
    service = BemSubmitService(
        bem_client=_FakeBemClientOk(),
        bem_run_repository=repo,
        now_provider=_now_provider_factory(),
        run_id_provider=lambda: "run-det-2",
    )

    run = service.submit("tenant-a", "wf-1", {"a": 1})

    assert run.response_payload == {"provider_run_id": "bem-1", "accepted": True}


def test_client_recibe_workflow_id_y_payload(tmp_path: Path):
    repo = BemRunRepository(tmp_path / "bem_runs.db")
    client = _FakeBemClientOk()
    payload = {"k": "v"}
    service = BemSubmitService(
        bem_client=client,
        bem_run_repository=repo,
        now_provider=_now_provider_factory(),
        run_id_provider=lambda: "run-det-3",
    )

    service.submit("tenant-a", "wf-xyz", payload)

    assert client.last_workflow_id == "wf-xyz"
    assert client.last_payload == payload


def test_fallo_client_marca_failed(tmp_path: Path):
    repo = BemRunRepository(tmp_path / "bem_runs.db")
    service = BemSubmitService(
        bem_client=_FakeBemClientFail(),
        bem_run_repository=repo,
        now_provider=_now_provider_factory(),
        run_id_provider=lambda: "run-det-4",
    )

    with pytest.raises(RuntimeError, match="bem unavailable"):
        service.submit("tenant-a", "wf-1", {"x": 1})

    run = repo.get_by_run_id("tenant-a", "run-det-4")
    assert run is not None
    assert run.status == "FAILED"
    assert run.error_message == "bem unavailable"


def test_tenant_vacio(tmp_path: Path):
    repo = BemRunRepository(tmp_path / "bem_runs.db")
    service = BemSubmitService(
        bem_client=_FakeBemClientOk(),
        bem_run_repository=repo,
        now_provider=_now_provider_factory(),
        run_id_provider=lambda: "run-det-5",
    )
    with pytest.raises(ValueError, match="tenant_id"):
        service.submit("", "wf-1", {"x": 1})


def test_workflow_vacio(tmp_path: Path):
    repo = BemRunRepository(tmp_path / "bem_runs.db")
    service = BemSubmitService(
        bem_client=_FakeBemClientOk(),
        bem_run_repository=repo,
        now_provider=_now_provider_factory(),
        run_id_provider=lambda: "run-det-6",
    )
    with pytest.raises(ValueError, match="workflow_id"):
        service.submit("tenant-a", "", {"x": 1})


def test_payload_vacio(tmp_path: Path):
    repo = BemRunRepository(tmp_path / "bem_runs.db")
    service = BemSubmitService(
        bem_client=_FakeBemClientOk(),
        bem_run_repository=repo,
        now_provider=_now_provider_factory(),
        run_id_provider=lambda: "run-det-7",
    )
    with pytest.raises(ValueError, match="payload"):
        service.submit("tenant-a", "wf-1", {})


def test_run_id_deterministico(tmp_path: Path):
    repo = BemRunRepository(tmp_path / "bem_runs.db")
    service = BemSubmitService(
        bem_client=_FakeBemClientOk(),
        bem_run_repository=repo,
        now_provider=_now_provider_factory(),
        run_id_provider=lambda: "run-fixed-001",
    )

    run = service.submit("tenant-a", "wf-1", {"x": 1})

    assert run.run_id == "run-fixed-001"


def test_tenant_isolation(tmp_path: Path):
    repo = BemRunRepository(tmp_path / "bem_runs.db")
    service_a = BemSubmitService(
        bem_client=_FakeBemClientOk(),
        bem_run_repository=repo,
        now_provider=_now_provider_factory(),
        run_id_provider=lambda: "run-shared",
    )
    service_b = BemSubmitService(
        bem_client=_FakeBemClientOk(),
        bem_run_repository=repo,
        now_provider=_now_provider_factory(),
        run_id_provider=lambda: "run-shared",
    )

    run_a = service_a.submit("tenant-a", "wf-1", {"x": 1})
    run_b = service_b.submit("tenant-b", "wf-1", {"x": 2})

    assert run_a.tenant_id == "tenant-a"
    assert run_b.tenant_id == "tenant-b"
    assert len(repo.list_by_tenant("tenant-a")) == 1
    assert len(repo.list_by_tenant("tenant-b")) == 1
