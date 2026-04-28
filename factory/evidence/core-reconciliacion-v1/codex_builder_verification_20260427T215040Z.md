# core-reconciliacion-v1 - Codex Builder verification

## Scope
- Objective: validate the first deterministic CSV reconciliation engine.
- Inputs: two CSV files.
- Output: structured hallazgos by entity with quantified numeric difference.
- Productive files inspected: `app/core/reconciliation/service.py`, `app/core/reconciliation/models.py`.
- Test inspected: `tests/core/test_reconciliation_csv.py`.

## Commands
```bash
pwd
git status --short
sed -n '1,220p' CODEX.md
sed -n '1,220p' factory/control/NEXT_CYCLE.md
sed -n '1,220p' pyproject.toml
find app/core/reconciliation -maxdepth 3 -type f -print | sort
sed -n '1,360p' app/core/reconciliation/service.py
sed -n '360,760p' app/core/reconciliation/service.py
sed -n '1,260p' tests/core/test_reconciliation_csv.py
test -f app/core/reconciliation/service.py && ls -la app/core/reconciliation/service.py
test -f app/core/reconciliation/models.py && ls -la app/core/reconciliation/models.py
test -f tests/core/test_reconciliation_csv.py && ls -la tests/core/test_reconciliation_csv.py
python3 -m compileall app/core/reconciliation tests/core/test_reconciliation_csv.py
.venv/bin/pytest tests/core/test_reconciliation_csv.py -q
if [ -x .venv/bin/ruff ]; then .venv/bin/ruff check app/core/reconciliation/service.py app/core/reconciliation/models.py tests/core/test_reconciliation_csv.py; else echo 'RUFF_NOT_AVAILABLE'; fi
```

## Key outputs
```text
pwd:
/opt/smartpyme-factory/repos/SmartPyme

physical verification:
-rw-r--r-- 1 neoalmasana neoalmasana 60132 Apr 27 19:47 app/core/reconciliation/service.py
-rw-r--r-- 1 neoalmasana neoalmasana 8478 Apr 27 19:56 app/core/reconciliation/models.py
-rw-r--r-- 1 neoalmasana neoalmasana 1150 Apr 27 19:21 tests/core/test_reconciliation_csv.py

compileall:
Listing 'app/core/reconciliation'...

pytest:
.                                                                        [100%]

ruff:
RUFF_NOT_AVAILABLE
```

## Manual CSV smoke
```text
Input A:
order_id,amount,status
o-1,100.00,paid
o-2,50.00,paid

Input B:
order_id,amount,status
o-1,125.50,paid
o-2,50.00,paid

Output:
1
Hallazgo(... tipo='mismatch_valor', entidad_id='o-1', entidad_tipo='order',
  diferencia_cuantificada=25.5,
  evidencia={'field': 'amount', 'value_a': 100, 'value_b': 125.5, 'delta': 25.5},
  status='pending')
```

## Decision
INCOMPLETO

Reason: the deterministic CSV reconciliation unit is present and the specific pytest passes,
but Ruff is not installed in `.venv`, so lint validation cannot be completed.
