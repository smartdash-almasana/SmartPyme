# ruff: noqa: I001

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any
from uuid import uuid4

from app.factory.business_task_executor import AUDIT_VENTA_BAJO_COSTO
from app.mcp.tools.factory_control_tool import enqueue_factory_task
from app.mcp.tools.owner_status_tool import get_owner_status
from app.services.document_intake_service import DocumentIntakeService
from app.services.identity_service import IdentityService


DEFAULT_IDENTITY_DB = Path("data/identity.db")
ALLOWED_DOCUMENT_EXTENSIONS = {".pdf", ".xlsx", ".csv"}
AUDIT_VENTA_BAJO_COSTO_COMMAND = "/auditar_venta_bajo_costo"

OwnerStatusProvider = Callable[[str], dict]
FactoryTaskEnqueuer = Callable[..., dict]


class TelegramAdapter:
    def __init__(
        self,
        identity_service: IdentityService | None = None,
        owner_status_provider: OwnerStatusProvider = get_owner_status,
        factory_task_enqueuer: FactoryTaskEnqueuer = enqueue_factory_task,
        document_intake_service: DocumentIntakeService | None = None,
    ) -> None:
        self.identity_service = identity_service or IdentityService(DEFAULT_IDENTITY_DB)
        self.owner_status_provider = owner_status_provider
        self.factory_task_enqueuer = factory_task_enqueuer
        self.document_intake_service = document_intake_service or DocumentIntakeService()

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

        if text.startswith("/status"):
            status = self.owner_status_provider(cliente_id)
            return {
                "status": "ok",
                "telegram_user_id": str(user_id),
                "cliente_id": cliente_id,
                "message": self._format_owner_status(status),
                "data": status,
            }

        if text.startswith(AUDIT_VENTA_BAJO_COSTO_COMMAND):
            return self._handle_audit_venta_bajo_costo(user_id, cliente_id, text)

        return {
            "status": "unsupported_command",
            "telegram_user_id": str(user_id),
            "cliente_id": cliente_id,
            "message": (
                "Comando no soportado. Comandos disponibles: /status, "
                "/auditar_venta_bajo_costo."
            ),
        }

    def _handle_link(self, user_id: int | str, text: str) -> dict:
        parts = text.split(maxsplit=1)
        if len(parts) != 2 or not parts[1].strip():
            return {
                "status": "invalid_command",
                "telegram_user_id": str(user_id),
                "message": "Formato inválido. Usá /vincular <token>.",
            }

        token = parts[1].strip()
        result = self.identity_service.link_telegram_user(user_id, token)
        if result["status"] != "linked":
            return {
                "status": "invalid_token",
                "telegram_user_id": str(user_id),
                "message": "Token inválido o ya utilizado.",
            }

        return {
            "status": "linked",
            "telegram_user_id": str(user_id),
            "cliente_id": result["cliente_id"],
            "message": "Cuenta vinculada correctamente.",
        }

    def _handle_document(self, user_id: int | str, cliente_id: str, document: dict) -> dict:
        filename = document.get("file_name") or ""
        file_id = document.get("file_id")
        extension = Path(filename).suffix.lower()

        if extension not in ALLOWED_DOCUMENT_EXTENSIONS:
            return {
                "status": "unsupported_document",
                "telegram_user_id": str(user_id),
                "cliente_id": cliente_id,
                "message": "Formato no soportado. Enviá PDF, XLSX o CSV.",
            }

        candidate = self.document_intake_service.register_telegram_document_candidate(
            cliente_id=cliente_id,
            telegram_user_id=user_id,
            file_id=file_id,
            file_name=filename,
            mime_type=document.get("mime_type"),
        )

        task_id = f"telegram:{cliente_id}:{file_id or filename}"
        objective = f"Procesar evidencia Telegram para cliente {cliente_id}: {filename}"
        queued = self.factory_task_enqueuer(task_id, objective)

        return {
            "status": "queued",
            "telegram_user_id": str(user_id),
            "cliente_id": cliente_id,
            "document": {
                "file_id": file_id,
                "file_name": filename,
                "mime_type": document.get("mime_type"),
            },
            "evidence_candidate": candidate.model_dump(mode="json"),
            "task": queued,
            "message": (
                "Documento recibido, registrado como candidato de evidencia "
                "y enviado a la factoría."
            ),
        }

    def _handle_audit_venta_bajo_costo(
        self,
        user_id: int | str,
        cliente_id: str,
        text: str,
    ) -> dict:
        parsed = self._parse_audit_venta_bajo_costo_command(text)
        if parsed["status"] != "ok":
            return {
                "status": "invalid_command",
                "telegram_user_id": str(user_id),
                "cliente_id": cliente_id,
                "message": (
                    "Formato inválido. Usá /auditar_venta_bajo_costo "
                    "<ventas> <costos>."
                ),
            }

        ventas = parsed["ventas"]
        costos = parsed["costos"]
        task_id = f"telegram:{cliente_id}:audit_venta_bajo_costo:{uuid4()}"
        source_ref = f"telegram:{user_id}:{AUDIT_VENTA_BAJO_COSTO_COMMAND}"
        payload: dict[str, Any] = {
            "cliente_id": cliente_id,
            "ventas": ventas,
            "costos": costos,
            "source_refs": [source_ref],
        }
        objective = (
            f"Auditar venta bajo costo para cliente {cliente_id} "
            "desde Telegram"
        )
        queued = self.factory_task_enqueuer(
            task_id,
            objective,
            task_type=AUDIT_VENTA_BAJO_COSTO,
            payload=payload,
        )

        return {
            "status": "queued",
            "telegram_user_id": str(user_id),
            "cliente_id": cliente_id,
            "task": queued,
            "payload": payload,
            "message": (
                "Auditoría venta bajo costo encolada en la factoría."
            ),
        }

    def _parse_audit_venta_bajo_costo_command(self, text: str) -> dict:
        parts = text.split()
        if len(parts) != 3 or parts[0] != AUDIT_VENTA_BAJO_COSTO_COMMAND:
            return {"status": "invalid"}
        try:
            ventas = float(parts[1])
            costos = float(parts[2])
        except ValueError:
            return {"status": "invalid"}
        return {"status": "ok", "ventas": ventas, "costos": costos}

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
            f"jobs={status.get('jobs_count', 0)}, "
            f"hallazgos={status.get('findings_count', 0)}, "
            f"fórmulas={status.get('formula_results_count', 0)}, "
            f"patologías={status.get('pathology_findings_count', 0)}."
        )
