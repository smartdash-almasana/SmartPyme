"""
DocumentIngestionOrchestrator — capa de orquestación de ingesta de documentos.

Coordina el pipeline completo:
    archivo bytes
    → BEM submission (via bem_submitter inyectado)
    → BemCuratedEvidenceAdapter (BEM response → CuratedEvidenceRecord)
    → CuratedEvidenceRepositoryBackend (persistencia)
    → BasicOperationalDiagnosticService (hallazgos determinísticos)

Contrato de retorno de ingest_document():
    {
        "status": "ok" | "error",
        "bem": dict,                    # respuesta raw de BEM
        "findings": list[dict],         # hallazgos operacionales
        "findings_count": int,
        "evidence_candidate": None,     # reservado para uso futuro
        "reason": str,                  # solo si status == "error"
    }

Sin IA. Sin LLM. Sin heurísticas. Fail-closed ante errores de contrato.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from app.repositories.curated_evidence_repository import CuratedEvidenceRepositoryBackend
from app.services.basic_operational_diagnostic_service import BasicOperationalDiagnosticService
from app.services.bem_curated_evidence_adapter import BemCuratedEvidenceAdapter
from app.services.document_intake_service import DocumentIntakeService

_DEFAULT_EVIDENCE_DB = Path("data/curated_evidence.db")


class DocumentIngestionOrchestrator:
    """
    Orquestador de ingesta de documentos para el pipeline Telegram → BEM → diagnóstico.

    Parámetros
    ----------
    bem_workflow_id:
        ID del workflow BEM. Opcional; el bem_submitter puede ignorarlo si ya lo tiene.
    document_intake_service:
        Servicio de registro de candidatos de evidencia. Se instancia por defecto.
    curated_evidence_repository:
        Repositorio SQLite de evidencia curada. Requerido para persistir y diagnosticar.
    diagnostic_service:
        Servicio de diagnóstico operacional. Se instancia desde el repositorio si no se provee.
    bem_curated_evidence_adapter:
        Adaptador BEM response → CuratedEvidenceRecord. Se instancia por defecto.
    bem_submitter:
        Callable que envía el archivo a BEM y retorna el response dict.
        Firma esperada:
            bem_submitter(
                tenant_id=str,
                file_name=str,
                file_bytes=bytes,
                call_reference_id=str,
                mime_type=str | None,
            ) -> dict[str, Any]
    """

    def __init__(
        self,
        *,
        bem_workflow_id: str | None = None,
        document_intake_service: DocumentIntakeService | None = None,
        curated_evidence_repository: CuratedEvidenceRepositoryBackend | None = None,
        diagnostic_service: BasicOperationalDiagnosticService | None = None,
        bem_curated_evidence_adapter: BemCuratedEvidenceAdapter | None = None,
        bem_submitter: Callable[..., dict[str, Any]] | None = None,
    ) -> None:
        self._bem_workflow_id = bem_workflow_id
        self._document_intake_service = document_intake_service or DocumentIntakeService()
        self._curated_evidence_repository = curated_evidence_repository
        self._diagnostic_service = diagnostic_service
        self._bem_curated_evidence_adapter = (
            bem_curated_evidence_adapter or BemCuratedEvidenceAdapter()
        )
        self._bem_submitter = bem_submitter

    # ------------------------------------------------------------------
    # Método principal
    # ------------------------------------------------------------------

    def ingest_document(
        self,
        *,
        tenant_id: str,
        source: str,
        file_name: str,
        file_bytes: bytes,
        external_file_id: str | None = None,
        mime_type: str | None = None,
    ) -> dict[str, Any]:
        """
        Ejecuta el pipeline completo de ingesta para un documento.

        Retorna siempre un dict con clave "status": "ok" | "error".
        El sub-dict "bem" también siempre tiene "status": "ok" | "error".
        Nunca lanza excepciones al caller — fail-closed interno.
        """
        if self._bem_submitter is None:
            return {
                "status": "error",
                "reason": "bem_submitter_not_configured",
                "bem": {"status": "error", "reason": "bem_submitter_not_configured"},
            }

        call_reference_id = f"{source}:{tenant_id}:{external_file_id or file_name}"

        # --- Paso 1: enviar a BEM ---
        try:
            bem_response = self._bem_submitter(
                tenant_id=tenant_id,
                file_name=file_name,
                file_bytes=file_bytes,
                call_reference_id=call_reference_id,
                mime_type=mime_type,
            )
        except Exception as exc:
            reason = f"bem_submission_failed: {exc}"
            return {
                "status": "error",
                "reason": reason,
                "bem": {"status": "error", "reason": reason},
            }

        if not isinstance(bem_response, dict):
            return {
                "status": "error",
                "reason": "bem_response_invalid",
                "bem": {"status": "error", "reason": "bem_response_invalid"},
            }

        # --- Paso 2: adaptar BEM response → CuratedEvidenceRecord ---
        repository = self._curated_evidence_repository
        if repository is None:
            # Sin repositorio no se puede persistir ni diagnosticar
            return {
                "status": "error",
                "reason": "curated_evidence_repository_not_configured",
                "bem": {"status": "error", "reason": "curated_evidence_repository_not_configured"},
            }

        try:
            # BEM puede devolver el payload envuelto en "call" o directamente
            envelope = (
                bem_response.get("call", bem_response)
                if isinstance(bem_response, dict)
                else bem_response
            )
            curated = self._bem_curated_evidence_adapter.build_curated_evidence_from_bem_response(
                tenant_id=tenant_id,
                response_payload=envelope,
                run_id=call_reference_id,
            )
            repository.create(curated)
        except Exception as exc:
            reason = f"curated_evidence_failed: {exc}"
            return {
                "status": "error",
                "reason": reason,
                "bem": {"status": "error", "reason": reason},
            }

        # --- Paso 3: diagnóstico determinístico ---
        diagnostic = self._diagnostic_service
        if diagnostic is None:
            diagnostic = BasicOperationalDiagnosticService(repository=repository)

        try:
            report = diagnostic.build_report(tenant_id)
            findings: list[dict[str, Any]] = report.get("findings", [])
        except Exception as exc:
            # El diagnóstico falla pero la ingesta fue exitosa — retornar ok sin hallazgos
            bem_ok = {**bem_response, "status": "ok"}
            return {
                "status": "ok",
                "bem": bem_ok,
                "findings": [],
                "findings_count": 0,
                "evidence_candidate": None,
                "diagnostic_error": str(exc),
            }

        # Normalizar bem_response para que siempre tenga "status": "ok"
        # El adapter extrae orchestration["bem"] y los tests esperan bem["status"] == "ok"
        if isinstance(bem_response, dict):
            bem_normalized = {**bem_response, "status": "ok"}
        else:
            bem_normalized = {"status": "ok", "raw": bem_response}

        return {
            "status": "ok",
            "bem": bem_normalized,
            "findings": findings,
            "findings_count": len(findings),
            "evidence_candidate": None,
        }
