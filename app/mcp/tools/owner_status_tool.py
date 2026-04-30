from app.mcp.tools.formula_results_tool import get_formula_results, interpret_formula_result
from app.mcp.tools.hermes_interpreter import interpret_findings
from app.mcp.tools.jobs_read_tool import get_findings, get_jobs


def get_owner_status(cliente_id: str) -> dict:
    jobs = get_jobs(cliente_id)
    findings = get_findings(cliente_id)
    formula_results = get_formula_results(cliente_id)

    finding_messages = interpret_findings(findings)
    formula_messages = [interpret_formula_result(result) for result in formula_results]
    messages = finding_messages + formula_messages

    return {
        "cliente_id": cliente_id,
        "jobs_count": len(jobs),
        "findings_count": len(findings),
        "formula_results_count": len(formula_results),
        "jobs": jobs,
        "findings": findings,
        "formula_results": formula_results,
        "messages": messages,
    }
