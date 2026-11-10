# Ticket 021: Trusted legacy redirect provenance

- **ID**: ticket-021
- **Owner**: agent:codex-legacy-docs-20261110
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Created**: 2026-11-10

## Goal and scope

SESSION_EXECUTION_AUTHORIZATION: continue C2004 CI repair PLF-25969/#792
through owner request PLF-005/#25. The operator accepted the exact narrow
editing profile on 2026-11-10. The canonical worktree has a controller-issued
editing lease. The implementation stays within the three source/test/policy
paths declared in intent.json; it adds no dependency or consumer pin change.

Architecture accepted here means the bounded implementation design is selected.
Independent protected review still owns policy approval and publication.
The source admission metadata amendment changes only architecture.status;
base, paths, owner and absolute profile lifetime remain unchanged.

## Acceptance criteria

- [x] AC-01: Strict defaults and negative provenance/target canaries pass.
- [x] AC-02: An explicit trusted immutable anchor permits a historical source
  introduced after the unchanged full audit base; complete-range discovery remains.
- [ ] AC-03: Native checks and independent protected publication precede adoption.

## Implementation and validation

The optional --redirect-provenance-revision input is supplied by the protected
caller; document metadata and origin refs cannot choose it. The checker validates
commit type, both ancestry bounds, regular UTF-8 source bytes and absence of a
redirect source. Existing target, owner, index and version controls remain.
API audit and completion support the same input; prepare/fleet reject it.

Full standard suite: 129 tests, OK with six pre-existing optional skips.
New regression first failed on the missing optional API argument, then passed.
Governance first reported GOV-INTENT-002; the bounded accepted-status amendment
was admitted with a new genuine lease after explicit release of the old lease.
No independent approval, merge, consumer rollout or deployment is claimed.
