ZOPTYMALIZOWANI – X-RAY

# CONF-01

*Standard oceny pewności wyników diagnostycznych X-Ray*

Karta metodologiczna i specyfikacja implementacyjna

| METADANE DOKUMENTU | WARTOŚĆ |
| --- | --- |
| Identyfikator | ZOP-CONF-01 |
| Wersja | v1.0 |
| Status | ZAMKNIĘTY METODOLOGICZNIE DO IMPLEMENTACJI |
| Zakres | Ocena siły wsparcia miary, wyniku diagnostycznego i mechanizmu przez jawne dowody |
| Zależności | Core 10 i ZOP-PRI-01 – ZAMROŻONE; pełna orkiestracja next_tests – DO OPRACOWANIA |
| Odbiorca implementacyjny | Aleksander / warstwa technologiczna X-Ray |

> **PYTANIE DIAGNOSTYCZNE Jak mocno dostępne dowody wspierają konkretną miarę, wynik diagnostyczny albo interpretację mechanizmu – oraz jakie ograniczenia tej pewności pozostają jawne?**

## 1. Rola, cel i granice CONF-01

CONF-01 ocenia siłę wsparcia konkretnego twierdzenia diagnostycznego. Podstawową jednostką nie jest test jako całość ani organizacja, lecz jedno jawne twierdzenie osadzone w zakresie, okresie, kontekście i wersji podstawy dowodowej.

| CONF-01 robi | CONF-01 nie robi |
| --- | --- |
| ocenia pewność miary, wyniku i mechanizmu | nie ustala ważności problemu ani kolejności uwagi |
| wiąże klasę z wymaganymi bramami i dowodami | nie ocenia pełnej gotowości informacyjnej decyzji |
| ujawnia ograniczenia, konflikty i walidacje | nie tworzy prawdopodobieństwa prawdziwości |
| przekazuje kontrakt do PRI-01 i przyszłej orkiestracji | nie projektuje pełnej orkiestracji next_tests |
| działa deterministycznie bez AI | nie wydaje rekomendacji wykonawczych |

### 1.1. Nienaruszalne rozdzielenia

| Rozdzielenie | Znaczenie implementacyjne |
| --- | --- |
| confidence ≠ priority | siła wsparcia twierdzenia nie ustala znaczenia ani pilności problemu |
| confidence ≠ decision readiness | pewność konkretnego twierdzenia nie przesądza kompletności informacji do decyzji |
| confidence ≠ probability | klasa jakościowa nie jest procentem prawdopodobieństwa prawdziwości |
| metric confidence ≠ finding confidence | poprawnie wyliczona liczba nie przesądza, że wspiera pełną treść wyniku |
| finding confidence ≠ mechanism confidence | potwierdzony sygnał nie jest automatycznie potwierdzoną przyczyną |
| hypothesis ≠ confirmed mechanism | hipoteza wymaga dowodu odnoszącego się do mechanizmu |
| correlation ≠ causal proof | współwystępowanie nie dowodzi związku przyczynowego |
| shared source ≠ independent evidence | kilka testów na wspólnej podstawie nie stanowi niezależnej triangulacji |
| absence of evidence ≠ contradictory evidence | brak wsparcia nie jest dowodem przeciwnym |

### 1.2. Hierarchia źródeł i ochrona dokumentów zamrożonych

| Poziom | Źródła | Reguła |
| --- | --- | --- |
| 1 | niniejsze polecenie; ZOP-XR-MGT-01 v1.0; ZOP-PRI-01 v1.0 | źródła nadrzędne kontraktu przekrojowego |
| 2 | FIN-01, FIN-02, FIN-03, CAP-01, CAP-02, HR-01, PORT-01, PROC-01, PROC-02 | lokalne kontrakty testów pozostają bez zmian |
| 3 | ZOP-TECH-01; bieżący ZOP-MASTER-01 | kontekst fundamentu technologicznego i rozwoju produktu |

> **ZASADA ZAMROŻENIA Core 10 oraz ZOP-PRI-01 pozostają niezmienione. Jawny konflikt źródeł jest zachowywany i wpływa na ocenę pewności; CONF-01 nie rozstrzyga go arbitralnie.**

## 2. Jednostka oceny i trzy poziomy pewności

| Poziom | Pole klasy | Pytanie |
| --- | --- | --- |
| pewność miary | metric_confidence_class | Czy miara została odpowiedzialnie wyliczona i opisuje właściwy zakres? |
| pewność wyniku diagnostycznego | finding_confidence_class | Czy test i dane wspierają sformułowany sygnał diagnostyczny? |
| pewność mechanizmu | mechanism_confidence_class | Czy dowody wspierają określone wyjaśnienie mechanizmu? |

> **PRZYKŁAD ROZDZIELENIA metric_confidence_class = well_supported; finding_confidence_class = well_supported; mechanism_confidence_class = weakly_supported. Klasy nie są automatycznie przenoszone między poziomami.**

### 2.1. Powiązanie twierdzenia z właściwą klasą

Jeden claim_id reprezentuje jedno konkretne twierdzenie, a claim_type wskazuje jego poziom. Klasa właściwa dla claim_type jest klasą podstawową rekordu. Jeżeli trzy poziomy są prezentowane razem dla jednej ścieżki diagnostycznej, pozostają trzema oddzielnymi ocenami twierdzeń, również wtedy, gdy warstwa prezentacyjna pokazuje je w jednym widoku.

| claim_type | Klasa podstawowa | confidence_class_source_level |
| --- | --- | --- |
| metric_claim | metric_confidence_class | metric_confidence |
| finding_claim | finding_confidence_class | finding_confidence |
| mechanism_claim | mechanism_confidence_class | mechanism_confidence |

> **REGUŁA PRZEKAZANIA KLASY confidence_class przekazywana dalej musi odpowiadać confidence_class_source_level. Nie wolno przepisywać klasy z jednego poziomu na drugi.**

### 2.2. Wspólny katalog klas

| Klasa techniczna | Warstwa użytkowa | Znaczenie ogólne |
| --- | --- | --- |
| well_supported | dobrze potwierdzone | wymagane bramy przechodzą; podstawa jest wystarczająca dla danego typu twierdzenia |
| supported_with_limitations | potwierdzone z ograniczeniami | twierdzenie ma odpowiedzialną podstawę, lecz pozostają jawne nieblokujące ograniczenia |
| partially_supported | częściowo potwierdzone | wsparcie dotyczy tylko części treści lub zakresu; wymagane jest zawężenie |
| weakly_supported | słabo potwierdzone | istnieje realny sygnał, ale podstawa nie jest stabilna bez dalszej walidacji |
| not_assessable | brak podstaw do oceny | nie można odpowiedzialnie ocenić twierdzenia na dostępnej podstawie |

> **ZAKAZ WSKAŹNIKA confidence_score = null. CONF-01 nie tworzy wyniku 0–100, wag, średniej ważonej, arbitralnych progów ani katalogu HIGH/MEDIUM/LOW.**

## 3. Kontrakt twierdzenia diagnostycznego

| Pole | Wymagalność | Kontrakt |
| --- | --- | --- |
| claim_id | required | trwały identyfikator twierdzenia |
| claim_type | required | metric_claim; finding_claim; mechanism_claim |
| claim_text | required | oryginalna treść ocenianego twierdzenia; nie jest nadpisywana przy zawężeniu |
| claim_scope | required | zakres, którego dotyczy twierdzenie |
| claim_period | required | okres lub punkt czasu właściwy dla twierdzenia |
| claim_source_test | required | identyfikator testu źródłowego |
| claim_source_finding_id | conditional | identyfikator wyniku źródłowego, jeśli twierdzenie powstało z FINDINGS |
| claim_version | required | wersja treści twierdzenia; zmiana treści tworzy nową wersję |
| confidence_context | required | kontekst użycia, w którym oceniana jest siła wsparcia |

Jedna ocena CONF-01 dotyczy jednego claim_id, claim_type, claim_scope, claim_period i confidence_context. Rozszerzenie zakresu, zmiana okresu albo zmiana treści nie dziedziczą automatycznie wcześniejszej klasy.

### 3.1. Wymagania informacyjne właściwe dla twierdzenia

| Pole | Reguła |
| --- | --- |
| claim_required_information_objects | obiekty informacji niezbędne do oceny konkretnego twierdzenia |
| claim_required_dimensions | wymiary MGT-01 wymagane dla tego twierdzenia; nie wszystkie wymiary organizacji |
| claim_required_validations | walidacje, których brak może ograniczyć albo zablokować klasę |
| claim_allowed_limitations | ograniczenia akceptowalne bez utraty odpowiedzialnej podstawy |

## 4. Kontrakt dowodu

| Pole | Kontrakt |
| --- | --- |
| evidence_id | jednoznaczny identyfikator rekordu dowodowego |
| evidence_type | rodzaj informacji lub wyniku stanowiącego dowód |
| evidence_source | źródło z zachowaniem identyfikatora i wersji |
| evidence_scope | zakres objęty dowodem |
| evidence_period | okres objęty dowodem |
| evidence_role | primary_evidence; supporting_evidence; contextual_evidence; contradictory_evidence; validation_evidence |
| evidence_group_id | grupa rekordów opisujących ten sam dowód lub zdarzenie |
| evidence_source_group_id | grupa wspólnego źródła używana do ochrony niezależności |
| evidence_traceability_status | status możliwości prześledzenia dowodu do źródła i transformacji |

### 4.1. Role dowodów

| Rola | Znaczenie | Ograniczenie |
| --- | --- | --- |
| primary_evidence | dowód główny wymagany dla twierdzenia | jego braku nie zastępuje dowód wspierający |
| supporting_evidence | dowód dodatkowo wspierający twierdzenie | nie działa jak kolejny głos ani samodzielna podstawa, gdy wymagany jest primary_evidence |
| contextual_evidence | dowód opisujący kontekst interpretacji | nie podnosi klasy tak jak dowód bezpośredni |
| contradictory_evidence | jawny dowód sprzeczny z twierdzeniem lub jego częścią | pozostaje widoczny także przy wysokiej klasie |
| validation_evidence | dowód wykonania i wyniku wymaganej walidacji | nie zmienia źródłowej miary; aktualizuje podstawę oceny |

> **REGUŁA BRAKU DOWODU Brak dowodu wspierającego nie jest dowodem przeciwnym. contradictory_evidence wymaga jawnego źródła sprzeczności.**

## 5. Niezależność dowodów i zgodność wielu testów

| evidence_independence_status | Znaczenie |
| --- | --- |
| documented_independent | pochodzenie i transformacje dowodów są udokumentowane jako niezależne |
| partly_shared | część źródła, mapowania albo transformacji jest wspólna |
| shared_source | dowody korzystają z tego samego źródła lub podstawowego rekordu |
| unknown | nie ma wystarczającej podstawy do oceny niezależności |

| Pole | Reguła |
| --- | --- |
| independent_evidence_count | liczba udokumentowanych niezależnych grup dowodowych; nie jest wynikiem punktowym |
| shared_source_flag | true, gdy co najmniej dwa dowody mają wspólne źródło istotne dla twierdzenia |
| shared_transformation_flag | true, gdy odrębne wyniki korzystają z tej samej istotnej transformacji |
| independence_basis | audytowalne uzasadnienie statusu niezależności |
| evidence_independence_required | true, gdy metodologia źródłowa wymaga niezależnego potwierdzenia albo wysoka klasa mechanizmu zależy od rzeczywistej niezależności triangulowanych dowodów |
| evidence_independence_requirement_basis | audytowalna podstawa ustalenia, czy niezależność jest wymagana |
| evidence_independence_sufficient | true tylko wtedy, gdy wymagana niezależność została odpowiedzialnie wykazana |

> **DETERMINISTYCZNY WYMÓG NIEZALEŻNOŚCI Jeżeli evidence_independence_required = true i evidence_independence_sufficient = false, mechanism_confidence_class = well_supported jest niedopuszczalne. evidence_independence_required = false może być dopuszczalne, gdy jeden dowód główny samodzielnie i bezpośrednio weryfikuje mechanizm zgodnie z zamrożoną metodologią testu źródłowego. Dwa źródła nie oznaczają automatycznie well_supported.**

### 5.1. Zgodność wielu testów

| cross_test_support_status | Znaczenie |
| --- | --- |
| consistent | testy wspierają to samo twierdzenie i nie ma istotnej sprzeczności semantycznej |
| consistent_with_limitations | kierunek jest zgodny, lecz istnieją ograniczenia zakresu, źródła lub niezależności |
| mixed | część dowodów wspiera, a część nie wspiera albo dotyczy tylko fragmentu twierdzenia |
| contradictory | istnieje jawna sprzeczność dowodów odnoszących się do twierdzenia |
| not_assessable | nie można odpowiedzialnie ocenić zgodności |

