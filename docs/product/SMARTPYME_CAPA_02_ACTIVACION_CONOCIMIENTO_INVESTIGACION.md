# SmartPyme — Capa 02: Activación de Conocimiento e Investigación

## Estado

DOCUMENTO RECTOR — ACTUALIZADO

**Versión:** 2.0  
**Fecha:** Mayo 2026  
**Cambios v2:** Incorporación del Núcleo Entrópico Principal, Unidad Cuántica de Resolución, Cuadro Sintomático Priorizado, Roadmap de Transformación Inicial y ejemplo conversacional Mario/Perales.

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
- arma un grafo de investigación;
- **contrae el grafo en un Núcleo Entrópico Principal**;
- **identifica la Unidad Cuántica de Resolución**;
- **produce un Cuadro Sintomático Priorizado**;
- prioriza rutas por ROI, riesgo, evidencia disponible y costo;
- **genera un Roadmap de Transformación Inicial**;
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

## 30. Objetos conceptuales completos (v2)

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
