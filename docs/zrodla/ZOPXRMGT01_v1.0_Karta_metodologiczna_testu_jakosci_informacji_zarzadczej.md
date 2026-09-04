ZOPTYMALIZOWANI – X-RAY

MGT-01

Jakość informacji zarządczej

Karta metodologiczna i specyfikacja implementacyjna

> **STATUS MGT-01 ZAMKNIĘTY METODOLOGICZNIE DO IMPLEMENTACJI**

| Pole | Wartość |
| --- | --- |
| Identyfikator | ZOP-XR-MGT-01 |
| Wersja / data | v1.0 / 2 września 2026 |
| Rola | dziesiąty pełny test diagnostyczny X-Ray; przekrojowy kontrakt jakości informacji dla Core 10 |
| Odbiorcy | zarządzający, analityk, Aleksander – implementacja |
| Źródła nadrzędne | polecenie; FIN-01; FIN-02; FIN-03; CAP-01; CAP-02; HR-01; PORT-01; PROC-01; PROC-02; ZOP-TECH-01; ZOP-MASTER-01 |
| Zależności | ZOP-PRI-01 i ZOP-CONF-01 – DO OPRACOWANIA |

MGT-01 ocenia, czy informacja jest wystarczająca dla konkretnego zastosowania zarządczego. Nie tworzy drugiej definicji pól Core 10, nie ocenia prestiżu technologii, nie buduje wskaźnika jakości danych (Data Quality Score) i nie zastępuje ZOP-CONF-01 ani ZOP-PRI-01.

> **ZASADA NADRZĘDNA Jakość danych i przydatność informacji zarządczej nie są tym samym. Informacja jest oceniana względem konkretnego wniosku lub decyzji, a brak informacji może być pełnoprawnym wynikiem diagnostycznym.**

## 1. Rola, pytanie diagnostyczne i granice MGT-01

> **PYTANIE DIAGNOSTYCZNE Czy informacja używana do zarządzania danym obszarem jest wystarczająco dobrze zdefiniowana, kompletna, aktualna, porównywalna, uzgadnialna i możliwa do prześledzenia, aby odpowiedzialnie wyprowadzić z niej konkretny wniosek lub podjąć konkretną decyzję?**

| Etap | Produkt | Granica |
| --- | --- | --- |
| Źródło | udokumentowane pochodzenie | typ źródła ≠ jakość |
| Definicja | jednoznaczne znaczenie i wersja | ta sama nazwa może oznaczać coś innego |
| Zakres | zakres zgodny z decyzją | nie łącz różnych populacji bez uzgodnienia |
| Okres | okres i podstawa czasu | różne kalendarze mogą niszczyć porównywalność |
| Transformacja | jawne mapowanie / formuła / alokacja | zmiana metody wymaga śladu |
| Miara | obliczalny obiekt informacji (information_object) | null ≠ 0 |
| Uzgodnienie | uzgodnienie (reconciliation) | różnica ≠ automatycznie błąd danych |
| Wynik diagnostyczny | fakt + ograniczenia | hipoteza ≠ dowód |
| Decyzja | status gotowości decyzyjnej (decision_information_status) | gotowość zależy od wymagań decyzji |

### 1.1. Granice względem CONF, PRI i IT

| Obszar | Pytanie | Czego MGT-01 nie robi |
| --- | --- | --- |
| MGT-01 | czy struktura informacji pozwala odpowiedzialnie wyprowadzić wynik/decyzję? | nie liczy pewności ani ważności biznesowej |
| ZOP-CONF-01 | jak wysoka jest pewność wyniku przy dostępnych dowodach? | MGT-01 tylko przekazuje sygnały jakości |
| ZOP-PRI-01 | jak ważny/pilny jest problem? | MGT-01 nie ustala istotność biznesowa |
| IT | jak działa technologia i architektura? | MGT-01 nie jest audytem ERP/BI/chmury/bazy danych |

## 2. Kontekst decyzji i gotowość decyzyjna

### 2.1. Kontekst decyzji (decision_context)

| Pole | Kontrakt |
| --- | --- |
| decision_id | jednoznaczny identyfikator decyzji lub wniosku |
| decision_question | pytanie, na które informacja ma odpowiedzieć |
| decision_scope | zakres organizacyjny / działalności / populacji |
| decision_period | okres, którego dotyczy decyzja |
| decision_required_metrics | miary wymagane do odpowiedzialnego wniosku |
| decision_required_granularity | minimalny poziom szczegółowości użyteczny dla decyzji |
| decision_required_timeliness | wymagana aktualność / maksymalne akceptowalne opóźnienie wynikające z decyzji |
| decision_required_comparability | czy decyzja wymaga porównania okresu bieżącego, okresu odniesienia lub trendu |
| decision_required_lineage | minimalny wymagany ślad pochodzenia dla tej decyzji |

Bez jawnego decision_context MGT-01 może ocenić wymiary informacji ogólnie, ale decision_information_status nie może przyjąć decision_ready. Gdy nie znamy wymagań decyzji, status = not_assessable.

### 2.2. Status gotowości decyzyjnej (decision_information_status)

| Status | Warunek | Znaczenie |
| --- | --- | --- |
| decision_ready | wszystkie obiekty informacji klasy required dostępne; wymagane walidacje bez CRITICAL; zakres, okres, poziom szczegółowości, aktualność, porównywalność i pochodzenie informacji spełniają wymagania decyzji | decyzja ma odpowiedzialną podstawę informacyjną |
| decision_ready_with_limitations | rdzeń informacji klasy required spełniony; jawne ograniczenia dotyczą klas supporting/optional albo innych akceptowanych ograniczeń | decyzja możliwa z opisanymi ograniczeniami |
| decision_partial | część zakresu lub wniosków gotowa, część nie; miara bieżąca może istnieć bez porównania | nie upraszczaj do PASS/FAIL |
| decision_blocked | brak elementu klasy required lub nierozstrzygnięty konflikt bez odpowiedzialnego rozwiązania zastępczego | konkretna decyzja / wniosek zablokowany |
| not_assessable | brak wymagań decyzji albo brak możliwości oceny samej informacji | nie jest synonimem decision_blocked |

> **BRAMA decision_ready nie wymaga 100% wszystkich możliwych danych organizacji. Wymaga kompletnego rdzenia informacji potrzebnej do konkretnej decyzji.**

### 2.3. Klasa wymagań informacyjnych (information_requirement_class) i powiązanie reguły decyzji (decision_rule_binding)

| Pole | Kontrakt |
| --- | --- |
| information_requirement_class | required / supporting / optional / contextual |
| decision_rule_id | identyfikator minimalnego kontraktu decyzji |
| required_information_objects | lista obiektów informacji klasy required |
| required_validation_conditions | walidacje, które muszą być spełnione dla wniosku |
| allowed_limitations | jawnie dopuszczone ograniczenia nieblokujące |

Brak informacji klasy optional nie blokuje decyzji. Brak informacji klasy required może prowadzić do decision_partial lub decision_blocked zależnie od tego, czy istnieje odpowiedzialne rozwiązanie zastępcze i czy część wniosku pozostaje dostępna.

## 3. Obiekt informacji, źródło i pochodzenie informacji

### 3.1. Obiekt informacji (information_object)

| Pole | Znaczenie |
| --- | --- |
| information_object_id | unikalny identyfikator analizowanego elementu informacji |
| information_object_name | nazwa użytkowa |
| information_object_type | miara / pole / wskaźnik / zestaw danych / raport / wynik testu / definicja / mianownik / koszt / wolumen / zdolność / trasa / czas / inne |
| information_object_scope | zakres, którego dotyczy obiekt |
| information_object_period | okres lub moment obowiązywania |

### 3.2. Pochodzenie informacji (information_lineage) i możliwość prześledzenia

| Pole | Kontrakt |
| --- | --- |
| source_system | system lub środowisko źródłowe, jeśli dotyczy |
| source_object / source_field | obiekt i pole źródłowe |
| source_document | dokument źródłowy, jeśli dotyczy |
| source_owner | punkt odpowiedzialności za źródło |
| transformation_steps | kolejne jawne transformacje |
| calculation_formula | formuła użyta do obliczenia |
| allocation_basis | podstawa alokacji, jeśli używana |
| manual_adjustment_flag / manual_adjustment_basis | jawna korekta ręczna i jej podstawa |
| derived_from | obiekty, z których wynik pochodzi |
| lineage_status | complete / partial / missing / not_applicable |
| traceability_status | full / partial / missing; możliwość przejścia od wyniku diagnostycznego do wzoru, składników, transformacji i źródła |

> **ROZRÓŻNIENIE Pochodzenie informacji (lineage) opisuje źródło i łańcuch zależności. Możliwość prześledzenia (traceability) opisuje praktyczną możliwość przejścia od wyniku diagnostycznego z powrotem do jego podstawy. Pełne pochodzenie informacji może istnieć bez wygodnej możliwości prześledzenia i odwrotnie.**

### 3.3. Typ i autorytet źródła

| Pole | Wartości / zasada |
| --- | --- |
| source_type | system_record / document / manual_register / calculation / allocation / estimate / external_source / other_documented_source |
| source_authority | główne / pomocnicze / historyczne / wtórne / nieuzgodnione – wyłącznie przy jawnej podstawie |
| source_authority_basis | dlaczego źródło ma daną rolę w tym kontekście |

Typ źródła nie determinuje jakości. Dane ręczne mogą być wystarczające do podjęcia decyzji, a dane systemowe mogą być błędnie zmapowane, nieaktualne lub semantycznie nieporównywalne.

## 4. Definicja, zakres, okres i porównywalność

### 4.1. Jakość definicji i spójność semantyczna (semantic_consistency)

| Pole | Kontrakt |
| --- | --- |
| definition_status | defined / partially_defined / ambiguous / missing / conflicting |
| definition_source | źródło definicji |
| definition_version | wersja użyta w obliczeniu |
| definition_effective_from / to | okres obowiązywania |
| definition_owner | punkt odpowiedzialności za definicję |
| semantic_consistency_status | czy to samo pole / pojęcie oznacza to samo między testami, okresami, jednostkami i raportami |

> **SEMANTYKA MGT-01 nie redefiniuje pól Core 10. Wykrywa sytuację „ta sama nazwa – różne znaczenie” i zapisuje ją jako niespójność wymagającą uzgodnienie albo walidacji.**

### 4.2. Jakość zakresu

| Pole | Kontrakt |
| --- | --- |
| scope_status | fit / fit_with_limitations / partial / failed / not_assessable albo status szczegółowy mapowany do dimension_status |
| scope_definition | jawna granica informacji |
| scope_owner | właściciel definicji zakresu |
| scope_comparability | porównywalność okresu bieżącego i odniesienia oraz pomiędzy testami |

Kontrola zakresu obejmuje licznik, mianownik, koszt, przychód, wolumen, zdolność, proces i okres. Informacja nie jest gotowa do podjęcia decyzji, jeżeli kluczowe składniki dotyczą różnych zakresów bez jawnego uzgodnienia.

### 4.3. Jakość okresu (period_quality)

| Pole | Kontrakt |
| --- | --- |
| period_status | ocena poprawności okresu obiektu informacji |
| period_basis | kalendarz / okres księgowy / okno operacyjne / podstawa znacznika czasu |
| period_alignment_status | czy składniki miary dotyczą zgodnego okresu |
| period_comparability | czy okres bieżący, okres odniesienia i trend są porównywalne |

Różne okresy księgowe, kalendarze operacyjne i podstawy znaczników czasu mogą być poprawne osobno, ale nieporównywalne między sobą. MGT-01 przechowuje to rozróżnienie.

## 5. Pokrycie, poziom szczegółowości i aktualność

### 5.1. Pokrycie

