# SmartPyme — Capa 03: Apertura del Caso Operativo

## Estado

DOCUMENTO RECTOR — REESCRITO v2.0  
**Fecha:** Mayo 2026  
**Cambio principal:** Capa 03 ya no diagnostica. Capa 03 determina si existe un caso investigable y produce `OperationalCase`.

---

## Regla rectora

```text
Capa 03 no diagnostica.
Capa 03 determina si existe un caso investigable.
```

El diagnóstico, los hallazgos, las propuestas de acción y las decisiones pertenecen a capas posteriores.

Capa 03 tiene una sola responsabilidad: evaluar si el `OperationalCaseCandidate` que viene de Capa 02 tiene suficiencia para convertirse en un `OperationalCase` formal y abrirlo.

---

## 1. Posición en la arquitectura

```text
Capa 01   → InitialCaseAdmission
Capa 1.5  → NormalizedEvidencePackage
Capa 02   → OperationalCaseCandidate
Capa 03   → OperationalCase  ← esta capa
Capa 04+  → Investigación, diagnóstico, hallazgos, propuesta, decisión
```

Capa 03 es la frontera entre preparación e investigación.

No investiga.  
No diagnostica.  
No propone acciones.  
Abre o rechaza el caso.

---

## 2. Qué entra a Capa 03

La entrada principal es:

```text
OperationalCaseCandidate
```

Este objeto proviene de Capa 02 y debe traer, como mínimo:

```text
candidate_id
cliente_id
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

Si esta información no existe o está incompleta, Capa 03 no la inventa.  
Devuelve `INSUFFICIENT_EVIDENCE` o `REJECTED_OUT_OF_SCOPE` según corresponda.

---

## 3. Qué hace Capa 03

Capa 03 evalúa tres preguntas en orden:

### Pregunta 1: ¿El candidato tiene suficiencia mínima?

```text
¿Hay al menos una patología principal identificada?
¿Hay al menos una variable disponible con evidencia trazable?
¿Hay al menos una fórmula o método activado?
¿El candidato tiene un núcleo entrópico identificado?
```

Si la respuesta a alguna de estas preguntas es no, el caso no puede abrirse.

### Pregunta 2: ¿El caso está dentro del alcance operativo?

```text
¿La patología principal corresponde a un dominio que SmartPyme puede investigar?
¿Las variables requeridas son investigables con los recursos disponibles?
¿El caso no duplica un OperationalCase ya abierto para el mismo cliente?
```

Si el caso está fuera de alcance, se rechaza con razón explícita.

### Pregunta 3: ¿Se necesita aclaración antes de abrir?

```text
¿Hay brechas de evidencia críticas que bloquean la investigación?
¿Hay ambigüedades no resueltas en entidades o variables?
¿El dueño necesita confirmar algo antes de que el sistema investigue?
```

Si se necesita aclaración, el caso queda en `CLARIFICATION_REQUIRED` hasta que se resuelva.

---

## 4. Qué NO hace Capa 03

Capa 03 no:

- diagnostica;
- confirma ni descarta hallazgos;
- genera `DiagnosticReport`;
- genera `FindingRecord`;
- genera `ActionProposal`;
- genera `DecisionDraft`;
- genera `DecisionRecord`;
- activa `AuthorizationGate`;
- ejecuta acciones;
- re-normaliza evidencia documental;
- re-clasifica CERTEZA / DUDA / DESCONOCIMIENTO;
- reconstruye `InitialCaseAdmission`;
- reconstruye `NormalizedEvidencePackage`;
- genera otro `OperationalCaseCandidate`;
- re-mapea personas, herramientas o flujos de trabajo;
- re-activa grafos desde cero.

Todo eso pertenece a Capa 01, Capa 1.5, Capa 02 o capas posteriores.

---

## 5. Salida de Capa 03

La única salida de Capa 03 es:

```text
OperationalCase
```

El `OperationalCase` tiene cuatro estados posibles:

### READY_FOR_INVESTIGATION

El caso tiene suficiencia mínima, está dentro del alcance y no requiere aclaración previa.

El sistema puede iniciar la investigación formal en la capa siguiente.

```text
Condiciones:
- al menos una variable disponible con evidencia trazable
- al menos una fórmula activada
- núcleo entrópico identificado
- sin brechas críticas bloqueantes
- sin ambigüedades no resueltas en variables críticas
- caso dentro del alcance operativo
```

### CLARIFICATION_REQUIRED

El caso tiene potencial investigable pero necesita que el dueño confirme o aporte algo antes de continuar.

El sistema devuelve una pregunta mayéutica concreta al dueño y espera.

```text
Condiciones:
- hay brechas de evidencia que pueden resolverse con una acción del dueño
- hay ambigüedades en entidades o variables que el dueño puede aclarar
- el caso no puede investigarse con la evidencia actual pero podría con más
```

### INSUFFICIENT_EVIDENCE

El caso no tiene suficiencia mínima para investigar y las brechas no pueden resolverse con una acción simple del dueño.

El sistema devuelve el caso a Capa 1.5 o Capa 02 con razón explícita.

```text
Condiciones:
- no hay variables disponibles con evidencia trazable
- las brechas críticas no tienen fuente conocida
- el candidato no tiene núcleo entrópico identificado
```

### REJECTED_OUT_OF_SCOPE

El caso no corresponde al alcance operativo de SmartPyme o duplica un caso ya abierto.

El sistema rechaza el caso con razón explícita y no lo reabre.

```text
Condiciones:
- la patología principal no es investigable por SmartPyme
- el caso duplica un OperationalCase ya abierto para el mismo cliente
- el caso fue rechazado previamente por el dueño sin cambios sustanciales
```

---

## 6. Contrato del OperationalCase

```text
OperationalCase:
  case_id                   UUID único del caso
  cliente_id                tenant
  candidate_id              ID del OperationalCaseCandidate de origen
  source_admission_case_id  ID del InitialCaseAdmission de origen
  source_package_id         ID del NormalizedEvidencePackage de origen
  primary_pathology         patología principal a investigar
  related_pathologies       patologías relacionadas
  activated_formulas        fórmulas activadas para la investigación
  required_variables        variables requeridas
  available_variables       variables disponibles con evidencia trazable
  evidence_gaps             brechas de evidencia detectadas
  knowledge_tools           herramientas de conocimiento activadas
  investigation_graph       grafo investigativo de Capa 02
  principal_entropic_core   núcleo entrópico identificado
  recommended_route         ruta investigativa recomendada
  status                    READY_FOR_INVESTIGATION | CLARIFICATION_REQUIRED |
                            INSUFFICIENT_EVIDENCE | REJECTED_OUT_OF_SCOPE
  clarification_question    pregunta mayéutica si status=CLARIFICATION_REQUIRED
  rejection_reason          razón si status=REJECTED_OUT_OF_SCOPE
  insufficiency_reason      razón si status=INSUFFICIENT_EVIDENCE
  opened_at                 timestamp de apertura
  next_step                 instrucción para la capa siguiente o para el dueño
