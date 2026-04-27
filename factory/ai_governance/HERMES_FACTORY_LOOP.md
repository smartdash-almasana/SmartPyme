# Hermes Factory Loop

Hermes Agent es el orquestador operativo de SmartPyme Factory.

## Flujo

```text
pending -> in_progress -> done | blocked
```

## Responsabilidades

- Hermes: orquesta, mueve estados, delega y registra evidencia.
- Builder: ejecuta solo rutas autorizadas por el hallazgo.
- Auditor: valida evidencia y no corrige archivos.

## Evidencia

Cada ciclo debe escribir evidencia en:

```text
factory/evidence/<hallazgo_id>/
```

Archivos esperados:

```text
builder_report.md
auditor_report.md
git_status.txt
diff.patch
status.json
```

## Regla

Sin evidencia verificable, el resultado es NO_VALIDADO.
