# SmartPyme — Capa 02: Activación de Conocimiento e Investigación

## Estado

DOCUMENTO RECTOR — ACTUALIZADO

**Versión:** 3.0  
**Fecha:** Mayo 2026  
**Cambios v2:** Incorporación del Núcleo Entrópico Principal, Unidad Cuántica de Resolución, Cuadro Sintomático Priorizado, Roadmap de Transformación Inicial y ejemplo conversacional Mario/Perales.  
**Cambios v3:** Incorporación de Herramientas y Flujos de Trabajo, HumanKnowledgeNode, ToolNode, WorkflowStepNode, WorkflowTrace, EpistemicPrintCycle, dimensión temporal en flujos y actores, investigación forense-operativa y relación entre workflow roto y Núcleo Entrópico Principal.

Este documento define la Capa 2 de SmartPyme: la capa que transforma una admisión validada y evidencia normalizada en un grafo investigativo **contraído en un núcleo atacable**.

No implementa código.  
No define todavía diagnóstico.  
No ejecuta acciones.

---

## 1. Ubicación en el sistema

```text
Capa 1   → Admisión Epistemológica
Capa 1.5 → Normalización Documental, Entidades y Tiempo
Capa 2   → Activación de Conocimiento e Investigación
```

Capa 1 produce:

```text
InitialCaseAdmission
```

Capa 1.5 produce:

```text
NormalizedEvidencePackage
```

Capa 2 produce:

```text
OperationalCaseCandidate
InvestigationGraph
InvestigationPlan
PrincipalEntropicCore
InitialTransformationRoadmap
WorkflowTrace
EpistemicPrintCycle
```

---

## 2. Principio fundamental

Una demanda no activa una respuesta.

Una demanda activa un grafo investigativo.

```text
síntoma expresado
→ patología principal candidata
→ patologías asociadas
→ fórmulas/métodos relacionados
→ variables requeridas
→ evidencia disponible
→ brechas
→ ruta prioritaria de investigación
```

El sistema no responde directamente al dueño con una conclusión.  
El sistema construye la red de conocimiento necesaria para investigar correctamente.

---

## 3. Qué problema resuelve esta capa

Después de Capa 1 y Capa 1.5, SmartPyme ya tiene:

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

> ¿Qué conocimiento hay que activar para investigar este caso?

Capa 2 responde esa pregunta.

---

## 4. Qué entra a Capa 2

Capa 2 recibe como entrada mínima:

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

## 5. Qué hace Capa 2

Capa 2:

- selecciona una patología prioritaria candidata;
- identifica patologías asociadas;
- activa Knowledge Tanks internos o externos;
- recupera fórmulas, métodos y formalismos útiles;
- identifica variables requeridas;
- cruza variables requeridas contra variables disponibles;
- detecta brechas de evidencia;
- **mapea actores humanos como HumanKnowledgeNode**;
- **mapea herramientas operativas como ToolNode**;
- **reconstruye flujos de trabajo como WorkflowStepNode**;
- **detecta puntos de fricción y pérdida en los flujos**;
- arma un grafo de investigación;
- **contrae el grafo en un Núcleo Entrópico Principal**;
- **identifica la Unidad Cuántica de Resolución**;
- **produce un Cuadro Sintomático Priorizado**;
- prioriza rutas por ROI, riesgo, evidencia disponible y costo;
- **genera un Roadmap de Transformación Inicial**;
- **registra el ciclo epistémico de impresión progresiva**;
- produce un candidato de caso operativo.

---

## 6. Qué no hace Capa 2

Capa 2 no:

- diagnostica;
- emite hallazgos confirmados;
- ejecuta acciones;
- decide por el dueño;
- calcula fórmulas finales como verdad cerrada;
- crea un `OperationalCase` final;
- reemplaza la validación humana;
- inventa variables faltantes;
- fuerza una causa única.

---

## 7. Grafo investigativo

La unidad central de la capa es:

```text
InvestigationGraph
```

El grafo representa relaciones entre:

- síntomas;
- patologías;
- fórmulas;
- variables;
- evidencias;
- brechas;
- rutas de investigación;
- riesgos;
- prioridades.

El grafo puede ser dirigido porque muchas relaciones expresan dependencia o propagación.

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

---

## 8. Tipos de nodos

### SymptomNode

Representa un síntoma expresado por el dueño.

Ejemplo:

```text
"No sé cuánto stock tengo"
```

Nodo:

```text
symptom_id: stock_desordenado
```

---

### PathologyNode

Representa una patología operativa candidata.

Ejemplos:

```text
inventario_no_confiable
precio_desalineado
margen_invisible
flujo_caja_debilitado
```

---

### FormulaNode

Representa una fórmula o método que podría ser necesario.

Ejemplos:

```text
diferencia_stock = stock_teorico - stock_actual
capital_inmovilizado = stock_actual * costo_unitario
margen_reposicion = precio_venta - costo_reposicion
flujo_neto = ingresos_periodo - egresos_periodo
```

---

### VariableNode

Representa una variable requerida por una fórmula o método.

Ejemplos:

```text
stock_actual
stock_teorico
precio_venta
costo_reposicion
ventas_periodo
egresos_periodo
```

---

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

---

### GapNode

Representa una variable faltante, ambigua o insuficiente.

Ejemplos:

```text
costo_unitario_faltante
ventas_periodo_anterior_faltante
fecha_no_detectada
proveedor_no_resuelto
```

---

### KnowledgeToolNode

Representa una herramienta conceptual, matemática, algorítmica o metodológica útil.

Ejemplos:

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

### HumanKnowledgeNode

Representa un actor humano de la PyME como nodo de conocimiento operativo.

Cada persona es un testigo parcial de la realidad del negocio.

Tiene conocimiento fragmentado, sesgado y temporalmente acotado.

Ejemplos:

```text
Mario (dueño): visión general, decisiones, caja negra, contexto informal
Paulita (administración): stock, precios, ventas operativas, Excel
Andrés (contador): gastos blancos, caja formal, declaraciones
Ana (compras): proveedores, costos, condiciones comerciales
```

Estructura:

```text
HumanKnowledgeNode:
  person_id
  name
  role
  knowledge_domains       qué sabe esta persona
  tools_used              herramientas que usa
  information_owned       qué información gestiona
  information_format      en qué formato la tiene
  availability            cuándo está disponible
  reliability             confianza en su información
  temporal_scope          de qué período tiene información
  contact_channel         cómo se le pide información
```

---

### ToolNode

Representa una herramienta operativa real usada en el negocio.

No es una herramienta conceptual o matemática.

Es el instrumento concreto con el que el negocio opera, registra y comunica.

Ejemplos:

```text
WhatsApp
Excel
PDF
banco
sistema contable
facturador
cuaderno
memoria del dueño
```

Estructura:

```text
ToolNode:
  tool_id
  tool_name
  tool_type               digital / físico / humano
  used_by_person_ids      personas que lo usan
  stores_information      qué información almacena
  information_format      formato de la información
  reliability             confianza en la información que produce
  temporal_coverage       de qué período tiene datos
  access_difficulty       qué tan fácil es acceder a la información
  loss_risk               riesgo de pérdida de información
```

---

### WorkflowStepNode

Representa un paso operativo concreto en el flujo de trabajo del negocio.

