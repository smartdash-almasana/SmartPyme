# codex_minimal_example

PLAN
- objetivo: Crear archivo de prueba sin tocar core.
- archivos permitidos: factory/sandbox/test_codex.txt; factory/evidence/codex_minimal_example/
- archivos prohibidos: core/; services/
- criterio de cierre: archivo creado; sin errores de ejecucion.
- tests esperados: test -f factory/sandbox/test_codex.txt

WRITE
- creado factory/sandbox/test_codex.txt
- creada evidencia en factory/evidence/codex_minimal_example/

DECISION
- CORRECTO

VERIFY
- pwd: /opt/smartpyme-factory/repos/SmartPyme
- git status --short: muestra cambios no trackeados de esta tarea y un directorio de evidencia previo no relacionado.
- test -f factory/sandbox/test_codex.txt: exit 0
- ls -la factory/sandbox/test_codex.txt: -rw-r--r-- 1 neoalmasana neoalmasana 22 Apr 27 14:03 factory/sandbox/test_codex.txt

INSPECT
- contenido: codex_minimal_example

RUN
- test -f factory/sandbox/test_codex.txt: PASS
