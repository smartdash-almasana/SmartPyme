# ADR-XXX: Task Lineage and Correction Chain Protocol

**Status:** Proposed

**Context:**

The current Factory_V3 model executes tasks in isolation. When a task fails its validation (e.g., failing tests), a human operator can manually create a *new* task targeting the same branch to attempt a fix.

This approach has a significant drawback: the new "correction" task has no formal, machine-readable link to the original failed task. It lacks context about what failed, why the correction is needed, and how many attempts have been made. This leads to "operational drift," where the intent of a sequence of fixes can become lost, making auditing difficult and preventing the system from programmatically guiding a task toward convergence.

**Decision:**

We will introduce a formal "Task Lineage" protocol to chain related tasks together, specifically for handling corrections. This is not a system for autonomous, iterative execution or stateful replay. It is a simple, explicit metadata chain to link manually-triggered correction tasks to their predecessors.

A new task can be designated as a "correction pass," which requires it to include a `correction_metadata` block in its specification.

**Lineage Metadata Definition:**

The `correction_metadata` block will contain the following fields:

*   **`lineage_chain_id`**: A unique identifier shared by the original task and all its subsequent correction passes. This allows for grouping the entire chain of attempts.
*   **`parent_task_id`**: The `task_id` of the immediately preceding task that failed and triggered this correction pass.
*   **`correction_pass_number`**: A simple integer counter for the correction attempt (e.g., 1, 2, 3).
*   **`target_branch`**: The git branch the correction should be applied to. Must be the same as the parent task.
*   **`target_commit_hash`**: The commit hash produced by the `parent_task_id` that contains the failing code. The correction worker MUST check out this specific commit before starting its work.
*   **`previous_artifacts_path`**: The storage path where the `parent_task_id`'s artifacts (logs, diffs, test results) can be found. The worker will use this to understand the context of the failure.
*   **`failed_tests_to_fix`**: An explicit list of test nodes that the parent task failed. The worker's objective is strictly limited to making these tests pass.

**Consequences:**

*   **Benefits:**
    *   **Auditability:** We can now reconstruct the entire history of a task, from initial implementation to final fix, by following the `parent_task_id` chain.
    *   **Convergence:** By providing the explicit list of `failed_tests_to_fix`, the correction worker has a clear, narrow, and deterministic goal, increasing the probability of a successful fix.
    *   **Governance:** The `correction_pass_number` allows the Task Orchestrator to enforce guardrails, such as a maximum number of correction attempts before escalating to a human operator.

*   **Limitations (Explicit Scope):**
    *   This is **not a replay system**. The worker does not restore the runtime state of the previous task. It only reads the *outcome* from the persisted artifacts.
    *   This is **not a full snapshot system**. We are not saving the state of the filesystem or running processes.
    *   This does **not enable full autonomy**. A human operator is still required to approve the creation of a correction pass. The system simply provides a formal structure for these approved corrections.

This protocol establishes a minimum viable foundation for auditable, multi-step task resolution without the complexity of building a full stateful replay system at this stage.
