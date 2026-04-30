# SmartPyme Baseline Report — TS_006 a TS_009

## Veredicto

**TS_006_009_BASELINE_READY**

La rama `factory/ts-006-jobs-sovereign-persistence` consolida el primer baseline funcional del SME OS:

- Jobs soberanos
- Herramientas Hermes de lectura e interpretación
- Loop multiagente mínimo
- Catálogo de fórmulas determinístico
- Resultados calculados persistidos y auditables

---

## Estado validado

### TS_006 — Jobs soberanos

Estado: **CERRADO**

Componentes:

- `JobRepository`
- `POST /jobs`
- `GET /jobs`
- `GET /jobs/{job_id}`
- `JobWorker`

Garantías:

- `cliente_id` obligatorio
- aislamiento por cliente
- lectura cruzada devuelve `404` o `None`
- lifecycle `PENDING -> RUNNING -> SUCCESS/FAILED`

---

### TS_007 — Hermes read-only + interpretación

Estado: **CERRADO**

Componentes:

- `app/mcp/tools/jobs_read_tool.py`
- `app/mcp/tools/hermes_interpreter.py`
- `app/mcp/tools/owner_status_tool.py`

Garantías:

- Hermes lee jobs y findings por `cliente_id`
- no escribe datos
- interpreta hallazgos sin exponer JSON técnico crudo
- salida consolidada para owner

---

### TS_008 — Loop multiagente mínimo

Estado: **CERRADO**

Componentes:

- `MultiagentTask`
- `run_multiagent_task_cycle`
- persistencia JSON
- queue runner
- CLI enqueue
- CLI run once
- smoke end-to-end

Garantías:

- tarea `pending -> in_progress -> done`
- bloqueo si la tarea no parte desde `pending`
- evidencia escrita
- cola procesable desde terminal o cron

---

### TS_009 — Catálogo de fórmulas base

Estado: **CERRADO**

Componentes:

- `FormulaInput`
- `FormulaDefinition`
- `FormulaResult`
- `FormulaEngineService`
- `FormulaResultRepository`
- `FormulaCalculationAgent`
- `POST /formulas/calculate`
- `GET /formulas/results`
- `GET /formulas/results/{result_id}`
- Hermes formula tool
- owner status extendido

Fórmulas soportadas:

- `ganancia_bruta = ventas - costos`
- `margen_bruto = (ventas - costos) / ventas`

Garantías:

- sin IA
- sin `eval`
- división por cero devuelve `BLOCKED`
- resultados con `source_refs`
- persistencia soberana por `cliente_id`
- lectura cruzada devuelve `404` o `None`

---

## Smoke validado

Comando ejecutado:

```bash
PYTHONPATH=. pytest \
  tests/test_formula_contract_ts_009a.py \
  tests/test_formula_engine_service_ts_009b.py \
  tests/test_formula_result_repository_ts_009c.py \
  tests/test_formula_calculation_agent_ts_009d.py \
  tests/test_formula_api_ts_009e.py \
  tests/test_formula_results_api_ts_009f.py \
  tests/test_formula_results_tool_ts_009g.py \
  tests/test_owner_status_extended_ts_009h.py
```

Resultado:

```text
28 passed, 1 warning
```

Warning externo:

- `PendingDeprecationWarning` en `starlette/formparsers.py` por `python_multipart`.
- No bloquea baseline.

---

## Reglas arquitectónicas preservadas

- `cliente_id` siempre obligatorio
- no usar `tenant_id`
- no contexto global para identidad
- PK compuesta en tablas multi-tenant nuevas
- lectura cruzada no revela existencia de recursos
- operaciones de cálculo determinísticas
- resultados con trazabilidad de fuentes

---

## Próxima fase recomendada

### TS_010 — Conexión de fórmulas con facts reales

Objetivo:

Tomar facts/canonical rows existentes y convertirlos en `FormulaInput` sin carga manual.

Alcance sugerido:

1. extractor determinístico `facts -> FormulaInput`
2. mapeo de nombres de facts a inputs (`ventas`, `costos`)
3. cálculo automático por `FormulaCalculationAgent`
4. persistencia de resultados con `source_refs`
5. exposición en `owner_status`

Criterio de cierre:

Hermes debe poder responder al dueño con un número calculado desde evidencia real, no desde inputs manuales.