```

---

## 7. Regla de no-regresión

Capa 03 no puede regresar a capas anteriores salvo que declare explícitamente una condición de insuficiencia.

Las regresiones permitidas son:

```text
INSUFFICIENT_EVIDENCE
  → volver a Capa 1.5 para obtener nueva evidencia
  → razón explícita requerida

CLARIFICATION_REQUIRED
  → esperar respuesta del dueño
  → no avanzar hasta recibir aclaración
  → no reabrir Capa 01 ni Capa 02 automáticamente

REJECTED_OUT_OF_SCOPE
  → no reabrir
  → registrar razón
  → informar al dueño
```

Toda regresión debe ser:

- explícita;
- registrada en el `OperationalCase`;
- justificada con razón concreta;
- comunicada al dueño.

---

## 8. Control contra reanálisis infinito

El riesgo central de Capa 03 es la parálisis por reanálisis perpetuo.

Si Capa 03 vuelve a normalizar, clasificar, mapear o contraer grafos, el sistema queda atrapado en un loop de preparación y nunca llega a la investigación.

Reglas anti-loop:

1. Capa 03 no puede generar un nuevo `OperationalCaseCandidate`. Solo puede aceptar o rechazar el que recibe.
2. Capa 03 no puede solicitar más de una aclaración por ciclo. Si hay múltiples ambigüedades, prioriza la más crítica.
3. Si un caso fue devuelto a Capa 1.5 o Capa 02 más de dos veces por la misma razón, Capa 03 debe declarar `REJECTED_OUT_OF_SCOPE` con razón `REPEATED_INSUFFICIENCY`.
4. Capa 03 no puede quedarse en `CLARIFICATION_REQUIRED` indefinidamente. Si el dueño no responde en el plazo acordado, el caso pasa a `INSUFFICIENT_EVIDENCE`.
5. Capa 03 no puede abrir un `OperationalCase` con `READY_FOR_INVESTIGATION` si hay brechas críticas sin resolver.

---

## 9. Validación de suficiencia del candidato

Antes de asignar cualquier estado, Capa 03 ejecuta una validación de suficiencia sobre el `OperationalCaseCandidate`.

### Criterios mínimos para READY_FOR_INVESTIGATION

| Criterio | Requerido | Descripción |
|---|---|---|
| `primary_pathology` | Sí | Debe existir y ser no vacío |
| `available_variables` | Sí | Al menos una variable con `evidence_ref_id` trazable |
| `activated_formulas` | Sí | Al menos una fórmula con `required_variable_ids` |
| `principal_entropic_core` | Sí | Núcleo entrópico identificado por Capa 02 |
| `recommended_route` | Sí | Ruta investigativa con al menos un nodo |
| `evidence_gaps` críticos | No | No debe haber brechas con `priority=CRITICAL` sin fuente conocida |

### Criterios para CLARIFICATION_REQUIRED

| Criterio | Descripción |
|---|---|
| Brechas `HIGH` con fuente conocida | El dueño puede resolver la brecha con una acción concreta |
| Ambigüedades en entidades canónicas | El dueño puede confirmar el nombre canónico |
| Variables con `temporal_status=UNKNOWN` | El dueño puede confirmar el período |

### Criterios para INSUFFICIENT_EVIDENCE

| Criterio | Descripción |
|---|---|
| Sin `available_variables` | No hay ninguna variable con evidencia trazable |
| Brechas `CRITICAL` sin fuente | No hay forma conocida de obtener la variable |
| Sin `principal_entropic_core` | Capa 02 no pudo identificar el núcleo |

### Criterios para REJECTED_OUT_OF_SCOPE

| Criterio | Descripción |
|---|---|
| Patología fuera de dominio | SmartPyme no puede investigar esta patología |
| Caso duplicado | Ya existe un `OperationalCase` abierto para el mismo cliente y patología |
| `REPEATED_INSUFFICIENCY` | El caso fue devuelto más de dos veces por la misma razón |

---

## 10. Ejemplo — Perales: apertura del caso de stock

### Entrada (OperationalCaseCandidate de Capa 02)

```text
candidate_id: cand_perales_001
primary_pathology: inventario_no_confiable
available_variables:
  - stock_por_modelo_talle (Excel Paulita, observed_at: 2026-05-10, NEEDS_REVIEW)
  - precio_lista (Excel Paulita, valid_from: 2025-11-01, NEEDS_REVIEW)
