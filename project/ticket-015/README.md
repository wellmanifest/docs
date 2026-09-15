# Ticket 015: Harden readiness receipt deduplication and hostile input handling

- **ID**: ticket-015
- **Owner**: codex
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Created**: 2026-09-15

## Goal and scope

Domknąć pilot readiness receipt po PR #18: zapewnić stabilny klucz
deduplikacji bounded rollout oraz fail-closed walidację list zawierających
niezaufane typy. Zakres jest wyłącznie w standardzie i testach; nie zmienia
consumerów ani nie wykonuje migracji.

## Acceptance criteria

- [x] AC-01: Zakres wynika z autoryzacji sesji „kontynuuj” i pozostaje bounded.
- [x] AC-02: `dedup_key` identyfikuje tę samą obserwację i rozróżnia nowy HEAD/root/fazę.
- [x] AC-03: Złośliwe typy wejściowe zwracają findings zamiast wyjątku.
- [ ] AC-04: Testy i chroniony Validator przechodzą dla exact-head.

## Validation evidence

- `python -m unittest discover -s docs/standard/tests`: 115 passed, 6 skipped (opcjonalny corpus zewnętrzny).
- `python -m py_compile docs/standard/readiness.py docs/standard/tests/test_readiness.py`: PASS.
- `ruff check docs/standard/readiness.py docs/standard/tests/test_readiness.py`: PASS.
- `./project/governance-check.sh --base 69c1c91c07afc7a772c00f7c654ae62e47068946 --head HEAD`: PASS.

## Session authorization

`SESSION_EXECUTION_AUTHORIZATION`: użytkownik polecił kontynuowanie wdrożenia
i udoskonalania `wellmanifest/docs`; follow-up pozostaje w jego zakresie.
Nie obejmuje sekretów, consumerów, Issues ani samodzielnego merge.

## Tracking boundary

This directory contains the minimal reviewed intent. Optional participant prose
and raw command logs are not required delivery output.
