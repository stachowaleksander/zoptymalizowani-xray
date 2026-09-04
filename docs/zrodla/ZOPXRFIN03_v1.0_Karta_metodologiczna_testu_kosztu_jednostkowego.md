ZOPTYMALIZOWANI – X-RAY

# FIN-03

# Koszt jednostkowy

Karta metodologiczna i specyfikacja implementacyjna

> **STATUS FIN-03 ZAMKNIĘTY METODOLOGICZNIE DO IMPLEMENTACJI**

| Pole | Wartość |
| --- | --- |
| Identyfikator | ZOP-XR-FIN-03 |
| Wersja / data | v1.0 / 2 września 2026 |
| Rola | dziewiąty pełny test diagnostyczny X-Ray; wzorzec rodziny testów kosztowych |
| Odbiorcy | zarządzający, analityk, Aleksander – implementacja |
| Źródła nadrzędne | polecenie; FIN-02 v1.0; PORT-01 v1.0; HR-01 v1.0; CAP-01 v1.0; CAP-02 v1.0; PROC-01 v1.0; PROC-02 v1.0; FIN-01 v1.0; ZOP-TECH-01; ZOP-MASTER-01 |
| Zależności | ZOP-PRI-01 i ZOP-CONF-01 – DO OPRACOWANIA |

FIN-03 definiuje koszt jednostkowy wyłącznie dla jawnego mianownika i rozdziela poprawność mianownika w każdym okresie od porównywalności current/reference. Zmianę kosztu jednostkowego rozlicza dokładnym mostem Shapleya koszt + denominator, zachowuje matched scope, okresową atrybucję shared cost i sygnały wyjaśniające z innych testów. Nie projektuje FIN-04, aplikacji, panelu ani AI.

> **ZASADA NADRZĘDNA Koszt jednostkowy ma sens tylko wtedy, gdy licznik i mianownik opisują tę samą działalność, ten sam zakres i porównywalną jednostkę efektu.**

## 1. Rola, pytanie diagnostyczne i granice FIN-03

> **PYTANIE DIAGNOSTYCZNE Ile kosztuje wytworzenie jednej porównywalnej jednostki działalności, jak zmienia się ten koszt względem wartości odniesienia oraz czy zmiana wynika ze wzrostu kosztu, spadku skali, zmiany miksu, większej pracochłonności, niewykorzystania capacity, przeciążenia, rework lub zmiany procesu?**

| Etap | Produkt | Granica |
| --- | --- | --- |
| Koszt | licznik warstwy kosztowej | ten sam scope co activity |
| Jednostka działalności | unit_cost_denominator_type / unit_cost_denominator_unit | mianownik musi mieć źródło |
| Porównywalność | unit_cost_denominator_comparability / weighting_quality | brak podstawy → null/partial |
| Koszt jednostkowy | VARIABLE / COMMITTED / FULL / LABOR / WORK_CONTENT_BASED | jedna warstwa na finding |
| Zmiana | signed gap / adverse gap | signed ≠ adverse |
| Most | cost_effect + denominator_effect | Shapley; dokładna rekonsyliacja; volume_effect tylko jako alias dla mianowników wolumenowych |
| Wyjaśnienia | PORT / HR / CAP / PROC | evidence ≠ bridge component |
| Hipotezy | mechanizmy do weryfikacji | hipoteza ≠ przyczyna |
| Dalej | next_tests | bez automatycznej decyzji |

### 1.1. FIN-02 ≠ FIN-03

| FIN-02 | FIN-03 |
| --- | --- |
| wynik i stopa rentowności | koszt na porównywalną jednostkę działalności |
| most wyniku i most marży | most kosztu jednostkowego: koszt + mianownik |
| cost load względem revenue | cost numerator względem jawnego unit_cost_denominator |
| wyjaśnia erozję rentowności | wyjaśnia zmianę kosztu jednej jednostki |

### 1.2. PORT-01 ≠ FIN-03

| PORT-01 | FIN-03 |
| --- | --- |
| czy produkt/element portfela jest rentowny | dlaczego koszt jednej porównywalnej jednostki rośnie lub spada |
| CM1 / SM / warunkowo Full_result | VARIABLE / COMMITTED / FULL / LABOR / WORK_CONTENT_BASED |
| mix_effect i margin_effect portfela | mix wyłącznie evidence albo kontrola weighted_volume |
| portfolio_item jako podstawowa jednostka | organization / unit / portfolio_group / portfolio_item / resource_group / process_stage |

### 1.3. Najważniejsza ochrona mianownika

> **NIE DZIEL AUTOMATYCZNIE Nie wolno automatycznie liczyć koszt / liczba przypadków ani przełączać denominator_type między current i reference. activity_volume, weighted_volume, good_output_volume, work_content i inherited_hr_effect odpowiadają na różne pytania i muszą mieć jawny unit_cost_denominator_basis.**

## 2. Scope, jednostka działalności i porównywalność mianownika

### 2.1. unit_cost_scope

| Wartość | Znaczenie |
| --- | --- |
| organization | cała organizacja lub uzgodniony zakres |
| unit | jednostka organizacyjna |
| portfolio_group | grupa elementów portfela |
| portfolio_item | pojedynczy produkt/usługa – tylko przy wiarygodnej atrybucji |
| resource_group | grupa zasobów przy zgodnym mianowniku |
| process_stage | etap procesu przy zgodnym cost attribution |
| other_documented_scope | inny jawny, źródłowo zdefiniowany zakres |

### 2.2. activity_unit i activity_unit_basis

Centralnym mianownikiem jest activity_unit zgodna z semantyką PORT-01. Może oznaczać sztukę, usługę, case, wizytę, pacjentodzień, tonokilometr, kilometr, cykl, godzinę maszynową, roboczogodzinę, pakiet, jednostkę ważoną albo inną udokumentowaną jednostkę. Nazwa i znaczenie muszą pochodzić ze źródła lub jawnego mapowania.

| Pole | Kontrakt |
| --- | --- |
| activity_unit | jednoznaczna jednostka działalności |
| activity_unit_basis | co oznacza 1 jednostka, jak jest liczona, co obejmuje/wyklucza i czy definicja jest stabilna |
| activity_volume_current; activity_volume_reference | wolumen okresu bieżącego i odniesienia w tej samej activity_unit |
| volume_comparability | true / false / null-not_assessable; false blokuje proste porównanie unit cost |
| activity_recognition_comparability | czy zasady rozpoznania activity są zgodne current/reference |

### 2.3. weighted_volume

Gdy surowy wolumen jest heterogeniczny, dopuszczalne jest weighted_volume wyłącznie przy udokumentowanym systemie wag, stabilnym current/reference i braku arbitralnych wag. weighting_quality zasila ZOP-CONF-01.

| Pole | Reguła |
| --- | --- |
| weighted_volume_current; weighted_volume_reference | ważony wolumen dla current/reference |
| weighted_volume_basis | źródło, wersja, zakres i metoda wag |
| weighting_quality | jakość i stabilność systemu wag |
| mix_comparability | czy miks pozwala użyć prostego volume; false → prosty bridge może być mylący |

> **ZAKAZ FIN-03 nie tworzy wag lokalnie po zobaczeniu wyniku. Brak źródłowych wag oznacza weighted_volume = null, a nie arbitralną korektę miksu.**

### 2.4. work_content jako alternatywny mianownik

work_content zachowuje semantykę HR-01/CAP-02: ilość mierzalnego nakładu lub zgodnej capacity wymaganej do wykonania pracy, w udokumentowanej work_content_unit. work_content ≠ activity_volume.

### 2.5. Jawny kontrakt mianownika

| Pole | Kontrakt |
| --- | --- |
| unit_cost_denominator_type | activity_volume / weighted_volume / good_output_volume / work_content / inherited_hr_effect |
| unit_cost_denominator_current | wartość mianownika faktycznie użyta w current; pochodzi z pola źródłowego wskazanego przez type |
| unit_cost_denominator_reference | wartość tego samego rodzaju mianownika w reference, jeżeli wiarygodna podstawa reference istnieje |
| unit_cost_denominator_unit | jednostka zgodna z wybranym denominator_type; bez cichego przeliczenia |
| unit_cost_denominator_basis | źródło, reguła wyznaczenia, zakres i – jeśli dotyczy – wersja wag/definicji efektu |
| unit_cost_denominator_comparability | ocena wyłącznie current vs reference: true / false / null-not_assessable. Dla porównania wymagane są zgodne type, unit i porównywalna basis; pole nie decyduje o samodzielnej obliczalności current lub reference. |
| unit_cost_denominator_valid_current | true / false / null-not_assessable; poprawność mianownika current niezależnie od istnienia i porównywalności reference |
| unit_cost_denominator_valid_reference | true / false / null-not_assessable; poprawność mianownika reference niezależnie od current |
| unit_cost_denominator_validation_basis_current | opcjonalny ślad walidacyjny current: źródło, kontrola scope/okresu, reguła >0, jakość definicji i inne ograniczenia |
| unit_cost_denominator_validation_basis_reference | opcjonalny ślad walidacyjny reference: źródło, kontrola scope/okresu, reguła >0, jakość definicji i inne ograniczenia |

| unit_cost_period | cost_numerator_period / unit_cost_denominator_period. Obliczalny, gdy denominator_period > 0, unit_cost_denominator_valid_period = true oraz licznik i mianownik należą do tego samego scope i okresu. Nie wymaga istnienia drugiego okresu. |
| --- | --- |
| unit_cost_current / unit_cost_reference | każdy okres jest obliczany niezależnie na własnej poprawnej podstawie; brak lub niewiarygodność reference nie usuwa poprawnego unit_cost_current. |
| gap / change rate / bridge | wymagają obliczalnych current i reference, unit_cost_denominator_comparability = true oraz zgodnych denominator_type, denominator_unit i porównywalnej denominator_basis. W przeciwnym razie gap/change/bridge = null. |

activity_volume, weighted_volume, good_output_volume i work_content pozostają polami źródłowymi. unit_cost_denominator_* jednoznacznie wskazuje, które z nich zostało użyte w danym obliczeniu. Poprawność mianownika ocenia się osobno dla current i reference; unit_cost_denominator_comparability opisuje wyłącznie porównywalność między okresami. Nie wolno przełączać denominator_type między current i reference dla gapu, change rate ani bridge.

| cost_per_work_content_unit | documented_cost_numerator / comparable_work_content Tylko przy zgodnym scope, work_content_unit i jakości danych. Nie zastępuje kosztu per activity_unit. |
| --- | --- |

| work_content_per_activity_unit | work_content / comparable_activity_volume Tylko przy porównywalnym activity_volume i work_content. |
| --- | --- |

### 2.6. Kontrakt pól dziedziczonych – bez redefinicji

