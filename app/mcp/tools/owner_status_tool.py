from app.mcp.tools.hermes_interpreter import interpret_findings
from app.mcp.tools.jobs_read_tool import get_findings, get_jobs


def get_owner_status(cliente_id: str) -> dict:
    jobs = get_jobs(cliente_id)
    findings = get_findings(cliente_id)
    messages = interpret_findings(findings)

    return {
        "cliente_id": cliente_id,
        "jobs_count": len(jobs),
        "findings_count": len(findings),
        "jobs": jobs,
        "findings": findings,
        "messages": messages,
    }