| Pole | Kontrakt |
| --- | --- |
| coverage_current | pokrycie okresu bieżącego według jawnej podstawy |
| coverage_reference | pokrycie okresu odniesienia według tej samej lub jawnie nieporównywalnej podstawy |
| coverage_basis | np. revenue / cost / volume / scope_count / documented_weight / inne udokumentowane |
| coverage_missing_scope | co konkretnie pozostaje poza pokryciem |
| coverage_unknown_scope | zakres o nieznanym statusie pokrycia |

> **BRAK PROGU Pokrycie jest faktem, nie oceną. 95% może blokować decyzję, gdy brakujące 5% obejmuje wymagany zakres; 70% może wystarczyć z ograniczeniami, jeśli brakująca część nie jest wymagana dla danej decyzji.**

### 5.2. Poziom szczegółowości

| Pole | Wartości / reguła |
| --- | --- |
| available_granularity | rzeczywista szczegółowość danych |
| required_granularity | szczegółowość wymagana przez decision_context |
| granularity_fit | fit / coarser_than_required / finer_than_required / mixed / unknown |

Finer_than_required nie jest automatycznie problemem. Coarser_than_required może uniemożliwić wniosek, np. koszt na poziomie jednostki nie pozwala rozstrzygnąć decyzji na poziomie zmiany.

### 5.3. Aktualność i opóźnienie raportowania

| Pole | Kontrakt |
| --- | --- |
| data_as_of | moment aktualności danych |
| refresh_frequency | częstotliwość odświeżania |
| reporting_delay | opóźnienie raportowania |
| required_timeliness | wymaganie decyzji |
| timeliness_fit | fit / fit_with_limitations / partial / failed / not_assessable |
| freshness_status | ocena aktualności względem required_timeliness |
| reporting_latency / reporting_latency_unit | zmierzone opóźnienie i jednostka |

Nie istnieje globalna reguła „dane starsze niż X są złe”. Ta sama informacja może być zbyt stara dla decyzji operacyjnej i wystarczająca dla decyzji strategicznej.

## 6. Odtwarzalność, transformacje, wersje i zmiana metody

### 6.1. Odtwarzalność

| Pole | Kontrakt |
| --- | --- |
| reproducibility_status | fit / fit_with_limitations / partial / failed / not_assessable albo status szczegółowy |
| reproducibility_basis | źródła + reguły + wersje pozwalające niezależnemu analitykowi odtworzyć wynik |

Odtwarzalność nie wymaga pełnej automatyzacji. Ręczny proces może być reprodukowalny, jeżeli wejścia, reguły i kroki są jawne.

### 6.2. Jakość transformacji

| Pole | Kontrakt |
| --- | --- |
| transformation_status | status poprawności i odtwarzalności transformacji |
| transformation_owner | właściciel reguły transformacji |
| transformation_version | wersja użytej reguły |
| transformation_change_flag | czy reguła zmieniła się między porównywanymi okresami |
| transformation_change_basis | źródło i opis zmiany |

### 6.3. Wersjonowanie i kontrola zmian

| Pole | Kontrakt |
| --- | --- |
| data_definition_version | wersja definicji danych |
| calculation_version | wersja formuły / modułu |
| mapping_version | wersja mapowania |
| allocation_version | wersja alokacji |
| effective_date | data wejścia wersji w życie |
| method_change_flag | czy zaszła zmiana metody |
| method_change_type | definition / calculation / mapping / allocation / scope / period_basis / other |
| method_change_effective_date | moment obowiązywania zmiany |
| method_change_impact | wpływ na porównywalność i wynik diagnostyczny |
| historical_restated_flag | czy historia została przeliczona do nowej metody |

> **ZASADA Zmiana metody może zniszczyć porównywalność trendu. Jeżeli historia została odpowiedzialnie przeliczona, porównywalność może zostać odzyskana. MGT-01 nie wymaga rozbudowanego systemu wersjonowania IT – wymaga możliwości ustalenia, czym policzono wynik.**

## 7. Uzgodnienie i przekrojowa spójność Core 10

### 7.1. Kontrakt uzgodnienia

| Pole | Kontrakt |
| --- | --- |
| reconciliation_id | identyfikator uzgodnienia |
| reconciliation_metric | pole / miara uzgadniana |
| reconciliation_scope | zakres A i B |
| reconciliation_period | okres A i B |
| reconciliation_value_a / b | wartości porównywane |
| reconciliation_gap | różnica po uwzględnieniu zgodnej jednostki i podstawa |
| reconciliation_status | reconciled / reconciled_with_explanation / unreconciled / not_comparable / not_applicable |
| reconciliation_explanation | udokumentowane wyjaśnienie różnicy |

Niezgodność uzgodnienia nie oznacza automatycznie złych danych. Różnica może wynikać z innego zakresu, okresu, definicji, alokacji, przeliczenia historii (restatement), zaokrąglenia albo błędu. MGT-01 najpierw klasyfikuje różnicę.

### 7.2. Techniczna tolerancja uzgodnienia (technical_reconciliation_tolerance)

| Pole | Reguła |
| --- | --- |
| technical_reconciliation_tolerance | wyłącznie precyzja / zaokrąglenie / konwersja formatu |
| technical_reconciliation_tolerance_basis | jawna podstawa techniczna |
| istotność biznesowa | poza MGT-01; należy do ZOP-PRI-01 / decyzji zarządczej |

### 7.3. Macierz uzgodnień Core 10

| Para | Pola / obszary | Reguła MGT-01 |
| --- | --- | --- |
| FIN-01 ↔ FIN-02 | net_revenue; cost; scope; period | uzgodnij tylko przy zgodnym zakresie; wyjaśnione różnice nie są błędem |
| FIN-02 ↔ FIN-03 | cost layers; shared_cost; allocation; matched scope | kontrola spójności warstw i atrybucji bez ponownego liczenia testów |
| FIN-03 ↔ PORT-01 | activity_unit; weighted_volume; cost attribution; unit-cost related inputs | to samo znaczenie działalności i kosztu w tym samym zakresie |
| HR-01 ↔ FIN-03 | labor_cost; labor_input; unit_labor_cost; work_content | identyczny zakres → wynik nie może być sprzeczny |
| CAP-01 ↔ CAP-02 | effective_available; used; resource_group; capacity_unit | CAP-02 zachowuje semantykę CAP-01 |
| CAP-02 ↔ PROC-02 | required_capacity; constraint mapping; resource_group | mapowanie procesu do zasobu musi być jawne |
| PROC-01 ↔ PROC-02 | case_id; stage; routing; ready_at; start; end; time basis | wspólna oś czasu i semantyka trasowania |

## 8. Minimalny rejestr pól wspólnych Core 10, jednostki i wartości null

### 8.1. Minimalny rejestr pól między testami (CROSS_TEST_FIELD_REGISTRY)

| Pole rejestru | Znaczenie |
| --- | --- |
| canonical_field_name | nazwa pola już zdefiniowanego w zamrożonej karcie |
| canonical_definition_source | zamrożony dokument będący źródłem definicji |
| used_by_tests | testy używające pola |
| scope_requirement | wymagania zakresu |
| period_requirement | wymagania okresu |
| unit_requirement | wymagania jednostki |
| allowed_null_semantics | dopuszczalne znaczenia null |
| reconciliation_required | czy przy wspólnym zakres wymagane jest uzgodnienie |

Rejestr nie jest pełnym systemem zarządzania danymi podstawowymi (master data management). Nie tworzy drugiej definicji; wskazuje wyłącznie istniejące źródło definicji i interfejsy Core 10.

| canonical_field_name | canonical_definition_source | used_by_tests |
| --- | --- | --- |
| net_revenue | PORT-01 / FIN-02 zgodnie z zamrożoną semantyką | FIN-01; FIN-02; PORT-01 |
| direct_variable_cost | PORT-01 | FIN-02; FIN-03; PORT-01 |
| direct_committed_cost | PORT-01 | FIN-02; FIN-03; PORT-01 |
| shared_cost | PORT-01 | FIN-02; FIN-03; PORT-01 |
| operating_cost_total | FIN-02 | FIN-02; FIN-03 jako źródłowy kontekst |
| activity_unit | PORT-01 | PORT-01; FIN-03; HR/CAP pomocniczo |
| weighted_volume | PORT-01 | PORT-01; HR-01; FIN-03 |
| work_content | CAP-02 / HR-01 – wspólne pole bez lokalnej redefinicji | CAP-02; HR-01; FIN-03; PROC |
| effective_available | CAP-01 | CAP-01; CAP-02; PROC-02 |
| matched_effective_available | CAP-02 | CAP-02 |
| required_capacity | CAP-02 | CAP-02; PROC-02 jako interfejs |
| unit_cost | FIN-03 | FIN-03 |
| case_lead_time | PROC-01 | PROC-01 |
| constraint_status | PROC-02 | PROC-02 |

### 8.2. Spójność jednostek

| Pole | Kontrakt |
| --- | --- |
| unit_status | fit / converted_with_basis / conflicting / missing / not_applicable |
| unit_current / unit_reference | jednostki wartości porównywanych |
| unit_conversion_basis | jawna reguła konwersji |

PLN ≠ tys. PLN; minuty ≠ godziny bez konwersji; capacity_unit i activity_unit nie są wymienne bez udokumentowanej podstawy.

### 8.3. Semantyka wartości null (NULL_SEMANTICS)

| Wartość | Znaczenie |
| --- | --- |
| null_missing | wartość powinna istnieć, ale brak źródła/danych |
| null_not_applicable | pole nie ma zastosowania w danym zakres |
| null_not_computable | dane istnieją, ale warunki matematyczne nie pozwalają policzyć miary |
| null_not_assessable | nie ma podstaw do oceny jakości/porównywalności |
| null_blocked_by_validation | miara świadomie zatrzymana przez walidację |

> **ZERO ≠ NULL 0 oznacza znaną wartość zerową. Null oznacza brak wartości albo brak możliwości jej odpowiedzialnego ustalenia. Zamiana null na 0 jest błędem semantycznym.**

## 9. Dane ręczne, systemowe, szacunki, założenia i dane zewnętrzne

### 9.1. Dane ręczne i dane systemowe

| Pole | Kontrakt |
| --- | --- |
| manual_data_flag | czy obiekt pochodzi z rejestru / korekty ręcznej |
| manual_data_owner | osoba/rola utrzymująca dane |
| manual_data_control | kontrola wersji / zatwierdzenia / kompletności |
| manual_data_validation_status | wynik walidacji ręcznej informacji |
| system_generated_flag | czy wartość wygenerował system; nie oznacza automatycznie poprawności |

MGT-01 kontroluje definicję, zakres, mapowanie, duplikaty, znaczniki czasu, aktualność i zmiany systemowe. Automatyzacja jest cechą procesu, nie dowodem jakości.

### 9.2. Szacunki i założenia

| Pole | Kontrakt |
| --- | --- |
| estimate_flag | czy wartość jest szacunkiem |
| estimate_method | metoda szacunku |
| estimate_basis | źródłowa podstawa |
| estimate_owner | odpowiedzialność za założenia szacunku |
| estimate_uncertainty_note | jawna niepewność |
| assumption_flag | czy użyto założenia |
| assumption_text | treść założenia |
| assumption_basis | podstawa założenia |
| assumption_impact | wpływ na wynik/decyzję |

> **ROZRÓŻNIENIE Szacunek może być legalną informacją zarządczą, jeśli jest jawny i ma podstawę. Założenie ≠ dana; szacunek ≠ wartość zmierzona.**

### 9.3. Dane zewnętrzne

| Pole | Kontrakt |
| --- | --- |
| external_source_name | nazwa źródła zewnętrznego |
| external_source_date | data publikacji / pobrania |
| external_source_scope | zakres, do którego źródło się odnosi |
| external_source_methodology | metoda wyznaczenia wartości zewnętrznej |
| external_source_comparability | czy źródło jest porównywalne z badanym zakres |

