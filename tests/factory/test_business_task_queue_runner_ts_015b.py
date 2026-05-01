from pathlib import Path

from app.agents.business_task_executor import AUDIT_VENTA_BAJO_COSTO
from app.mcp.tools.factory_control_tool import (
    enqueue_factory_task,
    get_factory_task_status,
    run_factory_once,
)
from app.mcp.tools.owner_status_tool import get_owner_status
from app.repositories.formula_result_repository import FormulaResultRepository
from app.repositories.pathology_repository import PathologyRepository


def test_queue_runner_executes_audit_venta_bajo_costo_business_task(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    tasks_dir = Path("factory/multiagent/tasks")
    evidence_dir = Path("factory/multiagent/evidence")

    queued = enqueue_factory_task(
        task_id="task_audit_venta_bajo_costo_1",
        objective="Auditar venta bajo costo para pyme_A",
        tasks_dir=tasks_dir,
        task_type=AUDIT_VENTA_BAJO_COSTO,
        payload={
            "cliente_id": "pyme_A",
            "ventas": 1000,
            "costos": 1200,
            "source_refs": ["orden:1", "costo:1"],
            "formula_result_id": "fr_queue_1",
            "pathology_finding_id": "pf_queue_1",
        },
    )

    assert queued["status"] == "queued"
    assert queued["task_type"] == AUDIT_VENTA_BAJO_COSTO

    run_result = run_factory_once(tasks_dir=tasks_dir, evidence_dir=evidence_dir)

    assert run_result["status"] == "done"
    assert run_result["task_id"] == "task_audit_venta_bajo_costo_1"
    assert Path(run_result["report_path"]).exists()

    task_status = get_factory_task_status("task_audit_venta_bajo_costo_1", tasks_dir=tasks_dir)
    assert task_status["status"] == "done"
    assert task_status["task_type"] == AUDIT_VENTA_BAJO_COSTO
    assert task_status["output"]["formula_result"]["value"] == -200.0
    assert task_status["output"]["pathology_finding"]["status"] == "ACTIVE"

    formula = FormulaResultRepository("pyme_A", Path("data/formula_results.db")).get("fr_queue_1")
    assert formula is not None
    assert formula.formula_id == "ganancia_bruta"
    assert formula.value == -200.0

    finding = PathologyRepository("pyme_A", Path("data/pathologies.db")).get("pf_queue_1")
    assert finding is not None
    assert finding.pathology_id == "venta_bajo_costo"
    assert finding.status.value == "ACTIVE"

    owner_status_a = get_owner_status("pyme_A")
    assert owner_status_a["formula_results_count"] >= 1
    assert owner_status_a["pathology_findings_count"] >= 1

    owner_status_b = get_owner_status("pyme_B")
    assert owner_status_b["formula_results_count"] == 0
    assert owner_status_b["pathology_findings_count"] == 0


def test_queue_runner_keeps_generic_task_behavior(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    tasks_dir = Path("factory/multiagent/tasks")
    evidence_dir = Path("factory/multiagent/evidence")

    enqueue_factory_task(
        task_id="task_generic_1",
        objective="Tarea genérica existente",
        tasks_dir=tasks_dir,
    )

    run_result = run_factory_once(tasks_dir=tasks_dir, evidence_dir=evidence_dir)

    assert run_result["status"] == "done"
    assert run_result["task_id"] == "task_generic_1"

    task_status = get_factory_task_status("task_generic_1", tasks_dir=tasks_dir)
    assert task_status["status"] == "done"
    assert task_status["task_type"] is None
    assert task_status["output"]["status"] == "built"
