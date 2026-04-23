---
name: build_topology_catalog
description: Construye y gobierna la topologia de excavacion cantera->capa para la factoria SmartPyme.
---

# Skill: build_topology_catalog

## Proposito
Construir y mantener la topologia rectora de la factoria para gobernar excavacion de canteras por capa destino del kernel SmartPyme.

## Cuando usar
- Antes de iniciar una nueva tanda de excavacion.
- Cuando se incorpora una cantera nueva.
- Cuando cambia el orden oficial de ensamblaje por capas.
- Cuando hay exceso de `blocked` por deriva de rutas o alcance.

## Cuando no usar
- Para implementar logica de negocio de `app/core`.
- Para ejecutar portados de slices.
- Para cambiar contratos productivos fuera del catalogo de topologia.

## Entradas obligatorias
- Archivo rector: `docs/topologia.txt`.
- Catalogo actual: `factory/topology_catalog.json`.
- Manifest activo: `factory/canteras_manifest.json`.

## Salida esperada
- Catalogo de capas destino del kernel con archivos objetivo por capa.
- Catalogo de canteras con `path_prefix`, prioridad y capas posibles.
- Orden oficial de ensamblaje por capas.
- Reglas de gobierno aplicables a `run_factory`, `run_codex_worker` y `continuous_factory`.

## Reglas obligatorias
- Fail-closed: si una capa no existe en catalogo, no excavar.
- Fail-closed: si una cantera no esta habilitada para la capa objetivo, no excavar.
- No habilitar rutas fuera del repo destino.
- No proponer destino `src/` ni contratos fuera de `app/core` y `tests/core`.
- Mantener `clarification` como capa consolidada base.
- Priorizar `reconciliation` como proxima capa posterior a contratos/modelos.

## Criterio de bloqueo
- Falta de capa objetivo en catalogo.
- Manifest con modulo fuera de topologia oficial.
- Hallazgo con `modulo_objetivo` inexistente o sin mapping valido de rutas.
- Cantera sin mapeo claro a la capa objetivo.

## Protocolo minimo de uso
1. Leer `docs/topologia.txt`.
2. Actualizar `factory/topology_catalog.json`.
3. Validar que `factory/canteras_manifest.json` solo use capas conocidas.
4. Ejecutar `factory/run_factory.py` y `factory/continuous_factory.py` con el catalogo aplicado.
5. Verificar que `blocked` baje por invalidaciones tempranas.

## Ejemplo minimo
Objetivo: excavar `reconciliation`.

1. Confirmar en catalogo:
- capa `reconciliation` existe en `core_layers`
- canteras habilitadas incluyen `reconciliation`

2. Correr:
```powershell
python -m factory.run_factory --modo execute_ready --modulo reconciliation --rutas-fuente E:\BuenosPasos\smartcounter --repo-destino E:\BuenosPasos\smartbridge\SmartPyme
```

Resultado esperado:
- si cantera y capa son compatibles: genera hallazgo y avanza a `in_progress` o `done`
- si no son compatibles: bloqueo inmediato con error `CANTERA_NO_HABILITADA_PARA_CAPA`
