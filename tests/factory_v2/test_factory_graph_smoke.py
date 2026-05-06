"""Smoke test del grafo determinístico factory_v2."""

import json

from factory_v2.contracts import NodeStatus, TaskSpecV2
from factory_v2.graph import run_graph


class TestFactoryGraphSmoke:
    def test_flujo_completo_pass(self):
        """Flujo completo: audit → implement → sandbox → review, todos PASS."""
        spec = TaskSpecV2(
            task_id="T-SMOKE-001",
            objective="Crear función saludar con test",
            modo="WRITE_AUTHORIZED",
        )

        state = run_graph(spec)

        # No debe halt
        assert state.halted is False

        # Los 4 nodos deben existir
        assert state.audit_result is not None
        assert state.implement_result is not None
        assert state.sandbox_result is not None
        assert state.review_result is not None

        # Todos PASS
        assert state.audit_result.status == NodeStatus.PASS
        assert state.implement_result.status == NodeStatus.PASS
        assert state.sandbox_result.status == NodeStatus.PASS
        assert state.review_result.status == NodeStatus.PASS

        # Código generado
        assert "saludar" in state.generated_code
        assert "test_saludar" in state.test_code

    def test_audit_bloquea_task_sin_objective(self):
        """Audit debe bloquear task sin objective."""
        spec = TaskSpecV2(task_id="T-SMOKE-002", objective="")

        state = run_graph(spec)

        assert state.halted is True
        assert state.halt_reason == "BLOCKED_MISSING_REQUIRED_FIELDS"
        assert state.audit_result.status == NodeStatus.BLOCKED
        # Nodos posteriores no deben ejecutarse
        assert state.implement_result is None
        assert state.sandbox_result is None
        assert state.review_result is None

    def test_evidencia_escrita(self):
        """Cada nodo debe escribir evidencia en disco."""
        spec = TaskSpecV2(
            task_id="T-SMOKE-003",
            objective="Test de evidencia",
            modo="AUDIT_ONLY",
        )

        state = run_graph(spec)

        # Verificar que los 4 evidence_path existen y son archivos
        for result in [
            state.audit_result,
            state.implement_result,
            state.sandbox_result,
            state.review_result,
        ]:
            assert result is not None
            assert result.evidence_path is not None
            path = result.evidence_path
            # Leer y validar que es JSON
            with open(path) as f:
                data = json.load(f)
            assert data["task_id"] == "T-SMOKE-003"
            assert data["status"] == "PASS"