evidence_gaps:
  - costo_reposicion (priority: HIGH, fuente: proveedor)
  - ventas_periodo (priority: MEDIUM, fuente: WhatsApp Mario)
principal_entropic_core: stock-precio-revendedores
recommended_route: P1 → stock_actual → capital_inmovilizado → precio_desalineado
status: PARTIAL_EVIDENCE
```

### Evaluación de Capa 03

```text
Pregunta 1 — Suficiencia mínima:
  primary_pathology: ✓ inventario_no_confiable
  available_variables: ✓ stock_por_modelo_talle (trazable)
  activated_formulas: ✓ capital_inmovilizado = stock_actual * costo_unitario
  principal_entropic_core: ✓ identificado
  brechas CRITICAL: ninguna
  → Suficiencia mínima: CUMPLIDA

Pregunta 2 — Alcance:
  patología investigable: ✓
  no duplica caso abierto: ✓
  → Alcance: DENTRO

Pregunta 3 — Aclaración:
  costo_reposicion: HIGH, fuente conocida (proveedor)
  → Hay brecha HIGH con fuente conocida
  → Se puede investigar sin costo_reposicion pero con alcance limitado
  → No es bloqueante para abrir el caso
```

### Salida (OperationalCase)

```text
OperationalCase:
  case_id: case_perales_001
  cliente_id: cliente_perales
  candidate_id: cand_perales_001
  primary_pathology: inventario_no_confiable
  status: READY_FOR_INVESTIGATION
  next_step: "Iniciar investigación sobre stock real vs stock declarado.
              Brecha de costo_reposicion queda pendiente para segunda fase."
```

---

## 11. Ejemplo — caso con CLARIFICATION_REQUIRED

### Entrada

```text
candidate_id: cand_perales_002
primary_pathology: precio_desalineado
available_variables:
  - precio_lista (Excel Paulita, valid_from: 2025-11-01)
evidence_gaps:
  - precio_venta_actual (priority: HIGH, fuente: Mario)
  - costo_reposicion (priority: HIGH, fuente: proveedor)
principal_entropic_core: precio-revendedores
```

### Evaluación

```text
Hay dos brechas HIGH con fuente conocida.
Sin precio_venta_actual no se puede calcular margen_reposicion.
El dueño puede confirmar el precio actual en una respuesta.
→ CLARIFICATION_REQUIRED
```

### Salida

```text
OperationalCase:
  case_id: case_perales_002
  status: CLARIFICATION_REQUIRED
  clarification_question: "¿Cuál es el precio de venta actual del Jean Azul talle 42?
                           ¿Es el mismo que figura en el Excel de Paulita ($5.500)
                           o lo actualizaste desde noviembre?"
  next_step: "Esperar respuesta del dueño antes de iniciar investigación."
