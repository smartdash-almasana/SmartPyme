# Factory Runtime Real

Este documento describe el modelo de operación de la factoría de software, un sistema diseñado para gestionar el ciclo de vida de los hallazgos (tareas) de manera eficiente y validada.

## Modelo de Operación

El modelo se basa en archivos Markdown que representan "hallazgos" o tareas. Cada hallazgo es una unidad de trabajo que transita por diferentes estados y es gestionada por roles específicos, siguiendo un protocolo estricto para garantizar la calidad y la trazabilidad.

## Estados de un Hallazgo

Cada hallazgo puede encontrarse en uno de los siguientes estados:

-   `pending`: La tarea está esperando ser asignada y no ha sido iniciada.
-   `in_progress`: La tarea está siendo ejecutada activamente por un agente.
-   `done`: La tarea ha sido completada, validada y la evidencia ha sido aceptada.
-   `blocked`: La tarea no puede continuar debido a un impedimento o dependencia externa.

## Roles del Sistema

-   **Hermes (Orquestador):** Es el agente principal que gestiona el flujo de trabajo. Asigna tareas, mueve los hallazgos entre estados y coordina a los demás agentes.
-   **Builder (Ejecutor):** Es el agente responsable de ejecutar las tareas definidas en un hallazgo. Su trabajo consiste en escribir código, crear archivos o realizar cualquier acción técnica necesaria.
-   **Auditor (Validador):** Es el agente encargado de verificar que el trabajo realizado por el Builder cumple con los requisitos del hallazgo. Su validación se basa en la evidencia presentada.

## Protocolo: Write → Verify → Report

El ciclo de vida de una tarea sigue un protocolo estricto para asegurar la calidad y la trazabilidad del trabajo:

1.  **Write:** El `Builder` ejecuta la tarea y genera la evidencia de su trabajo.
2.  **Verify:** El `Auditor` revisa la evidencia y valida si el trabajo cumple con los criterios de aceptación.
3.  **Report:** Se genera un informe final que certifica la finalización y validación del hallazgo.

## Validación Basada en Evidencia

Un principio fundamental del sistema es que todo trabajo debe ser verificable. Por lo tanto:

**Un trabajo sin evidencia adjunta se considera `NO_VALIDADO`.**

La evidencia es la única prueba de que una tarea se ha completado correctamente y es indispensable para que un hallazgo pueda moverse al estado `done`.
