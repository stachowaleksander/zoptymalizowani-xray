ZOPTYMALIZOWANI – X-RAY

# FIN-02

# Erozja rentowności

Karta metodologiczna i specyfikacja implementacyjna

> **STATUS FIN-02 ZAMKNIĘTY METODOLOGICZNIE DO IMPLEMENTACJI**

| Pole | Wartość |
| --- | --- |
| Identyfikator | ZOP-XR-FIN-02 |
| Wersja / data | v1.0 / 2 września 2026 |
| Rola | ósmy pełny test diagnostyczny X-Ray; wzorzec rodziny testów ekonomicznych |
| Odbiorcy | zarządzający, analityk, Aleksander – implementacja |
| Źródła nadrzędne | polecenie; FIN-01 v1.0; PORT-01 v1.0; HR-01 v1.0; CAP-01 v1.0; CAP-02 v1.0; PROC-01 v1.0; PROC-02 v1.0; ZOP-TECH-01; ZOP-MASTER-01 |
| Zależności | ZOP-PRI-01 i ZOP-CONF-01 – DO OPRACOWANIA |

FIN-02 rozdziela zmianę wyniku kwotowego od erozji stopy rentowności, uzgadnia zmianę za pomocą mostu wyniku i mostu marży oraz korzysta z PORT/HR/CAP/PROC wyłącznie jako warstwy wyjaśniającej. Nie projektuje FIN-03, FIN-04, aplikacji, panelu ani AI.

> **GRANICA Most rachunkowy rozlicza zmianę matematycznie. Explanatory evidence pomaga ją wyjaśnić. Tych warstw nie wolno dodawać do siebie ani przedstawiać jako jednego „100% przyczyn”.**

## 1. Rola, pytanie diagnostyczne i granice FIN-02

> **PYTANIE DIAGNOSTYCZNE Czy rentowność organizacji lub badanego zakresu pogarsza się, czy pogorszenie dotyczy kwoty wyniku, stopy marży czy obu jednocześnie oraz jakie mierzalne elementy rachunku ekonomicznego odpowiadają za tę zmianę?**

| Etap | Produkt | Granica |
| --- | --- | --- |
| Przychód | net_revenue | semantyka FIN-01 / PORT-01 |
| Koszt zmienny | direct_variable_cost | warstwa CM1 |
| Marża kontrybucyjna | CM1 / CM1R | kwota ≠ stopa |
| Koszt utrzymania zakresu | direct_committed_cost | warstwa SM |
| Wynik segmentowy | SM / SMR | hierarchiczny scope |
| Koszt wspólny | shared_cost | bez podwójnego allocated_shared_cost |
| Wynik operacyjny | operating_result_amount / operating_margin_rate | jawny operating_cost_basis |
| Zmiana | signed amount/rate gaps | signed ≠ adverse |
| Most wyniku | result_bridge_* | rachunkowe rozliczenie kwoty |
| Most marży | cost_load_gap_signed | rachunkowe rozliczenie stopy |
| Wyjaśnienia | explanatory_evidence | hipoteza ≠ przyczyna |
| Dalej | next_tests | bez automatycznej decyzji |

### 1.1. Najważniejsza zasada

> **ZASADA NADRZĘDNA Spadek kwoty wyniku i erozja rentowności procentowej nie są tym samym zjawiskiem.**

FIN-02 musi umieć rozpoznać niższy wynik przy stabilnej lub lepszej marży, wyższy wynik mimo gorszej marży, jednoczesne pogorszenie obu miar oraz jednoczesną poprawę. Nie ma lokalnego progu „istotnej erozji” — podstawą jest znak poprawnie policzonej zmiany i porównywalność danych.

### 1.2. FIN-01 ≠ FIN-02

| FIN-01 | FIN-02 |
| --- | --- |
| czy koszty zmieniają się niekorzystnie względem przychodów? | jak zmienia się wynik i stopa rentowności oraz jak matematycznie rozlicza się tę zmianę? |
| CRG i CI jako relacja dynamiki i intensywności kosztowej | kwota/rate + most wyniku + most marży |
| luka ekonomiczna względem referencyjnego CI | luki warstwy rentowności i rachunkowe efekty mostu |
| nie tworzy drugiej ekonomiki | musi uzgadniać przychód i koszt z FIN-01 |

### 1.3. PORT-01 ≠ FIN-02

| PORT-01 | FIN-02 |
| --- | --- |
| portfolio_item: produkt/usługa/pakiet | organization / unit / portfolio_group |
| CM1/SM/Full_result elementu | mechanizm zmiany całkowitej rentowności scope |
| mix_effect i margin_effect portfela | wykorzystuje wyniki PORT wyłącznie jako evidence |
| alokacja shared cost warunkowo | nie powtarza pełnej analizy portfela |

## 2. Zakres ekonomiczny, warstwy rentowności i koszt operacyjny

### 2.1. profitability_scope

| Wartość | Znaczenie |
| --- | --- |
| organization | cała organizacja lub uzgodniony pełny zakres ekonomiczny |
| unit | jednostka organizacyjna; operating result tylko przy poprawnym przypisaniu kosztów |
| portfolio_group | większy uzgodniony agregat portfela; nie pojedynczy portfolio_item |
| other_documented_scope | opcjonalny większy zakres o jawnych granicach |

FIN-02 nie schodzi automatycznie do pracownika, pojedynczego klienta ani pojedynczego case. Pełna ekonomika pojedynczego portfolio_item pozostaje domeną PORT-01.

### 2.2. profitability_layer

| Warstwa | Kwota | Stopa | Koszt należący do warstwy |
| --- | --- | --- | --- |
| CM1 | CM1 = net_revenue − direct_variable_cost | CM1R = CM1 / net_revenue | direct_variable_cost |
| SEGMENT_MARGIN | SM = CM1 − direct_committed_cost | SMR = SM / net_revenue | direct_variable_cost + direct_committed_cost |
| OPERATING_RESULT | operating_result_amount = net_revenue − operating_cost_total | operating_margin_rate = operating_result_amount / net_revenue | operating_cost_total zgodnie z jawną podstawą |

Każdy FINDING wskazuje profitability_layer. Luk i udziałów nie miesza się pomiędzy warstwami.

### 2.3. operating_cost_total

| operating_cost_total | direct_variable_cost + direct_committed_cost + shared_cost + unclassified_operating_cost Tylko przy wystarczającym mapowaniu; unclassified_operating_cost pozostaje jawny. |
| --- | --- |

| operating_result_amount | net_revenue − operating_cost_total |
| --- | --- |

| operating_margin_rate | operating_result_amount / net_revenue Tylko przy net_revenue > 0; przy net_revenue ≤ 0 → null / not_computable. |
| --- | --- |

| Pole | Kontrakt |
| --- | --- |
| operating_cost_basis | źródło i reguły zakresu kosztu operacyjnego; uzgadnialne z FIN-01 |
| operating_cost_scope | organizacyjna i ekonomiczna granica kosztu |
| unclassified_operating_cost | koszt należący do scope, którego nie wolno arbitralnie zaklasyfikować |
| cost_attribution_scope | semantyka PORT-01: organization / unit / portfolio_group / portfolio_item |
| allocation_basis / allocation_quality | warunek użycia pochodnej alokacji shared cost |

> **ZASADA SHARED COST allocated_shared_cost jest pochodnym przypisaniem części shared_cost. Nie jest czwartą pulą i nie może zostać drugi raz dodany do operating_cost_total.**

### 2.4. Hierarchiczny wynik

Jeżeli shared_cost istnieje wyłącznie na poziomie organization, jednostka może mieć poprawne CM1 i SM, ale warstwa OPERATING_RESULT dla unit pozostaje niepełna bez wiarygodnej allocation_basis. Brak alokacji nie blokuje warstw niższych; może powodować TEST_PARTIAL dla pełnego wyniku.

## 3. Walidacja danych FIN02-VAL-01–48

Każda kontrola zwraca PASS, WARNING albo CRITICAL. CRITICAL zatrzymuje moduł zależny, jeśli pozostała część testu może być wykonana odpowiedzialnie. WARNING zasila validation_notes i ZOP-CONF-01. Brak podstawy nie jest uzupełniany sztuczną wartością.

| Id | Kontrola | Skutek negatywny |
| --- | --- | --- |
| FIN02-VAL-01 | profitability_scope jest jawny i stabilny | CRITICAL dla porównania scope |
| FIN02-VAL-02 | profitability_layer jest jawny | CRITICAL dla interpretacji |
| FIN02-VAL-03 | net_revenue istnieje i ma zgodną semantykę | CRITICAL dla większości warstw |
| FIN02-VAL-04 | revenue_basis jest jawna i porównywalna | WARNING/CRITICAL |
| FIN02-VAL-05 | operating_cost_total jest uzgadnialny | CRITICAL dla OPERATING_RESULT |
| FIN02-VAL-06 | operating_cost_basis i operating_cost_scope są jawne | CRITICAL dla warstwy operacyjnej |
| FIN02-VAL-07 | direct_variable_cost zachowuje PORT-01 | CRITICAL dla CM1 |
| FIN02-VAL-08 | direct_committed_cost zachowuje PORT-01 | CRITICAL dla SM |
| FIN02-VAL-09 | shared_cost zachowuje PORT-01 | CRITICAL dla kosztu pełnego |
| FIN02-VAL-10 | allocated_shared_cost nie jest liczony drugi raz | CRITICAL przy double count |
| FIN02-VAL-11 | unclassified_operating_cost jest jawny | WARNING/CRITICAL wg pokrycia |
| FIN02-VAL-12 | CM1 uzgadnia się z revenue i variable cost | CRITICAL dla CM1 |
| FIN02-VAL-13 | SM uzgadnia się z CM1 i committed cost | CRITICAL dla SM |
| FIN02-VAL-14 | operating_result_amount uzgadnia się z revenue i operating cost | CRITICAL |
| FIN02-VAL-15 | net_revenue > 0 dla miar rate/load | CRITICAL dla rate; amount może pozostać |
| FIN02-VAL-16 | referencja jest źródłowa i porównywalna | WARNING; gaps=null |
| FIN02-VAL-17 | horyzont current/reference jest zgodny | CRITICAL dla porównań |
| FIN02-VAL-18 | 3M/6M/12M liczone z sum, nie średnich marż | CRITICAL przy złej agregacji |
| FIN02-VAL-19 | matched profitability scope jest jawny | WARNING/CRITICAL dla bridge |
| FIN02-VAL-20 | new/discontinued/materially_changed są oddzielone | WARNING/CRITICAL dla bridge |
| FIN02-VAL-21 | matched coverage current i reference są osobne | WARNING |
| FIN02-VAL-22 | structural_scope_change jest rozpoznany | WARNING/CRITICAL wg skali |
| FIN02-VAL-23 | accounting_basis_comparability jest znana | WARNING/CRITICAL |
| FIN02-VAL-24 | revenue_recognition_comparability jest znana | WARNING/CRITICAL |

