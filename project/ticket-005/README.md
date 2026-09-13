# Ticket 005: Adopt governance 0.20.26 and verify update coverage

- **ID**: ticket-005
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Created**: 2026-09-13

## Goal and scope

SESSION_EXECUTION_AUTHORIZATION: owner requested continuation of refactoring,
current Wellmanifest adoption, update automation diagnosis and protected
publication on 2026-09-13. The managed allocator reserved ticket-005 after
authenticated remote inspection established that ticket-003 already merged.
Do not reuse that completed ticket or overwrite its stale primary-checkout draft.

Advance the existing new-project pin from published 0.20.14 (e65857ea) to
published 0.20.26 (8d86cd61) through Goal atomic adoption. Preserve Docs 0.2.0
policy, source and tests. The source package already fixes the old workspace
basename restriction; adoption replaces managed copies without local patches.

Fleet rollout and automation gaps are owned by
subactor/report:docs/refactoring/subactor-fleet-continuation.md. A scheduled
governance audit is not an updater; this adoption does not claim otherwise.

## Acceptance criteria

- [x] AC-01: published adoption check reports no drift at the exact source SHA.
- [x] AC-02: managed governance and all existing Docs tests pass.
- [ ] AC-03: independent exact-head publication preserves required checks.

Local evidence: Goal reports up-to-date at 8d86cd61404d51809532a8292ce9c0cc02ed6157;
the managed exact-base/head governance gate passes (0 errors, 0 warnings);
all 37 existing Docs unit tests pass. Atomic adoption proof requires the
material commit range; the uncommitted preview correctly refused that proof.

## Tracking boundary

This directory contains the minimal reviewed intent. Optional participant prose
and raw command logs are not required delivery output.
