# Ticket 017: algocode deduplication and drift integration

- **ID**: ticket-017
- **Owner**: agent:gemini
- **Status**: DONE
- **Workflow state**: DONE
- **Created**: 2026-09-19

## Goal and scope

Integrate algorithmic deduplication, drift detection, and DSL communication standards (`semcod/algocode`) into `wellmanifest/docs` (Rule DOCS-013). Extend `docs/standard/check.py` to support duplicate detection across documentation headers and section hashes, linking AST inspection and structural clone detection with DSL contracts between LLMs, humans, and deterministic algorithms.

## Acceptance criteria

- [x] AC-01: Formulate and document DOCS-013 in `docs/standard/POLICY.md`.
- [x] AC-02: Implement duplicate detection and verification in `docs/standard/check.py` with optional integration to `semcod/algocode`.
- [x] AC-03: Add unit tests in `docs/standard/tests/` covering the duplicate detection logic.
- [x] AC-04: Pass all governance and test checks cleanly (`GOV-PASS`, unittests).

## Tracking boundary

This directory contains the minimal reviewed intent. Optional participant prose
and raw command logs are not required delivery output.
