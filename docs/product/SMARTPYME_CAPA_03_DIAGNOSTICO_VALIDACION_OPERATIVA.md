# SmartPyme — Capa 03: Diagnóstico y Validación Operativa

## Estado

PROPUESTA CANONICA — CONTRATO DE FRONTERA POSTERIOR A CAPA 02

---

## Propósito

La Capa 03 define el paso desde un `OperationalCaseCandidate` hacia un diagnóstico operativo parcial, validable y accionable.

No descubre el caso desde cero. No reabre admisión, normalización ni activación de conocimiento salvo que declare insuficiencia explícita.

---

## Principio fundamental

```text
Capa 02 prepara y contrae.
Capa 03 diagnostica y valida.
```

Otra formulación:

```text
Capa 03 ataca el núcleo; no vuelve a dibujarlo.
```

---

## Entrada principal

La entrada principal de Capa 03 es:

```text
OperationalCaseCandidate
```

Este objeto proviene de Capa 02 y debe traer, como mínimo:

```text
candidate_id
primary_pathology
related_pathologies
activated_formulas
required_variables
available_variables
evidence_gaps
knowledge_tools
investigation_graph
principal_entropic_core
recommended_route
initial_transformation_roadmap
next_step
status
```

Si esta información no existe, Capa 03 no debe inventarla. Debe devolver `INSUFFICIENT_CANDIDATE` o equivalente.

---

## Qué NO debe hacer Capa 03

Capa 03 no debe duplicar tareas de capas anteriores.

Queda prohibido:

```text
reactivar grafos desde cero
re-mapear personas
re-mapear herramientas
re-mapear flujos de trabajo
re-normalizar evidencia documental
re-clasificar CERTEZA / DUDA / DESCONOCIMIENTO
reconstruir InitialCaseAdmission
reconstruir NormalizedEvidencePackage
generar otro OperationalCaseCandidate equivalente
abrir investigación externa sin razón explícita
```

Todo eso pertenece a Capa 01, Capa 1.5 o Capa 02.

---

## Qué SÍ debe hacer Capa 03

Capa 03 transforma el candidato en diagnóstico operativo.

Funciones principales:

```text
evaluar suficiencia diagnóstica
confirmar o descartar hallazgos
generar DiagnosticReport
producir hallazgos trazables
validar diagnóstico parcial con el dueño
crear OperationalCase definitivo si corresponde
producir una propuesta de acción ejecutable
definir condiciones de autorización
preparar DecisionRecord
```

---

## Salidas esperadas

Capa 03 puede producir:

```text
OperationalCase
DiagnosticReport
FindingRecord
OwnerValidationRequest
ActionProposal
DecisionDraft
InsufficientEvidenceReport
```

No todas las salidas aparecen siempre. Dependen del estado de evidencia y validación.

---

## Estados posibles

```text
INSUFFICIENT_CANDIDATE
INSUFFICIENT_EVIDENCE
DIAGNOSTIC_PARTIAL
DIAGNOSTIC_CONTESTED
DIAGNOSTIC_CONFIRMED
OWNER_VALIDATION_REQUIRED
READY_FOR_PROPOSAL
READY_FOR_DECISION
```

---

## DiagnosticReport

El `DiagnosticReport` no debe ser una narrativa libre.

Debe incluir:

```text
case_id
candidate_id
diagnostic_state
confirmed_findings
rejected_findings
insufficient_evidence_items
evidence_refs
source_comparisons
quantified_differences
confidence_score
owner_validation_status
next_recommended_action
```

---

## Hallazgo válido

Un hallazgo válido exige:

```text
entidad específica
+ diferencia cuantificada
+ comparación explícita de fuentes
+ evidencia trazable
+ estado de confianza
```

Ejemplo válido:

```text
El modelo Jean Azul talle 42 presenta una diferencia de 180 unidades entre el Excel de stock y el conteo físico parcial, comparando evidencia Excel_Paulita_2026_05 contra Conteo_Estanteria_A_2026_05.
```

Ejemplo inválido:

```text
Hay problemas de stock.
```

---

## Validación con el dueño

Capa 03 no solo informa. Debe pedir validación o corrección cuando corresponda.

Ejemplos:

```text
¿Confirmás que este Excel es el último que usa Paulita?
¿Este conteo físico corresponde a toda la estantería o solo a un sector?
¿Este precio es de venta actual o precio viejo?
¿Autorizás que tomemos este diagnóstico parcial como base para el plan de acción?
```

---

## Propuesta de acción

La propuesta no debe aparecer antes del diagnóstico parcial.

Debe estar vinculada a:

```text
hallazgos confirmados
brechas pendientes
impacto esperado
horizonte temporal
recursos necesarios
responsables
riesgos
decisión requerida
```

Ejemplo:

```text
Durante 15 días reconstruir la verdad operativa del inventario textil, empezando por las familias Jean Azul con mayor rotación, validando Excel contra conteo físico parcial y actualizando precios de venta mínimos.
```

---

## Riesgo principal

El riesgo central de Capa 03 es:

```text
parálisis por re-análisis perpetuo
```

Si Capa 03 vuelve a normalizar, clasificar, mapear o contraer grafos, el sistema queda atrapado en un loop de preparación y nunca llega al diagnóstico.

Capa 02 ya contrajo el problema en un núcleo atacable. Capa 03 debe decidir si ese núcleo puede diagnosticarse, validarse y convertirse en acción.

---

## Relación entre capas

```text
Capa 01 → InitialCaseAdmission
Capa 1.5 → NormalizedEvidencePackage
Capa 02 → OperationalCaseCandidate
Capa 03 → OperationalCase + DiagnosticReport + ActionProposal
```

---

## Regla de no-regresión

Capa 03 no puede regresar a capas anteriores salvo que declare explícitamente una condición de insuficiencia.

Ejemplos:

```text
INSUFFICIENT_EVIDENCE → volver a Capa 1.5 para nueva evidencia
INSUFFICIENT_CANDIDATE → volver a Capa 02 para reconstrucción del candidato
OWNER_CONTESTED → volver a Capa 01 o 02 según el tipo de corrección
```

La vuelta debe ser explícita, registrada y justificada.

---

## Frase rectora

```text
Capa 03 no descubre el caso:
decide si el caso ya puede convertirse en diagnóstico operativo parcial.
```

Otra formulación:

```text
Capa 03 transforma un candidato investigativo en una representación diagnóstica validable.
```

---

## Contratos sugeridos

```text
OperationalCase
DiagnosticReport
FindingRecord
OwnerValidationRequest
ActionProposal
DecisionDraft
InsufficientEvidenceReport
```

---

## Cierre

La Capa 03 es el puente entre investigación y acción.

Sin Capa 03, SmartPyme queda preparando candidatos. Con Capa 03, SmartPyme empieza a producir diagnósticos operativos, propuestas y decisiones trazables.

La función de esta capa es impedir dos errores opuestos:

```text
diagnosticar demasiado pronto
o investigar para siempre
```

Su misión es encontrar el punto justo:

```text
evidencia suficiente
+ hallazgo trazable
+ validación humana
+ propuesta accionable
```
