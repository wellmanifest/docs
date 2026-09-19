---
{
  "schema": "wellmanifest.docs/document/v1",
  "id": "workflow-priority",
  "kind": "information",
  "version": 1,
  "title": "Hierarchia Priorytetów Workflow: URGENT -> BUGFIX -> FEATURE -> SERVICE",
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
    "github://wellmanifest/priority/docs/STANDARD.md",
    "github://semcod/taskand/STANDARD-v2.2.md"
  ]
}
---

# Informacja: Hierarchia Priorytetów Workflow: URGENT -> BUGFIX -> FEATURE -> SERVICE

<!-- docs:section purpose -->
## Purpose

Dokument definiuje normatywną hierarchię priorytetów inżynierii oprogramowania oraz zasady kolejkowania prac dla agentów autonomicznych (w tym developerów Taskand) i operatorów ludzkich:
`URGENT -> BUGFIX -> FEATURE -> SERVICE`.

Celem jest formalne powiązanie kosztu awarii krytycznych z nakładami na higienę techniczną, zapobieganie eskalacji długu technologicznego oraz zapewnienie deterministycznego szeregowania zadań w systemach ciągłej autonomii.

<!-- docs:section scope -->
## Scope

Standard obejmuje wszystkie procesy planowania, orkiestracji i realizacji zadań w ekosystemach `wellmanifest`, `subactor`, `semcod` oraz agenta `taskand`. Dotyczy zarówno kolejkowania ticketów w Planfile/Git, jak i dynamicznego wyboru celów przez planistę (`proc://taskand.dev/planner/plan/v1`).

<!-- docs:section evidence -->
## Evidence

- `wellmanifest/priority` (`docs/STANDARD.md`): model porządkowania leksykograficznego `floor -> standard -> opportunistic`, eliminujący wypieranie niezmienników poprawności przez sumę drobnych zadań.
- `semcod/taskand` (`STANDARD-v2.2.md`): dekompozycja zadań DAG z twardą blokadą kroków zależnych przy błędach poprzedników (`fail-closed`).
- Obserwacje awarii operacyjnych: błędy bezpieczeństwa i wycieki poświadczeń w systemach autonomicznych generują lawinowy koszt wstrzymania floty (URGENT), którego pierwotną przyczyną było odraczanie zadań serwisowych (SERVICE) i ignorowanie drobnych usterek (BUGFIX).

<!-- docs:section content -->
## Content

### 1. Definicja i Koszt Tiers

```
+-------------------------------------------------------------------------+
|  URGENT   (Blokada systemu, wyciek, krytyczna awaria)   - KOSZT EKSTREMALNY |
+-------------------------------------------------------------------------+
       ^
       | eskalacja przy braku reakcji
+-------------------------------------------------------------------------+
|  BUGFIX   (Prewencja awarii, naprawa niezgodności)      - KOSZT UMIARKOWANY |
+-------------------------------------------------------------------------+
       ^
       | realizacja po zabezpieczeniu stabilności
+-------------------------------------------------------------------------+
|  FEATURE  (Nowa wartość biznesowa, rozszerzenia)        - KOSZT PLANOWANY   |
+-------------------------------------------------------------------------+
       ^
       | immunizacja fundamentu (redukuje BUGFIX i URGENT)
+-------------------------------------------------------------------------+
|  SERVICE  (Refaktoryzacja, higiena, dług, wydajność)   - KOSZT MINIMALNY   |
+-------------------------------------------------------------------------+
```

#### A. URGENT (Priorytet Krytyczny — Natychmiastowy)
- **Charakterystyka**: Zagrożenie integralności systemu, wyciek sekretów/tokenów, luka bezpieczeństwa, awaria bramki autoryzacyjnej (fail-open), uszkodzenie danych lub całkowity paraliż węzła.
- **Ekonomia i koszt**: Skrajnie wysoki koszt operacyjny. Wymaga natychmiastowego zrzucenia kontekstu, przejścia agentów w tryb bezpieczny (`safe-mode`), odcięcia sieci lub wyłączenia podatnego modułu oraz głębokiej analizy śledczej (root-cause analysis).
- **Zasada**: Nic nie konkuruje z URGENT. Każde inne zadanie (w tym wdrożenia nowych funkcji) zostaje wstrzymane.

