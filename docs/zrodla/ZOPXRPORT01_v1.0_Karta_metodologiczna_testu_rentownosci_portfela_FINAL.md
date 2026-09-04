ZOPTYMALIZOWANI – X-RAY

# PORT-01

# Rentowność portfela

Karta metodologiczna i specyfikacja implementacyjna

> **STATUS PORT-01 ZAMKNIĘTY METODOLOGICZNIE DO IMPLEMENTACJI**

| Pole | Wartość |
| --- | --- |
| Identyfikator | ZOP-XR-PORT-01 |
| Wersja / data | v1.0 / 2 września 2026 |
| Rola | czwarty pełny test diagnostyczny; wzorzec rodziny testów portfelowych |
| Odbiorcy | zarządzający, analityk, Aleksander – implementacja |
| Zależności | ZOP-PRI-01 i ZOP-CONF-01 – DO OPRACOWANIA |

Dokument metodologiczny, kontrakt implementacyjny i wzorzec rozwoju testów portfelowych. Nie jest narzędziem zamykania produktów, pełnym rachunkiem kosztów, aplikacją, panelem ani warstwą AI.

## 1. Rola, cel i granice PORT-01

> **PYTANIE DIAGNOSTYCZNE Które elementy portfela tworzą dodatnią wartość ekonomiczną, które ją pogarszają, jak zmienia się struktura portfela oraz czy zmiana miksu poprawia czy pogarsza ekonomikę całej organizacji?**

### 1.1. Łańcuch diagnostyczny

| Etap | Wynik | Granica |
| --- | --- | --- |
| Portfel | jednoznaczny portfolio_item | bez sztucznego rozbijania pakietu |
| Przychód | gross_revenue → net_revenue | jawna revenue_attribution_basis |
| Koszty | zmienne → utrzymujące → wspólne | bez arbitralnej alokacji |
| Ekonomika | CM1 → SM → warunkowo Full_result | CM1 ≠ Full_result |
| Czas i miks | trend, udziały, mix_effect, margin_effect | tylko portfele porównywalne |
| Capacity | CM1/SM na zgodną capacity_unit | sygnał, nie decyzja |
| Diagnoza | hipotezy i next_tests | hipoteza ≠ przyczyna |

### 1.2. Granice testu

PORT-01 nie podejmuje automatycznej decyzji o zamknięciu elementu, nie tworzy rankingu „dobrych” i „złych” usług, pełnego rachunku kosztów, arbitralnych kluczy kosztów wspólnych, prognozy popytu, strategii całego przedsiębiorstwa ani systemu cenowego.

> **ZASADA NADRZĘDNA Wynik po alokacji kosztów wspólnych nie może być jedyną miarą rentowności elementu portfela.**

## 2. Jednostka analizy i kontrakt danych

### 2.1. portfolio_item

Podstawową jednostką analizy jest portfolio_item: produkt, usługa, pakiet, zakres świadczeń, kontrakt, typ zlecenia, linia biznesowa albo inna jednoznacznie zdefiniowana jednostka działalności. Bazowe product z ACTIVITY może pełnić tę funkcję.

| Pole | Znaczenie implementacyjne |
| --- | --- |
| portfolio_item | stabilny identyfikator elementu analizowanego |
| portfolio_item_type | opcjonalna klasa elementu |
| portfolio_group | opcjonalna grupa do dekompozycji |
| portfolio_item_status | aktywny / nowy / wycofany / zmieniony według danych |

### 2.2. Tabele bazowe – bez zmiany ZOP-TECH-01

| Tabela | Pola bazowe | Rola PORT-01 |
| --- | --- | --- |
| ACTIVITY | date, unit, product, volume, revenue | element, aktywność i przychód |
| COST | date, unit, category, amount | źródło kosztu i uzgodnienie |
| RESOURCE – opcjonalna | date, unit, resource, available, used, cost | capacity przypisana do elementu |
| PLAN – opcjonalna | date, unit, metric, target | plan jako możliwa referencja |

### 2.3. Rozszerzenia

portfolio_item; portfolio_item_type; portfolio_group; portfolio_item_status; gross_revenue; net_revenue; revenue_basis; revenue_attribution_basis; direct_variable_cost; direct_committed_cost; shared_cost; allocated_shared_cost; allocation_basis; allocation_quality; cost_attribution_scope; cost_avoidability; decision_horizon; activity_unit; comparable_volume; weighted_volume; volume_comparability; matched_revenue_share_current; matched_revenue_share_reference; capacity_used_attributable; capacity_unit; capacity_constraint_status; portfolio_context_flags.

## 3. Przychód i trzy ekonomiczne pule kosztu

### 3.1. Przychód netto

| Pole | Reguła |
| --- | --- |
| gross_revenue | przychód przed poprawnie rozpoznanymi obniżeniami |
| net_revenue | wartość po rabatach, zwrotach, korektach, bonifikatach i innych obniżeniach |
| revenue_basis | źródło i znaczenie wartości przychodowej |
| revenue_attribution_basis | udokumentowane uzasadnienie przypisania do portfolio_item |

> **PAKIET Jeżeli przychód obejmuje kilka produktów bez wiarygodnej metody podziału, analizuj pakiet jako osobny portfolio_item albo oznacz TEST_PARTIAL. Nie odtwarzaj net_revenue arbitralnie.**

### 3.2. Trzy ekonomiczne pule kosztu

