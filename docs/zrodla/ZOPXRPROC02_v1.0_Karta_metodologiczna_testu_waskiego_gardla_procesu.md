ZOPTYMALIZOWANI – X-RAY

# PROC-02

# Wąskie gardło procesu

Karta metodologiczna i specyfikacja implementacyjna

> **STATUS PROC-02 ZAMKNIĘTY METODOLOGICZNIE DO IMPLEMENTACJI**

| Pole | Wartość |
| --- | --- |
| Identyfikator | ZOP-XR-PROC-02 |
| Wersja / data | v1.0 / 2 września 2026 |
| Rola | piąty pełny test diagnostyczny X-Ray; wzorzec rodziny testów procesowych |
| Odbiorcy | zarządzający, analityk, Aleksander – implementacja |
| Źródła nadrzędne | niniejsze polecenie; FIN-01 v1.0; CAP-01 v1.0; HR-01 v1.0; PORT-01 v1.0; ZOP-TECH-01; ZOP-MASTER-01 v1.1 |
| Zależności | ZOP-PRI-01 i ZOP-CONF-01 – DO OPRACOWANIA |

Dokument jednocześnie definiuje metodę wykrywania rzeczywistego ograniczenia przepływu, kontrakt danych, reguły walidacji i obliczeń, strukturę FINDINGS, scenariusze regresyjne oraz kryteria odbioru implementacji. Nie projektuje PROC-01, PROC-03, aplikacji, panelu ani warstwy AI.

> **GRANICA PROC-02 może liczyć miary czasowe potrzebne do identyfikacji ograniczenia, ale nie zastępuje pełnej metodologii PROC-01. PROC-02 odpowiada na pytanie „co ogranicza przepływ systemu?”, a nie „gdzie i dlaczego tracimy czas?”.**

## 1. Rola, cel i granice PROC-02

PROC-02 bada przepływ przypadków przez proces i identyfikuje etap, zasób, regułę lub mechanizm, który realnie ogranicza zdolność całego badanego systemu do kończenia pracy. Test rozdziela miejsce, w którym problem jest widoczny, od miejsca, które rzeczywiście ogranicza przepustowość.

> **PYTANIE DIAGNOSTYCZNE Który etap, zasób, reguła lub mechanizm procesu realnie ogranicza przepływ badanego systemu, jak trwałe jest to ograniczenie, jaki jest jego wpływ na kolejkę i przepustowość oraz czy mamy do czynienia z rzeczywistym wąskim gardłem, czy tylko z miejscem, w którym problem staje się widoczny?**

### 1.1. Łańcuch diagnostyczny

| Etap | Produkt | Granica |
| --- | --- | --- |
| Przypadek | jednoznaczny case_id | bez założeń branżowych |
| Ścieżka | route_variant i stage_sequence | bez mieszania nieporównywalnych tras |
| Napływ | stage_arrivals | gotowość do etapu musi mieć podstawę |
| Oczekiwanie | queue_time i queue_wip | kolejka ≠ praca aktywna |
| Realizacja | stage_elapsed_time / touch_time | czas kalendarzowy ≠ praca aktywna |
| Przepustowość | stage_throughput_rate i system_throughput_rate | etap ≠ system |
| Zdolność | effective_available i work_content | zgodne capacity_unit |
| Ograniczenie | evidence vector + constraint_status | sygnał ≠ verified constraint |
| Wpływ systemowy | flow_evidence, throughput_response | bez automatycznej wyceny |
| Hipotezy | mechanizmy do weryfikacji | hipoteza ≠ przyczyna |
| Kolejne testy | next_tests z uzasadnieniem | bez projektowania testów następczych |

> **ZASADA NADRZĘDNA Wąskie gardło nie jest etapem, który wygląda najgorzej. Jest ograniczeniem, które realnie limituje przepływ badanego systemu.**

| Sygnał | Dlaczego nie wystarcza |
| --- | --- |
| najdłuższy etap | może mieć dużą równoległość i nie ograniczać throughput |
| największa kolejka | może być miejscem ujawnienia problemu wcześniejszego lub efektem batchingu |
| najdroższy etap | koszt nie dowodzi ograniczenia przepływu |
| najwyższe wykorzystanie | wysokie U bez presji na przepływ nie oznacza constraint |
| największy WIP | WIP wymaga referencji i rozdzielenia kolejki od pracy aktywnej |
| wskazanie użytkownika | jest hipotezą wymagającą danych |

## 2. Jednostki analizy i kontrakt danych

### 2.1. case_id – przypadek

Podstawową jednostką procesu jest case_id. Może oznaczać zlecenie, zamówienie, sprawę, paczkę, zgłoszenie, projekt, jednostkę produkcyjną, klienta przechodzącego przez proces albo inny mierzalny przypadek. PROC-02 nie zakłada charakteru branżowego.

### 2.2. stage – etap

Podstawową jednostką dekompozycji jest stage. Etap powinien mieć możliwie stabilną definicję w czasie. Opcjonalne pola stage_id, stage_name, stage_sequence, stage_group i stage_resource_group służą identyfikacji, kolejności i mapowaniu zasobów. Istotnie zmienionej definicji etapu nie porównuje się bez właściwego oznaczenia.

### 2.3. Bazowa tabela PROCESS

| Tabela | Pola bazowe | Rola PROC-02 |
| --- | --- | --- |
| PROCESS | case_id, stage, start, end, unit | zdarzenia przejścia przypadków przez proces |
| RESOURCE – opcjonalna | date, unit, resource, available, used, cost | zdolność i wykorzystanie przy wiarygodnym mapowaniu stage → resource_group |
| ACTIVITY – opcjonalna | date, unit, product, volume, revenue | portfolio_item / sygnał miksu i skali |
| PLAN – opcjonalna | date, unit, metric, target | referencja planowa dla czasu, przepustowości lub zdolności |

> **NIEZMIENNOŚĆ MODELU PROC-02 nie zmienia bazowych tabel ZOP-TECH-01. Wszystkie dodatkowe pola są rozszerzeniami pomocniczymi.**

### 2.4. Rozszerzenia PROC-02

| Grupa | Pola techniczne |
| --- | --- |
| Proces i routing | process_type; route_variant; route_comparability; stage_sequence; parallel_group; case_status |
| Czas | ready_at; case_created_at; case_completed_at; stage_time_basis; touch_time; blocked_time; predecessor_relation; predecessor_stage |
| Powroty | repeat_visit; rework_iteration |
| Portfel / praca | portfolio_item; work_content; work_content_unit; work_content_comparability |
| Zasoby | resource_group; capacity_mapping_quality; effective_available; capacity_unit |
| Constraint | constraint_entity_type; constraint_entity_id; constraint_entity_scope; constraint_status; constraint_verification_basis; constraint_entity_by_bucket; constraint_stage_by_bucket; constraint_migration |
| Kontrola | exclusion_flags; validation_notes; arrival_basis; stage_operating_time; stage_operating_time_unit; operating_time_basis; system_observation_time; system_observation_time_unit; system_observation_time_basis; time_bucket |

## 3. Model czasu, gotowość i routing

### 3.1. Cztery różne czasy

| Miara | Definicja | Reguła ochronna |
| --- | --- | --- |
| queue_time | czas od ready_at do start | nie twórz bez wiarygodnej gotowości do etapu |
| stage_elapsed_time | czas kalendarzowy od start do end | nie nazywaj automatycznie aktywną pracą |
| touch_time | rzeczywisty aktywny czas pracy | brak pomiaru → null; nie zastępuj end − start |
| transition_delay | ready_at_current − predecessor_completion_at | poprzednik i moment spełnienia zależności muszą wynikać z udokumentowanego kontraktu procesu |

| queue_time | queue_time = start − ready_at |
| --- | --- |

| stage_elapsed_time | stage_elapsed_time = end − start |
| --- | --- |

