# Ticket 018: harden check discovery and diagnostic clarity

- **ID**: ticket-018
- **Owner**: agent:gemini
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Created**: 2026-09-19
- **Authorization**: SESSION_EXECUTION_AUTHORIZATION

## Goal and scope

Harden `docs/standard/check.py` to automatically discover and validate `.governance/managed-copies.json` when present in tracked repository files, provide granular and actionable field-level diagnostics for `DOCS_METADATA` violations, and ensure test suites and consumer pilot tests (`test_consumer_pilots.py`) run reliably across environments.

## Acceptance criteria

- [x] AC-01: Auto-discover and validate `.governance/managed-copies.json` in `check.py` when `--managed-copies` is omitted.
- [x] AC-02: Provide granular field-level diagnostics for `DOCS_METADATA` failures (identifying specific field, format constraint, or missing/unexpected key).
- [x] AC-03: Fix test import in `test_consumer_pilots.py` and add comprehensive tests for managed-copies auto-discovery and granular metadata diagnostics.
- [x] AC-04: Pass all governance checks and unit tests cleanly (`GOV-PASS`, unittests).

## Tracking boundary

This directory contains the minimal reviewed intent. Optional participant prose
and raw command logs are not required delivery output.
