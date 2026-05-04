# Manual de instrucción de seteo Hermes — SmartPyme Factory

## Estado

Manual operativo de referencia.

## Propósito

Evitar repetir auditorías, discusiones y reconstrucciones sobre cómo setear Hermes para SmartPyme Factory.

Este documento fija el criterio operativo para configurar, verificar y usar Hermes dentro del flujo SmartPyme, sin tocar archivos críticos a ciegas ni volver a deducir lo ya cerrado.

---

# 1. Fuentes de verdad

## Repo SmartPyme

```text
/opt/smartpyme-factory/repos/SmartPyme
```

## Repo Hermes real

```text
/opt/smartpyme-factory/repos/hermes-agent
```

## Configuración runtime activa de Hermes

```text
/home/neoalmasana/.hermes/config.yaml
```

## Variables de entorno runtime Hermes

```text
/home/neoalmasana/.hermes/.env
```

## Launcher Hermes Gateway

```text
/home/neoalmasana/run-hermes-gateway.sh
```

## Regla

No asumir rutas alternativas.
No asumir backups.
No asumir `origin/main` como rama activa.
No asumir configuración desde plantillas si existe runtime real.

---

# 2. Rama de trabajo vigente SmartPyme

La rama activa del ciclo actual es:

```text
factory/ts-006-jobs-sovereign-persistence
```

Antes de cualquier operación:

```bash
cd /opt/smartpyme-factory/repos/SmartPyme
git branch --show-current
git status --short
```

Si la rama no coincide:

```text
BLOCKED_WRONG_BRANCH
```

Si el worktree tiene cambios no explicados:

```text
BLOCKED_DIRTY_WORKTREE
```

---

# 3. Regla de sincronización

GitHub/rama activa es la fuente compartida.

Un solo agente modifica por vez.

Si la VM modifica y pushea:

```bash
cd /opt/smartpyme-factory/repos/SmartPyme
git push origin factory/ts-006-jobs-sovereign-persistence
```

Después el repo local Windows debe hacer pull:

```powershell
cd E:\BuenosPasos\smartbridge\SmartPyme
git pull --ff-only origin factory/ts-006-jobs-sovereign-persistence
git status --short
```

Si GPT/GitHub modifica y pushea, VM y local deben hacer pull.

Sin:

```text
VEREDICTO + RAMA + COMMIT/PUSH + GIT_STATUS
```

no se continúa.

---

# 4. Comandos correctos por entorno

## VM Linux

Usar:

```bash
systemctl status smartpyme-telegram-control.service || true
grep -R "texto" -n archivo1 archivo2 || true
python3
```

No asumir que existe `python`; usar `python3`.

## Windows PowerShell local

No usar:

```text
systemctl
grep
|| true
```

Usar:

```powershell
Select-String -Path archivo1, archivo2 -Pattern "texto"
Remove-Item ruta\archivo.md
git status --short
```

---

# 5. Archivos que no se tocan sin autorización explícita

No modificar sin TaskSpec específico:

```text
/home/neoalmasana/.hermes/config.yaml
/home/neoalmasana/.hermes/.env
/home/neoalmasana/run-hermes-gateway.sh
app/
core/
factory/
docs/product/
.env
MCP
Telegram
```

Plantillas o documentación pueden modificarse si el objetivo está autorizado y el patch es mínimo.

---

# 6. Seteo Hermes: criterio operativo

Hermes debe configurarse desde su runtime real:

```text
/home/neoalmasana/.hermes/config.yaml
```

La plantilla del repo:

```text
hermes/config.template.yaml.example
```

sirve como referencia documental, no como prueba de runtime activo.

Nunca afirmar modelo activo, provider activo o toolsets activos sin leer el runtime real.

---

# 7. Modelo activo

Regla:

Si se menciona un modelo activo, debe usarse el `model_id` exacto leído desde:

```text
/home/neoalmasana/.hermes/config.yaml
```