| Źródło | Pola zachowane | Granica FIN-03 |
| --- | --- | --- |
| FIN-02 | net_revenue; direct_variable_cost; direct_committed_cost; shared_cost; unclassified_operating_cost; operating_cost_total; profitability_scope; profitability_layer; matched_profitability_scope; accounting_basis_comparability; cost_classification_comparability; allocation_basis; allocation_quality; oneoff_flag; adjustment_basis | FIN-03 używa tych samych znaczeń; nie tworzy drugiej klasyfikacji ekonomicznej. |
| PORT-01 | activity_unit; weighted_volume; volume_comparability; CM1; SM; cost_attribution_scope | Mianownik i atrybucja pozostają zgodne z PORT; rentowność produktu nadal należy do PORT-01. |
| HR-01 | labor_input; labor_cost; work_content; productivity; unit_labor_cost | LABOR i work-content evidence nie mogą być sprzeczne z HR-01. |
| CAP-01 / CAP-02 | effective_available; matched_effective_available; used; required_capacity; capacity_pressure_ratio; extra_capacity_dependency | Pola capacity są wyłącznie evidence/kontekstem mianownika; FIN-03 nie zmienia ich matematyki. |
| PROC-01 / PROC-02 | rework; repeat_visit; process_delay_evidence; constraint_status; constraint_entity_type | Proces może wyjaśniać zmianę nakładu/output, ale czas i constraint nie są automatycznie kosztem. |

Jeżeli pole źródłowe nie jest dostępne lub jego scope nie odpowiada FIN-03, pozostaje null/not_assessable. Brak danych nie upoważnia do stworzenia lokalnej definicji zastępczej.

## 3. Warstwy kosztu jednostkowego i liczniki

### 3.1. unit_cost_layer

| Warstwa | Podstawowa konstrukcja | Ochrona |
| --- | --- | --- |
| VARIABLE | direct_variable_cost / unit_cost_denominator | wybrany denominator musi odpowiadać temu samemu scope i warstwie |
| COMMITTED | direct_committed_cost / unit_cost_denominator | koszt utrzymania zdolności / zakresu na ten sam jawny denominator |
| FULL | attributable_total_cost / unit_cost_denominator | pełny koszt przypisany do scope przy poprawnym shared cost attribution gate |
| LABOR | unit_labor_cost zgodny z HR-01 | nie twórz drugiej definicji ULC |
| WORK_CONTENT_BASED | documented_cost_numerator / unit_cost_denominator | dla denominator_type = work_content; nie zastępuje innych denominator types |

### 3.2. attributable_total_cost i FULL gate

attributable_total_cost_period obejmuje direct_variable_cost_period, direct_committed_cost_period, attributable_shared_cost_period oraz inne udokumentowane koszty należące do unit_cost_scope w tym samym okresie, bez podwójnego liczenia. attributable_total_cost_current i attributable_total_cost_reference korzystają z właściwej dla danego okresu struktury shared cost.

> **FULL UNIT COST GATE FULL wymaga odpowiedzialnej atrybucji całego kosztu do unit_cost_scope osobno dla current i reference. direct_in_scope nie wymaga klucza alokacyjnego; allocated_from_parent_scope wymaga allocation_basis_period i odpowiedniej allocation_quality_period; przy mixed gate dotyczy wyłącznie części alokowanej. Różna metoda atrybucji między okresami wymaga shared_cost_attribution_comparability. Brak porównywalności może pozostawić FULL current/reference jako poprawne wartości okresowe, lecz FULL gap/bridge = null / TEST_PARTIAL. VARIABLE i COMMITTED pozostają niezależne od tej bramki.**

Dla każdego okresu osobno: attributable_shared_cost_period = direct_in_scope_shared_cost_period + allocated_shared_cost_period. allocated_shared_cost_period pozostaje pochodną alokacją części shared cost z wyższego scope. Koszt wspólny, który już bezpośrednio należy do badanego unit_cost_scope, nie wymaga sztucznego klucza alokacyjnego. Nie dodaje się jednocześnie całego shared_cost i allocated_shared_cost dla tej samej puli. Zmiana metody atrybucji między current i reference jest jawna i nie może zostać automatycznie uznana za zmianę ekonomiczną.

| Pole | Kontrakt |
| --- | --- |
| shared_cost_attribution_type_current | direct_in_scope / allocated_from_parent_scope / mixed / none – osobno dla current |
| shared_cost_attribution_type_reference | direct_in_scope / allocated_from_parent_scope / mixed / none – osobno dla reference |
| direct_in_scope_shared_cost_current | część shared cost źródłowo i bezpośrednio należąca do badanego unit_cost_scope w current; nie wymaga allocation_basis |
| direct_in_scope_shared_cost_reference | analogiczna bezpośrednia część shared cost dla reference |
| allocated_shared_cost_current | część current przeniesiona z parent scope; wymaga allocation_basis_current i odpowiedniej allocation_quality_current |
| allocated_shared_cost_reference | część reference przeniesiona z parent scope; wymaga allocation_basis_reference i odpowiedniej allocation_quality_reference |
| attributable_shared_cost_current | direct_in_scope_shared_cost_current + allocated_shared_cost_current; składniki rozłączne, bez double count |
| attributable_shared_cost_reference | direct_in_scope_shared_cost_reference + allocated_shared_cost_reference; składniki rozłączne, bez double count |
| allocation_basis_current | źródło i reguła alokacji current, jeżeli występuje część allocated_from_parent_scope |
| allocation_basis_reference | źródło i reguła alokacji reference, jeżeli występuje część allocated_from_parent_scope |
| allocation_quality_current | jakość alokacji current; dotyczy wyłącznie części alokowanej |
| allocation_quality_reference | jakość alokacji reference; dotyczy wyłącznie części alokowanej |
| shared_cost_attribution_comparability | true / false / null-not_assessable; czy metody atrybucji shared cost current/reference są odpowiedzialnie porównywalne dla FULL gap/bridge |
| shared_cost_attribution_change_flag | true, gdy metoda atrybucji shared cost różni się między current i reference; sama zmiana metody nie jest zmianą ekonomiczną |
| FULL gate | FULL current/reference liczy się oddzielnie z poprawnej struktury okresowej. FULL gap/bridge wymaga dodatkowo shared_cost_attribution_comparability=true. Brak tej porównywalności nie blokuje VARIABLE/COMMITTED. |

### 3.3. LABOR i uzgodnienie z HR-01

FIN-03 nie redefiniuje unit_labor_cost. Gdy scope, labor_cost, labor_input/comparable_effect oraz mianownik są identyczne z HR-01, wynik warstwy LABOR musi uzgodnić się z HR-01. labor_rate i productivity pozostają explanatory evidence.

## 4. Walidacja danych FIN03-VAL-01–64

Każda kontrola zwraca PASS, WARNING albo CRITICAL. CRITICAL zatrzymuje moduł zależny; WARNING pozwala kontynuować z validation_required i validation_notes. Brak podstawy pozostawia miarę null / not_computable; nie tworzy wartości zastępczej.

| Id | Kontrola | Skutek negatywny |
| --- | --- | --- |
| FIN03-VAL-01 | unit_cost_scope jest jawny i stabilny | CRITICAL dla porównania |
| FIN03-VAL-02 | unit_cost_layer jest jawny | CRITICAL dla interpretacji |
| FIN03-VAL-03 | activity_unit istnieje | CRITICAL dla unit cost |
| FIN03-VAL-04 | activity_unit_basis jest jednoznaczna | CRITICAL/WARNING |
| FIN03-VAL-05 | activity_volume_current istnieje, jeśli denominator_type=activity_volume albo volume jest używane pomocniczo | CRITICAL tylko dla zależnego volume-based UC; inaczej WARNING/null source |
| FIN03-VAL-06 | activity_volume_reference istnieje dla porównania, jeśli denominator_type=activity_volume | WARNING/CRITICAL dla zależnego volume-based comparison |
| FIN03-VAL-07 | unit_cost_denominator_current i reference mają osobną walidację >0 / valid_period dla zależnych unit cost | CRITICAL tylko dla miary danego okresu; brak reference nie blokuje poprawnego current |
| FIN03-VAL-08 | negative activity_volume jest wyjaśniony; jeśli jest wybranym denominatorem → unit cost null | CRITICAL dla volume-based UC bez wyjaśnienia |
| FIN03-VAL-09 | volume_comparability jest znana | WARNING/CRITICAL |
| FIN03-VAL-10 | activity_recognition_comparability jest znana | WARNING/CRITICAL |
| FIN03-VAL-11 | weighted_volume ma udokumentowany basis, jeśli używany | CRITICAL dla weighted UC |
| FIN03-VAL-12 | weighting_quality jest wystarczająca i stabilna current/reference | WARNING/CRITICAL |
| FIN03-VAL-13 | brak arbitralnych wag | CRITICAL przy wykryciu |
| FIN03-VAL-14 | work_content ma jawny work_content_unit/basis, jeśli używany | CRITICAL dla work-content UC |
| FIN03-VAL-15 | work_content i activity_volume nie są utożsamiane | CRITICAL dla błędnego mianownika |
| FIN03-VAL-16 | cost numerator i unit_cost_denominator dotyczą tego samego scope/okresu | CRITICAL |
| FIN03-VAL-17 | cost coverage jest znane | WARNING/CRITICAL |
| FIN03-VAL-18 | direct_variable_cost zachowuje FIN-02/PORT-01 | CRITICAL dla VARIABLE |
| FIN03-VAL-19 | direct_committed_cost zachowuje FIN-02/PORT-01 | CRITICAL dla COMMITTED |
| FIN03-VAL-20 | shared cost przenoszony z parent scope ma allocation_basis; direct_in_scope nie wymaga sztucznej alokacji | CRITICAL dla zależnej części FULL |
| FIN03-VAL-21 | allocation_quality jest wymagana wyłącznie dla allocated_from_parent_scope / części mixed | WARNING/CRITICAL |
| FIN03-VAL-22 | direct_in_scope_shared_cost i allocated_shared_cost są rozłączne; attributable_shared_cost nie double countuje shared | CRITICAL |
| FIN03-VAL-23 | attributable_total_cost ma jawny scope i obejmuje attributable_shared_cost bez double count | CRITICAL dla FULL |
| FIN03-VAL-24 | matched_activity_scope jest jawny przy bridge matched | CRITICAL |

