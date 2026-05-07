# ADR DB Genetic Model SmartPyme

- Estado: ACCEPTED
- Fecha: 2026-05-07
- Decisores: Dirección técnica SmartPyme
- Alcance: Persistencia de producto SmartPyme (core + módulos acoplados)

## 1. Contexto

SmartPyme evolucionó sobre persistencia local con SQLite y repositorios por dominio. La auditoría técnica vigente confirmó:

- Convención canónica actual: `cliente_id`.
- Aislamiento funcional multi-cliente apoyado en `cliente_id` y `X-Client-ID`.
- Reutilización conceptual actual en entidades de Job, OperationalCase, DecisionRecord, EvidenceCandidate, FormulaResult y PathologyFinding.
- Ausencia de migración formal end-to-end hacia una base relacional compartida de escala.

Se necesita fijar una decisión arquitectónica estable para evitar deriva, producto paralelo o fragmentación de datos al acoplar Laboratorio PyME como primer flujo vendible.

## 2. Decisión

Se adopta un modelo genético de persistencia con estas decisiones vinculantes:

1. `cliente_id` es el eje soberano de aislamiento de datos de negocio.
2. La arquitectura de datos se organiza en un **core estable** y **módulos acoplados** por relaciones explícitas.
3. El destino escalable de persistencia es Supabase/Postgres.
4. SQLite legacy permanece operativo y sin ruptura en esta fase.
5. Laboratorio PyME se acopla al producto SmartPyme como primer módulo vendible, sin base separada.

## 3. Principios genéticos

1. Soberanía por cliente.
- Toda entidad de negocio debe poder filtrarse y auditarse por `cliente_id`.

2. Ensamblaje por núcleo.
- El core modela identidades, casos, evidencia, jobs, hallazgos, informes y decisiones.
- Los módulos extienden capacidades sin duplicar núcleo.

3. Trazabilidad explícita.
- Cada proceso relevante conserva estado, timestamps, referencia de origen y relación con entidades núcleo.

4. Evolución por slices.
- La transición SQLite -> Supabase/Postgres se hace por cortes acotados, verificables y reversibles.

5. Compatibilidad semántica.
- Los contratos funcionales del negocio deben mantener continuidad durante la transición.

## 4. Entidades core

Las entidades núcleo conceptuales de SmartPyme son:

- `clientes`: raíz de soberanía de datos.
- `usuarios`: identidad de actor humano/sistema dentro de cliente.
- `jobs`: unidad de ejecución y orquestación.
- `operational_cases`: unidad operativa del flujo de diagnóstico.
- `documents`: documento fuente trazable.
- `evidence_candidates`: evidencia utilizable en análisis.
- `findings`: hallazgo comparado y cuantificado.
- `reports`: informe/diagnóstico consolidado.
- `decisions`: decisión humana o de control sobre casos/informes.
- `action_proposals` y `action_executions`: propuesta y ejecución de tratamiento/acción.

## 5. Entidades modulares

Los módulos se acoplan al core sin quebrar su semántica:

- Laboratorio PyME (primer módulo vendible):
  - `laboratory_runs`: corrida analítica acoplada a case/job.
  - `laboratory_results`: resultado específico de módulo, proyectable a findings/reports.

Regla de modularidad:
- Las entidades modulares referencian entidades core; no reemplazan ni duplican su función primaria.

## 6. Modelo `cliente_id`

Reglas obligatorias:

1. `cliente_id` obligatorio en toda entidad de negocio core y modular.
2. Lecturas y escrituras deben estar condicionadas por `cliente_id`.
3. Las restricciones de integridad deben impedir mezcla entre clientes.
4. `cliente_id` se propaga desde frontera de entrada (`X-Client-ID`) hasta persistencia final.

Queda prohibido:
- usar `tenant_id` en nuevos contratos del producto;
- usar `owner_id` como clave primaria de aislamiento.

## 7. Relación Laboratorio ↔ Core

Laboratorio PyME se integra así:

- Se inicia sobre `jobs` y `operational_cases` existentes.
- Consume y/o produce `evidence_candidates`, `findings` y `reports`.
- Puede requerir `decisions` para validación humana y continuidad.
- Toda su persistencia queda dentro del modelo unificado SmartPyme, con `cliente_id` en cadena completa.

Resultado esperado:
- Laboratorio es un flujo vendible del producto SmartPyme, no un producto paralelo.

## 8. Tablas Supabase conceptuales

Tipología conceptual objetivo (sin SQL en este ADR):

Core:
- `clientes`
- `usuarios`
- `jobs`
- `operational_cases`
- `documents`
- `evidence_candidates`
- `findings`
- `reports`
- `decisions`
- `action_proposals`
- `action_executions`

Módulo Laboratorio:
- `laboratory_runs`
- `laboratory_results`

Auditoría/observabilidad:
- `job_events`
- `audit_events`

Todas con convención de naming consistente y acople por claves foráneas conceptuales al core.

## 9. Reglas anti-conflicto

1. Prohibido crear base separada por módulo.
2. Prohibido introducir campos de aislamiento alternativos al eje `cliente_id`.
3. Prohibido duplicar entidades core bajo nombres modulares.
4. Core no depende funcionalmente de tablas modulares.
5. Los módulos extienden por relación y no por copia.
6. Naming estable en `snake_case` con sufijos semánticos (`*_id`, `*_at`, `*_json`).
7. Cambios de esquema se gobiernan por contrato y slices controlados.

## 10. Estrategia SQLite legacy

Directriz:

- SQLite legacy queda quieto en esta fase para no romper la operación actual.
- Se mantiene compatibilidad de contratos y repositorios existentes durante la transición.
- La adopción de Supabase/Postgres se realizará por slices implementables, sin big-bang.

## 11. Primer slice implementable

Slice mínimo recomendado para iniciar transición sin ruptura:

1. Consolidar el flujo vendible Laboratorio sobre entidades core existentes (jobs, cases, reports, decisions).
2. Definir adaptadores de persistencia compatibles para destino Supabase/Postgres en paralelo controlado.
3. Validar aislamiento por `cliente_id` con pruebas de no-leak y trazabilidad.
4. Mantener continuidad operativa de SQLite hasta validación completa del slice.

## 12. Consecuencias

Positivas:
- Reduce riesgo de diversificación del producto.
- Alinea crecimiento modular sobre un núcleo estable.
- Facilita gobernanza de integridad y trazabilidad.
- Prepara transición escalable a Supabase/Postgres.

Trade-offs:
- Requiere disciplina de contratos y secuenciación por slices.
- Impone control estricto de naming y aislamiento en cada nuevo módulo.

## 13. No objetivos

Este ADR no:

- implementa código;
- define SQL definitivo;
- crea migraciones;
- cambia repositorios actuales;
- reemplaza SQLite en forma inmediata;
- diseña una base aislada para Laboratorio.

Su función es fijar la decisión arquitectónica y los límites de evolución de persistencia SmartPyme.
