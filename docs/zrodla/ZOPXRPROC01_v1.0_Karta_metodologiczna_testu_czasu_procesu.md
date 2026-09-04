ZOPTYMALIZOWANI – X-RAY

# PROC-01

# Czas procesu

Karta metodologiczna i specyfikacja implementacyjna

> **STATUS PROC-01 ZAMKNIĘTY METODOLOGICZNIE DO IMPLEMENTACJI**

| Pole | Wartość |
| --- | --- |
| Identyfikator | ZOP-XR-PROC-01 |
| Wersja / data | v1.0 / 2 września 2026 |
| Rola | szósty pełny test diagnostyczny X-Ray; wzorzec rodziny analiz czasu i przepływu |
| Odbiorcy | zarządzający, analityk, Aleksander – implementacja |
| Źródła nadrzędne | niniejsze polecenie; PROC-02 v1.0; CAP-01 v1.0; HR-01 v1.0; PORT-01 v1.0; FIN-01 v1.0; ZOP-TECH-01; ZOP-MASTER-01 |
| Zależności | ZOP-PRI-01 i ZOP-CONF-01 – DO OPRACOWANIA |

Dokument definiuje metodę pomiaru czasu przejścia przez proces, kontrakt danych, reguły walidacji i porównywalności, luki czasowe, hotspoty opóźnień, strukturę FINDINGS, scenariusze regresyjne oraz kryteria odbioru implementacji. Nie projektuje PROC-03, aplikacji, panelu, warstwy AI, Priority Score ani Confidence Score.

> **GRANICA PROC-01 diagnozuje czas. PROC-02 diagnozuje ograniczenie przepływu. PROC-01 nie nadaje constraint_status i nie nazywa delay_hotspot wąskim gardłem.**

## 1. Rola, cel i granice PROC-01

PROC-01 bada, ile rzeczywiście trwa przejście przypadku przez proces, jak ten czas rozkłada się pomiędzy oczekiwaniem, realizacją i przekazaniem oraz gdzie występuje pogorszenie względem właściwej wartości odniesienia. Test działa dla procesów sekwencyjnych, równoległych, wariantowych, z etapami opcjonalnymi i powrotami.

> **PYTANIE DIAGNOSTYCZNE Ile rzeczywiście trwa przejście przypadku przez proces, gdzie powstaje oczekiwanie lub inne opóźnienie, jak stabilny jest czas realizacji oraz które części procesu odpowiadają za pogorszenie czasu względem właściwej wartości odniesienia?**

### 1.1. Łańcuch diagnostyczny

| Etap | Produkt | Granica |
| --- | --- | --- |
| Przypadek | case_id | jednoznaczna jednostka analizy |
| Granice | case_created_at → case_completed_at | jawny process_scope i process_boundary_basis |
| Ścieżka | route_variant | bez mieszania istotnie różnych tras |
| Gotowość | ready_at | warunek kolejki |
| Oczekiwanie | queue_time | gotowość ≠ rozpoczęcie |
| Realizacja | stage_elapsed_time / touch_time | elapsed ≠ aktywna praca |
| Przekazanie | transition_delay | wymaga poprawnej relacji poprzedników |
| Całość | case_lead_time | z granic procesu, nie z sumy etapów |
| Rozkład | median / P75 / P90 | średnia wyłącznie pomocnicza |
| Hotspot | delay_hotspot | hotspot ≠ bottleneck |
| Trend | 1M/3M/6M/12M | incydent ≠ trwałe pogorszenie |
| Dalej | next_tests | bez automatycznej decyzji |

### 1.2. Najważniejsza zasada

> **ZASADA NADRZĘDNA Czas procesu jest właściwością ścieżki przypadku w czasie. Nie jest prostą sumą wszystkich czasów zapisanych przy jego etapach.**

Zasada dotyczy szczególnie etapów równoległych, nakładającej się pracy, wielu zasobów, powrotów, rework, etapów opcjonalnych i różnych wariantów trasy. W procesie równoległym suma stage_elapsed_time albo suma touch_time różnych równoległych etapów może przekraczać kalendarzowy case_lead_time, ponieważ okresy nakładają się na osi czasu. Nie oznacza to, że pojedynczy touch_time danego case_id × stage × visit może przekraczać jego stage_elapsed_time.

### 1.3. Granica względem PROC-02

| PROC-01 | PROC-02 |
| --- | --- |
| diagnozuje czas i jego pogorszenie | diagnozuje constraint ograniczający przepływ |
| wykrywa queue/stage/transition hotspot | wymaga dowodu wpływu na system throughput |
| nie nadaje constraint_status | jest właścicielem constraint_status |
| hotspot może istnieć bez bottleneck | candidate_constraint ≠ verified_constraint |
| kieruje do PROC-02 przy sygnale wpływu na przepływ | może kierować do PROC-01 przy delay_hotspot bez constraint |

## 2. Jednostki analizy, granice procesu i kontrakt danych

### 2.1. case_id i stage

Podstawową jednostką procesu pozostaje case_id. Może oznaczać zlecenie, zamówienie, sprawę, paczkę, zgłoszenie, projekt, jednostkę produkcyjną, klienta przechodzącego przez proces albo inny mierzalny przypadek. Podstawową jednostką dekompozycji pozostaje stage o możliwie stabilnej definicji w czasie.

### 2.2. process_scope i process_boundary_basis

Każdy test wymaga jawnego process_scope oraz process_boundary_basis. case_created_at oznacza początek badanego procesu, a case_completed_at – terminalne zakończenie badanego procesu. Jeżeli źródłowe „utworzenie sprawy” nie odpowiada rzeczywistemu początkowi analizowanego zakresu, pole nie może zostać użyte bez jawnego przemapowania i udokumentowania podstawy.

> **OCHRONA GRANIC Granice procesu muszą odpowiadać pytaniu biznesowemu. Zmiana granicy między okresami bez walidacji unieważnia porównanie end-to-end.**

### 2.3. Bazowa tabela PROCESS

| Tabela | Pola bazowe | Rola PROC-01 |
| --- | --- | --- |
| PROCESS | case_id, stage, start, end, unit | oś czasu przypadku i przejścia przez etapy |
| PLAN – opcjonalna | date, unit, metric, target | plan / target / SLA jako możliwa referencja |
| RESOURCE – opcjonalna | date, unit, resource, available, used, cost | sygnał capacity do next_tests; bez zmiany definicji CAP |
| ACTIVITY – opcjonalna | date, unit, product, volume, revenue | portfolio_item / miks i skala procesu |

PROC-01 nie zmienia bazowej struktury ZOP-TECH-01. Wszystkie dodatkowe pola są rozszerzeniami pomocniczymi.

### 2.4. Rozszerzenia PROC-01

| Grupa | Pola techniczne |
| --- | --- |
| Proces i granice | process_type; process_scope; process_boundary_basis; case_status; case_created_at; case_completed_at |
| Routing | route_variant; route_comparability; stage_sequence; parallel_group; predecessor_relation; predecessor_stage |
| Czas | ready_at; queue_time; stage_elapsed_time; touch_time; transition_delay; non_touch_elapsed_time; blocked_time |
| Kalendarz | time_basis; calendar_id; calendar_basis; operating_time_basis; stage_operating_time; stage_operating_time_unit; system_observation_time; system_observation_time_unit |
| Powroty | repeat_visit; rework_iteration; repeat_visit_count; repeat_visit_rate; rework_time |
| Wynik end-to-end | case_lead_time; calendar_lead_time; operating_lead_time; critical_path_candidate |
| Target / kontekst | target_time; target_time_basis; required_wait_time; process_context_flags |
| Struktura tras | route_mix_change; matched_route_case_count_current; matched_route_case_count_reference; eligible_case_count_current; eligible_case_count_reference; matched_route_coverage_current; matched_route_coverage_reference; matched_route_coverage; new_route_variant; discontinued_route_variant; materially_changed_route |
| Kontrola | left_censored_case; right_censored_case; complete_case; time_bucket; exclusion_flags; validation_notes |

