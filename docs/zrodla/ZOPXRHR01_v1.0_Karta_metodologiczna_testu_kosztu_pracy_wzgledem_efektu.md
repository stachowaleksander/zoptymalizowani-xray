ZOPTYMALIZOWANI – X-RAY

HR-01

Koszt pracy względem efektu

Karta metodologiczna i specyfikacja implementacyjna

> **STATUS HR-01 ZAMKNIĘTY METODOLOGICZNIE DO IMPLEMENTACJI**

| Pole | Wartość |
| --- | --- |
| Identyfikator | ZOP-XR-HR-01 |
| Wersja / data | v1.0 / 2 września 2026 |
| Rola | trzeci pełny test diagnostyczny X-Ray; wzorzec ekonomiki pracy |
| Odbiorcy | zarządzający, analityk, Aleksander – implementacja |
| Źródła nadrzędne | niniejsze polecenie; FIN-01 v1.0; CAP-01 v1.0; ZOP-TECH-01 |
| Zależności | ZOP-PRI-01 i ZOP-CONF-01 – DO OPRACOWANIA |

Dokument jednocześnie definiuje metodę, kontrakt danych, reguły obliczeń, strukturę FINDINGS, scenariusze regresyjne i kryteria odbioru implementacji. Nie projektuje aplikacji, panelu, AI, systemu premiowego ani oceny pojedynczych pracowników.

> **ZASADA NADRZĘDNA Wyższy koszt pracy nie jest równoznaczny z niższą efektywnością. HR-01 rozdziela cenę pracy od produktywności i nie zamienia sygnału diagnostycznego w automatyczną decyzję kadrową.**

## 1. Rola, cel i granica HR-01

HR-01 ocenia relację kosztu pracy do mierzalnego efektu w organizacji, jednostce albo porównywalnej grupie zasobów ludzkich. Lokalizuje zmianę, rozdziela koszt jednostki nakładu pracy od produktywności, bada trwałość i przekazuje hipotezy do dalszych testów.

> **PYTANIE DIAGNOSTYCZNE Czy koszt pracy pozostaje w odpowiedniej relacji do mierzalnego efektu działalności, a jeżeli nie – czy sygnał wiąże się ze wzrostem ceny pracy, zmianą nakładu, spadkiem produktywności, zmianą struktury działalności albo innym zjawiskiem wymagającym dalszej diagnozy?**

### 1.1. Granica testu

| HR-01 jest | HR-01 nie jest |
| --- | --- |
| testem relacji koszt → nakład → efekt | oceną jakości pracy pojedynczej osoby |
| analizą organizacja → unit → role_group/resource_group | rankingiem, systemem premiowym lub oceną kompetencji |
| sygnałem diagnostycznym i lokalizatorem odchylenia | narzędziem automatycznej redukcji zatrudnienia |
| specyfikacją mierzalnych reguł implementacyjnych | oceną kliniczną ani systemem czasu i ruchu |

Poziom pojedynczego resource może być użyty technicznie tylko przy porównywalnych danych i właściwej podstawie biznesowej. FINDINGS oraz komunikat zarządczy nie mogą generować automatycznej rekomendacji dotyczącej konkretnej osoby.

## 2. Łańcuch diagnostyczny

| Etap | Produkt | Granica |
| --- | --- | --- |
| Koszt pracy | labor_cost_total i labor_cost_basis | pełny koszt pracodawcy w jawnym zakresie |
| Nakład pracy | labor_input i labor_input_unit | bez mieszania jednostek i bez automatycznego mapowania FTE |
| Efekt | comparable_effect i effect_unit | null, gdy efekt nie jest odpowiedzialnie porównywalny |
| Produktywność | LP | efekt na jednostkę nakładu, nie cena pracy |
| Koszt jednostkowy | ULC | koszt pracy na jednostkę porównywalnego efektu |
| Trend i dekompozycja | 1M/3M/6M/12M; unit i role_group | bez prostych średnich wskaźników |
| Hipotezy i next_tests | mechanizmy do weryfikacji | hipoteza ≠ przyczyna |

## 3. Dane wejściowe i rozszerzenia

| Tabela | Pola bazowe | Rola w HR-01 |
| --- | --- | --- |
| RESOURCE | date, unit, resource, available, used, cost | zasób, zdolność, wykorzystanie i koszt; RESOURCE.used jest sygnałem CAP-01, a nie automatycznym labor_input |
| ACTIVITY | date, unit, product, volume, revenue | efekt działalności, produkt, wolumen; revenue wyłącznie pomocniczo |
| COST | date, unit, category, amount | składniki kosztu pracy; kontrola kompletności i uzgodnienie bez duplikacji |
| PLAN – opcjonalna | date, unit, metric, target | referencja planowa dla kosztu, nakładu, efektu lub wskaźnika |

## 4. Definicje i zgodność zakresu

Dopuszczalne rozszerzenia: role_group, resource_group, labor_input, labor_input_unit, labor_input_basis, productive_labor_input, labor_cost_total, labor_fixed_cost, labor_variable_cost, fte, paid_hours, effect_unit, comparable_effect, weighted_volume, effect_comparability, effect_quality_comparability, accepted_effect, rework_signal, labor_cost_basis, employment_scope. Rozszerzenia nie zmieniają bazowej struktury ZOP-TECH-01.

| Pole | Definicja operacyjna | Warunek użycia |
| --- | --- | --- |
| labor_cost_total | całkowity koszt pracy przypisany do badanego zakresu i okresu | jawny labor_cost_basis; koszt pracodawcy, nie wynagrodzenie netto |
| labor_input | kosztotwórczy / opłacony nakład pracy należący do tego samego employment_scope, okresu i zakresu co labor_cost_total i comparable_effect | jawny labor_input_basis; wspólny mianownik LR i LP oraz podstawy tożsamości ULC = LR / LP |
| labor_input_unit | godziny, roboczogodziny, FTE-hours lub inna jednoznaczna jednostka | jedna jednostka w porównaniu albo udokumentowane przeliczenie |
| effect | mierzalny rezultat działalności: usługi, produkty, przepustowość lub wolumen | nie jest automatycznie przychodem |
| effect_unit | jednostka efektu | jawna, stabilna i zgodna w okresach |
| comparable_effect | efekt dopuszczony do obliczenia LP i ULC | porównywalny produkt, osobna analiza albo udokumentowany weighted_volume |

