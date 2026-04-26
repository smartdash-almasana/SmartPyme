# Core Pipeline Status

## 1. Resumen Ejecutivo
Este documento certifica el estado del pipeline de procesamiento de datos de SmartPyme después del commit `79e94e4`. El pipeline ahora define una frontera clara entre la decisión y la ejecución a través del `ExecutionAdapter`. SmartPyme sigue decidiendo qué hacer, pero delega la ejecución a un adaptador externo, que reporta el resultado. Esto formaliza la separación de responsabilidades y prepara la integración con ejecutores externos como Hermes, sin ceder el control del flujo principal.

## 2. Estado Validado del Pipeline
El `ActionExecutionService` ahora actúa como un puente hacia un `ExecutionAdapter` opcional.
`... → execution guard → EXECUTION ADAPTER BOUNDARY → PipelineResult`

**Estado:** `ESTABLE`
**Última Validación:** 81 tests pasados / 0 fallidos.

## 3. Tabla de Componentes Existentes
| Componente                          | Ruta                                                 | Rol en el Pipeline                                     |
| ----------------------------------- | ---------------------------------------------------- | ------------------------------------------------------ |
| `...`                               | `...`                                                | `...`                                                  |
| `ActionExecutionService`            | `app/services/action_execution_service.py`           | **Guard y Puente:** Valida y delega la ejecución al adapter. |
| `ExecutionAdapterContract`          | `app/contracts/execution_adapter_contract.py`        | Define la interfaz para los adaptadores de ejecución.    |

## 4. Frontera de Ejecución: SmartPyme ↔ Adaptador (Hermes)
Se establece una frontera formal para la ejecución de acciones, desacoplando la lógica de negocio del mundo exterior.

- **SmartPyme sigue decidiendo:** El core de SmartPyme es responsable de generar, proponer y aprobar acciones. Mantiene la autoridad sobre *qué* se debe hacer y *cuándo*.
- **El Adaptador ejecuta y reporta:** El `ExecutionAdapter` recibe una acción aprobada y es responsable únicamente de ejecutarla y reportar el resultado (`executed`, `failed`, `blocked`). No tiene lógica de negocio ni poder de decisión sobre el flujo.
- **Hermes como Adaptador:** Hermes puede ser un `ExecutionAdapter` futuro. En ese rol, recibiría órdenes de SmartPyme, las ejecutaría en su propio entorno (MCP) y devolvería un `ExecutionAdapterResult`. Hermes no gobierna el core de SmartPyme; es un ejecutor especializado.

### Contrato `ExecutionAdapter`
```python
class ExecutionAdapter(Protocol):
    def execute(self, action: ActionProposal) -> ExecutionAdapterResult:
        ...
```

### Contrato `ExecutionAdapterResult`
```python
@dataclass
class ExecutionAdapterResult:
    status: str  # "executed", "failed", "blocked_by_user"
    message: str
    original_action: ActionProposal
```

## 5. Tests que Validan la Frontera
- Si se provee un `ExecutionAdapter`, `ActionExecutionService` lo invoca.
- El estado final de la acción (`executed`) depende del `status` en el `ExecutionAdapterResult`.
- Si el adapter devuelve `failed` o `blocked`, la acción NO se marca como `executed` en SmartPyme.
- Si no se provee un adapter, el servicio mantiene su comportamiento interno (marcar como `executed` sin hacer nada más).

## 6. Reglas de Negocio Preservadas
- **Separación de Responsabilidades:** El core decide, el adaptador ejecuta. Esta es la nueva regla fundamental que gobierna la interacción con sistemas externos.
- **Guardián de Aprobación:** Se mantiene. El `ActionExecutionService` sigue validando que la acción esté `approved` antes de pasarla a cualquier adaptador.

## 7. Qué NO Está Implementado
La ejecución real sigue siendo una simulación a nivel de contrato.
- **`HermesExecutionAdapter`:** No existe una implementación real de un adaptador que se comunique con Hermes.
- **Llamadas HTTP Reales:** Ningún adaptador realiza llamadas de red.
- **Infraestructura MCP:** No hay un `Multi-Cloud Piper` (MCP) real para que Hermes opere.
- **Conectores Externos:** Sigue sin haber conectores que traduzcan acciones a llamadas de API específicas.

## 8. Riesgos Técnicos Actuales
1.  **Contrato del Adaptador:** La robustez del contrato entre SmartPyme y los adaptadores es crítica. Cambios en este contrato podrían romper integraciones.
2.  **Seguridad de Conectores:** Sin cambios. Sigue siendo el principal riesgo futuro.
3.  **Idempotencia:** Sin cambios.

## 9. Próximo Paso Recomendado
**Implementar un `MockHermesExecutionAdapter` y un test de integración.**
1.  Crear una clase `MockHermesExecutionAdapter` que implemente el protocolo `ExecutionAdapter`.
2.  En su método `execute`, simular una llamada a Hermes devolviendo un `ExecutionAdapterResult` exitoso.
3.  Crear un test de integración que inyecte este mock en el `ActionExecutionService` y verifique que la acción se marca como `executed` solo cuando el mock devuelve `status="executed"`.

## 10. Criterio para no Romper este Contrato
(Sin cambios)