## 3. Model czasu PROC-01

### 3.1. Czas całkowity procesu

| case_lead_time | case_completed_at − case_created_at Wyłącznie dla complete_case. Źródłem są granice procesu, nie suma etapów. |
| --- | --- |

Przypadek lewostronnie albo prawostronnie cenzorowany nie może zostać potraktowany jak pełna obserwacja end-to-end lead time. Może jednak zasilać inne moduły, jeżeli obserwacja danej miary jest kompletna.

### 3.2. Kalendarzowy i operacyjny czas

| calendar_lead_time | case_completed_at − case_created_at w bazie calendar_elapsed |
| --- | --- |

| operating_lead_time | czas pomiędzy granicami liczony według udokumentowanego calendar_id / calendar_basis Brak poprawnego kalendarza → null; nie wymyślaj globalnego kalendarza. |
| --- | --- |

| Pole | Znaczenie |
| --- | --- |
| time_basis | calendar_elapsed / operating_elapsed / scheduled_elapsed albo inna jawna baza |
| calendar_id | identyfikator kalendarza użytego w obliczeniu |
| calendar_basis | źródło, wersja, zakres i zasady kalendarza |
| operating_time_basis | znaczenie czasu operacyjnego; zgodne z semantyką PROC-02 |
| stage_operating_time | czas operacyjny etapu w zdefiniowanej jednostce; pole odziedziczone z PROC-02 |
| system_observation_time | jawny czas obserwacji całego procesu; pole odziedziczone z PROC-02 |

> **PRZYKŁAD Sprawa czeka od piątku 15:55 do poniedziałku 8:05. Calendar lead time i operating lead time odpowiadają na dwa różne pytania. Czas poza godzinami pracy nie jest automatycznie nieefektywnością.**

### 3.3. Cztery czasy etapu – semantyka 1:1 z PROC-02

| Miara | Wzór / definicja | Reguła ochronna |
| --- | --- | --- |
| queue_time | start − ready_at | wymaga wiarygodnego momentu gotowości |
| stage_elapsed_time | end − start | czas kalendarzowy etapu; nie utożsamiaj z aktywną pracą |
| touch_time | rzeczywisty aktywny czas dotyczący jednego case_id × stage × visit, mierzony na osi czasu etapu | przy zgodnej podstawie czasu: 0 ≤ touch_time ≤ stage_elapsed_time; brak pomiaru → null; touch_time ≠ labor_input ≠ work_content; nie jest sumą osobogodzin wielu osób |
| transition_delay | ready_at_current − predecessor_completion_at | wymaga poprawnego kontraktu predecessor_relation / predecessor_stage |

### 3.4. non_touch_elapsed_time

| non_touch_elapsed_time | stage_elapsed_time − touch_time Tylko przy zgodnych jednostkach i bazach czasu oraz wiarygodnym touch_time. Wynik < 0 → CRITICAL dla tej miary. |
| --- | --- |

non_touch_elapsed_time nie jest automatycznie marnotrawstwem, przestojem ani czasem do usunięcia. Może obejmować prawidłowe oczekiwanie technologiczne, inkubację, schnięcie, przetwarzanie automatyczne, wymagany okres prawny albo inne uzasadnione zdarzenie.

### 3.5. blocked_time

blocked_time jest używane wyłącznie wtedy, gdy źródło rzeczywiście potwierdza zablokowanie przypadku lub zasobu po wykonaniu pracy. Nie wolno wyprowadzać blocked_time automatycznie z długiego stage_elapsed_time, transition_delay ani różnicy end/start.

## 4. Routing, równoległość, poprzednicy, powroty i cenzorowanie

### 4.1. route_variant i porównywalność

PROC-01 obsługuje proces sekwencyjny, równoległość, warianty ścieżki, etapy opcjonalne, powroty i rework. Istotnie różne route_variant analizuje się osobno. Nie porównuje się bez kontroli krótkiej ścieżki A→B z trasą A→C→D→B.

### 4.2. Proces równoległy

> **REGUŁA KRYTYCZNA Jeżeli A i B odbywają się równolegle, lead time wspólnego fragmentu wynika z osi czasu przypadku. Nie przyjmuj lead_time = duration_A + duration_B.**

Suma touch_time różnych równoległych etapów może być większa od kalendarzowego case_lead_time, ponieważ okresy aktywnej pracy etapów nakładają się na osi czasu. Każdy pojedynczy touch_time dotyczy jednego case_id × stage × visit i przy zgodnej podstawie czasu spełnia 0 ≤ touch_time ≤ stage_elapsed_time. touch_time nie jest labor_input ani work_content i nie jest sumą osobogodzin wielu równolegle pracujących osób. Łączny nakład pracy kilku zasobów należy do wspólnego przyszłego kontraktu work_content i pozostaje poza metodologią PROC-01. Dla procesów równoległych lokalne stage times pozostają charakterystykami etapów; nie przedstawia się ich sumy jako 100% lead time.

### 4.3. Kontrakt poprzedników dla transition_delay

| jeden poprzednik | predecessor_completion_at = end_predecessor |
| --- | --- |

| wielu wymaganych poprzedników | predecessor_completion_at = max(end_required_predecessors) Tylko wtedy, gdy udokumentowana logika procesu wymaga zakończenia wszystkich poprzedników. |
| --- | --- |

predecessor_relation i predecessor_stage muszą pozwalać jednoznacznie odtworzyć zależność. Przy innej logice należy użyć jej udokumentowanej reguły. Jeżeli zależności nie da się odtworzyć, transition_delay = null i ograniczenie trafia do validation_notes. Ujemny transition_delay nie jest zwykłą miarą opóźnienia bez wyjaśnienia relacji równoległej lub błędu danych.

### 4.4. Powroty i rework

Powtórne odwiedzenie stage nie jest duplikatem. repeat_visit i rework_iteration zachowują kolejne przejścia. repeat_visit_count i repeat_visit_rate pokazują skalę powrotów. rework_time może być liczony tylko wtedy, gdy znaczenie powtórnej pracy zostało potwierdzone; przy nieznanym znaczeniu powrotu pozostaje neutralny repeat visit.

### 4.5. Cenzorowanie

| Klasa | Definicja | Użycie |
| --- | --- | --- |
| left_censored_case | proces rozpoczął się przed początkiem okna | nie jako pełny lead time; może zasilać WIP i kompletne miary etapowe |
| right_censored_case | proces nie osiągnął terminalnego końca do końca okna | nie jako zakończony lead time; może zasilać WIP |
| complete_case | początek i terminalne zakończenie obserwowane zgodnie z scope | pełne miary end-to-end |

### 4.6. critical_path_candidate

PROC-01 v1.0 nie projektuje pełnego Critical Path Method. Jeżeli zależności i czasy pozwalają jednoznacznie odtworzyć ścieżkę determinującą zakończenie przypadku, można ustawić critical_path_candidate. Przy braku podstawy wynik pozostaje null. Formalny moduł critical path pozostaje kwestią wspólną poza PROC-01.

## 5. Walidacja danych PROC01-VAL-01–25

Każda kontrola zwraca PASS, WARNING albo CRITICAL. CRITICAL zatrzymuje wyłącznie moduł zależny, jeżeli pozostała analiza pozostaje wiarygodna. WARNING pozwala kontynuować z validation_required i validation_notes. Brak podstawy nie jest uzupełniany wartością zastępczą.

| Id | Kontrola | Skutek negatywny |
| --- | --- | --- |
| PROC01-VAL-01 | istnieje case_id | CRITICAL dla rekonstrukcji przypadku |
| PROC01-VAL-02 | istnieje stage | CRITICAL dla dekompozycji |
| PROC01-VAL-03 | start jest prawidłowym znacznikiem czasu | CRITICAL dla miar etapowych |
| PROC01-VAL-04 | end ≥ start albo rekord jest jawnie otwarty | CRITICAL/WARNING zależnie od modułu |
| PROC01-VAL-05 | case_created_at ma jednoznaczne znaczenie | CRITICAL dla lead time |
| PROC01-VAL-06 | case_completed_at odpowiada terminalnemu zakończeniu | CRITICAL dla lead time |
| PROC01-VAL-07 | process_scope i process_boundary_basis są stabilne | WARNING/CRITICAL dla porównań |
| PROC01-VAL-08 | strefy czasowe są zgodne | CRITICAL przy nieusuwalnej niespójności |
| PROC01-VAL-09 | time_basis jest jawna | WARNING/CRITICAL dla porównania czasów |
| PROC01-VAL-10 | calendar_basis jest jawna przy operating time | CRITICAL dla operating_lead_time |
| PROC01-VAL-11 | ready_at ≤ start, jeżeli ready_at istnieje | CRITICAL dla queue_time |
| PROC01-VAL-12 | predecessor_relation / predecessor_stage odtwarzają zależność | WARNING/CRITICAL dla transition_delay |
| PROC01-VAL-13 | routing i route_variant są spójne | WARNING/CRITICAL dla agregacji tras |
| PROC01-VAL-14 | równoległość jest rozpoznana i obsłużona | CRITICAL, gdy grozi podwójnym liczeniem czasu |
| PROC01-VAL-15 | repeat_visit jest odróżniony od duplikatu | CRITICAL przy ryzyku usunięcia zdarzeń |
| PROC01-VAL-16 | brak niewyjaśnionych duplikatów | CRITICAL, gdy wpływu nie można wyłączyć |
| PROC01-VAL-17 | left/right censoring jest prawidłowo rozpoznany | WARNING/CRITICAL dla rozkładu lead time |
| PROC01-VAL-18 | route_comparability jest znana | WARNING; luki tras mogą pozostać null |
| PROC01-VAL-19 | definicja stage jest stabilna | WARNING/CRITICAL dla trendu stage |
| PROC01-VAL-20 | 0 ≤ touch_time ≤ stage_elapsed_time dla tego samego case_id × stage × visit przy zgodnej podstawie czasu | CRITICAL dla touch_time/non_touch_elapsed_time przy naruszeniu |
| PROC01-VAL-21 | blocked_time ma wiarygodne źródło | WARNING; blocked_time=null bez podstawy |
| PROC01-VAL-22 | target_time ma źródło i target_time_basis | WARNING; SLA moduł pozostaje null |
| PROC01-VAL-23 | porównywane okresy mają zgodne kalendarze albo jawne różnice | WARNING/CRITICAL dla operating comparison |
| PROC01-VAL-24 | czasy równoległe nie są sumowane jako case_lead_time | CRITICAL dla błędnej dekompozycji |
| PROC01-VAL-25 | istnieje właściwa referencja albo luka pozostaje null | WARNING; signed/adverse gap=null |

## 6. Rozkład czasu, horyzonty, referencje i target

### 6.1. Rozkład czasu

Dla case_lead_time, queue_time, stage_elapsed_time i transition_delay test przechowuje N oraz – gdy liczebność pozwala – medianę, P75 i P90; P95 opcjonalnie. Mean jest miarą pomocniczą. Długich obserwacji nie usuwa się automatycznie jako outliers.

| tail_ratio | P90 / median Tylko gdy median > 0. Miara opisowa bez arbitralnego progu problemu. |
| --- | --- |

Długi ogon może wynikać z wyjątkowych przypadków, niestabilności, różnych route_variant, braków danych, powrotów albo innego problemu procesowego. Pozostaje sygnałem do dalszej diagnozy.

### 6.2. Horyzonty i time_bucket

| Horyzont | Rola |
| --- | --- |
| 1M | sygnał bieżący; incydent nie dowodzi trwałości |
| 3M | krótkoterminowe potwierdzenie |
| 6M | trwałość średnioterminowa |
| 12M / r/r | sezonowość i porównanie roczne |
| 24–36M | trend, zmiany strukturalne, stabilność |
| dzień / tydzień / zmiana / naturalny cykl | analiza operacyjna przy odpowiedniej granularności |

Każdy wynik przechowuje time_bucket i jego podstawę. Granularność wynika z procesu i danych; nie jest narzucana arbitralnie.

### 6.3. Hierarchia wartości odniesienia

| Priorytet | Źródło | Warunek |
| --- | --- | --- |
| 1 | historia tego samego procesu i route_variant | stabilne granice, kalendarz i definicje |
| 2 | wcześniejszy porównywalny okres | zgodna trasa, sezon i time_basis |
| 3 | plan | jawna definicja miary |
| 4 | umowny / SLA target | wyłącznie przy źródłowym target_time |
| 5 | najlepszy własny stabilny okres | bez istotnego zdarzenia wyjątkowego |
| 6 | porównywalny proces wewnętrzny | udokumentowana porównywalność |
| 7 | benchmark zewnętrzny | wiarygodne źródło i zgodne definicje |

> **BRAK ARBITRALNYCH NORM PROC-01 nie tworzy reguł typu „dobry proces trwa maksymalnie X” ani „kolejka powinna wynosić Y”. Brak właściwej referencji pozostawia lukę jako null.**

### 6.4. Target / SLA

| on_time_cases | liczba complete_case spełniających target_time w tej samej target_time_basis |
| --- | --- |

| on_time_rate | on_time_cases / właściwa liczba przypadków objętych targetem |
| --- | --- |
| on_time_rate_gap_signed | on_time_rate_reference − on_time_rate_current Dodatnia wartość oznacza pogorszenie terminowości. Brak źródłowego target_time / SLA → null. |
| adverse_on_time_rate_gap | max(on_time_rate_gap_signed, 0) Brak źródłowego target_time / SLA → null. Bez progu alarmowego. |

| lateness_time | max(observed_time − target_time, 0) Tylko dla przypadków objętych udokumentowanym targetem. |
| --- | --- |

Brak target_time nie blokuje analizy historycznej. PROC-01 nie rekonstruuje ani nie wymyśla SLA.

## 7. Podpisane luki czasowe i ekspozycja na opóźnienie

### 7.1. Luka end-to-end

| lead_time_gap_signed | lead_time_current − lead_time_reference Dodatnia wartość oznacza wydłużenie względem referencji. |
| --- | --- |

| adverse_lead_time_gap | max(lead_time_gap_signed, 0) Nie jest automatycznie czasem możliwym do odzyskania. |
| --- | --- |

### 7.2. Luka queue time

| queue_time_gap_signed | queue_time_current − queue_time_reference |
| --- | --- |

| adverse_queue_time_gap | max(queue_time_gap_signed, 0) |
| --- | --- |

### 7.3. Luka stage elapsed

| stage_elapsed_gap_signed | stage_elapsed_current − stage_elapsed_reference |
| --- | --- |

| adverse_stage_elapsed_gap | max(stage_elapsed_gap_signed, 0) Nie interpretuj automatycznie jako wolniejszej pracy pracownika. |
| --- | --- |

### 7.4. Luka transition delay

| transition_delay_gap_signed | transition_delay_current − transition_delay_reference |
| --- | --- |

