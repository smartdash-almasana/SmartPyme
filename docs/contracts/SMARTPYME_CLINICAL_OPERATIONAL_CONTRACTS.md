# SMARTPYME Clinical-Operational Contracts

## Estado

Documento de contratos conceptuales base para SmartPyme.

Regla rectora del sistema:

**IA interpreta. Deterministico decide. Evidencia gobierna. Dueno confirma.**

Este documento no define codigo ejecutable ni schemas de implementacion directa.

---

## Convenciones Comunes para Todos los Contratos

Campos transversales minimos (conceptuales):

- `tenant_id`
- `trace_id`
- `record_id`
- `status`
- `created_at`
- `updated_at`
- `source_refs`
- `knowledge_version_ref`

Estados macro de referencia:

- `DRAFT`
- `READY`
- `BLOCKED`
- `CLOSED`

Bloqueo transversal fail-closed:

- Sin evidencia trazable -> no se avanza a hallazgo.
- Sin contrato completo -> estado `BLOCKED`.

---

## 1) ReceptionRecord

### Proposito

Registrar el ingreso inicial del relato y contexto soberano del dueno para abrir la rampa clinica.

### Input

- Relato libre del dueno.
- Identidad de tenant/cliente.
- Canal de ingreso.

### Output

- Registro de admision trazable para iniciar anamnesis y priorizacion.

### Campos obligatorios

- `tenant_id`
- `cliente_id`
- `reception_id`
- `raw_message`
- `channel`
- `received_at`
- `status`

### Estados validos

- `RECEIVED`
- `CONTEXT_REQUIRED`
- `READY_FOR_ANAMNESIS`
- `BLOCKED_INVALID_TENANT`

### Evidencia requerida

- Trazabilidad minima del origen del mensaje.

### Que puede decidir

- Si hay datos minimos para pasar a anamnesis.

### Que NO puede decidir

- Diagnostico.
- Hallazgo.
- Apertura de caso operativo formal.

### Relacion con IA

- IA puede resumir y extraer sintomas preliminares.

### Relacion con deterministico

- Deterministico valida tenant, estado y completitud minima.

### Relacion con BEM

- Sin relacion directa obligatoria.

### Relacion con TCR

- Mapeo preliminar opcional de sintomas a conceptos.

### Condiciones de bloqueo

- `tenant_id` faltante.
- Mensaje vacio/no trazable.

---

## 2) EvidenceRecord

### Proposito

Representar evidencia canonica trazable, independiente del proveedor de extraccion.

### Input

- Datos estructurados provenientes de BEM u otras fuentes.
- Referencias de origen documental.

### Output

- Evidencia validada y utilizable por contratos posteriores.

### Campos obligatorios

- `evidence_id`
- `tenant_id`
- `evidence_code`
- `evidence_value`
- `source_document_id`
- `source_locator` (pagina/segmento)
- `trace_hash`
- `status`

### Estados validos

- `EXTRACTED`
- `VALIDATED`
- `NEEDS_REVIEW`
- `REJECTED`

### Evidencia requerida

- Fuente documental verificable.

### Que puede decidir

- Calidad/validez tecnica de la evidencia.

### Que NO puede decidir

- Patologia final.
- Hallazgo final.

### Relacion con IA

- IA puede etiquetar o resumir, no aprobar evidencia.

### Relacion con deterministico

- Deterministico valida trazabilidad y estado.

### Relacion con BEM

- BEM es fuente principal de estructura para este contrato.

### Relacion con TCR

- `evidence_code` debe mapear a catalogo de evidencia TCR/patologias.

### Condiciones de bloqueo

- Sin `source_document_id` o `trace_hash`.
- `evidence_code` no reconocido.

---

## 3) DocumentIngestion

### Proposito

Gestionar el ciclo de ingreso documental previo a extraccion y transformacion a evidencia.

### Input

- Archivo/documento.
- Metadata de canal y tenant.

### Output

- Ingestion registrada con estado y linkage al flujo BEM.

### Campos obligatorios

- `ingestion_id`
- `tenant_id`
- `document_id`
- `document_type`
- `source_channel`
- `received_at`
- `status`

### Estados validos

- `INGESTED`
- `QUEUED_FOR_BEM`
- `PROCESSED`
- `FAILED`

### Evidencia requerida

- Identificacion inequívoca del documento y su origen.

### Que puede decidir

- Si el documento es apto para pipeline tecnico.

### Que NO puede decidir

- Relevancia clinica final.

### Relacion con IA

- IA no decide ingestion.

### Relacion con deterministico

- Deterministico valida formato, ownership, estado.

### Relacion con BEM

- Dispara workflow BEM.

