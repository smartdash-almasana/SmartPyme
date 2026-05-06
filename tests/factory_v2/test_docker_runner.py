"""Tests para el runner explícito de Docker en factory_v2."""

from factory_v2.contracts import GraphState, TaskSpecV2
from factory_v2 import docker_runner


class RecordingAdapter:
    """Adapter fake para validar inyección explícita sin Docker real."""

    def __init__(self) -> None:
        self.called = False

    def execute(self, task_id: str, code: str, test_code: str):
        self.called = True
        from factory_v2.contracts import ExecutionResultV2, NodeStatus

        return ExecutionResultV2(
            task_id=task_id,
            node_name="sandbox",
            status=NodeStatus.PASS,
            stdout="recording adapter ok",
            return_code=0,
        )


def test_run_with_docker_injects_docker_adapter(monkeypatch):
    """run_with_docker usa DockerSandboxAdapter por inyección, no default global."""
    adapter = RecordingAdapter()

    monkeypatch.setattr(docker_runner, "DockerSandboxAdapter", lambda: adapter)

    state = docker_runner.run_with_docker(
        TaskSpecV2(
            task_id="test_docker_runner",
            objective="validar runner explícito Docker",
        )
    )

    assert isinstance(state, GraphState)
    assert adapter.called is True
    assert state.sandbox_result is not None
    assert state.sandbox_result.status.value == "PASS"
    assert state.review_result is not None
    assert state.review_result.status.value == "PASS"