| adverse_transition_delay_gap | max(transition_delay_gap_signed, 0) Może wskazywać problem przekazania; nie przesądza przyczyny. |
| --- | --- |

### 7.5. Standaryzowana ekspozycja na opóźnienie

| delay_metric_type | lead_time / queue_time / stage_elapsed / transition_delay / lateness Określa typ jednorodnej miary, dla której liczona jest ekspozycja. |
| --- | --- |
| adverse_delay_exposure | adverse_time_gap × comparable_case_count Wyłącznie przy zgodnej jednostce czasu, route_variant, time_basis, okresie i referencji. Nie jest to recoverable time. |

| adverse_delay_exposure_share_i | adverse_delay_exposure_i / Σadverse_delay_exposure Przy sumie 0 → null. Mianownik obejmuje wyłącznie jednorodną populację: ten sam delay_metric_type, poziom analizy, okres, referencję i zgodny time_basis. Nie łącz lead-time, queue, stage ani transition exposure w jednym mianowniku i nie sumuj nakładających się etapów jako „całkowitego opóźnienia procesu”. |
| --- | --- |

> **GRANICA INTERPRETACJI Podpisana luka zachowuje kierunek zmiany. Część adverse służy lokalizacji pogorszenia. Ani gap, ani adverse_delay_exposure nie są automatycznie czasem możliwym do odzyskania.**

## 8. Hotspot opóźnienia, trend i kontekst

### 8.1. delay_hotspot

delay_hotspot wskazuje miejsce koncentracji obserwowanego czasu lub jego pogorszenia. Może wynikać z queue_time, stage_elapsed_time, transition_delay, P90, lateness albo powtarzalności. Nie wymaga constraint_status i może istnieć bez wąskiego gardła.

| delay_hotspot_type | Znaczenie |
| --- | --- |
| queue | koncentracja w oczekiwaniu przed etapem |
| stage_elapsed | koncentracja w kalendarzowym czasie realizacji etapu |
| transition | koncentracja pomiędzy zakończeniem poprzednika a gotowością |
| tail | problem dotyczy głównie ogona rozkładu |
| rework | powroty zwiększają czas obserwowany |
| mixed | więcej niż jeden komponent bez dominującej pojedynczej klasy |

> **OCHRONA delay_hotspot ≠ bottleneck. Jeżeli hotspot może ograniczać przepływ całego systemu, next_test = PROC-02.**

### 8.2. Trend i trwałość

| Status / kierunek | Znaczenie bez progu priorytetu |
| --- | --- |
| INCIDENT | pojedynczy bardzo długi okres/przypadek bez potwierdzenia trwałości |
| DETERIORATING | porównywalne obserwacje i horyzonty potwierdzają pogorszenie |
| STABLE | brak trwałego kierunku po uwzględnieniu zmienności |
| IMPROVING | potwierdzona poprawa w więcej niż jednym horyzoncie |
| NO_ADVERSE_SIGNAL | brak potwierdzonego niekorzystnego odchylenia |
| TEST_PARTIAL / TEST_BLOCKED | częściowa wykonalność / brak podstaw do zależnego modułu |

### 8.3. process_context_flags

| Flaga | Znaczenie |
| --- | --- |
| seasonality | sezonowość |
| demand_spike | chwilowy skok popytu |
| policy_change | zmiana polityki/reguł |
| system_change | zmiana systemu |
| route_change | zmiana trasy |
| staffing_change | zmiana struktury obsady |
| schedule_change | zmiana harmonogramu |
| launch_phase | faza uruchomienia |
| reorganization | reorganizacja |
| temporary_shutdown | czasowe wyłączenie |
| external_dependency | zależność zewnętrzna |
| regulatory_wait | wymagany czas regulacyjny |
| other_context | inne istotne zdarzenie |

### 8.4. required_wait_time i brak automatycznego „waste”

required_wait_time może być przechowywany, jeżeli źródło potwierdza świadomie wymagany czas technologiczny, regulacyjny, kontraktowy albo inny prawidłowy okres oczekiwania. PROC-01 rozdziela czas istniejący od czasu niepożądanego i nie nazywa całego non-touch time marnotrawstwem, zbędnym czasem ani czasem do odzyskania.

## 9. Miks tras, nowe trasy i porównywalność

### 9.1. route_mix_change

Jeżeli route A ma 3 etapy, a route B ma 8 etapów, średni lub medianowy czas całego procesu może zmienić się wyłącznie dlatego, że zmienił się udział tras. PROC-01 pokazuje wynik całkowity oraz wyniki wewnątrz porównywalnych route_variant.

| Pole | Reguła |
| --- | --- |
| route_mix_change | jawny sygnał zmiany struktury route_variant między current i reference |
| matched_route_coverage | prezentacyjny alias matched_route_coverage_current; reference coverage zawsze pokazuj osobno |
| new_route_variant | trasa obecna current bez porównywalnej historii |
| discontinued_route_variant | trasa obecna reference, nieobecna current |
| materially_changed_route | trasa o istotnie zmienionej definicji / granicy / sekwencji |
| matched_route_case_count_current | liczba przypadków current należących do porównywalnych route_variant obecnych w obu okresach |
| matched_route_case_count_reference | liczba przypadków reference należących do porównywalnych route_variant obecnych w obu okresach |
| eligible_case_count_current | liczba przypadków current kwalifikujących się do oceny pokrycia; mianownik current |
| eligible_case_count_reference | liczba przypadków reference kwalifikujących się do oceny pokrycia; mianownik reference |
| matched_route_coverage_current | matched_route_case_count_current / eligible_case_count_current; mianownik 0 → null |
| matched_route_coverage_reference | matched_route_case_count_reference / eligible_case_count_reference; mianownik 0 → null |

> **ZASADA Nowych, wycofanych lub materialnie zmienionych tras nie wciska się do historycznego porównania. Brak referencji oznacza gap = null, a nie sztuczną wartość.**

### 9.2. Brak addytywnej dekompozycji przy równoległości

Dla sequential_non_overlapping możliwa jest kontrolowana dekompozycja czasu. Dla procesu równoległego stage times są lokalnymi charakterystykami. Nie wolno przedstawiać ich sumy jako udziałów 100% lead time ani generować sztucznych udziałów procentowych przekraczających 100%.

## 10. Relacje diagnostyczne i granica ekonomiczna

| next_test | Warunek rekomendacji | Cel |
| --- | --- | --- |
| PROC-02 | lead time / queue / transition może ograniczać przepływ albo występuje sygnał system throughput | wąskie gardło i constraint_status |
| CAP-01 | queue rośnie przy sygnale wolnej capacity | niewykorzystanie i niedopasowanie capacity |
| CAP-02 | queue rośnie przy potwierdzonej presji ponad zdolność | przeciążenie – metodologia poza PROC-01 |
| HR-01 | stage_elapsed zmienia się wraz z work_content, produktywnością lub strukturą pracy | koszt pracy względem efektu |
| PORT-01 | portfolio_item / route mix może tłumaczyć zmianę czasu | struktura portfela i tras |
| FIN-03 | wydłużenie procesu może podnosić koszt jednostkowy | metodologia poza PROC-01 |
| FIN-01 | problem czasowy może mieć istotny wpływ ekonomiczny | relacja kosztów i przychodów |

### 10.1. Typowe wzorce

