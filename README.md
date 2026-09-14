# wellmanifest/docs

Standard tworzenia i przechowywania informacji, analiz, decyzji i planów refaktoryzacji. Profil **Subactor obejmuje każde `subactor/*`**. Dokumentacja rezultatu należy do repozytorium właściciela, jest wersjonowana w Git i ma jawny indeks. Logi oraz kopie odzyskiwania pozostają prywatnymi artefaktami operacyjnymi.

HOME: `wellmanifest` · SHAPE: `domain_pack` · ADOPT przez konsumentów: `wellmanifest/docs`.

Profil kompaktowy v2: `docs/FEATURE/PROVIDER_DNS_CHANGE_DETECTION.md`,
`docs/BUGFIX/CONFIG_RELOAD_TIMEOUT.md` lub `docs/SERVICE/CACHE_CLEANUP.md`.
Jeden temat, cztery sekcje, najwyżej 120 linii / 600 słów / 12 KiB.
URGENT to priorytet P0/P1 w metadanych; nazwa i link pozostają stabilne.
Changelog zawiera krótki skutek i link. Zobacz
[reguły v2](docs/standard/POLICY.md#docs-009--profil-kompaktowy-v2),
[szablon](docs/standard/templates/COMPACT.md) i
[pomiar przykładów](docs/ANALYSIS/COMPACT_DOCUMENTATION.md).
Poniższe wcześniejsze przykłady v1 pozostają interfejsem kompatybilności;
nowy generator wybiera jawnie `--format v2`.

Przy podziale istniejącego pliku zostaw `wellmanifest.docs/redirect/v1`:
wyłącznie dotychczasowe nagłówki i linki do kanonicznych dokumentów.
Checker weryfikuje cele i pochodzenie dawnej ścieżki przy podanym `--base`.
Szczegóły migracji opisuje [polityka](docs/standard/POLICY.md).

- [Wytyczne normatywne DOCS-001–008](docs/standard/POLICY.md)
- [Maszynowy katalog kontraktu](docs/standard/policy.json)
- [Szablon informacji](docs/standard/templates/information.md)
- [Szablon analizy](docs/standard/templates/analysis.md)
- [Szablon planu refaktoryzacji](docs/standard/templates/refactoring-plan.md)
- [Szablon decyzji](docs/standard/templates/decision.md)
- [Indeks dokumentacji](docs/README.md)

## Najważniejsza reguła

Przed pracą określ `repozytorium + rodzaj dokumentu + ścieżkę kanoniczną`.

Przykład: `subactor/core:docs/refactoring/publication-controller.md`.
Raport organizacyjny (`scope: organization`) ma jedno źródło w `[org]/report`, np.
`subactor/report:docs/analysis/subactor-fleet-audit-2026-09-13.md`.
Raport konkretnego repozytorium (`scope: repository`) pozostaje u jego właściciela,
także gdy wskazuje zależności między repozytoriami. Pole `owner` zawiera dokładne `org/repo`.
Istniejącego repozytorium nie tworzymy ponownie; brak repo rozwiązuje uprawniony
proces tworzenia z przyjętymi standardami, nie sam checker.
Końcowego wyniku nie wolno pozostawić wyłącznie w `/tmp`, `$HOME/.local/state`,
czacie ani katalogu ticketu. Nie wolno publikować backupów i transkrypcji jako dokumentacji.

## Adopcja w projekcie

Publikacja pakietu i adopcja u konsumenta to osobne etapy. Samo scalenie
tego standardu nie instaluje jego checkera w CI pozostałych repozytoriów.
Profil v2 waliduje dokumenty i mapy odsyłaczy. Od 0.4 opcjonalny kontrakt
FEATURE/BUGFIX używa przypiętego Policy DSL; nie jest dowodem wykonania testów.
Zobacz [profil i przykład](docs/FEATURE/CHANGE_CONTRACTS.md).

Dokument z blokiem `dsl` wymaga dodatkowo `--policy-dsl-root` wskazującego
niezależnie przygotowany checkout z `docs/standard/policy-dsl.lock.json`.
Nie kopiujemy parsera, nie pobieramy kodu automatycznie i nie przyjmujemy
ścieżki runtime z dokumentu kandydata. Zwykłe v1/v2 nie wymagają runtime DSL.

1. Wybierz pełny SHA opublikowanej wersji standardu i zweryfikuj jego pochodzenie przez używany proces adopcji. Standard nie nadaje sam sobie statusu opublikowanego.
2. Utwórz `.governance/docs.json` w normalnym tickecie integracyjnym. Wstaw prawdziwy identyfikator repozytorium, pełną rewizję i SHA-256 dokładnych bajtów `docs/standard/policy.json`:

```json
{
  "schema": "wellmanifest.docs/adoption/v1",
  "repository": "subactor/example",
  "standard": "wellmanifest/docs",
  "source_revision": "<40-character-published-commit-sha>",
  "policy_sha256": "<64-character-policy-file-sha256>"
}
```

3. Dodaj indeks `docs/README.md`, odnośnik z README projektu oraz instrukcję agenta wskazującą przypiętą rewizję. W `subactor/docs` indeksem jest główny README.
4. Korzystaj z szablonów i dodaj do istniejącego CI/OneDev poniższe sprawdzenie. `DOCS_STANDARD_ROOT` oraz `DOCS_STANDARD_REVISION` muszą pochodzić z zaufanej konfiguracji wykonawcy. Nie pobieraj i nie wykonuj checkera wskazanego przez niezaufany PR.

Przed generowaniem, po rozwiązaniu standardu i artefaktu w istniejącym rejestrze:

```bash
python3 "$DOCS_STANDARD_ROOT/docs/standard/check.py" \
  --root . --standard-revision "$DOCS_STANDARD_REVISION" --prepare \
  --scope repository --kind refactoring-plan --id publication-controller \
  --deliverable docs/refactoring/publication-controller.md
```

Generator MUSI zatrzymać się przy błędzie. Dla raportu organizacyjnego uruchom
preflight w checkoutcie `org/report` z `--scope organization`. JSON planu opisuje
miejsce i przypięcie; nie udziela uprawnień, nie tworzy repozytorium ani pliku.
Po zapisaniu i dodaniu wyniku do Git uruchom kontrolę końcową:

```bash
python3 "$DOCS_STANDARD_ROOT/docs/standard/check.py" \
  --root . --standard-revision "$DOCS_STANDARD_REVISION" \
  --base "$TRUSTED_BASE_SHA" \
  --deliverable docs/refactoring/publication-controller.md
```

`--deliverable` można powtórzyć; jest wymagane dla jawnie dostarczanych nowych raportów, także gdy ktoś omyłkowo zapisał je poza repo. Checker sam rozpoznaje śledzone dokumenty profilu po nagłówku. `--base` sprawdza wzrost wersji zmienionego dokumentu; bez niego historia wersji nie jest porównywana. Stare formaty nie są masowo przepisywane. Nowy wynik MUSI przyjąć profil.

Checker wymaga wyłącznie Python 3.10+ i Git, nie sieci, LLM ani GitHub Actions. Zwraca JSON i kod `1` przy błędzie. Brak adopcji, błędny digest, nieprawidłowa ścieżka, nieśledzony rezultat, brak indeksu, niekompletny plan i placeholder są błędami. Przekroczony termin review jest widocznym ostrzeżeniem.

## Audyt floty

```bash
python3 "$DOCS_STANDARD_ROOT/docs/standard/check.py" \
  --fleet /path/to/subactor \
  --standard-revision "$DOCS_STANDARD_REVISION"
```

To audyt read-only bezpośrednich lokalnych checkoutów z origin `subactor/*`.
Nie jest dowodem adopcji wszystkich repozytoriów organizacji GitHub. Brak pliku
adopcji jest raportowany jako brak, a nie jako zgodność. Instalacja pakietu ani
wpisanie wytycznej do AGENTS nie oznacza, że każdy pipeline już uruchamia gate.
Adopcję floty zamyka się dopiero po dowodach z każdego objętego repozytorium.

## Walidacja standardu

```bash
POLICY_DSL_ROOT=/path/to/pinned/policy-dsl \
python3 -m unittest discover -s docs/standard/tests -v
./project/governance-check.sh
```

Bez `POLICY_DSL_ROOT` suite jawnie pomija testy integracji parsera. Nie jest
to pełna walidacja kontraktów; przed publikacją wymagane jest wykonanie suite
z przypiętym runtime i bez pominiętych testów integracyjnych.

Polityka należy do tego pakietu. Checker jest testem zgodności, nie generatorem
produktowym, kontrolerem publikacji ani źródłem uprawnień. Implementacje i
automatyzacja agentów pozostają w `subactor/*`; standard współpracuje z
`wellmanifest/new-project`, `wellmanifest/project-ssot`, istniejącym rejestrem
artefaktów i mechanizmem receiptów, zamiast tworzyć ich konkurencyjne kopie.
