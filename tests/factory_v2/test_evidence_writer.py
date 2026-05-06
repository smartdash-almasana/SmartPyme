"""Test unitario para EvidenceWriter — write + write_run."""

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


class TestEvidenceWriterWriteRun:
    def test_write_run_guarda_run_json(self):
        """write_run() debe crear evidence/<task_id>/run.json con task_id, status, nodes."""
        with TemporaryDirectory() as tmpdir:
            writer = EvidenceWriter(base_dir=Path(tmpdir))
            payload = {
                "task_id": "T-RUN-001",
                "run_status": "PASS",
                "halted": False,
                "nodes": {
                    "audit": "PASS",
                    "sandbox": "PASS",
                    "review": "PASS",
                },
            }

            path = writer.write_run("T-RUN-001", payload)

            assert path.exists()
            assert path.name == "run.json"
            assert path.parent.name == "T-RUN-001"

            data = json.loads(path.read_text())
            assert data["task_id"] == "T-RUN-001"
            assert data["run_status"] == "PASS"
            assert data["halted"] is False
            assert data["nodes"]["audit"] == "PASS"
