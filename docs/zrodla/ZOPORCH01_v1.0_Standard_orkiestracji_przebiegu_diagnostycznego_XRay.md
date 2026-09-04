ZOPTYMALIZOWANI – X-RAY

# ORCH-01

*Standard orkiestracji przebiegu diagnostycznego X-Ray*

Karta metodologiczna i specyfikacja implementacyjna

| METADANE DOKUMENTU | WARTOŚĆ |
| --- | --- |
| Identyfikator | ZOP-ORCH-01 |
| Wersja | v1.0 |
| Status | ZAMKNIĘTY METODOLOGICZNIE DO IMPLEMENTACJI |
| Zakres | Deterministyczne prowadzenie jednej sprawy diagnostycznej przez istniejącą sieć testów, walidacji, priorytetów i ocen pewności |
| Dokumenty zamrożone | Core 10, ZOP-PRI-01 v1.0 i ZOP-CONF-01 v1.0 – 0 zmian |
| Odbiorca implementacyjny | Aleksander / warstwa technologiczna X-Ray |

> **PYTANIE NADRZĘDNE Mając określone pytanie diagnostyczne, wyniki Core 10, jakość informacji MGT-01, priorytet PRI-01 i pewność CONF-01 – jaki jest następny legalny i uzasadniony krok, kiedy należy walidować, uruchomić test, dopuścić równoległość, legalnie powtórzyć test, zatrzymać ścieżkę albo przekazać wybór człowiekowi?**

## 1. Rola, cel i granice ORCH-01

ORCH-01 prowadzi jedną sprawę diagnostyczną od jawnego pytania wejściowego do jawnego stanu zakończenia. Nie wykonuje obliczeń Core 10, nie zastępuje MGT-01, PRI-01 ani CONF-01 i nie wydaje decyzji wykonawczych. Wybiera wyłącznie następny krok dozwolony przez istniejące kontrakty.

| ORCH-01 robi | ORCH-01 nie robi |
| --- | --- |
| tworzy audytowalny przebieg sprawy, gałęzi i kroków | nie jest jedenastym testem diagnostycznym |
| kwalifikuje kandydatów z legalnych źródeł | nie wymyśla testów ani działań walidacyjnych |
| stosuje bramy informacji, zakresu, zależności i wartości diagnostycznej | nie reinterpretowuje matematyki ani statusów źródłowych |
| zarządza sekwencją, równoległością, powtórzeniem i scaleniem | nie tworzy Priority, Confidence, Data Quality ani Value of Information Score |
| zatrzymuje ścieżkę w poprawnym stanie | nie rekomenduje zatrudnienia, zwolnień, cen, zakupów ani zamknięcia produktów |
| prowadzi do bramy decyzji człowieka | nie zastępuje decyzji zarządczej |

> **ZASADA ZAMROŻENIA Core 10, MGT-01, PRI-01 i CONF-01 pozostają bez zmian. Rzeczywista sprzeczność ich kontraktów jest blokadą metodologiczną; ORCH-01 nie naprawia jej lokalnie.**

### 1.1. Hierarchia i precedencja warstw

| Kolejność | Warstwa | Znaczenie dla prowadzenia ścieżki |
| --- | --- | --- |
| 1 | MGT-01 i wymagane walidacje | blokada wymaganej informacji ma pierwszeństwo przed zależnym testem |
| 2 | PRI-01 | ustala legalny porządek uwagi i walidacji tam, gdzie kontrakt pozwala porównywać |
| 3 | CONF-01 | określa siłę wsparcia i konkretne potrzeby walidacyjne; nie ustala priorytetu |
| 4 | Core 10 / next_tests | dostarcza wyniki i kandydatów, lecz nie automatyczny plan wykonania |
| 5 | ORCH-01 | kwalifikuje kandydatów i wybiera następny krok bez sumowania warstw |

## 2. Model sprawy diagnostycznej

### 2.1. Rekord sprawy

| Pole | Wymagalność | Kontrakt |
| --- | --- | --- |
| diagnostic_case_id | required | trwały, jednoznaczny identyfikator sprawy |
| diagnostic_question | required | jawne pytanie, na które ma odpowiedzieć ścieżka |
| decision_context | required | kontekst, w którym odpowiedź może zostać użyta |
| case_scope | required | zakres organizacyjny, produktowy, zasobowy lub procesowy |
| case_period | required | okres bieżący i – gdy dotyczy – odniesienia |
| case_version | required | wersja rekordu sprawy; historia nie jest nadpisywana |
| case_created_at | required | znacznik utworzenia sprawy |
| case_status | required | jedna wartość z zamkniętego katalogu |
| entry_trigger | required | źródło rozpoczęcia ścieżki |
| entry_trigger_basis | required | audytowalna podstawa wejścia |

| case_status | Znaczenie |
| --- | --- |
| open | sprawa utworzona, bez wykonanego kroku |
| in_progress | co najmniej jedna gałąź jest aktywna lub gotowa |
| awaiting_validation | dalsza diagnoza wymaga zdefiniowanej i możliwej walidacji |
| awaiting_human_decision | dalszy przebieg zależy od jawnego wyboru człowieka |
| paused_monitoring | brak podstawy do dalszego testu teraz; wymagany monitoring lub przyszły przegląd |
| completed | cel odpowiedzialnie osiągnięty albo brak sygnału potwierdzony dla badanego zakresu |
| blocked | brak legalnej ścieżki do odpowiedzi lub blokada metodologiczna/informacyjna/techniczna |
| cancelled | sprawa anulowana z zachowaniem pełnej historii |

### 2.2. Maszyna stanów sprawy

| Pole przejścia | Kontrakt |
| --- | --- |
| case_status_previous | status przed rozpatrywanym przejściem |
| case_status_current | status po dozwolonym przejściu albo status niezmieniony po odrzuceniu |
| case_status_transition_reason | jednoznaczny powód biznesowo-diagnostyczny przejścia |
| case_status_transition_basis | odwołania do kroku, walidacji, decyzji, wyzwalacza albo warunku zatrzymania |
| case_status_transition_allowed | true wyłącznie dla przejścia dopuszczonego przez poniższy kontrakt |

| Status poprzedni | Status bieżący | Warunek dopuszczający przejście |
| --- | --- | --- |
| open | in_progress | wykonano pierwszy legalny krok |
| in_progress | awaiting_validation | wymagana walidacja blokuje dalszą trasę |
| awaiting_validation | in_progress | walidacja zmieniła podstawę i umożliwia ponowną kwalifikację |
| in_progress | awaiting_human_decision | aktywowano prawidłową bramę decyzji człowieka |
| awaiting_human_decision | in_progress | rozwiązana decyzja pozwala wznowić diagnozę |
| in_progress | paused_monitoring | obserwacja jest właściwym dalszym stanem |
| paused_monitoring | in_progress | nowy legalny entry_trigger albo jawna zmiana podstawy |
| in_progress | completed | spełniono warunki stop_completed |
| in_progress / awaiting_validation | blocked | nie istnieje legalna droga do wymaganej odpowiedzi |
| blocked | in_progress | jawna zmiana podstawy: nowe dane, rozwiązanie blokady albo nowa wersja kontraktu |

> **STANY KOŃCOWE WERSJI SPRAWY completed oraz cancelled nie przechodzą do in_progress. Nowy okres, sygnał lub kontekst tworzy nową sprawę albo derived_case_id. Wznowienie blocked zachowuje poprzedni status i pełną podstawę przejścia w historii.**

### 2.3. Cel diagnostyczny

| Pole | Kontrakt |
| --- | --- |
| diagnostic_objective | jawny efekt poznawczy: wykrycie zjawiska, określenie skali, zawężenie zakresu, rozróżnienie mechanizmów albo potwierdzenie mechanizmu |
| diagnostic_objective_status | unanswered; partially_answered; answered; blocked; not_assessable |
| diagnostic_objective_basis | uzasadnienie statusu przez wyniki, walidacje, luki i pozostałych kandydatów |

Liczba wykonanych testów nie stanowi warunku zakończenia. Status answered wymaga odpowiedzi w zakresie i na poziomie szczegółowości określonym przez diagnostic_objective.

### 2.4. Zakres i okres trasy

| Pole | Reguła |
| --- | --- |
| route_scope | zakres właściwy dla konkretnej gałęzi i kroku |
| route_period | okres właściwy dla konkretnej gałęzi i kroku |
| route_scope_basis | podstawa dopasowania, transformacji albo utworzenia nowej gałęzi |
| route_period_basis | podstawa zgodności okresów bieżącego i odniesienia |
| matched scope / full scope | zachowują znaczenie kart źródłowych; wynik nie przechodzi między nimi bez jawnej podstawy |

## 3. Sprawa, gałąź i krok

| Poziom | Identyfikator | Rola |
| --- | --- | --- |
| sprawa | diagnostic_case_id | wspólne pytanie, kontekst decyzji, zakres nadrzędny i stan zakończenia |
| gałąź | diagnostic_branch_id | odrębne pytanie pomocnicze albo cel dowodowy |
| krok | diagnostic_step_id | jedna jawna decyzja orkiestracyjna i jej wykonanie |

| branch_status | Znaczenie |
| --- | --- |
| active | gałąź prowadzona |
| waiting | oczekuje na zależność lub wybór |
| completed | cel gałęzi osiągnięty |
| blocked | gałąź nie ma legalnego przejścia |
| merged | wynik włączony do grupy scalającej |
| cancelled | anulowana bez usuwania historii |

| Pole gałęzi | Kontrakt |
| --- | --- |
| diagnostic_branch_id | jednoznaczny identyfikator w ramach sprawy |
| parent_branch_id | gałąź nadrzędna albo null dla gałęzi głównej |
| branch_question | odrębne pytanie pomocnicze |
| branch_target_claim | twierdzenie, którego wsparcie ma zmienić gałąź |
| branch_dependency_status | jawne zależności od innych gałęzi, walidacji lub decyzji |
| branch_status | wartość z katalogu zamkniętego |

### 3.1. Rodzaje kroku i status wykonania

| orchestration_action | Znaczenie |
| --- | --- |
| run_test | uruchom jeden zakwalifikowany test |
| run_parallel_tests | uruchom niezależną grupę zakwalifikowanych testów |
| validate_information | wykonaj istniejącą walidację MGT-01 lub CONF-01 |
| rerun_test | powtórz test po jawnej zmianie podstawy |
| merge_branches | połącz zależności bez uśredniania wyników |
| observe | przejdź do obserwacji albo monitoringu |
| stop_completed | zakończ cel osiągnięty w wymaganym zakresie |
| stop_blocked | zatrzymaj ścieżkę z jawną blokadą |
| human_decision_gate | przekaż konkretny wybór człowiekowi |
| cancel_branch | anuluj gałąź z zachowaniem historii |

| step_status | Znaczenie |
| --- | --- |
| planned | krok zaplanowany |
| ready | spełnia wymagania uruchomienia |
| running | wykonywany |
| completed | wykonany technicznie i zapisany |
| blocked | zatrzymany przez jawną blokadę |
| failed_technical | błąd wykonania, nie wynik diagnostyczny |
| skipped | pominięty z jawną podstawą |
| cancelled | anulowany bez utraty historii |

## 4. Rozpoczęcie ścieżki

| entry_trigger | Znaczenie |
| --- | --- |
| manual_question | jawne pytanie człowieka |
| adverse_finding | niekorzystny wynik istniejącego testu |
| information_gap | luka informacyjna wymagająca walidacji |
| validation_result | wynik walidacji zmieniający podstawę |
| recurring_signal | powtarzalny sygnał na nowej wersji danych |
| external_trigger | zdarzenie zewnętrzne wymagające diagnozy |
| scheduled_review | zaplanowany przegląd bez automatycznego założenia problemu |

Każdy entry_trigger ma entry_trigger_basis. Sam fakt dostępności danych lub testów nie tworzy podstawy do uruchomienia wszystkich Core 10.

### 4.1. Typ pytania i mapowanie pierwszych kandydatów

| diagnostic_question_type | Kandydaci wejściowi | Podstawa mapowania |
| --- | --- | --- |
| financial_performance | FIN-01; FIN-02 | relacja dynamiki kosztów i przychodów albo erozja rentowności; wybór zależy od jawnej treści pytania |
| unit_economics | FIN-03 | koszt jednostkowy i źródła jego zmiany |
| portfolio_economics | PORT-01 | ekonomika i struktura portfela |
| labor_productivity | HR-01 | koszt pracy, nakład i efekt |
| capacity_utilization | CAP-01 | wykorzystanie dostępnej zdolności |
| capacity_pressure | CAP-02 | zapotrzebowanie na pracę względem dostępnej zdolności |
| process_time | PROC-01 | czas realizacji, oczekiwanie i opóźnienie |
| process_constraint | PROC-02 | rzeczywiste ograniczenie przepływu |
| information_readiness | MGT-01 | gotowość informacji dla miary, testu albo decyzji |
| unknown_or_cross_domain | MGT-01 / doprecyzowanie / legalne gałęzie | brak arbitralnego wyboru testu; wymagane question_type_basis |

> **GRANICA MAPOWANIA Mapowanie question_type → candidate tests jest jawnym kontraktem regułowym, nie klasyfikatorem języka naturalnego. Pytanie niejednoznaczne prowadzi do doprecyzowania, MGT-01 albo kilku gałęzi tylko przy jawnej podstawie.**

## 5. Kontrakty wejściowe

| Źródło | Pola wejściowe | Granica ORCH-01 |
| --- | --- | --- |
| Core 10 | test_id; finding_id; status; finding; metric_value; reference_value; gap; next_tests; validation_required | bez przeliczania lub reinterpretacji testu |
| MGT-01 | decision_information_status; critical_information_gap; information_gap_id; blocked_metrics_count; blocked_tests_count; blocked_decisions_count; reconciliation_status; data_conflict_flag; urgent_validation | bez redefinicji jakości informacji |
| PRI-01 | problem_priority_action; validation_priority_action; management_attention_route; priority_order_status; priority_rank_within_group; priority_tie_group_id; priority_horizon; next_test_priority_order; next_test_priority_basis | bez własnego priorytetu i bez sumowania wymiarów |
| CONF-01 | finding_confidence_class; mechanism_confidence_class; confidence_validation_required; confidence_validation_action; confidence_validation_actions; confidence_validation_basis; cross_test_support_status; evidence_independence_status; confidence_conflict_status; critical_confidence_limitation_flag; confidence_stability_status | bez przeliczania klas albo tworzenia wyniku punktowego |

## 6. Kandydat na następny krok

| Pole | Kontrakt |
| --- | --- |
| route_candidate_id | jednoznaczny identyfikator kandydata w sprawie |
| route_candidate_type | test; validation; human_gate; stop; observe |
| route_candidate_target | nazwa testu, walidacji, bramy albo stanu zakończenia |
| route_candidate_target_id | identyfikator konkretnego celu |
| route_candidate_source | next_tests; CONF validation actions; MGT required validation; PRI management route; stop conditions |
| route_candidate_basis | źródłowa i audytowalna podstawa utworzenia |
| route_candidate_status | candidate; qualified; blocked; duplicate; not_applicable; selected; rejected |

ORCH-01 nie tworzy kandydata poza katalogami źródłowymi. next_tests oznacza zbiór kandydatów, nie polecenie automatycznego uruchomienia.

### 6.1. Bramki kwalifikacji kandydata

| Brama | Pytanie | Skutek negatywny |
| --- | --- | --- |
| candidate_applicability_gate | Czy krok odpowiada na konkretne nierozstrzygnięte pytanie, lukę albo mechanizm? | brak związku → not_applicable |
| candidate_information_gate | Czy wymagane informacje są dostępne albo możliwe do zwalidowania? | wymagana luka → validation lub blocked |
| candidate_scope_period_gate | Czy zakres i okres kandydata są zgodne z gałęzią? | niedopasowanie → transformacja, nowa gałąź lub odrzucenie |
| candidate_duplication_gate | Czy route_signature nie powtarza istniejącego wykonania bez nowej podstawy? | duplikat → duplicate |
| candidate_dependency_gate | Czy zakończono kroki ustalające parametry lub sens kandydata? | nierozwiązana zależność → waiting lub sequential |
| candidate_diagnostic_value_gate | Czy krok może zmienić cel, rozwiązać lukę, zawęzić twierdzenie albo rozróżnić mechanizmy? | supporting_only/duplicate/no_new_information może zostać odrzucone |
| candidate_human_boundary_gate | Czy krok pozostaje diagnozą, a nie decyzją wykonawczą lub polityczną? | przekroczenie granicy → human_decision_gate |

| candidate_gate_status | Znaczenie |
| --- | --- |
| pass | warunek spełniony |
| pass_with_limitations | warunek spełniony z jawnym nieblokującym ograniczeniem |
| fail | warunek niespełniony i blokuje kwalifikację |
| not_assessable | brak podstaw do oceny bramy; kandydat nie może zostać selected |

Kandydat uzyskuje route_candidate_status = qualified tylko wtedy, gdy wszystkie wymagane bramy mają pass albo dopuszczalne pass_with_limitations. Status selected może otrzymać wyłącznie kandydat qualified po zastosowaniu reguł kolejności, równoległości i granicy człowieka.

### 6.2. Deterministyczna kolejność kwalifikacji

| Etap | Reguła |
| --- | --- |
| 1 | zbierz kandydatów wyłącznie z legalnych źródeł |
| 2 | usuń kandydatów nieadekwatnych dla diagnostic_objective |
| 3 | sprawdź required information oraz walidacje MGT-01 / CONF-01 |
| 4 | sprawdź route_scope, route_period i ich podstawy |
| 5 | wylicz deterministyczną route_signature i sprawdź duplikację |
| 6 | sprawdź zależności i możliwy tryb wykonania |
| 7 | określ information_contribution_status |
| 8 | sprawdź granicę decyzji człowieka |
| 9 | zastosuj wyłącznie legalne uporządkowanie z PRI-01; nie rozstrzygaj tied/incomparable arbitralnie |
| 10 | wybierz krok, równoległą grupę, walidację, obserwację, bramę człowieka albo warunek zatrzymania |

## 7. Sygnatura trasy i deduplikacja

| Element route_signature | Wymaganie |
| --- | --- |
| target | test albo walidacja i identyfikator celu |
| route_scope | zakres wykonania |
| route_period | okres wykonania |
| data_version | merytoryczna wersja danych |
| evidence_version | wersja podstawy dowodowej |
| diagnostic_objective / claim | nierozstrzygnięty cel albo twierdzenie |
| orchestration_rule_version | wersja reguł kwalifikacji |

Metodologia nie narzuca funkcji skrótu. Implementacja ma zapewnić deterministyczną identyfikację równoważnego wykonania. duplicate_execution_flag i duplicate_execution_basis dokumentują wynik sprawdzenia.

> **KONWERGENCJA Jeżeli dwie gałęzie prowadzą do tego samego testu i tej samej route_signature, test wykonuje się raz, a wynik przypisuje do obu zależności. Różny zakres, okres, wersja danych albo cel nie może zostać błędnie deduplikowany.**

## 8. Sekwencyjność, równoległość i kolejność

| execution_mode | Warunek |
| --- | --- |
| sequential | wynik jednego kroku ustala zakres, dane, twierdzenie, parametry albo sens kolejnego |
| parallel | kandydaci są niezależni, nie dzielą nierozwiązanej walidacji, odpowiadają na odrębne pytania i nie dublują informacji |
| not_applicable | tryb nie dotyczy pojedynczej decyzji zatrzymania, obserwacji albo bramy człowieka |

| Pole | Kontrakt |
| --- | --- |
| sequential_dependency_basis | jawna zależność wymuszająca kolejność |
| parallel_execution_allowed | wartość logiczna wynikająca ze wszystkich warunków równoległości |
| parallel_execution_basis | audytowalne uzasadnienie niezależności i braku wspólnej blokady |
| parallel_group_id | wspólny identyfikator kroków wykonanych równolegle |
| route_order_source | PRI-01 albo not_applicable; ORCH nie tworzy własnego rankingu |
| route_order_status | ordered; tied; incomparable; not_assessable; not_applicable |

> **REMIS I NIEPORÓWNYWALNOŚĆ tied oraz incomparable nie są rozstrzygane losowo ani nowym rankingiem. Niezależni kandydaci mogą tworzyć parallel_group_id; kandydaci, których nie można wykonać równolegle, prowadzą do human_decision_gate typu route_choice albo pozostają waiting.**

### 8.1. Wyjście pojedynczego i równoległego wyboru

| Pole | Kontrakt |
| --- | --- |
| selected_route_candidate_id | pole zgodności dla pojedynczego wyboru; przy wielu wybranych kandydatach null albo jawnie not_used_in_parallel |
| selected_route_target | pole zgodności dla pojedynczego celu; w trybie równoległym null albo jawnie not_used_in_parallel |
| selected_route_candidate_ids | uporządkowany zbiór unikalnych identyfikatorów wybranych kandydatów |
| selected_route_targets | uporządkowany zbiór unikalnych celów odpowiadających wybranym kandydatom |
| selected_route_edge_ids | uporządkowany zbiór unikalnych krawędzi grafu użytych przez wybrane trasy |

| orchestration_action | Liczność zbiorów wyboru | Reguła pola pojedynczego |
| --- | --- | --- |
| run_test | dokładnie 1 element | selected_route_candidate_id i selected_route_target odpowiadają jedynemu elementowi |
| run_parallel_tests | co najmniej 2 unikalne elementy; jeden parallel_group_id | selected_route_candidate_id i selected_route_target są null albo not_used_in_parallel |
| stop_completed; stop_blocked; observe; human_decision_gate | 0 elementów jest dopuszczalne bez wykonawczego kandydata | pola pojedyncze mogą być null |

> **BRAK SZTUCZNEGO KANDYDATA GŁÓWNEGO Jeżeli selected_route_candidate_ids zawiera więcej niż jeden element, ORCH-01 nie wybiera pierwszego rekordu jako głównego. Wszystkie elementy run_parallel_tests mają równorzędny status wyboru i wspólny parallel_group_id.**

## 9. Legalne powtórzenie testu

| repeat_test_reason | Znaczenie |
| --- | --- |
| data_updated | merytorycznie zmieniła się podstawa danych |
| validation_completed | zakończona walidacja zmieniła podstawę |
| conflict_resolved | rozwiązano konflikt wpływający na test |
| scope_changed | zmienił się zakres wykonania |
| period_changed | zmienił się okres wykonania |
| evidence_updated | zmieniła się podstawa dowodowa |
| definition_version_changed | zmieniła się zatwierdzona definicja |
| upstream_result_changed | zmienił się wynik kroku nadrzędnego istotny dla testu |

| Pole | Kontrakt |
| --- | --- |
| repeat_test_allowed | true tylko przy co najmniej jednym prawdziwym i udokumentowanym repeat_test_reason |
| repeat_test_reason | jedna wartość z katalogu zamkniętego |
| repeat_test_previous_execution_id | identyfikator wykonania, które ma zostać powtórzone |
| source_version_change_basis | wyjaśnia merytoryczną zmianę wersji, nie tylko zmianę techniczną pliku |

> **ZAKAZ POWTÓRZENIA Jeżeli nie zmieniły się dane, zakres, okres, dowody, definicja, walidacja ani wynik nadrzędny, rerun_test dla tej samej route_signature jest zabronione.**

### 9.1. Pętla walidacyjna

Sekwencja TEST → MGT/CONF → WALIDACJA → RERUN TEST jest legalna wyłącznie wtedy, gdy walidacja zmieniła podstawę informacyjną lub dowodową, utworzono jej nową wersję i powiązano ją z poprzednim krokiem. Techniczne wykonanie walidacji bez zmiany podstawy nie otwiera powtórzenia.

| Stan walidacji | Następny krok |
| --- | --- |
| zdefiniowana, możliwa, wymagana | validate_information; case_status = awaiting_validation |
| zakończona i zmieniająca podstawę | ponowna kwalifikacja kandydatów; rerun może być legalny |
| zakończona bez nowej informacji | brak prawa do rerun z validation_completed |
| niemożliwa, a niezbędna | stop_blocked albo human_decision_gate zgodnie z przyczyną |
| failed_technical | błąd techniczny; brak zmiany klasy lub wyniku biznesowego |

## 10. Wykrywanie cykli

| cycle_type | Znaczenie |
| --- | --- |
| exact_repeat | ponowienie identycznej sygnatury bez nowej podstawy |
| closed_loop_no_new_information | powrót do wcześniejszego węzła bez nowej informacji |
| validation_loop | pętla z walidacją; legalna tylko po zmianie podstawy |
| branch_loop | gałęzie odsyłają się wzajemnie bez rozstrzygającego wkładu |
| unknown | wykryto powtarzalność, ale nie można odpowiedzialnie sklasyfikować typu |

| Pole | Reguła |
| --- | --- |
| cycle_detected | true po wykryciu powrotu do istniejącej sygnatury lub zamkniętego łańcucha |
| cycle_type | wartość z katalogu zamkniętego |
| cycle_basis | lista kroków, sygnatur i wersji wykazująca pętlę |
| cycle_resolution | stop duplicate, stop no_new_information, validate, human gate albo legal continuation po nowej wersji |

## 11. Wartość dodatkowej informacji bez wyniku punktowego

| information_contribution_status | Znaczenie |
| --- | --- |
| changes_route | wynik może zmienić wybór dalszej trasy |
| resolves_gap | wynik może rozwiązać wymaganą lukę |
| narrows_claim | wynik może odpowiedzialnie zawęzić twierdzenie |
| tests_mechanism | wynik może potwierdzić lub obalić mechanizm zgodnie z metodologią |
| distinguishes_alternatives | wynik może odróżnić konkurencyjne wyjaśnienia |
| supporting_only | wynik może jedynie dodać wsparcie do już wystarczającej odpowiedzi |
| duplicate | wynik dubluje istniejące wykonanie lub informację |
| no_new_information | wynik nie może zmienić celu, luki, twierdzenia ani trasy |
| not_assessable | brak podstaw do odpowiedzialnej oceny wkładu |

| Pole | Kontrakt |
| --- | --- |
| additional_information_needed | true tylko wtedy, gdy pozostał konkretny nierozstrzygnięty cel |
| additional_information_basis | wyjaśnia, co następny krok może rozstrzygnąć |
| information_contribution_status | jedna wartość z katalogu; nie jest wynikiem punktowym |

> **GRANICA KONTYNUACJI supporting_only, duplicate i no_new_information nie wymuszają kolejnego testu. Dalszy krok musi mieć rolę rozstrzygającą względem bieżącego celu, luki, zakresu albo mechanizmu.**

## 12. Warunki zatrzymania

| stop_reason | Znaczenie |
| --- | --- |
| diagnostic_question_answered | pytanie zostało odpowiedziane w wymaganym zakresie |
| mechanism_sufficiently_supported | cel wymagał mechanizmu i nie pozostała rozstrzygająca walidacja ani test |
| no_adverse_signal_for_scope | brak niekorzystnego sygnału potwierdzony wyłącznie dla badanego zakresu |
| validation_required_before_continuation | dalszy krok zależy od zdefiniowanej walidacji |
| insufficient_information | brak wymaganej informacji uniemożliwia odpowiedź |
| no_applicable_next_test | brak legalnego kandydata; skutek zależy od statusu celu |
| duplicate_path | jedyna dalsza trasa byłaby duplikatem |
| scope_exhausted | wyczerpano odpowiedzialnie dostępny zakres diagnozy |
| human_decision_required | dalszy wybór przekracza granicę diagnozy albo wymaga decyzji zarządczej |
| monitoring_only | obecnie uzasadniona jest wyłącznie obserwacja |
| technical_blocker | konieczny krok jest technicznie niewykonalny |

| Akcja | Warunek deterministyczny | case_status |
| --- | --- | --- |
| stop_completed | diagnostic_objective_status = answered albo odpowiedzialnie potwierdzony no_adverse_signal_for_scope; brak wymaganej walidacji i rozstrzygającego kandydata | completed |
| stop_blocked | required information/evidence nieosiągalne, nierozwiązany konflikt, techniczna niemożność koniecznego kroku albo brak legalnej ścieżki do odpowiedzi | blocked |
| validate_information | walidacja jest wymagana, zdefiniowana i możliwa | awaiting_validation |
| human_decision_gate | dalszy wybór wymaga człowieka | awaiting_human_decision |
| observe | PRI-01 wskazuje obserwację, a obecnie brak podstawy do dalszej diagnozy | paused_monitoring albo completed zależnie od objective |

> **BRAK NASTĘPNEGO TESTU no_applicable_next_test prowadzi do completed tylko przy answered. Przy unanswered lub partially_answered prowadzi do blocked albo human_decision_gate, zależnie od przyczyny. stop_completed i stop_blocked nigdy nie są równoważne.**

### 12.1. Wystarczająco potwierdzony mechanizm

mechanism_sufficiently_supported nie używa globalnego progu pewności. Jest dopuszczalne tylko wtedy, gdy cel sprawy wymaga identyfikacji mechanizmu, CONF-01 nie wskazuje krytycznej blokady, wszystkie required validations są zakończone, a żaden kandydat nie ma uzasadnionej roli rozstrzygającej. well_supported finding nie wystarcza, jeżeli cel dotyczy mechanizmu.

## 13. Brama decyzji człowieka

| human_decision_type | Znaczenie |
| --- | --- |
| management_action | wybór działania wykonawczego |
| scope_choice | wybór zakresu diagnozy lub decyzji |
| route_choice | wybór między legalnymi, nieporównywalnymi trasami |
| materiality_choice | ustalenie istotności biznesowej, której brak w kontrakcie globalnym |
| policy_choice | wybór polityki organizacyjnej potrzebnej do dalszej oceny |
| risk_acceptance | akceptacja ryzyka lub ograniczenia informacji |
| other_governance_choice | inny jawny wybór właściciela zarządczego |

| Pole | Kontrakt |
| --- | --- |
| human_decision_gate_required | true, gdy wybór przekracza legalną granicę reguł ORCH-01 |
| human_decision_type | jedna wartość z katalogu zamkniętego |
| human_decision_basis | konkretna przyczyna, której system nie może odpowiedzialnie rozstrzygnąć |
| human_decision_options | jawne legalne opcje bez sugerowania wykonawczej rekomendacji |
| human_decision_context | wyniki, ograniczenia, konflikty i konsekwencje diagnostyczne potrzebne człowiekowi |

> **HUMAN GATE NIE JEST OBEJŚCIEM Brama decyzji człowieka nie ukrywa niekompletnej metodologii. Musi wskazać konkretny wybór: działanie, zakres, trasę, istotność, politykę albo akceptację ryzyka. Nie zawiera rekomendacji wykonawczej.**

