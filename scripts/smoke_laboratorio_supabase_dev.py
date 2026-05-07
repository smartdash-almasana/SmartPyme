"""Smoke test real end-to-end del Laboratorio MVP contra Supabase DEV.

Carga .env.local, construye el contexto de persistencia real con provider=supabase,
ejecuta crear_caso_persistente + cerrar_caso_persistente y valida filas creadas.

NO imprime secretos. NO limpia datos. NO usa drop/truncate/delete.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# 1. Cargar .env.local
# ---------------------------------------------------------------------------
env_path = Path(__file__).parent.parent / ".env.local"
if not env_path.exists():
    print("BLOCKED: .env.local no encontrado")
    sys.exit(1)

with open(env_path) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, val = line.partition("=")
            os.environ.setdefault(key.strip(), val.strip())

# ---------------------------------------------------------------------------
# 2. Verificar provider
# ---------------------------------------------------------------------------
from app.repositories.persistence_provider import get_provider, PersistenceProvider

provider = get_provider()
print(f"PROVIDER: {provider.value}")
if provider != PersistenceProvider.SUPABASE:
    print("BLOCKED: SMARTPYME_PERSISTENCE_PROVIDER no es supabase")
    sys.exit(1)

# ---------------------------------------------------------------------------
# 3. Verificar env Supabase (sin imprimir valores)
# ---------------------------------------------------------------------------
url_present = bool(os.environ.get("SMARTPYME_SUPABASE_URL", "").strip())
key_present = bool(os.environ.get("SMARTPYME_SUPABASE_KEY", "").strip())
print(f"SMARTPYME_SUPABASE_URL: {'PRESENT' if url_present else 'MISSING'}")
print(f"SMARTPYME_SUPABASE_KEY: {'PRESENT' if key_present else 'MISSING'}")
if not url_present or not key_present:
    print("BLOCKED: faltan variables de entorno Supabase")
    sys.exit(1)

# ---------------------------------------------------------------------------
# 4. Construir cliente Supabase real
# ---------------------------------------------------------------------------
try:
    from supabase import create_client
    supabase_url = os.environ["SMARTPYME_SUPABASE_URL"]
    supabase_key = os.environ["SMARTPYME_SUPABASE_KEY"]
    real_client = create_client(supabase_url, supabase_key)
    print("SUPABASE_CLIENT: OK")
except ImportError:
    print("BLOCKED: librería supabase no instalada. pip install supabase")
    sys.exit(1)
except Exception as e:
    print(f"BLOCKED: error al construir cliente Supabase: {e}")
    sys.exit(1)

# ---------------------------------------------------------------------------
# 5. Datos de prueba
# ---------------------------------------------------------------------------
CLIENTE_ID = "cliente_smoke_laboratorio_dev"
NOMBRE = "Cliente Smoke Laboratorio DEV"
DUENO_NOMBRE = "Dueño Smoke"

from app.laboratorio_pyme.tipos import TipoLaboratorio
LABORATORIOS = [TipoLaboratorio.analisis_comercial]

from app.laboratorio_pyme.contracts import DiagnosticFinding
HALLAZGOS = [
    DiagnosticFinding(
        cliente_id=CLIENTE_ID,
        finding_id="finding-smoke-001",
        case_id="PLACEHOLDER",  # se reemplaza después de crear el caso
        laboratorio=TipoLaboratorio.analisis_comercial,
        hallazgo="Smoke test: caso persistente creado y cerrado correctamente",
        prioridad="alta",
        impacto_estimado="valida flujo P0 Supabase",
    )
]

# ---------------------------------------------------------------------------
# 6. Insertar cliente test si no existe
# ---------------------------------------------------------------------------
existing = real_client.table("clientes").select("cliente_id").eq("cliente_id", CLIENTE_ID).execute()
if existing.data:
    print(f"CLIENTE_ROW: ya existe ({CLIENTE_ID})")
else:
    real_client.table("clientes").insert({
        "cliente_id": CLIENTE_ID,
        "nombre": NOMBRE,
        "status": "active",
        "metadata": {"smoke": True},
    }).execute()
    print(f"CLIENTE_ROW: insertado ({CLIENTE_ID})")

# ---------------------------------------------------------------------------
# 7. Construir LaboratorioPersistenceContext con cliente real
# ---------------------------------------------------------------------------
from app.laboratorio_pyme.persistence import LaboratorioPersistenceContext
ctx = LaboratorioPersistenceContext.from_repository_factory(
    cliente_id=CLIENTE_ID,
    provider="supabase",
    supabase_client=real_client,
)
print("PERSISTENCE_CONTEXT: OK")

# ---------------------------------------------------------------------------
# 8. Construir LaboratorioService y LaboratorioApplicationService
# ---------------------------------------------------------------------------
from app.laboratorio_pyme.service import LaboratorioService
from app.laboratorio_pyme.application_service import LaboratorioApplicationService

svc = LaboratorioService()
app_svc = LaboratorioApplicationService(
    laboratorio_service=svc,
    persistence_context=ctx,
)
print("APPLICATION_SERVICE: OK")

# ---------------------------------------------------------------------------
# 9. crear_caso_persistente
# ---------------------------------------------------------------------------
try:
    creado = app_svc.crear_caso_persistente(
        cliente_id=CLIENTE_ID,
        dueno_nombre=DUENO_NOMBRE,
        laboratorios=LABORATORIOS,
    )
    print(f"CREAR_CASO_RESULT: OK — case_id={creado.case_id} job_id={creado.job_id}")
except Exception as e:
    print(f"CREAR_CASO_RESULT: ERROR — {e}")
    sys.exit(1)

# ---------------------------------------------------------------------------
# 10. cerrar_caso_persistente
# ---------------------------------------------------------------------------
# Actualizar case_id en hallazgos
from dataclasses import replace
hallazgos_con_case = [
    DiagnosticFinding(
        cliente_id=CLIENTE_ID,
        finding_id="finding-smoke-001",
        case_id=creado.case_id,
        laboratorio=TipoLaboratorio.analisis_comercial,
        hallazgo="Smoke test: caso persistente creado y cerrado correctamente",
        prioridad="alta",
        impacto_estimado="valida flujo P0 Supabase",
    )
]

try:
    cerrado = app_svc.cerrar_caso_persistente(
        cliente_id=CLIENTE_ID,
        case_id=creado.case_id,
        job_id=creado.job_id,
        hallazgos=hallazgos_con_case,
        hypothesis=f"Investigar si {DUENO_NOMBRE} presenta síntomas detectables en analisis_comercial?",
        reasoning_summary="Smoke test P0 Supabase DEV — flujo completo validado.",
    )
    print(f"CERRAR_CASO_RESULT: OK — report_id={cerrado.report_id}")
except Exception as e:
    print(f"CERRAR_CASO_RESULT: ERROR — {e}")
    sys.exit(1)

# ---------------------------------------------------------------------------
# 11. Validar filas creadas en Supabase
# ---------------------------------------------------------------------------
print("\n--- ROWS_CREATED ---")

job_rows = real_client.table("jobs").select("job_id,cliente_id,job_type,status").eq("cliente_id", CLIENTE_ID).eq("job_id", creado.job_id).execute()
print(f"jobs: {len(job_rows.data)} fila(s) — job_id={creado.job_id}")

case_rows = real_client.table("operational_cases").select("case_id,cliente_id,status").eq("cliente_id", CLIENTE_ID).eq("case_id", creado.case_id).execute()
print(f"operational_cases: {len(case_rows.data)} fila(s) — case_id={creado.case_id}")

report_rows = real_client.table("reports").select("report_id,cliente_id,status").eq("cliente_id", CLIENTE_ID).eq("report_id", cerrado.report_id).execute()
print(f"reports: {len(report_rows.data)} fila(s) — report_id={cerrado.report_id}")

# ---------------------------------------------------------------------------
# 12. Verificar aislamiento: no hay filas de otro cliente_id
# ---------------------------------------------------------------------------
print("\n--- CLIENTE_ID_CHECK ---")
OTHER_ID = "otro_cliente_no_debe_aparecer"
other_jobs = real_client.table("jobs").select("job_id").eq("cliente_id", OTHER_ID).execute()
other_cases = real_client.table("operational_cases").select("case_id").eq("cliente_id", OTHER_ID).execute()
other_reports = real_client.table("reports").select("report_id").eq("cliente_id", OTHER_ID).execute()
print(f"jobs de otro cliente: {len(other_jobs.data)} (esperado: 0)")
print(f"operational_cases de otro cliente: {len(other_cases.data)} (esperado: 0)")
print(f"reports de otro cliente: {len(other_reports.data)} (esperado: 0)")

# ---------------------------------------------------------------------------
# 13. Resultado final
# ---------------------------------------------------------------------------
jobs_ok = len(job_rows.data) == 1
cases_ok = len(case_rows.data) == 1
reports_ok = len(report_rows.data) == 1
isolation_ok = len(other_jobs.data) == 0 and len(other_cases.data) == 0 and len(other_reports.data) == 0

print("\n--- VEREDICTO FINAL ---")
if jobs_ok and cases_ok and reports_ok and isolation_ok:
    print("VEREDICTO: PASS — flujo P0 Supabase DEV validado end-to-end")
else:
    print("VEREDICTO: PARTIAL")
    if not jobs_ok: print("  FAIL: jobs no encontrado")
    if not cases_ok: print("  FAIL: operational_cases no encontrado")
    if not reports_ok: print("  FAIL: reports no encontrado")
    if not isolation_ok: print("  FAIL: aislamiento multi-cliente comprometido")
