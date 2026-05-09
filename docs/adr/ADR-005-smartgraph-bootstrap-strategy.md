# ADR-005 — SmartGraph Bootstrap Strategy

Estado: Aprobado
Fecha: 2026-05-09
Ámbito: SmartPyme SmartGraph bootstrap

## Contexto
El repositorio ya cuenta con:
- Puerto de repositorio SmartGraph.
- Adapter in-memory para validación determinística.
- Adapter Supabase para persistencia soberana SQL.
- Tests de contrato para aislamiento multi-tenant, claims, confidence, evidencia y human-review gating.

## Decisión de Bootstrap
La estrategia de bootstrap se ejecuta por capas mínimas y verificables:

1. **Capa de contrato**: consolidar `node/edge/alias/claim` como API estable.
2. **Capa de persistencia**: asegurar esquema SQL mínimo y paridad con adapters.
3. **Capa de resolución**: siguiente módulo recomendado será `EntityResolutionService` usando aliases y canonical keys.
4. **Capa de activación**: `SmartGraphActivationEngine` queda posterior a resolución + validación de ontología/esquema.

## Reglas de gobernanza
- Tenant isolation obligatorio en todas las lecturas/escrituras.
- `confidence` restringido a [0,1].
- `evidence_ids` como lista estructurada de UUIDs.
- `requires_human_review` bloquea promoción a `SUPPORTED` sin revisión.
- No LLM direct writes.
- Graphify no es dependencia productiva.

## Criterio de avance
Se puede avanzar a `EntityResolutionService` cuando:
- tests de repositorios estén en verde;
- esquema mínimo esté documentado;
- ontología y relaciones estén explícitas en docs de arquitectura.
