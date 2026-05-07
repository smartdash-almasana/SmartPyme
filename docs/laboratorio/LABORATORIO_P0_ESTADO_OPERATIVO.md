# Laboratorio P0 — Estado Operativo

**Fecha:** 2026-05-07
**Rama:** `product/laboratorio-mvp-vendible`
**Proyecto Supabase DEV:** `msfcjyssiaqegxbpkdai`

---

## Estado actual

El flujo P0 del Laboratorio de Análisis PyME está operativo en DEV.
El backend escribe en Supabase usando `service_role`. RLS Phase 1 está activa (fail-closed).
No hay autenticación JWT ni policies de acceso por cliente todavía.

---

## Commits recientes relevantes

```
5419c01  feat(db): add laboratorio p0 rls phase1 migration   ← HEAD
fdfd359  feat(api): add fastapi app entrypoint
5d7b10f  feat(laboratorio): expose p0 flow via api endpoint
87a411a  feat(laboratorio): add p0 cli entrypoint
b8eae57  build: add supabase python dependency
66b58e2  test(laboratorio): add supabase dev smoke script
```

---

## Endpoints disponibles

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET`  | `/health` | Health check — devuelve `{"status": "ok"}` |
| `POST` | `/api/v1/laboratorio/p0/casos` | Crea caso P0 completo (job + case + report) |

### Payload POST /api/v1/laboratorio/p0/casos

```json
{
  "cliente_id": "string (requerido)",
  "dueno_nombre": "string (requerido)",
  "laboratorio": "string (requerido)",
  "hallazgo": "string (requerido)"
}
```

### Respuesta exitosa

```json
{
  "cliente_id": "...",
  "case_id": "...",
  "job_id": "...",
  "report_id": "...",
  "status": "closed"
}
```

---

## Comandos de smoke

### CLI real (contra Supabase DEV)

```bash
python -m scripts.laboratorio_p0_cli \
  --cliente-id cliente_demo_rls_cli \
  --dueno-nombre "Dueño Demo RLS CLI" \
  --laboratorio diagnostico_operativo \
  --hallazgo "Smoke RLS phase1 desde CLI"
```

Resultado esperado: `{"status": "closed", ...}`

### API real (requiere servidor local)

```bash
# Iniciar servidor
uvicorn app.main:app --port 8000

# Smoke
curl -X POST http://localhost:8000/api/v1/laboratorio/p0/casos \
  -H "Content-Type: application/json" \
  -d '{
    "cliente_id": "cliente_demo_rls_api",
    "dueno_nombre": "Demo",
    "laboratorio": "diagnostico_operativo",
    "hallazgo": "Smoke RLS API"
  }'
```

### Tests unitarios

```bash
pytest tests/laboratorio_pyme -q
pytest tests/test_api_laboratorio_p0.py -q
```

---

## Estado Supabase DEV

| tabla | RLS enabled | RLS forced | Policies |
|-------|-------------|------------|----------|
| `clientes` | ✅ ON | ❌ OFF | ninguna |
| `jobs` | ✅ ON | ❌ OFF | ninguna |
| `operational_cases` | ✅ ON | ❌ OFF | ninguna |
| `reports` | ✅ ON | ❌ OFF | ninguna |
| `decisions` | ✅ ON | ❌ OFF | ninguna |
| `evidence_candidates` | ✅ ON | ❌ OFF | ninguna |

**Migración aplicada:** `supabase/migrations/20260507_p0_laboratorio_rls_phase1_fail_closed.sql`

---

## Estado RLS Phase 1

- `ENABLE ROW LEVEL SECURITY` activo en las 6 tablas P0.
- Sin `FORCE ROW LEVEL SECURITY`.
- Sin `CREATE POLICY`.
- `service_role` bypasea RLS por diseño — backend operativo sin cambios.
- `anon` / `authenticated` bloqueados por defecto (fail-closed).
- Clave soberana de aislamiento: `cliente_id` (TEXT). No se usa `tenant_id` ni `owner_id`.

---

## Qué NO está hecho todavía

- ❌ Autenticación JWT — no hay login, no hay tokens de cliente.
- ❌ RLS Phase 2 — no hay `CREATE POLICY` con claim `cliente_id`.
- ❌ Aislamiento soberano por cliente desde el frontend — anon/authenticated siguen bloqueados.
- ❌ Laboratorios adicionales (stock, financiero, compras, automatización) — solo `diagnostico_operativo`.
- ❌ Informe PDF/Markdown exportable.
- ❌ Landing comercial.

---

## Próximo paso recomendado

**RLS Phase 2 — Policies por cliente_id**

1. Definir cómo el backend inyecta `cliente_id` en el JWT (claim custom o `sub`).
2. Crear migración `20260507_p0_laboratorio_rls_phase2_policies.sql` con:
   ```sql
   CREATE POLICY "cliente_aislado" ON public.jobs
     USING (cliente_id = auth.jwt() ->> 'cliente_id');
   -- (repetir para las 6 tablas)
   ```
3. Smoke test con token JWT de cliente real para validar aislamiento soberano.
4. Solo después: implementar auth de cliente (login, JWT, claim).
## Próximo paso recomendado

No avanzar todavía a RLS Phase 2.

Prioridad inmediata:
1. Crear una interfaz mínima usable: formulario web o bot que llame a `POST /api/v1/laboratorio/p0/casos`.
2. Mantener acceso a Supabase solo server-side con `service_role`.
3. Definir RLS Phase 2 recién cuando exista contrato JWT estable con claim `cliente_id`.