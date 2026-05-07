-- =============================================================================
-- DEV PHASE 1 — RLS FAIL-CLOSED — NO POLICIES
-- =============================================================================
-- Objetivo: activar Row Level Security en las 6 tablas P0 de Laboratorio.
--
-- Comportamiento esperado tras esta migración:
--   - service_role: bypass RLS por defecto (Supabase garantiza esto).
--     El backend sigue operativo sin cambios en adapters.
--   - anon / authenticated: bloqueados por defecto (fail-closed).
--     Sin CREATE POLICY, ninguna fila es accesible desde el cliente.
--
-- Clave soberana de aislamiento: cliente_id (TEXT).
--   - NO se usa tenant_id.
--   - NO se usa owner_id como aislamiento primario.
--
-- Fase 2 (pendiente):
--   Requiere claim JWT con cliente_id para crear policies de acceso
--   controlado por cliente. No implementar hasta que el contrato JWT
--   esté definido y validado.
--
-- NO EJECUTAR EN PRODUCCIÓN SIN REVISIÓN HUMANA.
-- NO contiene CREATE POLICY.
-- NO contiene FORCE ROW LEVEL SECURITY.
-- =============================================================================

-- clientes
ALTER TABLE public.clientes ENABLE ROW LEVEL SECURITY;

-- jobs
ALTER TABLE public.jobs ENABLE ROW LEVEL SECURITY;

-- operational_cases
ALTER TABLE public.operational_cases ENABLE ROW LEVEL SECURITY;

-- reports
ALTER TABLE public.reports ENABLE ROW LEVEL SECURITY;

-- decisions
ALTER TABLE public.decisions ENABLE ROW LEVEL SECURITY;

-- evidence_candidates
ALTER TABLE public.evidence_candidates ENABLE ROW LEVEL SECURITY;

-- =============================================================================
-- FIN PHASE 1
-- Próximo paso: Fase 2 — CREATE POLICY con claim JWT cliente_id
-- =============================================================================