| Id | Kontrola | Skutek negatywny |
| --- | --- | --- |
| FIN03-VAL-25 | new/discontinued/materially_changed są poza matched bridge | WARNING/CRITICAL |
| FIN03-VAL-26 | matched_cost i matched_unit_cost_denominator należą do tego samego matched_activity_scope | CRITICAL |
| FIN03-VAL-27 | gross_activity_volume i good_output_volume są rozdzielone | WARNING/CRITICAL |
| FIN03-VAL-28 | yield_rate używa gross>0 i zgodnego scope | WARNING/CRITICAL |
| FIN03-VAL-29 | rework jest źródłowo potwierdzony | WARNING; rework fields=null bez podstawy |
| FIN03-VAL-30 | rework nie zwiększa automatycznie good_output | CRITICAL dla mianownika |
| FIN03-VAL-31 | oneoff_flag ma oneoff_basis | WARNING |
| FIN03-VAL-32 | adjusted_unit_cost ma adjustment_basis i actual pozostaje widoczny | CRITICAL dla adjusted |
| FIN03-VAL-33 | negative_cost_flag jest ustawiony i kontekst wyjaśniony | WARNING/CRITICAL |
| FIN03-VAL-34 | accounting_basis_comparability jest znana | WARNING/CRITICAL |
| FIN03-VAL-35 | cost_classification_comparability jest znana | WARNING/CRITICAL |
| FIN03-VAL-36 | unit_cost_reclassification_flag rozpoznaje przesunięcia klas | WARNING/CRITICAL |
| FIN03-VAL-37 | referencja jest źródłowa i porównywalna | WARNING; gap=null |
| FIN03-VAL-38 | horyzont current/reference jest zgodny | CRITICAL dla porównania |
| FIN03-VAL-39 | 3M/6M/12M liczone jako Σcost / Σtego samego unit_cost_denominator_type | CRITICAL przy średniej miesięcznych UC lub zmianie denominator type |
| FIN03-VAL-40 | bridge_scope jest jawny i zgodny z full/matched | CRITICAL |
| FIN03-VAL-41 | cost_effect_signed i denominator_effect_signed używają tego samego bridge_scope i bridge denominator contract | CRITICAL |
| FIN03-VAL-42 | unit cost bridge uzgadnia bridge_unit_cost_gap_signed = cost_effect_signed + denominator_effect_signed | CRITICAL przy istotnej niezgodności |
| FIN03-VAL-43 | brak balancing item | CRITICAL |
| FIN03-VAL-44 | adverse/compensating effects używają cost_effect i denominator_effect z tego samego scope/denominator | CRITICAL |
| FIN03-VAL-45 | unit_cost_coverage_current/reference mają wspólną basis zgodną z denominator type albo jawnie inną miarę | WARNING/CRITICAL |
| FIN03-VAL-46 | unit_cost_coverage current/reference używa wspólnej basis | WARNING/CRITICAL; niezgodność → null |
| FIN03-VAL-47 | uzgodnienia FIN-02/PORT/HR wykonane, gdy scope identyczny | WARNING/CRITICAL zależnie od warstwy |
| FIN03-VAL-48 | explanatory_evidence nie jest dodawane do bridge | CRITICAL przy double count |
| FIN03-VAL-49 | unit_cost_denominator_type/current/reference/unit/basis/comparability oraz valid_current/valid_reference tworzą kompletny kontrakt | CRITICAL dla niejednoznacznego mianownika; local period validity oceniana niezależnie |
| FIN03-VAL-50 | dla gap/change/bridge current i reference używają tego samego denominator_type i zgodnej unit/basis | CRITICAL wyłącznie dla porównania; nie usuwa poprawnej miary pojedynczego okresu |
| FIN03-VAL-51 | bridge_denominator_type/current/reference/unit odpowiada denominatorowi właściwemu dla bridge_scope | CRITICAL dla bridge |
| FIN03-VAL-52 | volume_effect_signed jest aliasem tylko dla activity_volume/weighted_volume/good_output_volume; dla work_content/inherited_hr_effect = null | CRITICAL dla błędnej semantyki efektu |
| FIN03-VAL-53 | matched_unit_cost_denominator current/reference/type/basis należą do tego samego matched_activity_scope co matched_cost | CRITICAL dla matched bridge |
| FIN03-VAL-54 | unit_cost_coverage_basis obejmuje wymagane typy i jest wspólna current/reference | WARNING/CRITICAL; niezgodność → coverage null |
| FIN03-VAL-55 | shared_cost_attribution_type_current/reference rozróżniają direct_in_scope, allocated_from_parent_scope, mixed i none osobno dla obu okresów | CRITICAL dla FULL danego okresu przy niejednoznacznej atrybucji |
| FIN03-VAL-56 | attributable_shared_cost_current/reference = direct_in_scope + allocated osobno dla okresu, bez double count; allocation gate dotyczy tylko części alokowanej | CRITICAL dla FULL danego okresu |
| FIN03-VAL-57 | unit_cost_denominator_valid_current ocenia current niezależnie od reference i cross-period comparability | CRITICAL wyłącznie dla unit_cost_current, jeśli denominator current nie jest poprawny |
| FIN03-VAL-58 | unit_cost_denominator_valid_reference ocenia reference niezależnie od current | CRITICAL wyłącznie dla unit_cost_reference i porównań zależnych |
| FIN03-VAL-59 | brak lub nieporównywalna reference nie usuwa poprawnego unit_cost_current | WARNING; reference/gap/change/bridge=null; TEST_PARTIAL, jeśli current pozostaje wiarygodny |
| FIN03-VAL-60 | gap, adverse gap, change rate i bridge wymagają denominator_comparability=true oraz zgodnych type/unit/basis current/reference | CRITICAL dla porównania; samodzielne miary okresowe mogą pozostać |
| FIN03-VAL-61 | shared cost attribution fields, allocation_basis i allocation_quality są prowadzone osobno dla current i reference | WARNING/CRITICAL dla FULL zależnie od brakującego okresu |
| FIN03-VAL-62 | attributable_shared_cost_period = direct_in_scope_shared_cost_period + allocated_shared_cost_period bez double count dla obu okresów | CRITICAL dla FULL danego okresu |
| FIN03-VAL-63 | shared_cost_attribution_comparability i shared_cost_attribution_change_flag ujawniają zmianę metody między okresami | WARNING/CRITICAL dla FULL comparison; zmiana metody ≠ zmiana ekonomiczna |
| FIN03-VAL-64 | przy nieuzgodnionej metodzie atrybucji FULL gap/bridge pozostają null/TEST_PARTIAL, a VARIABLE/COMMITTED nadal mogą działać | CRITICAL, jeśli system fałszywie blokuje niższe warstwy lub udaje FULL comparability |

## 5. Obliczenia kosztu jednostkowego i signed gap

| variable_unit_cost | direct_variable_cost_period / unit_cost_denominator_period / denominator_period >0, unit_cost_denominator_valid_period=true i ten sam scope/okres. |
| --- | --- |

| committed_unit_cost | direct_committed_cost_period / unit_cost_denominator_period / Ten sam okresowy denominator contract; porównywalność current/reference nie jest warunkiem samodzielnego wyniku okresu. |
| --- | --- |

| full_unit_cost | attributable_total_cost_period / unit_cost_denominator_period / Tylko przy przejściu okresowego FULL gate i poprawnym denominatorze tego okresu; FULL gap/bridge dodatkowo wymagają porównywalności current/reference. |
| --- | --- |

| unit_cost_gap_signed | unit_cost_current − unit_cost_reference / Dodatnia wartość = pogorszenie kosztowe. Wymaga unit_cost_denominator_comparability=true oraz zgodnych type/unit/basis current/reference; inaczej null. |
| --- | --- |

| adverse_unit_cost_gap | max(unit_cost_gap_signed, 0) / Jeżeli signed gap=null, adverse gap=null. Nie jest automatycznie oszczędnością ani potencjałem. |
| --- | --- |

| unit_cost_change_rate | unit_cost_current / unit_cost_reference − 1 / Tylko gdy unit_cost_reference>0 oraz comparison gate jest spełniony. Miara pomocnicza, nie jedyna. |
| --- | --- |

### 5.1. Zero i ujemne wartości

| Sytuacja | Wynik techniczny |
| --- | --- |
| unit_cost_denominator_current = 0 albo valid_current ≠ true | unit_cost_current = null / not_computable; reference może pozostać dostępny, jeśli jego podstawa jest poprawna |
| unit_cost_denominator_reference = 0 albo valid_reference ≠ true | unit_cost_reference = null; unit_cost_current pozostaje dostępny, jeżeli current jest poprawny; gap/change/bridge = null; zwykle TEST_PARTIAL |
| unit_cost_denominator < 0 | unit cost dla danego okresu = null; validation_required; pole źródłowe wymaga wyjaśnienia |
| unit_cost_denominator_comparability ≠ true | poprawne unit_cost_current i/lub unit_cost_reference mogą pozostać widoczne; gap/adverse/change/bridge = null; TEST_PARTIAL zamiast fałszywego TEST_BLOCKED, jeśli current metric jest odpowiedzialnie obliczalna |
| brak wiarygodnej reference | unit_cost_current pozostaje dostępny przy valid_current=true; unit_cost_reference/gap/change/bridge=null; TEST_PARTIAL |
| cost <0 | negative_cost_flag=true; amount zachowany, interpretacja wymaga kontekstu |

## 6. Dokładny most kosztu jednostkowego – dekompozycja Shapleya

FIN-03 wybiera jedną obowiązującą metodę mostu dla funkcji UC = C / D: symetryczną dekompozycję Shapleya dla kosztu i faktycznie użytego mianownika. Zapewnia ona brak arbitralnej kolejności czynników i dokładną addytywną rekonsyliację. D oznacza bridge_denominator zgodny z unit_cost_denominator właściwym dla bridge_scope.

> **DECYZJA METODOLOGICZNA W FIN-03 v1.0 obowiązuje wyłącznie dokładna dekompozycja Shapleya dla dwóch czynników: cost i denominator. Nie stosuje się przybliżenia pochodnych ani alternatywnej kolejności czynników.**

| oznaczenia | C0 = bridge_cost_reference; C1 = bridge_cost_current; D0 = bridge_denominator_reference; D1 = bridge_denominator_current |
| --- | --- |

| cost_effect_signed | 0,5 × [(C1/D0 − C0/D0) + (C1/D1 − C0/D1)] Równoważnie: 0,5 × (C1 − C0) × (1/D0 + 1/D1). |
| --- | --- |

| denominator_effect_signed | 0,5 × [(C0/D1 − C0/D0) + (C1/D1 − C1/D0)] Równoważnie: 0,5 × (C0 + C1) × (1/D1 − 1/D0). |
| --- | --- |

| volume_effect_signed | alias = denominator_effect_signed wyłącznie gdy bridge_denominator_type ∈ {activity_volume, weighted_volume, good_output_volume}. Dla work_content albo inherited_hr_effect: volume_effect_signed = null. |
| --- | --- |

| tożsamość | bridge_unit_cost_gap_signed = cost_effect_signed + denominator_effect_signed Dokładnie w granicach wyłącznie technicznej tolerancji numerycznej. |
| --- | --- |

| unit_cost_bridge_reconciliation_gap | bridge_unit_cost_gap_signed − cost_effect_signed − denominator_effect_signed Istotna niezgodność → validation_required; bez balancing item. |
| --- | --- |

### 6.1. Znaczenie znaków

| Efekt | Dodatni | Ujemny |
| --- | --- | --- |
| cost_effect_signed | zmiana kosztu kwotowego pogarsza unit cost | zmiana kosztu kompensuje / poprawia unit cost |
| denominator_effect_signed | zmiana faktycznie użytego mianownika pogarsza unit cost | zmiana faktycznie użytego mianownika kompensuje / poprawia unit cost |

> **PRZYKŁAD INTERPRETACYJNY Koszt kwotowy może być stabilny, a unit cost rosnąć wyłącznie dlatego, że wybrany mianownik spadł. Wtedy denominator_effect_signed > 0. Jeżeli mianownik jest wolumenowy, volume_effect_signed może być aliasem. Przy work_content nie wolno nazywać tej zmiany „efektem wolumenu”.**

### 6.2. bridge_scope