#### B. BUGFIX (Priorytet Naprawczy)
- **Charakterystyka**: Zaobserwowana niezgodność z kontraktem, regresja zachowania, błąd w logice biznesowej, błąd testu jednostkowego lub naruszenie schematu.
- **Ekonomia i koszt**: Umiarkowany. Naprawa na tym etapie jest rzędy wielkości tańsza niż po eskalacji do URGENT.
- **Zasada**: Ciągłe i częste wdrażanie poprawek jest tarczą antykryzysową. Zgromadzony dług błędów blokuje otwieranie nowych strumieni FEATURE.

#### C. FEATURE (Priorytet Rozwojowy)
- **Charakterystyka**: Dostarczanie nowej wartości, dodawanie nowych procesów `proc://`, integracji API lub adapterów.
- **Ekonomia i koszt**: Przewidywalny i kontrolowany budżet.
- **Zasada**: Nowe funkcjonalności są wdrażane wyłącznie na stabilnym fundamencie. Jeżeli wskaźnik otwartych defektów przekracza próg tolerancji, capacity przechodzi na BUGFIX.

#### D. SERVICE (Priorytet Higieny i Długu Technicznego)
- **Charakterystyka**: Aktualizacje zależności, usuwanie martwego kodu, podnoszenie pokrycia testami, optymalizacja zużycia zasobów (performance tuning), odświeżanie certyfikatów, standaryzacja worktree i struktury repozytorium.
- **Ekonomia i koszt**: Najniższy koszt jednostkowy, dający najwyższy długoterminowy zwrot z inwestycji (ROI).
- **Zasada**: SERVICE to systemowa profilaktyka. Zaniedbany serwis bezpośrednio prowadzi do wysypu błędów BUGFIX, które w warunkach stresowych eskalują do katastrofy URGENT.

### 2. Reguły Kolejkowania dla Developera Taskand

1. **Bezwzględna preempcja URGENT**: Gdy w kolejce pojawia się zadanie ze znacznikiem `URGENT` (lub `tier: floor`), planista i orkiestrator Taskand natychmiast zamrażają bieżące wątki typu FEATURE/SERVICE, zabezpieczają stan transakcji i kierują wszystkie dostępne zasoby na izolację i naprawę problemu.
2. **Limit zaległości BUGFIX (WIP Gate)**: Jeśli w rejestrze projektu znajduje się więcej niż `N` nierozwiązanych bugów, planista odrzuca generowanie planów dla nowych zadań typu FEATURE, kierując model GLM na drenaż kolejki naprawczej.
3. **Ciągły Serwis w tle (Idle & Background Service)**: Gdy kolejki URGENT i BUGFIX są puste, a zadania FEATURE oczekują na zatwierdzenie człowieka lub dane zewnętrzne, agent uruchamia procesy SERVICE: optymalizację indeksów, audyt nieużywanych paczek, weryfikację integralności sum SHA-256 i odświeżanie cache.

### 3. Odwzorowanie na Standard `wellmanifest/priority`

| Poziom Workflow | Warstwa `wellmanifest/priority` | Modyfikator wagi i zachowanie |
|---|---|---|
| **URGENT** | `tier: floor` | Brak możliwości przeważyenia przez jakąkolwiek sumę innych prac; waga eskaluje z upływem czasu. |
| **BUGFIX** | `tier: standard` (wysoka waga) | Mnożnik bazowy x2.0 względem feature; zapobiega przedawnieniu. |
| **FEATURE** | `tier: standard` (waga nominalna) | Standardowa ewaluacja wag według wartości biznesowej. |
| **SERVICE** | `tier: opportunistic` / standing | Uruchamiane przy wolnych zasobach; w przypadku zaniedbania eskaluje do BUGFIX. |

<!-- docs:section limitations -->
## Limitations

Standard opisuje reguły szeregowania i decyzji architektonicznych. Nie stanowi samodzielnego upoważnienia do modyfikacji kodu w środowisku produkcyjnym, restartowania klastra ani usuwania danych bez uprzedniej weryfikacji w piaskownicy (Digital Twin).

<!-- docs:section next_actions -->
## Next actions

1. Zaimplementować filtrację i wagowanie priorytetów w plannera taskand (`semcod/taskand/glm53`).
2. Wdrożyć sprawdzanie zgodności priorytetów w module `monag resume` w celu rekomendowania właściwego zadania do podjęcia przez agenta.
3. Zaktualizować szablony ticketów w `new-project` o jawne pole `classification.kind` (`URGENT` | `BUGFIX` | `FEATURE` | `SERVICE`).
