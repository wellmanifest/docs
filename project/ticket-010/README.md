# Ticket 010: Correct DSL pilot publication validation

- **ID**: ticket-010
- **Owner**: codex
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Created**: 2026-09-14

## Goal and scope

Correct the malformed dependency declaration published with ticket-009 and
exercise the delivered DSL checker through its public CLI. Preserve the merged
history and protected policy. Publish only after exact-base/head governance
and the full parser-backed suite pass.

## Acceptance criteria

- [x] AC-01: Canonical dependency declaration uses the required string list.
- [x] AC-02: CLI regression proves explicit runtime success and fail-closed absence.

## Validation

89 tests passed with POLICY_DSL_ROOT at pinned revision
7109aee92c2bb7ac2db8e3b0b4ddd7ded4750257. Working-tree governance passed.
Publication additionally requires the committed exact-base/head gate and both
hosted governance checks; local working-tree PASS is not sufficient evidence.

## Tracking boundary

This directory contains the minimal reviewed intent. Optional participant prose
and raw command logs are not required delivery output.
