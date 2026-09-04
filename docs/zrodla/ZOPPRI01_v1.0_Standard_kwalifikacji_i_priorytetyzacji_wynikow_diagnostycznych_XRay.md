ZOPTYMALIZOWANI – X-RAY

# PRI-01

*Standard kwalifikacji i priorytetyzacji wyników diagnostycznych X-Ray*

Karta metodologiczna i specyfikacja implementacyjna

| METADANE DOKUMENTU | WARTOŚĆ |
| --- | --- |
| Identyfikator | ZOP-PRI-01 |
| Wersja | v1.0 |
| Status | ZAMKNIĘTY METODOLOGICZNIE DO IMPLEMENTACJI |
| Zakres | Kwalifikacja wyników Core 10, priorytet problemu, priorytet walidacji i trasa uwagi zarządczej |
| Zależności | ZOP-CONF-01 – DO OPRACOWANIA; orkiestracja next_tests – DO OPRACOWANIA |
| Odbiorca implementacyjny | Aleksander / warstwa technologiczna X-Ray |

> **PYTANIE DIAGNOSTYCZNE Który z wykrytych problemów lub braków informacyjnych powinien otrzymać wcześniej uwagę zarządczą albo walidację – i na jakiej jawnej podstawie?**

## 1. Rola, cel i granice PRI-01

PRI-01 kwalifikuje konkretne wyniki diagnostyczne i luki informacyjne. Nie ustala ważności testów jako takich. Jego produktem jest audytowalny profil priorytetu, dwie niezależne kolejności działania oraz trasa uwagi zarządczej. Każda kwalifikacja pozostaje osadzona w określonym kontekście decyzji, zakresie, okresie i wersji podstawy.

| PRI-01 robi | PRI-01 nie robi |
| --- | --- |
| porządkuje uwagę wobec wyników diagnostycznych | nie tworzy globalnego wyniku punktowego 0–100 |
| oddziela priorytet problemu od priorytetu walidacji | nie zastępuje ZOP-CONF-01 |
| chroni wpływy przed podwójnym liczeniem | nie sumuje nieporównywalnych jednostek |
| pozwala rangować tylko grupy porównywalne | nie wydaje decyzji wykonawczych |
| przekazuje kontrakt do przyszłej orkiestracji | nie projektuje algorytmu uruchamiania testów |

### 1.1. Nienaruszalne rozdzielenia

| Rozdzielenie | Znaczenie implementacyjne |
| --- | --- |
| priority ≠ confidence | znaczenie i kolejność uwagi nie są miarą siły dowodu |
| problem priority ≠ validation priority | uwaga wobec problemu i pilność sprawdzenia informacji mają osobne pola |
| importance ≠ stability | ważność nie jest trwałością sygnału ani stabilnością kwalifikacji |
| supporting evidence ≠ second impact | dowód wspierający nie tworzy dodatkowej kwoty ani dodatkowej straty |
| related findings ≠ common cause | powiązanie nie dowodzi wspólnego mechanizmu przyczynowego |

### 1.2. Hierarchia źródeł i ochrona Core 10

Poziom 1 stanowią polecenie PRI-01 i zamrożone karty Core 10. Poziom 2 stanowią ZOP-TECH-01 oraz ZOP-MASTER-01. PRI-01 przejmuje pola źródłowe bez zmiany ich semantyki. Sprzeczności wartości nie rozstrzyga intuicyjnie: wykorzystuje statusy uzgodnienia i dane MGT-01.

> **ZASADA ZAMROŻENIA FIN-01, FIN-02, FIN-03, CAP-01, CAP-02, HR-01, PORT-01, PROC-01, PROC-02 i MGT-01 pozostają niezmienione.**

## 2. Jednostka analizy i kontekst priorytetu

| Obiekt | Pola obowiązkowe | Reguła |
| --- | --- | --- |
| wynik diagnostyczny | finding_id; source_test; finding_scope; finding_period; finding_status; finding_metric; finding_gap; finding_reference | jeden rekord opisuje jeden wynik źródłowy |
| luka informacyjna | information_gap_id; critical_information_gap; missing_information_element; affected_test; blocked_metric; affected_decision; gap_consequence | luka może mieć priorytet walidacji bez wyceny finansowej |
| kontekst priorytetu | priority_context_id; priority_scope; priority_period; priority_decision_context; priority_evaluation_date; priority_basis_version | wyników nie porównuje się poza kontekstem użycia |

### 2.1. Tożsamość i wersjonowanie

Połączenie finding_id + priority_context_id + priority_evaluation_date + priority_basis_version identyfikuje pojedynczą kwalifikację. Zmiana podstawy lub kontekstu tworzy nową ewaluację, nie nadpisuje śladu wcześniejszej oceny.

## 3. Profil priorytetu – bez wyniku punktowego

Profil jest zestawem jawnych przesłanek. Żaden wymiar nie otrzymuje arbitralnej wagi, a brak wartości nie jest zastępowany zerem. Profil może prowadzić do działania wyłącznie przez reguły kwalifikacji opisane w rozdziale 8.

| Wymiar profilu | Pola techniczne | Reguła kwalifikacji |
| --- | --- | --- |
| skala ekonomiczna | economic_impact_value; economic_impact_unit; economic_impact_period; economic_impact_scope; economic_impact_source; economic_impact_role | tylko wartość źródłowo mierzalna; bez przeliczania czasu i capacity na pieniądze |
| skala operacyjna | operational_impact_metric; operational_impact_value; operational_impact_unit; operational_impact_scope; operational_impact_period | jednostka źródłowa pozostaje zachowana |
| zakres oddziaływania | affected_scope_type; affected_scope_count; affected_units; affected_portfolio_items; affected_processes; affected_resources | szeroki zakres jest przesłanką, nie automatyczną klasą priorytetu |
| trwałość | persistence_status; persistence_periods; recurrence_count; recurring_signal_flag | incident; intermittent; persistent; resolved; unknown |
| trend | trend_direction; trend_basis | deteriorating; stable; improving; mixed; not_assessable |
| pilność | urgency_flag; urgency_basis; required_response_window; required_response_window_basis | termin lub warunek musi mieć jawną podstawę |
| zależności | downstream_tests_affected; blocked_metrics_count; blocked_tests_count; blocked_decisions_count; dependency_impact_basis | liczba powiązań nie jest przyczynowością |
| incydent / one-off | incident_flag; incident_basis; oneoff_flag; oneoff_basis | pilność i strukturalność są oceniane odrębnie |
| jakość podstawy | validation_required; reconciliation; comparability; coverage; MGT statusy; przyszłe pola CONF | brak CONF-01 nie tworzy zastępczego score |

### 3.1. Zamknięte katalogi trwałości, trendu i stabilności

| Pole | Katalog zamknięty | Znaczenie |
| --- | --- | --- |
| persistence_status | incident; intermittent; persistent; resolved; unknown | charakter występowania źródłowego sygnału |
| trend_direction | deteriorating; stable; improving; mixed; not_assessable | kierunek wyłącznie na porównywalnych okresach |
| priority_stability_status | stable; increasing_attention; decreasing_attention; fluctuating; unknown | stabilność samej kwalifikacji priorytetu |

priority_stability_periods i priority_change_reason dokumentują okres stabilności oraz powód zmiany. Zmiana kwalifikacji po usunięciu luki informacyjnej jest prawidłową aktualizacją, a nie błędem modelu.

### 3.2. Stabilność priorytetu w jednym wymiarze i kontekście

increasing_attention i decreasing_attention wynikają wyłącznie z porównania priority_action_previous z priority_action_current w tym samym priority_stability_dimension i priority_context_id. Kolejności semantyczne nie są Priority Score, nie służą do agregacji między wymiarami i nie przypisują porządku management_attention_route.

| Pole | Katalog zamknięty | Znaczenie |
| --- | --- | --- |
| priority_stability_dimension | problem_priority; validation_priority | porównanie zawsze w jednym wymiarze i tym samym priority_context_id |
| problem_priority | observe < plan_review < review_next < review_now | porządek służy wyłącznie do ustalenia zmiany uwagi w czasie |
| validation_priority | no_additional_validation < validate_when_needed < validate_next < validate_now | porządek służy wyłącznie do ustalenia zmiany pilności walidacji |
| priority_action_previous | poprzednie działanie w tym samym wymiarze i kontekście | wymagane dla oceny zmiany |
| priority_action_current | bieżące działanie w tym samym wymiarze i kontekście | wymagane dla oceny zmiany |
| priority_stability_basis | jawna podstawa zgodności wymiaru, kontekstu i okresów | brak podstawy oznacza unknown |
| not_assessable | nie uczestniczy w porządku | przejście z lub do not_assessable wymaga priority_change_reason; nie daje automatycznie increasing/decreasing_attention |
| management_attention_route | brak liniowego porządku | trasa nie jest używana do obliczania stabilności |

## 4. Źródła Core 10 i ich role w profilu

| Test | Rola diagnostyczna | Przykładowe wejścia do PRI-01 |
| --- | --- | --- |
| FIN-01 | luka dynamiki kosztów i przychodów | Gap / economic_scale; persistence; trend_direction; organizational_scope; result_risk; urgent_validation |
| FIN-02 | wynik, stopa rentowności, most wyniku i most marży | adverse amount/rate gaps; bridge shares; cost-load gaps; explanatory_evidence |
| FIN-03 | koszt jednostkowy i most koszt–mianownik | adverse_unit_cost_gap; effects; denominator comparability; coverage; evidence |
| PORT-01 | ekonomika portfela, miks i marże | adverse contribution/segment gaps; mix_effect; shares; portfolio scope |
| HR-01 | koszt pracy względem efektu | labor_cost_effect_gap; rate; productivity; unit labor cost; affected role groups |
| CAP-01 | wykorzystanie zdolności | utilization_gap; unused/capacity gap units; demand signal; affected resources |
| CAP-02 | presja, shortage i extra capacity dependency | capacity gaps; pressure ratio; overload status; duration; evidence vector |
| PROC-01 | czas procesu, opóźnienie i rework | signed/adverse time gaps; delay exposure; affected cases; hotspot; on-time rate |
| PROC-02 | kandydat / potwierdzone ograniczenie przepływu | constraint status; queue/throughput gaps; backlog; affected cases; migration |
| MGT-01 | gotowość informacji, luki, blokady i uzgodnienia | decision_information_status; unique counts; gaps; reconciliation; urgent_validation |

