# STAGING Auth Tenant Provisioning Plan

## Objetivo
Documentar el provisioning seguro de `app_metadata` para staging, alineado al hardening RLS tenant-aware, sin ejecutar cambios sobre Supabase en este paso.

## Contrato `app_metadata`
- Claim canónico: `tenant_id`.
- Claim legacy transitorio: `cliente_id`.
- Regla de compatibilidad:
  - `tenant_id` manda como fuente principal de autorización.
  - `cliente_id` solo fallback temporal para tablas legacy.
- Regla fail-closed:
  - Si faltan ambos claims, el acceso queda denegado por RLS.

## Flujo Seguro Read-Modify-Write
1. GET user
- Leer usuario objetivo por `user_id` desde Admin API.
- Capturar snapshot completo de `app_metadata` actual.

2. Backup `app_metadata_before`
- Guardar backup inmutable antes de cualquier edición.
- Persistir con timestamp, actor y correlación operativa.

3. Merge seguro de claims
- Partir de `app_metadata_before`.
- Preservar todas las claves existentes.
- Sobrescribir/agregar solo:
  - `tenant_id`
  - `cliente_id` (si aplica por compatibilidad)

4. PATCH `app_metadata` completo
- Enviar objeto merged completo (no parcial ambiguo).
- Evitar borrar claves no relacionadas.

5. GET verify
- Releer usuario.
- Confirmar igualdad exacta entre esperado y recibido para los claims de tenant.

6. Refresh / sign-in
- Forzar refresh de sesión o re-login para renovar JWT.
- Validar que el token emitido contiene claims actualizados.

7. Rollback exacto desde backup
- Si falla verificación funcional o de seguridad, restaurar `app_metadata_before` completo.
- Revalidar con GET posterior al rollback.

## Formato JSON de Backup
```json
{
  "backup_version": 1,
  "environment": "staging",
  "captured_at": "2026-05-14T00:00:00Z",
  "captured_by": "<actor>",
  "correlation_id": "<uuid-or-ticket>",
  "user_id": "<supabase-auth-user-id>",
  "app_metadata_before": {
    "role": "user",
    "tenant_id": "tenant_a",
    "cliente_id": "tenant_a",
    "other_existing_key": "preserved"
  }
}
```

## Pseudocódigo Seguro (No Ejecutable)
```text
function provisionTenantClaims(user_id, target_tenant_id, target_cliente_id_optional):
  user_before = admin_get_user(user_id)
  assert user_before exists

  app_metadata_before = user_before.app_metadata or {}
  backup = build_backup(user_id, app_metadata_before, actor, correlation_id, now)
  persist_backup(backup)

  merged = copy(app_metadata_before)
  merged.tenant_id = target_tenant_id

  if target_cliente_id_optional is present:
    merged.cliente_id = target_cliente_id_optional
  else if merged.cliente_id missing:
    merged.cliente_id = target_tenant_id   # compat fallback only

  admin_patch_user_app_metadata(user_id, merged)

  user_after = admin_get_user(user_id)
  assert user_after.app_metadata.tenant_id == merged.tenant_id
  assert user_after.app_metadata.cliente_id == merged.cliente_id

  force_session_refresh_or_relogin(user_id)
  token_claims = inspect_fresh_token(user_id)
  assert token_claims.tenant_id == merged.tenant_id OR token_claims.cliente_id == merged.cliente_id

  return success

on_failure:
  admin_patch_user_app_metadata(user_id, app_metadata_before)
  user_rollback = admin_get_user(user_id)
  assert user_rollback.app_metadata == app_metadata_before
  return rollback_success
```

## Rollback Seguro
- Trigger de rollback:
  - claims no persisten tras PATCH;
  - token refrescado no refleja tenant esperado;
  - pruebas RLS fallan (cross-tenant allow inesperado o deny indebido).
- Acción:
  - restaurar exactamente `app_metadata_before` desde backup;
  - revalidar con GET;
  - forzar refresh de sesión;
  - registrar incidente y bloquear rollout.

## Matriz de Validación
| Caso | Precondición | Acción | Esperado |
|---|---|---|---|
| Set canónico nuevo | user sin `tenant_id` | merge + PATCH + verify | `tenant_id` presente y correcto |
| Compat legacy | tabla usa `cliente_id` | merge incluye `cliente_id` | fallback funcional sin perder claves |
| Preservación de metadata | app_metadata con claves extra | merge + PATCH | claves extra intactas |
| Token freshness | claims actualizados en storage | refresh/re-login | JWT refleja claim actualizado |
| Rollback exacto | falla validación | restore backup | `app_metadata` idéntico al backup |
| Fail-closed | sin claims tenant | prueba de acceso | RLS DENY |

## Riesgos
- Riesgo de sobreescritura accidental de claves si no se usa merge completo.
- Riesgo de decisiones con token stale si no se fuerza refresh/re-login.
- Riesgo temporal por dualidad `tenant_id`/`cliente_id` hasta normalizar esquema.
- Riesgo operativo si no existe trazabilidad de backup por usuario.

## Confirmación Explícita NO APPLY
- Este documento es solo diseño operativo.
- No se ejecutaron scripts.
- No se llamó Supabase Admin API.
- No se aplicaron migraciones.
- No se realizaron mutaciones en DB ni en Auth runtime.
