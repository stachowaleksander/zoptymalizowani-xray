ZOPTYMALIZOWANI – X-RAY

# CAP-01

# Wykorzystanie zasobu

Karta metodologiczna i specyfikacja implementacyjna

> **STATUS CAP-01 ZAMKNIĘTY METODOLOGICZNIE DO IMPLEMENTACJI**

| Pole | Wartość |
| --- | --- |
| Identyfikator | ZOP-XR-CAP-01 |
| Wersja / data | v1.0 / 1 września 2026 |
| Rola | drugi pełny test diagnostyczny; wzorzec rodziny testów zasobowych |
| Odbiorcy | zarządzający, analityk, Aleksander – implementacja |
| Zależności | ZOP-PRI-01 i ZOP-CONF-01 – DO OPRACOWANIA |

Dokument rozdziela walidację, obliczenia, interpretację i wsparcie decyzji. Nie jest projektem aplikacji, panelu użytkownika, warstwy AI ani metodologią CAP-02.

## 1. Rola, cel i granice CAP-01

CAP-01 ocenia wykorzystanie mierzalnej zdolności w relacji do jej rzeczywistej dostępności, kosztu, trwałości zjawiska i sygnału popytowego. Test lokalizuje niewykorzystaną zdolność, ale nie rozstrzyga automatycznie o jej przyczynie ani o możliwości redukcji zasobu.

> **PYTANIE DIAGNOSTYCZNE Czy organizacja wykorzystuje dostępne zasoby adekwatnie do ich dostępności, kosztu i rzeczywistej działalności, a jeżeli nie – gdzie występuje niewykorzystana zdolność, od kiedy trwa, jaka jest jej skala oraz jaki może być jej wpływ ekonomiczny?**

### 1.1. Łańcuch diagnostyczny

| Etap | Produkt | Granica |
| --- | --- | --- |
| Dane | RESOURCE + ACTIVITY + opcjonalny PLAN | bez obliczeń przed walidacją |
| Zdolność | available, used, capacity_unit | dostępna ≠ nominalna teoretyczna |
| Odchylenie | U, UC, UCR, UG | 100% nie jest automatycznym optimum |
| Trend | trwałość i horyzonty | 1M nie dowodzi problemu |
| Lokalizacja | unit → resource → grupa | tylko zasoby porównywalne |
| Ekonomika | koszt przypisany do luki | koszt ≠ oszczędność |
| Interpretacja | popyt i hipotezy | korelacja ≠ przyczyna |
| Kolejny krok | next_tests z uzasadnieniem | bez projektowania testów następczych |

### 1.2. Granice testu

CAP-01 wykrywa niewykorzystanie, pogorszenie wykorzystania, nierównomierność podobnych zasobów, lokalizację luki, związek z wolumenem oraz koszt przypisany arytmetycznie do niewykorzystanej części zdolności. Przekroczenie właściwego poziomu lub used > available jest wyłącznie sygnałem do walidacji i CAP-02. CAP-01 nie jest pełnym testem przeciążenia.

> **ZASADA NADRZĘDNA Ocena = wartość odniesienia + trwałość + popyt + koszt + porównywalność zasobu. Odległość od 100% nie stanowi samodzielnego kryterium.**

## 2. Definicje i jednostka zdolności

| Pojęcie / pole | Definicja implementacyjna |
| --- | --- |
| resource | Mierzalne źródło zdolności: osoba lub grupa, maszyna, linia, pojazd, pomieszczenie, stanowisko, urządzenie albo inny zasób. |
| available_source | Wartość available otrzymana lub zmapowana ze źródła; pozostaje nienaruszona i nie jest po cichu zastępowana wartością skorygowaną. |
| effective_available | Zdolność wykorzystywana do obliczeń po jawnych, udokumentowanych korektach; nie musi być równa zdolności nominalnej. |
| used | Część effective_available rzeczywiście wykorzystana do działalności w tym samym okresie, zakresie i jednostce. |
| capacity_unit | Jednoznaczna jednostka: godziny, roboczogodziny, maszynogodziny, miejsca, sloty, kilometry, cykle lub inna mierzalna jednostka. |
| UC | effective_available − used, wyłącznie gdy dane są porównywalne i used ≤ effective_available. |
| U | used / effective_available; przy effective_available = 0 wynik null / not_computable. |

UC nie jest automatycznie stratą, marnotrawstwem, nadmiarem zatrudnienia ani potencjałem redukcji. Zasobów o różnych capacity_unit nie sumuje się i nie obejmuje wspólnym wskaźnikiem U.

## 3. Dane wejściowe i kontrakt danych

| Tabela | Pola bazowe | Rola |
| --- | --- | --- |
| RESOURCE | date, unit, resource, available, used, cost | zdolność, wykorzystanie, koszt |
| ACTIVITY | date, unit, product, volume, revenue | wolumen i opcjonalny sygnał przychodowy |
| PLAN – opcjonalna | date, unit, metric, target | plan jako możliwa referencja |

### 3.1. Rozszerzenia opcjonalne

