"""Test unitario mínimo para EvidenceWriter.write."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory

from factory_v2.contracts import ExecutionResultV2, NodeStatus
from factory_v2.evidence import EvidenceWriter


class TestEvidenceWriterWrite:
    def test_write_guarda_json_valido(self):
        """write() debe crear un JSON con task_id, node_name, status, stdout, return_code."""
        with TemporaryDirectory() as tmpdir:
            writer = EvidenceWriter(base_dir=Path(tmpdir))
            result = ExecutionResultV2(
                task_id="T-001",
                node_name="audit",
                status=NodeStatus.PASS,
                stdout="ok",
                return_code=0,
            )

            path = writer.write(result)

            assert path.exists()
            data = json.loads(path.read_text())
            assert data["task_id"] == "T-001"
            assert data["node_name"] == "audit"
            assert data["status"] == "PASS"
            assert data["stdout"] == "ok"
            assert data["return_code"] == 0