| bridge_scope | Wejścia | Gap do uzgodnienia |
| --- | --- | --- |
| full_scope | bridge_cost_current/reference oraz bridge_denominator_current/reference dla pełnego, porównywalnego scope | unit_cost_gap_signed |
| matched_scope | wyłącznie matched_cost_current/reference oraz matched_unit_cost_denominator_current/reference z tego samego matched_activity_scope | matched_unit_cost_gap_signed |

Przy new/discontinued/materially_changed scope podstawowym bridge porównawczym jest matched_scope. Nie wolno uzgadniać matched bridge z full-scope gap. Bridge wymaga poprawnych mianowników obu okresów oraz unit_cost_denominator_comparability=true dla użytego scope. Brak porównywalnej reference pozostawia poprawny current unit cost, ale bridge = null.

| Pole | Kontrakt |
| --- | --- |
| bridge_denominator_type | musi odpowiadać unit_cost_denominator_type właściwemu dla bridge_scope |
| bridge_denominator_current | full: unit_cost_denominator_current; matched: matched_unit_cost_denominator_current |
| bridge_denominator_reference | full: unit_cost_denominator_reference; matched: matched_unit_cost_denominator_reference |
| bridge_denominator_unit | ta sama jednostka dla current/reference i zgodna z bridge_denominator_type |
| comparison gate | bridge current/reference musi mieć poprawne denominatory obu okresów, unit_cost_denominator_comparability=true oraz zgodne denominator_type, denominator_unit i porównywalną denominator_basis; inaczej bridge=null. |

### 6.3. Udziały adverse i compensating effects

| adverse_unit_cost_effect_i | max(effect_signed_i, 0) |
| --- | --- |

| adverse_unit_cost_effect_share_i | adverse_unit_cost_effect_i / Σ adverse_unit_cost_effect Suma 0 → null. Mianownik wyłącznie dla tego samego bridge_scope, unit_cost_layer, current/reference i podstawy mianownika. |
| --- | --- |

Ujemne cost_effect_signed i denominator_effect_signed są zachowane osobno jako compensating_unit_cost_effects. volume_effect_signed jest tylko warunkowym aliasem denominator_effect_signed dla denominator types opartych na wolumenie. Efektów kompensujących nie odejmuje się z mianownika udziałów adverse.

## 7. Miks, pracochłonność, rework, gross/good output i yield

### 7.1. Miks

Jeżeli activity_volume obejmuje heterogeniczny miks, bridge z bridge_denominator_type = activity_volume może być mylący. FIN-03 nie wciska mix effect do dwuczynnikowego bridge. Stosuje weighted_volume przy poprawnych wagach albo pozostawia mix_comparability=false i korzysta z PORT-01 jako explanatory evidence.

### 7.2. Work content

Wzrost work_content_per_activity_unit może wskazywać na większą pracochłonność przy stabilnym volume. Jest to warstwa wyjaśniająca. work_content_effect_evidence nie jest automatycznie trzecim składnikiem księgowego bridge.

### 7.3. Rework i output

| Pole | Reguła |
| --- | --- |
| rework_cost | koszt dodatkowej, źródłowo potwierdzonej pracy poprawkowej |
| rework_work_content | dodatkowy work_content potwierdzonego rework |
| rework_activity_count | liczba technicznych powtórzeń; nie final output bez podstawy |
| gross_activity_volume | cała aktywność techniczna, w tym ewentualne poprawki/odrzuty |
| good_output_volume | zaakceptowany efekt końcowy właściwy dla mianownika ekonomicznego |
| yield_rate | good_output_volume / gross_activity_volume przy gross>0 |

> **OCHRONA Rework nie zwiększa automatycznie good_output_volume. Koszt jednostkowy efektu końcowego powinien używać good_output_volume, gdy to właśnie zaakceptowany rezultat jest właściwym mianownikiem ekonomicznym.**

## 8. Explanatory evidence – bez dodawania do bridge

| Pole | Znaczenie |
| --- | --- |
| cost_amount_evidence | zmiana licznika kosztowego |
| volume_evidence | zmiana porównywalnego mianownika |
| mix_evidence | zmiana struktury działalności / PORT |
| labor_rate_evidence | HR-01: cena jednostki nakładu pracy |
| labor_productivity_evidence | HR-01: produktywność |
| work_content_evidence | zmiana pracochłonności |
| capacity_underutilization_evidence | CAP-01: wykorzystanie spada przy utrzymanym committed cost |
| capacity_pressure_evidence | CAP-02: pressure / extra capacity dependency |
| rework_evidence | potwierdzony rework |
| process_evidence | PROC: delay/constraint/handoff/batching jako możliwy mechanizm |
| yield_evidence | spadek good/gross |
| input_price_evidence | udokumentowana zmiana ceny inputu |
| accounting_change_evidence | zmiana cost/activity recognition |
| data_quality_evidence | braki, nieporównywalność, reconciliation |

Każde evidence przyjmuje true / false / null-not_assessable. Brak danych ≠ false. Explanatory evidence opisuje możliwe mechanizmy, ale nie jest dodawane do cost_effect_signed ani denominator_effect_signed. mix, work_content, CAP, HR i PROC nie mogą zostać przedstawione jako dodatkowe „100%” bridge bez odrębnej matematyki.

### 8.1. Relacje z testami zamrożonymi

| Test | Sygnał | Granica |
| --- | --- | --- |
| FIN-02 | cost load erosion vs unit-cost movement | zgodny sygnał, ale nie tożsamość przyczynowa |
| PORT-01 | mix / ekonomika produktów | mix evidence; bez drugiego mix modelu |
| HR-01 | unit labor cost, labor rate, productivity, work_content | wymagane uzgodnienie ULC przy identycznym scope |
| CAP-01 | underutilization | możliwy wzrost committed UC przez mniejszy denominator |
| CAP-02 | pressure / extra capacity | możliwy wzrost variable/labor cost; gap capacity ≠ bridge component |
| PROC-01 | rework/czas | czas ≠ koszt; tylko evidence przy kosztowej podstawie |
| PROC-02 | constraint_status / constraint_entity_type | constraint może wpływać na output, ale status pozostaje własnością PROC-02 |

### 8.2. Koszt na jednostkę rzeczywiście ograniczonej capacity

Opcjonalne cost_per_constraint_unit może być pokazane wyłącznie wtedy, gdy PORT-01/CAP-02/PROC-02 dostarczają wiarygodną jednostkę ograniczenia i właściwy scope. Jest to miara pomocnicza; FIN-03 nie projektuje nowej ekonomiki constraintu ani nie uznaje constraint_status za składnik mostu cost/denominator.

## 9. Matched activity scope, coverage i zmiany strukturalne

### 9.1. matched_activity_scope

matched_activity_scope obejmuje wyłącznie działalność porównywalną current/reference. Nowe, wycofane i materially changed elementy pozostają poza matched unit-cost bridge.

| Pole | Kontrakt |
| --- | --- |
| matched_cost_current; matched_cost_reference | licznik właściwy dla unit_cost_layer w dokładnie tym samym matched_activity_scope |
| matched_unit_cost_denominator_current; matched_unit_cost_denominator_reference | faktyczny denominator current/reference należący do dokładnie tego samego matched_activity_scope co matched_cost |
| matched_unit_cost_current; matched_unit_cost_reference | każdy okres osobno: matched_cost / matched_unit_cost_denominator przy denominator>0 i poprawnej okresowej podstawie; matched gap/bridge wymagają dopiero porównywalności current/reference |
| matched_unit_cost_gap_signed | matched_unit_cost_current − matched_unit_cost_reference |
| adverse_matched_unit_cost_gap | max(matched_unit_cost_gap_signed,0) |
| bridge_scope | full_scope / matched_scope; strukturalne zmiany preferują matched_scope |
| matched_unit_cost_denominator_type | activity_volume / weighted_volume / good_output_volume / work_content / inherited_hr_effect; identyczny current/reference |
| matched_unit_cost_denominator_basis | źródło i reguła denominatora matched; nie zakłada automatycznie matched_activity_volume |

### 9.2. unit_cost_coverage

| Pole | Znaczenie |
| --- | --- |
| unit_cost_coverage_current | pokrycie current na jawnej basis |
| unit_cost_coverage_reference | pokrycie reference na tej samej basis |
| unit_cost_coverage_basis | activity_volume / weighted_volume / good_output_volume / work_content / cost / documented_weight |
| matched_scope_comparability | jakość porównania matched_activity_scope |

> **WSPÓLNA PODSTAWA Current i reference coverage muszą używać tej samej unit_cost_coverage_basis. Jeżeli coverage ocenia mianownik używany przez unit cost, basis musi odpowiadać unit_cost_denominator_type; inna miara pokrycia musi być jawnie opisana. Niezgodna podstawa → coverage porównawcze = null i validation_required.**

### 9.3. Uzgodnienia z FIN-02, PORT-01 i HR-01

| Pole | Reguła |
| --- | --- |
| FIN02_cost_reconciliation_gap | różnica licznika kosztowego FIN-03 i odpowiedniej klasy FIN-02 przy identycznym scope; świadomie inny scope wymaga wyjaśnienia, nie wymuszenia zera |
| PORT_cost_reconciliation_gap | różnica cost attribution / activity basis z PORT-01, gdy analizowany jest portfolio scope |
| HR_unit_labor_cost_reconciliation_gap | różnica warstwy LABOR i unit_labor_cost HR-01 przy identycznym scope/mianowniku |
| reconciliation_notes | jawne przyczyny różnic: scope, okres, klasyfikacja, allocation, activity recognition |

FIN-03 nie tworzy drugiej wersji kosztu ani działalności. Niezgodność bez wyjaśnienia zasila validation_required i ZOP-CONF-01.

## 10. Accounting basis, reclassification, one-off i adjusted view

| Pole | Reguła |
| --- | --- |
| accounting_basis_comparability | porównywalność sposobu ujęcia kosztów |
| cost_classification_comparability | porównywalność klas variable/committed/shared/other |
| activity_recognition_comparability | porównywalność momentu i definicji rozpoznania activity |
| unit_cost_reclassification_flag | przesunięcie kosztu między warstwami przy niezmienionym total attributable cost |
| oneoff_flag / oneoff_basis | actual pozostaje; zdarzenie zmienia interpretację |
| adjusted_unit_cost / adjustment_basis | opcjonalny widok źródłowo udokumentowany; nie zastępuje actual |

Reclassification variable → committed albo committed → shared może zmienić warstwy VARIABLE/COMMITTED, ale przy niezmienionym attributable_total_cost nie może stworzyć fałszywego movement FULL unit cost.

## 11. Horyzonty, agregacja, referencja i standard cost

### 11.1. Horyzonty

| Horyzont | Reguła |
| --- | --- |
| 1M | sygnał bieżący |
| 3M | Σcost / Σunit_cost_denominator w całym oknie |
| 6M | Σcost / Σunit_cost_denominator; trwałość |
| 12M / r/r | Σcost / Σunit_cost_denominator dla porównywalnych 12M |
| 24–36M | trend, sezonowość i zmiany strukturalne przy danych |

