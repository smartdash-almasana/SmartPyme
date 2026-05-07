"""Tests determinísticos para comportamiento default e inyectado del sandbox adapter.

Cubre:
- Propiedad 1: Equivalencia default vs explícito
- Propiedad 2: Forwarding fiel de argumentos
- Propiedad 3: Identidad del resultado del adapter
- Propiedad 4: Propagación monotónica sandbox → review
- Propiedad 5: Determinismo del adapter default
- Req 7: Escritura de evidencia con adapter inyectado
"""

import json
from pathlib import Path

from factory_v2.contracts import ExecutionResultV2, NodeStatus, TaskSpecV2
from factory_v2.graph import run_graph
from factory_v2.sandbox import FakeSandboxAdapter, SandboxAdapter


class SpySandboxAdapter:
    """Adapter de test que registra llamadas y retorna resultado configurable."""

    def __init__(self, status: NodeStatus = NodeStatus.PASS):
        self.calls: list[dict] = []
        self._status = status

    def execute(self, task_id: str, code: str, test_code: str) -> ExecutionResultV2:
        self.calls.append({"task_id": task_id, "code": code, "test_code": test_code})
        return ExecutionResultV2(
            task_id=task_id,
            node_name="sandbox",
            status=self._status,
            stdout=f"[spy] status={self._status.value}",
            return_code=0 if self._status == NodeStatus.PASS else 1,
        )


# ---------------------------------------------------------------------------
# Sub-tarea 3.3 — Protocolo satisfecho por FakeSandboxAdapter
# ---------------------------------------------------------------------------

def test_protocol_satisfied_by_fake():
    """isinstance(FakeSandboxAdapter(), SandboxAdapter) es True."""
    assert isinstance(FakeSandboxAdapter(), SandboxAdapter)


# ---------------------------------------------------------------------------
# Sub-tarea 3.4 — Protocolo satisfecho por SpySandboxAdapter
# ---------------------------------------------------------------------------

def test_spy_satisfies_protocol():
    """isinstance(SpySandboxAdapter(), SandboxAdapter) es True."""
    assert isinstance(SpySandboxAdapter(), SandboxAdapter)


# ---------------------------------------------------------------------------
# Sub-tarea 3.5 — Propiedad 1 (default): run_graph sin adapter → PASS
# ---------------------------------------------------------------------------

def test_default_run_passes():
    """run_graph(spec) sin adapter retorna sandbox_result.status == NodeStatus.PASS."""
    spec = TaskSpecV2(task_id="t-default", objective="test default")
    state = run_graph(spec)
    assert state.sandbox_result.status == NodeStatus.PASS


# ---------------------------------------------------------------------------
# Sub-tarea 3.6 — Propiedad 1 (equivalencia): default == FakeSandboxAdapter explícito
# ---------------------------------------------------------------------------

def test_default_equals_explicit_fake():
    """run_graph(spec) y run_graph(spec, FakeSandboxAdapter()) producen el mismo sandbox_result.status."""
    spec = TaskSpecV2(task_id="t-equiv", objective="test equivalencia")
    state_default = run_graph(spec)
    state_explicit = run_graph(spec, sandbox_adapter=FakeSandboxAdapter())
    assert state_default.sandbox_result.status == state_explicit.sandbox_result.status
    assert state_default.review_result.status == state_explicit.review_result.status


# ---------------------------------------------------------------------------
# Sub-tarea 3.7 — Propiedad 2: Spy recibe task_id, code, test_code sin transformación
# ---------------------------------------------------------------------------

def test_adapter_receives_correct_arguments():
    """Spy Adapter recibe task_id, code, test_code sin transformación."""
    spec = TaskSpecV2(task_id="t-forward", objective="test forwarding")
    spy = SpySandboxAdapter()
    state = run_graph(spec, sandbox_adapter=spy)
    assert len(spy.calls) == 1
    call = spy.calls[0]
    assert call["task_id"] == spec.task_id
    assert call["code"] == state.generated_code
    assert call["test_code"] == state.test_code


