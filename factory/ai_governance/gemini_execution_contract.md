# Gemini Builder Execution Contract

## Orden obligatorio

1. Leer TaskSpec.
2. Ejecutar preflight.
3. Si hay archivo fuera de `allowed_files`, responder BLOCKED.
4. Si hay archivo en `locked_files`, no modificar.
5. Escribir solo lo permitido.
6. Ejecutar `required_tests`.
7. Emitir BuildReport.

## Prohibiciones

- No reescribir archivos validados si están en locked_files.
- No cambiar contratos existentes para que los tests pasen.
- No crear fixtures falsas salvo que la TaskSpec lo pida.
- No declarar VALIDADO.
- No tocar producto si la TaskSpec es factory/governance.
- No hacer commit ni push.

## Salida obligatoria

VEREDICTO_BUILDER:
FILES_TOUCHED:
COMMANDS_RUN:
TEST_RESULT:
EVIDENCE:
GIT_STATUS:
BLOCKERS:
