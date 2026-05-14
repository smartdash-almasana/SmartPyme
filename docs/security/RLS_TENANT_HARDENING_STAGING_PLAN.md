# RLS Tenant Hardening Staging Plan

## Objetivo
Definir y versionar un hardening RLS tenant-aware para Supabase en SmartPyme, listo para staging como diseño de migración, sin ejecutar cambios en base de datos.

## Tablas Afectadas
- public.clientes
- public.jobs
- public.operational_cases
- public.reports
- public.decisions
- public.evidence_candidates
- public.curated_evidence

## Contrato de Identidad
- Claim canónico: `tenant_id` en `app_metadata` del JWT.
- Compatibilidad transitoria: `cliente_id` como fallback legacy.
- Resolución usada en SQL: `public.request_tenant_key()` lee `tenant_id` primero y luego `cliente_id`.
- Sin claim (`tenant_id`/`cliente_id` vacío o ausente): denegación por RLS (fail-closed).

## Matriz de Pruebas por Rol
| tabla | rol | claim | operación | esperado | razón |
|---|---|---|---|---|---|
| todas | anon | n/a | SELECT/INSERT/UPDATE/DELETE | DENY | anon sin grants + RLS |
| clientes | authenticated | tenant A | SELECT fila `cliente_id=A` | ALLOW | policy SELECT tenant-aware |
| clientes | authenticated | tenant A | SELECT fila `cliente_id=B` | DENY | aislamiento cross-tenant |
| clientes | authenticated | tenant A | INSERT/UPDATE/DELETE | DENY | sin grant operativo |
| jobs | authenticated | tenant A | INSERT con `cliente_id=A` | ALLOW | `WITH CHECK` válido |
| jobs | authenticated | tenant A | INSERT con `cliente_id=B` | DENY | spoof cross-tenant bloqueado |
| reports | authenticated | tenant B | UPDATE fila B -> set `cliente_id=A` | DENY | `WITH CHECK` en UPDATE |
| operational_cases | authenticated | tenant A | DELETE fila `cliente_id=B` | DENY | `USING` cross-tenant |
| curated_evidence | authenticated | tenant A | SELECT fila `tenant_id=A` | ALLOW | policy por `tenant_id` |
| curated_evidence | authenticated | tenant A | SELECT fila `tenant_id=B` | DENY | aislamiento cross-tenant |
| curated_evidence | authenticated | tenant B | INSERT con `tenant_id=A` | DENY | `WITH CHECK` bloquea spoof |
| todas | authenticated | sin claim | cualquier operación | DENY | `request_tenant_key()` => NULL |
| todas | service_role | n/a | SELECT/INSERT/UPDATE/DELETE | ALLOW | rol backend privilegiado |

## Riesgos Residuales
- Exposición alta si se filtra `service_role` key (bypass operativo backend).
- Riesgo de corte funcional si consumidores no envían claim canónico de tenant.
- Divergencia semántica temporal entre `tenant_id` (canónico) y `cliente_id` (legacy) hasta completar normalización.
- Necesidad de validar que `authenticated` realmente requiere DML completo en las 6 tablas no-`clientes`.

## Confirmación Explícita de NO APPLY
- Este plan y los SQL asociados son solo diseño para staging.
- No se ejecutó SQL.
- No se aplicaron migraciones.
- No se mutó la base de datos.