resource_type; capacity_unit; planned_unavailability; capacity_basis; documented_extra_capacity; resource_group; available_source; effective_available; resource_cost_total; capacity_committed_cost; usage_variable_cost; activity_unit; weighted_volume; volume_comparability; peer_comparability. Rozszerzenia nie zmieniają bazowej struktury ZOP-TECH-01 i są używane wyłącznie wtedy, gdy zostały dostarczone lub wiarygodnie zmapowane.

| Zakres | Wymaganie | Skutek |
| --- | --- | --- |
| Minimum | 12 miesięcy, miesiąc jako granularność podstawowa | test podstawowy z oceną ograniczeń |
| Preferowane | 24–36 miesięcy | trwałość, sezonowość, punkt zwrotny |
| Dane krótsze | wyłącznie moduły z podstawą | TEST_PARTIAL albo TEST_BLOCKED |
| Dane dzienne/tygodniowe | analiza dodatkowa | bez zmiany podstawowej architektury |
| Klucze | date + unit + resource + capacity_unit | ochrona przed duplikacją i mieszaniem jednostek |

## 4. Walidacja danych

Każda kontrola zwraca PASS, WARNING albo CRITICAL. CRITICAL zatrzymuje tylko moduły zależne, jeżeli pozostała część testu może zostać odpowiedzialnie wykonana. Wyniki trafiają do validation_notes i danych dla ZOP-CONF-01.

| Id | Kontrola | Reakcja |
| --- | --- | --- |
| CAP01-VAL-01 | istnieje available | CRITICAL dla U, UC i luk |
| CAP01-VAL-02 | istnieje used | CRITICAL dla miar wykorzystania |
| CAP01-VAL-03 | jednoznaczna capacity_unit | CRITICAL dla agregacji; WARNING lokalnie |
| CAP01-VAL-04 | available ≥ 0 | CRITICAL dla rekordu/zakresu |
| CAP01-VAL-05 | used ≥ 0 | CRITICAL dla rekordu/zakresu |
| CAP01-VAL-06 | porównywalne okresy | CRITICAL dla porównania; WARNING dla trendu |
| CAP01-VAL-07 | spójne unit i resource | CRITICAL przy nieusuwalnej wieloznaczności |
| CAP01-VAL-08 | brak duplikatów | CRITICAL, gdy grozi podwójnym liczeniem |
| CAP01-VAL-09 | brak brakujących okresów | WARNING lub CRITICAL zależnie od modułu |
| CAP01-VAL-10 | cost i podstawa kosztowa dostępne dla ekonomiki | WARNING; ekonomika null albo wskaźnik brutto |
| CAP01-VAL-11 | available i used w tej samej jednostce | CRITICAL dla rekordu/zakresu |
| CAP01-VAL-12 | brak agregacji różnych jednostek | CRITICAL dla agregatu |
| CAP01-VAL-13 | obsłużono used > effective_available | WARNING/CRITICAL + validation_required |
| CAP01-VAL-14 | wystarczająca i porównywalna referencja | WARNING; UG i luki referencyjne = null |
| CAP01-VAL-15 | ACTIVITY i jednostka volume porównywalne z RESOURCE | WARNING/CRITICAL dla interpretacji popytu |

### 4.1. Reguły wykonania

| Sytuacja | Zachowanie |
| --- | --- |
| CRITICAL globalny | TEST_BLOCKED dla zależnych modułów; brak zastępczych wartości |
| CRITICAL lokalny | wyłączenie zakresu i kontynuacja pozostałych, jeżeli odpowiedzialna |
| WARNING | kontynuacja, validation_notes, sygnał do ZOP-CONF-01 |
| effective_available = 0 | U, UCR i kosztowe proporcje = null / not_computable |
| brak cost | miary fizyczne działają; economic_gap = null |

## 5. Szczególny przypadek: used > available

Przekroczenie nie jest automatycznie błędem logicznym. Najpierw sprawdza się documented_extra_capacity, nadgodziny, dodatkową zmianę, pracę ponad plan, czasowo uruchomiony zasób lub inną udokumentowaną przyczynę.

| Stan | Działanie | Wynik |
| --- | --- | --- |
| dodatkowa zdolność udokumentowana | zachować available_source; zapisać documented_extra_capacity | effective_available = available_source + documented_extra_capacity |
| przyczyna nieudokumentowana | nie korygować po cichu | validation_required=true; CAP-02 |
| przekroczenie lokalne | zachować rekord i wyłączyć zależną lukę UC | pozostałe zakresy mogą być TEST_PARTIAL |

| Ślad korekty | Wymaganie |
| --- | --- |
| source / reason | źródło i powód korekty |
| period / scope | okres i zakres zasobu objęty korektą |
| adjustment_value | wartość documented_extra_capacity |
| capacity_basis | jawna podstawa przejścia od wartości źródłowej do effective_available |

Jeżeli available_source jest zdolnością netto po ograniczeniach planowych, planned_unavailability nie jest odejmowane ponownie. Jeżeli źródło przedstawia zdolność brutto, przejście do effective_available musi być jawnie opisane w capacity_basis, łącznie z ograniczeniami planowymi i każdą udokumentowaną korektą.

