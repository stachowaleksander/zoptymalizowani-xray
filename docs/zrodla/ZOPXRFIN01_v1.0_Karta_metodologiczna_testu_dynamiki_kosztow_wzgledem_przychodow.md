ZOPTYMALIZOWANI – X-RAY

# FIN-01

# Dynamika kosztów względem przychodów

Karta metodologiczna i specyfikacja implementacyjna

> **STATUS FIN-01 ZAMKNIĘTY METODOLOGICZNIE DO IMPLEMENTACJI**

| Pole | Wartość |
| --- | --- |
| Identyfikator | ZOP-XR-FIN-01 |
| Wersja / data | v1.0 / 1 września 2026 |
| Rola | pierwszy test wzorcowy Core 10 |
| Odbiorcy | zarządzający, analityk, programista |
| Zależności | ZOP-PRI-01 i ZOP-CONF-01 – DO OPRACOWANIA |

Dokument metodologiczny, specyfikacja dla Aleksandra i wzorzec konstrukcyjny kolejnych testów. Nie jest projektem aplikacji, dashboardu ani globalnej metodologii X-Ray.

## 1. Rola, cel i zakres FIN-01

FIN-01 diagnozuje relację ekonomiczną, a nie sam wzrost kosztów. Łączy przychody, koszty, trend, strukturę i wynik ekonomiczny. Test działa dla organizacji oraz wskazanego zakresu: jednostki, grupy jednostek, produktu albo okresu.

> **PYTANIE DIAGNOSTYCZNE Czy koszty organizacji rosną szybciej niż jej przychody, a jeżeli tak – gdzie występuje to zjawisko, od kiedy trwa, jaka jest jego skala oraz jaki może być jego wpływ ekonomiczny?**

### 1.1. Łańcuch diagnostyczny

| Etap | Produkt | Granica |
| --- | --- | --- |
| Dane | porównywalne szeregi R, C i aktywności | bez wnioskowania przed walidacją |
| Odchylenie | GR, GC, CRG i CI | dodatni CRG nie przesądza istotności |
| Trend | incydent / odchylenie / pogorszenie / stabilność / poprawa | 1M nie dowodzi trwałości |
| Lokalizacja | jednostki i kategorie | zależna od mapowania |
| Dekompozycja | udział w zmianie i aktywność | korelacja nie dowodzi przyczyny |
| Luka | wartość względem referencji | nie jest automatyczną oszczędnością |
| Hipotezy | mechanizmy do weryfikacji | zawsze HIPOTEZA DO WERYFIKACJI |
| Kolejne testy | rekomendacja z uzasadnieniem | bez projektowania ich metodologii |

### 1.2. Pytania objęte testem

FIN-01 odpowiada na 12 pytań: zmiana przychodów; zmiana kosztów; różnica dynamik; koszt wygenerowania 100 zł przychodu; trwałość; początek pogorszenia; jednostki odpowiedzialne; kategorie kosztów; wyjaśnienie zmianą działalności; zdarzenia zaburzające; luka ekonomiczna; dalsze testy.

## 2. Dane wejściowe i kontrakt danych

| Tabela | Pola | Rola |
| --- | --- | --- |
| ACTIVITY | date, unit, product, volume, revenue | czas, lokalizacja, portfel, aktywność i przychód |
| COST | date, unit, category, amount | czas, lokalizacja, kategoria i koszt |
| PLAN – opcjonalna | date, unit, metric, target | plan lub budżet jako referencja |

### 2.1. Zakres dowodowy

| Warunek | Wymaganie | Skutek |
| --- | --- | --- |
| Minimum | 12 miesięcy | pełny test podstawowy z oceną ograniczeń |
| Preferowane | 24–36 miesięcy | ocena trwałości i sezonowości |
| Krótszy szereg | liczenie tylko modułów z podstawą | WARNING albo CRITICAL; sygnał do pewności |
| Granularność | miesięczna | 1M, 3M, 6M, 12M / r/r |
| Klucze | jawne date + unit + product/category | ochrona przed podwójnym liczeniem |
| Waluta i znaki | jedna konwencja | brak ukrytego przeliczania |

> **ZASADA Revenue i amount są sumowane wyłącznie po poprawnie zdefiniowanych kluczach. scope zapisuje filtry, populację jednostek, okres i poziom agregacji.**