| transition_delay | transition_delay = ready_at_current − predecessor_completion_at |
| --- | --- |
| jeden poprzednik | predecessor_completion_at = end_predecessor |
| wielu wymaganych poprzedników | jeżeli wszystkie muszą być zakończone: predecessor_completion_at = max(end_required_predecessors); przy innej logice użyj udokumentowanej reguły zależności |

### 3.2. ready_at – początek kolejki

Najlepszym źródłem początku kolejki jest ready_at – moment, w którym przypadek spełnia warunki wejścia do etapu. end_previous_stage może być użyty jako przybliżenie tylko przy procesie sekwencyjnym, natychmiastowej gotowości po poprzednim etapie oraz braku odrębnego transportu, decyzji, warunku biznesowego lub kalendarza. W przeciwnym razie queue_time pozostaje null i ograniczenie trafia do validation_notes.

### 3.3. Routing, równoległość i powroty

| Sytuacja | Zachowanie PROC-02 |
| --- | --- |
| proces sekwencyjny | kontroluj stage_sequence i przejścia pomiędzy etapami |
| warianty ścieżki | użyj route_variant; istotnie różne warianty analizuj osobno |
| etap opcjonalny | brak etapu nie jest błędem, jeżeli wariant go nie wymaga |
| proces równoległy | nakładanie czasów jest dozwolone przy parallel_group lub innej dokumentacji |
| powrót do etapu | repeat_visit/rework_iteration; nie usuwaj automatycznie jako duplikatu |
| nieznane znaczenie powtórzenia | zachowaj zdarzenie; nie nazywaj automatycznie reworkiem |
| wielu poprzedników | użyj predecessor_relation / predecessor_stage; nie wybieraj arbitralnie jednego previous_stage; gdy zależności nie można odtworzyć, transition_delay=null i validation_notes |

## 4. Walidacja danych PROC02-VAL-01–24

| Id | Kontrola | Skutek negatywny |
| --- | --- | --- |
| PROC02-VAL-01 | istnieje case_id | CRITICAL dla rekonstrukcji procesu |
| PROC02-VAL-02 | istnieje stage | CRITICAL dla dekompozycji |
| PROC02-VAL-03 | istnieje start | CRITICAL dla przejścia przez etap |
| PROC02-VAL-04 | istnieje end albo przypadek jest jawnie otwarty | CRITICAL/WARNING zależnie od modułu |
| PROC02-VAL-05 | end ≥ start | CRITICAL dla rekordu |
| PROC02-VAL-06 | znaczniki czasu mają spójną strefę / bazę | CRITICAL dla nieusuwalnej niespójności |
| PROC02-VAL-07 | stage ma stabilną definicję | WARNING/CRITICAL dla porównań |
| PROC02-VAL-08 | route_variant można odtworzyć albo jawnie brak tej możliwości | WARNING/CRITICAL dla agregacji tras |
| PROC02-VAL-09 | stage_sequence jest spójna | WARNING/CRITICAL dla routingu |
| PROC02-VAL-10 | powtórzenia etapu są odróżniane od duplikatów | CRITICAL przy ryzyku fałszywego usuwania |
| PROC02-VAL-11 | równoległość nie jest błędnie uznawana za błąd | WARNING/CRITICAL dla kolejności |
| PROC02-VAL-12 | ready_at ≤ start, jeżeli ready_at istnieje | CRITICAL dla queue_time |
| PROC02-VAL-13 | predecessor_relation / predecessor_stage pozwalają prawidłowo odtworzyć poprzednika lub logikę wielu poprzedników | WARNING/CRITICAL dla transition_delay; przy braku jednoznacznej relacji transition_delay=null |
| PROC02-VAL-14 | przypadki otwarte są jawnie oznaczone | WARNING/CRITICAL dla WIP/czasu |
| PROC02-VAL-15 | przypadki na granicach okresu są rozpoznane | WARNING dla miar okresowych |
| PROC02-VAL-16 | brak niewyjaśnionych duplikatów zdarzeń | CRITICAL, gdy grozi podwójnym liczeniem |
| PROC02-VAL-17 | resource_group jest wiarygodnie mapowany do stage przy analizie capacity | WARNING/CRITICAL dla capacity |
| PROC02-VAL-18 | capacity_unit jest zgodna | CRITICAL dla bilansu capacity |
| PROC02-VAL-19 | portfolio_item jest poprawnie przypisany przy analizie miksu | WARNING/CRITICAL dla miksu |
| PROC02-VAL-20 | route_comparability pozwala porównać okresy | WARNING/CRITICAL dla trendu |
| PROC02-VAL-21 | istnieje właściwy okres odniesienia | WARNING; luki referencyjne = null |
| PROC02-VAL-22 | definicja terminalnego zakończenia procesu jest znana | CRITICAL dla system throughput / system WIP |
| PROC02-VAL-23 | odrzucenia, anulowania i wyjścia są jawnie rozpoznawane | WARNING/CRITICAL dla flow conservation |
| PROC02-VAL-24 | przepływ między etapami może być uzgodniony | WARNING/CRITICAL wg skali flow gap |

### 4.1. Reguły wykonania

| Sytuacja | Zachowanie |
| --- | --- |
| CRITICAL globalny | TEST_BLOCKED dla zależnej diagnozy; brak wartości zastępczych |
| CRITICAL lokalny | wyłączenie zakresu lub modułu; poprawne części mogą działać jako TEST_PARTIAL |
| WARNING | kontynuacja z validation_required i validation_notes, jeśli wpływ jest istotny |
| brak wymaganej podstawy | miara = null / not_computable; bez sztucznego proxy |
| sprzeczność danych z evidence | verified_constraint zabroniony do wyjaśnienia sprzeczności |

## 5. Cenzorowanie i zdarzenia przepływu

### 5.1. Przypadki na granicach okna

| Klasa | Definicja | Dopuszczalne użycie |
| --- | --- | --- |
| left_censored_case | przypadek rozpoczął proces przed początkiem okna | nie używaj jako pełnej obserwacji lead time; może zasilać WIP |
| right_censored_case | przypadek nie osiągnął terminalnego końca do końca okna | nie używaj jako zakończonego czasu procesu; może zasilać WIP |
| complete_case | początek i terminalne zakończenie są obserwowane zgodnie z zakresem | pełne miary czasu i przepływu |

### 5.2. Arrivals, starts i completions

| Miara | Definicja |
| --- | --- |
| stage_arrivals | liczba przypadków gotowych do wejścia w stage w oknie; preferowane ready_at |
| arrival_basis | ready_at albo udokumentowany proxy end_previous_stage |
| stage_starts | liczba rzeczywistych rozpoczęć etapu w oknie |
| stage_completions | liczba zakończonych przejść przez etap w oknie |
| unique_cases_started/completed | liczba unikalnych case_id – osobno od liczby przejść przy powrotach |

> **REWORK Każde rzeczywiste ponowne rozpoczęcie lub zakończenie etapu jest zdarzeniem przepływu. Liczba unikalnych case_id nie może zastępować liczby przejść, gdy powroty zwiększają obciążenie procesu.**

## 6. Przepustowość, kolejka i WIP

### 6.1. Przepustowość etapu i systemu

| stage_throughput_rate | stage_throughput_rate = stage_completions / stage_operating_time; stage_operating_time = 0 → null / not_computable |
| --- | --- |
| system_throughput_rate | system_throughput_rate = system_completions / system_observation_time; wymagane jawne system_observation_time_basis i zgodna jednostka |

stage_operating_time musi mieć jednoznaczną operating_time_basis i stage_operating_time_unit. stage_throughput_rate liczy się wyłącznie przy poprawnie zdefiniowanym mianowniku. Jeżeli stage_operating_time = 0, wynik = null / not_computable. Dla całego procesu system_observation_time musi mieć jawne system_observation_time_basis i system_observation_time_unit. Wskaźników opartych na różnych podstawach czasu nie porównuje się bez odpowiedniego oznaczenia. Wspólny standard kalendarzy operacyjnych pozostaje kwestią otwartą poza PROC-02.