### 4.1. Zasada dziedziczenia

Pola z Core 10 zachowują źródłowy zakres, jednostkę, horyzont, znak, status i ograniczenia. PRI-01 nie oblicza ponownie mostów, luk, udziałów, wykorzystania, kosztu jednostkowego ani liczników MGT-01. Pole economic_impact_role określa, czy wartość jest główną podstawą wpływu, dowodem wspierającym, kontekstem nieaddytywnym albo nierozstrzygniętym nakładaniem.

## 5. Grupowanie wyników i ochrona przed podwójnym liczeniem

| Mechanizm | Katalog / pola | Ochrona |
| --- | --- | --- |
| relacja klastra | cluster_relation_type: same_metric; same_scope; same_economic_effect; supporting_evidence; possible_shared_mechanism; confirmed_shared_mechanism; other_documented_relation | confirmed_shared_mechanism wymaga jawnej podstawy źródłowej |
| rola wyniku w klastrze | finding_role_in_cluster: primary_problem; supporting_evidence; contextual_signal; validation_signal | nie każdy sygnał wspierający staje się osobnym problemem |
| rola w rozliczeniu wpływu | impact_accounting_role: primary_impact; supporting_evidence; non_additive_context; unresolved_overlap | tylko poprawnie wskazany primary_impact może wejść do podstawy ekonomicznej |
| tożsamość wpływu | impact_group_id; impact_overlap_flag; impact_overlap_basis; impact_included_in_priority_basis | ta sama złotówka, luka lub skutek nie zwiększa priorytetu wielokrotnie |

### 5.1. Reguła FIN-01 / FIN-02 / FIN-03

> **OCHRONA WPŁYWU Jeżeli trzy testy opisują ten sam zakres i mechanizm ekonomiczny, jedna wartość może być primary_impact, a pozostałe są supporting_evidence albo non_additive_context. PRI-01 nie sumuje trzech wartości.**

### 5.2. Dowody PORT / HR / CAP / PROC

Sygnały wyjaśniające mogą wzmacniać opis zakresu, trwałości lub możliwego mechanizmu. Nie są automatycznie kolejną kwotą wpływu. cross_test_support opisuje zgodność sygnałów, a supporting_tests przechowuje ich źródła. evidence_independence_status ma katalog: documented_independent; partly_shared; shared_source; unknown. independent_evidence_count jest dozwolone wyłącznie przy udokumentowanej niezależności.

### 5.3. Klaster i główna podstawa wpływu

| Pole | Reguła |
| --- | --- |
| finding_cluster_id | identyfikator grupy powiązanych wyników; nie oznacza wspólnej przyczyny |
| cluster_basis | jawna przesłanka utworzenia grupy |
| cluster_validation_status | status walidacji relacji pomiędzy wynikami |
| primary_impact_finding_id | wynik wskazany jako główna podstawa wpływu |
| primary_impact_basis | uzasadnienie zgodności zakresu, okresu i znaczenia ekonomicznego |
| cluster_priority_action | katalog problem_priority_action: review_now; review_next; plan_review; observe; not_assessable |
| cluster_validation_priority_action | katalog validation_priority_action: validate_now; validate_next; validate_when_needed; no_additional_validation; not_assessable |
| cluster_management_attention_route | katalog management_attention_route: review_now; validate_first; review_and_validate_in_parallel; review_next; plan; observe; insufficient_basis |
| cluster_priority_basis_summary | audytowalne uzasadnienie działań klastra, ochrony impact_group_id i braku sumowania nakładających się wpływów |
| cluster_priority_record | finding_cluster_id; cluster_priority_action; cluster_validation_priority_action; cluster_management_attention_route; cluster_priority_basis_summary; primary_impact_finding_id; impact_group_id |

## 6. Porównywalność i ranking warunkowy

PRI-01 nie tworzy rankingu wszystkich problemów organizacji. Ranking jest dopuszczalny tylko w obrębie priority_comparability_group, gdy rodzaj wpływu, jednostka, zakres i horyzont są zgodne albo istnieje zatwierdzona polityka normalizacji.

| Warunek | Wynik |
| --- | --- |
| zgodna miara, jednostka, zakres i horyzont | priority_comparability_status=comparable; ranking może być ordered lub tied |
| różne waluty bez źródłowego przeliczenia | incomparable |
| różne horyzonty bez uzgodnienia | incomparable |
| wpływ finansowy zestawiony z czasem, capacity lub liczbą decyzji | incomparable bez zatwierdzonej normalizacji |
| nieporównywalny current/reference | brak rankingu opartego na gap; możliwy priorytet walidacji |
| brak wystarczającej podstawy | insufficient_basis |

### 6.1. Pola rankingu

| Pole | Kontrakt |
| --- | --- |
| priority_comparability_group | jawna grupa elementów porównywalnych |
| priority_comparability_status | comparable; incomparable; insufficient_basis |
| priority_comparability_basis | źródłowe uzasadnienie porównywalności |
| priority_rank_within_group | pozycja wyłącznie w poprawnej grupie |
| priority_rank_basis | mierzalna wartość źródłowa; bez wag i standaryzacji lokalnej |
| priority_rank_tie_flag | true przy remisie; elementy mogą dzielić priority_rank_within_group |
| priority_order_status | ordered; tied; incomparable; insufficient_basis |
| priority_tie_group_id | wspólny identyfikator elementów remisowych; pozwala zapisać A > B = C > D |

## 7. Luka informacyjna i tryb bez ZOP-CONF-01

MGT-01 może dostarczyć samodzielny przedmiot priorytetu walidacji. Brak wyceny finansowej nie obniża znaczenia luki, jeśli blokuje miarę, test lub decyzję. Jedna luka zachowuje jeden information_gap_id niezależnie od liczby skutków.

| Dane MGT-01 | Wykorzystanie w PRI-01 |
| --- | --- |
| decision_information_status | określa gotowość informacji w konkretnym kontekście decyzji |
| critical_information_gap; information_gap_count | odróżnia krytyczność i liczbę unikalnych luk |
| blocked_metrics_count; blocked_tests_count; blocked_decisions_count | opisuje skutki bez mnożenia samej luki |
| reconciliation_failure_count; recurring_gap_flag | wspiera priorytet walidacji i opis trwałości |
| coverage; comparability; reconciliation; validation_required | tworzy jawną podstawę działania przed powstaniem CONF-01 |
| urgent_validation | może stanowić źródłową przesłankę validate_now |

### 7.1. Relacja z ZOP-CONF-01

ZOP-CONF-01 pozostaje DO OPRACOWANIA. Pola confidence_score, confidence_class i confidence_basis mogą do czasu jego powstania pozostawać null. PRI-01 nie projektuje ich wartości, klas ani progów i nie tworzy wskaźnika zastępczego. Niska pewność może zwiększyć pilność walidacji, ale nie zmniejsza automatycznie skali źródłowego wpływu. Wysoka pewność nie podnosi automatycznie priorytetu drobnego problemu.

## 8. Wyniki działania i reguły kwalifikacji

| Pole | Katalog zamknięty | Znaczenie |
| --- | --- | --- |
| problem_priority_action | review_now; review_next; plan_review; observe; not_assessable | kolejność uwagi zarządczej wobec samego problemu; kwalifikacja wymaga problem_priority_basis i problem_priority_basis_status |
| validation_priority_action | validate_now; validate_next; validate_when_needed; no_additional_validation; not_assessable | pilność uzupełnienia, uzgodnienia lub weryfikacji informacji; kwalifikacja wymaga validation_priority_basis |
| management_attention_route | review_now; validate_first; review_and_validate_in_parallel; review_next; plan; observe; insufficient_basis | syntetyczna trasa dalszego postępowania bez decyzji wykonawczej |

### 8.1. Deterministyczna kwalifikacja problem_priority_action

problem_priority_basis przechowuje audytowalne przesłanki kwalifikacji. problem_priority_basis_status ma katalog sufficient; insufficient. Pierwsze cztery działania wymagają sufficient; insufficient prowadzi do not_assessable. Katalog nie wprowadza progów kwotowych, procentowych ani wag.

| Pole | Katalog zamknięty | Znaczenie |
| --- | --- | --- |
| review_now | Niekorzystny albo incydentalny wynik źródłowy; jawna urgency_basis; informacja pozwala odpowiedzialnie zakwalifikować problem do natychmiastowej uwagi. | problem_priority_basis opisuje wynik, pilność i wystarczalność informacji; problem_priority_basis_status=sufficient. |
| review_next | Potwierdzony niekorzystny wynik wymaga uwagi w najbliższym cyklu zarządczym; brak podstawy natychmiastowej pilności. | problem_priority_basis wskazuje wynik, najbliższy cykl i brak urgency_basis dla review_now; status=sufficient. |
| plan_review | Wynik jest strukturalny, rozwojowy albo długookresowy; nie wymaga natychmiastowej reakcji; priority_horizon=planning_horizon. | problem_priority_basis wskazuje charakter i horyzont planistyczny; status=sufficient. |
| observe | Brak niekorzystnego sygnału, problem jest rozwiązany albo właściwe pozostaje monitorowanie. | problem_priority_basis wskazuje NO_ADVERSE_SIGNAL, resolved albo podstawę monitorowania; status=sufficient. |
| not_assessable | Brak odpowiedzialnej podstawy do ustalenia kolejności uwagi wobec samego problemu. | problem_priority_basis opisuje brak; problem_priority_basis_status=insufficient. |

