ZOPTYMALIZOWANI – X-RAY

# CAP-02

# Przeciążenie zasobu

Karta metodologiczna i specyfikacja implementacyjna

> **STATUS CAP-02 ZAMKNIĘTY METODOLOGICZNIE DO IMPLEMENTACJI**

| Pole | Wartość |
| --- | --- |
| Identyfikator | ZOP-XR-CAP-02 |
| Wersja / data | v1.0 / 2 września 2026 |
| Rola | siódmy pełny test diagnostyczny; wzorzec testów bilansowania popytu i zdolności |
| Odbiorcy | zarządzający, analityk, Aleksander – implementacja |
| Zależności | ZOP-PRI-01 i ZOP-CONF-01 – DO OPRACOWANIA |
| Źródła nadrzędne | polecenie; CAP-01; PROC-02; PROC-01; HR-01; PORT-01; FIN-01; ZOP-TECH-01; ZOP-MASTER-01 |

Dokument definiuje metodę bilansowania wymaganego work content z rzeczywiście dostępną, zgodną zdolnością. Nie zmienia CAP-01 ani pozostałych zamrożonych testów, nie projektuje CAP-03, aplikacji, panelu użytkownika ani warstwy AI.

## 1. Rola, cel i granice CAP-02

CAP-02 odpowiada na pytanie, czy zapotrzebowanie na pracę przekracza rzeczywiście dostępną zdolność zasobu lub grupy zasobów, kiedy i gdzie występuje presja, czy ma charakter chwilowy czy trwały oraz czy wynika z rzeczywistego niedoboru, czy z harmonogramu, struktury zasobów, procesu albo miksu działalności.

> **PYTANIE DIAGNOSTYCZNE Ile zgodnej zdolności potrzebujemy względem tego, ile rzeczywiście mamy w tym samym zakresie, czasie, lokalizacji, grupie zasobów, capability i jednostce?**

### 1.1. Łańcuch diagnostyczny

| Etap | Produkt | Granica |
| --- | --- | --- |
| Popyt | nowy, zaległy wymagany i rework | cały backlog ≠ popyt bieżącego okresu |
| Wymagana praca | work_content + podstawa | case count tylko przy jednorodności |
| Wymagana capacity | required_capacity | used ≠ required_capacity |
| Dostępna capacity | matched_effective_available | filtrowany widok effective_available |
| Bilans | signed gap, adverse gap, ratio | zgodne jednostki, scope i okres |
| Dowody | evidence vector | sygnał pojedynczy ≠ shortage |
| Trwałość i typ | overload_status + pressure_pattern + capacity_pressure_mechanisms | wzorzec czasowy ≠ mechanizm; presja bazowa ≠ niepokryty shortage |
| Hipotezy | przyczyny do weryfikacji | hipoteza ≠ ustalona przyczyna |
| Kolejne testy | next_tests z uzasadnieniem | bez globalnej orkiestracji |

> **ZASADA NADRZĘDNA Przeciążenie zasobu nie jest synonimem wysokiego wykorzystania. Zachodzi wtedy, gdy wiarygodnie oszacowane zapotrzebowanie na zgodną zdolność przekracza zdolność rzeczywiście dostępną w tym samym zakresie i okresie.**

Nie wolno automatycznie uznawać za przeciążenie: U = 100%; wysokiego utilization; dużej liczby usług; nadgodzin; kolejki; długiego czasu oczekiwania; used > available_source; ani opinii, że „brakuje ludzi”. Każdy element może być sygnałem, lecz żaden sam nie dowodzi trwałego niedoboru capacity.

## 2. CAP-01 a CAP-02

| Wymiar | CAP-01 | CAP-02 |
| --- | --- | --- |
| Pytanie | Ile posiadanej zdolności wykorzystujemy? | Ile zdolności potrzebujemy względem tego, ile rzeczywiście mamy? |
| Relacja | used / effective_available | required_capacity / matched_effective_available |
| Punkt ciężkości | wykorzystanie zdolności | bilans popytu i zgodnej zdolności |
| Praca | used – wykonana | required_capacity – wymagana |
| Wniosek | 100% nie dowodzi przeciążenia | presja może istnieć mimo used ≤ capacity |

> Relacja CAP-01
> U = used / effective_available Mierzy wykorzystanie; nie jest testem niedoboru.

> Relacja CAP-02
> capacity_pressure_ratio = required_capacity / matched_effective_available Mierzy presję tylko dla zgodnych jednostek, zakresu i okresu.

> **PRZYKŁAD required_capacity = 120, effective_available = 100, used = 100. CAP-01 może wykazać U = 100%, a CAP-02 dodatnią lukę 20 jednostek. Jeżeli used = 110, najpierw sprawdza się documented_extra_capacity, nadgodziny i błąd danych; available_source pozostaje nienaruszone.**

## 3. Wspólne definicje i semantyka capacity

| Pole | Definicja implementacyjna |
| --- | --- |
| available_source | Wartość dostępnej zdolności ze źródła, zachowana bez nadpisywania. |
| documented_extra_capacity | Dodatkowa faktycznie udostępniona zdolność, wprowadzona wyłącznie z dokumentacją zgodną z CAP-01. |
| effective_available | Zdolność używana do obliczeń po jawnych, udokumentowanych korektach CAP-01; CAP-02 nie tworzy drugiej definicji. |
| matched_effective_available | Suma effective_available wyłącznie zasobów mogących wykonać badaną pracę w zgodnym zakresie, czasie, lokalizacji, resource_group, capability i capacity_unit. Musi uzgadniać się równocześnie według źródła capacity oraz sposobu przypisania do demand scope. |
| used | Zdolność rzeczywiście wykorzystana do wykonanej pracy; nie opisuje popytu ani pracy wymaganej. |
| capacity_unit | Jednoznaczna jednostka zdolności, np. roboczogodzina, maszynogodzina, slot, cykl, minuta urządzenia. |
| capacity_basis | Podstawa przejścia od danych źródłowych do effective_available. |
| resource_group / resource_type | Grupa zasobów objęta bilansem / rodzaj zasobu. |
| capacity_committed_cost | Koszt utrzymywania zdolności z CAP-01; CAP-02 nie używa go do automatycznej wyceny luki. |
| activity_unit / weighted_volume / volume_comparability | Pola współdzielone do opisu działalności; nie zastępują work_content bez podstawy. |
| matched_base_available | Filtrowana część bazowej puli capacity zgodna z resource/capability/location/time; nie zmienia available_source ani effective_available. |
| matched_extra_capacity | Filtrowana część udokumentowanej extra capacity zgodna z tym samym demand scope. Wchodzi do matched_effective_available tylko raz. |
| direct_matched_available | Część matched_effective_available przypisana bezpośrednio i wyłącznie do danego demand scope. |
| allocated_shared_matched_capacity | Część rzeczywistej wspólnej puli przypisana do demand scope według capacity_allocation_basis; nie może być pełną pulą dla kilku odbiorców jednocześnie. |
| shared_effective_available | Rzeczywista effective_available wspólnej fizycznej puli, stanowiąca górną granicę sumy alokacji w tym samym okresie i capacity_unit. |
| shared_base_available | Bazowa część rzeczywistej wspólnej puli dostępnej dla konkurujących demand scopes, przed alokacją lokalną. |
| shared_extra_capacity | Udokumentowana dodatkowa część wspólnej puli, odrębna od shared_base_available i zgodna z semantyką CAP-01. |
| direct_base_available | Bazowa capacity przypisana bezpośrednio i wyłącznie do danego demand scope. |
| direct_extra_capacity | Udokumentowana extra capacity przypisana bezpośrednio i wyłącznie do danego demand scope. |
| allocated_shared_base_capacity | Część shared_base_available przypisana do demand scope według capacity_allocation_basis. |
| allocated_shared_extra_capacity | Część shared_extra_capacity przypisana do demand scope według capacity_allocation_basis. |

> **OCHRONA SEMANTYKI CAP-01 CAP-02 nie nadpisuje available_source, documented_extra_capacity ani effective_available. Nadgodzina, dodatkowa zmiana, wynajęty zasób, dodatkowa sesja lub inne zwiększenie capacity trafia do documented_extra_capacity tylko przy prawidłowym śladzie źródłowym.**

## 4. Zgodność zasobu z popytem

| Pole | Reguła |
| --- | --- |
| required_resource_group | Grupa zasobów wymagana przez badaną pracę. |
| capability_group | Jednoznaczna grupa kompetencji, uprawnień, funkcji lub parametrów technicznych wymaganych do realizacji. |
| capacity_match_status | matched / partially_matched / not_matched / unknown. |
| capacity_match_basis | Udokumentowana podstawa uznania zasobu za wymienny lub niewymienny w danym scope. |
| capacity_match_quality | Jakość dopasowania przekazywana do ZOP-CONF-01; bez lokalnego score. |
| capability_mapping_quality | Jakość mapy capability ↔ demand. |
| capacity_mapping_quality | Pole PROC-02: jakość mapy procesu/stage ↔ resource_group i capacity. |
| location | Lokalizacja faktycznie dostępna dla pracy; capacity niedostępna lokalizacyjnie nie jest matched. |

