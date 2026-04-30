# SmartPyme Baseline Report — TS_010 Pathology Catalog

## Veredicto

**TS_010_PATHOLOGY_BASELINE_READY**

La rama `factory/ts-006-jobs-sovereign-persistence` consolida la primera versión operativa del Catálogo de Patologías de SmartPyme.

La Fase C convierte resultados calculados en diagnósticos determinísticos, auditables y soberanos por `cliente_id`.

---

## Estado validado

### TS_010A — Pathology Contract

Estado: **CERRADO**

Componentes:

- `PathologyDefinition`
- `PathologyEvaluationInput`
- `PathologyFinding`
- `PathologyStatus`
- `PathologySeverity`

Primera patología soportada:

- `margen_bruto_negativo`

Regla determinística:

```text
formula_id = margen_bruto
value < 0
```

Garantías:

- no usa IA
- no usa `eval`
- preserva `cliente_id`
- preserva `source_refs`
- fórmula bloqueada genera `PENDING_DATA`
- fórmula incorrecta genera `PENDING_DATA`

---

### TS_010B — Pathology Engine Service

Estado: **CERRADO**

Componente:

- `PathologyEngineService`

Garantías:

- separa evaluación del contrato
- mantiene wrapper de compatibilidad `evaluate_pathology`
- detecta `ACTIVE` si margen bruto es negativo
- devuelve `NOT_DETECTED` si margen bruto es saludable
- devuelve `PENDING_DATA` si la patología es desconocida o no evaluable

---

### TS_010C — Pathology Repository

Estado: **CERRADO**

Componente:

- `PathologyRepository`

Tabla:

- `pathology_findings`

Clave soberana:

```text
PRIMARY KEY (cliente_id, pathology_finding_id)
```

Garantías:

- guarda diagnósticos
- recupera por `pathology_finding_id`
- lista por `pathology_id` y `status`
- bloquea mismatch de `cliente_id`
- lectura cruzada devuelve `None`
- preserva `source_refs`

---

### TS_010D — Pathology Auditor Agent

Estado: **CERRADO**

Componente:

- `PathologyAuditorAgent`

Flujo:

1. recibe `cliente_id`
2. carga `FormulaResult` por `formula_result_id`
3. evalúa patología con `PathologyEngineService`
4. persiste `PathologyFinding` con `PathologyRepository`

Garantías:

- no evalúa datos de otros clientes
- missing formula result devuelve `None`
- persiste `ACTIVE`
- persiste `NOT_DETECTED`

---

### TS_010E — Pathology API

Estado: **CERRADO**

Endpoints:

- `POST /pathologies/audit`
- `GET /pathologies/findings`
- `GET /pathologies/findings/{pathology_finding_id}`

Garantías:

- requiere `X-Client-ID`
- detecta y persiste `margen_bruto_negativo`
- fórmula inexistente devuelve `404`
- lectura cruzada devuelve `404`

---

### TS_010F — Hermes Pathology Tool

Estado: **CERRADO**

Componentes:

- `pathology_explanation_tool.py`
- `owner_status_tool.py` extendido

Garantías:

- Hermes lee patologías persistidas
- explica `ACTIVE` como alerta de negocio
- explica `NOT_DETECTED` como control saludable
- explica `PENDING_DATA` como diagnóstico pendiente
- oculta patologías entre clientes
- integra patologías en `get_owner_status(cliente_id)`

`owner_status` ahora consolida:

- jobs
- findings
- formula_results
- pathology_findings
- mensajes humanos consolidados

---

## Smoke validado

Comando ejecutado:

```bash
PYTHONPATH=. pytest \
  tests/test_pathology_contract_ts_010a.py \
  tests/test_pathology_engine_service_ts_010b.py \
  tests/test_pathology_repository_ts_010c.py \
  tests/test_pathology_auditor_agent_ts_010d.py \
  tests/test_pathology_api_ts_010e.py \
  tests/test_hermes_pathology_ts_010f.py
```

Resultado:

```text
24 passed
```

---

## Reglas arquitectónicas preservadas

- `cliente_id` siempre obligatorio
- no usar `tenant_id`
- no contexto global para identidad
- PK compuesta en tabla multi-tenant nueva
- lectura cruzada no revela existencia de recursos
- diagnóstico determinístico
- resultados con trazabilidad de fuentes
- Hermes no diagnostica usando datos de otro cliente

---

## Próxima fase recomendada

### TS_011 — Catálogo industrial ampliado de patologías

Objetivo:

Mover el catálogo ampliado de patologías a capa `catalog`, sin contaminar contratos.

Archivo sugerido:

```text
app/catalog/pathologies.py
```

Primeras candidatas:

- `margen_unitario_ilusorio`
- `venta_bajo_costo`
- `acos_destructivo`
- `falla_precision_int64`
- `limbo_liquidaciones_ml`
- `clasificacion_iva_lesiva`

Criterio de cierre:

Cada patología nueva debe tener:

1. definición de catálogo
2. fórmula o condición determinística
3. test de detección
4. test de no detección
5. test de `PENDING_DATA`
6. preservación de `source_refs`
7. aislamiento por `cliente_id`
