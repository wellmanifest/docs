---
{
  "schema": "wellmanifest.docs/document/v2",
  "id": "duplicate-dsl-contract",
  "kind": "bugfix",
  "version": 1,
  "title": "Odrzucanie niejednoznacznych bloków DSL",
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

# Odrzucanie niejednoznacznych bloków DSL

<!-- docs:section summary -->
## Cel

Dokument kompaktowy nie może deklarować dwóch kontraktów DSL. Wcześniejszy checker v0.3 sprawdzał strukturę Markdown, lecz nie interpretował takich bloków.

<!-- docs:section details -->
## Kontrakt

Profil wymaga dokładnie jednego pełnego bloku. Drugi blok, niedomknięte ogrodzenie lub nieprawidłowa etykieta prowadzą do błędu; przykłady niewchodzące do kontraktu zapisuje się jako `text`.

```dsl
DOCUMENT DOCS_BUGFIX
VERSION 1
MODE STRICT
POLICY "wellmanifest.docs/change/v1"
SUBJECT = "duplicate-dsl-contract"
COMPATIBILITY = "Plain compact guides remain unchanged"
REPRODUCTION = "Place two top-level dsl fences in one compact guide"
BEFORE = "The Markdown checker did not inspect DSL contracts"
AFTER = "Ambiguous contracts are rejected before parser loading"
INPUTS IN ["CONTRACT_COUNT", "DIAGNOSTIC"]
RULE AC-01 TYPE REQUIRED
WHEN CONTRACT_COUNT = 2
ASSERT DIAGNOSTIC = "DOCS_DSL_CONTRACT"
DO VALIDATE "docs/standard/tests/test_change_contract.py"
```

[Opis formatu](../FEATURE/CHANGE_CONTRACTS.md) rozdziela formalną deklarację od wykonania.

<!-- docs:section validation -->
## Weryfikacja

Test `FenceTests.test_duplicate_contracts_fail_before_loading_code` odtwarza przypadek bez runtime. Testy integracyjne wymagają przypiętego `POLICY_DSL_ROOT`; sprawdzają też odrzucenie efektów, nieznanych symboli, fałszywych ścieżek i zmienionego parsera.

<!-- docs:section risks -->
## Granice

Zagnieżdżony przykład w zewnętrznym ogrodzeniu `text` jest treścią przykładową, nie kontraktem. Zmiana odbiera tolerancję dla niezwalidowanego `dsl` w zarządzanych dokumentach: istniejące przykłady należy oznaczyć `text` albo jawnie przyjąć profil. Rollback to wcześniejszy pin standardu; zachować historię dokumentu.