Nie sumuje się capacity zasobów, które nie mogą się zastąpić. Sto wolnych godzin zasobu A nie kompensuje automatycznie trzydziestu brakujących godzin zasobu B. Status partially_matched wymaga jawnego wydzielenia części dopasowanej i niedopasowanej; nie daje prawa do zaliczenia całej puli.

> **MATCHED_EFFECTIVE_AVAILABLE Nie jest nową definicją capacity, lecz filtrowanym widokiem effective_available. Obowiązują równocześnie: direct_matched_available = direct_base_available + direct_extra_capacity; allocated_shared_matched_capacity = allocated_shared_base_capacity + allocated_shared_extra_capacity; matched_base_available = direct_base_available + allocated_shared_base_capacity; matched_extra_capacity = direct_extra_capacity + allocated_shared_extra_capacity; matched_effective_available = matched_base_available + matched_extra_capacity; shared_effective_available = shared_base_available + shared_extra_capacity; oraz równoważnie matched_effective_available = direct_matched_available + allocated_shared_matched_capacity. Wszystkie składniki zachowują filtry resource/capability/location/time i muszą uzgadniać się do identycznego wyniku.**

## 5. Work content – centralny kontrakt popytowy

| Pole | Znaczenie |
| --- | --- |
| work_content | Ilość zgodnej capacity wymaganej do wykonania danego elementu pracy. |
| work_content_unit | Jednostka work content zgodna z capacity_unit albo objęta udokumentowanym przeliczeniem. |
| work_content_basis | measured / documented_standard / validated_weight / historical_observation / contractual_standard / other_documented_basis. |
| work_content_comparability | Czy praca jest porównywalna między okresami, trasami, produktami i grupami. |
| case_homogeneity_status | homogeneous / sufficiently_homogeneous / heterogeneous / unknown. |
| work_content_per_case | work_content / liczba porównywalnych przypadków; tylko przy prawidłowym mianowniku. |
| demand_component_id | Identyfikator pochodzenia elementu pracy chroniący przed podwójnym liczeniem. |

Nie używa się automatycznie case count, volume, revenue ani stage_elapsed_time jako work_content. Liczba przypadków może zastąpić work_content wyłącznie wtedy, gdy przypadki są wystarczająco jednorodne, jedna jednostka zużywa porównywalną capacity, capacity_unit jest zgodna, a założenie jawnie udokumentowane. Przy istotnej heterogeniczności surowy case count jest niedopuszczalny.

> **BRAK WIARYGODNEGO WORK CONTENT Nie tworzy się arbitralnych wag. Moduł bilansu capacity przyjmuje TEST_PARTIAL, a przy braku podstaw dla kluczowego scope – TEST_BLOCKED; pozostałe sygnały mogą być raportowane bez udawania pełnego bilansu.**

> Pracochłonność przypadku
> work_content_per_case = work_content / comparable_case_count Tylko przy porównywalnych przypadkach i work_content_unit.

> Podpisana luka pracochłonności
> work_content_per_case_gap_signed = work_content_per_case_current − work_content_per_case_reference Wartość dodatnia oznacza większą pracochłonność, nie automatycznie gorszą produktywność pracownika.

## 6. Zapotrzebowanie nowe, zaległe i rework

| Składnik | Definicja i ochrona |
| --- | --- |
| new_demand_work_content | Nowa praca wymagana w badanym okresie zgodnie z due_basis; nie obejmuje przyszłych zleceń. |
| carryover_due_work_content | Zaległa praca nadal wymagająca wykonania w okresie; pochodzi z backlog_due_work_content i nie jest ponownie nowym demand. |
| rework_work_content | Dodatkowa, potwierdzona praca z powtórzeń, poprawek lub ponownych przejść; oddzielona od nowych przypadków. |
| required_capacity | Suma składników wymaganego work content w tym samym scope, okresie i jednostce, po kontroli double count. |

> Wymagana zdolność
> required_capacity = new_demand_work_content + carryover_due_work_content + rework_work_content Wyłącznie przy zgodnych jednostkach, due basis i braku podwójnego liczenia demand_component_id.

Rework nie może zostać policzony jednocześnie jako nowy demand oraz rework_work_content. Jeden work item nie może wystąpić równocześnie jako new demand, carryover i rework bez udokumentowanego rozdzielenia różnych porcji pracy.

## 7. Due demand, backlog, deferral i unmet demand

| Pole | Semantyka |
| --- | --- |
| due_basis | Źródłowa reguła terminu: umowa, SLA, plan, zlecenie, polityka albo inna udokumentowana podstawa. |
| due_at | Termin wymagalności elementu pracy. |
| service_window | Dopuszczalne okno realizacji w spójnym kalendarzu. |
| deferrable_status | deferrable / not_deferrable / conditional / unknown. |
| backlog_start / backlog_end | Liczba elementów oczekujących na początku i końcu okresu. |
| backlog_work_content_start / end | Work content backlogu na początku i końcu, jeżeli możliwy do wyznaczenia. |
| backlog_due_work_content | Część backlogu wymagana w badanym okresie. |
| future_backlog_work_content | Praca oczekująca, której prawidłowy termin leży po badanym okresie. |
| unmet_demand_work_content | Część wymaganego work content niezrealizowana w wymaganym okresie. |
| deferred_work_content / deferral_basis | Praca legalnie lub biznesowo przesunięta / udokumentowana podstawa przesunięcia. |

> **REGUŁA DUE DEMAND Do required_capacity włącza się pracę wymaganą w okresie, należną w okresie oraz zaległą i nadal wymagającą realizacji. Nie włącza się automatycznie całej przyszłej kolejki. Przesunięcie zgodne z deferral_basis nie jest automatycznie service failure.**

## 8. Bilans capacity i wzory

> Podpisana luka względem bazowej capacity
> base_capacity_gap_signed = required_capacity − matched_base_available Wartość dodatnia wskazuje presję względem bazowej, zgodnej puli capacity.

> Niekorzystna luka względem bazowej capacity
> adverse_base_capacity_gap = max(base_capacity_gap_signed, 0) Nie oznacza automatycznie niedoboru strukturalnego, potrzeby zatrudnienia ani zakupu zasobu.

> Podpisana luka po udokumentowanej extra capacity
> effective_capacity_gap_signed = required_capacity − matched_effective_available Wartość dodatnia oznacza niepokryte zapotrzebowanie po uwzględnieniu rzeczywiście udostępnionej extra capacity.

> Niekorzystna luka effective i udział
> adverse_effective_capacity_gap = max(effective_capacity_gap_signed, 0) adverse_effective_capacity_gap_share_i = adverse_effective_capacity_gap_i / Σ adverse_effective_capacity_gap Suma 0 → null. Udział tylko dla zgodnej capacity_unit, okresu i porównywalnego scope.

> Współczynnik presji i czas występowania
> capacity_pressure_ratio = required_capacity / matched_effective_available. Dla matched_effective_available = 0 ratio = null / not_computable; required_capacity > 0 daje zero_capacity_with_demand = true. Czas zapisuje się oddzielnie: pressure_duration, pressure_duration_unit i pressure_bucket_count. Nie mnoży się luki przez czas i nie tworzy globalnego pressure score.

Wartość capacity_pressure_ratio > 1 matematycznie oznacza, że wiarygodnie oszacowane wymagane capacity przewyższa matched_effective_available w tej samej jednostce i okresie. Nie jest to arbitralny próg oraz nie przesądza o trwałym, strukturalnym niedoborze.

| Sytuacja | Wynik techniczny |
| --- | --- |
| required = 0; matched effective = 0 | ratio = null; zero_capacity_with_demand = false |
| required > 0; matched effective = 0 | ratio = null / not_computable; zero_capacity_with_demand = true |
| required > matched effective > 0 | effective gap > 0; adverse effective gap > 0; ratio > 1 |
| required ≤ matched effective | effective gap ≤ 0; adverse effective gap = 0; brak automatycznego shortage |

## 9. Capacity współdzielona, pooling i podwójne liczenie

