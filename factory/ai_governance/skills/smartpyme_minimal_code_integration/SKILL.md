## SmartPyme Minimal Code Integration

metadata:
  hermes:
    category: development
    tags: [smartpyme, integration, minimal, guardrail]
---

# smartpyme_minimal_code_integration

## Propósito

Integrar cambios mínimos de código sin caer en auditorías extensas.

Regla central:

```text
leer poco -> decidir punto -> patch mínimo -> test puntual -> parar
```

## Límites duros

```text
ARCHIVOS_LEIDOS <= 5
BUSQUEDAS <= 2
PUNTOS_DE_INTEGRACION = 1
ARCHIVOS_PRODUCTIVOS_MODIFICADOS <= 2
ARCHIVOS_TEST_MODIFICADOS <= 1
```

## Bloqueos

Responder con bloqueo si ocurre cualquiera de estos casos:

```text
BLOCKED_WRONG_BRANCH
BLOCKED_DIRTY_WORKTREE
BLOCKED_INTEGRATION_POINT
BLOCKED_SCOPE_VIOLATION
BLOCKED_CONTRACT_UNCERTAINTY
BLOCKED_MODEL_TARGET_MISSING
BLOCKED_MODEL_TARGET_INVALID
```

## Prohibido

```text
No auditar repo completo.
No rediseñar arquitectura.
No tocar documentación conceptual.
No tocar runtime.
No tocar configuración.
No tocar Hermes.
No tocar evidencia histórica.
No ampliar alcance.
```

## Procedimiento

1. Confirmar rama y estado de trabajo.
2. Leer solo archivos directamente necesarios.
3. Declarar punto de integración antes del patch.
4. Aplicar cambio mínimo.
5. Ejecutar test puntual.
6. Parar.

## Salida obligatoria

```text
VEREDICTO:
RAMA:
GIT_STATUS_ANTES:
ARCHIVOS_LEIDOS:
BUSQUEDAS:
PUNTO_DE_INTEGRACION:
ARCHIVOS_MODIFICADOS:
TEST_RESULT:
LIMITES:
BLOQUEOS:
NEXT_STEP:
```

## Frase rectora

```text
Si no puede integrarse con 5 archivos y 1 test, no se integra: se bloquea.
```