Zewnętrzna wartość odniesienia (benchmark) bez źródła nie może być użyta jako odpowiedzialna informacja referencyjna.

### 9.4. Status automatyzacji (automation_status)

| Wartość | Znaczenie |
| --- | --- |
| manual | proces ręczny |
| semi_automated | część kroków automatyczna |
| automated | proces automatyczny |
| mixed | różne mechanizmy w łańcuchu |

automation_status nie wpływa automatycznie na gotowość decyzyjną ani dimension_status.

## 10. Duplikaty, integralność referencyjna, właściciele i konflikty

### 10.1. Duplikaty

| Pole | Kontrakt |
| --- | --- |
| duplicate_status | none / candidate / confirmed_duplicate / legitimate_repeat / unresolved |
| duplicate_detection_basis | reguła detekcji |
| duplicate_resolution_status | resolved / retained_as_valid / unresolved |

Powtarzający się rekord może być błędem, legalnym repeat_visit, rework albo osobnym zdarzeniem. MGT-01 nie usuwa duplikatów semantycznie bez podstawy.

### 10.2. Integralność referencyjna (referential_integrity_status)

referential_integrity_status kontroluje co najmniej relacje: case ↔ stage; product ↔ unit; resource ↔ resource_group; koszt ↔ scope; przychód ↔ scope; zdolność ↔ resource. MGT-01 nie projektuje pełnej bazy danych.

### 10.3. Właściciele informacji

| Pole | Znaczenie |
| --- | --- |
| information_owner | odpowiedzialność za utrzymanie informacji |
| definition_owner | odpowiedzialność za definicję |
| source_owner | odpowiedzialność za źródło |
| validation_owner | odpowiedzialność za walidację |

Właściciel informacji nie jest winny problemu. Brak właściciela jest luką informacyjną, ale nie blokuje automatycznie wyniku, jeśli pochodzenie informacji i odtwarzalność są wystarczające dla konkretnej decyzji.

### 10.4. Konflikt danych i jego rozstrzygnięcie (data_conflict_flag, conflict_resolution_status)

| Pole | Kontrakt |
| --- | --- |
| data_conflict_flag | true / false / null |
| conflicting_sources | identyfikatory źródeł |
| conflict_type | value / definition / scope / period / version / mapping / inne |
| conflict_resolution_status | resolved / resolved_with_limitation / unresolved / not_applicable |
| conflict_resolution_basis | udokumentowana podstawa rozstrzygnięcia |

> **ZAKAZ Nie wybieraj automatycznie większej wartości, nowszego pliku ani danych systemowych. Nierozstrzygnięty konflikt dotyczący informacji wymaganej może blokować decyzję.**

## 11. Luka informacyjna, zablokowana miara/test/decyzja i dług informacyjny

### 11.1. Kontrakt luki informacyjnej

| Pole | Kontrakt |
| --- | --- |
| information_gap_id | unikalny identyfikator luki |
| missing_information_element | czego konkretnie brakuje |
| information_gap_type | missing_source / missing_definition / missing_scope / missing_period_alignment / missing_denominator / missing_allocation_basis / missing_work_content / missing_capacity_mapping / missing_route_mapping / missing_reference / missing_owner / missing_lineage / missing_reconciliation / insufficient_granularity / insufficient_timeliness / non_comparable_method / other |
| affected_test | test, którego dotyczy luka |
| affected_metric | miara niedostępna lub ograniczona |
| affected_finding | wynik diagnostyczny częściowy/zablokowany |
| affected_decision | decyzja, na którą luka wpływa |
| gap_consequence | metric_unavailable / comparison_unavailable / bridge_unavailable / finding_partial / finding_blocked / decision_limited / decision_blocked / validation_required |
| workaround_available | true / false / null |
| workaround_basis | źródłowa podstawa obejścia |

### 11.2. Mapa blokad decyzyjnych

| Pole | Znaczenie |
| --- | --- |
| blocked_metric | miara, której nie wolno policzyć |
| blocked_reason | konkretna przyczyna |
| blocking_information_object | obiekt brakujący lub niewiarygodny |
| blocked_test | test albo moduł zależny |
| blocked_decision_id | identyfikator decyzji |
| blocked_decision_reason | dlaczego brak uniemożliwia konkretny wniosek |

> **MAPA information_gap → blocked_metric → affected_test → affected_decision. Przykład: brak work_content → required_capacity niedostępne w CAP-02 → brak możliwości potwierdzenia niedoboru → decyzja o zwiększeniu zdolności zablokowana.**

### 11.3. Krytyczna luka informacyjna, luka powtarzalna i dług informacyjny (critical_information_gap, recurring_gap, information_debt)

| Pole | Reguła |
| --- | --- |
| critical_information_gap | true tylko gdy luka blokuje element wymagany konkretnej decyzji lub testu; false gdy nie blokuje; null gdy nie można ocenić |
| recurring_gap_flag | czy ten sam brak powtarza się w wielu okresach |
| recurring_gap_count | liczba powtórzeń |
| recurring_gap_periods | okresy występowania |
| information_debt_flag | opcjonalny sygnał utrzymywanej, powtarzalnej niespójności / rozwiązania zastępczego / braku definicji; bez automatycznej wyceny pieniężnej |

## 12. Brama gotowości decyzyjnej i rozwiązanie zastępcze

### 12.1. Deterministyczna logika statusu

| Warunek | Status minimalny |
| --- | --- |
| brak kontekstu decyzji (decision_context) / brak znanych wymagań decyzji | not_assessable |
| brak obiektu informacji klasy required lub nierozstrzygnięty konflikt/CRITICAL oraz brak odpowiedzialnego rozwiązania zastępczego | decision_blocked |
| część zakresu lub wniosków klasy required dostępna, część nie | decision_partial |
| rdzeń informacji klasy required spełniony, ale jawne ograniczenia klas supporting/optional, szacunku lub pokrycia są akceptowane | decision_ready_with_limitations |
| wszystkie obiekty informacji klasy required i wymagane walidacje spełnione; zakres, okres, poziom szczegółowości, aktualność, porównywalność i pochodzenie informacji zgodne | decision_ready |

Brama ocenia konkretne zastosowanie. Ten sam information_object może mieć status fit dla jednej decyzji i failed dla innej.

### 12.2. Rozwiązanie zastępcze

| Pole | Kontrakt |
| --- | --- |
| workaround_type | alternative_source / manual_register / documented_mapping / estimate / other_documented |
| workaround_basis | źródło i reguła obejścia |
| workaround_limitations | jawne ograniczenia i zakres stosowania |

Rozwiązanie zastępcze (workaround) nie jest zgadywaniem. Kontrolowany rejestr ręczny może przywrócić gotowość z ograniczeniami. Nieudokumentowane założenie nie jest rozwiązaniem zastępczym.

### 12.3. Wymiary jakości informacji

| Wymiar | Co ocenia |
| --- | --- |
| jakość źródła (source_quality) | czy źródło i jego rola są znane i użyte odpowiednio |
| jakość definicji (definition_quality) | jednoznaczność, wersja i konflikt definicji |
| jakość zakresu (scope_quality) | zgodność granic informacji z decyzją |
| zgodność okresów (period_alignment) | zgodność okresów i podstaw czasu |
| kompletność / pokrycie (completeness_coverage) | ile i czego obejmuje informacja |
| porównywalność (comparability) | czy wartości można odpowiedzialnie porównać |
| poziom szczegółowości (granularity) | czy szczegółowość pasuje do decyzji |
| aktualność (timeliness) | czy aktualność odpowiada required_timeliness |
| pochodzenie informacji (lineage) | czy pochodzenie jest znane |
| odtwarzalność (reproducibility) | czy wynik można niezależnie odtworzyć |
| uzgodnienie (reconciliation) | czy te same pojęcia/wartości są uzgadnialne |
| przydatność decyzyjna (decision_fitness) | czy informacja wystarcza dla konkretnego wniosku |
| właściciele informacji (ownership) | czy wiadomo, kto utrzymuje źródło/definicję/walidację |
| stabilność (stability) | czy definicje, mapowanie i źródła są stabilne |
| spójność jednostek (unit_consistency) | czy jednostki są zgodne lub prawidłowo konwertowane |
| jakość transformacji (transformation_quality) | czy transformacje są jawne i wersjonowane |

### 12.4. Status wymiaru (dimension_status) i kontrakt rekordu oceny wymiaru

| Status | Znaczenie |
| --- | --- |
| fit | wymiar spełnia wymaganie decyzji |
| fit_with_limitations | wymiar wystarcza przy jawnych ograniczeniach |
| partial | część zakresu spełnia wymaganie |
| failed | wymiar blokuje zależny wniosek |
| not_assessable | brak podstaw do oceny |

| Pole | Kontrakt |
| --- | --- |
| information_dimension_name | jeden z co najmniej: source_quality / definition_quality / scope_quality / period_alignment / completeness_coverage / comparability / granularity / timeliness / lineage / reproducibility / reconciliation / decision_fitness / ownership / stability / unit_consistency / transformation_quality |
| information_dimension_status | jedna wartość z katalogu dimension_status: fit / fit_with_limitations / partial / failed / not_assessable |
| information_dimension_basis | źródło, reguła lub wymaganie decyzji stanowiące podstawę oceny konkretnego wymiaru |
| information_dimension_limitations | jawne ograniczenia właściwe tylko dla danego wymiaru; null, gdy brak ograniczeń |
| information_dimension_evidence | dowody i identyfikatory obiektów informacji wspierające status danego wymiaru |
| information_dimension_validation_required | wartość logiczna wskazująca, czy status wymiaru wymaga dodatkowej walidacji |
| klucz rekordu | decision_id + information_object_id + scope + period + information_dimension_name; jeden rekord = jeden wymiar |

dimension_status pozostaje katalogiem dozwolonych statusów, natomiast information_dimension_status jest statusem konkretnego wymiaru konkretnego information_object w danym decision_id, zakresie i okresie. Wymiary nie są agregowane do wspólnej średniej, wskaźnika ani jednego statusu jakości.

> **WSKAŹNIK JAKOŚCI DANYCH (DATA QUALITY SCORE) = 0 MGT-01 nie agreguje wymiarów do jednego wyniku 0–100, średniej ważonej ani HIGH/MEDIUM/LOW. Zachowuje wielowymiarowy obraz informacji.**

## 13. Macierz gotowości informacyjnej i graf zależności

### 13.1. Macierz gotowości informacyjnej (INFORMATION_READINESS_MATRIX)

| Obszar informacji | Wymaganie | Stan | Konsekwencja | Test/decyzja | Działanie walidacyjne |
| --- | --- | --- | --- | --- | --- |
| Definicja przychodu (revenue) | defined + ta sama wersja | fit | brak ograniczenia | FIN-01/FIN-02 | brak |
| Mianownik FIN-03 | poprawny w okresie bieżącym; porównywalny dla luki | partial | bieżący koszt jednostkowy (UC) dostępny; luka = null | FIN-03 / decyzja kosztowa | uzgodnij okres odniesienia |
| CAP-02 work_content | wymagany dla required_capacity | failed | required_capacity jest zablokowane | CAP-02 / decyzja dotycząca zdolności | potwierdź work_content |
| PROC ready_at | wymagany dla queue_time | partial | queue_time zablokowane; czas etapu dostępny | PROC-01/PROC-02 | odtwórz gotowość |
| Alokacja portfela | podstawa wymagana dla Full_result | fit_with_limitations | CM1/SM dostępne; Full_result częściowy | PORT-01 | zweryfikuj podstawę alokacji |

Tabela jest mapą diagnostyczną, nie kartą punktową.

### 13.2. Graf zależności informacji (INFORMATION_DEPENDENCY_GRAPH) – kontrakt logiczny

