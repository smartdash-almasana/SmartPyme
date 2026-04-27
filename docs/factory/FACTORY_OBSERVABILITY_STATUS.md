# FACTORY OBSERVABILITY STATUS

Estado: CANONICO v1

Objetivo: dejar un registro observable desde GitHub para responder si la factoria esta viva, bloqueada o sin actividad reciente.

Archivo vivo obligatorio:
- factory/control/FACTORY_STATUS.md

Contenido minimo:
- updated_at
- service_expected: smartpyme-sfma.service
- last_cycle_started_at
- last_cycle_finished_at
- last_cycle_result: CORRECTO | BLOCKED | NO_VALIDADO | RUNNING | IDLE | UNKNOWN
- last_commit
- last_evidence_path
- last_error
- next_action

Regla:
Cada ciclo debe actualizar FACTORY_STATUS.md. Si el ciclo se bloquea, debe quedar registrado el motivo. Si no hay cambios, debe registrar IDLE. Si hay error, debe registrar BLOCKED o NO_VALIDADO.

Auditoria externa:
ChatGPT puede auditar FACTORY_STATUS.md desde GitHub sin acceder a la VM. Si FACTORY_STATUS.md esta viejo, se considera posible bloqueo del loop o falta de push.

Criterios de aceptacion:
- existe FACTORY_STATUS.md
- se actualiza en cada ciclo
- contiene evidencia o error
- permite responder estado actual sin SSH