> **AGREGACJA Nie uśredniaj miesięcznych unit costs prostą średnią przy różnych mianownikach. Najpierw sumuj koszt i wybrany, porównywalny unit_cost_denominator w całym oknie, następnie licz unit cost. Nie przełączaj denominator_type między okresami.**

### 11.2. Hierarchia referencji

| Priorytet | Źródło | Warunek |
| --- | --- | --- |
| 1 | ten sam matched activity scope | ta sama activity_unit/basis i cost basis |
| 2 | wcześniejszy porównywalny okres | zgodność struktury i sezonu |
| 3 | plan | jawna definicja unit cost |
| 4 | standard kosztowy | wyłącznie źródłowy standard_unit_cost |
| 5 | porównywalna jednostka wewnętrzna | udokumentowana comparability |
| 6 | najlepszy własny stabilny okres | bez zdarzenia zaburzającego |
| 7 | benchmark zewnętrzny | wiarygodne źródło i zgodne definicje |

| unit_cost_vs_standard_gap_signed | unit_cost_current − standard_unit_cost Tylko przy udokumentowanym standard_unit_cost_basis. Brak standardu → null. |
| --- | --- |

## 12. Granice interpretacji, hipotezy i next_tests

> **EFFICIENCY ≠ COST Wysoki koszt jednostkowy nie oznacza automatycznie niskiej efektywności. Może wynikać m.in. z droższego inputu, trudniejszego miksu, niższej skali, one-off, rework, niewykorzystania capacity, wyższej jakości albo zmiany zakresu produktu.**

> **UNIT COST ≠ PRICE Koszt jednostkowy nie jest ceną, stawką, taryfą ani przychodem jednostkowym. Relacja unit revenue vs unit cost należy do PORT-01 / FIN-02.**

> **AVERAGE ≠ MARGINAL FIN-03 liczy przede wszystkim średni koszt jednostkowy w zdefiniowanym scope. Nie nazywa go marginal cost. Koszt krańcowy wymaga odrębnej metodologii.**

### 12.1. Hipotezy

Dopuszczalne hipotezy: wzrost kosztu inputu; spadek volume; niekorzystny mix; wzrost pracochłonności; spadek produktywności; rework; spadek yield; niewykorzystanie capacity; extra capacity / overtime; przeciążenie; problem procesu; one-off; reclassification; zmiana activity definition; zmiana cost basis; błąd danych. Każda pozostaje HIPOTEZĄ DO WERYFIKACJI.

### 12.2. next_tests

| next_test | Warunek |
| --- | --- |
| FIN-02 | zmiana unit cost może wpływać na rentowność |
| FIN-01 | problem dotyczy szerszej dynamiki kosztów |
| PORT-01 | miks lub ekonomika produktów wyjaśnia zmianę |
| HR-01 | labor rate/productivity/work content jest podejrzane |
| CAP-01 | mianownik maleje przy niewykorzystaniu capacity |
| CAP-02 | koszt rośnie przy pressure / extra capacity |
| PROC-01 | rework lub czas może zwiększać nakład |
| PROC-02 | constraint może wpływać na output |
| MGT-01 | brak właściwego cost attribution lub activity definition |

## 13. Dane dla ZOP-PRI-01, ZOP-CONF-01 i FINDINGS

### 13.1. ZOP-PRI-01 – DO OPRACOWANIA

> **PRI PAYLOAD unit_cost_scope; unit_cost_layer; unit_cost_current; unit_cost_reference; unit_cost_gap_signed; adverse_unit_cost_gap; unit_cost_change_rate; unit_cost_denominator_type; unit_cost_denominator_current; unit_cost_denominator_reference; unit_cost_denominator_unit; unit_cost_denominator_basis; unit_cost_denominator_comparability; unit_cost_denominator_valid_current; unit_cost_denominator_valid_reference; unit_cost_denominator_validation_basis_current; unit_cost_denominator_validation_basis_reference; cost_effect_signed; denominator_effect_signed; volume_effect_signed; bridge_denominator_type; bridge_denominator_current; bridge_denominator_reference; adverse_unit_cost_effect_share; matched_unit_cost_gap_signed; matched_unit_cost_denominator_current; matched_unit_cost_denominator_reference; matched_unit_cost_denominator_type; bridge_scope; shared_cost_attribution_type_current; shared_cost_attribution_type_reference; direct_in_scope_shared_cost_current; direct_in_scope_shared_cost_reference; allocated_shared_cost_current; allocated_shared_cost_reference; attributable_shared_cost_current; attributable_shared_cost_reference; allocation_basis_current; allocation_basis_reference; allocation_quality_current; allocation_quality_reference; shared_cost_attribution_comparability; shared_cost_attribution_change_flag; weighted_volume; work_content_per_activity_unit; yield_rate; rework_evidence; capacity_underutilization_evidence; capacity_pressure_evidence; persistence; trend_direction; economic_scale; affected_units; explanatory_evidence; result_risk; urgent_validation. FIN-03 nie tworzy lokalnego Priority Score ani progów.**

### 13.2. ZOP-CONF-01 – DO OPRACOWANIA

> **CONF PAYLOAD cost_coverage; activity_volume_coverage; unit_cost_coverage_current; unit_cost_coverage_reference; unit_cost_coverage_basis; unit_cost_denominator_type; unit_cost_denominator_unit; unit_cost_denominator_basis; unit_cost_denominator_comparability; unit_cost_denominator_valid_current; unit_cost_denominator_valid_reference; unit_cost_denominator_validation_basis_current; unit_cost_denominator_validation_basis_reference; bridge_denominator_type; matched_unit_cost_denominator_type; matched_unit_cost_denominator_basis; activity_unit_quality; volume_comparability; weighted_volume_quality; work_content_quality; shared_cost_attribution_type_current; shared_cost_attribution_type_reference; allocation_basis_current; allocation_basis_reference; allocation_quality_current; allocation_quality_reference; shared_cost_attribution_comparability; shared_cost_attribution_change_flag; accounting_basis_comparability; cost_classification_comparability; activity_recognition_comparability; matched_scope_comparability; reference_quality; bridge_reconciliation_quality; oneoff_quality; adjustment_quality; manual_validation; exclusion_flags. FIN-03 nie liczy lokalnego Confidence Score.**

### 13.3. Bazowe FINDINGS

| Pole bazowe | Reguła FIN-03 |
| --- | --- |
| test_id | FIN-03 |
| scope | unit_cost_scope + filtry |
| period | current + reference + horyzont |
| status | status logiczny X-Ray |
| finding | komunikat faktograficzny |
| metric_value / reference_value | unit cost i referencja |
| gap | signed gap albo null |
| impact_low / impact_high | tylko przy odrębnej odpowiedzialnej podstawie; nie automatyczny potencjał |
| confidence_score / confidence_class | wynik ZOP-CONF-01 albo null |
| next_tests | tablica id + uzasadnienie |
| validation_required | boolean + validation_notes |

### 13.4. Rozszerzenia FINDINGS FIN-03

| Grupa | Pola techniczne |
| --- | --- |
| Identyfikacja | unit_cost_scope; unit_cost_layer; unit; portfolio_group; portfolio_item; resource_group; process_stage |
| Mianownik | activity_unit; activity_unit_basis; activity_volume_current; activity_volume_reference; weighted_volume_current; weighted_volume_reference; weighted_volume_basis; volume_comparability; unit_cost_denominator_type; unit_cost_denominator_current; unit_cost_denominator_reference; unit_cost_denominator_unit; unit_cost_denominator_basis; unit_cost_denominator_comparability; unit_cost_denominator_valid_current; unit_cost_denominator_valid_reference; unit_cost_denominator_validation_basis_current; unit_cost_denominator_validation_basis_reference |
| Work content / output | work_content_current; work_content_reference; work_content_per_activity_unit; gross_activity_volume; good_output_volume; yield_rate |
| Koszt | direct_variable_cost_current; direct_variable_cost_reference; direct_committed_cost_current; direct_committed_cost_reference; shared_cost_attribution_type_current; shared_cost_attribution_type_reference; direct_in_scope_shared_cost_current; direct_in_scope_shared_cost_reference; allocated_shared_cost_current; allocated_shared_cost_reference; attributable_shared_cost_current; attributable_shared_cost_reference; allocation_basis_current; allocation_basis_reference; allocation_quality_current; allocation_quality_reference; shared_cost_attribution_comparability; shared_cost_attribution_change_flag; attributable_total_cost_current; attributable_total_cost_reference |
| Unit cost | unit_cost_current/reference; unit_cost_gap_signed; adverse_unit_cost_gap; unit_cost_change_rate |
| Bridge | bridge_scope; bridge_cost_current/reference; bridge_denominator_type; bridge_denominator_current; bridge_denominator_reference; bridge_denominator_unit; bridge_unit_cost_gap_signed; cost_effect_signed; denominator_effect_signed; volume_effect_signed; unit_cost_bridge_reconciliation_gap; adverse_unit_cost_effect_share; compensating_unit_cost_effects |
| Matched | matched_activity_scope; matched_cost_current; matched_cost_reference; matched_activity_volume_current; matched_activity_volume_reference; matched_unit_cost_denominator_current; matched_unit_cost_denominator_reference; matched_unit_cost_denominator_type; matched_unit_cost_denominator_basis; matched_unit_cost_current; matched_unit_cost_reference; matched_unit_cost_gap_signed; adverse_matched_unit_cost_gap |
| Coverage | unit_cost_coverage_current; unit_cost_coverage_reference; unit_cost_coverage_basis |
| Kontekst | rework_cost; rework_work_content; rework_activity_count; oneoff_flag; adjusted_unit_cost; negative_cost_flag; unit_cost_reclassification_flag |
| Evidence / kontrola | explanatory_evidence; exclusion_flags; validation_notes |

## 14. Statusy logiczne i komunikat zarządczy

| Status | Znaczenie |
| --- | --- |
| NO_ADVERSE_SIGNAL | brak potwierdzonego niekorzystnego odchylenia |
| ADVERSE_SIGNAL | niekorzystna zmiana bez rozstrzygnięcia trwałości/przyczyny |
| INCIDENT | jednorazowe zdarzenie |
| DETERIORATING | trwałe pogorszenie w porównywalnym zakresie |
| STABLE | brak trwałego kierunku |
| IMPROVING | potwierdzona poprawa |
| TEST_PARTIAL | część warstw obliczalna |
| TEST_BLOCKED | brak odpowiedzialnej podstawy zależnego modułu |

> **WZORZEC KOMUNIKATU [STATUS] KOSZT JEDNOSTKOWY „Koszt jednej porównywalnej jednostki w zakresie [scope] wyniósł [unit_cost_current] wobec [unit_cost_reference] w okresie odniesienia, jeżeli reference jest wiarygodna i porównywalna. Użyty mianownik: [unit_cost_denominator_type / unit]. Podpisana zmiana wynosi [unit_cost_gap_signed], jeżeli comparison gate jest spełniony. Most kosztu jednostkowego wskazuje wpływ zmiany kosztu kwotowego [cost_effect] oraz wpływ zmiany faktycznie użytego mianownika [denominator_effect]. Dla mianownika wolumenowego można dodatkowo użyć aliasu volume_effect. Przy braku porównywalnej reference poprawny current metric pozostaje widoczny, a reference/gap/bridge = null i status może być TEST_PARTIAL. Czynniki kompensujące: [compensating effects]. Dane z pozostałych testów wskazują jako możliwe wyjaśnienia [explanatory evidence]. Wynik nie oznacza automatycznie niskiej efektywności ani możliwości obniżenia kosztu o wskazaną lukę. Dalsza weryfikacja: [next_tests].”**