Pola supporting_tests, contradictory_tests i cross_test_support_basis dokumentują źródła oceny. Liczba testów nie jest liczbą głosów. Zgodność kilku testów korzystających z jednego źródła pozostaje widoczna, ale nie stanowi pełnej niezależnej triangulacji.

## 6. MGT-01 jako podstawa informacyjna

CONF-01 dziedziczy semantykę informacji z MGT-01 i nie tworzy jej lokalnych odpowiedników. Statusy MGT są wejściem do oceny wymaganych elementów twierdzenia, a nie automatycznym przelicznikiem klasy pewności.

| Wejście z MGT-01 | Sposób użycia w CONF-01 |
| --- | --- |
| decision_information_status | kontekst gotowości informacyjnej decyzji; nie jest klasą pewności |
| information_dimension_statuses | rekordy name + status + basis oraz ograniczenia, dowody i wymagana walidacja |
| critical_information_gap | wpływa tylko wtedy, gdy luka dotyczy informacji wymaganej dla ocenianego twierdzenia |
| definition_status / scope_status / period_alignment_status | wejścia do właściwych bram bez redefinicji |
| coverage_current / coverage_reference / coverage_basis | pokrycie oceniane względem claim; bez globalnego progu |
| lineage_status / traceability_status / reproducibility_status | podstawa bramy pochodzenia i odtwarzalności |
| reconciliation_status | rozróżnia m.in. reconciled, reconciled_with_explanation, unreconciled i not_comparable |
| trend_comparability_status | comparable; partially_comparable; not_comparable; unknown |
| manual_data_validation_status | walidacja danych ręcznych bez automatycznego obniżenia ich klasy |
| estimate_flag / estimate_basis / assumption_flag | zachowanie rozdzielenia wartości zmierzonej, szacunku i założenia |
| data_conflict_flag | jawne wejście do conflict_gate |

> **STATUS MGT ≠ KLASA PEWNOŚCI fit nie oznacza automatycznie well_supported. failed w wymiarze niewymaganym dla claim nie oznacza automatycznie not_assessable. decision_blocked może współistnieć z dobrze potwierdzonym wynikiem.**

## 7. Bramy oceny pewności

| Katalog statusów bramy | Znaczenie |
| --- | --- |
| pass | wymaganie dla twierdzenia jest spełnione |
| pass_with_limitations | wymaganie jest spełnione z jawnym, nieblokującym ograniczeniem |
| partial | wymaganie jest spełnione tylko dla części twierdzenia lub zakresu |
| fail | brak wymaganego elementu lub występuje blokada uniemożliwiająca utrzymanie pełnego twierdzenia |
| not_assessable | brak podstaw do oceny samej bramy |

| Brama | Co sprawdza | Reguła krytyczna |
| --- | --- | --- |
| required_information_gate | dostępność informacji wymaganej dla twierdzenia | brak wymaganego elementu = fail; brak progu procentowego liczby pól |
| definition_semantics_gate | jednoznaczność definicji i spójność semantyczna | sprzeczna lub niejednoznaczna definicja elementu wymaganego ogranicza albo blokuje claim |
| scope_period_gate | zgodność zakresu i okresu danych, miary i twierdzenia | mieszane zakresy wymagają jawnego uzgodnienia; klasa nie przechodzi z matched na full scope |
| comparability_gate | porównywalność wartości bieżącej i odniesienia, trendu, rankingu lub mostu | nieporównywalna wartość odniesienia nie usuwa poprawnej miary bieżącej, lecz blokuje twierdzenie o zmianie |
| lineage_reproducibility_gate | pochodzenie, transformacje, wzór i odtwarzalność | pełna automatyzacja nie jest wymagana; wymagany jest adekwatny ślad |
| reconciliation_gate | uzgodnienie źródeł, testów albo warstw kosztu | reconciled_with_explanation nie jest błędem; unresolved required może blokować |
| conflict_gate | wpływ jawnych konfliktów danych | nierozwiązany konflikt required nie może zostać pominięty ani rozstrzygnięty arbitralnie |
| estimate_assumption_gate | rola szacunku i założenia w podstawie | udokumentowany estimate może być legalnym dowodem; unsupported essential assumption blokuje wysoką klasę |
| evidence_independence_gate | niezależność dowodów adekwatna do typu twierdzenia | twierdzenie o mierze i wyniku nie wymaga wielu źródeł; twierdzenie o mechanizmie ma ostrzejszy wymóg |
| mechanism_evidence_gate | dowód odnoszący się do samego wyjaśnienia mechanizmu | hipoteza, korelacja lub zgodny kierunek nie wystarczają do dobrze potwierdzonego mechanizmu |

### 7.1. Wymagalność bram według typu twierdzenia

| Brama | metric_claim | finding_claim | mechanism_claim |
| --- | --- | --- | --- |
| required_information_gate | required | required | required |
| definition_semantics_gate | required | required | required |
| scope_period_gate | required | required | required |
| comparability_gate | required dla porównań | required dla wyniku porównawczego | required, gdy mechanizm opiera się na zmianie |
| lineage_reproducibility_gate | required | required | required |
| reconciliation_gate | conditional | conditional | conditional |
| conflict_gate | required, gdy istnieje konflikt | required, gdy istnieje konflikt | required, gdy istnieje konflikt |
| estimate_assumption_gate | conditional | conditional | conditional |
| evidence_independence_gate | ocena jawna; niezależność niewymagana | ocena jawna; może wzmacniać | required w zakresie wynikającym z mechanizmu |
| mechanism_evidence_gate | not_applicable | not_applicable | required |

## 8. Deterministyczna reguła klasyfikacji

| Warunek nadrzędny | Dopuszczalny wynik |
| --- | --- |
| co najmniej jedna wymagana brama = fail | well_supported oraz supported_with_limitations są niedopuszczalne; wynik zależy od zachowanej podstawy albo = not_assessable |
| co najmniej jedna wymagana brama = partial | co najwyżej partially_supported albo weakly_supported; pełne twierdzenie wymaga zawężenia lub odrzucenia |
| wszystkie wymagane bramy = pass i brak krytycznych ograniczeń | well_supported jest dopuszczalne po spełnieniu warunków właściwych dla claim_type |
| wymagane bramy = pass / pass_with_limitations i istnieją niekrytyczne ograniczenia | supported_with_limitations, a ograniczenia są zapisane w confidence_limitations |
| brak podstaw do oceny wymaganej bramy | not_assessable dla pełnego twierdzenia, chyba że odpowiedzialnie możliwe jest jego zawężenie |

> **REGUŁA NADRZĘDNA Klasa wynika z wymaganych bram i jawnych ograniczeń, a nie z sumy punktów. Nie istnieje globalny limit klasy tylko dlatego, że pojedyncze pole ma status estimate, manual albo partial.**

### 8.1. Precedencja częściowego wsparcia, słabego wsparcia i braku podstaw

| Klasa | Wspólna reguła dla każdego claim_type |
| --- | --- |
| partially_supported | pełne twierdzenie nie ma kompletnej podstawy, lecz można jednoznacznie wydzielić odpowiedzialnie wspartą część; wymagane są claim_narrowing_required = true, narrowed_claim_text != null i wystarczająca podstawa dla zawężonej treści |
| weakly_supported | istnieje realny sygnał wspierający pełne twierdzenie, lecz nie można odpowiedzialnie wydzielić części dla partially_supported; ograniczenia wymagają walidacji przed traktowaniem twierdzenia jako stabilnej podstawy |
| not_assessable | brak wymaganej informacji lub wymaganego dowodu uniemożliwia odpowiedzialne wsparcie zarówno pełnego, jak i możliwego zawężonego twierdzenia |

| Krok | Kolejność kwalifikacji |
| --- | --- |
| 1 | sprawdź, czy twierdzenie może być ocenione w pełni |
| 2 | jeżeli nie — sprawdź, czy można odpowiedzialnie utworzyć narrowed_claim_text |
| 3 | jeżeli tak — partially_supported |
| 4 | jeżeli nie, ale istnieje rzeczywisty sygnał dowodowy — weakly_supported |
| 5 | jeżeli nie istnieje wystarczający sygnał — not_assessable |

Kolejność jest regułą kwalifikacji, a nie skalą punktową. Nie służy do sumowania, ważenia ani porównywania siły różnych twierdzeń.

### 8.2. Kolejność wykonania mechanizmu regułowego

| Krok | Operacja | Wynik |
| --- | --- | --- |
| 1 | Zidentyfikuj twierdzenie | claim_id, type, text, scope, period, source i version |
| 2 | Ustal wymagania twierdzenia | required objects, dimensions, validations i allowed limitations |
| 3 | Powiąż dowody | role, scope, period, source group i traceability |
| 4 | Oceń niezależność | status, flags, count i basis bez głosowania |
| 5 | Oceń zgodność testów | supporting/contradictory tests i cross_test_support_status |
| 6 | Pobierz wejścia MGT-01 | statusy i pola źródłowe bez redefinicji |
| 7 | Uruchom bramy właściwe dla twierdzenia | status każdej bramy z audytowalną podstawą |
| 8 | Zastosuj reguły claim_type | oddzielna klasa metric, finding albo mechanism |
| 9 | Zapisz ograniczenia i konflikty | limitations, critical flag, conflict status i counts |
| 10 | Rozstrzygnij zawężenie lub odrzucenie | oryginalny claim pozostaje zachowany |
| 11 | Zapisz walidację i stabilność | validation action oraz change_reason bez ustalania priorytetu |
| 12 | Zbuduj wynik | FINDINGS, payload PRI i dane dla przyszłej orkiestracji |

## 9. Reguły klas dla pewności miary

| Klasa | Warunek zastosowania |
| --- | --- |
| well_supported | required_information_gate, definition_semantics_gate i scope_period_gate przechodzą; walidacje wymagane nie mają blokady; wynik jest odtwarzalny; dla miary porównawczej przechodzi comparability_gate |
| supported_with_limitations | miara jest odpowiedzialnie obliczalna, lecz występuje jawne niekrytyczne ograniczenie, np. częściowe pochodzenie, ograniczone pokrycie, udokumentowany szacunek lub jakość alokacji |
| partially_supported | odpowiedzialnie dostępna jest część zakresu, okresu lub składowych i twierdzenie zostało odpowiednio zawężone |
| weakly_supported | istnieje realny sygnał liczbowy, ale istotne ograniczenia wymagają walidacji przed traktowaniem miary jako stabilnej podstawy |
| not_assessable | brak required information, definicji, zakresu albo walidacji uniemożliwia odpowiedzialne określenie miary |

Brak wartości odniesienia nie blokuje poprawnej miary bieżącej. Może natomiast spowodować not_assessable dla twierdzenia o zmianie wartości bieżącej względem odniesienia.

## 10. Reguły klas dla pewności wyniku diagnostycznego

| Klasa | Warunek zastosowania |
| --- | --- |
| well_supported | test źródłowy oraz jego kompletna i wystarczająca podstawa wspierają treść wyniku diagnostycznego; wiele testów nie jest wymagane |
| supported_with_limitations | wynik diagnostyczny ma wystarczającą podstawę, a ograniczenia są jawne i nieblokujące |
| partially_supported | wsparta jest tylko część wyniku diagnostycznego; pełna treść musi zostać zawężona |
| weakly_supported | istnieje sygnał diagnostyczny, lecz podstawa pełnego wyniku jest słaba albo wymaga walidacji |
| not_assessable | brak podstaw do odpowiedzialnej oceny wyniku diagnostycznego |

> **NO_ADVERSE_SIGNAL Może być dobrze potwierdzonym wynikiem tylko wtedy, gdy test miał wystarczającą zdolność wykrycia badanego zjawiska w swoim zakresie. Nie dowodzi braku problemu poza tym zakresem.**

## 11. Reguły klas dla pewności mechanizmu

| Klasa | Warunek zastosowania |
| --- | --- |
| well_supported | mechanizm jest jawnie zweryfikowany przez metodologię źródłową albo wsparty spójnymi dowodami odnoszącymi się do mechanizmu, bez krytycznej sprzeczności i z udokumentowaną niezależnością tam, gdzie jest potrzebna |
| supported_with_limitations | mechanizm ma realne wsparcie, lecz pozostaje ograniczenie pokrycia, niezależności, porównywalności albo zakresu |
| partially_supported | wsparta jest część mechanizmu; pełna interpretacja jest zbyt szeroka i wymaga narrowed_claim_text |
| weakly_supported | istnieje hipoteza albo sygnał zgodny z mechanizmem, ale brak bezpośredniej podstawy potwierdzającej |
| not_assessable | brak dowodów odnoszących się do mechanizmu albo wymagana brama mechanizmu nie przechodzi |

> **WYŻSZY PRÓG DOWODOWY Pewność mechanizmu ma wyższy próg niż pewność wyniku. hypothesis / hypothesis_to_verify, korelacja lub zgodny kierunek wskaźników nie wystarczają do mechanism_confidence_class = well_supported.**

### 11.1. Zweryfikowany mechanizm i zweryfikowane ograniczenie

Jawny status verified mechanism, verified constraint albo równoważny status z karty źródłowej może stanowić podstawę oceny mechanizmu wyłącznie zgodnie z warunkami tej metodologii. CONF-01 nie rozszerza zakresu takiej weryfikacji i nie zmienia statusu testu źródłowego.

## 12. Reguły dziedzinowe bez zmiany Core 10

| Obszar | Elementy oceny pewności | Nienaruszalna granica |
| --- | --- | --- |
| FIN-02 / FIN-03 – most | uzgodnienie, porównywalność składników, zgodność zakresu; bridge_confidence_class i bridge_confidence_basis | CONF-01 nie tworzy nowej matematyki mostu |
| FIN / PORT – koszty i portfel | przypisanie kosztów, dopasowany zakres, porównywalność, one-off, reklasyfikacja i poprawność mianownika | nie przelicza wyników finansowych i nie tworzy polityki kosztowej |
| alokacja kosztów wspólnych | allocation_quality, podstawa alokacji i porównywalność wartości bieżącej z odniesieniem | allocation_confidence_class dotyczy alokacji, nie całego wyniku diagnostycznego |
| HR / CAP / PROC | work_content, mapowanie capacity, podstawa kalendarza i zastępowalność zasobów zgodnie ze źródłami | lokalne twierdzenie może być ocenione; globalne kontrakty pozostają otwarte |
| PROC-01 / PROC-02 | timestamp quality, route definition, ready_at, calendar basis, constraint evidence i mechanism evidence | najdłuższy etap, największa kolejka lub najwyższe utilization nie są same w sobie mechanizmem |
| actual / adjusted | oddzielne twierdzenia, zakresy i podstawy korekty one-off | wartości nie są mieszane |

## 13. Zakres, okres, porównanie i aktualność

| Pole / przypadek | Reguła |
| --- | --- |
| confidence_scope | klasa odnosi się wyłącznie do jawnego zakresu twierdzenia |
| confidence_period | klasa odnosi się do okresu lub punktu czasu twierdzenia |
| matched scope / full scope | klasa nie jest przenoszona między zakresami; każdy wymaga własnej podstawy |
| current / reference | miara bieżąca może być dobrze potwierdzona przy braku podstaw do twierdzenia o zmianie |
| evidence_coverage_status | pokrycie jest oceniane względem twierdzenia, bez arbitralnego progu procentowego |
| evidence_coverage_basis | źródłowe uzasadnienie, które elementy twierdzenia są objęte dowodem |
| evidence_timeliness_fit | aktualność oceniana względem charakteru i okresu twierdzenia; bez globalnego progu wieku danych |

## 14. Konflikty, uzgodnienie, szacunki i pochodzenie danych

| Zasada | Kontrakt |
| --- | --- |
| konflikt źródeł | confidence_conflict_status: none; resolved; resolved_with_limitations; unresolved; not_assessable |
| dowody sprzeczne | contradictory_evidence_count pozostaje licznikiem rekordów, nie wynikiem punktowym; dowody nie są usuwane przez większość |
| rozstrzygnięcie konfliktu | conflict_resolution_status i podstawa; brak arbitralnego wyboru wartości większej, nowszej albo wygodniejszej |
| uzgodnienie | reconciled_with_explanation nie jest błędem; różnica może wynikać z zakresu, okresu, wersji, alokacji lub restatement |
| szacunek | estimate_flag i estimate_basis pozostają widoczne; udokumentowany estimate nie udaje measured data |
| założenie | assumption nie jest dowodem; istotne założenie bez wsparcia uniemożliwia wysoką klasę |
| dane ręczne | nie są automatycznie słabsze; liczą się walidacja, definicja, pochodzenie, zakres i odtwarzalność |
| dane systemowe | nie są automatycznie mocniejsze; błędne mapowanie albo transformacja ograniczają podstawę |

## 15. Ograniczenia, wymagana walidacja, zawężenie i odrzucenie

| Mechanizm | Pola | Reguła |
| --- | --- | --- |
| ograniczenia pewności | confidence_limitations; limitation_count; critical_confidence_limitation_flag | ograniczenia są jawne i nie są sumowane do score |
| wymagana walidacja | confidence_validation_required; confidence_validation_action; confidence_validation_actions; confidence_validation_basis | CONF wskazuje potrzebę i działania, ale nie ustala ich priorytetu |
| cel walidacji | confidence_validation_target; confidence_validation_target_id | każde działanie wskazuje rodzaj oraz identyfikator przedmiotu walidacji |
| zawężenie twierdzenia | claim_narrowing_required; narrowed_claim_text; claim_narrowing_basis | oryginalny claim_text pozostaje niezmieniony; zawężenie może zachować odpowiedzialny częściowy wniosek |
| odrzucenie twierdzenia | claim_rejection_flag; claim_rejection_basis | tylko przy sprzeczności z podstawą albo braku możliwości utrzymania; nie dowodzi tezy przeciwnej |

### 15.1. Zamknięty katalog działań walidacyjnych

| confidence_validation_action | Znaczenie użytkowe |
| --- | --- |
| complete_required_information | uzupełnienie wymaganej informacji |
| validate_source_data | walidacja danych źródłowych |
| validate_definition_semantics | walidacja definicji i semantyki |
| validate_scope_period | walidacja zakresu i okresu |
| validate_comparability | walidacja porównywalności |
| validate_lineage_reproducibility | walidacja pochodzenia i odtwarzalności |
| reconcile_sources | uzgodnienie źródeł |
| resolve_data_conflict | rozwiązanie konfliktu danych |
| validate_estimate_assumption | walidacja szacunku lub założenia |
| validate_evidence_independence | walidacja niezależności dowodów |
| validate_mechanism_evidence | walidacja dowodów mechanizmu |
| no_additional_validation | brak dodatkowej walidacji |

| Pole | Kontrakt |
| --- | --- |
| confidence_validation_required | wartość logiczna wskazująca potrzebę co najmniej jednej dodatkowej walidacji |
| confidence_validation_action | pojedyncza wartość z zamkniętego katalogu |
| confidence_validation_actions | uporządkowany zbiór unikalnych rekordów działania; każdy rekord zawiera action, target, target_id i basis |
| confidence_validation_basis | audytowalna podstawa przypisana do każdego działania |
| confidence_validation_target | rodzaj przedmiotu walidacji |
| confidence_validation_target_id | identyfikator konkretnego przedmiotu walidacji |

Gdy potrzebna jest więcej niż jedna walidacja, confidence_validation_actions przechowuje uporządkowany zbiór unikalnych działań. Każde działanie ma własne confidence_validation_basis oraz wskazuje confidence_validation_target i confidence_validation_target_id. no_additional_validation nie może współwystępować z innym działaniem. CONF-01 nie nadaje działaniom kolejności ważności; kolejność walidacji pozostaje w kompetencji PRI-01.

## 16. Stabilność i wersjonowanie oceny

| Pole | Kontrakt |
| --- | --- |
| confidence_stability_dimension | metric_confidence; finding_confidence; mechanism_confidence |
| confidence_stability_status | stable; strengthening; weakening; fluctuating; unknown |
| confidence_class_previous / current | porównywane wyłącznie dla tego samego claim_id, claim_type, zakresu i kontekstu |
| confidence_change_reason | jawna zmiana podstawy dowodowej, walidacji, konfliktu albo ograniczenia |
| confidence_basis_version | wersja podstawy dowodowej użytej do klasyfikacji |
| confidence_evaluation_date | data wykonania oceny |
| confidence_evaluator_type | rule_based_system; analyst_validated; mixed; typ wykonawcy nie jest oceną jakości |

Dla stabilności dopuszcza się wyłącznie porządek semantyczny weakly_supported < partially_supported < supported_with_limitations < well_supported. Porządek nie jest wynikiem punktowym, nie służy do agregacji ani porównywania różnych twierdzeń. not_assessable nie uczestniczy w porządku; przejście z not_assessable nie jest automatycznie strengthening.

## 17. Kontrakt wyniku FINDINGS

### 17.1. Pola bazowe

| Pole | Reguła CONF-01 |
| --- | --- |
| test_id; scope; period; status; finding | zachowane zgodnie ze wspólnym kontraktem Core 10 |
| metric_value; reference_value; gap | CONF-01 nie przelicza wartości źródłowych |
| confidence_score | zawsze null w CONF-01 v1.0 |
| confidence_class | wskazuje klasę odpowiadającą confidence_class_source_level właściwemu dla claim_type; nie jest kopiowana między poziomami |
| confidence_class_source_level | metric_confidence; finding_confidence; mechanism_confidence |
| next_tests; validation_required | dziedziczone i uzupełniane bez pełnej orkiestracji |

### 17.2. Rozszerzenia CONF-01

| Grupa | Pola techniczne |
| --- | --- |
| tożsamość claim | claim_id; claim_type; claim_text; claim_scope; claim_period |
| klasy | metric_confidence_class; finding_confidence_class; mechanism_confidence_class; confidence_class_source_level |
| podstawa | confidence_basis; confidence_basis_summary; confidence_basis_version |
| ograniczenia | confidence_limitations; critical_confidence_limitation_flag |
| walidacja | confidence_validation_required; confidence_validation_action; confidence_validation_actions; confidence_validation_basis; confidence_validation_target; confidence_validation_target_id |
| bramy I | required_information_gate; definition_semantics_gate; scope_period_gate; comparability_gate |
| bramy II | lineage_reproducibility_gate; reconciliation_gate; conflict_gate; estimate_assumption_gate |
| bramy III | evidence_independence_gate; mechanism_evidence_gate |
| zgodność i niezależność | cross_test_support_status; evidence_independence_status; evidence_independence_required; evidence_independence_requirement_basis; evidence_independence_sufficient; independent_evidence_count; shared_source_flag |
| konflikt | confidence_conflict_status; contradictory_evidence_count |
| zawężenie / odrzucenie | claim_narrowing_required; narrowed_claim_text; claim_rejection_flag |
| stabilność | confidence_stability_status; confidence_change_reason |

### 17.3. Kontrakt pełnego rekordu oceny

Rekord oceny zachowuje powiązania: twierdzenie → dowody → wymagania → bramy → klasy → ograniczenia → walidacja → stabilność. Każda klasa ma confidence_basis możliwe do audytu. Wartość null oznacza brak oceny albo nieadekwatność pola zgodnie z kontraktem; nie jest automatycznie zerem ani wynikiem negatywnym.

## 18. Interfejs z PRI-01 i przyszłą orkiestracją

### 18.1. Dane przekazywane do PRI-01

| Pole | Reguła przekazania |
| --- | --- |
| confidence_class | klasa odpowiadająca confidence_class_source_level właściwemu dla claim_type |
| confidence_class_source_level | metric_confidence; finding_confidence; mechanism_confidence; wskazuje źródłowy poziom przekazywanej klasy |
| confidence_score | null |
| confidence_basis / confidence_basis_summary | audytowalna podstawa i zwięzły opis |
| metric_confidence_class / finding_confidence_class / mechanism_confidence_class | trzy rozdzielone poziomy |
| confidence_limitations | jawne ograniczenia właściwe dla claim |
| confidence_validation_required / action / actions | potrzeba oraz uporządkowany zbiór unikalnych działań bez nadania validation_priority_action |
| confidence_stability_status | stabilność dla tego samego claim i kontekstu |
| evidence_independence_status / cross_test_support_status | niezależność oraz zgodność wielu testów |
| confidence_conflict_status | status konfliktu bez arbitralnego rozstrzygnięcia |

> **OCHRONA PRI-01 CONF-01 nie zmienia problem_priority_action ani validation_priority_action. Niska pewność nie obniża automatycznie skali źródłowego wpływu, a wysoka pewność nie podnosi priorytetu problemu.**

### 18.2. Dane dla przyszłej orkiestracji next_tests