| Pula | Znaczenie | Rola |
| --- | --- | --- |
| direct_variable_cost | zmienia się wraz z realizacją i jest bezpośredni | podstawa CM1 |
| direct_committed_cost | utrzymuje element, lecz nie każdą jednostkę | podstawa SM na właściwym poziomie |
| shared_cost | wspólny wielu elementom | pula organizacyjna / wspólna |

### 3.3. Alokacja pochodna, hierarchia i możliwość uniknięcia

allocated_shared_cost nie jest czwartą addytywną klasą kosztu. Jest pochodnym przypisaniem części shared_cost według udokumentowanego allocation_basis, używanym wyłącznie do warunkowego Full_result. W uzgodnieniu kosztu nie wolno ponownie dodawać allocated_shared_cost do shared_cost.

Kontrola puli: allocated_shared_cost_total ≤ shared_cost_eligible_for_allocation z tolerancją techniczną. Jeżeli alokacja obejmuje całą kwalifikowaną pulę, Σallocated_shared_cost = shared_cost_eligible_for_allocation w granicach tolerancji. PORT-01 nie wymusza alokacji całego shared_cost.

cost_attribution_scope przyjmuje: organization, unit, portfolio_group albo portfolio_item. Koszt przypisany bezpośrednio wyższemu poziomowi nie przechodzi automatycznie niżej. SM_item = CM1_item − direct_committed_cost_item. SM_group = ΣSM_item − direct_committed_cost_group. Podział kosztu grupy na produkty wymaga jawnego allocation_basis i nie jest już bezpośrednim kosztem produktu.

cost_avoidability odpowiada wyłącznie na pytanie, czy koszt może zniknąć w decision_horizon: avoidable_short_term, avoidable_medium_term, not_avoidable_within_horizon albo unknown. Atrybucję opisują pule kosztu; wartości variable i shared nie są wartościami pola cost_avoidability. Gdy warstwa SM nie ma wiarygodnej podstawy, pozostaje null lub TEST_PARTIAL.

## 4. Walidacja danych PORT01-VAL-01–20

| Id | Kontrola | Reakcja |
| --- | --- | --- |
| PORT01-VAL-01 | istnieje portfolio_item | PASS / WARNING / CRITICAL |
| PORT01-VAL-02 | istnieje revenue | PASS / WARNING / CRITICAL |
| PORT01-VAL-03 | revenue przypisano do właściwego elementu | PASS / WARNING / CRITICAL |
| PORT01-VAL-04 | revenue_basis jest spójna | PASS / WARNING / CRITICAL |
| PORT01-VAL-05 | direct_variable_cost istnieje albo jawnie brak podstawy | PASS / WARNING / CRITICAL |
| PORT01-VAL-06 | koszt nie jest podwójnie przypisany; shared_cost i allocated_shared_cost nie są sumowane addytywnie | PASS / WARNING / CRITICAL |
| PORT01-VAL-07 | direct_committed_cost ma jednoznaczny cost_attribution_scope | PASS / WARNING / CRITICAL |
| PORT01-VAL-08 | shared_cost nie został potraktowany jak direct cost | PASS / WARNING / CRITICAL |
| PORT01-VAL-09 | allocated_shared_cost ma allocation_basis i nie przekracza shared_cost_eligible_for_allocation | PASS / WARNING / CRITICAL |
| PORT01-VAL-10 | allocation_basis jest odtwarzalna; suma alokacji uzgadnia się z objętą pulą w tolerancji | PASS / WARNING / CRITICAL |
| PORT01-VAL-11 | product / portfolio_item jest spójny w czasie | PASS / WARNING / CRITICAL |
| PORT01-VAL-12 | okres kosztowy odpowiada przychodowemu | PASS / WARNING / CRITICAL |
| PORT01-VAL-13 | nie występują duplikaty | PASS / WARNING / CRITICAL |
| PORT01-VAL-14 | volume jest porównywalny | PASS / WARNING / CRITICAL |
| PORT01-VAL-15 | matched portfolio jest porównywalne, a matched_revenue_share w każdym okresie sumuje się do 1 | PASS / WARNING / CRITICAL |
| PORT01-VAL-16 | nie zaszła istotna zmiana definicji produktu | PASS / WARNING / CRITICAL |
| PORT01-VAL-17 | nie zaszła niewyjaśniona zmiana księgowania | PASS / WARNING / CRITICAL |
| PORT01-VAL-18 | przychody można uzgodnić z FIN-01 | PASS / WARNING / CRITICAL |
| PORT01-VAL-19 | koszty można uzgodnić z COST/FIN | PASS / WARNING / CRITICAL |
| PORT01-VAL-20 | istnieje odpowiednia referencja | PASS / WARNING / CRITICAL |

CRITICAL zatrzymuje moduł zależny; WARNING pozostawia wynik warunkowy i zasila validation_notes oraz ZOP-CONF-01. TEST_BLOCKED stosuje się, gdy nie istnieje odpowiedzialna podstawa diagnozy; TEST_PARTIAL, gdy część warstw pozostaje obliczalna.

## 5. Miary ekonomiczne

### 5.1. Marża kontrybucyjna I

CM1 = net_revenue − direct_variable_cost

Wartość pozostająca po pokryciu kosztów bezpośrednio zmiennych.

CM1R = CM1 / net_revenue

Stopa marży kontrybucyjnej I; przy net_revenue = 0 wynik null.

### 5.2. Wynik segmentowy

SM = CM1 − direct_committed_cost

Wartość po kosztach zmiennych i kosztach bezpośrednio utrzymujących element.

