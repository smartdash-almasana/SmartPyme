# ADR-002: Persistencia de la Conversación Clínica SmartPyme

## Estado

**ACEPTADO** — Mayo 2026

---

## Contexto

La capa conversacional clínica de SmartPyme (`app/laboratorio_pyme/conversation/`) está operativa y verde:

- Core determinístico sin LLM: `engine.py`, `state.py`, `hypotheses.py`, `questions.py`
- Puerto de persistencia: `ConversationRepository` (ABC)
- Serialización pura: `conversation_state_to_dict` / `conversation_state_from_dict`
- Adapter in-memory: `InMemoryConversationRepository`
- Orquestador: `ConversationService`
- 43 tests verdes, sin dependencias externas

El sistema conversa con el dueño de PyME, activa hipótesis clínicas, pide evidencia y detecta dimensión (dinero / tiempo / ambas) sin emitir diagnóstico definitivo.

El problema a resolver: **cómo persistir la historia clínica conversacional por cliente sin acoplar el core a Supabase ni romper el diseño actual.**

---

## Decisión

### 1. El core conversacional permanece determinístico y sin DB

`conversation/` no importa ni conoce Supabase, SQL ni ningún adapter concreto.  
El engine opera sobre `ConversationState` en memoria. La persistencia es responsabilidad exclusiva del adapter inyectado.

### 2. `ConversationService` es el único punto de orquestación

```
repository.get_or_create_active_session(cliente_id)
  → procesar_mensaje(state, mensaje)
    → repository.save_active_session(state)
      → return result
```

Ningún otro componente llama directamente al engine con estado persistido.

### 3. `ConversationRepository` es el port. Supabase es un adapter futuro

```
ConversationRepository (ABC, ports.py)
    ↑
    InMemoryConversationRepository   ← tests, desarrollo local
    SupabaseConversationRepository   ← producción (a implementar)
```

El dominio depende del port. El port no depende de Supabase.

### 4. La DB guarda historia clínica operacional. No decide

La base de datos es un store pasivo. No activa hipótesis, no genera preguntas, no emite diagnósticos.  
Toda la lógica clínica vive en el core Python.

### 5. No guardar solo un blob opaco del ConversationState

Guardar el estado completo como un único JSONB opaco impide:
- consultar historial por cliente sin deserializar
- auditar hipótesis activas
- filtrar por fase o dimensión
- construir reportes clínicos

Se adopta modelo normalizado con snapshot auxiliar opcional.

### 6. Reconstrucción de `ConversationState` vía `serialization.py`

El adapter Supabase reconstruirá el estado desde tablas normalizadas usando `conversation_state_from_dict`. El proceso es determinístico y no requiere LLM.

### 7. Sin LLM, sin Prefect, sin Hermes en esta capa

La capa conversacional clínica es infraestructura de dominio puro.  
Hermes, Prefect y la IA tipada operan **por encima** del core, nunca dentro de él.

---

## Modelo de datos recomendado

```sql
-- Sesión activa por cliente
conversation_sessions (
    id              UUID PRIMARY KEY,
    cliente_id      TEXT NOT NULL,
    fase            TEXT NOT NULL,          -- FaseConversacion.value
    dolor_principal TEXT,
    dimension_foco  TEXT,
    ultima_pregunta TEXT,
    created_at      TIMESTAMPTZ,
    updated_at      TIMESTAMPTZ
)

-- Historial de mensajes del dueño
conversation_messages (
    id          UUID PRIMARY KEY,
    session_id  UUID REFERENCES conversation_sessions,
    orden       INT NOT NULL,
    contenido   TEXT NOT NULL,
    created_at  TIMESTAMPTZ
)

-- Hipótesis activadas con su peso y evidencia
conversation_hypotheses (
    id                    UUID PRIMARY KEY,
    session_id            UUID REFERENCES conversation_sessions,
    codigo                TEXT NOT NULL,
    nombre                TEXT NOT NULL,
    peso                  NUMERIC(5,4),
    dimension             TEXT,
    evidencia_faltante    JSONB,   -- list[str]
    evidencia_confirmada  JSONB,   -- list[str]
    subsistemas_afectados JSONB    -- list[str]
)

-- Evidencia requerida y confirmada por sesión
conversation_evidence (
    id          UUID PRIMARY KEY,
    session_id  UUID REFERENCES conversation_sessions,
    item        TEXT NOT NULL,
    estado      TEXT NOT NULL,   -- 'requerida' | 'confirmada'
    created_at  TIMESTAMPTZ
)

-- Preguntas formuladas (deduplicación y auditoría)
conversation_questions (
    id          UUID PRIMARY KEY,
    session_id  UUID REFERENCES conversation_sessions,
    orden       INT NOT NULL,
    pregunta    TEXT NOT NULL,
    created_at  TIMESTAMPTZ
)

-- Snapshot completo opcional (recovery rápido)
conversation_state_snapshots (
    id          UUID PRIMARY KEY,
    session_id  UUID REFERENCES conversation_sessions,
    snapshot    JSONB NOT NULL,   -- conversation_state_to_dict(state)
    created_at  TIMESTAMPTZ
)
```

---

## Normalizado vs JSONB

