# Archivo Legacy Útil — Hermes Factory

## Estado

DOCUMENTO DE CONSOLIDACIÓN LEGACY.  
Este archivo concentra aprendizaje útil de artefactos Hermes/Factory que ya no deben gobernar el runtime vigente.

---

## Regla de lectura

Este archivo es histórico y explicativo.  
No define runtime activo.

Para runtime vigente, leer primero:

```text
docs/factory/FACTORY_CONTRATO_OPERATIVO.md
docs/factory/RUNTIME_VIGENTE.md
docs/SMARTPYME_OS_ACTUAL.md
docs/factory/HERMES_DOCUMENTATION_INDEX.md
```

---

## Runtime vigente

La auditoría vigente establece:

```text
Hermes Gateway externo = runtime conversacional
factory/hermes_control_cli.py = adaptador interno permitido
MCP stdio = frontera de herramientas
SmartPyme core = fuente de verdad operativa
```

Hermes no debe entrar al core por atajos.  
Hermes entra por MCP, con herramientas limitadas y contratos explícitos.

---

## Artefactos legacy ya eliminados o ausentes

Estos artefactos fueron referenciados históricamente, pero no existen actualmente en el worktree operativo:

```text
scripts/hermes_factory_runner.py
scripts/telegram_factory_control.py
run_sfma_cycle.sh
```

Estado:

```text
LEGACY_REMOVED_OR_ABSENT
```

Aprendizaje útil:

- existió una etapa de runners caseros;
- esos runners confundían runtime, factoría y control Telegram;
- el camino vigente separa Hermes Gateway, MCP, adaptador interno y core SmartPyme;
- ningún agente debe reactivarlos ni regenerarlos.

---

## Instalador legacy eliminado

Archivo eliminado por consolidación:

```text
scripts/install_telegram_control_service.sh
```

Motivo:

- instalaba `smartpyme-telegram-control.service`;
- el `ExecStart` apuntaba a `scripts/telegram_factory_control.py`;
- ese archivo ya no existe;
- si se ejecutaba en VM podía instalar un servicio roto o reiniciar en loop.

Reemplazo vigente:

```text
Hermes Gateway externo
/home/neoalmasana/run-hermes-gateway.sh
/home/neoalmasana/.hermes/config.yaml
```

Acción operativa pendiente en VM:

```bash
systemctl status smartpyme-telegram-control.service || true
```

Si existe y está activo, detener/deshabilitar con task explícita.

---

## Artefactos conservados como históricos

Estos archivos no deben gobernar runtime por sí mismos, pero pueden conservar aprendizaje histórico:

```text
factory/ai_governance/hermes_orchestrator_contract.md
factory/ai_governance/tasks/0000_legacy_isolation_001.yaml
factory/ai_governance/HERMES_FACTORY_LOOP.md
docs/factory/HERMES_PROFESSIONAL_RESET_PLAN.md
factory/reports/kernel_total_audit_001.md
factory/evidence/**
```

Criterio:

```text
si es evidencia histórica, no se borra;
si contradice runtime vigente, se subordina al contrato operativo actual;
si un agente lo lee aislado, debe verificar contra HERMES_DOCUMENTATION_INDEX.md.
```

---

## Artefactos experimentales marcados

Estos archivos fueron detectados como no runtime vigente:

```text
factory/local_mcp_server.py
factory/multiagent_runner.py
```

Estado:

```text
EXPERIMENTAL_NOT_RUNTIME
```

Regla:

- no deben ejecutarse como runtime de producción;
- no deben usarse para deducir arquitectura vigente;
- cualquier reutilización futura requiere TaskSpec explícita, tests y aprobación.

---

## Referencias legacy remanentes permitidas

```text
factory/hermes_control_cli.py → LEGACY_PATTERNS
```

Esa referencia es válida porque sirve para detectar procesos o patrones legacy activos.  
No es una reactivación del legacy.

---

## Riesgos detectados

1. **Servicio systemd roto**  
   Puede existir `smartpyme-telegram-control.service` instalado en VM, apuntando a un archivo eliminado.

2. **Reportes históricos confusos**  
   Algunos reportes antiguos nombran runners caseros como “actuales”. Deben tratarse como evidencia histórica, no como fuente vigente.

3. **Reactivación accidental**  
   Un agente que lea solo archivos históricos puede intentar reconstruir runners legacy. Esto queda prohibido.

---

## Regla final

```text
Borrar runtime muerto.
Conservar aprendizaje útil.
No borrar evidencia histórica.
No reactivar runners caseros.
```

Hermes Factory queda subordinado a contratos vigentes, MCP y evidencia trazable.
