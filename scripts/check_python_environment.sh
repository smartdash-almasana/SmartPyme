#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

python --version
python3 --version
python -m pytest --version
python -m ruff --version
python -c "import polars; print(polars.__version__)"
python -m pytest tests/factory/test_build_audit_context.py -q
python -m py_compile scripts/build_audit_context.py
python scripts/build_audit_context.py --output /tmp/smartpyme_audit_context_env_test.txt