| Pole | Rola |
| --- | --- |
| claim_id; finding_id | tożsamość twierdzenia i wyniku |
| finding_confidence_class; mechanism_confidence_class | siła wsparcia sygnału i wyjaśnienia |
| confidence_validation_required; confidence_validation_action; confidence_validation_actions | potrzeba i działania walidacyjne bez nadania priorytetu |
| confidence_validation_target; confidence_validation_target_id | rodzaj oraz identyfikator przedmiotu walidacji |
| cross_test_support_status; evidence_independence_status | zgodność oraz niezależność podstawy |
| confidence_conflict_status; critical_confidence_limitation_flag | konflikt i krytyczne ograniczenie |
| next_tests | dziedziczona lista możliwych testów; bez algorytmu uruchamiania |
| confidence_stability_status | zmiana jakości podstawy w tym samym kontekście |

CONF-01 przekazuje kontrakt wejściowy. Nie projektuje kolejności między wszystkimi wynikami, grafu zależności ani silnika reguł decyzyjnych.

## 19. Podstawa pewności i komunikat zarządczy

| Pole | Wymaganie |
| --- | --- |
| confidence_basis | pełna audytowalna podstawa: kluczowe dowody, role, bramy, konflikty, niezależność, ograniczenia i walidacje |
| confidence_basis_summary | zwięzłe objaśnienie użytkowe bez nieokreślonych sformułowań, gdy możliwe jest wskazanie podstawy |

> **WZORZEC KOMUNIKATU [PEWNOŚĆ] WYNIK DIAGNOSTYCZNY. Twierdzenie [treść twierdzenia] ma klasę [finding_confidence_class / mechanism_confidence_class]. Podstawę stanowią [główne dowody]. Ograniczenia dotyczą [confidence_limitations]. Dowody między testami są [cross_test_support_status], a ich niezależność oceniono jako [evidence_independence_status]. Konflikty: [confidence_conflict_status]. Wymagana walidacja: [confidence_validation_required / confidence_validation_action / confidence_validation_actions]. Klasa nie jest prawdopodobieństwem statystycznym i nie określa priorytetu problemu.**

Komunikat nie wydaje poleceń: zatrudnij, zwolnij, kup, zamknij, podnieś cenę, zmniejsz lub zwiększ zdolność. Nie wycenia oszczędności ani potencjału i nie potwierdza mechanizmu bez źródła.

## 20. Scenariusze testowe CONF01-T

Każdy scenariusz kończy się PASS tylko wtedy, gdy klasy, bramy, ograniczenia, pola kontraktu i komunikat są zgodne z oczekiwaniem. Poprawna narracja bez poprawnego rekordu danych nie wystarcza.

| ID | Scenariusz | Oczekiwany wynik | Status |
| --- | --- | --- | --- |
| CONF01-T01 | Miara poprawna, pełne pochodzenie i zgodny zakres | metric_confidence_class=well_supported. | PASS |
| CONF01-T02 | Miara poprawna, niekrytyczne ograniczenie coverage | supported_with_limitations; limitation jawne. | PASS |
| CONF01-T03 | Current poprawny, reference nieporównywalny | current metric może być well_supported; claim o zmianie nie może udawać porównywalnego. | PASS |
| CONF01-T04 | Częściowy zakres danych | partially_supported tylko dla zawężonego claim. | PASS |
| CONF01-T05 | Brak required denominatora | metric claim = not_assessable. | PASS |
| CONF01-T06 | Dane ręczne z walidacją | Brak automatycznego obniżenia klasy. | PASS |
| CONF01-T07 | Dane systemowe z błędnym mappingiem | Wysoka klasa niedopuszczalna. | PASS |
| CONF01-T08 | Udokumentowany estimate jako supporting input | Możliwy supported_with_limitations. | PASS |
| CONF01-T09 | Essential unsupported assumption | well_supported niedopuszczalne; weak/not_assessable zależnie od claim. | PASS |
| CONF01-T10 | FIN-03 unit cost dobrze policzony, mechanizm capacity tylko hipoteza | metric/finding mocne; mechanism weakly_supported. | PASS |
| CONF01-T11 | PROC-02 verified constraint z pełnym evidence | mechanism może być well_supported zgodnie z metodologią źródłową. | PASS |
| CONF01-T12 | Największa kolejka bez mechanizmu | mechanism_confidence nie może być well_supported. | PASS |
| CONF01-T13 | Trzy testy, jedno wspólne źródło | cross-test support tak; evidence_independence=shared_source. | PASS |
| CONF01-T14 | Dwa niezależne źródła zgodne | Może wzmacniać klasę bez automatycznego well_supported. | PASS |
| CONF01-T15 | Dwa niezależne źródła sprzeczne | conflict jawny; brak głosowania większościowego. | PASS |
| CONF01-T16 | reconciled_with_explanation | Nie obniżaj automatycznie klasy. | PASS |
| CONF01-T17 | unreconciled required metric | Wysoka klasa niedopuszczalna. | PASS |
| CONF01-T18 | NO_ADVERSE_SIGNAL przy pełnym pokryciu | Finding może być well_supported w swoim scope. | PASS |
| CONF01-T19 | NO_ADVERSE_SIGNAL przy słabym coverage | Nie interpretuj jako pewny brak problemu. | PASS |
| CONF01-T20 | Finding dobrze potwierdzony, decyzja MGT blocked | Confidence może być wysoka mimo decision_blocked. | PASS |
| CONF01-T21 | MGT fit, ale mechanizm bez evidence | mechanism weak/not_assessable; fit ≠ confidence. | PASS |
| CONF01-T22 | MGT partial w wymiarze optional | Confidence może pozostać supported_with_limitations. | PASS |
| CONF01-T23 | Critical information gap required dla claim | Wysoka klasa niedopuszczalna. | PASS |
| CONF01-T24 | Różny scope current/reference | comparability_gate fail dla claim o zmianie. | PASS |
| CONF01-T25 | Restated history odzyskuje porównywalność | Confidence może wzrosnąć; change_reason jawne. | PASS |
| CONF01-T26 | One-off jawnie skorygowany obok actual | Ocena actual i adjusted osobno; brak mieszania. | PASS |
| CONF01-T27 | Shared cost allocation z dobrą basis current/reference | Allocation confidence może być well_supported. | PASS |
| CONF01-T28 | Zmiana metody shared cost allocation bez uzgodnienia | Full finding confidence ograniczona/partial. | PASS |
| CONF01-T29 | Work_content globalnie otwarty, ale lokalnie źródłowo zdefiniowany | Oceń claim lokalny bez rozstrzygania globalnego kontraktu. | PASS |
| CONF01-T30 | Mechanizm oparty tylko na korelacji | Maksymalnie weakly_supported bez dodatkowych evidence. | PASS |
| CONF01-T31 | Mechanizm częściowo potwierdzony | partially_supported z narrowed_claim_text. | PASS |
| CONF01-T32 | Contradictory evidence później rozwiązany | confidence może się wzmocnić; change_reason jawne. | PASS |
| CONF01-T33 | not_assessable → well_supported po nowych danych | Nie klasyfikuj automatycznie jako strengthening; not_assessable poza porządkiem. | PASS |
| CONF01-T34 | well_supported → supported_with_limitations | confidence_stability_status=weakening dla tego samego claim/context. | PASS |
| CONF01-T35 | PRI review_now, CONF weakly_supported | CONF nie zmienia PRI; przyszła orkiestracja może użyć obu osi. | PASS |
| CONF01-T36 | PRI observe, CONF well_supported | Wysoka confidence nie podnosi priorytetu. | PASS |
| CONF01-T37 | P-value istotne, ale scope mismatch | Nie nadaj well_supported tylko z powodu statystyki. | PASS |
| CONF01-T38 | Brak dowodu wspierającego i brak dowodu sprzecznego | Nie zamieniaj absence of evidence w contradictory evidence. | PASS |
| CONF01-T39 | Claim zbyt szeroki, część dobrze wsparta | claim_narrowing_required=true; partial zamiast sztucznego full support. | PASS |
| CONF01-T40 | Brak AI i brak score | Deterministyczne gate prowadzą do klasy; confidence_score=null. | PASS |
| CONF01-T41 | Dwie walidacje jednego twierdzenia | Brak porównywalności i konflikt danych tworzą uporządkowane confidence_validation_actions: validate_comparability oraz resolve_data_conflict; bez nadania priorytetu. | PASS |
| CONF01-T42 | Mechanizm wymaga niezależności | Dla triangulacji wyników z jednego źródła: evidence_independence_required = true, evidence_independence_sufficient = false oraz mechanism_confidence_class != well_supported. | PASS |
| CONF01-T43 | Pojedynczy bezpośredni dowód mechanizmu | Gdy zamrożona metodologia bezpośrednio weryfikuje mechanizm, evidence_independence_required = false może być dopuszczalne; nie powstaje sztuczny wymóg drugiego źródła. | PASS |
| CONF01-T44 | Partially vs weak | Część możliwa do jednoznacznego zawężenia daje partially_supported i narrowed_claim_text; ogólny słaby sygnał bez odpowiedzialnego zawężenia daje weakly_supported. | PASS |
| CONF01-T45 | Typ twierdzenia i właściwa klasa | Rekordy metric_claim, finding_claim i mechanism_claim mają właściwy confidence_class_source_level; klasy nie są kopiowane między poziomami. | PASS |

## 21. Walidacja CONF01-VAL

