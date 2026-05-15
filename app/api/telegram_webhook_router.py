from __future__ import annotations

import os
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from app.adapters.telegram_adapter import TelegramAdapter

router = APIRouter()


def get_telegram_adapter() -> TelegramAdapter:
    return TelegramAdapter(
        telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN"),
        bem_workflow_id=os.getenv("BEM_WORKFLOW_ID"),
    )


def _sanitize_result(data: dict[str, Any]) -> dict[str, Any]:
    sanitized: dict[str, Any] = {}
    sensitive_fragments = ("token", "secret", "api_key", "password", "credential")
    for key, value in data.items():
        key_l = str(key).lower()
        if any(fragment in key_l for fragment in sensitive_fragments):
            continue
        sanitized[key] = value
    return sanitized


def _deliver_telegram_message(adapter: TelegramAdapter, result: dict[str, Any]) -> None:
    chat_id = result.get("telegram_user_id")
    text = result.get("message")
    if chat_id is None or not isinstance(text, str) or not text.strip():
        return
    try:
        adapter._safe_send_message(chat_id, text)
    except Exception:
        return


@router.post("/webhook/telegram")
def telegram_webhook(
    update: dict[str, Any],
    adapter: TelegramAdapter = Depends(get_telegram_adapter),
) -> dict[str, Any]:
    if not isinstance(update, dict):
        raise HTTPException(status_code=400, detail="invalid update payload")
    try:
        result = adapter.handle_update(update)
    except Exception as exc:
        raise HTTPException(status_code=500, detail="telegram webhook processing error") from exc

    if not isinstance(result, dict):
        raise HTTPException(status_code=502, detail="invalid adapter response")

    _deliver_telegram_message(adapter, result)

    return {"status": "ok", "result": _sanitize_result(result)}
