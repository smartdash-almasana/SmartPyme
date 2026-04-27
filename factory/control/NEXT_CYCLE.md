OBJETIVO CICLO ACTUAL:

Implementar servicio de loop continuo en VM (hermes-factory-pool.service) pero SIN intervención manual.

TAREA:
1. Crear archivo versionado en repo: infra/systemd/hermes-factory-pool.service
2. Definir ExecStart apuntando a hermes_factory_runner.py --loop
3. Documentar en docs/factory cómo instalarlo en VM
4. Validar que el runner pueda operar en modo loop sin errores

RESTRICCIONES:
- No usar skills externos
- No romper flujo actual de GitHub Actions
- No modificar core sin evidencia

CRITERIO DE CIERRE:
- archivo .service creado
- documentación creada
- evidencia en factory/evidence/
- commit consistente

