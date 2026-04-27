# Runtime real de SmartPyme Factory

SmartPyme Factory opera mediante hallazgos markdown persistidos en el repositorio. Cada hallazgo es una unidad de trabajo chica, auditable y trazable.

El repositorio es la fuente de verdad. GitHub conserva el historial. Hermes actua como orquestador operativo. Builder ejecuta. Auditor valida.

## Estados

Los hallazgos viven en estas carpetas:

```text
factory/hallazgos/pending
factory/hallazgos/in_progress
factory/hallazgos/done
factory/hallazgos/blocked
```

- `pending`: hallazgo creado, todavia no ejecutado.
- `in_progress`: hallazgo tomado por Hermes y derivado a Builder.
- `done`: trabajo validado por Auditor.
- `blocked`: trabajo detenido por error, falta de evidencia o violacion de contrato.

## Roles

- Hermes orquesta el flujo, mueve estados y exige evidencia.
- Architect disena hallazgos ejecutables.
- Builder ejecuta solo las rutas permitidas por el hallazgo.
- Auditor valida evidencia contra criterios de aceptacion.

Ningun agente valida su propio trabajo.

## Protocolo

Todo cambio debe seguir:

```text
Write -> Verify -> Report
```

Builder escribe, verifica y reporta. Auditor revisa y emite `VALIDADO` o `NO_VALIDADO`.

## Evidencia

La evidencia se guarda en:

```text
factory/evidence/<hallazgo_id>/
```

Si no hay evidencia verificable, el resultado es `NO_VALIDADO` y el hallazgo no puede cerrarse como `done`.

## Regla de alcance

No se toca codigo de producto, tests ni servicios sin un hallazgo explicito que autorice esas rutas.
