"""Tests de integración para DockerSandboxAdapter — mock sobre DockerExecutor."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from factory.contracts.sandbox import SandboxExecutionResult
from factory_v2.contracts import NodeStatus
from factory_v2.sandbox import (
    DockerSandboxAdapter,
    _build_shell_command,
    _map_result,
    FakeSandboxAdapter,
)


# ── Tests de helpers ──────────────────────────────────────────────


def test_build_shell_command_base64():
    """El comando debe ser un pipe base64 que empaqueta code + test_code."""
    command = _build_shell_command("print(1)", "assert True")
    assert "echo " in command
    assert "base64 -d" in command
    assert "python3 -" in command


def test_map_result_pass():
    sr = SandboxExecutionResult(
        task_id="T1",
        command="echo hi",
        returncode=0,
        stdout="hi",
        stderr="",
        blocked=False,
    )
    result = _map_result(sr)
    assert result.status == NodeStatus.PASS
    assert result.return_code == 0
    assert result.stdout == "hi"
    assert result.reasons == []


def test_map_result_fail():
    sr = SandboxExecutionResult(
        task_id="T2",
        command="exit 1",
        returncode=1,
        stdout="",
        stderr="Error",
        blocked=False,
        reasons=["RUNTIME_ERROR"],
    )
    result = _map_result(sr)
    assert result.status == NodeStatus.FAIL
    assert result.return_code == 1
    assert result.stderr == "Error"
    assert result.reasons == ["RUNTIME_ERROR"]


def test_map_result_blocked():
    sr = SandboxExecutionResult(
        task_id="T3",
        command="rm -rf /",
        returncode=126,
        stdout="",
        stderr="Blocked",
        blocked=True,
        reasons=["DANGEROUS_COMMAND"],
    )
    result = _map_result(sr)
    assert result.status == NodeStatus.BLOCKED
    assert result.return_code == 126
    assert result.reasons == ["DANGEROUS_COMMAND"]


# ── Tests de DockerSandboxAdapter ─────────────────────────────────


def test_execute_safe_command_pass():
    """Comando exitoso → PASS."""
    mock_executor = MagicMock()
    mock_executor.execute.return_value = SandboxExecutionResult(
        task_id="T_SAFE",
        command="echo hello",
        returncode=0,
        stdout="hello",
        stderr="",
        blocked=False,
    )

    adapter = DockerSandboxAdapter(executor=mock_executor)
    result = adapter.execute(task_id="T_SAFE", code="print(1)", test_code="assert True")

    assert result.status == NodeStatus.PASS
    assert result.task_id == "T_SAFE"
    assert result.return_code == 0
    assert result.stdout == "hello"
    assert result.reasons == []

    mock_executor.execute.assert_called_once()


def test_execute_command_failure():
    """Comando con returncode != 0 → FAIL."""
    mock_executor = MagicMock()
    mock_executor.execute.return_value = SandboxExecutionResult(
        task_id="T_FAIL",
        command="exit 1",
        returncode=1,
        stdout="",
        stderr="Error: algo falló",
        blocked=False,
    )

    adapter = DockerSandboxAdapter(executor=mock_executor)
    result = adapter.execute(task_id="T_FAIL", code="raise", test_code="")

    assert result.status == NodeStatus.FAIL
    assert result.task_id == "T_FAIL"
    assert result.return_code == 1
    assert result.stderr == "Error: algo falló"


def test_execute_blocked_by_policy():
    """Comando bloqueado por command_policy → BLOCKED con reasons."""
    mock_executor = MagicMock()
    mock_executor.execute.return_value = SandboxExecutionResult(
        task_id="T_BLOCKED",
        command="git push",
        returncode=126,
        stdout="",
        stderr="Command blocked by policy before Docker execution.",
        blocked=True,
        reasons=["DANGEROUS_COMMAND_PATTERN:^git\\\\s+push"],
    )

    adapter = DockerSandboxAdapter(executor=mock_executor)
    result = adapter.execute(task_id="T_BLOCKED", code="print(1)", test_code="")

    assert result.status == NodeStatus.BLOCKED
    assert result.return_code == 126
    assert "DANGEROUS_COMMAND_PATTERN" in result.reasons[0]


def test_execute_docker_unavailable():
    """Docker no disponible → BLOCKED con DOCKER_UNAVAILABLE.

    Usa docker_available=False para forzar la detección de indisponibilidad
    sin mockear el executor directamente.
    """
    # docker_available=False fuerza a DockerExecutor a reportar indisponibilidad
    adapter = DockerSandboxAdapter(docker_available=False)
    result = adapter.execute(
        task_id="T_NO_DOCKER",
        code="print(1)",
        test_code="assert True",
    )

    assert result.status == NodeStatus.BLOCKED
    assert result.task_id == "T_NO_DOCKER"
    assert result.return_code == 1
    assert "DOCKER_UNAVAILABLE" in result.reasons
    assert "Docker daemon not available" in result.stderr


def test_fake_sandbox_adapter_still_works():
    """FakeSandboxAdapter sigue funcionando tras los cambios."""
    adapter = FakeSandboxAdapter()
    result = adapter.execute(task_id="T_FAKE", code="x=1", test_code="assert x==1")

    assert result.status == NodeStatus.PASS
    assert result.return_code == 0
    assert "fake-sandbox" in result.stdout
    assert result.reasons == []
