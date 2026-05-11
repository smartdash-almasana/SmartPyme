import json
import os
import uuid
from dataclasses import asdict
from pathlib import Path

from mcp.server.fastmcp import FastMCP

# Inicialización del servidor MCP para SmartPyme
mcp = FastMCP("SmartPyme-Bridge")


def _get_evidence_root() -> Path:
    raw_path = os.getenv("SMARTPYME_EVIDENCE_ROOT")
    if raw_path:
        return Path(raw_path)
    return Path(__file__).parent / "evidence_store"

@mcp.tool()
async def create_job(
    cliente_id: str,
    owner_request: str,
    objective: str,
    period: dict | None = None,
    operational_vectors: list[str] | None = None,
    required_sources: list[str] | None = None,
    acceptance_criteria: list[str] | None = None,
) -> dict:
    """
    Crea un Job real desde un OperationalPlanContract minimo.
    """
    from app.contracts.operational_plan_contract import create_operational_plan
    from app.orchestrator.models import STATE_CREATED, Job
    from app.orchestrator.persistence import save_job

    try:
        plan = create_operational_plan(
            cliente_id=cliente_id,
            owner_request=owner_request,
            objective=objective,
            period=period,
            operational_vectors=operational_vectors or [],
            required_sources=required_sources or [],
            acceptance_criteria=acceptance_criteria or [],
            status="ready_for_job",
        )

        job_id = f"job-{uuid.uuid4().hex[:12]}"
        plan_payload = asdict(plan)
        job = Job(
            job_id=job_id,
            current_state=STATE_CREATED,
            status="created",
            skill_id="skill_create_job_from_plan",
            payload={"operational_plan": plan_payload},
        )
        save_job(job)

        return {
            "job_id": job_id,
            "plan_id": plan.plan_id,
            "status": job.status,
            "current_state": job.current_state,
            "skill_id": job.skill_id,
            "source": "real",
        }
    except Exception as e:
        return {
            "status": "ERROR",
            "source": "real",
            "reason": str(e),
        }


@mcp.tool()
async def get_job_status(job_id: str) -> dict:
    """
    Consulta el estado actual de un Job en el JobEngine.
    Utilizar cuando el usuario pregunte 'cómo va la tarea X'.
    """
    from app.orchestrator.persistence import get_job

    job_data = get_job(job_id)

    if job_data:
        payload = job_data.get("payload") or {}
        operational_plan = payload.get("operational_plan") or {}
        plan_id = operational_plan.get("plan_id")
        return {
            "job_id": job_data["job_id"],
            "status": job_data["status"],
            "current_state": job_data["current_state"],
            "skill_id": job_data.get("skill_id"),
            "plan_id": plan_id,
            "payload": payload,
            "blocking_reason": job_data["blocking_reason"],
            "evidence_count": job_data.get("evidence_count", 0),
            "source": "real",
        }
    else:
        return {
            "job_id": job_id,
            "status": "NOT_FOUND",
            "source": "real",
            "reason": "job_not_found",
        }

@mcp.tool()
async def list_pending_validations(owner_id: str) -> list[dict]:
    """
    Lista validaciones pendientes que requieren atención humana.
    """
    from app.core.clarification.persistence import list_pending_clarifications

    # The owner_id argument is kept for future use but not applied in this phase.
    pending = list_pending_clarifications()

    if not pending:
        return []

    # Map the real records to the contract expected by Hermes
    return [
        {
            "id": record.clarification_id,
            "type": "clarification", # The tool is specific to clarifications
            "description": record.reason,
            "status": "AWAITING_VALIDATION",
            "source": "real"
        }
        for record in pending
    ]

@mcp.tool()
async def resolve_clarification(clarification_id: str, resolution: str) -> dict:
    """
    Resuelve una clarificación pendiente con la respuesta del usuario.
    """
    from app.core.clarification.persistence import resolve_clarification as resolve_in_db

    success = resolve_in_db(clarification_id, resolution)

    if success:
        return {
            "clarification_id": clarification_id,
            "status": "RESOLVED",
            "source": "real"
        }
    else:
        return {
            "clarification_id": clarification_id,
            "status": "NOT_FOUND",
            "source": "real",
            "reason": "clarification_not_found"
        }