FIN02-VAL-25–48 – ciąg dalszy

| Id | Kontrola | Skutek negatywny |
| --- | --- | --- |
| FIN02-VAL-25 | cost_classification_comparability jest znana | WARNING/CRITICAL |
| FIN02-VAL-26 | reclassification jest rozpoznana i ma basis | WARNING/CRITICAL |
| FIN02-VAL-27 | oneoff_flag ma oneoff_basis | WARNING; nie usuwać pozycji |
| FIN02-VAL-28 | adjusted view ma adjustment_basis | CRITICAL dla adjusted; actual pozostaje |
| FIN02-VAL-29 | allocation_quality pozwala na lokalny pełny wynik | WARNING/CRITICAL dla unit operating result |
| FIN02-VAL-30 | FIN-01 revenue reconciliation jest wykonane | WARNING/CRITICAL wg luki |
| FIN02-VAL-31 | FIN-01 cost reconciliation jest wykonane | WARNING/CRITICAL wg luki |
| FIN02-VAL-32 | PORT reconciliation wykonane, jeśli używane warstwy PORT | WARNING/CRITICAL |
| FIN02-VAL-33 | result bridge uzgadnia signed amount gap | CRITICAL przy istotnej niezgodności |
| FIN02-VAL-34 | margin bridge oraz adverse margin effects używają wyłącznie bridge_cost_load_gap_signed właściwych dla tego samego bridge_scope, profitability_layer, current/reference i podstawy ekonomicznej | CRITICAL przy mieszaniu full_scope i matched_scope |
| FIN02-VAL-35 | brak balancing item bez źródła | CRITICAL przy sztucznym domknięciu |
| FIN02-VAL-36 | signed i adverse gaps pozostają oddzielne | CRITICAL dla udziałów adverse |
| FIN02-VAL-37 | compensating_margin_effects zawierają wyłącznie ujemne bridge_cost_load_gap_signed właściwe dla tego samego bridge_scope | WARNING/CRITICAL przy mieszaniu full i matched |
| FIN02-VAL-38 | coverage ma zgodne mianowniki i scope | WARNING/CRITICAL |
| FIN02-VAL-39 | explanatory_evidence nie jest dodawane do bridge | CRITICAL przy double count |
| FIN02-VAL-40 | 0 danych SPZOZ/pacjentów i brak niezdefiniowanych danych wrażliwych | CRITICAL dla zgodności produktu |
| FIN02-VAL-41 | profitability_amount_direction i profitability_rate_direction wynikają ze signed gap; comparison_tolerance_basis jest wyłącznie techniczna | WARNING/CRITICAL przy niespójnej klasyfikacji |
| FIN02-VAL-42 | profitability_condition obejmuje stable amount/rate i nie używa mechanizmu scale contraction jako klasy amount/rate | CRITICAL dla klasyfikacji condition |
| FIN02-VAL-43 | bridge_scope jest jawny i odpowiada full_scope albo matched_scope | CRITICAL dla bridge |
| FIN02-VAL-44 | wszystkie matched_* current/reference należą do dokładnie tego samego matched_profitability_scope | CRITICAL dla matched bridge |
| FIN02-VAL-45 | result i margin bridge uzgadniają się wyłącznie z gapem tego samego bridge_scope | CRITICAL dla reconciliation |
| FIN02-VAL-46 | matched_profitability_coverage_current/reference mają wspólną matched_profitability_coverage_basis | WARNING/CRITICAL; różna podstawa → coverage null + validation_required |
| FIN02-VAL-47 | reported_vs_matched_amount_gap_difference_signed jest prezentowane osobno i nie stanowi balancing item ani causal attribution | CRITICAL dla fałszywej dekompozycji |
| FIN02-VAL-48 | new/discontinued/materially_changed pozostają poza matched bridge, gdy ograniczają porównywalność | WARNING/CRITICAL zależnie od wpływu |

## 4. Wynik kwotowy, stopa rentowności i profitability_condition

| Pole | Definicja |
| --- | --- |
| profitability_amount_current | kwota wybranej profitability_layer w current |
| profitability_amount_reference | kwota tej samej warstwy w reference |
| profitability_rate_current | stopa tej samej warstwy w current |
| profitability_rate_reference | stopa tej samej warstwy w reference |
| profitability_amount_direction | deteriorating / stable / improving / unresolved; wyznaczane z profitability_amount_gap_signed. >0 = deteriorating, <0 = improving, =0 = stable; brak porównywalnej podstawy = unresolved. |
| profitability_rate_direction | deteriorating / stable / improving / unresolved; analogicznie z profitability_rate_gap_signed. Dodatnia luka = deteriorating. |
| comparison_tolerance_basis | jawna techniczna tolerancja precyzji/zaokrągleń, jeżeli potrzebna do traktowania wartości numerycznie równych jako stable; nie jest progiem biznesowej istotności. |
| scale_contraction_signal | true, gdy revenue_change_signed < 0; false, gdy revenue_change_signed ≥ 0; null, gdy przychód nie jest porównywalny. Jest faktem pomocniczym, nie klasyfikacją mechanizmu. |

| profitability_amount_gap_signed | profitability_amount_reference − profitability_amount_current Dodatnia wartość = pogorszenie kwoty wyniku. |
| --- | --- |

| adverse_profitability_amount_gap | max(profitability_amount_gap_signed, 0) Nie jest automatycznie stratą, oszczędnością ani kwotą do odzyskania. |
| --- | --- |

| profitability_rate_gap_signed | profitability_rate_reference − profitability_rate_current Dodatnia wartość = erozja stopy rentowności. Jednostkę pp / udział dziesiętny zapisuj jawnie. |
| --- | --- |

| adverse_profitability_rate_gap | max(profitability_rate_gap_signed, 0) |
| --- | --- |

### 4.1. Macierz sytuacji rentowności

| profitability_condition | Warunek znaku | Znaczenie |
| --- | --- | --- |
| combined_deterioration | amount = deteriorating; rate = deteriorating | pogorszenie kwoty wyniku i stopy |
| growth_masking_margin_erosion | amount = improving; rate = deteriorating | wynik nominalny poprawia się mimo erozji stopy rentowności |
| stable_amount_margin_erosion | amount = stable; rate = deteriorating | kwota wyniku stabilna, lecz stopa rentowności się pogarsza |
| amount_deterioration_without_margin_erosion | amount = deteriorating; rate = stable lub improving | pogorszenie kwoty bez erozji stopy; mechanizm pozostaje do wyjaśnienia |
| improving_or_stable_profitability | amount = stable lub improving; rate = stable lub improving | brak erozji obu osi w porównywalnym zakresie |
| unresolved | brak porównywalnej podstawy dla co najmniej jednej osi | brak odpowiedzialnej klasyfikacji |

> **OCHRONA profitability_condition nie jest Priority Score i nie wprowadza progu biznesowej istotności. Kierunki amount/rate wynikają ze signed gap; dopuszczalna jest wyłącznie jawna comparison_tolerance_basis dla precyzji numerycznej. scale_contraction_signal jest osobnym faktem pomocniczym i nie zastępuje hipotezy mechanizmu.**

## 5. Most wyniku kwotowego

Most wyniku jest obowiązkowym rachunkowym rozliczeniem podpisanej zmiany kwoty wyniku. Dodatni składnik pogarsza wynik względem referencji, ujemny go kompensuje. Most nie jest causal attribution.

| Pole | Kontrakt |
| --- | --- |
| bridge_scope | full_scope / matched_scope |
| full_scope | most używa pełnych current/reference i uzgadnia się z profitability_amount_gap_signed oraz profitability_rate_gap_signed |
| matched_scope | most używa wyłącznie matched_* current/reference i uzgadnia się z matched_profitability_amount_gap_signed oraz matched_profitability_rate_gap_signed |
| reguła wyboru | gdy new/discontinued/materially_changed albo structural_scope_change ogranicza porównywalność, podstawowym bridge porównawczym jest matched_scope |
| zakaz | nie porównuj matched bridge z full-scope gap; elementów strukturalnych nie wciskaj do matched bridge |

| Pole | full_scope | matched_scope |
| --- | --- | --- |
| bridge_net_revenue_current | net_revenue_current | matched_net_revenue_current |
| bridge_net_revenue_reference | net_revenue_reference | matched_net_revenue_reference |
| bridge_direct_variable_cost_current/reference | direct_variable_cost_current/reference | matched_direct_variable_cost_current/reference |
| bridge_direct_committed_cost_current/reference | direct_committed_cost_current/reference | matched_direct_committed_cost_current/reference |
| bridge_shared_cost_current/reference | shared_cost_current/reference | matched_shared_cost_current/reference |
| bridge_unclassified_operating_cost_current/reference | unclassified_operating_cost_current/reference | matched_unclassified_operating_cost_current/reference |
| bridge_profitability_amount_gap_signed | profitability_amount_gap_signed | matched_profitability_amount_gap_signed |
| bridge_profitability_rate_gap_signed | profitability_rate_gap_signed | matched_profitability_rate_gap_signed |