Cada paso tiene un actor, una herramienta, una acción, una entrada, una salida y una dimensión temporal.

Estructura:

```text
WorkflowStepNode:
  step_id
  step_name
  actor_person_id         quién ejecuta el paso
  tool_id                 herramienta que usa
  action                  qué hace exactamente
  input                   qué recibe como entrada
  output                  qué produce como salida
  next_step_id            siguiente paso en el flujo
  friction_point          dónde se traba o demora
  loss_point              dónde se pierde información o valor
  evidence_generated      qué evidencia produce este paso
  operational_risk        riesgo operativo del paso
  estimated_duration      tiempo estimado del paso
  temporal_window         ventana temporal del paso
```

---

## 9. Tipos de relaciones

```text
TRIGGERS
REQUIRES
SUPPORTED_BY
MISSING
ASSOCIATED_WITH
IMPACTS
PRIORITIZES
USES_TOOL
HAS_GAP
DEPENDS_ON
```

### TRIGGERS

Un síntoma activa una patología candidata.

```text
stock_desordenado → TRIGGERS → inventario_no_confiable
```

### ASSOCIATED_WITH

Una patología está relacionada con otra.

```text
inventario_no_confiable → ASSOCIATED_WITH → precio_desalineado
```

### REQUIRES

Una fórmula o patología requiere variables.

```text
capital_inmovilizado → REQUIRES → stock_actual
capital_inmovilizado → REQUIRES → costo_unitario
```

### SUPPORTED_BY

Una variable está soportada por evidencia.

```text
stock_actual → SUPPORTED_BY → excel_paulita.stock
```

### MISSING

Una variable requerida no está disponible.

```text
costo_reposicion → MISSING → gap_costo_reposicion
```

### IMPACTS

Una patología puede impactar otra.

```text
precio_desalineado → IMPACTS → margen_invisible
margen_invisible → IMPACTS → flujo_caja_debilitado
```

### USES_TOOL

Una ruta investigativa requiere una herramienta auxiliar.

```text
red_de_dependencias → USES_TOOL → graph_theory
```

### OPERATED_BY

Una herramienta es operada por un actor humano.

```text
excel_paulita → OPERATED_BY → paulita
```

### FEEDS_INTO

Un paso de workflow alimenta al siguiente.

```text
whatsapp_mario → FEEDS_INTO → excel_paulita
```

### HAS_FRICTION

Un paso de workflow tiene un punto de fricción documentado.

```text
paso_registro_venta → HAS_FRICTION → intermediario_paulita
```

### HAS_LOSS

Un paso de workflow tiene un punto de pérdida de información o valor.

```text
paso_caja_negra → HAS_LOSS → gap_gastos_informales
```

---

## 10. Knowledge Tanks internos y externos

Capa 2 no depende solo de conocimiento de negocio.

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

La regla no es que SmartPyme sepa todo desde el inicio.

La regla es:

```text
SmartPyme debe saber dónde buscar el formalismo útil para investigar correctamente.
```

---

## 11. Auxiliary Knowledge Tank Resolver

Capa 2 necesita un resolutor de conocimiento auxiliar:

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
matriz de incidencia
centralidad
grado
ruta crítica
subgrafo
```

Aplicación SmartPyme:

```text
detectar nodos críticos
encontrar rutas de impacto
priorizar investigación
ver dependencias entre variables
ubicar evidencia faltante
detectar subproblemas conectados
```

---

## 13. Ejemplo: stock caótico

### Demanda del dueño

```text
No sé cuánto stock tengo.
No sé si los precios están bien.
No me dan los números.
```

### Capa 1

```text
fase: INESTABILIDAD o SANGRIA según contexto
síntomas:
  - stock_desordenado
  - precios_desactualizados
  - control_operativo_fragil
```

### Capa 1.5

Normaliza evidencia:

```text
producto
cantidad
precio
fecha
proveedor
```

Produce variables:

```text
stock_actual
precio_venta
proveedor
observed_at
```

### Capa 2

Activa grafo:

```text
stock_desordenado
→ inventario_no_confiable
→ capital_inmovilizado
→ precio_desalineado
→ margen_invisible
→ caida_de_ventas
→ flujo_caja_debilitado
```

---

## 14. Fórmulas relacionadas

### Inventario no confiable

```text
diferencia_stock = stock_teorico - stock_actual
```

Variables:

```text
stock_teorico
stock_actual
```

---

### Capital inmovilizado

```text
capital_inmovilizado = stock_actual * costo_unitario
```

Variables:

```text
stock_actual
costo_unitario
```

---

### Precio desalineado

```text
margen_reposicion = precio_venta - costo_reposicion
```

Variables:

```text
precio_venta
costo_reposicion
```

---

### Caída de ventas

```text
variacion_ventas = ventas_periodo_actual - ventas_periodo_anterior
```

Variables:

```text
ventas_periodo_actual
ventas_periodo_anterior
```

---

### Flujo de caja debilitado

```text
flujo_neto = ingresos_periodo - egresos_periodo
```

Variables:

```text
ingresos_periodo
egresos_periodo
```

---

## 15. Variables relacionadas

Capa 2 no mira variables aisladas.

Construye relaciones entre variables:

```text
stock_actual
→ afecta capital_inmovilizado
→ afecta necesidad_de_liquidez

precio_venta
→ afecta margen
→ afecta competitividad
→ afecta ventas

ventas_periodo
→ afecta flujo_caja
→ afecta reposición

costo_reposicion
→ afecta precio_correcto
→ afecta margen_real
```

---

## 16. Brechas de evidencia

Capa 2 compara:

```text
variables requeridas
vs
variables disponibles
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
- costo_unitario
- ventas_periodo
```

Cada brecha debe producir:

```text
EvidenceGap:
  variable_id
  reason
  impact
  required_source
  suggested_task
  priority
