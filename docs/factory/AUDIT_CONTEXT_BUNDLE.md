# AUDIT CONTEXT BUNDLE

Estado: CANONICO v1

Objetivo: generar un contexto tecnico compacto para auditoria humana sin modificar el
estado de la factoria.

Script:

```bash
python scripts/build_audit_context.py
```

Salida a archivo:

```bash
python scripts/build_audit_context.py --output /tmp/smartpyme_audit_context.txt
```

Contenido incluido:
- gate actual desde `factory/control/AUDIT_GATE.md`, si existe;
- estado de factoria desde `factory/control/FACTORY_STATUS.md`, si existe;
- ultima tarea desde `factory/control/NEXT_CYCLE.md`, si existe;
- hasta 5 archivos recientes en `factory/evidence`;
- hasta 5 archivos recientes en `factory/bugs`;
- `git status --short`;
- `git log --oneline -5`.

Reglas operativas:
- por defecto solo imprime por stdout;
- solo escribe en disco cuando se usa `--output`;
- tolera archivos y directorios ausentes;
- no cambia gate, tareas, evidencia, bugs ni commits;
- el TXT/MD generado puede pegarse en ChatGPT o enviarse por Telegram para decidir
  `APPROVED`, `REJECTED` o `BLOCKED`.

Criterio de uso:
Ejecutar antes de una decision humana cuando no se quiera revisar la VM manualmente.
Si el bundle muestra archivos ausentes, git con errores o estado viejo, la decision
recomendada es `BLOCKED` hasta obtener evidencia actualizada.