| Campo | Estrategia | Razón |
|---|---|---|
| `fase`, `dolor_principal`, `dimension_foco` | **Tabla normalizada** | Se filtra y consulta por ellos |
| `historial_mensajes` | **Tabla propia** (`conversation_messages`) | Orden importa, paginable |
| `historial_preguntas` | **Tabla propia** (`conversation_questions`) | Deduplicación requiere lookup |
| `evidencia_requerida` / `evidencia_confirmada` | **Tabla propia** (`conversation_evidence`) | Estado cambia individualmente |
| `hipotesis_activas[].evidencia_faltante` | **JSONB dentro de `conversation_hypotheses`** | Lista interna, no se consulta por separado |
| `hipotesis_activas[].subsistemas_afectados` | **JSONB dentro de `conversation_hypotheses`** | Referencial, no filtrable |
| `datos_conocidos` | **Derivado** de `conversation_evidence` al reconstruir | Redundante con evidencia confirmada |
| `incertidumbres` | **JSONB en snapshot** | Lista libre, no estructurada |
| Snapshot completo | **JSONB en `conversation_state_snapshots`** | Recovery de emergencia, no fuente de verdad |

**Regla:** todo lo que se filtra o actualiza individualmente → tabla normalizada. Todo lo que es lista interna de un objeto → JSONB.

---

## Reconstrucción de ConversationState desde DB

El adapter Supabase reconstruirá el estado en 5 pasos determinísticos:

```
1. SELECT conversation_sessions WHERE cliente_id = X
   → fase, dolor_principal, dimension_foco, ultima_pregunta

2. SELECT conversation_messages WHERE session_id = X ORDER BY orden
   → historial_mensajes

3. SELECT conversation_questions WHERE session_id = X ORDER BY orden
   → historial_preguntas

4. SELECT conversation_evidence WHERE session_id = X
   → separar en evidencia_requerida / evidencia_confirmada por campo `estado`
   → derivar datos_conocidos de evidencia_confirmada

5. SELECT conversation_hypotheses WHERE session_id = X
   → reconstruir list[HipotesisActiva] con JSONB internos
```

Luego: `conversation_state_from_dict(data)` → `ConversationState` listo para el engine.

**Alternativa de recovery:** leer el último `conversation_state_snapshots` y deserializar el JSONB directamente. Solo para emergencias; la fuente de verdad son las tablas normalizadas.

---

## Fronteras arquitectónicas

```
┌─────────────────────────────────────────────────────┐
│  IA tipada futura (LLM, Prefect, Hermes)            │
│  opera SOBRE el core, nunca dentro                  │
├─────────────────────────────────────────────────────┤
│  ConversationService                                │
│  (orquesta repository + engine)                     │
├──────────────────────┬──────────────────────────────┤
│  ConversationEngine  │  ConversationRepository      │
│  (core clínico puro) │  (port ABC)                  │
│  sin DB, sin LLM     ├──────────────────────────────┤
│                      │  InMemoryConversationRepo     │
│                      │  SupabaseConversationRepo (→) │
├──────────────────────┴──────────────────────────────┤
│  ConversationState + serialization.py               │
│  (dataclasses puros, JSON-compatible)               │
└─────────────────────────────────────────────────────┘
```

**Lo que NO cruza la frontera del core:**
- Supabase client
- httpx / requests
- LLM calls
- Prefect flows
- Hermes runtime

---

## Consecuencias

**Positivas:**
- El core es testeable sin DB (43 tests verdes, cero mocks de Supabase)
- Cualquier adapter nuevo (Redis, SQLite, Postgres directo) implementa el port sin tocar el dominio
- La serialización es el único contrato entre dominio y persistencia
- La historia clínica es auditable y consultable sin deserializar blobs
- El adapter Supabase puede implementarse en un commit aislado sin riesgo para el core

**Negativas / trade-offs:**
- El adapter Supabase requiere 5 queries por reconstrucción (mitigable con snapshot)
- `datos_conocidos` es redundante con `conversation_evidence` — se deriva al reconstruir, no se persiste por separado
- `incertidumbres` está vacío en el engine actual — se persiste como JSONB vacío sin bloquear

---

## Riesgos

| Riesgo | Severidad | Mitigación |
|---|---|---|
| `HipotesisActiva.peso` usa `float` — posible drift | Media | Guardar como `NUMERIC(5,4)` en Postgres |
| Snapshot JSONB puede desincronizarse de tablas | Media | Snapshot es solo recovery; fuente de verdad = tablas normalizadas |
| Supabase RLS puede bloquear inserts si no se configura | Alta | Definir políticas RLS por `cliente_id` antes de implementar el adapter |
| `cliente_id` es `str` libre sin validación de formato | Media | Agregar `CHECK` constraint o FK a tabla de clientes en el schema |
| `datos_conocidos` derivado puede diferir si la lógica de derivación cambia | Baja | Documentar la regla de derivación en el adapter |

---

## Próximo paso técnico

**Commit 3 — Schema SQL (documentación, sin migraciones automáticas):**

```
docs/db/conversation_schema.sql
```

DDL de las 6 tablas. Sin Alembic ni migraciones automáticas todavía.  
El adapter Supabase (`SupabaseConversationRepository`) se implementa en el commit siguiente, aislado del core.

Orden de implementación recomendado:

```
[HECHO] Commit 1: ports.py — ConversationRepository ABC
[HECHO] Commit 2: in_memory_repository.py + serialization.py + service.py
[ESTE]  Commit 3: ADR-002 (este documento)
[NEXT]  Commit 4: docs/db/conversation_schema.sql — DDL sin migraciones
[NEXT]  Commit 5: SupabaseConversationRepository — adapter concreto
[NEXT]  Commit 6: wiring en endpoint/Telegram adapter
```