@mcp.tool()
async def save_clarification(description: str, type: str = "clarification") -> dict:
    """
    Crea una nueva clarificación pendiente para ser atendida.
    """
    from app.core.clarification.models import ClarificationRequest
    from app.core.clarification.persistence import save_clarification as save_in_db

    try:
        clarification_id = f"CL-MANUAL-{uuid.uuid4().hex[:8]}"
        
        # Adapt the MCP input to the persistence model contract
        request = ClarificationRequest(
            clarification_id=clarification_id,
            entity_type="manual_entry", # Default for manually created clarifications
            value_a="N/A",
            value_b="N/A",
            reason=description,
            blocking=True # Manual entries should be blocking by default
        )

        save_in_db(request)

        return {
            "clarification_id": clarification_id,
            "status": "AWAITING_VALIDATION",
            "source": "real"
        }
    except Exception as e:
        return {
            "status": "ERROR",
            "source": "real",
            "reason": str(e)
        }

@mcp.tool()
async def get_evidence(evidence_id: str) -> dict:
    """
    Recupera los detalles de una evidencia específica (factura, remito, log).
    Utilizar cuando el usuario pida 'mostrame la factura' o 'dame el detalle del error'.
    """
    evidence_file = _get_evidence_root() / "document_chunks" / "chunks.jsonl"

    if not evidence_file.exists():
        return {
            "evidence_id": evidence_id,
            "status": "NOT_FOUND",
            "source": "stub_explicit",
            "reason": "evidence_store_not_found"
        }

    with open(evidence_file, "r", encoding="utf-8") as f:
        for line in f:
            try:
                record = json.loads(line.strip())
                if record.get("chunk_id") == evidence_id:
                    record["source"] = "real"
                    return record
            except json.JSONDecodeError:
                # Skip corrupted lines
                continue
    
    # If the loop finishes without finding the evidence
    return {
        "evidence_id": evidence_id,
        "status": "NOT_FOUND",
        "source": "real",
        "reason": "evidence_not_found_in_store"
    }

@mcp.tool()
async def ingest_document(file_path: str, source_id: str | None = None) -> dict:
    """
    Ingesta un documento local en el EvidenceStore de SmartPyme.
    """
    from app.repositories.raw_document_registry import register_raw_document
    from services.document_ingestion_service import DocumentIngestionService

    # The service expects an absolute path
    abs_file_path = Path(file_path).resolve()

    if not abs_file_path.exists():
        return {
            "status": "ERROR",
            "source": "real",
            "reason": f"file_not_found: {file_path}"
        }

    try:
        raw_document = register_raw_document(
            str(abs_file_path),
            source_id=source_id,
            metadata={"ingested_by": "mcp_smartpyme_ingest_document"},
        )
        evidence_root = _get_evidence_root()
        service = DocumentIngestionService(evidence_root=evidence_root)
        result = service.ingest_pdfs([abs_file_path])

        if result.errors:
            return {
                "status": "ERROR",
                "source": "real",
                "reason": "ingestion_failed",
                "details": result.errors
            }
        
        # Workaround: read back the chunks file to get the new chunk IDs
        chunks_file = evidence_root / "document_chunks" / "chunks.jsonl"
        evidence_ids = []
        if chunks_file.exists():
            with open(chunks_file, "r", encoding="utf-8") as f:
                for line in f:
                    chunk = json.loads(line)
                    if chunk.get("source_id") in result.source_ids:
                        evidence_ids.append(chunk.get("chunk_id"))

        return {
            "status": "INGESTED",
            "source": "real",
            "raw_document_id": raw_document["raw_document_id"],
            "raw_file_hash_sha256": raw_document["file_hash_sha256"],
            "evidence_ids": evidence_ids,
            "chunks_count": result.chunk_count
        }
    except Exception as e:
        return {
            "status": "ERROR",
            "source": "real",
            "reason": f"unexpected_ingestion_error: {str(e)}"
        }

@mcp.tool()
async def factory_get_queue_summary(tasks_dir: str | None = None) -> dict:
    """
    Obtiene un resumen de la cola operativa de la factoría.
    """
    from app.mcp.tools.factory_control_tool import get_factory_queue_summary
    return get_factory_queue_summary(tasks_dir)

@mcp.tool()
async def factory_get_queue_details(tasks_dir: str | None = None, include_done: bool = False) -> dict:
    """
    Obtiene los detalles completos de las tareas en la cola de la factoría.
    """
    from app.mcp.tools.factory_control_tool import get_factory_queue_details
    return get_factory_queue_details(tasks_dir, include_done=include_done)

