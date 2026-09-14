# Ticket 009: Pilot typed FEATURE and BUGFIX documentation contracts

- **ID**: ticket-009
- **Owner**: codex
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Created**: 2026-09-14

## Goal and scope

Implement an optional compact-document contract profile using the published
Policy DSL parser, not a new grammar. Validate FEATURE/BUGFIX identity,
acceptance assertions, declared observation symbols and tracked test references.
No test execution, inferred approval, consumer CI rollout or runtime deployment.

## Acceptance criteria

- [x] AC-01: Reuse a digest-pinned canonical parser through an explicit runtime root.
- [x] AC-02: Reject malformed, ambiguous and effect-bearing contracts; preserve plain v2.
- [x] AC-03: Deliver two compact examples, tests and publication-ready guidance.

## Validation

All 88 tests pass with POLICY_DSL_ROOT pointing to the lock's published revision;
both delivered examples are validated against that actual parser. Governance
passes against origin/main. No test reference is executed by the checker.
Whole-repository self-audit remains non-passing because the standard repository
has no adopter pin and distributes five unchanged placeholder templates.
Those existing findings are not waived or described as successful CI adoption.

Result: [FEATURE](../../docs/FEATURE/CHANGE_CONTRACTS.md) and
[BUGFIX](../../docs/BUGFIX/DUPLICATE_DSL_CONTRACT.md). Publication must use
the independent protected Validator and exact-head checks.

## Tracking boundary

This directory contains the minimal reviewed intent. Optional participant prose
and raw command logs are not required delivery output.
