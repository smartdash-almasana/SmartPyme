# TS_SUPABASE_ADAPTER_P0_001

## TASK_ID

`TS_SUPABASE_ADAPTER_P0_001`

## Objetivo

Implementar en un ciclo posterior una capa adaptadora opcional Supabase/Postgres
para persistencia P0 de SmartPyme (`clientes`, `jobs`, `operational_cases`, `reports`,
`decisions`, `evidence_candidates`) sin reemplazar SQLite legacy ni romper repos actuales.

## Alcance funcional

- Adapter seleccionable por configuración (no default global).
- Proyección de flujo Laboratorio hacia entidades core existentes:
  - `jobs`
  - `operational_cases`
  - `reports`
  - `decisions`
  - `evidence_candidates`
- Fail-closed si falta `cliente_id` en cualquier operación de persistencia.
- Mantener contratos funcionales existentes de repositorio/servicio.

## Contratos esperados

- Eje soberano: `cliente_id` obligatorio en lectura/escritura.
- Identificadores alineados: `cliente_id`, `case_id`, `job_id`, `report_id`, `decision_id`, `user_id`.
- Prohibido introducir `tenant_id`.
- Prohibido usar `owner_id` como clave primaria de aislamiento.
- `LaboratorioReportDraft` no se persiste como tabla permanente propia.
- Adapter no modifica semántica de repos legacy ni endpoints existentes.

## Diseño del adapter

### Patrón

- Definir interfaz/puerto de persistencia por agregado P0 (`jobs`/`cases`/`reports`/`decisions`/`evidence`).
- Mantener implementación SQLite existente como adapter legacy.
- Agregar implementación Supabase/Postgres como segundo adapter.
- Resolver adapter por configuración explícita (`env`/setting), con default legacy.

### Comportamiento

- Si `provider=supabase` y faltan variables críticas: `BLOCKED_ENVIRONMENT_CONTRACT_MISSING`.
- Si falta `cliente_id` en operación: `ValueError` o error de dominio equivalente (fail-closed).
- Sin dual-write obligatorio en P0 (evitar complejidad inicial); modo conmutado por provider.

### Compatibilidad

- No cambiar firmas públicas usadas por servicios/orquestadores en esta etapa, salvo inyección controlada.
- No romper tests existentes de SQLite.

## Variables/env esperadas

- `SMARTPYME_PERSISTENCE_PROVIDER=sqlite|supabase`
- `SMARTPYME_SUPABASE_URL`
- `SMARTPYME_SUPABASE_KEY` (service role en entorno seguro de backend)
- `SMARTPYME_SUPABASE_SCHEMA` (opcional, default `public`)
- `SMARTPYME_DB_STRICT_CLIENTE_ID=true` (opcional, recomendado `true` por default)

Notas:

- No introducir secretos en repo.
- Si `provider=supabase`, validar presencia de `URL/KEY` al iniciar adapter.

## Tablas conceptuales P0

- `clientes`
- `jobs`
- `operational_cases`
- `reports`
- `decisions`
- `evidence_candidates`

Mapeo base:

- `jobs <= background_jobs`
- `operational_cases <= operational_cases`
- `reports <= diagnostic_reports`
- `decisions <= decision_records`
- `evidence_candidates <= evidence_candidates`
- `clientes <= catálogo/base de identidad de cliente (mínimo viable para FK lógica)`

## Reglas cliente_id

- `cliente_id` es obligatorio en todas las operaciones.
- Filtrado por `cliente_id` en todas las consultas/listados.
- Escritura rechaza mismatch entre `cliente_id` del adapter y del payload/entidad.
- Pruebas de no-leak multi-cliente son criterio de aceptación.
- No admitir `tenant_id` como alias de entrada/salida.

## Tests obligatorios

### Unitarios

- Adapter supabase rechaza operación sin `cliente_id`.
- Adapter supabase aplica filtros por `cliente_id` en `get/list`.
- Adapter supabase preserva serialización JSON esperada de payloads.
- Selector de provider respeta config y fallback legacy.

### Integración controlada

- Suite existente SQLite sigue pasando sin cambios de comportamiento.
- Tests nuevos de no-leak para `jobs`/`cases`/`reports`/`decisions`/`evidence` con dos clientes.
- Proyección Laboratorio->Core persiste en tablas core P0 (sin tabla draft propia).

### Regresión

- Endpoints/herramientas actuales que dependen de repos P0 no rompen contrato.

## Criterios PASS/PARTIAL/BLOCKED

### PASS

- Adapter supabase implementado para 6 tablas P0.
- Provider configurable funcionando sin romper legacy.
- Todos los tests obligatorios en verde.
- Evidencia de no-leak multi-cliente.

### PARTIAL

- Adapter parcial (menos de 6 tablas) o gaps menores de contrato sin fuga de datos.

### BLOCKED

- Falta contrato de entorno (credenciales/provider) o no se puede garantizar `cliente_id` fail-closed.
- Cualquier riesgo de mezcla cross-cliente no resuelto.

## Fuera de alcance

- Migración total SQLite->Supabase.
- SQL definitivo y migraciones productivas.
- Cambios en `factory_v2/**`, `factory/core/**`, `queue_runner.py`, Hermes config.
- Persistir `LaboratorioReportDraft` como entidad permanente.
- Refactor global de dominios fuera de P0.

## Plan de implementación por pasos

1. Definir puertos de persistencia P0 (interfaces) y mapear repos legacy actuales.
2. Implementar selector de provider por configuración.
3. Implementar adapter supabase para `jobs` y `operational_cases`.
4. Implementar adapter supabase para `reports` y `decisions`.
5. Implementar adapter supabase para `evidence_candidates` y `clientes`.
6. Integrar proyección Laboratorio->Core sobre los puertos P0.
7. Agregar tests unitarios + no-leak multi-cliente + regresión.
8. Ejecutar validación completa y generar evidencia.

## Comandos de validación

- `pytest tests/laboratorio_pyme -q`
- `pytest tests/repositories -q`
- `pytest tests -q -k "no_leak or jobs or operational_case or decision or evidence"`
- `ruff check app`

Notas:

- Si `ruff/pytest` no disponibles: reportar `BLOCKED_ENVIRONMENT_CONTRACT_MISSING`.

## Evidencia mínima esperada

- `git status --short`
- `git diff` (paths P0)
- salida de tests obligatorios
- resumen de veredicto `PASS/PARTIAL/BLOCKED` con riesgos residuales
