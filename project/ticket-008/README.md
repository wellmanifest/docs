# Ticket 008: Compact categorized documentation and changelog links

- **ID**: ticket-008
- **Owner**: codex
- **Status**: IN_PROGRESS
- **Workflow state**: VALIDATION
- **Created**: 2026-09-14

## Goal and scope

Implement compact document/v2, stable uppercase names, type directories,
independent priority, bounded size and changelog links. Preserve v1 compatibility.

## Acceptance criteria

- [x] AC-01: Policy and template define concise, addressable documents.
- [x] AC-02: Checker and regressions enforce names, size and changelog links.
- [x] AC-03: Measured example, standard tests and managed governance pass.

## Validation and handoff

61 standard-library tests passed, including the actual compact template and
delivered example. Managed governance against origin/main: GOV-PASS, zero
errors and warnings. Git diff whitespace check passed. The example has
72 lines and 335 words; legacy Taskand inputs total 1495 lines / 11762 words.
Result: [policy](../../docs/standard/POLICY.md) and
[analysis](../../docs/ANALYSIS/COMPACT_DOCUMENTATION.md).

Local implementation only. No PR, release, protected merge or fleet adoption.
Ticket stays IN_PROGRESS pending any separately requested publication.

## Tracking boundary

This directory contains the minimal reviewed intent. Optional participant prose
and raw command logs are not required delivery output.
