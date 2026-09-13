# Ticket 004: Resolve report ownership before generation and enforce organization report homes

- **ID**: ticket-004
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Created**: 2026-09-13

## Goal and scope

SESSION_EXECUTION_AUTHORIZATION: owner requested standard discovery, implementation,
organization-owned reports and mandatory artifact/operational preflight on 2026-09-13.

The existing Docs standard already forbids temp-only final reports. Extend it
with explicit repository/organization ownership and a read-only pre-generation
gate. Organization reports belong to org/report; no duplicate wellmanifest/report
package is needed. Consumer adoption and protected enforcement need separate
observed receipts, not a claim that standard publication enforces every agent.

Canonical standard: docs/standard/POLICY.md; canonical fleet report consumer:
subactor/report:docs/analysis/subactor-fleet-audit-2026-09-13.md.

## Acceptance criteria

- [ ] AC-01: Preflight rejects missing adoption, wrong repository, unsafe destinations and unknown scopes before report generation.
- [ ] AC-02: Explicit org reports resolve to org/report; repository-owned results remain local; historical documents are preserved.
- [ ] AC-03: Tests and governance pass and the standard is published through independent review.

## Tracking boundary

This directory contains the minimal reviewed intent. Optional participant prose
and raw command logs are not required delivery output.
