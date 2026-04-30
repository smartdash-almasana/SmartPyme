from app.contracts.formula_contract import FormulaInput
from app.contracts.pathology_contract import PathologyStatus
from app.factory.agents.formula_calculation_agent import FormulaCalculationAgent
from app.factory.agents.pathology_auditor_agent import PathologyAuditorAgent
from app.repositories.pathology_repository import PathologyRepository


def test_auditor_detects_and_persists_negative_margin(tmp_path):
    formula_db = tmp_path / "formula_results.db"
    pathology_db = tmp_path / "pathologies.db"

    FormulaCalculationAgent("pyme_A", formula_db).calculate_and_persist(
        "margen_bruto",
        [
            FormulaInput(name="ventas", value=1000, source_refs=["ventas:1"]),
            FormulaInput(name="costos", value=1200, source_refs=["costos:1"]),
        ],
        result_id="fr1",
    )

    finding = PathologyAuditorAgent("pyme_A", formula_db, pathology_db).audit_formula_result(
        "fr1",
        pathology_finding_id="pf1",
    )

    assert finding is not None
    assert finding.status == PathologyStatus.ACTIVE

    persisted = PathologyRepository("pyme_A", pathology_db).get("pf1")
    assert persisted is not None
    assert persisted.status == PathologyStatus.ACTIVE
    assert persisted.source_refs == ["ventas:1", "costos:1"]


def test_auditor_persists_not_detected(tmp_path):
    formula_db = tmp_path / "formula_results.db"
    pathology_db = tmp_path / "pathologies.db"

    FormulaCalculationAgent("pyme_A", formula_db).calculate_and_persist(
        "margen_bruto",
        [
            FormulaInput(name="ventas", value=1000),
            FormulaInput(name="costos", value=600),
        ],
        result_id="fr2",
    )

    finding = PathologyAuditorAgent("pyme_A", formula_db, pathology_db).audit_formula_result(
        "fr2",
        pathology_finding_id="pf2",
    )

    assert finding is not None
    assert finding.status == PathologyStatus.NOT_DETECTED

    persisted = PathologyRepository("pyme_A", pathology_db).get("pf2")
    assert persisted is not None
    assert persisted.status == PathologyStatus.NOT_DETECTED


def test_auditor_returns_none_when_formula_result_missing(tmp_path):
    finding = PathologyAuditorAgent(
        "pyme_A",
        tmp_path / "formula_results.db",
        tmp_path / "pathologies.db",
    ).audit_formula_result("missing")

    assert finding is None


def test_auditor_isolation(tmp_path):
    formula_db = tmp_path / "formula_results.db"
    pathology_db = tmp_path / "pathologies.db"

    FormulaCalculationAgent("pyme_A", formula_db).calculate_and_persist(
        "margen_bruto",
        [
            FormulaInput(name="ventas", value=1000),
            FormulaInput(name="costos", value=1200),
        ],
        result_id="fr-shared",
    )

    finding = PathologyAuditorAgent("pyme_B", formula_db, pathology_db).audit_formula_result(
        "fr-shared",
        pathology_finding_id="pf-shared",
    )

    assert finding is None
    assert PathologyRepository("pyme_B", pathology_db).get("pf-shared") is None
