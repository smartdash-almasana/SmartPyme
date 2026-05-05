from __future__ import annotations

import asyncio
import uuid

from prefect import flow, task

from factory_prefect.approval.client import ApprovalClient
from factory_prefect.contracts.hitl import HumanApprovalRequest, HumanApprovalResult
from factory_prefect.contracts.ledgers import LedgerTask, ProgressEntry, ProgressLedger, TaskLedger
from factory_prefect.contracts.messages import AgentRole, FactoryStatus, ReviewDecision
from factory_prefect.contracts.sandbox import SandboxExecutionResult
from factory_prefect.sandbox.command_policy import evaluate_command


DEFAULT_VALIDATION_COMMANDS = ["python --version"]


@task(retries=2, retry_delay_seconds=10, log_prints=True)
def reconcile_task(task_ledger: TaskLedger, progress_ledger: ProgressLedger) -> TaskLedger:
    for ledger_task in task_ledger.tasks:
        if ledger_task.status == FactoryStatus.RUNNING:
            ledger_task.status = FactoryStatus.READY
    return task_ledger


@task(log_prints=True)
def dispatch_task(task_ledger: TaskLedger) -> LedgerTask:
    for ledger_task in task_ledger.tasks:
        if ledger_task.status == FactoryStatus.READY:
            ledger_task.status = FactoryStatus.RUNNING
            return ledger_task
    raise RuntimeError("NO_READY_TASK")


@task(log_prints=True)
def reviewer_task(ledger_task: LedgerTask) -> ReviewDecision:
    dangerous_commands: list[str] = []
    safe_commands: list[str] = []

    for command in ledger_task.validation_commands:
        policy = evaluate_command(command)
        if policy.requires_human_approval:
            dangerous_commands.append(command)
        else:
            safe_commands.append(command)

    if dangerous_commands:
        return ReviewDecision(
            task_id=ledger_task.task_id,
            decision="HUMAN_REQUIRED",
            reasons=["Sandbox command policy requires human approval."],
            commands_to_validate=safe_commands,
            dangerous_commands_detected=dangerous_commands,
        )

    return ReviewDecision(
        task_id=ledger_task.task_id,
        decision="PASS",
        reasons=["Command policy review passed."],
        commands_to_validate=safe_commands,
    )


@task(log_prints=True)
async def approval_task(
    run_id: str,
    ledger_task: LedgerTask,
    review: ReviewDecision,
) -> HumanApprovalResult | None:
    if review.decision != "HUMAN_REQUIRED":
        return None

    client = ApprovalClient(endpoint=None)
    return await client.request_approval(
        HumanApprovalRequest(
            run_id=run_id,
            task_id=ledger_task.task_id,
            risk_type="DANGEROUS_COMMAND",
            question="Authorize the dangerous command detected by the sandbox policy?",
            context_summary="Reviewer_Agent detected commands requiring approval.",
            command="; ".join(review.dangerous_commands_detected),
            idempotency_key=f"{run_id}:{ledger_task.task_id}:approval",
        )
    )


@task(log_prints=True)
def sandbox_task(
    ledger_task: LedgerTask,
    review: ReviewDecision,
    approval: HumanApprovalResult | None,
) -> SandboxExecutionResult:
    if review.decision == "HUMAN_REQUIRED":
        if approval is None or not approval.approved:
            return SandboxExecutionResult(
                task_id=ledger_task.task_id,
                command="; ".join(review.dangerous_commands_detected),
                returncode=126,
                stdout="",
                stderr="Human approval required or denied before sandbox execution.",
                blocked=True,
                requires_human_approval=True,
                reasons=review.reasons,
            )

    from factory_prefect.sandbox.docker_executor import DockerExecutor
    from factory_prefect.contracts.sandbox import SandboxExecutionRequest

    command = review.commands_to_validate[0] if review.commands_to_validate else "python --version"
    executor = DockerExecutor()
    request = SandboxExecutionRequest(
        task_id=ledger_task.task_id,
        command=command,
        timeout_seconds=60,
        network_disabled=True,
    )
    return executor.execute(request)


@task(log_prints=True)
def collect_task(
    progress_ledger: ProgressLedger,
    ledger_task: LedgerTask,
    review: ReviewDecision,
    sandbox: SandboxExecutionResult,
    approval: HumanApprovalResult | None,
) -> ProgressLedger:
    status = FactoryStatus.DONE if sandbox.returncode == 0 and not sandbox.blocked else FactoryStatus.BLOCKED
    progress_ledger.append(
        ProgressEntry(
            step_id=f"step_{uuid.uuid4().hex}",
            task_id=ledger_task.task_id,
            agent=AgentRole.REVIEWER,
            status=status,
            summary="Collected review, approval and sandbox result.",
            details={
                "review": review.model_dump(mode="json"),
                "approval": approval.model_dump(mode="json") if approval else None,
                "sandbox": sandbox.model_dump(mode="json"),
            },
        )
    )
    return progress_ledger


@flow(name="software_factory_flow", log_prints=True, retries=0)
async def software_factory_flow(
    root_objective: str,
    validation_commands: list[str] | None = None,
) -> ProgressLedger:
    run_id = f"run_{uuid.uuid4().hex}"
    commands = validation_commands if validation_commands is not None else DEFAULT_VALIDATION_COMMANDS
    task_ledger = TaskLedger(
        run_id=run_id,
        root_objective=root_objective,
        facts=[
            "Prefect owns durable orchestration.",
            "Pydantic contracts own message shape.",
            "ApprovalClient is fail-closed in HITO_005.",
            "Sandbox execution is mocked in HITO_005.",
        ],
        tasks=[
            LedgerTask(
                task_id="TASK_001_PREFECT_POLICY_SMOKE",
                objective="Validate Reconcile -> Dispatch -> Review -> Approval -> SandboxMock -> Collect.",
                assigned_role=AgentRole.REVIEWER,
                validation_commands=commands,
            )
        ],
    )
    progress_ledger = ProgressLedger(run_id=run_id)

    reconciled = reconcile_task(task_ledger, progress_ledger)
    task_to_run = dispatch_task(reconciled)
    review = reviewer_task(task_to_run)
    approval = await approval_task(run_id, task_to_run, review)
    sandbox = sandbox_task(task_to_run, review, approval)
    return collect_task(progress_ledger, task_to_run, review, sandbox, approval)


def main() -> None:
    result = asyncio.run(
        software_factory_flow("Build deterministic SmartPyme Prefect factory.")
    )
    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
