# ZOP-XR-FOUNDATION-BIND-01 v1.0

**Kontrakt wiążący fundament technologiczny X-Ray z zamrożoną metodologią i wspólnym modelem wyniku**

IMPLEMENTATION BINDING CONTRACT

**Status: KANDYDAT ARCHITEKTA — FOUNDATION_BIND_ACTIVE = false**

Ścieżka: ARCHITEKT → CONTROLLING REVIEW → CONTROLLING RELEASE FOR IMPLEMENTATION → ALEKSANDER IMPLEMENTS

Dokument nie zmienia Core 10, ZOP-TECH-01, ZOP-PRI-01, ZOP-CONF-01 ani ZOP-ORCH-01.

## 1. ROLA, GRANICE I ŹRÓDŁA

ZOP-XR-FOUNDATION-BIND-01 v1.0 jest kontraktem odwzorowania implementacyjnego. Zamyka dokładnie dziesięć niejednoznaczności fundamentu X-Ray bez tworzenia nowej metodologii diagnostycznej i bez ponownego otwierania zamrożonych kart.

existing_methodology_change_count = 0

Core_10_change_count = 0

PRI_01_change_count = 0

CONF_01_change_count = 0

ORCH_01_change_count = 0

NO_LABORATORY_KNOWLEDGE_TRANSFER_TO_PRODUCT_BINDING = true

Dozwoloną podstawą są: bieżący obowiązujący ZOP-MASTER-01, ZOP-TECH-01, zamrożone Core 10, ZOP-PRI-01 v1.0, ZOP-CONF-01 v1.0, ZOP-ORCH-01 v1.0, pytania Aleksandra z 09.09.2026 oraz wiążące decyzje Controllingu dla punktów 01–10, w tym finalna Decision 08.

KORDENIA-M1, SYN/EXEC/HIST/CAL, wyniki Laboratorium i inne Lab-only artifacts są poza zakresem.

Nowa rzeczywista sprzeczność pomiędzy frozen sources wymaga: CONTRACT_CONFLICT_DISCOVERED = true → CONTROLLING_DECISION_REQUIRED → STOP.

### 1.1. Macierz dziesięciu decyzji

| # | Obszar | Binding |
|---|---|---|
| 01 | CRITICAL i zależności | MODULE blokuje wyłącznie zależne moduły; GLOBAL_TEST blokuje cały test. |
| 02 | Moduł | Formalny byt kontraktu; status testu wynika deterministycznie ze statusów modułów. |
| 03 | Scope identity | Label nie jest identity; scope ma kanoniczną definicję i hash. |
| 04 | Reference identity | Różna referencja tworzy różną tożsamość wyniku. |
| 05 | Wersja karty | Każda nowa wersja deklaruje comparison_compatibility. |
| 06 | Waluta | Jedna waluta dataset/profil; brak automatycznego FX. |
| 07 | Dalsza weryfikacja | Walidator może sugerować wyłącznie techniczną ścieżkę sprawdzenia. |
| 08 | Structural required | record_id techniczne; wszystkie bazowe pola ZOP-TECH-01 są kolumnami wymaganymi; missing column ≠ null. |
| 09 | Wyłączenia | Wspólny record/mechanizm, wersjonowane namespaces, bez sztucznego globalnego słownika. |
| 10 | validation_required | Stan źródłowy jest immutable; PRI ustala osobno validation_priority_action. |

## 2. A — MODULE CONTRACT

| Pole | Typ / katalog | Reguła wiążąca |
|---|---|---|
| test_id | string | Identyfikator frozen test contract. |
| test_contract_version | string | Wersja karty będąca częścią identity wyniku. |
| module_id | string; unique within test version | Stały identyfikator modułu; nie pochodzi z label użytkowego. |
| module_name | string | Opis użytkowy; nie jest kluczem. |
| module_requirements | ordered/list of requirement references | Wyłącznie wymagania wynikające z frozen source; FOUNDATION-BIND nie dopisuje semantyki testu. |
| required_validations | list(validation_id) | Walidacje wymagane przed legalnym wykonaniem modułu. |
| module_execution_status | MODULE_NOT_APPLICABLE / MODULE_READY / MODULE_BLOCKED / MODULE_EXECUTED | Status technicznego wykonania. |
| module_result_status | null albo exact source-defined result status | null dopóki moduł nie jest MODULE_EXECUTED; po execution przejmuje status z właściwego frozen test contract. |