> **Nie ukrywać przekroczenia. CAP-01 rejestruje sygnał, lecz nie projektuje metodologii CAP-02.**

## 6. Metodyka obliczeń

| Miara | Wzór | Warunek i znaczenie |
| --- | --- | --- |
| Wykorzystanie | U = used / effective_available | effective_available = 0 → null |
| Niewykorzystana zdolność | UC = effective_available − used | tylko przy zgodnych jednostkach i used ≤ effective_available |
| Udział niewykorzystanej zdolności | UCR = UC / effective_available = 1 − U | effective_available = 0 → null |
| Luka wykorzystania | UG = U_ref − U_current | dodatnia oznacza wykorzystanie poniżej referencji |
| Oczekiwane wykorzystanie | Expected_used = effective_available_current × U_ref | fizyczny poziom przy referencji |
| Luka zdolności | Capacity_gap_units = Expected_used − used_current | nie jest automatycznie utraconą sprzedażą |

### 6.1. Koszt niewykorzystanej zdolności

| Pole | Znaczenie |
| --- | --- |
| resource_cost_total | całkowity koszt zasobu w badanym okresie |
| capacity_committed_cost | koszt utrzymywania dostępnej zdolności, niezależny lub w znacznym stopniu niezależny od bieżącego wykorzystania |
| usage_variable_cost | koszt zależny od rzeczywistego wykorzystania lub działalności |
| Capacity_cost_base | podstawa miar kosztowych; capacity_committed_cost |

Capacity_cost_base = capacity_committed_cost

Raw_unused_capacity_cost = Capacity_cost_base × UC / effective_available

Reference_capacity_cost_gap = Capacity_cost_base × Capacity_gap_units / effective_available

Do miar kosztowych nie stosuje się automatycznie resource_cost_total, jeżeli zawiera usage_variable_cost. Podstawa musi odpowiadać temu samemu okresowi i zakresowi co zdolność.

Jeżeli capacity_committed_cost nie jest możliwy do wiarygodnego wyodrębnienia, nie wymyśla się jego wartości. Wynik oparty na resource_cost_total może być pokazany wyłącznie jako: WSKAŹNIK ARYTMETYCZNY BRUTTO – WYMAGA WALIDACJI STRUKTURY KOSZTU, z validation_required=true. Nie przedstawia się go jako kosztu możliwego do odzyskania.

> **OBOWIĄZKOWE ZASTRZEŻENIE Kwota nie oznacza automatycznie kosztu możliwego do usunięcia ani potencjalnej oszczędności. Przed decyzją wymaga ustalenia przyczyny niewykorzystania, struktury kosztu oraz zapotrzebowania na zasób.**

## 7. Horyzonty i trend

| Horyzont | Reguła deterministyczna | Rola |
| --- | --- | --- |
| 1M | Σused / Σeffective_available w miesiącu vs porównywalna referencja | sygnał, nie dowód trwałości |
| 3M | sumuj effective_available i used w całym oknie; U na agregatach | krótki trend |
| 6M | jak wyżej vs analogiczne porównywalne 6M | trwałość średnioterminowa |
| 12M / r/r | jak wyżej vs analogiczne porównywalne 12M | sezonowość i trwałość |
| 24–36M | okna zgodne z regułą + pełny przebieg | punkt zwrotny i wzorce |

Nie liczy się prostej średniej miesięcznych procentów, jeżeli effective_available różni się między miesiącami. Analiza przebiegu jest dodatkowa i służy klasyfikacji kierunku, trwałości oraz zmienności.

| Status logiczny | Znaczenie bez arbitralnego progu |
| --- | --- |
| NO_ADVERSE_SIGNAL | brak potwierdzonego pogorszenia względem poprawnej referencji |
| INCIDENT | pojedynczy okres bez potwierdzenia w szerszych oknach |
| SHORT_TERM_DEVIATION | kilka okresów bez podstaw do trwałości |
| DETERIORATING | kolejne obserwacje i horyzonty potwierdzają pogorszenie |
| STABLE | brak trwałego kierunku po uwzględnieniu zmienności |
| IMPROVING | potwierdzona poprawa w więcej niż jednym horyzoncie |
| VOLATILE / SEASONAL | niestabilność lub powtarzalny wzorzec sezonowy |
| TEST_PARTIAL / TEST_BLOCKED | częściowa wykonalność / brak podstaw do zależnych modułów |

## 8. Wartość odniesienia

| Kolejność | Źródło | Warunek |
| --- | --- | --- |
| 1 | historia własnego zasobu | ta sama definicja zdolności i porównywalny zakres |
| 2 | wcześniejszy porównywalny okres | zgodność sezonu, dostępności i portfela |
| 3 | plan | zgodna definicja miary i podstawy available |
| 4 | porównywalne zasoby wewnętrzne | udokumentowana porównywalność |
| 5 | najlepszy własny okres | brak zdarzenia wyjątkowego |
| 6 | benchmark zewnętrzny | wiarygodne, jednoznaczne źródło |