### 8.2. Deterministyczna kwalifikacja validation_priority_action

validation_priority_basis przechowuje audytowalną podstawę potrzeby i pilności walidacji. Kwalifikacja nie zależy od progu liczbowego ani od przyszłego Confidence Score.

| Pole | Katalog zamknięty | Znaczenie |
| --- | --- | --- |
| validate_now | Krytyczna luka required; decision_blocked; urgent_validation=true; albo brak informacji blokuje bieżącą decyzję wymagającą rozstrzygnięcia. | validation_priority_basis wskazuje lukę, klasę required, blokadę decyzji lub urgent_validation. |
| validate_next | Walidacja jest wymagana dla bieżącego albo najbliższego cyklu decyzji, bez podstawy natychmiastowej walidacji. | validation_priority_basis wskazuje cykl decyzji, potrzebną informację i brak warunku validate_now. |
| validate_when_needed | Brak jest obecnie niekrytyczny; walidacja będzie potrzebna po przyszłym warunku albo na kolejnym etapie analizy. | validation_priority_basis wskazuje przyszły warunek lub etap. |
| no_additional_validation | Wszystkie wymagane warunki informacji i walidacji w danym kontekście są spełnione. | validation_priority_basis wskazuje spełnione wymagania kontekstu. |
| not_assessable | Nie można odpowiedzialnie ustalić potrzeby albo pilności walidacji. | validation_priority_basis opisuje brak podstawy oceny. |

### 8.3. Macierz zgodności obu priorytetów z trasą uwagi

Każda para problem_priority_action × validation_priority_action prowadzi do poniższej trasy. Jedyny rozgałęziony przypadek review_now + validate_now jest rozstrzygany przez jawny stan wymaganej informacji, a nie przez arbitralny próg.

| Trasa | Warunki | Skutek |
| --- | --- | --- |
| review_now | validate_now; required information wystarcza do odpowiedzialnej uwagi zarządczej | review_and_validate_in_parallel |
| review_now | validate_now; brak required information uniemożliwia odpowiedzialną kwalifikację decyzji | validate_first |
| review_now | validate_next | review_now |
| review_now | validate_when_needed | review_now |
| review_now | no_additional_validation | review_now |
| review_now | not_assessable | review_now |
| review_next | validate_now | validate_first |
| review_next | validate_next | review_next |
| review_next | validate_when_needed | review_next |
| review_next | no_additional_validation | review_next |
| review_next | not_assessable | review_next |
| plan_review | validate_now | validate_first |
| plan_review | validate_next | validate_first |
| plan_review | validate_when_needed | plan |
| plan_review | no_additional_validation | plan |
| plan_review | not_assessable | plan |
| observe | validate_now | validate_first |
| observe | validate_next | validate_first |
| observe | validate_when_needed | observe |
| observe | no_additional_validation | observe |
| observe | not_assessable | observe |
| not_assessable | validate_now | validate_first |
| not_assessable | validate_next | validate_first |
| not_assessable | validate_when_needed | insufficient_basis |
| not_assessable | no_additional_validation | insufficient_basis |
| not_assessable | not_assessable | insufficient_basis |

### 8.4. Deterministyczne reguły trasy uwagi

| Trasa | Warunki | Skutek |
| --- | --- | --- |
| validate_first | kluczowa decyzja zależy od required information; luka jest krytyczna; brak wystarczającej alternatywnej podstawy | walidacja przed dalszą kwalifikacją decyzji |
| review_and_validate_in_parallel | udokumentowana pilność lub incydent oraz równoczesna luka części podstawy | uwaga i walidacja równolegle; brak zgody na nieodwracalną decyzję bez wymaganych danych |
| review_now | jawna podstawa pilności oraz wystarczająca podstawa kwalifikacji problemu | natychmiastowa uwaga zarządcza, nie decyzja wykonawcza |
| review_next | brak potrzeby natychmiastowej uwagi, lecz problem powinien wejść do najbliższej kolejki | kolejny przegląd zarządczy |
| plan | problem strukturalny lub rozwojowy bez podstawy pilności | ujęcie w planowaniu |
| observe | brak niekorzystnego sygnału albo brak potrzeby działania poza monitoringiem | obserwacja |
| insufficient_basis | brak podstawy do odpowiedzialnej kwalifikacji trasy | uzupełnienie podstawy zgodnie z walidacją |

### 8.5. Pilność, horyzont i odwracalność

| Pole | Katalog / reguła |
| --- | --- |
| priority_horizon | immediate_context; near_term; planning_horizon; monitoring_horizon; not_assessable |
| urgency_basis | incydent, blokada ciągłości, termin zewnętrzny, okno decyzji lub inny udokumentowany warunek |
| decision_reversibility | reversible; partly_reversible; difficult_to_reverse; unknown; pole nie służy do scoringu |
| validation_effort_estimate | opcjonalna miara źródłowa z validation_effort_unit i validation_effort_basis; bez automatycznej wyceny |

### 8.6. Granica istotności biznesowej

> **OTWARTY KONTRAKT Globalna polityka istotności biznesowej nie jest definiowana w PRI-01 v1.0. source_threshold_value może być użyte wyłącznie razem z source_threshold_flag i source_threshold_basis. Progu z jednego testu nie przenosi się do innego bez jawnej podstawy.**

## 9. Kontrakt danych i pola FINDINGS

| Grupa | Pola techniczne |
| --- | --- |
| tożsamość | finding_id; source_test; finding_scope; finding_period; finding_status; finding_metric; finding_gap; finding_reference |
| kontekst | priority_context_id; priority_scope; priority_period; priority_decision_context; priority_evaluation_date; priority_basis_version |
| wpływ ekonomiczny | economic_impact_value; economic_impact_unit; economic_impact_period; economic_impact_scope; economic_impact_source; economic_impact_role |
| wpływ operacyjny | operational_impact_metric; operational_impact_value; operational_impact_unit; operational_impact_scope; operational_impact_period |
| zakres | affected_scope_type; affected_scope_count; affected_units; affected_portfolio_items; affected_processes; affected_resources |
| czas i pilność | persistence_status; persistence_periods; recurrence_count; recurring_signal_flag; trend_direction; trend_basis; urgency_flag; urgency_basis; required_response_window; required_response_window_basis |
| zależności | downstream_tests_affected; blocked_metrics_count; blocked_tests_count; blocked_decisions_count; dependency_impact_basis |
| incydent i one-off | incident_flag; incident_basis; oneoff_flag; oneoff_basis |
| luka informacyjna | information_gap_id; critical_information_gap; missing_information_element; affected_test; blocked_metric; affected_decision; gap_consequence |
| klaster | finding_cluster_id; cluster_relation_type; cluster_basis; cluster_validation_status; finding_role_in_cluster; primary_impact_finding_id; primary_impact_basis |
| ochrona wpływu | impact_group_id; impact_accounting_role; impact_overlap_flag; impact_overlap_basis; impact_included_in_priority_basis |
| porównywalność | priority_comparability_group; priority_comparability_status; priority_comparability_basis; priority_rank_within_group; priority_rank_basis; priority_rank_tie_flag; priority_tie_group_id; priority_order_status |
| działanie | problem_priority_action; problem_priority_basis; problem_priority_basis_status; validation_priority_action; validation_priority_basis; management_attention_route; priority_horizon; priority_basis_summary |
| stabilność i wsparcie | priority_stability_dimension; priority_action_previous; priority_action_current; priority_stability_status; priority_stability_periods; priority_stability_basis; priority_change_reason; cross_test_support; supporting_tests; cross_test_support_basis; evidence_independence_status; independent_evidence_count |
| walidacja i następne testy | validation_required; validation_notes; next_tests; next_test_priority_order; next_test_priority_basis |
| CONF – rezerwa | confidence_score; confidence_class; confidence_basis; do czasu ZOP-CONF-01 wartości null |
| priorytet klastra | cluster_priority_record: finding_cluster_id; cluster_priority_action; cluster_validation_priority_action; cluster_management_attention_route; cluster_priority_basis_summary; primary_impact_finding_id; impact_group_id |

### 9.1. Pola bazowe wspólnego FINDINGS

PRI-01 zachowuje pola wspólne Core 10: test_id, scope, period, status, finding, metric_value, reference_value, gap, impact_low, impact_high, confidence_score, confidence_class, next_tests oraz validation_required. Rozszerzenia PRI-01 nie zmieniają ich semantyki.

### 9.2. Semantyka null i blokady

Brak danych nie jest false ani zero. Pole nieobliczalne lub nieporównywalne pozostaje null wraz z właściwym statusem i validation_notes. Dla remisu elementy zachowują wspólne priority_rank_within_group oraz priority_tie_group_id; dla incomparable i insufficient_basis pozycja pozostaje null. independent_evidence_count pozostaje null, jeśli niezależność nie została udokumentowana.

## 10. Przetwarzanie rekordu PRI-01

| Etap | Działanie | Wymagany rezultat |
| --- | --- | --- |
| 1 | Przyjmij finding lub information_gap | zachowaj identyfikator, źródło, zakres, okres, status i wersję |
| 2 | Ustal priority_context | bez jawnego kontekstu nie wymuszaj kwalifikacji |
| 3 | Zbuduj profil | przenieś źródłowe miary ekonomiczne i operacyjne bez normalizacji |
| 4 | Sprawdź nakładanie wpływów | nadaj impact_group_id i impact_accounting_role |
| 5 | Ustal relacje klastra | oddziel primary_problem, supporting_evidence, contextual_signal i validation_signal |
| 6 | Oceń porównywalność | utwórz grupę tylko przy zgodnej jednostce, zakresie i horyzoncie |
| 7 | Ustal priorytet problemu | zapisz problem_priority_basis i problem_priority_basis_status; zastosuj reguły katalogu |
| 8 | Ustal priorytet walidacji | zapisz validation_priority_basis; zastosuj reguły required gap, decyzji i czasu |
| 9 | Wyznacz trasę uwagi | zastosuj macierz problem_priority_action × validation_priority_action |
| 10 | Zapisz uzasadnienie | priority_basis_summary wskazuje źródłowe przesłanki i ograniczenia |
| 11 | Przekaż next_tests | nadaj kolejność lokalną bez budowania pełnej orkiestracji |
| 12 | Zapisz FINDINGS i ślad walidacji | utrzymaj statusy, wersję podstawy i możliwość audytu |