| Pole / kontrola | Reguła |
| --- | --- |
| shared_resource_flag | Wskazuje fizyczną pulę obsługującą wiele konkurujących demand scopes. |
| capacity_allocation_basis | Odtwarzalna podstawa podziału base i extra capacity między odbiorców w tym samym okresie i capacity_unit. |
| shared_base_available | Źródłowo ustalona bazowa część wspólnej puli przed alokacją. |
| shared_extra_capacity | Źródłowo ustalona udokumentowana extra capacity wspólnej puli przed alokacją. |
| direct_base_available / direct_extra_capacity | Bezpośrednio przypisane składniki bazowy i dodatkowy danego demand scope. |
| allocated_shared_base_capacity | Alokowana do scope część shared_base_available; nie może być przesuwana bez capacity_allocation_basis. |
| allocated_shared_extra_capacity | Alokowana do scope część shared_extra_capacity; nie może być przesuwana bez capacity_allocation_basis. |
| direct_matched_available | direct_base_available + direct_extra_capacity. |
| allocated_shared_matched_capacity | allocated_shared_base_capacity + allocated_shared_extra_capacity. |
| matched_base_available | direct_base_available + allocated_shared_base_capacity. |
| matched_extra_capacity | direct_extra_capacity + allocated_shared_extra_capacity. |
| matched_effective_available | matched_base_available + matched_extra_capacity = direct_matched_available + allocated_shared_matched_capacity. |
| shared_effective_available | shared_base_available + shared_extra_capacity. |
| kontrole wspólnej puli | Σallocated_shared_base_capacity ≤ shared_base_available; Σallocated_shared_extra_capacity ≤ shared_extra_capacity; Σallocated_shared_matched_capacity ≤ shared_effective_available. |
| brak źródłowego podziału base/extra | extra_capacity_dependency dla zależnego lokalnego scope = null / not_assessable; podziału nie wolno zgadywać. |

> **CRITICAL Pełna wspólna pula nie może być matched capacity dla kilku demand scopes jednocześnie. Osobno kontroluje się sumy alokacji base i extra, a następnie sumę effective. Bez wiarygodnego capacity_allocation_basis lokalny bilans pozostaje TEST_PARTIAL albo TEST_BLOCKED. Gdy źródło nie pozwala rozdzielić shared pool na base i extra, nie wyznacza się extra_capacity_dependency dla zależnego scope.**

## 10. Nadgodziny i dodatkowa capacity

| Pole | Reguła |
| --- | --- |
| overtime_capacity | Zdolność udostępniona przez nadgodziny; jeśli spełnia CAP-01, stanowi część documented_extra_capacity. |
| overtime_used | Rzeczywiście wykorzystana część capacity nadgodzinowej; jest podzbiorem used, a nie dodatkowym użyciem. |
| overtime_basis | Dokumentacja okresu, zakresu, jednostki i źródła nadgodzin. |
| temporary_extra_capacity | Flaga kontekstu udokumentowanej czasowej zdolności. Powtarzalna zależność od extra capacity jest osobnym sygnałem diagnostycznym, a nie automatycznym verified shortage. |

Nadgodziny mogą być planowe, sezonowe, dobrowolną polityką organizacji albo elementem extra capacity. Nie są samodzielnym dowodem strukturalnego niedoboru. Nie wolno dodać tej samej overtime capacity jednocześnie do documented_extra_capacity i ponownie do matched_effective_available poza effective_available.

## 11. Rodzaje presji i niedopasowania

| pressure_pattern | Definicja diagnostyczna | Interpretacja |
| --- | --- | --- |
| temporary | Jednorazowy lub krótkotrwały wzorzec presji. | realna presja w oknie; bez tezy o trwałości |
| persistent | Presja powtarza się w porównywalnych okresach. | bez arbitralnej liczby miesięcy |
| seasonal | Presja odpowiada udokumentowanemu wzorcowi sezonowemu. | może być realna okresowo, nie całoroczna |
| volatile | Presja zmienia się nieregularnie między porównywalnymi oknami. | wymaga kontekstu i mapowania popytu |
| unknown | Brak podstaw do przypisania wzorca czasowego. | null evidence nie zastępuje się false |

| capacity_pressure_mechanism | Znaczenie |
| --- | --- |
| temporal_mismatch | capacity istnieje, lecz w niewłaściwym czasie |
| capability_mismatch | wolna capacity nie ma wymaganej capability |
| location_mismatch | capacity nie jest dostępna w wymaganej lokalizacji |
| allocation_mismatch | capacity istnieje, lecz została przydzielona do innego konkurującego scope |
| process_induced | rework, batching, gate, routing lub handoff zwiększa wymagane work content |
| structural_shortage | verified shortage po wykluczeniu dominujących temporal/capability/location/allocation/process mismatch |
| unresolved | brak podstaw do przypisania mechanizmu |
| capacity_pressure_mechanisms | lista wielu równoczesnych, udokumentowanych mechanizmów; nie wymusza jednej przyczyny |
| primary_capacity_pressure_mechanism | opcjonalny; tylko przy wystarczającej podstawie dominacji |
| capacity_pressure_mechanism_basis | dowody i reguła przypisania mechanizmu; wzorzec czasowy pozostaje osobnym polem |

Nie wymusza się mechanizmu bez danych. pressure_pattern opisuje charakter czasowy, a capacity_pressure_mechanism albo lista capacity_pressure_mechanisms opisuje sposób powstania presji. Przykładowo persistent i capability_mismatch mogą wystąpić równocześnie. structural_shortage jest dopuszczalne wyłącznie przy overload_status = verified_capacity_shortage i braku podstaw, że dominującym wyjaśnieniem jest niedopasowanie temporalne, capability, lokalizacyjne, alokacyjne lub procesowe.

## 12. Evidence vector

Każde pole dowodowe przyjmuje true, false albo null / not_assessable. Brak danych nie jest false. CAP-02 nie przekształca wektora dowodowego w lokalny wynik 0–100.

| Dowód | Warunek true | Granica |
| --- | --- | --- |
| base_capacity_pressure_evidence | required_capacity > matched_base_available na wiarygodnej, zgodnej podstawie | dowód presji względem puli bazowej; nie dowód niepokrytego shortage |
| queue_evidence | narasta backlog/queue albo pogarsza się queue_time | kolejka sama nie dowodzi shortage |
| overtime_evidence | udokumentowane overtime jest związane z absorpcją presji | samo overtime nie wystarcza |
| service_level_evidence | pogarsza się źródłowe SLA/terminowość lub występuje niezrealizowany popyt | bez wymyślania targetu |
| utilization_evidence | CAP-01 potwierdza wysokie/stabilne U lub użycie extra capacity | dowód pomocniczy |
| flow_evidence | PROC-02 potwierdza wpływ resource constraint na przepływ | gate/handoff nie jest shortage zasobu |
| response_evidence | po wzroście matched capacity przy porównywalnym popycie poprawia się queue/throughput/SLA | korelacja bez kontroli warunków nie wystarcza |
| process_evidence | udokumentowany rework, batching, gate, routing lub handoff zwiększa required work | możliwy process_induced_pressure |
| mix_evidence | zmiana portfolio mix zwiększa work_content przy porównywalnym volume | PORT-01 / HR-01 |
| schedule_mismatch_evidence | popyt i capacity rozmijają się w time_bucket mimo bilansu szerszego okresu | nie automatycznie structural |
| uncovered_capacity_shortage_evidence | required_capacity > matched_effective_available na wiarygodnej, zgodnej podstawie | podstawowy dowód niepokrytej luki; wymagany w bramce verified |

## 13. Overload status i bramka potwierdzenia

| overload_status | Warunek i znaczenie |
| --- | --- |
| not_detected | Brak wiarygodnej dodatniej luki w badanym scope albo popyt nie przekracza matched capacity. |
| candidate_overload | effective_capacity_gap_signed > 0 i jakość danych pozwala uznać niepokrytą presję za wiarygodny sygnał, lecz brak pełnego potwierdzenia niedoboru. |
| verified_capacity_shortage | Spełniona bramka dowodowa, dopasowanie capacity jest wiarygodne i brak krytycznej sprzeczności. |
| unresolved | Dane, mapowanie albo sprzeczności nie pozwalają rozstrzygnąć wyniku. |

> **BRAMKA VERIFIED_CAPACITY_SHORTAGE Wymaga uncovered_capacity_shortage_evidence = true; wiarygodnego capacity_match_status; co najmniej jednego z queue_evidence, overtime_evidence, service_level_evidence, flow_evidence lub response_evidence = true; oraz braku krytycznej sprzeczności danych. not_matched i unknown nie przechodzą bramki. partially_matched wymaga jawnego wydzielenia analizowanej części. Sama base_capacity_pressure_evidence lub extra_capacity_dependency nie wystarcza.**

Jeżeli presję wyjaśnia przede wszystkim schedule_mismatch_evidence, process_induced_pressure albo niewłaściwa alokacja zasobu, nie klasyfikuje się jej automatycznie jako structural_shortage. pressure_pattern zachowuje charakter czasowy, a capacity_pressure_mechanisms zachowują wszystkie udokumentowane mechanizmy bez wymuszania jednej przyczyny.

## 14. Trwałość, trend, sezonowość i miks