> **NIE GENERUJ AUTOMATYCZNIE „koszt jest za wysoki”; „możemy oszczędzić X”; „trzeba zwiększyć wolumen”; „trzeba zwolnić pracowników”; „trzeba zmniejszyć zasoby”; „należy podnieść cenę”.**

## 15. Scenariusze regresyjne FIN03-T01–T14

| Id | Scenariusz | Dane | Oczekiwane |
| --- | --- | --- | --- |
| FIN03-T01 | stabilny unit cost | Cost i volume stabilne. | NO_ADVERSE_SIGNAL. |
| FIN03-T02 | koszt rośnie, volume stabilny | C↑; V≈. | cost effect adverse; volume effect≈0. |
| FIN03-T03 | koszt stabilny, volume spada | C≈; V↓. | UC↑; adverse volume effect; bez „koszt wzrósł”. |
| FIN03-T04 | cost↑, volume↑ szybciej | UC spada. | cost adverse; volume compensating; overall improvement. |
| FIN03-T05 | cost↓, volume↓↓ | UC rośnie. | cost compensating; volume adverse. |
| FIN03-T06 | zero volume current | V1=0. | unit_cost_current=null. |
| FIN03-T07 | zero volume reference | V0=0. | reference/gap/bridge=null. |
| FIN03-T08 | negative volume | V<0. | validation_required; UC=null. |
| FIN03-T09 | heterogeneous case mix | case count nieporównywalny. | TEST_PARTIAL bez weighted volume. |
| FIN03-T10 | poprawny weighted volume | źródłowe stabilne wagi. | unit cost na weighted activity. |
| FIN03-T11 | arbitralne wagi | brak źródła. | weighted UC blocked. |
| FIN03-T12 | work content denominator | count stabilny; work content↑. | cost/case i cost/work-content osobno. |
| FIN03-T13 | rework | gross↑; good output stabilny. | cost per good output↑; rework evidence. |
| FIN03-T14 | yield spada | good/gross↓. | yield evidence; bez automatycznej przyczyny. |

## 16. Scenariusze regresyjne FIN03-T15–T33

| Id | Scenariusz | Dane | Oczekiwane |
| --- | --- | --- | --- |
| FIN03-T15 | committed cost stabilny + volume↓ | committed C≈; V↓. | committed UC↑; volume effect adverse. |
| FIN03-T16 | capacity underutilization | CAP-01 potwierdza U↓. | capacity_underutilization_evidence. |
| FIN03-T17 | overtime / extra capacity | CAP-02 potwierdza dependency. | capacity_pressure_evidence. |
| FIN03-T18 | labor rate wzrasta | HR-01 potwierdza. | labor_rate_evidence. |
| FIN03-T19 | productivity spada | HR-01 potwierdza. | labor_productivity_evidence. |
| FIN03-T20 | mix worsens | PORT-01 potwierdza miks. | mix evidence; brak double count w bridge. |
| FIN03-T21 | reclassification | variable→committed; total cost bez zmiany. | FULL UC bez fałszywego movement; warstwy mogą się zmienić. |
| FIN03-T22 | shared allocation missing | unit scope; shared cost pochodzi z parent scope; brak allocation_basis/allocation_quality. | VARIABLE/COMMITTED działają; FULL=null/TEST_PARTIAL. direct_in_scope przypadek nie wymaga sztucznej alokacji. |
| FIN03-T23 | one-off | actual UC↑. | actual pokazany; adjusted tylko warunkowo. |
| FIN03-T24 | nowy produkt/jednostka | obecny current, brak reference. | poza matched bridge. |
| FIN03-T25 | discontinued scope | obecny reference, brak current. | poza matched bridge. |
| FIN03-T26 | matched bridge | full zmienia się przez nowy scope; matched stabilny. | matched bridge=0; reconciliation gap=0. |
| FIN03-T27 | fałszywa średnia miesięczna | miesiące mają różne volume. | 12M UC=Σcost/Σvolume; nie średnia miesięcznych UC. |
| FIN03-T28 | accounting/activity definition change | definicja jednostki zmieniona. | TEST_PARTIAL/BLOCKED; brak fałszywego gap. |
| FIN03-T29 | weighted volume jako rzeczywisty mianownik | Raw case count current/reference różni się; weighted volume stabilny; unit_cost_denominator_type=weighted_volume. | unit cost i bridge używają weighted volume; raw count poza Shapley bridge; bridge_denominator_type=weighted_volume. |
| FIN03-T30 | work_content-based bridge | unit_cost_denominator_type=work_content; porównywalny work_content current/reference. | denominator_effect_signed obliczony; volume_effect_signed=null; brak komunikatu „efekt wolumenu”; exact reconciliation. |
| FIN03-T31 | FULL organization vs alokacja w dół | Organization: direct cost=100; shared cost=30; denominator=10. Następnie unit A wymaga części shared z organization. | FULL organization=13/jednostkę bez allocation key; dla unit A allocation_basis/allocation_quality wymagane dla części shared; bez nich VARIABLE/COMMITTED działają, FULL=null/TEST_PARTIAL. |
| FIN03-T32 | current unit cost bez porównywalnej reference | Current: cost=120; denominator=10; unit_cost_denominator_valid_current=true. Reference: brak wiarygodnego denominatora albo brak cross-period comparability. | unit_cost_current=12; unit_cost_reference=null; unit_cost_gap_signed=null; bridge=null; current finding dostępny; TEST_PARTIAL; brak fałszywego zablokowania current metric. |
| FIN03-T33 | zmiana metody atrybucji shared cost | Reference: shared cost direct_in_scope. Current: część direct_in_scope, część allocated_from_parent_scope. | oba okresy mają własne attribution fields; brak double count; FULL current/reference tylko przy poprawnej podstawie okresu; różnica metody jawna; bez shared_cost_attribution_comparability FULL gap/bridge nie udają porównywalności; VARIABLE/COMMITTED pozostają dostępne. |

> **PASS SCENARIUSZA Wymaga zgodności walidacji, bridge_scope, unit_cost_denominator contract, null/not_computable, signed/adverse gaps, evidence, next_tests i zakazów interpretacyjnych. Sama poprawna liczba nie wystarcza. Zestaw regresyjny: FIN03-T01–T33.**

## 17. Przebieg implementacji

| Krok | Operacja | Warunek |
| --- | --- | --- |
| 1 | ustal unit_cost_scope, unit_cost_layer i unit_cost_denominator_type/basis | jawny licznik i jeden faktycznie użyty mianownik |
| 2 | zwaliduj unit_cost_denominator_current i reference osobno | valid_current/valid_reference oceniają każdy okres niezależnie; comparability jest osobnym cross-period gate |
| 3 | ustal cost numerator i okresową strukturę shared cost attribution | current/reference osobno; direct_in_scope bez sztucznej alokacji; allocated część ma własny basis/quality |
| 4 | wykonaj FIN03-VAL-01–64 | PASS/WARNING/CRITICAL per moduł |
| 5 | oblicz unit_cost_current i unit_cost_reference niezależnie | brak reference nie usuwa poprawnego current; gap/change dopiero przy comparability=true |
| 6 | wybierz bridge_scope i C0/C1/D0/D1 | bridge tylko przy poprawnych obu okresach i porównywalnym denominator contract |
| 7 | oblicz Shapley cost_effect i denominator_effect | volume_effect tylko warunkowy alias dla denominatorów wolumenowych |
| 8 | zapisz adverse shares i compensating effects | ta sama warstwa/scope/reference |
| 9 | dołącz evidence PORT/HR/CAP/PROC | bez dodawania do bridge |
| 10 | zapisz FINDINGS, PRI/CONF payload i next_tests | bez lokalnych score i decyzji |

## 18. Kryteria odbioru implementacji FIN03-ACC-01–90

| Id | Kontrola / status | Id | Kontrola / status |
| --- | --- | --- | --- |
| FIN03-ACC-01 | zachowuje semantykę FIN-02 dla klas kosztu i comparability – PASS | FIN03-ACC-02 | zachowuje activity_unit/weighted_volume PORT-01 – PASS |
| FIN03-ACC-03 | zachowuje unit_labor_cost HR-01 bez redefinicji – PASS | FIN03-ACC-04 | zachowuje CAP evidence bez zmiany matematyki – PASS |
| FIN03-ACC-05 | zachowuje PROC evidence bez zmiany statusów – PASS | FIN03-ACC-06 | unit_cost_scope jest jawny – PASS |
| FIN03-ACC-07 | unit_cost_layer jest jawny – PASS | FIN03-ACC-08 | activity_unit_basis jest jawny – PASS |
| FIN03-ACC-09 | simple volume używany tylko przy porównywalności – PASS | FIN03-ACC-10 | weighted_volume wymaga źródłowych wag – PASS |
| FIN03-ACC-11 | arbitralne wagi są blokowane – PASS | FIN03-ACC-12 | work_content ≠ activity_volume – PASS |
| FIN03-ACC-13 | cost_per_work_content_unit ma zgodny scope – PASS | FIN03-ACC-14 | VARIABLE używa direct_variable_cost – PASS |
| FIN03-ACC-15 | COMMITTED używa direct_committed_cost – PASS | FIN03-ACC-16 | FULL używa attributable_total_cost – PASS |
| FIN03-ACC-17 | FULL gate rozróżnia direct_in_scope i allocated shared; allocation_quality tylko dla części alokowanej – PASS | FIN03-ACC-18 | shared_cost / allocated_shared_cost nie są double counted – PASS |
| FIN03-ACC-19 | LABOR uzgadnia HR-01 przy identycznym scope – PASS | FIN03-ACC-20 | matched_activity_scope jest jawny – PASS |
| FIN03-ACC-21 | new scope pozostaje poza matched bridge – PASS | FIN03-ACC-22 | discontinued scope pozostaje poza matched bridge – PASS |
| FIN03-ACC-23 | materially changed scope pozostaje poza matched bridge – PASS | FIN03-ACC-24 | unit_cost_current/reference są obliczane niezależnie na własnej poprawnej podstawie – PASS |
| FIN03-ACC-25 | unit_cost_gap_signed ma poprawny znak – PASS | FIN03-ACC-26 | adverse_unit_cost_gap = max(signed,0) – PASS |
| FIN03-ACC-27 | unit_cost_change_rate tylko przy reference>0 – PASS | FIN03-ACC-28 | bridge_scope = full_scope albo matched_scope – PASS |
| FIN03-ACC-29 | bridge inputs należą do tego samego scope – PASS | FIN03-ACC-30 | Shapley cost_effect ma dokładną formułę – PASS |
| FIN03-ACC-31 | Shapley denominator_effect ma dokładną formułę – PASS | FIN03-ACC-32 | cost effect + denominator effect = bridge gap – PASS |
| FIN03-ACC-33 | unit_cost_bridge_reconciliation_gap ≈0 przy poprawnych danych – PASS | FIN03-ACC-34 | brak balancing item – PASS |
| FIN03-ACC-35 | adverse shares używają tylko dodatnich effects – PASS | FIN03-ACC-36 | adverse shares nie mieszają bridge scopes – PASS |
| FIN03-ACC-37 | compensating effects są zachowane osobno – PASS | FIN03-ACC-38 | mix evidence nie wchodzi do prostego bridge – PASS |