### 4.1. Podstawa kosztu pracy

labor_cost_basis opisuje, które składniki tworzą labor_cost_total. Co najmniej rozstrzyga wynagrodzenia zasadnicze, premie, nadgodziny, narzuty pracodawcy, świadczenia, umowy cywilnoprawne, podwykonawców i inne koszty pracy. Zakres powinien być spójny między okresami i grupami.

| Sytuacja | Reguła |
| --- | --- |
| RESOURCE.cost i COST.amount opisują ten sam koszt | uzgodnić i wyeliminować podwójne liczenie; zachować źródło i reconciliation_notes |
| podstawa zmieniła się między okresami | WARNING albo CRITICAL zależnie od wpływu; nie porównywać bez korekty lub ujawnienia |
| nieznany skład labor_cost_total | validation_required=true; obliczenia tylko w zakresie nieprowadzącym do fałszywej interpretacji |
| podwykonawcy lub UCP zmieniają employment_scope | ujawnić outsourcing_change/insourcing_change; zapewnić ten sam zakres kosztu i efektu |

> **ZASADA Nie wolno mieszać składników kosztu bez kontroli ani rekonstruować brakującej struktury arbitralnie. Zmiana labor_cost_basis wpływa na interpretację i dane dla ZOP-CONF-01.**

### 4.2. Nakład pracy

labor_input_basis określa źródło i znaczenie kosztotwórczego nakładu, np. paid_hours, cost_bearing_hours albo inną udokumentowaną podstawę. RESOURCE.used nie jest automatycznie mapowane do labor_input tylko dlatego, że oznacza pracę wykonaną; można go użyć wyłącznie przy udokumentowanej równoważności z nakładem odpowiadającym labor_cost_total. W przeciwnym razie RESOURCE.used pozostaje sygnałem CAP-01. Opcjonalne productive_labor_input służy analizie pomocniczej i nie zastępuje labor_input w LR, LP ani tożsamości ULC = LR / LP. FTE bez przeliczenia na porównywalny czas nie jest labor_input.

### 4.3. Efekt i porównywalność

Gdy produkty różnią się pracochłonnością lub charakterem, system analizuje je osobno, używa udokumentowanego weighted_volume albo ustawia comparable_effect=null. Wagi muszą mieć źródło, zakres, okres obowiązywania i stabilną metodę; HR-01 nie tworzy wag automatycznie. comparable_effect może zasilać LP i ULC tylko wtedy, gdy definicja ukończonej lub zaakceptowanej jednostki działalności pozostaje porównywalna. Wzrost surowego volume nie oznacza automatycznie wzrostu produktywności.

> **WSPÓLNA GRANICA labor_cost_total ↔ labor_input ↔ comparable_effect muszą mieć zgodne: okres, employment_scope, zakres organizacyjny i działalności oraz udokumentowany labor_input_basis. Praca pośrednia może wymagać wyższego poziomu agregacji; nie wolno przypisywać jej do produktu bez podstawy.**

## 5. Walidacja danych HR01-VAL-01–16

Każda kontrola zwraca PASS, WARNING albo CRITICAL. CRITICAL zatrzymuje zależny moduł lub zakres; WARNING pozwala kontynuować z validation_required i zapisem ograniczenia. Wynik lokalny nie blokuje automatycznie poprawnych zakresów.

| Id | Kontrola | Skutek negatywny |
| --- | --- | --- |
| HR01-VAL-01 | istnieje labor_cost_total | CRITICAL dla miar kosztowych; inaczej WARNING zakresowy |
| HR01-VAL-02 | istnieje labor_input | CRITICAL dla LR, LP i ULC |
| HR01-VAL-03 | labor_input_unit jest jednoznaczna | CRITICAL przy mieszaniu bez przeliczenia |
| HR01-VAL-04 | istnieje efekt działalności | WARNING; LP i ULC mogą pozostać null |
| HR01-VAL-05 | effect_unit jest jednoznaczna | CRITICAL dla LP/ULC przy niejednoznaczności |
| HR01-VAL-06 | koszt i labor_input dotyczą tego samego okresu | CRITICAL dla niezgodnego zakresu |
| HR01-VAL-07 | labor_input i effect dotyczą tego samego zakresu | CRITICAL dla niezgodnej granicy organizacyjnej/działalności |
| HR01-VAL-08 | brak duplikatów | CRITICAL, jeżeli wpływu nie można wiarygodnie wyłączyć |
| HR01-VAL-09 | istnieją porównywalne okresy | WARNING albo CRITICAL dla trendu i indeksów |
| HR01-VAL-10 | labor_cost_basis nie zmieniła się między okresami | WARNING/CRITICAL zależnie od materialności i możliwości korekty |
| HR01-VAL-11 | effect jest porównywalny | comparable_effect=null, gdy brak podstawy |
| HR01-VAL-12 | role_group/resource_group są porównywalne | brak peer/dekompozycji zbiorczej bez podstawy |
| HR01-VAL-13 | brak labor_input=0 przy dodatnim effect bez wyjaśnienia | CRITICAL dla LP/ULC; sygnał błędu mapowania |
| HR01-VAL-14 | ACTIVITY jest porównywalne z RESOURCE | CRITICAL dla połączenia efektu i pracy; zachować LR, jeśli możliwe |
| HR01-VAL-15 | istnieje właściwa referencja | WARNING; indeksy i wzrosty zależne pozostają null |
| HR01-VAL-16 | labor_cost_total ↔ labor_input ↔ comparable_effect mają wspólny okres, employment_scope, zakres i labor_input_basis | CRITICAL dla LR/LP/ULC przy niespójności; bez automatycznego mapowania RESOURCE.used |

### 5.1. Reguły wykonania

| Sytuacja | Zachowanie |
| --- | --- |
| mianownik = 0 | miara = null / not_computable; bez wartości zastępczej |
| comparable_effect = null | LR może być liczony; LP i ULC = null; TEST_PARTIAL |
| CRITICAL lokalny | zatrzymanie modułu dla zakresu; poprawne zakresy liczone oddzielnie |
| WARNING lub zdarzenie strukturalne | wynik zachowany; validation_required i validation_notes |
| niespójny poziom osoby | agregacja do właściwego role_group/resource_group albo brak findingu indywidualnego |

## 6. Metodyka obliczeń

### 6.1. Koszt jednostki nakładu pracy – Labor Rate