## 11. Reguły przypadków szczególnych

| Przypadek | Reguła |
| --- | --- |
| NO_ADVERSE_SIGNAL | problem_priority_action może być observe; brak sztucznego problemu |
| TEST_PARTIAL | nie oznacza niskiego priorytetu; routing zależy od zakresu braków i możliwości decyzji |
| TEST_BLOCKED | może generować validate_now, jeśli luka blokuje ważną decyzję |
| one-off | zachowaj oneoff_flag i oneoff_basis; nie oznaczaj automatycznie problemu strukturalnego |
| incident | może być pilny mimo krótkiej trwałości, jeśli istnieje urgency_basis |
| persistent | wspiera kolejność uwagi, ale bez wagi i bez automatycznego review_now |
| różne jednostki | PLN, godziny, dni, capacity, liczba decyzji i procent rework pozostają w osobnych grupach |
| różne horyzonty | 1M i 12M nie są automatycznie porównywane |
| różne waluty | brak rankingu bez źródłowego przeliczenia; PRI-01 nie pobiera kursów |
| zmiana scope | matched impact i full-scope / structural impact pozostają rozdzielone |
| not_comparable | brak rankingu opartego na gap; możliwy priorytet walidacji |
| duplikat | ten sam finding w dwóch raportach pozostaje jednym problemem |

## 12. Dane dla przyszłej orkiestracji next_tests

| Pole | Rola |
| --- | --- |
| finding_id; finding_cluster_id; impact_group_id | tożsamość wyniku, grupy i wpływu |
| problem_priority_action; validation_priority_action; management_attention_route | trzy wyniki kwalifikacji |
| priority_comparability_group; priority_rank_within_group | pozycja tylko w zakresie porównywalnym |
| priority_horizon; priority_stability_status | horyzont i stabilność uwagi |
| next_tests; next_test_priority_order; next_test_priority_basis | lokalna kolejność i jawne uzasadnienie |
| validation_required | sygnał potrzeby sprawdzenia |

PRI-01 nie projektuje algorytmu uruchamiania testów, pełnego grafu zależności ani silnika reguł decyzyjnych. Przekazuje kontrakt wejściowy do tych mechanizmów.

## 13. Komunikat zarządczy

> **WZORZEC [TRASA UWAGI] PRIORYTET WYNIKU. Wynik [finding] dotyczy [scope] i ma status [problem_priority_action]. Podstawą kolejności są: [wpływ ekonomiczny/operacyjny], [trwałość], [pilność], [zakres] i [zależności]. Jakość informacji powoduje [validation_priority_action]. Powiązane sygnały: [supporting_tests]. Wpływy [są / nie są] addytywne. Dalsze sprawdzenie: [next_tests]. PRI-01 ustala kolejność uwagi i walidacji, nie podejmuje decyzji wykonawczej.**

Komunikat nie używa automatycznych poleceń: zwolnij, zatrudnij, kup, zamknij, podnieś cenę, zmniejsz capacity, zwiększ capacity ani zmień proces. Nie nazywa luki oszczędnością, stratą możliwą do odzyskania ani potwierdzoną przyczyną bez źródła.

## 14. Scenariusze testowe PRI01-T01–T40

| ID | Warunek | Oczekiwany rezultat |
| --- | --- | --- |
| PRI01-T01 | Brak niekorzystnego sygnału | NO_ADVERSE_SIGNAL; observe; brak sztucznego problemu. |
| PRI01-T02 | Duża kwotowa luka, pełna walidacja i jawna pilność | Źródło potwierdza termin reakcji; review_now. |
| PRI01-T03 | Duża potencjalna luka, słaba podstawa informacji | validate_first; brak automatycznego obniżenia znaczenia. |
| PRI01-T04 | Niewyceniona luka informacyjna blokuje trzy decyzje | validate_now bez tworzenia kwoty wpływu. |
| PRI01-T05 | Jednorazowy incydent z terminem zewnętrznym | Pilność może być wysoka mimo persistence_status=incident. |
| PRI01-T06 | Trwały niekorzystny sygnał bez podstawy natychmiastowej reakcji | review_next albo plan zgodnie z kontekstem; bez progu. |
| PRI01-T07 | FIN-01, FIN-02 i FIN-03 opisują ten sam efekt ekonomiczny | Jeden impact_group_id; brak potrójnego liczenia. |
| PRI01-T08 | FIN-02 i CAP-01 dotyczą odrębnych skutków | Brak wymuszonego grupowania. |
| PRI01-T09 | Dwa wyniki powiązane czasowo bez dowodu wspólnej przyczyny | possible_shared_mechanism; bez causal claim. |
| PRI01-T10 | Dowód wspierający z HR-01 | Wspiera FIN-03, ale nie dodaje drugiej kwoty. |
| PRI01-T11 | Niska przyszła confidence przy wysokiej konsekwencji | validate_first lub parallel; nie automatycznie low priority. |
| PRI01-T12 | Wysoka confidence przy drobnym lokalnym problemie | Brak automatycznego review_now. |
| PRI01-T13 | MGT-01 decision_blocked przez required information gap | validation_priority_action=validate_now. |
| PRI01-T14 | Brak pola optional w MGT-01 | Nie podnosi priorytetu walidacji automatycznie. |
| PRI01-T15 | Dwa finansowe wyniki w tej samej walucie, scope i horyzoncie | Możliwy ranking w jednej priority_comparability_group. |
| PRI01-T16 | Finansowe wyniki w różnych walutach | incomparable bez źródłowego przeliczenia. |
| PRI01-T17 | Ten sam wskaźnik 1M i 12M | Brak bezpośredniego rankingu bez wspólnego horyzontu. |
| PRI01-T18 | Wpływ finansowy i czas procesu | Brak arbitralnego wspólnego rankingu. |

### 14.1. Scenariusze PRI01-T19–T35

| ID | Warunek | Oczekiwany rezultat |
| --- | --- | --- |
| PRI01-T19 | Incydent a strukturalny problem bez pilności | Odrębne profile; brak automatycznej przewagi. |
| PRI01-T20 | One-off kosztowy | Nie tworzy automatycznie priorytetu strukturalnego. |
| PRI01-T21 | Trzy testy korzystają z tej samej wartości źródłowej | cross_test_support możliwe; evidence_independence_status=shared_source. |
| PRI01-T22 | Dwa niezależne źródła potwierdzają problem | independent_evidence_count tylko przy udokumentowanej niezależności. |
| PRI01-T23 | Brak globalnej polityki materiality | Brak HIGH/MEDIUM/LOW i wymyślonego progu. |
| PRI01-T24 | Jawny termin ustawowy, kontraktowy lub operacyjny | urgency_basis istnieje; możliwe review_now. |
| PRI01-T25 | Brak podstawy pilności | Zakaz review_now tylko z powodu dużej liczby. |
| PRI01-T26 | Pilny problem i krytyczna luka informacji | review_and_validate_in_parallel przy odpowiedniej podstawie. |
| PRI01-T27 | Klaster: jeden primary_problem i trzy supporting_evidence | Tylko primary impact zwiększa podstawę ekonomiczną. |
| PRI01-T28 | Jedna luka blokuje dwie miary, dwa testy i jedną decyzję | information_gap_count=1; bez mnożenia luki. |
| PRI01-T29 | Duplikat tego samego findingu w dwóch raportach | Nie tworzy dwóch problemów. |
| PRI01-T30 | Sprzeczne kierunki FIN i PORT | insufficient_basis lub validation_required; bez arbitralnego rozstrzygnięcia. |
| PRI01-T31 | Priorytet stabilny przez kilka okresów | priority_stability_status=stable. |
| PRI01-T32 | Priorytet zmienia się po usunięciu luki danych | priority_change_reason jawne; zmiana nie jest błędem. |
| PRI01-T33 | Matched impact i structural change | Nie sumuje bez podstawy; oddzielne grupy wpływu. |
| PRI01-T34 | TEST_PARTIAL, current metric wiarygodna i decyzja częściowo możliwa | Nie blokuje wszystkiego; routing zgodny z zakresem braków. |
| PRI01-T35 | Brak CONF-01 | PRI działa na statusach źródłowych i MGT; brak zastępczego confidence score. |

PASS scenariusza wymaga zgodności pól źródłowych, profilu, ochrony wpływu, porównywalności, obu priorytetów, trasy uwagi, FINDINGS oraz validation_required. Poprawny komunikat bez poprawnego kontraktu danych nie wystarcza.

### 14.2. Regresje PRI01-T36–T40

| ID | Warunek | Oczekiwany rezultat |
| --- | --- | --- |
| PRI01-T36 | REVIEW_NEXT VS PLAN_REVIEW: dwa niepilne niekorzystne wyniki; jeden wymaga najbliższego przeglądu, drugi ma horyzont planistyczny. | Pierwszy=review_next; drugi=plan_review; bez progu liczbowego. |
| PRI01-T37 | VALIDATE_NEXT VS VALIDATE_WHEN_NEEDED: jedna informacja jest wymagana w najbliższym cyklu, druga dopiero po przyszłym warunku. | validate_next vs validate_when_needed. |
| PRI01-T38 | KLASTER MA WŁASNY REKORD PRIORYTETU: kilka findings tworzy jeden klaster. | cluster_priority_record zawiera działania i cluster_priority_basis_summary; brak sumowania impactów. |
| PRI01-T39 | ZMIANA PRIORYTETU W CZASIE: review_next → review_now w tym samym kontekście. | dimension=problem_priority; status=increasing_attention. not_assessable → review_now wymaga opisu zmiany podstawy. |
| PRI01-T40 | REMIS CZĘŚCIOWY: cztery porównywalne wyniki A > B = C > D. | Wspólna pozycja i priority_tie_group_id dla B/C zachowują dokładny porządek. |