| result_bridge_revenue_effect_signed | bridge_net_revenue_reference − bridge_net_revenue_current |
| --- | --- |

| result_bridge_variable_cost_effect_signed | bridge_direct_variable_cost_current − bridge_direct_variable_cost_reference |
| --- | --- |

| result_bridge_committed_cost_effect_signed | bridge_direct_committed_cost_current − bridge_direct_committed_cost_reference |
| --- | --- |

| result_bridge_shared_cost_effect_signed | bridge_shared_cost_current − bridge_shared_cost_reference |
| --- | --- |

| result_bridge_unclassified_cost_effect_signed | bridge_unclassified_operating_cost_current − bridge_unclassified_operating_cost_reference |
| --- | --- |

| result_bridge_total_signed | Σ właściwych result_bridge_effect_signed dla profitability_layer i bridge_scope |
| --- | --- |

Dla CM1 most zawiera tylko revenue i direct_variable_cost. Dla SEGMENT_MARGIN: revenue, direct_variable_cost i direct_committed_cost. Dla OPERATING_RESULT: revenue, direct_variable_cost, direct_committed_cost, shared_cost i unclassified_operating_cost.

| result_bridge_reconciliation_gap | bridge_profitability_amount_gap_signed − result_bridge_total_signed Przy pełnym pokryciu ≈ 0 w granicach wyłącznie technicznej tolerancji; nie dopasowuj składnika ręcznie. |
| --- | --- |

### 5.1. Udziały adverse i czynniki kompensujące

| adverse_result_effect_i | max(result_bridge_effect_signed_i, 0) |
| --- | --- |

| adverse_result_effect_share_i | adverse_result_effect_i / Σ adverse_result_effect Przy sumie 0 → null. Mianownik zawiera tylko składniki pogarszające w tej samej warstwie i scope. |
| --- | --- |

Składniki ujemne zachowuj jako compensating_result_effects. Poprawa jednego składnika nie może zniknąć tylko dlatego, że wynik całkowity się pogorszył.

> **REGUŁA KRYTYCZNA Most wyniku rozlicza arytmetycznie zmianę. Nie oznacza winy, oszczędności, możliwości odzyskania ani ustalonej przyczyny.**

## 6. Most marży i obciążenia kosztem

Most marży odpowiada na pytanie, która warstwa kosztu konsumuje większą lub mniejszą część przychodu. Nie jest drugim mostem kwotowym.

| Pole | Definicja zależna od bridge_scope |
| --- | --- |
| bridge_variable_cost_load_current/reference | bridge_direct_variable_cost_current/reference ÷ bridge_net_revenue_current/reference |
| bridge_committed_cost_load_current/reference | bridge_direct_committed_cost_current/reference ÷ bridge_net_revenue_current/reference |
| bridge_shared_cost_load_current/reference | bridge_shared_cost_current/reference ÷ bridge_net_revenue_current/reference |
| bridge_unclassified_cost_load_current/reference | bridge_unclassified_operating_cost_current/reference ÷ bridge_net_revenue_current/reference |
| bridge_*_cost_load_gap_signed | bridge_cost_load_current − bridge_cost_load_reference |
| bridge_cost_load_gaps | zestaw właściwych bridge_*_cost_load_gap_signed dla tego samego bridge_scope, profitability_layer, current/reference i podstawy ekonomicznej; full_scope używa full-scope cost loads, matched_scope wyłącznie matched/bridge cost loads |

| variable_cost_load | direct_variable_cost / net_revenue |
| --- | --- |

| committed_cost_load | direct_committed_cost / net_revenue |
| --- | --- |

| shared_cost_load | shared_cost / net_revenue |
| --- | --- |

| unclassified_cost_load | unclassified_operating_cost / net_revenue |
| --- | --- |

| operating_margin_rate | 1 − variable_cost_load − committed_cost_load − shared_cost_load − unclassified_cost_load Tylko przy pełnym pokryciu i net_revenue > 0. |
| --- | --- |

| cost_load_gap_signed_i | cost_load_current_i − cost_load_reference_i Dodatnia wartość = większa część przychodu konsumowana przez tę klasę kosztu. |
| --- | --- |

Dla CM1 profitability_rate_gap_signed = variable_cost_load_gap_signed. Dla SEGMENT_MARGIN jest sumą variable + committed. Dla OPERATING_RESULT jest sumą variable + committed + shared + unclassified, w granicach technicznej tolerancji.

| margin_bridge_reconciliation_gap | bridge_profitability_rate_gap_signed − Σ właściwych bridge_cost_load_gap_signed dla profitability_layer Przy tym samym bridge_scope; nie porównuj matched bridge z full-scope rate gap. Nie twórz balancing item bez źródła. |
| --- | --- |

| adverse_bridge_cost_load_gap_i | max(bridge_cost_load_gap_signed_i, 0) Wyłącznie dla składnika należącego do faktycznie prezentowanego bridge_scope i profitability_layer. |
| --- | --- |

| adverse_margin_erosion_share_i | adverse_bridge_cost_load_gap_i / Σ adverse_bridge_cost_load_gap Przy sumie 0 → null. Mianownik obejmuje wyłącznie składniki tego samego bridge_scope, profitability_layer, current/reference i podstawy ekonomicznej. Dla full_scope używaj full-scope bridge cost loads; dla matched_scope wyłącznie matched/bridge cost loads. Nie wolno używać full-scope cost_load_gap_signed_i do udziałów matched bridge. |
| --- | --- |
| compensating_margin_effects | ujemne bridge_cost_load_gap_signed_i właściwe dla tego samego bridge_scope, profitability_layer, current/reference i podstawy ekonomicznej; full i matched nie są mieszane |

> **ZASADA adverse_result_effect_share i adverse_margin_erosion_share odpowiadają na różne pytania. adverse_margin_erosion_share zawsze odpowiada faktycznie prezentowanemu margin bridge i jego bridge_scope. Nie wolno mieszać full_scope z matched_scope ani obu udziałów w jednym rankingu.**

## 7. Cost amount ≠ cost load

> **ZASADA NADRZĘDNA Koszt może się nie zmienić kwotowo, a mimo to jego ciężar względem przychodu może wzrosnąć.**

Przykład: shared_cost = 100 w current i reference, lecz revenue spada. shared_cost_amount_change = 0, ale shared_cost_load rośnie. Jest to erozja marży wskutek spadku skali przy niezmienionym koszcie; nie wolno pisać „shared cost wzrósł”.

| cost_amount_change_signed_i | cost_current_i − cost_reference_i |
| --- | --- |

| cost_load_gap_signed_i | cost_load_current_i − cost_load_reference_i |
| --- | --- |

### 7.1. cost_load_driver – wyłącznie typologia

| cost_load_driver | Znaczenie |
| --- | --- |
| cost_amount_increase | kwota kosztu wzrosła i wspiera wzrost load |
| revenue_contraction | kwota kosztu stabilna/spada, ale revenue spadł silniej |
| mixed | jednoczesny wpływ zmian numerator/denominator bez lokalnej dekompozycji PVM |
| compensating | składnik poprawia obciążenie marży |
| unresolved | brak podstaw do typologii |

FIN-02 nie przypisuje dokładnego procentu erozji numeratorowi i denominatorowi za pomocą arbitralnej sekwencyjnej dekompozycji ratio. Nie projektuje lokalnego price-volume-mix.

### 7.2. Revenue scale i comparable volume

| revenue_change_signed | net_revenue_current − net_revenue_reference Spadek revenue nie jest automatycznie erozją marży; może oznaczać wyłącznie scale contraction. |
| --- | --- |

| Pole | Reguła |
| --- | --- |
| comparable_volume | wolumen używany wyłącznie przy stabilnej activity_unit i porównywalnej strukturze |
| net_revenue_per_unit | net_revenue / comparable_volume; mianownik 0 lub brak porównywalności → null |
| variable_cost_per_unit | direct_variable_cost / comparable_volume; wyłącznie przy zgodnej podstawie kosztu |
| volume_comparability | warunek użycia miar jednostkowych; false → miary per unit = null |

> **GRANICA PRICE / VOLUME / MIX FIN-02 v1.0 nie buduje własnego modelu price-volume-mix. Gdy PORT-01 posiada wiarygodny mix_effect lub margin_effect, FIN-02 używa ich jako explanatory evidence. Gdy potrzebna jest pełna analiza kosztu jednostkowego, next_test = FIN-03.**

### 7.3. Zerowy lub ujemny przychód

| Sytuacja | Amount | Rate / cost load | Status zależny |
| --- | --- | --- | --- |
| net_revenue > 0 | obliczalny przy poprawnych kosztach | obliczalny | pełny moduł, jeśli pozostałe walidacje PASS |
| net_revenue = 0 | może pozostać obliczalny | null / not_computable | TEST_PARTIAL dla warstwy procentowej |
| net_revenue < 0 | może odzwierciedlać korekty | null / not_computable | validation_required; bez mechanicznej marży procentowej |

## 8. Explanatory evidence – warstwa wyjaśniająca

Mosty FIN-02 są warstwą księgowo-matematyczną. PORT, HR, CAP i PROC dostarczają dowodów wyjaśniających. Nie wolno dodawać mix_effect_rate, labor effects, capacity gap ani process time do mostu marży lub wyniku.

