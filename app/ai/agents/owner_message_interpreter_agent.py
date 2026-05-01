from __future__ import annotations

import asyncio
import logging
import os
from typing import Any

from pydantic import ValidationError

from app.ai.schemas.owner_message_interpretation import OwnerMessageInterpretation

logger = logging.getLogger(__name__)

DEFAULT_MODEL_NAME = "openai:gpt-4o-mini"

OWNER_MESSAGE_INTERPRETER_PROMPT = """
Sos un interprete blando de mensajes del dueno de una pyme.

Tu tarea:
- interpretar la intencion operativa del mensaje
- extraer entidades mencionadas
- extraer variables mencionadas
- extraer evidencia mencionada
- registrar dudas o faltantes

Reglas:
- no tomes decisiones
- no diagnostiques de forma definitiva
- no inventes datos
- no generes hallazgos
- no confirmes contexto operativo
- devolve solo una estructura compatible con OwnerMessageInterpretation

El LLM interpreta. Pydantic valida. El core decide. El dueno confirma.
""".strip()


_REQUIRED_API_KEY_NAMES = (
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "GEMINI_API_KEY",
    "GOOGLE_API_KEY",
)


def _load_agent_class() -> type[Any] | None:
    try:
        from pydantic_ai import Agent  # type: ignore
    except Exception:
        return None
    return Agent


def _has_llm_credentials() -> bool:
    return any(os.getenv(name) for name in _REQUIRED_API_KEY_NAMES)


def _build_agent(agent_class: type[Any], model_name: str) -> Any:
    try:
        return agent_class(
            model_name,
            output_type=OwnerMessageInterpretation,
            system_prompt=OWNER_MESSAGE_INTERPRETER_PROMPT,
        )
    except TypeError:
        return agent_class(
            model_name,
            result_type=OwnerMessageInterpretation,
            system_prompt=OWNER_MESSAGE_INTERPRETER_PROMPT,
        )


def create_owner_message_interpreter_agent(
    model_name: str | None = None,
) -> Any | None:
    agent_class = _load_agent_class()
    if agent_class is None:
        return None

    if not _has_llm_credentials():
        return None

    try:
        return _build_agent(agent_class, model_name or DEFAULT_MODEL_NAME)
    except Exception as exc:
        logger.debug("OwnerMessageInterpreterAgent creation failed: %s", exc)
        return None


def _coerce_interpretation(raw_output: Any) -> OwnerMessageInterpretation | None:
    candidate = getattr(raw_output, "output", raw_output)
    candidate = getattr(candidate, "data", candidate)

    if isinstance(candidate, OwnerMessageInterpretation):
        return candidate

    try:
        return OwnerMessageInterpretation.model_validate(candidate)
    except (TypeError, ValueError, ValidationError) as exc:
        logger.debug("OwnerMessageInterpretation validation failed: %s", exc)
        return None


async def interpret_owner_message_with_ai_async(
    message: str,
    *,
    model_name: str | None = None,
) -> OwnerMessageInterpretation | None:
    if not message.strip():
        return None

    agent = create_owner_message_interpreter_agent(model_name=model_name)
    if agent is None:
        return None

    user_prompt = f"Mensaje del dueno de pyme:\n{message.strip()}"

    try:
        result = await agent.run(user_prompt)
    except Exception as exc:
        logger.debug("OwnerMessageInterpreterAgent run failed: %s", exc)
        return None

    return _coerce_interpretation(result)


def interpret_owner_message_with_ai(
    message: str,
    *,
    model_name: str | None = None,
) -> OwnerMessageInterpretation | None:
    try:
        return asyncio.run(
            interpret_owner_message_with_ai_async(message=message, model_name=model_name)
        )
    except RuntimeError as exc:
        logger.debug("OwnerMessageInterpreterAgent sync execution failed: %s", exc)
        return None
