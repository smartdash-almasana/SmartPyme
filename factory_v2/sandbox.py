"""Fake sandbox adapter para POC — sin Docker real todavía."""

from factory_v2.contracts import ExecutionResultV2, NodeStatus


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
