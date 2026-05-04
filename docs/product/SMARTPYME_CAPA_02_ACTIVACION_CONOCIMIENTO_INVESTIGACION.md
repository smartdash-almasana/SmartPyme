# SmartPyme — Capa 02: Activación de Conocimiento e Hipótesis Candidata

## Estado

DOCUMENTO RECTOR — REESCRITO v4.0  
**Fecha:** Mayo 2026  
**Cambio principal v4:** Capa 02 ya no produce diagnóstico, núcleo entrópico como output, roadmap de transformación ni propuestas de acción. Capa 02 produce exclusivamente `OperationalCaseCandidate`. Los conceptos de Núcleo Entrópico, Roadmap y Workflow quedan documentados como herramientas internas de análisis, no como outputs de la capa.

---

## Regla rectora

```text
Capa 02 no diagnostica.
Capa 02 no propone acción.
Capa 02 transforma dolor + intención + evidencia normalizada
en OperationalCaseCandidate.
```

---

## 1. Ubicación en el sistema

```text
Capa 01   → Admisión Epistemológica       → InitialCaseAdmission
Capa 1.5  → Normalización Documental      → NormalizedEvidencePackage
Capa 02   → Activación de Conocimiento    → OperationalCaseCandidate  ← esta capa
Capa 03   → Apertura del Caso Operativo   → OperationalCase
Capa 04+  → Investigación, diagnóstico, hallazgos, propuesta, decisión
```

Capa 02 es la capa de hipótesis.

Recibe evidencia normalizada y síntomas candidatos.  
Activa conocimiento relevante.  
Formula hipótesis investigables.  
Produce un candidato de caso operativo para que Capa 03 decida si puede abrirse.

---

## 2. Principio fundamental

Una demanda no activa una respuesta.

Una demanda activa un proceso de formulación de hipótesis.

```text
síntoma expresado
→ patologías posibles como candidatas (no confirmadas)
→ hipótesis investigable
→ skill candidata
→ variables requeridas
→ evidencia disponible
→ evidencia faltante
→ brechas para Capa 03
→ OperationalCaseCandidate
```

El sistema no responde directamente al dueño con una conclusión.  
El sistema construye la red de conocimiento necesaria para formular una hipótesis investigable.

---

## 3. Qué problema resuelve esta capa

Después de Capa 01 y Capa 1.5, SmartPyme ya tiene:

- demanda ordenada;
- fase clínica;
- personas;
- fuentes;
- evidencia disponible o faltante;
- entidades canónicas;
- variables limpias;
- fuente trazable;
- ventana temporal.

Pero todavía falta una pregunta central:

> ¿Qué conocimiento hay que activar para formular una hipótesis investigable sobre este caso?

Capa 02 responde esa pregunta.

---

## 4. Qué entra a Capa 02

Capa 02 recibe como entrada mínima:

```text
InitialCaseAdmission
NormalizedEvidencePackage
```

Desde `InitialCaseAdmission` recibe:

- demanda original;
- fase clínica;
- síntomas candidatos;
- patologías candidatas;
- tareas de evidencia;
- próximo paso inicial.

Desde `NormalizedEvidencePackage` recibe:

- documentos normalizados;
- entidades canónicas;
- aliases;
- mapeos de columnas;
- referencias de evidencia;
- variables limpias;
- ventanas temporales;
- alertas de ambigüedad.

---

## 5. Qué hace Capa 02

Capa 02:

- selecciona una patología prioritaria candidata desde el catálogo del Domain Pack activo;
- identifica patologías asociadas;
- activa Knowledge Tanks internos o externos relevantes para el caso;
- recupera fórmulas, métodos y formalismos útiles del Knowledge Tank;
- formula una hipótesis investigable a partir de los síntomas y patologías candidatas;
- identifica variables requeridas para verificar la hipótesis;
- cruza variables requeridas contra variables disponibles del paquete normalizado;
- detecta brechas de evidencia;
- arma un grafo de investigación como herramienta interna de análisis;
- identifica la ruta investigativa prioritaria dentro del grafo;
- produce un `OperationalCaseCandidate` con toda la información anterior.

**Nota sobre semántica de dominio:**  
Los síntomas, patologías, fórmulas y variables de PyME no viven en el core de Capa 02.  
Viven en catálogos, Domain Packs o Knowledge Tanks.  
Capa 02 activa ese conocimiento; no lo hardcodea.

