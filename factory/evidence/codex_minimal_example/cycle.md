# codex_minimal_example

PLAN
- objetivo: Crear archivo de prueba sin tocar core.
- archivos permitidos: factory/sandbox/test_codex.txt; evidencia requerida en factory/evidence/codex_minimal_example/
- archivos prohibidos: core/; services/
- criterio de cierre: archivo creado; sin errores de ejecucion.
- tests esperados: test -f factory/sandbox/test_codex.txt

WRITE
- factory/sandbox/test_codex.txt ya existia fisicamente al inicio de esta ejecucion y esta versionado con contenido valido.
- se actualiza evidencia reproducible en factory/evidence/codex_minimal_example/ sin modificar core/ ni services/.

VERIFY
- pwd: /opt/smartpyme-factory/repos/SmartPyme
- test -f factory/sandbox/test_codex.txt: exit 0
- ls -la factory/sandbox/test_codex.txt: -rw-r--r-- 1 neoalmasana neoalmasana 22 Apr 27 14:09 factory/sandbox/test_codex.txt
- git ls-files --stage factory/sandbox/test_codex.txt: 100644 7cd80fa32cba359e00865ea293955857a6b10fc4 0 factory/sandbox/test_codex.txt
- test -f factory/evidence/codex_minimal_example/cycle.md: exit 0

INSPECT
- contenido observado: codex_minimal_example

RUN
- test -f factory/sandbox/test_codex.txt: PASS
- git diff --name-only -- core services: sin salida

REPORT
- archivo objetivo creado/existente y verificable.
- no se tocaron core/ ni services/.
- existe evidencia en factory/evidence/codex_minimal_example/.
- hay cambios previos/no relacionados en factory/control/PRIORITY_BOARD.md y otros directorios de evidencia codex_template_* que se dejan intactos.
- se leyo factory/control/NEXT_CYCLE.md; la orden directa del usuario limita esta unidad a codex_minimal_example.

DECISION
- CORRECTO
