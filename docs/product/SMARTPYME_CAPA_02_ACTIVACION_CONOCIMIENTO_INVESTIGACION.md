# SmartPyme — Capa 02: Activación de Conocimiento e Investigación

## Estado

PROPUESTA CANONICA PENDIENTE DE VALIDACION

Este documento define la Capa 2 de SmartPyme: la capa que transforma una admisión validada y evidencia normalizada en un grafo investigativo.

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
- prioriza rutas por ROI, riesgo, evidencia disponible y costo;
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
```

---

## 22. Próximo paso

Convertir este documento rector en contratos Pydantic:

```text
TS_020_001_CONTRATOS_ACTIVACION_INVESTIGATIVA
```

Archivos sugeridos:

```text
app/contracts/investigation_contract.py
tests/contracts/test_investigation_contract.py
```
