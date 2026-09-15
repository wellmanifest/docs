---
{
  "schema": "wellmanifest.docs/document/v1",
  "id": "autonomous-leverage-and-queue-drain",
  "kind": "information",
  "version": 1,
  "title": "Protokół Dźwigni Zasobów, Ekstrakcji Intencji i Drenażu Kolejki Zadań",
  "status": "implemented",
  "owner": "wellmanifest/docs",
  "scope": "repository",
  "created": "2026-09-15",
  "updated": "2026-09-15",
  "review_after": "2027-03-15",
  "source_revision": "9fb5fc41a7d65b16f39d10e060010839c0fa1e57",
  "affected_repositories": [
    "wellmanifest/docs"
  ],
  "evidence": [
    "github://autogrammar/todo2code/README.md",
    "github://autogrammar/data2dsl/README.md",
    "github://semcod/monag/src/monag/resume.py"
  ]
}
---

# Informacja: Protokół Dźwigni Zasobów, Ekstrakcji Intencji i Drenażu Kolejki Zadań

<!-- docs:section purpose -->
## Purpose

Dokument ustanawia standard maksymalizacji dźwigni operacyjnej dla agentów autonomicznych (`taskand`, `subactor`). Definiuje zasady wielokrotnego wykorzystania poświadczeń i sesji bez powtarzających się pytań do człowieka, procedurę ekstrakcji intencji historycznej z Git (`todo2code`, `data2dsl`) oraz strategię masowego drenażu kolejki zaległych zadań w rozproszonych repozytoriach.

<!-- docs:section scope -->
## Scope

Dotyczy runtime'ów Taskand v2.2+, maszynowego frameworka subactor oraz integracji narzędziowych w obrębie całego środowiska roboczego programisty (`~/github/*/*`).

<!-- docs:section evidence -->
## Evidence

- Telemetria `semcod/monag` wykazuje 693 projekty w przestrzeni roboczej, z czego 383 zawierają niezmergowane commity lub modyfikacje, a setki ticketów Planfile oczekują na realizację. Pasywne czekanie na polecenia blokuje drenaż zaległości.
- Pakiety `autogrammar/todo2code` oraz `autogrammar/data2dsl` dowodzą możliwości automatycznego odtworzenia intencji architektonicznych z logów Git i różnic schematów.
- Analiza czasu pracy agenta wskazuje, że do 70% opóźnień wynika z niepotrzebnych rund pytań o zgodę na użycie znanych narzędzi lub ponownego uwierzytelniania.

<!-- docs:section content -->
## Content

### 1. Zasada Pełnej Dźwigni Poświadczeń (Zero Re-Prompting Once Granted)

W środowiskach autonomicznych człowiek deleguje uprawnienia blokowo, a nie per pojedyncze wywołanie:

1. **Trwała autoryzacja sesji**: Gdy użytkownik przekazuje agentowi poświadczenia (tokeny, dostęp do sesji w przeglądarce Digital Twin przez CDP/noVNC, klucz do Vault AES-256), agent ma obowiązek **maksymalizować reużycie tych poświadczeń** w celu rozwiązania postawionego celu.
2. **Autonomiczne generowanie tokenów AI**: Agent posiadający sesję w serwisach zewnętrznych generuje niezbędne klucze API i tokeny pomocnicze, buforuje je w lokalnym sejfie (`taskand/vault`) i współdzieli między podległymi procesami bez angażowania człowieka.
3. **Zakaz sztucznych blokad**: Agent nie pyta: „czy mogę użyć tokenu X?”, jeżeli token ten mieści się w zdefiniowanym profilu zadania i polityce `grants.yaml`. Pytanie człowieka jest dozwolone wyłącznie w przypadku:
   - operacji destrukcyjnych (kasowanie bazy, usunięcie gałęzi main),
   - operacji generujących wysokie koszty finansowe powyżej ustalonego limitu,
   - wyjścia poza zadeklarowany obwód uprawnień.

### 2. Introspekcja i Reużycie Lokalne (`~/github/*/*`)

System nie powinien tworzyć od zera bibliotek, które istnieją już w zasobach programisty:

1. **Indeks Zdolności Workspace**: Taskand buduje katalog zdolności z lokalnych projektów:
   - `autogrammar/curllm`: zapytania HTTP i ekstrakcja danych,
   - `autogrammar/doql`: transformacje schematów i obiektów,
   - `autogrammar/testql`: generowanie i analiza scenariuszy testowych,
   - `autogrammar/code2schema`: inspekcja struktur danych kodu.
2. **Izolowane katalogi wykonawcze**: Wywołanie zewnętrznych narzędzi odbywa się w dedykowanych folderach roboczych w ramach `taskand/generated/` lub kontenerów Docker, uniemożliwiając zanieczyszczenie głównego repozytorium narzędzia.

### 3. Ekstrakcja Intencji z Historii Git

Kod źródłowy opisuje *jak* system działa dzisiaj, ale historia Git wyjaśnia *dlaczego* tak działa:

```
[Git History: log -p, PRs, Tickets]
                │
                ▼
      [autogrammar/todo2code]  ──►  Ekstrakcja intencji z TODO i zmian
                │
                ▼
      [autogrammar/data2dsl]   ──►  Formalizacja reguł i schematów
                │
                ▼
       [Graf Intencji SSOT]
                │
                ├──► Weryfikacja bieżących zmian (Detekcja Regresji Intencji)
                └──► Automatyczne wystawianie ticketów BUGFIX / SERVICE
```

1. **Wykrywanie Regresji Intencji**: Podczas analizy zmian w worktree Taskand weryfikuje, czy nowa implementacja nie łamie reguł ustalonych w commitach historycznych.
2. **Auto-Ticket Serwisowy**: Jeżeli zaobserwowano dryft intencji lub rosnące skomplikowanie bez testów, system automatycznie alokuje ticket `SERVICE` lub `BUGFIX`, zapobiegając degradacji architektury.

### 4. Strategia Masowego Drenażu Kolejki (High-Throughput Drain)

Aby zredukować setki zaległych ticketów zidentyfikowanych m.in. przez `monag`:

1. **Indukcja Predykcyjna**: Planista Taskand nie czeka na nowe zadania w bezczynności — analizuje otwarte tickety z Planfile, generuje wstępne plany DAG, pobiera dokumentację i przeprowadza weryfikację zależności w tle.
2. **Izolowane Worktrees v5**: Każde zadanie z kolejki jest przetwarzane w dedykowanym katalogu `.worktrees/ticket-NNN--<slug>`, co zapobiega konfliktom edycyjnym i blokadom na gałęzi `main`.
3. **Równoległa orkiestracja**: Zadania o rozłącznych ścieżkach (`allowedPaths`) są wykonywane współbieżnie z zachowaniem budżetów CPU/RAM stacji roboczej.

<!-- docs:section limitations -->
## Limitations

Dźwignia operacyjna nie zwalnia z obowiązku weryfikacji zmian przez bramki Gate A (kontrakt) i Gate B (regresja) w Digital Twin. Przechowywane poświadczenia muszą pozostawać w zaszyfrowanym sejfie, a ich wyciek do logów lub commita traktowany jest jako incydent krytyczny (URGENT).

<!-- docs:section next_actions -->
## Next actions

1. Dołączyć skaner `autogrammar` do fazy bootstrapu Taskand.
2. Skonfigurować automatyczny drenaż kolejki w pętli nocnej/tła.
3. Wdrożyć weryfikator braku sekretów w wyjściu procesów `proc://`.
