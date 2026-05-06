"""Escritor de evidencia local mínima para factory_v2."""

import json
from pathlib import Path

from factory_v2.contracts import ExecutionResultV2


class EvidenceWriter:
    """Escribe evidencia JSON local en factory_v2/evidence/<task_id>/."""

    def __init__(self, base_dir: Path | None = None):
        if base_dir is None:
            base_dir = Path(__file__).resolve().parent / "evidence"
        self.base_dir = Path(base_dir)

    def write(self, result: ExecutionResultV2) -> Path:
        """Escribe un ExecutionResultV2 como evidencia y retorna la ruta."""
        task_dir = self.base_dir / result.task_id
        task_dir.mkdir(parents=True, exist_ok=True)

        filename = f"{result.node_name}_{result.timestamp.strftime('%Y%m%dT%H%M%SZ')}.json"
        evidence_path = task_dir / filename

        evidence_path.write_text(result.model_dump_json(indent=2))
        return evidence_path

    def write_run(self, task_id: str, payload: dict) -> Path:
        """Escribe un resumen de ejecución en evidence/<task_id>/run.json."""
        task_dir = self.base_dir / task_id
        task_dir.mkdir(parents=True, exist_ok=True)

        run_path = task_dir / "run.json"
        run_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False))
        return run_path
