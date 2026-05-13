from __future__ import annotations

import os
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="SmartPyme Vertex Gemma Proxy")


class ChatMessage(BaseModel):
    role: str
    content: str | list[dict[str, Any]] | None = None


class ChatCompletionRequest(BaseModel):
    model: str = Field(default="gemma-4-26b-a4b-it-maas")
    messages: list[ChatMessage]
    temperature: float | None = 0.1
    max_tokens: int | None = 800
    max_completion_tokens: int | None = None
    stream: bool | None = False


def _message_text(content: str | list[dict[str, Any]] | None) -> str:
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    parts: list[str] = []
    for item in content:
        if not isinstance(item, dict):
            continue
        if item.get("type") == "text" and isinstance(item.get("text"), str):
            parts.append(item["text"])
    return "\n".join(parts)


def _build_prompt(messages: list[ChatMessage]) -> str:
    chunks: list[str] = []
    for message in messages:
        text = _message_text(message.content).strip()
        if not text:
            continue
        chunks.append(f"<{message.role}>\n{text}\n</{message.role}>")
    return "\n\n".join(chunks).strip()


def _extract_text_from_mapping(value: Any) -> str:
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, list):
        chunks = [_extract_text_from_mapping(item) for item in value]
        return "\n".join(chunk for chunk in chunks if chunk).strip()
    if not isinstance(value, dict):
        return ""

    direct = value.get("text")
    if isinstance(direct, str) and direct.strip():
        return direct.strip()

    chunks: list[str] = []
    for key in ("candidates", "content", "parts"):
        text = _extract_text_from_mapping(value.get(key))
        if text:
            chunks.append(text)
    return "\n".join(chunks).strip()


def _extract_vertex_text(response: Any) -> str:
    """Extract text from google-genai responses across SDK/model variants."""

    text = getattr(response, "text", None)
    if isinstance(text, str) and text.strip():
        return text.strip()

    candidates = getattr(response, "candidates", None) or []
    for candidate in candidates:
        content = getattr(candidate, "content", None)
        parts = getattr(content, "parts", None) if content is not None else None
        if not parts:
            continue
        extracted: list[str] = []
        for part in parts:
            part_text = getattr(part, "text", None)
            if isinstance(part_text, str) and part_text.strip():
                extracted.append(part_text.strip())
        if extracted:
            return "\n".join(extracted).strip()

    for dump_name in ("model_dump", "to_dict"):
        dump_fn = getattr(response, dump_name, None)
        if not callable(dump_fn):
            continue
        try:
            dumped = dump_fn()
        except Exception:
            continue
        text = _extract_text_from_mapping(dumped)
        if text:
            return text

    return ""


def _generate_vertex(prompt: str, request: ChatCompletionRequest) -> str:
    try:
        from google import genai
        from google.genai import types
    except ImportError as exc:
        raise HTTPException(status_code=503, detail="google-genai is not installed") from exc

    project = os.getenv("GOOGLE_CLOUD_PROJECT")
    location = os.getenv("HERMES_PRODUCT_VERTEX_LOCATION") or "global"
    model = os.getenv("HERMES_PRODUCT_VERTEX_MODEL_ID") or request.model
    if not project:
        raise HTTPException(status_code=503, detail="GOOGLE_CLOUD_PROJECT is required")

    try:
        client = genai.Client(vertexai=True, project=project, location=location)
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=request.temperature,
                max_output_tokens=request.max_completion_tokens or request.max_tokens or 800,
            ),
        )
        text = _extract_vertex_text(response)
        if not text:
            raise HTTPException(status_code=502, detail="empty Vertex response")
        return text
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Vertex request failed: {exc}") from exc


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/v1/models")
def models() -> dict[str, Any]:
    model = os.getenv("HERMES_PRODUCT_VERTEX_MODEL_ID") or "gemma-4-26b-a4b-it-maas"
    return {"object": "list", "data": [{"id": model, "object": "model"}]}


@app.post("/v1/chat/completions")
def chat_completions(request: ChatCompletionRequest) -> dict[str, Any]:
    # Hermes can still send stream=true even when display.streaming is disabled.
    # The Vertex Gemma backend is non-streaming, so this proxy deliberately
    # downgrades streaming requests to a normal OpenAI-compatible response
    # instead of failing Telegram with HTTP 400.
    prompt = _build_prompt(request.messages)
    if not prompt:
        raise HTTPException(status_code=400, detail="messages are required")
    content = _generate_vertex(prompt, request)
    return {
        "id": "smartpyme-vertex-gemma",
        "object": "chat.completion",
        "model": request.model,
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": content},
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
    }
