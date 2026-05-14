# STAGING RLS Execution Runbook

## Estado Actual
- Rama objetivo: `product/laboratorio-mvp-vendible` sincronizada con `origin`.
- Commit `3cc8fb2` contiene artefactos de seguridad RLS/Auth provisioning.
- Commit `8e61cdf` agrega ignore para `.aider*`.
- Confirmado: no se aplicó SQL ni se tocó Supabase.

## Alcance
- Este runbook aplica solo a **staging**.
- Producción queda fuera de alcance en este ciclo.

## Precondiciones
- Backup completo de `app_metadata` en Auth para los usuarios de staging.
- Mapeo validado `user_id/email -> tenant_id`.
- Cada `tenant_id` debe existir en `public.clientes.cliente_id`.
- `service_role` disponible solo en entorno seguro y controlado.

## Secuencia Operativa
1. Verificar repo limpio
- `git status --short` debe estar vacío.
- Confirmar branch esperada y commit objetivo.

2. Preparar mapeo de usuarios staging
- Consolidar lista de usuarios y tenant destino.
- Revisar duplicados, faltantes y tenants inválidos.

3. Ejecutar provisioning Auth read-modify-write
- GET user.
- Backup `app_metadata_before`.
- Merge de claims preservando claves existentes.
- PATCH de `app_metadata` completo.
- GET verify.

4. Forzar refresh/sign-in
- Forzar renovación de sesión para claims actualizados.

5. Validar `auth.jwt() ->> 'tenant_id'`
- Confirmar claim canónico en token fresco.
- Si falta claim, bloquear ejecución de migración.

6. Aplicar migración RLS solo en staging
- Ejecutar únicamente los SQL aprobados para hardening staging.
- No aplicar en producción.

7. Ejecutar matriz RLS
- Correr pruebas por rol/tenant y registrar evidencia.

8. Documentar resultado
- Guardar evidencia de comandos/salidas, veredicto y riesgos.

## Rollback
- Auth rollback:
  - Restaurar `app_metadata_before` exacto por usuario.
  - Revalidar con GET + token refresh.

- SQL rollback seguro:
  - Usar rollback seguro aprobado.
  - Mantener `anon` cerrado.

- Regla explícita:
  - No reabrir `anon` bajo ningún rollback estándar.

## Matriz Mínima de Validación
- `anon` -> deny.
- Tenant A ve solo Tenant A.
- Tenant A no ve Tenant B.
- Usuario sin claim tenant -> deny.
- `curated_evidence` aislada por `tenant_id`.
- `clientes` solo `SELECT` para `authenticated`.
- `service_role` allow para operación backend.

## Criterio de Salida
- PASS:
  - Provisioning correcto, claims vigentes en token, matriz RLS completa sin violaciones.

- PARTIAL:
  - Cambios aplicados en staging pero con casos no concluyentes o evidencia incompleta.

- BLOCKED:
  - Faltan precondiciones, falla claim canónico, o no hay garantías de aislamiento tenant.

## Confirmación Explícita NO APPLY
- Este runbook es documentación operativa local.
- No se ejecutó SQL en este paso.
- No se llamaron APIs de Supabase.
- No se aplicaron migraciones.
- No se crearon scripts ejecutables.
- No se tocó VM/runtime.
