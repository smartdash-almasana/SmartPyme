"""Smoke test del grafo determinístico factory_v2."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock

from factory.contracts.sandbox import SandboxExecutionResult
from factory_v2.contracts import NodeStatus, TaskSpecV2
from factory_v2.graph import run_graph
from factory_v2.sandbox import DockerSandboxAdapter, FakeSandboxAdapter


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

    def test_flujo_con_docker_sandbox_adapter(self):
        """Grafo completo con DockerSandboxAdapter mockeado → PASS."""
        mock_executor = MagicMock()
        mock_executor.execute.return_value = SandboxExecutionResult(
            task_id="T-DOCKER-SMOKE",
            command="echo ... | base64 -d | python3 -",
            returncode=0,
            stdout="Hola, Mundo!",
            stderr="",
            blocked=False,
        )

        spec = TaskSpecV2(
            task_id="T-DOCKER-SMOKE",
            objective="Test con DockerSandboxAdapter",
            modo="WRITE_AUTHORIZED",
        )
        adapter = DockerSandboxAdapter(executor=mock_executor)

        state = run_graph(spec, sandbox_adapter=adapter)

        assert state.halted is False
        assert state.audit_result is not None
        assert state.audit_result.status == NodeStatus.PASS
        assert state.sandbox_result is not None
        assert state.sandbox_result.status == NodeStatus.PASS
        assert state.review_result.status == NodeStatus.PASS
        assert state.sandbox_result.stdout == "Hola, Mundo!"

        mock_executor.execute.assert_called_once()

    def test_flujo_con_fake_sandbox_adapter_explicito(self):
        """Grafo con FakeSandboxAdapter explícito (no default) → PASS."""
        spec = TaskSpecV2(
            task_id="T-FAKE-EXPLICIT",
            objective="Test con FakeSandboxAdapter explícito",
        )
        adapter = FakeSandboxAdapter()

        state = run_graph(spec, sandbox_adapter=adapter)

        assert state.halted is False
        assert state.sandbox_result.status == NodeStatus.PASS
        assert "fake-sandbox" in state.sandbox_result.stdout

    def test_run_json_escrito_en_flujo_completo(self):
        """run_graph debe escribir run.json al finalizar flujo completo."""
        spec = TaskSpecV2(
            task_id="T-RUNJSON-001",
            objective="Test run.json en flujo completo",
            modo="WRITE_AUTHORIZED",
        )

        state = run_graph(spec)
        assert state.halted is False

        run_dir = Path(state.audit_result.evidence_path).parent
        run_path = run_dir / "run.json"
        assert run_path.exists()

        data = json.loads(run_path.read_text())
        assert data["task_id"] == "T-RUNJSON-001"
        assert data["status"] == "PASS"
        assert data["halted"] is False
        assert data["halt_reason"] is None
        assert len(data["nodes"]) == 4

    def test_run_json_escrito_en_halt(self):
        """run_graph debe escribir run.json también cuando halted=true."""
        spec = TaskSpecV2(task_id="T-RUNJSON-HALT", objective="")

        state = run_graph(spec)
        assert state.halted is True

        run_dir = Path(state.audit_result.evidence_path).parent
        run_path = run_dir / "run.json"
        assert run_path.exists()

        data = json.loads(run_path.read_text())
        assert data["task_id"] == "T-RUNJSON-HALT"
        assert data["status"] == "BLOCKED"
        assert data["halted"] is True
        assert data["halt_reason"] == "BLOCKED_MISSING_REQUIRED_FIELDS"
        assert len(data["nodes"]) == 1
        assert "audit_result" in data["nodes"]
