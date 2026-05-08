# SMARTPYME Sistema Clinico-Operacional Relacional

## 1. Estado

- **DOCUMENTO RECTOR - DESIGN_FULL**
- Alcance: diseno funcional y de datos del sistema clinico-operacional relacional de SmartPyme.
- **No implementacion de codigo**.
- **No migracion SQL ejecutable**.
- **No endpoint API**.

Este documento consolida la direccion de la capa conversacional clinica existente y su evolucion hacia un modelo relacional completo, trazable y gobernable.

---

## 2. Principio Arquitectonico

SmartPyme es un laboratorio clinico-operacional PyME:

- No es chatbot generico.
- No es ERP.
- No es un motor de respuestas por probabilidad.

La conversacion es una **rampa clinica** para transformar relato humano en hipotesis operacionales contrastables.

Principios:

1. El dueno es la fuente soberana contextual del caso.
2. El conocimiento referencial (TCR + catalogos) orienta la investigacion.
3. BEM aporta evidencia estructurada, pero **no diagnostica**.
4. SmartPyme interpreta clinicamente la evidencia y la contrasta contra relato y modelos.
5. Sin evidencia trazable, no hay hallazgo accionable.
6. Toda conclusion debe tener trazabilidad: origen, transformacion, regla y version.

Regla BEM-SmartPyme:

- **BEM estructura evidencia**.
- **SmartPyme interpreta clinicamente**.
- **BEM nunca diagnostica**.

---

## 3. Modelo Relacional de los 3 Tanques

### 3.1 Tanque A: TCR (Tanque de Conocimiento Referencial)

Objetivo: representar conceptos clinico-operacionales y su marco de interpretacion.

Entidades propuestas:

- `tcr_domains`
  - `domain_id` (PK)
  - `code` (unique)
  - `name`
  - `description`
  - `is_active`
  - `version_id` (FK -> `knowledge_versions`)

- `tcr_concepts`
  - `concept_id` (PK)
  - `domain_id` (FK -> `tcr_domains`)
  - `code` (unique por version)
  - `name`
  - `definition`
  - `unit_type` (money/time/rate/count/text)
  - `is_active`
  - `version_id` (FK)

- `tcr_concept_relations`
  - `relation_id` (PK)
  - `source_concept_id` (FK -> `tcr_concepts`)
  - `target_concept_id` (FK -> `tcr_concepts`)
  - `relation_type` (causes, influences, constrains, derives)
  - `strength`
  - `version_id` (FK)

Cardinalidades:

- `tcr_domains` 1 -> N `tcr_concepts`
- `tcr_concepts` N <-> N `tcr_concepts` via `tcr_concept_relations`
- `knowledge_versions` 1 -> N `tcr_domains`/`tcr_concepts`

### 3.2 Tanque B: Catalogo de Patologias/Desvios Usuales PyME

Objetivo: codificar desviaciones recurrentes con sintomas, evidencia y posibles hallazgos.

Entidades propuestas:

- `pathology_catalog`
  - `pathology_id` (PK)
  - `code` (unique)
  - `name`
  - `description`
  - `dimension` (dinero/tiempo/mixta)
  - `is_active`
  - `version_id` (FK)

- `pathology_symptoms`
  - `symptom_id` (PK)
  - `pathology_id` (FK)
  - `symptom_text`
  - `weight_hint`
  - `is_active`

- `pathology_required_evidence`
  - `pre_id` (PK)
  - `pathology_id` (FK)
  - `evidence_code`
  - `priority` (critical/high/medium/low)
  - `is_blocking`

- `pathology_possible_findings`
  - `finding_id` (PK)
  - `pathology_id` (FK)
  - `finding_code`
  - `finding_description`
  - `requires_threshold_eval` (bool)

Cardinalidades:

- `pathology_catalog` 1 -> N `pathology_symptoms`
- `pathology_catalog` 1 -> N `pathology_required_evidence`
- `pathology_catalog` 1 -> N `pathology_possible_findings`

### 3.3 Tanque C: Catalogo de Formulas, Modelos Administrativos y Grafos Causales

Objetivo: habilitar contraste cuantitativo y causal reproducible.

Entidades propuestas:

