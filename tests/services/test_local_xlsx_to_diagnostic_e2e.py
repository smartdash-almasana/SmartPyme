from __future__ import annotations

from pathlib import Path

from openpyxl import Workbook

from app.repositories.curated_evidence_repository import CuratedEvidenceRepositoryBackend
from app.services.basic_operational_diagnostic_service import BasicOperationalDiagnosticService
from app.services.local_xlsx_diagnostic_ingestion_service import (
    LocalXlsxDiagnosticIngestionService,
)


def _build_xlsx(path: Path) -> None:
    wb = Workbook()
    ws = wb.active
    ws.append(
        [
            "evidence_id",
            "precio_venta",
            "costo_unitario",
            "stock_actual",
            "ventas_periodo",
            "compras_periodo",
            "precio_lista",
            "costo_actual",
        ]
    )
    ws.append(["ev-venta-bajo-costo", 10, 20, 5, 2, 1, 20, 20])
    ws.append(["ev-rentabilidad-nula", 50, 50, 3, 1, 1, 60, 50])
    ws.append(["ev-stock-inmovilizado", 100, 60, 15, 0, 2, 130, 60])
    ws.append(["ev-descuento-excesivo", 60, 30, 2, 2, 1, 100, 30])
    wb.save(path)
    wb.close()


def test_local_xlsx_end_to_end_generates_required_findings(tmp_path: Path) -> None:
    db_path = tmp_path / "diag_xlsx.db"
    xlsx_path = tmp_path / "smoke.xlsx"
    _build_xlsx(xlsx_path)

    repo = CuratedEvidenceRepositoryBackend(db_path=db_path)
    ingest = LocalXlsxDiagnosticIngestionService(repository=repo)

    imported = ingest.ingest_file(tenant_id="tenant-xlsx", file_path=xlsx_path)
    assert imported == 4

    service = BasicOperationalDiagnosticService(repository=repo)
    report = service.build_report("tenant-xlsx")
    finding_types = {finding["finding_type"] for finding in report["findings"]}

    assert report["evidence_count"] == 4
    assert "VENTA_BAJO_COSTO" in finding_types
    assert "RENTABILIDAD_NULA" in finding_types
    assert "STOCK_INMOVILIZADO" in finding_types
    assert "DESCUENTO_EXCESIVO" in finding_types