| ID | Kontrola | Wynik |
| --- | --- | --- |
| CONF01-VAL-01 | claim_id jest obecny i jednoznaczny | PASS |
| CONF01-VAL-02 | claim_type należy do katalogu | PASS |
| CONF01-VAL-03 | claim_text zachowuje oryginalną treść | PASS |
| CONF01-VAL-04 | claim_scope jest jawny | PASS |
| CONF01-VAL-05 | claim_period jest jawny | PASS |
| CONF01-VAL-06 | claim_source_test jest jawny | PASS |
| CONF01-VAL-07 | claim_version jest jawna | PASS |
| CONF01-VAL-08 | confidence_context jest jawny | PASS |
| CONF01-VAL-09 | evidence_id jest obecny | PASS |
| CONF01-VAL-10 | evidence_role należy do katalogu | PASS |
| CONF01-VAL-11 | primary_evidence wymagany przez claim jest obecny | PASS |
| CONF01-VAL-12 | supporting_evidence nie zastępuje primary_evidence | PASS |
| CONF01-VAL-13 | contextual_evidence nie jest traktowany jak primary_evidence | PASS |
| CONF01-VAL-14 | contradictory_evidence ma źródłową podstawę | PASS |
| CONF01-VAL-15 | validation_evidence wskazuje wykonaną walidację | PASS |
| CONF01-VAL-16 | evidence_scope jest zgodny lub ograniczenie jest jawne | PASS |
| CONF01-VAL-17 | evidence_period jest zgodny lub ograniczenie jest jawne | PASS |
| CONF01-VAL-18 | evidence_traceability_status jest jawny | PASS |
| CONF01-VAL-19 | evidence_source_group_id chroni przed pozorną niezależnością | PASS |
| CONF01-VAL-20 | claim_required_information_objects są jawne | PASS |
| CONF01-VAL-21 | claim_required_dimensions są jawne | PASS |
| CONF01-VAL-22 | claim_required_validations są jawne | PASS |
| CONF01-VAL-23 | claim_allowed_limitations są jawne | PASS |
| CONF01-VAL-24 | required_information_gate ma dozwolony status | PASS |
| CONF01-VAL-25 | definition_semantics_gate ma dozwolony status | PASS |
| CONF01-VAL-26 | scope_period_gate ma dozwolony status | PASS |
| CONF01-VAL-27 | comparability_gate jest oceniony dla claim porównawczego | PASS |
| CONF01-VAL-28 | lineage_reproducibility_gate ma podstawę | PASS |
| CONF01-VAL-29 | reconciliation_gate respektuje status MGT-01 | PASS |
| CONF01-VAL-30 | conflict_gate obejmuje każdy required konflikt | PASS |
| CONF01-VAL-31 | estimate_assumption_gate rozdziela estimate i assumption | PASS |
| CONF01-VAL-32 | evidence_independence_gate jest oceniony adekwatnie do claim_type | PASS |
| CONF01-VAL-33 | mechanism_evidence_gate jest wymagany dla mechanism_claim | PASS |
| CONF01-VAL-34 | information_dimension_statuses są dziedziczone bez agregacji | PASS |
| CONF01-VAL-35 | decision_information_status nie jest mapowany na confidence_class | PASS |
| CONF01-VAL-36 | critical_information_gap wpływa tylko na wymagany claim | PASS |
| CONF01-VAL-37 | manual_data_validation_status jest respektowany | PASS |
| CONF01-VAL-38 | trend_comparability_status jest respektowany | PASS |
| CONF01-VAL-39 | data_conflict_flag jest respektowany | PASS |
| CONF01-VAL-40 | coverage jest oceniane względem claim | PASS |
| CONF01-VAL-41 | brak arbitralnego progu coverage | PASS |
| CONF01-VAL-42 | aktualność jest oceniana względem claim | PASS |
| CONF01-VAL-43 | brak globalnego progu wieku danych | PASS |
| CONF01-VAL-44 | current metric nie jest blokowana przez słaby reference | PASS |
| CONF01-VAL-45 | claim o zmianie wymaga porównywalnego reference | PASS |
| CONF01-VAL-46 | matched scope nie jest przenoszony na full scope | PASS |
| CONF01-VAL-47 | bridge_confidence nie zmienia matematyki mostu | PASS |
| CONF01-VAL-48 | allocation_confidence nie zmienia polityki alokacji | PASS |
| CONF01-VAL-49 | work_content i capacity korzystają z kontraktów źródłowych | PASS |
| CONF01-VAL-50 | PROC korzysta z timestamp i route evidence | PASS |
| CONF01-VAL-51 | FIN/PORT korzysta z cost attribution i matched scope | PASS |
| CONF01-VAL-52 | actual i adjusted pozostają oddzielne | PASS |
| CONF01-VAL-53 | NO_ADVERSE_SIGNAL jest ograniczony do zdolności i zakresu testu | PASS |
| CONF01-VAL-54 | dane ręczne nie są automatycznie słabsze | PASS |
| CONF01-VAL-55 | dane systemowe nie są automatycznie mocniejsze | PASS |
| CONF01-VAL-56 | estimate nie jest przedstawiany jako measured data | PASS |
| CONF01-VAL-57 | assumption nie jest liczony jako evidence | PASS |
| CONF01-VAL-58 | independent_evidence_count nie jest score | PASS |
| CONF01-VAL-59 | cross_test_support_status nie działa jak głosowanie | PASS |
| CONF01-VAL-60 | shared_source_flag ogranicza triangulację | PASS |
| CONF01-VAL-61 | confidence_limitations są jawne | PASS |
| CONF01-VAL-62 | critical_confidence_limitation_flag jest jawny | PASS |
| CONF01-VAL-63 | confidence_validation_required ma wartość logiczną | PASS |
| CONF01-VAL-64 | confidence_validation_action nie ustala priorytetu walidacji | PASS |
| CONF01-VAL-65 | claim_narrowing zachowuje claim_text | PASS |
| CONF01-VAL-66 | claim_rejection ma podstawę i nie dowodzi tezy przeciwnej | PASS |
| CONF01-VAL-67 | stabilność porównuje ten sam claim i kontekst | PASS |
| CONF01-VAL-68 | not_assessable nie uczestniczy w porządku stabilności | PASS |
| CONF01-VAL-69 | confidence_change_reason jest jawny przy zmianie | PASS |
| CONF01-VAL-70 | confidence_class mapuje się do PRI zgodnie z regułą | PASS |
| CONF01-VAL-71 | confidence_score pozostaje null | PASS |
| CONF01-VAL-72 | brak modelu prawdopodobieństwa | PASS |
| CONF01-VAL-73 | brak wag i sum punktów | PASS |
| CONF01-VAL-74 | brak arbitralnych progów confidence | PASS |
| CONF01-VAL-75 | tryb regułowy działa bez AI | PASS |
| CONF01-VAL-76 | scenariusze CONF01-T01–T45 są kompletne | PASS |
| CONF01-VAL-77 | confidence_validation_action należy do zamkniętego katalogu | PASS |
| CONF01-VAL-78 | confidence_validation_actions jest uporządkowanym zbiorem unikalnym | PASS |
| CONF01-VAL-79 | każde działanie walidacyjne ma confidence_validation_basis | PASS |
| CONF01-VAL-80 | confidence_validation_target jest jawny dla działania | PASS |
| CONF01-VAL-81 | confidence_validation_target_id jest jawny dla działania | PASS |
| CONF01-VAL-82 | wiele walidacji nie nadaje priorytetu | PASS |
| CONF01-VAL-83 | evidence_independence_required ma wartość logiczną | PASS |
| CONF01-VAL-84 | evidence_independence_requirement_basis jest jawne | PASS |
| CONF01-VAL-85 | evidence_independence_sufficient ma wartość logiczną | PASS |
| CONF01-VAL-86 | niewystarczająca wymagana niezależność blokuje well_supported dla mechanizmu | PASS |
| CONF01-VAL-87 | bezpośredni dowód mechanizmu nie wymaga sztucznego drugiego źródła | PASS |
| CONF01-VAL-88 | partially_supported wymaga jawnego zawężenia | PASS |
| CONF01-VAL-89 | weakly_supported wymaga rzeczywistego sygnału bez odpowiedzialnego zawężenia | PASS |
| CONF01-VAL-90 | not_assessable oznacza brak wystarczającej podstawy pełnej i zawężonej | PASS |
| CONF01-VAL-91 | confidence_class_source_level odpowiada claim_type | PASS |
| CONF01-VAL-92 | confidence_class nie jest kopiowana między poziomami | PASS |

## 22. Kryteria odbioru implementacji CONF01-ACC

Odbiór implementacji wymaga wyniku PASS dla wszystkich kryteriów. Kryteria scenariuszowe są niezależne od kontroli kompletności kontraktu.