- `formula_catalog`
  - `formula_id` (PK)
  - `code` (unique)
  - `name`
  - `expression_ref`
  - `output_variable_code`
  - `is_active`
  - `version_id` (FK)

- `formula_variables`
  - `fv_id` (PK)
  - `formula_id` (FK)
  - `variable_code`
  - `role` (input/output/aux)
  - `is_required`

- `administrative_models`
  - `model_id` (PK)
  - `code` (unique)
  - `name`
  - `description`
  - `domain_id` (FK -> `tcr_domains`)
  - `is_active`
  - `version_id` (FK)

- `model_formulas` (join N:M)
  - `model_id` (FK)
  - `formula_id` (FK)
  - PK compuesta (`model_id`,`formula_id`)

- `causal_graphs`
  - `graph_id` (PK)
  - `model_id` (FK -> `administrative_models`)
  - `code` (unique por version)
  - `name`
  - `is_active`
  - `version_id` (FK)

- `causal_graph_nodes`
  - `node_id` (PK)
  - `graph_id` (FK)
  - `node_code`
  - `node_type` (variable/event/constraint)
  - `concept_id` (FK -> `tcr_concepts`, nullable)

- `causal_graph_edges`
  - `edge_id` (PK)
  - `graph_id` (FK)
  - `source_node_id` (FK)
  - `target_node_id` (FK)
  - `causal_type` (direct/inverse/moderated)
  - `weight_hint`

- `graph_thresholds`
  - `threshold_id` (PK)
  - `graph_id` (FK)
  - `node_id` (FK)
  - `metric_code`
  - `operator` (>, >=, <, <=, between)
  - `threshold_value`
  - `severity_level`

- `graph_blocking_rules`
  - `rule_id` (PK)
  - `graph_id` (FK)
  - `required_evidence_code`
  - `blocking_reason`

Cardinalidades clave:

- `administrative_models` 1 -> N `causal_graphs`
- `administrative_models` N <-> N `formula_catalog` via `model_formulas`
- `causal_graphs` 1 -> N `causal_graph_nodes`
- `causal_graphs` 1 -> N `causal_graph_edges`
- `causal_graph_nodes` 1 -> N `graph_thresholds`

### 3.4 Versionado, Estado y Trazabilidad

Entidades transversales:

- `knowledge_versions`
  - `version_id` (PK)
  - `version_tag`
  - `status` (draft/active/deprecated)
  - `released_at`
  - `change_summary`

- `knowledge_change_log`
  - `change_id` (PK)
  - `version_id` (FK)
  - `entity_name`
  - `entity_id`
  - `change_type` (create/update/deactivate)
  - `change_payload`
  - `author_type` (human/system)
  - `created_at`

Relaciones:

- `knowledge_versions` 1 -> N casi todos los catalogos.
- Cada entidad catalogica tiene `is_active` para activacion/inactivacion sin borrado destructivo.

---

## 4. Modelo BEM -> SmartPyme

Objetivo: desacoplar extraccion estructurada (BEM) de interpretacion clinica (SmartPyme).

Entidades propuestas:

- `document_ingestions`
  - `ingestion_id` (PK)
  - `cliente_id`
  - `document_id`
  - `document_type`
  - `source_channel`
  - `received_at`

- `bem_workflows`
  - `bem_workflow_id` (PK)
  - `ingestion_id` (FK)
  - `workflow_name`
  - `workflow_version`
  - `status`

- `bem_calls`
  - `bem_call_id` (PK)
  - `bem_workflow_id` (FK)
  - `step_name`
  - `provider`
  - `started_at`
  - `finished_at`
  - `status`

- `bem_events`
  - `bem_event_id` (PK)
  - `bem_call_id` (FK)
  - `event_type`
  - `event_payload`
  - `created_at`

- `bem_extraction_outputs`
  - `bem_output_id` (PK)
  - `bem_call_id` (FK)
  - `schema_name`
  - `schema_version`
  - `output_payload`

- `extracted_entities`
  - `extracted_entity_id` (PK)
  - `bem_output_id` (FK)
  - `entity_type`
  - `entity_value`
  - `confidence`

- `extracted_variables`
  - `extracted_variable_id` (PK)
  - `bem_output_id` (FK)
  - `variable_code`
  - `raw_value`
  - `normalized_value`
  - `unit`
  - `confidence`