| Horyzont | Sposób użycia |
| --- | --- |
| zmiana / okno operacyjne | krótkookresowy bilans popytu i dostępności w naturalnym rytmie pracy |
| dzień / tydzień | piki, rozkład godzinowy, mismatch grafiku |
| 1M | sygnał miesięczny, nie dowód strukturalny |
| 3M / 6M | powtarzalność i kierunek w porównywalnych oknach |
| 12M / r/r | sezonowość i trwałość roczna |
| 24–36M | wzorzec wielookresowy, punkt zmiany, jeżeli dane istnieją |

| Pole | Reguła |
| --- | --- |
| pressure_persistence | Opis udziału porównywalnych time_bucket z presją oraz pressure_duration, pressure_duration_unit i pressure_bucket_count; bez arbitralnej granicy miesięcy. |
| pressure_trend_direction | DETERIORATING / STABLE / IMPROVING / VOLATILE / SEASONAL / unknown na podstawie porównywalnych obserwacji. |
| seasonality_context | Źródło i charakter sezonowości; nie kasuje wyniku lokalnego. |
| work_content_comparability | Warunek interpretacji zmiany pracochłonności i miksu. |
| portfolio_mix_change | Flaga zmiany struktury działalności; stabilny case count nie wyklucza rosnącego work content. |
| pressure_pattern | temporary / persistent / seasonal / volatile / unknown; nie koduje przyczyny presji. |
| capacity_pressure_mechanism_basis | Podstawa pozwalająca zachować równocześnie wzorzec czasowy i jeden lub wiele mechanizmów. |

## 15. Harmonogram, fragmentacja i kalendarze

| Pole | Znaczenie |
| --- | --- |
| time_bucket | Okno bilansu zgodne z naturalnym cyklem operacyjnym i danymi. |
| stage_operating_time | Czas operacyjny etapu z PROC-02; wymaga zgodnej podstawy czasu. |
| capacity_distribution_basis | Źródło rozkładu popytu i capacity wewnątrz szerszego okresu. |
| schedule_mismatch_evidence | True, gdy szersza pula wystarcza, ale nie jest dostępna w time_bucket zapotrzebowania. |
| capacity_fragmentation_signal | Capacity rozbita na krótkie okna, lokalizacje, niepasujące capability lub nieciągłe zmiany. |
| calendar_quality | Jakość i zgodność kalendarzy popytu, zasobu i procesu przekazywana do ZOP-CONF-01. |

> **KALENDARZE CAP-02 korzysta z istniejących podstaw czasu i zgłasza wymagania do wspólnego standardu kalendarzy operacyjnych. Nie zamyka tego standardu lokalnie i nie porównuje bilansów opartych na niezgodnych kalendarzach.**

## 16. Granica z PROC-01 i PROC-02

| Przypadek | Obserwacja | Interpretacja / następny test |
| --- | --- | --- |
| A | required > available; queue rośnie; PROC-02 potwierdza resource constraint | silne verified_capacity_shortage |
| B | required > available 8–10; capacity niewykorzystana 12–16 | temporal/schedule mismatch; nie structural |
| C | queue rośnie; required_capacity ≤ matched_effective_available | CAP-02 nie potwierdza shortage; PROC-02 |
| D | dodanie capacity nie zwiększa throughput | constraint prawdopodobnie gdzie indziej; PROC-02 |

PROC-01 dostarcza czas oczekiwania, delay hotspot, kalendarze, route_variant i miks tras. Delay hotspot ≠ bottleneck. PROC-02 dostarcza flow_evidence, constraint_status, constraint_entity_type, constraint_entity_id, mechanism_evidence, response_evidence, stage_operating_time, time_bucket i capacity_mapping_quality. Tylko verified_constraint o charakterze zasobowym wspiera shortage; gate_rule, handoff albo inny niezasobowy constraint nie jest dowodem braku zasobu.

## 17. Granice z pozostałymi testami

| Test | Relacja z CAP-02 |
| --- | --- |
| CAP-01 | Niskie U + brak presji: możliwa nadwyżka. Wysokie U + brak presji: dobrze wykorzystana capacity. Wysokie U + presja: możliwe przeciążenie. Niskie U + presja: sprawdź czas, capability, lokalizację, proces, gate i routing. |
| HR-01 | Wzrost work content lub spadek produktywności może zwiększać required_capacity. CAP-02 nie wnioskuje automatycznie „więcej ludzi”; HR-01 rozdziela cenę pracy, produktywność i efekt. |
| PORT-01 | Zmiana miksu może zwiększać required_capacity mimo stabilnego revenue lub volume. PORT-01 bada ekonomię na jednostkę constraint; CAP-02 nie decyduje o miksie. |
| FIN-01 / FIN-03 | CAP-02 przekazuje skalę fizyczną i sygnały. Nie przelicza gap × wynagrodzenie, unmet demand × revenue ani backlog × marża na pieniądze. |

> **GRANICA EKONOMICZNA CAP-02 nie tworzy „kosztu przeciążenia”. adverse_base_capacity_gap, adverse_effective_capacity_gap, unmet demand i backlog mogą zasilić test ekonomiczny dopiero z właściwą metodologią oraz podstawą przypisania. extra_capacity_dependency nie jest automatyczną decyzją o zatrudnieniu ani zakupie capacity.**

## 18. Wartość odniesienia i kontekst

| Kolejność | Źródło referencji | Warunek |
| --- | --- | --- |
| 1 | historia tego samego resource_group i capability | zgodna definicja i capacity_unit |
| 2 | wcześniejszy porównywalny okres | zgodny sezon i scope |
| 3 | plan | udokumentowana podstawa popytu i capacity |
| 4 | udokumentowany demand plan | zgodny due basis |
| 5 | porównywalny internal peer | udokumentowana wymienność i zakres |
| 6 | najlepszy własny stabilny okres | bez zdarzeń wyjątkowych |
| 7 | benchmark zewnętrzny | wyłącznie z wiarygodnym źródłem |

Nie ustanawia się arbitralnych norm utilization, staffing ratios ani progów pressure. Brak poprawnej referencji ogranicza analizę trendu i trwałości, ale nie musi blokować jednego zgodnego bilansu okresowego.

| process_context_flags | Katalog |
| --- | --- |
| flagi | demand_spike; seasonality; staff_absence; planned_shutdown; unplanned_downtime; system_failure; schedule_change; policy_change; launch_phase; reorganization; rework_spike; portfolio_mix_change; temporary_extra_capacity; external_dependency; other_context |

Flaga nie unieważnia wyniku. Zmienia interpretację, dobór referencji, pressure_pattern, capacity_pressure_mechanisms lub next_tests i pozostaje widoczna w FINDINGS.

## 19. Dekompozycja i hipotezy

| Poziom | Wynik minimalny |
| --- | --- |
| organization | bilans zbiorczy wyłącznie dla porównywalnych pul |
| unit | lokalizacja presji organizacyjnej |
| resource_group | podstawowy obiekt bilansu |
| capability_group | zgodność wymaganej i dostępnej capability |
| time_bucket | czas wystąpienia presji |
| opcjonalnie: stage / portfolio_item / route_variant | wyjaśnienie źródła popytu i mechanizmu |

> **HIPOTEZY DO WERYFIKACJI trwały niedobór capacity; chwilowy pik; sezonowość; grafik; niewłaściwy skill mix; lokalizacja; fragmentacja capacity; rework; wzrost pracochłonności; zmiana portfolio mix; nieprawidłowy routing; gate; batching; awaria; absencja; zbyt mała extra capacity; błąd work_content; błąd danych; błąd przypisania demand. Żadna pozycja nie jest automatycznie uznaną przyczyną.**

## 20. Walidacja danych – CAP02-VAL

Kontrole rodziny CAP02-VAL mają identyfikatory CAP02-VAL-01–CAP02-VAL-40. Każda zwraca PASS, WARNING albo CRITICAL. CRITICAL blokuje bilans zależny; moduły niezależne mogą działać jako TEST_PARTIAL z exclusion_flags i validation_notes.

### 20.1. Kontrole CAP02-VAL-01–CAP02-VAL-20