### FIN03-ACC-39–90 – ciąg dalszy

| Id | Kontrola / status | Id | Kontrola / status |
| --- | --- | --- | --- |
| FIN03-ACC-39 | work_content evidence nie wchodzi do bridge – PASS | FIN03-ACC-40 | gross_activity_volume ≠ good_output_volume – PASS |
| FIN03-ACC-41 | rework nie zwiększa good output automatycznie – PASS | FIN03-ACC-42 | yield_rate liczony przy gross>0 – PASS |
| FIN03-ACC-43 | capacity underutilization jest evidence – PASS | FIN03-ACC-44 | capacity pressure jest evidence – PASS |
| FIN03-ACC-45 | process time nie jest automatycznie kosztem – PASS | FIN03-ACC-46 | input price effect pozostaje evidence – PASS |
| FIN03-ACC-47 | zero wybranego unit_cost_denominator daje null/not_computable – PASS | FIN03-ACC-48 | ujemny wybrany denominator daje validation – PASS |
| FIN03-ACC-49 | negative cost jest flagowany – PASS | FIN03-ACC-50 | one-off pozostaje w actual – PASS |
| FIN03-ACC-51 | adjusted view nie zastępuje actual – PASS | FIN03-ACC-52 | accounting basis comparability jest kontrolowana – PASS |
| FIN03-ACC-53 | cost classification comparability jest kontrolowana – PASS | FIN03-ACC-54 | activity recognition comparability jest kontrolowana – PASS |
| FIN03-ACC-55 | reclassification nie tworzy fałszywego FULL movement – PASS | FIN03-ACC-56 | 3M/6M/12M liczone jako Σcost/Σtego samego denominator – PASS |
| FIN03-ACC-57 | nie uśrednia miesięcznych unit costs – PASS | FIN03-ACC-58 | referencja pochodzi z hierarchii – PASS |
| FIN03-ACC-59 | standard_unit_cost ma źródło – PASS | FIN03-ACC-60 | brak arbitralnego target unit cost – PASS |
| FIN03-ACC-61 | unit cost coverage current/reference są osobne – PASS | FIN03-ACC-62 | unit_cost_coverage_basis jest wspólna i zgodna z denominator albo jawnie inną miarą – PASS |
| FIN03-ACC-63 | FIN-02 reconciliation działa przy identycznym scope – PASS | FIN03-ACC-64 | PORT reconciliation działa przy identycznym scope – PASS |
| FIN03-ACC-65 | HR reconciliation działa przy identycznym scope – PASS | FIN03-ACC-66 | explanatory_evidence ma true/false/null – PASS |
| FIN03-ACC-67 | PRI payload kompletny bez Priority Score – PASS | FIN03-ACC-68 | CONF payload kompletny bez Confidence Score – PASS |
| FIN03-ACC-69 | FINDINGS kompletne – PASS | FIN03-ACC-70 | next_tests istnieją z uzasadnieniem – PASS |
| FIN03-ACC-71 | brak automatycznych rekomendacji kosztowych/kadrowych/capacity/cenowych – PASS | FIN03-ACC-72 | brak automatycznej wyceny potencjału – PASS |
| FIN03-ACC-73 | przechodzi FIN03-T01–T33 – PASS | FIN03-ACC-74 | 0 danych SPZOZ/pacjentów i 0 FIN-04 – PASS |
| FIN03-ACC-75 | jawny unit_cost_denominator contract obejmuje type/current/reference/unit/basis/comparability oraz valid_current/valid_reference – PASS | FIN03-ACC-76 | denominator_type/unit/basis są zgodne current/reference wyłącznie dla porównań; current metric nie wymaga reference – PASS |
| FIN03-ACC-77 | bridge_denominator odpowiada unit_cost_denominator właściwemu dla bridge_scope – PASS | FIN03-ACC-78 | volume_effect jest aliasem tylko dla denominatorów wolumenowych; inaczej null – PASS |
| FIN03-ACC-79 | matched denominator należy do tego samego matched_activity_scope co matched_cost – PASS | FIN03-ACC-80 | coverage basis obejmuje activity/weighted/good/work_content/cost/documented_weight – PASS |
| FIN03-ACC-81 | okresowa shared cost attribution current/reference obsługuje direct/allocated/mixed bez double count – PASS | FIN03-ACC-82 | FIN03-T29–T31 przechodzą regresję – PASS |
| FIN03-ACC-83 | unit_cost_denominator_valid_current pozwala zachować poprawny current bez reference – PASS | FIN03-ACC-84 | unit_cost_denominator_valid_reference jest oceniany niezależnie – PASS |
| FIN03-ACC-85 | gap/change/bridge wymagają cross-period comparability i zgodnych type/unit/basis – PASS | FIN03-ACC-86 | brak porównywalnej reference daje TEST_PARTIAL, nie fałszywy TEST_BLOCKED current – PASS |
| FIN03-ACC-87 | shared_cost_attribution_type/current/reference oraz allocation fields są okresowe – PASS | FIN03-ACC-88 | attributable_shared_cost_current/reference uzgadniają direct+allocated bez double count – PASS |
| FIN03-ACC-89 | shared_cost_attribution_comparability/change_flag kontrolują FULL comparison bez blokowania VARIABLE/COMMITTED – PASS | FIN03-ACC-90 | FIN03-T32–T33 przechodzą regresję – PASS |

## 19. Definition of Done FIN03-DOD-01–84

| Id | Kontrola / status | Id | Kontrola / status |
| --- | --- | --- | --- |
| FIN03-DOD-01 | cel i pytanie diagnostyczne – PASS | FIN03-DOD-02 | granica FIN-02 – PASS |
| FIN03-DOD-03 | granica PORT-01 – PASS | FIN03-DOD-04 | unit_cost_scope – PASS |
| FIN03-DOD-05 | activity_unit – PASS | FIN03-DOD-06 | activity_unit_basis – PASS |
| FIN03-DOD-07 | activity_volume – PASS | FIN03-DOD-08 | volume_comparability – PASS |
| FIN03-DOD-09 | weighted_volume – PASS | FIN03-DOD-10 | weighted_volume_basis – PASS |
| FIN03-DOD-11 | weighting_quality – PASS | FIN03-DOD-12 | work_content jako alternatywny mianownik – PASS |
| FIN03-DOD-13 | work_content ≠ activity volume – PASS | FIN03-DOD-14 | unit_cost_layer – PASS |
| FIN03-DOD-15 | VARIABLE unit cost – PASS | FIN03-DOD-16 | COMMITTED unit cost – PASS |
| FIN03-DOD-17 | FULL unit cost – PASS | FIN03-DOD-18 | LABOR unit cost zgodny z HR – PASS |
| FIN03-DOD-19 | WORK_CONTENT_BASED unit cost – PASS | FIN03-DOD-20 | attributable_total_cost – PASS |
| FIN03-DOD-21 | shared cost attribution gate: direct vs allocated – PASS | FIN03-DOD-22 | brak shared double count – PASS |
| FIN03-DOD-23 | signed unit cost gap – PASS | FIN03-DOD-24 | adverse unit cost gap – PASS |
| FIN03-DOD-25 | unit_cost_change_rate – PASS | FIN03-DOD-26 | decyzja Shapley bridge – PASS |
| FIN03-DOD-27 | cost_effect_signed – PASS | FIN03-DOD-28 | denominator_effect_signed + warunkowy volume_effect alias – PASS |
| FIN03-DOD-29 | exact reconciliation – PASS | FIN03-DOD-30 | brak balancing item – PASS |
| FIN03-DOD-31 | adverse unit cost effect share – PASS | FIN03-DOD-32 | compensating effects – PASS |
| FIN03-DOD-33 | mix boundary – PASS | FIN03-DOD-34 | input price evidence – PASS |

### FIN03-DOD-35–84 – ciąg dalszy

| Id | Kontrola / status | Id | Kontrola / status |
| --- | --- | --- | --- |
| FIN03-DOD-35 | work_content evidence – PASS | FIN03-DOD-36 | rework fields – PASS |
| FIN03-DOD-37 | gross output – PASS | FIN03-DOD-38 | good output – PASS |
| FIN03-DOD-39 | yield – PASS | FIN03-DOD-40 | capacity underutilization evidence – PASS |
| FIN03-DOD-41 | capacity pressure evidence – PASS | FIN03-DOD-42 | process evidence – PASS |
| FIN03-DOD-43 | portfolio mix evidence – PASS | FIN03-DOD-44 | matched_activity_scope – PASS |
| FIN03-DOD-45 | matched_cost – PASS | FIN03-DOD-46 | matched denominator contract – PASS |
| FIN03-DOD-47 | matched_unit_cost – PASS | FIN03-DOD-48 | bridge_scope + bridge denominator – PASS |
| FIN03-DOD-49 | coverage current/reference – PASS | FIN03-DOD-50 | coverage basis aligned/disclosed – PASS |
| FIN03-DOD-51 | zero unit_cost_denominator – PASS | FIN03-DOD-52 | ujemny unit_cost_denominator – PASS |
| FIN03-DOD-53 | negative cost – PASS | FIN03-DOD-54 | one-off – PASS |
| FIN03-DOD-55 | adjusted view – PASS | FIN03-DOD-56 | accounting basis – PASS |
| FIN03-DOD-57 | cost classification – PASS | FIN03-DOD-58 | activity recognition – PASS |
| FIN03-DOD-59 | reclassification – PASS | FIN03-DOD-60 | horizons – PASS |
| FIN03-DOD-61 | reference – PASS | FIN03-DOD-62 | standard cost – PASS |
| FIN03-DOD-63 | efficiency boundary – PASS | FIN03-DOD-64 | price boundary – PASS |
| FIN03-DOD-65 | marginal cost boundary – PASS | FIN03-DOD-66 | hypotheses i next_tests – PASS |
| FIN03-DOD-67 | PRI/CONF/FINDINGS + VAL/scenarios/ACC – PASS | FIN03-DOD-68 | status FIN-03 zamknięty do implementacji – PASS |
| FIN03-DOD-69 | unit_cost_denominator contract – PASS | FIN03-DOD-70 | current/reference denominator consistency – PASS |
| FIN03-DOD-71 | generalized Shapley denominator bridge – PASS | FIN03-DOD-72 | volume_effect conditional alias – PASS |
| FIN03-DOD-73 | matched_unit_cost_denominator contract – PASS | FIN03-DOD-74 | coverage basis aligned/disclosed – PASS |
| FIN03-DOD-75 | okresowa shared cost attribution + attributable_shared_cost FULL gate – PASS | FIN03-DOD-76 | FIN03-T01–T33 + zaktualizowane VAL/ACC/Q – PASS |
| FIN03-DOD-77 | period denominator validity current/reference – PASS | FIN03-DOD-78 | cross-period denominator comparability oddzielona od validity – PASS |
| FIN03-DOD-79 | current unit cost zachowany bez porównywalnej reference – PASS | FIN03-DOD-80 | gap/change/bridge null przy braku comparability – PASS |
| FIN03-DOD-81 | shared cost attribution fields prowadzone osobno current/reference – PASS | FIN03-DOD-82 | shared attribution comparability/change flag – PASS |
| FIN03-DOD-83 | FULL comparison gate nie blokuje VARIABLE/COMMITTED – PASS | FIN03-DOD-84 | FIN03-T32–T33 + VAL/ACC/Q – PASS |

