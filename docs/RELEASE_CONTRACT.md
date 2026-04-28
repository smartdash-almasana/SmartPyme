# Release Contract — SmartPyme Factory

## Regla

Ningún cambio de factoría pasa a operativo sin evidencia, test y aprobación humana.

## Versionado

- SemVer para releases formales.
- Changelog desde TaskSpecs y git log.
- Rollback por revert commit, no por force push.

## Estados

- `AWAITING_HUMAN_MERGE`: listo para revisión humana.
- `MERGED`: integrado.
- `CLOSED`: ciclo cerrado.
- `ABANDONED`: descartado.

## Feature flags

Archivo esperado:

```text
factory/control/feature_flags.yaml
```

No crear flags activas sin TaskSpec.
