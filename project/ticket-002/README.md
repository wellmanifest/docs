# ticket-002: Base-aware documentation discovery

- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Owner**: codex

SESSION_EXECUTION_AUTHORIZATION: User requested continuation of implementation and verification of documentation placement after the reproduced discovery gap.

## Acceptance criteria

- [x] AC-01: With a trusted base, new or changed non-carrier Markdown cannot bypass placement validation by omitting metadata; unchanged legacy documents remain untouched.
- [x] AC-02: Managed documents replaced by symlinks or stripped of metadata fail; organizational files remain compatible.

## Validation

25 regression tests passed; managed gate GOV-PASS (0 errors, 0 warnings). Publication uses protected Validator review. The new immutable pin must be adopted separately by OneDev and target repositories; this change does not claim fleet enforcement.