@mcp.tool()
async def factory_preview_next_task(tasks_dir: str | None = None) -> dict:
    """
    Obtiene una vista previa de la próxima tarea pendiente en la cola de la factoría sin ejecutarla.
    """
    from app.mcp.tools.factory_control_tool import get_next_task_preview
    return get_next_task_preview(tasks_dir)

@mcp.tool()
async def factory_execute_task(task_id: str, tasks_dir: str | None = None) -> dict:
    """
    Ejecuta exactamente la tarea con el task_id proporcionado de la cola de la factoría.
    """
    from app.mcp.tools.factory_control_tool import execute_one_task_by_id
    return execute_one_task_by_id(task_id, tasks_dir)

@mcp.tool()
async def factory_process_intake(message: str, cliente_id: str) -> dict:
    """
    Procesa un mensaje del dueño usando IA para interpretar la intención y validar condiciones operativas.
    """
    from app.ai.orchestrators.ai_intake_orchestrator import AIIntakeOrchestrator
    
    try:
        orchestrator = AIIntakeOrchestrator()
        return orchestrator.process_owner_message(message, cliente_id)
    except Exception as e:
        return {
            "status": "REJECTED",
            "skill_id": None,
            "error_type": "INTERNAL_ERROR",
            "reason": str(e)
        }

@mcp.tool()
async def factory_confirm_intake(
    cliente_id: str,
    skill_id: str,
    action: str,
    overrides: dict | None = None
) -> dict:
    """
    Confirma la creación de un Job real tras la propuesta del intake (CONFIRM o REJECT).
    """
    from app.ai.orchestrators.owner_confirmation_orchestrator import OwnerConfirmationOrchestrator
    
    try:
        orchestrator = OwnerConfirmationOrchestrator()
        # Note: We pass raw data; orchestrator handles validation.
        # TypedDict and Literal are for internal use.
        return orchestrator.confirm_job({
            "cliente_id": cliente_id,
            "skill_id": skill_id,
            "action": action, # type: ignore
            "overrides": overrides or {} # type: ignore
        })
    except Exception as e:
        return {
            "status": "REJECTED",
            "skill_id": skill_id,
            "error_type": "INTERNAL_ERROR",
            "reason": str(e)
        }

@mcp.tool()
async def factory_record_decision(
    cliente_id: str,
    tipo_decision: str,
    mensaje_original: str,
    propuesta: dict,
    accion: str,
    overrides: dict | None = None,
    job_id: str | None = None,
    db_path: str | None = None
) -> dict:
    """
    Registra formalmente una decisión del dueño (INFORMAR, EJECUTAR, RECHAZAR) en el DecisionRepository.
    """
    from app.ai.orchestrators.decision_orchestrator import record_owner_decision
    import os

    # Determinar ruta de DB por defecto si no se provee
    target_db = db_path or os.getenv("SMARTPYME_DECISIONS_DB") or "decisions.db"

    try:
        input_data = {
            "tipo_decision": tipo_decision,
            "mensaje_original": mensaje_original,
            "propuesta": propuesta,
            "accion": accion,
            "overrides": overrides,
            "job_id": job_id
        }
        
        result = record_owner_decision(input_data, cliente_id, target_db)
        
        if result["status"] == "REJECTED":
            error_type = result.get("error_type", "INVALID_DECISION_INPUT")
            if error_type == "INVALID_INPUT":
                error_type = "INVALID_DECISION_INPUT"
                
            return {
                "status": "REJECTED",
                "error_type": error_type,
                "reason": result["reason"]
            }
            
        return result
    except Exception as e:
        return {
            "status": "REJECTED",
            "error_type": "INTERNAL_ERROR",
            "reason": str(e)
        }

@mcp.tool()
async def factory_start_authorized_job(cliente_id: str, job_id: str) -> dict:
    """
    Inicia la ejecución de un Job que ya cuenta con autorización formal del dueño.
    Solo realiza la transición a estado RUNNING.
    """
    from app.services.job_executor_service import JobExecutorService
    from app.repositories.decision_repository import DecisionRepository
    import app.orchestrator.persistence as job_repo_module
    import os

    class JobRepoWrapper:
        def get_job(self, jid): return job_repo_module.get_job(jid)
        def save_job(self, job): return job_repo_module.save_job(job)

    try:
        executor = JobExecutorService()
        
        # Resolver ruta de DB de decisiones
        decisions_db = os.getenv("SMARTPYME_DECISIONS_DB") or "decisions.db"
        decision_repo = DecisionRepository(cliente_id=cliente_id, db_path=decisions_db)
        
        return executor.start_authorized_job(
            cliente_id=cliente_id,
            job_id=job_id,
            job_repository=JobRepoWrapper(),
            decision_repository=decision_repo
        )
    except Exception as e:
        return {
            "status": "REJECTED",
            "error_type": "INTERNAL_ERROR",
            "reason": str(e)
        }