| Pole | Znaczenie / źródło |
| --- | --- |
| portfolio_mix_evidence | PORT-01: niekorzystny mix_effect lub zmiana struktury portfela |
| product_margin_evidence | PORT-01: pogorszenie margin_effect / adverse contribution gaps |
| labor_rate_evidence | HR-01: sygnał wzrostu ceny jednostki nakładu pracy |
| labor_productivity_evidence | HR-01: sygnał produktywności przy zgodnym scope/okresie |
| capacity_underutilization_evidence | CAP-01: spadek utilization przy stabilnym committed/shared cost |
| extra_capacity_dependency_evidence | CAP-02: regularna zależność od udokumentowanej extra capacity |
| capacity_shortage_evidence | CAP-02: verified capacity shortage w zgodnym scope |
| process_delay_evidence | PROC-01: delay/rework mogący zwiększać nakład; czas ≠ koszt |
| constraint_evidence | PROC-02: verified constraint powiązany z wolumenem/kosztem |
| unit_cost_evidence | FIN-03 w przyszłości: koszt jednostkowy |
| data_quality_evidence | walidacje, reconciliation i comparability |

Każde pole przyjmuje true / false / null/not_assessable. Brak danych nie jest false. Evidence wymaga zgodności scope i okresu z findingiem FIN-02.

### 8.1. Reguły relacji z testami

| Test | Sygnał | Granica |
| --- | --- | --- |
| PORT-01 | mix_effect < 0 / margin_effect < 0 / adverse gaps | ustaw odpowiednie portfolio evidence; nie dodawaj do bridge |
| HR-01 | rate/productivity/ULC signal | wspiera hipotezę kosztu pracy; nie przypisuje całej erozji |
| CAP-01 | U spada, committed/shared koszt stabilny | hipoteza gorszej absorpcji kosztu stałego |
| CAP-02 | extra dependency / verified shortage | evidence presji capacity; gap capacity nie wchodzi do bridge |
| PROC-01 | rework/delay może zwiększać work content | process evidence; 0 automatycznego przeliczenia czasu na pieniądze |
| PROC-02 | constraint może ograniczać wolumen lub wymuszać koszt | constraint evidence; bez causal shortcut |
| FIN-03 | variable cost load rośnie lub mechanizm jednostkowy niejasny | next_test; metodologia poza FIN-02 |

## 9. Matched profitability scope, zmiany strukturalne i rachunkowość

### 9.1. scope_item_status

| Status | Znaczenie |
| --- | --- |
| matched | element obecny i porównywalny current/reference |
| new | obecny tylko current lub bez poprawnej referencji |
| discontinued | obecny reference, nieobecny current |
| materially_changed | istotnie zmieniona definicja scope/cost center/działalności |

| Pole | Kontrakt |
| --- | --- |
| matched_profitability_coverage_basis | revenue / operating_cost / scope_count / documented_weight / other documented common basis |
| reguła porównywalności | current i reference muszą używać tej samej podstawy; nie pokazuj dwóch procentów opartych na różnych mianownikach |

| matched_profitability_coverage_current | matched_basis_value_current / eligible_basis_value_current Mianownik 0 → null. Podstawa jest określona przez matched_profitability_coverage_basis i musi być identyczna z reference. |
| --- | --- |

| matched_profitability_coverage_reference | matched_basis_value_reference / eligible_basis_value_reference Mianownik 0 → null. Ta sama matched_profitability_coverage_basis co current; przy różnej podstawie oba coverage porównawcze = null i validation_required=true. |
| --- | --- |

matched_profitability_scope_current i matched_profitability_scope_reference przechowują jednoznacznie zdefiniowany zakres porównywalny. Nowe i wycofane elementy pozostają poza matched bridge, chyba że istnieje odpowiedzialny mapping.

| Pole | Definicja / reguła |
| --- | --- |
| matched_net_revenue_current | net_revenue current wyłącznie dla dokładnie tego samego matched_profitability_scope |
| matched_net_revenue_reference | net_revenue reference dla dokładnie tego samego matched_profitability_scope |
| matched_direct_variable_cost_current | direct_variable_cost current w matched scope |
| matched_direct_variable_cost_reference | direct_variable_cost reference w matched scope |
| matched_direct_committed_cost_current | direct_committed_cost current w matched scope |
| matched_direct_committed_cost_reference | direct_committed_cost reference w matched scope |
| matched_shared_cost_current | shared_cost current w matched scope; bez double count allocated_shared_cost |
| matched_shared_cost_reference | shared_cost reference w matched scope |
| matched_unclassified_operating_cost_current | unclassified_operating_cost current w matched scope |
| matched_unclassified_operating_cost_reference | unclassified_operating_cost reference w matched scope |
| matched_profitability_amount_current | kwota profitability_layer current w matched scope |
| matched_profitability_amount_reference | kwota tej samej profitability_layer reference w matched scope |
| matched_profitability_amount_gap_signed | matched_profitability_amount_reference − matched_profitability_amount_current |
| adverse_matched_profitability_amount_gap | max(matched_profitability_amount_gap_signed, 0) |
| matched_profitability_rate_current | stopa profitability_layer current w matched scope; revenue > 0 |
| matched_profitability_rate_reference | stopa tej samej warstwy reference w matched scope; revenue > 0 |
| matched_profitability_rate_gap_signed | matched_profitability_rate_reference − matched_profitability_rate_current |
| adverse_matched_profitability_rate_gap | max(matched_profitability_rate_gap_signed, 0) |
| reported_vs_matched_amount_gap_difference_signed | profitability_amount_gap_signed − matched_profitability_amount_gap_signed; różnica opisowa full vs matched, nie balancing item, oszczędność, causal attribution ani „efekt restrukturyzacji” |

### 9.2. structural_scope_change

Powstanie lub likwidacja unit, przeniesienie działalności, zmiana cost center albo granicy organizacyjnej musi zostać ujawniona jako structural_scope_change. FIN-02 pokazuje wynik całkowity oraz wynik matched scope; nie nazywa całej zmiany „pogorszeniem porównywalnego biznesu”.

### 9.3. accounting comparability i reclassification

| Pole | Rola |
| --- | --- |
| accounting_basis_comparability | zgodność zasad księgowych i zakresu rachunku |
| revenue_recognition_comparability | zgodność momentu i zasad rozpoznania przychodu |
| cost_classification_comparability | zgodność klasyfikacji klas kosztu |
| cost_reclassification_flag | wskazuje przesunięcie tej samej ekonomiki między klasami |
| reclassification_basis | źródło i mapowanie reclassification |

> **RECLASSIFICATION Przeniesienie kosztu z direct_committed_cost do shared_cost przy niezmienionym operating_cost_total nie może stworzyć dwóch niezależnych zmian ekonomicznych. Całkowity result bridge pozostaje uzgodniony.**

### 9.4. One-off i adjusted view

| Pole | Reguła |
| --- | --- |
| oneoff_flag | oznacza zdarzenie jednorazowe; pozostaje w wyniku reported |
| oneoff_basis | źródło, okres, scope i opis zdarzenia |
| adjusted_profitability_amount | opcjonalny widok po udokumentowanej korekcie |
| adjusted_profitability_rate | opcjonalny widok stopy po udokumentowanej korekcie |
| adjustment_basis | jawna podstawa każdej korekty; actual zawsze obok |

## 10. Horyzonty, referencja, pokrycie i uzgodnienia

### 10.1. Horyzonty

| Horyzont | Reguła |
| --- | --- |
| 1M | sygnał bieżący / incydent |
| 3M | sumuj revenue i koszty w całym oknie; rates z agregatów |
| 6M | jak wyżej; trwałość średnioterminowa |
| 12M / r/r | porównywalne sumy roczne; sezonowość |
| 24–36M | trend, zmiany strukturalne, punkt zwrotny |

> **AGREGACJA Najpierw sumuj revenue, koszty i wyniki w oknie. Następnie licz margin rates i cost loads. Prosta średnia miesięcznych procentów jest niedopuszczalna, gdy mianowniki różnią się między okresami.**

### 10.2. Hierarchia referencji

| Priorytet | Źródło | Warunek |
| --- | --- | --- |
| 1 | historia tego samego matched profitability scope | stabilny zakres i accounting basis |
| 2 | wcześniejszy porównywalny okres | zgodna sezonowość i struktura |
| 3 | plan | jawna definicja wyniku/stopy |
| 4 | porównywalna jednostka wewnętrzna | udokumentowana comparability |
| 5 | najlepszy własny stabilny okres | bez materialnego one-off/zmiany scope |
| 6 | benchmark zewnętrzny | wiarygodne źródło i zgodne definicje |

Brak właściwej referencji pozostawia profitability_*_gap_signed i adverse_*_gap jako null. FIN-02 nie wymyśla benchmarku marży.

### 10.3. Pokrycie danych

| Pole | Znaczenie |
| --- | --- |
| revenue_coverage | część scope objęta wiarygodnym przychodem |
| operating_cost_coverage | część kosztu operacyjnego objęta rachunkiem |
| cost_classification_coverage | część kosztu wiarygodnie przypisana do klas |
| matched_profitability_coverage_current | pokrycie porównywalne current |
| matched_profitability_coverage_reference | pokrycie porównywalne reference |
| bridge_coverage | część zmiany objęta uzgadnialnym mostem |
| matched_profitability_coverage_basis | wspólna podstawa current/reference: revenue / operating_cost / scope_count / documented_weight; różna podstawa → coverage porównawcze null + validation_required |

Coverage zasila ZOP-CONF-01. FIN-02 nie ustanawia arbitralnego progu akceptacji.

### 10.4. Uzgodnienie z FIN-01 i PORT-01

| Pole | Znaczenie |
| --- | --- |
| revenue_reconciliation_gap_FIN01 | różnica przychodu FIN-02 vs FIN-01 w identycznym scope |
| cost_reconciliation_gap_FIN01 | różnica kosztu FIN-02 vs FIN-01 |
| result_reconciliation_gap | różnica uzgodnionego wyniku między warstwami/źródłami |
| PORT_revenue_reconciliation_gap | różnica przychodu przy użyciu semantyki PORT |
| PORT_cost_reconciliation_gap | różnica kosztów klas PORT |
| PORT_margin_reconciliation_gap | różnica CM1/SM w zgodnym scope |

### 10.5. Dostępność modułów przy niepełnych danych

