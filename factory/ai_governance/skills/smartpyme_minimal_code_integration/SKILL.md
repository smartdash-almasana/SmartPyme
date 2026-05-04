## SmartPyme Minimal Code Integration

metadata:
  hermes:
    category: development
    tags: [smartpyme, integration, minimal, guardrail, close-loop]
---

# smartpyme_minimal_code_integration

## Propósito

Integrar cambios mínimos de código sin caer en auditorías extensas ni ciclos abiertos.

Regla central:

```text
leer poco -> decidir punto -> patch mínimo -> test puntual -> diff -> cierre -> parar
```

## Límites duros

```text
ARCHIVOS_LEIDOS <= 5
BUSQUEDAS <= 2
PUNTOS_DE_INTEGRACION = 1
ARCHIVOS_PRODUCTIVOS_MODIFICADOS <= 2
ARCHIVOS_TEST_MODIFICADOS <= 1
INTENTOS_CORRECCION <= 1
```

## Bloqueos

```text
BLOCKED_WRONG_BRANCH
BLOCKED_DIRTY_WORKTREE
BLOCKED_INTEGRATION_POINT
BLOCKED_SCOPE_VIOLATION
BLOCKED_CONTRACT_UNCERTAINTY
BLOCKED_MODEL_TARGET_MISSING
BLOCKED_MODEL_TARGET_INVALID
BLOCKED_TESTS_FAIL
BLOCKED_LOOP_DETECTED
BLOCKED_CLOSE_DECISION_MISSING
```

## Prohibido

```text
No auditar repo completo.
No rediseñar arquitectura.
No ampliar alcance.
No seguir leyendo después del patch.
No seguir buscando después del patch.
No modificar después de entrar en cierre salvo una corrección mínima.
```

## Procedimiento obligatorio

1. Confirmar rama y estado de trabajo.
2. Leer solo archivos directamente necesarios.
3. Declarar punto de integración antes del patch.
4. Aplicar cambio mínimo.
5. Ejecutar test puntual.
6. Mostrar diff acotado de archivos tocados.
7. Decidir cierre.
8. Parar.

## Cierre transaccional obligatorio

Después de aplicar patch queda prohibido continuar con exploración.

El agente debe pasar a una de dos decisiones:

```text
COMMIT_AND_PUSH
BLOCKED_NO_COMMIT
```

Si decide `COMMIT_AND_PUSH`, debe terminar con commit, push y estado limpio.

Si decide `BLOCKED_NO_COMMIT`, debe terminar con bloqueo, causa y estado de trabajo.

## Condición anti-loop

Si después de patch/test el agente intenta leer más archivos, buscar más contexto o abrir otro frente, debe responder:

```text
BLOCKED_LOOP_DETECTED
```

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
GIT_DIFF_RESUMEN:
DECISION_CIERRE:
COMMIT:
PUSH_RESULT:
GIT_STATUS:
LIMITES:
BLOQUEOS:
NEXT_STEP:
```

## Frase rectora

```text
Si no puede integrarse con 5 archivos, 1 test y cierre transaccional, no se integra: se bloquea.
```