Stan MODULE_NOT_APPLICABLE wynika wyłącznie z source-defined applicability. MODULE_READY oznacza, że moduł jest applicable i nie ma blokującego wymogu. MODULE_BLOCKED oznacza, że legalne wykonanie uniemożliwia niespełniony source requirement albo blokująca walidacja. MODULE_EXECUTED oznacza zakończone wykonanie modułu zgodnie z jego kontraktem.

W terminalnej ocenie testu nie może pozostać applicable module w stanie MODULE_READY. Taki stan oznacza niedokończone wykonanie, a nie podstawę do arbitralnego TEST_PARTIAL.

### 2.1. Deterministyczny status testu

| Warunek | Wynik |
|---|---|
| GLOBAL_TEST prerequisite ma CRITICAL | TEST_BLOCKED |
| all_modules_have_resolved_applicability = true; applicable_module_count = 0 | TEST_NOT_APPLICABLE |
| applicable_module_count > 0; executed = 0; blocked = applicable | TEST_BLOCKED |
| executed > 0; blocked > 0; executed + blocked = applicable | TEST_PARTIAL |
| executed = applicable; blocked = 0; applicable > 0 | TEST_COMPLETE |
| applicability któregokolwiek modułu nierozstrzygnięta | terminal_test_status_allowed = false; execution_incomplete_or_applicability_unresolved = true |
| applicable module pozostaje MODULE_READY przy próbie finalizacji | terminal_test_status_allowed = false; execution incomplete |

Zamknięty terminalny katalog test_execution_status obejmuje: TEST_NOT_APPLICABLE, TEST_BLOCKED, TEST_PARTIAL, TEST_COMPLETE. TEST_NOT_APPLICABLE wynika wyłącznie z legalnej source-defined applicability: all_modules_have_resolved_applicability = true oraz applicable_module_count = 0. Nie może służyć do obejścia brakujących danych, błędu walidacji, CRITICAL, brakującej kolumny ani nieukończonego wykonania. Dla TEST_NOT_APPLICABLE diagnostic_finding_required = false, ale technical_execution_record_required = true. Rekord techniczny zachowuje co najmniej test_id, test_contract_version, scope_id, analysis_period, module applicability states, test_execution_status = TEST_NOT_APPLICABLE oraz applicability_basis. TEST_PARTIAL jest wyłącznie technicznym statusem kompletności wykonania; nie jest confidence, severity, problem priority ani validation priority.

## 3. B — VALIDATION DEPENDENCY CONTRACT

| Pole | Dopuszczalne wartości / reguła |
|---|---|
| validation_id | Identyfikator wymaganej kontroli. |
| validation_dependency_scope | MODULE \| GLOBAL_TEST |
| affected_module_ids | Dla MODULE: niepusty zbiór module_id; dla GLOBAL_TEST: pusty. |
| validation_outcome | Exact outcome/severity z właściwego frozen validator/test contract; FOUNDATION-BIND rozpoznaje co najmniej CRITICAL. |
| blocking_effect | CRITICAL + MODULE → affected module(s) = MODULE_BLOCKED. CRITICAL + GLOBAL_TEST → TEST_BLOCKED. |

Nie istnieje automatyczna zasada „CRITICAL blokuje cały test” dla scope MODULE. FOUNDATION-BIND nie dodaje własnego blokowania dla non-CRITICAL; bardziej szczegółowy frozen contract zachowuje pierwszeństwo.

## 4. C — SCOPE IDENTITY CONTRACT