| Moduł | Minimalna podstawa | Zachowanie przy braku |
| --- | --- | --- |
| CM1 amount | revenue + direct_variable_cost | może działać mimo braku shared allocation |
| SM amount | CM1 + direct_committed_cost | może działać mimo braku shared allocation |
| OPERATING_RESULT amount | pełny operating_cost_total lub odpowiedzialny scope | TEST_PARTIAL/BLOCKED przy nieuzgadnialnym koszcie |
| profitability rate | net_revenue > 0 + zgodna warstwa | null przy nieprawidłowym mianowniku |
| result bridge | porównywalne current/reference + pokrycie składników | reconciliation_gap jawny |
| margin bridge | net_revenue > 0 w obu okresach + zgodna klasyfikacja | reconciliation_gap jawny |
| matched bridge | jawny matched scope current/reference | new/discontinued/changed osobno |
| adjusted view | udokumentowany adjustment_basis | nigdy nie zastępuje reported |

> **BRAK SZTUCZNEGO DOMYKANIA Jeżeli modułu nie da się odpowiedzialnie policzyć, wynik pozostaje null / TEST_PARTIAL / TEST_BLOCKED. FIN-02 nie tworzy balancing item, arbitralnej klasyfikacji ani sztucznej alokacji tylko po to, aby tabela była pełna.**

## 11. Dekompozycja, hipotezy i next_tests

### 11.1. Dekompozycja

| Poziom | Zakres | Minimalny wynik |
| --- | --- | --- |
| I | organization | amount/rate, condition, oba bridge, coverage |
| II | unit | lokalizacja erosion; CM1/SM/warunkowo operating result |
| III – opcjonalny | portfolio_group | większy porównywalny zakres; nie pojedynczy portfolio_item |

FIN-02 nie schodzi automatycznie do pracownika, pojedynczego klienta ani pojedynczego case. Jeżeli potrzebna jest ekonomika pojedynczego elementu portfela, next_test = PORT-01.

### 11.2. Hipotezy do weryfikacji

> **HIPOTEZY spadek skali działalności; niekorzystny miks; spadek ceny / stawki; wzrost kosztu zmiennego; wzrost kosztu utrzymania zdolności; wzrost kosztu wspólnego; gorsza absorpcja kosztów stałych; wzrost ceny pracy; spadek produktywności; niewykorzystanie capacity; zależność od extra capacity; przeciążenie; rework; problem procesu; zmiana klasyfikacji księgowej; one-off; zmiana zakresu działalności; błąd danych. Każda pozostaje HIPOTEZĄ DO WERYFIKACJI do czasu właściwego dowodu.**

### 11.3. next_tests

| Test | Kiedy rekomendować |
| --- | --- |
| FIN-01 | szersza analiza dynamiki kosztów i przychodów |
| FIN-03 | koszt jednostkowy / niejasny variable cost load |
| PORT-01 | miks lub ekonomika produktów |
| HR-01 | koszt pracy / produktywność |
| CAP-01 | niewykorzystanie i absorpcja committed/shared cost |
| CAP-02 | presja lub extra capacity może zwiększać koszt |
| PROC-01 | czas / rework może zwiększać nakład |
| PROC-02 | constraint może ograniczać wolumen lub koszt |
| MGT-01 | główny problem to brak uzgodnienia, klasyfikacji albo wiarygodnej informacji |

FIN-02 zapisuje rekomendację i uzasadnienie. Nie uruchamia testu bez wspólnej orkiestracji i nie projektuje metodologii testów niezamrożonych.

## 12. Dane dla ZOP-PRI-01, ZOP-CONF-01 i FINDINGS

### 12.1. Payload ZOP-PRI-01

> **ZOP-PRI-01 – DO OPRACOWANIA profitability_layer; profitability_condition; profitability_amount_direction; profitability_rate_direction; comparison_tolerance_basis; profitability_amount_gap_signed; adverse_profitability_amount_gap; profitability_rate_gap_signed; adverse_profitability_rate_gap; bridge_scope; matched_profitability_amount_current; matched_profitability_amount_reference; matched_profitability_amount_gap_signed; adverse_matched_profitability_amount_gap; matched_profitability_rate_current; matched_profitability_rate_reference; matched_profitability_rate_gap_signed; adverse_matched_profitability_rate_gap; reported_vs_matched_amount_gap_difference_signed; scale_contraction_signal; adverse_result_effect_share; bridge_cost_load_gaps; adverse_bridge_cost_load_gap; adverse_margin_erosion_share; result_bridge_reconciliation_gap; margin_bridge_reconciliation_gap; revenue_change_signed; cost_load_gaps; persistence; trend_direction; economic_scale; organizational_scope; affected_units; explanatory_evidence; result_risk; urgent_validation. FIN-02 nie projektuje Priority Score.**

### 12.2. Payload ZOP-CONF-01

> **ZOP-CONF-01 – DO OPRACOWANIA revenue_coverage; operating_cost_coverage; cost_classification_coverage; bridge_coverage; bridge_scope; matched_profitability_coverage_current; matched_profitability_coverage_reference; matched_profitability_coverage_basis; matched_scope_comparability; comparison_tolerance_basis; accounting_basis_comparability; revenue_recognition_comparability; cost_classification_comparability; allocation_quality; reference_quality; FIN01_reconciliation_quality; PORT01_reconciliation_quality; scope_comparability; oneoff_quality; adjustment_quality; manual_validation; exclusion_flags. Różna matched_profitability_coverage_basis current/reference → coverage porównawcze null + validation_required. FIN-02 nie liczy lokalnego Confidence Score.**

### 12.3. Bazowa struktura FINDINGS

| Pole bazowe | Reguła FIN-02 |
| --- | --- |
| test_id | FIN-02 |
| scope | profitability_scope + filtry + warstwa |
| period | current + reference + horyzont |
| status | status logiczny X-Ray |
| finding | komunikat faktograficzny |
| metric_value / reference_value | główna kwota lub stopa i referencja |
| gap | signed gap właściwy dla findingu |
| impact_low / impact_high | odpowiedzialny przedział albo null; nie automatyczny potencjał |
| confidence_score / confidence_class | wynik ZOP-CONF-01 albo null |
| next_tests | tablica id + uzasadnienie |
| validation_required | boolean + validation_notes |

### 12.4. Rozszerzenia FINDINGS FIN-02

| Grupa | Pola techniczne |
| --- | --- |
| Identyfikacja | profitability_scope; profitability_layer; unit; portfolio_group; profitability_condition; profitability_amount_direction; profitability_rate_direction; comparison_tolerance_basis; bridge_scope; scale_contraction_signal |
| Revenue i koszt | net_revenue_current/reference; operating_cost_total_current/reference; direct_variable_cost_current/reference; direct_committed_cost_current/reference; shared_cost_current/reference; unclassified_operating_cost_current/reference |
| Kwota/stopy | profitability_amount_current/reference; profitability_amount_gap_signed; adverse_profitability_amount_gap; profitability_rate_current/reference; profitability_rate_gap_signed; adverse_profitability_rate_gap; matched_profitability_amount_current; matched_profitability_amount_reference; matched_profitability_amount_gap_signed; adverse_matched_profitability_amount_gap; matched_profitability_rate_current; matched_profitability_rate_reference; matched_profitability_rate_gap_signed; adverse_matched_profitability_rate_gap |
| Cost loads | variable_cost_load_current/reference/gap_signed; committed_cost_load_current/reference/gap_signed; shared_cost_load_current/reference/gap_signed; unclassified_cost_load_current/reference/gap_signed |
| Most wyniku | result_bridge_revenue_effect_signed; result_bridge_variable_cost_effect_signed; result_bridge_committed_cost_effect_signed; result_bridge_shared_cost_effect_signed; result_bridge_unclassified_cost_effect_signed; result_bridge_reconciliation_gap |
| Most marży | margin_bridge_reconciliation_gap; bridge_cost_load_gaps; adverse_bridge_cost_load_gap; adverse_margin_erosion_share; compensating_margin_effects; adverse_result_effect_share; compensating_result_effects; cost_load_driver |
| Wyjaśnienia | explanatory_evidence; revenue_change_signed; comparable_volume; net_revenue_per_unit; variable_cost_per_unit |
| Porównywalność | matched_profitability_scope_current/reference; matched_profitability_coverage_current/reference; accounting_basis_comparability; revenue_recognition_comparability; cost_classification_comparability |
| Kontekst | cost_reclassification_flag; reclassification_basis; oneoff_flag; oneoff_basis; structural_scope_change; adjusted_profitability_amount/rate; adjustment_basis; exclusion_flags; validation_notes |
| Matched / struktura | matched_net_revenue_current; matched_net_revenue_reference; matched_direct_variable_cost_current/reference; matched_direct_committed_cost_current/reference; matched_shared_cost_current/reference; matched_unclassified_operating_cost_current/reference; reported_vs_matched_amount_gap_difference_signed; matched_profitability_coverage_current; matched_profitability_coverage_reference; matched_profitability_coverage_basis; structural_scope_change; scope_item_status |

### 12.5. Kolejność wykonania modułu FIN-02

| Krok | Operacja |
| --- | --- |
| 1 | ustal profitability_scope, profitability_layer, current i reference |
| 2 | wykonaj FIN02-VAL i ustal moduły dostępne / zablokowane |
| 3 | uzgodnij net_revenue oraz operating cost z FIN-01 |
| 4 | odtwórz klasy PORT: variable / committed / shared; unclassified pozostaw jawny |
| 5 | oblicz amount i rate dla wybranej warstwy; revenue≤0 blokuje rate |
| 6 | wyznacz signed i adverse amount/rate gaps |
| 7 | przypisz profitability_condition na podstawie znaków, bez progu |
| 8 | zbuduj result bridge tylko ze składników należących do warstwy |
| 9 | zbuduj margin bridge tylko z odpowiednich cost loads |
| 10 | sprawdź oba reconciliation gaps; bez balancing item |
| 11 | oddziel adverse shares od compensating effects |
| 12 | kontroluj matched scope, structural changes, accounting comparability i one-off |
| 13 | dołącz explanatory_evidence z PORT/HR/CAP/PROC bez dodawania do bridge |
| 14 | zapisz FINDINGS, PRI/CONF payload i next_tests z validation_notes |

