# Core Pipeline Status

## 1. Resumen Ejecutivo
Este documento certifica el estado del pipeline de procesamiento de datos de SmartPyme después del commit `da18e2f`. El pipeline ahora incluye un `ActionProposalService`, que genera propuestas de acción concretas a partir de los hallazgos. Esto completa la primera fase del ciclo "Generar → Mostrar → Confirmar → Ejecutar". El pipeline es funcional, estable y determinístico.

## 2. Estado Validado del Pipeline
El pipeline extiende su flujo para incluir la generación de propuestas de acción. A partir de los `messages`, el `ActionProposalService` genera una o más `action_proposals`.
`... → hallazgos → persistencia → mensajes → ACTION PROPOSALS → PipelineResult`

**Estado:** `ESTABLE`
**Última Validación:** 62 tests pasados / 0 fallidos.

## 3. Tabla de Componentes Existentes
| Componente                          | Ruta                                                 | Rol en el Pipeline                                     |
| ----------------------------------- | ---------------------------------------------------- | ------------------------------------------------------ |
| `...`                               | `...`                                                | `...`                                                  |
| `FindingCommunicationService`       | `app/services/finding_communication_service.py`      | Convierte `findings` en `messages` legibles.           |
| `ActionProposalService`             | `app/services/action_proposal_service.py`            | Genera `action_proposals` a partir de `messages`.      |
| `Pipeline`                          | `app/core/pipeline.py`                               | Orquesta el flujo completo del pipeline.               |

## 4. Contratos de Salida

### Contrato `PipelineResult`
El contrato se extiende para incluir las propuestas de acción.

```python
@dataclass
class PipelineCounts:
    # ... sin cambios
    messages: int
    action_proposals: int

@dataclass
class PipelineResult:
    # ... sin cambios
    blocking_reason: str | None = None
    # ...
    messages: list
    action_proposals: list  # This is the PipelineResult.action_proposals field
    counts: PipelineCounts
    errors: list
```

### Contrato `ActionProposal`
Representa una acción sugerida, su justificación y el comando para ejecutarla.
```python
@dataclass
class ActionProposal:
    status: str  # Siempre "proposed" en esta etapa
    title: str
    finding_id: str
    reason: str
    action_type: str  # ej: "api_call", "human_task"
    command: dict     # ej: {"verb": "POST", "url": "...", "body": "..."}
```

## 5. Tests que Validan Cada Capa
Se han añadido tests específicos para el `ActionProposalService` que validan:
- Si `action_proposal_service` está configurado y hay `messages`, se generan `action_proposals`.
- Si el servicio no está configurado, `action_proposals` es una lista vacía.
- Todas las propuestas generadas tienen `status="proposed"`.
- La estructura de las propuestas se alinea con el contrato `ActionProposal`.

## 6. Reglas de Negocio Preservadas
Se añade una nueva regla:
- **Generar antes de Actuar:** Las acciones no se ejecutan directamente. Primero deben ser propuestas, presentadas a un agente (humano o máquina) y confirmadas explícitamente. Esta implementación solo cubre la etapa de **Generación**.

## 7. Qué NO Está Implementado
El `ActionProposalService` solo genera propuestas; no las ejecuta. El ciclo completo no está implementado:
- **Aprobación/Rechazo de Propuestas:** No hay un mecanismo para que un usuario o sistema apruebe o rechace una `ActionProposal`.
- **Motor de Ejecución:** No existe un `ActionExecutionEngine` que tome una propuesta aprobada y la ejecute.
- **Canales de Comunicación para Acciones:** No hay UI ni APIs para mostrar las propuestas de acción o recibir confirmaciones.
- **Clarification Loop y Canales de Salida:** Sin cambios.

## 8. Riesgos Técnicos Actuales
1.  **Seguridad de Ejecución:** Cuando se implemente el motor de ejecución, será crítico asegurar que los comandos propuestos sean seguros y no puedan ser explotados.
2.  **Resolución de Bloqueos Manual:** Sin cambios.
3.  **Escalabilidad de Repositorios en Memoria:** Sin cambios.

## 9. Próximo Paso Recomendado
**Desarrollar el `ActionExecutionEngine` y un mecanismo de aprobación.** Esto implicaría:
1.  Crear un servicio que pueda recibir una `action_id` aprobada.
2.  Implementar la lógica para ejecutar la acción descrita en el campo `command` de la propuesta.
3.  Diseñar un endpoint o interfaz simple para que un humano o sistema pueda enviar la señal de "aprobado".

## 10. Criterio para no Romper este Contrato
(Sin cambios)
