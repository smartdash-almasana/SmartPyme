"""Planta conversacional investigativa de SmartPyme.

Core mínimo sin red, sin LLM y sin persistencia.
"""
from __future__ import annotations

from app.laboratorio_pyme.conversation.engine import procesar_mensaje
from app.laboratorio_pyme.conversation.state import ConversationState, crear_estado_inicial

__all__ = [
    "ConversationState",
    "crear_estado_inicial",
    "procesar_mensaje",
]