system_throughput_rate to liczba prawidłowo zakończonych przypadków całego procesu na jednostkę jawnie zdefiniowanego system_observation_time, zgodnie ze zdefiniowanym terminalnym zakończeniem. Stage throughput i system throughput są odrębnymi miarami i nie wolno ich zamieniać.

### 6.2. Kolejka

Jeżeli istnieje wiarygodne ready_at, Queue(t) obejmuje przypadki gotowe do wejścia do etapu, dla których ready_at ≤ t oraz start > t albo start jeszcze nie wystąpił. Z tej funkcji mogą powstać queue_start, queue_end, queue_peak i queue_average.

| queue_delta | queue_delta = queue_end − queue_start |
| --- | --- |

| kontrola przepływu | queue_delta ≈ stage_arrivals − stage_starts |
| --- | --- |

Różnica wymaga uwzględnienia przypadków granicznych i zmian statusów. Dodatnia queue_delta oznacza narastanie kolejki, ale jeszcze nie dowodzi bottleneck.

### 6.3. WIP

| Miara | Definicja |
| --- | --- |
| queue_wip | przypadki gotowe, ale jeszcze nierozpoczęte |
| active_wip | przypadki rozpoczęte na etapie, ale niezakończone |
| stage_wip | queue_wip + active_wip |
| system_wip | przypadki rozpoczęte w procesie, które nie osiągnęły terminalnego zakończenia |

> **OCHRONA Wysoki WIP nie jest automatycznie błędem. Queue WIP i active WIP odpowiadają na różne pytania i muszą pozostać rozdzielone.**

## 7. Referencje, horyzonty i rozkład czasu

### 7.1. Hierarchia wartości odniesienia

| Priorytet | Źródło | Warunek |
| --- | --- | --- |
| 1 | historia tego samego stage w tym samym route_variant | stabilna definicja i porównywalny zakres |
| 2 | wcześniejszy porównywalny okres | zgodność trasy, kalendarza i struktury pracy |
| 3 | plan | jawna definicja miary i okresu |
| 4 | porównywalny etap wewnętrzny | udokumentowana process/stage comparability |
| 5 | najlepszy własny stabilny okres | bez istotnego zdarzenia wyjątkowego |
| 6 | benchmark zewnętrzny | wiarygodne źródło i zgodne definicje |

> **BRAK PROGU PROC-02 nie tworzy arbitralnego maksymalnego czasu kolejki, docelowego WIP, docelowego utilization ani progu bottleneck. Brak wiarygodnej referencji pozostawia zależną lukę jako null.**

### 7.2. Horyzonty i time_bucket

| Horyzont | Rola |
| --- | --- |
| 1M | sygnał bieżący i porównanie podstawowe |
| 3M | potwierdzenie krótkoterminowe |
| 6M | trwałość średnioterminowa |
| 12M / r/r | sezonowość i porównanie roczne |
| 24–36M | trwałość, migracja constraint i zmiany strukturalne |
| dzień / tydzień / zmiana / inne naturalne okno | analiza operacyjna tylko przy odpowiedniej granularności danych |

Każdy wynik zapisuje time_bucket i jego podstawę. Granularność wynika z danych i naturalnego cyklu operacyjnego; nie jest narzucana arbitralnie.

### 7.3. Mediana i ogony rozkładu

Dla queue_time, stage_elapsed_time i transition_delay preferowane są co najmniej mediana, P75 i P90; P95 jest opcjonalne. Diagnoza nie opiera się wyłącznie na średniej. Percentyli nie wymaga się przy zbyt małej liczebności – wynik pozostaje null lub opatrzony ograniczeniem jakości.

## 8. Model dowodowy ograniczenia przepływu

> **REGUŁA KRYTYCZNA Etap może być bardzo długi, mieć dużą kolejkę albo wysokie wykorzystanie i nadal nie być wąskim gardłem. PROC-02 wymaga dowodu wpływu na przepływ całego systemu.**

### 8.1. Sześć rodzajów dowodu

| Pole | Znaczenie | Przykładowa podstawa |
| --- | --- | --- |
| queue_evidence | presja widoczna w kolejce lub czasie oczekiwania | narastająca queue_delta; pogorszenie queue_time |
| capacity_evidence | udokumentowana niewystarczająca zdolność względem zapotrzebowania | capacity balance albo CAP-02 confirmation |
| flow_evidence | ograniczenie wskazanego constraint_entity przekłada się na przepływ downstream lub system throughput | spójny wzorzec przepływu i zasilania |
| starvation_evidence | kolejny etap ma zdolność, lecz nie dostaje wystarczającej pracy | wolna capacity + brak kolejki + niski arrivals downstream |
| response_evidence | uwolnienie podejrzanego constraint_entity poprawia przepływ systemu | operational change / controlled test przy porównywalnych warunkach |
| mechanism_evidence | udokumentowany mechanizm organizacyjny bezpośrednio ogranicza uwalnianie pracy albo przepływ między częściami systemu | reguła/bramka/harmonogram/akceptacja/handoff + zgodny wzorzec przepływu; sama opinia użytkownika nie wystarcza |

Każde pole evidence przyjmuje true, false albo null/not_assessable. Brak danych nie jest dowodem negatywnym, w szczególności mechanism_evidence bez podstawy = null/not_assessable, a nie false. PROC-02 nie zamienia evidence vector w lokalny score 0–100.

### 8.2. constraint_status

| Status | Znaczenie |
| --- | --- |
| not_detected | brak podstaw do wskazania ograniczenia dla badanego constraint_entity |
| candidate_constraint | istnieją sygnały, że wskazany constraint_entity może ograniczać przepływ, ale brakuje pełnego potwierdzenia systemowego |
| verified_constraint | spełniona bramka dowodowa ograniczenia systemowego dla wskazanego constraint_entity |
| unresolved | dane lub sprzeczne sygnały uniemożliwiają odpowiedzialne rozstrzygnięcie dla wskazanego constraint_entity |

constraint_status zawsze odnosi się do jednoznacznie wskazanego constraint_entity: constraint_entity_type, constraint_entity_id i constraint_entity_scope. Dopuszczalne constraint_entity_type obejmują co najmniej: stage, resource_group, gate_rule, handoff, system. Stage pozostaje podstawową i najczęstszą jednostką dekompozycji. Nie tworzy się sztucznych stage wyłącznie po to, aby zakodować regułę biznesową.

### 8.3. Bramka verified_constraint

> **WYMAGANIE verified_constraint dla wskazanego constraint_entity wymaga: flow_evidence = true ORAZ co najmniej jednego z: capacity_evidence = true LUB response_evidence = true LUB mechanism_evidence = true, a także braku krytycznej sprzeczności danych. mechanism_evidence nie może wynikać wyłącznie z opinii użytkownika: wymaga udokumentowanej reguły lub mechanizmu oraz zgodnego z nim wzorca przepływu. Jeżeli warunek nie jest spełniony, constraint_entity pozostaje candidate_constraint albo unresolved.**

### 8.4. constraint_verification_basis

| Wartość | Znaczenie |
| --- | --- |
| capacity_balance | zgodny jednostkowo bilans required_capacity ↔ effective_available |
| CAP_02_confirmation | potwierdzenie przeciążenia przez przyszły CAP-02 |
| flow_pattern | spójny wzorzec systemowego ograniczenia przepływu |
| operational_change | udokumentowana zmiana operacyjna i porównywalny efekt |
| controlled_test | kontrolowana próba zwiększenia przepustowości/zdolności |
| manual_validation | ręczna walidacja operacyjna z udokumentowaną podstawą |
| multiple_sources | zgodne potwierdzenie z kilku niezależnych źródeł |
| documented_mechanism | udokumentowana reguła, bramka, ograniczenie harmonogramowe, warunek akceptacji lub mechanizm przekazania wraz ze zgodnym wzorcem przepływu |

Przypadkowa korelacja czasowa nie jest podstawą verified_constraint.

## 9. Mechanizmy szczególne: starvation, blocking, batching i migracja