Po korekcie obowiązuje komplet PRI01-T01–T40. Wszystkie scenariusze = PASS.

## 15. Walidacja PRI01-VAL-01–78

| ID | Kontrola | Wynik |
| --- | --- | --- |
| PRI01-VAL-01 | finding_id istnieje i jest jednoznaczny | PASS |
| PRI01-VAL-02 | source_test należy do Core 10 | PASS |
| PRI01-VAL-03 | finding_scope jest jawny | PASS |
| PRI01-VAL-04 | finding_period jest jawny | PASS |
| PRI01-VAL-05 | finding_status zachowuje status źródłowy | PASS |
| PRI01-VAL-06 | priority_context_id istnieje | PASS |
| PRI01-VAL-07 | priority_scope jest jawny | PASS |
| PRI01-VAL-08 | priority_period jest jawny | PASS |
| PRI01-VAL-09 | priority_decision_context jest jawny albo wynik not_assessable | PASS |
| PRI01-VAL-10 | priority_basis_version istnieje | PASS |
| PRI01-VAL-11 | problem_priority_action należy do katalogu | PASS |
| PRI01-VAL-12 | validation_priority_action należy do katalogu | PASS |
| PRI01-VAL-13 | management_attention_route należy do katalogu | PASS |
| PRI01-VAL-14 | economic_impact ma źródło | PASS |
| PRI01-VAL-15 | economic_impact_unit jest jawna | PASS |
| PRI01-VAL-16 | economic_impact_period jest jawny | PASS |
| PRI01-VAL-17 | economic_impact_scope jest jawny | PASS |
| PRI01-VAL-18 | economic_impact_role jest jawna | PASS |
| PRI01-VAL-19 | operational_impact_unit pozostaje źródłowa | PASS |
| PRI01-VAL-20 | brak arbitralnej normalizacji jednostek | PASS |
| PRI01-VAL-21 | affected scope jest jawny | PASS |
| PRI01-VAL-22 | persistence_status należy do katalogu | PASS |
| PRI01-VAL-23 | recurrence_count nie dowodzi przyczyny | PASS |
| PRI01-VAL-24 | trend opiera się na porównywalnych okresach | PASS |
| PRI01-VAL-25 | urgency_flag ma urgency_basis | PASS |
| PRI01-VAL-26 | required_response_window ma podstawę | PASS |
| PRI01-VAL-27 | incident_flag ma incident_basis | PASS |
| PRI01-VAL-28 | oneoff_flag zachowuje oneoff_basis | PASS |
| PRI01-VAL-29 | liczniki blokad są deterministyczne | PASS |
| PRI01-VAL-30 | information_gap_count liczy unikalne luki | PASS |
| PRI01-VAL-31 | MGT inputs zachowują semantykę | PASS |
| PRI01-VAL-32 | finding_cluster_id ma cluster_basis | PASS |

### 15.1. Kontrole PRI01-VAL-33–63

| ID | Kontrola | Wynik |
| --- | --- | --- |
| PRI01-VAL-33 | cluster_relation_type należy do katalogu | PASS |
| PRI01-VAL-34 | finding_role_in_cluster należy do katalogu | PASS |
| PRI01-VAL-35 | primary impact ma primary_impact_basis | PASS |
| PRI01-VAL-36 | impact_group_id chroni nakładanie | PASS |
| PRI01-VAL-37 | impact_accounting_role należy do katalogu | PASS |
| PRI01-VAL-38 | impact_overlap jest jawny | PASS |
| PRI01-VAL-39 | supporting evidence nie zwiększa kwoty | PASS |
| PRI01-VAL-40 | porównywalność jednostki jest sprawdzona | PASS |
| PRI01-VAL-41 | porównywalność horyzontu jest sprawdzona | PASS |
| PRI01-VAL-42 | porównywalność scope jest sprawdzona | PASS |
| PRI01-VAL-43 | różne waluty bez przeliczenia są incomparable | PASS |
| PRI01-VAL-44 | ranking istnieje tylko w grupie porównywalnej | PASS |
| PRI01-VAL-45 | priority_rank_basis jest jawny | PASS |
| PRI01-VAL-46 | remis pozostaje remisem | PASS |
| PRI01-VAL-47 | brak podstawy daje insufficient_basis | PASS |
| PRI01-VAL-48 | materiality ma zewnętrzną podstawę albo pozostaje otwarta | PASS |
| PRI01-VAL-49 | source threshold ma źródło | PASS |
| PRI01-VAL-50 | evidence independence jest udokumentowana albo unknown | PASS |
| PRI01-VAL-51 | cross_test_support nie jest głosowaniem | PASS |
| PRI01-VAL-52 | next_tests są dziedziczone | PASS |
| PRI01-VAL-53 | next_test_priority_order ma podstawę | PASS |
| PRI01-VAL-54 | priority_horizon ma podstawę | PASS |
| PRI01-VAL-55 | priority_stability_status należy do katalogu | PASS |
| PRI01-VAL-56 | brak Priority Score | PASS |
| PRI01-VAL-57 | brak wag i średnich ważonych | PASS |
| PRI01-VAL-58 | brak arbitralnych progów | PASS |
| PRI01-VAL-59 | brak wnioskowania przyczynowego | PASS |
| PRI01-VAL-60 | brak automatycznych rekomendacji wykonawczych | PASS |
| PRI01-VAL-61 | payload do CONF zachowuje pola null | PASS |
| PRI01-VAL-62 | payload do orkiestracji jest kompletny | PASS |
| PRI01-VAL-63 | scenariusze PRI01-T01–T35 są wykonywalne | PASS |

Statusy kontroli: PASS / WARNING / CRITICAL. WARNING wymaga validation_notes i może ograniczyć ranking lub trasę. CRITICAL blokuje wynik, którego nie można odpowiedzialnie zakwalifikować.

### 15.2. Kontrole PRI01-VAL-64–78

| ID | Kontrola | Wynik |
| --- | --- | --- |
| PRI01-VAL-64 | problem_priority_basis istnieje dla każdej kwalifikacji | PASS |
| PRI01-VAL-65 | problem_priority_basis_status należy do katalogu sufficient / insufficient | PASS |
| PRI01-VAL-66 | review_now spełnia warunek wyniku, urgency_basis i wystarczalności informacji | PASS |
| PRI01-VAL-67 | review_next i plan_review są rozdzielone przez cykl oraz priority_horizon | PASS |
| PRI01-VAL-68 | validation_priority_basis istnieje dla każdej kwalifikacji | PASS |
| PRI01-VAL-69 | validate_now, validate_next i validate_when_needed mają rozłączne podstawy czasowe | PASS |
| PRI01-VAL-70 | macierz obejmuje wszystkie kombinacje obu katalogów | PASS |
| PRI01-VAL-71 | review_now + validate_now rozstrzyga required information | PASS |
| PRI01-VAL-72 | cluster_priority_record zawiera wszystkie wymagane pola | PASS |
| PRI01-VAL-73 | działania klastra używają katalogów głównych | PASS |
| PRI01-VAL-74 | stabilność porównuje ten sam wymiar i kontekst | PASS |
| PRI01-VAL-75 | not_assessable nie uczestniczy w porządku stabilności | PASS |
| PRI01-VAL-76 | management_attention_route nie ma liniowego porządku | PASS |
| PRI01-VAL-77 | priority_tie_group_id zachowuje remis częściowy | PASS |
| PRI01-VAL-78 | scenariusze PRI01-T01–T40 są wykonywalne | PASS |

## 16. Kryteria odbioru implementacji PRI01-ACC-01–95

| ID | Kryterium odbioru | Wynik |
| --- | --- | --- |
| PRI01-ACC-01 | implementacja przyjmuje finding Core 10 bez zmiany semantyki | PASS |
| PRI01-ACC-02 | implementacja przyjmuje lukę MGT-01 jako osobny obiekt | PASS |
| PRI01-ACC-03 | utrzymuje priority_context_id | PASS |
| PRI01-ACC-04 | wersjonuje priority_basis_version | PASS |
| PRI01-ACC-05 | rozdziela problem priority i validation priority | PASS |
| PRI01-ACC-06 | rozdziela priority i confidence | PASS |
| PRI01-ACC-07 | rozdziela importance i stability | PASS |
| PRI01-ACC-08 | nie tworzy Priority Score | PASS |
| PRI01-ACC-09 | nie tworzy wag | PASS |
| PRI01-ACC-10 | nie tworzy arbitralnych progów | PASS |
| PRI01-ACC-11 | utrzymuje profil ekonomiczny | PASS |
| PRI01-ACC-12 | utrzymuje profil operacyjny | PASS |
| PRI01-ACC-13 | zachowuje jednostkę wpływu | PASS |
| PRI01-ACC-14 | zachowuje horyzont wpływu | PASS |
| PRI01-ACC-15 | zachowuje zakres wpływu | PASS |
| PRI01-ACC-16 | utrzymuje affected scope | PASS |
| PRI01-ACC-17 | utrzymuje persistence | PASS |
| PRI01-ACC-18 | utrzymuje trend | PASS |
| PRI01-ACC-19 | utrzymuje urgency i jej podstawę | PASS |
| PRI01-ACC-20 | utrzymuje incident i one-off | PASS |
| PRI01-ACC-21 | utrzymuje luki informacyjne | PASS |
| PRI01-ACC-22 | korzysta z liczników MGT-01 bez ponownego liczenia | PASS |
| PRI01-ACC-23 | tworzy klaster tylko z podstawą | PASS |
| PRI01-ACC-24 | odróżnia role wyników w klastrze | PASS |
| PRI01-ACC-25 | chroni primary impact | PASS |
| PRI01-ACC-26 | nadaje impact_group_id | PASS |
| PRI01-ACC-27 | wykrywa overlap | PASS |
| PRI01-ACC-28 | nie sumuje supporting evidence | PASS |
| PRI01-ACC-29 | nie sumuje FIN-01/02/03 dla tego samego efektu | PASS |
| PRI01-ACC-30 | zapisuje evidence independence | PASS |