### 13.1. Rekord decyzji człowieka

| Pole | Kontrakt |
| --- | --- |
| human_decision_id | jednoznaczny identyfikator decyzji powiązany z bramą i sprawą |
| human_decision_status | pending; resolved; declined; cancelled |
| human_decision_selected_option | opcja wybrana z human_decision_options albo jawna zmiana zakresu/kontekstu |
| human_decision_result_basis | źródłowy zapis wyboru bez oceny, czy decyzja była dobra |
| human_decision_version | wersja rekordu decyzji; późniejsza zmiana nie nadpisuje poprzedniej |
| human_decision_at | znacznik czasu zarejestrowania decyzji |
| human_decision_effect | resume_diagnosis; create_branch; create_derived_case; cancel_branch; close_diagnostic_case; no_route_change |

| human_decision_status | Znaczenie |
| --- | --- |
| pending | brama oczekuje na wybór |
| resolved | wybór został jawnie dokonany i może zostać zastosowany jako nowe wejście |
| declined | człowiek odmówił wyboru; ścieżka nie zakłada opcji domyślnej |
| cancelled | rekord decyzji został anulowany z zachowaniem historii |

| human_decision_effect | Skutek rejestrowany przez ORCH-01 |
| --- | --- |
| resume_diagnosis | ponowna kwalifikacja bieżącej sprawy na nowym kroku |
| create_branch | utworzenie nowej gałęzi zgodnej z wyborem |
| create_derived_case | utworzenie sprawy pochodnej dla zmienionego zakresu lub kontekstu |
| cancel_branch | anulowanie wskazanej gałęzi bez usuwania historii |
| close_diagnostic_case | zamknięcie sprawy po osiągnięciu celu diagnostycznego |
| no_route_change | zapis decyzji bez zmiany aktualnej trasy |

human_decision_selected_option musi pochodzić z human_decision_options. Wyjątek dotyczy jawnej zmiany zakresu lub utworzenia nowego kontekstu; wtedy powstaje nowa wersja decyzji, nowa gałąź albo derived_case_id. ORCH-01 nie ocenia jakości wyboru zarządczego i nie wykonuje wybranego działania. Rejestruje decyzję jako nowe wejście do ścieżki.

### 13.2. Powrót z awaiting_human_decision

| Pole | Kontrakt |
| --- | --- |
| human_decision_resume_allowed | true tylko dla rozwiązanej decyzji, której skutek legalnie wznawia diagnozę |
| human_decision_resume_basis | odwołanie do wersjonowanej decyzji, jej efektu i aktualnej podstawy ścieżki |
| human_decision_resume_step_id | nowy diagnostic_step_id utworzony po decyzji człowieka |

| Kolejność | Reguła wznowienia |
| --- | --- |
| 1 | zapisz rozwiązaną decyzję jako nowe wersjonowane wejście |
| 2 | utwórz nowy diagnostic_step_id; nie nadpisuj kroku human_decision_gate |
| 3 | odczytaj aktualne MGT-01, PRI-01, CONF-01 i next_tests |
| 4 | ponownie utwórz oraz zakwalifikuj kandydatów |
| 5 | nie wracaj automatycznie do kandydata wybranego przed bramą |
| 6 | zapisz awaiting_human_decision → in_progress, jeżeli przejście jest legalne |

> **WARUNEK WZNOWIENIA human_decision_status = resolved i human_decision_effect = resume_diagnosis pozwalają na wznowienie dopiero po zapisaniu decyzji, utworzeniu nowego kroku i ponownej kwalifikacji na aktualnych wejściach.**

## 14. Gałęzie, scalanie i grupy wpływu

| merge_result_status | Reguła |
| --- | --- |
| merged_consistent | wyniki mogą zasilać wspólną odpowiedź bez uśredniania |
| merged_with_limitations | wyniki są zgodne kierunkowo, ale ograniczenia pozostają jawne |
| contradictory | sprzeczność pozostaje jawna i prowadzi do CONF/MGT, walidacji albo bramy człowieka |
| waiting | nie spełniono merge_condition |
| not_applicable | gałęzie nie powinny zostać scalone |

| Pole | Kontrakt |
| --- | --- |
| merge_group_id | identyfikator grupy gałęzi |
| merge_condition | warunek semantyczny umożliwiający scalenie |
| merge_basis | podstawa zgodności, ograniczeń albo sprzeczności |
| merge_result_status | wartość z katalogu zamkniętego |
| finding_cluster_id / impact_group_id | dziedziczone z PRI-01; wspólna ścieżka nie oznacza wspólnej przyczyny i nie przelicza wpływu |

Blokada jednej gałęzi nie zatrzymuje automatycznie całej sprawy. Jeżeli inna gałąź może legalnie dostarczyć potrzebnej informacji, case_status pozostaje in_progress, a zablokowana gałąź zachowuje branch_status = blocked.

### 14.1. Anulowanie i zmiana zakresu

| branch_cancellation_reason | Znaczenie |
| --- | --- |
| duplicate | gałąź dubluje istniejącą trasę |
| superseded_by_upstream_result | nowy wynik nadrzędny usunął jej rolę |
| no_longer_relevant | nie odpowiada już bieżącemu celowi |
| human_decision | człowiek wybrał inną legalną trasę |
| scope_changed | zmiana zakresu wymaga nowej gałęzi albo sprawy pochodnej |

Zmiana zakresu lub okresu, która istotnie zmienia pytanie diagnostyczne, tworzy nową gałąź albo derived_case_id z derived_case_basis. Nie nadpisuje poprzedniej historii.

Jeżeli człowiek wybiera jedną z kilku legalnych tras, wybrana gałąź otrzymuje branch_status = active albo powstaje nowa gałąź. Pozostałe gałęzie mogą otrzymać branch_status = cancelled i branch_cancellation_reason = human_decision. Każda anulowana gałąź oraz wszystkie jej dotychczasowe kroki pozostają w historii przebiegu.

## 15. Zasady współdziałania PRI-01, CONF-01 i MGT-01

| Sytuacja wejściowa | Działanie ORCH-01 | Zakaz |
| --- | --- | --- |
| management_attention_route = validate_first | najpierw legalna walidacja MGT/CONF; po niej ponowna kwalifikacja i ewentualny rerun | brak zależnego testu przed walidacją |
| review_and_validate_in_parallel | równolegle tylko z testem niezależnym od brakującej informacji | brak decyzji wykonawczej równolegle do walidacji |
| problem_priority_action = review_now | pierwszeństwo uwagi; każdy kandydat nadal przechodzi bramy | brak „uruchom wszystko” |
| problem_priority_action = observe | paused_monitoring albo completed zgodnie z celem i podstawą | brak testowania mechanizmu bez końca |
| finding well_supported; mechanism weak/not_assessable | kontynuacja tylko jeżeli cel dotyczy mechanizmu i istnieje rozstrzygający krok | brak automatycznego stop albo nieskończonego testowania |
| confidence_conflict_status = unresolved | resolve_data_conflict albo blokada zgodnie z CONF-01 | brak głosowania większości testów |
| critical_information_gap dla bieżącego kroku | walidacja ma pierwszeństwo | brak zastępczego assumption |
| kilka confidence_validation_actions | sekwencja albo równoległość według zależności i PRI-01 | ORCH nie nadaje własnego priorytetu |

## 16. Historia, wersjonowanie i idempotencja

| Pole kroku | Kontrakt |
| --- | --- |
| diagnostic_step_id | jednoznaczny identyfikator kroku |
| previous_step_id | poprzedni krok albo jawny start |
| orchestration_action | wybrana akcja z katalogu |
| step_input_refs | wersjonowane odwołania do wejść |
| step_output_refs | odwołania do wyników lub rekordów walidacji |
| route_candidate_ids | wszyscy rozważeni kandydaci |
| selected_route_candidate_id | wybrany kandydat albo null przy zatrzymaniu bez kandydata |
| orchestration_rule_id | identyfikator zastosowanej reguły |
| orchestration_basis | audytowalne uzasadnienie decyzji |
| step_created_at | znacznik utworzenia |
| step_status | wartość z katalogu zamkniętego |

| Pole wersji / odtwarzalności | Reguła |
| --- | --- |
| orchestration_decision_signature | deterministyczny zapis wejść, reguł, historii i wyniku decyzji |
| idempotent_replay_status | same_decision; different_due_to_version_change; conflict; not_assessable |
| orchestration_rule_version | wersja konkretnego zbioru reguł |
| orchestration_contract_version | wersja całego kontraktu ORCH-01 |
| data_version | merytoryczna wersja danych |
| evidence_version | wersja podstawy dowodowej |
| source_version_change_basis | podstawa uznania zmiany za merytoryczną |

> **IDEMPOTENCJA Identyczne wejście, wersje reguł i stan historii muszą zwrócić tę samą decyzję routingową. Zmiana orchestration_rule_version może zmienić nową decyzję, ale nie zmienia historii starej sprawy.**

### 16.1. Awaria techniczna

step_status = failed_technical oznacza błąd wykonania. Nie jest TEST_BLOCKED z przyczyn merytorycznych, not_assessable, niekorzystnym wynikiem ani zmianą pewności. Techniczna awaria walidacji nie tworzy validation_completed i nie legalizuje rerun.

ORCH-01 określa kolejność logiczną. Nie projektuje workerów, kolejek, cronów, technicznego SLA, timeoutów ani harmonogramowania zasobów obliczeniowych. AI nie jest wymagane do routingu.

## 17. Minimalny graf zależności

| Pole krawędzi | Kontrakt |
| --- | --- |
| route_edge_id | jednoznaczny identyfikator |
| from_node_id / to_node_id | węzeł źródłowy i docelowy |
| edge_type | diagnostic; validation; rerun; merge; human_gate; stop |
| edge_trigger | semantyczny warunek ze źródłowej metodologii, nie kolor interfejsu ani arbitralny próg |
| edge_required_conditions | warunki konieczne przejścia |
| edge_blocking_conditions | warunki zabraniające przejścia |
| edge_basis | źródło i uzasadnienie krawędzi |
| edge_status | candidate; qualified; blocked; traversed; inactive |

| node_type | Rola |
| --- | --- |
| test | test Core 10 |
| validation | walidacja MGT-01 lub CONF-01 |
| claim | twierdzenie oceniane przez CONF-01 |
| finding | wynik testu źródłowego |
| human_gate | jawny wybór człowieka |
| stop | stan zatrzymania ścieżki |

Graf obejmuje wyłącznie zależności potrzebne do prowadzenia ścieżki. Nie modeluje wszystkich zależności organizacji ani technicznych czynności wykonawczych.

## 18. Kontrakt wyjścia ORCH-01

| Pole | Reguła |
| --- | --- |
| diagnostic_case_id | tożsamość sprawy |
| case_status | stan całej sprawy |
| diagnostic_objective_status | stopień odpowiedzi na cel |
| selected_orchestration_action | wybrana akcja |
| selected_route_target | test, walidacja, brama, obserwacja lub stop |
| selected_route_basis | audytowalne uzasadnienie |
| selected_route_candidate_id | wybrany kandydat, jeśli dotyczy |
| next_steps | następne kroki logiczne bez rekomendacji wykonawczej |
| selected_route_candidate_ids | uporządkowany zbiór unikalnych kandydatów wybranych do wykonania |
| selected_route_targets | uporządkowany zbiór celów wybranych tras |
| selected_route_edge_ids | uporządkowany zbiór krawędzi grafu wybranych tras |
| stop_reason | powód zatrzymania, jeśli dotyczy |
| human_decision_gate_required | czy wymagany jest człowiek |
| human_decision_type | typ wyboru człowieka, jeśli dotyczy |
| orchestration_summary | krótkie uzasadnienie w języku polskim |
| path_history_ref | odwołanie do pełnej historii przebiegu |

> **WZORZEC KOMUNIKATU [ŚCIEŻKA DIAGNOSTYCZNA] Sprawa [diagnostic_case_id] dotyczy [diagnostic_question]. Ostatni krok wykazał [finding / information status]. Priorytet uwagi: [problem_priority_action], priorytet walidacji: [validation_priority_action], pewność wyniku: [finding_confidence_class], pewność mechanizmu: [mechanism_confidence_class]. Następny krok: [orchestration_action] → [target], ponieważ [basis]. Dalsze testowanie jest [uzasadnione / nieuzasadnione] z powodu [additional_information_basis]. Jeżeli wymagane: decyzja człowieka dotyczy [human_decision_type].**

## 19. Deterministyczny mechanizm decyzji ORCH

| Reguła | Warunek | Wynik |
| --- | --- | --- |
| ORCH-R01 | brak jawnego diagnostic_question albo case_scope/case_period | blocked albo doprecyzowanie przez human gate; brak arbitralnego testu |
| ORCH-R02 | istnieje required validation blokująca wybranego kandydata | validate_information; awaiting_validation |
| ORCH-R03 | kandydat przekracza granicę diagnozy | human_decision_gate |
| ORCH-R04 | route_signature została wykonana bez zmiany podstawy | duplicate; brak rerun |
| ORCH-R05 | kandydaci mają zależność ustalającą zakres lub sens | sequential |
| ORCH-R06 | kandydaci niezależni, bez wspólnej walidacji i dublowania | parallel może być dozwolone |
| ORCH-R07 | PRI porządkuje porównywalnych kandydatów | respektuj next_test_priority_order |
| ORCH-R08 | kandydaci tied/incomparable | parallel, waiting albo route_choice; brak własnego rankingu |
| ORCH-R09 | objective answered i brak rozstrzygającego kandydata | stop_completed |
| ORCH-R10 | objective unanswered i brak legalnego kandydata | stop_blocked albo human_decision_gate |
| ORCH-R11 | PRI = observe i brak obecnej wartości dalszego testu | paused_monitoring albo completed |
| ORCH-R12 | failed_technical | status techniczny bez interpretacji biznesowej |
| ORCH-R13 | run_parallel_tests wybrano dla wielu kandydatów | wypełnij zbiory wyboru; pola pojedyncze pozostaw null/not_used_in_parallel |
| ORCH-R14 | human_decision_status = resolved i effect = resume_diagnosis | nowy krok, aktualne wejścia i ponowna kwalifikacja |
| ORCH-R15 | case_status = completed albo cancelled i pojawia się nowe zdarzenie | nowa sprawa albo derived_case_id; brak wznowienia tej wersji |
| ORCH-R16 | case_status = blocked i podstawa uległa jawnej zmianie | nowy krok i ponowna kwalifikacja z zachowaniem historii |

## 20. Scenariusze testowe ORCH01-T

Każdy scenariusz wymaga jawnego wejścia, oczekiwanego prowadzenia ścieżki, statusu sprawy i zakazu zachowania niepożądanego. Sam poprawny opis użytkowy bez zgodnego rekordu i historii nie wystarcza.

