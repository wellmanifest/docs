# Ticket 014: Standardize declared configured deployed verified documentation readiness

- **ID**: ticket-014
- **Owner**: codex
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Created**: 2026-09-15

## Goal and scope

Wprowadzić inertny, maszynowy receipt gotowości adoptera standardu dokumentacji.
Receipt ma rozdzielać pięć faz, wiązać dokładne rooty oraz base/HEAD i digesty,
nie przyznając uprawnień do publikacji. Zakres obejmuje schemat, generator,
walidator, canary testy i opis użycia w `wellmanifest/docs`; nie obejmuje zmian
w consumerach ani automatycznych aktualizacji ich pinów.

## Acceptance criteria

- [x] AC-01: Zakres wynika z bieżącej autoryzacji sesji do kontynuowania wdrożenia.
- [x] AC-02: Receipt v1 i schemat rozdzielają `unavailable`, `unadopted`, `configured`, `deployed`, `verified` oraz wymagają dokładnych rootów, base/HEAD i digestów.
- [x] AC-03: Generator jest idempotentny, a canary odrzuca niebezpieczne rooty, przyszłe dowody, regresję fazy i zmianę źródła tej samej wersji bez review.
- [ ] AC-04: Testy standardu i zarządzana brama przechodzą; publikacja pozostaje decyzją chronionego Validatora.

## Validation evidence

- `python -m unittest discover -s docs/standard/tests`: 113 passed, 6 skipped (opcjonalny corpus zewnętrzny).
- `./project/governance-check.sh --base 6f475fb223e7a259d514b5483fb0d62f0e80a46e --head HEAD`: PASS.
- `ruff check docs/standard/readiness.py docs/standard/tests/test_readiness.py`: PASS.

## Session authorization

`SESSION_EXECUTION_AUTHORIZATION`: użytkownik wielokrotnie polecił
„kontynuuj” oraz wdrożenie i kolejne pilotaże standardu `wellmanifest/docs`.
Uprawnienie obejmuje ten bounded feature w repozytorium standardu, nie obejmuje
sekretów, zmian w consumerach ani samodzielnego merge.

## Tracking boundary

This directory contains the minimal reviewed intent. Optional participant prose
and raw command logs are not required delivery output.