### Relacion con TCR

- No directa; aplica en etapas posteriores.

### Condiciones de bloqueo

- Documento corrupto/sin metadata de tenant.

---

## 4) VariableObservation

### Proposito

Representar observaciones de variables cuantificables derivadas de evidencia.

### Input

- Uno o mas `EvidenceRecord`.
- Regla de transformacion variable.

### Output

- Observacion de variable trazable, usable por formulas.

### Campos obligatorios

- `observation_id`
- `tenant_id`
- `variable_code`
- `observed_value`
- `observed_at`
- `source_evidence_ids`
- `status`

### Estados validos

- `OBSERVED`
- `NORMALIZED`
- `CONFLICTED`
- `REJECTED`

### Evidencia requerida

- Al menos un `EvidenceRecord` trazable.

### Que puede decidir

- Calidad tecnica de la observacion.

### Que NO puede decidir

- Hallazgo por si sola.

### Relacion con IA

- IA puede sugerir normalizacion textual; no confirmar valor final.

### Relacion con deterministico

- Deterministico aplica coercion de tipos, unidades y validaciones.

### Relacion con BEM

- BEM provee insumos, no decide variable final.

### Relacion con TCR

- `variable_code` debe existir en TCR/catalogos.

### Condiciones de bloqueo

- Sin evidencia asociada.
- Unidad incompatible no resoluble.

---

## 5) PathologyCandidate

### Proposito

Formalizar hipotesis patologicas candidatas desde sintomas + evidencia disponible/faltante.

### Input

- Relato/anamnesis.
- Observaciones de variables.
- Catalogo de patologias.

### Output

- Lista priorizada de candidatas con gaps y grado de soporte.

### Campos obligatorios

- `pathology_candidate_id`
- `tenant_id`
- `pathology_code`
- `supporting_symptoms`
- `supporting_evidence_ids`
- `missing_evidence_codes`
- `priority_score`
- `status`

### Estados validos

- `CANDIDATE_ACTIVE`
- `CANDIDATE_WEAK`
- `CANDIDATE_BLOCKED`
- `CANDIDATE_DISCARDED`

### Evidencia requerida

- Minimo de sintomas trazables y/o evidencia asociada.

### Que puede decidir

- Priorizacion de investigacion, no confirmacion final.

### Que NO puede decidir

- Diagnostico definitivo.
- Hallazgo accionable final.

### Relacion con IA

- IA puede sugerir clasificacion inicial.

### Relacion con deterministico

- Deterministico calcula score y aplica reglas de activacion.

### Relacion con BEM

- Usa evidencia estructurada indirectamente.

### Relacion con TCR

- Depende del catalogo versionado de patologias/sintomas/evidencias.

### Condiciones de bloqueo

- Patologia fuera de catalogo activo.
- Sin evidencia minima para sostener candidata.

---

## 6) FormulaExecution

### Proposito

Ejecutar formulas canonicas sobre variables observadas para producir resultados comparables.

### Input

- `formula_code`
- Variables requeridas disponibles
- Contexto temporal

### Output

- Resultado de formula con trazabilidad completa.

### Campos obligatorios

- `formula_execution_id`
- `tenant_id`
- `formula_code`
- `input_variable_refs`
- `result_value`
- `result_unit`
- `knowledge_version_ref`
- `status`

### Estados validos

- `EXECUTED`
- `BLOCKED_MISSING_VARIABLES`
- `FAILED_VALIDATION`

### Evidencia requerida

- Variables observadas trazables para todos los inputs requeridos.

### Que puede decidir

- Resultado numerico de la formula.

### Que NO puede decidir

- Interpretacion clinica final del resultado.

### Relacion con IA

- IA no ejecuta formulas ni altera resultado.

### Relacion con deterministico

- Deterministico ejecuta, valida y persiste calculo.

### Relacion con BEM

- Ninguna directa; consume derivaciones de evidencia.

### Relacion con TCR

- Formula y variables deben existir en catalogo versionado.

### Condiciones de bloqueo

- Falta variable requerida.
- Formula inexistente/inactiva.

---

## 7) OperationalCaseCandidate

### Proposito

Consolidar estado investigable previo a apertura de caso operativo formal.

### Input

- PathologyCandidate(s)
- FormulaExecution(s)
- Evidence gaps
- Ruta/grafo sugerido

### Output

- Candidato de caso evaluable por Capa 03.

### Campos obligatorios

- `candidate_id`
- `tenant_id`
- `primary_pathology`
- `related_pathologies`
- `activated_formulas`
- `required_variables`
- `available_variables`
- `evidence_gaps`
- `investigation_graph_ref`
- `principal_entropic_core`
- `recommended_route`
- `status`

