-- =============================================================================
-- NO EJECUTAR — DRAFT P0
-- SmartPyme: persistencia conversacional clínica — iteración P0
-- =============================================================================
--
-- Tabla: public.conversation_sessions
--
-- Propósito:
--   Guardar el estado activo de la sesión clínica por cliente.
--   Una fila por cliente_id (sesión activa única).
--
-- Prerequisitos:
--   - public.clientes debe existir (ver P0_supabase_schema_draft.sql)
--   - public.set_updated_at() debe existir (ver P0_supabase_schema_draft.sql)
--
-- Deuda técnica documentada (ADR-002):
--   state_snapshot es un snapshot operativo P0.
--   La normalización clínica completa (conversation_messages,
--   conversation_hypotheses, conversation_evidence, conversation_questions)
--   queda diferida para la iteración siguiente según ADR-002.
--   Los campos fase / dolor_principal / dimension_foco se exponen como
--   columnas consultables para mitigar parcialmente el blob opaco.
-- =============================================================================

CREATE TABLE public.conversation_sessions (

    -- ------------------------------------------------------------------
    -- Identidad
    -- ------------------------------------------------------------------
    cliente_id      TEXT PRIMARY KEY,

    -- ------------------------------------------------------------------
    -- Campos consultables sin deserializar el snapshot
    -- Alineados con FaseConversacion y ConversationState de state.py
    -- ------------------------------------------------------------------
    fase            TEXT NOT NULL DEFAULT 'anamnesis_general',
    dolor_principal TEXT,
    dimension_foco  TEXT,
    ultima_pregunta TEXT,

    -- ------------------------------------------------------------------
    -- Snapshot operativo P0
    -- Contiene el ConversationState completo serializado via
    -- conversation_state_to_dict(state) de serialization.py.
    -- Reconstrucción: conversation_state_from_dict(state_snapshot).
    -- NOTA: este campo es snapshot auxiliar, no fuente de verdad
    -- normalizada. Ver deuda técnica en cabecera de este archivo.
    -- ------------------------------------------------------------------
    state_snapshot  JSONB NOT NULL DEFAULT '{}'::jsonb,

    -- ------------------------------------------------------------------
    -- Auditoría
    -- ------------------------------------------------------------------
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),

    -- ------------------------------------------------------------------
    -- Integridad referencial
    -- ------------------------------------------------------------------
    CONSTRAINT fk_conv_sessions_cliente
        FOREIGN KEY (cliente_id)
        REFERENCES public.clientes(cliente_id)
        ON DELETE RESTRICT,

    -- ------------------------------------------------------------------
    -- Constraints de dominio
    -- ------------------------------------------------------------------
    CONSTRAINT chk_conv_sessions_cliente_id_not_empty
        CHECK (length(trim(cliente_id)) > 0),

    CONSTRAINT chk_conv_sessions_fase
        CHECK (fase IN (
            'anamnesis_general',
            'foco_sintomas',
            'recoleccion_evidencia',
            'analisis_hipotesis',
            'bloqueo_por_evidencia'
        ))

);

-- =============================================================================
-- Trigger: updated_at automático
-- Reutiliza public.set_updated_at() definida en P0_supabase_schema_draft.sql
-- =============================================================================

CREATE TRIGGER trg_conversation_sessions_updated_at
    BEFORE UPDATE ON public.conversation_sessions
    FOR EACH ROW
    EXECUTE FUNCTION public.set_updated_at();

-- =============================================================================
-- Índices
-- =============================================================================

-- Filtrar sesiones por fase clínica (ej: todas en recoleccion_evidencia)
CREATE INDEX idx_conv_sessions_fase
    ON public.conversation_sessions (fase);

-- Filtrar por dimensión detectada (dinero / tiempo / ambas)
-- Parcial: solo filas donde dimension_foco no es NULL
CREATE INDEX idx_conv_sessions_dimension_foco
    ON public.conversation_sessions (dimension_foco)
    WHERE dimension_foco IS NOT NULL;

-- Búsqueda dentro del snapshot JSONB (hipótesis activas, evidencia, etc.)
CREATE INDEX idx_conv_sessions_state_snapshot_gin
    ON public.conversation_sessions
    USING gin (state_snapshot);

-- =============================================================================
-- Notas de implementación para SupabaseConversationRepository
-- =============================================================================
--
-- get_active_session(cliente_id):
--   SELECT * FROM conversation_sessions WHERE cliente_id = $1
--   → conversation_state_from_dict(row["state_snapshot"])
--
-- get_or_create_active_session(cliente_id):
--   Intentar get_active_session; si None → INSERT estado inicial
--
-- save_active_session(state):
--   INSERT INTO conversation_sessions (...) VALUES (...)
--   ON CONFLICT (cliente_id) DO UPDATE SET
--     fase            = EXCLUDED.fase,
--     dolor_principal = EXCLUDED.dolor_principal,
--     dimension_foco  = EXCLUDED.dimension_foco,
--     ultima_pregunta = EXCLUDED.ultima_pregunta,
--     state_snapshot  = EXCLUDED.state_snapshot,
--     updated_at      = now()
--
-- Prerequisito de negocio:
--   cliente_id debe existir en public.clientes antes de insertar sesión.
--   El adapter debe garantizar esto o recibir garantía del caller.
--
-- RLS (pendiente de configuración en Supabase):
--   CREATE POLICY conv_sessions_isolation ON public.conversation_sessions
--     USING (cliente_id = current_setting('app.cliente_id', true));
-- =============================================================================
