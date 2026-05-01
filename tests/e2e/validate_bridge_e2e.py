# E2E validation script for the SmartPyme MCP bridge.
# Uses isolated local artifacts under tests/fixtures/tmp_e2e_bridge.

import asyncio
import json
import os
import shutil
import sys
import uuid
from pathlib import Path
from typing import Any

smartpyme_root = Path(__file__).resolve().parents[2]
hermes_agent_root = smartpyme_root.parent / "hermes-agent"
sys.path.insert(0, str(hermes_agent_root))
sys.path.insert(0, str(smartpyme_root))

os.environ["HERMES_IGNORE_USER_CONFIG"] = "1"

from mcp_smartpyme_bridge import (  # noqa: E402
    create_job,
    get_evidence,
    get_job_status,
    ingest_document,
    list_pending_validations,
    resolve_clarification,
    save_clarification,
)

TOOL_FUNCTIONS = {
    "create_job": create_job,
    "get_job_status": get_job_status,
    "save_clarification": save_clarification,
    "list_pending_validations": list_pending_validations,
    "resolve_clarification": resolve_clarification,
    "ingest_document": ingest_document,
    "get_evidence": get_evidence,
}


def _parse_hermes_response(raw_response: dict[str, Any], tool_name: str) -> Any:
    result_value = raw_response.get("result", "{}")
    if isinstance(result_value, dict):
        return result_value.get("result", result_value)

    try:
        return json.loads(result_value)
    except (json.JSONDecodeError, TypeError) as exc:
        structured = raw_response.get("structuredContent")
        if structured:
            return structured["result"]
        raise ValueError(
            f"Could not parse JSON response for {tool_name}: {result_value}"
        ) from exc


def _get_hermes_handler():
    if os.getenv("SMARTPYME_E2E_USE_HERMES") != "1":
        return None

    try:
        from model_tools import handle_function_call
    except Exception as exc:
        print(f"[INFO] Hermes handler unavailable, using direct bridge calls: {exc}")
        return None
    return handle_function_call


def call_tool(tool_name: str, **kwargs) -> Any:
    print(f"[RUNNING] {tool_name}", end="... ")
    handle_function_call = _get_hermes_handler()

    if handle_function_call is not None:
        raw_response = handle_function_call(
            function_name=f"mcp_smartpyme_{tool_name}",
            function_args=kwargs,
        )
        if not raw_response or not isinstance(raw_response, dict):
            raise ValueError(
                f"Tool call for {tool_name} returned an invalid response: {raw_response}"
            )
        parsed_result = _parse_hermes_response(raw_response, tool_name)
    else:
        parsed_result = asyncio.run(TOOL_FUNCTIONS[tool_name](**kwargs))

    print("[OK]")
    return parsed_result


def _prepare_isolated_environment() -> tuple[Path, Path]:
    run_id = uuid.uuid4().hex[:8]
    base_dir = smartpyme_root / "tests" / "fixtures" / "tmp_e2e_bridge" / run_id
    base_dir.mkdir(parents=True, exist_ok=True)

    jobs_db = base_dir / f"jobs-{run_id}.db"
    clarifications_db = base_dir / f"clarifications-{run_id}.db"
    raw_documents_db = base_dir / f"raw-documents-{run_id}.db"
    evidence_root = base_dir / "evidence_store"

    os.environ["SMARTPYME_JOBS_DB"] = str(jobs_db)
    os.environ["SMARTPYME_CLARIFICATIONS_DB"] = str(clarifications_db)
    os.environ["SMARTPYME_RAW_DOCUMENTS_DB"] = str(raw_documents_db)
    os.environ["SMARTPYME_EVIDENCE_ROOT"] = str(evidence_root)

    print(f"[ENV] SMARTPYME_JOBS_DB={jobs_db}")
    print(f"[ENV] SMARTPYME_CLARIFICATIONS_DB={clarifications_db}")
    print(f"[ENV] SMARTPYME_RAW_DOCUMENTS_DB={raw_documents_db}")
    print(f"[ENV] SMARTPYME_EVIDENCE_ROOT={evidence_root}")
    return base_dir, base_dir / "e2e_test_doc.txt"


