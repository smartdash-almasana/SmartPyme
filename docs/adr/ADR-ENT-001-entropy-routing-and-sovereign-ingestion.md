# ADR-ENT-001: Entropy Routing and Sovereign Ingestion

**Status:** Accepted

## Contexto

SmartPyme necesita procesar evidencia documental proveniente de múltiples fuentes empresariales:

- PDFs
- imágenes
- lotes masivos de facturas
- Excel
- reportes de Mercado Libre
- extractos bancarios
- remitos
- liquidaciones

Estos documentos poseen distintos niveles de:

- entropía documental
- variabilidad estructural
- complejidad OCR
- costo de extracción
- sensibilidad soberana

Procesar todo internamente produce saturación operacional.

Delegar todo externamente destruye soberanía, aumenta costos y fuga inteligencia operacional.

Se requiere una arquitectura híbrida y adaptativa.

---

# Decisión

Se establece el patrón:

```text
Entropy Routing
```

como mecanismo oficial de decisión para el pipeline documental.

El runtime debe decidir dinámicamente:

- qué procesar localmente
- qué delegar a BEM
- qué costo aceptar
- qué riesgo soberano asumir
- qué workflow activar

---

# Axioma Arquitectónico

```text
BEM reduce entropía documental.
SmartPyme construye verdad operacional.
```

---

# Separación de Dominios

## Dominio BEM

Responsable de:

- Route
- Split
- OCR complejo
- clasificación documental
- separación de lotes
- reducción de caos documental

BEM opera como:

```text
coprocesador documental funcional
```

No participa en:

- Operational Truth
- patologías
- decisiones operacionales
- memoria soberana
- cálculo de negocio
- políticas del dueño

---

# Dominio SmartPyme

Responsable de:

- Transform soberano
- joins internos
- cálculo matemático
- catálogo de fórmulas
- señales
- patologías
- clarification gate
- memoria operacional
- graph epistemológico
- capabilities
- decisiones humanas

SmartPyme es:

```text
runtime epistemológico-operacional soberano
```

---

# Entropy Router

Se define el componente:

```text
document_entropy_router
```

como capability interna responsable de decidir el flujo de procesamiento documental.

---

# Responsabilidades del Router

## 1. Medición de Entropía

Evaluar:

- OCR complexity
- structure confidence
- supplier variability
- table consistency
- format predictability
- language noise
- document fragmentation

---

## 2. Evaluación de Riesgo

Evaluar:

- sensibilidad del tenant
- riesgo fiscal
- exposición de datos
- criticidad operacional
- necesidad de soberanía estricta

---

## 3. Evaluación de Costos

Evaluar:

- costo esperado de BEM
- costo local
- costo de procesamiento masivo
- costo de retries
- ROI esperado

---

## 4. Decisión de Routing

El router decide:

```text
- procesamiento local
- procesamiento híbrido
- delegación a BEM
- bloqueo
- clarification request
```

---

# Estrategia Inicial de Delegación

## Delegación Externa (BEM)

Funciones autorizadas inicialmente:

```text
- Route
- Split
```

Casos típicos:

- PDFs masivos
- OCR difícil
- lotes mezclados
- formatos desconocidos
- documentos altamente variables

---

# Procesamiento Soberano Interno

Procesamiento obligatorio interno:

```text
- formulas
- patologías
- joins soberanos
- Operational Truth
- tenant memory
- catalog matching
- financial diagnosis
- capability execution
```

Casos típicos:

- Excel estándar
- Mercado Libre exports
- extractos conocidos
- datasets tabulares
- facts estructurados

---

# Pipeline Híbrido

Flujo esperado:

```text
Documento
→ Entropy Router
→ BEM Route/Split (si aplica)
→ evidence_items
→ Transform soberano
→ Facts
→ Fórmulas
→ Signals
→ SmartGraph
→ Hermes orchestration
→ Capability execution
```

---

# Relación con Hermes

Hermes no procesa documentos.

Hermes:

- decide workflows
- coordina capabilities
- administra ambigüedad
- consulta soberanía
- dispara clarification gates
- integra resultados
- produce reportes epistemológicos

---

# Clarification Gate

Si:

- confidence score bajo
- conflicto documental
- extracción ambigua
- falta evidencia
- mismatch semántico

entonces:

```text
workflow_state = BLOCKED_BY_AMBIGUITY
```

Hermes debe solicitar resolución humana.

---

# Zero Retention Requirement

Toda integración externa debe intentar operar bajo:

```text
Zero Retention Mode
```

para minimizar persistencia externa de información empresarial sensible.

## Nota

La disponibilidad real y garantías efectivas de este modo deben verificarse contractualmente y técnicamente antes de considerarse una garantía operativa.

---

# Consecuencias

## Positivas

- reducción de complejidad interna
- menor costo operacional
- mejor escalabilidad
- aislamiento soberano
- runtime adaptativo
- reducción de saturación del kernel
- menor dependencia de parsers internos

## Riesgos

- dependencia parcial de proveedor externo
- cambios de pricing
- degradación API externa
- fuga epistemológica si se delega demasiado
- routing incorrecto
- sobreuso de BEM

---

# Principio Estratégico

```text
SmartPyme no monetiza OCR.
SmartPyme monetiza inteligencia operacional.
```

---

# No Decisiones

Este ADR no define todavía:

- scoring exacto del router
- thresholds finales
- retry policies
- scheduler distribuido
- cache documental
- strategy de batching
- policy de fallback offline
- multi-provider routing
- observabilidad financiera del routing

Estas decisiones deberán resolverse en contratos técnicos posteriores.
