# smartpyme_minimal_code_integration

## Propósito

Skill operativo para integrar cambios mínimos de código sin caer en auditorías extensas.

Regla central:

```text
leer poco -> decidir punto -> patch mínimo -> test puntual -> parar
```

## Uso

Usar cuando ya existe una pieza definida y solo falta conectarla en un punto acotado.

Ejemplos:

- integrar un contrato nuevo;
- conectar una capa mínima;
- agregar un test puntual;
- validar una frontera chica de código.

## Límites

- Máximo 5 archivos leídos.
- Máximo 2 búsquedas.
- Máximo 1 punto de integración.
- Máximo 2 archivos productivos modificados.
- Máximo 1 archivo de test modificado.
- Solo test puntual.

## Bloqueos

Responder con bloqueo si ocurre cualquiera de estos casos:

```text
BLOCKED_WRONG_BRANCH
BLOCKED_DIRTY_WORKTREE
BLOCKED_INTEGRATION_POINT
BLOCKED_SCOPE_VIOLATION
BLOCKED_CONTRACT_UNCERTAINTY
```

## Prohibido

- No auditar todo el repo.
- No rediseñar arquitectura.
- No tocar documentación conceptual.
- No tocar runtime.
- No tocar configuración.
- No tocar Hermes.
- No tocar evidencia histórica.
- No ampliar alcance.

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