LR = labor_cost_total / labor_input

Ile organizację kosztuje jedna jednostka nakładu pracy. LR nie jest produktywnością.

### 6.2. Produktywność pracy – Labor Productivity

LP = comparable_effect / labor_input

Ile porównywalnego efektu powstaje z jednostki nakładu pracy. Gdy comparable_effect = null, LP = null.

### 6.3. Koszt pracy na jednostkę efektu – Unit Labor Cost

ULC = labor_cost_total / comparable_effect

Ile kosztu pracy przypada na jednostkę porównywalnego efektu.

ULC = LR / LP

Tożsamość obowiązuje wyłącznie, gdy LR i LP są obliczalne i LP ≠ 0.

### 6.4. Dynamiki i luka

| Miara | Wzór | Znaczenie |
| --- | --- | --- |
| LCG | (LCₜ − LC_ref) / LC_ref | dynamika labor_cost_total |
| EG | (Eₜ − E_ref) / E_ref | dynamika porównywalnego efektu |
| LCEG | LCG − EG | różnica dynamiki kosztu pracy i efektu |

LCEG = LCG − EG

Dodatnie LCEG oznacza, że koszt pracy wzrósł szybciej niż porównywalny efekt. Nie dowodzi problemu kadrowego, nie wskazuje przyczyny i nie jest automatyczną oszczędnością.

### 6.5. Indeksy

| Indeks | Wzór | Interpretacja |
| --- | --- | --- |
| LRI | LR_current / LR_reference | zmiana ceny jednostki nakładu pracy |
| LPI | LP_current / LP_reference | zmiana efektu przypadającego na jednostkę nakładu |
| ULCI | ULC_current / ULC_reference | zmiana kosztu pracy na jednostkę efektu |
| Tożsamość | ULCI = LRI / LPI | rozdzielenie sygnału ceny pracy i produktywności bez przypisywania udziałów przyczynowych |

> **KOMUNIKACJA „Koszt pracy na jednostkę efektu wzrósł o X%. Jednocześnie koszt jednostki nakładu pracy wzrósł o A%, a produktywność zmieniła się o B%.” Nie wolno pisać, że określony procent zmiany „wynika z pracowników” bez odrębnej metodologii.**

### 6.6. Obsługa zer i znaków

Gdy LC_ref, E_ref, LR_reference, LP_reference lub ULC_reference = 0, zależna dynamika albo indeks jest null. Ujemne koszty lub efekty wymagają jawnego oznaczenia korekty; bez wyjaśnienia uruchamiają walidację i nie są mechanicznie interpretowane.

## 7. Horyzonty, agregacja i wartość odniesienia

### 7.1. Horyzonty czasowe

| Horyzont | Zastosowanie | Reguła agregacji |
| --- | --- | --- |
| 1M | sygnał bieżący / incydent | Σlabor_cost_total, Σlabor_input, Σcomparable_effect |
| 3M | krótkie potwierdzenie | wskaźniki liczone dopiero z sum okna |
| 6M | trwałość średnia | bez średniej prostych miesięcznych LR/LP/ULC |
| 12M / r/r | sezonowość i porównanie roczne | porównywalny okres i podstawa kosztowa |
| 24–36M | trend, zmiany strukturalne | jeżeli dane są dostępne i porównywalne |

> **AGREGACJA Najpierw sumuje się liczniki i mianowniki, następnie oblicza LR, LP i ULC. Prosta średnia miesięcznych wskaźników jest zabroniona, gdy denominatory różnią się między miesiącami.**

### 7.2. Hierarchia referencji

| Priorytet | reference_type | Warunek |
| --- | --- | --- |
| 1 | own_history | ten sam unit i role_group/resource_group; porównywalna podstawa |
| 2 | comparable_period | wcześniejszy okres o zgodnym zakresie i sezonowości |
| 3 | plan | jawny target dla tej samej miary i jednostki |
| 4 | internal_peer | pełna peer_comparability |
| 5 | best_own_period | najlepszy własny okres bez zdarzenia zaburzającego |
| 6 | external_benchmark | wiarygodne źródło, zgodne definicje i zakres |

Nie stosuje się arbitralnych benchmarków udziału kosztów pracy w przychodach ani uniwersalnych norm produktywności. Brak wiarygodnej referencji pozostawia wzrosty, indeksy i luki jako null, bez obniżania jakości dostępnych miar bieżących.

### 7.3. internal_peer i peer_comparability

| Warunek minimalny | Wymaganie |
| --- | --- |
| role_group | zgodna rola albo udokumentowana funkcjonalna porównywalność |
| labor_input_unit | ta sama jednostka i sposób pomiaru nakładu |
| zakres działalności | porównywalny proces, odpowiedzialność i granica efektu |
| effect_unit | ta sama jednostka efektu lub wiarygodny weighted_volume |
| portfel | porównywalna struktura produktów/usług i pracochłonność |
| labor_cost_basis | porównywalny zakres składników kosztu pracodawcy |
| labor_input_basis | to samo źródło i znaczenie kosztotwórczego / opłaconego nakładu pracy |

Jeżeli warunki nie są spełnione, system nie tworzy internal_peer: preferuje własną historię albo pozostawia reference_value=null. peer_comparability i ograniczenia zasilają ZOP-CONF-01.

## 8. Porównywalność efektu i relacja z CAP-01

### 8.1. effect_comparability

| Sytuacja | Dopuszczalne działanie | Zabroniony skrót |
| --- | --- | --- |
| jednorodny produkt i effect_unit | sumowanie w zgodnym zakresie | mieszanie okresów lub jednostek |
| różne produkty o różnej pracochłonności | analiza osobno według product | prosta suma surowego volume |
| udokumentowane wagi | weighted_volume z wersją, źródłem i zakresem | wagi arbitralne lub zmieniane po wyniku |
| brak podstawy porównania | comparable_effect=null; LP i ULC=null | sztuczna wartość efektu |
| zmiana jakości, poprawek, braków, zwrotów, odrzuceń lub definicji ukończenia | effect_quality_comparability=false albo validation_required=true | automatyczny wzrost comparable_effect na podstawie surowego volume |
| wiarygodny accepted_effect i stabilna definicja akceptacji | LP i ULC mogą użyć accepted_effect jako comparable_effect; rework_signal pozostaje jawny | projektowanie osobnej metodologii jakości w HR-01 |

### 8.2. Przychód nie zastępuje efektu