---

## 6. Qué NO hace Capa 02

Capa 02 no:

- diagnostica;
- confirma ni descarta hallazgos;
- genera `DiagnosticReport`;
- genera `FindingRecord`;
- genera `ActionProposal`;
- genera `DecisionDraft`;
- genera `DecisionRecord`;
- activa `AuthorizationGate`;
- ejecuta acciones;
- produce un `OperationalCase` final (eso es Capa 03);
- decide si el caso puede investigarse (eso es Capa 03);
- inventa variables faltantes;
- fuerza una causa única;
- reemplaza la validación humana;
- produce roadmaps de transformación como output formal;
- produce el Núcleo Entrópico Principal como output formal;
- produce la Unidad Cuántica de Resolución como output formal.

El Núcleo Entrópico, el Roadmap y la Unidad Cuántica son herramientas internas de análisis que Capa 02 puede usar para priorizar la hipótesis. No son outputs de la capa.

---

## 7. Grafo investigativo

El grafo investigativo es la herramienta interna central de Capa 02.

```text
InvestigationGraph
```

El grafo representa relaciones entre:

- síntomas;
- patologías candidatas;
- fórmulas;
- variables;
- evidencias;
- brechas;
- rutas de investigación;
- riesgos;
- prioridades.

El grafo es dirigido porque muchas relaciones expresan dependencia o propagación.

Ejemplo:

```text
stock_caotico
→ inventario_no_confiable
→ capital_inmovilizado
→ precio_desalineado
→ margen_invisible
→ caida_de_ventas
→ flujo_caja_debilitado
```

El grafo es una herramienta de análisis interno. No es el output de la capa.  
El output es el `OperationalCaseCandidate` que resume lo que el grafo reveló.

---

## 8. Tipos de nodos del grafo

### SymptomNode

Representa un síntoma expresado por el dueño.

```text
symptom_id: stock_desordenado
```

### PathologyNode

Representa una patología operativa candidata.  
No es hallazgo confirmado.

```text
inventario_no_confiable
precio_desalineado
margen_invisible
flujo_caja_debilitado
```

### FormulaNode

Representa una fórmula o método que podría ser necesario para verificar la hipótesis.

```text
diferencia_stock = stock_teorico - stock_actual
capital_inmovilizado = stock_actual * costo_unitario
margen_reposicion = precio_venta - costo_reposicion
flujo_neto = ingresos_periodo - egresos_periodo
```

### VariableNode

Representa una variable requerida por una fórmula o método.

```text
stock_actual
stock_teorico
precio_venta
costo_reposicion
ventas_periodo
egresos_periodo
```

### EvidenceNode

Representa evidencia disponible que soporta una variable.

Debe tener:

```text
evidence_ref_id
source_id
document_id
field_mapping
temporal_window
confidence
```

### GapNode

Representa una variable faltante, ambigua o insuficiente.

```text
costo_unitario_faltante
ventas_periodo_anterior_faltante
fecha_no_detectada
proveedor_no_resuelto
```

### KnowledgeToolNode

Representa una herramienta conceptual, matemática, algorítmica o metodológica útil para la hipótesis.

```text
graph_theory
adjacency_matrix
route_analysis
centrality
time_series_comparison
margin_formula
cashflow_formula
inventory_reconciliation
```

---

## 9. Tipos de relaciones del grafo

```text
TRIGGERS        → síntoma activa patología candidata
REQUIRES        → fórmula/patología requiere variable
SUPPORTED_BY    → variable soportada por evidencia disponible
MISSING         → variable requerida no disponible
ASSOCIATED_WITH → patología relacionada con otra
IMPACTS         → patología puede impactar otra
PRIORITIZES     → ruta prioriza un nodo sobre otro
USES_TOOL       → ruta requiere herramienta auxiliar
HAS_GAP         → nodo tiene brecha de evidencia
DEPENDS_ON      → dependencia general entre nodos
```

---

## 10. Knowledge Tanks internos y externos

Capa 02 no depende solo de conocimiento de negocio.

Debe poder activar tanques de conocimiento internos o externos:

```text
negocio
matemática
teoría de grafos
estadística
optimización
contabilidad
finanzas
logística
investigación operativa
ciencia de datos
economía
derecho tributario
```

**Regla de separación:**