| Wzorzec | Obserwacja | Kolejny krok |
| --- | --- | --- |
| A | lead time↑; queue_time↑; system throughput↓ | PROC-02 |
| B | lead time↑; stage_elapsed↑; throughput stabilny | delay_hotspot; PROC-02 tylko przy sygnale ograniczenia przepływu |
| C | transition_delay↑; CAP-01 pokazuje wolną capacity | hipoteza handoff/gate/organizacji; PROC-02 |
| D | długi etap równoległy; brak wpływu na end-to-end | nie nazywaj bottleneck |
| E | queue↑; capacity pressure wysoka | CAP-02 / PROC-02 |
| F | stage_elapsed↑; work_content/produktywność się zmienia | HR-01 |
| G | total lead time↑; czasy wewnątrz tras stabilne; mix tras zmieniony | PORT-01 / analiza route mix |

### 10.2. Granica ekonomiczna

> **BEZ AUTOMATYCZNEJ WYCENY PROC-01 nie przelicza godziny oczekiwania × przychód, lead time × marża ani kolejki × koszt pracy. Przekazuje czas, skalę, liczbę przypadków i zakres do FIN-01, FIN-03 lub PORT-01.**

Hipoteza ≠ przyczyna. elapsed increase ≠ automatycznie wolniejszy pracownik. queue increase ≠ automatycznie potrzeba zatrudnienia. PROC-01 nie rekomenduje automatycznie zwiększenia ani redukcji capacity.

## 11. Dekompozycja, dane dla PRI/CONF i FINDINGS

### 11.1. Poziomy dekompozycji

| Poziom | Klucz | Minimalny wynik |
| --- | --- | --- |
| I | organization | case lead time, rozkład, trend, route mix |
| II | process_type | wynik procesu i główne route_variant |
| III | route_variant | porównywalny end-to-end i coverage |
| IV | unit | lokalizacja organizacyjna |
| V | stage | N, median/P90 queue/elapsed/transition, trend i referencja |
| opcjonalny | portfolio_item | struktura przypadków i miks |
| opcjonalny | resource_group | kontekst capacity, bez oceny osoby |

### 11.2. Dane dla ZOP-PRI-01

> **ZOP-PRI-01 – DO OPRACOWANIA lead_time_gap_signed; adverse_lead_time_gap; queue_time_gap_signed; adverse_queue_time_gap; stage_elapsed_gap_signed; adverse_stage_elapsed_gap; transition_delay_gap_signed; adverse_transition_delay_gap; delay_metric_type; adverse_delay_exposure; adverse_delay_exposure_share; affected_cases; delay_hotspot; delay_hotspot_type; on_time_rate_gap_signed; adverse_on_time_rate_gap; trend_direction; persistence; route_scope; affected_units; affected_portfolio_items; result_risk; urgent_validation. PROC-01 nie tworzy lokalnego Priority Score ani progów.**

### 11.3. Dane dla ZOP-CONF-01

> **ZOP-CONF-01 – DO OPRACOWANIA process_data_completeness; timestamp_quality; process_boundary_quality; ready_at_quality; route_comparability; matched_route_case_count_current; matched_route_case_count_reference; eligible_case_count_current; eligible_case_count_reference; matched_route_coverage_current; matched_route_coverage_reference; calendar_quality; time_basis_quality; stage_definition_quality; predecessor_quality; touch_time_quality; censoring_share; rework_identification_quality; target_time_quality; reference_quality; parallel_route_quality; manual_validation; exclusion_flags. PROC-01 nie wylicza lokalnego Confidence Score; asymetria current/reference coverage pozostaje jawna i wpływa na ocenę jakości porównania.**

### 11.4. Bazowa struktura FINDINGS

| Pole bazowe | Reguła PROC-01 |
| --- | --- |
| test_id | PROC-01 |
| scope | process_scope + filtry + route_variant / unit / stage |
| period | current + reference + horyzont / time_bucket |
| status | status logiczny testu |
| finding | komunikat faktograficzny bez wniosku o bottleneck |
| metric_value / reference_value | główna miara czasowa i referencja |
| gap | podpisana luka właściwa dla findingu |
| impact_low / impact_high | odpowiedzialny przedział albo null; nie automatyczna wycena pieniężna |
| confidence_score / confidence_class | wynik ZOP-CONF-01 albo null |
| next_tests | tablica test_id + uzasadnienie |
| validation_required | boolean + validation_notes |

### 11.5. Rozszerzenia FINDINGS PROC-01

| Grupa | Pola techniczne |
| --- | --- |
| Identyfikacja | process_type; process_scope; route_variant; unit; stage; portfolio_item; time_basis; calendar_id |
| Populacja | case_count; complete_case_count; censoring_share; matched_route_case_count_current; matched_route_case_count_reference; eligible_case_count_current; eligible_case_count_reference; matched_route_coverage_current; matched_route_coverage_reference; matched_route_coverage |
| Lead time | case_lead_time_median; case_lead_time_p75; case_lead_time_p90; case_lead_time_reference; lead_time_gap_signed; adverse_lead_time_gap |
| Queue | queue_time_median; queue_time_p90; queue_time_reference; queue_time_gap_signed; adverse_queue_time_gap |
| Stage | stage_elapsed_median; stage_elapsed_p90; stage_elapsed_reference; stage_elapsed_gap_signed; adverse_stage_elapsed_gap |
| Transition | transition_delay_median; transition_delay_p90; transition_delay_reference; transition_delay_gap_signed; adverse_transition_delay_gap |
| Praca / oczekiwanie | touch_time_median; non_touch_elapsed_time; blocked_time; repeat_visit_rate; required_wait_time |
| Trasy | route_mix_change; new_route_variant; discontinued_route_variant; materially_changed_route |
| Target | target_time; target_time_basis; on_time_rate_current; on_time_rate_reference; on_time_rate_gap_signed; adverse_on_time_rate_gap; lateness_time |
| Hotspot | delay_hotspot; delay_hotspot_type; delay_metric_type; adverse_delay_exposure; adverse_delay_exposure_share |
| Kontekst / kontrola | process_context_flags; exclusion_flags; validation_notes; critical_path_candidate |

## 12. Komunikat zarządczy i statusy

> **WZORZEC KOMUNIKATU [STATUS] CZAS PROCESU Mediana czasu przejścia przez proces [process_type / route_variant] wynosi obecnie [X] wobec [Y] w okresie odniesienia. P90 wynosi [Z], co pokazuje skalę najdłużej trwających przypadków. Największe pogorszenie obserwujemy w [stage / transition], gdzie [queue/stage/transition time] zmienił się z [A] do [B]. Analizą porównywalną objęto [coverage] przypadków/tras. Wynik wskazuje miejsce koncentracji opóźnienia, ale nie przesądza, że jest ono wąskim gardłem lub że cały obserwowany czas można usunąć. Dalsza weryfikacja: [next_tests].**

### 12.1. Statusy logiczne

| Status | Znaczenie |
| --- | --- |
| NO_ADVERSE_SIGNAL | brak potwierdzonego niekorzystnego odchylenia |
| ADVERSE_SIGNAL | potwierdzona niekorzystna zmiana miary bez rozstrzygnięcia przyczyny |
| INCIDENT | pojedyncze zdarzenie bez podstaw do trwałości |
| DETERIORATING | trwałe pogorszenie w porównywalnym zakresie |
| STABLE | brak trwałego kierunku |
| IMPROVING | potwierdzona poprawa |
| TEST_PARTIAL | część modułów możliwa do odpowiedzialnego wykonania |
| TEST_BLOCKED | krytyczny brak uniemożliwia zależną diagnozę |

Statusy STANDARD / MEDIUM / HIGH / CRITICAL nada dopiero ZOP-PRI-01. confidence_score i confidence_class pozostają null do czasu zastosowania ZOP-CONF-01.

### 12.2. Zakazane skróty decyzyjne

> **NIE GENERUJ AUTOMATYCZNIE „pracownicy działają za wolno”; „ten etap jest bottleneckiem”; „X godzin można odzyskać”; „trzeba zatrudnić więcej ludzi”; „należy zwiększyć capacity”. Każde z tych zdań wymaga odrębnej podstawy dowodowej.**