## 20. Test końcowy QFIN03-01–104

| Id | Kontrola / status | Id | Kontrola / status |
| --- | --- | --- | --- |
| QFIN03-01 | FIN-03 jest uniwersalny branżowo – PASS | QFIN03-02 | FIN-03 ≠ FIN-02 – PASS |
| QFIN03-03 | FIN-03 ≠ PORT-01 – PASS | QFIN03-04 | cost numerator i wybrany denominator mają ten sam scope – PASS |
| QFIN03-05 | activity_unit jest jawna – PASS | QFIN03-06 | activity_unit_basis jest jawna – PASS |
| QFIN03-07 | activity_unit jest porównywalna – PASS | QFIN03-08 | case count nie jest zawsze właściwym denominator – PASS |
| QFIN03-09 | weighted volume ma źródło – PASS | QFIN03-10 | arbitralne wagi są zabronione – PASS |
| QFIN03-11 | work_content ≠ activity_volume – PASS | QFIN03-12 | variable UC ma poprawny licznik – PASS |
| QFIN03-13 | committed UC ma poprawny licznik – PASS | QFIN03-14 | FULL UC wymaga odpowiedzialnej atrybucji shared cost; allocation_quality tylko dla części alokowanej – PASS |
| QFIN03-15 | shared cost nie jest double counted – PASS | QFIN03-16 | unit labor cost zachowuje HR-01 – PASS |
| QFIN03-17 | signed gap ≠ adverse gap – PASS | QFIN03-18 | reference=0 nie tworzy change rate – PASS |
| QFIN03-19 | Shapley bridge jest jedyną metodą – PASS | QFIN03-20 | cost effect ma poprawny znak – PASS |
| QFIN03-21 | denominator effect ma poprawny znak – PASS | QFIN03-22 | cost effect + denominator effect = bridge gap – PASS |
| QFIN03-23 | stabilny cost + denominator↓ może dać adverse denominator effect – PASS | QFIN03-24 | cost↓ + denominator↓↓ może zwiększyć UC – PASS |
| QFIN03-25 | brak balancing item – PASS | QFIN03-26 | adverse share liczy tylko dodatnie effects – PASS |
| QFIN03-27 | compensating effects są zachowane – PASS | QFIN03-28 | adverse share nie miesza scopes/layers/references – PASS |
| QFIN03-29 | mix evidence nie jest dodawane do bridge – PASS | QFIN03-30 | work-content evidence nie jest bridge component – PASS |
| QFIN03-31 | rework nie zwiększa good output automatycznie – PASS | QFIN03-32 | gross output ≠ good output – PASS |
| QFIN03-33 | yield działa przy poprawnym mianowniku – PASS | QFIN03-34 | capacity underutilization jest evidence – PASS |
| QFIN03-35 | capacity pressure jest evidence – PASS | QFIN03-36 | PROC time ≠ koszt – PASS |
| QFIN03-37 | input price evidence ≠ automatyczny bridge component – PASS | QFIN03-38 | new scope jest poza matched bridge – PASS |
| QFIN03-39 | discontinued scope jest poza matched bridge – PASS | QFIN03-40 | materially changed scope jest poza matched bridge – PASS |
| QFIN03-41 | matched bridge uzgadnia matched gap – PASS | QFIN03-42 | full vs matched są oddzielone – PASS |
| QFIN03-43 | coverage current/reference są osobne – PASS | QFIN03-44 | coverage basis jest wspólna – PASS |

### QFIN03-45–104 – ciąg dalszy

| Id | Kontrola / status | Id | Kontrola / status |
| --- | --- | --- | --- |
| QFIN03-45 | zero wybranego denominatora daje null – PASS | QFIN03-46 | ujemny wybrany denominator daje validation – PASS |
| QFIN03-47 | negative cost jest flagowany – PASS | QFIN03-48 | one-off pozostaje actual – PASS |
| QFIN03-49 | adjusted nie zastępuje actual – PASS | QFIN03-50 | accounting basis jest porównywalny albo jawnie ograniczony – PASS |
| QFIN03-51 | cost classification jest porównywalna – PASS | QFIN03-52 | activity recognition jest porównywalna – PASS |
| QFIN03-53 | reclassification nie tworzy fałszywego FULL UC movement – PASS | QFIN03-54 | 3M/6M/12M są Σcost/Σtego samego denominator – PASS |
| QFIN03-55 | miesięczne unit costs nie są prostą średnią przy różnych denominatorach – PASS | QFIN03-56 | referencja jest źródłowa – PASS |
| QFIN03-57 | standard unit cost ma źródło – PASS | QFIN03-58 | brak arbitralnego target unit cost – PASS |
| QFIN03-59 | high UC ≠ automatycznie low efficiency – PASS | QFIN03-60 | unit cost ≠ price – PASS |
| QFIN03-61 | average unit cost ≠ marginal cost – PASS | QFIN03-62 | cost_per_constraint_unit pozostaje pomocniczy – PASS |
| QFIN03-63 | explanatory evidence ma true/false/null – PASS | QFIN03-64 | brak danych ≠ false – PASS |
| QFIN03-65 | explanatory evidence ≠ cause – PASS | QFIN03-66 | hypothesis ≠ cause – PASS |
| QFIN03-67 | FIN-02 pozostaje niezmieniony – PASS | QFIN03-68 | FIN-01 pozostaje niezmieniony – PASS |
| QFIN03-69 | PORT-01 pozostaje niezmieniony – PASS | QFIN03-70 | HR-01 pozostaje niezmieniony – PASS |
| QFIN03-71 | CAP-01 pozostaje niezmieniony – PASS | QFIN03-72 | CAP-02 pozostaje niezmieniony – PASS |
| QFIN03-73 | PROC-01 pozostaje niezmieniony – PASS | QFIN03-74 | PROC-02 pozostaje niezmieniony – PASS |
| QFIN03-75 | ZOP-TECH-01 pozostaje niezmieniony – PASS | QFIN03-76 | ZOP-MASTER-01 pozostaje niezmieniony – PASS |
| QFIN03-77 | PRI pozostaje DO OPRACOWANIA – PASS | QFIN03-78 | CONF pozostaje DO OPRACOWANIA – PASS |
| QFIN03-79 | FINDINGS są kompletne – PASS | QFIN03-80 | next_tests istnieją – PASS |
| QFIN03-81 | brak automatycznej rekomendacji redukcji kosztów – PASS | QFIN03-82 | brak automatycznej rekomendacji zatrudnienia – PASS |
| QFIN03-83 | brak automatycznej redukcji capacity – PASS | QFIN03-84 | brak automatycznej rekomendacji cenowej – PASS |
| QFIN03-85 | brak automatycznej wyceny potencjału – PASS | QFIN03-86 | FIN03-T01–T33 istnieją – PASS |
| QFIN03-87 | VAL/ACC/DOD są kompletne – PASS | QFIN03-88 | 0 danych SPZOZ, 0 danych pacjentów, 0 FIN-04 – PASS |
| QFIN03-89 | unit_cost_denominator_type/current/reference/unit/basis/comparability oraz valid_current/valid_reference są jawne – PASS | QFIN03-90 | current/reference mogą być obliczane niezależnie; zgodność type/unit/basis jest wymagana dopiero dla porównań – PASS |
| QFIN03-91 | bridge_denominator_type/current/reference/unit odpowiadają bridge_scope – PASS | QFIN03-92 | Shapley denominator_effect daje dokładną rekonsyliację – PASS |
| QFIN03-93 | volume_effect_signed=null dla work_content/inherited_hr_effect – PASS | QFIN03-94 | matched denominator należy do tego samego matched_activity_scope co matched numerator – PASS |
| QFIN03-95 | direct_in_scope shared nie wymaga sztucznej alokacji; okresowe allocated/mixed wymagają własnych gate – PASS | QFIN03-96 | coverage basis i FIN03-T29–T31 są poprawne – PASS |
| QFIN03-97 | unit_cost_denominator_valid_current jest niezależne od reference comparability – PASS | QFIN03-98 | unit_cost_denominator_valid_reference jest niezależne od current – PASS |
| QFIN03-99 | brak porównywalnej reference nie usuwa poprawnego unit_cost_current – PASS | QFIN03-100 | gap/adverse/change/bridge są null bez denominator_comparability=true – PASS |
| QFIN03-101 | shared cost attribution current/reference ma osobne type/direct/allocated/attributable/basis/quality – PASS | QFIN03-102 | shared_cost_attribution_change_flag nie jest automatycznie zmianą ekonomiczną – PASS |
| QFIN03-103 | bez shared_cost_attribution_comparability FULL gap/bridge nie udają porównywalności, VARIABLE/COMMITTED działają – PASS | QFIN03-104 | FIN03-T32–T33 przechodzą i wszystkie nowe pola są obecne – PASS |

### 20.1. Otwarte kwestie wspólne – poza FIN-03

| Kwestia | Status / granica |
| --- | --- |
| globalny standard work_content | FIN-03 korzysta z udokumentowanego work_content, nie zamyka kontraktu systemowego |
| globalny standard activity_unit | FIN-03 wymaga jawnej jednostki i basis, nie tworzy słownika dla wszystkich branż |
| globalne reguły weighted volume | wagi muszą być źródłowe; wspólna polityka pozostaje poza testem |
| globalna polityka allocation shared cost | FIN-03 rozróżnia direct_in_scope od allocated_from_parent_scope; nie projektuje globalnych kluczy alokacji |
| globalna orkiestracja next_tests | FIN-03 zapisuje rekomendacje, nie steruje całym grafem |
| ZOP-PRI-01 | DO OPRACOWANIA |
| ZOP-CONF-01 | DO OPRACOWANIA |

> **STATUS KOŃCOWY FIN-03 ZAMKNIĘTY METODOLOGICZNIE DO IMPLEMENTACJI. ZOP-PRI-01 – DO OPRACOWANIA. ZOP-CONF-01 – DO OPRACOWANIA.**

0 arbitralnych wag; 0 arbitralnego standard unit cost; 0 balancing item; 0 podwójnego liczenia shared cost; 0 podwójnego liczenia explanatory evidence; 0 automatycznych rekomendacji cięć, kadr, capacity lub cen; 0 automatycznej wyceny „potencjału”; 0 danych SPZOZ; 0 danych pacjentów; 0 rozpoczętego FIN-04.
