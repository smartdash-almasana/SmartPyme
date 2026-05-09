from __future__ import annotations

from factory_prefect.contracts.sandbox import SandboxExecutionRequest, SandboxExecutionResult
from factory_prefect.sandbox.docker_executor import DockerExecutor


class SandboxBridge:
    def __init__(self):
        # El executor se carga de forma perezosa para evitar importaciones costosas
        # al inicio y facilitar los tests sin dependencias de Docker.
        self._executor: DockerExecutor | None = None

    def _load_executor(self) -> DockerExecutor:
        if self._executor is None:
            self._executor = DockerExecutor()
        return self._executor

    def execute(self, request: SandboxExecutionRequest) -> SandboxExecutionResult:
        """
        Delega la ejecución de un comando al executor del sandbox (Docker).

        Este método actúa como un puente (Bridge) entre el runtime de la Factory V3
        y el sistema de ejecución aislado, desacoplando ambos sistemas.

        Args:
            request: Contrato de entrada con los detalles del comando a ejecutar.

        Returns:
            Contrato de salida con el resultado de la ejecución.
        """
        executor = self._load_executor()
        result = executor.execute(request)
        return result