| Pole | Reguła |
|---|---|
| scope_label | Opis użytkowy. Wykluczony z identity. |
| scope_definition.filters | Kanoniczne predicates: field, operator, value. Kolejność predykatów jest nieistotna i po normalizacji sortowana po canonical bytes. |
| scope_definition.population | Jawny selektor/populacja jednostek lub obiektów. Zbiór sortowany, jeżeli karta nie nadaje kolejności semantycznego znaczenia. |
| scope_definition.aggregation_level | Jawny poziom agregacji. Dla zestawu wymiarów kolejność nie jest identity-defining. |
| scope_definition.constraints | Inne jawne ograniczenia zakresu wymagane przez kartę. Kolejność nieistotna, chyba że source contract stanowi inaczej. |
| scope_definition.contract_scope_extensions | Dodatkowe scope-defining pola z frozen test contract, włączone pod ich technicznymi nazwami. |
| scope_definition_hash | SHA-256 lowercase hex z canonical UTF-8 JSON scope_definition. |
| scope_id | "SCOPE-" + scope_definition_hash. |

### 4.1. Kanoniczna serializacja scope

## 1. UTF-8; tekst normalizowany Unicode NFC; bez automatycznego case-folding, trim lub aliasing, chyba że frozen source jawnie definiuje taką równoważność.

## 2. Klucze obiektów sortowane leksykograficznie; bez insignificant whitespace.

## 3. Predykaty filtrów reprezentowane jako field/operator/value; dozwolony operator musi być technicznie jednoznaczny (np. EQ, NE, IN, NOT_IN, LT, LTE, GT, GTE, RANGE).

## 4. Listy o semantyce zbioru sortowane po canonical serialization elementu; listy o semantyce sekwencji zachowują kolejność source contract.

## 5. Wartości zachowują typ; liczba, data, tekst i null nie są zamienne.

## 6. scope_label, kolejność kluczy JSON i kolejność elementów zbiorowych nie wpływają na identity.

same_semantics → same_scope_id

different_filters_or_population_or_aggregation_or_scope_constraints → different_scope_id

## 5. D/E — RESULT IDENTITY I REFERENCE IDENTITY

### 5.1. REFERENCE SEMANTIC IDENTITY / PROVENANCE CONTRACT

| Pole | Reguła |
|---|---|
| reference_type | Część semantic reference identity; exact value z source contract. |
| reference_period | Część semantic reference identity; kanoniczny okres/data referencji. |
| reference_scope_id | Część semantic reference identity; scope referencji zgodny ze Scope Identity Contract. |
| reference_source_logical_id | Część semantic reference identity tylko wtedy, gdy wybór konkretnego logicznego obiektu referencyjnego jest częścią znaczenia referencji; w przeciwnym razie canonical null. |
| reference_semantic_extensions | Wyłącznie source-defined pola semantyczne referencji; default = {}. |
| reference_id | "REF-" + SHA256(canonical JSON {reference_type, reference_period, reference_scope_id, reference_source_logical_id, reference_semantic_extensions}). |
| reference_value | PROVENANCE/EXECUTION: exact wartość faktycznie użyta; domyślnie nie jest częścią reference_id. |
| reference_source_artifact_id | PROVENANCE/EXECUTION: exact artifact użyty do pozyskania referencji. |
| reference_source_SHA256 | PROVENANCE/EXECUTION: SHA-256 exact source bytes użytych w wykonaniu. |
| reference_source_location_or_member_path | PROVENANCE/EXECUTION: lokalizacja/member path exact bytes; nie jest semantic identity. |
| reference_extracted_at_utc | PROVENANCE/EXECUTION: moment pozyskania wartości referencyjnej. |
| reference_input_binding | PROVENANCE/EXECUTION: wiązanie exact input/reference użyte w konkretnym wykonaniu. |
| reference_applicable | true/false. Gdy false, reference_id = null; brak referencji nie może być maskowany etykietą. |