# ---------------------------------------------------------------------------
# Sub-tarea 3.8 — Propiedad 3: adapter PASS → state.sandbox_result.status == PASS, return_code == 0
# ---------------------------------------------------------------------------

def test_sandbox_result_not_transformed_pass():
    """Adapter inyectado con NodeStatus.PASS → state.sandbox_result.status == PASS y return_code == 0."""
    spec = TaskSpecV2(task_id="t-id-pass", objective="test identidad PASS")
    spy = SpySandboxAdapter(status=NodeStatus.PASS)
    state = run_graph(spec, sandbox_adapter=spy)
    assert state.sandbox_result.status == NodeStatus.PASS
    assert state.sandbox_result.return_code == 0


# ---------------------------------------------------------------------------
# Sub-tarea 3.9 — Propiedad 3: adapter FAIL → state.sandbox_result.status == FAIL, return_code == 1
# ---------------------------------------------------------------------------

def test_sandbox_result_not_transformed_fail():
    """Adapter inyectado con NodeStatus.FAIL → state.sandbox_result.status == FAIL y return_code == 1."""
    spec = TaskSpecV2(task_id="t-id-fail", objective="test identidad FAIL")
    spy = SpySandboxAdapter(status=NodeStatus.FAIL)
    state = run_graph(spec, sandbox_adapter=spy)
    assert state.sandbox_result.status == NodeStatus.FAIL
    assert state.sandbox_result.return_code == 1


# ---------------------------------------------------------------------------
# Sub-tarea 3.10 — Propiedad 4: sandbox PASS → review_result.status == PASS
# ---------------------------------------------------------------------------

def test_review_reflects_sandbox_pass():
    """sandbox PASS → review_result.status == PASS."""
    spec = TaskSpecV2(task_id="t-mono-pass", objective="test monotónica PASS")
    spy = SpySandboxAdapter(status=NodeStatus.PASS)
    state = run_graph(spec, sandbox_adapter=spy)
    assert state.review_result.status == NodeStatus.PASS


# ---------------------------------------------------------------------------
# Sub-tarea 3.11 — Propiedad 4: sandbox FAIL → review_result.status == FAIL
# ---------------------------------------------------------------------------

def test_review_reflects_sandbox_fail():
    """sandbox FAIL → review_result.status == FAIL."""
    spec = TaskSpecV2(task_id="t-mono-fail", objective="test monotónica FAIL")
    spy = SpySandboxAdapter(status=NodeStatus.FAIL)
    state = run_graph(spec, sandbox_adapter=spy)
    assert state.review_result.status == NodeStatus.FAIL


# ---------------------------------------------------------------------------
# Sub-tarea 3.12 — Propiedad 5: determinismo — dos ejecuciones con mismo spec → mismo status
# ---------------------------------------------------------------------------

def test_default_adapter_is_deterministic():
    """Dos ejecuciones con mismo spec producen mismo sandbox_result.status."""
    spec = TaskSpecV2(task_id="t-determ", objective="test determinismo")
    state1 = run_graph(spec)
    state2 = run_graph(spec)
    assert state1.sandbox_result.status == state2.sandbox_result.status
    assert state1.review_result.status == state2.review_result.status


# ---------------------------------------------------------------------------
# Sub-tarea 3.13 — Req 7: evidencia escrita con adapter inyectado
# ---------------------------------------------------------------------------

def test_evidence_written_with_injected_adapter():
    """evidence_path apunta a archivo JSON válido con task_id y status."""
    spec = TaskSpecV2(task_id="t-evidence", objective="test evidencia")
    spy = SpySandboxAdapter(status=NodeStatus.PASS)
    state = run_graph(spec, sandbox_adapter=spy)
    evidence_path = state.sandbox_result.evidence_path
    assert evidence_path, "evidence_path debe ser no vacío"
    p = Path(evidence_path)
    assert p.exists(), f"evidence file no existe: {evidence_path}"
    data = json.loads(p.read_text())
    assert data["task_id"] == spec.task_id
    assert "status" in data
