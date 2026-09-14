---
{
  "schema": "wellmanifest.docs/document/v2",
  "id": "compact-documentation",
  "kind": "analysis",
  "version": 2,
  "title": "Krótkie dokumenty adresowane z changelogu",
  "status": "proposed",
  "owner": "wellmanifest/docs",
  "scope": "repository",
  "updated": "2026-09-14",
  "source_revision": "dde1ecfc8325cc2d891504a083925db628a96109",
  "priority": "P2",
  "evidence": [
    "github://wellmanifest/docs/commit/4829a5dbeb418dc2606ffa0ce00796c20f44acf1",
    "github://wellmanifest/logs/commit/48c284ef7a069055c0bcb6b900147ce5e65f8b43",
    "repo://semcod/taskand-glm53/docs/refactoring/continuous-evolution-plan.md"
  ]
}
---

# Krótkie dokumenty adresowane z changelogu

<!-- docs:section summary -->
## Cel i rezultat

Ułatwić rozpoznawanie zawartości po ścieżce i skrócić opisy zmian.
Proponowany profil v2: jeden temat, cztery sekcje, nazwy UPPER_SNAKE_CASE.md,
katalog rodzaju i oddzielny priorytet. Specyfikacja:
[DOCS-009](../standard/POLICY.md#docs-009--profil-kompaktowy-v2).

<!-- docs:section details -->
## Obserwacje i decyzja

Lokalny odczyt 2026-09-14, metoda: wc -lw dla trzech wskazanych plików Taskand.
HEAD checkoutu: 6cc16a32fe97e16f5e5f597b5d48e22d5c304680; pomiar dotyczy
plików roboczych, nie dowodzi ich publikacji ani zgodności z tym HEAD.

| Plan w docs/refactoring | Linie | Słowa |
| --- | ---: | ---: |
| continuous-evolution-plan.md | 464 | 3760 |
| external-dependencies-handoff.md | 600 | 4613 |
| functional-recovery-plan.md | 431 | 3389 |

Łącznie 1495 linii i 11762 słowa. Rozmiar utrudnia szybkie adresowanie,
ale sam nie dowodzi zbędności treści. Standard v1 ma 13 wymaganych pól
metadanych i do 12 sekcji; nie ma limitu rozmiaru. Profil v2 ma 12 pól
i cztery sekcje. Główna oszczędność wynika z jednego tematu i limitów,
nie ze skracania metadanych.

Logs stosuje errors/{CODE}.md jako runbook błędu. W docs stosujemy trwałe
nazwy tematyczne, linkując do runbooka zamiast kopiować procedurę.
URGENT jest priorytetem P0/P1; katalog BUGFIX nie zmienia się po usunięciu
pilności. SERVICE oznacza utrzymanie/obsługę, FEATURE nowe zachowanie.

<!-- docs:section validation -->
## Weryfikacja

Budżet dokumentu: 120 linii, 600 słów, 12288 bajtów UTF-8, łącznie
z metadanymi. To początkowe limity projektowe, nie wynik badania użyteczności.
Checker i testy sprawdzają nazwy, limity, indeks, metadane, wersje oraz
istnienie śledzonych plików wskazanych lokalnymi linkami Markdown changelogu.

Pilotaż lokalny 2026-09-14 w Taskand-glm53, Goal i Koru: 12 przewodników
po 55–71 linii / 257–350 słów; pięć dawnych wejść zachowuje 67 nagłówków.
Wybrany materiał: 6732 → 4214 słów, łącznie z metadanymi i mapami.
Checker sprawdza teraz `redirect/v1`: istniejącą ścieżkę względem bazy,
ograniczoną mapę linków i kanoniczne cele bez łańcuchów przekierowań.
66 testów standardu przechodzi. Audyt zmienionych dokumentów nie ma błędów;
pełna adopcja pozostaje niezaliczona (brak pinów i wcześniejsze metadane).

<!-- docs:section risks -->
## Ograniczenia i migracja

Nie wykonano audytu całej floty ani chronionej publikacji pilota.
Podział planu Taskand obejmuje m.in. OFFLINE_NODE_UPDATES.md i
RUNTIME_PACKAGE_CONTRACT.md. Oryginał pozostaje mapą dawnych kotwic.
Treści wymagające wspólnego kontekstu pozostają w legacy v1 do zaplanowania
bezstratnego podziału. Właściciel pakietu weryfikuje pilota przed adopcją.
Przypięcie poprzedniej opublikowanej rewizji stanowi rollback konsumenta.