def _cleanup_isolated_environment(base_dir: Path) -> None:
    fixtures_root = smartpyme_root / "tests" / "fixtures" / "tmp_e2e_bridge"
    try:
        resolved_base = base_dir.resolve()
        resolved_root = fixtures_root.resolve()
        if resolved_root not in resolved_base.parents:
            raise RuntimeError(f"Refusing cleanup outside fixtures tmp root: {resolved_base}")
        shutil.rmtree(resolved_base, ignore_errors=True)
    except Exception as exc:
        print(f"[WARN] Isolated cleanup skipped: {exc}")


def run_validation() -> dict[str, dict[str, Any]]:
    print("--- Starting E2E Bridge Validation ---")
    test_results: dict[str, dict[str, Any]] = {}
    base_dir, doc_path = _prepare_isolated_environment()

    try:
        create_result = call_tool(
            "create_job",
            cliente_id="cliente-e2e",
            owner_request="Ordenar caja y gastos para validacion E2E.",
            objective="Crear job MCP desde plan operativo E2E.",
            period=None,
            operational_vectors=["caja", "gastos"],
            required_sources=["extracto_bancario"],
            acceptance_criteria=["job consultable en CREATED", "payload persistido"],
        )
        assert create_result["source"] == "real", "Create job source validation failed"
        assert create_result["current_state"] == "CREATED", "Create job state validation failed"
        assert (
            create_result["skill_id"] == "skill_create_job_from_plan"
        ), "Create job skill validation failed"
        assert create_result["job_id"], "Create job did not return job_id"
        assert create_result["plan_id"], "Create job did not return plan_id"
        test_results["create_job"] = {"status": "OK", "payload": create_result}

        job_status = call_tool("get_job_status", job_id=create_result["job_id"])
        assert job_status["source"] == "real", "Job status source validation failed"
        assert job_status["current_state"] == "CREATED", "Job status state validation failed"
        assert (
            job_status["plan_id"] == create_result["plan_id"]
        ), "Job status plan_id validation failed"
        assert job_status["payload"]["operational_plan"], "Job status payload validation failed"
        test_results["get_job_status"] = {"status": "OK", "payload": job_status}

        clarif_creation = call_tool(
            "save_clarification",
            description="E2E Test Clarification",
            type="clarification",
        )
        assert clarif_creation["status"] == "AWAITING_VALIDATION", "Clarification creation failed"
        clarification_id = clarif_creation["clarification_id"]
        test_results["save_clarification"] = {"status": "OK", "payload": clarif_creation}

        pending_list = call_tool("list_pending_validations", owner_id="e2e-owner")
        assert any(
            c["id"] == clarification_id for c in pending_list
        ), "List pending validation failed"
        test_results["list_pending_validations"] = {"status": "OK", "payload": pending_list}

        resolution = call_tool(
            "resolve_clarification",
            clarification_id=clarification_id,
            resolution="Resolved during E2E test.",
        )
        assert resolution["status"] == "RESOLVED", "Resolve clarification failed"
        test_results["resolve_clarification"] = {"status": "OK", "payload": resolution}

        final_list = call_tool("list_pending_validations", owner_id="e2e-owner")
        assert not any(c["id"] == clarification_id for c in final_list), "Confirm resolution failed"
        test_results["confirm_resolution"] = {"status": "OK", "payload": final_list}

        doc_path.write_text("This is the content of the E2E test document.", encoding="utf-8")
        ingest_result = call_tool("ingest_document", file_path=str(doc_path))
        assert (
            ingest_result["status"] == "INGESTED" and ingest_result["chunks_count"] > 0
        ), "Ingest document failed"
        assert ingest_result["raw_document_id"].startswith("raw_"), "Raw document id missing"
        assert ingest_result["raw_file_hash_sha256"], "Raw file hash missing"
        evidence_id = ingest_result["evidence_ids"][0]
        test_results["ingest_document"] = {"status": "OK", "payload": ingest_result}

        evidence_content = call_tool("get_evidence", evidence_id=evidence_id)
        assert (
            evidence_content["text"] == "This is the content of the E2E test document."
        ), "Get evidence failed"
        assert evidence_content["source"] == "real", "Get evidence source validation failed"
        test_results["get_evidence"] = {"status": "OK", "payload": evidence_content}

    finally:
        print("--- Cleaning up isolated E2E files ---")
        _cleanup_isolated_environment(base_dir)
        print("Cleanup complete.")

    print("--- E2E Bridge Validation Summary ---")
    for tool, result in test_results.items():
        print(f"  - {tool}: {result['status']}")
    print("Validation finished successfully.")
    return test_results


if __name__ == "__main__":
    run_validation()