### 2.2. Zakres uniwersalny branżowo

Kategorie kosztów i jednostki pochodzą z danych klienta. FIN-01 nie wymusza planu kont, branżowej klasyfikacji, danych medycznych ani szczególnej struktury organizacyjnej.

## 3. Walidacja danych

Każda kontrola zwraca PASS, WARNING albo CRITICAL. CRITICAL zatrzymuje moduły zależne; WARNING nie zatrzymuje testu, lecz trafia do validation_notes i danych dla ZOP-CONF-01.

| Id | Kontrola | Wynik krytyczny / ostrzeżenie |
| --- | --- | --- |
| FIN01-VAL-01 | istnieją dane przychodowe | CRITICAL, gdy uniemożliwia wiarygodne obliczenie; w innym przypadku WARNING |
| FIN01-VAL-02 | istnieją dane kosztowe | CRITICAL, gdy uniemożliwia wiarygodne obliczenie; w innym przypadku WARNING |
| FIN01-VAL-03 | okresy są porównywalne | CRITICAL, gdy uniemożliwia wiarygodne obliczenie; w innym przypadku WARNING |
| FIN01-VAL-04 | brak brakujących miesięcy | CRITICAL, gdy uniemożliwia wiarygodne obliczenie; w innym przypadku WARNING |
| FIN01-VAL-05 | kategorie kosztów są spójne | CRITICAL, gdy uniemożliwia wiarygodne obliczenie; w innym przypadku WARNING |
| FIN01-VAL-06 | jednostki są spójnie identyfikowane | CRITICAL, gdy uniemożliwia wiarygodne obliczenie; w innym przypadku WARNING |
| FIN01-VAL-07 | brak niewyjaśnionych wartości ujemnych | CRITICAL, gdy uniemożliwia wiarygodne obliczenie; w innym przypadku WARNING |
| FIN01-VAL-08 | brak duplikatów | CRITICAL, gdy uniemożliwia wiarygodne obliczenie; w innym przypadku WARNING |
| FIN01-VAL-09 | wystarczający okres odniesienia | CRITICAL, gdy uniemożliwia wiarygodne obliczenie; w innym przypadku WARNING |
| FIN01-VAL-10 | możliwe porównanie badanego okresu z referencją | CRITICAL, gdy uniemożliwia wiarygodne obliczenie; w innym przypadku WARNING |

### 3.1. Reguły wykonania

| Sytuacja | Zachowanie |
| --- | --- |
| CRITICAL globalny | TEST_BLOCKED; brak diagnozy zależnej od danych |
| CRITICAL lokalny | zatrzymanie zakresu; pozostałe zakresy liczone osobno |
| WARNING | kontynuacja i zapis wpływu na wynik |
| Mianownik 0 | miara = null / not_computable; bez wartości zastępczej |
| Ręczna walidacja | manual_validation=true wraz z notatką |

## 4. Metodyka obliczeń

### 4.1. Dynamika przychodów

GR = (Rₜ − Rₜ₋₁) / Rₜ₋₁

Rₜ – przychody okresu badanego; Rₜ₋₁ – przychody okresu odniesienia.

### 4.2. Dynamika kosztów

GC = (Cₜ − Cₜ₋₁) / Cₜ₋₁

Cₜ – koszty okresu badanego; Cₜ₋₁ – koszty okresu odniesienia.

### 4.3. Luka dynamiki

CRG = GC − GR

Wartość dodatnia oznacza szybszy wzrost kosztów; nie przesądza istotności.

### 4.4. Intensywność kosztowa

CI = C / R

Komunikat: „wygenerowanie 100 zł przychodu wymaga obecnie 100 × CI zł kosztu”.

| Miara | Format | Warunek brzegowy | Prezentacja |
| --- | --- | --- | --- |
| GR, GC, CRG | liczba dziesiętna | mianownik 0 → null | % i punkty procentowe |
| CI | liczba dziesiętna | R = 0 → null | zł na 100 zł przychodu |
| Kwoty | jedna waluta | brak mieszania walut | kwota i okres |
| Zaokrąglenie | po obliczeniu | pełna precyzja danych | 1–2 miejsca |

> **ZASADA Każda miara używa tego samego scope, filtra, okresu badanego i referencyjnego. Nie wolno łączyć różnych populacji jednostek bez jawnej flagi porównywalności.**

