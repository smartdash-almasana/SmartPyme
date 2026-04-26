# Core Pipeline Status

## 1. Resumen Ejecutivo
Este documento certifica el estado del pipeline de procesamiento de datos de SmartPyme después de los commits `7ca9034` y `e1a5236`. El pipeline ahora soporta un ciclo de vida de acciones completo a nivel lógico, incluyendo la propuesta, decisión (aprobación/rechazo) y un guardián de ejecución. Aunque no se ejecutan acciones externas reales, la plomería interna y las reglas de negocio para un manejo seguro de acciones están implementadas y validadas.

## 2. Estado Validado del Pipeline
El flujo de acciones se ha completado con la adición de servicios de decisión y ejecución.
`... → action_proposals → APPROVE/REJECT → EXECUTION GUARD → PipelineResult`

**Estado:** `ESTABLE`
**Última Validación:** 75 tests pasados / 0 fallidos.

## 3. Tabla de Componentes Existentes
| Componente                          | Ruta                                                 | Rol en el Pipeline                                     |
| ----------------------------------- | ---------------------------------------------------- | ------------------------------------------------------ |
| `...`                               | `...`                                                | `...`                                                  |
| `ActionProposalService`             | `app/services/action_proposal_service.py`            | Genera `action_proposals` a partir de `messages`.      |
| `ActionDecisionService`             | `app/services/action_decision_service.py`            | Cambia el estado de una acción a `approved`/`rejected`. |
| `ActionExecutionService`            | `app/services/action_execution_service.py`           | **Guard:** Permite la ejecución solo si `status="approved"`. |
| `Pipeline`                          | `app/core/pipeline.py`                               | Orquesta el flujo completo del pipeline.               |

## 4. Ciclo de Vida de Acciones (Action Lifecycle)
Se ha implementado un ciclo de vida estricto para las acciones, garantizando seguridad y control.
1.  **Propuesta (`proposed`):** `ActionProposalService` genera una acción con `status="proposed"`.
2.  **Decisión (`approved`/`rejected`):** Un agente externo (humano o sistema) invoca `ActionDecisionService` para aprobar o rechazar la propuesta. El servicio retorna una nueva instancia inmutable de la acción con el estado actualizado.
3.  **Ejecución (`executed`):** `ActionExecutionService` es invocado con la acción. Contiene un **guardián de seguridad (approved-only guard)** que verifica que el `status` sea `approved`. Si no lo es, levanta un error y bloquea la ejecución. Si es `approved`, cambia el estado a `executed`. **Actualmente no ejecuta nada externo.**

## 5. Tests que Validan Cada Capa
Se han añadido tests que validan el ciclo de vida de las acciones:
- `ActionDecisionService` cambia correctamente el estado a `approved` o `rejected`.
- `ActionExecutionService` levanta un `PermissionError` si se intenta ejecutar una acción que no está en estado `approved`.
- `ActionExecutionService` cambia el estado a `executed` si la acción fue aprobada previamente.
- Se usan `dataclasses.replace` para asegurar la inmutabilidad de las acciones a través de los estados.

## 6. Reglas de Negocio Preservadas
El ciclo de vida de acciones refuerza la seguridad y el control:
- **Inmutabilidad:** Las acciones son inmutables. Cada cambio de estado crea una nueva instancia.
- **Guardián de Aprobación (Approved-Only Guard):** Es imposible ejecutar una acción que no haya sido explícitamente aprobada. Este es un control de seguridad no negociable.
- **Generar → Decidir → Ejecutar:** El flujo es mandatorio. No se pueden saltar pasos.

## 7. Qué NO Está Implementado
La ejecución de acciones sigue siendo interna y simulada. Los conectores con el mundo real no existen.
- **Ejecución Externa Real:** El `ActionExecutionService` solo cambia el estado a `executed`; no realiza ninguna llamada a API, no modifica bases de datos ni interactúa con sistemas externos.
- **Conectores de Acción:** No hay `ActionConnectors` que traduzcan un comando de acción genérico en una llamada específica a un sistema (ej. un conector para Mercado Libre, un conector para Shopify, etc.).
- **Canales de Decisión:** No hay una UI, API o bot (Telegram/WhatsApp) que permita a un usuario ver las propuestas y aprobarlas o rechazarlas.

## 8. Riesgos Técnicos Actuales
1.  **Seguridad de Conectores:** El mayor riesgo se ha movido a la futura implementación de los conectores de acción. Será crítico que estos conectores sean seguros, validen los parámetros de entrada y tengan un manejo de errores robusto.
2.  **Idempotencia en Ejecución:** Cuando la ejecución sea real, será necesario garantizar que las acciones sean idempotentes para evitar efectos no deseados si se reintentan.
3.  **Resolución de Bloqueos Manual:** Sin cambios.

## 9. Próximo Paso Recomendado
**Implementar el primer `ActionConnector` real.** Por ejemplo, un conector para la API de Mercado Libre.
1.  Crear una clase `MercadoLibreActionConnector`.
2.  Implementar un método `execute` que reciba un `command` del `ActionProposal`.
3.  El método debe traducir el comando a una llamada de API real usando el cliente de Mercado Libre.
4.  Integrar este conector dentro del `ActionExecutionService` para que sea invocado cuando `action_type` sea `meli_api_call`.

## 10. Criterio para no Romper este Contrato
(Sin cambios)
