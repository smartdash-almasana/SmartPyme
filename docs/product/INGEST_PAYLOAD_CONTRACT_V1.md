# IngestPayload Contract v1 — SmartPyme

## Estado

HITO 07 — Contrato JSON/Pydantic de entrada del producto SmartPyme.

Este documento define el primer contrato soberano para convertir señales externas en una entrada procesable por SmartPyme.

Regla central:

```text
Nada entra al sistema como dato de negocio hasta convertirse en IngestPayload válido.
```

---

## 1. Propósito

`IngestPayload` es el objeto canónico de entrada entre la capa de plugins/conectores y la capa interpretativa de SmartPyme.

No representa verdad operacional.

Representa una señal recibida, normalizada mínimamente, trazable y lista para interpretación por AI Layer + validación Pydantic.

---

## 2. Ubicación conceptual

```text
Canal externo
→ Plugin / Conector
→ IngestPayload
→ AI Layer / Soft Core
→ Pydantic Domain Object
→ Hard Core determinístico
```

---

## 3. Principio de no contaminación

El `IngestPayload` no puede escribir en entidades canónicas.

Solo transporta:

```text
fuente,
contenido,
metadatos,
identidad de cliente,
evidencia primaria,
hints opcionales.
```

El Hard Core solo recibe objetos de dominio ya validados, no payloads crudos.

---

## 4. JSON Schema operativo v1

```json
{
  "payload_id": "ing_20260505_000001",
  "cliente_id": "cliente_demo_001",
  "source": {
    "channel": "whatsapp",
    "plugin_id": "plugin_whatsapp_v1",
    "external_message_id": "wamid.HBg...",
    "received_at": "2026-05-05T22:00:00Z"
  },
  "media": {
    "media_type": "pdf",
    "mime_type": "application/pdf",
    "filename": "factura_001.pdf",
    "size_bytes": 182044,
    "storage_uri": "storage://raw/cliente_demo_001/factura_001.pdf",
    "content_hash_sha256": "abc123"
  },
  "content": {
    "raw_text": "Texto extraído o transcripción si existe",
    "normalized_text": "Texto normalizado mínimo",
    "language": "es-AR",
    "segments": []
  },
  "structured_hints": {
    "document_type_hint": "invoice",
    "counterparty_hint": "Proveedor SA",
    "amount_hint": 125000.5,
    "currency_hint": "ARS",
    "date_hint": "2026-05-05"
  },
  "evidence": {
    "primary_evidence_uri": "storage://raw/cliente_demo_001/factura_001.pdf",
    "extraction_method": "ocr",
    "extraction_confidence": 0.87,
    "trace_id": "trace_000001"
  },
  "processing_policy": {
    "requires_owner_confirmation": false,
    "allowed_processing_modes": ["INTERPRET_ONLY", "EXTRACT_ENTITIES"],
    "sensitive": false
  },
  "status": "received"
}
```

---

## 5. Campos obligatorios

```text
payload_id
cliente_id
source.channel
source.plugin_id
source.received_at
media.media_type
content.raw_text OR media.storage_uri
evidence.primary_evidence_uri OR content.raw_text
status
```

---

## 6. Estados permitidos

```text
received
pre_normalized
ready_for_interpretation
interpretation_failed
blocked_needs_owner
rejected_invalid_payload
```

---

## 7. Canales permitidos v1

```text
owner_chat
whatsapp
telegram
email
excel
pdf
manual_upload
api
```

---

## 8. Tipos de media permitidos v1

```text
text
pdf
image
audio
video
spreadsheet
email_body
json
unknown
```

---

## 9. Invariantes

1. `cliente_id` es obligatorio en todo payload.
2. `tenant_id` no debe usarse como nombre de campo en contratos nuevos.
3. El payload conserva la fuente original mediante hash, URI o texto crudo.
4. `structured_hints` nunca son verdad operacional.
5. `extraction_confidence` informa incertidumbre, no autoriza persistencia canónica.
6. Ningún plugin puede saltar directo al Hard Core.
7. Todo payload sensible debe marcar `processing_policy.sensitive = true`.
8. Si falta evidencia primaria y falta texto crudo, el payload es inválido.

---

## 10. Modelo Pydantic esperado v1

```python
from pydantic import BaseModel, Field, model_validator
from typing import Literal

class SourceEnvelope(BaseModel):
    channel: Literal[
        "owner_chat", "whatsapp", "telegram", "email",
        "excel", "pdf", "manual_upload", "api"
    ]
    plugin_id: str
    external_message_id: str | None = None
    received_at: str

class MediaEnvelope(BaseModel):
    media_type: Literal[
        "text", "pdf", "image", "audio", "video",
        "spreadsheet", "email_body", "json", "unknown"
    ]
    mime_type: str | None = None
    filename: str | None = None
    size_bytes: int | None = None
    storage_uri: str | None = None
    content_hash_sha256: str | None = None

class ContentEnvelope(BaseModel):
    raw_text: str | None = None
    normalized_text: str | None = None
    language: str | None = "es-AR"
    segments: list[dict] = Field(default_factory=list)

class EvidenceEnvelope(BaseModel):
    primary_evidence_uri: str | None = None
    extraction_method: str | None = None
    extraction_confidence: float | None = None
    trace_id: str | None = None

class ProcessingPolicy(BaseModel):
    requires_owner_confirmation: bool = False
    allowed_processing_modes: list[str] = Field(default_factory=list)
    sensitive: bool = False

class IngestPayload(BaseModel):
    payload_id: str
    cliente_id: str
    source: SourceEnvelope
    media: MediaEnvelope
    content: ContentEnvelope
    structured_hints: dict = Field(default_factory=dict)
    evidence: EvidenceEnvelope
    processing_policy: ProcessingPolicy = Field(default_factory=ProcessingPolicy)
    status: Literal[
        "received", "pre_normalized", "ready_for_interpretation",
        "interpretation_failed", "blocked_needs_owner",
        "rejected_invalid_payload"
    ] = "received"

    @model_validator(mode="after")
    def require_content_or_storage(self):
        if not self.content.raw_text and not self.media.storage_uri:
            raise ValueError("IngestPayload requires raw_text or storage_uri")
        if not self.evidence.primary_evidence_uri and not self.content.raw_text:
            raise ValueError("IngestPayload requires evidence URI or raw_text")
        return self
```

---

## 11. Salida esperada hacia AI Layer

El AI Layer recibe `IngestPayload` y debe producir un objeto posterior tipado, por ejemplo:

```text
InvoiceCandidate
OwnerDemand
DocumentCandidate
TransactionCandidate
EvidenceCandidate
ClarificationRequest
```

El `IngestPayload` no es todavía una factura, una transacción ni un hallazgo.

---

## 12. Errores y bloqueos

```json
{
  "payload_id": "ing_20260505_000001",
  "status": "rejected_invalid_payload",
  "blocking_reason": "missing_cliente_id",
  "human_required": false
}
```

Escalar a humano solo si:

```text
- el payload contiene posible secreto o credencial;
- hay riesgo de pérdida de evidencia;
- se necesita autorización para investigar fuente externa;
- el dueño debe aclarar intención o alcance.
```

---

## 13. Cierre

`IngestPayload v1` es el primer contrato de producto que replica la disciplina de la factoría:

```text
entrada explícita,
cliente explícito,
evidencia primaria,
validación Pydantic,
no escritura canónica,
escalación humana mínima.
```