| Id | Kontrola | Reakcja |
| --- | --- | --- |
| CAP02-VAL-01 | Istnieje jednoznaczny resource_group i required_resource_group. | CRITICAL dla bilansu scope. |
| CAP02-VAL-02 | resource_type jest określony lub jawnie nieistotny. | WARNING / CRITICAL przy niejednoznaczności. |
| CAP02-VAL-03 | capacity_unit istnieje i jest jednoznaczna. | CRITICAL dla obliczeń. |
| CAP02-VAL-04 | direct_base_available, direct_extra_capacity, allocated_shared_base_capacity i allocated_shared_extra_capacity są nieujemne. | CRITICAL dla bilansu. |
| CAP02-VAL-05 | available_source zachowano bez nadpisania. | CRITICAL dla rekordu zależnego. |
| CAP02-VAL-06 | documented_extra_capacity ma źródło, powód, okres, scope i jednostkę. | CRITICAL dla extra; inaczej wyłączenie. |
| CAP02-VAL-07 | Wszystkie tożsamości base/extra oraz direct/shared uzgadniają się do matched_effective_available. | CRITICAL przy braku rekonsyliacji. |
| CAP02-VAL-08 | used istnieje, jest nieujemne i nie zostało utożsamione z demand. | WARNING / CRITICAL dla porównań CAP-01. |
| CAP02-VAL-09 | work_content istnieje dla modułu bilansu. | CRITICAL dla pełnego bilansu; TEST_PARTIAL możliwy. |
| CAP02-VAL-10 | work_content_unit istnieje. | CRITICAL dla required_capacity. |
| CAP02-VAL-11 | work_content_basis należy do udokumentowanego katalogu. | CRITICAL przy arbitralnej wadze. |
| CAP02-VAL-12 | work_content_unit i capacity_unit są zgodne lub mają udokumentowane przeliczenie. | CRITICAL. |
| CAP02-VAL-13 | direct_matched_available = direct_base_available + direct_extra_capacity. | CRITICAL dla lokalnego bilansu. |
| CAP02-VAL-14 | allocated_shared_matched_capacity = allocated_shared_base_capacity + allocated_shared_extra_capacity. | CRITICAL przy braku rekonsyliacji. |
| CAP02-VAL-15 | capability_group i capability mapping odpowiadają wymaganej pracy. | CRITICAL dla kompensacji. |
| CAP02-VAL-16 | Lokalizacja zasobu jest zgodna z dostępnością dla popytu. | WARNING / CRITICAL dla match. |
| CAP02-VAL-17 | due_basis istnieje dla pracy włączonej do okresu. | CRITICAL dla składnika demand. |
| CAP02-VAL-18 | due_at, service_window i deferrable_status są spójne. | WARNING / CRITICAL. |
| CAP02-VAL-19 | new_demand_work_content obejmuje tylko nową pracę due. | CRITICAL przy rozszerzeniu na przyszłość. |
| CAP02-VAL-20 | carryover_due_work_content pochodzi z backlogu due i nie jest new demand. | CRITICAL przy duplikacji. |

### 20.2. Kontrole CAP02-VAL-21–CAP02-VAL-40

| Id | Kontrola | Reakcja |
| --- | --- | --- |
| CAP02-VAL-21 | rework_work_content jest potwierdzony i wydzielony. | WARNING / CRITICAL. |
| CAP02-VAL-22 | demand_component_id chroni przed double count demand. | CRITICAL przy kolizji. |
| CAP02-VAL-23 | backlog_start/end są spójne z przepływem lub oznaczone ograniczeniem. | WARNING / CRITICAL dla queue evidence. |
| CAP02-VAL-24 | backlog_due i future_backlog są rozdzielone. | CRITICAL dla required_capacity. |
| CAP02-VAL-25 | deferred_work_content ma deferral_basis i nie jest automatycznie failure. | WARNING. |
| CAP02-VAL-26 | unmet_demand_work_content nie jest utożsamione z utraconym przychodem. | CRITICAL dla ekonomicznego wniosku. |
| CAP02-VAL-27 | Overtime i matched_extra_capacity są spójne z documented_extra_capacity i bez double count. | CRITICAL przy podwójnym liczeniu. |
| CAP02-VAL-28 | extra_capacity_dependency jest wyznaczane tylko przy źródłowym podziale shared pool na base i extra; inaczej null / not_assessable. | CRITICAL dla zgadywanego sygnału. |
| CAP02-VAL-29 | shared_base_available i shared_extra_capacity mają źródło oraz capacity_allocation_basis. | CRITICAL dla pełnego bilansu lokalnego. |
| CAP02-VAL-30 | Sumy allocated shared base, extra i matched nie przekraczają odpowiednich pul shared. | CRITICAL; TEST_PARTIAL albo TEST_BLOCKED. |
| CAP02-VAL-31 | pressure_pattern jest niezależny od capacity_pressure_mechanisms. | WARNING / CRITICAL dla klasyfikacji. |
| CAP02-VAL-32 | pressure_duration ma pressure_duration_unit; luka nie jest mnożona przez czas. | CRITICAL dla miary czasu. |
| CAP02-VAL-33 | route_variant/stage/process mapping nie miesza tras i etapów. | WARNING / CRITICAL. |
| CAP02-VAL-34 | case_homogeneity_status pozwala użyć case count jako proxy. | CRITICAL przy heterogeniczności. |
| CAP02-VAL-35 | Referencja ma źródło, okres, scope i reference_quality. | WARNING; trend/persistence częściowe. |
| CAP02-VAL-36 | work_content i mix są porównywalne między okresami. | WARNING / CRITICAL dla mix evidence. |
| CAP02-VAL-37 | seasonality_context i zdarzenia kontekstowe są jawne. | WARNING dla interpretacji. |
| CAP02-VAL-38 | Bramka verified wymaga uncovered_capacity_shortage_evidence i resource constraint, nie gate/handoff. | CRITICAL dla verified status. |
| CAP02-VAL-39 | structural_shortage ma verified status i wykluczone dominujące mismatch. | CRITICAL przy nieuprawnionej klasyfikacji. |
| CAP02-VAL-40 | Braki danych są null/not_assessable, a sprzeczności trafiają do exclusion_flags. | CRITICAL lub TEST_PARTIAL zależnie od modułu. |

## 21. Statusy logiczne X-Ray

| Status | Zastosowanie w CAP-02 |
| --- | --- |
| NO_ADVERSE_SIGNAL | brak wiarygodnej niekorzystnej presji w badanym scope |
| ADVERSE_SIGNAL | wiarygodny sygnał presji wymagający dalszego rozstrzygnięcia |
| INCIDENT | krótkotrwałe zdarzenie lub pojedynczy time_bucket |
| DETERIORATING | porównywalne okresy wskazują nasilanie presji |
| STABLE | brak kierunku zmiany albo stabilna presja opisana oddzielnie overload_status |
| IMPROVING | porównywalne okresy wskazują spadek presji |
| TEST_PARTIAL | część modułów ma wystarczającą podstawę |
| TEST_BLOCKED | brak podstaw do odpowiedzialnego bilansu zależnego |

overload_status jest oddzielnym technicznym statusem diagnostycznym. CAP-02 nie używa lokalnych kategorii MEDIUM, HIGH ani CRITICAL jako priorytetu; CRITICAL pozostaje wyłącznie wynikiem walidacji danych.

## 22. Dane dla ZOP-PRI-01 i ZOP-CONF-01

### 22.1. Payload dla ZOP-PRI-01

| Mechanizm | Pola |
| --- | --- |
| Priorytetyzacja – bez wzoru i progów | matched_base_available; matched_extra_capacity; shared_base_available; shared_extra_capacity; direct_base_available; direct_extra_capacity; allocated_shared_base_capacity; allocated_shared_extra_capacity; direct_matched_available; allocated_shared_matched_capacity; base_capacity_gap_signed; adverse_base_capacity_gap; effective_capacity_gap_signed; adverse_effective_capacity_gap; adverse_effective_capacity_gap_share; capacity_pressure_ratio; extra_capacity_dependency; extra_capacity_dependency_units; base_capacity_pressure_evidence; uncovered_capacity_shortage_evidence; overload_status; pressure_pattern; capacity_pressure_mechanism; capacity_pressure_mechanisms; capacity_pressure_mechanism_basis; pressure_duration; pressure_duration_unit; pressure_bucket_count; required_capacity; matched_effective_available; unmet_demand_work_content; backlog_due_work_content; pressure_persistence; pressure_trend_direction; overtime_evidence; queue_evidence; service_level_evidence; flow_evidence; response_evidence; process_induced_pressure; affected_units; affected_resource_groups; affected_portfolio_items; result_risk; urgent_validation |

### 22.2. Payload dla ZOP-CONF-01

| Mechanizm | Pola |
| --- | --- |
| Pewność – bez lokalnego score | capacity_data_completeness; effective_available_quality; matched_base_available_quality; matched_extra_capacity_quality; shared_base_available_quality; shared_extra_capacity_quality; direct_base_extra_quality; allocated_shared_base_extra_quality; shared_base_extra_split_quality; work_content_quality; work_content_comparability; capacity_match_quality; capacity_mapping_quality; capability_mapping_quality; due_basis_quality; backlog_quality; overtime_quality; extra_capacity_quality; extra_capacity_dependency_quality; demand_component_quality; reference_quality; calendar_quality; seasonality_quality; shared_resource_quality; shared_capacity_allocation_quality; capacity_pressure_mechanism_quality; pressure_duration_quality; double_count_control; PROC02_constraint_quality; manual_validation; exclusion_flags |

CAP-02 dostarcza dane obu mechanizmom. ZOP-PRI-01 i ZOP-CONF-01 pozostają DO OPRACOWANIA; dokument nie projektuje ich finalnych wzorów, klas ani progów.

## 23. Struktura FINDINGS

