# Standard informacji i planów refaktoryzacji — wellmanifest/docs 0.1.1

Słowa MUSI, NIE WOLNO i POWINIEN określają odpowiednio wymaganie, zakaz i zalecenie. `policy.json` jest kanonicznym katalogiem ścieżek, metadanych i sekcji; ten dokument opisuje ich znaczenie. HOME standardu: wellmanifest; projekty Subactor ADOPT ten pakiet i pozostają właścicielami swojego kodu oraz informacji.

## DOCS-001 — Zakres

Profil Subactor obowiązuje każde repozytorium `subactor/*`, obecne i przyszłe: usługi, biblioteki, CLI, agentów, standardy produktowe i repozytoria dokumentacji. Obejmuje nowe i zmieniane informacje trwałe, analizy, decyzje i plany refaktoryzacji. Istniejącej historii nie przepisuje się masowo; migracja dokumentu następuje przy jego następnej merytorycznej zmianie. Obowiązywanie wytycznej i potwierdzona adopcja w CI to dwa odrębne stany.

## DOCS-002 — Miejsce dokumentu ustala się przed pracą

Przed badaniem albo pisaniem agent/operator MUSI wskazać repozytorium właściciela, rodzaj dokumentu i docelową ścieżkę, np. `subactor/core:docs/refactoring/publication-controller.md`. Jeśli istnieje rejestr artefaktów, najpierw rozwiązuje w nim dokument i jego źródło wersji. Nie tworzy drugiego rejestru ani kopii istniejącego dokumentu.

Domyślne lokalizacje wewnątrz repozytorium:

| Rodzaj | Ścieżka |
| --- | --- |
| Informacja trwała | `docs/information/<id>.md` |
| Analiza i raport badania | `docs/analysis/<id>.md` |
| Plan refaktoryzacji | `docs/refactoring/<id>.md` |
| Decyzja architektoniczna | `docs/decisions/<id>.md` |
| Indeks | `docs/README.md` |

Identyfikator jest stabilny; poprawki aktualizują wersję dokumentu zamiast tworzyć REPORT-final-v2-new.md. Zmiana znaczenia lub aktualizacja ustaleń MUSI zwiększyć `version` i zaktualizować `updated`; historyczny stan pozostaje w Git. Repozytorium może mieć wcześniejszy system wersjonowania append-only — zachowuje go i wskazuje kanoniczny dokument, bez przepisywania starych wersji.

Wynik przekrojowy dotyczący kilku repozytoriów ma jednego właściciela: `subactor/docs`. W tym dedykowanym repo katalog główny pełni rolę dokumentacji: używa się `architecture/{information,analysis,refactoring,decisions}/<id>.md` i indeksu `README.md`. Pozostałe repozytoria zawierają odnośnik do kanonicznego dokumentu, nie jego pełne kopie. Dokument lokalnej zmiany może wskazywać zależności z innych repo bez przejmowania ich odpowiedzialności.

## DOCS-003 — Dokumentacja a dane robocze

Końcowy raport lub plan NIE MOŻE istnieć wyłącznie w `$HOME/.local/state`, `/tmp`, katalogu sesji agenta, czacie ani `project/ticket-*`. Te miejsca nie zastępują wersjonowanego rezultatu. Ticket przechowuje bounded intent i odnośnik do dokumentacji, nie drugi plan.

Surowe logi, pełne transkrypcje, sekrety, bazy robocze, backupy i Git bundle NIE SĄ dokumentacją do publikacji. Pozostają w prywatnym, ignorowanym magazynie zgodnym z przyjętym standardem recovery/continuity. Dokument może wskazać bezpieczny identyfikator receiptu i digest; nie przenosi się całego magazynu do `docs/` tylko po to, by był blisko repozytorium. Ścieżka lokalna nie jest trwałym dowodem dostępnym całemu zespołowi.

## DOCS-004 — Metadane i jakość informacji

Dokument MUSI mieć nagłówek JSON pomiędzy separatorami `---`, zgodny z szablonem. Zawiera właściciela, wersję, status, zakres repozytoriów, dokładną rewizję źródła, daty i referencje dowodowe. `review_after` oznacza termin ponownego sprawdzenia, nie automatyczną utratę historii. Przeterminowany dokument nie może być przedstawiany jako świeża obserwacja.

Fakty, hipotezy i rekomendacje MUSZĄ być odróżnione. Pomiary podają zakres, metodę, wykluczenia, rewizje i ograniczenia. Liczba linii lub podobieństwo tekstowe nie dowodzą błędu ani szkodliwej duplikacji. Celowe kopie zarządzanych standardów oraz projekcje jednego źródła oznacza się jako adopcję/projekcję.

Dowód MUSI być konkretną referencją do kodu w rewizji, testu, obserwacji lub receiptu. Nie wolno wymyślać wyników testów, utożsamiać exit code z osiągniętym celem ani traktować starego raportu jako bieżącego stanu wdrożenia. Brak dowodu oznacza jawnie opisaną lukę.

## DOCS-005 — Plan refaktoryzacji