| ID | Scenariusz / wejście | Oczekiwane prowadzenie i status | Wynik |
| --- | --- | --- | --- |
| ORCH01-T01 | Manualne pytanie o spadek rentowności | Prawidłowe mapowanie do kandydatów finansowych bez uruchamiania wszystkich Core 10. | PASS |
| ORCH01-T02 | Adverse finding FIN-02 z legalnym next_tests | Kandydaci pochodzą z next_tests; ORCH nie dodaje własnego testu. | PASS |
| ORCH01-T03 | FIN-03 weakly_supported przez brak porównywalności | validate_information przed CAP/HR, jeżeli PRI/CONF wymagają validate_first. | PASS |
| ORCH01-T04 | Walidacja porównywalności zakończona | rerun FIN-03 legalny z repeat_test_reason=validation_completed. | PASS |
| ORCH01-T05 | Rerun bez zmiany danych lub evidence | duplicate_execution_flag=true; rerun zabroniony. | PASS |
| ORCH01-T06 | Dwa niezależne next_tests bez zależności | run_parallel_tests dopuszczalne przy jawnej parallel_execution_basis. | PASS |
| ORCH01-T07 | Drugi test zależy od scope ustalonego przez pierwszy | execution_mode=sequential. | PASS |
| ORCH01-T08 | Trzy next_tests, ale wszystkie zależą od tej samej krytycznej luki | najpierw jedna walidacja; brak trzech bezsensownych testów. | PASS |
| ORCH01-T09 | PRI review_now, CONF well_supported | ORCH nadal przechodzi candidate gates; brak automatycznego uruchomienia wszystkich testów. | PASS |
| ORCH01-T10 | PRI review_now, CONF weakly_supported, validate_now | walidacja przed dalszą ścieżką albo równolegle tylko zgodnie z PRI. | PASS |
| ORCH01-T11 | PRI observe, dobrze potwierdzony brak adverse signal | paused_monitoring albo stop_completed; brak dalszego testowania. | PASS |
| ORCH01-T12 | Finding well_supported, mechanism weakly_supported, objective=mechanism | ścieżka trwa do testu mechanizmu lub walidacji. | PASS |
| ORCH01-T13 | Finding well_supported, objective tylko wykrycie zjawiska | stop_completed możliwe bez wymuszonej analizy mechanizmu. | PASS |
| ORCH01-T14 | MGT decision_blocked przez required gap | awaiting_validation; brak run_test zależnego od luki. | PASS |
| ORCH01-T15 | CONF unresolved required conflict | resolve_data_conflict albo blocked, bez głosowania większościowego. | PASS |
| ORCH01-T16 | Dwie gałęzie prowadzą do tego samego testu i tego samego route_signature | jedno wykonanie przypisane do obu gałęzi. | PASS |
| ORCH01-T17 | Dwie gałęzie prowadzą do tego samego testu, ale różny scope | dwa odrębne wykonania lub jawna gałąź; brak błędnej deduplikacji. | PASS |
| ORCH01-T18 | Jedna gałąź blocked, druga ma legalny next_test | case pozostaje in_progress. | PASS |
| ORCH01-T19 | Parallel branches zwracają zgodne wyniki | merge_branches=merged_consistent; bez uśredniania. | PASS |
| ORCH01-T20 | Parallel branches zwracają sprzeczne wyniki | merge_result_status=contradictory; route do CONF/MGT/validation. | PASS |
| ORCH01-T21 | FIN-01, FIN-02, FIN-03 wskazują ten sam impact_group | jedna ścieżka ekonomiczna; brak potrójnego liczenia wpływu. | PASS |
| ORCH01-T22 | Kandydat może tylko dodać supporting evidence | jeżeli objective już answered – stop zamiast testu. | PASS |
| ORCH01-T23 | Kandydat może odróżnić dwa konkurencyjne mechanizmy | candidate_diagnostic_value_gate=pass; test uzasadniony. | PASS |
| ORCH01-T24 | Brak applicable next_test, objective answered | stop_completed. | PASS |
| ORCH01-T25 | Brak applicable next_test, objective unanswered | stop_blocked albo human gate – nie completed. | PASS |
| ORCH01-T26 | Następny krok to decyzja o zatrudnieniu | human_decision_gate; ORCH nie rekomenduje zatrudnienia. | PASS |
| ORCH01-T27 | Dwa legalne, nieporównywalne i nierównoległe kierunki | human_decision_gate typu route_choice. | PASS |
| ORCH01-T28 | Zmiana business materiality potrzebna do dalszej ścieżki | human_decision_gate typu materiality_choice. | PASS |
| ORCH01-T29 | Pętla FIN-03 → CAP-01 → FIN-03 bez nowych danych | cycle_detected=closed_loop_no_new_information; stop. | PASS |
| ORCH01-T30 | Pętla FIN-03 → validation → FIN-03 z nową wersją danych | legalna pętla; brak cycle error. | PASS |
| ORCH01-T31 | Test wykonany technicznie nieudanie | step_status=failed_technical; brak merytorycznej interpretacji. | PASS |
| ORCH01-T32 | Validation action technicznie nieudana | case nie otrzymuje fałszywej confidence; pozostaje awaiting_validation/blocked technical. | PASS |
| ORCH01-T33 | Zmiana period po kwartale | nowa route_signature; rerun legalny z period_changed. | PASS |
| ORCH01-T34 | Zmiana scope na inną jednostkę | nowa gałąź lub derived case, bez nadpisania starej historii. | PASS |
| ORCH01-T35 | Nowy upstream result zmienia mechanizm | rerun downstream legalny z upstream_result_changed. | PASS |
| ORCH01-T36 | No adverse signal przy słabym coverage | brak stop_completed jako „problemu nie ma”; route zgodny z CONF/MGT. | PASS |
| ORCH01-T37 | No adverse signal przy pełnej podstawie i objective=detect signal | stop_completed dla badanego scope. | PASS |
| ORCH01-T38 | Trzy testy korzystają z tego samego źródła i zwracają zgodne wyniki | ORCH nie interpretuje liczby testów jako niezależnego potwierdzenia. | PASS |
| ORCH01-T39 | Jedna gałąź daje dobrze potwierdzony mechanizm; drugi kandydat jest duplikatem / wyłącznie dowodem wspierającym | zatrzymanie ścieżki zamiast kolejnego testowania. | PASS |
| ORCH01-T40 | validation_priority_action=validate_when_needed i current route nie zależy od tej luki | kontynuacja legalnego testu; brak przedwczesnej walidacji. | PASS |
| ORCH01-T41 | review_and_validate_in_parallel i test nie zależy od brakującej informacji | parallel dozwolone bez decyzji wykonawczej. | PASS |
| ORCH01-T42 | review_and_validate_in_parallel, ale test zależy od brakującej informacji | parallel zabronione; validate first. | PASS |
| ORCH01-T43 | priority_order tied, kandydaci niezależni | parallel lub human gate według warunków; brak własnego rankingu. | PASS |
| ORCH01-T44 | priority_order incomparable, kandydaci niezależni | parallel możliwe, ale bez sztucznej kolejności. | PASS |
| ORCH01-T45 | Identyczne wejście i ta sama wersja reguł | idempotent_replay_status potwierdza tę samą decyzję ORCH. | PASS |
| ORCH01-T46 | Zmiana orchestration_rule_version | nowa decyzja może się różnić, ale stara historia pozostaje odtwarzalna. | PASS |
| ORCH01-T47 | Pytanie typu unknown_or_cross_domain z wejścia ręcznego | brak arbitralnego wyboru testu; MGT/doprecyzowanie albo legalne gałęzie. | PASS |
| ORCH01-T48 | Luka informacyjna jako entry_trigger | ścieżka może rozpocząć się od walidacji bez pierwszego testu Core 10. | PASS |
| ORCH01-T49 | Sygnał powtarzalny jako entry_trigger | nowa sprawa/review opiera się na bieżącej wersji danych i zachowuje historię poprzedniej. | PASS |
| ORCH01-T50 | Firma syntetyczna – pełny przebieg | system przechodzi kilka testów, walidację, PRI, CONF, nie wpada w pętlę, zatrzymuje się w poprawnym miejscu i przekazuje human gate bez rekomendacji wykonawczej. | PASS |
| ORCH01-T51 | Trzy testy równoległe | Trzy niezależne zakwalifikowane testy tworzą run_parallel_tests; selected_route_candidate_ids ma dokładnie trzy unikalne elementy we wspólnym parallel_group_id; brak sztucznego kandydata głównego. | PASS |
| ORCH01-T52 | Wybór trasy przez człowieka i wznowienie | Dwie nieporównywalne nierównoległe trasy prowadzą do awaiting_human_decision. Rozwiązana decyzja ma human_decision_id i effect=resume_diagnosis; powstaje nowy krok, ponowna kwalifikacja i niezmieniona historia. | PASS |
| ORCH01-T53 | Management action kończy diagnozę, nie wykonuje działania | ORCH zapisuje wybór człowieka, nie wykonuje działania, a po osiągnięciu celu może zapisać human_decision_effect=close_diagnostic_case. | PASS |
| ORCH01-T54 | Completed nie jest wznawiany | Nowy okres lub sygnał nie powoduje completed → in_progress; powstaje nowa sprawa albo derived_case_id. | PASS |
| ORCH01-T55 | Powrót po walidacji | Skuteczna walidacja zmienia podstawę i pozwala na awaiting_validation → in_progress oraz ponowną kwalifikację kandydatów bez zmiany historii poprzednich kroków. | PASS |

## 21. Walidacja ORCH01-VAL

Kontrole walidacyjne obejmują kontrakty sprawy, gałęzi i kroku, wejścia źródłowe, kwalifikację kandydatów, przebieg, zatrzymanie, historię, graf oraz komunikację.