- `extracted_evidence`
  - `extracted_evidence_id` (PK)
  - `bem_output_id` (FK)
  - `evidence_code`
  - `evidence_value`
  - `quality_flag`

- `evidence_source_links`
  - `esl_id` (PK)
  - `extracted_evidence_id` (FK)
  - `document_id`
  - `page_or_segment_ref`
  - `trace_hash`

- `variable_observations`
  - `observation_id` (PK)
  - `cliente_id`
  - `variable_code`
  - `observed_value`
  - `observed_at`
  - `source_evidence_id` (FK -> `extracted_evidence`)
  - `quality_score`

- `document_quality_signals`
  - `dqs_id` (PK)
  - `document_id`
  - `signal_type`
  - `signal_value`
  - `severity`

- `human_review_required`
  - `review_id` (PK)
  - `target_type` (document/variable/evidence)
  - `target_id`
  - `reason_code`
  - `status` (pending/resolved/rejected)

### Mapeo canonico de flujo

1. `bem_extraction_outputs` -> `extracted_evidence`
2. `extracted_evidence` -> `variable_observations` (si evidencia soporta variable)
3. `variable_observations` -> `formula_catalog` (evaluacion de formulas)
4. `formula_catalog` -> `administrative_models`
5. `administrative_models` -> `causal_graphs`
6. `causal_graphs` + thresholds -> `pathology_possible_findings`
7. Faltantes de evidencia (`pathology_required_evidence` no cubiertos) -> repreguntas clinicas

---

## 5. Rampa Conversacional Extensa

Flujo objetivo end-to-end:

1. Relato libre del dueno.
2. Anamnesis clinica inicial (dolor, contexto, proceso, impacto, periodo).
3. Captura estructurada de contexto (`anamnesis_contexto`).
4. Deteccion de sintomas y dimension.
5. Activacion de hipotesis.
6. Seleccion de patologias candidatas.
7. Repreguntas clinicas de faltantes criticos.
8. Pedido de evidencia (solo cuando contexto minimo existe).
9. Ingreso documental.
10. Procesamiento BEM (estructuracion).
11. Evidencia estructurada trazable.
12. Contraste relato vs datos observados.
13. Brechas y contradicciones.
14. Bloqueo clinico si falta evidencia critica.
15. Construccion de `OperationalCaseCandidate` (Capa 02).
16. Apertura de `OperationalCase` (Capa 03) o bloqueo.
17. Hallazgo accionable en capas posteriores.

Regla de control:

- Sin cierre de incertidumbres minimas de anamnesis, no avanzar a evidencia documental como unico eje.

---

## 6. Relacion con Capas Existentes

### Con `conversation/` actual

- El core actual (deterministico) es semilla valida: estado, hipotesis, repreguntas, evidencia requerida, serializacion.
- Debe evolucionar a productor de datos para `OperationalCaseCandidate` sin perder desacople infra.

### Con ADR-002

- Se preserva el principio: DB guarda historia operacional, no decide.
- Se mantiene frontera dominio/adapters.
- El snapshot P0 es tactico, no destino final del modelo clinico.

### Con `conversation_sessions_p0.sql`

- Es un staging de sesion activa (`state_snapshot`) con campos espejo.
- No reemplaza normalizacion clinica completa.
- Debe coexistir temporalmente con futuro esquema relacional de conocimiento y evidencia.

### Con Capa 03 (`OperationalCase`)

- Capa conversacional no diagnostica; prepara suficiencia investigable.
- Capa 03 decide apertura de caso segun evidencia y alcance.

### Con futuro Capa 02 (`OperationalCaseCandidate`)

- La conversacion debe alimentar:
  - patologias candidatas,
  - variables requeridas/disponibles,
  - evidencia faltante,
  - incertidumbres y bloqueos,
  - ruta sugerida de investigacion.

---

## 7. Ejemplos Clinicos Completos

### 7.1 Margen erosionado

