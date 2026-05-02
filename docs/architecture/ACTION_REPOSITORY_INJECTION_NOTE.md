# Nota Técnica: Inyección de ActionRepository en CaseClosureService

## 1. Estado Actual
El `CaseClosureService` implementa una inyección opcional de `action_repo` en su constructor:
```python
def __init__(self, repo: OperationalCaseRepository, action_repo=None):
    self.repo = repo
    self.action_repo = action_repo
```
- **Con `action_repo`**: Tras un cierre exitoso, el servicio emite una `ActionProposal` de tipo `CASE_CLOSED`.
- **Sin `action_repo`**: El servicio ignora la emisión de acciones y mantiene el flujo de cierre operativo estándar, garantizando compatibilidad retroactiva.

## 2. Motivo del Diseño
El patrón opcional fue seleccionado para:
- Preservar la compatibilidad con puntos de instanciación existentes.
- Evitar un refactor transversal invasivo en ausencia de un contenedor de dependencias (DI container) o factory centralizada.

## 3. Bloqueo de Wiring Productivo
Actualmente, no existe un punto único de composición de dependencias. Forzar la inyección en todos los puntos de entrada (endpoints, cli, orquestadores) presenta un riesgo elevado de desincronización e inestabilidad en producción. Por tanto, el wiring productivo completo queda **bloqueado**.

## 4. Regla para Evolución Futura
Cuando se implemente una infraestructura de DI/factory global:
1. `CaseClosureService` deberá recibir `ActionExecutionRepository` como dependencia obligatoria en la composición.
2. Los tests de integración del sistema deberán validar que el servicio siempre reciba una instancia no nula de `action_repo` en entornos operativos.
3. El comportamiento opcional debe ser retirado en favor de una configuración explícita.
