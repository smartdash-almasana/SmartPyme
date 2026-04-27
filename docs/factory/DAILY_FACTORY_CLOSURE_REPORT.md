# DAILY FACTORY CLOSURE REPORT

Estado: CANONICO v1

Objetivo: cerrar cada dia operativo de SmartPyme Factory con una auditoria global de ciclos, evidencia, tests, commits, riesgos y prioridades.

Horario canonico: 00:00 America/Argentina/Buenos_Aires.

Flujo:
1. leer factory/evidence del dia
2. leer git log del dia
3. leer PRIORITY_BOARD y TECH_SPEC_QUEUE
4. consolidar QA global
5. generar reporte local
6. entregar por canal externo si existe MCP disponible

Output local obligatorio:
- factory/daily_reports/YYYY-MM-DD/daily_summary.md
- factory/daily_reports/YYYY-MM-DD/git_log.txt
- factory/daily_reports/YYYY-MM-DD/qa_global.md
- factory/daily_reports/YYYY-MM-DD/priority_snapshot.md
- factory/daily_reports/YYYY-MM-DD/delivery_status.md

Contenido minimo:
- fecha operativa
- cantidad de ciclos detectados
- ciclos CORRECTO, BLOCKED y NO_VALIDADO
- commits del dia
- archivos modificados
- tests ejecutados
- riesgos detectados
- estado anti-deriva
- prioridades para el siguiente dia

Canales de entrega:
1. email al owner
2. Google Drive en carpeta SmartPyme Factory Reports
3. Notion MCP si existe conector configurado

Fallback obligatorio: si no hay canal externo, el reporte local queda como fuente de verdad y se registra DELIVERY_BLOCKED_EXTERNAL_CONNECTOR.

Criterios de aceptacion:
- reporte diario generado sin intervencion humana
- evidencia local persistida
- canal externo registrado como SENT o BLOCKED
- prioridad del dia siguiente actualizada