```text
Los síntomas, patologías, fórmulas y variables de PyME
viven en catálogos, Domain Packs o Knowledge Tanks.
Capa 02 activa ese conocimiento.
Capa 02 no hardcodea semántica PyME en el core.
```

La regla no es que SmartPyme sepa todo desde el inicio.

La regla es:

```text
SmartPyme debe saber dónde buscar el formalismo útil
para formular una hipótesis investigable correctamente.
```

---

## 11. Auxiliary Knowledge Tank Resolver

Capa 02 necesita un resolutor de conocimiento auxiliar:

```text
AuxiliaryKnowledgeTankResolver
```

Función:

```text
problema operativo
→ dominio de conocimiento relevante
→ herramienta conceptual o algorítmica útil
→ variables requeridas
→ forma de aplicación
```

Ejemplo:

```text
problema: stock_caotico_relacionado_con_caja
dominio: teoria_de_grafos
herramienta: grafo_dirigido_de_dependencias
uso: modelar propagación de inventario hacia precios, margen y flujo de caja
```

---

## 12. Teoría de grafos como tanque auxiliar

La teoría de grafos es un tanque auxiliar natural para SmartPyme porque permite representar relaciones binarias entre objetos:

```text
producto —proveído_por→ proveedor
producto —vendido_en→ canal
precio —impacta→ margen
margen —impacta→ caja
documento —contiene→ variable
variable —soporta→ fórmula
```

Herramientas útiles:

```text
grafo
digrafo
nodo
arista
camino
distancia
componente conexa
matriz de adyacencia
centralidad
grado
ruta crítica
subgrafo
```

Aplicación en Capa 02:

```text
detectar nodos críticos para la hipótesis
encontrar rutas de impacto
priorizar variables a investigar
ver dependencias entre variables
ubicar evidencia faltante
detectar subproblemas conectados
```

---

## 13. Hipótesis investigable

La hipótesis es el output conceptual central de Capa 02.

Una hipótesis investigable debe:

- ser falsable;
- declarar qué se investiga;
- declarar sobre qué entidad;
- declarar en qué período;
- declarar qué variables se necesitan para verificarla.

Ejemplo correcto:

```text
Investigar si existe pérdida de margen por desalineación entre costos reales
y precios de venta durante el período mayo 2026,
comparando Excel_Paulita contra lista de costos del proveedor.
```

Ejemplo incorrecto:

```text
Hay pérdida de margen.
```

La hipótesis no afirma. La hipótesis investiga.

---

## 14. Brechas de evidencia

Capa 02 compara:

```text
variables requeridas para verificar la hipótesis
vs
variables disponibles en el NormalizedEvidencePackage
```

Ejemplo:

```text
Requeridas:
- stock_actual
- costo_unitario
- precio_venta
- ventas_periodo

Disponibles:
- stock_actual
- precio_venta

Brechas:
- costo_unitario  (priority: HIGH)
- ventas_periodo  (priority: MEDIUM)
```

Cada brecha produce un `EvidenceGap`:

```text
EvidenceGap:
  variable_id
  reason
  impact
  required_source
  suggested_task
  priority
```

Las brechas se incluyen en el `OperationalCaseCandidate` para que Capa 03 decida si el caso puede abrirse.

---

## 15. Priorización de la hipótesis

Capa 02 prioriza la hipótesis según:

```text
1. riesgo de sangría activa
2. evidencia disponible
3. costo de obtener evidencia faltante
4. impacto económico estimado
5. urgencia del dueño
6. ventana temporal de las variables
7. confianza de los datos disponibles
```

La priorización orienta qué hipótesis formular primero.  
No es un diagnóstico.  
No es un roadmap de transformación.

---

## 16. Output: OperationalCaseCandidate

La única salida formal de Capa 02 es:

```text
OperationalCaseCandidate
```

Este objeto consolida todo lo que Capa 02 construyó y lo entrega a Capa 03 para que decida si puede convertirse en un `OperationalCase` formal.

Campos mínimos:

```text
candidate_id
cliente_id
source_admission_case_id
source_normalized_package_id
primary_pathology           patología principal candidata (no confirmada)
related_pathologies         patologías relacionadas candidatas
hypothesis                  hipótesis investigable formulada
activated_formulas          fórmulas activadas para verificar la hipótesis
required_variables          variables requeridas
available_variables         variables disponibles con evidencia trazable
evidence_gaps               brechas de evidencia detectadas
knowledge_tools             herramientas de conocimiento activadas
investigation_graph         grafo investigativo interno
recommended_route           ruta investigativa prioritaria
next_step                   instrucción para Capa 03 o para el dueño
status                      READY_FOR_INVESTIGATION | PARTIAL_EVIDENCE |
                            BLOCKED_MISSING_VARIABLES | PENDING_OWNER_VALIDATION
```