> **source → canonical field → transformation → metric → test → finding → decision**

| Węzeł | Minimalne pola |
| --- | --- |
| źródło | source_type; source_object; source_field; version |
| pole kanoniczne | canonical_field_name; definition_source; scope/period/unit requirements |
| transformacja | transformation_version; formula / mapping / allocation basis |
| miara | information_object_id; scope; period; unit; null semantics |
| test | test_id; validation status; finding |
| decyzja | decision_id; requirement class; decision_information_status |

MGT-01 definiuje kontrakt danych grafu. Nie projektuje silnika grafowego ani globalnego silnika reguł decyzyjnych.

### 13.3. Stabilność informacji i porównywalność trendu (information_stability_status, trend_comparability_status)

| Pole | Kontrakt |
| --- | --- |
| information_stability_status | ocena powtarzalności definicji, źródła, mapowania i ręcznych korekt |
| trend_comparability_status | comparable / partially_comparable / not_comparable / unknown |

Niestabilność nie oznacza automatycznie błędu, ale może uniemożliwić analizę trendu. Bez porównywalności trendu nie wolno tworzyć pozornego trendu z podobnych, lecz zmiennie definiowanych danych.

## 14. Relacje MGT-01 z dziewięcioma testami Core 10

| Test | MGT-01 kontroluje | Nie robi |
| --- | --- | --- |
| FIN-01 | revenue/cost scope; period; basis; current/reference; reconciliation with FIN-02 | nie liczy GR/GC/CRG/CI |
| FIN-02 | profitability_scope; cost layers; shared_cost; bridge_scope; matched scope; reclassification; one-off; reconciliation | nie przelicza mostu wyniku/marży |
| FIN-03 | activity_unit; unit_cost_denominator_type; validity current/reference; comparability; shared cost attribution current/reference; weighted_volume; work_content; matched bridge | nie liczy ponownie Shapleya |
| HR-01 | labor_input; labor_cost; effect denominator; productivity; work_content; unit_labor_cost; scope/time mapping | nie ocenia ludzi |
| CAP-01 | available_source; documented_extra_capacity; effective_available; used; capacity_unit; resource_group; calendar basis | nie zmienia definicji zdolności |
| CAP-02 | matched base/effective capacity; required_capacity; work_content; capability mapping; shared resource allocation; extra capacity dependency; pressure evidence | nie potwierdza niedoboru za CAP-02 |
| PORT-01 | portfolio_item identity; revenue; variable/committed/shared allocation; activity_unit; weighted_volume; matched scope | nie ocenia rentowności produktu |
| PROC-01 | case boundaries; timestamps; ready_at; routing; parallelism; time basis; calendar; censoring; route comparability | nie liczy czasu procesu |
| PROC-02 | stage identity; constraint_entity; flow/capacity/mechanism evidence; predecessor; operating time; resource mapping | nie nadaje constraint_status |

### 14.1. Niespójność między testami (cross_test_inconsistency_flag)

| Pole | Kontrakt |
| --- | --- |
| cross_test_inconsistency_flag | true / false / null |
| cross_test_inconsistency_fields | pola objęte rozbieżnością |
| cross_test_inconsistency_tests | testy, w których rozbieżność występuje |
| cross_test_inconsistency_reason | scope / period / definition / unit / mapping / allocation / unknown |
| cross_test_resolution_status | resolved / resolved_with_limitation / unresolved / not_comparable |

MGT-01 nie naprawia automatycznie wyników innych testów. Jeśli rozbieżność jest rzeczywistą sprzecznością zamrożonych interfejsów, dokument oznacza BLOCKER DO DECYZJI zamiast zmieniać źródło.

### 14.2. Kontrola interfejsów Core 10

Kontrola wykonana wyłącznie na poziomie interfejsów: MGT-01 odwołuje się do istniejących pól zgodnie z zamrożonymi kartami; nie redefiniuje ich, nie zmienia danych przekazywanych przez testy źródłowe i nie wprowadza sprzecznej matematyki. Nie stwierdzono nierozwiązanego krytycznego BLOCKER DO DECYZJI.

## 15. Testy następcze, działanie walidacyjne, PRI/CONF i FINDINGS

### 15.1. Testy następcze (next_tests) i działanie walidacyjne (validation_action)

MGT-01 może rekomendować ponowne uruchomienie FIN-01, FIN-02, FIN-03, HR-01, CAP-01, CAP-02, PORT-01, PROC-01 albo PROC-02 po usunięciu luki informacyjnej. Może również wskazać działanie walidacyjne (validation_action) zamiast kolejnego testu. Nie projektuje orkiestracji Core 10 ani MGT-02.

| validation_action – przykłady | Znaczenie |
| --- | --- |
| uzgodnij definicję | usuń konflikt / niejednoznaczność |
| uzgodnij zakres | doprowadź licznik/mianownik/okres do wspólnej granicy |
| potwierdź właściciela informacji | ustanów punkt odpowiedzialności, jeśli potrzebny |
| odtwórz pochodzenie informacji (lineage) | udokumentuj pochodzenie i transformacje |
| uzgodnij okres bieżący i odniesienia | przywróć porównywalność |
| zweryfikuj podstawę alokacji (allocation_basis) | potwierdź podstawę przypisania |
| uzupełnij brakujące źródło (missing_source) | pozyskaj wymagany obiekt informacji |
| potwierdź work_content | odblokuj zależną miarę zdolności |
| potwierdź mapowanie zdolności (capacity mapping) | odblokuj relację zapotrzebowanie ↔ zasób |
| uzgodnij definicję trasy (route definition) | przywróć porównywalność procesu |

### 15.2. Dane przekazywane do ZOP-PRI-01 – DO OPRACOWANIA

MGT-01 przekazuje do ZOP-PRI-01 dane diagnostyczne i deterministyczne liczniki w granicy jednej ewaluacji. Nie tworzy z nich Priority Score ani progów.

| Pole | Kontrakt |
| --- | --- |
| aggregation_scope | granica agregacji liczników; odpowiada decision_scope lub jawnie węższemu zakresowi ewaluacji |
| aggregation_period | okres agregacji liczników; jest evaluation_period dla poniższych liczników |
| information_gap_count | dla decision_id + decision_scope + aggregation_period: liczba unikalnych information_gap_id |
| blocked_metrics_count | liczba unikalnych kombinacji affected_test + blocked_metric + scope + period |
| blocked_tests_count | liczba unikalnych blocked_test / affected_test, dla których istnieje rzeczywista konsekwencja blokująca; ograniczenie bez blokady nie jest liczone |
| blocked_decisions_count | liczba unikalnych blocked_decision_id, których decision_information_status = decision_blocked |
| reconciliation_failure_count | liczba unikalnych reconciliation_id ze statusem unreconciled; reconciled, reconciled_with_explanation, not_comparable i not_applicable nie są liczone jako niepowodzenie uzgodnienia |
| pozostałe pola | decision_information_status; critical_information_gap; recurring_gap_flag; cross_test_inconsistency_flag; coverage_current; coverage_reference; decision_scope; affected_tests; affected_decisions; urgent_validation |

### 15.3. Dane przekazywane do ZOP-CONF-01 – DO OPRACOWANIA

MGT-01 przekazuje do ZOP-CONF-01 jawne rekordy wymiarów oraz szczegółowe pola źródłowe. Każdy element przekazywanego zestawu danych ma kontrakt w MGT-01; nie powstaje lokalny Confidence Score.

| Pole | Kontrakt |
| --- | --- |
| information_dimension_statuses | zbiór rekordów: information_dimension_name + information_dimension_status + information_dimension_basis; opcjonalnie information_dimension_limitations / information_dimension_evidence / information_dimension_validation_required; bez agregacji do jednego wskaźnika |
| definition_status / scope_status / period_alignment_status | szczegółowe istniejące pola źródłowe zachowane zgodnie z ich kontraktami |
| coverage_current / coverage_reference | wartości pokrycia wraz z coverage_basis; bez arbitralnego progu |
| granularity_fit / timeliness_fit | szczegółowe dopasowanie do wymagań kontekstu decyzji (decision_context) |
| lineage_status / traceability_status / reproducibility_status | szczegółowe statusy pochodzenia, śledzenia i odtwarzalności |
| reconciliation_status / trend_comparability_status / transformation_status | szczegółowe statusy zgodnie z kontraktami MGT-01 |
| manual_data_validation_status | istniejące pole z kontraktu manual_data; używane zamiast niezdefiniowanego manual_validation_status |
| data_conflict_flag / cross_test_inconsistency_flag / critical_information_gap | szczegółowe flagi przekazywane bez lokalnego wskaźnika |
| zakaz niejednoznacznych pól | source_quality i comparability_status nie występują jako samodzielne niezdefiniowane pola przekazywanego zestawu danych; odpowiadają im rekordy information_dimension_statuses dla source_quality i comparability |

### 15.4. FINDINGS – pola bazowe

| Pole bazowe | Reguła MGT-01 |
| --- | --- |
| test_id | MGT-01 |
| scope | decision_scope / information_object_scope |
| period | decision_period / information_object_period |
| status | wspólny status logiczny X-Ray |
| finding | komunikat faktograficzny o przydatności informacji i ograniczeniach |
| metric_value | główna oceniana wartość / status obiektu |
| reference_value | wartość referencyjna, jeśli dotyczy |
| gap | luka uzgodnienia / luka pokrycia / właściwe odchylenie albo null |
| impact_low / impact_high | null, chyba że istnieje osobna odpowiedzialna metodologia; nie wyceniaj luki informacyjnej automatycznie |
| confidence_score / confidence_class | wynik ZOP-CONF-01 albo null |
| next_tests | test_id + uzasadnienie albo validation_action |
| validation_required | wartość logiczna + validation_notes |

### 15.5. FINDINGS – rozszerzenia MGT-01

decision_id; decision_question; decision_scope; decision_information_status; information_object_id; information_object_name; information_object_type; source_type; source_system; source_object; source_field; source_owner; definition_status; definition_source; definition_version; scope_status; period_status; coverage_current; coverage_reference; coverage_basis; granularity_fit; timeliness_fit; lineage_status; traceability_status; reproducibility_status; reconciliation_status; semantic_consistency_status; trend_comparability_status; transformation_status; unit_status; manual_data_flag; estimate_flag; assumption_flag; data_conflict_flag; method_change_flag; critical_information_gap; information_gap_id; information_gap_type; missing_information_element; blocked_metric; affected_test; affected_decision; gap_consequence; workaround_available; validation_action; information_owner; exclusion_flags; validation_notes; information_dimension_name; information_dimension_status; information_dimension_basis; information_dimension_limitations; information_dimension_evidence; information_dimension_validation_required; aggregation_scope; aggregation_period

## 16. Statusy logiczne i komunikat zarządczy

| Status logiczny X-Ray | Znaczenie w MGT-01 |
| --- | --- |
| NO_ADVERSE_SIGNAL | brak potwierdzonego ograniczenia informacyjnego dla badanego zakres |
| ADVERSE_SIGNAL | istnieje luka/niespójność wymagająca walidacji |
| INCIDENT | jednorazowe zdarzenie informacyjne |
| DETERIORATING | jakość/przydatność informacji pogarsza się w porównywalnym trendzie |
| STABLE | brak trwałego kierunku |
| IMPROVING | potwierdzona poprawa |
| TEST_PARTIAL | część wymiarów/wniosków dostępna |
| TEST_BLOCKED | brak podstaw do zależnego modułu |

decision_information_status oraz information_dimension_status (korzystający z katalogu dimension_status) są odrębnymi opisami technicznymi i nie zastępują wspólnego statusu X-Ray. Każdy information_dimension_status dotyczy jednego konkretnego wymiaru; nie istnieje automatyczny status zagregowany.