### 16.1. PRI01-ACC-31–60

| ID | Kryterium odbioru | Wynik |
| --- | --- | --- |
| PRI01-ACC-31 | nie liczy wspólnych źródeł jako niezależnych dowodów | PASS |
| PRI01-ACC-32 | tworzy grupy porównywalności | PASS |
| PRI01-ACC-33 | nie porównuje różnych walut bez źródła | PASS |
| PRI01-ACC-34 | nie porównuje różnych horyzontów bez uzgodnienia | PASS |
| PRI01-ACC-35 | nie normalizuje PLN, czasu, capacity i liczników | PASS |
| PRI01-ACC-36 | pozwala na remis | PASS |
| PRI01-ACC-37 | pozwala na incomparable | PASS |
| PRI01-ACC-38 | pozwala na insufficient_basis | PASS |
| PRI01-ACC-39 | wyznacza problem_priority_action z katalogu | PASS |
| PRI01-ACC-40 | wyznacza validation_priority_action z katalogu | PASS |
| PRI01-ACC-41 | wyznacza management_attention_route z katalogu | PASS |
| PRI01-ACC-42 | validate_first spełnia warunki required gap | PASS |
| PRI01-ACC-43 | parallel zachowuje ograniczenie decyzji nieodwracalnej | PASS |
| PRI01-ACC-44 | review_now wymaga urgency_basis | PASS |
| PRI01-ACC-45 | observe obsługuje NO_ADVERSE_SIGNAL | PASS |
| PRI01-ACC-46 | TEST_PARTIAL nie obniża automatycznie priorytetu | PASS |
| PRI01-ACC-47 | TEST_BLOCKED może podnieść walidację | PASS |
| PRI01-ACC-48 | działa bez ZOP-CONF-01 | PASS |
| PRI01-ACC-49 | pozostawia confidence fields null bez zastępczego score | PASS |
| PRI01-ACC-50 | utrzymuje priority horizon | PASS |
| PRI01-ACC-51 | utrzymuje reversibility bez scoringu | PASS |
| PRI01-ACC-52 | utrzymuje validation effort bez scoringu | PASS |
| PRI01-ACC-53 | przekazuje next_tests bez pełnej orkiestracji | PASS |
| PRI01-ACC-54 | generuje audytowalny priority_basis_summary | PASS |
| PRI01-ACC-55 | nie generuje automatycznych decyzji wykonawczych | PASS |
| PRI01-ACC-56 | scenariusz PRI01-T01 zwraca oczekiwany rezultat | PASS |
| PRI01-ACC-57 | scenariusz PRI01-T02 zwraca oczekiwany rezultat | PASS |
| PRI01-ACC-58 | scenariusz PRI01-T03 zwraca oczekiwany rezultat | PASS |
| PRI01-ACC-59 | scenariusz PRI01-T04 zwraca oczekiwany rezultat | PASS |
| PRI01-ACC-60 | scenariusz PRI01-T05 zwraca oczekiwany rezultat | PASS |

### 16.2. PRI01-ACC-61–95

| ID | Kryterium odbioru | Wynik |
| --- | --- | --- |
| PRI01-ACC-61 | scenariusz PRI01-T06 zwraca oczekiwany rezultat | PASS |
| PRI01-ACC-62 | scenariusz PRI01-T07 zwraca oczekiwany rezultat | PASS |
| PRI01-ACC-63 | scenariusz PRI01-T08 zwraca oczekiwany rezultat | PASS |
| PRI01-ACC-64 | scenariusz PRI01-T09 zwraca oczekiwany rezultat | PASS |
| PRI01-ACC-65 | scenariusz PRI01-T10 zwraca oczekiwany rezultat | PASS |
| PRI01-ACC-66 | scenariusz PRI01-T11 zwraca oczekiwany rezultat | PASS |
| PRI01-ACC-67 | scenariusz PRI01-T12 zwraca oczekiwany rezultat | PASS |
| PRI01-ACC-68 | scenariusz PRI01-T13 zwraca oczekiwany rezultat | PASS |
| PRI01-ACC-69 | scenariusz PRI01-T14 zwraca oczekiwany rezultat | PASS |
| PRI01-ACC-70 | scenariusz PRI01-T15 zwraca oczekiwany rezultat | PASS |
| PRI01-ACC-71 | scenariusz PRI01-T16 zwraca oczekiwany rezultat | PASS |
| PRI01-ACC-72 | scenariusz PRI01-T17 zwraca oczekiwany rezultat | PASS |
| PRI01-ACC-73 | scenariusz PRI01-T18 zwraca oczekiwany rezultat | PASS |
| PRI01-ACC-74 | scenariusz PRI01-T19 zwraca oczekiwany rezultat | PASS |
| PRI01-ACC-75 | scenariusz PRI01-T20 zwraca oczekiwany rezultat | PASS |
| PRI01-ACC-76 | scenariusz PRI01-T21 zwraca oczekiwany rezultat | PASS |
| PRI01-ACC-77 | scenariusz PRI01-T22 zwraca oczekiwany rezultat | PASS |
| PRI01-ACC-78 | scenariusz PRI01-T23 zwraca oczekiwany rezultat | PASS |
| PRI01-ACC-79 | scenariusz PRI01-T24 zwraca oczekiwany rezultat | PASS |
| PRI01-ACC-80 | scenariusz PRI01-T25 zwraca oczekiwany rezultat | PASS |
| PRI01-ACC-81 | scenariusz PRI01-T26 zwraca oczekiwany rezultat | PASS |
| PRI01-ACC-82 | scenariusz PRI01-T27 zwraca oczekiwany rezultat | PASS |
| PRI01-ACC-83 | scenariusz PRI01-T28 zwraca oczekiwany rezultat | PASS |
| PRI01-ACC-84 | scenariusz PRI01-T29 zwraca oczekiwany rezultat | PASS |
| PRI01-ACC-85 | scenariusz PRI01-T30 zwraca oczekiwany rezultat | PASS |
| PRI01-ACC-86 | scenariusz PRI01-T31 zwraca oczekiwany rezultat | PASS |
| PRI01-ACC-87 | scenariusz PRI01-T32 zwraca oczekiwany rezultat | PASS |
| PRI01-ACC-88 | scenariusz PRI01-T33 zwraca oczekiwany rezultat | PASS |
| PRI01-ACC-89 | scenariusz PRI01-T34 zwraca oczekiwany rezultat | PASS |
| PRI01-ACC-90 | scenariusz PRI01-T35 zwraca oczekiwany rezultat | PASS |
| PRI01-ACC-91 | scenariusz PRI01-T36 zwraca oczekiwany rezultat | PASS |
| PRI01-ACC-92 | scenariusz PRI01-T37 zwraca oczekiwany rezultat | PASS |
| PRI01-ACC-93 | scenariusz PRI01-T38 zwraca oczekiwany rezultat | PASS |
| PRI01-ACC-94 | scenariusz PRI01-T39 zwraca oczekiwany rezultat | PASS |
| PRI01-ACC-95 | scenariusz PRI01-T40 zwraca oczekiwany rezultat | PASS |

## 17. Warunki zamknięcia PRI01-DOD-01–95

| ID | Warunek zamknięcia | Wynik |
| --- | --- | --- |
| PRI01-DOD-01 | cel PRI-01 jest jednoznaczny | PASS |
| PRI01-DOD-02 | granica PRI/CONF jest zamknięta | PASS |
| PRI01-DOD-03 | granica PRI/orkiestracja jest zamknięta | PASS |
| PRI01-DOD-04 | brak Priority Score | PASS |
| PRI01-DOD-05 | profil priorytetu jest kompletny | PASS |
| PRI01-DOD-06 | skala ekonomiczna ma kontrakt | PASS |
| PRI01-DOD-07 | skala operacyjna ma kontrakt | PASS |
| PRI01-DOD-08 | scope jest jawny | PASS |
| PRI01-DOD-09 | persistence ma katalog | PASS |
| PRI01-DOD-10 | trend ma katalog | PASS |
| PRI01-DOD-11 | urgency ma podstawę | PASS |
| PRI01-DOD-12 | dependencies są jawne | PASS |
| PRI01-DOD-13 | incident ma podstawę | PASS |
| PRI01-DOD-14 | information gap jest osobnym obiektem | PASS |
| PRI01-DOD-15 | clustering ma reguły | PASS |
| PRI01-DOD-16 | finding roles mają katalog | PASS |
| PRI01-DOD-17 | double count protection działa | PASS |
| PRI01-DOD-18 | comparability groups mają kontrakt | PASS |
| PRI01-DOD-19 | ranking jest warunkowy | PASS |
| PRI01-DOD-20 | ties są dozwolone | PASS |
| PRI01-DOD-21 | problem priority ma katalog | PASS |
| PRI01-DOD-22 | validation priority ma katalog | PASS |
| PRI01-DOD-23 | management route ma katalog | PASS |
| PRI01-DOD-24 | materiality pozostaje otwartym kontraktem | PASS |
| PRI01-DOD-25 | source thresholds są źródłowe | PASS |
| PRI01-DOD-26 | stability ma katalog | PASS |
| PRI01-DOD-27 | cross-test support nie jest głosowaniem | PASS |
| PRI01-DOD-28 | evidence independence jest jawna | PASS |
| PRI01-DOD-29 | relacja z MGT-01 jest zamknięta | PASS |

