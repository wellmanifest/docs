# Standard informacji i planów refaktoryzacji — wellmanifest/docs 0.3.0

Słowa MUSI, NIE WOLNO i POWINIEN określają odpowiednio wymaganie, zakaz i zalecenie. `policy.json` jest kanonicznym katalogiem ścieżek, metadanych i sekcji; ten dokument opisuje ich znaczenie. HOME standardu: wellmanifest; projekty Subactor ADOPT ten pakiet i pozostają właścicielami swojego kodu oraz informacji.

Nowe krótkie dokumenty POWINNY używać profilu kompaktowego v2 (DOCS-009).
Reguły metadanych, ścieżek i sekcji DOCS-002/004/005 opisują format v1;
dla v2 zastępuje je DOCS-009. Zasady właściciela, dowodów i uprawnień są wspólne.

## DOCS-009 — Profil kompaktowy v2

Jeden plik opisuje jeden problem, zmianę, decyzję albo procedurę. Nazwa MUSI
określać temat i rezultat: `PROVIDER_DNS_CHANGE_DETECTION.md`, a nie
`REPORT.md`, `SUMMARY_FINAL_V2.md` czy `URGENT_FIX.md`. Używamy ASCII
`UPPER_SNAKE_CASE.md`: wielkie litery w nazwie, podkreślniki, rozszerzenie
małe `.md`. Stabilne `id: provider-dns-change-detection` daje tę samą nazwę
przez zamianę myślników na podkreślniki i wielkie litery; id zaczyna się literą.
Wersja, data i priorytet nie należą do nazwy.

| kind | Katalog | Zawartość |
| --- | --- | --- |
| bugfix | docs/BUGFIX/ | Objaw, przyczyna, poprawka, dowód regresji |
| feature | docs/FEATURE/ | Nowe zachowanie, zakres, użycie i odbiór |
| service | docs/SERVICE/ | Utrzymanie, obsługa lub procedura operacyjna |
| information | docs/INFORMATION/ | Trwała instrukcja lub opis kontraktu |
| analysis | docs/ANALYSIS/ | Pytanie, metoda, ustalenia i ograniczenia |
| refactoring-plan | docs/REFACTORING/ | Mała zmiana struktury, zgodność i migracja |
| decision | docs/DECISION/ | Wybór, alternatywy i konsekwencje |

Obowiązuje istniejący wyjątek układu `subactor/docs` z prefiksem
`architecture/` i indeksem `README.md`. Raport organizacyjny nadal należy do
`org/report`. Profil można adoptować w dowolnym repo; `--fleet` nadal
obejmuje wyłącznie lokalne checkouty Subactor.

Nie tworzymy katalogu URGENT. Pilność to `priority: P0|P1|P2|P3`;
P0/P1 oznaczają pilne prace zgodnie z klasyfikacją projektu. Poprawka pozostaje
w BUGFIX po obniżeniu priorytetu. Rodzaj opisuje dokument, nie nadaje uprawnień
i nie zastępuje klasyfikacji ticketu. Nie tworzymy pustych katalogów na zapas.

[Szablon COMPACT.md](templates/COMPACT.md) ma 12 wymaganych pól JSON
i cztery sekcje: `summary`, `details`, `validation`, `risks`.
Tytuł nazywa rezultat; summary w 1–3 zdaniach podaje cel i stan.
Details mieści zakres, przyczynę lub decyzję; analysis odróżnia fakty od hipotez.
Validation podaje kryterium, metodę i wynik lub jawną lukę.
Risks podaje zgodność, rollback, odpowiedzialnego i następny krok, o ile dotyczą.
Refaktoryzacja zachowuje zależności etapów i warunek zatrzymania; bugfix
wskazuje odtwarzalny objaw i test regresji. Sekcje nie mogą być puste.

