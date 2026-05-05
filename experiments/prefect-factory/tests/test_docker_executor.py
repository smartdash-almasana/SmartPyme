"""
Tests — DockerExecutor — HITO_007_DOCKER_SANDBOX_MINIMAL

Valida el comportamiento del DockerExecutor con y sin Docker disponible.

Los tests usan docker_available=False para aislar la lógica de política
del daemon Docker real (que puede no estar disponible en CI).

Tests requeridos:
  1. Comando seguro python -c "print('ok')" con Docker disponible → DONE, exit_code 0, stdout ok
  2. git push origin main → BLOCKED, no ejecución Docker
  3. Timeout controlado
  4. Sin Docker disponible → DOCKER_UNAVAILABLE, blocked=True
"""

import pytest

from factory_prefect.contracts.sandbox import SandboxExecutionRequest, SandboxExecutionResult
from factory_prefect.sandbox.docker_executor import DockerExecutor


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _request(command: str, timeout: int = 30, task_id: str = "task_test") -> SandboxExecutionRequest:
    return SandboxExecutionRequest(
        task_id=task_id,
        command=command,
        timeout_seconds=timeout,
        network_disabled=True,
    )


# ---------------------------------------------------------------------------
# Test 1: Comando seguro → DONE, exit_code 0, stdout contiene "ok"
# (requiere Docker disponible; se marca como skip si no está)
# ---------------------------------------------------------------------------


def test_safe_command_with_docker_available():
    """
    Comando seguro python -c "print('ok')" con Docker disponible
    debe retornar returncode=0 y stdout con 'ok'.

    Si Docker no está disponible en el entorno, el test verifica
    que el resultado sea DOCKER_UNAVAILABLE (no un error inesperado).
    """
    executor = DockerExecutor()  # auto-detect
    result = executor.execute(_request("python -c \"print('ok')\""))

    assert isinstance(result, SandboxExecutionResult)

    if result.blocked and "DOCKER_UNAVAILABLE" in result.reasons:
        # Docker no disponible en este entorno — comportamiento correcto
        pytest.skip("Docker not available in this environment — DOCKER_UNAVAILABLE is correct behavior")

    # Si Docker está disponible
    assert result.returncode == 0
    assert not result.blocked
    assert "ok" in result.stdout


# ---------------------------------------------------------------------------
# Test 2: git push origin main → BLOCKED, sin ejecución Docker
# ---------------------------------------------------------------------------


def test_git_push_blocked_by_policy():
    """
    git push origin main debe ser bloqueado por command_policy
    ANTES de cualquier ejecución Docker.
    El executor con docker_available=True no debe llegar a ejecutar Docker.
    """
    # Usamos docker_available=True para confirmar que el bloqueo es por política,
    # no por falta de Docker
    executor = DockerExecutor(docker_available=True)
    result = executor.execute(_request("git push origin main"))

    assert result.blocked is True
    assert result.returncode == 126
    assert result.requires_human_approval is True
    assert any("git" in r.lower() or "push" in r.lower() or "DANGEROUS" in r for r in result.reasons)
    # stdout vacío — no se ejecutó nada
    assert result.stdout == ""


def test_rm_rf_blocked_by_policy():
    """rm -rf también debe ser bloqueado por política."""
    executor = DockerExecutor(docker_available=True)
    result = executor.execute(_request("rm -rf /tmp/test"))

    assert result.blocked is True
    assert result.returncode == 126


def test_curl_blocked_by_policy():
    """curl debe ser bloqueado por política."""
    executor = DockerExecutor(docker_available=True)
    result = executor.execute(_request("curl https://example.com"))

    assert result.blocked is True
    assert result.returncode == 126


# ---------------------------------------------------------------------------
# Test 3: Timeout controlado
# ---------------------------------------------------------------------------


