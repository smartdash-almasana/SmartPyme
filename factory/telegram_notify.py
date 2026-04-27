from __future__ import annotations

import os
import urllib.parse
import urllib.request


def _env(name: str) -> str:
    return os.getenv(name, "").strip()


def _compact_details(details: str) -> str:
    if not details.strip():
        return ""
    lines = [line.strip() for line in details.splitlines() if line.strip()]
    if not lines:
        return ""
    return "\n\nDatos tecnicos:\n" + "\n".join(f"- {line}" for line in lines[:8])


def format_cycle_message(status: str, details: str = "") -> str:
    status_key = status.strip().upper()

    if status_key == "CYCLE_START":
        text = (
            "SmartPyme Factory esta despierta.\n\n"
            "Voy a revisar si hay permiso para ejecutar una nueva tarea. "
            "Todavia no se modifico codigo ni se envio trabajo a Codex."
        )
    elif status_key == "AUDIT_BLOCKED":
        text = (
            "SmartPyme Factory esta pausada por auditoria.\n\n"
            "El sistema intento iniciar un ciclo, pero no ejecuto nada porque el gate sigue en WAITING_AUDIT.\n\n"
            "Esto es una pausa de seguridad: no hubo dispatch, no corrio Codex y no se tocaron archivos.\n\n"
            "Decision pendiente: aprobar, rechazar o mantener bloqueado el ultimo ciclo."
        )
    elif status_key == "TASK_DISPATCH":
        text = (
            "SmartPyme Factory envio una tarea a Codex.\n\n"
            "Ahora se esta trabajando sobre una tarea gobernada y con alcance limitado."
        )
    elif status_key == "TASK_DONE":
        text = (
            "SmartPyme Factory termino una tarea.\n\n"
            "Falta revisar la evidencia antes de permitir otro ciclo."
        )
    elif status_key == "CYCLE_OK":
        text = (
            "SmartPyme Factory cerro el ciclo correctamente.\n\n"
            "El sistema queda en espera de auditoria humana antes de continuar."
        )
    elif status_key == "CYCLE_FAIL":
        text = (
            "SmartPyme Factory fallo durante el ciclo.\n\n"
            "No conviene aprobar nada hasta revisar evidencia y logs."
        )
    elif status_key == "AUTO_PUSH_OK":
        text = (
            "SmartPyme Factory subio cambios al repo.\n\n"
            "Hay un nuevo commit disponible para auditoria."
        )
    elif status_key == "NO_TASK":
        text = (
            "SmartPyme Factory no encontro tareas pendientes.\n\n"
            "El sistema esta activo, pero no tiene trabajo listo para ejecutar."
        )
    else:
        text = (
            f"SmartPyme Factory reporto el evento {status_key}.\n\n"
            "Revisar el contexto tecnico antes de decidir."
        )

    return text + _compact_details(details)


def send_telegram_message(text: str) -> bool:
    token = _env("TELEGRAM_BOT_TOKEN")
    chat_id = _env("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        print("TELEGRAM_NOTIFY_SKIPPED missing env")
        return False

    data = urllib.parse.urlencode({
        "chat_id": chat_id,
        "text": text[:3900],
        "disable_web_page_preview": "true",
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.telegram.org/bot" + token + "/sendMessage",
        data=data,
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            print(f"TELEGRAM_NOTIFY_STATUS {resp.status}")
            return 200 <= resp.status < 300
    except Exception as exc:
        print(f"TELEGRAM_NOTIFY_FAILED {type(exc).__name__}: {exc}")
        return False


def notify_cycle_result(status: str, details: str = "") -> bool:
    return send_telegram_message(format_cycle_message(status, details))