```

---

## 12. Relación con capas anteriores y posteriores

### Lo que Capa 03 recibe (no modifica)

```text
InitialCaseAdmission     → Capa 01 — solo referencia
NormalizedEvidencePackage → Capa 1.5 — solo referencia
OperationalCaseCandidate  → Capa 02 — entrada principal
```

### Lo que Capa 03 produce

```text
OperationalCase → entrada para Capa 04+
```

### Lo que Capa 03 NO produce (pertenece a capas posteriores)

```text
DiagnosticReport     → Capa 04+
FindingRecord        → Capa 04+
ActionProposal       → Capa 05+
DecisionDraft        → Capa 06+
DecisionRecord       → Capa 06+
AuthorizationGate    → Capa 06+
```

---

## 13. Reglas rectoras completas

1. Capa 03 no diagnostica.
2. Capa 03 determina si existe un caso investigable.
3. La única salida de Capa 03 es `OperationalCase`.
4. `OperationalCase` tiene exactamente cuatro estados: `READY_FOR_INVESTIGATION`, `CLARIFICATION_REQUIRED`, `INSUFFICIENT_EVIDENCE`, `REJECTED_OUT_OF_SCOPE`.
5. Capa 03 no puede generar un nuevo `OperationalCaseCandidate`.
6. Capa 03 no puede solicitar más de una aclaración por ciclo.
7. Capa 03 no puede regresar a capas anteriores sin declarar razón explícita.
8. Si un caso fue devuelto más de dos veces por la misma razón, se declara `REJECTED_OUT_OF_SCOPE` con `REPEATED_INSUFFICIENCY`.
9. Capa 03 no re-normaliza, no re-mapea, no re-clasifica, no re-activa grafos.
10. Toda regresión debe ser explícita, registrada y justificada.
11. Sin evidencia trazable no hay caso investigable.
12. Sin núcleo entrópico identificado no hay caso investigable.
13. La ambigüedad se registra en el `OperationalCase`, no se oculta.
14. El dueño valida antes de que el sistema investigue formalmente.

---

## 14. Objetos conceptuales de Capa 03

```text
OperationalCase
  (con estados: READY_FOR_INVESTIGATION | CLARIFICATION_REQUIRED |
                INSUFFICIENT_EVIDENCE | REJECTED_OUT_OF_SCOPE)
```

Eso es todo.

Capa 03 no introduce nuevos objetos de diagnóstico, hallazgo, propuesta ni decisión.

---

## 15. Próximo paso

Implementar contratos Pydantic para `OperationalCase`:

```text
TS_030_001_CONTRATO_OPERATIONAL_CASE
app/contracts/operational_case_v2_contract.py
tests/contracts/test_operational_case_v2_contract.py
```

Campos mínimos requeridos:

```python
class OperationalCase(BaseModel):
    case_id: str
    cliente_id: str
    candidate_id: str
    source_admission_case_id: Optional[str]
    source_package_id: Optional[str]
    primary_pathology: str
    related_pathologies: list[str]
    activated_formulas: list[FormulaCandidate]
    required_variables: list[RequiredVariable]
    available_variables: list[AvailableVariableMatch]
    evidence_gaps: list[EvidenceGap]
    knowledge_tools: list[KnowledgeToolCandidate]
    investigation_graph: Optional[InvestigationGraph]
    principal_entropic_core: Optional[str]
    recommended_route: Optional[InvestigationRoute]
    status: Literal[
        "READY_FOR_INVESTIGATION",
        "CLARIFICATION_REQUIRED",
        "INSUFFICIENT_EVIDENCE",
        "REJECTED_OUT_OF_SCOPE",
    ]
    clarification_question: Optional[str]
    rejection_reason: Optional[str]
    insufficiency_reason: Optional[str]
    opened_at: Optional[datetime]
    next_step: str
```

Tests mínimos requeridos:

1. Construir `OperationalCase` con `READY_FOR_INVESTIGATION`.
2. `CLARIFICATION_REQUIRED` requiere `clarification_question` no vacío.
3. `REJECTED_OUT_OF_SCOPE` requiere `rejection_reason` no vacío.
4. `INSUFFICIENT_EVIDENCE` requiere `insufficiency_reason` no vacío.
5. `status` rechaza valores fuera del Literal.
6. `OperationalCase` no tiene atributos de `DiagnosticReport` ni `FindingRecord`.
