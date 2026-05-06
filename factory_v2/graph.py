"""Grafo determinístico mínimo — audit → implement → sandbox → review.

Sin LLM. Cada nodo es lógica determinística Python pura.
En fases posteriores se migrará a LangGraph con agentes reales.
"""

from __future__ import annotations

from typing import Optional, Protocol

from factory_v2.contracts import (
    ExecutionResultV2,
    GraphState,
    NodeStatus,
    TaskSpecV2,
)
from factory_v2.evidence import EvidenceWriter
from factory_v2.sandbox import FakeSandboxAdapter


class SandboxAdapterProtocol(Protocol):
    """Protocolo mínimo que debe cumplir cualquier adapter de sandbox."""

    def execute(self, task_id: str, code: str, test_code: str) -> ExecutionResultV2: ...


def _audit_node(state: GraphState) -> GraphState:
    """Valida alcance y modo del TaskSpec."""
    spec = state.task_spec

    # Check básico: task_id y objective deben estar presentes
    if not spec.task_id or not spec.objective:
        state.audit_result = ExecutionResultV2(
            task_id=spec.task_id,
            node_name="audit",
            status=NodeStatus.BLOCKED,
            stdout="",
            stderr="task_id y objective son obligatorios",
            return_code=1,
        )
        state.halted = True
        state.halt_reason = "BLOCKED_MISSING_REQUIRED_FIELDS"
        return state

    # Check: modo WRITE_AUTHORIZED no bloquea en POC
    state.audit_result = ExecutionResultV2(
        task_id=spec.task_id,
        node_name="audit",
        status=NodeStatus.PASS,
        stdout=f"scope ok: files_allowed={spec.files_allowed} files_forbidden={spec.files_forbidden}",
        return_code=0,
    )
    return state


def _implement_node(state: GraphState) -> GraphState:
    """Genera un stub de implementación determinístico — sin LLM."""
    spec = state.task_spec

    # Stub: genera código y test mínimos basados en el objetivo
    code = (
        f"# Stub generado para: {spec.objective}\n"
        f"# task_id: {spec.task_id}\n\n"
        f"def saludar(nombre: str) -> str:\n"
        f'    return f"Hola, {{nombre}}!"\n'
    )

    test_code = (
        f"# Test stub para: {spec.objective}\n"
        f"def test_saludar():\n"
        f"    from stub_module import saludar\n"
        f'    assert saludar("Mundo") == "Hola, Mundo!"\n'
    )

    state.generated_code = code
    state.test_code = test_code

    state.implement_result = ExecutionResultV2(
        task_id=spec.task_id,
        node_name="implement",
        status=NodeStatus.PASS,
        stdout=f"stub generado: code={len(code)}B test={len(test_code)}B",
        return_code=0,
    )
    return state


def _sandbox_node(state: GraphState, adapter: SandboxAdapterProtocol) -> GraphState:
    """Ejecuta código en sandbox usando el adapter inyectado."""
    result = adapter.execute(
        task_id=state.task_spec.task_id,
        code=state.generated_code,
        test_code=state.test_code,
    )
    state.sandbox_result = result
    return state


def _review_node(state: GraphState) -> GraphState:
    """Revisa resultados del sandbox y emite veredicto."""
    spec = state.task_spec

    if state.sandbox_result is None:
        state.review_result = ExecutionResultV2(
            task_id=spec.task_id,
            node_name="review",
            status=NodeStatus.FAIL,
            stderr="sandbox_result ausente",
            return_code=1,
        )
        state.halted = True
        state.halt_reason = "BLOCKED_NO_SANDBOX_RESULT"
        return state

    sb = state.sandbox_result
    status = NodeStatus.PASS if sb.status == NodeStatus.PASS else NodeStatus.FAIL

    state.review_result = ExecutionResultV2(
        task_id=spec.task_id,
        node_name="review",
        status=status,
        stdout=f"review completo: sandbox_status={sb.status.value} return_code={sb.return_code}",
        return_code=0 if status == NodeStatus.PASS else 1,
    )
    return state


def _write_run_evidence(writer: EvidenceWriter, state: GraphState) -> None:
    """Escribe run.json con el resumen de la ejecución."""
    nodes = {}
    for attr in ("audit_result", "implement_result", "sandbox_result", "review_result"):
        result = getattr(state, attr, None)
        if result is not None:
            nodes[attr] = result.status.value

    if state.halted:
        status = "BLOCKED"
    elif state.review_result and state.review_result.status != NodeStatus.PASS:
        status = "FAIL"
    else:
        status = "PASS"

    payload = {
        "task_id": state.task_spec.task_id,
        "status": status,
        "halted": state.halted,
        "halt_reason": state.halt_reason or None,
        "nodes": nodes,
    }
    writer.write_run(state.task_spec.task_id, payload)


def run_graph(
    task_spec: TaskSpecV2,
    sandbox_adapter: Optional[SandboxAdapterProtocol] = None,
) -> GraphState:
    """Ejecuta el grafo determinístico completo y escribe evidencia.

    Flujo: audit → implement → sandbox → review
    Cada nodo escribe evidencia local al terminar.

    Parámetros:
        task_spec: Especificación de la tarea.
        sandbox_adapter: Adapter de sandbox inyectable. Si es None, usa FakeSandboxAdapter.
    """
    adapter: SandboxAdapterProtocol = sandbox_adapter or FakeSandboxAdapter()
    state = GraphState(task_spec=task_spec)
    writer = EvidenceWriter()

    # Nodo 1: Audit
    state = _audit_node(state)
    if state.audit_result:
        state.audit_result.evidence_path = str(writer.write(state.audit_result))
    if state.halted:
        _write_run_evidence(writer, state)
        return state

    # Nodo 2: Implement
    state = _implement_node(state)
    if state.implement_result:
        state.implement_result.evidence_path = str(writer.write(state.implement_result))

    # Nodo 3: Sandbox
    state = _sandbox_node(state, adapter)
    if state.sandbox_result:
        state.sandbox_result.evidence_path = str(writer.write(state.sandbox_result))

    # Nodo 4: Review
    state = _review_node(state)
    if state.review_result:
        state.review_result.evidence_path = str(writer.write(state.review_result))

    _write_run_evidence(writer, state)
    return state
