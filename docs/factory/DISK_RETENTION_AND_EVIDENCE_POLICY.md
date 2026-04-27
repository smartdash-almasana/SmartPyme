# Disk, Retention and Evidence Policy — SmartPyme Factory

## Objetivo

Evitar que la VM de factoría se quede sin espacio y asegurar que cada ciclo quede documentado con trazabilidad reproducible.

## Riesgo operativo

Si el disco de la VM se agota:

- Hermes puede fallar en medio de un ciclo.
- Codex puede fallar al escribir archivos o evidencia.
- Git puede fallar en pull, commit o rebase.
- Los logs pueden quedar incompletos.
- La evidencia puede perderse o quedar corrupta.

Por eso el loop debe operar fail-closed ante presión de disco.

## Umbrales

```text
< 80% uso     → OK
80% - 89%     → WARNING_DISK_PRESSURE
>= 90%        → BLOCKED_DISK_CRITICAL
```

Si el disco está en estado crítico, Hermes no debe iniciar un ciclo nuevo.

## Directorios controlados

```text
factory/evidence/
factory/runner_logs/
.actions-runner/_work/          # workspace externo del runner, no versionado
~/.cache/pip/
~/.npm/_cacache/
```

## Evidencia obligatoria por ciclo

Cada ciclo debe dejar:

```text
factory/evidence/<task_id>/
  cycle.md
  commands.txt
  git_status.txt
  git_diff.patch
  tests.txt
  decision.txt
```

## Cierre documental obligatorio

Cada ciclo debe registrar:

- qué se hizo;
- por qué se hizo;
- archivos modificados;
- comandos ejecutados;
- resultado de tests/linter;
- evidencia generada;
- decisión final;
- riesgos abiertos;
- siguiente paso sugerido.

Sin cierre documental:

```text
NO_VALIDADO
```

## Retención local recomendada

```text
factory/runner_logs/      → conservar 14 días localmente
factory/evidence/         → conservar 30 días localmente
runner workspaces viejos   → limpiar semanalmente
pip/npm cache             → limpiar cuando disco > 80%
```

## Bucket externo

Conviene mover evidencia histórica a bucket para no saturar disco.

Diseño recomendado:

```text
gs://<bucket-smartpyme-factory-evidence>/
  evidence/YYYY/MM/DD/<task_id>/
  runner_logs/YYYY/MM/DD/
```

Reglas:

- La evidencia reciente queda local para debugging rápido.
- La evidencia vieja se sincroniza al bucket.
- La VM conserva índice mínimo local.
- No subir secretos, `.env`, credenciales ni bases SQLite con datos sensibles sin cifrado.

## Política de borrado

No borrar evidencia sin antes:

1. comprimir o sincronizar a bucket;
2. verificar subida;
3. registrar índice local;
4. dejar log de limpieza.

## Comando recomendado de sincronización

```bash
gsutil -m rsync -r factory/evidence gs://<bucket>/evidence
```

## Estado actual

Pendiente de implementación:

- script `scripts/factory_disk_guard.py`;
- integración del guard en `hermes_factory_runner.py`;
- bucket real definido;
- rotación automática;
- índice local de evidencia archivada.