Dla reference_type=internal_peer zgodność capacity_unit jest warunkiem koniecznym, ale niewystarczającym. Trzeba udokumentować także zgodność capacity_basis, resource_group albo porównywalnej funkcji/roli oraz porównywalnego zakresu działalności lub portfela. Gdy warunek nie jest spełniony, preferuje się historię tego samego zasobu albo pozostawia U_ref=null; informacja o ograniczeniu zasila ZOP-CONF-01.

| Pole | Treść |
| --- | --- |
| reference_type | own_history / comparable_period / plan / internal_peer / best_own_period / external_benchmark |
| reference_period / scope | okres, zasoby, unit, capacity_unit |
| reference_value | U_ref użyte w obliczeniu |
| reference_quality | dane dla ZOP-CONF-01, bez lokalnego score |
| reference_notes / source | założenia, korekty, ograniczenia, źródło |

> **Nie ustala się automatycznie 80%, 85%, 90% ani 100% jako właściwego poziomu. Brak referencji pozostawia U_ref, UG, Capacity_gap_units i referencyjną lukę kosztową jako null.**

## 9. Agregacja, porównywalność i dekompozycja

Dla porównywalnej grupy: U_group = Σused / Σeffective_available. Nie stosuje się średniej arytmetycznej indywidualnych U bez ważenia.

| Zasób | used / effective_available | U indywidualne |
| --- | --- | --- |
| A | 10 / 10 | 100% |
| B | 10 / 100 | 10% |
| Grupa – poprawnie | 20 / 110 | 18,18% |

Prosta średnia (100% + 10%) / 2 = 55% jest błędną reprezentacją wykorzystania grupy. Godzin, maszynogodzin, slotów, kilometrów i cykli nie łączy się w jednym U; wyniki prowadzi się równolegle według capacity_unit.

### 9.1. Poziomy dekompozycji

| Poziom | Klucz | Wynik minimalny |
| --- | --- | --- |
| I | unit | available_source, effective_available, used, U, UC, U_ref, UG, luka jednostkowa i kosztowa |
| II | resource | jak wyżej + pozycja w grupie i trwałość |
| III – opcjonalny | resource_type / resource_group | agregat tylko w zgodnej capacity_unit |

### 9.2. Udziały i czynniki kompensujące

| Pole | Reguła |
| --- | --- |
| gross_unused_capacity_share | UC zasobu / ΣUC porównywalnej grupy |
| adverse_capacity_gap_share | dodatnia Capacity_gap_units zasobu / sumę dodatnich luk grupy |
| compensating_resources | zasoby poprawiające wykorzystanie względem referencji; zachowane osobno |

Poprawa jednego nieporównywalnego zasobu nie może maskować pogorszenia innego. Udziały liczy się osobno dla każdej grupy capacity_unit.

## 10. Popyt, flagi i hipotezy

| Sygnał | Interpretacja warunkowa | Możliwy kolejny krok |
| --- | --- | --- |
| U i volume spadają | hipoteza popytu lub portfela | PORT-01; ewentualnie FIN-03 |
| U spada, volume stabilne | hipoteza organizacji, rozmieszczenia albo danych | PROC-01/02 lub HR-01 |
| U niskie, a proces ma kolejkę | hipoteza wąskiego gardła lub niedopasowania | PROC-01/02; CAP-02 |
| revenue zmienia się inaczej niż volume | hipoteza miksu lub ceny | PORT-01; FIN-01/03 |

CAP-01 analizuje Δused, Δavailable, Δvolume, opcjonalnie Δrevenue, U_current i U_reference. Zależność czasowa lub korelacja pozostaje sygnałem – nie dowodem przyczyny.

Volume wolno agregować lub porównywać tylko w porównywalnej activity_unit. Jeżeli produkty lub usługi różnią się pracochłonnością albo charakterem, analizuje się volume na poziomie produktu, stosuje udokumentowany weighted_volume albo uznaje zagregowany sygnał za niewystarczający. Nie tworzy się automatycznych wag, a revenue nie zastępuje volume. Gdy volume_comparability=false, CAP-01 nie formułuje wniosku o zmianie popytu na podstawie zagregowanego wolumenu.

### 10.1. Flagi planowej rezerwy

| exclusion_flag | Znaczenie |
| --- | --- |
| planned_reserve / seasonal_reserve | celowa lub sezonowa rezerwa |
| maintenance / training / leave | serwis, szkolenie, urlop |
| safety_buffer / demand_variability | bezpieczeństwo lub zmienność popytu |
| startup_phase / temporary_shutdown | rozruch lub czasowe wyłączenie |
| other_planned_unavailability | inne udokumentowane ograniczenie planowe |

Aktywna flaga nie usuwa danych. Wymusza interpretację warunkową, może ustawić validation_required=true i zasila przyszły ZOP-CONF-01.

### 10.2. Hipotezy do weryfikacji

Dopuszczalne wyłącznie jako HIPOTEZY DO WERYFIKACJI: niedostateczny popyt; zła konstrukcja grafiku; nierównomierne rozmieszczenie; ograniczenie wcześniejszego lub późniejszego etapu procesu; niekorzystna struktura portfela; nadmierna dostępna zdolność; sezonowość; planowa rezerwa; błąd danych; zmiana organizacji pracy.