## 5. Horyzonty i analiza trendu

| Horyzont | Reguła deterministyczna | Rola analizy przebiegu |
| --- | --- | --- |
| 1M | R i C miesiąca vs analogiczny miesiąc referencyjny; GR, GC, CRG i CI na agregatach | sygnał, nie dowód trwałości |
| 3M | agregacja R i C w całym oknie 3M vs analogiczne porównywalne 3M; GR, GC, CRG i CI na agregatach | dodatkowa klasyfikacja kierunku i trwałości |
| 6M | agregacja R i C w całym oknie 6M vs analogiczne porównywalne 6M; GR, GC, CRG i CI na agregatach | dodatkowa klasyfikacja kierunku i trwałości |
| 12M / r/r | agregacja R i C w całym oknie 12M vs analogiczne porównywalne 12M; GR, GC, CRG i CI na agregatach | dodatkowa klasyfikacja kierunku, trwałości i sezonowości |
| 24–36M | okna zgodne z powyższymi regułami oraz pełny przebieg szeregu | trwałość, sezonowość i punkt zwrotny |

Dla każdego horyzontu podstawą obliczeń są agregaty R i C z całego badanego okna oraz analogicznego, porównywalnego okna referencyjnego. Analiza przebiegu danych pozostaje dodatkowym elementem służącym wyłącznie klasyfikacji kierunku i trwałości.

### 5.1. Klasy trendu

| Klasa | Definicja bez arbitralnego progu |
| --- | --- |
| INCIDENT | pojedynczy okres bez potwierdzenia 3M/6M/12M |
| SHORT_TERM_DEVIATION | kilka okresów bez podstaw do trwałości |
| DETERIORATING | kolejne obserwacje i horyzonty potwierdzają pogorszenie |
| STABLE | brak trwałego kierunku po uwzględnieniu zmienności |
| IMPROVING | potwierdzona poprawa w więcej niż jednym horyzoncie |
| VOLATILE / SEASONAL | niestabilność lub powtarzalny wzorzec sezonowy |

### 5.2. Początek pogorszenia

Silnik wskazuje najwcześniejszy okres, od którego pogorszenie utrzymuje się w kolejnych obserwacjach i znajduje potwierdzenie w szerszym horyzoncie. Przy sezonowości lub zdarzeniu zaburzającym zwraca przedział i validation_required=true.

## 6. Wartość odniesienia

| Kolejność | Źródło | Warunek |
| --- | --- | --- |
| 1 | historia własnej organizacji | porównywalny zakres i zasady |
| 2 | wcześniejszy porównywalny okres | zgodność sezonu i struktury |
| 3 | plan / budżet | zgodna definicja miary |
| 4 | porównywalne jednostki wewnętrzne | udokumentowana porównywalność |
| 5 | najlepszy własny okres | brak zdarzenia wyjątkowego |
| 6 | benchmark zewnętrzny | wiarygodne i jednoznaczne źródło |

### 6.1. Zapis referencji

| Pole | Treść |
| --- | --- |
| reference_type | own_history / comparable_period / plan_budget / internal_peer / best_own_period / external_benchmark |
| reference_period | okres lub data planu |
| reference_scope | zakres jednostek i produktów |
| reference_value | wartość użyta w obliczeniu |
| reference_quality | dane dla ZOP-CONF-01, bez lokalnego score |
| reference_notes / source | założenia, korekty, ograniczenia i źródło |

> **BRAK REFERENCJI FIN-01 może opisać trend i dekompozycję, ale nie wyznacza Gap. Pola gap, impact_low i impact_high pozostają null, a ograniczenie trafia do validation_notes.**

## 7. Dekompozycja i udział w zmianie

### 7.1. Poziom I – jednostka organizacyjna

Dla każdej jednostki: ΔR, ΔC, CI bieżące i referencyjne, wkład kwotowy oraz udział w pogorszeniu relacji globalnej. Ranking zachowuje także wkłady ujemne, które kompensują pogorszenie.

### 7.2. Poziom II – kategoria kosztu

Globalnie i w istotnych jednostkach: ΔC według category i udział w zmianie kosztów. Kategorie wynikają z danych klienta; mapowanie musi być stabilne albo jawnie zwalidowane.

net_contribution_shareᵢ = Δdriverᵢ / Σⱼ Δdriverⱼ