### 17.1. PRI01-DOD-30–58

| ID | Warunek zamknięcia | Wynik |
| --- | --- | --- |
| PRI01-DOD-30 | relacja z CONF-01 jest zamknięta | PASS |
| PRI01-DOD-31 | tryb przed CONF-01 działa | PASS |
| PRI01-DOD-32 | priority horizon ma kontrakt | PASS |
| PRI01-DOD-33 | reversibility nie jest scoringiem | PASS |
| PRI01-DOD-34 | validation effort nie jest scoringiem | PASS |
| PRI01-DOD-35 | next_tests nie stają się orkiestracją | PASS |
| PRI01-DOD-36 | output do orkiestracji jest kompletny | PASS |
| PRI01-DOD-37 | komunikat zarządczy ma wzorzec | PASS |
| PRI01-DOD-38 | FINDINGS ma pola bazowe | PASS |
| PRI01-DOD-39 | FINDINGS ma rozszerzenia PRI | PASS |
| PRI01-DOD-40 | VAL jest kompletne | PASS |
| PRI01-DOD-41 | scenariusze są kompletne | PASS |
| PRI01-DOD-42 | ACC jest kompletne | PASS |
| PRI01-DOD-43 | Core 10 pozostaje bez zmian | PASS |
| PRI01-DOD-44 | kontekst priorytetu jest wersjonowany | PASS |
| PRI01-DOD-45 | economic impact zachowuje jednostkę | PASS |
| PRI01-DOD-46 | operational impact zachowuje jednostkę | PASS |
| PRI01-DOD-47 | affected scope zachowuje listy źródłowe | PASS |
| PRI01-DOD-48 | recurrence nie dowodzi przyczyny | PASS |
| PRI01-DOD-49 | trend nie używa nieporównywalnych okresów | PASS |
| PRI01-DOD-50 | urgency nie tworzy terminów | PASS |
| PRI01-DOD-51 | one-off nie staje się automatycznie structural | PASS |
| PRI01-DOD-52 | MGT gap nie wymaga kwoty finansowej | PASS |
| PRI01-DOD-53 | jedna luka nie jest mnożona przez skutki | PASS |
| PRI01-DOD-54 | cluster nie oznacza przyczyny | PASS |
| PRI01-DOD-55 | primary impact ma uzasadnienie | PASS |
| PRI01-DOD-56 | supporting evidence nie jest drugim impactem | PASS |
| PRI01-DOD-57 | impact overlap jest jawny | PASS |
| PRI01-DOD-58 | FIN-01/02/03 nie są sumowane potrójnie | PASS |

### 17.2. PRI01-DOD-59–85

| ID | Warunek zamknięcia | Wynik |
| --- | --- | --- |
| PRI01-DOD-59 | PORT/HR/CAP/PROC pozostają dowodami, gdy właściwe | PASS |
| PRI01-DOD-60 | różne waluty pozostają odrębne | PASS |
| PRI01-DOD-61 | różne horyzonty pozostają odrębne | PASS |
| PRI01-DOD-62 | różne jednostki pozostają odrębne | PASS |
| PRI01-DOD-63 | matched i structural scope są rozdzielone | PASS |
| PRI01-DOD-64 | not_comparable blokuje ranking gap | PASS |
| PRI01-DOD-65 | priority order ma katalog | PASS |
| PRI01-DOD-66 | rank basis jest audytowalny | PASS |
| PRI01-DOD-67 | tie flag zachowuje remis | PASS |
| PRI01-DOD-68 | review_now wymaga podstawy | PASS |
| PRI01-DOD-69 | validate_first wymaga required gap | PASS |
| PRI01-DOD-70 | parallel nie autoryzuje decyzji bez danych | PASS |
| PRI01-DOD-71 | observe nie tworzy problemu | PASS |
| PRI01-DOD-72 | TEST_PARTIAL ma routing zakresowy | PASS |
| PRI01-DOD-73 | TEST_BLOCKED ma routing walidacyjny | PASS |
| PRI01-DOD-74 | confidence nie steruje automatycznie znaczeniem | PASS |
| PRI01-DOD-75 | priority stability nie jest confidence | PASS |
| PRI01-DOD-76 | source threshold ma basis | PASS |
| PRI01-DOD-77 | priority basis summary jest audytowalne | PASS |
| PRI01-DOD-78 | payload CONF pozostaje rezerwą | PASS |
| PRI01-DOD-79 | payload orchestration nie zawiera algorytmu | PASS |
| PRI01-DOD-80 | brak automatycznych zaleceń kadrowych | PASS |
| PRI01-DOD-81 | brak automatycznych zaleceń kosztowych | PASS |
| PRI01-DOD-82 | brak automatycznych zaleceń cenowych | PASS |
| PRI01-DOD-83 | brak automatycznych zaleceń capacity | PASS |
| PRI01-DOD-84 | brak danych SPZOZ | PASS |
| PRI01-DOD-85 | brak danych pacjentów | PASS |

### 17.3. PRI01-DOD-86–95

| ID | Warunek zamknięcia | Wynik |
| --- | --- | --- |
| PRI01-DOD-86 | problem_priority_basis i status podstawy są kompletne | PASS |
| PRI01-DOD-87 | validation_priority_basis jest kompletna | PASS |
| PRI01-DOD-88 | kwalifikacja obu priorytetów jest deterministyczna | PASS |
| PRI01-DOD-89 | macierz zgodności obejmuje wszystkie kombinacje | PASS |
| PRI01-DOD-90 | cluster_priority_record jest częścią kontraktu FINDINGS | PASS |
| PRI01-DOD-91 | działania klastra używają katalogów głównych | PASS |
| PRI01-DOD-92 | stabilność rozdziela problem_priority i validation_priority | PASS |
| PRI01-DOD-93 | not_assessable jest wyłączone z porządku stabilności | PASS |
| PRI01-DOD-94 | remis częściowy zachowuje wspólną pozycję i tie group | PASS |
| PRI01-DOD-95 | scenariusze PRI01-T01–T40 są kompletne | PASS |

## 18. Test końcowy QPRI01-001–125

| ID | Kontrola końcowa | Wynik |
| --- | --- | --- |
| QPRI01-001 | PRI-01 jest uniwersalny branżowo | PASS |
| QPRI01-002 | Priorytet ≠ pewność | PASS |
| QPRI01-003 | Priorytet problemu ≠ priorytet walidacji | PASS |
| QPRI01-004 | Ważność ≠ stabilność | PASS |
| QPRI01-005 | Brak Priority Score 0–100 | PASS |
| QPRI01-006 | Brak średniej ważonej | PASS |
| QPRI01-007 | Brak arbitralnych wag | PASS |
| QPRI01-008 | Brak HIGH/MEDIUM/LOW jako metodologii | PASS |
| QPRI01-009 | Brak arbitralnej business materiality | PASS |
| QPRI01-010 | Brak arbitralnych progów pilności | PASS |
| QPRI01-011 | review_now wymaga jawnej podstawy | PASS |
| QPRI01-012 | validate_first wymaga krytycznego required gap albo równoważnej blokady | PASS |
| QPRI01-013 | parallel nie oznacza zgody na nieodwracalną decyzję bez wymaganych danych | PASS |
| QPRI01-014 | Niska confidence nie obniża automatycznie priorytetu | PASS |
| QPRI01-015 | Wysoka confidence nie podnosi automatycznie priorytetu | PASS |
| QPRI01-016 | PRI działa przed powstaniem CONF-01 | PASS |
| QPRI01-017 | Brak zastępczego Confidence Score | PASS |
| QPRI01-018 | Ten sam wpływ FIN-01/02/03 nie jest liczony trzy razy | PASS |
| QPRI01-019 | Supporting evidence nie jest drugim impactem | PASS |
| QPRI01-020 | Impact overlap jest jawny | PASS |
| QPRI01-021 | Klaster nie oznacza przyczynowości | PASS |
| QPRI01-022 | Primary finding jest odróżniony od supporting evidence | PASS |
| QPRI01-023 | Evidence independence jest jawna | PASS |
| QPRI01-024 | Trzy testy z jednego źródła nie są trzema niezależnymi dowodami | PASS |
| QPRI01-025 | Ranking istnieje tylko w grupie porównywalności | PASS |
| QPRI01-026 | Różne waluty bez źródłowego przeliczenia są incomparable | PASS |
| QPRI01-027 | Różne horyzonty bez uzgodnienia są incomparable | PASS |

### 18.1. QPRI01-028–054

