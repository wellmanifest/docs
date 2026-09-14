# Ticket 008: Compact categorized documentation and changelog links

- **ID**: ticket-008
- **Owner**: codex
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Created**: 2026-09-14

## Goal and scope

Implement compact document/v2, stable uppercase names, type directories,
independent priority, bounded size and changelog links. Preserve v1 compatibility.

## Acceptance criteria

- [x] AC-01: Policy and template define concise, addressable documents.
- [x] AC-02: Checker and regressions enforce names, size and changelog links.
- [x] AC-03: Measured example, standard tests and managed governance pass.
- [x] AC-04: Legacy link maps preserve old paths and heading anchors while
  validating every destination against a canonical managed document.

## Validation and handoff

66 standard-library tests passed, including legacy map rejection cases, the actual compact template and
delivered example. Managed governance against origin/main: GOV-PASS, zero
errors and warnings. Git diff whitespace check passed. The example has
the original baseline of 72 lines and 335 words; pilot results are now appended
to the versioned analysis. Legacy Taskand inputs total 1495 lines / 11762 words.
Three local pilots preserve 67 legacy headings. Every changed guide/map passes
format and destination checks; missing adoption and five unchanged legacy
metadata findings remain explicit, not waived as successful fleet adoption.
Result: [policy](../../docs/standard/POLICY.md) and
[analysis](../../docs/ANALYSIS/COMPACT_DOCUMENTATION.md).

Publication authorized by the user on 2026-09-14: push this ticket branch,
open its PR and invoke independent protected review and merge. No deployment,
fleet adoption or unimplemented DSL extension is included. Keep IN_PROGRESS
through exact-head review; only the protected controller proves integration.

## Tracking boundary

This directory contains the minimal reviewed intent. Optional participant prose
and raw command logs are not required delivery output.
