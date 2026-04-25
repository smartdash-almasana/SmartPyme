import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.services.comparison_service import ComparisonResult
from app.services.findings_service import FindingsService


def test_generate_findings_creates_finding_with_correct_severity():
    service = FindingsService()
    comparison_results = [
        ComparisonResult(
            entity_id_a="p1",
            entity_id_b="p1",
            entity_type="product",
            attribute="price",
            value_a=100,
            value_b=125,
            difference=25.0,
            difference_pct=25.0,
        )
    ]

    findings = service.generate_findings(comparison_results)

    assert len(findings) == 1
    finding = findings[0]
    assert finding.severity == "CRITICO"
    assert finding.suggested_action == "Revisión inmediata requerida"

def test_generate_findings_maps_severities_correctly():
    service = FindingsService()
    test_cases = [
        (15.0, "ALTO"),
        (8.0, "MEDIO"),
        (2.0, "BAJO"),
        (0.0, None) # No finding should be generated
    ]

    for diff_pct, expected_severity in test_cases:
        comparison_results = [
            ComparisonResult(
                entity_id_a="p1",
                entity_id_b="p1",
                entity_type="product",
                attribute="price",
                value_a=100,
                value_b=100 + diff_pct,
                difference=diff_pct,
                difference_pct=diff_pct,
            )
        ]
        findings = service.generate_findings(comparison_results)
        if expected_severity:
            assert len(findings) == 1
            assert findings[0].severity == expected_severity
        else:
            assert len(findings) == 0
