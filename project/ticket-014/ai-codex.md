# Plan agenta — ticket-014

## Intencja

Dodać kontrakt `wellmanifest.docs/readiness/v1` jako mały, inertny komponent
standardu. Receipt ma być dowodem obserwacji, nigdy źródłem authority.

## Zakres implementacji

- `docs/standard/readiness.schema.json` — zamknięty schemat receiptu.
- `docs/standard/readiness.py` — czysty generator, walidator i CLI.
- `docs/standard/tests/test_readiness.py` — pozytywne i negatywne canary.
- `docs/standard/POLICY.md`, `policy.json`, `docs/README.md`, `CHANGELOG.md`,
  `VERSION` — opis i wersja pakietu.

## Kryteria i dowody

Generator dla tych samych wejść emituje ten sam obiekt. Walidator wymaga
pełnych digestów, stabilnych względnych `covered_roots`, osobnego evidence dla
każdej fazy i monotonicznego łańcucha. Zmiana rewizji przy tej samej wersji
semantycznej wymaga zaakceptowanego `compatibility_review`. Uruchomić testy
jednostkowe, `./project/governance-check.sh`, checker docs i `git diff --check`.

## Granice

Nie modyfikować checkoutów `semcod/*` ani `autogrammar/*`, nie czytać `.env`,
nie tworzyć repozytoriów, nie zmieniać Issues i nie wykonywać merge. Publikację
może wykonać wyłącznie chroniony Validator po exact-head review.
