"""Runner explícito para ejecutar factory_v2 con Docker real.

Este módulo provee una entrada operacional clara para usar DockerSandboxAdapter
sin convertir Docker en default global de run_graph.
"""

from __future__ import annotations

from factory_v2.contracts import GraphState, TaskSpecV2
from factory_v2.graph import run_graph
from factory_v2.sandbox import DockerSandboxAdapter


def run_with_docker(task_spec: TaskSpecV2) -> GraphState:
    """Ejecuta run_graph con DockerSandboxAdapter inyectado explícitamente.

    Regla operativa:
        - run_graph(task_spec) mantiene FakeSandboxAdapter como default seguro.
        - run_with_docker(task_spec) usa Docker real de forma deliberada.
        - Docker no queda habilitado como default global.
    """
    return run_graph(
        task_spec,
        sandbox_adapter=DockerSandboxAdapter(),
    )
