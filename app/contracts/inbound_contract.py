"""
Contratos Pydantic — Capa 00: Canal y Entrada Cruda
TS_000_001_CONTRATO_RAW_INBOUND_EVENT

Modelo de datos mínimo para representar RawInboundEvent.

Principios:
  - Capa 00 registra sin interpretar.
  - El contenido crudo no se modifica.
  - Todo evento de entrada produce exactamente un RawInboundEvent.
  - event_id es único e inmutable.
  - received_at es el momento de recepción en el canal.

Documento rector:
  docs/product/SMARTPYME_CAPA_00_CANAL_ENTRADA_CRUDA.md
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field, model_validator


# ---------------------------------------------------------------------------
# Tipos literales
# ---------------------------------------------------------------------------

Channel = Literal["telegram", "whatsapp", "web", "api", "email", "cli", "otro"]
"""Canal de origen del evento."""

SourceType = Literal["human", "system", "file", "webhook"]
"""Tipo de fuente del evento."""

RawContentType = Literal["text", "file", "audio", "image", "document", "json", "otro"]
"""Tipo de contenido crudo recibido."""

InboundProcessingStatus = Literal["PENDING", "DELIVERED", "FAILED"]
"""Estado de procesamiento del evento."""


# ---------------------------------------------------------------------------
# RawInboundEvent
# ---------------------------------------------------------------------------


class RawInboundEvent(BaseModel):
    """
    Evento de entrada cruda recibido por Capa 00.

    Registra cualquier entrada desde cualquier canal sin interpretación de negocio.
    No clasifica intención, no detecta síntomas, no diagnostica.

    Validaciones cruzadas:
      - Al menos uno de raw_text, raw_file_ref, raw_audio_ref, raw_image_ref
        debe existir, o metadata debe ser no vacío.
      - raw_file_size_bytes no puede ser negativo.
      - Si raw_content_type == "text", raw_text debe existir.
      - Si raw_content_type == "file" o "document", raw_file_ref debe existir.
      - Si raw_content_type == "audio", raw_audio_ref debe existir.
      - Si raw_content_type == "image", raw_image_ref debe existir.
    """

    event_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="UUID único del evento. Se autogenera si no se pasa.",
    )
    channel: Channel = Field(
        ...,
        description="Canal de origen: telegram, whatsapp, web, api, email, cli, otro.",
    )
    source_type: SourceType = Field(
        ...,
        description="Tipo de fuente: human, system, file, webhook.",
    )
    received_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp UTC de recepción. Se autogenera si no se pasa.",
    )
    conversation_id: Optional[str] = Field(
        default=None,
        description="ID de conversación si existe en el canal.",
    )
    user_id: Optional[str] = Field(
        default=None,
        description="ID del usuario en el canal.",
    )
    cliente_id: Optional[str] = Field(
        default=None,
        description="ID del cliente/tenant si está disponible. Capa 01 lo resuelve si falta.",
    )
    raw_content_type: RawContentType = Field(
        ...,
        description="Tipo de contenido crudo: text, file, audio, image, document, json, otro.",
    )
    raw_text: Optional[str] = Field(
        default=None,
        description="Texto crudo del mensaje. Requerido si raw_content_type='text'.",
    )
    raw_file_ref: Optional[str] = Field(
        default=None,
        description=(
            "Referencia al archivo recibido (ruta, URI, ID de storage). "
            "Requerido si raw_content_type='file' o 'document'."
        ),
    )
    raw_file_name: Optional[str] = Field(
        default=None,
        description="Nombre original del archivo.",
    )
    raw_file_type: Optional[str] = Field(
        default=None,
        description="Extensión o MIME type del archivo.",
    )
    raw_file_size_bytes: Optional[int] = Field(
        default=None,
        description="Tamaño del archivo en bytes. No puede ser negativo.",
    )
    raw_audio_ref: Optional[str] = Field(
        default=None,
        description="Referencia al audio recibido. Requerido si raw_content_type='audio'.",
    )
    raw_image_ref: Optional[str] = Field(
        default=None,
        description="Referencia a la imagen recibida. Requerido si raw_content_type='image'.",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Metadata adicional del canal. Preservada sin modificar.",
    )
    processing_status: InboundProcessingStatus = Field(
        default="PENDING",
        description="Estado de procesamiento: PENDING (default), DELIVERED, FAILED.",
    )

    @model_validator(mode="after")
    def validate_content_presence_and_consistency(self) -> "RawInboundEvent":
        """
        Valida que:
        1. Haya al menos un contenido o metadata no vacía.
        2. raw_file_size_bytes no sea negativo.
        3. El contenido requerido exista según raw_content_type.
        """
        # Validación 1: al menos un contenido o metadata no vacía
        has_content = any([
            self.raw_text is not None,
            self.raw_file_ref is not None,
            self.raw_audio_ref is not None,
            self.raw_image_ref is not None,
            bool(self.metadata),
        ])
        if not has_content:
            raise ValueError(
                "RawInboundEvent debe tener al menos uno de: "
                "raw_text, raw_file_ref, raw_audio_ref, raw_image_ref, "
                "o metadata no vacío."
            )

        # Validación 2: raw_file_size_bytes no negativo
        if self.raw_file_size_bytes is not None and self.raw_file_size_bytes < 0:
            raise ValueError(
                "raw_file_size_bytes no puede ser negativo."
            )

        # Validación 3: consistencia entre raw_content_type y campos de contenido
        ctype = self.raw_content_type

        if ctype == "text" and self.raw_text is None:
            raise ValueError(
                "raw_content_type='text' requiere raw_text."
            )

        if ctype in ("file", "document") and self.raw_file_ref is None:
            raise ValueError(
                f"raw_content_type='{ctype}' requiere raw_file_ref."
            )

        if ctype == "audio" and self.raw_audio_ref is None:
            raise ValueError(
                "raw_content_type='audio' requiere raw_audio_ref."
            )

        if ctype == "image" and self.raw_image_ref is None:
            raise ValueError(
                "raw_content_type='image' requiere raw_image_ref."
            )

        return self