> **WZORZEC KOMUNIKATU [STATUS] JAKOŚĆ INFORMACJI ZARZĄDCZEJ. Dla decyzji [decision_question] dostępna informacja ma status [decision_information_status]. Dostępne są wymagane obiekty informacji [required_information_objects], natomiast ograniczenia dotyczą luk informacyjnych [information_gap_id / missing_information_element]. Pokrycie wynosi [coverage_current / coverage_reference], a główne problemy dotyczą [information_dimension_name / information_dimension_status]. W konsekwencji możliwe jest [dopuszczalny wniosek], natomiast nie można odpowiedzialnie stwierdzić [zablokowany wniosek]. Brakująca informacja wpływa na testy [affected_test]. Zalecane działanie walidacyjne: [validation_action].**

Zakazane automatyczne komunikaty: „organizacja ma złe dane”; „system IT jest zły”; „pracownicy źle raportują”; „trzeba kupić ERP”; „trzeba wdrożyć BI”.

## 17. Scenariusze regresyjne MGT01-T01–T35

| Scenariusz | Dane / warunek | Oczekiwane |
| --- | --- | --- |
| MGT01-T01 – pełna gotowość decyzyjna | obiekty informacji klasy required dostępne; zakres, okres i porównywalność poprawne | decision_ready |
| MGT01-T02 – brak pola opcjonalnego | brak informacji klasy optional | decision_ready_with_limitations |
| MGT01-T03 – brak wymaganego mianownika | brak mianownika klasy required | blocked_metric + decision_blocked |
| MGT01-T04 – okres bieżący dostępny, brak okresu odniesienia | miara bieżąca poprawna; porównanie niedostępne | miara bieżąca dostępna; decision_partial |
| MGT01-T05 – definicja różna między okresami | okres bieżący i odniesienia mają różną definition_version | brak porównywalności |
| MGT01-T06 – ta sama nazwa, różna definicja w testach | semantyka pola konfliktowa | niespójność semantyczna |
| MGT01-T07 – różne zakresy, poprawnie wyjaśnione | wartości różne z powodu jawnej różnicy zakresu | reconciled_with_explanation |
| MGT01-T08 – różne zakresy, brak wyjaśnienia | brak reconciliation_explanation | unreconciled |
| MGT01-T09 – pokrycie 70%, brakujący zakres niewymagany | brakujące 30% dotyczy informacji kontekstowej | decision_ready_with_limitations |
| MGT01-T10 – pokrycie 95%, brakujące 5% obejmuje element wymagany | brak kluczowej populacji | decision_blocked / partial; brak progu |
| MGT01-T11 – poprawna dana ręczna | rejestr ręczny + właściciel + walidacja | brak automatycznego obniżenia statusu |
| MGT01-T12 – dane systemowe z błędnym mapowaniem | rekord systemowy; nieprawidłowy mapping_version | informacja niegotowa do decyzji |
| MGT01-T13 – szacunek z jawną metodą | estimate_basis i nota o niepewności są obecne | możliwe użycie z ograniczeniami |
| MGT01-T14 – szacunek bez podstawy | estimate_flag=true; brak podstawy | nie udawaj wartości zmierzonej |
| MGT01-T15 – null zamieniony na zero | brak źródła; zapisano 0 | niepowodzenie walidacji |
| MGT01-T16 – brak wymaganego poziomu szczegółowości | dane dostępne na poziomie jednostki; wymagane na poziomie zmiany | niewystarczający poziom szczegółowości |
| MGT01-T17 – zbyt stara informacja dla decyzji operacyjnej | data_as_of nie spełnia required_timeliness | niedopasowanie aktualności |
| MGT01-T18 – ta sama informacja wystarczająco aktualna dla decyzji strategicznej | wymaganie required_timeliness jest szersze | fit |
| MGT01-T19 – FIN-01 i FIN-02 – przychód zgodny | ten sam zakres/okres/podstawa | reconciled |
| MGT01-T20 – FIN-01 i FIN-02 – przychód różny z powodu zakresu | różnica udokumentowana | reconciled_with_explanation |
| MGT01-T21 – FIN-01 i FIN-02 – przychód różny bez wyjaśnienia | brak podstawy różnicy | niespójność między testami |
| MGT01-T22 – mianownik FIN-03 nieporównywalny | mianownik bieżący poprawny; mianownik odniesienia nieporównywalny | bieżący UC może pozostać; luka porównawcza zablokowana |
| MGT01-T23 – CAP-02 bez work_content | wymagany work_content jest niedostępny | required_capacity jest zablokowane; wniosek o niedoborze zablokowany |
| MGT01-T24 – PROC bez ready_at | ready_at jest niedostępne | queue_time zablokowane; czas etapu dostępny |
| MGT01-T25 – zmiana podstawy alokacji | allocation_version uległa zmianie | zmiana metody + kontrola porównywalności |
| MGT01-T26 – przeliczona historia | nowa metoda + historia przeliczona | porównywalność trendu może zostać odzyskana |
| MGT01-T27 – nierozstrzygnięty konflikt danych | dwa wymagane źródła; brak rozstrzygnięcia | decision_blocked / decision_partial |
| MGT01-T28 – ręczne rozwiązanie zastępcze | brak pola systemowego; kontrolowany rejestr | możliwy status decision_ready_with_limitations |
| MGT01-T29 – powtarzalna luka informacyjna | ta sama luka w wielu okresach | recurring_gap_flag=true |
| MGT01-T30 – brak właściciela informacji przy pełnym pochodzeniu informacji | brak właściciela informacji; pełna odtwarzalność | luka dotycząca właściciela widoczna; brak automatycznej blokady |
| MGT01-T31 – techniczna tolerancja a różnica biznesowa | różnica przekracza tolerancję zaokrągleń/precyzji | nie maskuj jej tolerancją techniczną; istotność biznesowa poza MGT-01 |
| MGT01-T32 – brak decision_context | informacja istnieje, lecz nie znamy wymagań decyzji | decision_information_status=not_assessable |
| MGT01-T33 – dwa wymiary, różne statusy | dla jednego information_object: definition_quality = fit; comparability = failed | dwa oddzielne rekordy information_dimension_status; brak jednego zagregowanego statusu; failed comparability może blokować porównanie mimo poprawnej definicji |
| MGT01-T34 – dane CONF bez niezdefiniowanych pól | generowany zestaw danych przekazywanych do CONF | każdy element ma źródło lub kontrakt; brak samodzielnego niezdefiniowanego source_quality i comparability_status; używane manual_data_validation_status |
| MGT01-T35 – jedna luka blokuje wiele elementów | jeden information_gap_id blokuje 2 miary, 2 testy i 1 decyzję | information_gap_count=1; blocked_metrics_count=2; blocked_tests_count=2; blocked_decisions_count=1; bez podwójnego liczenia samej luki |

## 18. Walidacja MGT01-VAL-01–66

| Id | Kontrola | Skutek negatywny |
| --- | --- | --- |
| MGT01-VAL-01 | decision_context istnieje i ma decision_id / decision_question / decision_scope / decision_period | CRITICAL dla gotowości decyzyjnej |
| MGT01-VAL-02 | decision_required_metrics są jawne | WARNING/CRITICAL |
| MGT01-VAL-03 | decision_required_granularity jest znana | WARNING/CRITICAL |
| MGT01-VAL-04 | decision_required_timeliness jest znana | WARNING/CRITICAL |
| MGT01-VAL-05 | decision_required_comparability jest znana | WARNING/CRITICAL |
| MGT01-VAL-06 | decision_required_lineage jest znane | WARNING/CRITICAL |
| MGT01-VAL-07 | information_object_id jest jednoznaczny | CRITICAL dla śledzenia |
| MGT01-VAL-08 | information_object_scope jest jawny | CRITICAL dla porównania zakresu |
| MGT01-VAL-09 | information_object_period jest jawny | CRITICAL dla okresu |
| MGT01-VAL-10 | source_type i referencja źródłowa są jawne | WARNING/CRITICAL |
| MGT01-VAL-11 | dla source_authority istnieje podstawa, jeśli pole jest używane | WARNING |
| MGT01-VAL-12 | definition_status jest znany | WARNING/CRITICAL |
| MGT01-VAL-13 | definition_source istnieje dla pola klasy required | WARNING/CRITICAL |
| MGT01-VAL-14 | definition_version jest znana przy porównaniu | WARNING/CRITICAL |
| MGT01-VAL-15 | semantic_consistency_status nie wskazuje niewyjaśnionego konfliktu | CRITICAL dla zależnego porównania |
| MGT01-VAL-16 | scope_status odpowiada decision_scope | WARNING/CRITICAL |
| MGT01-VAL-17 | scope_comparability jest znana dla okresu bieżącego i odniesienia | WARNING/CRITICAL |
| MGT01-VAL-18 | period_status jest znany | WARNING/CRITICAL |
| MGT01-VAL-19 | period_alignment_status jest poprawny | CRITICAL dla niezgodnych okresów |
| MGT01-VAL-20 | period_comparability jest znana | WARNING/CRITICAL |
| MGT01-VAL-21 | coverage_current ma jawny coverage_basis | WARNING |
| MGT01-VAL-22 | coverage_reference ma jawny coverage_basis | WARNING |
| MGT01-VAL-23 | pokrycie nie jest interpretowane przez arbitralny próg | CRITICAL dla metodologii |
| MGT01-VAL-24 | coverage_missing_scope jest jawny, gdy pokrycie nie obejmuje pełnego zakresu | WARNING |
| MGT01-VAL-25 | available_granularity jest znana | WARNING |
| MGT01-VAL-26 | granularity_fit odpowiada required_granularity | WARNING/CRITICAL |
| MGT01-VAL-27 | data_as_of / opóźnienie raportowania są dostępne, jeśli wymagane | WARNING |
| MGT01-VAL-28 | timeliness_fit porównuje się z required_timeliness | WARNING/CRITICAL |
| MGT01-VAL-29 | lineage_status jest jawny | WARNING/CRITICAL |

### MGT01-VAL-30–66 – ciąg dalszy

