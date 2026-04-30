from __future__ import annotations

from pathlib import Path
from typing import Callable

from app.mcp.tools.factory_control_tool import enqueue_factory_task
from app.mcp.tools.owner_status_tool import get_owner_status
from app.services.identity_service import IdentityService


DEFAULT_IDENTITY_DB = Path("data/identity.db")
ALLOWED_DOCUMENT_EXTENSIONS = {".pdf", ".xlsx", ".csv"}

OwnerStatusProvider = Callable[[str], dict]
FactoryTaskEnqueuer = Callable[[str, str], dict]


class TelegramAdapter:
    def __init__(
        self,
        identity_service: IdentityService | None = None,
        owner_status_provider: OwnerStatusProvider = get_owner_status,
        factory_task_enqueuer: FactoryTaskEnqueuer = enqueue_factory_task,
    ) -> None:
        self.identity_service = identity_service or IdentityService(DEFAULT_IDENTITY_DB)
        self.owner_status_provider = owner_status_provider
        self.factory_task_enqueuer = factory_task_enqueuer

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
                "message": "Cuenta no vinculada. Usá /vincular <token> para autorizar Telegram.",
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

        return {
            "status": "unsupported_command",
            "telegram_user_id": str(user_id),
            "cliente_id": cliente_id,
            "message": "Comando no soportado. Comandos disponibles: /status.",
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
            "task": queued,
            "message": "Documento recibido y enviado a la factoría.",
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
            f"jobs={status.get('jobs_count', 0)}, "
            f"hallazgos={status.get('findings_count', 0)}, "
            f"fórmulas={status.get('formula_results_count', 0)}, "
            f"patologías={status.get('pathology_findings_count', 0)}."
        )