## 11. Kolejne testy i wspólne mechanizmy

| Wzorzec | next_test | Uzasadnienie |
| --- | --- | --- |
| niewykorzystanie + pogorszenie ekonomiki | FIN-01 | relacja kosztów i przychodów |
| koszt jednostkowy rośnie przy spadającym U | FIN-03 | koszt jednostkowy |
| zasób osobowy | HR-01 | koszt pracy względem efektu |
| zmiana popytu lub miksu | PORT-01 | struktura produktów/usług |
| kolejka, spiętrzenie, ograniczenie procesu | PROC-01 / PROC-02 | proces i wąskie gardło |
| nierównowaga lub used > available | CAP-02 | sygnał przeciążenia; metodologia poza CAP-01 |

CAP-01 zapisuje rekomendację i uzasadnienie. Nie uruchamia testu bez reguł orkiestracji i nie projektuje metodologii testów następczych.

### 11.1. Dane dla ZOP-PRI-01

utilization_gap; unused_capacity_units; capacity_gap_units; economic_gap; persistence; trend_direction; deterioration_rate; organizational_scope; affected_resources; demand_signal; result_risk; urgent_validation. CAP-01 nie projektuje finalnego Priority Score.

### 11.2. Dane dla ZOP-CONF-01

Kompletność danych; spójność jednostek; jakość available i used; zgodność capacity_unit; ślad przejścia available_source → effective_available; długość szeregu; jakość i porównywalność referencji; jakość podziału kosztu; dostępność i porównywalność ACTIVITY; planowa rezerwa; used > available; liczba braków; ręczna walidacja; zdarzenia zaburzające. CAP-01 nie wylicza Confidence Score.

## 12. Struktura FINDINGS

| Pole bazowe | Reguła CAP-01 |
| --- | --- |
| test_id | CAP-01 |
| scope | filtry, unit, zasoby i capacity_unit |
| period | current + reference + horyzont |
| status | status logiczny testu |
| finding | komunikat faktograficzny |
| metric_value / reference_value | U_current / U_ref |
| gap | UG albo Capacity_gap_units zgodnie z opisem |
| impact_low / impact_high | odpowiedzialny przedział albo null |
| confidence_score / confidence_class | wynik ZOP-CONF-01 albo null |
| next_tests | tablica id + uzasadnienie |
| validation_required | boolean |

### 12.1. Rozszerzenia CAP-01

| Pole techniczne | Treść |
| --- | --- |
| resource / resource_type | identyfikacja zasobu i typu |
| capacity_unit | jednostka zdolności |
| available_source / documented_extra_capacity | wartość źródłowa i jawna korekta |
| effective_available / capacity_basis | podstawa zdolności użyta w obliczeniach |
| available_adjustment_source / reason / period / scope | pełny ślad korekty |
| available_current / used_current | effective_available i used badanego okna |
| utilization_current | U_current |
| unused_capacity / unused_capacity_rate | UC / UCR |
| utilization_reference | U_ref |
| utilization_gap | UG |
| capacity_gap_units | luka w capacity_unit |
| resource_cost / resource_cost_total | pole źródłowe cost i całkowity koszt zasobu |
| capacity_committed_cost | preferowana Capacity_cost_base |
| usage_variable_cost | koszt zależny od użycia |
| capacity_cost_base | podstawa miar kosztowych |
| raw_unused_capacity_cost | koszt UC na właściwej podstawie |
| reference_capacity_cost_gap | koszt odpowiadający luce do referencji |
| activity_unit / weighted_volume / volume_comparability | podstawa porównania ACTIVITY |
| peer_comparability | udokumentowana porównywalność internal_peer |
| volume_current / volume_reference / volume_change | porównywalny sygnał ACTIVITY |
| main_resources | ranking i lokalizacja |
| gross_unused_capacity_share | udział w UC porównywalnej grupy |
| adverse_capacity_gap_share | udział w dodatnich lukach |
| compensating_resources | osobna lista poprawiających |
| exclusion_flags | kod, okres, zakres, źródło |
| validation_notes | VAL, braki, ostrzeżenia i walidacja |

> **WARSTWY Dane → walidacja → obliczenia CAP-01 → interpretacja warunkowa → wsparcie decyzji. Hipoteza ≠ przyczyna; koszt luki ≠ oszczędność.**

## 13. Komunikat zarządczy

| Lp. | Element |
| --- | --- |
| 1 | status |
| 2 | nazwa problemu |
| 3 | wykorzystanie bieżące |
| 4 | wartość odniesienia |
| 5 | luka |
| 6 | trwałość |
| 7 | lokalizacja |
| 8 | wolumen / sygnał popytowy |
| 9 | ekonomiczna skala |
| 10 | ocena pewności |
| 11 | ograniczenia |
| 12 | kolejny krok |