```

---

## 17. Priorización investigativa

El sistema no investiga todo.

Prioriza rutas según:

```text
1. riesgo de sangría
2. evidencia disponible
3. costo de obtener evidencia faltante
4. impacto económico estimado
5. urgencia del dueño
6. ventana temporal
7. confianza de los datos
```

Ejemplo:

```text
Primero validar stock actual y costo de reposición.
Luego calcular capital inmovilizado.
Después revisar precio desalineado y margen.
Finalmente medir impacto en ventas y caja.
```

---

## 18. Output: OperationalCaseCandidate

Capa 2 produce un candidato de caso operativo.

No es diagnóstico final.

Debe contener:

```text
candidate_id
cliente_id
source_admission_case_id
source_normalized_package_id
primary_pathology
related_pathologies
activated_formulas
required_variables
available_variables
evidence_gaps
knowledge_tools
investigation_graph
recommended_route
next_step
status
```

---

## 19. Diferencia con OperationalCase

### OperationalCaseCandidate

Es candidato investigativo.

Dice:

```text
Esto parece investigable.
Estas son las rutas posibles.
Estas variables faltan.
Esta es la ruta prioritaria.
```

### OperationalCase

Nace después.

Solo debe crearse cuando:

```text
evidencia mínima suficiente
dueño valida alcance
variables críticas disponibles o tareas aceptadas
ruta prioritaria aprobada
```

---

## 20. Reglas rectoras

1. Una demanda activa un grafo, no una respuesta.
2. Capa 2 no diagnostica.
3. Capa 2 no ejecuta acciones.
4. Capa 2 no inventa variables.
5. Toda fórmula debe declarar variables requeridas.
6. Toda variable requerida debe mapearse contra evidencia disponible o gap.
7. Toda ruta debe tener prioridad explícita.
8. Toda activación de conocimiento debe registrar dominio y herramienta.
9. Los Knowledge Tanks pueden ser internos o externos.
10. La teoría de grafos es un tanque auxiliar válido.
11. El output es `OperationalCaseCandidate`, no `OperationalCase`.
12. El dueño valida antes de investigación formal.
13. Sin entidad, fuente y tiempo no hay variable investigable.
14. Sin variables suficientes no hay diagnóstico.
15. La ambigüedad se registra, no se oculta.
16. **El grafo debe contraerse en un Núcleo Entrópico Principal antes de presentar al dueño.**
17. **No se ataca el síntoma más ruidoso. Se ataca el núcleo con mayor poder de reorganización.**
18. **El Roadmap de Transformación Inicial debe tener al menos tres fases temporales.**
19. **La Unidad Cuántica de Resolución es el mínimo foco causal atacable en el primer ciclo.**
20. **El Cuadro Sintomático Priorizado ordena síntomas por impacto sistémico, no por urgencia declarada.**
21. **No hay diagnóstico operativo sin mapa de herramientas y flujos.**
22. **El núcleo entrópico suele estar en la unión entre herramienta, persona y flujo.**
23. **Cada actor humano es un HumanKnowledgeNode con conocimiento parcial y temporalmente acotado.**
24. **Cada herramienta operativa es un ToolNode con riesgo de pérdida de información.**
25. **Cada paso operativo es un WorkflowStepNode con dimensión temporal obligatoria.**
26. **La realidad operativa se imprime progresivamente por ciclos epistémicos trazables.**
27. **Toda entidad, herramienta, flujo y paso debe tener dimensión temporal.**
28. **Un workflow roto es evidencia de un núcleo entrópico activo.**

---

## 21. Objetos conceptuales mínimos

```text
KnowledgeDomain
KnowledgeToolCandidate
FormulaCandidate
RequiredVariable
AvailableVariableMatch
EvidenceGap
InvestigationNode
InvestigationEdge
InvestigationGraph
InvestigationRoute
InvestigationPlan
OperationalCaseCandidate
PrincipalEntropicCore
InitialTransformationRoadmap
```

---

## 22. Próximo paso

Contratos Pydantic ya implementados en:

```text
TS_020_001_CONTRATOS_ACTIVACION_INVESTIGATIVA
app/contracts/investigation_contract.py
tests/contracts/test_investigation_contract.py
```

Próxima tarea sugerida:

```text
TS_020_002_CONTRATOS_NUCLEO_ENTROPICO
```

Archivos sugeridos:

```text
app/contracts/entropic_core_contract.py
tests/contracts/test_entropic_core_contract.py
```

---

## 23. Núcleo Entrópico Principal

### Definición

El **Núcleo Entrópico Principal** es el mínimo foco causal cuya resolución reduce el máximo desorden conectado.

No es el síntoma más ruidoso.

No es la queja más urgente del dueño.

Es el nodo del grafo investigativo con mayor poder de reorganización sistémica: el punto donde una intervención mínima produce el mayor colapso de entropía operativa.

### Principio rector

```text
No se ataca el síntoma más ruidoso.
Se ataca el núcleo con mayor poder de reorganización.
```

### Por qué existe este concepto

El grafo investigativo puede tener decenas de nodos y relaciones.

Sin contracción, el sistema presenta al dueño un mapa complejo que no puede atacar.

La contracción del grafo en un núcleo entrópico permite:

- identificar el punto de máximo apalancamiento;
- proponer una intervención mínima y concreta;
- ordenar el resto del trabajo en fases posteriores;
- evitar la parálisis por análisis;
- dar al dueño una dirección clara y ejecutable.

### Cómo se identifica

El Núcleo Entrópico Principal se identifica por:

```text
1. centralidad en el grafo (nodo con más conexiones entrantes y salientes);
2. número de patologías que dependen de él;
3. impacto económico estimado de su resolución;
4. disponibilidad de evidencia para atacarlo;
5. costo de intervención;
6. velocidad de impacto (tiempo hasta valor).
```

El núcleo no siempre es la patología más grave.

A veces es la más conectada.

A veces es la más barata de resolver.

A veces es la que desbloquea todas las demás.

### Estructura conceptual

```text
PrincipalEntropicCore:
  core_id
  cliente_id
  graph_id
  primary_node_id           nodo central del núcleo
  connected_pathology_ids   patologías que dependen del núcleo
  connected_symptom_ids     síntomas que alimentan el núcleo
  resolution_impact         impacto estimado de resolver el núcleo
  required_variables        variables mínimas para atacar el núcleo
  available_variables       variables ya disponibles
  critical_gaps             brechas que bloquean la resolución
  resolution_cost           costo estimado de intervención
  time_to_value             tiempo estimado hasta primer resultado
  confidence                confianza en la identificación del núcleo
  rationale                 justificación de por qué este es el núcleo
```

### Ejemplo: Perales

El grafo de Perales tiene:

```text
stock_desordenado
→ inventario_no_confiable
→ capital_inmovilizado
→ precio_desalineado
→ margen_invisible
→ politica_comercial_informal
→ flujo_caja_debilitado
```

El Núcleo Entrópico Principal no es `flujo_caja_debilitado` (el síntoma más doloroso).

Es el nodo `stock-precio-revendedores` porque:

- concentra `inventario_no_confiable`, `precios_desalineados`, `margen_invisible`, `política_comercial_informal`, `capital_inmovilizado` y `flujo_caja_debilitado`;
- tiene evidencia parcialmente disponible (Excel de Paulita);
- su resolución desbloquea todas las demás patologías;
- el costo de intervención es bajo (ordenar el Excel + conteo físico);
- el tiempo hasta valor es corto (días, no meses).

---

## 24. Unidad Cuántica de Resolución

### Definición

La **Unidad Cuántica de Resolución** es el mínimo trabajo ejecutable en un ciclo que produce un resultado verificable sobre el Núcleo Entrópico Principal.

Es la granularidad mínima de intervención.

No es un proyecto.

No es un roadmap completo.

Es la acción más pequeña que produce evidencia real de avance.

### Principio rector

```text
El sistema no propone proyectos.
El sistema propone unidades cuánticas de resolución.
```

### Por qué existe este concepto

El dueño de una PyME no puede ejecutar un plan de 6 meses.

Puede ejecutar una tarea concreta esta semana.

La Unidad Cuántica de Resolución convierte el Núcleo Entrópico en una acción ejecutable inmediata.

### Estructura conceptual

```text
QuantumResolutionUnit:
  unit_id
  core_id
  description               qué se hace exactamente
  responsible               quién lo hace
  required_inputs           qué se necesita para ejecutarlo
  expected_output           qué produce cuando termina
  verification_criterion    cómo se sabe que terminó
  estimated_duration        tiempo estimado
  blocks_if_missing         qué se bloquea si no se ejecuta