### 9.1. Niedostateczne zasilanie – starvation

Jeżeli etap ma wolną capacity, brak kolejki i niską liczbę arrivals, a wcześniejszy etap nie dostarcza pracy, możliwy jest starvation_signal. Taki etap nie jest źródłem ograniczenia tylko dlatego, że ma niskie wykorzystanie. Analiza kieruje się upstream.

### 9.2. Blocking a handoff delay

| Sytuacja | Dopuszczalny wniosek |
| --- | --- |
| wiarygodny blocked_time pokazuje zajęcie zasobu po zakończeniu pracy | blocking signal; sprawdź downstream |
| długi czas po end bez dowodu zajęcia zasobu | handoff_delay / transition_delay; nie nazywaj blocking |

### 9.3. Ograniczenie organizacyjne / procesowe

Zdolność teoretycznie może istnieć, a przepływ nadal być ograniczony przez grafik, okna dostępności, batching, regułę akceptacji, decyzję, przekazanie między jednostkami, priorytety lub dostęp do informacji. Jeżeli taki mechanizm jest udokumentowany i zgodny z obserwowanym wzorcem przepływu, może stanowić mechanism_evidence i zostać wskazany jako constraint_entity typu gate_rule, handoff lub system. Nie nazywa się go automatycznie niedoborem capacity.

### 9.4. Batching

Przy pracy partiami kolejka może cyklicznie rosnąć i gwałtownie spadać. batching_signal wymaga analizy pełnego cyklu. Sam queue_peak nie dowodzi trwałego bottleneck.

### 9.5. Wędrujące ograniczenie

constraint_entity_by_bucket przechowuje wskazany constraint_entity w kolejnych time_bucket. Dla sytuacji stage-level zachowuje się constraint_stage_by_bucket jako pole kompatybilne. Jeżeli ograniczenie przesuwa się między etapami, resource_group, gate_rule, handoff lub poziomem systemowym, constraint_migration=true. PROC-02 opisuje wtedy wędrujące / niestabilne ograniczenie procesu i nie wymusza jednego stałego bottleneck.

## 10. Work content, miks przypadków i bilans capacity

### 10.1. Case count ≠ work content

Sto przypadków prostych nie musi odpowiadać stu przypadkom złożonym. Gdy portfolio_item lub work_content wskazują zmianę struktury pracy, sama liczba case_id nie jest wystarczającą miarą zapotrzebowania. work_content_comparability określa, czy obciążenie można odpowiedzialnie porównywać między okresami.

### 10.2. Rework load

| repeat_visit_rate | repeat_visit_rate = repeat_visit_count / liczba właściwych przypadków bazowych |
| --- | --- |

Mianownik musi odpowiadać zdefiniowanemu scope; powtórzenie nie jest automatycznie reworkiem.

rework_load może być liczony tylko wtedy, gdy znaczenie powtórnej pracy zostało potwierdzone. Powtórna praca może zwiększać obciążenie constraint bez zmiany liczby unikalnych przypadków.

### 10.3. Capacity w PROC-02

Mapowanie stage → resource_group jest używane tylko przy wystarczającej capacity_mapping_quality. PROC-02 przejmuje z CAP zasady available_source/effective_available/used/capacity_unit. Nie zestawia liczby spraw z godzinami capacity bez właściwego work_content albo innego udokumentowanego przelicznika.

### 10.4. Bilans zapotrzebowania i zdolności

| required_capacity | required_capacity = Σ work_content |
| --- | --- |

| capacity_pressure_ratio | capacity_pressure_ratio = required_capacity / effective_available |
| --- | --- |

Wyłącznie przy zgodnych work_content_unit i capacity_unit. effective_available = 0 → null/not_computable, a nie wartość zastępcza.

> **INTERPRETACJA Wartość 1 oznacza matematycznie równość zapotrzebowania i dostępnej zdolności w danym modelu. Nie jest arbitralnym progiem bottleneck i nadal wymaga walidacji zakresu, czasu i jakości work_content.**

## 11. Wpływ na system, uwolnienie ograniczenia i kontrole pomocnicze

### 11.1. System throughput a constraint

PROC-02 sprawdza, czy podejrzany constraint_entity rzeczywiście ogranicza system_throughput_rate. Sam fakt, że etap lub zasób jest zajęty, nie wystarcza. Jeżeli zwiększenie przepustowości wskazanego miejsca nie poprawia system throughput, a kolejka tworzy się dalej, możliwe jest przesunięcie constraint.

### 11.2. constraint_release_event i throughput_response

Jeżeli w danych historycznych występuje zwiększenie godzin, dodatkowa zmiana, zmiana grafiku, automatyzacja, zwiększenie wydajności lub dodatkowy zasób i można porównać podobne okresy, system zapisuje constraint_release_event oraz throughput_response. Może to stanowić response_evidence tylko przy wystarczającej porównywalności innych istotnych warunków.

### 11.3. delay_hotspot

> **ODRĘBNE ZJAWISKO Etap z długim stage_elapsed_time, transition_delay lub dużym udziałem w lead time może być delay_hotspot bez spełnienia warunków candidate_constraint. Wtedy rekomendowany jest PROC-01, a nie etykieta bottleneck.**

### 11.4. Flow conservation

Na porównywalnej trasie system uzgadnia napływ, przejścia, zakończenia, anulowania, wyjścia i WIP. flow_reconciliation_gap przechowuje niewyjaśnioną różnicę. Duży, niewyjaśniony gap ustawia validation_required=true i może ograniczyć lub zablokować interpretację constraint.

### 11.5. Little’s Law – wyłącznie kontrola

| kontrola spójności | WIP ≈ Throughput × Flow Time |
| --- | --- |

Stosuj pomocniczo tylko przy wystarczająco stabilnym procesie i zgodnych definicjach. Nie wymuszaj w silnej sezonowości, gwałtownej zmianie popytu, rozruchu ani przy dużej liczbie otwartych przypadków.

## 12. Dekompozycja, luki i granica ekonomiczna

### 12.1. Poziomy dekompozycji

| Poziom | Klucz | Minimalny wynik |
| --- | --- | --- |
| I | organization | system throughput, WIP, status ograniczenia |
| II | process_type | wynik procesu i główne route_variant |
| III | route_variant | porównywalny przepływ dla wariantu |
| IV | unit | lokalizacja organizacyjna |
| V | stage | arrivals/starts/completions, queue, throughput, evidence |
| VI – opcjonalny | resource_group | capacity i utilization przy wiarygodnym mapowaniu |
| opcjonalny | portfolio_item | wyjaśnienie miksu i work content |

### 12.2. Udział w kolejce i opóźnieniu

| queue_share_i | queue_share_i = queue_end_i / Σ queue_end |
| --- | --- |

Wyłącznie dla porównywalnych zakresów. Udział w kolejce nie jest udziałem w przyczynie bottleneck.

### 12.3. Luka czasu oczekiwania

| queue_time_gap_signed | queue_time_gap_signed = queue_time_current − queue_time_reference |
| --- | --- |

| adverse_queue_time_gap | adverse_queue_time_gap = max(queue_time_gap_signed, 0) |
| --- | --- |

Dodatnia wartość oznacza pogorszenie względem referencji. Ujemna wartość podpisanej luki pozostaje sygnałem poprawy/kompensacji.

### 12.4. Luka przepustowości

| throughput_gap | throughput_gap = throughput_reference − throughput_current |
| --- | --- |

Referencja może pochodzić z historii, planu lub potwierdzonej zdolności. Luka nie jest automatycznie utraconą sprzedażą ani stratą.

### 12.5. Granica ekonomiczna

> **BEZ AUTOMATYCZNEJ WYCENY PROC-02 nie przelicza kolejki, opóźnienia ani throughput_gap na pieniądze. Przekazuje liczbę przypadków, czas, capacity units, throughput gap i affected portfolio items do FIN-01, PORT-01 lub FIN-03.**

## 13. Hipotezy, next_tests i relacja z innymi testami