SMR = SM / net_revenue

Stopa wyniku segmentowego; SM nie jest wynikiem netto przedsiębiorstwa.

### 5.3. Pełny wynik po alokacji

Full_result = SM − allocated_shared_cost

Wyłącznie przy wiarygodnej, uzasadnionej, stabilnej i odtwarzalnej allocation_basis.

> **REGUŁA KRYTYCZNA Gdy allocation_basis jest niewystarczająca, Full_result = null albo warstwa otrzymuje TEST_PARTIAL. Nie tworzy się sztucznej alokacji dla kompletności tabeli.**

> **INTERPRETACJA CM1 > 0, SM > 0 i Full_result < 0 nie oznacza automatycznie, że zamknięcie elementu poprawi wynik. Najpierw trzeba ustalić, czy przypisany koszt wspólny rzeczywiście zniknie.**

## 6. Wolumen, horyzonty i referencja

### 6.1. Miary jednostkowe

| Miara | Wzór | Warunek |
| --- | --- | --- |
| unit_net_revenue | net_revenue / comparable_volume | porównywalna activity_unit |
| unit_variable_cost | direct_variable_cost / comparable_volume | porównywalna podstawa kosztu |
| unit_contribution | CM1 / comparable_volume | volume_comparability=true |

Jeżeli wolumen nie jest porównywalny, miary jednostkowe pozostają null. weighted_volume wolno stosować tylko z udokumentowanymi wagami. Revenue nie zastępuje wolumenu ani efektu.

### 6.2. Horyzonty

| Horyzont | Reguła |
| --- | --- |
| 1M | okres sygnałowy; bez automatycznej tezy o trwałości |
| 3M / 6M / 12M | sumuj wartości ekonomiczne w oknie, następnie licz wskaźniki na agregatach |
| 12M / r/r | porównaj z analogicznym, porównywalnym okresem |
| 24–36M | trend, sezonowość i punkt zmiany, jeżeli dane istnieją |

### 6.3. Kolejność referencji

1. historia tego samego portfolio_item; 2. wcześniejszy porównywalny okres; 3. plan; 4. porównywalny portfolio_item; 5. najlepszy własny okres; 6. benchmark zewnętrzny wyłącznie ze źródłem. Brak wiarygodnej referencji oznacza null dla luki, a nie wartość zastępczą.

## 7. Luka marży, uzgodnienie i pokrycie

### 7.1. Luka marży

Contribution_margin_rate_gap = CM1R_ref − CM1R_current

Dodatnia wartość oznacza pogorszenie stopy CM1 względem poprawnej referencji.

contribution_gap_amount_signed = net_revenue_current × (CM1R_ref − CM1R_current)

adverse_contribution_gap_amount = max(contribution_gap_amount_signed, 0); adverse_contribution_gap_share_i = adverse_contribution_gap_amount_i / Σadverse_contribution_gap_amount; przy sumie 0 → null. Ujemne wartości contribution_gap_amount_signed pozostają czynnikami kompensującymi. Luka nie jest automatycznie stratą, oszczędnością ani potencjałem do odzyskania.

### 7.2. Uzgodnienie z FIN-01

| Pole | Znaczenie |
| --- | --- |
| revenue_reconciliation_gap | różnica zakresu PORT-01 i porównywalnego przychodu FIN-01 |
| cost_reconciliation_gap | różnica kosztów PORT-01 i COST/FIN po wyłączeniu podwójnego liczenia alokacji |
| unmapped_revenue | przychód poprawnie nierozpisany na portfolio_item |
| unmapped_cost | koszt poprawnie nierozpisany na element portfela |

PORT-01 nie tworzy drugiej ekonomiki organizacji. W uzgodnieniu całkowitego kosztu źródłem jest shared_cost, nie shared_cost + allocated_shared_cost. Zero luki nie jest wymuszane, gdy pozycje poza zakresem są jawnie zidentyfikowane i uzasadnione.

### 7.3. Pokrycie portfela

| Miara | Definicja interpretacyjna |
| --- | --- |
| revenue_coverage | część rzeczywistego przychodu objęta wiarygodnym przypisaniem |
| cost_coverage | część odpowiednich kosztów objęta wiarygodnym przypisaniem |
| matched_portfolio_coverage | część porównywalnego portfela obecna w okresie current i reference |

> **BRAK PROGU PORT-01 raportuje pokrycie i przekazuje je do ZOP-CONF-01. Nie ustanawia arbitralnego progu akceptacji.**

## 8. Struktura portfela i udziały

### 8.1. Udziały elementu

| Miara | Podstawa | Reguła |
| --- | --- | --- |
| revenue_share | net_revenue_item / net_revenue_portfolio | liczona dla zgodnego scope |
| cm1_share | CM1_item / ΣCM1 | tylko gdy mianownik jest interpretowalny |
| segment_margin_share | SM_item / ΣSM | tylko gdy mianownik jest interpretowalny |

Udziały odpowiadają na dwa różne pytania: jaka jest stopa marży elementu oraz jaką część wartości portfela ten element tworzy. Wkłady dodatnie i ujemne zachowują znaki; przy mianowniku bliskim zeru interpretacja wymaga validation_required.

### 8.2. Zmiana udziałów

Δrevenue_shareᵢ = revenue_share_currentᵢ − revenue_share_referenceᵢ

Zmiana wagi elementu w przychodzie portfela.