Revenue może wspierać interpretację ekonomiczną, ale nie jest automatycznie effect. Wpływ cen, inflacji, taryf, portfela i innych zasobów uniemożliwia mechaniczne revenue/employee. Gdy revenue rośnie przy stabilnym volume, HR-01 kieruje uwagę do PORT-01 lub FIN-01, nie podnosi automatycznie LP.

### 8.3. Wzorce łączące HR-01 z CAP-01

| Wzorzec | Obserwacja | Interpretacja warunkowa / next_test |
| --- | --- | --- |
| A | ULC rośnie; LP spada; U spada | możliwe niewykorzystanie zdolności → CAP-01 |
| B | ULC rośnie; LP spada; U wysokie lub stabilne | proces, portfel, organizacja pracy lub role mix → PROC / PORT / dalsza analiza HR |
| C | ULC rośnie; LP stabilne; LR rośnie | sygnał ceny pracy, nie spadku produktywności |
| D | ULC stabilne; LR rośnie; LP rośnie | wzrost ceny pracy może być kompensowany wzrostem produktywności |

> **GRANICA PRZYCZYNOWA Żaden wzorzec nie jest przyczyną. CAP-01 dostarcza capacity_signal tylko wtedy, gdy dostępne są porównywalne available_source, effective_available i used. Brak CAP-01 obniża zakres interpretacji, nie unieważnia poprawnych miar HR-01.**

### 8.4. Sygnały kosztu i produktywności

| LR | LP | ULC | Sygnał diagnostyczny |
| --- | --- | --- | --- |
| ↑ | ≈ | ↑ | price/rate signal |
| ≈ | ↓ | ↑ | productivity signal |
| ↑ | ↓ | ↑↑ | dwa odrębne zjawiska; bez sztucznego podziału udziałów |
| ↑ | ↑ szybciej | ≈ lub ↓ | koszt jednostkowy stabilny lub lepszy |

### 8.5. Kontrakt danych z CAP-01

available_source, effective_available, used i capacity_unit określają podstawę capacity_signal. activity_unit, weighted_volume i volume_comparability określają, czy sygnał działalności może wspierać interpretację effect. peer_comparability pozostaje warunkiem użycia porównania wewnętrznego. HR-01 przejmuje te pola bez zmiany ich definicji z CAP-01.

## 9. Dekompozycja, udziały i zdarzenia

### 9.1. Poziomy analizy

| Poziom | Klucz | Minimalny wynik |
| --- | --- | --- |
| I | organization | LC, labor_input, comparable_effect, LR, LP, ULC, trendy |
| II | unit | jak wyżej + udział w zmianie i lokalizacja odchylenia |
| III | role_group / resource_group | jak wyżej, wyłącznie dla porównywalnej grupy |
| IV – opcjonalny | product / activity | efekt i pracochłonność, jeśli przypisanie pracy jest dowodowe |

Pojedynczy resource nie jest obowiązkowym poziomem FINDINGS. Jeżeli techniczna granularność jest dostępna, system stosuje zasady ochrony porównywalności i nie formułuje automatycznej oceny osoby.

### 9.2. Lokalizacja wzrostu kosztu i udział w pogorszeniu

labor_cost_increase_shareᵢ = max(ΔLCᵢ, 0) / Σ max(ΔLCⱼ, 0)

Neutralny udział jednostki lub grupy w dodatnim wzroście labor_cost_total w porównywalnym zakresie; lokalizuje wzrost kosztu, lecz nie oznacza nieefektywności ani pogorszenia. Przy sumie 0 wynik null.

adverse_ulc_gap_amountᵢ = max(ULCₜᵢ − ULC_refᵢ, 0) × comparable_effectₜᵢ

Ekonomiczna skala dodatniej luki ULC dla bieżącego efektu; nie jest automatyczną oszczędnością.

adverse_ulc_gap_shareᵢ = adverse_ulc_gap_amountᵢ / Σ adverse_ulc_gap_amountⱼ

Udział wyłącznie wewnątrz grupy zgodnej effect_unit i porównywalnej podstawy.

compensating_labor_groups przechowuje oddzielnie grupy poprawiające wynik (np. ujemna luka ULC lub spadek kosztu). Nie kompensuje nimi dodatnich udziałów i nie miesza nieporównywalnych effect_unit.

### 9.3. Flagi zmiany struktury pracy

| Flaga | Znaczenie | Flaga | Znaczenie |
| --- | --- | --- | --- |
| salary_change | zmiana stawek | regulatory_change | zmiana regulacyjna |
| overtime | nadgodziny | bonus | premia |
| severance | odprawa | new_hires | nowe zatrudnienia |
| role_mix_change | zmiana miksu ról | outsourcing_change | zmiana outsourcingu |
| insourcing_change | zmiana insourcingu | training | szkolenie |
| leave | nieobecność/urlop | startup_phase | rozruch |
| reorganization | reorganizacja | other_labor_event | inne zdarzenie |

Flaga nie usuwa wyniku. Wpływa na interpretację, validation_required i dane dla ZOP-CONF-01.

## 10. Hipotezy i kolejne testy

### 10.1. Hipotezy do weryfikacji

| Kod grupy | Dopuszczalne hipotezy |
| --- | --- |
| CENA PRACY | wzrost stawek; regulacja; premie; nadgodziny; zmiana form zatrudnienia |
| PRODUKTYWNOŚĆ | spadek produktywności; większa pracochłonność; wzrost pracy pośredniej |
| ZDOLNOŚĆ | niewykorzystana zdolność; przeciążenie; niekorzystna struktura grafiku |
| PORTFEL / PROCES | zmiana portfela; wąskie gardło; niedopasowanie organizacji pracy |
| STRUKTURA | role_mix_change; sezonowość; reorganizacja; startup_phase |
| DANE | błąd danych; niespójny labor_cost_basis; błędne mapowanie nakładu lub efektu |

> **ETYKIETA OBOWIĄZKOWA Każdy mechanizm jest zapisywany jako HIPOTEZA DO WERYFIKACJI. HR-01 nie zamienia korelacji, wskaźnika ani flagi w potwierdzoną przyczynę.**

### 10.2. next_tests

