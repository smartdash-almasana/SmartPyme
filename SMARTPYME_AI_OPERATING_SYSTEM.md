# SmartPyme AI Operating System — Diseño de Gobernanza Multiagente

## Veredicto

El modo anterior fallaba porque Gemini recibía intención general y podía reinterpretar el contrato.
El nuevo modo no le pide “ayuda”: le entrega una unidad cerrada, archivos permitidos, archivos bloqueados, verificador previo y formato de salida obligatorio.

ChatGPT no debe operar como Builder.
ChatGPT queda como Auditor Arquitectónico externo.

## Mapa de roles

| Pieza | Rol | Escribe código | Decide |
|---|---|---:|---:|
| Hermes | Orquestador de tareas, cola, estado y handoff | No | Sí, sobre flujo |
| Gemini Builder | Implementa una TaskSpec cerrada | Sí | No |
| Gemini Auditor | Revisa diff, tests y evidencia | No | Sí, sobre validación técnica |
| QA | Corre tests/smokes | No negocio | No |
| ChatGPT | Diseña contratos, audita reportes, corta tareas | No repo | Sí, sobre arquitectura |
| Humano | Aprueba gobernanza/deploy/bloqueos | Manual | Sí |

## Regla de oro

Ningún agente recibe un objetivo abierto.
Todo agente recibe un archivo TaskSpec y un contrato de ejecución.

## Flujo correcto

1. Hermes crea o selecciona una TaskSpec.
2. Gemini Builder solo puede tocar `allowed_files`.
3. Gemini Builder debe ejecutar `preflight` antes de escribir.
4. Gemini Builder escribe.
5. Gemini Builder corre tests exactos de `required_tests`.
6. Gemini Builder emite BuildReport.
7. Gemini Auditor revisa diff + tests + scope.
8. Hermes registra estado: VALIDADO / NO_VALIDADO / BLOCKED.
9. ChatGPT audita solo si hay reporte.

## Anti-deriva

- Si el agente necesita tocar un archivo no permitido: BLOCKED.
- Si intenta modificar tests para adaptar el contrato: NO_VALIDADO.
- Si cambia funciones ya validadas sin permiso explícito: NO_VALIDADO.
- Si crea fixtures falsas no derivadas de TaskSpec: NO_VALIDADO.
- Si cambia schema de datos sin TaskSpec de governance: NO_VALIDADO.

## Primer uso

Copiar este pack al repo y usar:
`factory/ai_governance/tasks/task_loop_001.yaml`
como fuente única para Gemini Builder.