No inventar nombres.
No traducir nombres.
No normalizar nombres.
No asumir aliases comerciales.

Formato correcto:

```text
MODEL_ID_ACTIVO_LEIDO: <valor exacto del config.yaml>
```

Si no se leyó:

```text
MODEL_ID_ACTIVO_LEIDO: BLOCKED_NOT_READ
```

---

# 8. Ruteo operativo de modelos en SmartPyme Factory

Este ruteo es política SmartPyme, no necesariamente contrato interno oficial de Hermes.

## Hermes / DeepSeek

Uso recomendado:

```text
lectura corta
auditoría documental puntual
verificación de existencia
comparación de pocos documentos
resumen de salida operativa
```

No usar para:

```text
refactor delicado
diseño profundo de arquitectura
cambios masivos
modificaciones de configuración crítica sin revisión
```

## Gemini

Uso recomendado:

```text
auditoría semántica
coherencia arquitectónica
specs y contratos
priorización de backlog
lectura amplia con síntesis
```

## Codex

Uso recomendado:

```text
código Python
tests
diffs verificables
refactor delicado
correcciones con suite automatizada
```

## GPT

Uso recomendado:

```text
coordinación operativa
diseño conceptual
prompts
TaskSpecs
interpretación de salidas
control de continuidad
```

---

# 9. Diferencia entre política SmartPyme y seteo oficial Hermes

## Política SmartPyme

Define cómo SmartPyme decide usar cada agente/modelo en la factoría.

Ejemplo:

```text
Gemini para coherencia arquitectónica.
Codex para código y tests.
GPT para coordinación y prompts.
```

## Seteo oficial Hermes

Está definido por:

```text
repo hermes-agent
AGENTS.md
README.md
GEMINI.md
GPT.md
config real
comandos reales del runtime
```

Regla:

No llamar “oficial Hermes” a una política SmartPyme salvo que esté respaldada por documentación leída del repo Hermes.

---

# 10. Lectura mínima si hay duda sobre Hermes

Cuando haya duda real sobre Hermes, no debatir. Leer.

Comando base:

```bash
cd /opt/smartpyme-factory/repos/hermes-agent
find . -maxdepth 3 -type f | sort | grep -Ei "agent|model|config|provider|governance|routing|README|GEMINI|GPT"
```

Luego leer solo los archivos relevantes.

Si no hay evidencia documental:

```text
BLOCKED_NO_EVIDENCIA_OFICIAL_HERMES
```

---

# 11. Documentos SmartPyme relacionados con Hermes

Autoridad documental detectada:

```text
AGENTS.md = CANONICO raíz
GPT.md = CANONICO
docs/SMARTPYME_OS_ACTUAL.md = CANONICO/OPERATIVO
docs/factory/HERMES_DOCUMENTATION_INDEX.md = CANONICO DOCUMENTAL
docs/factory/FACTORY_CONTRATO_OPERATIVO.md = CANONICO EJECUTIVO
docs/HERMES_SMARTPYME_NO_ALUCINACION.md = OPERATIVO
docs/HERMES_MCP_RUNTIME.md = OPERATIVO
docs/factory/HERMES_SKILLS_INTEGRATION.md = OPERATIVO
docs/factory/HERMES_CODEX_GEMINI_GOVERNANCE.md = CANONICO
factory/ai_governance/hermes_orchestrator_contract.md = LEGACY/DEPRECADO
factory/ai_governance/skills/hermes_smartpyme_factory/SKILL.md = SKILL/PROMPT
prompts/hermes_control_telegram_prompt.md = SKILL/PROMPT
hermes/config.template.yaml.example = CONFIGURACION
```

Documento ejecutivo que manda:

```text
docs/factory/FACTORY_CONTRATO_OPERATIVO.md
```

---

# 12. PATH canónico SmartPyme

Ruta canónica vigente:

```text
/opt/smartpyme-factory/repos/SmartPyme
```