| ID | Kontrola | Wynik |
| --- | --- | --- |
| ORCH01-VAL-01 | diagnostic_case_id jest obecny i jednoznaczny | PASS |
| ORCH01-VAL-02 | diagnostic_question jest jawne | PASS |
| ORCH01-VAL-03 | decision_context jest jawny | PASS |
| ORCH01-VAL-04 | case_scope jest jawny | PASS |
| ORCH01-VAL-05 | case_period jest jawny | PASS |
| ORCH01-VAL-06 | case_version jest jawna | PASS |
| ORCH01-VAL-07 | case_created_at jest jawny | PASS |
| ORCH01-VAL-08 | case_status należy do katalogu | PASS |
| ORCH01-VAL-09 | entry_trigger należy do katalogu | PASS |
| ORCH01-VAL-10 | entry_trigger_basis jest obecna | PASS |
| ORCH01-VAL-11 | diagnostic_objective jest jawny | PASS |
| ORCH01-VAL-12 | diagnostic_objective_status należy do katalogu | PASS |
| ORCH01-VAL-13 | diagnostic_objective_basis jest obecna | PASS |
| ORCH01-VAL-14 | route_scope jest jawny | PASS |
| ORCH01-VAL-15 | route_period jest jawny | PASS |
| ORCH01-VAL-16 | route_scope_basis jest obecna | PASS |
| ORCH01-VAL-17 | route_period_basis jest obecna | PASS |
| ORCH01-VAL-18 | diagnostic_branch_id jest jednoznaczny | PASS |
| ORCH01-VAL-19 | parent_branch_id jest poprawny albo null | PASS |
| ORCH01-VAL-20 | branch_status należy do katalogu | PASS |
| ORCH01-VAL-21 | branch_question jest jawne | PASS |
| ORCH01-VAL-22 | branch_target_claim jest jawny, gdy dotyczy | PASS |
| ORCH01-VAL-23 | branch_dependency_status jest jawny | PASS |
| ORCH01-VAL-24 | diagnostic_step_id jest jednoznaczny | PASS |
| ORCH01-VAL-25 | previous_step_id istnieje albo krok ma jawny start | PASS |
| ORCH01-VAL-26 | orchestration_action należy do katalogu | PASS |
| ORCH01-VAL-27 | step_status należy do katalogu | PASS |
| ORCH01-VAL-28 | failed_technical pozostaje statusem technicznym | PASS |
| ORCH01-VAL-29 | wejście Core 10 zachowuje test_id i finding_id | PASS |
| ORCH01-VAL-30 | next_tests są odczytane bez automatycznego uruchomienia | PASS |
| ORCH01-VAL-31 | wejście MGT zachowuje decision_information_status | PASS |
| ORCH01-VAL-32 | critical_information_gap jest respektowana dla zależnego kroku | PASS |
| ORCH01-VAL-33 | reconciliation_status i data_conflict_flag są zachowane | PASS |
| ORCH01-VAL-34 | wejście PRI zachowuje problem_priority_action | PASS |
| ORCH01-VAL-35 | validation_priority_action jest zachowane | PASS |
| ORCH01-VAL-36 | management_attention_route jest zachowane | PASS |
| ORCH01-VAL-37 | next_test_priority_order ma next_test_priority_basis | PASS |
| ORCH01-VAL-38 | tied i incomparable nie otrzymują własnego rankingu | PASS |
| ORCH01-VAL-39 | wejście CONF zachowuje finding_confidence_class | PASS |
| ORCH01-VAL-40 | mechanism_confidence_class pozostaje odrębna | PASS |
| ORCH01-VAL-41 | confidence_validation_required jest respektowane | PASS |
| ORCH01-VAL-42 | confidence_validation_actions nie są rozszerzane | PASS |
| ORCH01-VAL-43 | confidence_conflict_status jest respektowany | PASS |
| ORCH01-VAL-44 | critical_confidence_limitation_flag jest respektowany | PASS |
| ORCH01-VAL-45 | route_candidate_id jest obecny | PASS |
| ORCH01-VAL-46 | route_candidate_type należy do katalogu | PASS |
| ORCH01-VAL-47 | route_candidate_target jest jawny | PASS |
| ORCH01-VAL-48 | route_candidate_target_id jest jawny | PASS |
| ORCH01-VAL-49 | route_candidate_source jest legalny | PASS |
| ORCH01-VAL-50 | route_candidate_basis jest obecna | PASS |
| ORCH01-VAL-51 | route_candidate_status należy do katalogu | PASS |
| ORCH01-VAL-52 | candidate_applicability_gate jest oceniona | PASS |
| ORCH01-VAL-53 | candidate_information_gate jest oceniona | PASS |
| ORCH01-VAL-54 | candidate_scope_period_gate jest oceniona | PASS |
| ORCH01-VAL-55 | candidate_duplication_gate jest oceniona | PASS |
| ORCH01-VAL-56 | candidate_dependency_gate jest oceniona | PASS |
| ORCH01-VAL-57 | candidate_diagnostic_value_gate jest oceniona | PASS |
| ORCH01-VAL-58 | candidate_human_boundary_gate jest oceniona | PASS |
| ORCH01-VAL-59 | kandydat z fail nie otrzymuje selected | PASS |
| ORCH01-VAL-60 | kandydat not_assessable nie otrzymuje selected | PASS |
| ORCH01-VAL-61 | route_signature obejmuje target | PASS |
| ORCH01-VAL-62 | route_signature obejmuje scope i period | PASS |
| ORCH01-VAL-63 | route_signature obejmuje data_version i evidence_version | PASS |
| ORCH01-VAL-64 | route_signature obejmuje objective albo claim | PASS |
| ORCH01-VAL-65 | duplicate_execution_flag jest deterministyczny | PASS |
| ORCH01-VAL-66 | duplicate_execution_basis wskazuje istniejące wykonanie | PASS |
| ORCH01-VAL-67 | execution_mode należy do katalogu | PASS |
| ORCH01-VAL-68 | sequential ma sequential_dependency_basis | PASS |
| ORCH01-VAL-69 | parallel ma parallel_execution_allowed = true | PASS |
| ORCH01-VAL-70 | parallel ma parallel_execution_basis | PASS |
| ORCH01-VAL-71 | parallel ma parallel_group_id | PASS |
| ORCH01-VAL-72 | parallel nie omija wspólnej required validation | PASS |
| ORCH01-VAL-73 | route_order_source jest jawne | PASS |
| ORCH01-VAL-74 | route_order_status jest jawny | PASS |
| ORCH01-VAL-75 | repeat_test_allowed jest logiczne | PASS |
| ORCH01-VAL-76 | rerun_test ma repeat_test_reason | PASS |
| ORCH01-VAL-77 | repeat_test_reason należy do katalogu | PASS |
| ORCH01-VAL-78 | repeat_test_previous_execution_id jest obecny | PASS |
| ORCH01-VAL-79 | zmiana wersji ma source_version_change_basis | PASS |
| ORCH01-VAL-80 | brak nowej podstawy blokuje rerun | PASS |
| ORCH01-VAL-81 | cycle_detected jest logiczne | PASS |
| ORCH01-VAL-82 | cycle_type należy do katalogu | PASS |
| ORCH01-VAL-83 | cycle_basis wskazuje ścieżkę | PASS |
| ORCH01-VAL-84 | cycle_resolution jest jawne | PASS |
| ORCH01-VAL-85 | exact_repeat jest zatrzymany | PASS |
| ORCH01-VAL-86 | validation_loop wymaga nowej wersji podstawy | PASS |
| ORCH01-VAL-87 | additional_information_needed jest logiczne | PASS |
| ORCH01-VAL-88 | additional_information_basis jest jawna | PASS |
| ORCH01-VAL-89 | information_contribution_status należy do katalogu | PASS |
| ORCH01-VAL-90 | supporting_only nie wymusza testu | PASS |
| ORCH01-VAL-91 | duplicate nie wymusza testu | PASS |
| ORCH01-VAL-92 | no_new_information nie wymusza testu | PASS |
| ORCH01-VAL-93 | stop_reason należy do katalogu | PASS |
| ORCH01-VAL-94 | stop_completed wymaga answered albo pełnej podstawy no adverse signal | PASS |
| ORCH01-VAL-95 | stop_blocked nie jest sukcesem diagnozy | PASS |
| ORCH01-VAL-96 | awaiting_validation jest użyte przy możliwej walidacji | PASS |
| ORCH01-VAL-97 | paused_monitoring jest zgodne z objective | PASS |
| ORCH01-VAL-98 | human_decision_gate_required jest logiczne | PASS |
| ORCH01-VAL-99 | human_decision_type należy do katalogu | PASS |
| ORCH01-VAL-100 | human_decision_basis jest obecna | PASS |
| ORCH01-VAL-101 | human_decision_options są jawne | PASS |
| ORCH01-VAL-102 | merge_condition jest jawny | PASS |
| ORCH01-VAL-103 | merge_basis jest jawna | PASS |
| ORCH01-VAL-104 | merge_result_status należy do katalogu | PASS |
| ORCH01-VAL-105 | sprzeczne gałęzie nie są uśredniane | PASS |
| ORCH01-VAL-106 | ten sam route_signature jest wykonywany raz | PASS |
| ORCH01-VAL-107 | impact_group_id nie powoduje ponownego liczenia wpływu | PASS |
| ORCH01-VAL-108 | blokada gałęzi nie blokuje automatycznie sprawy | PASS |
| ORCH01-VAL-109 | branch_cancellation_reason należy do katalogu | PASS |
| ORCH01-VAL-110 | anulowanie nie usuwa historii | PASS |
| ORCH01-VAL-111 | derived_case_id zachowuje derived_case_basis | PASS |
| ORCH01-VAL-112 | step_input_refs są wersjonowane | PASS |
| ORCH01-VAL-113 | step_output_refs są wersjonowane | PASS |
| ORCH01-VAL-114 | orchestration_rule_id jest jawny | PASS |
| ORCH01-VAL-115 | orchestration_basis jest jawna | PASS |
| ORCH01-VAL-116 | orchestration_rule_version jest jawna | PASS |
| ORCH01-VAL-117 | orchestration_contract_version jest jawna | PASS |
| ORCH01-VAL-118 | orchestration_decision_signature jest deterministyczna | PASS |
| ORCH01-VAL-119 | idempotent_replay_status jest jawny | PASS |
| ORCH01-VAL-120 | route_edge_id jest jednoznaczny | PASS |
| ORCH01-VAL-121 | from_node_id i to_node_id są jawne | PASS |
| ORCH01-VAL-122 | edge_type należy do katalogu | PASS |
| ORCH01-VAL-123 | edge_trigger jest semantyczny | PASS |
| ORCH01-VAL-124 | edge_required_conditions są jawne | PASS |
| ORCH01-VAL-125 | edge_blocking_conditions są jawne | PASS |
| ORCH01-VAL-126 | edge_basis jest jawna | PASS |
| ORCH01-VAL-127 | node_type należy do katalogu | PASS |
| ORCH01-VAL-128 | diagnostic_question_type należy do katalogu | PASS |
| ORCH01-VAL-129 | question_type_basis jest obecna | PASS |
| ORCH01-VAL-130 | unknown_or_cross_domain nie jest arbitralnie mapowane | PASS |
| ORCH01-VAL-131 | wyjście zawiera selected_orchestration_action | PASS |
| ORCH01-VAL-132 | wyjście zawiera selected_route_basis | PASS |
| ORCH01-VAL-133 | wyjście zawiera next_steps | PASS |
| ORCH01-VAL-134 | wyjście zawiera path_history_ref | PASS |
| ORCH01-VAL-135 | orchestration_summary jest po polsku | PASS |
| ORCH01-VAL-136 | scenariusze ORCH01-T01–T55 są kompletne | PASS |
| ORCH01-VAL-137 | selected_route_candidate_ids jest uporządkowanym zbiorem unikalnym | PASS |
| ORCH01-VAL-138 | selected_route_targets jest uporządkowanym zbiorem unikalnym | PASS |
| ORCH01-VAL-139 | selected_route_edge_ids jest uporządkowanym zbiorem unikalnym | PASS |
| ORCH01-VAL-140 | run_test ma dokładnie jeden selected_route_candidate_id w zbiorze | PASS |
| ORCH01-VAL-141 | run_parallel_tests ma co najmniej dwa selected_route_candidate_ids | PASS |
| ORCH01-VAL-142 | kandydaci równolegli mają wspólny parallel_group_id | PASS |
| ORCH01-VAL-143 | w trybie równoległym pole pojedyncze jest null albo not_used_in_parallel | PASS |
| ORCH01-VAL-144 | brak wykonawczego kandydata pozwala na puste zbiory wyboru | PASS |
| ORCH01-VAL-145 | human_decision_id jest jednoznaczny | PASS |
| ORCH01-VAL-146 | human_decision_status należy do katalogu | PASS |
| ORCH01-VAL-147 | human_decision_selected_option pochodzi z opcji albo tworzy nowy kontekst | PASS |
| ORCH01-VAL-148 | human_decision_result_basis jest jawna | PASS |
| ORCH01-VAL-149 | human_decision_version jest jawna | PASS |
| ORCH01-VAL-150 | human_decision_at jest jawny | PASS |
| ORCH01-VAL-151 | human_decision_effect należy do katalogu | PASS |
| ORCH01-VAL-152 | human_decision_resume_allowed jest logiczne | PASS |
| ORCH01-VAL-153 | human_decision_resume_basis jest jawna | PASS |
| ORCH01-VAL-154 | human_decision_resume_step_id wskazuje nowy krok | PASS |
| ORCH01-VAL-155 | krok bramy człowieka nie jest nadpisany | PASS |
| ORCH01-VAL-156 | wznowienie używa aktualnych wejść MGT PRI CONF i next_tests | PASS |
| ORCH01-VAL-157 | case_status_previous jest jawny | PASS |
| ORCH01-VAL-158 | case_status_current jest jawny | PASS |
| ORCH01-VAL-159 | case_status_transition_reason jest jawny | PASS |
| ORCH01-VAL-160 | case_status_transition_basis jest jawna | PASS |
| ORCH01-VAL-161 | case_status_transition_allowed jest logiczne | PASS |
| ORCH01-VAL-162 | completed nie przechodzi do in_progress | PASS |
| ORCH01-VAL-163 | cancelled nie przechodzi do in_progress | PASS |
| ORCH01-VAL-164 | blocked wraca do in_progress tylko po zmianie podstawy | PASS |
| ORCH01-VAL-165 | decyzja człowieka aktywuje albo tworzy wybraną gałąź | PASS |
| ORCH01-VAL-166 | pozostałe gałęzie anulowane decyzją zachowują historię | PASS |

## 22. Kryteria odbioru implementacji ORCH01-ACC

Kryterium ma wynik PASS tylko wtedy, gdy zachowanie jest deterministyczne, odtwarzalne i widoczne w rekordzie danych oraz historii przebiegu.