Limity MUSZĄ być spełnione jednocześnie: **120 linii, 600 słów, 12288 bajtów
UTF-8** całego pliku, również JSON, tabel i kodu. Słowo to token oddzielony
białymi znakami. Docelowo 40–80 linii i 150–400 słów. Limity są początkowym
budżetem redakcyjnym; nie gwarantują jakości. Nie wolno usuwać istotnych
ograniczeń ani dowodów, by zmieścić tekst. Podzielić go na samodzielne tematy,
połączyć linkami i dodać krótkie opisy do indeksu. Logi i pełne wyniki testów
pozostają artefaktami; procedury błędów należą do runbooków `errors/{CODE}.md`
standardu logs i są linkowane.

V2 usuwa duplikowane created/review_after/affected_repositories; historię dat
zapewnia Git, datę obserwacji updated, właściciela owner i zakres scope.
source_revision nadal wiąże pełny SHA badanego źródła, evidence podaje konkretne
referencje. Zmiana ustaleń zwiększa version; updated musi opisywać rzeczywisty
przegląd. Wymóg aktualności pozostaje merytoryczny: v2 nie emituje automatycznego
ostrzeżenia review_after. Status dokumentu nie jest statusem wdrożenia.

### Changelog i migracja

Changelog POWINIEN zawierać jedno zdanie o skutku dla użytkownika i względny
link do dokumentu, np.:

```markdown
- Wykrywanie zmiany adresu providera — [opis](docs/FEATURE/PROVIDER_DNS_CHANGE_DETECTION.md).
```

Szczegóły, polecenia i dowody należą do dokumentu. Nie tworzymy dokumentu dla
każdej literówki; samodzielny opis ma być użyteczny poza historią commitu.
Indeks `docs/README.md` zawiera temat i krótkie objaśnienie, bez kopii treści.
Preferowane są linki do całych plików. Checker weryfikuje lokalne cele Markdown
w śledzonym CHANGELOG.md (inline i definicje referencyjne), również usunięte
lub nieśledzone pliki i dowiązania. Nie sprawdza sieci ani kotwic renderera;
nie ocenia długości zdań i trafności opisu. Przykłady w fenced code są pomijane.

Format v1 i jego dotychczasowe ścieżki pozostają obsługiwane. Brama nie wymusza
masowej konwersji ani nie uznaje v1 za dowód adopcji v2. Migrację planujemy przy
merytorycznej zmianie: spis linków, podział tematów, aktualizacja indeksu
i changelogu w jednym diffie, kontrola odnośników. Zachować dawny plik jako
mapę do nowych tematów i dotychczasowe kotwice dla starszych linków; nie
przepisywać opublikowanej historii wydań. W razie zmiany rodzaju utrzymać
stare wejście na czas migracji. Nie kopiować pełnej treści do dwóch katalogów.

Preflight dla v2 jawnie wybiera format:

```bash
python3 "$DOCS_STANDARD_ROOT/docs/standard/check.py" \
  --root . --standard-revision "$DOCS_STANDARD_REVISION" --prepare --format v2 \
  --scope repository --kind feature --id provider-dns-change-detection \
  --deliverable docs/FEATURE/PROVIDER_DNS_CHANGE_DETECTION.md
```

Po zapisaniu i git add uruchomić checker z zaufanym `--base` i
`--deliverable`. Przygotowanie bez `--format` zachowuje v1 dla dotychczasowych
generatorów. Nowy pin i ustawienie v2 w generatorze wymagają adopcji konsumenta;
wdrożenie źródła standardu nie oznacza wdrożenia na flocie.

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

Nowy lub merytorycznie zmieniany wynik MUSI deklarować `scope` i dokładny `owner` w postaci `org/repo`. Dla `scope: repository` właścicielem pozostaje konkretne repozytorium, również gdy analiza wskazuje zależności z innych repo. Dla `scope: organization` właścicielem jest `[org]/report`, np. `subactor/report:docs/analysis/subactor-fleet-audit-2026-09-13.md`. Liczba `affected_repositories` nie zastępuje decyzji o odpowiedzialności. Raport kilku organizacji musi mieć wskazaną organizację odpowiedzialną; nie wolno zgadywać właściciela ani powielać całego raportu.