```

### Ejemplo: Perales

```text
QuantumResolutionUnit:
  description: "Pedir a Paulita el Excel de stock con modelo, talle, color, cantidad y precio."
  responsible: dueño
  required_inputs: acceso a Paulita
  expected_output: Excel con columnas completas
  verification_criterion: el Excel tiene al menos modelo, talle, cantidad y precio
  estimated_duration: 1 día
  blocks_if_missing: no se puede calcular capital inmovilizado ni precio desalineado
```

---

## 25. Cuadro Sintomático Priorizado

### Definición

El **Cuadro Sintomático Priorizado** es la representación ordenada de los síntomas del caso, clasificados por impacto sistémico sobre el Núcleo Entrópico Principal.

No ordena por urgencia declarada del dueño.

Ordena por poder de reorganización: qué síntoma, si se resuelve, reduce más el desorden total.

### Estructura conceptual

```text
PrioritizedSymptomTable:
  table_id
  core_id
  entries:
    - symptom_id
      symptom_label
      systemic_impact_score   0.0 a 1.0
      connected_pathologies   cuántas patologías dependen de este síntoma
      evidence_available      si hay evidencia para investigarlo
      resolution_priority     P1 / P2 / P3
      notes
```

### Ejemplo: Perales

| Síntoma | Impacto sistémico | Patologías conectadas | Evidencia | Prioridad |
|---|---|---|---|---|
| stock_desordenado | 0.95 | 6 | Parcial (Excel Paulita) | P1 |
| precios_desactualizados | 0.88 | 4 | Parcial (Excel Paulita) | P1 |
| politica_comercial_informal | 0.75 | 3 | No disponible | P2 |
| flujo_caja_debilitado | 0.70 | 2 | No disponible | P2 |
| margen_invisible | 0.65 | 2 | Parcial | P2 |
| capital_inmovilizado | 0.60 | 1 | Parcial | P3 |

El síntoma más doloroso para el dueño puede ser `flujo_caja_debilitado`.

Pero el de mayor impacto sistémico es `stock_desordenado` porque conecta con 6 patologías.

Por eso se ataca primero.

---

## 26. Roadmap de Transformación Inicial

### Definición

El **Roadmap de Transformación Inicial** es la secuencia de fases de intervención propuesta por Capa 2, ordenada por impacto sistémico y viabilidad operativa.

No es un plan de proyecto.

Es una propuesta de orden de ataque al desorden.

### Principio rector

```text
Primero el núcleo.
Después las consecuencias del núcleo.
Después la optimización.
```

### Estructura conceptual

```text
InitialTransformationRoadmap:
  roadmap_id
  core_id
  cliente_id
  phases:
    - phase_id
      phase_number
      name
      objective
      target_pathologies
      target_symptoms
      required_evidence
      expected_outputs
      estimated_duration
      success_criteria
      depends_on_phase_id
```

### Ejemplo: Perales

```text
InitialTransformationRoadmap:
  roadmap_id: roadmap_perales_001

  Fase 1 — Mes 1: Atacar núcleo stock/precio/revendedores
    objetivo: reconstruir base mínima de stock, precios y flujo de ventas
    patologías objetivo:
      - inventario_no_confiable
      - precios_desalineados
    evidencia requerida:
      - Excel Paulita (stock + precios)
      - WhatsApps de ventas a revendedores
    outputs esperados:
      - stock real por modelo/talle/color
      - precio actualizado por producto
      - ventas del período
    criterio de éxito:
      - stock contado y registrado
      - precios actualizados en sistema
      - ventas del mes consolidadas
    duración estimada: 2–3 semanas

  Fase 2 — Mes 2: Caja y margen
    objetivo: consolidar resultado real y detectar sangría
    patologías objetivo:
      - margen_invisible
      - flujo_caja_debilitado
    evidencia requerida:
      - reporte contador (gastos blancos)
      - Excel sueldos
      - ventas consolidadas de Fase 1
    outputs esperados:
      - resultado real del período
      - margen por producto
      - flujo neto
    criterio de éxito:
      - resultado real calculado
      - margen por producto conocido
    duración estimada: 2–3 semanas
    depende de: Fase 1

  Fase 3 — Mes 3: Política comercial y ventas
    objetivo: formalizar política de precios y canales
    patologías objetivo:
      - politica_comercial_informal
      - capital_inmovilizado_sin_rotacion
    evidencia requerida:
      - lista de revendedores
      - condiciones de venta actuales
      - historial de ventas de Fase 1 y 2
    outputs esperados:
      - política de precios documentada
      - condiciones por canal
      - plan de rotación de stock
    criterio de éxito:
      - política de precios aprobada por el dueño
      - condiciones por revendedor documentadas
    duración estimada: 3–4 semanas
    depende de: Fase 2
```

---

## 27. Ejemplo conversacional — Mario y Perales

### Contexto

Mario es el dueño de Textil Perales.

Tiene entre 15.000 y 20.000 pantalones de jean azules.

No sabe cuántos tiene exactamente.

No sabe los precios.

Los vende a revendedores.

Paulita anota las ventas en un Excel cuando Mario le manda un WhatsApp.

### Conversación con SmartPyme

---

**Mario:**

```text
No sé cuánto stock tengo.
No sé si los precios están bien.
No me dan los números.
```

---

**SmartPyme (Capa 1 — Admisión):**

```text
Entiendo. Antes de avanzar, necesito entender mejor el negocio.

Tenés pantalones de jean. ¿Cuántos modelos y talles manejás?
¿Paulita tiene el Excel de stock y precios?
¿Cuándo fue la última vez que actualizaron los precios?
```

---

**Mario:**

```text
Tengo 4 modelos y 5 talles.
Paulita tiene un Excel pero no sé si está actualizado.
Los precios los actualicé hace como 6 meses.
```

---

**SmartPyme (Capa 1 — Admisión, continuación):**

```text
Bien. Entonces tenemos:

CERTEZA:
- Hay stock de pantalones (15.000–20.000 unidades aprox.)
- Hay 4 modelos y 5 talles
- Hay un Excel de Paulita
- Los precios tienen 6 meses sin actualizar

DUDA:
- Cantidad exacta por modelo/talle
- Precios actuales en el Excel
- Ventas del período

DESCONOCIMIENTO:
- Costo de reposición actual
- Margen real por producto

Primer paso: ¿podés pedirle a Paulita el Excel esta semana?
```

---

**Mario:**

```text
Sí, se lo pido hoy.
```

---

**SmartPyme (Capa 1.5 — Normalización, cuando llega el Excel):**

```text
Recibí el Excel de Paulita.

Detecté estas columnas:
- producto (modelo + talle)
- cantidad
- precio
- fecha (algunas filas sin año)
- prov. (¿es proveedor o vendedor?)

Necesito confirmar:
1. ¿"prov." es el proveedor del producto o el revendedor que lo compró?
2. Las fechas sin año, ¿son de 2026?
```

---

**Mario:**

```text
"prov." es el proveedor de donde compro.
Las fechas son de 2026, sí.
```

---

**SmartPyme (Capa 2 — Activación de conocimiento):**

```text
Bien. Con lo que tenemos, armé el mapa del problema.

NÚCLEO ENTRÓPICO PRINCIPAL:
El centro del desorden es stock + precio + revendedores sin control común.

