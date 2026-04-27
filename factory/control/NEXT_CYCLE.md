OBJETIVO CICLO ACTUAL:

Implementar core-reconciliacion-v1.

TAREA:
1. Implementar primer motor deterministico de reconciliacion entre dos fuentes CSV.
2. Crear o modificar solo los archivos minimos necesarios para esta unidad.
3. Agregar tests especificos para validar una diferencia numerica por entidad.
4. Generar evidencia en factory/evidence/core-reconciliacion-v1/ o en el directorio de evidencia del runner.
5. Cerrar con git status, git diff, tests y decision verificable.

ALCANCE AUTORIZADO:
- Se autoriza tocar codigo de core o modulo equivalente si es necesario para implementar la reconciliacion.
- Se autoriza crear tests especificos.
- Se autoriza definir estructuras minimas de salida tipo hallazgo.

RESTRICCIONES:
- No usar IA para logica core.
- No hacer refactor global.
- No tocar integraciones externas.
- No mezclar con Telegram, reporting ni systemd.
- Mantener salida de negocio con entidad, diferencia cuantificada y fuentes.

CRITERIO DE CIERRE:
- input: 2 CSV.
- output: diferencias por entidad.
- al menos un test pasa.
- no hay cambios fuera del alcance.
- evidencia real guardada.