| Sygnał | Interpretacja diagnostyczna |
| --- | --- |
| Przychód rośnie, CM1R stabilna | wzrost skali bez sygnału pogorszenia ekonomiki |
| Przychód rośnie, CM1R spada | pogorszenie ekonomiki mimo wzrostu sprzedaży |
| Udział niskomarżowych elementów rośnie | możliwy niekorzystny efekt miksu |
| Udział wysokomarżowych elementów rośnie | możliwy korzystny efekt miksu |

> **ZASTRZEŻENIE PORT-01 opisuje strukturę i jej zmianę. Nie ustala arbitralnych minimów marży ani progów koncentracji.**

## 9. Czysty efekt miksu i efekt marży

Czystą dekompozycję wykonuje się wyłącznie dla elementów należących jednocześnie do current i reference oraz spełniających warunek porównywalności. matched_revenue_share_current_i i matched_revenue_share_reference_i liczy się w obrębie tej populacji; w każdym okresie Σmatched_revenue_share = 1 z tolerancją zaokrągleń.

Portfolio_CM1R_ref = Σ(matched_revenue_share_referenceᵢ × CM1R_refᵢ)

Referencyjna stopa marży portfela.

Portfolio_CM1R_mix = Σ(matched_revenue_share_currentᵢ × CM1R_refᵢ)

Stopa przy aktualnym miksie i niezmienionej referencyjnej marżowości elementów.

Mix_effect_rate = Portfolio_CM1R_mix − Portfolio_CM1R_ref

Czysty wpływ zmiany udziałów elementów.

Portfolio_CM1R_current = Σ(matched_revenue_share_currentᵢ × CM1R_currentᵢ)

Bieżąca stopa dla matched portfolio.

Margin_effect_rate = Portfolio_CM1R_current − Portfolio_CM1R_mix

Wpływ zmiany ekonomiki poszczególnych elementów.

> **TOŻSAMOŚĆ KONTROLNA Portfolio_CM1R_current − Portfolio_CM1R_ref = Mix_effect_rate + Margin_effect_rate, z zastrzeżeniem tej samej populacji matched portfolio i precyzji zaokrągleń.**

new_item, discontinued_item i materially_changed_item pozostają poza matched portfolio i są prezentowane osobno jako zmiana strukturalna wraz z udziałem w przychodzie i CM1, jeżeli dane pozwalają. Nie wpływają sztucznie na Mix_effect_rate. Gdy normalizacja lub porównywalność nie jest wiarygodna, mix/margin pozostają null i otrzymują TEST_PARTIAL.

## 10. Zmiany portfela, capacity i kontekst

### 10.1. Nowe, wycofane i zmienione elementy

| Flaga | Warunek | Prezentacja |
| --- | --- | --- |
| new_item | obecny current, brak porównywalnej referencji | osobno: structural/new item, udział przychodu i CM1; poza matched |
| discontinued_item | obecny reference, brak current | osobno: structural/discontinued item, udział referencyjny i CM1; poza matched |
| materially_changed_item | zmieniona definicja, pakiet lub ekonomika | zmiana strukturalna; osobna walidacja i prezentacja; poza matched |

### 10.2. Ekonomika skorygowana o capacity

CM1_per_capacity_unit = CM1 / capacity_used_attributable

Wyłącznie dla wiarygodnego przypisania i zgodnego capacity_unit.

SM_per_capacity_unit = SM / capacity_used_attributable

Miara opcjonalna; te same warunki porównywalności.

capacity_constraint_status przyjmuje: verified_constraint, not_verified, not_constrained albo unknown. CM1_per_capacity_unit i SM_per_capacity_unit są miarami opisowymi przy poprawnym przypisaniu capacity. Rekomendacja zmiany miksu z powodu wartości na jednostkę capacity wymaga verified_constraint albo potwierdzenia przez właściwy CAP/PROC; bez tego pozostaje wyłącznie sygnałem diagnostycznym.

### 10.3. portfolio_context_flags

launch_phase; sunset_phase; strategic_item; mandatory_item; bundled_item; loss_leader_declared; contractual_obligation; regulatory_obligation; cross_sell_dependency; capacity_anchor; temporary_price_action; other_context. Flaga nie ukrywa wyniku ekonomicznego i nie przesądza decyzji.

## 11. Dekompozycja, udział w pogorszeniu i hipotezy

### 11.1. Poziomy

| Poziom | Zakres | Wynik minimalny |
| --- | --- | --- |
| I | organization | ekonomika i struktura całego portfela |
| II | unit | lokalizacja przychodu, CM1, SM i luk |
| III | portfolio_group | agregat porównywalnych elementów |
| IV | portfolio_item | pełny wynik elementu |
| opcjonalny | customer_segment / channel | wyłącznie przy danych porównywalnych |

### 11.2. Udział w zmianie

| Pole | Znaczenie |
| --- | --- |
| revenue_change_share | neutralny, podpisany udział elementu w zmianie przychodów |
| adverse_contribution_gap_share | contribution_gap_amount_signed_i = net_revenue_current_i × (CM1R_ref_i − CM1R_current_i); adverse_contribution_gap_amount_i = max(contribution_gap_amount_signed_i, 0); adverse_contribution_gap_share_i = adverse_contribution_gap_amount_i / Σadverse_contribution_gap_amount; przy sumie 0 → null |
| adverse_segment_margin_gap_share | segment_margin_rate_gap_signed_i = SMR_ref_i − SMR_current_i; segment_margin_gap_amount_signed_i = net_revenue_current_i × segment_margin_rate_gap_signed_i; adverse_segment_margin_gap_amount_i = max(segment_margin_gap_amount_signed_i, 0); adverse_segment_margin_gap_share_i = adverse_segment_margin_gap_amount_i / Σadverse_segment_margin_gap_amount; przy sumie 0 → null |
| compensating_portfolio_items | elementy z ujemną wartością contribution_gap_amount_signed lub segment_margin_gap_amount_signed pozostają czynnikami kompensującymi i są zachowane osobno |