| Id | Kontrola | Skutek negatywny |
| --- | --- | --- |
| MGT01-VAL-30 | traceability_status jest jawny | WARNING/CRITICAL |
| MGT01-VAL-31 | reproducibility_status jest jawny | WARNING/CRITICAL |
| MGT01-VAL-32 | reconciliation_status jest jawny dla wspólnej miary | WARNING/CRITICAL |
| MGT01-VAL-33 | reconciled_with_explanation ma reconciliation_explanation | WARNING |
| MGT01-VAL-34 | unit_status jest spójny; konwersja ma podstawę | CRITICAL przy mieszaniu jednostek |
| MGT01-VAL-35 | null semantics są jawne | CRITICAL dla zależnych pól |
| MGT01-VAL-36 | zero nie zastępuje null | CRITICAL |
| MGT01-VAL-37 | manual_data_flag ma kontrolę/walidację, jeśli jest to wymagane | WARNING/CRITICAL |
| MGT01-VAL-38 | system_generated_flag nie omija walidacji | CRITICAL dla metodologii |
| MGT01-VAL-39 | estimate_flag ma method/podstawa, jeśli używany | WARNING/CRITICAL |
| MGT01-VAL-40 | assumption_flag rozdziela założenie od danych | CRITICAL przy pomieszaniu |
| MGT01-VAL-41 | transformation_status i version są jawne dla derived miara | WARNING/CRITICAL |
| MGT01-VAL-42 | method_change_flag jest obsłużony | WARNING/CRITICAL dla trendu |
| MGT01-VAL-43 | historical_restated_flag jest znany przy zmianie metody | WARNING |
| MGT01-VAL-44 | duplicate_status rozróżnia repeat/rework od błędu | CRITICAL przy automatycznej deduplikacji |
| MGT01-VAL-45 | referential_integrity_status jest znany dla kluczowych relacji | WARNING/CRITICAL |
| MGT01-VAL-46 | information_owner / source_owner / validation_owner są jawni, jeśli wymagani | WARNING |
| MGT01-VAL-47 | information_gap ma jawny brakujący element i konsekwencję | CRITICAL dla mapy luki |
| MGT01-VAL-48 | blocked_metric ma blocked_reason i blocking_information_object | CRITICAL dla decyzji blokowanej |
| MGT01-VAL-49 | blocked_decision ma blocked_decision_reason | CRITICAL dla decision_blocked |
| MGT01-VAL-50 | information_requirement_class jest jawny | CRITICAL dla bramy gotowości decyzyjnej |
| MGT01-VAL-51 | rozwiązanie zastępcze ma podstawę i jawne ograniczenia | CRITICAL, jeśli ma odblokować informację klasy required |
| MGT01-VAL-52 | konflikt danych ma status rozstrzygnięcia | WARNING/CRITICAL |
| MGT01-VAL-53 | freshness_status wynika z required_timeliness, nie globalnego progu | CRITICAL dla metodologii |
| MGT01-VAL-54 | trend_comparability_status jest znany przy trendzie | WARNING/CRITICAL |
| MGT01-VAL-55 | między testami pole rejestr wskazuje źródło definicji, nie redefiniuje pola | CRITICAL |
| MGT01-VAL-56 | macierz uzgodnień Core 10 obejmuje wymagane pary | CRITICAL dla interfejsu |
| MGT01-VAL-57 | tolerancja techniczna ma wyłącznie podstawa precyzji/zaokrągleń/format | CRITICAL przy wprowadzaniu istotności biznesowej |
| MGT01-VAL-58 | brama gotowości decyzyjnej nie wymaga 100% danych organizacji i nie tworzy wskaźnika jakości | CRITICAL dla metodologii |
| MGT01-VAL-59 | każdy rekord information_dimension_status ma decision_id + information_object_id + scope + period + information_dimension_name | CRITICAL dla interpretacji wymiaru |
| MGT01-VAL-60 | information_dimension_status korzysta wyłącznie z katalogu dimension_status i nie jest agregowany do wspólnego wskaźnika ani średniej | CRITICAL dla metodologii |
| MGT01-VAL-61 | dane przekazywane do CONF używają information_dimension_statuses z information_dimension_name + information_dimension_status + information_dimension_basis; brak niezdefiniowanych source_quality / comparability_status | CRITICAL dla interfejsu CONF |
| MGT01-VAL-62 | dane przekazywane do CONF używają manual_data_validation_status zgodnie z istniejącym kontraktem manual_data | WARNING/CRITICAL dla interfejsu CONF |
| MGT01-VAL-63 | liczniki PRI są liczone dla decision_id + decision_scope + aggregation_period i mają jawne aggregation_scope/aggregation_period | CRITICAL dla agregacji PRI |
| MGT01-VAL-64 | blocked_tests_count liczy tylko rzeczywiste konsekwencje blokujące, a reconciliation_failure_count wyłącznie unreconciled | CRITICAL przy podwójnym lub błędnym liczeniu |
| MGT01-VAL-65 | rejestr dziedziczonych otwartych kontraktów Core 10 istnieje i nie oznacza ich rozwiązania przez MGT-01 | CRITICAL dla statusu Core 10 |
| MGT01-VAL-66 | scenariusze MGT01-T01–T35 są kompletne i obejmują T33–T35 | CRITICAL dla regresji |

## 19. Kryteria odbioru implementacji MGT01-ACC-01–101

| Id | Kontrola | Id | Kontrola |
| --- | --- | --- | --- |
| MGT01-ACC-01 | MGT-01 jest uniwersalny branżowo – PASS | MGT01-ACC-02 | MGT-01 nie jest audytem IT – PASS |
| MGT01-ACC-03 | MGT-01 ≠ ZOP-CONF-01 – PASS | MGT01-ACC-04 | MGT-01 ≠ ZOP-PRI-01 – PASS |
| MGT01-ACC-05 | brak wskaźnika jakości danych (Data Quality Score) – PASS | MGT01-ACC-06 | decision_context kompletny – PASS |
| MGT01-ACC-07 | decision_id i question jawne – PASS | MGT01-ACC-08 | decision_scope i okres jawne – PASS |
| MGT01-ACC-09 | wymagany miary jawne – PASS | MGT01-ACC-10 | required_granularity jawna – PASS |
| MGT01-ACC-11 | required_timeliness jawna – PASS | MGT01-ACC-12 | wymagany comparability jawna – PASS |
| MGT01-ACC-13 | decision_required_lineage jawne – PASS | MGT01-ACC-14 | decision_information_status ma 5 wartości – PASS |
| MGT01-ACC-15 | decision_ready ma bramę wymaganych informacji – PASS | MGT01-ACC-16 | ready_with_limitations zachowuje ograniczenia – PASS |
| MGT01-ACC-17 | decision_partial zachowuje częściowy wynik – PASS | MGT01-ACC-18 | decision_blocked tylko dla wymagany blocker – PASS |
| MGT01-ACC-19 | not_assessable ≠ decision_blocked – PASS | MGT01-ACC-20 | information_object ma id/name/type – PASS |
| MGT01-ACC-21 | information_object ma zakres/okres – PASS | MGT01-ACC-22 | source_type neutralny jakościowo – PASS |
| MGT01-ACC-23 | dla source_authority istnieje podstawa – PASS | MGT01-ACC-24 | pola pochodzenia informacji kompletne – PASS |
| MGT01-ACC-25 | lineage_status działa – PASS | MGT01-ACC-26 | traceability_status działa – PASS |
| MGT01-ACC-27 | reproducibility_status działa – PASS | MGT01-ACC-28 | definition_status działa – PASS |
| MGT01-ACC-29 | źródło, wersja i daty obowiązywania definicji – PASS | MGT01-ACC-30 | spójność semantyczna między testami – PASS |
| MGT01-ACC-31 | jakość zakresu działa – PASS | MGT01-ACC-32 | okres alignment działa – PASS |
| MGT01-ACC-33 | coverage_current / coverage_reference osobne – PASS | MGT01-ACC-34 | coverage_basis jawna – PASS |
| MGT01-ACC-35 | brak arbitralnego progu pokrycia – PASS | MGT01-ACC-36 | poziom szczegółowości fit działa – PASS |
| MGT01-ACC-37 | aktualność fit działa – PASS | MGT01-ACC-38 | brak globalnego progu aktualności – PASS |
| MGT01-ACC-39 | opóźnienie raportowania jawne – PASS | MGT01-ACC-40 | unit consistency działa – PASS |
| MGT01-ACC-41 | conversion podstawa jawna – PASS | MGT01-ACC-42 | null semantics 5 typów – PASS |
| MGT01-ACC-43 | zero ≠ null – PASS | MGT01-ACC-44 | dane ręczne nie jest karane automatycznie – PASS |
| MGT01-ACC-45 | dane systemowe nie jest promowane automatycznie – PASS | MGT01-ACC-46 | szacunek jawny – PASS |

### MGT01-ACC-47–101 – ciąg dalszy

| Id | Kontrola | Id | Kontrola |
| --- | --- | --- | --- |
| MGT01-ACC-47 | założenie ≠ dana – PASS | MGT01-ACC-48 | transformation version jawna – PASS |
| MGT01-ACC-49 | zmiana metody jawna – PASS | MGT01-ACC-50 | przeliczona historia obsłużona – PASS |
| MGT01-ACC-51 | duplicate semantyka bez auto-dedupe – PASS | MGT01-ACC-52 | integralność referencyjna jest kontrolowana – PASS |
| MGT01-ACC-53 | ownership pola obecne – PASS | MGT01-ACC-54 | właściciel informacji ≠ winny – PASS |
| MGT01-ACC-55 | information_gap kontrakt kompletny – PASS | MGT01-ACC-56 | luka consequence kompletne – PASS |
| MGT01-ACC-57 | blocked_metric mapowany – PASS | MGT01-ACC-58 | blocked_test mapowany – PASS |
| MGT01-ACC-59 | blocked_decision mapowany – PASS | MGT01-ACC-60 | requirement class działa – PASS |
| MGT01-ACC-61 | decision_rule_binding minimalny – PASS | MGT01-ACC-62 | rozwiązanie zastępcze ma podstawę – PASS |
| MGT01-ACC-63 | rozwiązanie zastępcze nie jest zgadywaniem – PASS | MGT01-ACC-64 | rozstrzygnięcie konfliktu status działa – PASS |
| MGT01-ACC-65 | brak arbitralnego wyboru źródła – PASS | MGT01-ACC-66 | aktualność względem decyzji – PASS |
| MGT01-ACC-67 | status stabilności informacji – PASS | MGT01-ACC-68 | status porównywalności trendu – PASS |
| MGT01-ACC-69 | automation neutralna dla jakości – PASS | MGT01-ACC-70 | kontrakt danych zewnętrznych kompletny – PASS |
| MGT01-ACC-71 | katalog statusów uzgodnienia kompletny – PASS | MGT01-ACC-72 | niezgodność uzgodnienia ≠ złe dane – PASS |
| MGT01-ACC-73 | tolerancja techniczna wyłącznie techniczna – PASS | MGT01-ACC-74 | istotność biznesowa poza MGT – PASS |
| MGT01-ACC-75 | 16 wymiary bez agregacji – PASS | MGT01-ACC-76 | dimension_status katalog kompletny – PASS |
| MGT01-ACC-77 | critical_information_gap zależny od konkretnej decyzji – PASS | MGT01-ACC-78 | dług informacyjny bez wyceny pieniężnej – PASS |
| MGT01-ACC-79 | recurring luka rozpoznany – PASS | MGT01-ACC-80 | minimalny rejestr pól Core 10 – PASS |
| MGT01-ACC-81 | macierz uzgodnień Core 10 kompletna – PASS | MGT01-ACC-82 | kontrakt niespójności między testami – PASS |
| MGT01-ACC-83 | macierz gotowości informacyjnej istnieje – PASS | MGT01-ACC-84 | mapa blokad decyzyjnych istnieje – PASS |
| MGT01-ACC-85 | kontrakt grafu zależności istnieje – PASS | MGT01-ACC-86 | next_tests tylko 9 zamrożonych testów – PASS |
| MGT01-ACC-87 | validation_action istnieje – PASS | MGT01-ACC-88 | dane przekazywane do PRI kompletne – PASS |
| MGT01-ACC-89 | dane przekazywane do CONF kompletne – PASS | MGT01-ACC-90 | FINDINGS bazowe zachowane – PASS |
| MGT01-ACC-91 | FINDINGS rozszerzenia kompletne – PASS | MGT01-ACC-92 | MGT01-T01–T32 kompletne – PASS |
| MGT01-ACC-93 | 0 automatycznych rekomendacji IT – PASS |  |  |
| MGT01-ACC-94 | information_dimension record związany z decyzją, obiektem, zakres, okres i wymiarem – PASS | MGT01-ACC-95 | różne wymiary jednego obiektu mogą mieć różne statusy – PASS |
| MGT01-ACC-96 | brak agregacji dimension_status do wskaźnika/średniej – PASS | MGT01-ACC-97 | dane przekazywane do CONF obejmują information_dimension_statuses z jawnym kontraktem – PASS |
| MGT01-ACC-98 | CONF używa manual_data_validation_status; brak niezdefiniowanych source_quality/comparability_status – PASS | MGT01-ACC-99 | PRI counters są deterministyczne i mają aggregation_scope/aggregation_period – PASS |
| MGT01-ACC-100 | dziedziczone otwarte kontrakty Core 10 są jawne i pozostają nierozwiązane – PASS | MGT01-ACC-101 | MGT01-T01–T35 kompletne – PASS |

