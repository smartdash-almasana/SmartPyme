# ruff: noqa: I001

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any
from urllib import request as urllib_request
from urllib.error import HTTPError, URLError
from uuid import uuid4

from app.adapters.hermes_product_adapter import HermesProductAdapter
from app.agents.business_task_executor import AUDIT_VENTA_BAJO_COSTO
from app.mcp.tools.factory_control_tool import enqueue_factory_task
from app.mcp.tools.owner_status_tool import get_owner_status
from app.repositories.supabase_curated_evidence_repository import SupabaseCuratedEvidenceRepository
from app.services.basic_operational_diagnostic_service import BasicOperationalDiagnosticService
from app.services.bem_client import BemClient
from app.services.bem_curated_evidence_adapter import BemCuratedEvidenceAdapter
from app.services.document_intake_service import DocumentIntakeService
from app.services.identity_service import IdentityService
from app.services.initial_laboratory_anamnesis_service import InitialLaboratoryAnamnesisService

DEFAULT_IDENTITY_DB = Path("data/identity.db")
ALLOWED_DOCUMENT_EXTENSIONS = {".pdf", ".xlsx", ".csv"}
AUDIT_VENTA_BAJO_COSTO_COMMAND = "/auditar_venta_bajo_costo"

OwnerStatusProvider = Callable[[str], dict]
FactoryTaskEnqueuer = Callable[..., dict]
TelegramGetFile = Callable[[str], dict[str, Any]]
TelegramDownloadFile = Callable[[str], bytes]
TelegramSendMessage = Callable[[int | str, str], Any]
BEMXlsxSubmitter = Callable[[str, str, bytes, str], dict[str, Any]]


class TelegramAdapter:
    def __init__(
        self,
        identity_service: IdentityService | None = None,
        owner_status_provider: OwnerStatusProvider = get_owner_status,
        factory_task_enqueuer: FactoryTaskEnqueuer = enqueue_factory_task,
        document_intake_service: DocumentIntakeService | None = None,
        telegram_bot_token: str | None = None,
        telegram_get_file: TelegramGetFile | None = None,
        telegram_download_file: TelegramDownloadFile | None = None,
        telegram_send_message: TelegramSendMessage | None = None,
        bem_xlsx_submitter: BEMXlsxSubmitter | None = None,
        bem_workflow_id: str | None = None,
        curated_evidence_repository: Any | None = None,
        diagnostic_service: BasicOperationalDiagnosticService | None = None,
        bem_curated_evidence_adapter: BemCuratedEvidenceAdapter | None = None,
        hermes_product_adapter: HermesProductAdapter | None = None,
        initial_laboratory_anamnesis_service: InitialLaboratoryAnamnesisService | None = None,
    ) -> None:
        self.identity_service = identity_service or IdentityService(DEFAULT_IDENTITY_DB)
        self.owner_status_provider = owner_status_provider
        self.factory_task_enqueuer = factory_task_enqueuer
        self.document_intake_service = document_intake_service or DocumentIntakeService()
        self.telegram_bot_token = telegram_bot_token
        self.telegram_get_file = telegram_get_file
        self.telegram_download_file = telegram_download_file
        self.telegram_send_message = telegram_send_message
        self.bem_xlsx_submitter = bem_xlsx_submitter
        self.bem_workflow_id = bem_workflow_id
        self.curated_evidence_repository = curated_evidence_repository
        self.diagnostic_service = diagnostic_service
        self.bem_curated_evidence_adapter = (
            bem_curated_evidence_adapter or BemCuratedEvidenceAdapter()
        )
        self.hermes_product_adapter = hermes_product_adapter or HermesProductAdapter()
        self.initial_laboratory_anamnesis_service = (
            initial_laboratory_anamnesis_service or InitialLaboratoryAnamnesisService()
        )

    def handle_update(self, update_dict: dict) -> dict:
        user_id = self._extract_user_id(update_dict)
        text = self._extract_text(update_dict)

        if user_id is None:
            return self._security_error("Falta telegram_user_id en el update.")

        if text.startswith("/vincular"):
            return self._handle_link(user_id, text)

        cliente_id = self.identity_service.get_cliente_id_for_telegram_user(user_id)
        if cliente_id is None:
            return {
                "status": "unauthorized",
                "telegram_user_id": str(user_id),
                "message": (
                    "Cuenta no vinculada. Usá /vincular <token> para "
                    "autorizar Telegram."
                ),
            }

        document = self._extract_document(update_dict)
        if document is not None:
            return self._handle_document(user_id, cliente_id, document)

        if text and not text.startswith("/"):
            conversational = self._handle_conversational_message(
                user_id=user_id,
                cliente_id=cliente_id,
                text=text,
            )
            if conversational is not None:
                return conversational

        return {
            "status": "unsupported_command",
            "telegram_user_id": str(user_id),
            "cliente_id": cliente_id,
            "message": "Comando no soportado.",
        }

    def _handle_conversational_message(
        self,
        *,
        user_id: int | str,
        cliente_id: str,
        text: str,
    ) -> dict[str, Any] | None:
        anamnesis_result = self.initial_laboratory_anamnesis_service.process(
            tenant_id=cliente_id,
            channel="telegram",
            text=text,
        )

        if anamnesis_result is not None:
            return {
                "status": "ok",
                "telegram_user_id": str(user_id),
                "cliente_id": cliente_id,
                "message": anamnesis_result.message,
                "mode": "initial_laboratory_anamnesis",
                "anamnesis": anamnesis_result.anamnesis.model_dump(mode="json"),
                "laboratorio_inicial": anamnesis_result.laboratorio.model_dump(mode="json"),
            }

        status = self.owner_status_provider(cliente_id)
        summary = self._format_owner_status(status)

        message = self.hermes_product_adapter.get_assistant_response(
            tenant_id=cliente_id,
            user_message=text,
            summary={"text": summary, "owner_status": status},
            findings=[],
            operational_report={},
        )

        if not message:
            return None

        return {
            "status": "ok",
            "telegram_user_id": str(user_id),
            "cliente_id": cliente_id,
            "message": message,
            "mode": "hermes_product_assistant",
        }

    def _handle_link(self, user_id: int | str, text: str) -> dict:
        return {
            "status": "linked",
            "telegram_user_id": str(user_id),
            "cliente_id": "demo",
            "message": "Cuenta vinculada correctamente.",
        }

    def _handle_document(self, user_id: int | str, cliente_id: str, document: dict) -> dict:
        return {
            "status": "queued",
            "telegram_user_id": str(user_id),
            "cliente_id": cliente_id,
            "document": document,
            "message": "Documento recibido para laboratorio inicial.",
        }

    def _extract_user_id(self, update_dict: dict) -> int | str | None:
        message = update_dict.get("message") or {}
        user = message.get("from") or {}
        return user.get("id")

    def _extract_text(self, update_dict: dict) -> str:
        message = update_dict.get("message") or {}
        text = message.get("text") or ""
        return text.strip()

    def _extract_document(self, update_dict: dict) -> dict | None:
        message = update_dict.get("message") or {}
        document = message.get("document")
        if isinstance(document, dict):
            return document
        return None

    def _security_error(self, reason: str) -> dict:
        return {
            "status": "security_error",
            "message": reason,
        }

    def _format_owner_status(self, status: dict) -> str:
        return (
            f"Estado SmartPyme para {status.get('cliente_id')}: "
            f"jobs={status.get('jobs_count', 0)}"
        )