### 11.3. Hipotezy do weryfikacji

Spadek ceny; wzrost kosztu zmiennego; zmiana struktury wolumenu; zmiana miksu; pracochłonność; wzrost kosztu pracy; niewykorzystanie lub przeciążenie capacity; warunki kontraktu; błąd alokacji kosztu; błąd przypisania przychodu; wąskie gardło; pakietowanie; sezonowość; zmiana jakości; etap cyklu życia. Każda pozostaje HIPOTEZĄ DO WERYFIKACJI.

### 11.4. next_tests

| Test | Sygnał |
| --- | --- |
| FIN-01 | wpływ na ekonomikę organizacji |
| FIN-03 | pogorszenie kosztu jednostkowego |
| CAP-01 | nierównomierne wykorzystanie capacity |
| CAP-02 | przeciążenie |
| HR-01 | koszt pracy / produktywność |
| PROC-01 / PROC-02 | proces lub wąskie gardło |

## 12. Dane dla mechanizmów wspólnych

### 12.1. Payload dla ZOP-PRI-01

| Cel | Pola |
| --- | --- |
| Priorytetyzacja – bez lokalnego wzoru | negative_cm1; negative_segment_margin; contribution_margin_rate_gap; contribution_gap_amount_signed; adverse_contribution_gap_amount; adverse_contribution_gap_share; segment_margin_rate_gap_signed; segment_margin_gap_amount_signed; adverse_segment_margin_gap_amount; adverse_segment_margin_gap_share; mix_effect_rate; margin_effect_rate; revenue_share; cm1_share; persistence; trend_direction; economic_scale; portfolio_scope; capacity_signal; capacity_constraint_status; strategic_context; result_risk; urgent_validation |

### 12.2. Payload dla ZOP-CONF-01

| Cel | Pola |
| --- | --- |
| Pewność – bez lokalnego score | revenue_coverage; cost_coverage; matched_portfolio_coverage; matched_revenue_share_normalization; revenue_attribution_quality; cost_attribution_quality; cost_attribution_scope_quality; allocation_quality; volume_comparability; portfolio_comparability; reference_quality; cost_avoidability_quality; capacity_attribution_quality; reconciliation_quality; data_completeness; manual_validation; context_flags |

### 12.3. Bazowa struktura FINDINGS

| Pole bazowe | Reguła PORT-01 |
| --- | --- |
| test_id | PORT-01 |
| scope | filtry, poziom i populacja |
| period | current + reference + horyzont |
| status | status logiczny testu |
| finding | komunikat faktograficzny |
| metric_value / reference_value | główna miara i referencja |
| gap | odchylenie właściwe dla findingu |
| impact_low / impact_high | odpowiedzialny przedział albo null |
| confidence_score / confidence_class | wynik ZOP-CONF-01 albo null |
| next_tests | tablica id + uzasadnienie |
| validation_required | boolean |

## 13. Rozszerzenia FINDINGS i komunikat zarządczy

| Grupa | Pola techniczne |
| --- | --- |
| Identyfikacja, przychód i koszt | portfolio_item; portfolio_group; portfolio_item_status; net_revenue_current; net_revenue_reference; revenue_share_current; revenue_share_reference; direct_variable_cost; direct_committed_cost; shared_cost; allocated_shared_cost; allocation_basis; allocation_quality; cost_attribution_scope |
| Wyniki elementu | cm1_current; cm1_reference; cm1_rate_current; cm1_rate_reference; segment_margin_current; segment_margin_reference; segment_margin_rate_current; segment_margin_rate_reference; full_result; unit_net_revenue; unit_variable_cost; unit_contribution; contribution_gap_amount_signed; adverse_contribution_gap_amount; adverse_contribution_gap_share; segment_margin_rate_gap_signed; segment_margin_gap_amount_signed; adverse_segment_margin_gap_amount; adverse_segment_margin_gap_share |
| Portfel, capacity i walidacja | matched_revenue_share_current; matched_revenue_share_reference; mix_effect_rate; margin_effect_rate; matched_portfolio_coverage; revenue_coverage; cost_coverage; capacity_used_attributable; capacity_constraint_status; cm1_per_capacity_unit; portfolio_context_flags; main_portfolio_items; compensating_portfolio_items; exclusion_flags; validation_notes |

### 13.1. Statusy logiczne

NO_ADVERSE_SIGNAL; ADVERSE_SIGNAL; INCIDENT; DETERIORATING; STABLE; IMPROVING; TEST_PARTIAL; TEST_BLOCKED. Statusy STANDARD / MEDIUM / HIGH / CRITICAL nada dopiero ZOP-PRI-01. confidence_score i confidence_class pozostają null do czasu ZOP-CONF-01.

### 13.2. Komunikat zarządczy

