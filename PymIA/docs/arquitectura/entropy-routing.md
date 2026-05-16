# ADR-ENT-001: Entropy Routing and Sovereign Ingestion

**Status:** Accepted

---

## Axioma Arquitectónico

```text
BEM reduce entropía documental.
SmartPyme construye verdad operacional.
```

---

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

Estos documentos poseen distintos niveles de entropía documental, variabilidad estructural, complejidad OCR, costo de extracción y sensibilidad soberana.

Procesar todo internamente produce saturación operacional.
Delegar todo externamente destruye soberanía, aumenta costos y fuga inteligencia operacional.

Se requiere una arquitectura híbrida y adaptativa.

---

## Decisión

Se establece el patrón **Entropy Routing** como mecanismo oficial de decisión para el pipeline documental.

El runtime debe decidir dinámicamente:

- qué procesar localmente
- qué delegar a BEM
- qué costo aceptar
- qué riesgo soberano asumir
- qué workflow activar

---

## Separación de Dominios

### Dominio BEM

Responsable de:

- Route
- Split
- OCR complejo
- clasificación documental
- separación de lotes
- reducción de caos documental

BEM opera como coprocesador documental funcional.

No participa en Operational Truth, patologías, decisiones operacionales, memoria soberana, cálculo de negocio ni políticas del dueño.

### Dominio SmartPyme

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

SmartPyme es el runtime epistemológico-operacional soberano.

---

## Entropy Router

Se define el componente `document_entropy_router` como capability interna responsable de decidir el flujo de procesamiento documental.

### Responsabilidades

1. **Medición de Entropía:** OCR complexity, structure confidence, supplier variability, table consistency, format predictability.
2. **Evaluación de Riesgo:** sensibilidad del tenant, riesgo fiscal, exposición de datos, criticidad operacional.
3. **Evaluación de Costos:** costo esperado de BEM, costo local, ROI esperado.
4. **Decisión de Routing:** procesamiento local / procesamiento híbrido / delegación a BEM / bloqueo / clarification request.

---

## Pipeline Híbrido

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

## Clarification Gate

Si confidence score bajo, conflicto documental, extracción ambigua, falta evidencia o mismatch semántico:

```text
workflow_state = BLOCKED_BY_AMBIGUITY
```

Hermes debe solicitar resolución humana.

---

## Principio Estratégico

```text
SmartPyme no monetiza OCR.
SmartPyme monetiza inteligencia operacional.
```
