# FREEZE — Telegram Factory Control Layer

Estado: `FROZEN_FOR_MERGE`
Rama: `factory/ts-006-jobs-sovereign-persistence`
Alcance cerrado: `FM_024` a `FM_031`

## Decisión

La capa de control Telegram de SmartPyme Factory queda congelada funcionalmente.

No se agregan nuevos comandos, rutas de control ni variantes de flujo antes del merge controlado. Solo se aceptan bugfixes, correcciones de compatibilidad o ajustes mínimos necesarios para que el smoke integral siga pasando.

## Capacidades cerradas

- `FM_024` — detección real de `changed_paths` vía git diff.
- `FM_025` — `RunReport` incluye `changed_paths` reales.
- `FM_026` — Telegram `/diff <task_id>`.
- `FM_027` — Telegram `/run_report_summary`.
- `FM_028` — Telegram `/failed_paths`.
- `FM_029` — Telegram `/factory_health`.
- `FM_030` — Telegram `/factory_help`.
- `FM_031` — smoke integral de comandos Telegram Factory.

## Comandos soportados

```text
/factory_help
/factory_health
/status_factory
/tasks_pending
/blocked
/retry_blocked <task_id>
/task <task_id>
/evidence <task_id>
/diff <task_id>
/templates
/enqueue_template <template> <objetivo>
/enqueue_dev <objetivo>
/run_one
/run_batch <n>
/last_report
/run_report_summary
/failed_paths
/report <report_id>
```

## Contrato de freeze

1. La capa Telegram es plano de control de la factoría, no runtime de producto.
2. No importa `app/*` desde `factory/*`.
3. Todo comando debe respetar autorización por `superowner_telegram_user_id`.
4. Toda ejecución debe dejar evidencia reproducible.
5. Los reportes deben mantener trazabilidad por `task_id`, `changed_paths`, `path_errors` y `evidence_paths`.
6. El smoke integral `FM_031` es el gate mínimo para aceptar merge.

## Validación mínima obligatoria

```bash
PYTHONPATH=. pytest \
  tests/factory/test_telegram_factory_commands_smoke_fm_031.py \
  tests/factory/test_factory_help_fm_030.py \
  tests/factory/test_factory_health_fm_029.py \
  tests/factory/test_failed_paths_fm_028.py \
  tests/factory/test_run_report_summary_fm_027.py \
  tests/factory/test_telegram_diff_fm_026.py \
  tests/factory/test_run_report_changed_paths_fm_025.py \
  tests/factory/test_git_diff_detector_fm_024.py \
  -q
```

## Próximo frente permitido

Después del freeze, el siguiente frente recomendado es producto/core, no más comandos Telegram:

```text
TS_007 — Kernel identity gap: cliente_id en HallazgoOperativo
```

## Resultado

`TELEGRAM_FACTORY_CONTROL_LAYER_FROZEN`