@mcp.tool()
async def factory_build_operational_case(cliente_id: str, job_id: str) -> dict:
    """
    Construye un OperationalCase (expediente investigativo) desde un Job en estado RUNNING.
    """
    from app.ai.orchestrators.operational_case_orchestrator import build_operational_case
    from app.repositories.operational_case_repository import OperationalCaseRepository
    import app.orchestrator.persistence as job_repo_module
    import os

    class JobRepoWrapper:
        def get_job(self, jid): return job_repo_module.get_job(jid)

    try:
        # Resolver ruta de DB de casos operativos
        target_db = os.getenv("SMARTPYME_CASES_DB") or "operational_cases.db"
        case_repo = OperationalCaseRepository(cliente_id=cliente_id, db_path=target_db)
        
        return build_operational_case(
            cliente_id=cliente_id,
            job_id=job_id,
            job_repository=JobRepoWrapper(),
            operational_case_repository=case_repo
        )
    except Exception as e:
        return {
            "status": "REJECTED",
            "error_type": "INTERNAL_ERROR",
            "reason": str(e)
        }

@mcp.tool()
async def factory_run_deepseek_audit(
    task_id: str,
    files: list[str],
    objective: str,
    model: str | None = None,
    timeout_seconds: int = 900,
) -> dict:
    """
    Ejecuta una auditoria local con DeepSeek via Ollama y escribe evidencia en factory/evidence/deepseek_audit/<task_id>/.
    """
    from app.mcp.tools.deepseek_audit_tool import DEFAULT_MODEL, run_deepseek_audit

    try:
        return run_deepseek_audit(
            task_id=task_id,
            files=files,
            objective=objective,
            model=model or DEFAULT_MODEL,
            timeout_seconds=timeout_seconds,
        )
    except Exception as e:
        return {
            "status": "AUDIT_BLOCKED",
            "source": "deepseek_local",
            "task_id": task_id,
            "reason": str(e),
        }


@mcp.tool()
async def bem_submit_workflow(
    tenant_id: str,
    workflow_id: str,
    payload: dict,
    db_path: str | None = None,
) -> dict:
    """
    Ejecuta un submit de SmartPyme hacia BEM y registra el run en SQLite.
    Si BEM responde COMPLETED, también persiste CuratedEvidenceRecord.
    """
    from pathlib import Path

    from app.repositories.bem_run_repository import BemRunRepository
    from app.repositories.curated_evidence_repository import CuratedEvidenceRepositoryBackend
    from app.services.bem_client import BemClient
    from app.services.bem_submit_service import BemSubmitService

    target_db = (
        db_path
        or os.getenv("SMARTPYME_BEM_RUNS_DB_PATH")
        or str(Path("data") / "bem_runs.db")
    )
    curated_db = (
        os.getenv("SMARTPYME_CURATED_EVIDENCE_DB_PATH")
        or str(Path("data") / "curated_evidence.db")
    )

    try:
        service = BemSubmitService(
            bem_client=BemClient(),
            bem_run_repository=BemRunRepository(target_db),
            curated_evidence_repository=CuratedEvidenceRepositoryBackend(curated_db),
        )
        run = service.submit(
            tenant_id=tenant_id,
            workflow_id=workflow_id,
            payload=payload,
        )
        return {
            "status": "COMPLETED",
            "tenant_id": run.tenant_id,
            "run_id": run.run_id,
            "workflow_id": run.workflow_id,
            "response_payload": run.response_payload,
            "source": "real",
        }
    except RuntimeError as e:
        return {
            "status": "REJECTED",
            "error_type": "BEM_UPSTREAM_ERROR",
            "reason": str(e),
            "source": "real",
        }
    except Exception as e:
        return {
            "status": "REJECTED",
            "error_type": "INTERNAL_ERROR",
            "reason": str(e),
            "source": "real",
        }

if __name__ == "__main__":
    # El servidor corre por defecto en modo stdio para ser consumido por Hermes
    mcp.run()
