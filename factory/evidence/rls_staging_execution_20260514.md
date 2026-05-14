# RLS Staging Execution Report - 2026-05-14

## Project Information

- **Project Ref:** `msfcjyssiaqegxbpkdai`
- **Project Name:** PymIA
- **Environment:** staging/dev

## Migration Applied

- **File:** `supabase/migrations/20260514_lockdown_rls_tenant_aware.sql`
- **SHA256:** `B344D9D100AA2ABA1BB0906F0276CA26D83346E12C8B057EA4EE49ADC5A3E204`
- **Execution Method:** `psql`
- **Exit Code:** `APPLY_EXIT=0`

## Structural Checks

- **Overall Check:** `CHECK_EXIT=0`
- **`request_tenant_key` function:** Exists
- **RLS Enabled:** 7 tables
- **FORCE RLS:** 7 tables
- **Policies:**
  - `clientes`: 1 policy
  - Rest of tables: 4 policies each
- **`anon_dml` role:** `false` on 7 tables
- **Authenticated Role (`clientes`):** `SELECT` only
- **Authenticated Role (operational tables):** `SELECT`, `INSERT`, `UPDATE`, `DELETE`

## Confirmations

- Auth configuration was not modified during migration.
- Public data was not modified.
- Production environment was not touched.
- No secrets were printed.

## Next Step

- Execute functional RLS matrix with `rls-a` / `rls-b`.

## Verdict

**PASS**