> **[STATUS] RENTOWNOŚĆ PORTFELA Portfel wygenerował w badanym okresie [R] przychodu netto oraz [CM1] marży kontrybucyjnej I. Stopa marży zmieniła się z [ref] do [current]. Największy udział w marży tworzą [elementy]. Największa ujemna luka względem referencji występuje w [elementy]. Zmiana struktury portfela wpłynęła na stopę marży o [mix effect], natomiast zmiana ekonomiki samych produktów o [margin effect]. [X]% przychodów objęto analizą o wystarczającej jakości danych. Wynik nie przesądza o utrzymaniu lub wycofaniu produktu. Najpierw należy zweryfikować [next_tests].**

### 13.3. Dwie sytuacje ochronne

| Sytuacja | Wniosek |
| --- | --- |
| CM1 < 0 | silny sygnał; najpierw walidacja danych, ceny, umowy, pakietu, obowiązku, kosztu i procesu |
| CM1 > 0, SM > 0, Full_result < 0 | brak rekomendacji zamknięcia; sprawdź allocation_basis i możliwość zniknięcia kosztu wspólnego |

## 14. Scenariusze testowe PORT01-T01–T08

| Id | Scenariusz | Dane | Oczekiwane |
| --- | --- | --- | --- |
| PORT01-T01 | stabilny portfel | Revenue, CM1 i miks stabilne | NO_ADVERSE_SIGNAL |
| PORT01-T02 | wzrost przychodu, stabilna marża | Revenue↑; CM1R stabilne | bez fałszywego alarmu |
| PORT01-T03 | wzrost przychodu, spadek marży | Revenue↑; CM1R↓ | ADVERSE_SIGNAL mimo wzrostu sprzedaży |
| PORT01-T04 | ujemna CM1 | net_revenue < direct_variable_cost | silny sygnał; bez auto-zamknięcia |
| PORT01-T05 | dodatnia CM1/SM, ujemny Full_result | alokacja czyni wynik ujemnym | walidacja allocation_basis; bez auto-zamknięcia |
| PORT01-T06 | niewiarygodna alokacja | brak poprawnej allocation_basis | Full_result=null; TEST_PARTIAL |
| PORT01-T07 | nieporównywalny wolumen | różne activity_unit | brak sztucznego unit_contribution |
| PORT01-T08 | pogorszenie miksu | udział elementów o niższej CM1R_ref rośnie | Mix_effect_rate < 0 |

### 14.1. Warunek PASS scenariusza

PASS wymaga zgodności walidacji, wartości na agregatach, statusu logicznego, flag, null dla miar niewykonalnych, struktury FINDINGS, next_tests oraz zakazów decyzyjnych. Sama poprawna liczba CM1 nie wystarcza.

## 15. Scenariusze testowe PORT01-T09–T18

| Id | Scenariusz | Dane | Oczekiwane |
| --- | --- | --- | --- |
| PORT01-T09 | poprawa miksu | udział elementów o wyższej CM1R_ref rośnie | Mix_effect_rate > 0 |
| PORT01-T10 | spadek marży bez zmiany miksu | miks stabilny; CM1R elementów↓ | Margin_effect_rate < 0 |
| PORT01-T11 | nowy produkt | znaczny revenue bez referencji | niższe matched coverage; bez sztucznej referencji |
| PORT01-T12 | produkt wycofany | obecny tylko w reference | discontinued_item; poza matched |
| PORT01-T13 | strategiczny element z ujemnym wynikiem | strategic_item / mandatory_item | wynik jawny; bez auto-wycofania |
| PORT01-T14 | wysoka CM1, dużo wąskiego capacity | CM1% wysoka; CM1/capacity niska | CAP/PROC; bez rankingu tylko po CM1% |
| PORT01-T15 | niepełne pokrycie kosztowe | część kosztów unmapped | TEST_PARTIAL; validation_required |
| PORT01-T16 | nowy produkt, brak zmiany miksu matched | Ref A/B 50/50; current A/B/C 40/40/20 | matched A/B 50/50; Mix_effect bez wpływu C; C osobno; coverage↓ |
| PORT01-T17 | koszt utrzymujący na poziomie grupy | licencja/zespół dla portfolio_group | koszt pozostaje group-level; SM_item bez podziału; SM_group uwzględnia koszt |
| PORT01-T18 | shared cost i alokacja bez podwójnego liczenia | shared_cost=100; allocated=80 | alokacja 80; 20 niealokowane; koszt całkowity 100, nie 180 |

### 15.1. Obowiązkowy scenariusz regresyjny T05

> **REGRESJA Dodatnia CM1 i SM przy ujemnym Full_result nie mogą wygenerować rekomendacji zamknięcia elementu. Silnik ma zachować wszystkie warstwy wyniku, allocation_quality, cost_avoidability, decision_horizon i validation_required.**

### 15.2. Wyłączenia

exclusion_flags zapisują zmianę definicji, księgowania, zakresu, pakietowania, zdarzenie jednorazowe lub brak porównywalności. Nie usuwają danych; ograniczają interpretację i zasilają ZOP-CONF-01.

## 16. Kryteria odbioru implementacji PORT01-ACC-01–34

