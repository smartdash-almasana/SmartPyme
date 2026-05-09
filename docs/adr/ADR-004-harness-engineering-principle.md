# ADR-004 — Harness Engineering Principle

Estado: Aprobado
Fecha: 2026-05-09
Ámbito: SmartPyme SmartGraph (documentación y contrato)

## Contexto
SmartPyme necesita una memoria estructural que sirva al sistema clínico-operacional sin contaminar su runtime principal. El repositorio ya define un contrato de persistencia SmartGraph mediante `SmartGraphRepositoryPort` con reglas fail-closed, tenant isolation y distinción epistemológica de claims.

## Decisión
Se adopta Harness Engineering como principio rector para SmartGraph:

1. SmartGraph es memoria estructural soberana de soporte, no sustituto del core clínico-operacional.
2. Todo acceso a persistencia de SmartGraph se hace vía puerto (`node/edge/alias/claim`).
3. No se permiten escrituras directas desde LLM a persistencia SmartGraph.
4. Toda operación es tenant-scoped con fail-closed ante tenant inválido o vacío.
5. Claims inferenciales (`INFERRED`, `AMBIGUOUS`, `HYPOTHESIS`) no pasan a `SUPPORTED` sin evidencia (`evidence_ids`) o revisión humana explícita.
6. La persistencia canónica de producción es SQL/Supabase; cualquier herramienta externa (incluyendo Graphify) se permite solo como inspiración o spike, nunca como runtime productivo.

## Implicancias
- El runtime principal conserva separación de responsabilidades.
- SmartGraph aporta trazabilidad: `claim_type`, `confidence`, `evidence_ids`, `requires_human_review`, `reviewed_by`, `review_decision`.
- Los adapters deben implementar las mismas invariantes del port.

## No-objetivos
- No define aquí `EntityResolutionService`.
- No define aquí `SmartGraphActivationEngine`.
- No cambia semántica actual de `cliente_id`/`tenant_id`.
