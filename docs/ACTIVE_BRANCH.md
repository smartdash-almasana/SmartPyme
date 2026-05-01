# Active Branch Guard

## Current active engineering branch

```text
factory/ts-006-jobs-sovereign-persistence
```

This is the active SmartPyme working branch.

Do not start new SmartPyme tasks from `main` unless the owner explicitly says so.

## Required workflow

For new implementation work:

```bash
git fetch origin
git checkout factory/ts-006-jobs-sovereign-persistence
git pull --ff-only origin factory/ts-006-jobs-sovereign-persistence
git checkout -b factory/<task-id>-<short-name>
```

For documentation work related to the current front:

```bash
git fetch origin
git checkout factory/ts-006-jobs-sovereign-persistence
git pull --ff-only origin factory/ts-006-jobs-sovereign-persistence
git checkout -b docs/<task-id>-<short-name>
```

## Pull request rule

New PRs for this front must target:

```text
base: factory/ts-006-jobs-sovereign-persistence
```

They must not target `main`.

## Why this exists

Previous work was accidentally created from `main`.
That produced valid code on the wrong base branch.
The corrected PR is:

```text
#7: factory/ts-016-019-ai-layer-on-ts-006 -> factory/ts-006-jobs-sovereign-persistence
```

## Current valid continuation

Continue from PR #7 or from branches derived from:

```text
factory/ts-006-jobs-sovereign-persistence
```

## Safety rule for future chats

Before creating any branch, PR, or commit, verify:

```bash
git branch --show-current
```

Expected active branch:

```text
factory/ts-006-jobs-sovereign-persistence
```
