from __future__ import annotations

import json
import os
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
GATE = REPO / "factory" / "control" / "AUDIT_GATE.md"
STATUS = REPO / "factory" / "control" / "FACTORY_STATUS.md"
OFFSET_FILE = REPO / "factory" / "control" / ".telegram_control_offset"

BUTTONS = {
    "GO": "/run",
    "STOP": "/stop",
    "FIX": "/retry",
    "STATUS": "/status",
}


def env(name: str) -> str:
    return os.getenv(name, "").strip()


def token() -> str:
    value = env("TELEGRAM_BOT_TOKEN")
    if not value:
        raise RuntimeError("missing TELEGRAM_BOT_TOKEN")
    return value


def allowed_chat_id() -> str:
    value = env("TELEGRAM_CHAT_ID")
    if not value:
        raise RuntimeError("missing TELEGRAM_CHAT_ID")
    return value


def api(method: str, payload: dict | None = None) -> dict:
    data = None
    if payload is not None:
        data = urllib.parse.urlencode(payload).encode("utf-8")
    req = urllib.request.Request(
        "https://api.telegram.org/bot" + token() + "/" + method,
        data=data,
        method="POST" if data else "GET",
    )
    with urllib.request.urlopen(req, timeout=35) as resp:
        return json.loads(resp.read().decode("utf-8"))


def control_keyboard() -> str:
    return json.dumps(
        {
            "inline_keyboard": [
                [
                    {"text": "▶ GO", "callback_data": "GO"},
                    {"text": "⛔ STOP", "callback_data": "STOP"},
                ],
                [
                    {"text": "🔁 FIX", "callback_data": "FIX"},
                    {"text": "📊 STATUS", "callback_data": "STATUS"},
                ],
            ]
        }
    )


def send(text: str, buttons: bool = True) -> None:
    payload = {"chat_id": allowed_chat_id(), "text": text[:3900]}
    if buttons:
        payload["reply_markup"] = control_keyboard()
    api("sendMessage", payload)


def answer_callback(callback_id: str) -> None:
    api("answerCallbackQuery", {"callback_query_id": callback_id})


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_offset() -> int:
    try:
        return int(OFFSET_FILE.read_text().strip())
    except Exception:
        return 0


def write_offset(value: int) -> None:
    OFFSET_FILE.parent.mkdir(parents=True, exist_ok=True)
    OFFSET_FILE.write_text(str(value), encoding="utf-8")


def gate_status() -> str:
    if not GATE.exists():
        return "APPROVED"
    for line in GATE.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("status:"):
            return line.split(":", 1)[1].strip().upper()
    return "UNKNOWN"


def write_gate(status: str, reason: str) -> None:
    GATE.parent.mkdir(parents=True, exist_ok=True)
    previous = gate_status()
    GATE.write_text(
        "# AUDIT GATE\n\n"
        f"status: {status}\n"
        f"updated_at: {now()}\n"
        f"updated_by: telegram_control\n"
        f"previous_status: {previous}\n"
        f"reason: {reason}\n",
        encoding="utf-8",
    )


def status_text() -> str:
    lines = ["SmartPyme Factory", f"gate: {gate_status()}"]
    if STATUS.exists():
        text = STATUS.read_text(encoding="utf-8", errors="replace")
        for line in text.splitlines():
            if line.startswith(("updated_at:", "last_cycle_result:", "audit_gate:", "last_error:")):
                lines.append(line)
    return "\n".join(lines)


def handle_command(text: str) -> str:
    cmd = text.strip().split()[0].lower() if text.strip() else ""
    if cmd in {"/run", "/start", "/approve", "/go", "/seguir"}:
        write_gate("APPROVED", cmd)
        return "OK: gate=APPROVED. La factoría puede ejecutar el próximo ciclo."
    if cmd in {"/stop", "/block", "/kill", "/frenar"}:
        write_gate("BLOCKED", cmd)
        return "OK: gate=BLOCKED. La factoría queda frenada."
    if cmd in {"/retry", "/reject", "/fix", "/reprocesar"}:
        write_gate("REJECTED", cmd)
        return "OK: gate=REJECTED. El runner reabrirá la última tarea."
    if cmd in {"/status", "/state", "/s", "/estado"}:
        return status_text()
    if cmd in {"/help", "help", "/panel"}:
        return "SmartPyme Control\n\nUsá los botones o comandos: /go, /kill, /fix, /s"
    return "Comando no reconocido. Usá los botones o /panel."


def handle_callback(data: str) -> str:
    command = BUTTONS.get(data, "")
    if not command:
        return "Botón no reconocido."
    return handle_command(command)


def poll_once() -> None:
    offset = read_offset()
    payload = {"timeout": 25, "allowed_updates": json.dumps(["message", "callback_query"])}
    if offset:
        payload["offset"] = offset
    result = api("getUpdates", payload)
    for update in result.get("result", []):
        write_offset(int(update["update_id"]) + 1)

        callback = update.get("callback_query")
        if callback:
            message = callback.get("message") or {}
            chat = message.get("chat") or {}
            chat_id = str(chat.get("id", ""))
            if chat_id != allowed_chat_id():
                continue
            answer_callback(callback.get("id", ""))
            reply = handle_callback(callback.get("data", ""))
            send(reply)
            continue

        message = update.get("message") or {}
        chat = message.get("chat") or {}
        chat_id = str(chat.get("id", ""))
        text = message.get("text", "")
        if chat_id != allowed_chat_id():
            continue
        reply = handle_command(text)
        send(reply)


def main() -> None:
    send("SmartPyme Control activo. Usá los botones.")
    while True:
        try:
            poll_once()
        except Exception as exc:
            print(f"TELEGRAM_CONTROL_ERROR {type(exc).__name__}: {exc}", flush=True)
            time.sleep(10)


if __name__ == "__main__":
    main()
