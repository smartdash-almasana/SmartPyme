# SMARTPYME Hybrid AI + Deterministic Architecture

## 1. Principio Arquitectonico

SmartPyme disena sistemas hibridos con separacion explicita de responsabilidades:

- La IA opera en zonas ambiguas (lenguaje natural, contexto incompleto, redaccion explicativa).
- El codigo deterministico opera en zonas criticas (estados, calculos, contratos, bloqueos, trazabilidad).
- BEM estructura evidencia documental, pero no interpreta clinicamente ni decide.
- TCR + catalogos de patologias/formulas/modelos/grafos gobiernan el conocimiento referencial.
- El dueno valida contexto del negocio y confirma decisiones sensibles.

Regla rectora:

**IA interpreta. Deterministico decide. Evidencia gobierna. Dueno confirma.**

---

## 2. Capas del Sistema Hibrido

1. Rampa conversacional.
2. IA interpretativa.
3. Core deterministico.
4. TCR y catalogos clinico-operacionales.
5. BEM / ingesta documental.
6. Evidencia estructurada.
7. Formulas y contraste.
8. OperationalCaseCandidate.
9. OperationalCase.
10. Hallazgos accionables.

Secuencia esperada:

- Conversacion y relato -> interpretacion asistida por IA.
- Estructuracion y validacion -> reglas deterministicas.
- Contraste cuantitativo -> formulas/modelos/grafos.
- Decision de apertura de caso -> estados deterministas.
- Hallazgo accionable -> solo con evidencia trazable.

---

## 3. Que Puede Hacer la IA

La IA puede:

- Entender relato del dueno en lenguaje natural.
- Extraer sintomas y senales contextuales.
- Sugerir clasificaciones iniciales.
- Proponer repreguntas mayeuticas.
- Redactar explicaciones para usuario humano.
- Resumir evidencia disponible y faltante.

Siempre bajo supervision de contratos y validacion deterministica.

---

## 4. Que NO Puede Hacer la IA

La IA no puede:

- Inventar datos no observados.
- Confirmar hallazgos por si sola.
- Calcular resultados fuera de formulas definidas.
- Saltar evidencia requerida.
- Decidir por el dueno.
- Diagnosticar sin reglas y evidencia trazable.

Si falta evidencia o contrato, el sistema debe bloquear.

---

## 5. Que Debe Ser Deterministico

Debe permanecer deterministico:

- `tenant_id` y aislamiento multi-tenant.
- Estados del flujo y transiciones.
- `EvidenceRecord` y trazabilidad de origen.
- Catalogo de formulas.
- Calculos numericos.
- Comparacion fuente A vs fuente B.
- Reglas de bloqueo (fail-closed).
- Contratos de entrada/salida.
- Persistencia y versionado.
- Auditoria de cambios y decisiones.

---

## 6. Contratos Necesarios

Contratos canonicos minimos:

- `ReceptionRecord`
- `EvidenceRecord`
- `VariableObservation`
- `PathologyCandidate`
- `FormulaExecution`
- `OperationalCaseCandidate`
- `OperationalCase`
- `FindingRecord`

Todos deben incluir:

- `tenant_id`
- `trace_id` o equivalente
- `source_refs`
- `status`
- metadatos de version

---

## 7. Relacion con BEM

BEM cumple rol de proveedor de estructura documental:

- Convierte documentos en JSON estructurado.
- Entrega entidades/variables/evidencias extraidas.

SmartPyme luego:

- Mapea JSON a evidencia canonica.
- Deriva observaciones variables.
- Evalua formulas y modelos.

Regla:

- BEM no diagnostica.
- BEM no decide.

---

## 8. Relacion con TCR

TCR en SmartPyme:

- No es prompt libre.
- Es conocimiento versionado, relacional y auditable.
- Relaciona conceptos, patologias, sintomas, evidencias, variables, formulas, modelos y grafos causales.

TCR debe mantener:

- versionado activo/inactivo
- trazabilidad de cambios
- semantica estable para calculo y decision

---

## 9. Reglas de Bloqueo

Reglas fail-closed obligatorias:

1. Sin evidencia trazable no hay hallazgo.
2. Sin variable disponible no hay formula.
3. Sin formula no hay comparacion.
4. Sin comparacion no hay diferencia cuantificada.
5. Sin diferencia cuantificada no hay hallazgo fuerte.

Estado recomendado ante faltantes:

- `BLOCKED_MISSING_EVIDENCE`
- `BLOCKED_MISSING_VARIABLES`
- `BLOCKED_MISSING_FORMULA`

---

## 10. Riesgos

Riesgos arquitectonicos principales:

1. IA como cerebro decisor.
2. JSON opaco sin normalizacion.
3. Diagnostico sin evidencia.
4. BEM como caja negra decisora.
5. Endpoints prematuros sin contratos.
6. Reglas hardcodeadas en engine.
7. TCR degradado a texto libre no versionado.

Mitigacion transversal:

- Contratos tipados + trazabilidad + bloqueo fail-closed.

---

## 11. Proximo Artefacto Recomendado

Artefacto recomendado (sin implementacion):

- `docs/architecture/SMARTPYME_HYBRID_CONTRACTS_REFERENCE.md`

Objetivo del siguiente artefacto:

1. Definir schema minimo por cada contrato canonico.
2. Especificar invariantes deterministas por contrato.
3. Declarar reglas de bloqueo por contrato.
4. Mapear entradas IA/BEM a contratos internos SmartPyme.
5. Definir matriz de trazabilidad contrato -> formula -> hallazgo.