Udział drivera w zmianie netto, z zachowaniem znaków. Przy kompensujących się driverach wartość może wykraczać poza zakres 0–100%.

adverse_driver_shareᵢ = adverse_Δdriverᵢ / Σⱼ adverse_Δdriverⱼ

Udział drivera wyłącznie w sumie driverów pogarszających wynik; dla drivera niepogarszającego wartość wynosi 0 lub null zgodnie z kontraktem implementacyjnym.

| Element | Wynik | Ochrona |
| --- | --- | --- |
| Jednostka | ΔR, ΔC, CI, net_contribution_share i adverse_driver_share | bez łączenia różnych mianowników |
| Kategoria | ΔC oraz oba rodzaje udziału | zachować wzrosty i spadki |
| Czynniki kompensujące | drivery poprawiające wynik prezentowane osobno | nie usuwać ich z wyniku ani rankingu netto |
| Aktywność | Δvolume i relacja do R/C | nie uznawać korelacji za przyczynę |
| Ranking | main_units / main_cost_categories | metoda sortowania i pokrycie sumy |

> **WZORZEC „Jednostki B i D odpowiadają łącznie za 71% pogorszenia relacji kosztów do przychodów.” 71% jest przykładem komunikatu, nie progiem.**

## 8. Luka ekonomiczna i przedział wpływu

CI_ref = C_ref / R_ref

Referencyjna intensywność kosztowa.

C_expected = R_current × CI_ref

Koszt oczekiwany przy bieżącym przychodzie i referencyjnym CI.

Gap = C_actual − C_expected

Luka ekonomiczna względem przyjętej relacji referencyjnej.

| Wynik | Interpretacja |
| --- | --- |
| Gap > 0 | koszt faktyczny powyżej poziomu wynikającego z referencji |
| Gap = 0 | relacja zgodna z referencją w granicach precyzji |
| Gap < 0 | koszt poniżej referencji; nie nazywać automatycznie oszczędnością |
| Gap = null | brak referencji lub niewykonalne obliczenie |

### 8.1. impact_low / impact_high

Przedział powstaje tylko z co najmniej dwóch odpowiedzialnych referencji albo jawnego zakresu niepewności danych. Bez podstaw silnik zapisuje punktowe Gap, pozostawia przedział pusty i oznacza ograniczenie.

> **ZASTRZEŻENIE Kwota wymaga dekompozycji i weryfikacji przed uznaniem jej za potencjał możliwy do odzyskania.**

| Zakazane automatyczne określenie | Określenie właściwe |
| --- | --- |
| strata / oszczędność | luka ekonomiczna względem relacji referencyjnej |
| kwota do odzyskania | oszacowanie wymagające weryfikacji |

## 9. Flagi i hipotezy przyczyn

| exclusion_flag | Zdarzenie |
| --- | --- |
| acquisition | przejęcie przedsiębiorstwa |
| unit_open_close | otwarcie lub zamknięcie jednostki |
| major_investment | duża inwestycja |
| accounting_change | zmiana księgowania |
| oneoff_bonus | jednorazowa premia |
| severance | odprawy |
| restructuring | restrukturyzacja |
| major_price_change | znaczna zmiana cen |
| scope_change | zmiana zakresu działalności |
| oneoff_cost | jednorazowy koszt |
| accounting_adjustment | duża korekta księgowa |
| other_material_event | inne istotne zdarzenie |

Aktywna flaga ustawia validation_required=true i zapisuje okres, zakres, źródło oraz wpływ. Nie usuwa wyniku; wymusza interpretację warunkową.

### 9.1. Hipotezy do weryfikacji

| Wzorzec | Hipoteza – zawsze HIPOTEZA DO WERYFIKACJI |
| --- | --- |
| koszt pracy rośnie szybciej niż efekt | koszt pracy bez proporcjonalnego efektu |
| wolumen spada, koszty stabilne | koszty stałe / niewykorzystane zasoby |
| pogorszenie w produktach | zmiana portfela lub rentowności |
| koszt jednostkowy rośnie | pracochłonność lub ceny zakupów |
| skok w jednym okresie | zdarzenie jednorazowe / inwestycja / korekta |
| pogorszenie lokalne | wąskie gardło lub zmiana organizacji |

## 10. Kolejne testy i wspólne mechanizmy