### 13.1. Hipotezy do weryfikacji

| Grupa | Dopuszczalne hipotezy |
| --- | --- |
| ZDOLNOŚĆ | niewystarczająca capacity; przeciążenie; przestój; awaria |
| ORGANIZACJA | zły harmonogram; batching; priorytety; praca falami; okna dostępności |
| ZASILANIE / PRZEKAZANIE | brak zasilania; problem wcześniejszego etapu; transfer między jednostkami; brak informacji |
| REGUŁA / DECYZJA | akceptacja; decyzja; reguła biznesowa |
| PRACA / JAKOŚĆ | rework; większa pracochłonność; brak kompetencji |
| PORTFEL | zmiana portfolio mix; inna struktura przypadków |
| DANE | błąd danych; błędny routing; brak gotowości; niespójne mapowanie capacity |

> **ETYKIETA OBOWIĄZKOWA Każdy mechanizm pozostaje HIPOTEZĄ DO WERYFIKACJI, dopóki nie istnieje właściwa podstawa dowodowa. Evidence vector nie zastępuje analizy przyczynowej.**

### 13.2. next_tests

| next_test | Warunek rekomendacji | Cel |
| --- | --- | --- |
| PROC-01 | problem dotyczy głównie czasu, opóźnienia, transition delay lub delay_hotspot | pełna analiza czasu procesu – metodologia poza PROC-02 |
| CAP-01 | podejrzenie niewykorzystania dostępnej zdolności | wykorzystanie zasobu |
| CAP-02 | presja ponad dostępne capacity / przeciążenie | potwierdzenie przeciążenia – metodologia poza PROC-02 |
| HR-01 | ograniczenie wiąże się z pracochłonnością lub strukturą pracy | koszt pracy względem efektu |
| PORT-01 | zmiana portfolio mix wpływa na obciążenie constraint | rentowność i struktura portfela |
| FIN-03 | constraint wpływa na koszt jednostkowy | koszt jednostkowy |
| FIN-01 | problem procesowy może być istotny dla ekonomiki organizacji | relacja kosztów i przychodów |

### 13.3. Relacja z PORT-01

Jeżeli PROC-02 potwierdza rzeczywiste ograniczenie capacity w odpowiednim scope, przekazuje do PORT-01 capacity_constraint_status = verified_constraint. Verified constraint typu gate_rule, handoff albo system bez potwierdzenia ograniczenia capacity nie może automatycznie ustawić capacity_constraint_status=verified_constraint. Dzięki temu PORT-01 może odpowiedzialnie interpretować CM1 lub SM na jednostkę rzeczywiście ograniczonej capacity. PROC-02 nie podejmuje decyzji portfelowej.

## 14. Dane dla ZOP-PRI-01 i ZOP-CONF-01

### 14.1. Payload dla ZOP-PRI-01

| Cel | Pola |
| --- | --- |
| Priorytetyzacja – bez lokalnego wzoru | constraint_entity_type; constraint_entity_id; constraint_entity_scope; constraint_status; queue_delta; queue_time_gap_signed; adverse_queue_time_gap; throughput_gap; system_throughput_change; stage_throughput_change; backlog_scope; affected_cases; affected_units; affected_portfolio_items; constraint_migration; persistence; trend_direction; capacity_pressure_ratio; result_risk; urgent_validation |

### 14.2. Payload dla ZOP-CONF-01

| Cel | Pola |
| --- | --- |
| Pewność – bez lokalnego score | process_data_completeness; ready_at_quality; route_comparability; stage_definition_quality; timestamp_quality; flow_reconciliation_quality; capacity_mapping_quality; work_content_quality; reference_quality; censoring_share; rework_identification_quality; parallel_route_quality; constraint_verification_basis; mechanism_evidence; manual_validation; exclusion_flags |

PROC-02 nie projektuje finalnego Priority Score ani Confidence Score. Pola STANDARD/MEDIUM/HIGH/CRITICAL oraz confidence_score/confidence_class pozostają odpowiedzialnością mechanizmów wspólnych.

## 15. Struktura FINDINGS

### 15.1. Pola bazowe X-Ray

| Pole bazowe | Reguła PROC-02 |
| --- | --- |
| test_id | PROC-02 |
| scope | organization/process_type/route_variant/unit/stage/resource_group + filtry |
| period | current + reference + time_bucket |
| status | status logiczny wykonania/diagnostyki |
| finding | komunikat faktograficzny bez automatycznej tezy o przyczynie |
| metric_value | jawnie wskazana główna miara, np. queue_delta lub system_throughput_rate |
| reference_value | odpowiednia wartość odniesienia albo null |
| gap | jawnie nazwany gap, np. queue_time_gap_signed lub throughput_gap |
| impact_low / impact_high | null, chyba że odpowiedzialny przedział pochodzi z mechanizmu ekonomicznego poza PROC-02 |
| confidence_score / confidence_class | wynik ZOP-CONF-01 albo null |
| next_tests | tablica test_id + uzasadnienie |
| validation_required | boolean + validation_notes |

### 15.2. Rozszerzenia PROC-02

| Grupa pól | Pola techniczne |
| --- | --- |
| Identyfikacja | process_type; route_variant; unit; stage; resource_group; portfolio_item; time_bucket; constraint_entity_type; constraint_entity_id; constraint_entity_scope |
| Zdarzenia | stage_arrivals; stage_starts; stage_completions; unique_cases_started; unique_cases_completed |
| Throughput | stage_operating_time; stage_operating_time_unit; operating_time_basis; system_observation_time; system_observation_time_unit; system_observation_time_basis; stage_throughput_rate; system_throughput_rate; stage_throughput_change; system_throughput_change; throughput_gap |
| Kolejka | queue_start; queue_end; queue_delta; queue_peak; queue_average; queue_share |
| Czas | queue_time_median; queue_time_p75; queue_time_p90; stage_elapsed_median; stage_elapsed_p90; transition_delay_median; queue_time_gap_signed; adverse_queue_time_gap; predecessor_relation; predecessor_stage |
| WIP | active_wip; queue_wip; stage_wip; system_wip |
| Capacity | effective_available; capacity_unit; required_capacity; capacity_pressure_ratio; capacity_mapping_quality |
| Evidence | constraint_status; constraint_verification_basis; queue_evidence; capacity_evidence; flow_evidence; starvation_evidence; response_evidence; mechanism_evidence |
| Mechanizmy | constraint_migration; constraint_entity_by_bucket; constraint_stage_by_bucket; delay_hotspot; batching_signal; starvation_signal; blocked_time |
| Powroty / miks | repeat_visit_count; repeat_visit_rate; rework_load; work_content; work_content_unit; work_content_comparability |
| Kontrola | flow_reconciliation_gap; left_censored_case; right_censored_case; complete_case; exclusion_flags; validation_notes |

## 16. Statusy logiczne i komunikat zarządczy

### 16.1. Statusy logiczne X-Ray

PROC-02 zachowuje wspólny katalog: NO_ADVERSE_SIGNAL; ADVERSE_SIGNAL; INCIDENT; DETERIORATING; STABLE; IMPROVING; TEST_PARTIAL; TEST_BLOCKED. constraint_status jest oddzielnym polem opisującym stopień potwierdzenia ograniczenia, a nie priorytet problemu.

### 16.2. Wzorzec komunikatu zarządczego

> **[STATUS] OGRANICZENIE PRZEPŁYWU Najsilniejszy sygnał ograniczenia dotyczy [constraint_entity_type: constraint_entity_id] w zakresie [constraint_entity_scope]; jeżeli obiektem jest etap: [stage]. W badanym okresie do właściwego etapu napłynęło [X] przypadków, rozpoczęto [Y], zakończono [Z], a kolejka zmieniła się z [A] do [B]. Mediana czasu oczekiwania wynosi [Q] wobec [Q_ref] w okresie referencyjnym. Status ograniczenia: [constraint_status]. Podstawą są: [evidence]. Wynik nie oznacza automatycznie, że etap lub zasób wymaga zwiększenia zatrudnienia albo capacity. W pierwszej kolejności należy zweryfikować [next_tests / hipotezy].**

