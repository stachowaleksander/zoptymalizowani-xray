# Otwarte kontrakty — Zoptymalizowani X-Ray

Rejestr miejsc, w których implementacja dotyka niejednoznaczności metodologicznej.

Plik ma trzy sekcje i nie wolno ich mieszać:

- **Sekcja A — odwołania.** Kontrakty świadomie pozostawione otwarte przez
  ZOP-MASTER-01 v1.2 rozdz. 17. Nie są nowymi lukami. Zapisujemy tu wyłącznie
  *miejsce styku z kodem* oraz przyjęte założenie robocze, żeby dało się je
  odnaleźć, gdy kontrakt macierzysty będzie domykany.
- **Sekcja B — nowe otwarte kontrakty.** Realne luki i sprzeczności odsłonięte
  przez implementację, w formacie z CLAUDE.md. Aleksander przedstawia je Michałowi.
- **Sekcja C — rozstrzygnięte.** Wpisy zamknięte decyzją. Zachowują pełną treść wraz
  z odrzuconymi wariantami, bo uzasadnienie decyzji jest tak samo częścią śladu jak
  ona sama. Wpisu rozstrzygniętego nie otwiera się ponownie bez nowego faktu.

Zasada z MASTER v1.2 pkt 17.1 obowiązuje: kontraktów nie domykamy „dla kompletności
dokumentacji", tylko wtedy, gdy konkretna ścieżka implementacji tego wymaga.

**Założenie i decyzja to dwa różne stany.** Dopóki wpis jest otwarty, kod nosi
komentarz `# ASSUMPTION:`. Po rozstrzygnięciu komentarz zmienia się na
`# DECYZJA (Michał, RRRR-MM-DD):` z numerem wpisu. Po samym kodzie ma być widać,
czy coś jest przyjętym założeniem, czy podjętą decyzją.

---

## Sekcja A — odwołania do kontraktów otwartych w MASTER v1.2

Brak wpisów otwartych.

---

## Sekcja B — nowe otwarte kontrakty

### B-07 — jesienna zmiana czasu: dwa instanty, jedna lokalna godzina

**Dokument i miejsce:** DT-05, wariant A zatwierdzony 2026-09-14 (konwersja znaczników ze
strefą na czas lokalny organizacji wg `organization_timezone` z profilu), wobec zasady 5
z CLAUDE.md oraz uzasadnienia samego wariantu A: nie wolno tracić informacji kompletnej.
Konsumenci skutku: przyszłe miary czasu etapów w ZOP-XR-PROC-01 i ZOP-XR-PROC-02.

**Na czym polega niejednoznaczność:** w `Europe/Warsaw` ostatniej niedzieli października
godzina 02:00–02:59 czasu lokalnego występuje dwa razy:

| Instant źródłowy | Czas lokalny |
| --- | --- |
| `2026-10-25T00:30Z` | 02:30 czasu letniego (UTC+02:00) |
| `2026-10-25T01:30Z` | 02:30 czasu zimowego (UTC+01:00) |

Po konwersji na naiwny czas lokalny oba dają `2026-10-25 02:30` — dwa różne instanty,
jedna wartość. Python rozróżnia je atrybutem `fold`, ale kolumna `datetime64[ns]`, której
typ wyznacza DT-08, go gubi (sprawdzone 2026-09-14: po odczycie z ramki oba mają `fold=0`).
Wiosną problemu nie ma: luka 02:00–02:59 nie istnieje lokalnie, a konwersja **do** czasu
lokalnego nigdy jej nie wyprodukuje.

Poza zakresem wpisu: znacznik, który przychodzi od klienta **już naiwny** i leży w tej
godzinie, jest niejednoznaczny u źródła. Tej informacji nie tracimy, bo nigdy jej nie było.

**Warianty interpretacji:**

- A — scalić w ramce bez śladu.
- B — odrzucić wiersz z własną kategorią odrzucenia.
- C — zachować `fold` w danych.
- D — scalić w ramce; pierwotną wartość źródłową i przesunięcie UTC czasu lokalnego zapisać
  w raporcie importu, obok kontraktu.
- E — nie konwertować wartości niejednoznacznych i pozwolić modelowi je odrzucić.

**Konsekwencja każdego wariantu dla kodu:**

- A — najprostsze; utrata nieodwracalna. Czasy etapów przechodzących przez tę godzinę mogą
  wyjść ujemne albo zawyżone o godzinę, a żadna z ośmiu kontroli tego nie zobaczy.
- B — nowa kategoria wchodzi do semantycznego zestawienia odrzuceń, a więc do `run_id`;
  ginie cały rekord (`case_id`, `stage`, drugi znacznik), czyli więcej informacji niż sama
  niejednoznaczna godzina.
- C — niewykonalne bez zmiany typu kolumny z DT-08 (kolumna obiektowa zamiast
  `datetime64[ns]`), a to zmienia sposób sprawdzania braku we wszystkich warstwach wyżej.
- D — kontrakt danych bez zmian; instant jest odtwarzalny z raportu (`row_id`, pole,
  przesunięcie). Konsument liczący czasy musi czytać raport importu, bo sama ramka tego nie
  powie.