Ruta vieja incorrecta:

```text
/home/neoalmasana/smartpyme-factory/repos/SmartPyme
```

Verificación:

```bash
cd /opt/smartpyme-factory/repos/SmartPyme
grep -R "/home/neoalmasana/smartpyme-factory/repos/SmartPyme" -n prompts/hermes_control_telegram_prompt.md hermes/config.template.yaml.example || true
```

Si aparece, patch mínimo.

Cambio cerrado en la rama:

```text
b5aa056 fix hermes template canonical SmartPyme path
```

---

# 13. Servicio legacy Telegram Control

Servicio detectado:

```text
smartpyme-telegram-control.service
```

Estado detectado:

```text
Loaded: loaded
Active: inactive (dead)
Disabled
```

Regla:

Si existe pero está inactive/dead y disabled, no ejecutar acción destructiva.

No hacer:

```bash
systemctl stop ...
systemctl disable ...
rm ...
```

sin TaskSpec explícita.

---

# 14. Scripts legacy cerrados

Archivo eliminado del repo:

```text
scripts/install_telegram_control_service.sh
```

Motivo:

Apuntaba a script inexistente:

```text
scripts/telegram_factory_control.py
```

Commit:

```text
d4d79810a4545d6438d216c2812a9ba673a6ec4a
```

---

# 15. Archivo legacy documental creado

Archivo creado:

```text
docs/ARCHIVO_LEGACY_HERMES_FACTORY_UTIL.md
```

Commit:

```text
bb8729ecdc4315b4a4e0f5e5a21bdb3860a24f19
```

Función:

Registrar utilidad histórica y estado legacy de componentes Hermes Factory sin eliminar evidencia ni tocar históricos.

---

# 16. Regla sobre untracked locales

Si en local Windows aparece:

```text
?? docs/ARCHIVO_LEGACY_HERMES_FACTORY_UTIL.md
```

pero el archivo ya viene trackeado desde GitHub, debe eliminarse el untracked local antes del pull:

```powershell
Remove-Item docs\ARCHIVO_LEGACY_HERMES_FACTORY_UTIL.md
git pull --ff-only origin factory/ts-006-jobs-sovereign-persistence
```

Si aparece:

```text
?? docs/product/smartpyme_capa_02_activacion_conocimiento_extendida.md
```

no tocar sin autorización, porque pertenece a producto/documentación conceptual y está fuera del frente Hermes.

---

# 17. Formato obligatorio para salidas Hermes/Kiro/Codex/Gemini

Toda ejecución debe devolver:

```text
VEREDICTO:
RAMA:
ARCHIVOS_MODIFICADOS:
SUMMARY_DIFF:
LIMITES:
GIT_STATUS:
NEXT_RECOMMENDED_STEP:
```

Si hay commit/push:

```text
COMMIT:
PUSH:
```

Si se leyó modelo activo:

```text
MODEL_ID_ACTIVO_LEIDO:
```

---

# 18. Formato para auditoría

```text
VEREDICTO:
ARCHIVOS_ENCONTRADOS:
CONTRATOS_DETECTADOS:
RIESGOS:
BLOQUEOS:
PROPUESTA_MINIMA:
NEXT_STEP:
```

---

# 19. Formato para implementación

```text
VEREDICTO:
SUMMARY_DIFF:
ARCHIVOS_MODIFICADOS:
TEST_RESULT:
LIMITES:
NEXT_RECOMMENDED_STEP:
```

---

# 20. Formato para TaskSpec

```text
TASKSPEC:
MODO:
REPO:
RAMA_ESPERADA:
OBJETIVO:
ARCHIVOS_PERMITIDOS:
ARCHIVOS_SOLO_LECTURA:
PROHIBIDO:
CONTRATO_ESPERADO:
TESTS:
COMANDOS_DE_VERIFICACION:
SALIDA_OBLIGATORIA:
```

---

# 21. Regla de patch mínimo

