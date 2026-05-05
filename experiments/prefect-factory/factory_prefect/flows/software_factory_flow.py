from __future__ import annotations

import asyncio
import uuid

from prefect import flow, task

from factory_prefect.contracts.ledgers import LedgerTask, ProgressEntry, ProgressLedger, TaskLedger
from factory_prefect.contracts.messages import AgentRole, FactoryStatus, ReviewDecision


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
    return ReviewDecision(
        task_id=ledger_task.task_id,
        decision="PASS",
        reasons=["Static HITO_001 scaffold review passed."],
        commands_to_validate=ledger_task.validation_commands,
    )


@task(log_prints=True)
def collect_task(
    progress_ledger: ProgressLedger,
    ledger_task: LedgerTask,
    review: ReviewDecision,
) -> ProgressLedger:
    status = FactoryStatus.DONE if review.decision == "PASS" else FactoryStatus.BLOCKED
    progress_ledger.append(
        ProgressEntry(
            step_id=f"step_{uuid.uuid4().hex}",
            task_id=ledger_task.task_id,
            agent=AgentRole.REVIEWER,
            status=status,
            summary="Collected base Prefect scaffold review result.",
            details={"review": review.model_dump(mode="json")},
        )
    )
    return progress_ledger


@flow(name="software_factory_flow", log_prints=True, retries=0)
async def software_factory_flow(root_objective: str) -> ProgressLedger:
    run_id = f"run_{uuid.uuid4().hex}"
    task_ledger = TaskLedger(
        run_id=run_id,
        root_objective=root_objective,
        facts=[
            "Prefect owns durable orchestration.",
            "Pydantic contracts own message shape.",
            "Hermes and Docker are intentionally not connected in HITO_001.",
        ],
        tasks=[
            LedgerTask(
                task_id="TASK_001_PREFECT_SCAFFOLD_SMOKE",
                objective="Validate Reconcile -> Dispatch -> Collect scaffold.",
                assigned_role=AgentRole.REVIEWER,
                validation_commands=["python --version"],
            )
        ],
    )
    progress_ledger = ProgressLedger(run_id=run_id)

    reconciled = reconcile_task(task_ledger, progress_ledger)
    task_to_run = dispatch_task(reconciled)
    review = reviewer_task(task_to_run)
    return collect_task(progress_ledger, task_to_run, review)


def main() -> None:
    result = asyncio.run(
        software_factory_flow("Build deterministic SmartPyme Prefect factory.")
    )
    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