| Pole bazowe | Reguła CAP-02 |
| --- | --- |
| test_id | CAP-02 |
| scope | filtry organizacji, unit, zasobów, capability, procesu i capacity_unit |
| period | current + reference + horyzont / time_bucket |
| status | wspólny status logiczny X-Ray |
| finding | komunikat faktograficzny |
| metric_value | capacity_pressure_ratio albo jawnie wskazana miara |
| reference_value | wartość porównawcza albo null |
| gap | effective_capacity_gap_signed albo jawnie wskazana luka bazowa |
| impact_low / impact_high | odpowiedzialny przedział fizyczny albo null; bez automatycznej wyceny |
| confidence_score / confidence_class | wynik ZOP-CONF-01 albo null |
| next_tests | tablica testów z uzasadnieniem |
| validation_required | boolean |

| Grupa | Rozszerzenia CAP-02 |
| --- | --- |
| Identyfikacja | unit; resource_group; required_resource_group; resource_type; capability_group; stage; portfolio_item; route_variant; time_bucket |
| Capacity CAP-01 | capacity_unit; available_source; documented_extra_capacity; effective_available; used; capacity_basis; capacity_committed_cost |
| Capacity matched | matched_base_available; matched_extra_capacity; shared_base_available; shared_extra_capacity; direct_base_available; direct_extra_capacity; allocated_shared_base_capacity; allocated_shared_extra_capacity; matched_effective_available; direct_matched_available; allocated_shared_matched_capacity; shared_effective_available; capacity_match_status; capacity_match_basis; capacity_allocation_basis |
| Popyt i praca | work_content; work_content_unit; work_content_basis; work_content_comparability; work_content_per_case; case_homogeneity_status; demand_component_id |
| Składniki demand | new_demand_work_content; carryover_due_work_content; rework_work_content; required_capacity; unmet_demand_work_content; deferred_work_content |
| Due i backlog | due_basis; due_at; service_window; deferrable_status; deferral_basis; backlog_start; backlog_end; backlog_work_content_start; backlog_work_content_end; backlog_due_work_content; future_backlog_work_content |
| Bilans | base_capacity_gap_signed; adverse_base_capacity_gap; effective_capacity_gap_signed; adverse_effective_capacity_gap; adverse_effective_capacity_gap_share; capacity_pressure_ratio; zero_capacity_with_demand; extra_capacity_dependency; extra_capacity_dependency_units |
| Status i czas | overload_status; pressure_pattern; pressure_persistence; pressure_trend_direction; pressure_duration; pressure_duration_unit; pressure_bucket_count; seasonality_context |
| Evidence | base_capacity_pressure_evidence; uncovered_capacity_shortage_evidence; queue_evidence; overtime_evidence; service_level_evidence; utilization_evidence; flow_evidence; response_evidence; process_evidence; mix_evidence; schedule_mismatch_evidence |
| Mechanizm i proces | capacity_pressure_mechanism; capacity_pressure_mechanisms; primary_capacity_pressure_mechanism; capacity_pressure_mechanism_basis; capacity_fragmentation_signal; process_induced_pressure; capacity_distribution_basis; stage_operating_time; shared_resource_flag; compensating_capacity_groups |
| Kontekst i kontrola | process_context_flags; exclusion_flags; validation_notes |

## 24. Komunikat zarządczy

> **[STATUS] PRESJA NA ZDOLNOŚĆ W badanym okresie zapotrzebowanie na [resource_group / capability] wyniosło [required_capacity] [capacity_unit] wobec [matched_base_available] jednostek bazowych i [matched_effective_available] faktycznie dostępnych jednostek zgodnej capacity, w tym [matched_extra_capacity] extra capacity. Luka bazowa wynosi [base_gap], a luka po extra capacity [effective_gap]; capacity pressure ratio = [ratio]. Zależność od extra capacity: [extra_capacity_dependency / units]. Wzorzec presji: [pressure_pattern]; mechanizm(y): [capacity_pressure_mechanisms] na podstawie [basis]. Towarzyszące dowody: [evidence]. Wynik nie oznacza automatycznie potrzeby zwiększenia zatrudnienia ani zakupu zasobu. Dalsza weryfikacja: [next_tests].**

Zakazane skróty interpretacyjne: „brakuje X etatów”; „trzeba zatrudnić”; „trzeba kupić urządzenie”; „zasób jest za mały”; „przeciążenie kosztuje X zł”. Każda rekomendacja pozostaje testowalnym kolejnym krokiem, a nie automatyczną decyzją.

## 25. Scenariusze testowe CAP02-T01–T27

| Id | Scenariusz | Dane | Oczekiwane |
| --- | --- | --- | --- |
| CAP02-T01 | Równowaga | required = available; brak queue i overtime | NO_ADVERSE_SIGNAL; not_detected |
| CAP02-T02 | Trwałe przeciążenie | required > matched w kolejnych okresach; queue rośnie | candidate / verified zgodnie z evidence |
| CAP02-T03 | Chwilowy pik | jednorazowo required > capacity; potem normalizacja | INCIDENT; temporary |
| CAP02-T04 | Wysokie utilization bez przeciążenia | U wysokie; required ≤ capacity | brak shortage |
| CAP02-T05 | Pełne wykorzystanie i unmet demand | used = capacity; required > capacity | dodatni capacity gap |
| CAP02-T06 | Used > available_source z extra | documented_extra_capacity istnieje | available_source bez zmiany; effective zgodne z CAP-01 |
| CAP02-T07 | Used > effective bez extra | brak udokumentowanej dodatkowej capacity | validation_required; nie poprawiaj available |
| CAP02-T08 | Tydzień wystarcza, godziny nie | pik poniedziałek rano; wolna capacity później | temporal/schedule mismatch; nie structural |
| CAP02-T09 | Capability mismatch | wolna capacity w innej kompetencji | allocation/capability mismatch |
| CAP02-T10 | Location mismatch | wolny zasób w niedostępnej lokalizacji | brak sztucznej kompensacji |
| CAP02-T11 | Rework zwiększa demand | unique cases stabilne; rework rośnie | jawny rework_work_content |
| CAP02-T12 | Zmiana miksu | case count stabilny; pracochłonność rośnie | required rośnie; PORT-01 / HR-01 |
| CAP02-T13 | Heterogeniczne case bez work content | brak prawidłowego przelicznika | TEST_PARTIAL; brak fałszywego bilansu |
| CAP02-T14 | Jednorodne case jako proxy | udokumentowana jednorodność i zgodna jednostka | case count dopuszczalne |
| CAP02-T15 | Backlog jeszcze nie due | duża przyszła kolejka | nie włączaj całości do required |
| CAP02-T16 | Zaległy backlog due | carryover powinien być wykonany teraz | carryover_due w required |
| CAP02-T17 | Extra capacity absorbuje presję | matched_base_available=100; required_capacity=115; matched_extra_capacity=15; matched_effective_available=115 | base gap=+15; effective gap=0; base evidence=true; uncovered evidence=false; dependency=true; brak verified; presja w FINDINGS |
| CAP02-T18 | Capacity zmniejsza queue | porównywalny demand; po dodaniu capacity queue spada | response_evidence=true |
| CAP02-T19 | Capacity nie poprawia throughput | queue przenosi się do następnego stage | brak prostego structural; PROC-02 |
| CAP02-T20 | Gate przy wolnej capacity | queue rośnie; required ≤ matched; gate blokuje | brak verified shortage; PROC-02 |
| CAP02-T21 | Shared resource | ten sam zasób obsługuje A i B | Σallocation ≤ effective_available |
| CAP02-T22 | Demand double count | ta sama sprawa jako carryover i new | walidacja CRITICAL blokuje sumę |
| CAP02-T23 | Wędrująca presja | kolejno przeciążane różne resource_group | bez jednego structural; PROC-02 / allocation |
| CAP02-T24 | Shared flexible resource dla dwóch demand scope | jeden zasób=100 h; A wymaga 80 h; B wymaga 80 h | jawna alokacja; Σallocation≤100; bez alokacji lokalne bilanse TEST_PARTIAL/BLOCKED; nie 100 h dla A i B |
| CAP02-T25 | Persistent capability mismatch | presja w wielu porównywalnych oknach; wolna capacity w innej capability | pressure_pattern=persistent; capacity_pressure_mechanism=capability_mismatch; oba fakty zachowane |
| CAP02-T26 | Pressure duration bez mnożenia jednostek | capacity gap=20 roboczogodzin; presja trwa 3 dni | gap=20 roboczogodzin; pressure_duration=3; pressure_duration_unit=day; brak wartości roboczogodzino-dni |
| CAP02-T27 | Shared pool – alokacja base/extra | shared base=80 h; shared extra=20 h; konkurujące demand scopes A i B | osobne kontrole Σbase i Σextra; poprawne extra_capacity_dependency dla każdego scope; brak dowolnego przesuwania extra bez capacity_allocation_basis |

