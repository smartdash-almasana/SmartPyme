# XLSX Local Diagnostic Smoke

## Flujo real confirmado

XLSX local -> `LocalXlsxDiagnosticIngestionService.ingest_file()` -> `CuratedEvidenceRecord` en `CuratedEvidenceRepositoryBackend` -> `BasicOperationalDiagnosticService.build_report()` -> findings.

Este flujo es local y controlado, sin BEM ni routers.

## Comando de smoke

```bash
pytest tests/services/test_local_xlsx_to_diagnostic_e2e.py -q -vv
```

## Columnas requeridas

- `evidence_id`
- `precio_venta`
- `costo_unitario`
- `stock_actual`
- `ventas_periodo`
- `compras_periodo`
- `precio_lista`
- `costo_actual`

## Findings esperados

- `VENTA_BAJO_COSTO`
- `RENTABILIDAD_NULA`
- `STOCK_INMOVILIZADO`
- `DESCUENTO_EXCESIVO`

## Archivos involucrados

- `app/services/local_xlsx_diagnostic_ingestion_service.py`
- `tests/services/test_local_xlsx_to_diagnostic_e2e.py`
- `app/repositories/curated_evidence_repository.py`
- `app/services/basic_operational_diagnostic_service.py`

## Limites actuales

- Soporta solo `.xlsx`.
- Usa la hoja activa del workbook.
- Requiere columnas obligatorias exactas.
- Fail-closed en extensión, columnas y tipos numéricos.
- No expone endpoint HTTP dedicado para este camino.

## Aclaracion de alcance

Este smoke no reemplaza BEM. Es un camino local controlado para validación técnica mínima de XLSX hacia diagnóstico.
