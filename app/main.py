"""Entrypoint FastAPI mínimo para SmartPyme API."""
from __future__ import annotations

from fastapi import FastAPI

from app.api.v1.api import api_router

app = FastAPI(title="SmartPyme API")

app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
