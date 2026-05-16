<!--
FUENTE_ORIGINAL: docs/product/OWNER_DECISION_CONTRACT_V1.md
ESTADO: normalizado_minimo
NORMALIZACION: sección 7 "CAMBIOS FUTUROS" — removida referencia a "flujo soberano de factoría" y "AUDIT_GATE" (mecanismos de factoría irrelevantes para PymIA); texto de sección simplificado a invariante de producto
-->

# OWNER DECISION CONTRACT — V1

**Fecha de congelación:** 2026‑05‑05  
**Límite de validez:** Hasta que se modifique el flujo de decisiones de dueño en SmartPyme.  
**Propósito:** Formalizar el contrato OwnerDecision/DecisionRecord v1 como documento de producto, estableciendo invariantes y estructura JSON para registros de decisión dentro de SmartPyme.

---

## 1. INTRODUCCIÓN

SmartPyme **no decide**; solo propone.  
Cualquier acción que tenga impacto en el sistema (creación de recursos, aprobación de gastos, cambios de configuración, despliegues, escalaciones) debe estar respaldada por un **DecisionRecord** emitido por un dueño o actor autorizado.

Este contrato define el formato mínimo y los invariantes del registro de decisión (OwnerDecision/DecisionRecord v1) utilizado en la cadena de evidencia.

---

## 2. ESTRUCTURA JSON

```json
{
  "decision_id": "string",
  "cliente_id": "string",
  "owner_id": "string",
  "actor_role": "owner|admin|auditor|operator|guest",
  "linked_case_id": "string|null",
  "linked_evidence_chain_id": "string|null",
  "linked_report_id": "string|null",
  "decision_type": "APPROVE|REJECT|REQUEST_CLARIFICATION|AUTHORIZE_ACTION|STOP|DEFER",
  "decision_scope": "string",
  "decision_text": "string",
  "authorized_actions": ["string"],
  "rejected_actions": ["string"],
  "conditions": ["string"],
  "risk_acknowledgement": "string|null",
  "created_at": "2026-05-05T12:00:00Z",
  "valid_until": "2026-05-05T23:59:59Z|null",
  "source_channel": "telegram|web|cli|email|slack|other",
  "audit_trail": [
    {
      "timestamp": "2026-05-05T12:00:00Z",
      "event": "record_created|decision_made|action_executed|revoked",
      "actor_id": "string",
      "notes": "string|null"
    }
  ]
}
```

---

## 3. CAMPOS OBLIGATORIOS Y SEMÁNTICA

### 3.1. decision_id
- Identificador único de la decisión, generado por el sistema (UUID v4 o prefijo + timestamp).
- Formato libre, pero debe ser único dentro del `cliente_id`.

### 3.2. cliente_id (obligatorio)
- Identificador del cliente al que pertenece la decisión.
- **No confundir con `tenant_id`**, que está prohibido en este contexto.
- Proporciona contexto de negocio y aislamiento multi‑cliente.

### 3.3. owner_id / actor_id
- Identificador del dueño o actor que emite la decisión.
- Puede ser un usuario interno, un sistema externo o un rol automatizado.

### 3.4. actor_role
- Rol del actor en el momento de la decisión.
- Valores predefinidos:
  - `owner` → dueño real del recurso o proceso.
  - `admin` → administrador con delegación temporal.
  - `auditor` → auditor independiente (solo revisión, no ejecución).
  - `operator` → operador técnico (ejecuta acciones autorizadas).
  - `guest` → invitado con capacidad de consulta (sin decisión).

### 3.5. linked_case_id (opcional)
- Enlace a un caso operativo (`OperationalCase`) si la decisión responde a un incidente, solicitud o tarea registrada.

### 3.6. linked_evidence_chain_id (opcional)
- Enlace a una cadena de evidencia (`EvidenceChain`) que justifica la decisión.
- La evidencia **no equivale a autorización**; solo proporciona contexto.

### 3.7. linked_report_id (opcional)
- Enlace a un reporte (`Report`) generado previamente (análisis, auditoría, diagnóstico).

### 3.8. decision_type
- **APPROVE** → Aprobación explícita de una acción o propuesta.
- **REJECT** → Rechazo explícito de una acción o propuesta.
- **REQUEST_CLARIFICATION** → Solicitud de aclaración antes de decidir (no es aprobación).
- **AUTHORIZE_ACTION** → Autorización para ejecutar una acción concreta (puede incluir condiciones).
- **STOP** → Orden de detener un proceso o acción en curso.
- **DEFER** → Postergación de la decisión a una fecha futura (se debe indicar `valid_until`).

### 3.9. decision_scope
- Descripción textual del alcance de la decisión.

### 3.10. decision_text
- Texto libre que explica los motivos, consideraciones y contexto de la decisión.