## 20. Definicja ukończenia (Definition of Done) MGT01-DOD-01–95

| Id | Kontrola | Id | Kontrola |
| --- | --- | --- | --- |
| MGT01-DOD-01 | cel i pytanie diagnostyczne – PASS | MGT01-DOD-02 | granica MGT/CONF – PASS |
| MGT01-DOD-03 | granica MGT/PRI – PASS | MGT01-DOD-04 | granica MGT/IT – PASS |
| MGT01-DOD-05 | kontekst decyzji – PASS | MGT01-DOD-06 | gotowość decyzyjna – PASS |
| MGT01-DOD-07 | obiekty informacji – PASS | MGT01-DOD-08 | typ źródła – PASS |
| MGT01-DOD-09 | autorytet źródła – PASS | MGT01-DOD-10 | jakość definicji – PASS |
| MGT01-DOD-11 | spójność semantyczna – PASS | MGT01-DOD-12 | jakość zakresu – PASS |
| MGT01-DOD-13 | jakość okresu – PASS | MGT01-DOD-14 | pokrycie – PASS |
| MGT01-DOD-15 | poziom szczegółowości – PASS | MGT01-DOD-16 | aktualność – PASS |
| MGT01-DOD-17 | pochodzenie informacji – PASS | MGT01-DOD-18 | możliwość prześledzenia – PASS |
| MGT01-DOD-19 | odtwarzalność – PASS | MGT01-DOD-20 | uzgodnienie – PASS |
| MGT01-DOD-21 | uzgodnienie między testami – PASS | MGT01-DOD-22 | rejestr pól kanonicznych – PASS |
| MGT01-DOD-23 | spójność jednostek – PASS | MGT01-DOD-24 | semantyka null – PASS |
| MGT01-DOD-25 | zero/null – PASS | MGT01-DOD-26 | dane ręczne – PASS |
| MGT01-DOD-27 | dane systemowe – PASS | MGT01-DOD-28 | szacunek – PASS |
| MGT01-DOD-29 | założenia – PASS | MGT01-DOD-30 | jakość transformacji – PASS |
| MGT01-DOD-31 | wersjonowanie – PASS | MGT01-DOD-32 | kontrola zmian – PASS |
| MGT01-DOD-33 | duplikaty – PASS | MGT01-DOD-34 | integralność referencyjna – PASS |
| MGT01-DOD-35 | właściciele informacji – PASS | MGT01-DOD-36 | luka informacyjna – PASS |
| MGT01-DOD-37 | typ luki informacyjnej – PASS | MGT01-DOD-38 | konsekwencja luki – PASS |
| MGT01-DOD-39 | zablokowana miara – PASS | MGT01-DOD-40 | zablokowany test – PASS |
| MGT01-DOD-41 | zablokowana decyzja – PASS | MGT01-DOD-42 | klasa wymagań informacyjnych – PASS |
| MGT01-DOD-43 | powiązanie reguły decyzji – PASS | MGT01-DOD-44 | brama gotowości decyzyjnej – PASS |
| MGT01-DOD-45 | decision_ready_with_limitations – PASS | MGT01-DOD-46 | decision_partial – PASS |
| MGT01-DOD-47 | decision_blocked – PASS | MGT01-DOD-48 | rozwiązanie zastępcze – PASS |
| MGT01-DOD-49 | konflikt danych – PASS | MGT01-DOD-50 | rozstrzygnięcie konfliktu – PASS |
| MGT01-DOD-51 | aktualność – PASS | MGT01-DOD-52 | stabilność informacji – PASS |
| MGT01-DOD-53 | porównywalność trendu – PASS | MGT01-DOD-54 | opóźnienie raportowania – PASS |
| MGT01-DOD-55 | status automatyzacji neutralny jakościowo – PASS | MGT01-DOD-56 | dane zewnętrzne – PASS |
| MGT01-DOD-57 | klasyfikacja niezgodności uzgodnienia – PASS | MGT01-DOD-58 | techniczna tolerancja uzgodnienia – PASS |
| MGT01-DOD-59 | istotność biznesowa poza MGT-01 – PASS | MGT01-DOD-60 | zakaz globalnego wskaźnika jakości danych (Data Quality Score) – PASS |
| MGT01-DOD-61 | wymiary jakości informacji – PASS | MGT01-DOD-62 | dimension_status – PASS |
| MGT01-DOD-63 | critical_information_gap – PASS | MGT01-DOD-64 | information_debt – PASS |
| MGT01-DOD-65 | recurring_gap – PASS | MGT01-DOD-66 | relacja z FIN-01 – PASS |
| MGT01-DOD-67 | relacja z FIN-02 – PASS | MGT01-DOD-68 | relacja z FIN-03 – PASS |
| MGT01-DOD-69 | relacja z HR-01 – PASS | MGT01-DOD-70 | relacja z CAP-01 – PASS |
| MGT01-DOD-71 | relacja z CAP-02 – PASS | MGT01-DOD-72 | relacja z PORT-01 – PASS |
| MGT01-DOD-73 | relacja z PROC-01 – PASS | MGT01-DOD-74 | relacja z PROC-02 – PASS |
| MGT01-DOD-75 | niespójność między testami – PASS | MGT01-DOD-76 | macierz gotowości informacyjnej – PASS |
| MGT01-DOD-77 | mapa blokad decyzyjnych – PASS | MGT01-DOD-78 | graf zależności informacji – PASS |
| MGT01-DOD-79 | next_tests – PASS | MGT01-DOD-80 | validation_action – PASS |
| MGT01-DOD-81 | dane przekazywane do ZOP-PRI-01 – PASS | MGT01-DOD-82 | dane przekazywane do ZOP-CONF-01 – PASS |
| MGT01-DOD-83 | FINDINGS – PASS | MGT01-DOD-84 | statusy logiczne – PASS |
| MGT01-DOD-85 | komunikat zarządczy – PASS | MGT01-DOD-86 | scenariusze T01–T32 – PASS |
| MGT01-DOD-87 | VAL kompletne – PASS | MGT01-DOD-88 | ACC kompletne – PASS |
| MGT01-DOD-89 | QMGT01 kompletne – PASS |  |  |
| MGT01-DOD-90 | kontrakt information_dimension_name/status/podstawa/limitations/evidence/validation – PASS | MGT01-DOD-91 | dane przekazywane do ZOP-CONF-01 jednoznaczny i bez niezdefiniowanych pól – PASS |
| MGT01-DOD-92 | deterministyczne liczniki danych przekazywanych do ZOP-PRI-01 – PASS | MGT01-DOD-93 | aggregation_scope i aggregation_period – PASS |
| MGT01-DOD-94 | rejestr dziedziczonych otwartych kontraktów Core 10 – PASS | MGT01-DOD-95 | scenariusze T01–T35 i zachowanie statusu Core 10 – PASS |

## 21. Test końcowy QMGT01-01–131

| Id | Kontrola | Id | Kontrola |
| --- | --- | --- | --- |
| QMGT01-01 | MGT-01 jest uniwersalny branżowo – PASS | QMGT01-02 | MGT-01 nie jest audytem IT – PASS |
| QMGT01-03 | MGT-01 ≠ ZOP-CONF-01 – PASS | QMGT01-04 | MGT-01 ≠ ZOP-PRI-01 – PASS |
| QMGT01-05 | MGT-01 nie tworzy wskaźnika jakości danych (Data Quality Score) – PASS | QMGT01-06 | decision_context jest jawny – PASS |
| QMGT01-07 | decision_question jest jawne – PASS | QMGT01-08 | decision_scope jest jawny – PASS |
| QMGT01-09 | decision_period jest jawny – PASS | QMGT01-10 | wymagane informacje decyzji są jawne – PASS |
| QMGT01-11 | decision_information_status ma poprawną semantykę – PASS | QMGT01-12 | decision_ready wymaga tylko informacji potrzebnych konkretnej decyzji – PASS |
| QMGT01-13 | decision_ready_with_limitations zachowuje ograniczenia – PASS | QMGT01-14 | decision_partial zachowuje częściowo dostępne wnioski – PASS |
| QMGT01-15 | decision_blocked wymaga braku informacji klasy required – PASS | QMGT01-16 | not_assessable nie jest równoznaczne z decision_blocked – PASS |
| QMGT01-17 | brak informacji może być wynikiem diagnostycznym – PASS | QMGT01-18 | brak informacji nie jest zastępowany zerem – PASS |
| QMGT01-19 | zero ≠ null – PASS | QMGT01-20 | semantyka null jest rozdzielona – PASS |
| QMGT01-21 | null_missing ≠ null_not_applicable – PASS | QMGT01-22 | null_not_computable ≠ null_not_assessable – PASS |
| QMGT01-23 | null_blocked_by_validation ma odrębne znaczenie – PASS | QMGT01-24 | information_object ma identyfikator – PASS |
| QMGT01-25 | information_object ma zakres – PASS | QMGT01-26 | information_object ma okres – PASS |
| QMGT01-27 | pochodzenie informacji prowadzi od wyniku do źródła – PASS | QMGT01-28 | pochodzenie informacji może mieć status partial – PASS |
| QMGT01-29 | brak pochodzenia informacji jest jawny – PASS | QMGT01-30 | source_type nie determinuje jakości – PASS |
| QMGT01-31 | dane ręczne nie są automatycznie gorsze – PASS | QMGT01-32 | dane systemowe nie są automatycznie lepsze – PASS |
| QMGT01-33 | szacunek ≠ dane zmierzone – PASS | QMGT01-34 | założenie ≠ dane – PASS |
| QMGT01-35 | definicja ma źródło – PASS | QMGT01-36 | definicja ma wersję – PASS |
| QMGT01-37 | ta sama nazwa przy różnych definicjach jest wykrywana – PASS | QMGT01-38 | semantic_consistency_status działa przekrojowo – PASS |
| QMGT01-39 | zakres licznika i mianownika jest kontrolowany – PASS | QMGT01-40 | zakresy okresu bieżącego i odniesienia są kontrolowane – PASS |
| QMGT01-41 | okres bieżący i okres odniesienia są kontrolowane – PASS | QMGT01-42 | podstawa kalendarza/czasu jest kontrolowana – PASS |
| QMGT01-43 | pokrycie okresu bieżącego i odniesienia są osobne – PASS | QMGT01-44 | pokrycie ma podstawę – PASS |
| QMGT01-45 | brak arbitralnego progu pokrycia – PASS | QMGT01-46 | 95% pokrycia może blokować decyzję, jeśli brakujący zakres jest krytyczny – PASS |
| QMGT01-47 | 70% pokrycie może pozwolić na decyzję z ograniczeniami – PASS | QMGT01-48 | dostępny i wymagany poziom szczegółowości są porównywane – PASS |
| QMGT01-49 | coarser_than_required może blokować decyzję – PASS | QMGT01-50 | finer_than_required nie jest automatycznie problemem – PASS |
| QMGT01-51 | aktualność względem wymagań decyzji – PASS | QMGT01-52 | brak globalnej reguły wieku danych – PASS |
| QMGT01-53 | możliwość prześledzenia (traceability) ≠ pochodzenie informacji (lineage) – PASS | QMGT01-54 | odtwarzalność jest oceniana – PASS |
| QMGT01-55 | wynik jest odtwarzalny na tych samych źródłach/regułach – PASS | QMGT01-56 | uzgodnienie rozróżnia konflikt od różnicy zakresu – PASS |
| QMGT01-57 | reconciled_with_explanation ma własne znaczenie – PASS | QMGT01-58 | unreconciled ≠ automatycznie złe źródło – PASS |
| QMGT01-59 | uzgodnienie między testami obejmuje Core 10 – PASS | QMGT01-60 | FIN-01 ↔ FIN-02 uzgadniane – PASS |

### QMGT01-61–131 – ciąg dalszy