> **[STATUS] WYKORZYSTANIE ZASOBU Wykorzystanie badanej grupy wynosi obecnie [U] wobec [U_ref] w okresie referencyjnym. Odchylenie utrzymuje się od [okres]. Największa luka występuje w [jednostki / zasoby]. Przy obecnej dostępnej zdolności odpowiada to [Capacity_gap_units] jednostkom względem referencji. Część kosztu odpowiadająca tej luce wynosi [kwota], jednak nie oznacza automatycznie oszczędności możliwej do uzyskania. Wolumen działalności [zmiana]. Pewność: [klasa / oczekuje]. Ograniczenia: [flagi]. W pierwszej kolejności należy zweryfikować [next_tests / hipotezy].**

Zakazane skróty decyzyjne: „należy zwolnić pracowników”, „zasób jest zbędny”, „organizacja traci X zł” – jeżeli jedyną podstawą jest CAP-01.

### 13.1. Statusy i pola wspólne

Statusy STANDARD / MEDIUM / HIGH / CRITICAL nada później ZOP-PRI-01. Pola confidence_score i confidence_class pozostają null do czasu zastosowania ZOP-CONF-01. Nie obniża to statusu metodologicznego CAP-01.

## 14. Scenariusze testowe CAP01-T01–T05

| Scenariusz | Dane | Obliczenia | Status | Flagi / walidacja | FINDINGS | next_tests |
| --- | --- | --- | --- | --- | --- | --- |
| CAP01-T01 Stabilne wykorzystanie | 24M; zgodne jednostki; U stabilne | U=Σused/Σeffective_available; UG≈0 względem poprawnej referencji | NO_ADVERSE_SIGNAL | brak; validation_required=false | pełny zapis U/UC/referencji; brak adverse finding | brak |
| CAP01-T02 Jednomiesięczny spadek | 1M spadek; 3M/6M/12M bez potwierdzenia | dodatni UG tylko 1M; UC zgodnie z danymi | INCIDENT | wg zdarzeń; zwykle false | finding ograniczony do incydentu | walidacja zdarzenia; ewentualnie brak |
| CAP01-T03 Trwałe niewykorzystanie | 24M; U niższe od U_ref przez 6M | U/UG/Capacity_gap_units na agregatach 6M | DETERIORATING | brak lub wg danych | trend, początek, main_resources, luki | FIN-01 / FIN-03 / PORT-01 wg sygnałów |
| CAP01-T04 U i volume spadają | RESOURCE + porównywalna ACTIVITY | ΔU<0; Δvolume<0; bez wniosku przyczynowego | DETERIORATING | demand_signal; wg danych | hipoteza popytu/portfela | PORT-01; ewentualnie FIN-03 |
| CAP01-T05 U spada, volume stabilne | U niższe; volume bez istotnej zmiany | ΔU<0; Δvolume≈0; dekompozycja | DETERIORATING | organizational_signal; wg danych | hipoteza rozmieszczenia/organizacji/procesu | PROC-01/02 lub HR-01 |

## 15. Scenariusze testowe CAP01-T06–T10

| Scenariusz | Dane | Obliczenia | Status | Flagi / walidacja | FINDINGS | next_tests |
| --- | --- | --- | --- | --- | --- | --- |
| CAP01-T06 Jedna jednostka | wynik globalny maskuje pogorszenie unit | globalnie + unit → resource; udziały w zgodnej grupie | DETERIORATING lokalnie | brak; false | main_resources wskazuje jednostkę i zasoby | wg sygnału: HR/PROC/FIN |
| CAP01-T07 A niewykorzystany, B przeciążony | A: U<U_ref; B: sygnał wysokiego U / przekroczenia | osobne miary; brak kompensowania | DETERIORATING + sygnał CAP-02 | imbalance; validation wg danych | A bez rekomendacji redukcji; B jawny | CAP-02 / PROC-02 |
| CAP01-T08 used > available | brak documented_extra_capacity | U wykazane; UC i luki zależne niewyznaczane | TEST_PARTIAL lub TEST_BLOCKED | validation_required=true | przekroczenie zachowane, bez ukrytej korekty | CAP-02; walidacja danych |
| CAP01-T09 Różne capacity_unit | godziny + sloty + cykle | oddzielne Σused/Σeffective_available w każdej grupie | wg każdej grupy | unit_mismatch; wg zakresu | brak wspólnego U i wspólnych udziałów | wg wyników grup |
| CAP01-T10 Brak cost | available i used poprawne; cost null | U, UC, UCR, UG i luka fizyczna; ekonomika null | wg trendu; nie TEST_BLOCKED | WARNING; validation wg polityki | economic_gap=null; jawne ograniczenie | test merytoryczny wg sygnału |

### 15.1. Scenariusze regresyjne CAP01-T11–T13