### Estados validos

- `PARTIAL_EVIDENCE`
- `READY_FOR_CASE_EVALUATION`
- `BLOCKED_MISSING_CRITICAL_EVIDENCE`

### Evidencia requerida

- Al menos una variable disponible trazable.
- Al menos una formula activada.

### Que puede decidir

- Si existe base minima para pasar a evaluacion de apertura.

### Que NO puede decidir

- Apertura final del `OperationalCase`.

### Relacion con IA

- IA puede sugerir narrativa de priorizacion.

### Relacion con deterministico

- Deterministico valida completitud minima y consistencia.

### Relacion con BEM

- Usa outputs de evidencia/variables derivados de BEM.

### Relacion con TCR

- Debe referenciar patologias/formulas/modelos activos.

### Condiciones de bloqueo

- Sin formulas activadas.
- Sin variables trazables.

---

## 8) OperationalCase

### Proposito

Representar el caso operativo formal abierto/rechazado por reglas de Capa 03.

### Input

- `OperationalCaseCandidate`
- Reglas de suficiencia y alcance

### Output

- Caso abierto o bloqueado con razon explicita.

### Campos obligatorios

- `case_id`
- `tenant_id`
- `candidate_id`
- `primary_pathology`
- `available_variables`
- `evidence_gaps`
- `recommended_route`
- `status`
- `next_step`

### Estados validos

- `READY_FOR_INVESTIGATION`
- `CLARIFICATION_REQUIRED`
- `INSUFFICIENT_EVIDENCE`
- `REJECTED_OUT_OF_SCOPE`

### Evidencia requerida

- Minimos de suficiencia definidos por Capa 03.

### Que puede decidir

- Apertura, bloqueo o rechazo del caso.

### Que NO puede decidir

- Hallazgo final o decision ejecutiva final.

### Relacion con IA

- IA puede ayudar a redactar pregunta de aclaracion.

### Relacion con deterministico

- Deterministico evalua criterios y fija estado.

### Relacion con BEM

- Indirecta via evidencia ya estructurada.

### Relacion con TCR

- Usa conocimiento versionado para evaluar alcance/suficiencia.

### Condiciones de bloqueo

- Brechas criticas sin fuente.
- Patologia fuera de dominio.

---

## 9) FindingRecord

### Proposito

Registrar hallazgo accionable con diferencia cuantificada y trazabilidad completa.

### Input

- OperationalCase en investigacion.
- Resultados de formulas/modelos/grafos.
- Evidencia confirmada.

### Output

- Hallazgo formal comunicable y auditable.

### Campos obligatorios

- `finding_id`
- `tenant_id`
- `case_id`
- `finding_code`
- `finding_statement`
- `quantified_difference`
- `supporting_evidence_ids`
- `supporting_formula_execution_ids`
- `severity`
- `status`

### Estados validos

- `DRAFT`
- `SUPPORTED`
- `BLOCKED_EVIDENCE`
- `CONFIRMED`
- `REJECTED`

### Evidencia requerida

- Evidencia trazable + formula ejecutada + comparacion cuantificada.

### Que puede decidir

- Consolidacion de hallazgo fuerte solo si se cumplen condiciones.

### Que NO puede decidir

- Accion automatica irreversible sin capa de decision posterior.

### Relacion con IA

- IA puede redactar explicacion, no validar hallazgo.

### Relacion con deterministico

- Deterministico valida reglas de fortaleza del hallazgo.

### Relacion con BEM

- BEM solo aporta insumos de evidencia.

### Relacion con TCR

- El hallazgo debe mapear a taxonomias y umbrales versionados.

### Condiciones de bloqueo

- Sin diferencia cuantificada.
- Sin evidencia trazable.
- Sin formula/modelo/grafo aplicable.

---

## Matriz Resumida de Decisiones

- IA:
  - Interpreta relato, resume, sugiere repreguntas, propone clasificaciones.
  - No confirma hallazgos, no calcula fuera de contrato, no decide estados finales.

- Deterministico:
  - Valida contratos, estados, formulas, bloqueos y trazabilidad.
  - Decide aperturas, bloqueos y consistencia de outputs.

- BEM:
  - Estructura documento a JSON y extrae entidades/variables/evidencias.
  - No diagnostica ni decide.

- Dueno:
  - Confirma contexto, aclara ambiguedades y valida decisiones de negocio.

---

## Regla Final de Gobernanza

Si cualquier contrato no cumple completitud + evidencia + trazabilidad:

- Estado obligatorio: `BLOCKED`
- Sin excepciones por conveniencia operativa.

Sin evidencia trazable no hay hallazgo.