| Zakazany skrót | Wymagane zachowanie |
| --- | --- |
| „trzeba zatrudnić więcej osób” | najpierw potwierdź rodzaj constraint i przyczynę |
| „ten dział blokuje organizację” | opisz etap/mechanizm i podstawę evidence bez języka obwiniającego |
| „pracownicy są za wolni” | oddziel elapsed, touch time, work content, miks i routing |
| „należy zwiększyć capacity” | wymaga potwierdzenia capacity constraint i analizy alternatyw |
| „to jest przyczyna całego problemu” | hipoteza pozostaje hipotezą bez właściwego dowodu |

## 17. Scenariusze testowe PROC02-T01–T10

| Id | Scenariusz | Dane | Oczekiwane |
| --- | --- | --- | --- |
| PROC02-T01 | Proces stabilny | kolejki i throughput stabilne; brak presji capacity | constraint_status=not_detected; NO_ADVERSE_SIGNAL |
| PROC02-T02 | Bardzo długi etap bez ograniczenia przepływu | stage_elapsed wysoki; brak kolejki; duża równoległość; throughput stabilny | delay_hotspot=true; brak bottleneck; next_test=PROC-01 |
| PROC02-T03 | Narastająca kolejka i niewystarczająca capacity | arrivals > możliwości obsługi; queue rośnie; capacity evidence | candidate lub verified zgodnie z flow_evidence; CAP-02 |
| PROC02-T04 | Wysoki utilization bez kolejki | U wysokie; queue≈0; throughput stabilny | brak automatycznego bottleneck |
| PROC02-T05 | Kolejka i niski utilization | queue wysoka; capacity niewykorzystana | hipoteza grafiku/organizacji/gating; bez tezy o braku capacity |
| PROC02-T06 | Starvation downstream | downstream ma wolną capacity i mało arrivals; upstream ogranicza | starvation_evidence=true; kandydat upstream |
| PROC02-T07 | Blocking potwierdzony | wiarygodny blocked_time; upstream nie może zwolnić zasobu przez downstream | blocking signal; analiza downstream |
| PROC02-T08 | Handoff delay bez blocking | długi czas między etapami; brak dowodu zajęcia upstream | transition/handoff delay; nie nazywać blocking |
| PROC02-T09 | Batching | kolejka rośnie cyklicznie i znika po partii | batching_signal=true; analiza pełnego cyklu; bez auto verified |
| PROC02-T10 | Wędrujące wąskie gardło | A ogranicza, potem B, potem C | constraint_migration=true; brak jednego stałego bottleneck |

PASS scenariusza wymaga zgodności walidacji, miar, jawnej podstawy czasu, constraint_entity, constraint_status, evidence vector, statusu logicznego, FINDINGS, validation_required, next_tests i zakazów interpretacyjnych. Sama poprawna wartość queue_delta lub throughput nie wystarcza.

## 18. Scenariusze testowe PROC02-T11–T23

| Id | Scenariusz | Dane | Oczekiwane |
| --- | --- | --- | --- |
| PROC02-T11 | Rework zwiększa obciążenie | unique case stabilne; liczba przejść przez stage rośnie | repeat_visit/rework load; nie używać wyłącznie unique volume |
| PROC02-T12 | Brak ready_at | tylko start/end | elapsed i throughput możliwe; queue tylko przy wiarygodnym proxy; inaczej TEST_PARTIAL |
| PROC02-T13 | Proces równoległy | etapy zachodzą na siebie zgodnie z dokumentacją | brak fałszywego błędu kolejności |
| PROC02-T14 | Cenzorowanie | część spraw zaczęła przed oknem lub kończy po nim | left/right censoring; bez fałszywej mediany pełnego lead time |
| PROC02-T15 | Chwilowy skok popytu | queue rośnie jednorazowo i normalizuje się | INCIDENT; bez trwałego verified constraint |
| PROC02-T16 | Zwiększenie capacity uwalnia przepływ | capacity stage rośnie; queue spada; system throughput rośnie; warunki porównywalne | response_evidence=true; możliwy verified przy flow_evidence |
| PROC02-T17 | Zwiększenie capacity nie poprawia systemu | capacity A rośnie; system throughput bez zmiany; queue przechodzi do B | A nie jest już głównym constraint albo migracja do B |
| PROC02-T18 | Zmiana miksu przypadków | liczba case spada; work_content rośnie | brak tezy o spadku popytu; PORT-01 / HR-01 |
| PROC02-T19 | Duża kolejka, źródłem gating | stage ma capacity; uruchomienie tylko w oknie / po decyzji | organizacyjne/process constraint; nie capacity shortage |
| PROC02-T20 | Nieuzgodniony przepływ | cases między etapami nie uzgadniają się; brak wyjaśnienia wyjść | validation_required; TEST_PARTIAL/BLOCKED zależnie od skali |
| PROC02-T21 | Ograniczenie regułą / gate | capacity etapu wystarczająca; przejście dalej tylko po udokumentowanej regule lub w określonym oknie; kolejka przed bramką; downstream okresowo niedostatecznie zasilany | constraint_entity_type=gate_rule; mechanism_evidence=true; bez fałszywego capacity_evidence; verified_constraint możliwy przy flow_evidence=true; bez automatycznego capacity_constraint_status=verified_constraint w PORT-01 |
| PROC02-T22 | Równoległe poprzedniki | A i B biegną równolegle; C może rozpocząć się dopiero po zakończeniu obu | brak arbitralnego previous_stage; predecessor_completion_at zgodnie z kontraktem, np. max(end_required_predecessors), albo transition_delay=null przy niewystarczającej podstawie |
| PROC02-T23 | Różne podstawy czasu | dwa etapy mają różne kalendarze operacyjne | własne stage_operating_time i operating_time_basis; brak porównania throughput bez kontroli podstawy czasu |

## 19. Kryteria odbioru implementacji PROC02-ACC-01–48