| ID | Kryterium odbioru | Wynik |
| --- | --- | --- |
| ORCH01-ACC-001 | implementacja przyjmuje pełny rekord sprawy | PASS |
| ORCH01-ACC-002 | implementacja waliduje unikalność diagnostic_case_id | PASS |
| ORCH01-ACC-003 | implementacja wymaga diagnostic_question | PASS |
| ORCH01-ACC-004 | implementacja wymaga decision_context | PASS |
| ORCH01-ACC-005 | implementacja wymaga case_scope i case_period | PASS |
| ORCH01-ACC-006 | implementacja wersjonuje sprawę | PASS |
| ORCH01-ACC-007 | implementacja obsługuje wszystkie wartości case_status | PASS |
| ORCH01-ACC-008 | implementacja wymaga entry_trigger_basis | PASS |
| ORCH01-ACC-009 | implementacja obsługuje siedem entry_trigger | PASS |
| ORCH01-ACC-010 | implementacja nie uruchamia testów na wszelki wypadek | PASS |
| ORCH01-ACC-011 | implementacja przechowuje diagnostic_objective | PASS |
| ORCH01-ACC-012 | implementacja obsługuje pięć diagnostic_objective_status | PASS |
| ORCH01-ACC-013 | answered nie zależy od liczby testów | PASS |
| ORCH01-ACC-014 | implementacja rozdziela route_scope i route_period | PASS |
| ORCH01-ACC-015 | implementacja zachowuje matched scope i full scope | PASS |
| ORCH01-ACC-016 | implementacja tworzy wiele gałęzi w jednej sprawie | PASS |
| ORCH01-ACC-017 | implementacja wiąże branch z parent_branch_id | PASS |
| ORCH01-ACC-018 | implementacja obsługuje sześć branch_status | PASS |
| ORCH01-ACC-019 | implementacja wymaga branch_question | PASS |
| ORCH01-ACC-020 | implementacja wymaga branch_target_claim, gdy dotyczy | PASS |
| ORCH01-ACC-021 | implementacja przechowuje zależności gałęzi | PASS |
| ORCH01-ACC-022 | implementacja tworzy wiele kroków w gałęzi | PASS |
| ORCH01-ACC-023 | implementacja obsługuje dziesięć orchestration_action | PASS |
| ORCH01-ACC-024 | run_test wymaga zakwalifikowanego kandydata | PASS |
| ORCH01-ACC-025 | run_parallel_tests wymaga grupy kandydatów | PASS |
| ORCH01-ACC-026 | validate_information wskazuje walidację MGT albo CONF | PASS |
| ORCH01-ACC-027 | rerun_test wskazuje poprzednie wykonanie | PASS |
| ORCH01-ACC-028 | merge_branches nie uśrednia wyników | PASS |
| ORCH01-ACC-029 | observe zachowuje podstawę monitoringu | PASS |
| ORCH01-ACC-030 | stop_completed zapisuje stop_reason | PASS |
| ORCH01-ACC-031 | stop_blocked zapisuje stop_reason | PASS |
| ORCH01-ACC-032 | human_decision_gate zapisuje typ i opcje | PASS |
| ORCH01-ACC-033 | cancel_branch zachowuje historię | PASS |
| ORCH01-ACC-034 | implementacja obsługuje osiem step_status | PASS |
| ORCH01-ACC-035 | failed_technical jest odrębny od merytorycznej blokady | PASS |
| ORCH01-ACC-036 | wejście Core 10 jest konsumowane bez zmiany | PASS |
| ORCH01-ACC-037 | wejście MGT-01 jest konsumowane bez zmiany | PASS |
| ORCH01-ACC-038 | wejście PRI-01 jest konsumowane bez zmiany | PASS |
| ORCH01-ACC-039 | wejście CONF-01 jest konsumowane bez zmiany | PASS |
| ORCH01-ACC-040 | next_tests tworzy kandydatów, nie zadania obowiązkowe | PASS |
| ORCH01-ACC-041 | CONF validation actions tworzą wyłącznie legalne kandydatury walidacyjne | PASS |
| ORCH01-ACC-042 | MGT required validation tworzy wyłącznie legalne kandydatury walidacyjne | PASS |
| ORCH01-ACC-043 | PRI management route ogranicza przebieg bez zmiany statusu źródłowego | PASS |
| ORCH01-ACC-044 | stop conditions tworzą kandydatów zakończenia | PASS |
| ORCH01-ACC-045 | route_candidate ma pełny kontrakt tożsamości | PASS |
| ORCH01-ACC-046 | route_candidate_type ma pięć wartości | PASS |
| ORCH01-ACC-047 | route_candidate_status ma siedem wartości | PASS |
| ORCH01-ACC-048 | route_candidate_source jest audytowalne | PASS |
| ORCH01-ACC-049 | route_candidate_basis jest audytowalna | PASS |
| ORCH01-ACC-050 | applicability gate odrzuca krok bez związku z objective | PASS |
| ORCH01-ACC-051 | information gate zatrzymuje zależny test przy luce | PASS |
| ORCH01-ACC-052 | scope period gate chroni zakres i okres | PASS |
| ORCH01-ACC-053 | duplication gate używa route_signature | PASS |
| ORCH01-ACC-054 | dependency gate wymusza sekwencję, gdy potrzebna | PASS |
| ORCH01-ACC-055 | diagnostic value gate ocenia konkretny wkład bez score | PASS |
| ORCH01-ACC-056 | human boundary gate zatrzymuje decyzję wykonawczą | PASS |
| ORCH01-ACC-057 | candidate_gate_status ma cztery wartości | PASS |
| ORCH01-ACC-058 | status qualified wymaga przejścia wszystkich bram | PASS |
| ORCH01-ACC-059 | status selected wymaga qualified | PASS |
| ORCH01-ACC-060 | route_signature jest deterministyczna | PASS |
| ORCH01-ACC-061 | route_signature rozróżnia target | PASS |
| ORCH01-ACC-062 | route_signature rozróżnia scope | PASS |
| ORCH01-ACC-063 | route_signature rozróżnia period | PASS |
| ORCH01-ACC-064 | route_signature rozróżnia data_version | PASS |
| ORCH01-ACC-065 | route_signature rozróżnia evidence_version | PASS |
| ORCH01-ACC-066 | route_signature rozróżnia objective lub claim | PASS |
| ORCH01-ACC-067 | duplikat nie jest wykonywany ponownie | PASS |
| ORCH01-ACC-068 | konwergencja gałęzi nie dubluje wykonania | PASS |
| ORCH01-ACC-069 | różny zakres nie jest błędnie deduplikowany | PASS |
| ORCH01-ACC-070 | execution_mode obsługuje sequential | PASS |
| ORCH01-ACC-071 | execution_mode obsługuje parallel | PASS |
| ORCH01-ACC-072 | execution_mode obsługuje not_applicable | PASS |
| ORCH01-ACC-073 | sequential wymaga podstawy zależności | PASS |
| ORCH01-ACC-074 | parallel wymaga niezależności kandydatów | PASS |
| ORCH01-ACC-075 | parallel wymaga odrębnych pytań | PASS |
| ORCH01-ACC-076 | parallel nie służy zbieraniu większej liczby potwierdzeń | PASS |
| ORCH01-ACC-077 | parallel nie omija wspólnej walidacji | PASS |
| ORCH01-ACC-078 | PRI order jest respektowany dla porównywalnej grupy | PASS |
| ORCH01-ACC-079 | tied nie jest arbitralnie rozstrzygane | PASS |
| ORCH01-ACC-080 | incomparable nie jest arbitralnie rankowane | PASS |
| ORCH01-ACC-081 | route_choice jest dostępne przy nierównoległych trasach | PASS |
| ORCH01-ACC-082 | implementacja obsługuje osiem repeat_test_reason | PASS |
| ORCH01-ACC-083 | data_updated może legalizować rerun | PASS |
| ORCH01-ACC-084 | validation_completed może legalizować rerun | PASS |
| ORCH01-ACC-085 | conflict_resolved może legalizować rerun | PASS |
| ORCH01-ACC-086 | scope_changed może legalizować rerun | PASS |
| ORCH01-ACC-087 | period_changed może legalizować rerun | PASS |
| ORCH01-ACC-088 | evidence_updated może legalizować rerun | PASS |
| ORCH01-ACC-089 | definition_version_changed może legalizować rerun | PASS |
| ORCH01-ACC-090 | upstream_result_changed może legalizować rerun | PASS |
| ORCH01-ACC-091 | brak nowej podstawy zabrania rerun | PASS |
| ORCH01-ACC-092 | walidacja tworzy nową wersję podstawy tylko po rzeczywistej zmianie | PASS |
| ORCH01-ACC-093 | implementacja wykrywa exact_repeat | PASS |
| ORCH01-ACC-094 | implementacja wykrywa closed_loop_no_new_information | PASS |
| ORCH01-ACC-095 | implementacja obsługuje legalny validation_loop | PASS |
| ORCH01-ACC-096 | implementacja wykrywa branch_loop | PASS |
| ORCH01-ACC-097 | cycle_basis jest odtwarzalne | PASS |
| ORCH01-ACC-098 | cycle_resolution jest odtwarzalne | PASS |
| ORCH01-ACC-099 | information_contribution_status ma dziewięć wartości | PASS |
| ORCH01-ACC-100 | changes_route może uzasadnić test | PASS |
| ORCH01-ACC-101 | resolves_gap może uzasadnić test | PASS |
| ORCH01-ACC-102 | narrows_claim może uzasadnić test | PASS |
| ORCH01-ACC-103 | tests_mechanism może uzasadnić test | PASS |
| ORCH01-ACC-104 | distinguishes_alternatives może uzasadnić test | PASS |
| ORCH01-ACC-105 | supporting_only nie wymusza testu | PASS |
| ORCH01-ACC-106 | duplicate nie wymusza testu | PASS |
| ORCH01-ACC-107 | no_new_information nie wymusza testu | PASS |
| ORCH01-ACC-108 | not_assessable contribution nie prowadzi automatycznie do testu | PASS |
| ORCH01-ACC-109 | implementacja obsługuje jedenaście stop_reason | PASS |
| ORCH01-ACC-110 | answered może prowadzić do stop_completed | PASS |
| ORCH01-ACC-111 | no adverse signal kończy tylko właściwy zakres | PASS |
| ORCH01-ACC-112 | validation required nie jest sukcesem diagnozy | PASS |
| ORCH01-ACC-113 | insufficient information nie jest completed | PASS |
| ORCH01-ACC-114 | no applicable next test jest interpretowane wraz z objective | PASS |
| ORCH01-ACC-115 | duplicate path jest blokowane | PASS |
| ORCH01-ACC-116 | scope exhausted jest jawne | PASS |
| ORCH01-ACC-117 | human decision required jest jawne | PASS |
| ORCH01-ACC-118 | monitoring only jest jawne | PASS |
| ORCH01-ACC-119 | technical blocker jest jawny | PASS |
| ORCH01-ACC-120 | awaiting_validation jest odrębne od blocked | PASS |
| ORCH01-ACC-121 | paused_monitoring jest odrębne od completed | PASS |
| ORCH01-ACC-122 | mechanism sufficiently supported nie używa progu score | PASS |
| ORCH01-ACC-123 | implementacja obsługuje siedem human_decision_type | PASS |
| ORCH01-ACC-124 | human gate wymaga konkretnego wyboru | PASS |
| ORCH01-ACC-125 | human gate nie jest rekomendacją wykonawczą | PASS |
| ORCH01-ACC-126 | human gate nie maskuje luki metodologicznej | PASS |
| ORCH01-ACC-127 | implementacja obsługuje pięć merge_result_status | PASS |
| ORCH01-ACC-128 | sprzeczność gałęzi pozostaje sprzecznością | PASS |
| ORCH01-ACC-129 | merged consistent nie uśrednia wyników | PASS |
| ORCH01-ACC-130 | impact_group_id nie przelicza wpływu | PASS |
| ORCH01-ACC-131 | blocked branch nie blokuje automatycznie case | PASS |
| ORCH01-ACC-132 | implementacja obsługuje pięć branch_cancellation_reason | PASS |
| ORCH01-ACC-133 | anulowanie nie usuwa kroków | PASS |
| ORCH01-ACC-134 | scope change może tworzyć derived case | PASS |
| ORCH01-ACC-135 | validate_first jest respektowane | PASS |
| ORCH01-ACC-136 | review_and_validate_in_parallel ma warunki | PASS |
| ORCH01-ACC-137 | review_now nie uruchamia wszystkich testów | PASS |
| ORCH01-ACC-138 | observe nie wymusza dalszego testowania | PASS |
| ORCH01-ACC-139 | well_supported finding nie kończy celu mechanism | PASS |
| ORCH01-ACC-140 | weakly_supported nie uruchamia nieskończonej ścieżki | PASS |
| ORCH01-ACC-141 | unresolved conflict nie jest głosowaniem | PASS |
| ORCH01-ACC-142 | critical gap nie jest zastępowany assumption | PASS |
| ORCH01-ACC-143 | historia kroku ma input refs i output refs | PASS |
| ORCH01-ACC-144 | historia kroku ma rule id i basis | PASS |
| ORCH01-ACC-145 | idempotent replay zwraca tę samą decyzję | PASS |
| ORCH01-ACC-146 | zmiana rule version zachowuje starą historię | PASS |
| ORCH01-ACC-147 | failed_technical nie zmienia confidence | PASS |
| ORCH01-ACC-148 | minimalny graf ma pełny kontrakt krawędzi | PASS |
| ORCH01-ACC-149 | graf obsługuje sześć node_type | PASS |
| ORCH01-ACC-150 | manual question mapuje się przez diagnostic_question_type | PASS |
| ORCH01-ACC-151 | unknown_or_cross_domain wymaga doprecyzowania lub jawnych gałęzi | PASS |
| ORCH01-ACC-152 | wyjście zawiera wszystkie wymagane pola | PASS |
| ORCH01-ACC-153 | orchestration_summary jest po polsku | PASS |
| ORCH01-ACC-154 | implementacja nie tworzy Priority Score | PASS |
| ORCH01-ACC-155 | implementacja nie tworzy Confidence Score | PASS |
| ORCH01-ACC-156 | implementacja nie tworzy Data Quality Score | PASS |
| ORCH01-ACC-157 | implementacja nie tworzy Value of Information Score | PASS |
| ORCH01-ACC-158 | implementacja nie używa losowości | PASS |
| ORCH01-ACC-159 | implementacja nie wymaga AI | PASS |
| ORCH01-ACC-160 | implementacja nie wydaje rekomendacji wykonawczych | PASS |
| ORCH01-ACC-161 | implementacja przechodzi ORCH01-T01–T55 | PASS |
| ORCH01-ACC-162 | implementacja zwraca selected_route_candidate_ids | PASS |
| ORCH01-ACC-163 | implementacja zwraca selected_route_targets | PASS |
| ORCH01-ACC-164 | implementacja zwraca selected_route_edge_ids | PASS |
| ORCH01-ACC-165 | run_test wymusza liczność zbioru równą jeden | PASS |
| ORCH01-ACC-166 | run_parallel_tests wymusza liczność zbioru co najmniej dwa | PASS |
| ORCH01-ACC-167 | run_parallel_tests wymusza unikalność elementów | PASS |
| ORCH01-ACC-168 | run_parallel_tests wymusza wspólny parallel_group_id | PASS |
| ORCH01-ACC-169 | tryb równoległy nie wybiera sztucznego kandydata głównego | PASS |
| ORCH01-ACC-170 | tryb równoległy nie wybiera sztucznego celu głównego | PASS |
| ORCH01-ACC-171 | akcje bez wykonawczego kandydata akceptują puste zbiory | PASS |
| ORCH01-ACC-172 | implementacja tworzy human_decision_id | PASS |
| ORCH01-ACC-173 | implementacja obsługuje cztery human_decision_status | PASS |
| ORCH01-ACC-174 | implementacja obsługuje sześć human_decision_effect | PASS |
| ORCH01-ACC-175 | resolved wymaga human_decision_selected_option | PASS |
| ORCH01-ACC-176 | opcja spoza human_decision_options tworzy wersję albo nowy kontekst | PASS |
| ORCH01-ACC-177 | ORCH rejestruje decyzję bez oceny jej jakości | PASS |
| ORCH01-ACC-178 | ORCH rejestruje decyzję bez wykonywania działania | PASS |
| ORCH01-ACC-179 | resume_diagnosis tworzy wersjonowane wejście | PASS |
| ORCH01-ACC-180 | resume_diagnosis tworzy nowy diagnostic_step_id | PASS |
| ORCH01-ACC-181 | resume_diagnosis ponownie kwalifikuje kandydatów | PASS |
| ORCH01-ACC-182 | resume_diagnosis odczytuje aktualne MGT PRI CONF i next_tests | PASS |
| ORCH01-ACC-183 | resume_diagnosis nie przywraca automatycznie poprzedniego kandydata | PASS |
| ORCH01-ACC-184 | krok human_decision_gate pozostaje niezmienny | PASS |
| ORCH01-ACC-185 | implementacja zapisuje pięć pól przejścia case_status | PASS |
| ORCH01-ACC-186 | open przechodzi do in_progress po legalnym kroku | PASS |
| ORCH01-ACC-187 | in_progress przechodzi do awaiting_validation po blokującej walidacji | PASS |
| ORCH01-ACC-188 | awaiting_validation przechodzi do in_progress po skutecznej walidacji | PASS |
| ORCH01-ACC-189 | in_progress przechodzi do awaiting_human_decision po aktywacji bramy | PASS |
| ORCH01-ACC-190 | awaiting_human_decision przechodzi do in_progress po decyzji resume | PASS |
| ORCH01-ACC-191 | in_progress przechodzi do paused_monitoring zgodnie z observe | PASS |
| ORCH01-ACC-192 | paused_monitoring przechodzi do in_progress wyłącznie po nowym triggerze lub podstawie | PASS |
| ORCH01-ACC-193 | in_progress przechodzi do completed wyłącznie przez stop_completed | PASS |
| ORCH01-ACC-194 | in_progress albo awaiting_validation przechodzi do blocked bez legalnej drogi | PASS |
| ORCH01-ACC-195 | completed i cancelled pozostają końcowe dla wersji sprawy | PASS |
| ORCH01-ACC-196 | blocked może zostać wznowiony wyłącznie po zmianie podstawy | PASS |
| ORCH01-ACC-197 | wybrana przez człowieka gałąź jest active albo nowo utworzona | PASS |
| ORCH01-ACC-198 | pozostała gałąź może być cancelled przez human_decision | PASS |
| ORCH01-ACC-199 | anulowana gałąź zachowuje pełną historię | PASS |
| ORCH01-ACC-200 | implementacja przechodzi ORCH01-T51–T55 | PASS |

## 23. Warunki zamknięcia ORCH01-DOD

