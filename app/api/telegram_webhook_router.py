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
    blocked_tokens = ("token", "api_key", "secret", "password")
    for key, value in data.items():
        key_l = str(key).lower()
        if any(blocked in key_l for blocked in blocked_tokens):
            continue
        sanitized[key] = value
    return sanitized


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

    return {"status": "ok", "result": _sanitize_result(result)}