### 3.11. authorized_actions
- Lista de acciones específicas que el actor autoriza.
- Cada acción debe ser suficientemente específica para evitar ambigüedades.

### 3.12. rejected_actions
- Lista de acciones que el actor rechaza explícitamente.

### 3.13. conditions
- Condiciones que deben cumplirse para que la decisión sea efectiva.

### 3.14. risk_acknowledgement (opcional)
- Reconocimiento explícito de riesgos asociados a la decisión (firma textual o hash).

### 3.15. created_at
- Fecha‑hora de creación del registro (ISO 8601, UTC).

### 3.16. valid_until (opcional)
- Fecha‑hora de vencimiento de la decisión (ISO 8601, UTC).
- Después de esta fecha, la decisión se considera obsoleta y no puede usarse para autorizar acciones nuevas.

### 3.17. source_channel
- Canal por el que se recibió o emitió la decisión (telegram, web, cli, email, slack, other).

### 3.18. audit_trail
- Lista de eventos que documentan el ciclo de vida de la decisión.
- Cada entrada incluye timestamp, tipo de evento, actor y notas opcionales.

---

## 4. INVARIANTES

1. **SmartPyme no decide; propone.**  
   El sistema puede presentar opciones, calcular riesgos, generar evidencia y recomendar acciones, pero nunca tomar una decisión final sin un DecisionRecord válido.

2. **El dueño o actor autorizado decide.**  
   Solo un actor con rol `owner`, `admin` o `operator` (según delegación) puede emitir decisiones de tipo APPROVE, REJECT, AUTHORIZE_ACTION o STOP.

3. **Ninguna acción se ejecuta sin DecisionRecord válido.**  
   Cualquier modificación de estado, creación de recursos o despliegue que requiera autorización debe tener un DecisionRecord vinculado en la cadena de evidencia.

4. **Evidencia no equivale a autorización.**  
   Una cadena de evidencia (EvidenceChain) proporciona contexto y justificación, pero no sustituye un DecisionRecord de tipo APPROVE o AUTHORIZE_ACTION.

5. **Aclaración no equivale a aprobación.**  
   Una decisión de tipo REQUEST_CLARIFICATION no autoriza ninguna acción; solo solicita información adicional.

6. **`tenant_id` prohibido.**  
   El campo `tenant_id` no debe aparecer en el DecisionRecord; el aislamiento multi‑tenant se gestiona mediante `cliente_id`.

7. **`cliente_id` obligatorio.**  
   Todas las decisiones deben estar asociadas a un cliente identificable.

---

## 5. INTEGRACIÓN CON LA CADENA DE EVIDENCIA

Un DecisionRecord puede referenciarse en:

- **EvidenceChain** → campo `linked_decision_id` dentro de `evidence_links`.
- **OperationalCase** → campo `decision_record_id` dentro de `resolution`.
- **Job** → campo `owner_decision_id` cuando el estado es `PENDING_OWNER_CONFIRMATION`.

La presencia de un DecisionRecord con `decision_type: APPROVE` o `AUTHORIZE_ACTION` es condición necesaria para que un Job pase de `PENDING_OWNER_CONFIRMATION` a `RUNNING`.

---

## 6. EJEMPLO DE USO

```json
{
  "decision_id": "DEC_20260505120000_ABC123",
  "cliente_id": "cliente_empresa_x",
  "owner_id": "usuario_admin_001",
  "actor_role": "admin",
  "linked_case_id": "CASE_456",
  "linked_evidence_chain_id": "EVID_CHAIN_789",
  "decision_type": "AUTHORIZE_ACTION",
  "decision_scope": "Creación de Job con condiciones OK",
  "decision_text": "Se autoriza la creación del Job XYZ porque cumple las condiciones de suficiencia determinística y el riesgo operativo es bajo.",
  "authorized_actions": ["create_job", "allocate_budget_1000"],
  "rejected_actions": [],
  "conditions": ["budget_available", "valid_until 2026-05-06"],
  "risk_acknowledgement": "Se reconoce riesgo bajo de desfase presupuestario.",
  "created_at": "2026-05-05T12:00:00Z",
  "valid_until": "2026-05-06T23:59:59Z",
  "source_channel": "telegram",
  "audit_trail": [
    {
      "timestamp": "2026-05-05T11:58:00Z",
      "event": "record_created",
      "actor_id": "system_evidence_builder",
      "notes": "Generado automáticamente tras revisión de condiciones OK."
    },
    {
      "timestamp": "2026-05-05T12:00:00Z",
      "event": "decision_made",
      "actor_id": "usuario_admin_001",
      "notes": "Decisión firmada vía Telegram."
    }
  ]
}
```

---

**Última revisión de coherencia:** 2026‑05‑05