| ID | Warunek zamknięcia | Wynik |
| --- | --- | --- |
| ORCH01-DOD-01 | rola ORCH-01 jest jednoznaczna | PASS |
| ORCH01-DOD-02 | ORCH-01 nie jest jedenastym testem | PASS |
| ORCH01-DOD-03 | granica Core 10 jest zamknięta | PASS |
| ORCH01-DOD-04 | granica MGT-01 jest zamknięta | PASS |
| ORCH01-DOD-05 | granica PRI-01 jest zamknięta | PASS |
| ORCH01-DOD-06 | granica CONF-01 jest zamknięta | PASS |
| ORCH01-DOD-07 | brak Priority Score | PASS |
| ORCH01-DOD-08 | brak Confidence Score | PASS |
| ORCH01-DOD-09 | brak Data Quality Score | PASS |
| ORCH01-DOD-10 | brak Value of Information Score | PASS |
| ORCH01-DOD-11 | brak arbitralnych wag | PASS |
| ORCH01-DOD-12 | brak arbitralnego progu liczby testów | PASS |
| ORCH01-DOD-13 | kontrakt sprawy jest kompletny | PASS |
| ORCH01-DOD-14 | case_status ma katalog zamknięty | PASS |
| ORCH01-DOD-15 | entry_trigger ma katalog zamknięty | PASS |
| ORCH01-DOD-16 | entry_trigger_basis jest obowiązkowa | PASS |
| ORCH01-DOD-17 | diagnostic objective jest kompletny | PASS |
| ORCH01-DOD-18 | status objective nie zależy od liczby testów | PASS |
| ORCH01-DOD-19 | scope i period są chronione | PASS |
| ORCH01-DOD-20 | model sprawa-gałąź-krok jest zamknięty | PASS |
| ORCH01-DOD-21 | branch_status ma katalog zamknięty | PASS |
| ORCH01-DOD-22 | orchestration_action ma katalog zamknięty | PASS |
| ORCH01-DOD-23 | step_status ma katalog zamknięty | PASS |
| ORCH01-DOD-24 | failed_technical ma granicę merytoryczną | PASS |
| ORCH01-DOD-25 | wejścia Core 10 są kompletne | PASS |
| ORCH01-DOD-26 | wejścia MGT są kompletne | PASS |
| ORCH01-DOD-27 | wejścia PRI są kompletne | PASS |
| ORCH01-DOD-28 | wejścia CONF są kompletne | PASS |
| ORCH01-DOD-29 | źródła kandydatów są zamknięte | PASS |
| ORCH01-DOD-30 | kontrakt route_candidate jest kompletny | PASS |
| ORCH01-DOD-31 | route_candidate_type ma katalog | PASS |
| ORCH01-DOD-32 | route_candidate_status ma katalog | PASS |
| ORCH01-DOD-33 | applicability gate jest zamknięta | PASS |
| ORCH01-DOD-34 | information gate jest zamknięta | PASS |
| ORCH01-DOD-35 | scope period gate jest zamknięta | PASS |
| ORCH01-DOD-36 | duplication gate jest zamknięta | PASS |
| ORCH01-DOD-37 | dependency gate jest zamknięta | PASS |
| ORCH01-DOD-38 | diagnostic value gate jest zamknięta | PASS |
| ORCH01-DOD-39 | human boundary gate jest zamknięta | PASS |
| ORCH01-DOD-40 | kolejność kwalifikacji jest deterministyczna | PASS |
| ORCH01-DOD-41 | route_signature ma minimalny zestaw elementów | PASS |
| ORCH01-DOD-42 | deduplikacja jest deterministyczna | PASS |
| ORCH01-DOD-43 | konwergencja gałęzi jest obsłużona | PASS |
| ORCH01-DOD-44 | różny scope nie jest deduplikowany | PASS |
| ORCH01-DOD-45 | sequential ma zamknięty warunek | PASS |
| ORCH01-DOD-46 | parallel ma zamknięty warunek | PASS |
| ORCH01-DOD-47 | wspólna walidacja blokuje parallel | PASS |
| ORCH01-DOD-48 | route order respektuje PRI | PASS |
| ORCH01-DOD-49 | tied ma bezpieczne wyjście | PASS |
| ORCH01-DOD-50 | incomparable ma bezpieczne wyjście | PASS |
| ORCH01-DOD-51 | repeat_test_reason ma katalog zamknięty | PASS |
| ORCH01-DOD-52 | rerun wymaga nowej podstawy | PASS |
| ORCH01-DOD-53 | nielegalny rerun jest blokowany | PASS |
| ORCH01-DOD-54 | pętla walidacyjna ma kontrakt wersji | PASS |
| ORCH01-DOD-55 | cycle_type ma katalog zamknięty | PASS |
| ORCH01-DOD-56 | exact repeat jest zatrzymany | PASS |
| ORCH01-DOD-57 | closed loop bez informacji jest zatrzymany | PASS |
| ORCH01-DOD-58 | validation loop z nową informacją jest legalny | PASS |
| ORCH01-DOD-59 | branch loop jest wykrywany | PASS |
| ORCH01-DOD-60 | information contribution ma katalog zamknięty | PASS |
| ORCH01-DOD-61 | dalszy test wymaga roli rozstrzygającej | PASS |
| ORCH01-DOD-62 | supporting_only nie wymusza testu | PASS |
| ORCH01-DOD-63 | duplicate nie wymusza testu | PASS |
| ORCH01-DOD-64 | no_new_information nie wymusza testu | PASS |
| ORCH01-DOD-65 | stop_reason ma katalog zamknięty | PASS |
| ORCH01-DOD-66 | stop_completed ma warunek | PASS |
| ORCH01-DOD-67 | stop_blocked ma warunek | PASS |
| ORCH01-DOD-68 | awaiting_validation ma warunek | PASS |
| ORCH01-DOD-69 | paused_monitoring ma warunek | PASS |
| ORCH01-DOD-70 | brak testu jest interpretowany przez objective | PASS |
| ORCH01-DOD-71 | mechanism sufficiently supported nie używa globalnego progu | PASS |
| ORCH01-DOD-72 | human_decision_type ma katalog zamknięty | PASS |
| ORCH01-DOD-73 | human gate ma pełny kontrakt | PASS |
| ORCH01-DOD-74 | human gate nie jest obejściem | PASS |
| ORCH01-DOD-75 | gałęzie mają własny cel | PASS |
| ORCH01-DOD-76 | merge_result_status ma katalog zamknięty | PASS |
| ORCH01-DOD-77 | merge nie uśrednia | PASS |
| ORCH01-DOD-78 | sprzeczność pozostaje jawna | PASS |
| ORCH01-DOD-79 | finding_cluster_id jest respektowany | PASS |
| ORCH01-DOD-80 | impact_group_id jest respektowany | PASS |
| ORCH01-DOD-81 | blokada jednej gałęzi nie musi blokować sprawy | PASS |
| ORCH01-DOD-82 | branch cancellation ma katalog | PASS |
| ORCH01-DOD-83 | anulowanie zachowuje historię | PASS |
| ORCH01-DOD-84 | zmiana scope tworzy gałąź lub derived case | PASS |
| ORCH01-DOD-85 | precedencja MGT-PRI-CONF-next_tests jest jawna | PASS |
| ORCH01-DOD-86 | validate_first jest domknięte | PASS |
| ORCH01-DOD-87 | review_and_validate_in_parallel jest domknięte | PASS |
| ORCH01-DOD-88 | review_now zachowuje bramy kandydatów | PASS |
| ORCH01-DOD-89 | observe nie tworzy nieskończonej diagnozy | PASS |
| ORCH01-DOD-90 | wysoka pewność nie kończy automatycznie | PASS |
| ORCH01-DOD-91 | słaba pewność nie uruchamia automatycznie testów | PASS |
| ORCH01-DOD-92 | unresolved conflict ma legalną trasę | PASS |
| ORCH01-DOD-93 | critical information gap ma pierwszeństwo | PASS |
| ORCH01-DOD-94 | wiele confidence validation actions ma zasady zależności | PASS |
| ORCH01-DOD-95 | historia przebiegu jest kompletna | PASS |
| ORCH01-DOD-96 | każdy krok ma input refs | PASS |
| ORCH01-DOD-97 | każdy krok ma output refs | PASS |
| ORCH01-DOD-98 | każdy krok ma rule id | PASS |
| ORCH01-DOD-99 | każdy krok ma basis | PASS |
| ORCH01-DOD-100 | idempotencja jest domknięta | PASS |
| ORCH01-DOD-101 | rule version jest jawna | PASS |
| ORCH01-DOD-102 | contract version jest jawna | PASS |
| ORCH01-DOD-103 | data version jest jawna | PASS |
| ORCH01-DOD-104 | evidence version jest jawna | PASS |
| ORCH01-DOD-105 | zmiana wersji ma podstawę merytoryczną | PASS |
| ORCH01-DOD-106 | awaria techniczna ma odrębny status | PASS |
| ORCH01-DOD-107 | brak zegara i SLA jest jawny | PASS |
| ORCH01-DOD-108 | brak wymagania AI jest jawny | PASS |
| ORCH01-DOD-109 | brak rekomendacji wykonawczych jest jawny | PASS |
| ORCH01-DOD-110 | minimalny graf ma kontrakt krawędzi | PASS |
| ORCH01-DOD-111 | node_type ma katalog zamknięty | PASS |
| ORCH01-DOD-112 | edge trigger jest semantyczny | PASS |
| ORCH01-DOD-113 | mapowanie pytania ma osobny kontrakt | PASS |
| ORCH01-DOD-114 | diagnostic_question_type ma katalog zamknięty | PASS |
| ORCH01-DOD-115 | unknown_or_cross_domain nie jest arbitralne | PASS |
| ORCH01-DOD-116 | wyjście ORCH-01 jest kompletne | PASS |
| ORCH01-DOD-117 | orchestration summary jest audytowalne i polskie | PASS |
| ORCH01-DOD-118 | ORCH01-T01–T55 są kompletne | PASS |
| ORCH01-DOD-119 | ORCH01-VAL jest kompletne | PASS |
| ORCH01-DOD-120 | ORCH01-ACC jest kompletne | PASS |
| ORCH01-DOD-121 | QORCH01 jest kompletne | PASS |
| ORCH01-DOD-122 | Core 10 ma 0 zmian | PASS |
| ORCH01-DOD-123 | PRI-01 ma 0 zmian | PASS |
| ORCH01-DOD-124 | CONF-01 ma 0 zmian | PASS |
| ORCH01-DOD-125 | dane SPZOZ = 0 | PASS |
| ORCH01-DOD-126 | dane pacjentów = 0 | PASS |
| ORCH01-DOD-127 | ORCH-02 nie jest rozpoczęty | PASS |
| ORCH01-DOD-128 | warstwa rekomendacji nie jest rozpoczęta | PASS |
| ORCH01-DOD-129 | interfejs użytkownika nie jest projektowany | PASS |
| ORCH01-DOD-130 | zbiory wybranych kandydatów, celów i krawędzi są domknięte | PASS |
| ORCH01-DOD-131 | wybór pojedynczy ma dokładnie jeden element | PASS |
| ORCH01-DOD-132 | wybór równoległy ma co najmniej dwa unikalne elementy | PASS |
| ORCH01-DOD-133 | wybór równoległy ma wspólny parallel_group_id | PASS |
| ORCH01-DOD-134 | brak sztucznego kandydata głównego jest zagwarantowany | PASS |
| ORCH01-DOD-135 | rekord decyzji człowieka jest kompletny | PASS |
| ORCH01-DOD-136 | human_decision_status ma katalog zamknięty | PASS |
| ORCH01-DOD-137 | human_decision_effect ma katalog zamknięty | PASS |
| ORCH01-DOD-138 | opcja decyzji jest chroniona przez human_decision_options | PASS |
| ORCH01-DOD-139 | ORCH nie ocenia jakości decyzji człowieka | PASS |
| ORCH01-DOD-140 | ORCH nie wykonuje wybranego działania zarządczego | PASS |
| ORCH01-DOD-141 | powrót z awaiting_human_decision ma pełny kontrakt | PASS |
| ORCH01-DOD-142 | wznowienie tworzy nowy krok | PASS |
| ORCH01-DOD-143 | wznowienie ponownie kwalifikuje kandydatów | PASS |
| ORCH01-DOD-144 | krok bramy człowieka pozostaje w historii | PASS |
| ORCH01-DOD-145 | maszyna stanów case_status jest jawna | PASS |
| ORCH01-DOD-146 | każde przejście ma reason i basis | PASS |
| ORCH01-DOD-147 | completed jest stanem końcowym wersji | PASS |
| ORCH01-DOD-148 | cancelled jest stanem końcowym wersji | PASS |
| ORCH01-DOD-149 | blocked ma kontrolowane wznowienie po zmianie podstawy | PASS |
| ORCH01-DOD-150 | decyzja człowieka jest powiązana ze statusem gałęzi | PASS |
| ORCH01-DOD-151 | anulowane gałęzie nie są usuwane | PASS |
| ORCH01-DOD-152 | ORCH01-T51 jest zakończony PASS | PASS |
| ORCH01-DOD-153 | ORCH01-T52 jest zakończony PASS | PASS |
| ORCH01-DOD-154 | ORCH01-T53 jest zakończony PASS | PASS |
| ORCH01-DOD-155 | ORCH01-T54 jest zakończony PASS | PASS |
| ORCH01-DOD-156 | ORCH01-T55 jest zakończony PASS | PASS |

## 24. Test końcowy QORCH01

