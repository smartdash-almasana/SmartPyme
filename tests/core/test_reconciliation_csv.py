import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.core.reconciliation.service import reconcile_csv_sources


def test_reconcile_csv_sources_returns_hallazgo_for_numeric_difference(tmp_path):
    source_a = tmp_path / "source_a.csv"
    source_b = tmp_path / "source_b.csv"
    source_a.write_text(
        "order_id,amount,status\n"
        "o-1,100.00,paid\n"
        "o-2,50.00,paid\n",
        encoding="utf-8",
    )
    source_b.write_text(
        "order_id,amount,status\n"
        "o-1,125.50,paid\n"
        "o-2,50.00,paid\n",
        encoding="utf-8",
    )

    hallazgos = reconcile_csv_sources(
        source_a,
        source_b,
        key_field="order_id",
        entity_type="order",
    )

    assert len(hallazgos) == 1
    hallazgo = hallazgos[0]
    assert hallazgo.tipo == "mismatch_valor"
    assert hallazgo.entidad_id == "o-1"
    assert hallazgo.entidad_tipo == "order"
    assert hallazgo.diferencia_cuantificada == 25.5
    assert hallazgo.evidencia == {
        "field": "amount",
        "value_a": 100,
        "value_b": 125.5,
        "delta": 25.5,
    }
