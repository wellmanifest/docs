# Ticket 011: Explicit multi-namespace fleet audit and consumer pilots

- **ID**: ticket-011
- **Owner**: codex
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Created**: 2026-09-14

## Goal and scope

SESSION_EXECUTION_AUTHORIZATION: the user requested execution of planned
wellmanifest/docs work, further pilots and improvements, including protected
publication. Implement an explicit multi-namespace fleet audit, exercise it
against semcod/autogrammar and publish tested guidance. Preserve all consumer
files, disabled Issues settings, existing worktrees and unrelated changes.

## Acceptance criteria

- [x] AC-01: Explicit namespace selection covers semcod/autogrammar without
  changing the default Subactor audit or document ownership policy.
- [x] AC-02: Empty/missing coverage, invalid roots, duplicate checkouts and
  skipped entries are visible; no duplicate masks a failing checkout.
- [ ] AC-03: Regression suite including real pinned DSL parser and exact-head
  governance pass. Read-only consumer pilots document actual coverage/gaps.
- [ ] AC-04: Publish material changes through independent protected review;
  distinguish source publication from consumer CI enforcement.

## Tracking boundary

Validation: 117 tests PASS with real pinned DSL runtime and all three
published consumer corpora enabled; working-tree governance PASS. Exact-head
governance and protected review are required before merge. Read-only fleet
pilot: 106 checkouts / 104 declared origins; findings remain failures, not
adoption certificates. See docs/ANALYSIS/FLEET_COVERAGE_PILOT.md.

This directory contains the minimal reviewed intent. Optional participant prose
and raw command logs are not required delivery output.
