---
{
  "schema": "wellmanifest.docs/document/v2",
  "id": "fleet-coverage-pilot",
  "kind": "analysis",
  "version": 1,
  "title": "Jawne pokrycie floty i pilotaż opublikowanych dokumentów",
  "status": "proposed",
  "owner": "wellmanifest/docs",
  "scope": "repository",
  "updated": "2026-09-14",
  "source_revision": "867241833a7e69188d595505d116115736438c7a",
  "priority": "P2",
  "evidence": [
    "github://wellmanifest/docs/pull/10",
    "github://semcod/koru/commit/31ad18f9a78c1912ba12dd97b7e90c913c0c1e83",
    "github://semcod/goal/commit/d0b4ff013d225f1c2cc2b29f9a4a3d34735f68a7",
    "github://semcod/taskand-glm53/commit/0f9df49f33d6cd85006fe4e41378f06b7347d7dd"
  ]
}
---

# Pokrycie floty nie jest adopcją

<!-- docs:section summary -->
## Wynik

Wersja 0.4.0 jest scalona przez PR #9 i poprawkę #10. Następny pilotaż
wykazał lukę odkrywania: domyślny filtr Subactor nie obejmował semcod/autogrammar.
Wersja 0.5.0 dodaje jawne organizacje, wiele katalogów i diagnostykę pokrycia.
Nie instaluje bramy u konsumentów. Właściciel wyniku: opiekun standardu docs.

<!-- docs:section details -->
## Obserwacje i zakres

Audyt read-only z 2026-09-14: bezpośrednie checkouty pod `semcod`,
`semcod/taskand` i `autogrammar`, jawne namespace obu organizacji.
Badano lokalne pliki, nie aktualną flotę GitHub. Goal/Koru mają starsze
primary niż scalone pilotaże; nie wolno utożsamiać ich z origin/main.

| Pomiar | Wynik |
| --- | ---: |
| Checkouty semcod / autogrammar | 68 / 38 |
| Wszystkie checkouty / różne deklarowane origin | 106 / 104 |
| Brak lub rozbieżność adopcji / brak indeksu | 106 / 42 |
| Błędne metadane / link changelogu | 3 / 1 |

Badano kandydat 0.5.0 na bazie powyższego source_revision; wynik odmowny
nie jest certyfikatem adopcji żadnej rewizji. `semcod/monag` nie ma origin.
Dwie pary kopii: `semcod/fixos` oraz `autogrammar/testql`; każdą zbadano
oddzielnie, niczego nie usunięto. `semcod/2026` pozostaje jawnym pominięciem
bez rekursji. Origin nie rozwiązuje przekierowań GitHub ani uprawnień Issues.

Trzy błędy metadanych Taskand: `docs/analysis/digital-twin.md`,
`docs/information/complementary-runtime.md` i `instance-network.md`.
Wymagają osobnego uzgodnienia treści; nie pominięto ich dla zielonego wyniku.

<!-- docs:section validation -->
## Odtworzenie

[Test pilotaży](../standard/tests/test_consumer_pilots.py) odczytuje dokładne
scalone rewizje z evidence przez Git, bez zmiany checkoutów. W tymczasowych
fixture bada 12 dokumentów kompaktowych i 5 map z Koru, Goal i Taskand.
Adopcja i skrócony indeks są testowe, nie stanowią wdrożenia konsumenta.
Weryfikujemy zgodność, idempotencję, preflight bez adopcji, rozbieżny pin,
usunięte metadane względem bazy i brak celu mapy.

```bash
DOCS_PILOT_WORKSPACE=/path/to/github \
POLICY_DSL_ROOT=/path/to/pinned/policy-dsl \
python3 -m unittest discover -s docs/standard/tests
```

Brak pierwszej zmiennej jawnie pomija corpus; brak drugiej integrację DSL.
Fixture nie wykonują przykładowych komend z dokumentacji. Lokalnie 117 testów
PASS bez pominięć, w tym realny parser DSL i trzy corpora; governance PASS
dla plików roboczych. Exact-head governance pozostaje warunkiem publikacji.
Checker floty pokazuje HEAD i dirty state, aby odróżnić pliki od publikacji.

<!-- docs:section risks -->
## Warunek kolejnego etapu

Gotowe do kontrolowanych pilotaży, nie do bezwarunkowej masowej migracji.
Następne zadania: Koru #169, Goal #158, Taskand #20. Najpierw uzgodnić
aktywne scope; Taskand #18 już zmienia indeks. Następnie poprawić legacy
metadata, przyjąć opublikowany pin i udowodnić negatywne canary w zaufanym
procesie generowania oraz istniejącym CI. Symulacja nie zastępuje tego dowodu.
Zachować stare kotwice, unikalne wymagania i zarządzane kopie; podobieństwo
tekstu nie uprawnia do deduplikacji. Issues w gftest/gramtest pozostają wyłączone.
Rollback: poprzedni opublikowany pin, bez usuwania historii dokumentacji.
