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
            "Estoy revisando si hay una tarea autorizada para trabajar. "
            "Esto es solo una comprobacion automatica: todavia no se modifico codigo."
        )
    elif status_key == "AUDIT_BLOCKED":
        text = (
            "SmartPyme Factory esta pausada y necesita una orden tuya.\n\n"
            "No tengo suficiente informacion en este aviso para decirte si conviene aprobar o rechazar. "
            "Este mensaje solo confirma que la factoria esta detenida de forma segura.\n\n"
            "Responde una de estas opciones:\n"
            "APROBAR: si ya revisaste el ultimo ciclo y queres que siga con la proxima tarea.\n"
            "RECHAZAR: si el ultimo ciclo estuvo mal y queres que se corrija.\n"
            "PAUSAR: si queres que no haga nada por ahora.\n"
            "CONTEXTO: si queres recibir un resumen tecnico para pasarselo a GPT antes de decidir.\n\n"
            "Recomendacion si no estas seguro: responde CONTEXTO.\n\n"
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
            "Ahora responde una de estas opciones:\n"
            "APROBAR: aceptar el ciclo y permitir que siga.\n"
            "RECHAZAR: reabrir la ultima tarea para corregirla.\n"
            "PAUSAR: dejar la factoria detenida.\n"
            "CONTEXTO: pedir resumen tecnico para revisar con GPT."
        )
    elif status_key == "CYCLE_FAIL":
        text = (
            "SmartPyme Factory encontro un problema durante el ciclo.\n\n"
            "Respuesta recomendada: CONTEXTO o PAUSAR. No aprobar sin revisar evidencia."
        )
    elif status_key == "AUTO_PUSH_OK":
        text = (
            "SmartPyme Factory guardo cambios en el repo.\n\n"
            "Hay un nuevo commit para revisar. Si no sabes si aprobar, responde CONTEXTO."
        )
    elif status_key == "NO_TASK":
        text = (
            "SmartPyme Factory no encontro tareas pendientes.\n\n"
            "No tenes que responder nada salvo que quieras cargar una nueva tarea."
        )
    else:
        text = (
            "SmartPyme Factory envio una actualizacion.\n\n"
            "Si no sabes que decidir, responde CONTEXTO y pasa ese resumen a GPT."
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