| Id | Kontrola | Id | Kontrola |
| --- | --- | --- | --- |
| QMGT01-61 | FIN-02 ↔ FIN-03 uzgadniane – PASS | QMGT01-62 | FIN-03 ↔ PORT-01 uzgadniane – PASS |
| QMGT01-63 | HR-01 ↔ FIN-03 uzgadniane – PASS | QMGT01-64 | CAP-01 ↔ CAP-02 uzgadniane – PASS |
| QMGT01-65 | CAP-02 ↔ PROC-02 uzgadniane – PASS | QMGT01-66 | PROC-01 ↔ PROC-02 uzgadniane – PASS |
| QMGT01-67 | różny zakres nie jest fałszywym błędem – PASS | QMGT01-68 | canonical_field_name nie redefiniuje źródła – PASS |
| QMGT01-69 | rejestr pól nie staje się pełnym MDM – PASS | QMGT01-70 | spójność jednostek jest kontrolowana – PASS |
| QMGT01-71 | konwersja jednostki ma podstawę – PASS | QMGT01-72 | PLN ≠ tys. PLN – PASS |
| QMGT01-73 | minuty ≠ godziny bez konwersji – PASS | QMGT01-74 | duplikat może oznaczać legalne repeat/rework – PASS |
| QMGT01-75 | brak semantycznej automatycznej deduplikacji – PASS | QMGT01-76 | integralność referencyjna jest kontrolowana – PASS |
| QMGT01-77 | właściciel informacji ≠ winny – PASS | QMGT01-78 | brak właściciela informacji nie blokuje automatycznie – PASS |
| QMGT01-79 | luka informacyjna ma konsekwencję – PASS | QMGT01-80 | missing_information_element jawny – PASS |
| QMGT01-81 | affected_test jawny – PASS | QMGT01-82 | blocked_metric jawny – PASS |
| QMGT01-83 | affected_decision jawna – PASS | QMGT01-84 | required / supporting / optional / contextual są rozdzielone – PASS |
| QMGT01-85 | brak informacji klasy optional nie blokuje – PASS | QMGT01-86 | brak informacji klasy required może blokować – PASS |
| QMGT01-87 | rozwiązanie zastępcze ma podstawę – PASS | QMGT01-88 | ręczne rozwiązanie zastępcze dopuszczalne warunkowo – PASS |
| QMGT01-89 | rozwiązanie zastępcze ≠ zgadywanie – PASS | QMGT01-90 | rozstrzygnięcie konfliktu bez arbitralnego nowszego/większego – PASS |
| QMGT01-91 | zmiana metody jawna – PASS | QMGT01-92 | zmiana metody może zniszczyć porównywalność trendu – PASS |
| QMGT01-93 | przeliczona historia może odzyskać porównywalność – PASS | QMGT01-94 | tolerancja techniczna służy wyłącznie precyzji/zaokrągleniom – PASS |
| QMGT01-95 | tolerancja techniczna ≠ istotność biznesowa – PASS | QMGT01-96 | istotność biznesowa poza MGT – PASS |
| QMGT01-97 | brak globalnego wskaźnika 0–100 – PASS | QMGT01-98 | brak średniej z wymiarów jakości – PASS |
| QMGT01-99 | brak HIGH/MEDIUM/LOW – PASS | QMGT01-100 | dimension_status = fit/fit_with_limitations/partial/failed/not_assessable – PASS |
| QMGT01-101 | critical_information_gap zależy od decyzji/testu – PASS | QMGT01-102 | dług informacyjny bez automatycznej wyceny – PASS |
| QMGT01-103 | luka powtarzalna ≠ incydent – PASS | QMGT01-104 | niespójność między testami bez auto-naprawy – PASS |
| QMGT01-105 | mapa blokad decyzyjnych: luka → miara → test → decyzja – PASS | QMGT01-106 | validation_action ≠ projekt wdrożeniowy – PASS |
| QMGT01-107 | MGT może rekomendować ponowne uruchomienie 9 testów – PASS | QMGT01-108 | MGT-02 nie jest projektowany – PASS |
| QMGT01-109 | PRI pozostaje DO OPRACOWANIA – PASS | QMGT01-110 | CONF pozostaje DO OPRACOWANIA – PASS |
| QMGT01-111 | dziewięć kart pozostaje niezmienionych – PASS | QMGT01-112 | istnieją 32 scenariusze – PASS |
| QMGT01-113 | VAL kompletne – PASS | QMGT01-114 | ACC kompletne – PASS |
| QMGT01-115 | DOD kompletne – PASS | QMGT01-116 | FINDINGS kompletne – PASS |
| QMGT01-117 | dokument gotowy dla Aleksandra – PASS | QMGT01-118 | 0 danych SPZOZ – PASS |
| QMGT01-119 | 0 danych pacjentów – PASS | QMGT01-120 | 0 MGT-02 – PASS |
| QMGT01-121 | zamknięcie MGT-01 daje metodologicznie kompletne Core 10 – PASS |  |  |
| QMGT01-122 | information_dimension_name wiąże status z konkretnym wymiarem – PASS | QMGT01-123 | jeden information_object może mieć różne statusy różnych wymiarów bez agregacji – PASS |
| QMGT01-124 | rekord wymiaru ma decision_id + information_object_id + scope + period + information_dimension_name – PASS | QMGT01-125 | CONF przekazuje information_dimension_statuses z name + status + podstawa – PASS |
| QMGT01-126 | CONF nie używa niezdefiniowanych source_quality ani comparability_status – PASS | QMGT01-127 | CONF używa manual_data_validation_status zgodnie z kontraktem – PASS |
| QMGT01-128 | liczniki PRI information_gap_count, blocked_metrics_count, blocked_tests_count i blocked_decisions_count mają definicje unikalności bez podwójnego liczenia – PASS | QMGT01-129 | PRI reconciliation_failure_count liczy tylko unreconciled i ma aggregation_scope / aggregation_period – PASS |
| QMGT01-130 | dziedziczone otwarte kontrakty pozostają otwarte mimo kompletności Core 10 – PASS | QMGT01-131 | MGT01-T01–T35 kompletne; status Core 10 zachowany – PASS |

## 22. Otwarte kwestie wspólne i status Core 10

### 22.1. Otwarte kwestie wspólne – poza MGT-01

| Kwestia | Status / wpływ |
| --- | --- |
| ZOP-CONF-01 | globalny mechanizm pewności pozostaje DO OPRACOWANIA |
| ZOP-PRI-01 | globalny mechanizm priorytetu pozostaje DO OPRACOWANIA |
| orkiestracja next_tests | MGT-01 rekomenduje, nie projektuje globalnego silnika |
| globalny rejestr definicji | MGT-01 tworzy tylko minimalny rejestr Core 10 |
| docelowa architektura master data | poza MGT-01 |
| docelowa architektura danych | poza MGT-01 |
| docelowy system wersjonowania organizacyjnego | poza MGT-01 |
| docelowe standardy integracji IT | poza MGT-01 |
| docelowy silnik reguł decyzyjnych / pełny graf zależności | MGT-01 definiuje minimalny kontrakt, nie silnik |
| globalna polityka istotności biznesowej | poza MGT-01; nie zastępowana tolerancją techniczną |

### 22.1.1. DZIEDZICZONE OTWARTE KONTRAKTY WSPÓLNE CORE 10

| Rodzina kontraktu | Status po zamknięciu MGT-01 |
| --- | --- |
| work_content | globalny kontrakt nadal DO OPRACOWANIA; MGT-01 kontroluje jego użycie, nie ustanawia standardu systemowego |
| activity_unit | globalny standard nadal DO OPRACOWANIA |
| weighted_volume | globalne reguły wag i porównywalności nadal DO OPRACOWANIA |
| alokacja kosztów wspólnych (shared cost allocation) | wspólna polityka alokacji nadal DO OPRACOWANIA |
| kalendarze operacyjne i podstawa czasu (operating calendars / time basis) | globalny standard kalendarzy operacyjnych i podstaw czasu nadal DO OPRACOWANIA |
| zgodność i substytucja zasobów (capability / resource substitution) | wspólne reguły zgodności i substytucji zasobów nadal DO OPRACOWANIA |
| globalna podstawa kosztowa (global cost basis) | wspólna podstawa kosztowa nadal DO OPRACOWANIA |
| klasyfikacja zdarzeń jednorazowych (one-off classification) | wspólna klasyfikacja korekt jednorazowych nadal DO OPRACOWANIA |
| orkiestracja testów następczych (next_tests orchestration) | globalna orkiestracja nadal DO OPRACOWANIA |
| ZOP-PRI-01 / ZOP-CONF-01 | oba mechanizmy pozostają DO OPRACOWANIA |

Core 10 może być kompletny metodologicznie jako biblioteka dziesięciu testów, mimo że powyższe wspólne kontrakty systemowe pozostają świadomie otwarte do kolejnego etapu. Minimalny CROSS_TEST_FIELD_REGISTRY nie oznacza rozwiązania tych kontraktów.

### 22.2. Kontrola zamrożonych interfejsów

| Dokument | Status | Zmiana przez MGT-01 |
| --- | --- | --- |
| FIN-01 | ZAMROŻONY v1.0 | 0 |
| FIN-02 | ZAMROŻONY v1.0 | 0 |
| FIN-03 | ZAMROŻONY v1.0 | 0 |
| CAP-01 | ZAMROŻONY v1.0 | 0 |
| CAP-02 | ZAMROŻONY v1.0 | 0 |
| HR-01 | ZAMROŻONY v1.0 | 0 |
| PORT-01 | ZAMROŻONY v1.0 | 0 |
| PROC-01 | ZAMROŻONY v1.0 | 0 |
| PROC-02 | ZAMROŻONY v1.0 | 0 |
| MGT-01 | NOWY v1.0 | zamknięty metodologicznie |

Kontrola dotyczyła wyłącznie spójności interfejsów. MGT-01 odwołuje się do istniejących pól bez zmiany ich matematyki i semantyki. Dane przekazywane do PRI/CONF pozostają jednokierunkowym przekazaniem informacji jakościowych; nie modyfikują kart źródłowych.

### 22.3. Wynik odbioru MGT-01

| Element | Wynik |
| --- | --- |
| MGT-01 | ZAMKNIĘTY METODOLOGICZNIE DO IMPLEMENTACJI |
| ZOP-PRI-01 | DO OPRACOWANIA |
| ZOP-CONF-01 | DO OPRACOWANIA |
| MGT01-VAL | 66/66 PASS |
| MGT01-ACC | 101/101 PASS |
| MGT01-DOD | 95/95 PASS |
| QMGT01 | 131/131 PASS |
| Scenariusze | 35 – MGT01-T01–T35 |
| Nierozwiązane blockery krytyczne | 0 |

> **STATUS CORE 10 ZOPTYMALIZOWANI X-RAY – CORE 10 KOMPLETNY METODOLOGICZNIE DO IMPLEMENTACJI**

Status oznacza zamkniętą bibliotekę dziesięciu podstawowych testów diagnostycznych X-Ray. Wspólne kontrakty systemowe wskazane w rejestrze otwartym pozostają do opracowania w kolejnych etapach i nie są uznawane za rozwiązane przez samo zamknięcie Core 10. Nie oznacza to gotowej aplikacji, gotowego ZOP-PRI-01, gotowego ZOP-CONF-01, gotowej orkiestracji ani warstwy AI.

0 wskaźników jakości danych typu Data Quality Score; 0 arbitralnych progów pokrycia; 0 arbitralnych progów aktualności; 0 arbitralnej istotności biznesowej; 0 nowych progów Priority Score; 0 nowych progów Confidence Score; 0 automatycznych rekomendacji IT; 0 danych SPZOZ; 0 danych pacjentów; 0 rozpoczętego MGT-02.