| ID | Kontrola końcowa | Wynik |
| --- | --- | --- |
| QPRI01-028 | Różne jednostki operacyjne nie są arbitralnie normalizowane | PASS |
| QPRI01-029 | Remisy są dozwolone | PASS |
| QPRI01-030 | Brak podstawy może dać insufficient_basis | PASS |
| QPRI01-031 | TEST_PARTIAL nie oznacza automatycznie niskiego priorytetu | PASS |
| QPRI01-032 | TEST_BLOCKED może podnosić validation priority | PASS |
| QPRI01-033 | One-off nie jest automatycznie structural | PASS |
| QPRI01-034 | Incident może być pilny mimo braku persistence | PASS |
| QPRI01-035 | Persistent nie oznacza automatycznie review_now | PASS |
| QPRI01-036 | MGT-01 może generować priorytet walidacji bez kwoty | PASS |
| QPRI01-037 | information_gap_count nie jest mnożone przez blocked metrics | PASS |
| QPRI01-038 | blocked_decisions_count korzysta z definicji MGT-01 | PASS |
| QPRI01-039 | Priority horizon ma podstawę | PASS |
| QPRI01-040 | Reversibility nie jest scoringiem | PASS |
| QPRI01-041 | Validation effort nie jest scoringiem | PASS |
| QPRI01-042 | next_tests nie stają się pełną orkiestracją | PASS |
| QPRI01-043 | PRI nie projektuje ZOP-CONF-01 | PASS |
| QPRI01-044 | PRI nie projektuje pełnej orkiestracji | PASS |
| QPRI01-045 | PRI nie zmienia żadnego testu Core 10 | PASS |
| QPRI01-046 | Brak automatycznych zaleceń kadrowych | PASS |
| QPRI01-047 | Brak automatycznych zaleceń kosztowych | PASS |
| QPRI01-048 | Brak automatycznych zaleceń cenowych | PASS |
| QPRI01-049 | Brak automatycznych zaleceń capacity | PASS |
| QPRI01-050 | Brak automatycznych zaleceń zamknięcia produktu | PASS |
| QPRI01-051 | Brak automatycznej wyceny potencjału | PASS |
| QPRI01-052 | Czas nie jest przeliczany na pieniądze bez źródła | PASS |
| QPRI01-053 | Capacity nie jest przeliczana na pieniądze bez źródła | PASS |
| QPRI01-054 | Brak wspólnego score dla danych finansowych i operacyjnych | PASS |

### 18.2. QPRI01-055–081

| ID | Kontrola końcowa | Wynik |
| --- | --- | --- |
| QPRI01-055 | Priority basis summary jest audytowalne | PASS |
| QPRI01-056 | management_attention_route nie jest decyzją wykonawczą | PASS |
| QPRI01-057 | problem_priority_action ma katalog zamknięty | PASS |
| QPRI01-058 | validation_priority_action ma katalog zamknięty | PASS |
| QPRI01-059 | priority_order_status ma katalog zamknięty | PASS |
| QPRI01-060 | priority_stability_status ma katalog zamknięty | PASS |
| QPRI01-061 | impact_accounting_role ma katalog zamknięty | PASS |
| QPRI01-062 | finding_role_in_cluster ma katalog zamknięty | PASS |
| QPRI01-063 | cluster_relation_type nie tworzy przyczynowości | PASS |
| QPRI01-064 | Matched/full scope jest zachowane z testu źródłowego | PASS |
| QPRI01-065 | Source threshold jest źródłowy | PASS |
| QPRI01-066 | Urgency basis jest źródłowy | PASS |
| QPRI01-067 | 0 danych SPZOZ | PASS |
| QPRI01-068 | 0 danych pacjentów | PASS |
| QPRI01-069 | 0 rozpoczętego ZOP-CONF-01 | PASS |
| QPRI01-070 | 0 rozpoczętej pełnej orkiestracji | PASS |
| QPRI01-071 | 0 rozpoczętego PRI-02 | PASS |
| QPRI01-072 | Istnieje 40 scenariuszy | PASS |
| QPRI01-073 | VAL kompletne | PASS |
| QPRI01-074 | ACC kompletne | PASS |
| QPRI01-075 | DOD kompletne | PASS |
| QPRI01-076 | Dokument jest implementowalny przez Aleksandra | PASS |
| QPRI01-077 | Narracja jest po polsku, techniczne identyfikatory pozostają | PASS |
| QPRI01-078 | problem_priority_action opisuje kolejność uwagi | PASS |
| QPRI01-079 | validation_priority_action jest niezależne od problem_priority_action | PASS |
| QPRI01-080 | management_attention_route wynika z jawnych reguł | PASS |
| QPRI01-081 | rank istnieje wyłącznie w poprawnej grupie | PASS |

### 18.3. QPRI01-082–105

| ID | Kontrola końcowa | Wynik |
| --- | --- | --- |
| QPRI01-082 | tie flag zachowuje remis | PASS |
| QPRI01-083 | urgency_flag nie tworzy terminu bez basis | PASS |
| QPRI01-084 | response window ma jawną podstawę | PASS |
| QPRI01-085 | trudna odwracalność może wpływać na walidację bez score | PASS |
| QPRI01-086 | incident_flag ma podstawę | PASS |
| QPRI01-087 | persistence_status i periods są jawne | PASS |
| QPRI01-088 | recurrence_count nie dowodzi przyczyny | PASS |
| QPRI01-089 | finding role odróżnia problem od dowodu | PASS |
| QPRI01-090 | impact_group_id chroni wpływ | PASS |
| QPRI01-091 | economic_impact_role określa rolę wartości | PASS |
| QPRI01-092 | operational_impact_unit pozostaje źródłowa | PASS |
| QPRI01-093 | miary operacyjne nie są przeliczane na PLN bez źródła | PASS |
| QPRI01-094 | source threshold value ma basis | PASS |
| QPRI01-095 | priority_change_reason jest jawne | PASS |
| QPRI01-096 | nieporównywalność current/reference nie tworzy rankingu | PASS |
| QPRI01-097 | matched i structural impact pozostają rozdzielone | PASS |
| QPRI01-098 | liczniki MGT są deterministyczne | PASS |
| QPRI01-099 | jedna luka nie jest liczona wielokrotnie przez skutki | PASS |
| QPRI01-100 | next_test_priority_order nie jest pełną orkiestracją | PASS |
| QPRI01-101 | warstwa użytkowa jest po polsku | PASS |
| QPRI01-102 | metadane DOCX są zgodne | PASS |
| QPRI01-103 | cały dokument został wyrenderowany i sprawdzony | PASS |
| QPRI01-104 | pola Core 10 nie są redefiniowane sprzecznie | PASS |
| QPRI01-105 | brak metody Delphi i głosowania ekspertów | PASS |

### 18.4. QPRI01-106–125

| ID | Kontrola końcowa | Wynik |
| --- | --- | --- |
| QPRI01-106 | problem_priority_basis jest audytowalne | PASS |
| QPRI01-107 | problem_priority_basis_status jest jawny | PASS |
| QPRI01-108 | review_now wymaga niekorzystnego lub incydentalnego wyniku | PASS |
| QPRI01-109 | review_next różni się od plan_review bez progu liczbowego | PASS |
| QPRI01-110 | validation_priority_basis jest audytowalna | PASS |
| QPRI01-111 | validate_next różni się od validate_when_needed warunkiem czasowym | PASS |
| QPRI01-112 | macierz zgodności usuwa dowolność implementacyjną | PASS |
| QPRI01-113 | review_now + validate_now respektuje required information | PASS |
| QPRI01-114 | observe + no_additional_validation prowadzi do observe | PASS |
| QPRI01-115 | plan_review jest spójne z trasą plan | PASS |
| QPRI01-116 | cluster_priority_action używa katalogu problem_priority_action | PASS |
| QPRI01-117 | cluster_validation_priority_action używa katalogu validation_priority_action | PASS |
| QPRI01-118 | cluster_management_attention_route używa katalogu management_attention_route | PASS |
| QPRI01-119 | cluster_priority_basis_summary jest w kontrakcie danych | PASS |
| QPRI01-120 | stabilność porównuje tylko ten sam wymiar i kontekst | PASS |
| QPRI01-121 | porządki stabilności nie są Priority Score | PASS |
| QPRI01-122 | management_attention_route nie jest porządkowana liniowo | PASS |
| QPRI01-123 | not_assessable nie tworzy automatycznej zmiany uwagi | PASS |
| QPRI01-124 | priority_tie_group_id zachowuje B = C w porządku A > B = C > D | PASS |
| QPRI01-125 | PRI01-T36–T40 przechodzą regresję | PASS |

## 19. Status końcowy i otwarte kontrakty systemowe

| Element | Status |
| --- | --- |
| ZOP-PRI-01 v1.0 | ZAMKNIĘTY METODOLOGICZNIE DO IMPLEMENTACJI |
| ZOP-CONF-01 | DO OPRACOWANIA |
| Orkiestracja next_tests | DO OPRACOWANIA |
| Core 10 | ZAMROŻONY – 0 zmian |

### 19.1. Dziedziczone otwarte kontrakty

| Kontrakt | Zakres pozostający do opracowania |
| --- | --- |
| ZOP-CONF-01 | pewność diagnozy, klasy, podstawa i progi |
| globalna polityka istotności biznesowej | organizacyjne progi i zasady materiality |
| pełna orkiestracja next_tests | algorytm uruchamiania i kolejność między wynikami |
| globalny kontrakt work_content | wspólna semantyka nakładu pracy |
| globalny standard activity_unit i weighted_volume | jednostki i ważenie wolumenu |
| wspólna polityka alokacji shared cost | reguły przypisywania kosztów wspólnych |
| globalny standard kalendarzy i time basis | spójność czasu operacyjnego |
| capability/resource substitution | zasady zastępowalności zasobów |
| globalna podstawa kosztowa i klasyfikacja one-off | wspólna semantyka kosztu i korekt |
| pełny graf zależności i silnik reguł decyzyjnych | mechanizm wykonawczy poza PRI-01 |

### 19.2. Potwierdzenia granic

| Kontrola | Wynik |
| --- | --- |
| Priority Score 0–100 | 0 |
| arbitralne wagi i progi | 0 |
| podwójnie liczony wpływ | 0 |
| automatyczne rekomendacje wykonawcze | 0 |
| zmiany Core 10 | 0 |
| dane SPZOZ / dane pacjentów | 0 / 0 |
| rozpoczęty ZOP-CONF-01 / orkiestracja / PRI-02 | 0 / 0 / 0 |
| PRI01-VAL | 78 / PASS |
| PRI01-ACC | 95 / PASS |
| PRI01-DOD | 95 / PASS |
| QPRI01 | 125 / PASS |
| Scenariusze | 40 / PASS |

> **STATUS ZOP-PRI-01 v1.0 – ZAMKNIĘTY METODOLOGICZNIE DO IMPLEMENTACJI. Dokument ustala kolejność uwagi i walidacji; nie podejmuje decyzji wykonawczej.**