## 13. Scenariusze testowe PROC01-T01–T10

| Id | Scenariusz | Dane | Oczekiwane |
| --- | --- | --- | --- |
| PROC01-T01 | stabilny proces | Lead time, queue i stage times stabilne. | NO_ADVERSE_SIGNAL; brak fałszywego hotspotu. |
| PROC01-T02 | pogorszenie end-to-end | Lead time rośnie; trasa porównywalna. | ADVERSE_SIGNAL / DETERIORATING; dekompozycja. |
| PROC01-T03 | rośnie queue time | Stage elapsed stabilny. | delay_hotspot_type=queue; PROC-02/CAP wg danych. |
| PROC01-T04 | rośnie stage elapsed | Queue stabilna. | stage_elapsed hotspot; bez tezy o pracowniku. |
| PROC01-T05 | rośnie transition delay | Etapy same stabilne. | transition hotspot; PROC-02. |
| PROC01-T06 | długi etap równoległy | Stage A trwa długo, ale nie wydłuża end-to-end. | brak fałszywego przypisania wpływu. |
| PROC01-T07 | dwa równoległe etapy | A i B po 10 h równolegle. | wspólny fragment ≈10 h, nie 20 h. |
| PROC01-T08 | SUMA TOUCH_TIME RÓWNOLEGŁYCH ETAPÓW > LEAD TIME | Dwa równoległe etapy mają wiarygodne touch_time; każdy touch_time_i ≤ stage_elapsed_time_i; suma touch_time obu etapów > case_lead_time z powodu nakładania się pracy. | Brak błędu; brak podwójnego liczenia kalendarzowego lead time; touch_time pozostaje aktywnym czasem etapu, nie kontraktem nakładu pracy. |
| PROC01-T09 | brak ready_at | Start/end istnieją. | elapsed możliwe; queue_time=null; TEST_PARTIAL. |
| PROC01-T10 | weekend | Sprawa obejmuje weekend. | calendar i operating time rozdzielone; brak auto-inefficiency. |

## 14. Scenariusze testowe PROC01-T11–T23

| Id | Scenariusz | Dane | Oczekiwane |
| --- | --- | --- | --- |
| PROC01-T11 | rework | Przypadek wraca do stage. | powtórzenie zachowane; rework tylko przy podstawie. |
| PROC01-T12 | zmiana miksu tras | Udział długiej B rośnie; A/B wewnętrznie stabilne. | route_mix_change; bez fałszywego pogorszenia każdej trasy. |
| PROC01-T13 | nowa trasa | Brak historycznej referencji. | current widoczny; reference gap=null. |
| PROC01-T14 | zmiana definicji stage | Stage zmieniony między okresami. | brak porównania bez walidacji. |
| PROC01-T15 | cenzorowanie | Dużo otwartych spraw. | brak zaniżenia lead time; censoring_share jawny. |
| PROC01-T16 | kilka ekstremalnych spraw | Mean rośnie; median stabilna; P90 rośnie. | ogon widoczny; diagnoza nie tylko ze średniej. |
| PROC01-T17 | SLA istnieje | Źródłowy target_time=48 h. | on_time_rate i lateness_time. |
| PROC01-T18 | brak SLA | Brak targetu źródłowego. | 0 wymyślonego targetu; historia jako referencja. |
| PROC01-T19 | required_wait_time | 24 h technologicznego oczekiwania. | czas widoczny; brak etykiety waste. |
| PROC01-T20 | opóźnienie z wolną capacity | Queue rośnie przy niskim utilization. | bez auto-zatrudnienia; PROC-02/CAP-01. |
| PROC01-T21 | RÓŻNE RODZAJE DELAY EXPOSURE | Lead-time gap i queue-time gap występują równocześnie. | Oddzielne delay_metric_type; brak wspólnego denominatora adverse share; brak podwójnego „całkowitego opóźnienia”. |
| PROC01-T22 | SPADKI TERMINOWOŚCI | on_time_rate reference = 90%; current = 75%. | on_time_rate_gap_signed = 15 p.p.; adverse_on_time_rate_gap = 15 p.p.; brak sztucznego SLA. |
| PROC01-T23 | ASYMETRYCZNE MATCHED ROUTE COVERAGE | current coverage = 90%; reference coverage = 60%. | Obie wartości pokazane osobno; validation_required / CONF payload uwzględnia słabszą stronę porównania; brak jednego mylącego procentu. |

> **WARUNEK PASS Scenariusz przechodzi dopiero wtedy, gdy zgadzają się walidacja, null/not_computable, status, FINDINGS, route/context flags, validation_required, next_tests i zakazy interpretacyjne. Sama poprawna liczba czasu nie wystarcza.**

## 15. Przebieg implementacji

| Krok | Operacja | Warunek wyjścia |
| --- | --- | --- |
| 1 | ustal process_scope, process_boundary_basis i populację | jawne granice end-to-end |
| 2 | zmapuj PROCESS i pola rozszerzeń | bez zmiany tabeli bazowej |
| 3 | odtwórz route_variant, parallel_group i predecessor_relation | brak sztucznej kolejności |
| 4 | wykonaj PROC01-VAL-01–25 | PASS/WARNING/CRITICAL per moduł |
| 5 | oznacz complete/left/right censored | populacja rozkładu lead time |
| 6 | oblicz case/calendar/operating lead time | z granic procesu |
| 7 | oblicz queue/elapsed/touch/transition/non-touch warunkowo | null przy braku podstawy |
| 8 | wyznacz rozkład: N, median, P75, P90, mean pomocniczo | bez automatycznego usuwania ogona |
| 9 | wybierz referencje i targety wyłącznie ze źródła | reference metadata |
| 10 | licz signed/adverse gaps, typed adverse delay exposure i on_time_rate gaps | bez interpretacji jako recoverable time |
| 11 | analizuj route mix, context, hotspot, trend i persistence | bez bottleneck label |
| 12 | zapisz FINDINGS i next_tests; przekaż PRI/CONF payload | bez lokalnego score |

## 16. Kryteria odbioru implementacji PROC01-ACC-01–50