## 13. Statusy i komunikat zarządczy

| Status | Znaczenie |
| --- | --- |
| NO_ADVERSE_SIGNAL | brak potwierdzonego niekorzystnego zjawiska |
| ADVERSE_SIGNAL | niekorzystna zmiana bez rozstrzygnięcia trwałości/przyczyny |
| INCIDENT | zdarzenie jednorazowe / pojedynczy okres |
| DETERIORATING | porównywalne horyzonty potwierdzają pogorszenie |
| STABLE | brak trwałego kierunku po uwzględnieniu kontekstu |
| IMPROVING | potwierdzona poprawa |
| TEST_PARTIAL | część warstw lub scope jest obliczalna |
| TEST_BLOCKED | brak odpowiedzialnej podstawy dla zależnej diagnozy |

profitability_condition jest osobnym technicznym opisem sytuacji amount/rate. FIN-02 nie tworzy lokalnych statusów MEDIUM/HIGH/CRITICAL.

> **WZORZEC KOMUNIKATU [STATUS] RENTOWNOŚĆ W badanym okresie [profitability_layer] wyniosła [amount_current], wobec [amount_reference] w okresie odniesienia. Stopa rentowności zmieniła się z [rate_reference] do [rate_current], co oznacza [profitability_condition]. Most wyniku wskazuje, że niekorzystną zmianę tworzą przede wszystkim [result bridge components], natomiast w moście marży największe pogorszenie dotyczy [cost load components]. Czynniki kompensujące: [compensating effects]. Dane z innych testów wskazują jako możliwe wyjaśnienia [explanatory evidence]. Most jest rachunkowym rozliczeniem zmiany, a nie automatycznym dowodem przyczyny. Dalsza weryfikacja: [next_tests].**

> **NIE GENERUJ AUTOMATYCZNIE „firma traci X”; „można odzyskać X”; „winny jest koszt pracy”; „należy podnieść ceny”; „należy ciąć koszty”; „należy zamknąć produkt”.**

## 14. Scenariusze testowe FIN02-T01–T13

| Id | Scenariusz | Dane | Oczekiwane |
| --- | --- | --- | --- |
| FIN02-T01 | stabilny wynik i marża | Revenue i koszty proporcjonalne. | profitability_amount_direction=stable; profitability_rate_direction=stable; improving_or_stable_profitability; NO_ADVERSE_SIGNAL. |
| FIN02-T02 | wynik i marża pogarszają się | Amount↓; rate↓. | amount_direction=deteriorating; rate_direction=deteriorating; combined_deterioration. |
| FIN02-T03 | wynik rośnie, marża spada | Revenue silnie↑; wynik nominalny↑; rate↓. | amount_direction=improving; rate_direction=deteriorating; growth_masking_margin_erosion. |
| FIN02-T04 | wynik spada, marża poprawia się | Skala↓; koszty maleją proporcjonalnie bardziej. | amount_direction=deteriorating; rate_direction=improving; amount_deterioration_without_margin_erosion; scale_contraction_signal=true; mechanizm pozostaje hipotezą. |
| FIN02-T05 | wynik spada przy stabilnej marży | Revenue i koszty spadają proporcjonalnie. | amount_direction=deteriorating; rate_direction=stable; amount_deterioration_without_margin_erosion; scale_contraction_signal=true; brak erozji rate. |
| FIN02-T06 | variable cost load rośnie | Revenue stabilny; variable cost↑. | margin bridge: variable cost load adverse. |
| FIN02-T07 | committed load rośnie przez koszt | Revenue stabilny; committed cost↑. | cost amount↑ i load↑. |
| FIN02-T08 | committed load rośnie bez wzrostu kosztu | Committed stabilny; revenue↓. | cost amount stable; load worsens; bez „koszt wzrósł”. |
| FIN02-T09 | shared load rośnie przy spadku skali | Shared stabilny; revenue↓. | revenue_contraction driver; shared amount stable. |
| FIN02-T10 | kompensacja składników | Variable load↑; shared load↓. | signed bridge + adverse i compensating osobno. |
| FIN02-T11 | reclassification bez total change | Committed→shared; operating cost/result bez zmiany. | bridge total=0; reclassification flag; bez overall erosion. |
| FIN02-T12 | koszt unclassified | Część operating cost bez odpowiedzialnej klasyfikacji. | jawny component; coverage↓; bez sztucznej alokacji. |
| FIN02-T13 | revenue = 0 | Koszty istnieją; revenue=0. | rate/load null; amount możliwy; TEST_PARTIAL. |

## 15. Scenariusze testowe FIN02-T14–T29

| Id | Scenariusz | Dane | Oczekiwane |
| --- | --- | --- | --- |
| FIN02-T14 | revenue < 0 przez korekty | Ujemny net_revenue. | rate null; brak fałszywej marży procentowej. |
| FIN02-T15 | jednorazowy koszt | Reported result↓; oneoff_flag. | actual pokazany; brak auto-usunięcia. |
| FIN02-T16 | adjusted view ze źródłem | Udokumentowana korekta. | actual i adjusted obok; actual nie zastąpiony. |
| FIN02-T17 | pogorszenie miksu PORT | PORT: Mix_effect_rate<0. | portfolio_mix_evidence=true; mix nie trafia do bridge. |
| FIN02-T18 | wzrost labor rate | HR-01 potwierdza rate signal. | labor_rate_evidence; bez pełnej atrybucji erozji. |
| FIN02-T19 | spadek produktywności | HR-01 potwierdza productivity signal. | labor_productivity_evidence; hipoteza. |
| FIN02-T20 | niewykorzystanie capacity | CAP-01: U↓; committed stable; revenue↓. | hipoteza gorszej absorpcji; nie causal proof. |
| FIN02-T21 | zależność od extra capacity | CAP-02: regularna extra dependency; koszt↑. | extra_capacity_dependency_evidence. |
| FIN02-T22 | proces się pogarsza | PROC: rework/delay; koszt↑. | process_delay_evidence; 0 automatycznej wyceny procesu. |
| FIN02-T23 | nowa jednostka | Current ma unit C bez reference. | C poza matched bridge; bridge_scope=matched_scope; coverage current/reference jawne według wspólnej podstawy; structural_scope_change. |
| FIN02-T24 | jednostka wycofana | Reference ma unit B, current nie. | B poza matched bridge; structural_scope_change; bridge_scope=matched_scope; bez fałszywej matched erosion. |
| FIN02-T25 | reconciliation failure | FIN-01 revenue/cost ≠ FIN-02 bez wyjaśnienia. | validation_required; TEST_PARTIAL/BLOCKED wg skali. |
| FIN02-T26 | stabilny wynik kwotowy, erozja marży | Reference: revenue=100; rate=10%; amount=10. Current: revenue=125; rate=8%; amount=10. | profitability_amount_direction=stable; profitability_rate_direction=deteriorating; profitability_condition=stable_amount_margin_erosion; rate erosion widoczna; brak NO_ADVERSE_SIGNAL. |
| FIN02-T27 | nowa jednostka a matched bridge | Reference A amount=100. Current A=100 + nowa C=20. | reported current=120; full amount gap=−20; matched A 100/100; matched gap=0; bridge_scope=matched_scope; matched bridge=0; reconciliation=0; C poza matched; full-vs-matched różnica osobno; brak fałszywego reconciliation failure. |
| FIN02-T28 | asymetryczna podstawa coverage | Current coverage dostępne po revenue; reference tylko po scope_count. | brak porównywalnych coverage; validation_required; coverage dla porównania=null do czasu wspólnej matched_profitability_coverage_basis. |
| FIN02-T29 | matched margin bridge z nową jednostką | Reference: A – variable cost load 40%. Current: A – variable cost load 40%; nowa jednostka C – variable cost load 80%. bridge_scope=matched_scope. | matched margin bridge dla A=0; adverse_margin_erosion_share=null / brak adverse effect; C nie wpływa na udział matched margin erosion; full-scope wynik może być pokazany osobno; brak mieszania full i matched. |

> **WARUNEK PASS Scenariusz przechodzi dopiero wtedy, gdy zgadzają się obliczenia, bridge reconciliation, null/not_computable, status, profitability_condition, coverage, evidence, FINDINGS, next_tests oraz zakazy interpretacyjne. Sama poprawna marża nie wystarcza.**

## 16. Kryteria odbioru implementacji FIN02-ACC-01–76