| next_test | Warunek rekomendacji | Cel |
| --- | --- | --- |
| FIN-01 | wzrost kosztu pracy wpływa na relację kosztów do przychodów | ekonomika kosztów i przychodów |
| CAP-01 | sygnał niewykorzystanej dostępnej zdolności | wykorzystanie zasobu |
| CAP-02 | przeciążenie, nadgodziny lub przekroczenie zdolności | metodologia poza HR-01 |
| FIN-03 | rośnie koszt jednostkowy | dalsza analiza kosztu jednostkowego |
| PORT-01 | miks działalności zmienia się lub efekt nie jest porównywalny | portfel produktów/usług |
| PROC-01 / PROC-02 | LP spada przy stabilnym lub wysokim wykorzystaniu | proces i wąskie gardło |

HR-01 zapisuje identyfikator i uzasadnienie. Nie projektuje metodologii tych testów ani nie uruchamia ich bez przyszłych reguł orkiestracji.

### 10.3. Dane dla ZOP-PRI-01 i ZOP-CONF-01

| Mechanizm | Minimalny pakiet danych | Status |
| --- | --- | --- |
| ZOP-PRI-01 | labor_cost_growth; effect_growth; labor_cost_effect_gap; labor_rate_change; labor_productivity_change; unit_labor_cost_change; persistence; trend_direction; organizational_scope; affected_role_groups; economic_scale; capacity_signal; result_risk; urgent_validation | DO OPRACOWANIA – HR-01 nie tworzy progów |
| ZOP-CONF-01 | kompletność kosztu; labor_cost_basis; labor_input_basis; porównywalność labor_input i effect; effect_comparability; effect_quality_comparability; rework_signal; peer_comparability; długość szeregu; jakość referencji; zmiana zatrudnienia i portfela; CAP-01; zdarzenia jednorazowe; braki; ręczna walidacja | DO OPRACOWANIA – HR-01 nie liczy score |

## 11. Struktura FINDINGS

### 11.1. Pola bazowe

| Pole bazowe | Reguła HR-01 |
| --- | --- |
| test_id | HR-01 |
| scope | organization/unit/role_group/resource_group + filtry i granica działalności |
| period | current + reference + horyzont |
| status | status wykonania/logiczny; docelowa istotność z ZOP-PRI-01 |
| finding | komunikat faktograficzny bez oceny osoby |
| metric_value | preferencyjnie ULC_current albo miara wskazana jawnie |
| reference_value | odpowiednia wartość referencyjna |
| gap | LCEG, zmiana ULC lub ekonomiczna luka – z identyfikatorem |
| impact_low / impact_high | odpowiedzialny przedział albo null; nigdy automatyczna oszczędność |
| confidence_score / confidence_class | wynik ZOP-CONF-01 albo null |
| next_tests | tablica test_id + uzasadnienie |
| validation_required | boolean + validation_notes |

### 11.2. Rozszerzenia HR-01

| Grupa pól | Pola techniczne |
| --- | --- |
| Zakres pracy | role_group; resource_group; employment_scope; labor_input; labor_input_unit; labor_input_basis; productive_labor_input |
| Koszt pracy | labor_cost_total; labor_cost_basis; labor_fixed_cost; labor_variable_cost |
| Cena pracy | labor_rate_current; labor_rate_reference; labor_rate_index |
| Efekt | effect_current; effect_reference; effect_unit; effect_comparability; comparable_effect; weighted_volume; effect_quality_comparability; accepted_effect; rework_signal |
| Produktywność | labor_productivity_current; labor_productivity_reference; labor_productivity_index |
| Koszt jednostkowy | unit_labor_cost_current; unit_labor_cost_reference; unit_labor_cost_index |
| Dynamika | labor_cost_growth; effect_growth; labor_cost_effect_growth_gap |
| Lokalizacja | main_units; main_role_groups; labor_cost_increase_share; adverse_ulc_gap_amount; adverse_ulc_gap_share |
| Kompensacja i kontrola | compensating_labor_groups; exclusion_flags; validation_notes; peer_comparability; capacity_signal |

## 12. Przebieg implementacji

| Krok | Operacja | Warunek wyjścia |
| --- | --- | --- |
| 1 | ustal scope, period i employment_scope | jawna granica analizy |
| 2 | zmapuj RESOURCE/ACTIVITY/COST/PLAN | bez zmiany bazowego modelu |
| 3 | uzgodnij labor_cost_total i labor_cost_basis | brak duplikacji kosztu |
| 4 | ustal labor_input, labor_input_unit i labor_input_basis | kosztotwórczy nakład zgodny z labor_cost_total; bez automatycznego RESOURCE.used |
| 5 | ustal effect_unit, comparable_effect i bramkę jakości | effect_comparability i effect_quality_comparability albo null/walidacja |
| 6 | wykonaj HR01-VAL-01–16 | PASS/WARNING/CRITICAL per zakres |
| 7 | agreguj 1M/3M/6M/12M | sumy przed wskaźnikami |
| 8 | oblicz LR, LP, ULC, dynamiki i indeksy | null dla nieobliczalnych |
| 9 | wybierz referencję i oceń peer_comparability | reference_metadata |
| 10 | dekomponuj i licz udziały porównywalnych grup | bez mieszania effect_unit |
| 11 | zapisz FINDINGS, hipotezy i next_tests | bez decyzji kadrowej |
| 12 | przekaż pakiety do PRI/CONF | bez lokalnego Priority/Confidence Score |

## 13. Komunikat zarządczy i status wykonania

> **[STATUS] KOSZT PRACY WZGLĘDEM EFEKTU Koszt pracy w badanym zakresie zmienił się o [X%], podczas gdy porównywalny efekt działalności zmienił się o [Y%]. Koszt pracy przypadający na jednostkę efektu wynosi obecnie [ULC] wobec [ULC_ref]. Zmiana wiąże się ze wzrostem kosztu jednostki nakładu pracy do [LR] oraz zmianą produktywności do [LP]. Największe odchylenie występuje w [unit / role_group]. Wynik nie przesądza o przyczynie. W pierwszej kolejności należy zweryfikować [next_tests].**

| Status logiczny | Znaczenie |
| --- | --- |
| NO_ADVERSE_SIGNAL | brak pogorszenia w porównywalnym zakresie |
| ADVERSE_SIGNAL | potwierdzona niekorzystna zmiana miary; bez rozstrzygnięcia przyczyny |
| TEST_PARTIAL | część miar obliczalna, np. LR przy comparable_effect=null |
| TEST_BLOCKED | krytyczny brak uniemożliwia wiarygodne obliczenie zakresu |

