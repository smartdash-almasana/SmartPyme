# Laboratorio P0 — Estado operativo

Fecha: 2026-05-07  
Rama: `product/laboratorio-mvp-vendible`

## Estado actual

Laboratorio P0 está operativo en DEV con persistencia Supabase.

Estado validado:

- CLI real contra Supabase DEV: `PASS`
- API real contra Supabase DEV: `PASS`
- FastAPI entrypoint: `PASS`
- `GET /health`: `PASS`
- `POST /api/v1/laboratorio/p0/casos`: `PASS`
- RLS Phase 1 fail-closed en DEV: `PASS`
- Backend con `service_role`: operativo después de RLS

## Commits recientes relevantes

- `5419c01 feat(db): add laboratorio p0 rls phase1 migration`
- `fdfd359 feat(api): add fastapi app entrypoint`
- `5d7b10f feat(laboratorio): expose p0 flow via api endpoint`
- `87a411a feat(laboratorio): add p0 cli entrypoint`
- `b8eae57 build: add supabase python dependency`

## Supabase DEV

Proyecto DEV:

- `project_ref`: `msfcjyssiaqegxbpkdai`
- host conocido: `db.msfcjyssiaqegxbpkdai.supabase.co`

Tablas P0:

- `clientes`
- `jobs`
- `operational_cases`
- `reports`
- `decisions`
- `evidence_candidates`

## RLS Phase 1

Estado:

- RLS habilitado en las 6 tablas P0.
- Sin `CREATE POLICY` todavía.
- Sin `FORCE ROW LEVEL SECURITY`.
- `anon` / `authenticated` quedan bloqueados por defecto.
- Backend server-side con `service_role` sigue operativo.

Migración:

```text
supabase/migrations/20260507_p0_laboratorio_rls_phase1_fail_closed.sql
```

No avanzar a RLS Phase 2 hasta definir contrato JWT estable con claim `cliente_id`.

## API

Entrypoint local:

```powershell
uvicorn app.main:app --reload
```

Health:

```powershell
Invoke-RestMethod -Method Get -Uri http://127.0.0.1:8000/health
```

Endpoint Laboratorio P0:

```text
POST /api/v1/laboratorio/p0/casos
```

Payload esperado:

```json
{
  "cliente_id": "cliente_demo_api",
  "dueno_nombre": "Dueño Demo API",
  "laboratorio": "diagnostico_operativo",
  "hallazgo": "Primer hallazgo demo desde API P0"
}
```

Respuesta esperada:

```json
{
  "cliente_id": "cliente_demo_api",
  "case_id": "...",
  "job_id": "...",
  "report_id": "...",
  "status": "closed"
}
```

Smoke PowerShell:

```powershell
$body = @{
  cliente_id = "cliente_demo_api"
  dueno_nombre = "Dueño Demo API"
  laboratorio = "diagnostico_operativo"
  hallazgo = "Primer hallazgo demo desde API P0"
} | ConvertTo-Json

Invoke-RestMethod `
  -Method Post `
  -Uri http://127.0.0.1:8000/api/v1/laboratorio/p0/casos `
  -ContentType "application/json" `
  -Body $body
```

## CLI

Uso:

```powershell
python -m scripts.laboratorio_p0_cli `
  --cliente-id cliente_demo_cli `
  --dueno-nombre "Dueño Demo CLI" `
  --laboratorio diagnostico_operativo `
  --hallazgo "Primer hallazgo demo desde CLI P0"
```

Respuesta esperada:

```json
{
  "cliente_id": "cliente_demo_cli",
  "case_id": "...",
  "job_id": "...",
  "report_id": "...",
  "status": "closed"
}
```

## Qué no está hecho todavía

- No hay auth/JWT.
- No hay RLS Phase 2 por `cliente_id` claim.
- No hay frontend/formulario de captura.
- No hay limpieza de datos smoke en DEV.
- No hay endpoint de consulta de reportes/casos.
- No hay integración con bot.

## Próximo paso recomendado

Prioridad inmediata:

1. Exponer un flujo usable mínimo: formulario web o bot simple que llame al endpoint P0.
2. Mantener backend server-side con `service_role`.
3. Postergar RLS Phase 2 hasta definir claim JWT `cliente_id` y modelo de usuario.

No tocar producción sin autorización explícita.