Przed utworzeniem repozytorium operator MUSI sprawdzić jego istnienie i rejestr artefaktów. Błąd dostępu lub sieci nie jest dowodem nieistnienia. Jeśli `[org]/report` naprawdę nie istnieje, tworzy je wyłącznie uprawniony proces w zaakceptowanej widoczności, z wymaganym seedem standardów i chronioną publikacją. Checker nie tworzy repozytoriów. Brak uprawnienia, nieustalony właściciel albo brak adopcji zatrzymuje generowanie trwałego wyniku; nie uprawnia do publikowania go w `/tmp`.

Historyczne dokumenty przekrojowe w `subactor/docs` zachowują dotychczasowe ścieżki `architecture/{information,analysis,refactoring,decisions}/<id>.md` i indeks `README.md`. Brak `scope` jest tolerowany wyłącznie przy audycie lub dla dokumentu niezmienionego względem zaufanej bazy. Przy zmianie trzeba ustalić aktualnego właściciela: dokument repozytorium wiedzy może pozostać lokalny, raport całej organizacji trafia do `org/report` z odnośnikiem migracyjnym. Nie kasuje się historii ani nie wykonuje masowej migracji archiwów.

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

### Brama przed generowaniem i operacją

Generator lub agent MUSI najpierw rozwiązać obowiązujące standardy i istniejący artefakt w rejestrze, następnie wywołać zaufany checker z `--prepare --root ... --scope ... --kind ... --id ... --deliverable ...`. Wynik `ok: false` lub niezerowy kod zatrzymuje generator przed zapisem raportu. Kontrola wymaga przypięcia adopcji, właściwego repozytorium, śledzonego indeksu i bezpiecznej ścieżki bez dowiązań. Wynik `delivery-plan/v1` zawiera właściciela, ścieżkę, pin i digest polityki oraz digest planu.

Plan jest dowodem wyboru miejsca, NIE uprawnieniem do operacji i NIE poświadczeniem niezmienności środowiska. Konsument wiąże go z bieżącym zadaniem, sprawdza ponownie przed zapisem po zmianie wejść, nie nadpisuje istniejącego raportu bez kontroli wersji i po generowaniu uruchamia pełny checker z zaufaną bazą i jawnym rezultatem. Odbiór wymaga osobno chronionej publikacji. Błąd późniejszej kontroli oznacza niedostarczony rezultat, nawet jeśli plik został zapisany lokalnie.

Operacje deploy, merge, czyszczenie, publikacja i generowanie artefaktów nietekstowych nadal wymagają właściwego standardu domenowego, intencji i uprawnienia. DOCS nie zastępuje tych bram. Instrukcja w AGENTS albo nowy parametr CLI nie jest dowodem wdrożenia: odbiór automatyzacji MUSI wykazać, że konsument odmawia zapisu po błędzie preflight i odmawia publikacji po błędzie kontroli końcowej. Raport adopcji odróżnia opublikowaną regułę, podłączony generator i chronioną bramę każdego konsumenta.


### Odkrywanie zmian względem bazy

Brama publikacji MUSI przekazać zaufany `--base`. Checker obejmuje również każdy nowy lub zmieniony, śledzony plik Markdown względem tej bazy, nawet bez metadanych. Niezmienione dokumenty historyczne pozostają poza migracją. Zastąpienie dokumentu dowiązaniem lub usunięcie metadanych nie usuwa go z kontroli.

`policy.json/discovery` jawnie wyłącza pliki organizacyjne: indeksy README, instrukcje agentów, changelog, TODO, konwencjonalne instrukcje współpracy i bezpieczeństwa, katalogi konfiguracji governance/CI/hostów oraz bezpośrednie pliki Markdown ticketów. Wyjątki dotyczą tylko automatycznego odkrywania: dokument rozpoznany jako zarządzany obecnie lub w bazie, albo wskazany przez `--deliverable`, nadal podlega pełnej kontroli. Nie wolno używać pliku organizacyjnego jako jedynego miejsca raportu końcowego. Kontrola bez bazy jest audytem istniejącego profilu, nie pełną bramą nowych rezultatów; nie wykrywa nieśledzonych plików bez jawnego `--deliverable`.