Statusy STANDARD / MEDIUM / HIGH / CRITICAL oraz finalną ocenę istotności nada w przyszłości ZOP-PRI-01. HR-01 nie tworzy progów priorytetu ani pewności.

## 14. Scenariusze testowe HR01-T01–T07

| Scenariusz | Dane | Oczekiwane obliczenia | Status | FINDINGS / next_tests |
| --- | --- | --- | --- | --- |
| HR01-T01 Stabilny koszt i efekt | LC, labor_input i effect stabilne | LR/LP/ULC stabilne | NO_ADVERSE_SIGNAL | brak |
| HR01-T02 Koszt +10%, efekt +10% | porównywalne okresy i podstawa | ULC stabilny | NO_ADVERSE_SIGNAL | brak fałszywego alarmu |
| HR01-T03 Koszt +15%, efekt +3% | pełna porównywalność | LCEG>0; ULC rośnie | ADVERSE_SIGNAL | dekompozycja; FIN-01/FIN-03 |
| HR01-T04 Wzrost stawki | LR rośnie; LP stabilne | ULC rośnie przez price/rate signal | ADVERSE_SIGNAL | bez tezy o spadku produktywności |
| HR01-T05 Spadek produktywności | LR stabilne; LP spada | ULC rośnie | ADVERSE_SIGNAL | PROC/CAP/PORT wg danych |
| HR01-T06 Stawka i produktywność rosną | LR +10%; LP +12% | ULC stabilny lub spada | NO_ADVERSE_SIGNAL | bez negatywnej oceny kosztu |
| HR01-T07 Niewykorzystana zdolność | LP spada; CAP-01: U spada | capacity_signal=true | ADVERSE_SIGNAL | CAP-01; hipoteza do weryfikacji |

PASS wymaga zgodności danych, walidacji, obliczeń, statusu, FINDINGS, exclusion_flags, validation_required i next_tests. Sama poprawna wartość jednego wskaźnika nie wystarcza.

## 15. Scenariusze testowe HR01-T08–T17

| Scenariusz | Dane | Oczekiwane obliczenia | Status | FINDINGS / next_tests |
| --- | --- | --- | --- | --- |
| HR01-T08 Wysokie U, LP spada | CAP bez niewykorzystania; LP↓ | ULC↑; capacity nie wyjaśnia sygnału | ADVERSE_SIGNAL | PROC-01/02 lub PORT-01 |
| HR01-T09 Zmiana miksu | surowy volume nieporównywalny | comparable_effect=null lub weighted_volume | TEST_PARTIAL | PORT-01; brak fałszywego LP |
| HR01-T10 Premia / odprawa | jednorazowy skok LC | exclusion_flag; LR/ULC z ograniczeniem | ADVERSE_SIGNAL lub TEST_PARTIAL | validation_required=true |
| HR01-T11 Zmiana kompetencji | większy udział droższej role_group | role_mix_change; osobna dekompozycja | wg wyniku | bez automatycznej nieefektywności |
| HR01-T12 Brak comparable_effect | LC i labor_input dostępne | LR obliczalny; LP=ULC=null | TEST_PARTIAL | jawne ograniczenie; PORT-01 |
| HR01-T13 Nakład 0, efekt dodatni | labor_input=0; effect>0 | LR/LP/ULC zależne=null | TEST_BLOCKED lokalnie | CRITICAL; walidacja mapowania |
| HR01-T14 Nieporównywalny peer | zgodna rola, różny portfel/effect_unit | internal_peer odrzucony | TEST_PARTIAL lub własna historia | peer_comparability=false |
| HR01-T15 Referencja 0 | LC_ref/E_ref lub indeksowy mianownik=0 | dynamika/indeks=null | TEST_PARTIAL | bez sztucznej wartości; validation_required |
| HR01-T16 Spada wykorzystanie, stawka bez zmiany | labor_cost_total i opłacony labor_input stabilne; RESOURCE.used↓; effect↓ | LR stabilne; LP↓; ULC↑; bez price/rate signal | ADVERSE_SIGNAL | capacity_signal; CAP-01 |
| HR01-T17 Więcej volume, gorsza jakość / poprawki | surowy volume↑; rework_signal↑ albo zmiana definicji accepted output | bez automatycznego wzrostu comparable_effect; LP/ULC tylko z wiarygodnym accepted_effect | TEST_PARTIAL lub wg wiarygodnego efektu | effect_quality_comparability=false lub validation_required=true |

### 15.1. Reguły antyfałszywego alarmu

| Sytuacja | Wymagane zachowanie |
| --- | --- |
| LC rośnie proporcjonalnie do effect | nie generować adverse signal wyłącznie na podstawie wzrostu LC |
| LR rośnie, LP stabilne | price/rate signal; bez komunikatu o spadku produktywności |
| LP lub ULC nieobliczalne | null; TEST_PARTIAL; zakaz zastępowania revenue |
| flaga jednorazowa lub strukturalna | wynik zachowany, interpretacja warunkowa, validation_required wg wpływu |
| poziom pojedynczej osoby | brak automatycznej oceny i rekomendacji kadrowej |

### 15.2. Dane syntetyczne

Scenariusze są testowane wyłącznie na danych syntetycznych lub technicznych. Dokument nie wykorzystuje danych SPZOZ, pacjentów ani rzeczywistych pracowników. Każdy scenariusz powinien mieć kontrolowany expected result oraz test regresyjny dla null, ostrzeżeń i statusu.

## 16. Kryteria odbioru implementacji – Aleksander

