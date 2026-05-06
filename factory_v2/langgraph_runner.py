"""Runner LangGraph mínimo para factory_v2.

Este módulo introduce LangGraph de forma controlada, sin reemplazar run_graph.
El grafo LangGraph tiene un único nodo determinístico que delega en run_graph.
"""

from __future__ import annotations

from typing import Any, Optional, TypedDict

from factory_v2.contracts import GraphState, TaskSpecV2
from factory_v2.graph import SandboxAdapterProtocol, run_graph


class LangGraphRunnerState(TypedDict, total=False):
    """Estado mínimo usado por el runner LangGraph."""

    task_spec: TaskSpecV2
    graph_state: GraphState


def run_with_langgraph(
    task_spec: TaskSpecV2,
    sandbox_adapter: Optional[SandboxAdapterProtocol] = None,
) -> GraphState:
    """Ejecuta factory_v2 dentro de un StateGraph mínimo.

    Regla operativa:
        - No reemplaza run_graph.
        - No introduce agentes reales.
        - No cambia el default seguro de run_graph.
        - Solo valida integración mínima con LangGraph.
    """
    try:
        from langgraph.graph import END, StateGraph
    except ModuleNotFoundError as exc:  # pragma: no cover - depende del extra dev
        raise RuntimeError(
            "LangGraph no está instalado. Instalá el extra dev/opcional antes de usar "
            "run_with_langgraph."
        ) from exc

    def run_graph_node(state: LangGraphRunnerState) -> dict[str, Any]:
        graph_state = run_graph(
            state["task_spec"],
            sandbox_adapter=sandbox_adapter,
        )
        return {"graph_state": graph_state}

    workflow = StateGraph(LangGraphRunnerState)
    workflow.add_node("run_graph", run_graph_node)
    workflow.set_entry_point("run_graph")
    workflow.add_edge("run_graph", END)

    app = workflow.compile()
    result = app.invoke({"task_spec": task_spec})
    return result["graph_state"]