Semantic reference identity jest bezwzględnie oddzielona od provenance wykonania. Nie wolno zastępować reference_source_logical_id ścieżką pliku, nazwą loose copy, storage location, physical SHA ani timestampem. same_semantic_reference + different_physical_copy + identical_logical_source → same reference_id. corrected/new exact source bytes → same reference_id, jeżeli logical semantic reference nie uległa zmianie, ale powstaje nowy immutable execution/result record z własnym reference_value, reference provenance, input SHA i result values. reference_value domyślnie nie należy do reference_id. Zmiana reference_type, reference_period, reference_scope_id, reference_source_logical_id lub source-defined reference_semantic_extensions → different reference_id. Jeżeli bardziej szczegółowy frozen contract jawnie definiuje reference_value jako element semantycznej identity, more_specific_frozen_contract_wins = true. historical_result_mutation = false.

### 5.2. RESULT IDENTITY CONTRACT

| Element identity | Reguła |
|---|---|
| test_id | Wymagany. |
| test_contract_version | Wymagany; zmiana wersji zmienia result identity. |
| module_id | Wymagany dla wyniku modułowego; dla wyniku nie-modułowego canonical null. |
| scope_id | Wymagany. |
| analysis_period | Wymagany, w kanonicznej reprezentacji właściwej dla karty. |
| reference_id | Wymagany, gdy reference_applicable = true; w przeciwnym razie canonical null. |
| result_identity | "RESULT-" + SHA-256(canonical JSON powyższych elementów). |

same_semantics → same_result_identity

different_scope → different_result_identity

different_reference → different_result_identity

different_contract_version → different_result_identity

result_identity jest semantycznym kluczem wyniku, a nie uprawnieniem do destrukcyjnego UPSERT. Historyczny finding/result record pozostaje immutable. Powtórne obliczenie tworzy nowy immutable result record/finding record i może wskazywać ten sam result_identity, jeżeli semantyczna tożsamość jest identyczna.

## 6. F — VERSION COMPATIBILITY CONTRACT

| Pole | Katalog / reguła |
|---|---|
| from_contract_version / to_contract_version | Wersje porównywane. |
| comparison_compatibility | COMPATIBLE \| COMPATIBLE_WITH_LIMITATIONS \| INCOMPATIBLE |
| compatibility_basis | Jawny opis zmiany i podstawy kwalifikacji. |
| comparison_limitations | Obowiązkowe i niepuste dla COMPATIBLE_WITH_LIMITATIONS. |
| declared_by_contract_release | Deklaracja powstaje wraz z nową wersją karty/jej release; nie jest zgadywana przez storage. |

COMPATIBLE: porównanie nie zmienia znaczenia analizowanej miary. COMPATIBLE_WITH_LIMITATIONS: porównanie jest legalne wyłącznie w jawnie wskazanym zakresie, a limitations są przechowywane przy porównaniu/wyniku. INCOMPATIBLE: automatyczne porównanie wyników między wersjami jest zabronione.

Oceny kompatybilności wymagają co najmniej zmiany wzoru, licznika/mianownika, scope semantics, required input semantics, reference semantics, exclusions, jednostki oraz progu/klasyfikacji, jeśli karta taki element posiada. Dodanie wyłącznie opisowego pola lub optional non-semantic metadata może być COMPATIBLE.

Zmiana formuły jest INCOMPATIBLE, o ile bardziej szczegółowy frozen contract jawnie nie stanowi inaczej.

historical_result_mutation = false

## 7. G — DATASET CURRENCY CONTRACT

| Pole | Reguła |
|---|---|
| dataset_currency | Jedna jawna waluta profilu/datasetu; canonical uppercase 3-letter currency code. Nie jest automatycznie wyprowadzana z wartości. |
| currency_consistency_status | SINGLE_CURRENCY_CONFIRMED \| CURRENCY_NOT_DECLARED \| MULTI_CURRENCY_UNRESOLVED |
| monetary_modules_execution_allowed | true wyłącznie dla SINGLE_CURRENCY_CONFIRMED, z zastrzeżeniem innych frozen requirements. |

