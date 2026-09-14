# Ticket 006: Recognize template placeholders without rejecting nested JSON

- **ID**: ticket-006
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Created**: 2026-09-14

## Goal and scope

SESSION_EXECUTION_AUTHORIZATION, 2026-09-14: the user requested improvements
to Wellmanifest when its checks obstruct rapid, correct Taskand delivery.
Taskand's valid nested JSON example was rejected as DOCS_PLACEHOLDER because
the checker matches any adjacent closing braces. Reproduced on current main.
Agent: codex. Scope: placeholder detection and regression fixtures only.
Existing primary drafts and the clean historical ticket-001 worktree are preserved.
Managed work-start initially rejected the allocator's carrier-only placeholder
intent; rerun it after completing this material scope and before source edits.
Publication uses independent exact-head validation. No managed adopter patches.

## Acceptance criteria

- [x] AC-01: Valid nested JSON and code braces do not trigger DOCS_PLACEHOLDER.
- [x] AC-02: Actual template markers remain rejected in metadata, prose and code.
- [x] AC-03: Complete conformance suite and managed governance pass.

Baseline: four failed regression subcases reproduce the adjacent-brace bug.
Candidate: all 40 tests pass, including genuine placeholder rejection.
The local lease reuses the independently pinned controller backend with a
separate wellmanifest/docs resource and ticket-006 intent digest. Its external
receipt is available through the session continuity chain.
Budget adaptation explicitly authorized by the user: XS has an implicit 10-minute
ceiling in the checker, so select S for the measured validation/coordination work.
Keep exactly two implementation files, one component and zero dependency or
interface changes. Reacquire the lease against the revised intent before editing.

## Tracking boundary

This directory contains the minimal reviewed intent. Optional participant prose
and raw command logs are not required delivery output.
