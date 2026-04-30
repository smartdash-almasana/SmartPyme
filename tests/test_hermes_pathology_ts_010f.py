from app.contracts.formula_contract import FormulaInput
from app.factory.agents.formula_calculation_agent import FormulaCalculationAgent
from app.factory.agents.pathology_auditor_agent import PathologyAuditorAgent
from app.mcp.tools.owner_status_tool import get_owner_status
from app.mcp.tools.pathology_explanation_tool import (
    get_pathology_finding,
    get_pathology_findings,
    get_pathology_status_for_owner,
)


def _seed_active_pathology(tmp_path):
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
    PathologyAuditorAgent("pyme_A", formula_db, pathology_db).audit_formula_result(
        "fr1",
        pathology_finding_id="pf1",
    )
    return formula_db, pathology_db


def test_hermes_pathology_tool_reads_and_explains(tmp_path):
    _, pathology_db = _seed_active_pathology(tmp_path)

    import app.mcp.tools.pathology_explanation_tool as pathology_tool
    pathology_tool.Path = lambda p: pathology_db

    findings = get_pathology_findings("pyme_A")
    status = get_pathology_status_for_owner("pyme_A")

    assert len(findings) == 1
    assert findings[0]["status"] == "ACTIVE"
    assert status["count"] == 1
    assert "Alerta de negocio" in status["messages"][0]


def test_hermes_pathology_tool_hides_cross_client(tmp_path):
    _, pathology_db = _seed_active_pathology(tmp_path)

    import app.mcp.tools.pathology_explanation_tool as pathology_tool
    pathology_tool.Path = lambda p: pathology_db

    assert get_pathology_finding("pyme_B", "pf1") is None
    assert get_pathology_findings("pyme_B") == []


def test_owner_status_includes_pathologies(tmp_path):
    formula_db, pathology_db = _seed_active_pathology(tmp_path)

    import app.mcp.tools.jobs_read_tool as jobs_tool
    import app.mcp.tools.formula_results_tool as formula_tool
    import app.mcp.tools.pathology_explanation_tool as pathology_tool

    jobs_tool.Path = lambda p: tmp_path / "empty.db"
    formula_tool.Path = lambda p: formula_db
    pathology_tool.Path = lambda p: pathology_db

    status = get_owner_status("pyme_A")

    assert status["pathology_findings_count"] == 1
    assert len(status["pathology_findings"]) == 1
    assert any("Alerta de negocio" in msg for msg in status["messages"])