X-Ray nie pobiera kursów, nie wybiera kursu, nie wykonuje FX, nie sumuje różnych walut i nie konwertuje historycznie kwot. Jeżeli source metadata lub import mapping wskazuje więcej niż jedną walutę bez wcześniejszego legalnego ujednolicenia, monetary_modules_execution_allowed = false.

Ujednolicenie waluty oraz dokumentacja jego podstawy należą do warstwy przygotowania danych. Fundament jedynie waliduje zgodność z dataset_currency.

## 8. H — VALIDATION MESSAGE CONTRACT

| Pole | Reguła |
|---|---|
| validation_code | Techniczny kod problemu z właściwego validator/source contract. |
| validation_severity | Exact source-defined severity. |
| validation_basis | Podstawa wykrycia problemu; fakt/warunek techniczny. |
| technical_verification_suggestion | Opcjonalna, wyłącznie techniczna propozycja dalszego sprawdzenia. |
| affected_record_ids / affected_scope_id | Techniczne wskazanie miejsca problemu, jeżeli applicable. |

Dopuszczalne technical_verification_suggestion obejmuje np. sprawdzenie mapowania kolumn, formatu daty, alternatywnej nazwy kolumny, rekordu źródłowego, duplikatu klucza lub zgodności jednostki.

Niedopuszczalne są interpretacje biznesowe, np. uznanie pozycji za korektę księgową, ocena zasadności kosztu, uznanie odchylenia za błąd zarządczy lub zmiana biznesowej klasyfikacji.

describes_technical_verification_path = true

performs_business_interpretation = false

## 9. I — STRUCTURAL FIELD REQUIREMENT CONTRACT

### 9.1. Techniczne record_id

record_id_required = true

record_id_null_allowed = false

record_id_unique_within_dataset = true

record_id_deterministic = true

inferred_natural_key_allowed = false

record_id jest technicznym metadata field, a nie nowym polem biznesowym bazowej tabeli. Nie oznacza business entity identity ani analytical grain.

Wiążący sposób tworzenia record_id:

record_id = "REC-" + SHA256(canonical UTF-8 JSON {source_artifact_SHA256, source_object_or_sheet_id, source_row_ordinal})

source_row_ordinal oznacza fizyczny ordinal rekordu w exact source object, niezależny od późniejszego sortowania modelu wewnętrznego. Dla arkusza jest to numer źródłowego wiersza; dla CSV fizyczny ordinal rekordu zgodnie z import manifestem. Losowy UUID nie może być jedyną podstawą identity.

### 9.2. Finalna macierz bazowych tabel

| table_id | record identity | fields_required_for_base_table_contract | fields_optional |
|---|---|---|---|
| ACTIVITY | record_id | date, unit, product, volume, revenue | NONE |
| COST | record_id | date, unit, category, amount | NONE |
| RESOURCE | record_id | date, unit, resource, available, used, cost | NONE |
| PROCESS | record_id | case_id, stage, start, end, unit | NONE |
| PLAN | record_id | date, unit, metric, target | NONE |

Dla record_id value_level_nullability = NOT_NULL. Dla wszystkich wymienionych source fields null jest dopuszczalny wyłącznie na etapie ingestion z obowiązkową walidacją; nie oznacza to poprawności ani eligibility do kalkulacji.

COLUMN_MISSING → STRUCTURAL_SCHEMA_FAILURE

COLUMN_PRESENT_VALUE_NULL → MISSING_VALUE → VALUE_LEVEL_VALIDATION_ISSUE

silent_null_acceptance = false

silent_imputation = false

default_value_substitution = false

Jeżeli test wymaga wartości, required_value_missing → record_not_creditable_for_that_calculation oraz właściwy source-defined validation/module status. Optional table dla konkretnego testu nie oznacza optional fields w dostarczonej bazowej tabeli.

