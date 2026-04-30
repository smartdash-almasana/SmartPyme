# FM_024A — Legacy Factory Inventory

## Veredicto

SmartPyme contiene dos generaciones de factoría dentro del mismo repositorio. No deben mezclarse en auditorías, runners ni comandos Telegram.

- **LEGACY factory**: infraestructura histórica basada en hallazgos, runners previos y governance antigua.
- **FM factory nueva**: factoría multiagéntica desacoplada, controlada por `TaskSpec`, `TaskSpecStore`, `TaskSpecRunner` y `TelegramSuperownerAdapter`.

La fuente de verdad activa para el plano superowner es **FM factory nueva**.

---

## 1. FM factory nueva — ACTIVA

Rutas activas:

```text
factory/core/task_spec.py
factory/core/task_spec_store.py
factory/core/task_spec_runner.py
factory/core/run_report.py
factory/core/task_spec_templates.py
factory/adapters/telegram_superowner_adapter.py
factory/tools/factory_control.py
tests/factory/test_factory_decoupling_fm_011.py
tests/factory/test_factory_boundary_no_app_imports_fm_012.py
tests/factory/test_task_spec_contract_fm_013.py
tests/factory/test_task_spec_store_fm_014.py
tests/factory/test_task_spec_runner_fm_015.py
tests/factory/test_telegram_superowner_taskspec_fm_016.py
tests/factory/test_telegram_superowner_inspection_fm_017.py
tests/factory/test_retry_blocked_fm_018.py
tests/factory/test_run_batch_fm_019.py
tests/factory/test_factory_run_report_fm_020.py
tests/factory/test_report_retrieval_fm_021.py
tests/factory/test_task_spec_templates_fm_022.py
tests/factory/test_enqueue_template_fm_023.py
```

Responsabilidades:

- Definir tareas de desarrollo con `TaskSpec`.
- Persistir cola soberana por estados: `pending`, `in_progress`, `done`, `blocked`.
- Ejecutar validaciones determinísticas.
- Generar evidencia por tarea y reportes consolidados JSON/Markdown.
- Operar por Telegram para el superowner.
- Mantener frontera estricta: `factory/*` no importa `app/*`.

Comandos superowner activos:

```text
/status_factory
/tasks_pending
/task <task_id>
/blocked
/retry_blocked <task_id>
/evidence <task_id>
/run_one
/run_batch <n>
/last_report
/report <report_id>
/templates
/enqueue_template <template> <objetivo>
/enqueue_dev <objetivo>
```

Templates activos:

```text
code_change
docs_change
test_fix
refactor
audit_only
```

---

## 2. LEGACY factory — DEPRECATED PARA EL PLANO SUPEROWNER

Rutas históricas detectadas:

```text
factory/run_factory.py
factory/continuous_factory.py
factory/run_codex_worker.py
factory/multiagent_runner.py
factory/orchestrator/hermes_loop.py
factory/hallazgos/
factory/tasks/template_codex_task.yaml
factory/ai_governance/taskspec.schema.json
factory/ai_governance/
```

Estado:

- Mantener por compatibilidad histórica hasta migración explícita.
- No usar como fuente de verdad para nuevos ciclos FM.
- No usar para comandos Telegram superowner.
- No usar para medir el avance de FM_011+.

Motivo:

La legacy factory trabaja con convenciones anteriores: hallazgos, runners históricos, YAML/JSON schema previos y scripts de ejecución no alineados con el contrato `TaskSpec` nuevo.

---

## 3. Reglas de no mezcla

1. `factory/core/*` no debe importar desde `app/*`.
2. `factory/adapters/telegram_superowner_adapter.py` no debe depender de módulos legacy ni de `app/*`.
3. Los nuevos comandos Telegram superowner deben operar sobre `TaskSpecStore` y `TaskSpecRunner`.
4. Los nuevos tests FM deben vivir en `tests/factory/test_*_fm_*.py`.
5. Los reportes nuevos deben escribirse bajo `factory/evidence/taskspecs/run_reports/`.
6. La legacy factory no se elimina sin ciclo de migración dedicado.
7. Cualquier auditoría debe declarar explícitamente si audita:
   - `LEGACY factory`
   - `FM factory nueva`
   - ambas

---

## 4. Criterio de auditoría correcto

Una auditoría de la factoría nueva debe comprobar como mínimo:

```bash
PYTHONPATH=. pytest \
  tests/factory/test_factory_boundary_no_app_imports_fm_012.py \
  tests/factory/test_task_spec_contract_fm_013.py \
  tests/factory/test_task_spec_store_fm_014.py \
  tests/factory/test_task_spec_runner_fm_015.py \
  tests/factory/test_telegram_superowner_taskspec_fm_016.py \
  tests/factory/test_telegram_superowner_inspection_fm_017.py \
  tests/factory/test_retry_blocked_fm_018.py \
  tests/factory/test_run_batch_fm_019.py \
  tests/factory/test_factory_run_report_fm_020.py \
  tests/factory/test_report_retrieval_fm_021.py \
  tests/factory/test_task_spec_templates_fm_022.py \
  tests/factory/test_enqueue_template_fm_023.py
```

---

## 5. Estado al cierre FM_024A

```text
FM factory nueva: ACTIVA
Legacy factory: DEPRECATED PARA SUPEROWNER
Repo: SmartPyme
Branch activa: factory/ts-006-jobs-sovereign-persistence
Frontera crítica: factory/* no debe importar app/*
```