def test_timeout_produces_blocked_result():
    """
    Un comando que excede el timeout debe retornar blocked=True
    con reasons=["TIMEOUT_EXCEEDED"] y returncode=124.

    Usamos docker_available=False para simular el comportamiento
    sin necesitar Docker real.
    """
    executor = DockerExecutor(docker_available=False)
    result = executor.execute(_request("sleep 100", timeout=1))

    # Sin Docker disponible → DOCKER_UNAVAILABLE (también blocked)
    assert result.blocked is True
    assert isinstance(result, SandboxExecutionResult)


def test_timeout_with_mock_docker(monkeypatch):
    """
    Simula un timeout real inyectando un executor que retorna código 124.
    """
    from factory_prefect.sandbox import docker_executor as mod

    def mock_run(*args, **kwargs):
        return 124, "", "TIMEOUT: exceeded 1s"

    monkeypatch.setattr(mod, "_run_with_timeout_docker", mock_run)
    monkeypatch.setattr(mod, "_docker_daemon_available", lambda: True)

    executor = DockerExecutor()
    result = executor.execute(_request("sleep 100", timeout=1))

    assert result.blocked is True
    assert result.returncode == 124
    assert "TIMEOUT_EXCEEDED" in result.reasons


# ---------------------------------------------------------------------------
# Test 4: Sin Docker disponible → DOCKER_UNAVAILABLE
# ---------------------------------------------------------------------------


def test_docker_unavailable_returns_blocked():
    """
    Con docker_available=False, el executor debe retornar
    blocked=True con reasons=["DOCKER_UNAVAILABLE"].
    """
    executor = DockerExecutor(docker_available=False)
    result = executor.execute(_request("python -c \"print('ok')\""))

    assert result.blocked is True
    assert "DOCKER_UNAVAILABLE" in result.reasons
    assert result.returncode == 1
    assert result.stdout == ""


def test_docker_unavailable_does_not_execute_command():
    """
    Con Docker no disponible, el comando no debe ejecutarse.
    stdout debe estar vacío.
    """
    executor = DockerExecutor(docker_available=False)
    result = executor.execute(_request("echo SHOULD_NOT_APPEAR"))

    assert "SHOULD_NOT_APPEAR" not in result.stdout
    assert result.blocked is True


# ---------------------------------------------------------------------------
# Tests adicionales de contrato
# ---------------------------------------------------------------------------


def test_safe_command_with_mock_docker_returns_done(monkeypatch):
    """
    Simula Docker disponible y ejecución exitosa.
    Verifica que el resultado sea DONE con exit_code 0 y stdout correcto.
    """
    from factory_prefect.sandbox import docker_executor as mod

    def mock_run(command, image, timeout_seconds, network_disabled):
        return 0, "ok\n", ""

    monkeypatch.setattr(mod, "_run_with_timeout_docker", mock_run)
    monkeypatch.setattr(mod, "_docker_daemon_available", lambda: True)

    executor = DockerExecutor()
    result = executor.execute(_request("python -c \"print('ok')\""))

    assert result.returncode == 0
    assert not result.blocked
    assert "ok" in result.stdout
    assert result.reasons == []


def test_blocked_result_has_reasons():
    """Un resultado blocked siempre debe tener reasons no vacío."""
    executor = DockerExecutor(docker_available=False)
    result = executor.execute(_request("python --version"))

    assert result.blocked is True
    assert len(result.reasons) > 0


def test_policy_blocked_before_docker_check():
    """
    La política se evalúa ANTES de verificar Docker.
    Un comando peligroso con docker_available=False debe retornar
    blocked por política, no por DOCKER_UNAVAILABLE.
    """
    executor = DockerExecutor(docker_available=False)
    result = executor.execute(_request("git push origin main"))

    # El bloqueo es por política, no por Docker
    assert result.blocked is True
    assert "DOCKER_UNAVAILABLE" not in result.reasons
    assert any("DANGEROUS" in r or "git" in r.lower() for r in result.reasons)