PASS scenariusza wymaga poprawnej walidacji, obliczeń, overload_status, pressure_pattern, capacity_pressure_mechanisms, evidence vector, FINDINGS, validation_required, next_tests i wszystkich zakazów interpretacyjnych.

## 26. Kryteria odbioru implementacji

| Id | Kryterium / wynik | Id | Kryterium / wynik |
| --- | --- | --- | --- |
| CAP02-ACC-01 | zachowuje semantykę CAP-01 – PASS | CAP02-ACC-02 | zachowuje available_source bez nadpisania – PASS |
| CAP02-ACC-03 | przyjmuje documented_extra_capacity tylko z dokumentacją – PASS | CAP02-ACC-04 | wyznacza effective_available wyłącznie według CAP-01 – PASS |
| CAP02-ACC-05 | rekonsyliuje wszystkie tożsamości base/extra i direct/shared – PASS | CAP02-ACC-06 | waliduje capacity_unit – PASS |
| CAP02-ACC-07 | przyjmuje work_content – PASS | CAP02-ACC-08 | wymaga work_content_basis – PASS |
| CAP02-ACC-09 | obsługuje work_content_unit i zgodność przeliczenia – PASS | CAP02-ACC-10 | kontroluje case_homogeneity_status przy proxy – PASS |
| CAP02-ACC-11 | rozróżnia new_demand_work_content – PASS | CAP02-ACC-12 | rozróżnia carryover_due_work_content – PASS |
| CAP02-ACC-13 | rozróżnia rework_work_content – PASS | CAP02-ACC-14 | liczy required_capacity bez double count – PASS |
| CAP02-ACC-15 | liczy base_capacity_gap_signed – PASS | CAP02-ACC-16 | liczy adverse_base_capacity_gap – PASS |
| CAP02-ACC-17 | liczy effective_capacity_gap_signed i adverse_effective_capacity_gap – PASS | CAP02-ACC-18 | liczy ratio względem matched_effective_available – PASS |
| CAP02-ACC-19 | obsługuje zero_capacity_with_demand bez nieskończoności – PASS | CAP02-ACC-20 | waliduje capacity_match_status/basis – PASS |
| CAP02-ACC-21 | waliduje capability_group – PASS | CAP02-ACC-22 | waliduje location mismatch – PASS |
| CAP02-ACC-23 | bilansuje właściwy time_bucket – PASS | CAP02-ACC-24 | rozpoznaje schedule_mismatch_evidence – PASS |
| CAP02-ACC-25 | rozpoznaje capacity_fragmentation_signal – PASS | CAP02-ACC-26 | rozdziela backlog_start/end – PASS |
| CAP02-ACC-27 | rozdziela backlog due i future – PASS | CAP02-ACC-28 | stosuje due_basis, due_at i service_window – PASS |
| CAP02-ACC-29 | obsługuje deferral_basis – PASS | CAP02-ACC-30 | obsługuje unmet_demand_work_content bez wyceny – PASS |
| CAP02-ACC-31 | obsługuje overtime capacity/used/basis – PASS | CAP02-ACC-32 | ustala dependency tylko przy źródłowym podziale base/extra; inaczej null – PASS |
| CAP02-ACC-33 | obsługuje shared_base_available i shared_extra_capacity – PASS | CAP02-ACC-34 | alokuje shared base i extra wyłącznie z capacity_allocation_basis – PASS |
| CAP02-ACC-35 | kontroluje osobno Σbase, Σextra i Σmatched względem wspólnych pul – PASS | CAP02-ACC-36 | blokuje double count demand przez demand_component_id – PASS |
| CAP02-ACC-37 | ustala overload_status – PASS | CAP02-ACC-38 | rozdziela pressure_pattern od capacity_pressure_mechanisms – PASS |
| CAP02-ACC-39 | przechowuje oba pola pressure evidence jako true/false/null – PASS | CAP02-ACC-40 | verified gate wymaga uncovered_capacity_shortage_evidence – PASS |
| CAP02-ACC-41 | nie uznaje queue za samodzielny dowód – PASS | CAP02-ACC-42 | nie uznaje utilization za samodzielny dowód – PASS |
| CAP02-ACC-43 | nie uznaje overtime za samodzielny dowód – PASS | CAP02-ACC-44 | rozróżnia resource constraint od gate/handoff – PASS |
| CAP02-ACC-45 | kontroluje response_evidence – PASS | CAP02-ACC-46 | analizuje pressure_persistence bez arbitralnej liczby miesięcy – PASS |
| CAP02-ACC-47 | przechowuje pressure_duration i pressure_duration_unit bez mnożenia luki – PASS | CAP02-ACC-48 | uwzględnia seasonality_context – PASS |
| CAP02-ACC-49 | analizuje work_content_per_case i mix – PASS | CAP02-ACC-50 | wiąże PROC-01 bez zmiany jego metodologii – PASS |
| CAP02-ACC-51 | wiąże PROC-02 i capacity_mapping_quality – PASS | CAP02-ACC-52 | zapisuje w FINDINGS składniki shared/direct base/extra – PASS |
| CAP02-ACC-53 | przekazuje składniki alokacji base/extra do PRI – PASS | CAP02-ACC-54 | przekazuje jakość podziału shared base/extra do CONF – PASS |
| CAP02-ACC-55 | wskazuje next_tests z uzasadnieniem – PASS | CAP02-ACC-56 | nie rekomenduje automatycznie zatrudnienia ani zakupu zasobu – PASS |
| CAP02-ACC-57 | nie wycenia automatycznie capacity gap – PASS | CAP02-ACC-58 | przechodzi CAP02-T01–T27 – PASS |
| CAP02-ACC-59 | nie uruchamia CAP-03 – PASS | CAP02-ACC-60 | nie używa danych SPZOZ ani pacjentów – PASS |

## 27. Definition of Done

| Id | Kryterium / wynik | Id | Kryterium / wynik |
| --- | --- | --- | --- |
| CAP02-DOD-01 | cel – PASS | CAP02-DOD-02 | granica CAP-01 / CAP-02 – PASS |
| CAP02-DOD-03 | utilization ≠ overload – PASS | CAP02-DOD-04 | used ≠ required_capacity – PASS |
| CAP02-DOD-05 | effective_available z CAP-01 – PASS | CAP02-DOD-06 | matched capacity: pełne tożsamości base/extra i direct/shared – PASS |
| CAP02-DOD-07 | resource match – PASS | CAP02-DOD-08 | capability i lokalizacja – PASS |
| CAP02-DOD-09 | work content – PASS | CAP02-DOD-10 | work content basis – PASS |
| CAP02-DOD-11 | homogeneity proxy – PASS | CAP02-DOD-12 | due demand – PASS |
| CAP02-DOD-13 | new demand – PASS | CAP02-DOD-14 | carryover due – PASS |
| CAP02-DOD-15 | rework – PASS | CAP02-DOD-16 | required capacity – PASS |
| CAP02-DOD-17 | base/effective signed gaps – PASS | CAP02-DOD-18 | base/effective adverse gaps – PASS |
| CAP02-DOD-19 | effective gap share – PASS | CAP02-DOD-20 | pressure ratio i zero denominator – PASS |
| CAP02-DOD-21 | backlog – PASS | CAP02-DOD-22 | deferral – PASS |
| CAP02-DOD-23 | unmet demand – PASS | CAP02-DOD-24 | overtime – PASS |
| CAP02-DOD-25 | extra dependency nie jest zgadywane bez podziału źródłowego – PASS | CAP02-DOD-26 | shared base/extra oraz alokacje do scope – PASS |
| CAP02-DOD-27 | oddzielne kontrole shared base, extra i effective – PASS | CAP02-DOD-28 | double count demand control – PASS |
| CAP02-DOD-29 | pressure_pattern temporary/seasonal/volatile – PASS | CAP02-DOD-30 | pressure_pattern persistent bez arbitralnego progu – PASS |
| CAP02-DOD-31 | temporal mismatch jako mechanizm – PASS | CAP02-DOD-32 | capability/location/allocation mismatch – PASS |
| CAP02-DOD-33 | process-induced mechanism – PASS | CAP02-DOD-34 | overload status – PASS |
| CAP02-DOD-35 | capacity pressure mechanisms i basis – PASS | CAP02-DOD-36 | base/uncovered evidence vector – PASS |
| CAP02-DOD-37 | verified gate wymaga uncovered evidence – PASS | CAP02-DOD-38 | pressure duration i unit – PASS |
| CAP02-DOD-39 | trend – PASS | CAP02-DOD-40 | seasonality – PASS |
| CAP02-DOD-41 | mix – PASS | CAP02-DOD-42 | work content per case – PASS |
| CAP02-DOD-43 | context flags – PASS | CAP02-DOD-44 | reference – PASS |
| CAP02-DOD-45 | dekompozycja – PASS | CAP02-DOD-46 | capacity fragmentation – PASS |
| CAP02-DOD-47 | schedule mismatch – PASS | CAP02-DOD-48 | PROC-01 relationship – PASS |
| CAP02-DOD-49 | PROC-02 relationship – PASS | CAP02-DOD-50 | HR-01 relationship – PASS |
| CAP02-DOD-51 | PORT-01 relationship – PASS | CAP02-DOD-52 | economic boundary – PASS |
| CAP02-DOD-53 | next_tests – PASS | CAP02-DOD-54 | PRI payload z alokacją base/extra – PASS |
| CAP02-DOD-55 | CONF payload z jakością podziału shared base/extra – PASS | CAP02-DOD-56 | FINDINGS z pełną alokacją base/extra – PASS |
| CAP02-DOD-57 | komunikat zarządczy – PASS | CAP02-DOD-58 | 27 scenariuszy – PASS |
| CAP02-DOD-59 | 60 ACC – PASS | CAP02-DOD-60 | otwarte kwestie wspólne – PASS |