- Sintomas del dueno: "vendo mucho pero no queda plata", "subieron costos".
- Preguntas clinicas: rubro, proceso afectado, periodo, impacto estimado.
- Evidencia requerida: ventas_periodo, compras_periodo, lista_precios, costo_mercaderia_vendida.
- Documentos tipicos: libro ventas, facturas compras, lista precios vigente.
- Schema BEM conceptual: `extracted_variables(monto_ventas, costo_compra, precio_lista)`.
- Entidades extraidas: producto, proveedor, canal venta.
- Variables extraidas: margen_bruto, costo_unitario, precio_promedio.
- Formulas aplicables: margen = (ventas - costos)/ventas.
- Modelo administrativo: rentabilidad comercial por linea.
- Grafo causal: costos -> margen -> caja.
- Posibles hallazgos: precio atrasado, margen negativo en lineas clave.
- Condiciones de bloqueo: sin costos o sin ventas trazables.
- Repreguntas si falta evidencia: "Tenes compras del mismo periodo?".

### 7.2 Caja inconsistente

- Sintomas: "la caja no cierra", "falta plata".
- Preguntas clinicas: quien maneja caja, mezcla personal-negocio, desde cuando.
- Evidencia requerida: resumen_caja_diaria, ventas_registradas, egresos_registrados.
- Documentos tipicos: arqueos, planilla caja, extractos.
- BEM conceptual: eventos de ingreso/egreso por fecha.
- Entidades: punto_venta, responsable_turno.
- Variables: saldo_apertura, saldo_cierre, diferencia.
- Formula: diferencia_caja = ingresos - egresos - cierre.
- Modelo: control tesoreria diaria.
- Grafo: registro incompleto -> diferencia caja.
- Hallazgos posibles: fuga no registrada, mezcla de fondos.
- Bloqueo: ausencia total de egresos.
- Repreguntas: "Registras gastos del negocio todos los dias?".

### 7.3 Stock inmovilizado

- Sintomas: "stock parado", "deposito lleno".
- Preguntas: rotacion, proceso de compra, periodo de inmovilizacion.
- Evidencia requerida: inventario_actual, ultimas_ventas_por_producto, fecha_ultima_compra_por_item.
- Documentos: inventario, ventas por SKU, compras historicas.
- BEM conceptual: tabla SKU-cantidad-fecha_ultima_venta.
- Entidades: SKU, categoria, proveedor.
- Variables: dias_sin_movimiento, capital_inmovilizado.
- Formula: capital_inmovilizado = stock * costo_reposicion.
- Modelo: gestion de inventario y rotacion.
- Grafo: sobrecompra -> inmovilizacion -> tension de caja.
- Hallazgos: concentracion de capital en SKUs sin salida.
- Bloqueo: no hay inventario confiable.
- Repreguntas: "Que productos no se venden hace mas tiempo?".

### 7.4 Precios atrasados

- Sintomas: "no actualice precios", "me da verguenza subir".
- Preguntas: frecuencia de actualizacion, criterio de fijacion.
- Evidencia requerida: lista_precios_actual, fecha_ultima_actualizacion_precios, facturas_proveedores_recientes.
- Documentos: lista precios, facturas proveedor, historico de cambios.
- BEM conceptual: precio_actual, costo_actual, fecha_vigencia.
- Entidades: producto, proveedor, canal.
- Variables: mark_up, brecha_reposicion.
- Formula: brecha = precio_venta - costo_reposicion.
- Modelo: pricing defensivo por reposicion.
- Grafo: inflacion costos -> brecha negativa -> margen erosionado.
- Hallazgos: lineas vendidas a perdida.
- Bloqueo: no existe costo actualizado.
- Repreguntas: "Cuando cambiaste precios por ultima vez?".

### 7.5 Tiempo perdido

- Sintomas: "todo manual", "paso horas en excel".
- Preguntas: tarea repetitiva principal, horas/semana, herramientas.
- Evidencia requerida: descripcion_procesos_repetitivos, tiempo_estimado_por_tarea, herramientas_actuales_usadas.
- Documentos: SOPs, planillas operativas, logs operativos.
- BEM conceptual: catalogo de tareas + tiempo observado.
- Entidades: tarea, rol, herramienta.
- Variables: horas_repetitivas, tasa_error_manual.
- Formula: costo_tiempo = horas * costo_hora.
- Modelo: eficiencia operativa administrativa.
- Grafo: manualidad -> horas perdidas -> retraso y costo oculto.
- Hallazgos: cuello en tareas administrativas.
- Bloqueo: sin estimacion de tiempo minimo.
- Repreguntas: "Cuantas horas semanales consume esa tarea?".