| Id | Zakres / kontrola | Id | Zakres / kontrola |
| --- | --- | --- | --- |
| PROC02-ACC-01 | przyjmuje PROCESS zgodny z bazowym modelem – PASS | PROC02-ACC-02 | rozpoznaje case_id – PASS |
| PROC02-ACC-03 | rozpoznaje stage – PASS | PROC02-ACC-04 | waliduje start/end – PASS |
| PROC02-ACC-05 | obsługuje przypadki otwarte – PASS | PROC02-ACC-06 | obsługuje left/right censoring – PASS |
| PROC02-ACC-07 | obsługuje ready_at – PASS | PROC02-ACC-08 | nie tworzy queue_time bez podstawy – PASS |
| PROC02-ACC-09 | liczy stage_elapsed_time – PASS | PROC02-ACC-10 | nie utożsamia stage_elapsed z touch_time – PASS |
| PROC02-ACC-11 | liczy transition_delay, jeżeli możliwe – PASS | PROC02-ACC-12 | obsługuje route_variant – PASS |
| PROC02-ACC-13 | obsługuje równoległość – PASS | PROC02-ACC-14 | rozróżnia rework/repeat od duplikatu – PASS |
| PROC02-ACC-15 | liczy arrivals – PASS | PROC02-ACC-16 | liczy starts – PASS |
| PROC02-ACC-17 | liczy completions – PASS | PROC02-ACC-18 | liczy stage throughput – PASS |
| PROC02-ACC-19 | liczy system throughput – PASS | PROC02-ACC-20 | liczy queue/WIP, jeżeli dane pozwalają – PASS |
| PROC02-ACC-21 | liczy queue_delta – PASS | PROC02-ACC-22 | wykorzystuje medianę i percentile – PASS |
| PROC02-ACC-23 | nie uznaje long stage automatycznie za bottleneck – PASS | PROC02-ACC-24 | nie uznaje high utilization automatycznie za bottleneck – PASS |
| PROC02-ACC-25 | nie uznaje large queue automatycznie za bottleneck – PASS | PROC02-ACC-26 | obsługuje evidence vector bez lokalnego score – PASS |
| PROC02-ACC-27 | wyznacza constraint_status – PASS | PROC02-ACC-28 | verified_constraint wymaga flow_evidence oraz capacity_evidence, response_evidence lub mechanism_evidence i braku krytycznej sprzeczności – PASS |
| PROC02-ACC-29 | obsługuje starvation – PASS | PROC02-ACC-30 | obsługuje blocking wyłącznie z właściwą podstawą – PASS |
| PROC02-ACC-31 | obsługuje batching – PASS | PROC02-ACC-32 | obsługuje constraint_migration – PASS |
| PROC02-ACC-33 | obsługuje rework load – PASS | PROC02-ACC-34 | nie miesza case count z work_content – PASS |
| PROC02-ACC-35 | mapuje capacity tylko przy zgodnych jednostkach – PASS | PROC02-ACC-36 | liczy capacity_pressure_ratio warunkowo – PASS |
| PROC02-ACC-37 | kontroluje flow reconciliation – PASS | PROC02-ACC-38 | zapisuje FINDINGS – PASS |
| PROC02-ACC-39 | wskazuje next_tests – PASS | PROC02-ACC-40 | przekazuje do PORT-01 verified capacity constraint tylko przy rzeczywistym ograniczeniu capacity – PASS |
| PROC02-ACC-41 | nie wycenia automatycznie bottleneck w pieniądzu – PASS | PROC02-ACC-42 | nie rekomenduje automatycznie zwiększenia zatrudnienia/capacity – PASS |
| PROC02-ACC-43 | przechodzi PROC02-T01–T23 – PASS |  |  |
| PROC02-ACC-44 | obsługuje stage_operating_time, stage_operating_time_unit i operating_time_basis; stage_operating_time=0 → stage_throughput_rate=null – PASS | PROC02-ACC-45 | obsługuje system_observation_time, system_observation_time_unit i system_observation_time_basis – PASS |
| PROC02-ACC-46 | wiąże constraint_status z constraint_entity_type/id/scope; nie tworzy sztucznego stage dla reguły – PASS | PROC02-ACC-47 | obsługuje mechanism_evidence i nową bramkę verified_constraint; brak danych = null/not_assessable – PASS |
| PROC02-ACC-48 | obsługuje predecessor_relation / predecessor_stage, wielu poprzedników i transition_delay=null przy niejednoznaczności – PASS |  |  |

> **WARUNEK ODBIORU PROC02-ACC-01–PROC02-ACC-48 = PASS. Implementacja ma odtwarzać reguły dokumentu bez dodatkowej interpretacji metodologicznej.**

## 20. Definition of Done PROC02-DOD-01–53

| Id | Zakres / kontrola | Id | Zakres / kontrola |
| --- | --- | --- | --- |
| PROC02-DOD-01 | cel – PASS | PROC02-DOD-02 | granica względem PROC-01 – PASS |
| PROC02-DOD-03 | case_id – PASS | PROC02-DOD-04 | stage – PASS |
| PROC02-DOD-05 | route_variant – PASS | PROC02-DOD-06 | ready_at – PASS |
| PROC02-DOD-07 | queue_time – PASS | PROC02-DOD-08 | stage_elapsed_time – PASS |
| PROC02-DOD-09 | touch_time – PASS | PROC02-DOD-10 | transition_delay – PASS |
| PROC02-DOD-11 | routing i równoległość – PASS | PROC02-DOD-12 | rework – PASS |
| PROC02-DOD-13 | walidacja – PASS | PROC02-DOD-14 | cenzorowanie – PASS |
| PROC02-DOD-15 | arrivals – PASS | PROC02-DOD-16 | starts – PASS |
| PROC02-DOD-17 | completions – PASS | PROC02-DOD-18 | throughput stage – PASS |
| PROC02-DOD-19 | throughput system – PASS | PROC02-DOD-20 | queue – PASS |
| PROC02-DOD-21 | WIP – PASS | PROC02-DOD-22 | horyzonty – PASS |
| PROC02-DOD-23 | wartość odniesienia – PASS | PROC02-DOD-24 | median/P90 – PASS |
| PROC02-DOD-25 | long stage ≠ bottleneck – PASS | PROC02-DOD-26 | large queue ≠ bottleneck – PASS |
| PROC02-DOD-27 | high utilization ≠ bottleneck – PASS | PROC02-DOD-28 | evidence vector – PASS |
| PROC02-DOD-29 | constraint_status – PASS | PROC02-DOD-30 | constraint_verification_basis – PASS |
| PROC02-DOD-31 | starvation – PASS | PROC02-DOD-32 | blocking/handoff – PASS |
| PROC02-DOD-33 | batching – PASS | PROC02-DOD-34 | constraint migration – PASS |
| PROC02-DOD-35 | work_content – PASS | PROC02-DOD-36 | capacity mapping – PASS |
| PROC02-DOD-37 | capacity pressure – PASS | PROC02-DOD-38 | flow conservation – PASS |
| PROC02-DOD-39 | delay hotspot – PASS | PROC02-DOD-40 | hipotezy – PASS |
| PROC02-DOD-41 | next_tests – PASS | PROC02-DOD-42 | relacja z PORT-01 bez fałszywego capacity constraint – PASS |
| PROC02-DOD-43 | dane ZOP-PRI-01 – PASS | PROC02-DOD-44 | dane ZOP-CONF-01 – PASS |
| PROC02-DOD-45 | FINDINGS – PASS | PROC02-DOD-46 | komunikat zarządczy – PASS |
| PROC02-DOD-47 | scenariusze PROC02-T01–T23 – PASS | PROC02-DOD-48 | kryteria implementacyjne – PASS |
| PROC02-DOD-49 | stage_operating_time / unit / basis – PASS | PROC02-DOD-50 | system_observation_time / unit / basis – PASS |
| PROC02-DOD-51 | constraint_entity_type/id/scope i entity-aware constraint_status – PASS | PROC02-DOD-52 | mechanism_evidence i rozszerzona bramka verified_constraint – PASS |
| PROC02-DOD-53 | predecessor_relation / wielu poprzedników / transition_delay – PASS |  |  |

> **WYMAGANE PROC02-DOD-01–PROC02-DOD-53 = PASS.**

## 21. Test końcowy QPROC02

