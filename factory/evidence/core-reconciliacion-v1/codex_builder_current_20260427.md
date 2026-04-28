# core-reconciliacion-v1 - Codex Builder

PLAN
- objetivo: verificar unidad pequena para reconciliar dos CSV y emitir diferencias por entidad como hallazgos.
- archivos permitidos: app/core/reconciliation/*, tests/core/test_reconciliation_csv.py, factory/evidence/core-reconciliacion-v1/*.
- archivos prohibidos: integraciones externas, reporting, systemd, refactor global.
- criterio de cierre: diferencia numerica detectada, salida estructurada tipo Hallazgo, test focal validado.
- tests esperados: pytest focal, tests relacionados de reconciliacion/hallazgos, py_compile, Ruff si esta disponible.

WRITE
- No se agrego refactor global.
- El core existente expone reconcile_csv_sources en app/core/reconciliation/service.py.
- El test focal existe en tests/core/test_reconciliation_csv.py.
- app/core/reconciliation/models.py evita dependencia runtime no declarada en pydantic para ReconciliationRow.
- No se uso polars porque no esta instalado ni declarado en pyproject.toml.

VERIFY
- pwd_current.txt
- git_status_current.txt
- ls_files_current.txt
- inspect_models_current.txt
- inspect_reconcile_csv_sources_current.txt
- inspect_test_current.txt
- grep_symbols_current.txt
- dependencies_current.txt

RUN
- tests_current.txt: .venv/bin/python -m pytest tests/core/test_reconciliation_csv.py -q
- tests_related_current.txt: .venv/bin/python -m pytest tests/core/test_reconciliation.py tests/core/test_reconciliation_service.py tests/core/test_hallazgos_service.py tests/core/test_reconciliation_csv.py -q
- py_compile_current.txt: .venv/bin/python -m py_compile app/core/reconciliation/models.py app/core/reconciliation/service.py tests/core/test_reconciliation_csv.py
- manual_reconciliation_current.txt: smoke deterministico con dos CSV temporales.
- ruff_current.txt: .venv/bin/python -m ruff check app/core/reconciliation/models.py app/core/reconciliation/service.py tests/core/test_reconciliation_csv.py

RESULTADO
- pytest focal: pasa.
- pytest relacionado: pasa.
- py_compile: pasa.
- smoke manual: emite 1 Hallazgo mismatch_valor para entidad o-1 con delta 25.5.
- Ruff: bloqueado porque el modulo ruff no esta instalado en .venv.

DECISION
BLOCKED

BLOQUEO
BLOCKED_ENVIRONMENT_CONTRACT_MISSING: Ruff canonico esta configurado en pyproject.toml pero no esta disponible en el entorno ejecutable.