Pola rozszerzeń Core 10 nie są automatycznie częścią ZOP-TECH-01 base table contract; ich required/conditional/optional status pochodzi z konkretnej karty.

Nie ustanawia się case_id + stage ani case_id + stage + start jako globalnego naturalnego klucza PROCESS.

## 10. J — EXCLUSION RECORD CONTRACT

| Pole | Reguła |
|---|---|
| exclusion_code | Kod przyczyny w wersjonowanym namespace. |
| exclusion_namespace | Np. FIN.*, CAP.*, PROC.*, COMMON.* lub deterministyczny odpowiednik właściwego kontraktu; brak globalnego zamkniętego katalogu wszystkich przyszłych typów/kodów. |
| exclusion_subject_type | Source-defined techniczny typ identity wyłączanego obiektu, np. RECORD, CASE, RESOURCE, PRODUCT, UNIT, CATEGORY, SCOPE albo inny jawny typ kontraktu. |
| exclusion_subject_id | Kanoniczna identity konkretnego wyłączanego obiektu; np. record_id, source-defined case/resource identity albo scope_id. Human-readable label nie jest wystarczająca. |
| scope | scope_id zgodny z Scope Identity Contract. |
| period | Kanoniczny okres obowiązywania wyłączenia. |
| source | Identyfikator źródła/evidence, na którym opiera się exclusion. |
| basis | Audytowalna podstawa wyłączenia. |
| originating_test_or_contract | Test/kontrakt, który zapisał link do exclusion; nie jest częścią cross-test semantic subject identity. |
| exclusion_id | "EXCL-" + SHA256(canonical JSON {exclusion_namespace, exclusion_code, exclusion_subject_type, exclusion_subject_id, scope_id, period, source}). |
| calculation_component_id | Komponent kalkulacji, w którym exclusion wywiera skutek; canonical null, jeżeli właściwy test nie rozróżnia komponentów. |
| result_identity_or_calculation_identity | Tożsamość konkretnej kalkulacji/result context, w którego granicach działa ochrona przed double counting. |
| exclusion_application_key | "EXAPP-" + SHA256(canonical JSON {result_identity_or_calculation_identity, calculation_component_id, exclusion_subject_type, exclusion_subject_id}). |

Nie powstaje jeden sztuczny globalny katalog wszystkich przyszłych kodów. Wspólna jest struktura rekordu oraz mechanizm identity/linkowania.

same_exclusion_can_be_linked_cross_test = true

double_counting_protection_supported = true

exclusion_id identyfikuje konkretny zapis przyczyny wyłączenia, nie sam efekt wyłączenia. Ten sam subject może posiadać wiele exclusion_id dla różnych udokumentowanych przyczyn. multiple_exclusion_reasons_for_same_subject_allowed = true; multiple_exclusion_records_for_same_subject_allowed = true; multiple_exclusion_effects_on_same_subject_same_component = false. W granicach jednego result_identity_or_calculation_identity + calculation_component_id dany exclusion_subject może zmniejszyć populację, mianownik lub zbiór obliczeniowy co najwyżej raz. Dwa exclusion_code dla tego samego subject mogą więc tworzyć dwa exclusion_id, ale jeden exclusion_application_key i jeden faktyczny efekt. Cross-test linking przez kanoniczną subject identity jest dozwolony, lecz cross_test_exclusion_effect_automatic_propagation = false; każdy test stosuje własny frozen contract. Dla aggregate exclusion: exclusion_subject_type = SCOPE oraz exclusion_subject_id = scope_id; nie tworzy się sztucznego record_id.

## 11. K — validation_required / PRI-01 BINDING

| Pole / własność | Właściciel semantyki | Reguła |
|---|---|---|
| validation_required | source engine / frozen karta | Faktyczny stan źródłowy true/false; immutable dla historycznego wyniku. |
| validation_priority_action | ZOP-PRI-01 | Osobna kwalifikacja pilności/trybu walidacji. |
| validation_priority_basis | ZOP-PRI-01 | Audytowalna podstawa kwalifikacji. |
| problem_priority_action | ZOP-PRI-01 | Niezależne od validation_required. |
| confidence | ZOP-CONF-01 | Nie zastępuje execution completeness ani validation priority. |