Todo cambio debe cumplir:

```text
una intención
un archivo o el mínimo necesario
diff legible
sin reordenamientos cosméticos
sin tocar archivos fuera de alcance
sin modificar runtime salvo autorización explícita
```

Si el cambio requiere más alcance:

```text
BLOCKED_SCOPE_EXPANSION
```

---

# 22. Flujo estándar para modificar documentación Hermes en SmartPyme

```bash
cd /opt/smartpyme-factory/repos/SmartPyme
git branch --show-current
git status --short
```

Si rama y estado están correctos:

1. Modificar archivo permitido.
2. Ver diff.
3. Verificar grep/test si aplica.
4. Commit.
5. Push.
6. Confirmar status limpio.

Comandos base:

```bash
git diff -- <archivo>
git status --short
git add <archivo>
git commit -m "mensaje claro"
git push origin factory/ts-006-jobs-sovereign-persistence
git status --short
```

---

# 23. Flujo estándar de pull VM

```bash
cd /opt/smartpyme-factory/repos/SmartPyme
git branch --show-current
git status --short
git pull --ff-only origin factory/ts-006-jobs-sovereign-persistence
git status --short
```

---

# 24. Flujo estándar de pull local Windows

```powershell
cd E:\BuenosPasos\smartbridge\SmartPyme
git branch --show-current
git status --short
git pull --ff-only origin factory/ts-006-jobs-sovereign-persistence
git status --short
```

---

# 25. Bloqueos estándar

## Ruta dudosa

```text
BLOCKED_PATH_UNCERTAINTY
```

## Rama incorrecta

```text
BLOCKED_WRONG_BRANCH
```

## Worktree sucio

```text
BLOCKED_DIRTY_WORKTREE
```

## Falta evidencia oficial Hermes

```text
BLOCKED_NO_EVIDENCIA_OFICIAL_HERMES
```

## Falta lectura de config real

```text
BLOCKED_CONFIG_NOT_READ
```

## Alcance excesivo

```text
BLOCKED_SCOPE_EXPANSION
```

## Intento de tocar runtime sin autorización

```text
BLOCKED_RUNTIME_CHANGE_UNAUTHORIZED
```

---

# 26. Principios SmartPyme que Hermes debe respetar

```text
SmartPyme no decide; propone.
El dueño decide.
Sin evidencia trazable no hay diagnóstico.
Sin comparación entre fuentes no hay hallazgo fuerte.
Sin diferencia cuantificada no hay hallazgo accionable.
El dolor del dueño no es diagnóstico.
La hipótesis no afirma: investiga.
No se ejecuta acción sin DecisionRecord/autorización.
No hardcodear semántica PyME en core.
La semántica de dominio vive en catálogos, paquetes de dominio o tanques de conocimiento.
```

---

# 27. Checklist rápido antes de tocar Hermes

Antes de cualquier cambio relacionado con Hermes:

```text
[ ] Estoy en la VM correcta.
[ ] Estoy en /opt/smartpyme-factory/repos/SmartPyme o /opt/smartpyme-factory/repos/hermes-agent según corresponda.
[ ] Verifiqué rama.
[ ] Verifiqué git status.
[ ] Sé si estoy tocando documentación, plantilla o runtime.
[ ] No estoy tocando ~/.hermes/config.yaml sin autorización.
[ ] No estoy inventando modelo activo.
[ ] El patch es mínimo.
[ ] La salida final tendrá VEREDICTO + RAMA + GIT_STATUS.
```

---

# 28. Regla final

Este manual existe para no volver a empezar desde cero.

Si surge duda sobre Hermes:

```text
leer evidencia → interpretar → patch mínimo → verificar → commit/push → sincronizar
```

No debatir memoria.
No deducir capacidades.
No repetir auditorías completas si el cierre ya existe.

SmartPyme Factory avanza con evidencia, rama correcta, diff mínimo y cierre auditable.