- E — w praktyce B z kategorią „znacznik ze strefą", która myli przyczynę.

**Propozycja robocza (do zatwierdzenia przez Michała):** wariant D. Przyjęty 2026-09-14
jako **założenie tymczasowe**, nie decyzja. W kodzie konwersji oznaczony
`# ASSUMPTION: B-07`. Raport importu zawsze niesie licznik godzin niejednoznacznych, także
gdy wynosi 0 — brak pola znaczyłby jednocześnie „nie było" i „nie sprawdzaliśmy".

**Co blokuje:** nazwanie konwersji bezstratną; każdą przyszłą miarę czasu trwania, która
czyta wyłącznie ramkę (PROC-01, PROC-02) — do rozstrzygnięcia taka miara musi uwzględnić
raport importu albo jawnie ogłosić ograniczenie.

**Czego nie blokuje:** importu, konwersji pozostałych znaczników, kontroli 8, tożsamości
przebiegu ani odcisku wykonania.

---

## Sekcja C — rozstrzygnięte

Siedem wpisów rozstrzygniętych przez Michała: A-01 i B-01…B-05 dnia 2026-09-05,
B-06 dnia 2026-09-08.

Warianty robocze zatwierdzone przy A-01 i B-01…B-05 (A-01 i B-04 z zaostrzeniem).
**Przy B-06 wariant roboczy został odrzucony jako zbyt gruby** i zastąpiony mocniejszym
rozdzieleniem trzech stanów.

---

### A-01 — Etykieta okresu dla tabeli PROCESS

**Kontrakt macierzysty:** ZOP-MASTER-01 v1.2, rozdz. 17, wiersz
„kalendarze operacyjne / time_basis — różne procesy mają różne podstawy czasu —
wraca przy implementacji PROC/CAP". To **nie jest** nowy kontrakt.

**Miejsce styku z fundamentem:** ZOP-TECH-01 v0.1 pkt 5.3, kontrola 8 (zakres czasowy),
zastosowana do tabeli PROCESS.

**Na czym polega styk:** cztery pozostałe tabele bazowe niosą agregaty miesięczne
i mają `date` jako etykietę okresu. PROCESS niesie zdarzenia i ma czas rzeczywisty
w `start` / `end`. Etykieta okresu jest z nich wyliczalna, ale wynik zależy od
przyjętej podstawy: start sprawy, start etapu, koniec etapu albo zamknięcie sprawy.
Przypadek rozpoczęty w marcu i zamknięty w maju należy do innego miesiąca w każdym
z tych wariantów. Wybór podstawy jest regułą biznesową, nie decyzją techniczną,
a fundament nie zna jeszcze kart PROC-01 i PROC-02.

**Decyzja robocza z 2026-09-04 (Aleksander) — CZĘŚCIOWO UCHYLONA 2026-09-05.**
Punkty 1, 2 i 4 obowiązują. Punkt 3 (`time_basis_used = stage_start`) został
wycofany przez rozstrzygnięcie Michała poniżej. Treść zostaje, bo odrzucony wariant
jest częścią śladu.

1. Nie dodajemy pola `date` do PROCESS. Byłoby redundantne wobec `start` / `end`
   i zamrażałoby regułę biznesową, której TECH-01 nie rozstrzyga.
2. Kontrola zakresu czasowego dla PROCESS zwraca:
   `period_min` = min(`start`), `period_max` = max(`end`), `months_covered`,
   `months_without_events`, `time_basis_used`.
3. `time_basis_used` jest wartością jawną, nie domyślną. Na tym etapie `stage_start`,
   oznaczona w kodzie komentarzem `# ASSUMPTION:`.
4. `months_without_events` raportujemy jako **obserwację**, nie jako WARNING ani
   CRITICAL. W pozostałych tabelach brakujący miesiąc to luka w danych; w PROCESS
   może być miesiącem, w którym faktycznie nic nie przyszło, i bez referencji nie da
   się tych dwóch sytuacji rozróżnić. Zgodne z zasadą 5 z CLAUDE.md: brak informacji
   jest pełnoprawnym wynikiem, nie brakiem do wypełnienia.

**Co blokuje:** nic w zakresie ZOP-TECH-01.

**Czego nie blokuje:** importu, walidacji, kontraktu danych, struktury FINDINGS ani
generatora syntetycznego. Kontrola 8 jest wykonalna dla wszystkich pięciu tabel.

**Kiedy wraca:** przy implementacji PROC-01 / PROC-02 i CAP-01 / CAP-02, razem
z kontraktem macierzystym `time_basis`. Wtedy `time_basis_used` przestaje być
założeniem, a staje się wartością pochodzącą z karty.

**ROZSTRZYGNIĘCIE**

| | |
| --- | --- |
| Data | 2026-09-05 |
| Decydent | Michał (metodologia) |

**Treść decyzji:**

Nie rozstrzygamy teraz `time_basis`. Przechowujemy znaczniki czasu i **nie
przypisujemy procesu arbitralnie do miesiąca**. Podstawa przypisania będzie osobnym
kontraktem globalnym.

Robocze założenie `time_basis_used = stage_start` zostaje **wycofane** — nie zostaje jako
domyślna wartość ani jako założenie robocze. `DEFAULT_TIME_BASIS` znika z kodu. Kontrola 8
nie ma prawa wybrać sobie podstawy przypisania.