| ID | Kryterium odbioru | Wynik |
| --- | --- | --- |
| CONF01-ACC-001 | mechanizm przyjmuje jawny claim_id | PASS |
| CONF01-ACC-002 | mechanizm przyjmuje trzy wartości claim_type | PASS |
| CONF01-ACC-003 | mechanizm zachowuje claim_text | PASS |
| CONF01-ACC-004 | mechanizm rozdziela claim_scope i claim_period | PASS |
| CONF01-ACC-005 | mechanizm wersjonuje claim | PASS |
| CONF01-ACC-006 | mechanizm wiąże claim ze source_test | PASS |
| CONF01-ACC-007 | mechanizm przyjmuje wiele rekordów evidence | PASS |
| CONF01-ACC-008 | każdy evidence ma evidence_id | PASS |
| CONF01-ACC-009 | każdy evidence ma evidence_role | PASS |
| CONF01-ACC-010 | obsługiwany jest primary_evidence | PASS |
| CONF01-ACC-011 | obsługiwany jest supporting_evidence | PASS |
| CONF01-ACC-012 | obsługiwany jest contextual_evidence | PASS |
| CONF01-ACC-013 | obsługiwany jest contradictory_evidence | PASS |
| CONF01-ACC-014 | obsługiwany jest validation_evidence | PASS |
| CONF01-ACC-015 | brak primary_evidence nie jest maskowany supporting_evidence | PASS |
| CONF01-ACC-016 | dowody mają scope i period | PASS |
| CONF01-ACC-017 | dowody mają source group | PASS |
| CONF01-ACC-018 | dowody mają traceability status | PASS |
| CONF01-ACC-019 | obliczany jest evidence_independence_status | PASS |
| CONF01-ACC-020 | obsługiwany jest documented_independent | PASS |
| CONF01-ACC-021 | obsługiwany jest partly_shared | PASS |
| CONF01-ACC-022 | obsługiwany jest shared_source | PASS |
| CONF01-ACC-023 | obsługiwany jest unknown independence | PASS |
| CONF01-ACC-024 | shared transformation jest wykrywana | PASS |
| CONF01-ACC-025 | independent evidence count nie wpływa punktowo na klasę | PASS |
| CONF01-ACC-026 | obliczany jest cross_test_support_status | PASS |
| CONF01-ACC-027 | obsługiwany jest consistent | PASS |
| CONF01-ACC-028 | obsługiwany jest consistent_with_limitations | PASS |
| CONF01-ACC-029 | obsługiwany jest mixed | PASS |
| CONF01-ACC-030 | obsługiwany jest contradictory | PASS |
| CONF01-ACC-031 | obsługiwany jest not_assessable cross-test | PASS |
| CONF01-ACC-032 | brak głosowania większościowego | PASS |
| CONF01-ACC-033 | wejście MGT information_dimension_statuses jest przyjmowane | PASS |
| CONF01-ACC-034 | wejście decision_information_status jest kontekstem | PASS |
| CONF01-ACC-035 | wejście critical_information_gap jest przyjmowane | PASS |
| CONF01-ACC-036 | wejście data_conflict_flag jest przyjmowane | PASS |
| CONF01-ACC-037 | wejście reconciliation_status jest przyjmowane | PASS |
| CONF01-ACC-038 | wejście trend_comparability_status jest przyjmowane | PASS |
| CONF01-ACC-039 | wejście manual_data_validation_status jest przyjmowane | PASS |
| CONF01-ACC-040 | wejścia estimate i assumption są rozdzielone | PASS |
| CONF01-ACC-041 | required information jest claim-specific | PASS |
| CONF01-ACC-042 | required dimensions są claim-specific | PASS |
| CONF01-ACC-043 | required validations są claim-specific | PASS |
| CONF01-ACC-044 | allowed limitations są claim-specific | PASS |
| CONF01-ACC-045 | required_information_gate działa | PASS |
| CONF01-ACC-046 | definition_semantics_gate działa | PASS |
| CONF01-ACC-047 | scope_period_gate działa | PASS |
| CONF01-ACC-048 | comparability_gate działa | PASS |
| CONF01-ACC-049 | lineage_reproducibility_gate działa | PASS |
| CONF01-ACC-050 | reconciliation_gate działa | PASS |
| CONF01-ACC-051 | conflict_gate działa | PASS |
| CONF01-ACC-052 | estimate_assumption_gate działa | PASS |
| CONF01-ACC-053 | evidence_independence_gate działa | PASS |
| CONF01-ACC-054 | mechanism_evidence_gate działa | PASS |
| CONF01-ACC-055 | każda brama używa katalogu pięciu statusów | PASS |
| CONF01-ACC-056 | required fail blokuje dwie najwyższe klasy | PASS |
| CONF01-ACC-057 | required partial ogranicza klasę | PASS |
| CONF01-ACC-058 | all required pass dopuszcza, lecz nie wymusza well_supported | PASS |
| CONF01-ACC-059 | pass_with_limitations prowadzi do jawnych limitations | PASS |
| CONF01-ACC-060 | metric_confidence_class ma pięć klas | PASS |
| CONF01-ACC-061 | finding_confidence_class ma pięć klas | PASS |
| CONF01-ACC-062 | mechanism_confidence_class ma pięć klas | PASS |
| CONF01-ACC-063 | metric well_supported wymaga odtwarzalności | PASS |
| CONF01-ACC-064 | metric porównawcza wymaga comparability | PASS |
| CONF01-ACC-065 | finding well_supported może wynikać z jednego wystarczającego testu | PASS |
| CONF01-ACC-066 | mechanism well_supported wymaga mechanism evidence | PASS |
| CONF01-ACC-067 | hipoteza nie staje się potwierdzonym mechanizmem | PASS |
| CONF01-ACC-068 | korelacja nie staje się dowodem przyczynowym | PASS |
| CONF01-ACC-069 | verified constraint jest respektowane zgodnie z PROC-02 | PASS |
| CONF01-ACC-070 | NO_ADVERSE_SIGNAL jest ograniczony do zakresu testu | PASS |
| CONF01-ACC-071 | current metric może być mocna przy słabym reference | PASS |
| CONF01-ACC-072 | matched scope i full scope są rozdzielone | PASS |
| CONF01-ACC-073 | bridge confidence jest obsługiwane | PASS |
| CONF01-ACC-074 | allocation confidence jest obsługiwane | PASS |
| CONF01-ACC-075 | zależności work_content/capacity pozostają źródłowe | PASS |
| CONF01-ACC-076 | dane procesu wymagają właściwych timestampów i route | PASS |
| CONF01-ACC-077 | dane finansowe respektują attribution i one-off | PASS |
| CONF01-ACC-078 | konflikt required jest jawny | PASS |
| CONF01-ACC-079 | sprzeczny evidence nie jest usuwany | PASS |
| CONF01-ACC-080 | estimate z podstawą może być użyty z ograniczeniem | PASS |
| CONF01-ACC-081 | unsupported assumption ogranicza wysoką klasę | PASS |
| CONF01-ACC-082 | dane ręczne są oceniane przez walidację | PASS |
| CONF01-ACC-083 | dane systemowe są oceniane przez mapowanie i lineage | PASS |
| CONF01-ACC-084 | confidence limitations są zwracane | PASS |
| CONF01-ACC-085 | critical limitation flag jest zwracany | PASS |
| CONF01-ACC-086 | confidence validation required jest zwracany | PASS |
| CONF01-ACC-087 | validation action nie zmienia PRI | PASS |
| CONF01-ACC-088 | claim narrowing jest zwracany | PASS |
| CONF01-ACC-089 | narrowed claim nie nadpisuje claim text | PASS |
| CONF01-ACC-090 | claim rejection ma podstawę | PASS |
| CONF01-ACC-091 | stability ma pięć statusów | PASS |
| CONF01-ACC-092 | stability porównuje ten sam claim/context | PASS |
| CONF01-ACC-093 | change reason jest wymagany przy strengthening/weakening | PASS |
| CONF01-ACC-094 | confidence basis ma wersję i datę | PASS |
| CONF01-ACC-095 | evaluator type nie jest wskaźnikiem jakości | PASS |
| CONF01-ACC-096 | FINDINGS zachowuje pola bazowe Core 10 | PASS |
| CONF01-ACC-097 | FINDINGS zawiera rozszerzenia CONF-01 | PASS |
| CONF01-ACC-098 | confidence_class jest kompatybilne z PRI-01 | PASS |
| CONF01-ACC-099 | confidence_score pozostaje null | PASS |
| CONF01-ACC-100 | payload orkiestracji jest kompletny bez algorytmu | PASS |
| CONF01-ACC-101 | komunikat zarządczy jest generowany po polsku | PASS |
| CONF01-ACC-102 | mechanizm działa deterministycznie bez AI | PASS |
| CONF01-ACC-103 | obsługiwany jest zamknięty katalog confidence_validation_action | PASS |
| CONF01-ACC-104 | obsługiwane jest confidence_validation_actions | PASS |
| CONF01-ACC-105 | confidence_validation_actions usuwa duplikaty i zachowuje kolejność | PASS |
| CONF01-ACC-106 | każde działanie zwraca confidence_validation_basis | PASS |
| CONF01-ACC-107 | każde działanie zwraca confidence_validation_target | PASS |
| CONF01-ACC-108 | każde działanie zwraca confidence_validation_target_id | PASS |
| CONF01-ACC-109 | wiele działań walidacyjnych nie tworzy priorytetu | PASS |
| CONF01-ACC-110 | obsługiwane jest evidence_independence_required | PASS |
| CONF01-ACC-111 | obsługiwane jest evidence_independence_requirement_basis | PASS |
| CONF01-ACC-112 | obsługiwane jest evidence_independence_sufficient | PASS |
| CONF01-ACC-113 | wymagana i niewystarczająca niezależność blokuje najwyższą klasę mechanizmu | PASS |
| CONF01-ACC-114 | pojedynczy bezpośredni dowód mechanizmu może być wystarczający | PASS |
| CONF01-ACC-115 | partially_supported wymaga claim_narrowing_required | PASS |
| CONF01-ACC-116 | partially_supported wymaga narrowed_claim_text | PASS |
| CONF01-ACC-117 | weakly_supported jest stosowane dopiero po braku odpowiedzialnego zawężenia | PASS |
| CONF01-ACC-118 | not_assessable jest stosowane przy braku wystarczającego sygnału | PASS |
| CONF01-ACC-119 | precedencja klas nie działa jak skala punktowa | PASS |
| CONF01-ACC-120 | confidence_class_source_level ma trzy wartości | PASS |
| CONF01-ACC-121 | metric_claim wskazuje metric_confidence | PASS |
| CONF01-ACC-122 | finding_claim wskazuje finding_confidence | PASS |
| CONF01-ACC-123 | mechanism_claim wskazuje mechanism_confidence | PASS |
| CONF01-ACC-124 | confidence_class odpowiada wskazanemu poziomowi źródłowemu | PASS |
| CONF01-ACC-125 | klasy nie są automatycznie kopiowane między poziomami | PASS |
| CONF01-ACC-126 | CONF01-T01 przechodzi zgodnie z oczekiwanym wynikiem | PASS |
| CONF01-ACC-127 | CONF01-T02 przechodzi zgodnie z oczekiwanym wynikiem | PASS |
| CONF01-ACC-128 | CONF01-T03 przechodzi zgodnie z oczekiwanym wynikiem | PASS |
| CONF01-ACC-129 | CONF01-T04 przechodzi zgodnie z oczekiwanym wynikiem | PASS |
| CONF01-ACC-130 | CONF01-T05 przechodzi zgodnie z oczekiwanym wynikiem | PASS |
| CONF01-ACC-131 | CONF01-T06 przechodzi zgodnie z oczekiwanym wynikiem | PASS |
| CONF01-ACC-132 | CONF01-T07 przechodzi zgodnie z oczekiwanym wynikiem | PASS |
| CONF01-ACC-133 | CONF01-T08 przechodzi zgodnie z oczekiwanym wynikiem | PASS |
| CONF01-ACC-134 | CONF01-T09 przechodzi zgodnie z oczekiwanym wynikiem | PASS |
| CONF01-ACC-135 | CONF01-T10 przechodzi zgodnie z oczekiwanym wynikiem | PASS |
| CONF01-ACC-136 | CONF01-T11 przechodzi zgodnie z oczekiwanym wynikiem | PASS |
| CONF01-ACC-137 | CONF01-T12 przechodzi zgodnie z oczekiwanym wynikiem | PASS |
| CONF01-ACC-138 | CONF01-T13 przechodzi zgodnie z oczekiwanym wynikiem | PASS |
| CONF01-ACC-139 | CONF01-T14 przechodzi zgodnie z oczekiwanym wynikiem | PASS |
| CONF01-ACC-140 | CONF01-T15 przechodzi zgodnie z oczekiwanym wynikiem | PASS |
| CONF01-ACC-141 | CONF01-T16 przechodzi zgodnie z oczekiwanym wynikiem | PASS |
| CONF01-ACC-142 | CONF01-T17 przechodzi zgodnie z oczekiwanym wynikiem | PASS |
| CONF01-ACC-143 | CONF01-T18 przechodzi zgodnie z oczekiwanym wynikiem | PASS |
| CONF01-ACC-144 | CONF01-T19 przechodzi zgodnie z oczekiwanym wynikiem | PASS |
| CONF01-ACC-145 | CONF01-T20 przechodzi zgodnie z oczekiwanym wynikiem | PASS |
| CONF01-ACC-146 | CONF01-T21 przechodzi zgodnie z oczekiwanym wynikiem | PASS |
| CONF01-ACC-147 | CONF01-T22 przechodzi zgodnie z oczekiwanym wynikiem | PASS |
| CONF01-ACC-148 | CONF01-T23 przechodzi zgodnie z oczekiwanym wynikiem | PASS |
| CONF01-ACC-149 | CONF01-T24 przechodzi zgodnie z oczekiwanym wynikiem | PASS |
| CONF01-ACC-150 | CONF01-T25 przechodzi zgodnie z oczekiwanym wynikiem | PASS |
| CONF01-ACC-151 | CONF01-T26 przechodzi zgodnie z oczekiwanym wynikiem | PASS |
| CONF01-ACC-152 | CONF01-T27 przechodzi zgodnie z oczekiwanym wynikiem | PASS |
| CONF01-ACC-153 | CONF01-T28 przechodzi zgodnie z oczekiwanym wynikiem | PASS |
| CONF01-ACC-154 | CONF01-T29 przechodzi zgodnie z oczekiwanym wynikiem | PASS |
| CONF01-ACC-155 | CONF01-T30 przechodzi zgodnie z oczekiwanym wynikiem | PASS |
| CONF01-ACC-156 | CONF01-T31 przechodzi zgodnie z oczekiwanym wynikiem | PASS |
| CONF01-ACC-157 | CONF01-T32 przechodzi zgodnie z oczekiwanym wynikiem | PASS |
| CONF01-ACC-158 | CONF01-T33 przechodzi zgodnie z oczekiwanym wynikiem | PASS |
| CONF01-ACC-159 | CONF01-T34 przechodzi zgodnie z oczekiwanym wynikiem | PASS |
| CONF01-ACC-160 | CONF01-T35 przechodzi zgodnie z oczekiwanym wynikiem | PASS |
| CONF01-ACC-161 | CONF01-T36 przechodzi zgodnie z oczekiwanym wynikiem | PASS |
| CONF01-ACC-162 | CONF01-T37 przechodzi zgodnie z oczekiwanym wynikiem | PASS |
| CONF01-ACC-163 | CONF01-T38 przechodzi zgodnie z oczekiwanym wynikiem | PASS |
| CONF01-ACC-164 | CONF01-T39 przechodzi zgodnie z oczekiwanym wynikiem | PASS |
| CONF01-ACC-165 | CONF01-T40 przechodzi zgodnie z oczekiwanym wynikiem | PASS |
| CONF01-ACC-166 | CONF01-T41 przechodzi zgodnie z oczekiwanym wynikiem | PASS |
| CONF01-ACC-167 | CONF01-T42 przechodzi zgodnie z oczekiwanym wynikiem | PASS |
| CONF01-ACC-168 | CONF01-T43 przechodzi zgodnie z oczekiwanym wynikiem | PASS |
| CONF01-ACC-169 | CONF01-T44 przechodzi zgodnie z oczekiwanym wynikiem | PASS |
| CONF01-ACC-170 | CONF01-T45 przechodzi zgodnie z oczekiwanym wynikiem | PASS |

## 23. Warunki zamknięcia CONF01-DOD