| Id | Kontrola | Id | Kontrola |
| --- | --- | --- | --- |
| QPROC02-01 | uniwersalność branżowa – PASS | QPROC02-02 | wąskie gardło = ograniczenie przepływu systemu – PASS |
| QPROC02-03 | najdłuższy etap ≠ automatycznie bottleneck – PASS | QPROC02-04 | największa kolejka ≠ automatycznie bottleneck – PASS |
| QPROC02-05 | najwyższy utilization ≠ automatycznie bottleneck – PASS | QPROC02-06 | PROC-02 nie zastępuje PROC-01 – PASS |
| QPROC02-07 | queue_time wymaga ready_at lub wiarygodnego proxy – PASS | QPROC02-08 | stage_elapsed ≠ touch_time – PASS |
| QPROC02-09 | transition_delay ≠ queue_time – PASS | QPROC02-10 | routing jest kontrolowany – PASS |
| QPROC02-11 | procesy równoległe są obsługiwane – PASS | QPROC02-12 | powtórzenie etapu ≠ automatycznie duplikat – PASS |
| QPROC02-13 | przypadki cenzorowane są obsługiwane – PASS | QPROC02-14 | arrivals / starts / completions są rozdzielone – PASS |
| QPROC02-15 | queue_wip ≠ active_wip – PASS | QPROC02-16 | stage throughput ≠ system throughput – PASS |
| QPROC02-17 | 0 arbitralnych progów bottleneck – PASS | QPROC02-18 | 0 arbitralnych benchmarków kolejki – PASS |
| QPROC02-19 | evidence vector istnieje i obejmuje mechanism_evidence – PASS | QPROC02-20 | candidate_constraint ≠ verified_constraint – PASS |
| QPROC02-21 | verified wymaga flow evidence i capacity, response lub mechanism evidence – PASS | QPROC02-22 | constraint_verification_basis jest jawna – PASS |
| QPROC02-23 | starvation odróżniony od bottleneck danego etapu – PASS | QPROC02-24 | blocking wymaga właściwych danych – PASS |
| QPROC02-25 | handoff delay nie jest blocking bez podstawy – PASS | QPROC02-26 | batching jest obsługiwany – PASS |
| QPROC02-27 | constraint_migration jest obsługiwany – PASS | QPROC02-28 | rework zwiększa load niezależnie od unique case count – PASS |
| QPROC02-29 | work_content oddzielone od case count – PASS | QPROC02-30 | stage_elapsed nie jest work_content bez podstawy – PASS |
| QPROC02-31 | capacity_unit są zgodne – PASS | QPROC02-32 | capacity_pressure_ratio jest warunkowy – PASS |
| QPROC02-33 | flow reconciliation jest wykonywany – PASS | QPROC02-34 | Little’s Law wyłącznie jako kontrola pomocnicza – PASS |
| QPROC02-35 | delay_hotspot odróżniony od bottleneck – PASS | QPROC02-36 | throughput_gap nie jest automatycznie wyceniany – PASS |
| QPROC02-37 | 0 automatycznej rekomendacji zatrudnienia – PASS | QPROC02-38 | 0 automatycznej rekomendacji zwiększenia capacity – PASS |
| QPROC02-39 | hipoteza ≠ przyczyna – PASS | QPROC02-40 | next_tests istnieją – PASS |
| QPROC02-41 | verified capacity constraint może zasilić PORT-01; gate_rule/handoff bez capacity evidence nie tworzy capacity constraint – PASS | QPROC02-42 | FIN-01 pozostaje niezmieniony – PASS |
| QPROC02-43 | CAP-01 pozostaje niezmieniony – PASS | QPROC02-44 | HR-01 pozostaje niezmieniony – PASS |
| QPROC02-45 | PORT-01 pozostaje niezmieniony – PASS | QPROC02-46 | ZOP-PRI-01 pozostaje nieopracowany – PASS |
| QPROC02-47 | ZOP-CONF-01 pozostaje nieopracowany – PASS | QPROC02-48 | FINDINGS zgodne z architekturą X-Ray – PASS |
| QPROC02-49 | 23 scenariusze PROC02-T01–T23 – PASS | QPROC02-50 | PROC02-ACC-01–48 kompletne – PASS |
| QPROC02-51 | PROC02-DOD-01–53 = PASS – PASS | QPROC02-52 | gotowe dla Aleksandra – PASS |
| QPROC02-53 | 0 danych SPZOZ – PASS | QPROC02-54 | 0 danych pacjentów – PASS |
| QPROC02-55 | PROC-01 nie został opracowany – PASS | QPROC02-56 | PROC-03 nie został rozpoczęty – PASS |
| QPROC02-57 | brak automatycznego przeliczania kolejki na pieniądze – PASS | QPROC02-58 | brak automatycznej tezy o braku capacity przy niskim utilization – PASS |
| QPROC02-59 | brak sztucznego ready_at – PASS | QPROC02-60 | statusy STANDARD/MEDIUM/HIGH/CRITICAL pozostają poza PROC-02 – PASS |
| QPROC02-61 | stage_operating_time, stage_operating_time_unit i operating_time_basis są jawne – PASS | QPROC02-62 | stage_operating_time=0 → stage_throughput_rate=null/not_computable – PASS |
| QPROC02-63 | system_observation_time, jednostka i podstawa są jawne – PASS | QPROC02-64 | throughput o różnych podstawach czasu nie jest mieszany bez oznaczenia – PASS |
| QPROC02-65 | constraint_entity_type/id/scope identyfikują obiekt ograniczenia – PASS | QPROC02-66 | constraint_status odnosi się do entity; stage pozostaje podstawową jednostką bez sztucznych stage – PASS |
| QPROC02-67 | constraint_entity_by_bucket działa, a constraint_stage_by_bucket pozostaje kompatybilne – PASS | QPROC02-68 | mechanism_evidence wymaga dokumentu/mechanizmu i zgodnego flow; brak danych=null – PASS |
| QPROC02-69 | predecessor_relation obsługuje wielu poprzedników bez arbitralnego previous_stage – PASS | QPROC02-70 | PROC02-T21–T23 są obecne i kompletne – PASS |

> **WYNIK QPROC02 QPROC02-01–QPROC02-70 = PASS.**

## 22. Status końcowy i przekazanie do implementacji

> **PROC-02 ZAMKNIĘTY METODOLOGICZNIE DO IMPLEMENTACJI**

| Element | Status / wynik |
| --- | --- |
| ZOP-XR-PROC-02 | v1.0 – zamknięty metodologicznie do implementacji |
| ZOP-PRI-01 | DO OPRACOWANIA |
| ZOP-CONF-01 | DO OPRACOWANIA |
| PROC02-DOD | 53/53 PASS |
| QPROC02 | 70/70 PASS |
| Scenariusze | 23 – PROC02-T01–T23 |
| Kryteria implementacyjne | 48 – PROC02-ACC-01–48 PASS |
| next_tests | PROC-01; CAP-01; CAP-02; HR-01; PORT-01; FIN-03; FIN-01 |

### 22.1. Otwarte kwestie wspólne – poza PROC-02

| Kwestia | Status / wpływ |
| --- | --- |
| globalny mechanizm priorytetu | ZOP-PRI-01 do opracowania; PROC-02 dostarcza payload |
| globalny mechanizm pewności | ZOP-CONF-01 do opracowania; PROC-02 dostarcza sygnały jakości |
| wspólny standard kalendarzy operacyjnych / podstaw czasu | do ujednolicenia między branżami i źródłami danych; PROC-02 wymaga jawnych podstaw, ale nie projektuje jednego globalnego kalendarza |
| wspólny kontrakt work_content i przeliczeń capacity | do ujednolicenia z CAP-02/HR-01 bez arbitralnych wag |
| reguły orkiestracji next_tests | poza PROC-02; test jedynie rekomenduje |

### 22.2. Potwierdzenia granic

| Kontrola | Wynik |
| --- | --- |
| najdłuższy etap ≠ automatycznie bottleneck | PASS |
| największa kolejka ≠ automatycznie bottleneck | PASS |
| najwyższy utilization ≠ automatycznie bottleneck | PASS |
| candidate_constraint ≠ verified_constraint | PASS |
| arbitralne progi bottleneck | 0 |
| automatyczna wycena bottleneck w pieniądzu | 0 |
| automatyczne rekomendacje zatrudnienia | 0 |
| automatyczne rekomendacje zwiększenia capacity | 0 |
| nowe progi Priority Score | 0 |
| nowe progi Confidence Score | 0 |
| dane SPZOZ | 0 |
| dane pacjentów | 0 |
| rozpoczęty PROC-01 | 0 |
| rozpoczęty PROC-03 | 0 |

> **DEFINITION OF DONE Dokument zawiera cel, granice, kontrakt danych, 24 walidacje, model czasu i przepływu, jawne stage_operating_time i system_observation_time, entity-aware constraint_status, evidence vector z mechanism_evidence, bramkę verified_constraint, obsługę wielu poprzedników, capacity/work content, FINDINGS, komunikat zarządczy, 23 scenariusze, 48 kryteriów implementacyjnych i 70 kontroli końcowych. PROC-02 może zostać przekazany Aleksandrowi bez dodatkowej interpretacji metodologicznej.**

0 arbitralnych progów bottleneck; 0 automatycznych decyzji kadrowych; 0 automatycznej wyceny w pieniądzu; 0 nowych progów Priority Score; 0 nowych progów Confidence Score; 0 danych SPZOZ; 0 danych pacjentów; 0 rozpoczętego PROC-01; 0 rozpoczętego PROC-03.
