from pathlib import Path

from app.adapters.telegram_adapter import TelegramAdapter
from app.factory.business_task_executor import AUDIT_VENTA_BAJO_COSTO
from app.mcp.tools.factory_control_tool import enqueue_factory_task, run_factory_once
from app.mcp.tools.owner_status_tool import get_owner_status
from app.services.identity_service import IdentityService


def _update(user_id: int, text: str) -> dict:
    return {
        "message": {
            "from": {"id": user_id},
            "text": text,
        }
    }


def test_telegram_to_queue_runner_to_owner_status_smoke_ts_015d(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    tasks_dir = Path("factory/multiagent/tasks")
    evidence_dir = Path("factory/multiagent/evidence")

    identity = IdentityService(Path("data/identity.db"))
    identity.create_onboarding_token("token-a", "pyme_A")
    linked = identity.link_telegram_user(111, "token-a")
    assert linked["status"] == "linked"

    def enqueuer(task_id, objective, task_type=None, payload=None):
        return enqueue_factory_task(
            task_id=task_id,
            objective=objective,
            tasks_dir=tasks_dir,
            task_type=task_type,
            payload=payload,
        )

    adapter = TelegramAdapter(
        identity_service=identity,
        factory_task_enqueuer=enqueuer,
    )

    telegram_response = adapter.handle_update(
        _update(111, "/auditar_venta_bajo_costo 1000 1200")
    )

    assert telegram_response["status"] == "queued"
    assert telegram_response["cliente_id"] == "pyme_A"
    assert telegram_response["task"]["task_type"] == AUDIT_VENTA_BAJO_COSTO
    assert telegram_response["payload"]["cliente_id"] == "pyme_A"
    assert telegram_response["payload"]["ventas"] == 1000.0
    assert telegram_response["payload"]["costos"] == 1200.0

    run_result = run_factory_once(tasks_dir=tasks_dir, evidence_dir=evidence_dir)

    assert run_result["status"] == "done"
    assert run_result["task_id"] == telegram_response["task"]["task_id"]
    assert Path(run_result["report_path"]).exists()

    owner_status = get_owner_status("pyme_A")

    assert owner_status["cliente_id"] == "pyme_A"
    assert owner_status["formula_results_count"] == 1
    assert owner_status["pathology_findings_count"] == 1
    assert owner_status["formula_results"][0]["formula_id"] == "ganancia_bruta"
    assert owner_status["formula_results"][0]["value"] == -200.0
    assert owner_status["pathology_findings"][0]["pathology_id"] == "venta_bajo_costo"
    assert owner_status["pathology_findings"][0]["status"] == "ACTIVE"
    assert any("venta_bajo_costo" in message for message in owner_status["messages"])

    owner_status_b = get_owner_status("pyme_B")
    assert owner_status_b["formula_results_count"] == 0
    assert owner_status_b["pathology_findings_count"] == 0