| ID | Warunek zamknięcia | Wynik |
| --- | --- | --- |
| CONF01-DOD-01 | cel CONF-01 jest jednoznaczny | PASS |
| CONF01-DOD-02 | granica CONF względem PRI jest zamknięta | PASS |
| CONF01-DOD-03 | granica CONF względem MGT jest zamknięta | PASS |
| CONF01-DOD-04 | confidence ≠ priority | PASS |
| CONF01-DOD-05 | confidence ≠ decision readiness | PASS |
| CONF01-DOD-06 | confidence ≠ probability | PASS |
| CONF01-DOD-07 | brak confidence score | PASS |
| CONF01-DOD-08 | brak wag | PASS |
| CONF01-DOD-09 | brak arbitralnych progów | PASS |
| CONF01-DOD-10 | trzy poziomy pewności są rozdzielone | PASS |
| CONF01-DOD-11 | katalog klas jest zamknięty | PASS |
| CONF01-DOD-12 | claim contract jest kompletny | PASS |
| CONF01-DOD-13 | claim identity jest wersjonowana | PASS |
| CONF01-DOD-14 | claim scope i period są wymagane | PASS |
| CONF01-DOD-15 | evidence contract jest kompletny | PASS |
| CONF01-DOD-16 | evidence roles są kompletne | PASS |
| CONF01-DOD-17 | primary evidence ma ochronę | PASS |
| CONF01-DOD-18 | supporting evidence ma granicę | PASS |
| CONF01-DOD-19 | contextual evidence ma granicę | PASS |
| CONF01-DOD-20 | contradictory evidence pozostaje widoczny | PASS |
| CONF01-DOD-21 | validation evidence ma kontrakt | PASS |
| CONF01-DOD-22 | independence status jest zamknięty | PASS |
| CONF01-DOD-23 | shared source jest chronione | PASS |
| CONF01-DOD-24 | shared transformation jest chroniona | PASS |
| CONF01-DOD-25 | independent evidence count nie jest score | PASS |
| CONF01-DOD-26 | cross-test support ma katalog | PASS |
| CONF01-DOD-27 | cross-test support nie jest głosowaniem | PASS |
| CONF01-DOD-28 | wejścia MGT są jawne | PASS |
| CONF01-DOD-29 | MGT inputs nie są redefiniowane | PASS |
| CONF01-DOD-30 | required information jest claim-specific | PASS |
| CONF01-DOD-31 | required dimensions są claim-specific | PASS |
| CONF01-DOD-32 | required validations są claim-specific | PASS |
| CONF01-DOD-33 | required information gate jest zamknięty | PASS |
| CONF01-DOD-34 | definition semantics gate jest zamknięty | PASS |
| CONF01-DOD-35 | scope period gate jest zamknięty | PASS |
| CONF01-DOD-36 | comparability gate jest zamknięty | PASS |
| CONF01-DOD-37 | lineage reproducibility gate jest zamknięty | PASS |
| CONF01-DOD-38 | reconciliation gate jest zamknięty | PASS |
| CONF01-DOD-39 | conflict gate jest zamknięty | PASS |
| CONF01-DOD-40 | estimate assumption gate jest zamknięty | PASS |
| CONF01-DOD-41 | evidence independence gate jest zamknięty | PASS |
| CONF01-DOD-42 | mechanism evidence gate jest zamknięty | PASS |
| CONF01-DOD-43 | nadrzędna reguła gate jest deterministyczna | PASS |
| CONF01-DOD-44 | metric well_supported jest zdefiniowane | PASS |
| CONF01-DOD-45 | metric supported_with_limitations jest zdefiniowane | PASS |
| CONF01-DOD-46 | metric partially_supported jest zdefiniowane | PASS |
| CONF01-DOD-47 | metric weakly_supported jest zdefiniowane | PASS |
| CONF01-DOD-48 | metric not_assessable jest zdefiniowane | PASS |
| CONF01-DOD-49 | finding confidence ma kompletne reguły | PASS |
| CONF01-DOD-50 | mechanism confidence ma kompletne reguły | PASS |
| CONF01-DOD-51 | mechanism ma wyższy próg dowodowy | PASS |
| CONF01-DOD-52 | hypothesis boundary jest zamknięta | PASS |
| CONF01-DOD-53 | correlation boundary jest zamknięta | PASS |
| CONF01-DOD-54 | no-signal boundary jest zamknięta | PASS |
| CONF01-DOD-55 | current/reference boundary jest zamknięta | PASS |
| CONF01-DOD-56 | matched/full scope boundary jest zamknięta | PASS |
| CONF01-DOD-57 | bridge confidence ma kontrakt | PASS |
| CONF01-DOD-58 | allocation confidence ma kontrakt | PASS |
| CONF01-DOD-59 | work_content/capacity boundary jest zamknięta | PASS |
| CONF01-DOD-60 | process confidence respektuje Core 10 | PASS |
| CONF01-DOD-61 | portfolio/finance confidence respektuje Core 10 | PASS |
| CONF01-DOD-62 | actual/adjusted pozostają oddzielne | PASS |
| CONF01-DOD-63 | conflict status ma katalog | PASS |
| CONF01-DOD-64 | estimate pozostaje jawny | PASS |
| CONF01-DOD-65 | assumption pozostaje jawne | PASS |
| CONF01-DOD-66 | reconciliation with explanation nie jest błędem | PASS |
| CONF01-DOD-67 | manual/system data boundary jest zamknięta | PASS |
| CONF01-DOD-68 | coverage jest claim-specific | PASS |
| CONF01-DOD-69 | timeliness jest claim-specific | PASS |
| CONF01-DOD-70 | limitations contract jest kompletny | PASS |
| CONF01-DOD-71 | validation contract jest kompletny | PASS |
| CONF01-DOD-72 | claim narrowing contract jest kompletny | PASS |
| CONF01-DOD-73 | claim rejection contract jest kompletny | PASS |
| CONF01-DOD-74 | stability contract jest kompletny | PASS |
| CONF01-DOD-75 | not_assessable jest poza porządkiem stability | PASS |
| CONF01-DOD-76 | basis versioning jest kompletne | PASS |
| CONF01-DOD-77 | rule-based mode jest kompletny | PASS |
| CONF01-DOD-78 | AI nie jest zależnością | PASS |
| CONF01-DOD-79 | FINDINGS pola bazowe są zachowane | PASS |
| CONF01-DOD-80 | FINDINGS rozszerzenia są kompletne | PASS |
| CONF01-DOD-81 | payload PRI jest kompletny | PASS |
| CONF01-DOD-82 | output orchestration jest kompletny bez orkiestracji | PASS |
| CONF01-DOD-83 | komunikat zarządczy ma wzorzec | PASS |
| CONF01-DOD-84 | brak automatycznych rekomendacji wykonawczych | PASS |
| CONF01-DOD-85 | scenariusze T01–T45 są kompletne | PASS |
| CONF01-DOD-86 | CONF01-VAL jest kompletne | PASS |
| CONF01-DOD-87 | CONF01-ACC jest kompletne | PASS |
| CONF01-DOD-88 | QCONF01 jest kompletne | PASS |
| CONF01-DOD-89 | Core 10 pozostaje zamrożony | PASS |
| CONF01-DOD-90 | PRI-01 pozostaje zamrożony | PASS |
| CONF01-DOD-91 | pełna orkiestracja pozostaje otwarta | PASS |
| CONF01-DOD-92 | CONF-02 nie został rozpoczęty | PASS |
| CONF01-DOD-93 | brak danych SPZOZ | PASS |
| CONF01-DOD-94 | brak danych pacjentów | PASS |
| CONF01-DOD-95 | katalog confidence_validation_action jest zamknięty | PASS |
| CONF01-DOD-96 | confidence_validation_actions jest uporządkowane i unikalne | PASS |
| CONF01-DOD-97 | każde działanie walidacyjne ma podstawę i cel | PASS |
| CONF01-DOD-98 | CONF nie ustala priorytetu walidacji | PASS |
| CONF01-DOD-99 | wymóg niezależności jest deterministyczny | PASS |
| CONF01-DOD-100 | podstawa wymogu niezależności jest jawna | PASS |
| CONF01-DOD-101 | wystarczalność niezależności jest jawna | PASS |
| CONF01-DOD-102 | brak sztucznej reguły dwóch źródeł | PASS |
| CONF01-DOD-103 | precedencja partial / weak / not_assessable jest zamknięta | PASS |
| CONF01-DOD-104 | partially_supported wymaga zawężonej treści | PASS |
| CONF01-DOD-105 | weakly_supported wymaga rzeczywistego sygnału | PASS |
| CONF01-DOD-106 | not_assessable wymaga braku wystarczającego sygnału | PASS |
| CONF01-DOD-107 | claim_type wskazuje klasę podstawową | PASS |
| CONF01-DOD-108 | confidence_class_source_level jest zamknięty | PASS |
| CONF01-DOD-109 | klasy poziomów nie są przepisywane | PASS |

## 24. Test końcowy QCONF01

Test końcowy obejmuje 184 niezależne kontrole metodologiczne wskazane dla CONF-01. Wszystkie muszą mieć wynik PASS.