| Scenariusz | Dane | Obliczenia | Status | Flagi / walidacja | FINDINGS | next_tests |
| --- | --- | --- | --- | --- | --- | --- |
| CAP01-T11 KOSZT MIESZANY | zasób ma koszt utrzymania i usage_variable_cost | Capacity_cost_base=capacity_committed_cost; bez przypisania całego resource_cost_total | wg trendu U | przy nieznanej strukturze: wskaźnik brutto; validation_required=true | koszt na committed albo jawny wskaźnik brutto | wg sygnału testu |
| CAP01-T12 DODATKOWA ZDOLNOŚĆ | used>available_source; documented_extra_capacity prawidłowo udokumentowane | effective_available=available_source+documented_extra_capacity; U i UC na effective_available | wg trendu U | zachowany ślad: źródło, powód, okres, zakres, wartość | available_source bez zmian; jawna podstawa obliczeń | CAP-02 tylko gdy pozostaje sygnał przeciążenia |
| CAP01-T13 NIEPORÓWNYWALNY WOLUMEN | dwa produkty o istotnie różnej pracochłonności; surowy volume spada | produkt osobno albo udokumentowany weighted_volume; bez automatycznego wniosku o popycie | wg trendu U | właściwe volume_comparability; false przy braku podstawy | demand_signal=insufficient; validation_notes | PORT-01 lub walidacja ACTIVITY |

PASS scenariusza wymaga zgodności danych wejściowych, obliczeń, statusu logicznego, flag, validation_required, FINDINGS i next_tests. Sama poprawna wartość U nie wystarcza.

## 16. Kryteria odbioru implementacji – Aleksander

| Id | Kryterium | Odbiór |
| --- | --- | --- |
| CAP01-ACC-01 | przyjmuje RESOURCE zgodne z modelem | PASS |
| CAP01-ACC-02 | sprawdza capacity_unit | PASS |
| CAP01-ACC-03 | liczy U | PASS |
| CAP01-ACC-04 | liczy UC | PASS |
| CAP01-ACC-05 | liczy UCR | PASS |
| CAP01-ACC-06 | obsługuje effective_available = 0 | PASS |
| CAP01-ACC-07 | obsługuje used > available_source / effective_available | PASS |
| CAP01-ACC-08 | analizuje 1M/3M/6M/12M | PASS |
| CAP01-ACC-09 | agreguje jako Σused / Σeffective_available | PASS |
| CAP01-ACC-10 | nie agreguje nieporównywalnych jednostek | PASS |
| CAP01-ACC-11 | wyznacza U_ref | PASS |
| CAP01-ACC-12 | liczy UG | PASS |
| CAP01-ACC-13 | liczy Capacity_gap_units | PASS |
| CAP01-ACC-14 | wyznacza koszt niewykorzystanej zdolności, gdy możliwe | PASS |
| CAP01-ACC-15 | nie nazywa kosztu oszczędnością | PASS |
| CAP01-ACC-16 | dekomponuje do unit i resource | PASS |
| CAP01-ACC-17 | wykorzystuje ACTIVITY jako sygnał interpretacyjny | PASS |
| CAP01-ACC-18 | obsługuje exclusion_flags | PASS |
| CAP01-ACC-19 | ustawia validation_required | PASS |
| CAP01-ACC-20 | zapisuje FINDINGS | PASS |
| CAP01-ACC-21 | wskazuje next_tests | PASS |
| CAP01-ACC-22 | przechodzi CAP01-T01–T13 | PASS |
| CAP01-ACC-23 | nigdy nie nadpisuje available_source i zachowuje pełny ślad korekty | PASS |
| CAP01-ACC-24 | wykorzystuje effective_available w U, UC, UCR i lukach po udokumentowanej korekcie | PASS |
| CAP01-ACC-25 | rozróżnia capacity_committed_cost od usage_variable_cost i nie stosuje automatycznie resource_cost_total | PASS |
| CAP01-ACC-26 | nie interpretuje nieporównywalnego volume jako jednolitego sygnału popytowego | PASS |
| CAP01-ACC-27 | nie wykorzystuje nieporównywalnego zasobu jako internal_peer | PASS |

## 17. Definition of Done

| Id | Zakres | Status |
| --- | --- | --- |
| CAP01-DOD-01 | cel | PASS |
| CAP01-DOD-02 | definicja zasobu | PASS |
| CAP01-DOD-03 | available_source, documented_extra_capacity i effective_available bez nadpisania źródła | PASS |
| CAP01-DOD-04 | used | PASS |
| CAP01-DOD-05 | capacity_unit | PASS |
| CAP01-DOD-06 | walidacja | PASS |
| CAP01-DOD-07 | U na effective_available | PASS |
| CAP01-DOD-08 | UC i UCR na effective_available | PASS |
| CAP01-DOD-09 | referencja oraz kryteria peer_comparability dla internal_peer | PASS |
| CAP01-DOD-10 | UG | PASS |
| CAP01-DOD-11 | Capacity_gap_units na effective_available | PASS |
| CAP01-DOD-12 | resource_cost_total, capacity_committed_cost, usage_variable_cost i Capacity_cost_base | PASS |
| CAP01-DOD-13 | koszt ≠ oszczędność; wskaźnik brutto wymaga validation_required=true | PASS |
| CAP01-DOD-14 | ACTIVITY: activity_unit, weighted_volume i volume_comparability | PASS |
| CAP01-DOD-15 | horyzonty | PASS |
| CAP01-DOD-16 | agregacja | PASS |
| CAP01-DOD-17 | zasoby nieporównywalne | PASS |
| CAP01-DOD-18 | dekompozycja | PASS |
| CAP01-DOD-19 | flagi | PASS |
| CAP01-DOD-20 | hipotezy | PASS |
| CAP01-DOD-21 | next_tests | PASS |
| CAP01-DOD-22 | dane ZOP-PRI-01 | PASS |
| CAP01-DOD-23 | dane ZOP-CONF-01 obejmują porównywalność wolumenu, peer i podstawy kosztowej | PASS |
| CAP01-DOD-24 | FINDINGS zawiera pola pakietu korekcyjnego 02 | PASS |
| CAP01-DOD-25 | komunikat zarządczy | PASS |
| CAP01-DOD-26 | scenariusze CAP01-T01–T13 | PASS |
| CAP01-DOD-27 | odbiór implementacji CAP01-ACC-01–27 | PASS |