| Id | Kryterium | Id | Kryterium |
| --- | --- | --- | --- |
| PROC01-ACC-01 | przyjmuje PROCESS zgodny z modelem – PASS | PROC01-ACC-02 | rozpoznaje case_id i stage – PASS |
| PROC01-ACC-03 | waliduje process_scope i process_boundary_basis – PASS | PROC01-ACC-04 | liczy case_lead_time wyłącznie z granic procesu – PASS |
| PROC01-ACC-05 | nie odtwarza lead time przez sumę stage times – PASS | PROC01-ACC-06 | rozróżnia calendar_lead_time i operating_lead_time – PASS |
| PROC01-ACC-07 | obsługuje time_basis, calendar_id i calendar_basis – PASS | PROC01-ACC-08 | zachowuje stage_operating_time i operating_time_basis zgodnie z PROC-02 – PASS |
| PROC01-ACC-09 | zachowuje system_observation_time zgodnie z PROC-02 – PASS | PROC01-ACC-10 | liczy queue_time tylko przy wiarygodnym ready_at – PASS |
| PROC01-ACC-11 | liczy stage_elapsed_time – PASS | PROC01-ACC-12 | nie utożsamia stage_elapsed_time z touch_time; touch_time jest aktywnym czasem case_id × stage × visit – PASS |
| PROC01-ACC-13 | liczy transition_delay tylko przy poprawnym predecessor – PASS | PROC01-ACC-14 | obsługuje wielu wymaganych poprzedników bez arbitralnego wyboru – PASS |
| PROC01-ACC-15 | liczy non_touch_elapsed_time warunkowo – PASS | PROC01-ACC-16 | odrzuca non_touch_elapsed_time < 0 jako błąd tej miary – PASS |
| PROC01-ACC-17 | używa blocked_time tylko przy źródłowym potwierdzeniu – PASS | PROC01-ACC-18 | obsługuje route_variant i route_comparability – PASS |
| PROC01-ACC-19 | obsługuje parallel_group bez podwójnego liczenia czasu – PASS | PROC01-ACC-20 | dopuszcza sumę touch_time różnych równoległych etapów > case_lead_time, gdy każdy touch_time_i ≤ stage_elapsed_time_i; touch_time ≠ work_content – PASS |
| PROC01-ACC-21 | rozróżnia repeat_visit od duplikatu – PASS | PROC01-ACC-22 | identyfikuje rework tylko przy właściwej podstawie – PASS |
| PROC01-ACC-23 | obsługuje left/right censoring i complete_case – PASS | PROC01-ACC-24 | liczy N, medianę, P75 i P90, gdy dane pozwalają – PASS |
| PROC01-ACC-25 | nie opiera diagnozy wyłącznie na mean – PASS | PROC01-ACC-26 | nie usuwa automatycznie długich obserwacji – PASS |
| PROC01-ACC-27 | liczy tail_ratio warunkowo bez progu – PASS | PROC01-ACC-28 | obsługuje 1M/3M/6M/12M i 24–36M przy danych – PASS |
| PROC01-ACC-29 | wybiera referencję zgodnie z hierarchią – PASS | PROC01-ACC-30 | nie tworzy sztucznego target_time / SLA – PASS |
| PROC01-ACC-31 | liczy on_time_rate, on_time_rate_gap_signed i adverse_on_time_rate_gap tylko przy źródłowym target/SLA – PASS | PROC01-ACC-32 | rozróżnia signed gap od adverse gap – PASS |
| PROC01-ACC-33 | wyznacza delay_metric_type i adverse_delay_exposure tylko dla porównywalnej populacji – PASS | PROC01-ACC-34 | liczy adverse_delay_exposure_share wyłącznie w jednorodnym mianowniku typu/poziomu/okresu/referencji/time_basis – PASS |
| PROC01-ACC-35 | wyznacza delay_hotspot i delay_hotspot_type bez constraint_status – PASS | PROC01-ACC-36 | obsługuje process_context_flags i required_wait_time – PASS |
| PROC01-ACC-37 | obsługuje route_mix_change oraz osobne matched_route_coverage_current/reference – PASS | PROC01-ACC-38 | oddziela new/discontinued/materially_changed route od matched history – PASS |
| PROC01-ACC-39 | dekomponuje organization→process_type→route_variant→unit→stage – PASS | PROC01-ACC-40 | zapisuje kompletne FINDINGS – PASS |
| PROC01-ACC-41 | przekazuje payload do ZOP-PRI-01 i ZOP-CONF-01 bez lokalnych score – PASS | PROC01-ACC-42 | wskazuje next_tests z uzasadnieniem – PASS |
| PROC01-ACC-43 | nie nazywa hotspotu bottleneckiem i kieruje do PROC-02 warunkowo – PASS | PROC01-ACC-44 | nie wycenia czasu w pieniądzu ani nie generuje decyzji kadrowej/capacity – PASS |
| PROC01-ACC-45 | przechodzi PROC01-T01–T23 – PASS |  |  |
| PROC01-ACC-46 | touch_time nie jest labor_input ani work_content i nie agreguje osobogodzin wielu osób – PASS | PROC01-ACC-47 | adverse_delay_exposure nie łączy różnych delay_metric_type ani nakładających się etapów w „total delay” – PASS |
| PROC01-ACC-48 | matched route counts i eligible counts dają osobne current/reference coverage; mianownik 0 → null – PASS | PROC01-ACC-49 | brak źródłowego target/SLA ustawia on_time_rate_gap_signed i adverse_on_time_rate_gap = null – PASS |
| PROC01-ACC-50 | metadane DOCX: Title/Subject/Keywords zgodne z PROC-01 – PASS |  |  |

## 17. Definition of Done PROC01-DOD-01–52

| Id | Zakres / status | Id | Zakres / status |
| --- | --- | --- | --- |
| PROC01-DOD-01 | cel – PASS | PROC01-DOD-02 | granica względem PROC-02 – PASS |
| PROC01-DOD-03 | process_scope – PASS | PROC01-DOD-04 | process_boundary_basis – PASS |
| PROC01-DOD-05 | case_id – PASS | PROC01-DOD-06 | stage – PASS |
| PROC01-DOD-07 | case_created_at/case_completed_at – PASS | PROC01-DOD-08 | case_lead_time – PASS |
| PROC01-DOD-09 | calendar_lead_time – PASS | PROC01-DOD-10 | operating_lead_time – PASS |
| PROC01-DOD-11 | time_basis i calendar contract – PASS | PROC01-DOD-12 | queue_time – PASS |
| PROC01-DOD-13 | stage_elapsed_time – PASS | PROC01-DOD-14 | touch_time: case_id × stage × visit; 0 ≤ touch_time ≤ stage_elapsed_time – PASS |
| PROC01-DOD-15 | transition_delay – PASS | PROC01-DOD-16 | non_touch_elapsed_time – PASS |
| PROC01-DOD-17 | blocked_time – PASS | PROC01-DOD-18 | routing – PASS |
| PROC01-DOD-19 | parallelism – PASS | PROC01-DOD-20 | predecessor contract – PASS |
| PROC01-DOD-21 | repeat_visit / rework – PASS | PROC01-DOD-22 | censoring – PASS |
| PROC01-DOD-23 | walidacja VAL-01–25 – PASS | PROC01-DOD-24 | rozkład N/median/P75/P90 – PASS |
| PROC01-DOD-25 | tail_ratio – PASS | PROC01-DOD-26 | horyzonty i time_bucket – PASS |
| PROC01-DOD-27 | hierarchia referencji – PASS | PROC01-DOD-28 | target/SLA – PASS |
| PROC01-DOD-29 | signed/adverse lead gap – PASS | PROC01-DOD-30 | signed/adverse queue gap – PASS |
| PROC01-DOD-31 | signed/adverse stage gap – PASS | PROC01-DOD-32 | signed/adverse transition gap – PASS |
| PROC01-DOD-33 | delay_metric_type + adverse_delay_exposure – PASS | PROC01-DOD-34 | adverse_delay_exposure_share z jednorodnym mianownikiem – PASS |
| PROC01-DOD-35 | delay_hotspot – PASS | PROC01-DOD-36 | delay_hotspot_type – PASS |
| PROC01-DOD-37 | trend i persistence – PASS | PROC01-DOD-38 | process_context_flags – PASS |
| PROC01-DOD-39 | required_wait_time – PASS | PROC01-DOD-40 | route_mix_change – PASS |
| PROC01-DOD-41 | matched route counts + coverage current/reference – PASS | PROC01-DOD-42 | new/discontinued/materially_changed route – PASS |
| PROC01-DOD-43 | dekompozycja – PASS | PROC01-DOD-44 | granica ekonomiczna – PASS |
| PROC01-DOD-45 | next_tests – PASS | PROC01-DOD-46 | PRI/CONF payload – PASS |
| PROC01-DOD-47 | FINDINGS i komunikat zarządczy – PASS | PROC01-DOD-48 | scenariusze PROC01-T01–T23 i ACC – PASS |
| PROC01-DOD-49 | touch_time ≠ labor_input ≠ work_content – PASS | PROC01-DOD-50 | on_time_rate signed/adverse gap – PASS |
| PROC01-DOD-51 | current/reference matched route coverage bez ukrywania asymetrii – PASS | PROC01-DOD-52 | metadane DOCX PROC-01 – PASS |