### 7.6 Cuello de botella operativo

- Sintomas: demoras recurrentes, backlog, reprocesos.
- Preguntas: etapa donde se acumula trabajo, volumen afectado.
- Evidencia requerida: tiempos por etapa, volumen entrante/saliente, tasa de reproceso.
- Documentos: reportes operativos, tickets, planillas de tiempos.
- BEM conceptual: eventos por etapa con timestamps.
- Entidades: etapa, responsable, lote.
- Variables: throughput, lead_time, WIP.
- Formulas: lead_time promedio, porcentaje de reproceso.
- Modelo: flujo operativo y capacidad.
- Grafo: restriccion de capacidad -> cola -> demora -> perdida de venta.
- Hallazgos: etapa critica saturada.
- Bloqueo: sin medicion temporal por etapa.
- Repreguntas: "En que parte exacta del proceso se genera la demora?".

---

## 8. Reglas de Decision

### Que decide BEM

- Extraccion estructurada desde documentos.
- Senales de calidad documental.
- Vinculo evidencia-fuente.

### Que NO decide BEM

- Diagnostico operacional.
- Priorizacion clinica de hipotesis.
- Emision de hallazgos.
- Apertura/cierre de caso.

### Que decide SmartPyme

- Interpretacion clinico-operacional.
- Hipotesis activas y su priorizacion.
- Suficiencia de evidencia para avanzar.
- Bloqueo o apertura de caso.

### Que requiere dueno humano

- Contexto soberano del negocio.
- Aclaraciones de ambiguedad.
- Confirmacion de datos criticos.

### Que requiere evidencia

- Toda variable usada en formulas de decision.
- Todo hallazgo potencial con impacto economico/temporal.

### Que queda como hipotesis

- Toda inferencia sin evidencia trazable o sin contraste suficiente.

### Cuando se bloquea

- Falta evidencia critica bloqueante.
- Contradiccion fuerte relato-datos sin resolucion.
- Ambiguedad estructural no resuelta.

### Cuando se puede abrir caso

- Existe `OperationalCaseCandidate` con suficiencia minima y trazabilidad.

### Cuando se puede emitir hallazgo

- Solo en capas posteriores a apertura, con evidencia trazable y umbrales/modelos aplicados.

---

## 9. Riesgos y No-Regresion

1. Riesgo: convertir todo en JSON opaco.
   - Mitigacion: normalizar entidades consultables y usar snapshot solo como soporte.

2. Riesgo: hardcodear patologias en engine de forma cerrada.
   - Mitigacion: desplazar conocimiento a catalogos versionados y mantener engine como ejecutor.

3. Riesgo: endpoint prematuro sin contrato de dominio.
   - Mitigacion: primero contrato relacional + reglas de decision + pruebas de no regresion.

4. Riesgo: diagnostico sin evidencia.
   - Mitigacion: fail-closed, estados de bloqueo e incertidumbre obligatorios.

5. Riesgo: usar BEM como cerebro.
   - Mitigacion: separar extraccion (BEM) de interpretacion (SmartPyme).

6. Riesgo: sobredisenar sin operacionalizar.
   - Mitigacion: iterar por artefactos concretos (ADR/SQL/contratos) con trazabilidad de impacto.

No-regresion explicita:

- Mantener principio de ADR-002: dominio clinico no acoplado a proveedor.
- Mantener determinismo del core conversacional.
- Mantener prohibicion de diagnostico final en capa conversacional.

---

## 10. Primer Artefacto Tecnico Posterior

Propuesta recomendada:

- **ADR-003 - Modelo Relacional Clinico-Operacional SmartPyme (TCR + Catalogos + BEM Bridge + Candidate)**

Contenido minimo de ADR-003:

1. Fronteras de agregado y ownership por modulo.
2. Diccionario de entidades canonicamente versionadas.
3. Reglas de cardinalidad obligatorias.
4. Criterios de bloqueo por evidencia faltante.
5. Estrategia de migracion progresiva desde `conversation_sessions` P0.
6. Plan de pruebas de integridad y trazabilidad.

Este artefacto prepara luego un `draft SQL relacional` y contratos tipados, sin saltar directo a endpoints o infraestructura.