| Id | Kryterium | Odbiór |
| --- | --- | --- |
| HR01-ACC-01 | przyjmuje właściwe RESOURCE, ACTIVITY, COST i opcjonalne PLAN | PASS |
| HR01-ACC-02 | waliduje labor_cost_basis i uzgadnia źródła bez duplikacji | PASS |
| HR01-ACC-03 | waliduje labor_input_unit | PASS |
| HR01-ACC-04 | waliduje effect_unit i effect_comparability | PASS |
| HR01-ACC-05 | liczy LR | PASS |
| HR01-ACC-06 | liczy LP lub zwraca null | PASS |
| HR01-ACC-07 | liczy ULC lub zwraca null | PASS |
| HR01-ACC-08 | liczy LCG | PASS |
| HR01-ACC-09 | liczy EG tylko dla porównywalnego efektu | PASS |
| HR01-ACC-10 | liczy LCEG | PASS |
| HR01-ACC-11 | liczy LRI | PASS |
| HR01-ACC-12 | liczy LPI | PASS |
| HR01-ACC-13 | liczy ULCI i sprawdza tożsamość LRI/LPI | PASS |
| HR01-ACC-14 | analizuje 1M/3M/6M/12M oraz 24–36M, gdy dostępne | PASS |
| HR01-ACC-15 | sumuje liczniki i mianowniki przed obliczeniem; nie uśrednia prostych wskaźników | PASS |
| HR01-ACC-16 | nie miesza nieporównywalnych effect_unit ani labor_input_unit | PASS |
| HR01-ACC-17 | nie używa nieporównywalnego internal_peer | PASS |
| HR01-ACC-18 | dekomponuje do unit i role_group/resource_group | PASS |
| HR01-ACC-19 | obsługuje exclusion_flags bez usuwania wyniku | PASS |
| HR01-ACC-20 | ustawia validation_required i validation_notes | PASS |
| HR01-ACC-21 | zapisuje bazowe i rozszerzone FINDINGS | PASS |
| HR01-ACC-22 | wskazuje next_tests z uzasadnieniem | PASS |
| HR01-ACC-23 | nie generuje automatycznych decyzji kadrowych ani ocen osoby | PASS |
| HR01-ACC-24 | przechodzi HR01-T01–T17 | PASS |
| HR01-ACC-25 | obsługuje zera i nieobliczalne miary jako null | PASS |
| HR01-ACC-26 | nie zastępuje comparable_effect przychodem | PASS |
| HR01-ACC-27 | przekazuje komplet danych do ZOP-PRI-01 i ZOP-CONF-01 bez liczenia score | PASS |
| HR01-ACC-28 | liczy labor_cost_increase_share jako neutralną lokalizację wzrostu oraz adverse_ulc_gap_share jako miarę pogorszenia | PASS |
| HR01-ACC-29 | nie emituje findingu indywidualnego bez właściwej podstawy biznesowej i porównywalności | PASS |
| HR01-ACC-30 | waliduje labor_input_basis i zgodność labor_cost_total ↔ labor_input ↔ comparable_effect | PASS |
| HR01-ACC-31 | nie mapuje automatycznie RESOURCE.used do core labor_input; bez równoważności pozostawia capacity_signal | PASS |
| HR01-ACC-32 | nie generuje price/rate signal przy spadku wykorzystania, jeżeli LR pozostaje stabilne | PASS |
| HR01-ACC-33 | stosuje bramkę effect_quality_comparability i nie utożsamia surowego volume z produktywnością | PASS |
| HR01-ACC-34 | używa accepted_effect w LP/ULC wyłącznie przy wiarygodnej definicji akceptacji i uwzględnia rework_signal | PASS |

> **WARUNEK ODBIORU HR01-ACC-01–HR01-ACC-34 = PASS. Implementacja ma odtwarzać reguły dokumentu bez dodatkowej interpretacji metodologicznej.**

## 17. Definition of Done

| Id | Zakres | Status |
| --- | --- | --- |
| HR01-DOD-01 | cel | PASS |
| HR01-DOD-02 | granice testu | PASS |
| HR01-DOD-03 | labor_cost_total | PASS |
| HR01-DOD-04 | labor_input i labor_input_basis; brak automatycznego mapowania RESOURCE.used | PASS |
| HR01-DOD-05 | effect | PASS |
| HR01-DOD-06 | porównywalność efektu i bramka effect_quality_comparability | PASS |
| HR01-DOD-07 | walidacja HR01-VAL-01–16, w tym spójność koszt ↔ nakład ↔ efekt | PASS |
| HR01-DOD-08 | LR | PASS |
| HR01-DOD-09 | LP | PASS |
| HR01-DOD-10 | ULC | PASS |
| HR01-DOD-11 | LCG | PASS |
| HR01-DOD-12 | EG | PASS |
| HR01-DOD-13 | LCEG | PASS |
| HR01-DOD-14 | LRI | PASS |
| HR01-DOD-15 | LPI | PASS |
| HR01-DOD-16 | ULCI | PASS |
| HR01-DOD-17 | horyzonty i agregacja na sumach | PASS |
| HR01-DOD-18 | hierarchia referencji | PASS |
| HR01-DOD-19 | peer_comparability, w tym zgodność labor_input_basis | PASS |
| HR01-DOD-20 | dekompozycja; neutralny labor_cost_increase_share i adverse_ulc_gap_share | PASS |
| HR01-DOD-21 | flagi zdarzeń | PASS |
| HR01-DOD-22 | hipotezy ≠ przyczyny | PASS |
| HR01-DOD-23 | relacja z CAP-01 | PASS |
| HR01-DOD-24 | next_tests | PASS |
| HR01-DOD-25 | dane ZOP-PRI-01 bez Priority Score | PASS |
| HR01-DOD-26 | dane ZOP-CONF-01 bez Confidence Score | PASS |
| HR01-DOD-27 | FINDINGS | PASS |
| HR01-DOD-28 | komunikat zarządczy bez oceny pracownika | PASS |
| HR01-DOD-29 | scenariusze HR01-T01–T17 | PASS |
| HR01-DOD-30 | kryteria implementacyjne HR01-ACC-01–34 | PASS |

> **WYMAGANE HR01-DOD-01–HR01-DOD-30 = PASS.**

### 17.1. Ograniczenia wynikające z zależności wspólnych

ZOP-PRI-01 i ZOP-CONF-01 pozostają DO OPRACOWANIA. HR-01 dostarcza im komplet danych, ale nie tworzy finalnych wzorów, klas, progów ani score. Zależności te nie obniżają statusu HR-01.

## 18. Test końcowy QHR01