Co kontrola 8 dla PROCESS **może** zwracać:
- `period_min` = min(`start`), `period_max` = max(`end`) oraz rozpiętość między nimi —
  to jest **zakres danych**, a nie przypisanie,
- liczbę zdarzeń w miesiącu liczoną po **własnym znaczniku czasu zdarzenia**, bo
  zdarzenie ma jeden moment i nie wymaga wyboru podstawy,
- `months_without_events` — miesiące bez zdarzeń, nadal jako **obserwacja**, nie WARNING
  ani CRITICAL.

Czego kontrola 8 **nie może** robić: przypisywać sprawy (`case_id`) do miesiąca. Sprawa
rozpoczęta w marcu i zamknięta w maju nie należy do żadnego z nich, dopóki kontrakt
globalny nie powie, jak to liczyć.

`time_basis_used` zwraca `null` z jawną podstawą „kontrakt globalny nierozstrzygnięty" —
nigdy wybraną wartość.

---

### B-01 — brak oznaczenia korekty w tabeli COST

**Dokument i miejsce:** ZOP-TECH-01 v0.1 pkt 5.3, kontrola 5, wobec pkt 5.2 (COST).

**Na czym polega niejednoznaczność:** kontrola 5 brzmi „wartości podejrzane, np. ujemny
przychód lub koszt, **jeżeli nie został oznaczony jako korekta**". Minimalny zestaw pól
COST (`date`, `unit`, `category`, `amount`) nie zawiera żadnego pola pozwalającego na
takie oznaczenie. `exclusion_flags` z FIN-01 pkt 9 nie zamyka luki, bo działa na poziomie
okresu i zakresu analizy, a nie pojedynczego rekordu.

**Warianty interpretacji:**
- A — oznaczanie korekt jest poza zakresem TECH-01; walidator wyłącznie raportuje
  wartości ujemne, a rozstrzygnięcie należy do testu albo do ręcznej weryfikacji.
- B — COST otrzymuje opcjonalne pole korekty (np. `correction_flag`), wypełniane, gdy
  klient takie oznaczenie dostarczy.
- C — korekta jest rozpoznawana po `category` z profilu mapowania klienta, bez nowego
  pola w kontrakcie.

**Konsekwencja każdego wariantu dla kodu:**
- A — kontrakt COST bez zmian; kontrola 5 zwraca sygnał z podstawą i nigdy nie ustawia
  CRITICAL samodzielnie. Ujemna kwota pozostaje wartością dopuszczalną w modelu.