| ID | Kontrola | Wynik |
| --- | --- | --- |
| QCONF01-001 | CONF-01 jest uniwersalny branżowo. | PASS |
| QCONF01-002 | Confidence ≠ priority. | PASS |
| QCONF01-003 | Confidence ≠ decision readiness. | PASS |
| QCONF01-004 | Confidence ≠ probability. | PASS |
| QCONF01-005 | confidence_score pozostaje null. | PASS |
| QCONF01-006 | Brak globalnego score 0–100. | PASS |
| QCONF01-007 | Brak wag. | PASS |
| QCONF01-008 | Brak arbitralnych progów confidence. | PASS |
| QCONF01-009 | Brak HIGH/MEDIUM/LOW jako metodologii użytkowej. | PASS |
| QCONF01-010 | Istnieją trzy poziomy: metric, finding, mechanism. | PASS |
| QCONF01-011 | Metric confidence nie przenosi się automatycznie na finding. | PASS |
| QCONF01-012 | Finding confidence nie przenosi się automatycznie na mechanism. | PASS |
| QCONF01-013 | Claim ma jawny claim_id. | PASS |
| QCONF01-014 | Claim ma jawny claim_type. | PASS |
| QCONF01-015 | Claim ma scope i period. | PASS |
| QCONF01-016 | Evidence ma jawny evidence_id. | PASS |
| QCONF01-017 | Evidence ma rolę. | PASS |
| QCONF01-018 | Supporting evidence nie zastępuje required primary evidence. | PASS |
| QCONF01-019 | Contextual evidence nie jest automatycznie primary evidence. | PASS |
| QCONF01-020 | Contradictory evidence pozostaje widoczne. | PASS |
| QCONF01-021 | Brak evidence nie staje się contradictory evidence. | PASS |
| QCONF01-022 | Evidence independence jest jawna. | PASS |
| QCONF01-023 | Shared source nie jest niezależnym potwierdzeniem. | PASS |
| QCONF01-024 | Kilka testów nie działa jak głosowanie. | PASS |
| QCONF01-025 | Cross-test support ma status. | PASS |
| QCONF01-026 | Cross-test contradiction ma status. | PASS |
| QCONF01-027 | MGT inputs nie są redefiniowane. | PASS |
| QCONF01-028 | MGT fit ≠ well_supported. | PASS |
| QCONF01-029 | MGT decision_blocked ≠ low confidence. | PASS |
| QCONF01-030 | Required information jest claim-specific. | PASS |
| QCONF01-031 | Required information gate ma katalog. | PASS |
| QCONF01-032 | Definition/semantics gate istnieje. | PASS |
| QCONF01-033 | Scope/period gate istnieje. | PASS |
| QCONF01-034 | Comparability gate istnieje. | PASS |
| QCONF01-035 | Lineage/reproducibility gate istnieje. | PASS |
| QCONF01-036 | Reconciliation gate istnieje. | PASS |
| QCONF01-037 | Conflict gate istnieje. | PASS |
| QCONF01-038 | Estimate/assumption gate istnieje. | PASS |
| QCONF01-039 | Evidence independence gate istnieje. | PASS |
| QCONF01-040 | Mechanism evidence gate istnieje. | PASS |
| QCONF01-041 | Metric well_supported wymaga required gate pass. | PASS |
| QCONF01-042 | Comparative metric well_supported wymaga comparability. | PASS |
| QCONF01-043 | supported_with_limitations ma jawne limitations. | PASS |
| QCONF01-044 | partially_supported wymaga zawężenia zakresu lub claim. | PASS |
| QCONF01-045 | weakly_supported nie udaje stabilnej podstawy decyzji. | PASS |
| QCONF01-046 | not_assessable wymaga braku odpowiedzialnej podstawy. | PASS |
| QCONF01-047 | Finding well_supported nie wymaga wielu testów. | PASS |
| QCONF01-048 | Mechanism ma ostrzejszy próg niż finding. | PASS |
| QCONF01-049 | Hypothesis nie jest automatycznie well_supported. | PASS |
| QCONF01-050 | Correlation nie jest causal proof. | PASS |
| QCONF01-051 | Verified constraint może wspierać mechanism zgodnie z PROC-02. | PASS |
| QCONF01-052 | Największa kolejka nie jest mechanizmem sama w sobie. | PASS |
| QCONF01-053 | Najdłuższy etap nie jest mechanizmem sam w sobie. | PASS |
| QCONF01-054 | High utilization nie jest mechanizmem sam w sobie. | PASS |
| QCONF01-055 | NO_ADVERSE_SIGNAL nie dowodzi braku problemu poza zakresem. | PASS |
| QCONF01-056 | NO_ADVERSE_SIGNAL może być well_supported tylko przy wystarczającym teście. | PASS |
| QCONF01-057 | Manual data nie jest automatycznie słabsze. | PASS |
| QCONF01-058 | System data nie jest automatycznie mocniejsze. | PASS |
| QCONF01-059 | Estimate ≠ measured data. | PASS |
| QCONF01-060 | Assumption ≠ evidence. | PASS |
| QCONF01-061 | Unsupported essential assumption ogranicza confidence. | PASS |
| QCONF01-062 | reconciled_with_explanation nie jest błędem. | PASS |
| QCONF01-063 | unreconciled required evidence ogranicza confidence. | PASS |
| QCONF01-064 | Conflict nie jest rozstrzygany przez większą wartość. | PASS |
| QCONF01-065 | Conflict nie jest rozstrzygany przez nowszą wartość bez basis. | PASS |
| QCONF01-066 | Nie ma majority voting. | PASS |
| QCONF01-067 | Independent evidence może wzmacniać confidence. | PASS |
| QCONF01-068 | Dwa niezależne evidence nie gwarantują well_supported. | PASS |
| QCONF01-069 | Shared transformation ogranicza niezależność. | PASS |
| QCONF01-070 | Current metric może być mocne przy słabym reference. | PASS |
| QCONF01-071 | Claim o zmianie wymaga reference comparability. | PASS |
| QCONF01-072 | Matched scope nie jest mieszane z full scope. | PASS |
| QCONF01-073 | Bridge confidence nie zmienia matematyki mostu. | PASS |
| QCONF01-074 | Allocation confidence nie redefiniuje allocation policy. | PASS |
| QCONF01-075 | Work_content globalny pozostaje otwartym kontraktem. | PASS |
| QCONF01-076 | Capacity mapping globalny pozostaje otwartym kontraktem. | PASS |
| QCONF01-077 | PROC confidence korzysta z timestamp/route evidence. | PASS |
| QCONF01-078 | FIN/PORT confidence korzysta z cost attribution i matched scope. | PASS |
| QCONF01-079 | One-off actual i adjusted nie są mieszane. | PASS |
| QCONF01-080 | Confidence limitations są jawne. | PASS |
| QCONF01-081 | Critical limitation jest jawna. | PASS |
| QCONF01-082 | Confidence validation required jest jawne. | PASS |
| QCONF01-083 | CONF nie ustala priority walidacji. | PASS |
| QCONF01-084 | Claim narrowing jest możliwe. | PASS |
| QCONF01-085 | Claim rejection nie oznacza prawdziwości przeciwnej tezy. | PASS |
| QCONF01-086 | Evidence coverage jest claim-specific. | PASS |
| QCONF01-087 | Brak arbitralnego coverage threshold. | PASS |
| QCONF01-088 | Evidence timeliness jest context-specific. | PASS |
| QCONF01-089 | Brak arbitralnego freshness threshold. | PASS |
| QCONF01-090 | Confidence basis ma wersję. | PASS |
| QCONF01-091 | Confidence evaluation date jest jawna. | PASS |
| QCONF01-092 | Rule-based implementation jest możliwa. | PASS |
| QCONF01-093 | AI nie jest wymagane. | PASS |
| QCONF01-094 | AI nie zastępuje reguł. | PASS |
| QCONF01-095 | Nadrzędna klasyfikacja wynika z gate. | PASS |
| QCONF01-096 | Nie ma sumowania punktów gate. | PASS |
| QCONF01-097 | Required fail blokuje wysokie klasy. | PASS |
| QCONF01-098 | Required partial ogranicza klasę. | PASS |
| QCONF01-099 | All required pass pozwala na well_supported, ale nie wymusza go bez claim-specific conditions. | PASS |
| QCONF01-100 | Nie ma globalnego cap tylko z powodu jednego pola. | PASS |
| QCONF01-101 | PRI-01 pozostaje niezmieniony. | PASS |
| QCONF01-102 | Core 10 pozostaje niezmieniony. | PASS |
| QCONF01-103 | confidence_class jest kompatybilne z PRI-01. | PASS |
| QCONF01-104 | confidence_class domyślnie mapuje finding_confidence_class. | PASS |
| QCONF01-105 | confidence_score pozostaje null w payloadzie PRI. | PASS |
| QCONF01-106 | confidence_basis jest audytowalne. | PASS |
| QCONF01-107 | Output dla orkiestracji istnieje. | PASS |
| QCONF01-108 | Pełna orkiestracja nie jest projektowana. | PASS |
| QCONF01-109 | Mechanism confidence nie wydaje rekomendacji wykonawczej. | PASS |
| QCONF01-110 | CONF nie rekomenduje zatrudnienia. | PASS |
| QCONF01-111 | CONF nie rekomenduje zwolnień. | PASS |
| QCONF01-112 | CONF nie rekomenduje zmian cen. | PASS |
| QCONF01-113 | CONF nie rekomenduje zakupów. | PASS |
| QCONF01-114 | CONF nie rekomenduje zwiększenia capacity. | PASS |
| QCONF01-115 | CONF nie rekomenduje zamknięcia produktu. | PASS |
| QCONF01-116 | CONF nie wycenia potencjału. | PASS |
| QCONF01-117 | Brak danych SPZOZ. | PASS |
| QCONF01-118 | Brak danych pacjentów. | PASS |
| QCONF01-119 | Brak CONF-02. | PASS |
| QCONF01-120 | Istnieje co najmniej 40 scenariuszy. | PASS |
| QCONF01-121 | VAL kompletne. | PASS |
| QCONF01-122 | ACC kompletne. | PASS |
| QCONF01-123 | DOD kompletne. | PASS |
| QCONF01-124 | FINDINGS kompletne. | PASS |
| QCONF01-125 | Dokument jest implementowalny przez Aleksandra. | PASS |
| QCONF01-126 | Warstwa użytkowa jest po polsku. | PASS |
| QCONF01-127 | Angielskie nazwy są ograniczone do identyfikatorów technicznych. | PASS |
| QCONF01-128 | Metadane DOCX są zgodne. | PASS |
| QCONF01-129 | Dokument został wyrenderowany i sprawdzony wizualnie. | PASS |
| QCONF01-130 | Stabilność confidence porównuje ten sam claim_id, claim_type, scope i context. | PASS |
| QCONF01-131 | not_assessable nie uczestniczy w porządku stabilności. | PASS |
| QCONF01-132 | Porządek klas dla stabilności nie jest score. | PASS |
| QCONF01-133 | strengthening/weakening wymaga confidence_change_reason. | PASS |
| QCONF01-134 | Contradictory evidence count nie jest score. | PASS |
| QCONF01-135 | Independent evidence count nie jest score. | PASS |
| QCONF01-136 | Claim-specific limitations nie są uśredniane między claimami. | PASS |
| QCONF01-137 | Mechanism claim wymaga mechanism_evidence_gate. | PASS |
| QCONF01-138 | Finding claim może być well_supported bez mechanism claim. | PASS |
| QCONF01-139 | Metric claim może być well_supported bez finding claim. | PASS |
| QCONF01-140 | claim_narrowing_required zachowuje oryginalny claim_text. | PASS |
| QCONF01-141 | narrowed_claim_text nie nadpisuje danych źródłowych. | PASS |
| QCONF01-142 | claim_rejection_flag ma basis. | PASS |
| QCONF01-143 | bridge_confidence_class dotyczy bridge, nie całej organizacji. | PASS |
| QCONF01-144 | allocation_confidence_class dotyczy alokacji, nie automatycznie pełnego findingu. | PASS |
| QCONF01-145 | Evidence role contradictory nie jest usuwane przy klasie well_supported. | PASS |
| QCONF01-146 | Confidence class nie zmienia source test status. | PASS |
| QCONF01-147 | Confidence class nie zmienia problem_priority_action. | PASS |
| QCONF01-148 | Confidence class nie zmienia validation_priority_action. | PASS |
| QCONF01-149 | confidence_validation_action nie staje się pełną orkiestracją. | PASS |
| QCONF01-150 | Cross-test support consistent nie oznacza documented_independent. | PASS |
| QCONF01-151 | Cross-test support mixed nie oznacza automatycznie not_assessable. | PASS |
| QCONF01-152 | Unresolved conflict w supporting evidence nie musi blokować claim, jeśli nie jest required. | PASS |
| QCONF01-153 | Unresolved conflict w required evidence jest jawnie uwzględniony w gate. | PASS |
| QCONF01-154 | Estimate z dobrą podstawą może być legalnym evidence. | PASS |
| QCONF01-155 | Manual validation status z MGT jest respektowany. | PASS |
| QCONF01-156 | Data conflict flag z MGT jest respektowany. | PASS |
| QCONF01-157 | Trend comparability z MGT jest respektowana. | PASS |
| QCONF01-158 | Reconciliation status z MGT jest respektowany. | PASS |
| QCONF01-159 | Decision information status z MGT jest kontekstem, nie klasą confidence. | PASS |
| QCONF01-160 | confidence_validation_action korzysta z zamkniętego katalogu dwunastu działań. | PASS |
| QCONF01-161 | confidence_validation_actions jest uporządkowanym zbiorem unikalnych działań. | PASS |
| QCONF01-162 | Każde działanie walidacyjne ma confidence_validation_basis. | PASS |
| QCONF01-163 | confidence_validation_target wskazuje przedmiot walidacji. | PASS |
| QCONF01-164 | confidence_validation_target_id identyfikuje przedmiot walidacji. | PASS |
| QCONF01-165 | CONF-01 nie ustala priorytetu walidacji. | PASS |
| QCONF01-166 | evidence_independence_required ma deterministyczną podstawę. | PASS |
| QCONF01-167 | evidence_independence_requirement_basis jest jawne. | PASS |
| QCONF01-168 | evidence_independence_sufficient ma wartość logiczną. | PASS |
| QCONF01-169 | Wymagana i niewystarczająca niezależność blokuje mechanism_confidence_class = well_supported. | PASS |
| QCONF01-170 | Jeden bezpośredni dowód mechanizmu może być wystarczający zgodnie z metodologią źródłową. | PASS |
| QCONF01-171 | Dwa źródła nie oznaczają automatycznie well_supported. | PASS |
| QCONF01-172 | partially_supported wymaga claim_narrowing_required = true. | PASS |
| QCONF01-173 | partially_supported wymaga narrowed_claim_text. | PASS |
| QCONF01-174 | weakly_supported wymaga rzeczywistego sygnału dowodowego bez odpowiedzialnego zawężenia. | PASS |
| QCONF01-175 | not_assessable oznacza brak podstaw dla pełnego i możliwego zawężonego twierdzenia. | PASS |
| QCONF01-176 | Precedencja partially_supported / weakly_supported / not_assessable nie jest skalą punktową. | PASS |
| QCONF01-177 | Jeden claim_id reprezentuje jedno konkretne twierdzenie. | PASS |
| QCONF01-178 | claim_type wskazuje poziom ocenianego twierdzenia. | PASS |
| QCONF01-179 | confidence_class_source_level korzysta z zamkniętego katalogu trzech poziomów. | PASS |
| QCONF01-180 | metric_claim przekazuje metric_confidence_class. | PASS |
| QCONF01-181 | finding_claim przekazuje finding_confidence_class. | PASS |
| QCONF01-182 | mechanism_claim przekazuje mechanism_confidence_class. | PASS |
| QCONF01-183 | Klasa nie jest kopiowana automatycznie między poziomami. | PASS |
| QCONF01-184 | CONF01-T41–T45 są kompletne i zakończone wynikiem PASS. | PASS |

## 25. Status końcowy i otwarte kontrakty systemowe

| Element | Status |
| --- | --- |
| ZOP-CONF-01 v1.0 | ZAMKNIĘTY METODOLOGICZNIE DO IMPLEMENTACJI |
| ZOP-PRI-01 v1.0 | ZAMROŻONY – 0 zmian |
| Core 10 | ZAMROŻONY – 0 zmian |
| Pełna orkiestracja next_tests | DO OPRACOWANIA |
| ZOP-CONF-02 | NIE ROZPOCZĘTO |

### 25.1. Dziedziczone otwarte kontrakty

| Kontrakt | Zakres pozostający do opracowania |
| --- | --- |
| pełna orkiestracja next_tests | algorytm uruchamiania i kolejność między wynikami |
| globalna polityka istotności biznesowej | organizacyjne zasady materiality |
| globalny kontrakt work_content | wspólna semantyka nakładu pracy |
| globalny standard activity_unit i weighted_volume | jednostki aktywności i ważenie wolumenu |
| wspólna polityka alokacji shared cost | reguły przypisywania kosztów wspólnych |
| globalny standard kalendarzy operacyjnych i time_basis | spójność czasu operacyjnego |
| reguły capability/resource substitution | zasady zastępowalności zasobów |
| globalna podstawa kosztowa i klasyfikacja one-off | wspólna semantyka kosztu i korekt |
| pełny graf zależności i silnik reguł decyzyjnych | mechanizm wykonawczy poza CONF-01 i PRI-01 |
| ewentualna metodologia probabilistyczna | wyłącznie jako przyszły odrębnie zatwierdzony standard |

### 25.2. Potwierdzenia granic i kompletności

| Kontrola | Wynik |
| --- | --- |
| confidence_score 0–100 | 0 / null |
| arbitralne wagi | 0 |
| arbitralne progi confidence | 0 |
| automatyczne rekomendacje wykonawcze | 0 |
| zmiany FIN-01 / FIN-02 / FIN-03 | 0 / 0 / 0 |
| zmiany CAP-01 / CAP-02 / HR-01 | 0 / 0 / 0 |
| zmiany PORT-01 / PROC-01 / PROC-02 / MGT-01 | 0 / 0 / 0 / 0 |
| zmiany ZOP-PRI-01 | 0 |
| dane SPZOZ / dane pacjentów | 0 / 0 |
| rozpoczęta pełna orkiestracja / CONF-02 | 0 / 0 |
| CONF01-VAL | 92 / PASS |
| CONF01-ACC | 170 / PASS |
| CONF01-DOD | 109 / PASS |
| QCONF01 | 184 / PASS |
| Scenariusze CONF01-T | 45 / PASS |

> **STATUS ZOP-CONF-01 v1.0 – ZAMKNIĘTY METODOLOGICZNIE DO IMPLEMENTACJI. Dokument ocenia siłę wsparcia twierdzeń; nie ustala priorytetu problemu, nie ocenia pełnej gotowości decyzyjnej i nie podejmuje decyzji wykonawczej.**
