"""Entrypoint FastAPI mínimo para SmartPyme API."""
from __future__ import annotations

from fastapi import FastAPI

from app.api.bem_webhook_router import router as bem_webhook_router
from app.api.diagnostic_router import router as diagnostic_router
from app.api.telegram_webhook_router import router as telegram_webhook_router
from app.api.v1.api import api_router

app = FastAPI(title="SmartPyme API")

app.include_router(api_router, prefix="/api/v1")
app.include_router(bem_webhook_router)
app.include_router(diagnostic_router)
app.include_router(telegram_webhook_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