**El `OperationalCaseCandidate` no es un diagnóstico.**  
**El `OperationalCaseCandidate` no es un `OperationalCase`.**  
Es una propuesta investigativa que Capa 03 evalúa.

---

## 17. Diferencia entre OperationalCaseCandidate y OperationalCase

### OperationalCaseCandidate (Capa 02)

Es la propuesta investigativa.

Dice:

```text
Esto parece investigable.
Esta es la hipótesis.
Estas son las rutas posibles.
Estas variables faltan.
Esta es la ruta prioritaria.
```

### OperationalCase (Capa 03)

Nace después, cuando Capa 03 valida la suficiencia del candidato.

Solo debe crearse cuando:

```text
evidencia mínima suficiente
dueño valida alcance
variables críticas disponibles o tareas aceptadas
ruta prioritaria aprobada
```

---

## 18. Herramientas internas de análisis (no outputs)

Capa 02 puede usar internamente las siguientes herramientas de análisis para construir el `OperationalCaseCandidate`:

### Núcleo Entrópico Principal (herramienta interna)

El nodo del grafo con mayor poder de reorganización sistémica.  
Ayuda a priorizar qué hipótesis formular primero.  
**No es un output de Capa 02.**  
Si se incluye en el `OperationalCaseCandidate`, es como campo informativo para Capa 03.

### Cuadro Sintomático Priorizado (herramienta interna)

Tabla de síntomas ordenados por impacto sistémico.  
Ayuda a seleccionar la patología principal candidata.  
**No es un output de Capa 02.**

### Roadmap de Transformación Inicial (herramienta interna)

Secuencia de fases de intervención propuesta.  
Ayuda a contextualizar la hipótesis en el tiempo.  
**No es un output de Capa 02.**  
El roadmap formal pertenece a capas posteriores.

### WorkflowTrace y EpistemicPrintCycle (herramientas internas)

Trazado del flujo operativo y ciclos de impresión epistémica.  
Ayudan a entender cómo fluye la información en el negocio.  
**No son outputs de Capa 02.**  
Son insumos para construir el grafo y la hipótesis.

---

## 19. Qué pertenece a capas posteriores

Los siguientes elementos **no pertenecen a Capa 02**:

```text
DiagnosticReport          → Capa 04+
FindingRecord             → Capa 04+
ActionProposal            → Capa 05+
DecisionDraft             → Capa 06+
DecisionRecord            → Capa 06+
AuthorizationGate         → Capa 06+
OperationalCase           → Capa 03
Roadmap formal            → Capa 04+
Propuesta de acción       → Capa 05+
```

---

## 20. Reglas rectoras

1. Capa 02 no diagnostica.
2. Capa 02 no propone acción.
3. Capa 02 transforma dolor + intención + evidencia normalizada en `OperationalCaseCandidate`.
4. La única salida formal de Capa 02 es `OperationalCaseCandidate`.
5. Las patologías en Capa 02 son candidatas, no confirmadas.
6. La hipótesis no afirma: investiga.
7. Los síntomas, patologías, fórmulas y variables de PyME viven en catálogos, Domain Packs o Knowledge Tanks. Capa 02 los activa; no los hardcodea.
8. Toda fórmula debe declarar variables requeridas.
9. Toda variable requerida debe mapearse contra evidencia disponible o gap.
10. Toda ruta debe tener prioridad explícita.
11. Toda activación de conocimiento debe registrar dominio y herramienta.
12. Los Knowledge Tanks pueden ser internos o externos.
13. La teoría de grafos es un tanque auxiliar válido.
14. El Núcleo Entrópico, el Roadmap y el Cuadro Sintomático son herramientas internas de análisis, no outputs formales.
15. Capa 03 decide si el candidato puede convertirse en caso investigable.
16. El dueño valida antes de investigación formal.
17. Sin entidad, fuente y tiempo no hay variable investigable.
18. Sin variables suficientes no hay hipótesis verificable.
19. La ambigüedad se registra en el candidato, no se oculta.
20. Capa 02 no puede regresar a capas anteriores sin declarar razón explícita.