source_validation_required_is_immutable_for_that_result = true

PRI_01_may_change_validation_priority = true

PRI_01_may_clear_source_validation_required = false

Jeżeli późniejsza walidacja rozwiąże problem, nie mutuje się historycznego findingu. Powstaje nowy wynik/stan albo jawny resolution record zgodnie z właściwym storage contract.

execution completeness ≠ validation requirement ≠ validation priority ≠ problem priority ≠ confidence.

TEST_PARTIAL nie jest niskim confidence; CRITICAL walidatora nie jest problem severity; validation_required nie jest synonimem validate_now.

## 12. WŁAŚCICIELE SEMANTYKI I IMMUTABILITY

| Kontrakt | Właściciel semantyki | Immutable / granica |
|---|---|---|
| MODULE / VALIDATION DEPENDENCY | Frozen karta + ten binding techniczny | module_id/status logic binding nie może zmieniać matematyki testu. |
| SCOPE / REFERENCE / RESULT IDENTITY | ZOP-XR-FOUNDATION-BIND-01 + scope/reference fields frozen kart | Human labels nie mogą zmieniać identity. |
| VERSION COMPATIBILITY | Release nowej wersji karty / Controlling | Historyczne wyniki nie są przeliczane ani nadpisywane automatycznie. |
| DATASET CURRENCY | Profil wejściowy + FOUNDATION-BIND | Brak ukrytego FX. |
| VALIDATION MESSAGE | Frozen validator + FOUNDATION-BIND | Technical suggestion nie może przejść w interpretację biznesową. |
| BASE TABLE STRUCTURE / record_id | ZOP-TECH-01 + Decision 08 | record_id to technical source-record identity; base fields nie są optional. |
| EXCLUSION RECORD | Frozen karta/rodzina/common contract + FOUNDATION-BIND | Namespace nie jest globalnym słownikiem wszystkich przyczyn. |
| validation_required / PRI | Source karta / PRI-01 | PRI nie mutuje źródłowego validation_required. |

## 13. SCENARIUSZE AKCEPTACYJNE KONTRAKTU

| ID | Scenariusz | Wejście | Oczekiwany kontrakt |
|---|---|---|---|
| T01 | Global CRITICAL | GLOBAL_TEST prerequisite = CRITICAL | TEST_BLOCKED |
| T02 | Local CRITICAL | Module A CRITICAL/local; Module B executed | A=MODULE_BLOCKED; B=MODULE_EXECUTED; TEST_PARTIAL |
| T03 | Scope label collision | Ta sama label, różne filters | scope_id różne |
| T04 | Dwie referencje | Ten sam analysis_period, dwa reference_period | dwa result_identity |
| T05 | Non-semantic metadata | Dodane optional non-semantic metadata | COMPATIBLE jest dopuszczalne |
| T06 | Formula change | Zmiana wzoru | INCOMPATIBLE, chyba że bardziej szczegółowy frozen contract stanowi inaczej |
| T07 | Mixed currencies | Dwie waluty w monetary input bez legalnego ujednolicenia | monetary_modules_execution_allowed = false |
| T08 | Missing amount column | COST bez kolumny amount | COLUMN_MISSING; STRUCTURAL_SCHEMA_FAILURE |
| T09 | Null amount | amount istnieje; wartość null | MISSING_VALUE; nie COLUMN_MISSING; dalszy status wg source validation |
| T10 | PRI low urgency | validation_required=true; PRI ustala niski validation priority | validation_required pozostaje true |
| T11 | Cross-test exclusion lineage | Dwa testy wskazują ten sam exclusion_subject_id i ten sam exclusion_id | subject identity/exclusion lineage linkable; brak automatycznej propagacji skutku między testami |
| T12 | Version history | Istnieje wynik v1.0 i wynik v1.1 | v1.0 pozostaje immutable; v1.1 jest nowym wynikiem/wersją identity |
| T13 | Zero applicable modules | Wszystkie applicability resolved; applicable_module_count = 0 | TEST_NOT_APPLICABLE; technical execution record required; no diagnostic finding required |
| T14 | Reference provenance changes | Ta sama semantic reference; inna physical copy lub corrected exact bytes bez zmiany logical semantic source | same reference_id; nowy immutable execution/result record z nowym provenance/SHA/value |
| T15 | Multiple exclusion reasons | Ten sam subject + dwa exclusion_code w jednej kalkulacji i tym samym component | dwa exclusion_id; jeden exclusion_application_key; jeden faktyczny efekt wyłączenia |

