# Plan agenta — ticket-015

Naprawić dwa bounded braki zauważone po PR #18:

- dodać czysty `dedup_key` oparty o repozytorium, standard revision, covered
  roots, base/HEAD i fazę;
- zabezpieczyć walidator przed listami z dict/list, nadmiarem danych i
  niespodziewanymi typami, zawsze zwracając findings;
- dopisać checklistę rollout/dedup do DOCS-012 i negatywne canary testy.

Zmiana nie nadaje authority, nie czyta sekretów i nie dotyka checkoutów
consumerów. Walidacja: unittest, py_compile, ruff, `git diff --check` oraz
`./project/governance-check.sh --base origin/main --head HEAD`; publikacja tylko
przez chronionego Validatora.
