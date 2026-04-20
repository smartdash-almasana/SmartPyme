# SKILL: route_guard

## NOMBRE DEL SKILL
route_guard

## PROPÓSITO
Validar que las rutas de destino propuestas en un Hallazgo pertenezcan exclusivamente al perímetro autorizado de SmartPyme y al flujo técnico correspondiente.

## CUÁNDO USARLO
- Al definir la `PROPUESTA_DE_PORTADO` en el redactado del Hallazgo.
- Para prevenir la modificación accidental de código fuera del alcance (ej: bridge, cantera).

## CUÁNDO NO USARLO
- Para validar rutas de lectura en cantera.

## INPUT ESPERADO
- Ruta destino propuesta (absoluta o relativa al repo).
- `modulo_objetivo` (para validar coherencia de subdirectorio).

## OUTPUT ESPERADO
- Veredicto binario [VALIDA | RECHAZADA] con justificación de seguridad.

## REGLAS OBLIGATORIAS
1. La ruta DEBE estar contenida dentro de: `E:\BuenosPasos\smartbridge\SmartPyme`.
2. Rutas autorizadas incluyen: `app/...`, `tests/...`, `factory/hallazgos/...`, `core/...`, `catalog/...`.
3. PROHIBIDO modificar archivos en la raíz del bridge (`app/services`, `app/api/routes` de la raíz del proyecto).
4. El archivo propuesto debe tener sentido dentro del `modulo_objetivo` (ej: no poner modelos de 'entities' en la carpeta de 'ingesta').

## CRITERIO DE BLOQUEO
- Si la ruta cae fuera del directorio raíz de `SmartPyme`.
- Si la ruta apunta a archivos sensibles de configuración de agentes o sistema (.gemini, .agent).

## EJEMPLO MÍNIMO DE USO
Input: Destino `E:\BuenosPasos\smartbridge\SmartPyme\app\core\clarification\models.py`
Output: VALIDA - Dentro de SmartPyme y alineado con módulo objetivo.

## RELACIÓN CON LOS DEMÁS SKILLS
Actúa como filtro de seguridad final para `hallazgo_writer` antes de emitir la propuesta oficial.
