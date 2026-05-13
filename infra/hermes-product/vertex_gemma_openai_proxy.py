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
        text = getattr(response, "text", None)
        if not isinstance(text, str) or not text.strip():
            raise HTTPException(status_code=502, detail="empty Vertex response")
        return text.strip()
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
    if request.stream:
        raise HTTPException(status_code=400, detail="streaming is not supported")
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
