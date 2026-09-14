---
{
  "schema": "wellmanifest.docs/document/v2",
  "id": "change-contracts",
  "kind": "feature",
  "version": 1,
  "title": "Formalne kryteria FEATURE i BUGFIX",
  "status": "implemented",
  "owner": "wellmanifest/docs",
  "scope": "repository",
  "updated": "2026-09-14",
  "source_revision": "bfcb71ef19466e930218bb2a3bfdde758b2fd83d",
  "priority": "P2",
  "evidence": [
    "github://wellmanifest/docs/commit/bfcb71ef19466e930218bb2a3bfdde758b2fd83d",
    "github://wellmanifest/policy-dsl/commit/7109aee92c2bb7ac2db8e3b0b4ddd7ded4750257"
  ]
}
---

# Formalne kryteria FEATURE i BUGFIX

<!-- docs:section summary -->
## Cel

Opcjonalny kontrakt wewnątrz krótkiego dokumentu. Reużywa `wellmanifest.policy/v1`; nie wprowadza drugiej gramatyki ani automatycznego wykonania.

<!-- docs:section details -->
## Kontrakt

Jeden blok `dsl` wiąże identyfikator dokumentu, zgodność i kryteria z plikami testów. `INPUTS` deklaruje nazwy obserwacji, które dostarcza zewnętrzny system; checker ich nie odczytuje ani nie ocenia.

```dsl
DOCUMENT DOCS_FEATURE
VERSION 1
MODE STRICT
POLICY "wellmanifest.docs/change/v1"
SUBJECT = "change-contracts"
COMPATIBILITY = "Plain v2 remains valid without the DSL runtime"
INPUTS IN ["VALIDATION_RESULT"]
RULE AC-01 TYPE REQUIRED
WHEN TRUE
ASSERT VALIDATION_RESULT = "accepted"
DO VALIDATE "docs/standard/tests/test_change_contract.py"
```

`DOCS_FEATURE` odpowiada FEATURE, `DOCS_BUGFIX` odpowiada BUGFIX. Wersja bloku musi równać się wersji metadanych dokumentu. BUGFIX wymaga także `REPRODUCTION`, `BEFORE`, `AFTER`.

Pełny profil: [DOCS-010](../standard/POLICY.md#docs-010--opcjonalny-kontrakt-zmiany).

<!-- docs:section validation -->
## Weryfikacja

Uruchomić suite z `POLICY_DSL_ROOT` wskazującym checkout przypięty w `docs/standard/policy-dsl.lock.json`. Checker przyjmuje tę samą ścieżkę przez `--policy-dsl-root` i sprawdza hashe parsera, gramatyki i schematu przed importem. Brak runtime daje `DOCS_DSL_RUNTIME`, nie sukces.

<!-- docs:section risks -->
## Granice

Walidacja potwierdza strukturę i istnienie śledzonych plików testowych, nie ich wynik, kompletność ani poprawność zachowania. Deklaracje nie zastępują ticketu, `intent.json`, chronionego review i uprawnień. Adopcja CI konsumentów pozostaje osobnym etapem. Właściciel profilu: wellmanifest/docs; języka: wellmanifest/policy-dsl.
