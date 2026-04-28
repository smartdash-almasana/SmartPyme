from __future__ import annotations

import os
import urllib.parse
import urllib.request


def _env(name: str) -> str:
    return os.getenv(name, "").strip()


def _reserved_for_gpt(status: str, details: str = "") -> str:
    lines = [f"estado={status.strip().upper()}"]
    if details.strip():
        lines.extend(line.strip() for line in details.splitlines() if line.strip())
    return "\n\nReservado a GPT:\n" + "\n".join(f"- {line}" for line in lines[:10])


def format_cycle_message(status: str, details: str = "") -> str:
    status_key = status.strip().upper()

    if status_key == "CYCLE_START":
        text = (
            "SmartPyme Factory esta activa.\n\n"
            "Estoy revisando si corresponde iniciar una nueva tarea. "
            "Por ahora no se modifico codigo ni se envio trabajo al constructor."
        )
    elif status_key == "AUDIT_BLOCKED":
        text = (
            "SmartPyme Factory esta pausada.\n\n"
            "No arranco una nueva tarea porque antes falta decidir que hacer con el ultimo ciclo cerrado.\n\n"
            "Tenes tres opciones claras:\n"
            "1. Aprobar: el ultimo ciclo queda aceptado y la factoria puede seguir con la proxima tarea.\n"
            "2. Rechazar: la ultima tarea se reabre para corregirla.\n"
            "3. Mantener pausado: no se ejecuta nada hasta revisar mas evidencia.\n\n"
            "Estado seguro: no se ejecuto ninguna tarea nueva, no corrio Codex y no se tocaron archivos."
        )
    elif status_key == "TASK_DISPATCH":
        text = (
            "SmartPyme Factory empezo a trabajar en una tarea aprobada.\n\n"
            "El constructor recibio una tarea con alcance limitado."
        )
    elif status_key == "TASK_DONE":
        text = (
            "SmartPyme Factory termino una tarea.\n\n"
            "Ahora conviene revisar la evidencia antes de permitir otro ciclo."
        )
    elif status_key == "CYCLE_OK":
        text = (
            "SmartPyme Factory cerro el ciclo correctamente.\n\n"
            "Ahora tenes que decidir si ese ciclo queda aprobado, si debe corregirse o si preferis mantener la factoria pausada para revisar mas evidencia."
        )
    elif status_key == "CYCLE_FAIL":
        text = (
            "SmartPyme Factory encontro un problema durante el ciclo.\n\n"
            "La decision recomendada es mantener pausado o rechazar el ciclo hasta revisar la evidencia."
        )
    elif status_key == "AUTO_PUSH_OK":
        text = (
            "SmartPyme Factory guardo los cambios en el repo.\n\n"
            "Hay un nuevo commit disponible para revisar antes de aprobar el siguiente ciclo."
        )
    elif status_key == "NO_TASK":
        text = (
            "SmartPyme Factory no encontro tareas pendientes.\n\n"
            "El sistema esta activo, pero no tiene trabajo listo para ejecutar."
        )
    else:
        text = (
            "SmartPyme Factory envio una actualizacion.\n\n"
            "La parte reservada a GPT contiene el detalle tecnico para interpretar el evento."
        )

    return text + _reserved_for_gpt(status_key, details)


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