## 28. Test końcowy QCAP02

| Id | Kryterium / wynik | Id | Kryterium / wynik |
| --- | --- | --- | --- |
| QCAP02-01 | CAP-02 jest uniwersalny branżowo – PASS | QCAP02-02 | CAP-02 ≠ CAP-01 – PASS |
| QCAP02-03 | wykorzystanie ≠ przeciążenie – PASS | QCAP02-04 | used ≠ required_capacity – PASS |
| QCAP02-05 | effective_available zachowuje CAP-01 – PASS | QCAP02-06 | available_source nie jest nadpisywane – PASS |
| QCAP02-07 | matched capacity zachowuje pełne tożsamości base/extra i direct/shared – PASS | QCAP02-08 | work_content ma podstawę – PASS |
| QCAP02-09 | case count nie zastępuje automatycznie work content – PASS | QCAP02-10 | heterogeniczne case są chronione – PASS |
| QCAP02-11 | backlog ≠ cały bieżący demand – PASS | QCAP02-12 | due_basis istnieje – PASS |
| QCAP02-13 | future backlog nie wchodzi automatycznie do required – PASS | QCAP02-14 | carryover nie jest liczony dwa razy – PASS |
| QCAP02-15 | rework nie jest liczony dwa razy – PASS | QCAP02-16 | demand i capacity mają zgodne jednostki – PASS |
| QCAP02-17 | ratio > 1 dotyczy warstwy effective – PASS | QCAP02-18 | ratio przy zero capacity jest bezpieczne – PASS |
| QCAP02-19 | base/effective signed gap ≠ adverse gap – PASS | QCAP02-20 | effective adverse share ma zgodny scope – PASS |
| QCAP02-21 | nadwyżka capability A nie kompensuje shortage B – PASS | QCAP02-22 | overtime nie dubluje matched_extra_capacity – PASS |
| QCAP02-23 | dependency pozostaje null bez źródłowego podziału shared base/extra – PASS | QCAP02-24 | shared base, extra i effective mają oddzielne limity alokacji – PASS |
| QCAP02-25 | temporal mismatch ≠ structural_shortage – PASS | QCAP02-26 | capability mismatch współistnieje z pressure_pattern – PASS |
| QCAP02-27 | location/allocation mismatch nie jest sztucznie kompensowany – PASS | QCAP02-28 | process gate ≠ capacity shortage – PASS |
| QCAP02-29 | verified shortage wymaga uncovered_capacity_shortage_evidence – PASS | QCAP02-30 | brak danych ≠ false evidence – PASS |
| QCAP02-31 | queue sama nie wystarcza – PASS | QCAP02-32 | utilization samo nie wystarcza – PASS |
| QCAP02-33 | overtime samo nie wystarcza – PASS | QCAP02-34 | service failure samo nie wystarcza – PASS |
| QCAP02-35 | flow evidence rozróżnia resource od gate/handoff – PASS | QCAP02-36 | response evidence ma kontrolę porównywalności – PASS |
| QCAP02-37 | schedule mismatch jest mechanizmem, nie wzorcem czasowym – PASS | QCAP02-38 | capacity fragmentation istnieje – PASS |
| QCAP02-39 | seasonality jest pressure_pattern lub kontekstem – PASS | QCAP02-40 | mix jest kontrolowany – PASS |
| QCAP02-41 | rework load jest kontrolowany – PASS | QCAP02-42 | work_content_per_case nie jest oceną pracownika – PASS |
| QCAP02-43 | unmet demand nie jest utraconym revenue – PASS | QCAP02-44 | deferral nie jest automatycznie failure – PASS |
| QCAP02-45 | CAP-02 nie rekomenduje automatycznie zatrudnienia – PASS | QCAP02-46 | CAP-02 nie rekomenduje automatycznie zakupu sprzętu – PASS |
| QCAP02-47 | CAP-02 nie wycenia automatycznie gap w pieniądzu – PASS | QCAP02-48 | CAP-01 pozostaje niezmieniony – PASS |
| QCAP02-49 | PROC-01 pozostaje niezmieniony – PASS | QCAP02-50 | PROC-02 pozostaje niezmieniony – PASS |
| QCAP02-51 | HR-01 pozostaje niezmieniony – PASS | QCAP02-52 | PORT-01 pozostaje niezmieniony – PASS |
| QCAP02-53 | FIN-01 pozostaje niezmieniony – PASS | QCAP02-54 | ZOP-TECH-01 pozostaje niezmieniony – PASS |
| QCAP02-55 | ZOP-MASTER-01 pozostaje niezmieniony – PASS | QCAP02-56 | PRI pozostaje nieopracowane – PASS |
| QCAP02-57 | CONF pozostaje nieopracowane – PASS | QCAP02-58 | FINDINGS zawierają wszystkie składniki alokacji base/extra – PASS |
| QCAP02-59 | statusy logiczne są wspólne – PASS | QCAP02-60 | brak lokalnego Priority Score – PASS |
| QCAP02-61 | brak lokalnego Confidence Score – PASS | QCAP02-62 | istnieją CAP02-T01–T27 – PASS |
| QCAP02-63 | 60 ACC ma PASS – PASS | QCAP02-64 | 60 DOD ma PASS – PASS |
| QCAP02-65 | 40 VAL kontroluje rekonsyliację i limity shared base/extra – PASS | QCAP02-66 | next_tests nie podlegają lokalnej orkiestracji – PASS |
| QCAP02-67 | 0 danych SPZOZ – PASS | QCAP02-68 | 0 danych pacjentów – PASS |
| QCAP02-69 | 0 CAP-03 – PASS | QCAP02-70 | dokument można przekazać Aleksandrowi bez dodatkowej interpretacji – PASS |

## 29. Next tests i otwarte kwestie wspólne

| next_test | Kiedy rekomendować |
| --- | --- |
| PROC-02 | potwierdzenie rzeczywistego ograniczenia przepływu lub lokalizacja constraint |
| PROC-01 | presja objawia się głównie czasem oczekiwania, kolejką lub route_variant |
| CAP-01 | trzeba zbadać faktyczne wykorzystanie capacity i extra capacity |
| HR-01 | zmieniła się produktywność, work content lub organizacja pracy |
| PORT-01 | miks działalności generuje presję na wybraną capability |
| FIN-03 | presja może podnosić koszt jednostkowy |
| FIN-01 | problem może być istotny ekonomicznie dla organizacji |

| Otwarta kwestia wspólna | Status / wymaganie z CAP-02 |
| --- | --- |
| globalny kontrakt work_content | DO OPRACOWANIA; CAP-02 przekazuje pola, jednostki i zakaz arbitralnych wag |
| globalny standard kalendarzy operacyjnych | DO OPRACOWANIA; CAP-02 wymaga zgodności czasu |
| kwalifikacja capability i resource substitution | DO OPRACOWANIA; CAP-02 wymaga capacity_match_basis |
| globalna orkiestracja next_tests | DO OPRACOWANIA; CAP-02 przekazuje rekomendacje i uzasadnienia |
| ZOP-PRI-01 | DO OPRACOWANIA; payload bez score i progów |
| ZOP-CONF-01 | DO OPRACOWANIA; payload jakości bez score i progów |

> **DEFINITION OF DONE CAP02-DOD-01–CAP02-DOD-60 = PASS; QCAP02-01–QCAP02-70 = PASS; CAP02-T01–T27 = PASS; CAP02-ACC-01–CAP02-ACC-60 = PASS. CAP-02 może zostać przekazany Aleksandrowi do implementacji bez dodatkowej interpretacji metodologicznej.**

| Mechanizm | Status |
| --- | --- |
| CAP-02 | ZAMKNIĘTY METODOLOGICZNIE DO IMPLEMENTACJI |
| ZOP-PRI-01 | DO OPRACOWANIA |
| ZOP-CONF-01 | DO OPRACOWANIA |
| CAP-03 | NIE ROZPOCZĘTO |