Esto conecta con:
- inventario no confiable (no sabés cuánto tenés)
- precios desalineados (6 meses sin actualizar)
- margen invisible (no sabés si ganás por producto)
- política comercial informal (ventas por WhatsApp sin registro)
- capital inmovilizado (plata parada en stock sin rotar)
- flujo de caja debilitado (consecuencia de todo lo anterior)

CUADRO SINTOMÁTICO PRIORIZADO:
1. stock_desordenado → impacto sistémico 0.95 → atacar primero
2. precios_desactualizados → impacto 0.88 → atacar junto con stock
3. política_comercial_informal → impacto 0.75 → mes 2
4. flujo_caja_debilitado → impacto 0.70 → mes 2–3

UNIDAD CUÁNTICA DE RESOLUCIÓN (esta semana):
Contar el stock físico por modelo y talle, y actualizar el Excel con precios de reposición actuales.

ROADMAP PROPUESTO:
Mes 1: ordenar stock, precios y ventas
Mes 2: calcular margen real y flujo de caja
Mes 3: formalizar política comercial con revendedores

¿Arrancamos con el conteo de stock esta semana?
```

---

**Mario:**

```text
Sí. ¿Qué necesito hacer exactamente?
```

---

**SmartPyme:**

```text
Esta semana:
1. Contá el stock físico por modelo y talle.
2. Pedile a tu proveedor la lista de precios actualizada.
3. Mandame el Excel actualizado cuando esté listo.

Con eso puedo calcular:
- cuánto capital tenés inmovilizado en stock
- si los precios de venta cubren el costo de reposición
- cuánto margen real tenés por producto

¿Podés tener eso para el viernes?
```

---

### Qué muestra este ejemplo

1. La conversación no es un interrogatorio.
2. El sistema construye el caso por capas.
3. El Núcleo Entrópico Principal se presenta en lenguaje del dueño.
4. La Unidad Cuántica de Resolución es concreta y ejecutable.
5. El Roadmap es simple: tres fases, tres meses.
6. El dueño siempre sabe qué hacer esta semana.

---

## 28. Relación entre los nuevos conceptos y el grafo

```text
InvestigationGraph
  → contracción
  → PrincipalEntropicCore
      → identificación de Unidad Cuántica de Resolución
      → construcción de Cuadro Sintomático Priorizado
      → generación de InitialTransformationRoadmap
          → Fase 1 (Unidad Cuántica)
          → Fase 2
          → Fase 3
```

El grafo no desaparece.

El grafo es la base de análisis.

El Núcleo Entrópico es la contracción del grafo en algo atacable.

El Roadmap es la secuencia de ataque.

---

## 29. Reglas adicionales del Núcleo Entrópico

1. El Núcleo Entrópico Principal debe identificarse antes de presentar el plan al dueño.
2. El núcleo se identifica por centralidad, impacto y viabilidad, no solo por urgencia.
3. La Unidad Cuántica de Resolución debe ser ejecutable en días, no en semanas.
4. El Roadmap debe tener al menos tres fases temporales.
5. Cada fase debe tener criterio de éxito verificable.
6. El Cuadro Sintomático Priorizado ordena por impacto sistémico, no por dolor declarado.
7. El sistema no presenta el grafo completo al dueño: presenta el núcleo y el roadmap.
8. El grafo completo queda como evidencia interna para trazabilidad.
9. Si no se puede identificar un núcleo claro, el sistema declara `AMBIGUOUS_CORE` y pide más evidencia.
10. El núcleo puede cambiar cuando llega nueva evidencia.

---

## 30. Objetos conceptuales completos (v3)

```text
KnowledgeDomain
KnowledgeToolCandidate
FormulaCandidate
RequiredVariable
AvailableVariableMatch
EvidenceGap
InvestigationNode
InvestigationEdge
InvestigationGraph
InvestigationRoute
InvestigationPlan
OperationalCaseCandidate
PrincipalEntropicCore
QuantumResolutionUnit
PrioritizedSymptomTable
InitialTransformationRoadmap
HumanKnowledgeNode
ToolNode
WorkflowStepNode
WorkflowTrace
EpistemicPrintCycle
```

---

## 31. Próximos pasos

### Contratos ya implementados

```text
TS_020_001_CONTRATOS_ACTIVACION_INVESTIGATIVA
app/contracts/investigation_contract.py
```

### Próxima tarea sugerida

```text
TS_020_002_CONTRATOS_NUCLEO_ENTROPICO
```

Archivos sugeridos:

```text
app/contracts/entropic_core_contract.py
tests/contracts/test_entropic_core_contract.py
```

Contratos mínimos a implementar:

```python
class PrincipalEntropicCore(BaseModel): ...
class QuantumResolutionUnit(BaseModel): ...
class PrioritizedSymptomEntry(BaseModel): ...
class PrioritizedSymptomTable(BaseModel): ...
class TransformationPhase(BaseModel): ...
class InitialTransformationRoadmap(BaseModel): ...
```

---

## 32. Herramientas y flujos de trabajo como dimensión faltante

### El problema

El grafo investigativo de Capa 2 puede modelar síntomas, patologías, fórmulas y variables.

Pero hay una dimensión que falta en la mayoría de los análisis operativos de PyMEs:

> ¿Cómo fluye realmente la información en este negocio?

Sin ese mapa, el sistema puede identificar que falta una variable pero no puede explicar por qué falta ni dónde se pierde.

### La dimensión faltante

Las PyMEs no operan con sistemas integrados.

Operan con:

- personas que recuerdan cosas;
- WhatsApps que se pierden;
- Excels que no se actualizan;
- cuadernos que solo entiende una persona;
- contadores que ven solo la parte blanca;
- dueños que toman decisiones sin datos.

Cada uno de estos elementos es un nodo del grafo operativo real.

Y las relaciones entre ellos son los flujos de trabajo reales.

### Regla central

```text
No hay diagnóstico operativo sin mapa de herramientas y flujos.
```

Un sistema que no entiende cómo fluye la información en el negocio no puede:

- explicar por qué falta una variable;
- identificar dónde se pierde el dato;
- proponer una intervención que funcione en la práctica;
- entender por qué el dueño no tiene los números.

### Consecuencia para el grafo

El `InvestigationGraph` debe poder incluir:

- `HumanKnowledgeNode` para cada actor humano relevante;
- `ToolNode` para cada herramienta operativa;
- `WorkflowStepNode` para cada paso del flujo;
- relaciones `OPERATED_BY`, `FEEDS_INTO`, `HAS_FRICTION`, `HAS_LOSS`.

---

## 33. HumanKnowledgeNode — Actores humanos como nodos de conocimiento

### Principio

Cada persona en la PyME es un nodo de conocimiento parcial.

No es un obstáculo.

No es un recurso.

Es un testigo parcial de la realidad operativa del negocio.

Tiene información fragmentada, sesgada y temporalmente acotada.

### Por qué es un nodo del grafo

Porque la información no vive en sistemas.

Vive en personas.

Y para investigar correctamente, el sistema necesita saber:

- quién sabe qué;
- en qué formato lo tiene;
- de qué período tiene información;
- qué tan confiable es esa información;
- cómo se le puede pedir.

### Actores en Perales

```text
Mario (dueño):
  knowledge_domains: visión general, decisiones, caja negra, contexto informal
  tools_used: WhatsApp, memoria
  information_owned: ventas informales, decisiones de precio, relaciones con revendedores
  information_format: oral, WhatsApp
  reliability: alta en contexto, baja en números exactos
  temporal_scope: presente y reciente
  contact_channel: conversación directa