## 14. WARUNKI GOTOWOŚCI DLA IMPLEMENTATORA

Po release Aleksander ma móc bez decyzji metodologicznej odpowiedzieć, jak zadeklarować moduł; kiedy moduł/test się blokuje; kiedy test jest partial; jak zbudować scope_id i result_identity; jak reprezentować reference; jak ocenić comparison compatibility; jak obsłużyć walutę; jak odróżnić missing column od null; jak zapisać exclusion; kto ustawia validation_required i czego PRI-01 nie może zmienić.

CONTRACT_IMPLEMENTATION_AMBIGUITY_COUNT = 0

FOUNDATION_BIND_ACTIVE = false

Do momentu Controlling release Aleksander zachowuje obecny branch/kod i nie implementuje rozstrzyganych punktów według własnego uznania.

## 15. SELF-CHECK ARCHITEKTA

| Kontrola | Wynik |
|---|---|
| all_10_questions_resolved | true |
| new_methodology_created | false |
| Core_10_changed | false |
| ZOP_TECH_01_changed | false |
| PRI_01_changed | false |
| CONF_01_changed | false |
| ORCH_01_changed | false |
| Lab_only_knowledge_used | false |
| module_contract_complete | true |
| scope_identity_deterministic | true |
| result_identity_deterministic | true |
| reference_identity_explicit | true |
| version_compatibility_explicit | true |
| currency_contract_explicit | true |
| validator_business_interpretation_allowed | false |
| structural_missing_vs_null_separated | true |
| exclusion_common_mechanism_defined | true |
| validation_required_vs_PRI_separated | true |
| implementation_ambiguity_count | 0 |
| FIELD_REQUIREMENT_CONFLICT_OR_GAP | false |
| DECISION_08_RESOLVED | true |
| INFERRED_NATURAL_KEY_CREATED | false |
| BASE_TABLE_CONTRACT_DEFINED | true |
| MISSING_COLUMN_VS_NULL_SEPARATED | true |
| A01_ZERO_APPLICABLE_MODULES | RESOLVED |
| A02_REFERENCE_SEMANTIC_IDENTITY_VS_PROVENANCE | RESOLVED |
| A03_EXCLUSION_SUBJECT_IDENTITY | RESOLVED |
| OPEN_IMPLEMENTATION_AMBIGUITIES | 0 |
| CONTRACT_IMPLEMENTATION_AMBIGUITY_COUNT | 0 |
| ALL_10_DECISIONS_SUBSTANTIVELY_MATERIALIZED | true |

## 16. STATUS I ŚCIEŻKA ZATWIERDZENIA

ARCHITECT_REVIEW = COMPLETE

ALL_10_DECISIONS_SUBSTANTIVELY_MATERIALIZED = true

IMPLEMENTATION_AMBIGUITY_COUNT = 0

READY_FOR_CONTROLLING_REVIEW = true

FOUNDATION_BIND_ACTIVE = false

Następna decyzja należy do Controllingu. Kontrakt nie jest aktywowany przez Architekta. Nie wykonano kodu, nie zmodyfikowano branch Aleksandra i nie uruchomiono Laboratorium.

CONTROLLING_RELEASE_FOR_IMPLEMENTATION = false

STOP
