"""Adaptadores de sandbox para factory_v2 — Fake (POC) y Docker real (HITO_009)."""

from __future__ import annotations

import base64
from typing import Optional

from factory.contracts.sandbox import SandboxExecutionRequest, SandboxExecutionResult
from factory.sandbox.docker_executor import DockerExecutor
from factory_v2.contracts import ExecutionResultV2, NodeStatus
from factory_v2.policy import CommandPolicyV2


def _build_shell_command(code: str, test_code: str) -> str:
    """Construye un comando shell que ejecuta code + test_code via Docker.

    Usa base64 para evitar problemas de escaping de shell con código Python arbitrario.
    """
    combined = f"# === code ===\n{code}\n\n# === test ===\n{test_code}\n"
    encoded = base64.b64encode(combined.encode("utf-8")).decode("ascii")
    return f"echo {encoded} | base64 -d | python3 -"


def _map_result(result: SandboxExecutionResult, node_name: str = "sandbox") -> ExecutionResultV2:
    """Traduce SandboxExecutionResult → ExecutionResultV2."""
    if result.blocked:
        status = NodeStatus.BLOCKED
    elif result.returncode != 0:
        status = NodeStatus.FAIL
    else:
        status = NodeStatus.PASS

    return ExecutionResultV2(
        task_id=result.task_id,
        node_name=node_name,
        status=status,
        stdout=result.stdout,
        stderr=result.stderr,
        return_code=result.returncode,
        reasons=list(result.reasons),
    )


class FakeSandboxAdapter:
    """Sandbox fake que siempre devuelve PASS.

    En fases posteriores se reemplazará por DockerSandboxAdapter real
    usando el DockerExecutor validado en HITO_009.
    """

    def execute(
        self,
        task_id: str,
        code: str,
        test_code: str,
    ) -> ExecutionResultV2:
        """Ejecuta código y tests en sandbox fake."""
        combined = f"# === code ===\n{code}\n\n# === test ===\n{test_code}\n"

        # En POC determinística, siempre PASS
        return ExecutionResultV2(
            task_id=task_id,
            node_name="sandbox",
            status=NodeStatus.PASS,
            stdout=f"[fake-sandbox] code_len={len(code)} test_len={len(test_code)}\n{combined[:200]}",
            stderr="",
            return_code=0,
        )


class DockerSandboxAdapter:
    """Adaptador que envuelve DockerExecutor y expone la interfaz factory_v2.

    Traduce (task_id, code, test_code) → SandboxExecutionRequest para
    el DockerExecutor real de HITO_009, y mapea SandboxExecutionResult
    de vuelta a ExecutionResultV2.

    Uso:
        adapter = DockerSandboxAdapter()
        result = adapter.execute(task_id="T1", code="print(1)", test_code="assert True")
    """

    def __init__(
        self,
        *,
        docker_available: Optional[bool] = None,
        executor: Optional[DockerExecutor] = None,
        policy: Optional[CommandPolicyV2] = None,
    ) -> None:
        """Parámetros:
            docker_available: Override para tests (pasa a DockerExecutor).
            executor: Inyectar un DockerExecutor mockeado para tests.
            policy: Política de seguridad de comandos a aplicar.
        """
        self._executor: DockerExecutor = executor or DockerExecutor(
            docker_available=docker_available
        )
        self._policy = policy or CommandPolicyV2()

    def execute(
        self,
        task_id: str,
        code: str,
        test_code: str,
        *,
        timeout_seconds: int = 300,
    ) -> ExecutionResultV2:
        """Ejecuta code + test_code en Docker efímero.

        La política evalúa el comando wrapper generado, no el contenido semántico de code/test.
        Si Docker no está disponible, retorna BLOCKED con DOCKER_UNAVAILABLE.
        """
        command = _build_shell_command(code, test_code)

        allowed, reason = self._policy.evaluate(command)
        if not allowed:
            return ExecutionResultV2(
                task_id=task_id,
                node_name="sandbox",
                status=NodeStatus.BLOCKED,
                stdout="",
                stderr=f"Comando bloqueado por la política de seguridad: {reason}",
                return_code=126,
                reasons=[reason],
            )

        request = SandboxExecutionRequest(
            task_id=task_id,
            command=command,
            timeout_seconds=timeout_seconds,
            network_disabled=True,
        )

        sandbox_result = self._executor.execute(request)
        return _map_result(sandbox_result)
