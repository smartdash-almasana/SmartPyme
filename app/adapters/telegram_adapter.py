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
        if not isinstance(cliente_id, str) or not cliente_id.strip():
            return {
                "status": "security_error",
                "telegram_user_id": str(user_id),
                "message": "tenant_id inválido para usuario autenticado.",
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
            "message": (
                "Comando no soportado. Comandos disponibles: /status, "
                "/auditar_venta_bajo_costo."
            ),
        }

    def _handle_conversational_message(
        self,
        *,
        user_id: int | str,
        cliente_id: str,
        text: str,
    ) -> dict[str, Any] | None:
        status = self.owner_status_provider(cliente_id)
        summary = self._format_owner_status(status)
        findings = status.get("findings")
        if not isinstance(findings, list):
            findings = []
        report = status.get("operational_report")
        if not isinstance(report, dict):
            report = {}

        message = self.hermes_product_adapter.get_assistant_response(
            tenant_id=cliente_id,
            user_message=text,
            summary={"text": summary, "owner_status": status},
            findings=findings,
            operational_report=report,
        )
        if not message:
            return None

        return {
            "status": "ok",
            "telegram_user_id": str(user_id),
            "cliente_id": cliente_id,
            "message": message,
            "mode": "hermes_product_assistant",
            "grounding": {
                "summary": summary,
                "findings_count": len(findings),
                "has_operational_report": bool(report),
            },
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
        response_message = (
            "Documento recibido, registrado como candidato de evidencia "
            "y enviado a la factoría."
        )
        bem_result: dict[str, Any] | None = None

        if extension == ".xlsx":
            bem_result = self._submit_xlsx_to_bem(
                user_id=user_id,
                cliente_id=cliente_id,
                file_id=file_id,
                file_name=filename,
            )
            if bem_result["status"] == "ok":
                response_message = "Archivo recibido y procesado por BEM"
            else:
                response_message = "No se pudo procesar el XLSX en BEM en este momento."

        response: dict[str, Any] = {
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
            "message": response_message,
        }
        if bem_result is not None:
            response["bem"] = bem_result
        return response

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

    def _submit_xlsx_to_bem(
        self,
        *,
        user_id: int | str,
        cliente_id: str,
        file_id: str | None,
        file_name: str,
    ) -> dict[str, Any]:
        if not isinstance(file_id, str) or not file_id.strip():
            self._safe_send_message(user_id, "Error controlado: archivo XLSX sin file_id.")
            return {"status": "error", "reason": "missing_file_id"}
        try:
            get_file = self.telegram_get_file or self._default_telegram_get_file
            download_file = self.telegram_download_file or self._default_telegram_download_file
            submitter = self.bem_xlsx_submitter or self._default_bem_xlsx_submitter

            file_meta = get_file(file_id.strip())
            file_path = file_meta.get("file_path")
            if not isinstance(file_path, str) or not file_path.strip():
                raise ValueError("telegram file_path missing")
            file_bytes = download_file(file_path.strip())
            if not isinstance(file_bytes, bytes) or not file_bytes:
                raise ValueError("telegram download empty")

            result = submitter(cliente_id, file_name, file_bytes, file_id.strip())
            envelope = self._resolve_bem_envelope(result)
            repository = self.curated_evidence_repository or SupabaseCuratedEvidenceRepository()
            curated = self.bem_curated_evidence_adapter.build_curated_evidence_from_bem_response(
                tenant_id=cliente_id,
                response_payload=envelope,
                run_id=None,
            )
            repository.create(curated)

            diagnostic = (
                self.diagnostic_service
                or BasicOperationalDiagnosticService(repository=repository)
            )
            report = diagnostic.build_report(cliente_id)
            findings = report.get("findings", [])
            if findings:
                self._safe_send_message(user_id, self._build_findings_message(findings))
            else:
                self._safe_send_message(
                    user_id,
                    "Archivo procesado. No se detectaron hallazgos operacionales.",
                )
            return {
                "status": "ok",
                "response_keys": sorted(result.keys()),
                "findings_count": len(findings),
            }
        except Exception as exc:
            self._safe_send_message(
                user_id,
                "Error controlado al procesar XLSX con BEM. Intentá nuevamente.",
            )
            return {"status": "error", "reason": str(exc)}

    def _resolve_bem_envelope(self, raw_response: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(raw_response, dict):
            raise TypeError("bem response invalid")
        call = raw_response.get("call")
        if isinstance(call, dict):
            return call
        return raw_response

    def _build_findings_message(self, findings: list[dict[str, Any]]) -> str:
        counts: dict[str, int] = {}
        for finding in findings:
            code = str(finding.get("finding_type", "")).strip()
            if not code:
                continue
            counts[code] = counts.get(code, 0) + 1
        if not counts:
            return "Archivo procesado. No se detectaron hallazgos operacionales."
        lines = ["Hallazgos detectados:"]
        for code in sorted(counts.keys()):
            lines.append(f"- {code} ({counts[code]})")
        return "\n".join(lines)

    def _safe_send_message(self, chat_id: int | str, text: str) -> None:
        sender = self.telegram_send_message or self._default_telegram_send_message
        try:
            sender(chat_id, text)
        except Exception:
            return

    def _default_telegram_get_file(self, file_id: str) -> dict[str, Any]:
        token = self._require_bot_token()
        url = f"https://api.telegram.org/bot{token}/getFile?file_id={file_id}"
        payload = self._http_get_json(url)
        if not payload.get("ok"):
            raise RuntimeError("telegram getFile failed")
        result = payload.get("result")
        if not isinstance(result, dict):
            raise TypeError("telegram getFile result invalid")
        return result

    def _default_telegram_download_file(self, file_path: str) -> bytes:
        token = self._require_bot_token()
        url = f"https://api.telegram.org/file/bot{token}/{file_path}"
        try:
            with urllib_request.urlopen(url, timeout=15.0) as response:
                return response.read()
        except HTTPError as exc:
            raise RuntimeError(f"telegram download failed: {exc.code}") from exc
        except URLError as exc:
            raise RuntimeError("telegram download network error") from exc

    def _default_telegram_send_message(self, chat_id: int | str, text: str) -> Any:
        token = self._require_bot_token()
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = f'{{"chat_id":"{chat_id}","text":"{text}"}}'.encode()
        req = urllib_request.Request(
            url=url,
            method="POST",
            headers={"content-type": "application/json"},
            data=data,
        )
        try:
            with urllib_request.urlopen(req, timeout=10.0) as response:
                return response.read()
        except Exception:
            return None

    def _default_bem_xlsx_submitter(
        self,
        tenant_id: str,
        file_name: str,
        file_bytes: bytes,
        file_id: str,
    ) -> dict[str, Any]:
        workflow_id = (self.bem_workflow_id or "").strip()
        if not workflow_id:
            raise ValueError("bem_workflow_id missing")
        with NamedTemporaryFile(suffix=Path(file_name).suffix or ".xlsx") as tmp:
            tmp.write(file_bytes)
            tmp.flush()
            client = BemClient()
            return client.submit_file(
                workflow_id=workflow_id,
                file_path=tmp.name,
                call_reference_id=f"telegram-xlsx:{tenant_id}:{file_id}",
            )

    def _http_get_json(self, url: str) -> dict[str, Any]:
        try:
            with urllib_request.urlopen(url, timeout=10.0) as response:
                raw = response.read().decode("utf-8")
        except HTTPError as exc:
            raise RuntimeError(f"http error {exc.code}") from exc
        except URLError as exc:
            raise RuntimeError("network error") from exc
        if not raw:
            raise ValueError("empty response")
        import json

        data = json.loads(raw)
        if not isinstance(data, dict):
            raise TypeError("json object expected")
        return data

    def _require_bot_token(self) -> str:
        token = (self.telegram_bot_token or "").strip()
        if not token:
            raise ValueError("telegram_bot_token missing")
        return token