| Wzorzec | next_test | Dlaczego |
| --- | --- | --- |
| dominujący koszt pracy | HR-01 | koszt pracy względem efektu |
| spadek R/volume przy utrzymanych C | CAP-01 | wykorzystanie zasobu |
| pogorszenie w produktach / miksie | PORT-01 | rentowność portfela |
| C rośnie szybciej niż volume | FIN-03 | koszt jednostkowy |
| pracochłonność / spiętrzenie | PROC-01 / PROC-02 | proces i wąskie gardło |

FIN-01 zapisuje rekomendację i uzasadnienie. Nie uruchamia testu bez reguł orkiestracji i nie projektuje metodologii testów następczych.

### 10.1. Dane dla ZOP-PRI-01

| Pole | Treść |
| --- | --- |
| deviation_size | CRG i zmiana CI |
| persistence | liczba i ciągłość okresów |
| trend_direction / deterioration_rate | kierunek i tempo |
| economic_scale | Gap / przedział, jeśli dostępny |
| organizational_scope | liczba i udział jednostek |
| result_risk / urgent_validation | ryzyko wyniku i pilność weryfikacji |

### 10.2. Dane dla ZOP-CONF-01

Kompletność danych; długość szeregu; spójność kategorii i jednostek; liczba okresów; zgodność 3M/6M/12M; zdarzenia jednorazowe; jakość referencji; liczba braków; ręczna walidacja. FIN-01 nie wylicza własnego Confidence Score.

## 11. Struktura FINDINGS

| Pole bazowe | Reguła |
| --- | --- |
| test_id | FIN-01 |
| scope | zakres i filtry |
| period | current + reference |
| status | status logiczny |
| finding | komunikat faktograficzny |
| metric_value / reference_value | główna miara i referencja |
| gap / impact_low / impact_high | liczby lub null |
| confidence_score / class | wynik ZOP-CONF-01 lub null |
| next_tests | tablica id + uzasadnienie |
| validation_required | boolean |

### 11.1. Rozszerzenia FIN-01

| Pole techniczne | Treść |
| --- | --- |
| revenue_current | przychód okresu badanego |
| revenue_reference | przychód okresu referencyjnego |
| revenue_growth | GR |
| cost_current | koszt okresu badanego |
| cost_reference | koszt okresu referencyjnego |
| cost_growth | GC |
| growth_gap | CRG |
| cost_intensity_current | CI okresu badanego |
| cost_intensity_reference | CI okresu referencyjnego |
| trend | klasa, początek, horyzonty i sezonowość |
| main_units | ranking, wkład i oba rodzaje udziału |
| main_cost_categories | ranking, wkład i oba rodzaje udziału |
| net_contribution_share | udział drivera w zmianie netto, ze znakiem |
| adverse_driver_share | udział drivera w sumie driverów pogarszających |
| compensating_drivers | osobna lista driverów poprawiających wynik |
| exclusion_flags | kod, okres, zakres, źródło |
| validation_notes | VAL, braki, ostrzeżenia, walidacja |

> **WARSTWY Dane → diagnostyka FIN-01 → interpretacja zjawiska → wsparcie decyzji. Wspólne pola FINDINGS pozostają nienaruszone.**

## 12. Komunikat zarządczy

| Lp. | Element |
| --- | --- |
| 1 | status |
| 2 | nazwa problemu |
| 3 | co wykryto |
| 4 | dane potwierdzające |
| 5 | trend |
| 6 | miejsce występowania |
| 7 | luka ekonomiczna |
| 8 | ocena pewności |
| 9 | ograniczenia |
| 10 | rekomendowany kolejny krok |

> **[STATUS] DYNAMIKA KOSZTÓW WZGLĘDEM PRZYCHODÓW Koszty rosną szybciej od przychodów, a zjawisko utrzymuje się od [okres]. Przychody zmieniły się o [GR], koszty o [GC], a luka dynamiki wyniosła [CRG]. Wygenerowanie 100 zł przychodu wymaga [100 × CI] zł kosztu wobec [referencja]. Największy udział mają [jednostki] i [kategorie]. Luka względem [referencja] wynosi [Gap / przedział]. Pewność: [klasa / oczekuje]. Ograniczenia: [flagi]. Kolejny krok: [next_tests], ponieważ [uzasadnienie].**

### 12.1. Reguły językowe

