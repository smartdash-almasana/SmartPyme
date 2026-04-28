# Codex validation core-reconciliacion-v1 20260427T212729Z

## PLAN
- objetivo: validar una unidad pequena del motor de reconciliacion entre dos CSV con salida tipo hallazgo.
- archivos permitidos: app/core/reconciliation/models.py, app/core/reconciliation/service.py, tests/core/test_reconciliation_csv.py, factory/evidence/core-reconciliacion-v1/.
- archivos prohibidos: cambios de arquitectura, controles factory no relacionados, refactor global.
- criterio de cierre: detectar diferencia numerica y devolver Hallazgo estructurado con entidad y delta cuantificado.
- tests esperados: tests/core/test_reconciliation_csv.py y tests relacionados de reconciliation.

## VERIFY
```text
$ pwd
/opt/smartpyme-factory/repos/SmartPyme

$ test -f app/core/reconciliation/models.py && ls -la app/core/reconciliation/models.py
-rw-r--r-- 1 neoalmasana neoalmasana 8478 Apr 27 19:56 app/core/reconciliation/models.py

$ test -f app/core/reconciliation/service.py && ls -la app/core/reconciliation/service.py
-rw-r--r-- 1 neoalmasana neoalmasana 60132 Apr 27 19:47 app/core/reconciliation/service.py

$ test -f tests/core/test_reconciliation_csv.py && ls -la tests/core/test_reconciliation_csv.py
-rw-r--r-- 1 neoalmasana neoalmasana 1150 Apr 27 19:21 tests/core/test_reconciliation_csv.py
```

## INSPECT
```text
$ grep -R "def reconcile_csv_sources\|def reconcile_records\|class ReconciliationRow\|class SimpleReconciliation" -n app/core/reconciliation tests/core/test_reconciliation_csv.py
app/core/reconciliation/models.py:65:class ReconciliationRow:
app/core/reconciliation/models.py:285:class SimpleReconciliationFinding:
app/core/reconciliation/models.py:292:class SimpleReconciliationResult:
app/core/reconciliation/service.py:388:def reconcile_records(
app/core/reconciliation/service.py:524:def reconcile_csv_sources(
```

## RUN
```text
$ python3 - <<'PY'
try:
 import polars
 print('polars_available', polars.__version__)
except Exception as exc:
 print('polars_unavailable', type(exc).__name__, str(exc))
PY
polars_unavailable ModuleNotFoundError No module named 'polars'

$ .venv/bin/pytest tests/core/test_reconciliation_csv.py tests/core/test_reconciliation.py tests/core/test_reconciliation_service.py -q
........................................................................ [ 90%]
........                                                                 [100%]

$ .venv/bin/python -m compileall app/core/reconciliation tests/core/test_reconciliation_csv.py -q
<sin salida; exit code 0>

$ ruff check app/core/reconciliation/models.py app/core/reconciliation/service.py tests/core/test_reconciliation_csv.py
/bin/bash: line 1: ruff: command not found

$ test -x .venv/bin/ruff; echo ruff_exit=$?
ruff_exit=1
```

## MANUAL RECONCILIATION CHECK
```text
$ .venv/bin/python - <<'PY'
from pathlib import Path
from app.core.reconciliation.service import reconcile_csv_sources
from tempfile import TemporaryDirectory

with TemporaryDirectory() as tmpdir:
    a = Path(tmpdir) / 'a.csv'
    b = Path(tmpdir) / 'b.csv'
    a.write_text('order_id,amount,status\no-1,100.00,paid\no-2,50.00,paid\n', encoding='utf-8')
    b.write_text('order_id,amount,status\no-1,125.50,paid\no-2,50.00,paid\n', encoding='utf-8')
    hallazgos = reconcile_csv_sources(a, b, key_field='order_id', entity_type='order')
    for hallazgo in hallazgos:
        print(hallazgo)
PY
Hallazgo(id='cc06007061f00b4196053c6e1b515f497f329331ffae175eececb0d5d932aaa4', tipo='mismatch_valor', severidad='warning', entidad_id='o-1', entidad_tipo='order', diferencia_cuantificada=25.5, evidencia={'field': 'amount', 'value_a': 100, 'value_b': 125.5, 'delta': 25.5}, dedupe_key='mismatch:o-1:amount', status='pending')
```

## DECISION
INCOMPLETO: pytest y verificacion manual pasan, pero Ruff queda bloqueado porque no esta instalado en PATH ni en .venv.
