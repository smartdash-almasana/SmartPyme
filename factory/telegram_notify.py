from __future__ import annotations

import json
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


def _decision_keyboard() -> str:
    return json.dumps(
        {
            "inline_keyboard": [
                [
                    {"text": "✅ Aprobar y seguir", "callback_data": "GO"},
                    {"text": "🔁 Rechazar y corregir", "callback_data": "FIX"},
                ],
                [
                    {"text": "⏸️ Pausar", "callback_data": "STOP"},
                    {"text": "📊 Ver estado", "callback_data": "STATUS"},
                ],
            ]
        }
    )


def _needs_decision_buttons(status_key: str) -> bool:
    return status_key in {"AUDIT_BLOCKED", "CYCLE_OK", "CYCLE_FAIL", "AUTO_PUSH_OK"}


def format_cycle_message(status: str, details: str = "") -> str:
    status_key = status.strip().upper()

    if status_key == "CYCLE_START":
        text = (
            "SmartPyme Factory esta activa.\n\n"
            "Estoy revisando si hay una tarea autorizada para trabajar. "
            "Esto es solo una comprobacion automatica: todavia no se modifico codigo."
        )
    elif status_key == "AUDIT_BLOCKED":
        text = (
            "SmartPyme Factory esta pausada y necesita una orden tuya.\n\n"
            "No tengo suficiente informacion en este aviso para decirte si conviene aprobar o rechazar. "
            "Este mensaje solo confirma que la factoria esta detenida de forma segura.\n\n"
            "Toca un boton:\n"
            "✅ Aprobar y seguir: si ya revisaste el ultimo ciclo y queres que continue.\n"
            "🔁 Rechazar y corregir: si el ultimo ciclo estuvo mal.\n"
            "⏸️ Pausar: si queres que no haga nada por ahora.\n"
            "📊 Ver estado: si queres mas informacion antes de decidir.\n\n"
            "Recomendacion si no estas seguro: toca Ver estado.\n\n"
            "Estado seguro: no se ejecuto ninguna tarea nueva, no corrio Codex y no se tocaron archivos."
        )
    elif status_key == "TASK_DISPATCH":
        text = (
            "SmartPyme Factory empezo una tarea aprobada.\n\n"
            "No tenes que responder ahora. Espera el resultado del ciclo."
        )
    elif status_key == "TASK_DONE":
        text = (
            "SmartPyme Factory termino una tarea.\n\n"
            "Ahora espera el cierre del ciclo y la evidencia antes de decidir."
        )
    elif status_key == "CYCLE_OK":
        text = (
            "SmartPyme Factory termino el ciclo sin errores.\n\n"
            "Toca un boton para decidir si continua, corrige o queda pausada."
        )
    elif status_key == "CYCLE_FAIL":
        text = (
            "SmartPyme Factory encontro un problema durante el ciclo.\n\n"
            "No conviene aprobar sin revisar. Recomendacion: Ver estado o Pausar."
        )
    elif status_key == "AUTO_PUSH_OK":
        text = (
            "SmartPyme Factory guardo cambios en el repo.\n\n"
            "Hay un nuevo commit para revisar. Usa los botones para decidir el proximo paso."
        )
    elif status_key == "NO_TASK":
        text = (
            "SmartPyme Factory no encontro tareas pendientes.\n\n"
            "No tenes que responder nada salvo que quieras cargar una nueva tarea."
        )
    else:
        text = (
            "SmartPyme Factory envio una actualizacion.\n\n"
            "La parte reservada a GPT contiene el detalle tecnico para interpretar el evento."
        )

    return text + _reserved_for_gpt(status_key, details)


def send_telegram_message(text: str, reply_markup: str | None = None) -> bool:
    token = _env("TELEGRAM_BOT_TOKEN")
    chat_id = _env("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        print("TELEGRAM_NOTIFY_SKIPPED missing env")
        return False

    payload = {
        "chat_id": chat_id,
        "text": text[:3900],
        "disable_web_page_preview": "true",
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup

    data = urllib.parse.urlencode(payload).encode("utf-8")

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
    status_key = status.strip().upper()
    buttons = _decision_keyboard() if _needs_decision_buttons(status_key) else None
    return send_telegram_message(format_cycle_message(status, details), buttons)