## 18. Test końcowy QCAP01

| Kontrola | Przedmiot | Wynik |
| --- | --- | --- |
| QCAP01-01 | uniwersalność branżowa | PASS |
| QCAP01-02 | jednoznaczna definicja zasobu | PASS |
| QCAP01-03 | rozróżnienie available_source / effective_available / used | PASS |
| QCAP01-04 | capacity_unit | PASS |
| QCAP01-05 | U = used / effective_available | PASS |
| QCAP01-06 | effective_available = 0 → null | PASS |
| QCAP01-07 | 0 założenia 100% = optimum | PASS |
| QCAP01-08 | 0 arbitralnych progów U | PASS |
| QCAP01-09 | internal_peer wymaga capacity_unit, capacity_basis, resource_group/funkcji i porównywalnego portfela | PASS |
| QCAP01-10 | UG | PASS |
| QCAP01-11 | Capacity_gap_units | PASS |
| QCAP01-12 | Capacity_cost_base = capacity_committed_cost; usage_variable_cost nie obciąża automatycznie luki | PASS |
| QCAP01-13 | niskie U ≠ nadmiar | PASS |
| QCAP01-14 | activity_unit, weighted_volume i volume_comparability chronią interpretację popytu | PASS |
| QCAP01-15 | korelacja ≠ przyczyna | PASS |
| QCAP01-16 | agregacja ważona effective_available | PASS |
| QCAP01-17 | przykład błędu średniej | PASS |
| QCAP01-18 | brak agregacji różnych jednostek | PASS |
| QCAP01-19 | dekompozycja unit → resource | PASS |
| QCAP01-20 | czynniki kompensujące | PASS |
| QCAP01-21 | flagi planowej rezerwy | PASS |
| QCAP01-22 | obsługa used > available_source / effective_available | PASS |
| QCAP01-23 | hipoteza ≠ przyczyna | PASS |
| QCAP01-24 | next_tests | PASS |
| QCAP01-25 | CAP-02 nieopracowany | PASS |
| QCAP01-26 | dane ZOP-PRI-01 | PASS |
| QCAP01-27 | ZOP-CONF-01 otrzymuje jakość kosztu, volume_comparability i peer_comparability | PASS |
| QCAP01-28 | FINDINGS zawiera wszystkie pola pakietu korekcyjnego 02 | PASS |
| QCAP01-29 | CAP01-T01–T13, w tym T11 koszt, T12 capacity, T13 volume | PASS |
| QCAP01-30 | CAP01-ACC-01–27 obejmuje pięć nowych kontroli | PASS |
| QCAP01-31 | DOD 01–27 testuje zmienioną treść i ma PASS | PASS |
| QCAP01-32 | 0 danych SPZOZ | PASS |
| QCAP01-33 | 0 danych pacjentów | PASS |
| QCAP01-34 | 0 aplikacji / AI | PASS |
| QCAP01-35 | gotowe dla Aleksandra | PASS |

## 19. Status końcowy

> **CAP-01 ZAMKNIĘTY METODOLOGICZNIE DO IMPLEMENTACJI**

| Zależność | Status |
| --- | --- |
| Priority Score | ZOP-PRI-01 – DO OPRACOWANIA |
| Confidence Score | ZOP-CONF-01 – DO OPRACOWANIA |

### 19.1. Otwarte kwestie wspólne

| Kwestia | Wpływ na CAP-01 |
| --- | --- |
| globalne przypisanie priorytetu | CAP-01 dostarcza dane; nie ustala progów |
| globalna ocena pewności | CAP-01 dostarcza dane; nie wylicza score |
| reguły orkiestracji next_tests | CAP-01 rekomenduje; nie uruchamia |
| standard dokumentowania dodatkowej zdolności | wspólny kontrakt danych do ujednolicenia |
| standard oceny porównywalności zasobów | wspólna reguła jakości, bez arbitralnego progu |

0 arbitralnych progów wykorzystania; 0 założenia „100% = optimum”; 0 automatycznych rekomendacji redukcji zasobów; 0 nowych progów Priority Score; 0 nowych progów Confidence Score; 0 danych SPZOZ; 0 danych pacjentów; 0 rozpoczętego CAP-02.