| Id | Kryterium | Id | Kryterium |
| --- | --- | --- | --- |
| FIN02-ACC-01 | przyjmuje FIN-01 semantics revenue/cost – PASS | FIN02-ACC-02 | zachowuje PORT-01 cost layers bez zmiany – PASS |
| FIN02-ACC-03 | obsługuje profitability_scope – PASS | FIN02-ACC-04 | obsługuje profitability_layer – PASS |
| FIN02-ACC-05 | rozróżnia amount i rate – PASS | FIN02-ACC-06 | wyznacza profitability_condition bez progu – PASS |
| FIN02-ACC-07 | liczy CM1 zgodnie z PORT – PASS | FIN02-ACC-08 | liczy SM zgodnie z PORT – PASS |
| FIN02-ACC-09 | liczy operating_result_amount z jawnym scope – PASS | FIN02-ACC-10 | liczy operating_margin_rate tylko przy revenue>0 – PASS |
| FIN02-ACC-11 | nie utożsamia operating result z EBITDA/net/cash – PASS | FIN02-ACC-12 | rozróżnia operating_cost_basis i scope – PASS |
| FIN02-ACC-13 | buduje operating_cost_total z czterech składników – PASS | FIN02-ACC-14 | utrzymuje unclassified_operating_cost jawnie – PASS |
| FIN02-ACC-15 | nie liczy allocated_shared_cost drugi raz – PASS | FIN02-ACC-16 | wymaga allocation_quality dla unit operating result – PASS |
| FIN02-ACC-17 | nie blokuje CM1/SM przy braku shared allocation – PASS | FIN02-ACC-18 | zapisuje amount current/reference – PASS |
| FIN02-ACC-19 | zapisuje rate current/reference – PASS | FIN02-ACC-20 | liczy signed amount gap – PASS |
| FIN02-ACC-21 | liczy adverse amount gap – PASS | FIN02-ACC-22 | liczy signed rate gap – PASS |
| FIN02-ACC-23 | liczy adverse rate gap – PASS | FIN02-ACC-24 | nie miesza pp i procentów – PASS |
| FIN02-ACC-25 | buduje result bridge dla CM1 – PASS | FIN02-ACC-26 | buduje result bridge dla SEGMENT_MARGIN – PASS |
| FIN02-ACC-27 | buduje result bridge dla OPERATING_RESULT – PASS | FIN02-ACC-28 | result bridge używa poprawnego znaku revenue effect – PASS |
| FIN02-ACC-29 | result bridge używa poprawnych znaków cost effects – PASS | FIN02-ACC-30 | uzgadnia result_bridge_total_signed z amount gap – PASS |
| FIN02-ACC-31 | raportuje result_bridge_reconciliation_gap – PASS | FIN02-ACC-32 | nie tworzy balancing item bez źródła – PASS |
| FIN02-ACC-33 | liczy adverse_result_effect_share tylko z dodatnich – PASS | FIN02-ACC-34 | zachowuje compensating_result_effects – PASS |
| FIN02-ACC-35 | liczy variable_cost_load – PASS | FIN02-ACC-36 | liczy committed_cost_load – PASS |
| FIN02-ACC-37 | liczy shared_cost_load – PASS | FIN02-ACC-38 | liczy unclassified_cost_load – PASS |

FIN02-ACC-39–76 – ciąg dalszy

| Id | Kryterium | Id | Kryterium |
| --- | --- | --- | --- |
| FIN02-ACC-39 | uzgadnia operating margin identity – PASS | FIN02-ACC-40 | liczy cost_load_gap_signed – PASS |
| FIN02-ACC-41 | uzgadnia margin bridge z rate gap – PASS | FIN02-ACC-42 | raportuje margin_bridge_reconciliation_gap – PASS |
| FIN02-ACC-43 | liczy adverse_bridge_cost_load_gap i adverse_margin_erosion_share wyłącznie z bridge_cost_load_gaps tego samego bridge_scope/layer/current-reference – PASS | FIN02-ACC-44 | zachowuje compensating_margin_effects wyłącznie z ujemnych bridge_cost_load_gap_signed tego samego bridge_scope – PASS |
| FIN02-ACC-45 | rozróżnia cost amount change od cost load gap – PASS | FIN02-ACC-46 | rozpoznaje revenue_contraction bez „koszt wzrósł” – PASS |
| FIN02-ACC-47 | cost_load_driver pozostaje typologią bez PVM – PASS | FIN02-ACC-48 | explanatory_evidence ma true/false/null – PASS |
| FIN02-ACC-49 | nie dodaje explanatory evidence do bridges – PASS | FIN02-ACC-50 | nie liczy mix_effect drugi raz – PASS |
| FIN02-ACC-51 | HR evidence nie jest automatyczną przyczyną – PASS | FIN02-ACC-52 | CAP evidence nie jest automatyczną przyczyną – PASS |
| FIN02-ACC-53 | PROC time nie jest automatycznie kosztem – PASS | FIN02-ACC-54 | FIN-03 pozostaje wyłącznie next_test – PASS |
| FIN02-ACC-55 | obsługuje scope_item_status matched/new/discontinued/changed – PASS | FIN02-ACC-56 | pokazuje matched coverage current osobno – PASS |
| FIN02-ACC-57 | pokazuje matched coverage reference osobno – PASS | FIN02-ACC-58 | kontroluje structural_scope_change – PASS |
| FIN02-ACC-59 | kontroluje accounting_basis_comparability – PASS | FIN02-ACC-60 | kontroluje revenue_recognition_comparability – PASS |
| FIN02-ACC-61 | kontroluje cost_classification_comparability – PASS | FIN02-ACC-62 | kontroluje reclassification bez fałszywej erozji – PASS |
| FIN02-ACC-63 | one-off pozostaje w reported – PASS | FIN02-ACC-64 | adjusted view nie zastępuje reported – PASS |
| FIN02-ACC-65 | agreguje 3M/6M/12M na sumach – PASS | FIN02-ACC-66 | wykonuje FIN-01 i PORT reconciliation – PASS |
| FIN02-ACC-67 | zapisuje FINDINGS/PRI/CONF/next_tests bez score – PASS | FIN02-ACC-68 | przechodzi FIN02-T01–T29 i nie generuje automatycznych decyzji – PASS |
| FIN02-ACC-69 | wyznacza profitability_amount_direction i profitability_rate_direction z signed gap i technicznej tolerancji – PASS | FIN02-ACC-70 | obsługuje stable_amount_margin_erosion i amount_deterioration_without_margin_erosion bez causal label – PASS |
| FIN02-ACC-71 | wybiera bridge_scope full_scope/matched_scope zgodnie ze structural comparability – PASS | FIN02-ACC-72 | buduje komplet matched_* inputs i matched amount/rate gaps dla jednego matched_profitability_scope – PASS |
| FIN02-ACC-73 | uzgadnia result i margin bridge z gapem tego samego bridge_scope – PASS | FIN02-ACC-74 | pokazuje reported_vs_matched_amount_gap_difference_signed bez balancing item – PASS |
| FIN02-ACC-75 | wymaga wspólnej matched_profitability_coverage_basis current/reference – PASS | FIN02-ACC-76 | przechodzi FIN02-T01–T29, w tym matched margin bridge z FIN02-T29 – PASS |

## 17. Definition of Done FIN02-DOD-01–72

| Id | Zakres / status | Id | Zakres / status |
| --- | --- | --- | --- |
| FIN02-DOD-01 | cel – PASS | FIN02-DOD-02 | granica FIN-01 – PASS |
| FIN02-DOD-03 | granica PORT-01 – PASS | FIN02-DOD-04 | profitability_scope – PASS |
| FIN02-DOD-05 | profitability_layer – PASS | FIN02-DOD-06 | net_revenue – PASS |
| FIN02-DOD-07 | CM1 – PASS | FIN02-DOD-08 | SM – PASS |
| FIN02-DOD-09 | operating_result_amount – PASS | FIN02-DOD-10 | operating_margin_rate – PASS |
| FIN02-DOD-11 | operating_cost_total – PASS | FIN02-DOD-12 | operating_cost_basis/scope – PASS |
| FIN02-DOD-13 | shared cost – PASS | FIN02-DOD-14 | allocated shared cost gate – PASS |
| FIN02-DOD-15 | unclassified cost – PASS | FIN02-DOD-16 | amount current/reference – PASS |
| FIN02-DOD-17 | rate current/reference – PASS | FIN02-DOD-18 | signed amount gap – PASS |
| FIN02-DOD-19 | adverse amount gap – PASS | FIN02-DOD-20 | signed rate gap – PASS |
| FIN02-DOD-21 | adverse rate gap – PASS | FIN02-DOD-22 | profitability_condition – PASS |
| FIN02-DOD-23 | result bridge CM1 – PASS | FIN02-DOD-24 | result bridge SM – PASS |
| FIN02-DOD-25 | result bridge operating – PASS | FIN02-DOD-26 | result bridge components – PASS |
| FIN02-DOD-27 | result bridge reconciliation – PASS | FIN02-DOD-28 | adverse result shares – PASS |
| FIN02-DOD-29 | compensating result effects – PASS | FIN02-DOD-30 | margin bridge – PASS |
| FIN02-DOD-31 | cost loads – PASS | FIN02-DOD-32 | cost load gaps – PASS |
| FIN02-DOD-33 | margin reconciliation – PASS | FIN02-DOD-34 | bridge-scoped adverse margin effects i adverse_margin_erosion_share – PASS |
| FIN02-DOD-35 | bridge-scoped compensating_margin_effects – PASS | FIN02-DOD-36 | cost amount vs cost load – PASS |
| FIN02-DOD-37 | cost_load_driver – PASS | FIN02-DOD-38 | explanatory_evidence – PASS |
| FIN02-DOD-39 | PORT evidence – PASS | FIN02-DOD-40 | HR evidence – PASS |
| FIN02-DOD-41 | CAP-01 evidence – PASS | FIN02-DOD-42 | CAP-02 evidence – PASS |
| FIN02-DOD-43 | PROC evidence – PASS | FIN02-DOD-44 | FIN-03 relation – PASS |
| FIN02-DOD-45 | revenue scale – PASS | FIN02-DOD-46 | comparable volume boundary – PASS |
| FIN02-DOD-47 | matched scope – PASS | FIN02-DOD-48 | coverage current/reference – PASS |
| FIN02-DOD-49 | scope item status – PASS | FIN02-DOD-50 | structural changes – PASS |
| FIN02-DOD-51 | accounting comparability – PASS | FIN02-DOD-52 | revenue recognition – PASS |
| FIN02-DOD-53 | cost classification – PASS | FIN02-DOD-54 | reclassification – PASS |
| FIN02-DOD-55 | one-off – PASS | FIN02-DOD-56 | adjusted view – PASS |
| FIN02-DOD-57 | zero/negative revenue – PASS | FIN02-DOD-58 | horizons/agregacja – PASS |
| FIN02-DOD-59 | reference – PASS | FIN02-DOD-60 | coverage data – PASS |
| FIN02-DOD-61 | FIN-01 reconciliation – PASS | FIN02-DOD-62 | PORT reconciliation – PASS |
| FIN02-DOD-63 | dekompozycja – PASS | FIN02-DOD-64 | VAL/scenarios/ACC/FINDINGS/next_tests – PASS |
| FIN02-DOD-65 | amount/rate directions + comparison_tolerance_basis – PASS | FIN02-DOD-66 | stable profitability_condition matrix – PASS |
| FIN02-DOD-67 | bridge_scope full vs matched – PASS | FIN02-DOD-68 | matched profitability input/output contract – PASS |
| FIN02-DOD-69 | same-scope result/margin bridge reconciliation – PASS | FIN02-DOD-70 | reported vs matched difference without balancing item – PASS |
| FIN02-DOD-71 | matched coverage basis current/reference – PASS | FIN02-DOD-72 | FIN02-T01–T29 + bridge-scoped margin effects + VAL/ACC/FINDINGS/PRI updates – PASS |