Paulita (administración):
  knowledge_domains: stock, precios, ventas operativas
  tools_used: Excel, WhatsApp
  information_owned: Excel de stock y precios, registro de ventas
  information_format: Excel (.xlsx)
  reliability: media-alta (depende de actualización)
  temporal_scope: últimos meses
  contact_channel: WhatsApp de Mario

Andrés (contador):
  knowledge_domains: gastos blancos, caja formal, declaraciones fiscales
  tools_used: sistema contable, PDF
  information_owned: gastos blancos del mes, declaraciones
  information_format: PDF, Excel
  reliability: alta en parte blanca, no ve parte negra
  temporal_scope: mes anterior
  contact_channel: email o reunión mensual

Ana (compras):
  knowledge_domains: proveedores, costos, condiciones comerciales
  tools_used: WhatsApp, cuaderno, facturas
  information_owned: precios de proveedor, condiciones de pago
  information_format: facturas físicas, cuaderno
  reliability: alta en costos actuales
  temporal_scope: presente
  contact_channel: WhatsApp o presencial
```

### Dimensión temporal de los actores

Cada actor tiene una ventana temporal de conocimiento:

```text
Mario:
  observed_at: continuo (presente)
  temporal_scope: últimas semanas

Paulita:
  observed_at: última actualización del Excel
  temporal_scope: últimos 3–6 meses

Andrés:
  observed_at: cierre del mes anterior
  temporal_scope: mes anterior

Ana:
  observed_at: última compra
  temporal_scope: últimas semanas
```

Sin esta dimensión temporal, el sistema puede pedir información que ya no existe o que está desactualizada.

---

## 34. ToolNode — Herramientas operativas como nodos del grafo

### Principio

Cada herramienta operativa es un nodo del grafo investigativo.

No es solo un canal de comunicación.

Es un repositorio de información con:

- formato propio;
- riesgo de pérdida;
- cobertura temporal;
- dificultad de acceso;
- confiabilidad variable.

### Herramientas en Perales

```text
WhatsApp (Mario → Paulita):
  tool_type: digital
  used_by: Mario, Paulita
  stores_information: órdenes de venta informales
  information_format: texto libre
  reliability: baja (no estructurado, se pierde)
  temporal_coverage: últimas semanas (historial limitado)
  access_difficulty: media (hay que buscar en el chat)
  loss_risk: alto (mensajes se borran, no hay backup)

Excel de Paulita:
  tool_type: digital
  used_by: Paulita
  stores_information: stock, precios, ventas
  information_format: xlsx
  reliability: media (depende de actualización manual)
  temporal_coverage: últimos meses
  access_difficulty: baja (archivo compartible)
  loss_risk: medio (puede estar desactualizado)

Sistema contable (Andrés):
  tool_type: digital
  used_by: Andrés
  stores_information: gastos blancos, declaraciones
  information_format: PDF, exportación
  reliability: alta en parte blanca
  temporal_coverage: mes anterior
  access_difficulty: alta (requiere pedido al contador)
  loss_risk: bajo

Banco:
  tool_type: digital
  used_by: Mario
  stores_information: movimientos bancarios
  information_format: extracto PDF o CSV
  reliability: alta
  temporal_coverage: últimos 3 meses online
  access_difficulty: baja (descargable)
  loss_risk: bajo

Cuaderno (Ana):
  tool_type: físico
  used_by: Ana
  stores_information: precios de proveedor, condiciones
  information_format: manuscrito
  reliability: alta en contexto, baja en exactitud
  temporal_coverage: presente
  access_difficulty: alta (requiere presencia física)
  loss_risk: muy alto (único ejemplar)

Memoria del dueño:
  tool_type: humano
  used_by: Mario
  stores_information: contexto, decisiones, relaciones
  information_format: oral
  reliability: alta en contexto, baja en números
  temporal_coverage: variable
  access_difficulty: baja (conversación)
  loss_risk: muy alto (no trazable)
```

---

## 35. WorkflowStepNode — Pasos operativos con dimensión temporal

### Principio

Cada paso del flujo operativo es un nodo del grafo investigativo.

Tiene un actor, una herramienta, una acción, una entrada, una salida y una dimensión temporal.

Los puntos de fricción y pérdida son los lugares donde el desorden se genera.

### Flujo de ventas en Perales

```text
Paso 1: Revendedor llega o llama
  actor: revendedor
  herramienta: presencial / teléfono
  acción: solicita productos
  entrada: necesidad de compra
  salida: pedido verbal
  siguiente_paso: Mario recibe pedido
  punto_de_fricción: no hay registro formal del pedido
  punto_de_pérdida: si Mario no está, la venta se pierde
  evidencia_generada: ninguna
  riesgo_operativo: venta no registrada
  duración_estimada: 5–15 minutos
  temporal_window:
    observed_at: momento de la visita

Paso 2: Mario recibe pedido y manda WhatsApp a Paulita
  actor: Mario
  herramienta: WhatsApp
  acción: comunica la venta a Paulita
  entrada: pedido verbal del revendedor
  salida: mensaje de WhatsApp
  siguiente_paso: Paulita anota en Excel
  punto_de_fricción: Mario puede olvidar mandar el mensaje
  punto_de_pérdida: si el mensaje no llega, la venta no se registra
  evidencia_generada: mensaje de WhatsApp (no estructurado)
  riesgo_operativo: venta no registrada, stock no actualizado
  duración_estimada: 1–5 minutos
  temporal_window:
    observed_at: momento del mensaje

Paso 3: Paulita anota en Excel
  actor: Paulita
  herramienta: Excel
  acción: registra la venta en el Excel de stock
  entrada: mensaje de WhatsApp de Mario
  salida: fila en Excel con producto, cantidad, precio
  siguiente_paso: stock actualizado
  punto_de_fricción: Paulita puede no estar disponible
  punto_de_pérdida: si Paulita no anota, el stock queda desactualizado
  evidencia_generada: fila en Excel (estructurada pero manual)
  riesgo_operativo: stock incorrecto, precio desactualizado
  duración_estimada: 2–10 minutos
  temporal_window:
    observed_at: momento de la anotación (puede ser horas después)

Paso 4: Cobro y caja
  actor: Mario
  herramienta: caja negra / efectivo
  acción: cobra al revendedor
  entrada: venta acordada
  salida: dinero en caja negra
  siguiente_paso: ninguno (no hay registro)
  punto_de_fricción: no hay comprobante
  punto_de_pérdida: el cobro no llega al contador ni al sistema
  evidencia_generada: ninguna trazable
  riesgo_operativo: resultado real no calculable
  duración_estimada: 1–5 minutos
  temporal_window:
    observed_at: momento del cobro