| ID | Kontrola | Wynik |
| --- | --- | --- |
| QORCH01-001 | ORCH-01 nie jest jedenastym testem. | PASS |
| QORCH01-002 | Core 10 pozostaje zamrożony. | PASS |
| QORCH01-003 | PRI-01 pozostaje zamrożony. | PASS |
| QORCH01-004 | CONF-01 pozostaje zamrożony. | PASS |
| QORCH01-005 | MGT-01 nie jest redefiniowany. | PASS |
| QORCH01-006 | ORCH nie tworzy własnego Priority Score. | PASS |
| QORCH01-007 | ORCH nie tworzy własnego Confidence Score. | PASS |
| QORCH01-008 | ORCH nie tworzy Data Quality Score. | PASS |
| QORCH01-009 | ORCH nie tworzy Value of Information Score. | PASS |
| QORCH01-010 | Jedna sprawa ma diagnostic_case_id. | PASS |
| QORCH01-011 | Diagnostic question jest jawne. | PASS |
| QORCH01-012 | Decision context jest jawny. | PASS |
| QORCH01-013 | Case scope i period są jawne. | PASS |
| QORCH01-014 | Entry trigger ma katalog. | PASS |
| QORCH01-015 | Entry trigger ma basis. | PASS |
| QORCH01-016 | Case status ma katalog zamknięty. | PASS |
| QORCH01-017 | Diagnostic objective ma status. | PASS |
| QORCH01-018 | Answered ≠ wykonano N testów. | PASS |
| QORCH01-019 | Sprawa ≠ gałąź. | PASS |
| QORCH01-020 | Gałąź ≠ krok. | PASS |
| QORCH01-021 | Orchestration action ma katalog. | PASS |
| QORCH01-022 | run_test nie jest rekomendacją wykonawczą. | PASS |
| QORCH01-023 | run_parallel_tests wymaga basis. | PASS |
| QORCH01-024 | validate_information korzysta z MGT/CONF. | PASS |
| QORCH01-025 | rerun_test wymaga legalnego reason. | PASS |
| QORCH01-026 | merge_branches nie uśrednia wyników. | PASS |
| QORCH01-027 | human_decision_gate nie podejmuje decyzji. | PASS |
| QORCH01-028 | stop_completed ma jawny reason. | PASS |
| QORCH01-029 | stop_blocked ma jawny reason. | PASS |
| QORCH01-030 | next_tests są kandydatami, nie automatycznym planem. | PASS |
| QORCH01-031 | Route candidate ma identyfikator. | PASS |
| QORCH01-032 | Route candidate ma source. | PASS |
| QORCH01-033 | Route candidate ma basis. | PASS |
| QORCH01-034 | Candidate applicability gate istnieje. | PASS |
| QORCH01-035 | Candidate information gate istnieje. | PASS |
| QORCH01-036 | Candidate scope/period gate istnieje. | PASS |
| QORCH01-037 | Candidate duplication gate istnieje. | PASS |
| QORCH01-038 | Candidate dependency gate istnieje. | PASS |
| QORCH01-039 | Candidate diagnostic value gate istnieje. | PASS |
| QORCH01-040 | Candidate human boundary gate istnieje. | PASS |
| QORCH01-041 | Kandydat bez wartości diagnostycznej może być odrzucony. | PASS |
| QORCH01-042 | ORCH nie wymyśla nowego testu. | PASS |
| QORCH01-043 | ORCH nie wymyśla nowej walidacji. | PASS |
| QORCH01-044 | Route signature jest deterministyczna. | PASS |
| QORCH01-045 | Exact duplicate jest wykrywany. | PASS |
| QORCH01-046 | Ten sam test może być legalnie rerun po validation_completed. | PASS |
| QORCH01-047 | Data_updated może otworzyć rerun. | PASS |
| QORCH01-048 | Conflict_resolved może otworzyć rerun. | PASS |
| QORCH01-049 | Scope_changed może otworzyć rerun. | PASS |
| QORCH01-050 | Period_changed może otworzyć rerun. | PASS |
| QORCH01-051 | Evidence_updated może otworzyć rerun. | PASS |
| QORCH01-052 | Definition_version_changed może otworzyć rerun. | PASS |
| QORCH01-053 | Upstream_result_changed może otworzyć rerun. | PASS |
| QORCH01-054 | Brak zmiany podstawy blokuje rerun. | PASS |
| QORCH01-055 | Cycle detection istnieje. | PASS |
| QORCH01-056 | Exact repeat jest zatrzymywany. | PASS |
| QORCH01-057 | Closed loop bez nowej informacji jest zatrzymywany. | PASS |
| QORCH01-058 | Validation loop z nową informacją jest legalny. | PASS |
| QORCH01-059 | Parallel nie wynika wyłącznie z liczby next_tests. | PASS |
| QORCH01-060 | Sequential jest wymagane przy zależności scope. | PASS |
| QORCH01-061 | Parallel wymaga niezależności kandydatów. | PASS |
| QORCH01-062 | Parallel nie może omijać wspólnej required validation. | PASS |
| QORCH01-063 | PRI next_test_priority_order jest respektowane, gdy legalne. | PASS |
| QORCH01-064 | Tied nie jest arbitralnie rozstrzygane. | PASS |
| QORCH01-065 | Incomparable nie jest arbitralnie rankowane. | PASS |
| QORCH01-066 | Tied może prowadzić do parallel albo human gate. | PASS |
| QORCH01-067 | Additional information needed jest jawne. | PASS |
| QORCH01-068 | Information contribution status ma katalog. | PASS |
| QORCH01-069 | Supporting_only nie wymusza testu. | PASS |
| QORCH01-070 | Duplicate nie wymusza testu. | PASS |
| QORCH01-071 | No_new_information nie wymusza testu. | PASS |
| QORCH01-072 | changes_route uzasadnia dalszy krok. | PASS |
| QORCH01-073 | resolves_gap uzasadnia dalszy krok. | PASS |
| QORCH01-074 | narrows_claim może uzasadniać dalszy krok. | PASS |
| QORCH01-075 | tests_mechanism może uzasadniać dalszy krok. | PASS |
| QORCH01-076 | distinguishes_alternatives może uzasadniać dalszy krok. | PASS |
| QORCH01-077 | Stop reason ma katalog. | PASS |
| QORCH01-078 | Diagnostic question answered może zakończyć sprawę. | PASS |
| QORCH01-079 | Mechanism sufficiently supported nie używa globalnego progu confidence. | PASS |
| QORCH01-080 | No adverse signal kończy tylko właściwy scope. | PASS |
| QORCH01-081 | Validation required before continuation nie jest sukcesem diagnozy. | PASS |
| QORCH01-082 | Insufficient information nie jest completed. | PASS |
| QORCH01-083 | No applicable next test nie zawsze oznacza completed. | PASS |
| QORCH01-084 | Duplicate path jest stop reason. | PASS |
| QORCH01-085 | Scope exhausted jest jawne. | PASS |
| QORCH01-086 | Human decision required jest jawne. | PASS |
| QORCH01-087 | Monitoring only jest jawne. | PASS |
| QORCH01-088 | Technical blocker jest odrębny. | PASS |
| QORCH01-089 | Awaiting validation ≠ blocked, jeśli walidacja jest dostępna. | PASS |
| QORCH01-090 | Paused monitoring jest możliwe. | PASS |
| QORCH01-091 | Human gate ma typ. | PASS |
| QORCH01-092 | Human gate ma basis. | PASS |
| QORCH01-093 | Human gate ma options. | PASS |
| QORCH01-094 | Human gate nie jest workaroundem metodologicznym. | PASS |
| QORCH01-095 | Route choice może wymagać człowieka. | PASS |
| QORCH01-096 | Materiality choice może wymagać człowieka. | PASS |
| QORCH01-097 | Policy choice może wymagać człowieka. | PASS |
| QORCH01-098 | Risk acceptance może wymagać człowieka. | PASS |
| QORCH01-099 | Branch ma pytanie pomocnicze. | PASS |
| QORCH01-100 | Branch ma target claim. | PASS |
| QORCH01-101 | Branch ma status. | PASS |
| QORCH01-102 | Merge ma condition. | PASS |
| QORCH01-103 | Merge ma basis. | PASS |
| QORCH01-104 | Merge consistent nie oznacza uśredniania. | PASS |
| QORCH01-105 | Merge contradictory zachowuje konflikt. | PASS |
| QORCH01-106 | Dwie gałęzie do tego samego route_signature nie dublują testu. | PASS |
| QORCH01-107 | Różny scope nie jest błędnie deduplikowany. | PASS |
| QORCH01-108 | Jedna blocked branch nie blokuje automatycznie całej sprawy. | PASS |
| QORCH01-109 | Branch cancellation ma reason. | PASS |
| QORCH01-110 | Anulowanie nie usuwa historii. | PASS |
| QORCH01-111 | Zmiana scope nie nadpisuje starej historii. | PASS |
| QORCH01-112 | Derived case może być użyty. | PASS |
| QORCH01-113 | PRI problem priority pozostaje wejściem. | PASS |
| QORCH01-114 | PRI validation priority pozostaje wejściem. | PASS |
| QORCH01-115 | PRI management route pozostaje wejściem. | PASS |
| QORCH01-116 | CONF finding confidence pozostaje wejściem. | PASS |
| QORCH01-117 | CONF mechanism confidence pozostaje wejściem. | PASS |
| QORCH01-118 | CONF validation actions pozostają wejściem. | PASS |
| QORCH01-119 | MGT decision information status pozostaje wejściem. | PASS |
| QORCH01-120 | MGT critical gap pozostaje wejściem. | PASS |
| QORCH01-121 | validate_first jest respektowane. | PASS |
| QORCH01-122 | review_and_validate_in_parallel ma warunki. | PASS |
| QORCH01-123 | review_now ≠ uruchom wszystko. | PASS |
| QORCH01-124 | observe ≠ szukaj mechanizmu bez końca. | PASS |
| QORCH01-125 | well_supported finding ≠ zawsze stop. | PASS |
| QORCH01-126 | weakly_supported ≠ zawsze kolejny test. | PASS |
| QORCH01-127 | Unresolved conflict nie jest rozwiązywany większością. | PASS |
| QORCH01-128 | Critical information gap nie jest zastępowany assumption. | PASS |
| QORCH01-129 | Confidence validation actions mogą być sekwencyjne. | PASS |
| QORCH01-130 | Confidence validation actions mogą być równoległe tylko gdy niezależne. | PASS |
| QORCH01-131 | Historia kroku jest audytowalna. | PASS |
| QORCH01-132 | Każdy krok ma previous_step_id lub jawny start. | PASS |
| QORCH01-133 | Każdy krok ma input refs. | PASS |
| QORCH01-134 | Każdy krok ma output refs. | PASS |
| QORCH01-135 | Każdy krok ma rule id. | PASS |
| QORCH01-136 | Każdy krok ma basis. | PASS |
| QORCH01-137 | Step status ma katalog. | PASS |
| QORCH01-138 | failed_technical ≠ wynik diagnostyczny. | PASS |
| QORCH01-139 | Idempotent replay jest możliwy. | PASS |
| QORCH01-140 | Identyczne wejście i reguły dają tę samą decyzję. | PASS |
| QORCH01-141 | Orchestration rule version jest jawna. | PASS |
| QORCH01-142 | Orchestration contract version jest jawna. | PASS |
| QORCH01-143 | Data version jest jawna. | PASS |
| QORCH01-144 | Evidence version jest jawna. | PASS |
| QORCH01-145 | ORCH nie projektuje workerów. | PASS |
| QORCH01-146 | ORCH nie projektuje cronów. | PASS |
| QORCH01-147 | ORCH nie projektuje technicznego SLA. | PASS |
| QORCH01-148 | ORCH nie wymaga AI. | PASS |
| QORCH01-149 | AI nie zastępuje reguł ORCH. | PASS |
| QORCH01-150 | ORCH nie rekomenduje zatrudnienia. | PASS |
| QORCH01-151 | ORCH nie rekomenduje zwolnień. | PASS |
| QORCH01-152 | ORCH nie rekomenduje zmian cen. | PASS |
| QORCH01-153 | ORCH nie rekomenduje zakupu capacity. | PASS |
| QORCH01-154 | ORCH nie rekomenduje zamknięcia produktu. | PASS |
| QORCH01-155 | ORCH nie wycenia potencjału. | PASS |
| QORCH01-156 | Minimalny graf ma route_edge_id. | PASS |
| QORCH01-157 | Graf ma from_node i to_node. | PASS |
| QORCH01-158 | Edge ma trigger. | PASS |
| QORCH01-159 | Edge ma required conditions. | PASS |
| QORCH01-160 | Edge ma blocking conditions. | PASS |
| QORCH01-161 | Edge ma basis. | PASS |
| QORCH01-162 | Node type ma katalog. | PASS |
| QORCH01-163 | Manual question może rozpocząć ścieżkę. | PASS |
| QORCH01-164 | Diagnostic question type ma katalog. | PASS |
| QORCH01-165 | Unknown/cross-domain nie jest arbitralnie mapowane. | PASS |
| QORCH01-166 | Output zawiera selected orchestration action. | PASS |
| QORCH01-167 | Output zawiera selected route basis. | PASS |
| QORCH01-168 | Output zawiera next steps. | PASS |
| QORCH01-169 | Output zawiera stop reason, jeśli dotyczy. | PASS |
| QORCH01-170 | Output zawiera human decision gate, jeśli dotyczy. | PASS |
| QORCH01-171 | Orchestration summary jest po polsku. | PASS |
| QORCH01-172 | Angielskie nazwy w narracji są ograniczone. | PASS |
| QORCH01-173 | Dane SPZOZ = 0. | PASS |
| QORCH01-174 | Dane pacjentów = 0. | PASS |
| QORCH01-175 | ORCH-02 nie jest rozpoczynany. | PASS |
| QORCH01-176 | Warstwa rekomendacji wykonawczych nie jest rozpoczynana. | PASS |
| QORCH01-177 | Firma syntetyczna może przejść pełną ścieżkę bez pętli. | PASS |
| QORCH01-178 | Ilość scenariuszy >= 50. | PASS |
| QORCH01-179 | VAL kompletne. | PASS |
| QORCH01-180 | ACC kompletne. | PASS |
| QORCH01-181 | DOD kompletne. | PASS |
| QORCH01-182 | Dokument jest jednoznacznie implementowalny przez Aleksandra. | PASS |
| QORCH01-183 | Dokument jest wizualnie sprawdzony po renderze. | PASS |
| QORCH01-184 | Wyjście obsługuje selected_route_candidate_ids. | PASS |
| QORCH01-185 | Wyjście obsługuje selected_route_targets. | PASS |
| QORCH01-186 | Wyjście obsługuje selected_route_edge_ids. | PASS |
| QORCH01-187 | run_test ma dokładnie jeden element w każdym zbiorze wyboru. | PASS |
| QORCH01-188 | run_parallel_tests ma co najmniej dwa unikalne selected_route_candidate_ids. | PASS |
| QORCH01-189 | Wszystkie elementy run_parallel_tests należą do jednego parallel_group_id. | PASS |
| QORCH01-190 | W trybie równoległym selected_route_candidate_id nie wskazuje sztucznego kandydata głównego. | PASS |
| QORCH01-191 | W trybie równoległym selected_route_target nie wskazuje sztucznego celu głównego. | PASS |
| QORCH01-192 | Akcja bez wykonawczego kandydata może mieć puste zbiory wyboru. | PASS |
| QORCH01-193 | Rekord decyzji człowieka ma human_decision_id. | PASS |
| QORCH01-194 | human_decision_status ma katalog zamknięty. | PASS |
| QORCH01-195 | human_decision_effect ma katalog zamknięty. | PASS |
| QORCH01-196 | Rozwiązana decyzja wskazuje human_decision_selected_option. | PASS |
| QORCH01-197 | Wybrana opcja pochodzi z human_decision_options albo tworzy nową wersję lub sprawę pochodną. | PASS |
| QORCH01-198 | ORCH nie ocenia jakości wyboru zarządczego. | PASS |
| QORCH01-199 | Decyzja człowieka jest nowym wersjonowanym wejściem. | PASS |
| QORCH01-200 | Wznowienie ma human_decision_resume_allowed. | PASS |
| QORCH01-201 | Wznowienie ma human_decision_resume_basis. | PASS |
| QORCH01-202 | Wznowienie tworzy human_decision_resume_step_id. | PASS |
| QORCH01-203 | Wznowienie po decyzji ponownie kwalifikuje kandydatów. | PASS |
| QORCH01-204 | Wznowienie nie wybiera automatycznie poprzedniego kandydata. | PASS |
| QORCH01-205 | Krok bramy człowieka nie jest nadpisywany. | PASS |
| QORCH01-206 | Przejście case_status ma previous, current, reason, basis i allowed. | PASS |
| QORCH01-207 | open przechodzi do in_progress po pierwszym legalnym kroku. | PASS |
| QORCH01-208 | awaiting_validation wraca do in_progress po skutecznej walidacji. | PASS |
| QORCH01-209 | awaiting_human_decision wraca do in_progress wyłącznie po decyzji pozwalającej wznowić diagnozę. | PASS |
| QORCH01-210 | paused_monitoring wraca do in_progress wyłącznie po nowym legalnym triggerze albo zmianie podstawy. | PASS |
| QORCH01-211 | completed jest stanem końcowym wersji sprawy. | PASS |
| QORCH01-212 | cancelled jest stanem końcowym wersji sprawy. | PASS |
| QORCH01-213 | blocked może zostać wznowiony wyłącznie po jawnej zmianie podstawy. | PASS |
| QORCH01-214 | Decyzja człowieka może aktywować lub utworzyć wybraną gałąź. | PASS |
| QORCH01-215 | Pozostałe gałęzie mogą być cancelled z branch_cancellation_reason=human_decision. | PASS |
| QORCH01-216 | Anulowane gałęzie pozostają w historii. | PASS |
| QORCH01-217 | ORCH01-T51–T55 są kompletne i mają wynik PASS. | PASS |

## 25. Dziedziczone otwarte kontrakty wspólne

| Kontrakt | Sposób ochrony w ORCH-01 |
| --- | --- |
| globalna polityka istotności biznesowej | wybory materiality prowadzą do human_decision_gate |
| globalny kontrakt work_content | ORCH zatrzymuje trasę zależną od brakującej semantyki |
| globalny standard activity_unit i weighted_volume | bez lokalnego przeliczania jednostek |
| wspólna polityka alokacji shared cost | bez lokalnej polityki przypisania kosztów |
| globalny standard kalendarzy operacyjnych i time_basis | bez lokalnych założeń czasu |
| reguły capability/resource substitution | bez arbitralnej zastępowalności zasobów |
| globalna podstawa kosztowa | bez lokalnej zmiany semantyki kosztu |
| globalna klasyfikacja one-off | bez lokalnego oznaczania korekt |
| pełny system rekomendacji wykonawczych | poza ORCH-01 |
| techniczne harmonogramowanie i kolejki wykonawcze | poza logicznym porządkiem ORCH-01 |
| ewentualna metodologia probabilistyczna | wyłącznie jako przyszły odrębny standard |
| ewentualny ORCH-02 | nie rozpoczęto; może powstać tylko po osobnej decyzji |

### 25.1. Potwierdzenia granic i kompletności

| Kontrola | Wynik |
| --- | --- |
| Priority Score routingu / Confidence Score routingu | 0 / 0 |
| Data Quality Score / Value of Information Score | 0 / 0 |
| arbitralne wagi / arbitralny ranking tied-incomparable | 0 / 0 |
| automatyczne rekomendacje wykonawcze | 0 |
| zmiany FIN-01 / FIN-02 / FIN-03 | 0 / 0 / 0 |
| zmiany CAP-01 / CAP-02 / HR-01 | 0 / 0 / 0 |
| zmiany PORT-01 / PROC-01 / PROC-02 / MGT-01 | 0 / 0 / 0 / 0 |
| zmiany ZOP-PRI-01 / ZOP-CONF-01 | 0 / 0 |
| dane SPZOZ / dane pacjentów | 0 / 0 |
| ORCH-02 / implementacja kodowa / interfejs / rekomendacje | 0 / 0 / 0 / 0 |
| ORCH01-VAL | 166 / PASS |
| ORCH01-ACC | 200 / PASS |
| ORCH01-DOD | 156 / PASS |
| QORCH01 | 217 / PASS |
| Scenariusze ORCH01-T | 55 / PASS |

> **STATUS ZOP-ORCH-01 v1.0 – ZAMKNIĘTY METODOLOGICZNIE DO IMPLEMENTACJI. ORCH-01 prowadzi ścieżkę diagnostyczną deterministycznie i audytowalnie; nie jest testem, wynikiem punktowym ani autonomicznym doradcą zarządczym.**