Hipoteza nigdy nie jest faktem. „Contribution” w komunikacji oznacza „udział w zmianie”. Gap to „luka ekonomiczna względem przyjętej relacji referencyjnej”. Statusy STANDARD / MEDIUM / HIGH / CRITICAL nadaje dopiero ZOP-PRI-01.

### 12.2. Statusy logiczne testu

NO_ADVERSE_SIGNAL, INCIDENT, SHORT_TERM_DEVIATION, DETERIORATING, STABLE, IMPROVING, TEST_PARTIAL, TEST_BLOCKED. To statusy diagnostyczne, nie wynik globalnej priorytetyzacji.

## 13. Scenariusze testowe FIN01-T01–T04

FIN01-T01  Wzrost proporcjonalny

| Dane wejściowe | Oczekiwany wynik | Status | Flagi | Dalsze testy |
| --- | --- | --- | --- | --- |
| 24M; R i C proporcjonalne | GR≈GC; CRG≈0; CI stabilne | NO_ADVERSE_SIGNAL | brak | brak |

FIN01-T02  Jeden miesiąc

| Dane wejściowe | Oczekiwany wynik | Status | Flagi | Dalsze testy |
| --- | --- | --- | --- | --- |
| 1M GC>GR; szersze horyzonty bez sygnału | CRG dodatni tylko 1M | INCIDENT | wg zdarzeń | walidacja |

FIN01-T03  Sześć miesięcy

| Dane wejściowe | Oczekiwany wynik | Status | Flagi | Dalsze testy |
| --- | --- | --- | --- | --- |
| 24M; GC>GR przez 6M; CI rośnie | trend, początek, dekompozycja, Gap | DETERIORATING | wg danych | HR/CAP/PORT/FIN-03 |

FIN01-T04  Spadek R

| Dane wejściowe | Oczekiwany wynik | Status | Flagi | Dalsze testy |
| --- | --- | --- | --- | --- |
| R spada; C stabilne; volume jest | GR<0; GC≈0; CI rośnie | DETERIORATING | brak | CAP/PORT/FIN-03 |

## 14. Scenariusze testowe FIN01-T05–T08

FIN01-T05  Jedna jednostka

| Dane wejściowe | Oczekiwany wynik | Status | Flagi | Dalsze testy |
| --- | --- | --- | --- | --- |
| R/C per unit; dominująca jednostka | main_units i udział zgodny z sumą | DETERIORATING | wg danych | CAP lub HR |

FIN01-T06  Jedna kategoria

| Dane wejściowe | Oczekiwany wynik | Status | Flagi | Dalsze testy |
| --- | --- | --- | --- | --- |
| spójne category; dominujące ΔC | poprawna kategoria i udział | DETERIORATING | brak | HR/FIN-03/PROC |

FIN01-T07  Koszt jednorazowy

| Dane wejściowe | Oczekiwany wynik | Status | Flagi | Dalsze testy |
| --- | --- | --- | --- | --- |
| skok C; oneoff_cost | wynik warunkowy | INCIDENT | validation_required | ręczna walidacja |

FIN01-T08  Braki / krótki okres

| Dane wejściowe | Oczekiwany wynik | Status | Flagi | Dalsze testy |
| --- | --- | --- | --- | --- |
| 6–11M lub brak miesięcy | tylko wykonalne moduły | TEST_PARTIAL albo TEST_BLOCKED – zależnie od wyniku walidacji | validation_required | uzupełnienie danych |

PASS scenariusza wymaga zgodności obliczeń, statusu, flag, validation_required, FINDINGS i next_tests. Sama prawidłowa liczba nie wystarcza.

## 15. Kryteria odbioru implementacji – Aleksander

| Id | Kryterium | Odbiór |
| --- | --- | --- |
| FIN01-ACC-01 | przyjmuje dane zgodne z modelem | PASS |
| FIN01-ACC-02 | zatrzymuje analizę przy błędach krytycznych | PASS |
| FIN01-ACC-03 | przekazuje ostrzeżenia | PASS |
| FIN01-ACC-04 | liczy GR | PASS |
| FIN01-ACC-05 | liczy GC | PASS |
| FIN01-ACC-06 | liczy CRG | PASS |
| FIN01-ACC-07 | liczy CI | PASS |
| FIN01-ACC-08 | analizuje kilka horyzontów | PASS |
| FIN01-ACC-09 | identyfikuje jednostki | PASS |
| FIN01-ACC-10 | identyfikuje kategorie | PASS |
| FIN01-ACC-11 | szacuje Gap | PASS |
| FIN01-ACC-12 | nie nazywa Gap oszczędnością | PASS |
| FIN01-ACC-13 | obsługuje exclusion_flags | PASS |
| FIN01-ACC-14 | ustawia validation_required | PASS |
| FIN01-ACC-15 | zapisuje FINDINGS | PASS |
| FIN01-ACC-16 | wskazuje next_tests | PASS |
| FIN01-ACC-17 | przechodzi T01–T08 | PASS |