| Id | Zakres / kontrola | Id | Zakres / kontrola |
| --- | --- | --- | --- |
| PORT01-ACC-01 | przyjmuje portfolio_item – PASS | PORT01-ACC-02 | waliduje revenue attribution – PASS |
| PORT01-ACC-03 | waliduje cost attribution – PASS | PORT01-ACC-04 | rozróżnia direct_variable_cost – PASS |
| PORT01-ACC-05 | rozróżnia direct_committed_cost i cost_attribution_scope – PASS | PORT01-ACC-06 | rozróżnia trzy pule; allocated_shared_cost traktuje jako widok pochodny – PASS |
| PORT01-ACC-07 | nie alokuje bez podstawy, nie liczy podwójnie i kontroluje limit puli – PASS | PORT01-ACC-08 | liczy CM1 – PASS |
| PORT01-ACC-09 | liczy CM1R – PASS | PORT01-ACC-10 | liczy SM – PASS |
| PORT01-ACC-11 | liczy SMR – PASS | PORT01-ACC-12 | Full_result tylko przy poprawnej alokacji – PASS |
| PORT01-ACC-13 | obsługuje cost_avoidability – PASS | PORT01-ACC-14 | analizuje 1M/3M/6M/12M – PASS |
| PORT01-ACC-15 | liczy revenue_share – PASS | PORT01-ACC-16 | liczy cm1_share – PASS |
| PORT01-ACC-17 | rozróżnia podpisane i niekorzystne luki CM1/SM, liczy adverse gap amounts i shares z części niekorzystnej; przy sumie 0 zwraca null – PASS | PORT01-ACC-18 | liczy i normalizuje matched_revenue_share current/reference – PASS |
| PORT01-ACC-19 | oddziela zmianę strukturalną od czystych mix_effect i margin_effect – PASS | PORT01-ACC-20 | obsługuje new_item – PASS |
| PORT01-ACC-21 | obsługuje discontinued_item – PASS | PORT01-ACC-22 | kontroluje portfolio coverage – PASS |
| PORT01-ACC-23 | uzgadnia przychód z FIN-01 – PASS | PORT01-ACC-24 | uzgadnia koszty z FIN/COST – PASS |
| PORT01-ACC-25 | nie sumuje nieporównywalnego volume – PASS | PORT01-ACC-26 | stosuje capacity_constraint_status przed rekomendacją zmiany miksu – PASS |
| PORT01-ACC-27 | obsługuje portfolio_context_flags – PASS | PORT01-ACC-28 | dekomponuje hierarchicznie; nie rozdziela automatycznie kosztu grupy na item – PASS |
| PORT01-ACC-29 | obsługuje exclusion_flags – PASS | PORT01-ACC-30 | ustawia validation_required – PASS |
| PORT01-ACC-31 | zapisuje FINDINGS z jednoznacznymi polami signed/adverse oraz segment_margin_rate_current/reference – PASS | PORT01-ACC-32 | wskazuje next_tests – PASS |
| PORT01-ACC-33 | nie rekomenduje automatycznie zamknięcia produktu – PASS | PORT01-ACC-34 | przechodzi PORT01-T01–T18 – PASS |

## 17. Definition of Done PORT01-DOD-01–36

| Id | Zakres / kontrola | Id | Zakres / kontrola |
| --- | --- | --- | --- |
| PORT01-DOD-01 | cel – PASS | PORT01-DOD-02 | granica testu – PASS |
| PORT01-DOD-03 | portfolio_item – PASS | PORT01-DOD-04 | net_revenue – PASS |
| PORT01-DOD-05 | revenue attribution – PASS | PORT01-DOD-06 | direct_variable_cost – PASS |
| PORT01-DOD-07 | direct_committed_cost i cost_attribution_scope – PASS | PORT01-DOD-08 | trzy pule kosztu; allocated_shared_cost jako pochodna – PASS |
| PORT01-DOD-09 | allocation_basis, limit puli i brak podwójnego liczenia – PASS | PORT01-DOD-10 | CM1 – PASS |
| PORT01-DOD-11 | CM1R – PASS | PORT01-DOD-12 | SM – PASS |
| PORT01-DOD-13 | Full_result – PASS | PORT01-DOD-14 | cost_avoidability – PASS |
| PORT01-DOD-15 | volume comparability – PASS | PORT01-DOD-16 | horyzonty – PASS |
| PORT01-DOD-17 | referencja – PASS | PORT01-DOD-18 | podpisane i adverse luki CM1/SM wraz z udziałami – PASS |
| PORT01-DOD-19 | struktura oraz osobne new/discontinued/materially_changed – PASS | PORT01-DOD-20 | matched portfolio i normalizacja udziałów – PASS |
| PORT01-DOD-21 | mix effect wyłącznie na matched_revenue_share – PASS | PORT01-DOD-22 | margin effect wyłącznie na matched_revenue_share – PASS |
| PORT01-DOD-23 | nowe/wycofane produkty – PASS | PORT01-DOD-24 | portfolio coverage – PASS |
| PORT01-DOD-25 | reconciliation – PASS | PORT01-DOD-26 | capacity economics i capacity_constraint_status – PASS |
| PORT01-DOD-27 | context flags – PASS | PORT01-DOD-28 | hierarchiczna dekompozycja kosztu i SM – PASS |
| PORT01-DOD-29 | hipotezy – PASS | PORT01-DOD-30 | next_tests – PASS |
| PORT01-DOD-31 | dane ZOP-PRI-01 używają revenue_share, cm1_share i jednoznacznych pól luk – PASS | PORT01-DOD-32 | dane ZOP-CONF-01 – PASS |
| PORT01-DOD-33 | FINDINGS – jednoznaczne pola signed/adverse i SMR current/reference – PASS | PORT01-DOD-34 | komunikat zarządczy – PASS |
| PORT01-DOD-35 | scenariusze PORT01-T01–T18 – PASS | PORT01-DOD-36 | kryteria implementacyjne – PASS |

## 18. QPORT01 i status końcowy