```

### Qué revela este flujo

```text
El flujo tiene 4 pasos.
Solo 1 genera evidencia estructurada (Excel de Paulita).
Los otros 3 generan evidencia no trazable o ninguna.
Hay 3 puntos de pérdida activos.
El contador no ve ninguno de estos pasos.
```

Esto explica por qué Mario no tiene los números.

No es un problema de voluntad.

Es un problema de diseño del flujo.

---

## 36. WorkflowTrace — Trazado del flujo completo

### Definición

El `WorkflowTrace` es la representación completa del flujo operativo de un proceso de negocio, incluyendo todos los pasos, actores, herramientas, puntos de fricción y pérdida.

### Estructura conceptual

```text
WorkflowTrace:
  trace_id
  cliente_id
  process_name              nombre del proceso: "venta a revendedor"
  steps                     lista de WorkflowStepNode en orden
  actors_involved           lista de HumanKnowledgeNode
  tools_involved            lista de ToolNode
  friction_points           lista de pasos con fricción
  loss_points               lista de pasos con pérdida
  evidence_generated        evidencia total generada por el flujo
  evidence_gaps             información que el flujo no captura
  temporal_coverage         período que cubre el flujo
  workflow_health           HEALTHY / FRAGILE / BROKEN
  notes
```

### Estados de salud del flujo

```text
HEALTHY → el flujo genera evidencia trazable en todos los pasos críticos.
FRAGILE → el flujo tiene puntos de fricción o pérdida pero sigue funcionando.
BROKEN  → el flujo tiene pérdidas críticas que impiden la investigación.
```

---

## 37. EpistemicPrintCycle — Ciclo de impresión epistémica

### Definición

La realidad operativa de la PyME no se captura de una vez.

Se imprime progresivamente por ciclos trazables de aportes humanos, evidencia cruda, curación, contraste y actualización del grafo.

Cada ciclo agrega una capa de conocimiento al caso.

### Principio rector

```text
La realidad operativa se imprime progresivamente.
Cada ciclo epistémico agrega una capa de conocimiento trazable.
El grafo se actualiza con cada ciclo.
```

### Por qué existe este concepto

El dueño no puede dar toda la información en una sola conversación.

La evidencia llega en partes.

Paulita manda el Excel esta semana.

El contador manda el reporte el mes que viene.

Ana trae las facturas cuando puede.

El sistema debe poder:

- registrar qué se sabe en cada ciclo;
- actualizar el grafo con cada nuevo aporte;
- detectar contradicciones entre ciclos;
- mantener trazabilidad de cuándo llegó cada dato;
- saber qué cambió entre ciclos.

### Estructura conceptual

```text
EpistemicPrintCycle:
  cycle_id
  cliente_id
  case_id
  cycle_number              número de ciclo (1, 2, 3...)
  cycle_date                fecha del ciclo
  contributions:
    - contributor_person_id
      contribution_type     EVIDENCE / CLARIFICATION / CORRECTION / VALIDATION
      evidence_items        lista de evidencias aportadas
      new_variables         variables nuevas detectadas
      resolved_gaps         brechas resueltas en este ciclo
      new_gaps              brechas nuevas detectadas
      contradictions        contradicciones con ciclos anteriores
  graph_updates             cambios al InvestigationGraph en este ciclo
  epistemic_state_before    estado del conocimiento antes del ciclo
  epistemic_state_after     estado del conocimiento después del ciclo
  next_cycle_tasks          tareas para el próximo ciclo
```

### Ejemplo: Perales — ciclos epistémicos

```text
Ciclo 1 (semana 1):
  contributor: Mario
  contribution_type: EVIDENCE
  new_variables: stock_aproximado, precio_desactualizado
  resolved_gaps: ninguno
  new_gaps: stock_exacto, costo_reposicion, ventas_periodo
  epistemic_state_after: CERTEZA parcial, muchas DUDAS

Ciclo 2 (semana 2):
  contributor: Paulita
  contribution_type: EVIDENCE
  evidence_items: Excel de stock y precios
  new_variables: stock_por_modelo_talle, precio_lista
  resolved_gaps: stock_aproximado → stock_por_modelo_talle
  new_gaps: costo_reposicion (no está en el Excel)
  contradictions: precio en Excel difiere del precio que Mario recordaba

Ciclo 3 (semana 3):
  contributor: Andrés (contador)
  contribution_type: EVIDENCE
  evidence_items: reporte de gastos blancos
  new_variables: gastos_blancos_mes
  resolved_gaps: gastos_blancos
  new_gaps: gastos_informales (el contador no los ve)
  contradictions: ninguna

Ciclo 4 (semana 4):
  contributor: Mario
  contribution_type: CLARIFICATION
  clarification: confirma que los gastos informales son ~30% del total
  new_variables: gastos_informales_estimados
  resolved_gaps: gastos_informales (estimado)
  contradictions: ninguna
```

---

## 38. Tiempo en flujos, actores y herramientas

### Principio

Toda entidad, objeto, herramienta, flujo y paso debe tener dimensión temporal.

No alcanza con saber qué existe.

Hay que saber cuándo existe, cuándo fue actualizado y de qué período tiene información.

### Dimensiones temporales por tipo de objeto

```text
HumanKnowledgeNode:
  observed_at: cuándo se habló con esta persona
  temporal_scope: de qué período tiene información
  last_updated: cuándo fue la última vez que actualizó su información

ToolNode:
  observed_at: cuándo se accedió a la herramienta
  temporal_coverage: de qué período tiene datos
  last_updated: cuándo fue la última actualización

WorkflowStepNode:
  observed_at: cuándo ocurrió este paso
  duration: cuánto tardó
  period_start / period_end: si el paso cubre un período

WorkflowTrace:
  period_start: inicio del período que cubre el flujo
  period_end: fin del período que cubre el flujo

EpistemicPrintCycle:
  cycle_date: fecha del ciclo
  valid_from: desde cuándo es válido el conocimiento de este ciclo
  valid_to: hasta cuándo es válido (puede ser null si sigue vigente)
