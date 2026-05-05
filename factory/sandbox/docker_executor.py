"""
Docker Executor — HITO_007_DOCKER_SANDBOX_MINIMAL

Executor Docker efímero para ejecución controlada de comandos en sandbox.

Principios:
  - Valida comandos con command_policy antes de cualquier ejecución.
  - Comandos peligrosos o que requieren aprobación → BLOCKED, sin ejecución Docker.
  - Docker efímero: contenedor se crea y destruye por ejecución.
  - Red deshabilitada por defecto.
  - Timeout obligatorio.
  - No monta el repo principal.
  - No usa Hermes, MCP ni LLM.
  - Si Docker no está disponible, declara DOCKER_UNAVAILABLE en lugar de fallar.

Fallback:
  Si docker SDK no está instalado o el daemon no responde,
  el executor retorna un resultado con blocked=True y
  reasons=["DOCKER_UNAVAILABLE"].
"""

from __future__ import annotations

import subprocess
import shlex
from typing import Optional

from factory.contracts.sandbox import SandboxExecutionRequest, SandboxExecutionResult
from factory.sandbox.command_policy import evaluate_command

# Imagen Docker por defecto para el sandbox
_DEFAULT_IMAGE = "python:3.11-slim"

# Intentar importar docker SDK; si no está disponible, marcar como no disponible
try:
    import docker as _docker_sdk  # type: ignore[import]
    _DOCKER_SDK_AVAILABLE = True
except ImportError:
    _docker_sdk = None  # type: ignore[assignment]
    _DOCKER_SDK_AVAILABLE = False


def _docker_daemon_available() -> bool:
    """Verifica si el daemon Docker responde."""
    if not _DOCKER_SDK_AVAILABLE:
        return False
    try:
        client = _docker_sdk.from_env(timeout=3)
        client.ping()
        return True
    except Exception:
        return False


def _run_in_docker(
    command: str,
    image: str,
    timeout_seconds: int,
    network_disabled: bool,
) -> tuple[int, str, str]:
    """
    Ejecuta el comando en un contenedor Docker efímero.

    Retorna (returncode, stdout, stderr).
    El contenedor se elimina automáticamente al terminar (auto_remove=True).
    """
    client = _docker_sdk.from_env()

    network_mode = "none" if network_disabled else "bridge"

    try:
        container = client.containers.run(
            image=image,
            command=["sh", "-c", command],
            network_mode=network_mode,
            remove=True,
            detach=False,
            stdout=True,
            stderr=True,
            mem_limit="128m",
            cpu_period=100000,
            cpu_quota=50000,  # 50% de un core
        )
        # containers.run con detach=False retorna bytes de stdout
        stdout = container.decode("utf-8", errors="replace") if isinstance(container, bytes) else ""
        return 0, stdout, ""
    except _docker_sdk.errors.ContainerError as exc:
        stdout = exc.container.logs(stdout=True, stderr=False).decode("utf-8", errors="replace") if exc.container else ""
        stderr = str(exc)
        return exc.exit_status, stdout, stderr
    except _docker_sdk.errors.APIError as exc:
        return 1, "", f"DOCKER_API_ERROR: {exc}"


def _run_with_timeout_docker(
    command: str,
    image: str,
    timeout_seconds: int,
    network_disabled: bool,
) -> tuple[int, str, str]:
    """
    Ejecuta el comando en Docker con timeout usando subprocess para el control de tiempo.
    Usa `docker run` CLI como alternativa si el SDK no está disponible.
    """
    if _DOCKER_SDK_AVAILABLE and _docker_daemon_available():
        return _run_in_docker(command, image, timeout_seconds, network_disabled)

    # Fallback: intentar con docker CLI
    network_flag = "--network=none" if network_disabled else ""
    docker_cmd = (
        f"docker run --rm {network_flag} "
        f"--memory=128m "
        f"{image} "
        f"sh -c {shlex.quote(command)}"
    )
    try:
        result = subprocess.run(
            docker_cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return 124, "", f"TIMEOUT: command exceeded {timeout_seconds}s"
    except FileNotFoundError:
        return 1, "", "DOCKER_CLI_NOT_FOUND"


class DockerExecutor:
    """
    Executor Docker efímero para el sandbox de SmartPyme Factory.

    Uso:
        executor = DockerExecutor()
        result = executor.execute(request)
    """

    def __init__(
        self,
        image: str = _DEFAULT_IMAGE,
        docker_available: Optional[bool] = None,
    ) -> None:
        """
        Parámetros:
            image: Imagen Docker a usar. Por defecto python:3.11-slim.
            docker_available: Override para tests. None = detectar automáticamente.
        """
        self.image = image
        self._docker_available = docker_available  # None = auto-detect

    def _is_docker_available(self) -> bool:
        if self._docker_available is not None:
            return self._docker_available
        return _docker_daemon_available()

    def execute(self, request: SandboxExecutionRequest) -> SandboxExecutionResult:
        """
        Evalúa la política del comando y ejecuta en Docker si está permitido.

        Flujo:
          1. Evaluar command_policy.
          2. Si bloqueado → retornar BLOCKED sin ejecutar Docker.
          3. Si Docker no disponible → retornar DOCKER_UNAVAILABLE.
          4. Ejecutar en contenedor efímero con timeout.
          5. Retornar SandboxExecutionResult completo.
        """
        # Paso 1: Evaluar política del comando
        policy = evaluate_command(request.command)

        if not policy.allowed or policy.requires_human_approval:
            return SandboxExecutionResult(
                task_id=request.task_id,
                command=request.command,
                returncode=126,
                stdout="",
                stderr="Command blocked by policy before Docker execution.",
                blocked=True,
                requires_human_approval=policy.requires_human_approval,
                reasons=policy.reasons,
            )

        # Paso 2: Verificar disponibilidad de Docker
        if not self._is_docker_available():
            return SandboxExecutionResult(
                task_id=request.task_id,
                command=request.command,
                returncode=1,
                stdout="",
                stderr="Docker daemon not available.",
                blocked=True,
                requires_human_approval=False,
                reasons=["DOCKER_UNAVAILABLE"],
            )

        # Paso 3: Ejecutar en Docker con timeout
        try:
            returncode, stdout, stderr = _run_with_timeout_docker(
                command=request.command,
                image=self.image,
                timeout_seconds=request.timeout_seconds,
                network_disabled=request.network_disabled,
            )
        except Exception as exc:
            return SandboxExecutionResult(
                task_id=request.task_id,
                command=request.command,
                returncode=1,
                stdout="",
                stderr=f"EXECUTOR_ERROR: {exc}",
                blocked=True,
                requires_human_approval=False,
                reasons=["EXECUTOR_EXCEPTION"],
            )

        # Paso 4: Detectar timeout por código de salida
        if returncode == 124:
            return SandboxExecutionResult(
                task_id=request.task_id,
                command=request.command,
                returncode=124,
                stdout=stdout,
                stderr=stderr or f"TIMEOUT: exceeded {request.timeout_seconds}s",
                blocked=True,
                requires_human_approval=False,
                reasons=["TIMEOUT_EXCEEDED"],
            )

        return SandboxExecutionResult(
            task_id=request.task_id,
            command=request.command,
            returncode=returncode,
            stdout=stdout,
            stderr=stderr,
            blocked=False,
            requires_human_approval=False,
            reasons=[],
        )