| Kontrola | Przedmiot | Wynik |
| --- | --- | --- |
| QHR01-01 | uniwersalność branżowa | PASS |
| QHR01-02 | HR-01 nie jest systemem oceny pracownika | PASS |
| QHR01-03 | labor_cost_total zdefiniowany | PASS |
| QHR01-04 | labor_cost_basis jawny i porównywalny | PASS |
| QHR01-05 | labor_input porównywalny, kosztotwórczy i opisany przez labor_input_basis | PASS |
| QHR01-06 | effect oraz definicja accepted output są porównywalne | PASS |
| QHR01-07 | revenue nie zastępuje effect | PASS |
| QHR01-08 | LR ≠ LP | PASS |
| QHR01-09 | LP liczona jako comparable_effect/labor_input | PASS |
| QHR01-10 | ULC liczony jako labor_cost_total/comparable_effect | PASS |
| QHR01-11 | ULCI rozdziela sygnał ceny i produktywności bez fałszywej atrybucji | PASS |
| QHR01-12 | brak arbitralnych benchmarków | PASS |
| QHR01-13 | brak automatycznej redukcji zatrudnienia | PASS |
| QHR01-14 | zmiana stawek ≠ automatycznie nieefektywność | PASS |
| QHR01-15 | relacja z CAP-01 | PASS |
| QHR01-16 | dekompozycja organization → unit → role_group/resource_group | PASS |
| QHR01-17 | hipoteza ≠ przyczyna | PASS |
| QHR01-18 | next_tests obecne | PASS |
| QHR01-19 | ZOP-PRI-01 pozostaje nieopracowany | PASS |
| QHR01-20 | ZOP-CONF-01 pozostaje nieopracowany | PASS |
| QHR01-21 | FINDINGS zgodne z TECH/FIN/CAP | PASS |
| QHR01-22 | co najmniej 12 scenariuszy – faktycznie 17 | PASS |
| QHR01-23 | HR01-DOD-01–30 = PASS | PASS |
| QHR01-24 | gotowość dla Aleksandra | PASS |
| QHR01-25 | 0 danych SPZOZ | PASS |
| QHR01-26 | 0 danych pacjentów | PASS |
| QHR01-27 | 0 rozpoczętego HR-02 | PASS |
| QHR01-28 | agregacja na sumach, nie prostych średnich | PASS |
| QHR01-29 | internal_peer wymaga pełnej peer_comparability | PASS |
| QHR01-30 | weighted_volume wyłącznie z udokumentowanymi wagami | PASS |
| QHR01-31 | comparable_effect=null prowadzi do LP i ULC=null | PASS |
| QHR01-32 | mianownik 0 prowadzi do null | PASS |
| QHR01-33 | RESOURCE.used nie jest automatycznie labor_input; available/FTE również nie | PASS |
| QHR01-34 | RESOURCE.cost i COST.amount nie są podwójnie liczone | PASS |
| QHR01-35 | zdarzenia strukturalne nie usuwają wyniku | PASS |
| QHR01-36 | labor_cost_increase_share jest neutralny; adverse_ulc_gap_share mierzy pogorszenie bez mieszania effect_unit | PASS |
| QHR01-37 | ekonomiczna luka ULC ≠ automatyczna oszczędność | PASS |
| QHR01-38 | brak indywidualnego findingu bez podstawy | PASS |
| QHR01-39 | statusy PRI nie są projektowane lokalnie | PASS |
| QHR01-40 | confidence_score/class pozostają null bez CONF | PASS |
| QHR01-41 | HR01-ACC-01–34 = PASS | PASS |
| QHR01-42 | 0 aplikacji, panelu i AI | PASS |
| QHR01-43 | labor_input_basis jest jawny i zgodny z labor_cost_total, employment_scope, okresem i efektem | PASS |
| QHR01-44 | productive_labor_input nie zastępuje core labor_input w LR, LP ani ULC = LR / LP | PASS |
| QHR01-45 | spadek RESOURCE.used przy stabilnym LR nie tworzy fałszywego price/rate signal | PASS |
| QHR01-46 | bramka effect_quality_comparability chroni LP/ULC przed zmianą jakości i definicji ukończenia | PASS |
| QHR01-47 | surowy wzrost volume nie zwiększa automatycznie comparable_effect | PASS |
| QHR01-48 | accepted_effect i rework_signal są obsługiwane bez projektowania testu jakości | PASS |
| QHR01-49 | HR01-T01–T17, w tym T16 i T17, mają oczekiwane wyniki regresyjne | PASS |

> **WYNIK QHR01 QHR01-01–QHR01-49 = PASS.**

## 19. Status końcowy i przekazanie do implementacji

> **HR-01 ZAMKNIĘTY METODOLOGICZNIE DO IMPLEMENTACJI**

| Element | Status / wynik |
| --- | --- |
| ZOP-XR-HR-01 | v1.0 – zamknięty metodologicznie do implementacji |
| ZOP-PRI-01 | DO OPRACOWANIA |
| ZOP-CONF-01 | DO OPRACOWANIA |
| HR01-DOD | 30/30 PASS |
| QHR01 | 49/49 PASS |
| Scenariusze | 17 – HR01-T01–T17 |
| Kryteria implementacyjne | 34 – HR01-ACC-01–34 PASS |
| next_tests | FIN-01; CAP-01; CAP-02; FIN-03; PORT-01; PROC-01; PROC-02 |

### 19.1. Otwarte kwestie wspólne – poza HR-01

| Kwestia | Status / wpływ |
| --- | --- |
| globalny mechanizm priorytetu | ZOP-PRI-01 do opracowania; HR-01 dostarcza payload |
| globalny mechanizm pewności | ZOP-CONF-01 do opracowania; HR-01 dostarcza sygnały jakości |
| standard wag comparable_effect | wspólny kontrakt; HR-01 wymaga dokumentacji i nie tworzy wag |
| reguły orkiestracji next_tests | poza HR-01; test jedynie rekomenduje |
| standard podstawy kosztowej między formami zatrudnienia | do ujednolicenia globalnie; labor_cost_basis pozostaje obowiązkowy |

### 19.2. Potwierdzenia granic

| Kontrola | Wynik |
| --- | --- |
| arbitralne benchmarki | 0 |
| automatyczne oceny pracowników | 0 |
| automatyczne rekomendacje redukcji zatrudnienia | 0 |
| revenue użyte automatycznie jako effect | 0 |
| nowe progi Priority Score | 0 |
| nowe progi Confidence Score | 0 |
| dane SPZOZ | 0 |
| dane pacjentów | 0 |
| rozpoczęty HR-02 | 0 |

> **DEFINITION OF DONE Dokument zawiera cel, granice, dane, walidację, pełne wzory, referencje, dekompozycję, FINDINGS, komunikat, 17 scenariuszy, 34 kryteria implementacyjne i 49 kontroli końcowych. HR-01 może zostać przekazany Aleksandrowi bez dodatkowej interpretacji metodologicznej.**