```

### Regla

```text
Sin dimensión temporal, un actor, herramienta o flujo no puede usarse en investigación.
```

Un Excel de Paulita sin fecha de última actualización no es evidencia confiable.

Un reporte del contador sin período de cobertura no es evidencia usable.

Un WhatsApp sin timestamp no es evidencia trazable.

---

## 39. Investigación forense-operativa

### Analogía

La investigación operativa de una PyME es análoga a una investigación forense.

```text
Cada dato es una huella.
Cada humano es un testigo parcial.
Cada documento es una escena.
Cada contradicción es una pista.
```

### Por qué esta analogía es útil

Un investigador forense no acepta el primer relato como verdad.

Busca huellas.

Contrasta testimonios.

Detecta contradicciones.

Reconstruye la secuencia de eventos.

SmartPyme hace lo mismo con la operación de la PyME:

- no acepta el relato del dueño como verdad completa;
- busca evidencia documental;
- contrasta fuentes;
- detecta contradicciones entre lo que el dueño dice y lo que los documentos muestran;
- reconstruye el flujo operativo real.

### Aplicación en Perales

```text
Huella 1: Excel de Paulita muestra precio de $5.500 para PJ-AZ-42.
Huella 2: Mario dice que el precio es $6.000.
Contradicción: ¿cuál es el precio real?
Pista: el Excel no fue actualizado en 6 meses.
Conclusión provisional: el precio real puede ser $6.000 pero el Excel está desactualizado.
Tarea: confirmar precio actual con Mario y actualizar Excel.
```

```text
Huella 1: Excel muestra 120 unidades de PJ-AZ-42.
Huella 2: Mario dice que tiene "entre 15.000 y 20.000 pantalones en total".
Contradicción: ¿el Excel tiene todo el stock o solo parte?
Pista: el Excel tiene 87 filas pero Mario habla de 4 modelos × 5 talles = 20 combinaciones.
Conclusión provisional: el Excel puede estar incompleto.
Tarea: verificar si el Excel tiene todas las combinaciones de modelo/talle.
```

### Regla forense-operativa

```text
Toda contradicción entre fuentes es una pista, no un error.
Toda brecha de evidencia es una escena sin investigar.
Todo actor humano es un testigo parcial con su propia versión.
```

---

## 40. Relación entre workflow roto y Núcleo Entrópico Principal

### Principio

El Núcleo Entrópico Principal suele estar en la unión entre herramienta, persona y flujo.

No es solo una patología operativa.

Es el punto donde el flujo de información se rompe, se pierde o se distorsiona.

### Regla

```text
El núcleo entrópico suele estar en la unión entre herramienta, persona y flujo.
```

### Ejemplo: Perales

El Núcleo Entrópico Principal de Perales no es solo `inventario_no_confiable`.

Es la unión de:

```text
Mario (dueño) + WhatsApp + Paulita + Excel
```

Porque:

- Mario no registra directamente;
- usa WhatsApp como canal informal;
- Paulita es el único punto de registro;
- el Excel es la única fuente de verdad;
- si Paulita no está o no actualiza, todo el sistema falla.

Esta unión es el núcleo porque:

- concentra el mayor riesgo operativo;
- es el punto de mayor pérdida de información;
- su resolución (formalizar el registro) desbloquea todas las demás patologías;
- el costo de intervención es bajo (cambiar el proceso de registro).

### Cómo se detecta

```text
1. Identificar el WorkflowStep con más puntos de pérdida.
2. Identificar el HumanKnowledgeNode con más dependencias.
3. Identificar el ToolNode con mayor riesgo de pérdida.
4. Cruzar los tres: el nodo que aparece en los tres es el núcleo.
```

### Implicancia para el Roadmap

Si el núcleo está en el workflow, la Fase 1 del Roadmap debe atacar el workflow, no solo la patología.

Ejemplo:

```text
Fase 1 — Mes 1: Formalizar el registro de ventas
  objetivo: reemplazar WhatsApp → Paulita → Excel por registro directo
  acción: Mario registra la venta en el momento, no después
  herramienta: formulario simple o app de registro
  resultado esperado: stock actualizado en tiempo real
```

Esto es más efectivo que simplemente "ordenar el Excel".

---

## 41. Ejemplo Perales — Flujo completo con tiempo

### Flujo de venta a revendedor (WorkflowTrace)

```text
WorkflowTrace:
  process_name: "venta a revendedor"
  workflow_health: BROKEN

  Paso 1: Revendedor llega
    actor: revendedor
    herramienta: presencial
    temporal_window: observed_at = momento de visita
    evidencia_generada: ninguna
    pérdida: si Mario no está, venta perdida

  Paso 2: Mario manda WhatsApp a Paulita
    actor: Mario
    herramienta: WhatsApp
    temporal_window: observed_at = momento del mensaje
    evidencia_generada: mensaje no estructurado
    pérdida: si Paulita no lee, venta no registrada

  Paso 3: Paulita anota en Excel
    actor: Paulita
    herramienta: Excel
    temporal_window: observed_at = momento de anotación (puede ser horas después)
    evidencia_generada: fila en Excel
    pérdida: si Paulita no está, stock desactualizado

  Paso 4: Mario cobra en efectivo
    actor: Mario
    herramienta: caja negra
    temporal_window: observed_at = momento del cobro
    evidencia_generada: ninguna trazable
    pérdida: cobro no llega al contador

  friction_points: Paso 2 (Mario puede olvidar), Paso 3 (Paulita puede no estar)
  loss_points: Paso 1 (venta perdida), Paso 4 (cobro no trazable)
  evidence_generated: solo Paso 3 (Excel)
  evidence_gaps: ventas no registradas, cobros no trazables
```

### Ciclo epistémico 1 (semana 1)

```text
EpistemicPrintCycle:
  cycle_number: 1
  cycle_date: 2026-05-03
  contributor: Mario
  new_variables:
    - stock_aproximado (CERTEZA baja, observed_at: 2026-05-03)
    - precio_desactualizado (CERTEZA, valid_from: 2025-11-01, valid_to: null)
  resolved_gaps: ninguno
  new_gaps:
    - stock_exacto (DUDA, responsable: Paulita)
    - costo_reposicion (DESCONOCIMIENTO)
    - ventas_periodo (DUDA, responsable: Paulita)
  epistemic_state_after: CERTEZA parcial, muchas DUDAS
  next_cycle_tasks:
    - pedir Excel a Paulita
    - pedir lista de costos al proveedor
```

### Ciclo epistémico 2 (semana 2)

```text
EpistemicPrintCycle:
  cycle_number: 2
  cycle_date: 2026-05-10
  contributor: Paulita
  evidence_items: Excel stock_mayo_paulita.xlsx
  new_variables:
    - stock_por_modelo_talle (CERTEZA media, observed_at: 2026-05-10)
    - precio_lista (CERTEZA media, valid_from: 2025-11-01)
  resolved_gaps:
    - stock_aproximado → stock_por_modelo_talle
  new_gaps:
    - costo_reposicion (no está en el Excel)
  contradictions:
    - precio en Excel ($5.500) difiere del precio que Mario recordaba ($6.000)
  epistemic_state_after: stock conocido, precio contradictorio, costo desconocido
  next_cycle_tasks:
    - confirmar precio real con Mario
    - pedir lista de costos al proveedor
```

---

## 42. Objetos conceptuales completos (v3 — final)

```text
KnowledgeDomain
KnowledgeToolCandidate
FormulaCandidate
RequiredVariable
AvailableVariableMatch
EvidenceGap
InvestigationNode
InvestigationEdge
InvestigationGraph
InvestigationRoute
InvestigationPlan
OperationalCaseCandidate
PrincipalEntropicCore
QuantumResolutionUnit
PrioritizedSymptomTable
InitialTransformationRoadmap
HumanKnowledgeNode
ToolNode
WorkflowStepNode
WorkflowTrace
EpistemicPrintCycle
```

---

## 43. Próximos pasos (v3)

### Contratos ya implementados

```text
TS_020_001_CONTRATOS_ACTIVACION_INVESTIGATIVA
app/contracts/investigation_contract.py
```

### Próximas tareas sugeridas

```text
TS_020_002_CONTRATOS_NUCLEO_ENTROPICO
  app/contracts/entropic_core_contract.py
  → PrincipalEntropicCore, QuantumResolutionUnit,
    PrioritizedSymptomTable, InitialTransformationRoadmap

TS_020_003_CONTRATOS_WORKFLOW
  app/contracts/workflow_contract.py
  → HumanKnowledgeNode, ToolNode, WorkflowStepNode,
    WorkflowTrace, EpistemicPrintCycle
```
