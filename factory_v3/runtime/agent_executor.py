from __future__ import annotations

from typing import Callable, Optional

from factory_v3.contracts.entities import AgentCard, TaskEnvelope, TaskState
from factory_v3.ledgers.task_ledger import TaskLedger
from factory_v3.runtime.context_rehydrator import ContextRehydrator
from factory_v3.runtime.distributed_lock_manager import DistributedLockManager
from factory_v3.runtime.runtime_policies import RuntimePolicyEngine


class AgentExecutor:
    def __init__(
        self,
        *,
        task_ledger: TaskLedger,
        rehydrator: ContextRehydrator,
        lock_manager: Optional[DistributedLockManager] = None,
        policy_engine: Optional[RuntimePolicyEngine] = None,
    ):
        self.task_ledger = task_ledger
        self.rehydrator = rehydrator
        self.lock_manager = lock_manager or DistributedLockManager()
        self.policy_engine = policy_engine or RuntimePolicyEngine()

    def execute(
        self,
        *,
        task: TaskEnvelope,
        agent: AgentCard,
        execution_callable: Callable,
    ):
        task_id = task.task_id
        agent_id = agent.agent_id
        current_state = self.task_ledger.get_latest_state(task_id)

        policy_result = self.policy_engine.evaluate_task_assignment(
            task=task,
            agent=agent,
        )

        if not policy_result.allowed:
            self.task_ledger.transition_task(
                task_id=task_id,
                previous_state=current_state,
                next_state=TaskState.FAILED,
                producer_id=agent_id,
                reason="policy denied: " + "; ".join(policy_result.reasons),
            )
            raise PermissionError("runtime policy denied task execution")

        lock_acquired = self.lock_manager.acquire(task_id)

        if not lock_acquired:
            self.task_ledger.transition_task(
                task_id=task_id,
                previous_state=current_state,
                next_state=TaskState.FAILED,
                producer_id=agent_id,
                reason="task lock already acquired",
            )
            raise RuntimeError("task is already locked")

        try:
            self.task_ledger.transition_task(
                task_id=task_id,
                previous_state=current_state,
                next_state=TaskState.ACTIVE,
                producer_id=agent_id,
                reason="agent execution started",
            )

            snapshot = self.rehydrator.rebuild_task_context(task_id)
            result = execution_callable(snapshot)

            self.task_ledger.transition_task(
                task_id=task_id,
                previous_state=TaskState.ACTIVE,
                next_state=TaskState.DONE,
                producer_id=agent_id,
                reason="agent execution completed",
            )

            return result

        except Exception as exc:
            self.task_ledger.transition_task(
                task_id=task_id,
                previous_state=TaskState.ACTIVE,
                next_state=TaskState.FAILED,
                producer_id=agent_id,
                reason=str(exc),
            )
            raise

        finally:
            self.lock_manager.release(task_id)