## 18. Test końcowy QFIN02-01–88

| Id | Kontrola | Id | Kontrola |
| --- | --- | --- | --- |
| QFIN02-01 | FIN-02 jest uniwersalny branżowo – PASS | QFIN02-02 | FIN-02 ≠ FIN-01 – PASS |
| QFIN02-03 | FIN-02 ≠ PORT-01 – PASS | QFIN02-04 | wynik kwotowy ≠ stopa rentowności – PASS |
| QFIN02-05 | amount deterioration może istnieć bez rate erosion – PASS | QFIN02-06 | rate erosion może istnieć przy rosnącym amount – PASS |
| QFIN02-07 | profitability_condition działa bez progu – PASS | QFIN02-08 | CM1 zachowuje PORT-01 – PASS |
| QFIN02-09 | SM zachowuje PORT-01 – PASS | QFIN02-10 | operating result ma jawny scope – PASS |
| QFIN02-11 | operating result ≠ EBITDA/net/cash – PASS | QFIN02-12 | shared cost nie jest liczony dwa razy – PASS |
| QFIN02-13 | allocated_shared_cost nie jest czwartą pulą – PASS | QFIN02-14 | unit full result wymaga allocation quality – PASS |
| QFIN02-15 | unclassified cost jest jawny – PASS | QFIN02-16 | rate przy revenue≤0 jest null – PASS |
| QFIN02-17 | amount może pozostać przy revenue≤0 – PASS | QFIN02-18 | result bridge jest dokładnie uzgadnialny – PASS |
| QFIN02-19 | margin bridge jest dokładnie uzgadnialny – PASS | QFIN02-20 | brak balancing item bez źródła – PASS |
| QFIN02-21 | signed amount gap ≠ adverse amount gap – PASS | QFIN02-22 | signed rate gap ≠ adverse rate gap – PASS |
| QFIN02-23 | adverse result shares używają tylko dodatnich składników – PASS | QFIN02-24 | adverse margin shares używają wyłącznie dodatnich adverse_bridge_cost_load_gap z tego samego bridge_scope/layer/current-reference – PASS |
| QFIN02-25 | compensating result effects są zachowane – PASS | QFIN02-26 | compensating margin effects używają wyłącznie ujemnych bridge_cost_load_gap_signed tego samego bridge_scope – PASS |
| QFIN02-27 | cost amount ≠ cost load – PASS | QFIN02-28 | stabilny koszt przy revenue↓ może zwiększyć load – PASS |
| QFIN02-29 | nie nazywa się tego automatycznie wzrostem kosztu – PASS | QFIN02-30 | cost_load_driver nie jest arbitralnym PVM – PASS |
| QFIN02-31 | explanatory evidence nie wchodzi do bridge – PASS | QFIN02-32 | mix effect nie jest podwójnie liczony – PASS |
| QFIN02-33 | HR evidence nie jest automatyczną przyczyną – PASS | QFIN02-34 | CAP-01 evidence nie jest automatyczną przyczyną – PASS |
| QFIN02-35 | CAP-02 evidence nie jest automatyczną przyczyną – PASS | QFIN02-36 | process evidence nie jest automatycznie kosztem – PASS |
| QFIN02-37 | process time nie jest automatycznie wyceniany – PASS | QFIN02-38 | FIN-03 pozostaje osobnym testem – PASS |
| QFIN02-39 | matched scope jest jawny – PASS | QFIN02-40 | matched coverage current jest osobne – PASS |
| QFIN02-41 | matched coverage reference jest osobne – PASS | QFIN02-42 | new unit jest oddzielony – PASS |
| QFIN02-43 | discontinued unit jest oddzielony – PASS | QFIN02-44 | materially changed scope jest oddzielony – PASS |

QFIN02-45–88 – ciąg dalszy

| Id | Kontrola | Id | Kontrola |
| --- | --- | --- | --- |
| QFIN02-45 | structural change jest kontrolowany – PASS | QFIN02-46 | accounting basis jest porównywalny – PASS |
| QFIN02-47 | revenue recognition jest porównywalne – PASS | QFIN02-48 | cost classification jest porównywalna – PASS |
| QFIN02-49 | reclassification jest kontrolowana – PASS | QFIN02-50 | reclassification bez total change nie tworzy overall erosion – PASS |
| QFIN02-51 | one-off nie znika automatycznie – PASS | QFIN02-52 | adjusted view nie zastępuje reported – PASS |
| QFIN02-53 | adjustment_basis jest jawny – PASS | QFIN02-54 | horyzonty są agregowane na sumach – PASS |
| QFIN02-55 | marże nie są średnią miesięcznych procentów – PASS | QFIN02-56 | referencja jest źródłowa – PASS |
| QFIN02-57 | brak arbitralnych benchmarków marży – PASS | QFIN02-58 | brak arbitralnych progów erosion – PASS |
| QFIN02-59 | FIN-01 revenue reconciliation istnieje – PASS | QFIN02-60 | FIN-01 cost reconciliation istnieje – PASS |
| QFIN02-61 | PORT reconciliation istnieje warunkowo – PASS | QFIN02-62 | coverage jest jawne – PASS |
| QFIN02-63 | brak danych zasila CONF – PASS | QFIN02-64 | hipoteza ≠ przyczyna – PASS |
| QFIN02-65 | next_tests istnieją – PASS | QFIN02-66 | brak automatycznej rekomendacji cięcia kosztów – PASS |
| QFIN02-67 | brak automatycznej rekomendacji cenowej – PASS | QFIN02-68 | brak automatycznego zamknięcia produktu – PASS |
| QFIN02-69 | brak automatycznej redukcji zatrudnienia – PASS | QFIN02-70 | brak automatycznej wyceny potencjału – PASS |
| QFIN02-71 | PRI pozostaje DO OPRACOWANIA – PASS | QFIN02-72 | CONF pozostaje DO OPRACOWANIA – PASS |
| QFIN02-73 | zamrożone testy pozostają niezmienione – PASS | QFIN02-74 | istnieje 29 scenariuszy – PASS |
| QFIN02-75 | VAL/ACC/DOD kompletne – PASS | QFIN02-76 | 0 danych SPZOZ/pacjentów; 0 FIN-03/FIN-04 – PASS |
| QFIN02-77 | profitability_amount_direction ma pełne deteriorating/stable/improving/unresolved – PASS | QFIN02-78 | profitability_rate_direction ma pełne deteriorating/stable/improving/unresolved – PASS |
| QFIN02-79 | stable amount + deteriorating rate daje stable_amount_margin_erosion – PASS | QFIN02-80 | amount deterioration bez rate erosion nie jest automatycznie nazywane scale contraction – PASS |
| QFIN02-81 | scale_contraction_signal jest osobnym faktem revenue_change_signed<0 – PASS | QFIN02-82 | bridge_scope rozdziela full_scope i matched_scope – PASS |
| QFIN02-83 | matched bridge używa wyłącznie matched_* inputs jednego scope – PASS | QFIN02-84 | matched result bridge nie jest porównywany z full-scope amount gap – PASS |
| QFIN02-85 | matched margin bridge i jego adverse/compensating effects nie używają full-scope cost_load_gap_signed – PASS | QFIN02-86 | reported_vs_matched_amount_gap_difference_signed nie jest balancing item ani causal attribution – PASS |
| QFIN02-87 | matched coverage current/reference używa wspólnej matched_profitability_coverage_basis albo pozostaje null – PASS | QFIN02-88 | FIN02-T26–T29 oraz FIN02-T01–T29 przechodzą regresję – PASS |

### 18.1. Otwarte kwestie wspólne – poza FIN-02

| Kwestia | Status / wpływ |
| --- | --- |
| globalna podstawa kosztowa | FIN-02 wymaga jawnego operating_cost_basis, lecz nie buduje standardu dla całego X-Ray |
| globalny standard work_content | FIN-02 korzysta z evidence HR/CAP/PROC, nie zamyka wspólnego kontraktu |
| globalna klasyfikacja korekt jednorazowych | oneoff_basis jest lokalnie jawny; globalny katalog pozostaje otwarty |
| globalna orkiestracja next_tests | FIN-02 przekazuje rekomendacje, nie uruchamia pełnej sieci |
| ZOP-PRI-01 | payload gotowy; wzór i progi poza FIN-02 |
| ZOP-CONF-01 | payload jakości gotowy; score poza FIN-02 |

> **STATUS KOŃCOWY FIN-02 ZAMKNIĘTY METODOLOGICZNIE DO IMPLEMENTACJI. ZOP-PRI-01 – DO OPRACOWANIA. ZOP-CONF-01 – DO OPRACOWANIA.**

0 podwójnego liczenia shared cost; 0 sztucznego balancing item; 0 podwójnego liczenia explanatory evidence; 0 arbitralnych progów rentowności; 0 automatycznych decyzji kosztowych/cenowych/portfelowych/kadrowych; 0 automatycznej wyceny „potencjału”; 0 danych SPZOZ; 0 danych pacjentów; 0 rozpoczętego FIN-03; 0 rozpoczętego FIN-04.
