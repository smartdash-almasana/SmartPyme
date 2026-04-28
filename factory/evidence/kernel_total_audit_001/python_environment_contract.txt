# Python Environment Contract

Estado: CANONICO v1

Este contrato declara el entorno minimo para validar SmartPyme Factory.

## Comando Python

El comando canonico para automatizacion es:

```bash
python
```

El entorno debe garantizar que `python` existe y apunta a Python 3.11 o superior.
Si el sistema solo provee `python3`, se debe activar un entorno virtual del repo o
crear un alias/symlink operativo antes de ejecutar validaciones canonicas.

## Dependencias minimas

Las dependencias versionadas son:

- `polars>=1.0`
- `pytest>=8.0`
- `ruff>=0.8`

Fuente de verdad:

- `pyproject.toml`
- `requirements-dev.txt`

## Instalacion canonica

```bash
scripts/install_python_environment.sh
```

El script crea o reutiliza `.venv`, instala `requirements-dev.txt` y verifica que
`.venv/bin/python` existe como comando `python` dentro del entorno activado.

Para operar manualmente:

```bash
source .venv/bin/activate
```

## Verificacion canonica

```bash
scripts/check_python_environment.sh
python --version
python3 --version
python -m pytest --version
python -m ruff --version
python -c "import polars; print(polars.__version__)"
python -m pytest tests/factory/test_build_audit_context.py -q
python -m py_compile scripts/build_audit_context.py
python scripts/build_audit_context.py --output /tmp/smartpyme_audit_context_env_test.txt
```

## Politica fail-closed

Si `python`, `pytest`, `ruff` o `polars` no estan disponibles, el ciclo debe cerrar
como `BLOCKED_ENVIRONMENT_CONTRACT` o `BLOCKED_ENVIRONMENT_INSTALL`, incluyendo el
comando fallido y la causa exacta observada.