Plan MUSI wyjaśniać problem i mierzalny cel, stan obecny, zakres i non-goals, dowody, odpowiedzialności docelowe, kolejność małych zmian, kompatybilność, kryteria odbioru, testy, rollback, ryzyka oraz właściciela każdej części. Nie wolno zastępować go listą poleceń dla agenta ani postulatem „przepisać całość”.

Migracja obejmuje zależności między etapami i warunek zatrzymania. Kryteria odbioru opisują zachowanie, np. „równoległe żądania tego samego efektu dają jeden efekt”, a nie wyłącznie liczbę nowych plików. Przy zmianie stanów, serializacji, hashy, schematów lub authority wymagane są testy zgodności starych i nowych konsumentów oraz strategia odczytu historycznych danych.

Usuwanie duplikatów zaczyna się od ustalenia właściciela i kontraktu. Współdzieli się równoważne reguły, nie funkcje tylko dlatego, że podobnie wyglądają. Jedno źródło może mieć adaptery dla różnych języków i wspólne wektory testowe. Rozdzielenie uprawnień CI, Review i Merge musi zostać zachowane.

## DOCS-006 — Status nie jest uprawnieniem

`draft`, `proposed`, `accepted`, `implemented` i `superseded` opisują dokument. Nawet `accepted` nie jest zgodą na deploy, odczyt sekretów, usunięcie gałęzi ani merge. Właściwy proces wymaga własnego, aktualnego uprawnienia i dowodu. Raport analizy nie zamyka automatycznie ticketów i nie generuje commitów zamykających.

## DOCS-007 — Odkrywalność i odbiór

Dokument MUSI być śledzony przez Git i podlinkowany w indeksie dokumentacji. Końcowa odpowiedź agenta wskazuje ścieżkę w repozytorium oraz stan publikacji: lokalny plik, commit, PR, merged. Nie wolno przedstawiać pliku lokalnego jako opublikowanej dokumentacji.

Sekcje szablonów mają stabilne znaczniki `<!-- docs:section ... -->`, dlatego tytuły mogą być po polsku lub w języku projektu. Każda wymagana sekcja zawiera treść; nieadekwatność wymaga krótkiego uzasadnienia. Szablon z niewypełnionymi `{{...}}` nie jest gotowym rezultatem.

## DOCS-008 — Adopcja i egzekwowanie

Każdy `subactor/*` MUSI posiadać przypięcie `.governance/docs.json` i odnośnik w instrukcjach agentów do opublikowanej rewizji pakietu. Istniejący proces CI/OneDev wywołuje checker z zaufanej instalacji standardu. Nie tworzy się dodatkowego workflow GitHub tylko dla tej bramy.

Przypięcie zawiera `schema`, `repository`, `standard`, `source_revision` i `policy_sha256`. Źródło to pełny SHA opublikowanego standardu; ruchomy `main`, skrócony SHA i samo słowo „latest” są niewystarczające. Checker porównuje hash polityki i rewizję ze swoim zaufanym wejściem. PR nie może sam wybrać słabszego standardu ani ustawić zaufanej rewizji w miejsce chronionej konfiguracji CI.

Adopcja przebiega: audyt read-only → wskazanie właściciela dokumentacji → bounded PR z manifestem, indeksem i podłączeniem istniejącej bramy → weryfikacja → chroniona publikacja. Nowe repo otrzymuje to w seedzie; istniejące w normalnej zmianie integracyjnej. Fleet audit raportuje brak adopcji jako brak, nie jako zgodność.

Checker obejmuje dokumenty tego profilu w Git oraz jawnie wskazane `--deliverable`. Nie widzi wszystkich plików zapisanych przez agenta poza repozytorium i nie dowodzi prawdziwości treści. Dlatego deklaracja ścieżki przed pracą, przegląd merytoryczny i sprawdzenie publikacji pozostają konieczne. Zachowanie historycznych formatów nie uprawnia do omijania profilu dla nowego rezultatu.


### Odkrywanie zmian względem bazy

Brama publikacji MUSI przekazać zaufany `--base`. Checker obejmuje również każdy nowy lub zmieniony, śledzony plik Markdown względem tej bazy, nawet bez metadanych. Niezmienione dokumenty historyczne pozostają poza migracją. Zastąpienie dokumentu dowiązaniem lub usunięcie metadanych nie usuwa go z kontroli.

`policy.json/discovery` jawnie wyłącza pliki organizacyjne: indeksy README, instrukcje agentów, changelog, TODO, konwencjonalne instrukcje współpracy i bezpieczeństwa, katalogi konfiguracji governance/CI/hostów oraz bezpośrednie pliki Markdown ticketów. Wyjątki dotyczą tylko automatycznego odkrywania: dokument rozpoznany jako zarządzany obecnie lub w bazie, albo wskazany przez `--deliverable`, nadal podlega pełnej kontroli. Nie wolno używać pliku organizacyjnego jako jedynego miejsca raportu końcowego. Kontrola bez bazy jest audytem istniejącego profilu, nie pełną bramą nowych rezultatów; nie wykrywa nieśledzonych plików bez jawnego `--deliverable`.