- B — zmiana bazowej struktury z pkt 5.2, czyli dotknięcie kontraktu, który wszystkie
  karty Core 10 deklarują jako niezmienny („rozszerzenia nie zmieniają bazowej struktury
  ZOP-TECH-01"). Wymaga decyzji na poziomie karty, nie implementacji.
- C — brak zmiany kontraktu, ale reguła rozpoznania korekty przenosi się do profilu
  mapowania klienta i przestaje być audytowalna w jednym miejscu.

**Propozycja robocza (do zatwierdzenia przez Michała):** wariant A. Do czasu decyzji
walidator raportuje wartości ujemne jako sygnał z jawną podstawą, bez klasyfikowania ich
jako błędu, a model COST dopuszcza `amount` ujemne bez ograniczenia.

**Co blokuje:** nic. **Czego nie blokuje:** kontraktu COST, importu, kontroli 5.

**ROZSTRZYGNIĘCIE**

| | |
| --- | --- |
| Data | 2026-09-05 |
| Decydent | Michał (metodologia) |

**Treść decyzji:**

Wariant A zatwierdzony. Ujemny koszt pozostaje **sygnałem walidacyjnym**
z jawną podstawą. Bez jawnego oznaczenia w danych nie klasyfikujemy go ani jako błędu,
ani jako korekty. Kontrakt COST nie zyskuje pola korekty.

---

### B-02 — słownik pola `status` w FINDINGS

**Dokument i miejsce:** ZOP-TECH-01 v0.1 pkt 5.4 wobec ZOP-PRI-01 v1.0 rozdz. 8
oraz statusów logicznych kart Core 10.

**Na czym polega niejednoznaczność:** TECH-01 pkt 5.4 podaje dla `status` słownik
STANDARD / MEDIUM / HIGH / CRITICAL. FIN-01 pkt 12.1, PROC-01 pkt 12.1, PORT-01 pkt 13.1
i HR-01 rozdz. 13 potwierdzają ten słownik, ale przypisują jego nadawanie do ZOP-PRI-01.
PRI-01 v1.0 tego słownika nie zawiera w ogóle — jego zamknięte katalogi (rozdz. 8) to
`problem_priority_action` (review_now; review_next; plan_review; observe; not_assessable),
`validation_priority_action` oraz `management_attention_route`. Jednocześnie karty
opisują `status` w FINDINGS jako **status logiczny testu**, wyraźnie odróżniony od
priorytetyzacji (FIN-01 pkt 12.2: „to statusy diagnostyczne, nie wynik globalnej
priorytetyzacji"; CAP-02 rozdz. 21: „CRITICAL pozostaje wyłącznie wynikiem walidacji
danych").

**Druga niejednoznaczność — sam katalog statusów logicznych nie jest jednolity:**
- PROC-02 pkt 16.1 („zachowuje wspólny katalog"), PORT-01 13.1, PROC-01 12.1,
  FIN-03 rozdz. 14, CAP-02 rozdz. 21, MGT-01 rozdz. 16: NO_ADVERSE_SIGNAL;
  ADVERSE_SIGNAL; INCIDENT; DETERIORATING; STABLE; IMPROVING; TEST_PARTIAL; TEST_BLOCKED.
- FIN-01 pkt 12.2 i CAP-01 rozdz. 7: zamiast `ADVERSE_SIGNAL` występuje
  `SHORT_TERM_DEVIATION`.
- CAP-01 dodatkowo zawiera wiersz `VOLATILE / SEASONAL`, z którego nie wynika, czy to
  jedna wartość, czy dwie. Sąsiedni wiersz `TEST_PARTIAL / TEST_BLOCKED` sugeruje dwie,
  ale to przesłanka z formatowania tabeli, nie z treści karty.

**Warianty interpretacji:**
- A — `status` niesie status logiczny; STANDARD/MEDIUM/HIGH/CRITICAL to słownik
  porzucony, wycofany całkowicie; priorytet mieszka wyłącznie w polach PRI-01.
- B — jak A, ale STANDARD/MEDIUM/HIGH/CRITICAL zostaje jako osobne, odrębne pole
  FINDINGS zasilane przez PRI-01.
- C — `status` pozostaje polem priorytetu wg TECH-01, a status logiczny dostaje własne
  pole.

**Konsekwencja każdego wariantu dla kodu:**
- A — jeden enum statusu logicznego; brak pola priorytetowego poza katalogami PRI-01.
- B — jeden enum statusu logicznego plus drugi enum, którego żadna karta dziś nie
  definiuje; PRI-01 musiałby zostać rozszerzony, a jest ZAMROŻONY.
- C — sprzeczne z jednoznacznym opisem `status` jako statusu logicznego we wszystkich
  dziewięciu kartach, które to pole opisują.

**Propozycja robocza (do zatwierdzenia przez Michała):** wariant A. `status` w FINDINGS
niesie status logiczny testu. Enum obejmuje dziewięć wartości: osiem ze wspólnego
katalogu plus `SHORT_TERM_DEVIATION` z FIN-01 i CAP-01. `VOLATILE` / `SEASONAL`
świadomie **nie** wchodzą do enumu do czasu implementacji CAP-01 — nie zgadujemy, czy
to jedna wartość, czy dwie. W kodzie oznaczone `# ASSUMPTION:`.

**Co blokuje:** nic na etapie fundamentu; NOOP-01 używa wyłącznie `NO_ADVERSE_SIGNAL`,
które występuje w każdej karcie bez wyjątku. **Czego nie blokuje:** kontraktu FINDINGS,
zapisu, śladu audytowego.

**ROZSTRZYGNIĘCIE**

| | |
| --- | --- |
| Data | 2026-09-05 |
| Decydent | Michał (metodologia) |

**Treść decyzji:**

Wariant A zatwierdzony. Słownik STANDARD / MEDIUM / HIGH / CRITICAL jest
**historycznym zapisem ZOP-TECH-01 v0.1** i zostaje **wycofany**. Nie implementujemy go
jako priorytetu — ani teraz, ani później, ani jako osobnego pola.

`status` w FINDINGS niesie status logiczny testu. Priorytet mieszka wyłącznie
w kontraktach ZOP-PRI-01.

`VOLATILE` / `SEASONAL` z ZOP-XR-CAP-01 pozostają poza enumem do czasu implementacji
CAP-01 — nie zgadujemy, czy to jedna wartość, czy dwie.

---

### B-03 — `confidence_class` w FINDINGS: katalog i liczba poziomów

**Dokument i miejsce:** ZOP-TECH-01 v0.1 pkt 5.4 wobec ZOP-CONF-01 v1.0 pkt 2.1 i 2.2.

**Na czym polega niejednoznaczność:** TECH-01 pkt 5.4 opisuje `confidence_class` jako
„klasa pewności A / B / C". CONF-01 pkt 2.2 („Wspólny katalog klas") nie zna wartości
A/B/C — katalog to `well_supported`, `supported_with_limitations`, `partially_supported`,
`weakly_supported`, `not_assessable`. To ten sam rodzaj nieaktualnego zapisu w TECH-01
v0.1 co `confidence_score` 0–1, przy którym CONF-01 pkt 2.2 stwierdza dosłownie:
„ZAKAZ WSKAŹNIKA confidence_score = null".

**Druga część problemu:** CONF-01 pkt 2.1 rozdziela pewność na trzy niezależne poziomy —
`metric_confidence_class`, `finding_confidence_class`, `mechanism_confidence_class` —
i zakazuje przenoszenia klasy między poziomami („Klasa nie jest kopiowana automatycznie
między poziomami", QCONF01-183). Pojedyncze pole `confidence_class` w FINDINGS nie ma
odpowiednika w CONF-01 i nie da się jednoznacznie powiedzieć, który poziom niesie.

**Warianty interpretacji:**
- A — FINDINGS ma trzy pola klas zgodnie z CONF-01, a `confidence_class` z TECH-01
  znika jako zapis nieaktualny.
- B — FINDINGS zachowuje jedno pole `confidence_class` z jawnym
  `confidence_class_source_level` wskazującym poziom (CONF-01 pkt 3 zna to pole).
- C — FINDINGS zachowuje jedno pole i przyjmuje, że niesie `finding_confidence_class`.

**Konsekwencja każdego wariantu dla kodu:**
- A — trzy pola nullowalne; najbliżej karty, najdalej od TECH-01 pkt 5.4.
- B — jedno pole plus pole poziomu; zgodne z CONF-01 i nie łamie TECH-01.
- C — jedno pole; proste, ale zapisuje w kontrakcie założenie, którego karta nie robi,
  i traci pewność miary oraz mechanizmu.

**Propozycja robocza (do zatwierdzenia przez Michała):** wariant B. Na etapie fundamentu
i tak wszystkie te pola są `null` — CONF-01 nie jest implementowane. Enum klas budujemy
wg CONF-01 pkt 2.2, nie wg A/B/C.

**Co blokuje:** nic. **Czego nie blokuje:** kontraktu FINDINGS ani NOOP-01, który zapisuje
klasy jako `null`.

**Uwaga proceduralna:** B-03 dotyczy tej samej nieaktualności TECH-01 v0.1 co
`confidence_score`, którą Aleksander zgłasza już Michałowi jako poprawkę do TECH-01 v0.2.
Warto zgłosić oba zapisy razem.

**ROZSTRZYGNIĘCIE**

| | |
| --- | --- |
| Data | 2026-09-05 |
| Decydent | Michał (metodologia) |

**Treść decyzji:**

Wariant B zatwierdzony. Klas A / B / C **nie implementujemy** — to nieaktualny
zapis ZOP-TECH-01 v0.1. Obowiązuje katalog z ZOP-CONF-01 pkt 2.2.

Rozdzielenie pewności na miarę, wynik i mechanizm zostaje zgodnie z CONF-01 pkt 2.1:
klasy per poziom mieszkają w `ClaimRecord`, a `FindingRecord` niesie klasę przeniesioną
wraz z `confidence_class_source_level`. `confidence_score` pozostaje `null` na mocy
dosłownego zakazu z CONF-01 pkt 2.2.

---

### B-04 — znaczenie pola `metric` w tabeli PLAN

**Dokument i miejsce:** ZOP-TECH-01 v0.1 pkt 5.2 (PLAN) wobec ZOP-XR-FIN-01 v1.0
rozdz. 8, wiersz „plan / budżet".

**Na czym polega niejednoznaczność:** PLAN jest we wszystkich kartach opisana jako
możliwa referencja. FIN-01 rozdz. 8 dopuszcza plan jako źródło wartości odniesienia
pod warunkiem „zgodna definicja miary", ale żadna karta nie mówi, **skąd system ma
wiedzieć**, która wartość `metric` odpowiada mierze liczonej przez test. Bez tego
warunek „zgodna definicja miary" jest niesprawdzalny automatycznie: test nie ma jak
odnaleźć właściwego `target`.

**Warianty interpretacji:**
- A — `metric` to swobodny tekst klienta; dopasowanie do miary testu następuje przez
  profil mapowania klienta, tak samo jak dopasowanie kolumn.
- B — `metric` to słownik kontrolowany po stronie X-Ray; wartości spoza słownika są
  raportowane jako niedopasowane i nie mogą służyć jako referencja.
- C — plan w ogóle nie jest automatyczną referencją; użycie planu jako `reference_value`
  wymaga jawnego wskazania przez człowieka.

**Konsekwencja każdego wariantu dla kodu:**
- A — kontrakt PLAN bez zmian; `mapping/` zyskuje drugą odpowiedzialność obok mapowania
  kolumn: mapowanie wartości `metric` na miary testów. Ryzyko: dopasowanie staje się
  konfiguracją klienta, a nie regułą audytowalną w jednym miejscu.
- B — potrzebny zamknięty słownik miar, którego dziś nie ma żadna karta; zbudowanie go
  „z rozsądku" naruszałoby zasadę 1.
- C — plan pozostaje w danych, ale nie zasila automatycznie `reference_value`;
  najbezpieczniejsze metodologicznie, najuboższe funkcjonalnie.

**Propozycja robocza (do zatwierdzenia przez Michała):** fundament nie rozstrzyga.
Model przyjmuje `metric` jako tekst z danych klienta, niczego nie tłumaczy i nie
dopasowuje. Rozstrzygnięcie wraca przy pierwszym teście, który sięgnie po plan jako
referencję — czyli przy FIN-01 rozdz. 8.

**Co blokuje:** nic na etapie fundamentu. **Czego nie blokuje:** kontraktu PLAN,
importu, walidacji, kontroli zakresu czasowego.

**ROZSTRZYGNIĘCIE**

| | |
| --- | --- |
| Data | 2026-09-05 |
| Decydent | Michał (metodologia) |

**Treść decyzji:**

Wariant A zatwierdzony **z zaostrzeniem**: żadnego automatycznego dopasowania
PLAN do miary testu. Fundament ma **wymagać jawnego mapowania** i zgodności definicji.

Konsekwencja dla `mapping/`: kontrakt profilu mapowania zyskuje **czwarty element** obok
trzech list kolumn — deklarację mapowania miar planu. Deklaracja wskazuje, która wartość
`metric` odpowiada której mierze testu, wraz z podstawą zgodności definicji.

Brak takiej deklaracji **nie jest błędem importu**. Oznacza natomiast, że PLAN nie może
posłużyć jako `reference_type = plan_budget` (ZOP-XR-FIN-01 rozdz. 6, warunek „zgodna
definicja miary").

Model nadal nie normalizuje `metric` — wartość przechodzi taka, jaka przyszła. Zmienia
się to, że sam przepływ danych nie wystarcza: potrzebna jest jawna deklaracja obok.

---

### B-05 — powiązanie dowodu z twierdzeniem w CONF-01

**Dokument i miejsce:** ZOP-CONF-01 v1.0 rozdz. 3 (kontrakt twierdzenia) i rozdz. 4
(kontrakt dowodu).

**Na czym polega niejednoznaczność:** karta definiuje `claim_id` jako trwały
identyfikator twierdzenia oraz `evidence_id`, `evidence_group_id`
i `evidence_source_group_id` w kontrakcie dowodu, ale **nigdzie nie nazywa pola
wiążącego dowód z twierdzeniem**. W kontrakcie dowodu nie ma `claim_id`, a w kontrakcie
twierdzenia nie ma listy dowodów. Przeszukanie całej karty pod kątem `claim_evidence`,
`required_evidence` i `evidence_set` nie daje wyniku.

To **nie jest pytanie o nazwę pola, tylko o kardynalność**:

- jeżeli dowód należy do twierdzenia — relacja jest jeden-do-wielu,
- jeżeli ten sam dowód może wspierać kilka twierdzeń — relacja jest wiele-do-wielu.

Istnienie `evidence_group_id` („grupa rekordów opisujących ten sam dowód lub zdarzenie")
oraz `evidence_source_group_id` („grupa wspólnego źródła używana do ochrony
niezależności") przemawia za drugim odczytaniem: oba pola istnieją po to, żeby rozpoznać
wspólne pochodzenie dowodów używanych w różnych miejscach. Gdyby dowód należał na
własność do jednego twierdzenia, ochrona niezależności nie miałaby czego pilnować.

**Warianty interpretacji:**
- A — dowód należy do twierdzenia; `EvidenceRecord` nosi `claim_id`.
- B — dowód jest bytem niezależnym, a powiązanie z twierdzeniem jest jawnym rekordem
  wiążącym; ten sam dowód może być powiązany z wieloma twierdzeniami.
- C — dowód należy do wyniku (`finding_id`), a twierdzenia dziedziczą dowody wyniku.
  Sprzeczne z CONF-01 rozdz. 2.1, która zakazuje automatycznego dziedziczenia między
  poziomami twierdzeń.

**Konsekwencja każdego wariantu dla kodu:**
- A — najprostsze; ale ten sam dowód użyty przy dwóch twierdzeniach trzeba zduplikować,
  przez co `evidence_source_group_id` przestaje odróżniać duplikat od dwóch niezależnych
  źródeł — czyli traci swoją jedyną funkcję.
- B — jeden rekord wiążący więcej; ochrona niezależności działa, bo duplikacji nie ma.
- C — wymaga złamania zakazu dziedziczenia klas między poziomami.

**Propozycja robocza (do zatwierdzenia przez Michała):** wariant B, przez jawne
powiązanie, a nie przez własność.

Uzasadnienie jest **asymetryczne i to jest w nim najważniejsze**: wiele-do-wielu
degraduje się do jeden-do-wielu bez żadnej zmiany kodu — relacja po prostu nigdy nie ma
więcej niż jednego wiązania dla dowodu. Odwrotnie się nie da: jeden-do-wielu przerobione
później na wiele-do-wielu oznacza przepisanie zapisu i odczytu. Przy nierozstrzygniętej
karcie wybieramy wariant, który przetrwa oba rozstrzygnięcia.

**Co blokuje:** nic na etapie fundamentu — żaden kod nie wypełnia jeszcze dowodów.
**Czego nie blokuje:** kontraktu FINDINGS, NOOP-01, zapisu ani śladu.

**Kiedy wraca:** przy implementacji ZOP-CONF-01, czyli przy pierwszym teście
produkującym rekordy dowodowe.

**ROZSTRZYGNIĘCIE**

| | |
| --- | --- |
| Data | 2026-09-05 |
| Decydent | Michał (metodologia) |

**Treść decyzji:**

Wariant B zatwierdzony. Relacja wiele-do-wielu zostaje jako **architektura
bazowa**, przez jawne powiązanie `ClaimEvidenceLink`, a nie przez własność.

Dokładny kontrakt dowód–twierdzenie zostanie domknięty razem z implementacją
ZOP-CONF-01. Do tego czasu architektura jest ustalona i nie podlega ponownemu otwarciu.

---

### B-06 — co znaczy „kolumna wymagana" w kontroli 1

**Dokument i miejsce:** ZOP-TECH-01 v0.1 pkt 5.3, kontrola 1 („brak wymaganej kolumny")
wobec ZOP-XR-CAP-01 v1.0 pkt 4.1.

**Na czym polega niejednoznaczność:** TECH-01 pkt 5.3 wymienia brak wymaganej kolumny
jako kontrolę, a przykład („np. brak pola date, unit lub amount") sugeruje, że dotyczy to
każdego pola kontraktu. Tymczasem ZOP-XR-CAP-01 pkt 4.1 stwierdza wprost:
**„brak cost: miary fizyczne działają; economic_gap = null"** — czyli klient bez kolumny
`cost` ma być obsługiwalny, a nie odrzucony.

To **sprzeczność między kartą a kartą**, nie niespójność naszych zapisów.

**Kierunek rozstrzyga hierarchia z CLAUDE.md:** CAP-01 jest kartą zamrożoną i stoi wyżej
niż ZOP-TECH-01. Nie każde brakujące pole może więc dawać CRITICAL. Hierarchia **nie
rozstrzyga natomiast kryterium**: która kolumna jest wymagana, a która nie.

Dodatkowa okoliczność techniczna: w naszym kontrakcie żadne pole nie ma wartości
domyślnej, więc Pydantic wymaga **obecności** każdego z nich. Brak kolumny `cost` oznacza
dziś odrzucenie każdego wiersza RESOURCE — dokładnie to, czego CAP-01 zakazuje.

**Warianty interpretacji:**
- A — kryterium wynika z kontraktu: element `NATURAL_KEY` → CRITICAL, pole spoza klucza
  → WARNING i kolumna traktowana jak w całości pusta.
- B — wszystko CRITICAL, zgodnie z literą TECH-01.
- C — lista pól wymaganych deklarowana per tabela w konfiguracji albo w karcie.

**Konsekwencja każdego wariantu dla kodu:**
- A — kryterium jest maszynowo odczytywalne z `TableRecord.NATURAL_KEY`, więc nie ma
  drugiego źródła prawdy. Uzasadnienie jest wywodliwe: rekordu bez klucza nie da się
  przypisać do zakresu ani okresu, więc nie może uczestniczyć w audytowalnej agregacji;
  rekord bez `cost` może, tylko z węższym zakresem wniosków.
- B — klient bez jednej kolumny nieobowiązkowej nie przechodzi importu wcale. Sprzeczne
  z CAP-01 pkt 4.1.
- C — wprowadza drugie źródło prawdy obok kontraktu danych. Gdyby lista leżała w profilu
  klienta, klient mógłby ją skrócić i import przeszedłby bez pola wymaganego przez kartę:
  reguła metodologiczna wpełzłaby do danych wejściowych.

**Mechanizm dla wariantu A — materializacja pustej kolumny.** Brakująca kolumna spoza
klucza jest materializowana jako **w całości pusta**, a sama materializacja jest
odnotowana w raporcie mapowania. `None` oznacza tu **nieobecność kolumny**, a nie wartość
zastępczą wstawioną w miejsce danych — zasada 5 nie jest naruszona, ale to rozróżnienie
musi być widoczne w raporcie, a nie domyślane z liczby braków. Kontrola 3 pokaże wtedy
100% braków w tym polu, a `DiagnosticTestDeclaration.required_fields` pozwoli testowi
ogłosić `TEST_BLOCKED` albo `TEST_PARTIAL`.

**Propozycja robocza (do zatwierdzenia przez Michała):** wariant A. *(Michał poszedł dalej — patrz rozstrzygnięcie.)* Reguła jest wywodliwa
z kontraktu i zgodna z kartą zamrożoną, ale **definiuje zachowanie dla wszystkich
klientów**, więc wymaga potwierdzenia na poziomie metodologii, a nie implementacji.
W kodzie kontroli 1 oznaczone `# ASSUMPTION:`.

**Co blokuje:** nic. Hierarchia rozstrzyga kierunek, więc implementacja idzie dalej.

**Czego nie blokuje:** profilu mapowania, kontroli 1, importu ani magazynu.

**Kiedy wraca:** przy poprawce ZOP-TECH-01 do v0.2 — razem z zapisami o
`confidence_score` i `confidence_class`, które już czekają na tę samą korektę.

**ROZSTRZYGNIĘCIE**

| | |
| --- | --- |
| Data | 2026-09-08 |
| Decydent | Michał (metodologia) |

**Treść decyzji:**

Wariant A **odrzucony jako zbyt gruby**. Reguła „każde pole spoza klucza → WARNING" nadaje
ciężar, którego walidator nie zna. Zamiast dwóch stanów obowiązują **trzy**:

**1. `required_structurally`** — bez tego pola nie da się odpowiedzialnie zidentyfikować
rekordu ani zachować podstawowego kontraktu tabeli. Brak → **CRITICAL**. Przykład: element
klucza naturalnego.

**2. `required_by_test` / `required_by_claim`** — pole niewymagane strukturalnie, ale
potrzebne konkretnemu testowi albo twierdzeniu. Brak **nie blokuje przebiegu** i nie znaczy,
że tabela jest niepoprawna. Walidacja ma stan **ujawnić**, a test, który tego pola
potrzebuje, **nie może udawać wyniku** — zwraca `not_assessable` albo właściwy status braku
podstawy. Brak ogranicza ten test albo to twierdzenie, nie cały przebieg.

**3. Pole legalnie opcjonalne i niepotrzebne wykonywanemu testowi** — brak nie generuje ani
CRITICAL, ani automatycznego WARNING. Dopuszczalny stan danych.

Zdanie spinające całość:

> „Walidator danych ogłasza stan danych, ale nie przejmuje metodologicznej
> odpowiedzialności testu diagnostycznego. To konsument informacji wie, czy dane pole jest
> konieczne do wydania określonego twierdzenia."

**Skutki dla kodu:**

| Co | Zmiana |
| --- | --- |
| kontrola 1 | traci gałąź WARNING: brak elementu `NATURAL_KEY` → CRITICAL, brak dowolnego innego pola → **PASS z obserwacją** |
| rejestr testów | egzekwuje `required_by_test` wobec **rzeczywistych** raportów importu; dotąd deklaracja była sprawdzana tylko wobec kontraktu |

**Wykonanie (2026-09-08), z jednym odstępstwem od litery rozstrzygnięcia.** Egzekwowanie
nie stoi w rejestrze, tylko w metodzie szablonowej `DiagnosticTest.execute`, a
`engine.run_test()` jest cienką funkcją rejestru. Powód: rejestr da się obejść wywołaniem
`get_test(...)().run(...)` — i tak właśnie robiła nasza własna demonstracja, więc bramka
w rejestrze byłaby konwencją, a nie mechanizmem. Nadpisanie `execute` albo `readiness`
przez wtyczkę jest odrzucane przy tworzeniu klasy. Adres pozostaje ten, który wskazuje
rozstrzygnięcie; mechanizm siedzi piętro niżej. Szczegóły: wpis DT-20.

**Czego bramka nie zamyka.** Egzekwowania CRITICAL z `required_validations` — to osobny
mechanizm, którego rozstrzygnięcie B-06 nie dotyczy. Deklaracja istnieje, kontrole zwracają
statusy, ale nic nie łączy jednego z drugim; test wymagający pola, którego kolumna jest
obecna, wykona się także na tabeli rozbitej strukturalnie. Zamknięcie wymaga
rozstrzygnięcia metodologicznego (co CRITICAL wymaganej kontroli oznacza dla testu), więc
nie domykamy go technicznie z własnej inicjatywy.
| deklaracja testu | `required_fields` → `required_by_test`; nazwa niesie, **czyim** wymaganiem jest pole |

PASS przy braku pola spoza klucza **nie jest fałszywym przejściem**: fakt jest w wyniku jako
obserwacja z podstawą, tylko nie jako status. Sprowadza to kontrolę 1 do tego samego gatunku
co kontrola 3 — obraz, nie werdykt.

**ODCZYTANIE KRYTERIUM STRUKTURALNEGO (zapis jawny, do ewentualnego zaprotestowania).**

Michał pisze: „nie potrafimy odpowiedzialnie zidentyfikować rekordu **albo** zachować
podstawowego kontraktu tabeli". Pierwsza połowa to klucz naturalny; druga jest szersza
i wymaga przyłożenia do konkretu.

Przykładamy ją tak: **COST bez kolumny `amount` nie łamie podstawowego kontraktu tabeli.**
Wiersz nadal identyfikuje komórkę (miesiąc, jednostka, kategoria), której wartość jest
nieznana — a `null` jest poprawnym wynikiem (zasada 5). Test liczący z kwot zwróci
`not_assessable` i **to jest właściwe miejsce tej odmowy**.

Stąd: **strukturalnie wymagany = element klucza naturalnego i nic ponadto.**

To zastosowanie kryterium Michała, a nie luka w nim, więc nie zakładamy nowego kontraktu
otwartego. Zapis jest jawny po to, żeby Michał mógł zaprotestować, jeżeli miał na myśli
szerszy zbiór.

**ODROCZONE:** granulacja per twierdzenie (`required_by_claim`). **Termin wraca wcześniej,
niż zapisano pierwotnie: z CAP-01, nie z CONF-01** — i karta CAP-01 zawiera już dowód, że
będzie potrzebna. CAP01-T10: brak `cost` daje miary fizyczne i `economic_gap = null`,
„wg trendu; **nie TEST_BLOCKED**". Czyli `cost` jest wymagane twierdzeniom ekonomicznym,
a nie całemu testowi — gdyby CAP-01 wpisało je w `required_by_test`, bramka wyprodukowałaby
status, którego karta zakazuje. Do tego czasu obowiązuje reguła: w `required_by_test` trafia
wyłącznie pole, bez którego test nie wyda **żadnego** twierdzenia. Test może wydać część
twierdzeń i wstrzymać się od reszty — `TEST_PARTIAL` zamiast `TEST_BLOCKED`. Żaden test nie
produkuje dziś twierdzeń, więc deklaracja na poziomie testu wystarcza. Patrz wpis DT-18
w notatce technicznej; wraca z pierwszym testem produkującym twierdzenia.
