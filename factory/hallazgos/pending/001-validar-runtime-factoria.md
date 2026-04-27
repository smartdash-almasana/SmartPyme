# HALLAZGO

## META
- id: HLG-2026-04-27-SP-FACTORY-001
- estado: pending
- modulo_objetivo: factory
- prioridad: alta
- origen: gemini-architect
- repo_destino: E:\BuenosPasos\smartbridge\SmartPyme

## OBJETIVO
Validar el ciclo de ejecución de la factoría creando una pieza de documentación esencial sobre su propio funcionamiento.

## RUTAS_FUENTE
- N/A (creación de documentación)

## SLICES_CANDIDATOS
### Documentar Runtime de Factoría
- ruta: docs/factory_runtime_real.md
- tipo: document
- resumen: Explicar el modelo de operación basado en hallazgos markdown y sus estados.
- clasificacion: A
- motivo: Tarea documental segura y fundamental para la operatividad del equipo.

## TOP_SLICES
1. docs/factory_runtime_real.md

## PROPUESTA_DE_PORTADO
### Crear o modificar solo:
- `docs/factory_runtime_real.md`

## REGLAS_DE_EJECUCION
- Tarea exclusiva de documentación.
- NO TOCAR CÓDIGO PYTHON.
- NO TOCAR TESTS.
- NO TOCAR app/core/services.
- El archivo `docs/factory_runtime_real.md` debe contener una explicación del flujo.

### Contenido para `docs/factory_runtime_real.md`:
```markdown
# SmartPyme Factory: Runtime Real

La factoría de SmartPyme opera bajo un modelo de `hallazgos` basado en archivos Markdown, coordinando un equipo multiagente.

## Flujo de Estados

Los hallazgos transitan por los siguientes directorios, representando su estado:

1.  **`factory/hallazgos/pending`**: Hallazgos listos para ser evaluados y tomados por un agente.
2.  **`factory/hallazgos/in_progress`**: Hallazgos en ejecución activa por un agente.
3.  **`factory/hallazgos/done`**: Hallazgos completados y verificados.
4.  **`factory/hallazgos/blocked`**: Hallazgos que no pueden avanzar por dependencias o errores.

## Roles de Agentes

-   **Architect**: Diseña y crea los hallazgos en estado `pending`. Define el objetivo, alcance y criterios de cierre.
-   **Builder**: Toma hallazgos de `in_progress` y ejecuta la tarea de implementación o modificación.
-   **Auditor**: Verifica que los hallazgos en `done` cumplen con los criterios de aceptación y las reglas de la factoría.
```

## CRITERIO_DE_CIERRE
1. El archivo `docs/factory_runtime_real.md` existe y contiene el texto especificado.
2. El hallazgo `001-validar-runtime-factoría.md` es movido a `factory/hallazgos/done`.

## COMANDOS_DE_VALIDACION_TEXTO
```bash
# Verificar la existencia y contenido del archivo
cat docs/factory_runtime_real.md

# Confirmar que el contenido incluye los roles
grep -q "Roles de Agentes" docs/factory_runtime_real.md
```

## DUDAS_DETECTADAS
- ninguna

## PREGUNTA_AL_OWNER
- null