## 16. Definition of Done

| Id | Zakres | Status |
| --- | --- | --- |
| FIN01-DOD-01 | cel testu | PASS |
| FIN01-DOD-02 | wymagane dane | PASS |
| FIN01-DOD-03 | walidacja | PASS |
| FIN01-DOD-04 | wzory | PASS |
| FIN01-DOD-05 | referencje | PASS |
| FIN01-DOD-06 | trend | PASS |
| FIN01-DOD-07 | dekompozycja | PASS |
| FIN01-DOD-08 | luka ekonomiczna | PASS |
| FIN01-DOD-09 | zdarzenia zaburzające | PASS |
| FIN01-DOD-10 | hipotezy | PASS |
| FIN01-DOD-11 | kolejne testy | PASS |
| FIN01-DOD-12 | dane PRI | PASS |
| FIN01-DOD-13 | dane CONF | PASS |
| FIN01-DOD-14 | FINDINGS | PASS |
| FIN01-DOD-15 | komunikat | PASS |
| FIN01-DOD-16 | scenariusze | PASS |
| FIN01-DOD-17 | odbiór techniczny | PASS |

## 17. QFIN01 i status końcowy

| Kontrola | Przedmiot | Wynik |
| --- | --- | --- |
| QFIN01-01 | cel jednoznaczny | PASS |
| QFIN01-02 | relacja C↔R | PASS |
| QFIN01-03 | wzory | PASS |
| QFIN01-04 | horyzonty | PASS |
| QFIN01-05 | hierarchia referencji | PASS |
| QFIN01-06 | 0 benchmarków bez źródła | PASS |
| QFIN01-07 | jednostki | PASS |
| QFIN01-08 | kategorie | PASS |
| QFIN01-09 | Gap ≠ oszczędność | PASS |
| QFIN01-10 | flagi | PASS |
| QFIN01-11 | hipoteza ≠ przyczyna | PASS |
| QFIN01-12 | next_tests | PASS |
| QFIN01-13 | dane PRI | PASS |
| QFIN01-14 | dane CONF | PASS |
| QFIN01-15 | 0 wzoru Priority | PASS |
| QFIN01-16 | 0 wzoru Confidence | PASS |
| QFIN01-17 | FINDINGS zgodne | PASS |
| QFIN01-18 | komunikat | PASS |
| QFIN01-19 | 8 scenariuszy | PASS |
| QFIN01-20 | odbiór | PASS |
| QFIN01-21 | DOD 01–17 PASS | PASS |
| QFIN01-22 | uniwersalność | PASS |
| QFIN01-23 | 0 danych SPZOZ/pacjentów | PASS |
| QFIN01-24 | 0 nowych testów | PASS |
| QFIN01-25 | gotowe dla Aleksandra | PASS |

> **FIN-01 ZAMKNIĘTY METODOLOGICZNIE DO IMPLEMENTACJI**

| Zależność | Status |
| --- | --- |
| Priority Score | ZOP-PRI-01 – DO OPRACOWANIA |
| Confidence Score | ZOP-CONF-01 – DO OPRACOWANIA |

### 17.1. Otwarte kwestie wspólne

| Kwestia | Wpływ |
| --- | --- |
| globalne przypisanie STANDARD/MEDIUM/HIGH/CRITICAL | FIN-01 dostarcza dane |
| globalne klasy A/B/C i confidence_score | FIN-01 dostarcza dane |
| orkiestracja automatyczna next_tests | FIN-01 tylko rekomenduje |

0 arbitralnych benchmarków; 0 nowych progów Priority Score; 0 nowych progów Confidence Score; 0 danych SPZOZ; 0 danych pacjentów; 0 rozpoczętych kolejnych testów.