---

## 21. Objetos conceptuales de Capa 02

### Outputs formales

```text
OperationalCaseCandidate
```

### Objetos internos de análisis (no outputs)

```text
InvestigationGraph
InvestigationNode
InvestigationEdge
InvestigationRoute
InvestigationPlan
KnowledgeDomain
KnowledgeToolCandidate
FormulaCandidate
RequiredVariable
AvailableVariableMatch
EvidenceGap
```

### Herramientas internas de priorización (no outputs)

```text
PrincipalEntropicCore       (herramienta interna)
QuantumResolutionUnit       (herramienta interna)
PrioritizedSymptomTable     (herramienta interna)
InitialTransformationRoadmap (herramienta interna)
HumanKnowledgeNode          (herramienta interna)
ToolNode                    (herramienta interna)
WorkflowStepNode            (herramienta interna)
WorkflowTrace               (herramienta interna)
EpistemicPrintCycle         (herramienta interna)
```

---

## 22. Ejemplo — Perales: de síntoma a candidato

### Entrada

```text
InitialCaseAdmission:
  fase: INESTABILIDAD
  síntomas: [stock_desordenado, precios_desactualizados]
  patologías candidatas: [inventario_no_confiable, precio_desalineado]

NormalizedEvidencePackage:
  variables disponibles:
    - stock_por_modelo_talle (Excel Paulita, observed_at: 2026-05-10)
    - precio_lista (Excel Paulita, valid_from: 2025-11-01)
  brechas:
    - costo_reposicion (priority: HIGH)
    - ventas_periodo (priority: MEDIUM)
```

### Proceso interno de Capa 02

```text
1. Activar Knowledge Tank: finanzas + stock
2. Seleccionar patología principal: inventario_no_confiable
3. Formular hipótesis:
   "Investigar si existe diferencia entre stock declarado y stock real
    para pantalones jean azul, comparando Excel_Paulita_2026_05
    contra conteo físico, período mayo 2026."
4. Activar fórmula: diferencia_stock = stock_teorico - stock_actual
5. Variables requeridas: stock_teorico, stock_actual
6. Variables disponibles: stock_actual (Excel Paulita)
7. Brecha: stock_teorico (no disponible, priority: HIGH)
8. Ruta prioritaria: stock_actual → diferencia_stock → capital_inmovilizado
```

### Salida (OperationalCaseCandidate)

```text
OperationalCaseCandidate:
  candidate_id: cand_perales_001
  primary_pathology: inventario_no_confiable
  hypothesis: "Investigar si existe diferencia entre stock declarado y stock real..."
  activated_formulas: [diferencia_stock, capital_inmovilizado]
  available_variables: [stock_actual]
  evidence_gaps: [stock_teorico (HIGH), costo_reposicion (HIGH), ventas_periodo (MEDIUM)]
  status: PARTIAL_EVIDENCE
  next_step: "Capa 03: evaluar si el candidato tiene suficiencia para abrir el caso."
```

---

## 23. Relación con Capa 03

Capa 02 entrega el `OperationalCaseCandidate` a Capa 03.

Capa 03 evalúa:

```text
¿El candidato tiene suficiencia mínima para investigar?
¿Está dentro del alcance operativo?
¿Se necesita aclaración antes de abrir el caso?
```

Capa 03 produce el `OperationalCase` con uno de estos estados:

```text
READY_FOR_INVESTIGATION
CLARIFICATION_REQUIRED
INSUFFICIENT_EVIDENCE
REJECTED_OUT_OF_SCOPE
```

Capa 02 no toma esa decisión.

---

## 24. Próximos pasos

### Contratos ya implementados

```text
TS_020_001_CONTRATOS_ACTIVACION_INVESTIGATIVA
app/contracts/investigation_contract.py
```

### Próximas tareas sugeridas

```text
TS_020_002_INVESTIGATION_SERVICE_MINIMO
  app/services/investigation_service.py
  → InvestigationService.build(admission, normalized_package) → OperationalCaseCandidate

TS_020_003_CONTRATOS_WORKFLOW
  app/contracts/workflow_contract.py
  → HumanKnowledgeNode, ToolNode, WorkflowStepNode, WorkflowTrace, EpistemicPrintCycle
  (herramientas internas de análisis, no outputs de Capa 02)
```