| Id | Zakres / kontrola | Id | Zakres / kontrola |
| --- | --- | --- | --- |
| QPORT01-01 | uniwersalność branżowa – PASS | QPORT01-02 | portfolio_item jednoznaczny – PASS |
| QPORT01-03 | przychód ma podstawę przypisania – PASS | QPORT01-04 | CM1 poprawnie liczona – PASS |
| QPORT01-05 | direct_variable_cost ≠ shared_cost – PASS | QPORT01-06 | direct_committed_cost oddzielny i ma cost_attribution_scope – PASS |
| QPORT01-07 | shared_cost nie jest automatycznie alokowany ani liczony podwójnie – PASS | QPORT01-08 | allocated_shared_cost jest pochodny, ma podstawę i nie przekracza puli – PASS |
| QPORT01-09 | ujemny Full_result bez auto-zamknięcia – PASS | QPORT01-10 | dodatnia CM1 i ujemny Full_result poprawnie interpretowane – PASS |
| QPORT01-11 | direct_committed_cost ≠ automatycznie koszt usuwalny – PASS | QPORT01-12 | cost_avoidability jawna – PASS |
| QPORT01-13 | 0 arbitralnych progów rentowności – PASS | QPORT01-14 | 0 arbitralnych benchmarków – PASS |
| QPORT01-15 | volume porównywalny – PASS | QPORT01-16 | revenue nie zastępuje volume – PASS |
| QPORT01-17 | analiza struktury portfela – PASS | QPORT01-18 | matched_revenue_share current/reference znormalizowane do 1 – PASS |
| QPORT01-19 | mix_effect i margin_effect używają wyłącznie matched portfolio – PASS | QPORT01-20 | new_item oddzielony jako zmiana strukturalna – PASS |
| QPORT01-21 | discontinued/materially_changed oddzielone od czystego mix effect – PASS | QPORT01-22 | matched_portfolio_coverage kontrolowane – PASS |
| QPORT01-23 | revenue uzgodniony z FIN-01 – PASS | QPORT01-24 | koszty uzgodnione – PASS |
| QPORT01-25 | unmapped revenue/cost jawne – PASS | QPORT01-26 | coverage trafia do ZOP-CONF-01 – PASS |
| QPORT01-27 | capacity economics opisowe; rekomendacja wymaga verified_constraint lub CAP/PROC – PASS | QPORT01-28 | brak porównań niezgodnych capacity_unit – PASS |
| QPORT01-29 | context_flags nie ukrywają ekonomiki – PASS | QPORT01-30 | strategic_item bez auto-utrzymania – PASS |
| QPORT01-31 | signed contribution/segment gaps zachowują znak; adverse amounts/shares używają wyłącznie części niekorzystnej; poprawa osobno – PASS | QPORT01-32 | hipoteza ≠ przyczyna – PASS |
| QPORT01-33 | next_tests istnieją – PASS | QPORT01-34 | FIN-01 niezmieniony – PASS |
| QPORT01-35 | CAP-01 niezmieniony – PASS | QPORT01-36 | HR-01 niezmieniony – PASS |
| QPORT01-37 | ZOP-PRI-01 nieopracowany – PASS | QPORT01-38 | ZOP-CONF-01 nieopracowany – PASS |
| QPORT01-39 | FINDINGS zawiera jednoznaczne pola signed/adverse oraz segment_margin_rate_current/reference – PASS | QPORT01-40 | 18 scenariuszy PORT01-T01–T18 – PASS |
| QPORT01-41 | ACC jawnie kontroluje pakiet korekcyjny – PASS | QPORT01-42 | DOD-01–36 obejmuje pakiet korekcyjny – PASS |
| QPORT01-43 | gotowe dla Aleksandra – PASS | QPORT01-44 | 0 danych SPZOZ – PASS |
| QPORT01-45 | 0 danych pacjentów – PASS | QPORT01-46 | 0 PORT-02 – PASS |

> **PORT-01 ZAMKNIĘTY METODOLOGICZNIE DO IMPLEMENTACJI**

| Element | Status / wynik |
| --- | --- |
| ZOP-PRI-01 | DO OPRACOWANIA |
| ZOP-CONF-01 | DO OPRACOWANIA |
| PORT01-DOD | 36/36 PASS |
| QPORT01 | 46/46 PASS |
| Scenariusze | 18 – PORT01-T01–T18 |
| next_tests | FIN-01; FIN-03; CAP-01; CAP-02; HR-01; PROC-01; PROC-02 |

### 18.1. Otwarte kwestie metodologiczne

| Kwestia | Status / wpływ |
| --- | --- |
| globalny mechanizm priorytetu | ZOP-PRI-01 do opracowania; PORT-01 dostarcza payload |
| globalny mechanizm pewności | ZOP-CONF-01 do opracowania; PORT-01 dostarcza sygnały jakości |
| standard jakości allocation_basis | wspólny kontrakt; PORT-01 wymaga dokumentacji |
| standard cost_avoidability i decision_horizon | do ujednolicenia między branżami |
| reguły orkiestracji next_tests | poza PORT-01; test jedynie rekomenduje |

0 arbitralnych progów rentowności; 0 arbitralnych alokacji kosztów wspólnych; 0 automatycznych rekomendacji zamknięcia produktu; CM1 ≠ Full_result; koszt przypisany ≠ automatycznie koszt możliwy do usunięcia; 0 nowych progów Priority Score; 0 nowych progów Confidence Score; 0 danych SPZOZ; 0 danych pacjentów; 0 rozpoczętego PORT-02.