## 18. Test końcowy QPROC01-01–68 i status

| Id | Kontrola | Id | Kontrola |
| --- | --- | --- | --- |
| QPROC01-01 | uniwersalność branżowa – PASS | QPROC01-02 | PROC-01 ≠ PROC-02 – PASS |
| QPROC01-03 | case_lead_time pochodzi z granic procesu – PASS | QPROC01-04 | lead time ≠ suma stage times – PASS |
| QPROC01-05 | równoległość nie jest podwójnie liczona – PASS | QPROC01-06 | touch_time ≠ stage_elapsed_time; pojedynczy touch_time ≤ stage_elapsed_time – PASS |
| QPROC01-07 | queue_time wymaga ready_at lub poprawnej podstawy – PASS | QPROC01-08 | transition_delay wymaga predecessor contract – PASS |
| QPROC01-09 | wielu poprzedników bez arbitralnego previous_stage – PASS | QPROC01-10 | weekend nie jest automatycznie stratą – PASS |
| QPROC01-11 | kalendarz i time_basis są jawne – PASS | QPROC01-12 | stage_operating_time zachowuje semantykę PROC-02 – PASS |
| QPROC01-13 | system_observation_time zachowuje semantykę PROC-02 – PASS | QPROC01-14 | complete/censored są rozdzielone – PASS |
| QPROC01-15 | mean nie jest jedyną miarą – PASS | QPROC01-16 | mediana/P75/P90 istnieją, gdy N pozwala – PASS |
| QPROC01-17 | długie obserwacje nie są automatycznie usuwane – PASS | QPROC01-18 | tail_ratio jest opisowy i bez progu – PASS |
| QPROC01-19 | route_variant są kontrolowane – PASS | QPROC01-20 | równoległość nie tworzy udziałów >100% lead time – PASS |
| QPROC01-21 | repeat_visit ≠ automatycznie duplikat – PASS | QPROC01-22 | rework wymaga podstawy – PASS |
| QPROC01-23 | non_touch_elapsed_time wymaga touch_time – PASS | QPROC01-24 | non_touch_elapsed_time ≠ automatycznie waste – PASS |
| QPROC01-25 | blocked_time wymaga źródła – PASS | QPROC01-26 | required_wait_time ≠ automatycznie opóźnienie do usunięcia – PASS |
| QPROC01-27 | route mix jest kontrolowany – PASS | QPROC01-28 | matched_route_coverage_current i reference są jawne osobno – PASS |
| QPROC01-29 | new route nie dostaje sztucznej referencji – PASS | QPROC01-30 | materially_changed route nie jest wciskane do historii – PASS |
| QPROC01-31 | SLA/target nie jest wymyślany; on_time gaps tylko z targetu – PASS | QPROC01-32 | signed gap ≠ adverse gap – PASS |
| QPROC01-33 | delay_metric_type + adverse_delay_exposure ≠ recoverable time – PASS | QPROC01-34 | adverse_delay_exposure_share ma jednorodny mianownik i ≠ udział w przyczynie – PASS |
| QPROC01-35 | delay_hotspot ≠ bottleneck – PASS | QPROC01-36 | PROC-01 nie nadaje constraint_status – PASS |
| QPROC01-37 | elapsed increase ≠ automatycznie wolniejszy pracownik – PASS | QPROC01-38 | queue increase ≠ automatycznie potrzeba zatrudnienia – PASS |
| QPROC01-39 | brak arbitralnych benchmarków czasu – PASS | QPROC01-40 | brak arbitralnych progów czasu – PASS |
| QPROC01-41 | brak automatycznej wyceny czasu w pieniądzu – PASS | QPROC01-42 | brak automatycznej rekomendacji zatrudnienia – PASS |
| QPROC01-43 | brak automatycznej rekomendacji zwiększenia capacity – PASS | QPROC01-44 | hipoteza ≠ przyczyna – PASS |
| QPROC01-45 | next_tests istnieją – PASS | QPROC01-46 | payload ZOP-PRI-01 istnieje bez score – PASS |
| QPROC01-47 | payload ZOP-CONF-01 istnieje bez score – PASS | QPROC01-48 | FINDINGS zgodne z architekturą X-Ray – PASS |
| QPROC01-49 | statusy STANDARD/MEDIUM/HIGH/CRITICAL nie są tworzone lokalnie – PASS | QPROC01-50 | PROC-02 pozostaje niezmieniony – PASS |
| QPROC01-51 | FIN-01 pozostaje niezmieniony – PASS | QPROC01-52 | CAP-01 pozostaje niezmieniony – PASS |
| QPROC01-53 | HR-01 pozostaje niezmieniony – PASS | QPROC01-54 | PORT-01 pozostaje niezmieniony – PASS |
| QPROC01-55 | ZOP-TECH-01 pozostaje niezmieniony – PASS | QPROC01-56 | ZOP-MASTER-01 pozostaje niezmieniony – PASS |
| QPROC01-57 | ZOP-PRI-01 pozostaje DO OPRACOWANIA – PASS | QPROC01-58 | ZOP-CONF-01 pozostaje DO OPRACOWANIA – PASS |
| QPROC01-59 | 0 danych SPZOZ i 0 danych pacjentów – PASS | QPROC01-60 | 0 rozpoczętego PROC-03 – PASS |
| QPROC01-61 | touch_time dotyczy case_id × stage × visit i jest nieujemny – PASS | QPROC01-62 | touch_time ≠ labor_input ≠ work_content; brak agregacji osobogodzin – PASS |
| QPROC01-63 | delay_metric_type rozdziela lead/queue/stage/transition/lateness exposure – PASS | QPROC01-64 | brak wspólnego denominatora adverse share dla różnych delay_metric_type – PASS |
| QPROC01-65 | on_time_rate_gap_signed/adverse są zdefiniowane; bez targetu = null – PASS | QPROC01-66 | matched route current/reference coverage i liczniki są jawne; mianownik 0 → null – PASS |
| QPROC01-67 | PROC01-T01–T23 kompletne – PASS | QPROC01-68 | Title/Subject/Keywords DOCX zgodne z PROC-01 – PASS |

### 18.1. Otwarte kwestie wspólne – poza PROC-01

| Kwestia | Status / wpływ |
| --- | --- |
| globalny standard kalendarzy operacyjnych | PROC-01 przechowuje jawny calendar_id/calendar_basis; nie zamyka standardu globalnego |
| globalny kontrakt work_content | pozostaje poza PROC-01; HR/CAP/PROC korzystają tylko z jawnych podstaw |
| ZOP-PRI-01 – Priority Score | PROC-01 dostarcza payload, nie progi ani wzór |
| ZOP-CONF-01 – Confidence Score | PROC-01 dostarcza jakość danych i porównywalności, nie score |
| orkiestracja next_tests / formalny critical path | reguły uruchamiania i pełny CPM pozostają modułami wspólnymi przyszłości |

> **STATUS KOŃCOWY PROC-01 ZAMKNIĘTY METODOLOGICZNIE DO IMPLEMENTACJI. ZOP-PRI-01 – DO OPRACOWANIA. ZOP-CONF-01 – DO OPRACOWANIA.**

0 arbitralnych progów czasu; 0 sztucznego SLA; 0 automatycznej wyceny czasu w pieniądzu; 0 automatycznych rekomendacji kadrowych; 0 nowych progów Priority Score; 0 nowych progów Confidence Score; 0 danych SPZOZ; 0 danych pacjentów; 0 rozpoczętego PROC-03.
