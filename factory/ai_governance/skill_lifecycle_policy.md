# Skill Lifecycle Policy — SmartPyme Factory

## Principio

En Hermes, un skill es memoria procedural: describe como hacer algo. No es memoria factual ni verdad del negocio.

SmartPyme usa skills para rutinas operativas de factoria, no para guardar hechos de negocio.

## Regla

Los skills deben evolucionar junto con el codigo.

Un skill se actualiza cuando:

- el flujo real cambio;
- una tarea repetida encontro un camino mejor;
- un error se repitio;
- un Auditor detecto una brecha;
- el codigo agrego una capa nueva;
- un spec cambio;
- una rutina manual debe volverse automatica.

## No guardar en skills

- datos de tenants;
- secretos;
- resultados de una sola corrida;
- memoria conversacional;
- supuestos no validados.

## Promocion de aprendizaje

```text
evidencia -> hallazgo de mejora -> Builder ajusta skill -> Auditor valida -> commit
```

Hermes no debe reescribir skills por intuicion. Debe hacerlo por hallazgo o instruccion explicita.

## Skills base de SmartPyme Factory

- hermes_smartpyme_factory: ciclo principal.
- factory_builder: ejecucion de cambios.
- factory_auditor: validacion sin escritura.
- codex_builder: puente futuro para Codex MCP/CLI.
- skill_maintainer: mejora controlada de skills.

## Criterio de calidad

Un skill bueno debe ser:

- especifico;
- corto en flujo comun;
- con reglas de bloqueo;
- con rutas claras;
- con evidencia requerida;
- facil de auditar.

## Riesgo

Un skill obsoleto se vuelve deuda tecnica. Si contradice specs o codigo real, debe actualizarse o bloquearse.
