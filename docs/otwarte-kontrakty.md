# Otwarte kontrakty — Zoptymalizowani X-Ray

Rejestr miejsc, w których implementacja dotyka niejednoznaczności metodologicznej.

Plik ma trzy sekcje i nie wolno ich mieszać:

- **Sekcja A — odwołania.** Kontrakty świadomie pozostawione otwarte przez
  ZOP-MASTER-01 v1.2 rozdz. 17. Nie są nowymi lukami. Zapisujemy tu wyłącznie
  *miejsce styku z kodem* oraz przyjęte założenie robocze, żeby dało się je
  odnaleźć, gdy kontrakt macierzysty będzie domykany.
- **Sekcja B — nowe otwarte kontrakty.** Realne luki i sprzeczności odsłonięte
  przez implementację, w formacie z CLAUDE.md. Aleksander przedstawia je Michałowi.
- **Sekcja C — rozstrzygnięte.** Wpisy zamknięte decyzją. Zachowują pełną treść wraz
  z odrzuconymi wariantami, bo uzasadnienie decyzji jest tak samo częścią śladu jak
  ona sama. Wpisu rozstrzygniętego nie otwiera się ponownie bez nowego faktu.

Zasada z MASTER v1.2 pkt 17.1 obowiązuje: kontraktów nie domykamy „dla kompletności
dokumentacji", tylko wtedy, gdy konkretna ścieżka implementacji tego wymaga.

**Założenie i decyzja to dwa różne stany.** Dopóki wpis jest otwarty, kod nosi
komentarz `# ASSUMPTION:`. Po rozstrzygnięciu komentarz zmienia się na
`# DECYZJA (Michał, RRRR-MM-DD):` z numerem wpisu. Po samym kodzie ma być widać,
czy coś jest przyjętym założeniem, czy podjętą decyzją.

---

## Sekcja A — odwołania do kontraktów otwartych w MASTER v1.2

Brak wpisów otwartych.

---

## Sekcja B — nowe otwarte kontrakty

### B-16 — trwałość próby wobec atomowości zapisu wyników

**Dokument i miejsce:** ZOP-XR-V12-R1 karta wykonawcza §9
(`EVERY_ACTUAL_EXECUTION_ATTEMPT_PERSISTED = true`) wobec zasady zapisu z
`src/xray/store/findings.py`: „Przebieg, wykonanie i jego wyniki zapisujemy w jednej
transakcji. Wynik zapisany częściowo byłby śladem, który kłamie o tym, co policzono".
Miejsce styku z kodem: `FindingStore.save_run` — wywołanie `_save_attempt` jest ostatnie
wewnątrz `with self._db`.

**Na czym polega sprzeczność:** obie reguły są słuszne i wykluczają się w jednym
przypadku. Jeżeli zapis wyników zawiedzie (np. dwa rekordy o tym samym `finding_id`
w jednym wykonaniu naruszą klucz główny `findings`), transakcja cofa **całość** — razem
z wierszem próby. Obliczenie faktycznie się wykonało, a w magazynie nie zostaje po nim
nic. To jest dokładnie to, czego zakazuje §9: próba ma być trwała niezależnie od tego, co
stało się z jej wynikiem.

Druga strona jest równie twarda: gdyby próba zapisywała się osobno, mogłaby przeżyć zapis,
którego wyniki nie doszły — i magazyn niósłby ślad wykonania bez treści, czyli dokładnie
ten „ślad, który kłamie".

**Skala dzisiaj:** przypadek jest osiągalny wyłącznie przy błędzie zapisu, a każdy taki
błąd jest defektem wołającego (te same wyniki podane dwa razy) albo awarią bazy. Żadna
ścieżka produkcyjna go nie wywołuje. Zachowanie jest przypięte testem
`test_blad_zapisu_wynikow_cofa_takze_probe` w `tests/store/test_executions.py` — test pinuje
**stan otwartego kontraktu**, a nie regułę z karty.

**Warianty interpretacji:**

- A — jedna transakcja, stan dzisiejszy: przy błędzie zapisu próba ginie razem z wynikami.
- B — dwie transakcje: najpierw wyniki, potem próba w osobnej transakcji; próba przeżywa
  tylko wtedy, gdy wyniki doszły.
- C — próba w osobnym połączeniu i osobnej transakcji, zatwierdzana **przed** obliczeniem;
  ślad powstaje z chwilą uruchomienia, niezależnie od dalszego losu wyniku.

**Konsekwencja każdego wariantu dla kodu:**

- A — zero zmian; magazyn pozostaje spójny, ale w tym jednym przypadku łamie §9. Rozbieżność
  jest znana i zadeklarowana, a nie ukryta.
- B — próba przeżywa awarię zapisu wyników tylko częściowo: jeżeli padnie sam zapis próby,
  wracamy do punktu wyjścia. Kolejność odwrotna (najpierw próba) daje ślad wykonania bez
  treści — legalny według §9, ale wymagający pola mówiącego, że wyników nie ma.
- C — najbliżej litery §9: „faktycznie wykonana próba" zostaje zapisana w chwili, gdy
  faktycznie rusza. Cena: drugie połączenie do bazy, własna obsługa błędów i rekord próby,
  który przez moment nie ma jeszcze `execution_id` — czyli zmiana kontraktu tego pola.

**Propozycja robocza (do zatwierdzenia przez Michała / Controlling):** wariant A na czas
rundy V12-R1, jako **zadeklarowana rozbieżność**, nie jako rozstrzygnięcie. Wariant C jest
jedynym, który spełnia §9 co do litery, i to jego rekomenduję przy zamykaniu warstwy
wykonania — razem z decyzją, czym ma być `execution_provenance_ref` próby zapisanej przed
obliczeniem.

**Co blokuje:** zgodność z `EVERY_ACTUAL_EXECUTION_ATTEMPT_PERSISTED` w scenariuszu awarii
zapisu wyników; dowód trwałości próby w warunkach błędu.

**Czego nie blokuje:** trwałości prób na ścieżce poprawnej (każdy udany zapis zostawia
próbę), wektorów C-T14, C-T16, C-T18, C-T19, C-T22 i C-T23 ani żadnej tożsamości.

---

### B-15 — status testu, gdy §7.1 nie podaje reguły wyprowadzenia

**Dokument i miejsce:** ZOP-XR-FOUNDATION-BIND-01 **v1.2** §7.1 „Deterministyczny
TEST_PARTIAL" (l. 253–261) wobec §7, wiersz `execution_status` (l. 233), oraz §22, wiersze
T01 (l. 1213) i T02 (l. 1215). Miejsce styku z kodem: `src/xray/engine/units.py`, funkcja
`derive_test_status`.

**Na czym polega niejednoznaczność:** §7.1 podaje warunki wyłącznie dla **jednego** statusu
— `TEST_PARTIAL`. Cytat dosłowny warunków 1–4:

> 1. Wszystkie applicability legalnych execution units są rozstrzygnięte; nie ma UNIT_READY
>    przy finalizacji.
> 2. Co najmniej jedna applicable jednostka ma UNIT_EXECUTED.
> 3. Co najmniej jedna inna applicable jednostka ma UNIT_BLOCKED albo source-defined
>    not-computable outcome wpływający tylko na tę jednostkę.
> 4. Executed + blocked obejmuje wszystkie applicable jednostki.

§22 T01 domyka jeden przypadek poza tym: „GLOBAL prerequisite CRITICAL → TEST_BLOCKED.
| Bez zmiany." Zostają **dwa układy bez reguły**:

1. **wszystkie applicable jednostki są `UNIT_BLOCKED`** — warunek 2 nie jest spełniony, więc
   `TEST_PARTIAL` nie powstaje, a T01 mówi o blokadzie **globalnej**, nie o sumie blokad
   jednostkowych. Czy suma blokad jednostkowych to `TEST_BLOCKED`? Kontrakt nie mówi;
2. **żadna jednostka nie jest applicable** — v1.1 przewidywał tu `TEST_NOT_APPLICABLE`
   (scenariusz T13: „0 applicable modules … TEST_NOT_APPLICABLE"), ale ta wartość **nie
   należy do zamkniętego katalogu** `LogicalStatus`, który pochodzi z kart Core 10, a v1.2
   jej nie przywraca.

Trzeci układ — wszystkie jednostki wykonane — luką nie jest: status testu jest wtedy zwykłym
wynikiem diagnostycznym z zamrożonej karty, a jego wyliczenie to matematyka Core 10, poza
zakresem V12-R1 (v1.2 §21, kolumna „Nie dotyka": „Core10 formulas/results").

**Drugie pytanie, niezależne od pierwszego: wyjątek czy zapisywalny wynik?**

Pierwsze pytanie brzmi „jaki status", drugie — „co ma się stać, gdy statusu nie da się
wyprowadzić". Dziś `derive_test_status` podnosi `StatusNotDerivable`, czyli **wyjątek**.
Wyjątek nie zostawia śladu w FINDINGS, a zasada 5 z CLAUDE.md mówi wprost: „``null`` jest
poprawnym wynikiem. Brak informacji to pełnoprawny wynik diagnostyczny". Układ „wszystkie
jednostki zablokowane" jest faktem o danych, więc powinien dać się **zapisać** — z jawną
podstawą, tak jak każdy inny wynik.

Ryzyko jest konkretne i przewidywalne: ta ścieżka nie jest dziś uruchamiana przez żaden
test Core 10, więc pierwsza osoba implementująca FIN-01 trafi na wyjątek w połowie roboty
i „naprawi" go, wybierając status — czyli podejmie decyzję metodologiczną przy okazji
debugowania. Wpis ma temu zapobiec.

Warianty dla tego pytania: **E** — odmowa zostaje wyjątkiem, a warstwa uruchamiająca ma
obowiązek go obsłużyć; **F** — odmowa staje się wynikiem zapisywalnym: rekord z podstawą
i bez statusu logicznego, z polami wartości `null`; **G** — jedno i drugie: wyjątek na
poziomie funkcji wyprowadzającej, a warstwa uruchamiająca zamienia go na zapisywalny wynik
z podstawą. Wariant F i G wymagają rozstrzygnięcia pierwszego pytania tylko częściowo —
rekord bez statusu logicznego musi mieć w kontrakcie FINDINGS miejsce na taki stan.

**Warianty interpretacji (pierwsze pytanie — wartość statusu):**

- A — suma blokad jednostkowych daje `TEST_BLOCKED`; brak jednostek applicable wymaga
  osobnej decyzji o wartości statusu.
- B — oba układy dostają `TEST_BLOCKED`, przy czym drugi oznacza „nie ma czego liczyć".
- C — do katalogu wraca `TEST_NOT_APPLICABLE` dla drugiego układu; wymaga zmiany katalogu
  `LogicalStatus`, czyli decyzji metodologicznej na poziomie kart Core 10.
- D — stan dzisiejszy: `derive_test_status` **odmawia wyprowadzenia** i podnosi
  `StatusNotDerivable` z odesłaniem do tego wpisu.

**Konsekwencja każdego wariantu dla kodu:**

- A — jedna gałąź w wyprowadzeniu; drugi układ nadal otwarty.
- B — proste, ale zrównuje „wszystko zablokowane" z „nic nie dotyczy", a to dwa różne fakty
  diagnostyczne; wynik dla czytelnika komunikatu byłby mylący.
- C — najczystsze semantycznie i najdroższe: dotyka katalogu wspólnego dla dziesięciu kart,
  więc nie jest decyzją fundamentu.
- D — zero wymyślania. Koszt: test, który wpadnie w jeden z tych układów, nie dostanie
  statusu, tylko wyjątek z jawną podstawą — i to musi obsłużyć warstwa uruchamiająca.

**Propozycja robocza (do zatwierdzenia przez Michała / Controlling):** wariant D na czas
rundy V12-R1 dla pierwszego pytania i wariant G dla drugiego. Żaden test Core 10 nie jest
dziś zaimplementowany, więc układ ten nie wystąpi w praktyce przed rozstrzygnięciem; gdy
wystąpi, odmowa jest bezpieczniejsza niż zgadnięty status — ale ślad po tej odmowie powinien
trafić do FINDINGS, a nie zniknąć w wyjątku.

**Co blokuje:** wyprowadzenie statusu dla testu, którego wszystkie jednostki są zablokowane
albo nieaplikowalne.

**Czego nie blokuje:** `TEST_PARTIAL` (§7.1), `TEST_BLOCKED` z blokady globalnej (§22 T01),
statusów jednostek, blokowania selektywnego, wektorów T50 i T51 ani żadnej tożsamości.

---

### B-14 — katalog wartości trzech pól relacji w `ExecutionComparisonRecord`

**Dokument i miejsce:** ZOP-XR-V12-R1 karta wykonawcza §11 („ExecutionComparisonRecord
zawiera co najmniej: … **fingerprint_relation; payload_relation;
effective_exclusion_context_relation**; execution_relation_status; basis …") oraz
ZOP-XR-FOUNDATION-BIND-01 v1.2 §7.4.3. Miejsce styku z kodem:
`src/xray/store/comparisons.py`, stałe `RELATION_SAME`, `RELATION_DIFFERENT`,
`RELATION_NOT_ASSESSABLE`.

**Na czym polega niejednoznaczność:** to ta sama luka co w B-13, tylko o trzy pola dalej.
Kontrakt **wymaga** trzech osi relacji i dla żadnej nie podaje słownika wartości —
w przeciwieństwie do `execution_relation_status`, który §11.1 zamyka w tabeli na trzech
wartościach, i `fingerprint_status`, który §9 zamyka na `KNOWN | UNKNOWN`. Sprawdzone
2026-09-23: ani karta, ani v1.2 nie zawierają katalogu dla tych trzech pól.

Kod zapisuje w nich `"same"`, `"different"` albo `"not_assessable"` — wartości wyprowadzone
z faktów, nie z kontraktu.

**Dlaczego to nie jest blokada:** te trzy pola są **treścią** rekordu, a nie jego
tożsamością. `execution_comparison_id` hashuje wyłącznie profil relacji, kanoniczną parę
prób i referencję kontekstu (karta §11), więc rozbieżność słownictwa między wdrożeniami nie
rozjedzie żadnego identyfikatora ani nie zmieni `execution_relation_status`, który katalog
ma zamknięty.

**Warianty interpretacji:**

- A — Controlling zamyka trzy katalogi w karcie, tak jak zamknął `execution_relation_status`.
- B — pola stają się wartościami logicznymi (`same` jako `true`/`false`), a brak oceny
  wyraża `null`; prostsze, ale gubi rozróżnienie „różne" od „nie da się ocenić".
- C — pola pozostają opisowe i source-defined, a ich treść wiąże karta testu.
- D — stan dzisiejszy: trzy stałe w kodzie, jawnie oznaczone jako nasz opis.

**Konsekwencja każdego wariantu dla kodu:**

- A — trzy klasy wyliczeniowe i walidacja; ślad porównywalny między wdrożeniami.
- B — `fingerprint_relation` traci informację, której potrzebuje C-T18 i C-T19: „odciski
  różne" i „odcisku nie znamy" to nie to samo. Odradzam.
- C — fundament nie ma czego egzekwować w polu, którego sam wymaga.
- D — zero wymyślania; wartości czytelne lokalnie, nieporównywalne między wdrożeniami.

**Propozycja robocza (do zatwierdzenia przez Michała / Controlling):** wariant D jako stan
faktyczny, z rekomendacją A — najlepiej razem z B-13, bo to jedna decyzja o tym samym
kształcie.

**Co blokuje:** porównywalność treści rekordu relacji między niezależnymi wdrożeniami.

**Czego nie blokuje:** tożsamości relacji, katalogu `execution_relation_status`, wektorów
C-T14, C-T16, C-T18, C-T19, C-T22 ani C-T23.

**Bez migracji identyfikatorów:** te trzy pola nie wchodzą do skrótu — `execution_comparison_id`
hashuje wyłącznie `comparison_profile_version`, kanoniczną parę prób i
`comparison_context_reference` (karta §11). Zmiana słownika wartości nie unieważni więc
żadnego istniejącego identyfikatora relacji, a wpis da się rozstrzygnąć **po** rundzie R1
bez przeliczania czegokolwiek. To samo dotyczy `terminal_status` z B-13, który nie wchodzi
do `execution_attempt_id` (ten jest losowy).

---

### B-13 — katalog wartości `terminal_status` na rekordzie próby wykonania

**Dokument i miejsce:** ZOP-XR-V12-R1 karta wykonawcza §9 („ExecutionAttemptRecord wiąże co
najmniej: … **terminal status**; bindings do CalculationResultRecord; foundation_bind_version")
oraz ZOP-XR-FOUNDATION-BIND-01 v1.2 §7.4.2, gdzie pole występuje w identycznym wyliczeniu.
Miejsce styku z kodem: `src/xray/store/attempts.py`, pole
`ExecutionAttemptRecord.terminal_status`.

**Na czym polega niejednoznaczność:** oba dokumenty **wymagają** pola i żaden nie podaje
jego wartości. Sprawdzone 2026-09-23: w v1.2 fraza „terminal status" pada raz, w §7.4.2,
bez katalogu; w karcie raz, w §9, też bez katalogu. Dla porównania — `fingerprint_status`
dostaje w tej samej sekcji jawne `KNOWN | UNKNOWN`, a statusy relacji pary zamknięty zbiór
trzech wartości w §11.1. Tu takiego zamknięcia nie ma.

**Sprawdzone osobno 2026-09-23 — czy to nie jest nieporozumienie:** nie jest. Ani karta §9,
ani v1.2 §7.4.2 nie wiążą `terminal_status` próby ze statusem wykonania jednostki. Wartości
`UNIT_NOT_APPLICABLE | UNIT_READY | UNIT_BLOCKED | UNIT_EXECUTED` występują w v1.2 wyłącznie
w §7 (tabela pola `execution_status` jednostki wykonania) i w §7.1 (reguła deterministycznego
`TEST_PARTIAL`); w karcie V12-R1 nie padają ani razu, a w otoczeniu §7.4.2 nie ma do nich
odesłania. To zresztą dwie różne osie: `UNIT_*` opisuje **status komponentu testu**, a
`terminal_status` — **wynik jednego uruchomienia obliczenia**. Sklejenie ich byłoby tym
samym pomieszaniem osi, które mapa wpływu zgłosiła jako tezę T-3. Katalog statusów logicznych
(`LogicalStatus`) tym bardziej nie pasuje: opisuje wynik diagnostyczny, nie przebieg próby.

**Dlaczego mimo to nie jest to blokada:** pole jest proweniencją. Nie wchodzi do
`execution_attempt_id` (ten jest losowy), do żadnego skrótu kanonicznego ani do
`result_identity`. Rozbieżność wartości między implementacjami nie rozjedzie żadnej
tożsamości — utrudni jedynie czytanie śladu.

**Warianty interpretacji:**

- A — Controlling ustala zamknięty katalog (np. zakończenie poprawne, niepowodzenie,
  przerwanie) i wiąże go w karcie.
- B — katalog wywodzi się z istniejących statusów walidacji i logicznych, których X-Ray już
  używa; ryzyko: to są statusy **wyniku diagnostycznego**, nie przebiegu obliczenia, więc
  pomieszałyby dwie osie — dokładnie to, przed czym ostrzega teza T-3 z mapy wpływu.
- C — pole pozostaje łańcuchem source-defined, a katalog deklaruje karta testu.
- D — stan dzisiejszy: łańcuch niepusty, bez katalogu, z jawną adnotacją w docstringu.

**Konsekwencja każdego wariantu dla kodu:**

- A — jedna klasa wyliczeniowa i walidacja; ślad staje się porównywalny między wdrożeniami.
- B — zero nowej metodologii, ale wprowadza do warstwy wykonania słownik, który powstał dla
  warstwy diagnozy; odradzam.
- C — spójne z „source-defined", lecz fundament traci możliwość wyegzekwowania czegokolwiek.
- D — zero wymyślania; ślad czytelny lokalnie, nieporównywalny między wdrożeniami.

**Propozycja robocza (do zatwierdzenia przez Michała / Controlling):** wariant D jako stan
faktyczny na czas rundy V12-R1, z rekomendacją wariantu A przy zamykaniu warstwy rekordów.
Katalogu nie wymyślamy — byłby to słownik bez źródła, czyli złamanie zasady 1.

**Co blokuje:** porównywalność śladu wykonania między niezależnymi wdrożeniami; nic poza tym.

**Czego nie blokuje:** rekordu próby, bramki KNOWN/UNKNOWN, wektorów C-T18 i C-T19 ani
żadnej tożsamości.

---

### B-12 — co Scope Identity Contract v1.0 §4.1 zostawia otwarte w predykacie

**Dokument i miejsce:** ZOP-XR-FOUNDATION-BIND-01 v1.0 §4.1 pkt 3
(`docs/zrodla/ZOP-XR-FOUNDATION-BIND-01_v1.0.md:112`), dziedziczony i zamrożony
rozstrzygnięciem Controllingu z 2026-09-23 (wpis B-09, sekcja C). Miejsce styku z kodem:
`src/xray/canonical/scope.py`, klasy `ScopeOperator` i `ScopePredicate`.

**Na czym polega niejednoznaczność:** rozstrzygnięcie B-09 zamknęło pytanie o **strukturę**
predykatu, ale sam kontrakt zostawia trzy rzeczy nierozstrzygnięte.

**(1) Lista operatorów nie jest zamknięta.** Cytat dosłowny: „dozwolony operator musi być
technicznie jednoznaczny (**np.** EQ, NE, IN, NOT_IN, LT, LTE, GT, GTE, RANGE)". Wiążącym
kryterium jest „technicznie jednoznaczny", a dziewięć nazw to przykłady. Kod przyjmuje
dokładnie te dziewięć i odmawia pozostałych — nie dlatego, że lista jest zamknięta, tylko
dlatego, że nic w zamrożonym źródle innego operatora nie ustanawia. To samo rozumowanie
zastosowaliśmy przy wymiarach MGT-01 w pakiecie P3.

**(2) Kolekcja w `IN` i `NOT_IN`: zbiór czy sekwencja?** Kontrakt mówi o sortowaniu list
„o semantyce zbioru" (§4.1 pkt 4), ale nie mówi, że wartość `IN` taką semantykę ma.
Tymczasem `IN [A, B]` i `IN [B, A]` to ten sam zakres semantyczny — jeżeli dadzą różne
`scope_id`, złamana zostaje reguła `same_semantics → same_scope_id` z tego samego
paragrafu. Kod nie wnioskuje: kolekcja pozostaje sekwencją, dopóki wołający nie zadeklaruje
`CanonicalSet`.

**(3) Kształt wartości dla `RANGE` nie jest ustalony.** Ani liczba granic, ani ich
domknięcie (`[a,b]`, `[a,b)`), ani kolejność. Dwie implementacje zapiszą ten sam przedział
inaczej i policzą różne `scope_id`.

**(4) Skalar i jednoelementowy zestaw w `aggregation_level`.** Kontrakt mówi „Jawny poziom
agregacji. Dla zestawu wymiarów kolejność nie jest identity-defining" — przewiduje więc obie
postaci, ale nie rozstrzyga, czy `"UNIT"` i `["UNIT"]` to ten sam zakres. Kod traktuje je
jako różne (wynika to z reguły „wartości zachowują typ", §4.1 pkt 5) i pilnuje tego test
`test_pojedynczy_poziom_agregacji_to_nie_zestaw_jednoelementowy`. Jeżeli intencją było
utożsamienie, potrzebna jest decyzja, a nie zmiana kodu „z rozsądku".

**Warianty interpretacji:**

- A — Controlling domyka listę operatorów na dziewięciu, ustala, że kolekcja `IN`/`NOT_IN`
  ma semantykę zbioru, `RANGE` przyjmuje parę granic o jawnym domknięciu, a skalarny
  `aggregation_level` nie jest równy zestawowi jednoelementowemu.
- B — domknąć tylko operatory, resztę zostawić schematom kart testów.
- C — pozostawić wszystko trzy otwarte i wymagać, żeby każda karta wprowadzająca predykat
  deklarowała jego kształt u siebie.
- D — stan dzisiejszy: dziewięć operatorów, brak wnioskowania dla `IN`/`NOT_IN` i `RANGE`,
  odmowa dla operatorów nieustanowionych.

**Konsekwencja każdego wariantu dla kodu:**

- A — jedna zmiana w `ScopePredicate` (kwalifikacja wartości per operator) i komplet
  gwarancji zgodności między implementacjami; wymaga decyzji, bo domyka listę, której
  kontrakt nie domknął.
- B — połowiczne: operatory pewne, ale `IN [A,B]` nadal może dać dwa różne `scope_id`.
- C — zgodne z duchem „source-defined", ale przenosi ryzyko na dziesięć kart naraz i nie
  daje fundamentowi żadnej reguły do wyegzekwowania.
- D — zero wymyślania; `scope_id` z predykatem `IN` albo `RANGE` jest porównywalny tylko
  wtedy, gdy obie strony zbudowały go tym samym kodem.

**Propozycja robocza (do zatwierdzenia przez Michała / Controlling):** wariant D jako stan
faktyczny, wraz z rekomendacją wariantu A, bo tylko on przywraca regułę
`same_semantics → same_scope_id` dla predykatów zbiorowych i przedziałowych.

**Co blokuje:** zgodność bajtową `scope_id` między niezależnymi implementacjami dla
zakresów używających `IN`, `NOT_IN` albo `RANGE`; wprowadzenie operatora spoza dziewiątki.

**Czego nie blokuje:** pakietu P6 ani żadnego z wektorów C-T01–C-T21; zakresów opartych na
`EQ`, `NE` i porównaniach skalarnych, czyli wszystkich, jakie dziś budujemy.

---

### B-11 — jak liczba zmiennoprzecinkowa wchodzi do kanonicznego ładunku wyniku

**Dokument i miejsce:** ZOP-XR-FOUNDATION-BIND-01 v1.1 §7, wiersz `Decimal`
(„Skończona wartość decimal; canonical plain-decimal bez exponent, bez zbędnych trailing
zeros; `-0` → `0`; NaN/Inf prohibited") wobec kontraktu danych FINDINGS:
`src/xray/model/findings/finding.py:100` (`metric_value: float | None`), `:110` (`gap`),
`:117` (`impact_low`), `:120` (`impact_high`) oraz `src/xray/model/findings/refs.py:93`
(`reference_value: float | None`). Miejsce styku: `src/xray/canonical/result_payload.py`
— koperta odmawia wartości `float`, bo odmawia ich profil.

**Czego ten wpis NIE zgłasza:** to **nie jest** `RESULT_PAYLOAD_CANONICAL_TYPE_GAP`
i nie jest przesłanka STOP R1-S07. Profil ma typ dziesiętny, a v1.2 §7.4.1 ustala wprost
`RESULT_PAYLOAD_CANONICAL_TYPE_GAP = false` i `CONTROLLING_DECISION_REQUIRED = false`,
dopisując: „Dla obecnie legalnych result payload schemas nie zidentyfikowano typu poza
reprezentacją frozen XR_IDENTITY_CANONICAL_JSON_V1". Brakuje **wiązania**, nie typu.

**Na czym polega niejednoznaczność:** `float` jest liczbą binarną. Wartość zapisana
w kodzie jako `1250.5` ma dokładną wartość binarną, a wartość `0.1` — nie ma dokładnego
odpowiednika dziesiętnego o krótkim zapisie: jej dokładne rozwinięcie to
`0.1000000000000000055511151231257827021181583404541015625`. Przejście `float` →
`Decimal` można wykonać co najmniej na trzy sposoby, każdy daje inne bajty kanoniczne,
a więc inny `result_payload_digest`:

1. rozwinięcie dokładne (`Decimal(wartosc)`),
2. najkrótszy zapis odtwarzający tę samą liczbę binarną (`Decimal(repr(wartosc))`),
3. zaokrąglenie do skali zadeklarowanej przez schemat ładunku (np. dwa miejsca dla kwot).

Kontrakt nie wskazuje żadnego z nich, bo opisuje postać kanoniczną liczby dziesiętnej,
a nie sposób dojścia do niej z liczby binarnej. Dopóki to nie jest związane, dwie
implementacje policzą różne digesty z tej samej treści — czyli dokładnie to, czemu
kanonizacja ma zapobiegać.

**Warianty interpretacji:**

- A — schemat ładunku deklaruje skalę per pole (kwoty do grosza, wskaźniki do n miejsc),
  a konwersja kwantyzuje do niej jawnie.
- B — najkrótszy zapis odtwarzający tę samą wartość binarną (wariant 2).
- C — rozwinięcie dokładne (wariant 1).
- D — zmienić kontrakt danych FINDINGS z `float` na `Decimal` i nie konwertować w ogóle.

**Konsekwencja każdego wariantu dla kodu:**

- A — postać kanoniczna wynika ze schematu, a nie z przypadkowej reprezentacji binarnej;
  wymaga, żeby schemat ładunku deklarował skalę, czego dziś nie robi. Najbliżej intencji
  „canonical plain-decimal bez zbędnych zer".
- B — jedna linijka konwersji, zero deklaracji; wynik zależy od tego, jak liczba powstała
  w obliczeniu, więc dwie drogi do tej samej kwoty mogą dać różne digesty.
- C — wierny bajtom, ale kanoniczna kwota 1250.50 zapisuje się jako rozwinięcie
  z kilkudziesięcioma cyframi; audytowalne tylko formalnie.
- D — najczystsze semantycznie i najdroższe: dotyka kontraktu danych, walidacji, generatora
  i wszystkich tabel (`NumericValue` w `model/tables/base.py`). Poza zakresem V12-R1 — karta
  §15 zakazuje szerokiego refaktoru bez potrzeby rundy.

**Propozycja robocza (do zatwierdzenia przez Michała):** wariant A, wprowadzany dopiero
wtedy, gdy powstanie schemat ładunku wyniku (pakiet P7). Do tego czasu koperta **niczego
nie konwertuje i nie przyjmuje `float`** — odmowa jest świadoma i przypięta testem
`test_float_w_ladunku_odrzucony`. Cicha konwersja byłaby wybraniem jednego z czterech
wariantów bez decyzji.

**Co blokuje:** wpuszczenie dzisiejszej treści diagnostycznej (`metric_value`, `gap`,
`impact_low`, `impact_high`, `reference_value`) do `ResultPayloadEnvelopeV1`, a więc
wydanie `result_payload_digest` dla prawdziwego wyniku Core 10.

**Czego nie blokuje:** samej koperty, skrótu dla ładunków typowanych, wektorów C-T17,
C-T20 i C-T21, ani niczego w `XR_RESULT_IDENTITY_V2` — tożsamość wyniku nie zawiera
wartości liczbowych.

---

### B-10 — otwarty słownik `semantic_extensions` w zakresie, okresie i referencji

**Dokument i miejsce:** ZOP-XR-FOUNDATION-BIND-01 v1.1 §10 (`scope_definition` obejmuje
„source-defined extensions"), §11 (`semantic_extensions` — „Wyłącznie jawne source-defined
fields"), §12 (`reference_semantic_extensions`) oraz §7.1, gdzie wszystkie trzy wchodzą do
`scope_id` i `reference_id`. Miejsce styku z kodem: `src/xray/canonical/scope.py`
(pole `contract_scope_extensions` — tak nazywa je v1.0 §4, odziedziczony wpisem B-09),
`period.py` i `reference.py` (pola `semantic_extensions`).

**Na czym polega niejednoznaczność:** kontrakt wymaga, żeby rozszerzenia weszły do
tożsamości, ale **nie zamyka ich struktury**: nie ma wersji schematu, nie ma rejestru
dozwolonych kluczy, nie ma reguły odmowy dla klucza nieznanego. Dowolny klucz dopisany
przez wołającego po cichu zmienia `scope_id`, a przez niego `result_identity`.

Ten sam kontrakt zna lekarstwo i stosuje je **tylko w warstwie przebiegu**. v1.2 §11.1:
„`SEMANTIC_EXTENSIONS_SCHEMA_VERSION = XR_RUN_SEMANTIC_EXTENSIONS_V1`;
`ALLOWED_IDENTITY_AFFECTING_EXTENSION_KEYS_V1 = {}`; SemanticExtensionsV1 ma dokładnie dwa
klucze: `schema_version` oraz `values`… Nieznany klucz powoduje
`RUN_IDENTITY_EXTENSION_UNKNOWN`; semantic_run_id nie jest wydawany". Jest nawet wektor
negatywny T60. Dla zakresu, okresu i referencji odpowiednika nie ma — sprawdzone
2026-09-23 w v1.1 i v1.2: wystąpienia `SemanticExtensionsV1`, `schema_version` i rejestru
dozwolonych kluczy dotyczą wyłącznie `XR_SEMANTIC_RUN_PROFILE_01` i deskryptora odrzuceń.

**Dlaczego to jest materialne, a nie pedanteria:** karta V12-R1 §7 zamyka payload wyniku —
`XR_RESULT_IDENTITY_V2_OPEN_SEMANTIC_EXTENSIONS_ALLOWED = false`, „dokładnie siedem
składników i żadnych innych". Ale jednym z tych siedmiu jest `scope_id`, a wewnątrz niego
słownik otwarty. Zamknięcie zewnętrznego payloadu można więc obejść o jedno piętro niżej,
bez naruszenia litery kontraktu. To jest ta sama choroba co U-3 („CONTRACT COMPLETENESS /
OPEN IDENTITY PAYLOAD"), tyle że w warstwie, której v1.2 nie domknął.

**Warianty interpretacji:**

- A — rozciągnąć wzorzec z §11.1 na wszystkie trzy warstwy: `schema_version` + `values`,
  rejestr dozwolonych kluczy pusty w v1.2, nieznany klucz blokuje wydanie identyfikatora.
- B — zamknąć osobnym rejestrem per warstwa (inny zestaw kluczy dla zakresu, inny dla
  okresu, inny dla referencji), wersjonowanym niezależnie od profilu przebiegu.
- C — zostawić otwarte i uznać, że treść rozszerzeń jest odpowiedzialnością zamrożonej
  karty testu, która je wprowadza (stan dzisiejszy).
- D — wyłączyć rozszerzenia z tożsamości do czasu rozstrzygnięcia.

**Konsekwencja każdego wariantu dla kodu:**

- A — jednolita reguła i gotowy wzorzec do skopiowania; wymaga decyzji Controllingu, bo
  rozciąga wiązanie v1.2 na warstwy, których ono nie obejmuje.
- B — najbliżej intencji („wyłącznie jawne source-defined fields"), ale trzy rejestry do
  utrzymania i trzy wersje do pilnowania.
- C — zero pracy; `scope_id` pozostaje podatny na cichą zmianę przez klucz, którego nikt
  nie zatwierdził, a odmowy wydania identyfikatora nie ma.
- D — łamie v1.1 §10 i §12, gdzie rozszerzenia są wymienione wśród składników tożsamości.
  Odrzucone jako sprzeczne z kontraktem, wymienione dla kompletności.

**Propozycja robocza (do zatwierdzenia przez Michała):** wariant C jako **stan faktyczny**
na czas rundy V12-R1, bez zmiany kodu, oraz przedstawienie wariantu A Controllingowi jako
najbliższego istniejącemu wzorcowi §11.1. Ryzyko jest dziś niematerializowane: żaden moduł
nie produkuje jeszcze rozszerzeń, a wszystkie wektory P2–P4 budują porównywane obiekty tym
samym kodem. Materializuje się w chwili, gdy pierwsza karta testu wprowadzi własne pole
zakresowe.

**Co blokuje:** gwarancję, że `scope_id` i `reference_id` dwóch niezależnych implementacji
są równe dla tego samego zakresu semantycznego, gdy w grę wchodzą rozszerzenia; brak bramki
odpowiadającej `RUN_IDENTITY_EXTENSION_UNKNOWN` dla warstwy wyniku.

**Czego nie blokuje:** pakietów P1–P4 ani żadnego z wektorów C-T01–C-T09; obiektów bez
rozszerzeń, czyli wszystkich, które dziś potrafimy wyprodukować.

---

### B-08 — kanoniczna postać znacznika czasu w profilu tożsamości

**Dokument i miejsce:** ZOP-XR-FOUNDATION-BIND-01 v1.1 §7 (CANONICAL IDENTITY FRAMEWORK),
wiersz `Datetime`: „`{"$type":"datetime","value":"<RFC3339 canonical instant/local form wg
period/time contract>"}`". Profil przeniesiony bez zmiany przez v1.2 §17. Miejsce styku
z kodem: `src/xray/canonical/identity_json.py`, funkcja `_rfc3339`.

**Na czym polega niejednoznaczność:** kontrakt odsyła do „period/time contract", a takiego
kontraktu jeszcze nie ma. Nie wiadomo więc:

1. czy ten sam instant zapisany jako `2026-09-01T12:00:00+00:00` i `2026-09-01T12:00:00Z`
   ma dać te same bajty kanoniczne — RFC 3339 dopuszcza obie formy,
2. czy część ułamkowa sekundy jest normalizowana (`12:00:00` wobec `12:00:00.000000`),
3. czy „local form" jest w ogóle legalna w tożsamości, a jeżeli tak, to z jakim
   przesunięciem dla znacznika naiwnego.

Dla nas te pytania nie są teoretyczne: profil jest kontraktem **między implementacjami**.
Dwie implementacje, które rozstrzygną je inaczej, policzą różne `result_identity` z tych
samych danych — a właśnie temu profil ma zapobiegać.

**Warianty interpretacji:**

- A — przyjąć `isoformat()` wartości wejściowej; forma wynika z tego, co podał wołający.
- B — znormalizować do UTC i zapisywać zawsze z sufiksem `Z`.
- C — znormalizować do UTC z przesunięciem `+00:00`, bez `Z`.
- D — wymagać przesunięcia w postaci `±HH:MM` i zakazać `Z` na wejściu.

**Konsekwencja każdego wariantu dla kodu:**

- A — deterministyczne dla naszego kodu, ale nie dla kontraktu: dwie implementacje mogą
  dać różne bajty dla tego samego instantu. Zero pracy dziś, ryzyko przy pierwszej
  weryfikacji zewnętrznej.
- B — jedna postać dla instantu, ale traci lokalne przesunięcie; jeżeli „local form"
  z v1.1 §7 ma znaczenie semantyczne, wariant je niszczy.
- C — jak B, innym zapisem; wybór między `Z` a `+00:00` byłby wtedy naszą decyzją, nie
  kontraktową.
- D — zachowuje przesunięcie i daje jedną postać dla każdej wartości, ale odrzuca zapis
  `Z`, którego RFC 3339 nie zabrania.

**Propozycja robocza (do zatwierdzenia przez Michała):** wariant A jako **założenie
tymczasowe** na czas rundy V12-R1, oznaczone w kodzie `# ASSUMPTION: B-08`. Znacznik bez
strefy jest odrzucany — wybór formy lokalnej byłby wymyśleniem reguły, której kontrakt nie
ustala. Rozstrzygnięcia trzeba szukać razem z kontraktem okresu (`XR_PERIOD_CANONICAL_V1`,
pakiet P2), bo to ten sam obszar.

**Co blokuje:** wpuszczenie znacznika czasu do jakiejkolwiek tożsamości wydawanej na
zewnątrz jako wartość porównywalna między implementacjami; weryfikację bajtową profilu
przez stronę trzecią dla ładunków zawierających `datetime`.

**Czego nie blokuje:** reszty profilu (daty typowane, liczby, zbiory, sekwencje, klucze),
pakietu P1 ani tożsamości, które znaczników czasu nie zawierają — a zgodnie z v1.2 §7.2
`XR_RESULT_IDENTITY_V2` ich nie zawiera.

---

### B-07 — jesienna zmiana czasu: dwa instanty, jedna lokalna godzina

**Dokument i miejsce:** DT-05, wariant A zatwierdzony 2026-09-14 (konwersja znaczników ze
strefą na czas lokalny organizacji wg `organization_timezone` z profilu), wobec zasady 5
z CLAUDE.md oraz uzasadnienia samego wariantu A: nie wolno tracić informacji kompletnej.
Konsumenci skutku: przyszłe miary czasu etapów w ZOP-XR-PROC-01 i ZOP-XR-PROC-02.

**Na czym polega niejednoznaczność:** w `Europe/Warsaw` ostatniej niedzieli października
godzina 02:00–02:59 czasu lokalnego występuje dwa razy:

| Instant źródłowy | Czas lokalny |
| --- | --- |
| `2026-10-25T00:30Z` | 02:30 czasu letniego (UTC+02:00) |
| `2026-10-25T01:30Z` | 02:30 czasu zimowego (UTC+01:00) |

Po konwersji na naiwny czas lokalny oba dają `2026-10-25 02:30` — dwa różne instanty,
jedna wartość. Python rozróżnia je atrybutem `fold`, ale kolumna `datetime64[ns]`, której
typ wyznacza DT-08, go gubi (sprawdzone 2026-09-14: po odczycie z ramki oba mają `fold=0`).
Wiosną problemu nie ma: luka 02:00–02:59 nie istnieje lokalnie, a konwersja **do** czasu
lokalnego nigdy jej nie wyprodukuje.

Poza zakresem wpisu: znacznik, który przychodzi od klienta **już naiwny** i leży w tej
godzinie, jest niejednoznaczny u źródła. Tej informacji nie tracimy, bo nigdy jej nie było.

**Warianty interpretacji:**

- A — scalić w ramce bez śladu.
- B — odrzucić wiersz z własną kategorią odrzucenia.
- C — zachować `fold` w danych.
- D — scalić w ramce; pierwotną wartość źródłową i przesunięcie UTC czasu lokalnego zapisać
  w raporcie importu, obok kontraktu.
- E — nie konwertować wartości niejednoznacznych i pozwolić modelowi je odrzucić.

**Konsekwencja każdego wariantu dla kodu:**

- A — najprostsze; utrata nieodwracalna. Czasy etapów przechodzących przez tę godzinę mogą
  wyjść ujemne albo zawyżone o godzinę, a żadna z ośmiu kontroli tego nie zobaczy.
- B — nowa kategoria wchodzi do semantycznego zestawienia odrzuceń, a więc do `run_id`;
  ginie cały rekord (`case_id`, `stage`, drugi znacznik), czyli więcej informacji niż sama
  niejednoznaczna godzina.
- C — niewykonalne bez zmiany typu kolumny z DT-08 (kolumna obiektowa zamiast
  `datetime64[ns]`), a to zmienia sposób sprawdzania braku we wszystkich warstwach wyżej.
- D — kontrakt danych bez zmian; instant jest odtwarzalny z raportu (`row_id`, pole,
  przesunięcie). Konsument liczący czasy musi czytać raport importu, bo sama ramka tego nie
  powie.
- E — w praktyce B z kategorią „znacznik ze strefą", która myli przyczynę.

**Propozycja robocza (do zatwierdzenia przez Michała):** wariant D. Przyjęty 2026-09-14
jako **założenie tymczasowe**, nie decyzja. W kodzie konwersji oznaczony
`# ASSUMPTION: B-07`. Raport importu zawsze niesie licznik godzin niejednoznacznych, także
gdy wynosi 0 — brak pola znaczyłby jednocześnie „nie było" i „nie sprawdzaliśmy".

**Co blokuje:** nazwanie konwersji bezstratną; każdą przyszłą miarę czasu trwania, która
czyta wyłącznie ramkę (PROC-01, PROC-02) — do rozstrzygnięcia taka miara musi uwzględnić
raport importu albo jawnie ogłosić ograniczenie.

**Czego nie blokuje:** importu, konwersji pozostałych znaczników, kontroli 8, tożsamości
przebiegu ani odcisku wykonania.

---

## Sekcja C — rozstrzygnięte

Osiem wpisów. Siedem rozstrzygnął Michał: A-01 i B-01…B-05 dnia 2026-09-05,
B-06 dnia 2026-09-08. Ósmy, B-09, rozstrzygnął Controlling dnia 2026-09-23 w ramach
rundy V12-R1 — jest to jedyny wpis zamknięty poza ścieżką metodologiczną Michała.

Warianty robocze zatwierdzone przy A-01 i B-01…B-05 (A-01 i B-04 z zaostrzeniem).
**Przy B-06 wariant roboczy został odrzucony jako zbyt gruby** i zastąpiony mocniejszym
rozdzieleniem trzech stanów.

---

### A-01 — Etykieta okresu dla tabeli PROCESS

**Kontrakt macierzysty:** ZOP-MASTER-01 v1.2, rozdz. 17, wiersz
„kalendarze operacyjne / time_basis — różne procesy mają różne podstawy czasu —
wraca przy implementacji PROC/CAP". To **nie jest** nowy kontrakt.

**Miejsce styku z fundamentem:** ZOP-TECH-01 v0.1 pkt 5.3, kontrola 8 (zakres czasowy),
zastosowana do tabeli PROCESS.

**Na czym polega styk:** cztery pozostałe tabele bazowe niosą agregaty miesięczne
i mają `date` jako etykietę okresu. PROCESS niesie zdarzenia i ma czas rzeczywisty
w `start` / `end`. Etykieta okresu jest z nich wyliczalna, ale wynik zależy od
przyjętej podstawy: start sprawy, start etapu, koniec etapu albo zamknięcie sprawy.
Przypadek rozpoczęty w marcu i zamknięty w maju należy do innego miesiąca w każdym
z tych wariantów. Wybór podstawy jest regułą biznesową, nie decyzją techniczną,
a fundament nie zna jeszcze kart PROC-01 i PROC-02.

**Decyzja robocza z 2026-09-04 (Aleksander) — CZĘŚCIOWO UCHYLONA 2026-09-05.**
Punkty 1, 2 i 4 obowiązują. Punkt 3 (`time_basis_used = stage_start`) został
wycofany przez rozstrzygnięcie Michała poniżej. Treść zostaje, bo odrzucony wariant
jest częścią śladu.

1. Nie dodajemy pola `date` do PROCESS. Byłoby redundantne wobec `start` / `end`
   i zamrażałoby regułę biznesową, której TECH-01 nie rozstrzyga.
2. Kontrola zakresu czasowego dla PROCESS zwraca:
   `period_min` = min(`start`), `period_max` = max(`end`), `months_covered`,
   `months_without_events`, `time_basis_used`.
3. `time_basis_used` jest wartością jawną, nie domyślną. Na tym etapie `stage_start`,
   oznaczona w kodzie komentarzem `# ASSUMPTION:`.
4. `months_without_events` raportujemy jako **obserwację**, nie jako WARNING ani
   CRITICAL. W pozostałych tabelach brakujący miesiąc to luka w danych; w PROCESS
   może być miesiącem, w którym faktycznie nic nie przyszło, i bez referencji nie da
   się tych dwóch sytuacji rozróżnić. Zgodne z zasadą 5 z CLAUDE.md: brak informacji
   jest pełnoprawnym wynikiem, nie brakiem do wypełnienia.

**Co blokuje:** nic w zakresie ZOP-TECH-01.

**Czego nie blokuje:** importu, walidacji, kontraktu danych, struktury FINDINGS ani
generatora syntetycznego. Kontrola 8 jest wykonalna dla wszystkich pięciu tabel.

**Kiedy wraca:** przy implementacji PROC-01 / PROC-02 i CAP-01 / CAP-02, razem
z kontraktem macierzystym `time_basis`. Wtedy `time_basis_used` przestaje być
założeniem, a staje się wartością pochodzącą z karty.

**ROZSTRZYGNIĘCIE**

| | |
| --- | --- |
| Data | 2026-09-05 |
| Decydent | Michał (metodologia) |

**Treść decyzji:**

Nie rozstrzygamy teraz `time_basis`. Przechowujemy znaczniki czasu i **nie
przypisujemy procesu arbitralnie do miesiąca**. Podstawa przypisania będzie osobnym
kontraktem globalnym.

Robocze założenie `time_basis_used = stage_start` zostaje **wycofane** — nie zostaje jako
domyślna wartość ani jako założenie robocze. `DEFAULT_TIME_BASIS` znika z kodu. Kontrola 8
nie ma prawa wybrać sobie podstawy przypisania.

Co kontrola 8 dla PROCESS **może** zwracać:
- `period_min` = min(`start`), `period_max` = max(`end`) oraz rozpiętość między nimi —
  to jest **zakres danych**, a nie przypisanie,
- liczbę zdarzeń w miesiącu liczoną po **własnym znaczniku czasu zdarzenia**, bo
  zdarzenie ma jeden moment i nie wymaga wyboru podstawy,
- `months_without_events` — miesiące bez zdarzeń, nadal jako **obserwacja**, nie WARNING
  ani CRITICAL.

Czego kontrola 8 **nie może** robić: przypisywać sprawy (`case_id`) do miesiąca. Sprawa
rozpoczęta w marcu i zamknięta w maju nie należy do żadnego z nich, dopóki kontrakt
globalny nie powie, jak to liczyć.

`time_basis_used` zwraca `null` z jawną podstawą „kontrakt globalny nierozstrzygnięty" —
nigdy wybraną wartość.

---

### B-01 — brak oznaczenia korekty w tabeli COST

**Dokument i miejsce:** ZOP-TECH-01 v0.1 pkt 5.3, kontrola 5, wobec pkt 5.2 (COST).

**Na czym polega niejednoznaczność:** kontrola 5 brzmi „wartości podejrzane, np. ujemny
przychód lub koszt, **jeżeli nie został oznaczony jako korekta**". Minimalny zestaw pól
COST (`date`, `unit`, `category`, `amount`) nie zawiera żadnego pola pozwalającego na
takie oznaczenie. `exclusion_flags` z FIN-01 pkt 9 nie zamyka luki, bo działa na poziomie
okresu i zakresu analizy, a nie pojedynczego rekordu.

**Warianty interpretacji:**
- A — oznaczanie korekt jest poza zakresem TECH-01; walidator wyłącznie raportuje
  wartości ujemne, a rozstrzygnięcie należy do testu albo do ręcznej weryfikacji.
- B — COST otrzymuje opcjonalne pole korekty (np. `correction_flag`), wypełniane, gdy
  klient takie oznaczenie dostarczy.
- C — korekta jest rozpoznawana po `category` z profilu mapowania klienta, bez nowego
  pola w kontrakcie.

**Konsekwencja każdego wariantu dla kodu:**
- A — kontrakt COST bez zmian; kontrola 5 zwraca sygnał z podstawą i nigdy nie ustawia
  CRITICAL samodzielnie. Ujemna kwota pozostaje wartością dopuszczalną w modelu.
- B — zmiana bazowej struktury z pkt 5.2, czyli dotknięcie kontraktu, który wszystkie
  karty Core 10 deklarują jako niezmienny („rozszerzenia nie zmieniają bazowej struktury
  ZOP-TECH-01"). Wymaga decyzji na poziomie karty, nie implementacji.
- C — brak zmiany kontraktu, ale reguła rozpoznania korekty przenosi się do profilu
  mapowania klienta i przestaje być audytowalna w jednym miejscu.

**Propozycja robocza (do zatwierdzenia przez Michała):** wariant A. Do czasu decyzji
walidator raportuje wartości ujemne jako sygnał z jawną podstawą, bez klasyfikowania ich
jako błędu, a model COST dopuszcza `amount` ujemne bez ograniczenia.

**Co blokuje:** nic. **Czego nie blokuje:** kontraktu COST, importu, kontroli 5.

**ROZSTRZYGNIĘCIE**

| | |
| --- | --- |
| Data | 2026-09-05 |
| Decydent | Michał (metodologia) |

**Treść decyzji:**

Wariant A zatwierdzony. Ujemny koszt pozostaje **sygnałem walidacyjnym**
z jawną podstawą. Bez jawnego oznaczenia w danych nie klasyfikujemy go ani jako błędu,
ani jako korekty. Kontrakt COST nie zyskuje pola korekty.

---

### B-02 — słownik pola `status` w FINDINGS

**Dokument i miejsce:** ZOP-TECH-01 v0.1 pkt 5.4 wobec ZOP-PRI-01 v1.0 rozdz. 8
oraz statusów logicznych kart Core 10.

**Na czym polega niejednoznaczność:** TECH-01 pkt 5.4 podaje dla `status` słownik
STANDARD / MEDIUM / HIGH / CRITICAL. FIN-01 pkt 12.1, PROC-01 pkt 12.1, PORT-01 pkt 13.1
i HR-01 rozdz. 13 potwierdzają ten słownik, ale przypisują jego nadawanie do ZOP-PRI-01.
PRI-01 v1.0 tego słownika nie zawiera w ogóle — jego zamknięte katalogi (rozdz. 8) to
`problem_priority_action` (review_now; review_next; plan_review; observe; not_assessable),
`validation_priority_action` oraz `management_attention_route`. Jednocześnie karty
opisują `status` w FINDINGS jako **status logiczny testu**, wyraźnie odróżniony od
priorytetyzacji (FIN-01 pkt 12.2: „to statusy diagnostyczne, nie wynik globalnej
priorytetyzacji"; CAP-02 rozdz. 21: „CRITICAL pozostaje wyłącznie wynikiem walidacji
danych").

**Druga niejednoznaczność — sam katalog statusów logicznych nie jest jednolity:**
- PROC-02 pkt 16.1 („zachowuje wspólny katalog"), PORT-01 13.1, PROC-01 12.1,
  FIN-03 rozdz. 14, CAP-02 rozdz. 21, MGT-01 rozdz. 16: NO_ADVERSE_SIGNAL;
  ADVERSE_SIGNAL; INCIDENT; DETERIORATING; STABLE; IMPROVING; TEST_PARTIAL; TEST_BLOCKED.
- FIN-01 pkt 12.2 i CAP-01 rozdz. 7: zamiast `ADVERSE_SIGNAL` występuje
  `SHORT_TERM_DEVIATION`.
- CAP-01 dodatkowo zawiera wiersz `VOLATILE / SEASONAL`, z którego nie wynika, czy to
  jedna wartość, czy dwie. Sąsiedni wiersz `TEST_PARTIAL / TEST_BLOCKED` sugeruje dwie,
  ale to przesłanka z formatowania tabeli, nie z treści karty.

**Warianty interpretacji:**
- A — `status` niesie status logiczny; STANDARD/MEDIUM/HIGH/CRITICAL to słownik
  porzucony, wycofany całkowicie; priorytet mieszka wyłącznie w polach PRI-01.
- B — jak A, ale STANDARD/MEDIUM/HIGH/CRITICAL zostaje jako osobne, odrębne pole
  FINDINGS zasilane przez PRI-01.
- C — `status` pozostaje polem priorytetu wg TECH-01, a status logiczny dostaje własne
  pole.

**Konsekwencja każdego wariantu dla kodu:**
- A — jeden enum statusu logicznego; brak pola priorytetowego poza katalogami PRI-01.
- B — jeden enum statusu logicznego plus drugi enum, którego żadna karta dziś nie
  definiuje; PRI-01 musiałby zostać rozszerzony, a jest ZAMROŻONY.
- C — sprzeczne z jednoznacznym opisem `status` jako statusu logicznego we wszystkich
  dziewięciu kartach, które to pole opisują.

**Propozycja robocza (do zatwierdzenia przez Michała):** wariant A. `status` w FINDINGS
niesie status logiczny testu. Enum obejmuje dziewięć wartości: osiem ze wspólnego
katalogu plus `SHORT_TERM_DEVIATION` z FIN-01 i CAP-01. `VOLATILE` / `SEASONAL`
świadomie **nie** wchodzą do enumu do czasu implementacji CAP-01 — nie zgadujemy, czy
to jedna wartość, czy dwie. W kodzie oznaczone `# ASSUMPTION:`.

**Co blokuje:** nic na etapie fundamentu; NOOP-01 używa wyłącznie `NO_ADVERSE_SIGNAL`,
które występuje w każdej karcie bez wyjątku. **Czego nie blokuje:** kontraktu FINDINGS,
zapisu, śladu audytowego.

**ROZSTRZYGNIĘCIE**

| | |
| --- | --- |
| Data | 2026-09-05 |
| Decydent | Michał (metodologia) |

**Treść decyzji:**

Wariant A zatwierdzony. Słownik STANDARD / MEDIUM / HIGH / CRITICAL jest
**historycznym zapisem ZOP-TECH-01 v0.1** i zostaje **wycofany**. Nie implementujemy go
jako priorytetu — ani teraz, ani później, ani jako osobnego pola.

`status` w FINDINGS niesie status logiczny testu. Priorytet mieszka wyłącznie
w kontraktach ZOP-PRI-01.

`VOLATILE` / `SEASONAL` z ZOP-XR-CAP-01 pozostają poza enumem do czasu implementacji
CAP-01 — nie zgadujemy, czy to jedna wartość, czy dwie.

---

### B-03 — `confidence_class` w FINDINGS: katalog i liczba poziomów

**Dokument i miejsce:** ZOP-TECH-01 v0.1 pkt 5.4 wobec ZOP-CONF-01 v1.0 pkt 2.1 i 2.2.

**Na czym polega niejednoznaczność:** TECH-01 pkt 5.4 opisuje `confidence_class` jako
„klasa pewności A / B / C". CONF-01 pkt 2.2 („Wspólny katalog klas") nie zna wartości
A/B/C — katalog to `well_supported`, `supported_with_limitations`, `partially_supported`,
`weakly_supported`, `not_assessable`. To ten sam rodzaj nieaktualnego zapisu w TECH-01
v0.1 co `confidence_score` 0–1, przy którym CONF-01 pkt 2.2 stwierdza dosłownie:
„ZAKAZ WSKAŹNIKA confidence_score = null".

**Druga część problemu:** CONF-01 pkt 2.1 rozdziela pewność na trzy niezależne poziomy —
`metric_confidence_class`, `finding_confidence_class`, `mechanism_confidence_class` —
i zakazuje przenoszenia klasy między poziomami („Klasa nie jest kopiowana automatycznie
między poziomami", QCONF01-183). Pojedyncze pole `confidence_class` w FINDINGS nie ma
odpowiednika w CONF-01 i nie da się jednoznacznie powiedzieć, który poziom niesie.

**Warianty interpretacji:**
- A — FINDINGS ma trzy pola klas zgodnie z CONF-01, a `confidence_class` z TECH-01
  znika jako zapis nieaktualny.
- B — FINDINGS zachowuje jedno pole `confidence_class` z jawnym
  `confidence_class_source_level` wskazującym poziom (CONF-01 pkt 3 zna to pole).
- C — FINDINGS zachowuje jedno pole i przyjmuje, że niesie `finding_confidence_class`.

**Konsekwencja każdego wariantu dla kodu:**
- A — trzy pola nullowalne; najbliżej karty, najdalej od TECH-01 pkt 5.4.
- B — jedno pole plus pole poziomu; zgodne z CONF-01 i nie łamie TECH-01.
- C — jedno pole; proste, ale zapisuje w kontrakcie założenie, którego karta nie robi,
  i traci pewność miary oraz mechanizmu.

**Propozycja robocza (do zatwierdzenia przez Michała):** wariant B. Na etapie fundamentu
i tak wszystkie te pola są `null` — CONF-01 nie jest implementowane. Enum klas budujemy
wg CONF-01 pkt 2.2, nie wg A/B/C.

**Co blokuje:** nic. **Czego nie blokuje:** kontraktu FINDINGS ani NOOP-01, który zapisuje
klasy jako `null`.

**Uwaga proceduralna:** B-03 dotyczy tej samej nieaktualności TECH-01 v0.1 co
`confidence_score`, którą Aleksander zgłasza już Michałowi jako poprawkę do TECH-01 v0.2.
Warto zgłosić oba zapisy razem.

**ROZSTRZYGNIĘCIE**

| | |
| --- | --- |
| Data | 2026-09-05 |
| Decydent | Michał (metodologia) |

**Treść decyzji:**

Wariant B zatwierdzony. Klas A / B / C **nie implementujemy** — to nieaktualny
zapis ZOP-TECH-01 v0.1. Obowiązuje katalog z ZOP-CONF-01 pkt 2.2.

Rozdzielenie pewności na miarę, wynik i mechanizm zostaje zgodnie z CONF-01 pkt 2.1:
klasy per poziom mieszkają w `ClaimRecord`, a `FindingRecord` niesie klasę przeniesioną
wraz z `confidence_class_source_level`. `confidence_score` pozostaje `null` na mocy
dosłownego zakazu z CONF-01 pkt 2.2.

---

### B-04 — znaczenie pola `metric` w tabeli PLAN

**Dokument i miejsce:** ZOP-TECH-01 v0.1 pkt 5.2 (PLAN) wobec ZOP-XR-FIN-01 v1.0
rozdz. 8, wiersz „plan / budżet".

**Na czym polega niejednoznaczność:** PLAN jest we wszystkich kartach opisana jako
możliwa referencja. FIN-01 rozdz. 8 dopuszcza plan jako źródło wartości odniesienia
pod warunkiem „zgodna definicja miary", ale żadna karta nie mówi, **skąd system ma
wiedzieć**, która wartość `metric` odpowiada mierze liczonej przez test. Bez tego
warunek „zgodna definicja miary" jest niesprawdzalny automatycznie: test nie ma jak
odnaleźć właściwego `target`.

**Warianty interpretacji:**
- A — `metric` to swobodny tekst klienta; dopasowanie do miary testu następuje przez
  profil mapowania klienta, tak samo jak dopasowanie kolumn.
- B — `metric` to słownik kontrolowany po stronie X-Ray; wartości spoza słownika są
  raportowane jako niedopasowane i nie mogą służyć jako referencja.
- C — plan w ogóle nie jest automatyczną referencją; użycie planu jako `reference_value`
  wymaga jawnego wskazania przez człowieka.

**Konsekwencja każdego wariantu dla kodu:**
- A — kontrakt PLAN bez zmian; `mapping/` zyskuje drugą odpowiedzialność obok mapowania
  kolumn: mapowanie wartości `metric` na miary testów. Ryzyko: dopasowanie staje się
  konfiguracją klienta, a nie regułą audytowalną w jednym miejscu.
- B — potrzebny zamknięty słownik miar, którego dziś nie ma żadna karta; zbudowanie go
  „z rozsądku" naruszałoby zasadę 1.
- C — plan pozostaje w danych, ale nie zasila automatycznie `reference_value`;
  najbezpieczniejsze metodologicznie, najuboższe funkcjonalnie.

**Propozycja robocza (do zatwierdzenia przez Michała):** fundament nie rozstrzyga.
Model przyjmuje `metric` jako tekst z danych klienta, niczego nie tłumaczy i nie
dopasowuje. Rozstrzygnięcie wraca przy pierwszym teście, który sięgnie po plan jako
referencję — czyli przy FIN-01 rozdz. 8.

**Co blokuje:** nic na etapie fundamentu. **Czego nie blokuje:** kontraktu PLAN,
importu, walidacji, kontroli zakresu czasowego.

**ROZSTRZYGNIĘCIE**

| | |
| --- | --- |
| Data | 2026-09-05 |
| Decydent | Michał (metodologia) |

**Treść decyzji:**

Wariant A zatwierdzony **z zaostrzeniem**: żadnego automatycznego dopasowania
PLAN do miary testu. Fundament ma **wymagać jawnego mapowania** i zgodności definicji.

Konsekwencja dla `mapping/`: kontrakt profilu mapowania zyskuje **czwarty element** obok
trzech list kolumn — deklarację mapowania miar planu. Deklaracja wskazuje, która wartość
`metric` odpowiada której mierze testu, wraz z podstawą zgodności definicji.

Brak takiej deklaracji **nie jest błędem importu**. Oznacza natomiast, że PLAN nie może
posłużyć jako `reference_type = plan_budget` (ZOP-XR-FIN-01 rozdz. 6, warunek „zgodna
definicja miary").

Model nadal nie normalizuje `metric` — wartość przechodzi taka, jaka przyszła. Zmienia
się to, że sam przepływ danych nie wystarcza: potrzebna jest jawna deklaracja obok.

---

### B-05 — powiązanie dowodu z twierdzeniem w CONF-01

**Dokument i miejsce:** ZOP-CONF-01 v1.0 rozdz. 3 (kontrakt twierdzenia) i rozdz. 4
(kontrakt dowodu).

**Na czym polega niejednoznaczność:** karta definiuje `claim_id` jako trwały
identyfikator twierdzenia oraz `evidence_id`, `evidence_group_id`
i `evidence_source_group_id` w kontrakcie dowodu, ale **nigdzie nie nazywa pola
wiążącego dowód z twierdzeniem**. W kontrakcie dowodu nie ma `claim_id`, a w kontrakcie
twierdzenia nie ma listy dowodów. Przeszukanie całej karty pod kątem `claim_evidence`,
`required_evidence` i `evidence_set` nie daje wyniku.

To **nie jest pytanie o nazwę pola, tylko o kardynalność**:

- jeżeli dowód należy do twierdzenia — relacja jest jeden-do-wielu,
- jeżeli ten sam dowód może wspierać kilka twierdzeń — relacja jest wiele-do-wielu.

Istnienie `evidence_group_id` („grupa rekordów opisujących ten sam dowód lub zdarzenie")
oraz `evidence_source_group_id` („grupa wspólnego źródła używana do ochrony
niezależności") przemawia za drugim odczytaniem: oba pola istnieją po to, żeby rozpoznać
wspólne pochodzenie dowodów używanych w różnych miejscach. Gdyby dowód należał na
własność do jednego twierdzenia, ochrona niezależności nie miałaby czego pilnować.

**Warianty interpretacji:**
- A — dowód należy do twierdzenia; `EvidenceRecord` nosi `claim_id`.
- B — dowód jest bytem niezależnym, a powiązanie z twierdzeniem jest jawnym rekordem
  wiążącym; ten sam dowód może być powiązany z wieloma twierdzeniami.
- C — dowód należy do wyniku (`finding_id`), a twierdzenia dziedziczą dowody wyniku.
  Sprzeczne z CONF-01 rozdz. 2.1, która zakazuje automatycznego dziedziczenia między
  poziomami twierdzeń.

**Konsekwencja każdego wariantu dla kodu:**
- A — najprostsze; ale ten sam dowód użyty przy dwóch twierdzeniach trzeba zduplikować,
  przez co `evidence_source_group_id` przestaje odróżniać duplikat od dwóch niezależnych
  źródeł — czyli traci swoją jedyną funkcję.
- B — jeden rekord wiążący więcej; ochrona niezależności działa, bo duplikacji nie ma.
- C — wymaga złamania zakazu dziedziczenia klas między poziomami.

**Propozycja robocza (do zatwierdzenia przez Michała):** wariant B, przez jawne
powiązanie, a nie przez własność.

Uzasadnienie jest **asymetryczne i to jest w nim najważniejsze**: wiele-do-wielu
degraduje się do jeden-do-wielu bez żadnej zmiany kodu — relacja po prostu nigdy nie ma
więcej niż jednego wiązania dla dowodu. Odwrotnie się nie da: jeden-do-wielu przerobione
później na wiele-do-wielu oznacza przepisanie zapisu i odczytu. Przy nierozstrzygniętej
karcie wybieramy wariant, który przetrwa oba rozstrzygnięcia.

**Co blokuje:** nic na etapie fundamentu — żaden kod nie wypełnia jeszcze dowodów.
**Czego nie blokuje:** kontraktu FINDINGS, NOOP-01, zapisu ani śladu.

**Kiedy wraca:** przy implementacji ZOP-CONF-01, czyli przy pierwszym teście
produkującym rekordy dowodowe.

**ROZSTRZYGNIĘCIE**

| | |
| --- | --- |
| Data | 2026-09-05 |
| Decydent | Michał (metodologia) |

**Treść decyzji:**

Wariant B zatwierdzony. Relacja wiele-do-wielu zostaje jako **architektura
bazowa**, przez jawne powiązanie `ClaimEvidenceLink`, a nie przez własność.

Dokładny kontrakt dowód–twierdzenie zostanie domknięty razem z implementacją
ZOP-CONF-01. Do tego czasu architektura jest ustalona i nie podlega ponownemu otwarciu.

---

### B-06 — co znaczy „kolumna wymagana" w kontroli 1

**Dokument i miejsce:** ZOP-TECH-01 v0.1 pkt 5.3, kontrola 1 („brak wymaganej kolumny")
wobec ZOP-XR-CAP-01 v1.0 pkt 4.1.

**Na czym polega niejednoznaczność:** TECH-01 pkt 5.3 wymienia brak wymaganej kolumny
jako kontrolę, a przykład („np. brak pola date, unit lub amount") sugeruje, że dotyczy to
każdego pola kontraktu. Tymczasem ZOP-XR-CAP-01 pkt 4.1 stwierdza wprost:
**„brak cost: miary fizyczne działają; economic_gap = null"** — czyli klient bez kolumny
`cost` ma być obsługiwalny, a nie odrzucony.

To **sprzeczność między kartą a kartą**, nie niespójność naszych zapisów.

**Kierunek rozstrzyga hierarchia z CLAUDE.md:** CAP-01 jest kartą zamrożoną i stoi wyżej
niż ZOP-TECH-01. Nie każde brakujące pole może więc dawać CRITICAL. Hierarchia **nie
rozstrzyga natomiast kryterium**: która kolumna jest wymagana, a która nie.

Dodatkowa okoliczność techniczna: w naszym kontrakcie żadne pole nie ma wartości
domyślnej, więc Pydantic wymaga **obecności** każdego z nich. Brak kolumny `cost` oznacza
dziś odrzucenie każdego wiersza RESOURCE — dokładnie to, czego CAP-01 zakazuje.

**Warianty interpretacji:**
- A — kryterium wynika z kontraktu: element `NATURAL_KEY` → CRITICAL, pole spoza klucza
  → WARNING i kolumna traktowana jak w całości pusta.
- B — wszystko CRITICAL, zgodnie z literą TECH-01.
- C — lista pól wymaganych deklarowana per tabela w konfiguracji albo w karcie.

**Konsekwencja każdego wariantu dla kodu:**
- A — kryterium jest maszynowo odczytywalne z `TableRecord.NATURAL_KEY`, więc nie ma
  drugiego źródła prawdy. Uzasadnienie jest wywodliwe: rekordu bez klucza nie da się
  przypisać do zakresu ani okresu, więc nie może uczestniczyć w audytowalnej agregacji;
  rekord bez `cost` może, tylko z węższym zakresem wniosków.
- B — klient bez jednej kolumny nieobowiązkowej nie przechodzi importu wcale. Sprzeczne
  z CAP-01 pkt 4.1.
- C — wprowadza drugie źródło prawdy obok kontraktu danych. Gdyby lista leżała w profilu
  klienta, klient mógłby ją skrócić i import przeszedłby bez pola wymaganego przez kartę:
  reguła metodologiczna wpełzłaby do danych wejściowych.

**Mechanizm dla wariantu A — materializacja pustej kolumny.** Brakująca kolumna spoza
klucza jest materializowana jako **w całości pusta**, a sama materializacja jest
odnotowana w raporcie mapowania. `None` oznacza tu **nieobecność kolumny**, a nie wartość
zastępczą wstawioną w miejsce danych — zasada 5 nie jest naruszona, ale to rozróżnienie
musi być widoczne w raporcie, a nie domyślane z liczby braków. Kontrola 3 pokaże wtedy
100% braków w tym polu, a `DiagnosticTestDeclaration.required_fields` pozwoli testowi
ogłosić `TEST_BLOCKED` albo `TEST_PARTIAL`.

**Propozycja robocza (do zatwierdzenia przez Michała):** wariant A. *(Michał poszedł dalej — patrz rozstrzygnięcie.)* Reguła jest wywodliwa
z kontraktu i zgodna z kartą zamrożoną, ale **definiuje zachowanie dla wszystkich
klientów**, więc wymaga potwierdzenia na poziomie metodologii, a nie implementacji.
W kodzie kontroli 1 oznaczone `# ASSUMPTION:`.

**Co blokuje:** nic. Hierarchia rozstrzyga kierunek, więc implementacja idzie dalej.

**Czego nie blokuje:** profilu mapowania, kontroli 1, importu ani magazynu.

**Kiedy wraca:** przy poprawce ZOP-TECH-01 do v0.2 — razem z zapisami o
`confidence_score` i `confidence_class`, które już czekają na tę samą korektę.

**ROZSTRZYGNIĘCIE**

| | |
| --- | --- |
| Data | 2026-09-08 |
| Decydent | Michał (metodologia) |

**Treść decyzji:**

Wariant A **odrzucony jako zbyt gruby**. Reguła „każde pole spoza klucza → WARNING" nadaje
ciężar, którego walidator nie zna. Zamiast dwóch stanów obowiązują **trzy**:

**1. `required_structurally`** — bez tego pola nie da się odpowiedzialnie zidentyfikować
rekordu ani zachować podstawowego kontraktu tabeli. Brak → **CRITICAL**. Przykład: element
klucza naturalnego.

**2. `required_by_test` / `required_by_claim`** — pole niewymagane strukturalnie, ale
potrzebne konkretnemu testowi albo twierdzeniu. Brak **nie blokuje przebiegu** i nie znaczy,
że tabela jest niepoprawna. Walidacja ma stan **ujawnić**, a test, który tego pola
potrzebuje, **nie może udawać wyniku** — zwraca `not_assessable` albo właściwy status braku
podstawy. Brak ogranicza ten test albo to twierdzenie, nie cały przebieg.

**3. Pole legalnie opcjonalne i niepotrzebne wykonywanemu testowi** — brak nie generuje ani
CRITICAL, ani automatycznego WARNING. Dopuszczalny stan danych.

Zdanie spinające całość:

> „Walidator danych ogłasza stan danych, ale nie przejmuje metodologicznej
> odpowiedzialności testu diagnostycznego. To konsument informacji wie, czy dane pole jest
> konieczne do wydania określonego twierdzenia."

**Skutki dla kodu:**

| Co | Zmiana |
| --- | --- |
| kontrola 1 | traci gałąź WARNING: brak elementu `NATURAL_KEY` → CRITICAL, brak dowolnego innego pola → **PASS z obserwacją** |
| rejestr testów | egzekwuje `required_by_test` wobec **rzeczywistych** raportów importu; dotąd deklaracja była sprawdzana tylko wobec kontraktu |

**Wykonanie (2026-09-08), z jednym odstępstwem od litery rozstrzygnięcia.** Egzekwowanie
nie stoi w rejestrze, tylko w metodzie szablonowej `DiagnosticTest.execute`, a
`engine.run_test()` jest cienką funkcją rejestru. Powód: rejestr da się obejść wywołaniem
`get_test(...)().run(...)` — i tak właśnie robiła nasza własna demonstracja, więc bramka
w rejestrze byłaby konwencją, a nie mechanizmem. Nadpisanie `execute` albo `readiness`
przez wtyczkę jest odrzucane przy tworzeniu klasy. Adres pozostaje ten, który wskazuje
rozstrzygnięcie; mechanizm siedzi piętro niżej. Szczegóły: wpis DT-20.

**Czego bramka nie zamyka.** Egzekwowania CRITICAL z `required_validations` — to osobny
mechanizm, którego rozstrzygnięcie B-06 nie dotyczy. Deklaracja istnieje, kontrole zwracają
statusy, ale nic nie łączy jednego z drugim; test wymagający pola, którego kolumna jest
obecna, wykona się także na tabeli rozbitej strukturalnie. Zamknięcie wymaga
rozstrzygnięcia metodologicznego (co CRITICAL wymaganej kontroli oznacza dla testu), więc
nie domykamy go technicznie z własnej inicjatywy.
| deklaracja testu | `required_fields` → `required_by_test`; nazwa niesie, **czyim** wymaganiem jest pole |

PASS przy braku pola spoza klucza **nie jest fałszywym przejściem**: fakt jest w wyniku jako
obserwacja z podstawą, tylko nie jako status. Sprowadza to kontrolę 1 do tego samego gatunku
co kontrola 3 — obraz, nie werdykt.

**ODCZYTANIE KRYTERIUM STRUKTURALNEGO (zapis jawny, do ewentualnego zaprotestowania).**

Michał pisze: „nie potrafimy odpowiedzialnie zidentyfikować rekordu **albo** zachować
podstawowego kontraktu tabeli". Pierwsza połowa to klucz naturalny; druga jest szersza
i wymaga przyłożenia do konkretu.

Przykładamy ją tak: **COST bez kolumny `amount` nie łamie podstawowego kontraktu tabeli.**
Wiersz nadal identyfikuje komórkę (miesiąc, jednostka, kategoria), której wartość jest
nieznana — a `null` jest poprawnym wynikiem (zasada 5). Test liczący z kwot zwróci
`not_assessable` i **to jest właściwe miejsce tej odmowy**.

Stąd: **strukturalnie wymagany = element klucza naturalnego i nic ponadto.**

To zastosowanie kryterium Michała, a nie luka w nim, więc nie zakładamy nowego kontraktu
otwartego. Zapis jest jawny po to, żeby Michał mógł zaprotestować, jeżeli miał na myśli
szerszy zbiór.

**ODROCZONE:** granulacja per twierdzenie (`required_by_claim`). **Termin wraca wcześniej,
niż zapisano pierwotnie: z CAP-01, nie z CONF-01** — i karta CAP-01 zawiera już dowód, że
będzie potrzebna. CAP01-T10: brak `cost` daje miary fizyczne i `economic_gap = null`,
„wg trendu; **nie TEST_BLOCKED**". Czyli `cost` jest wymagane twierdzeniom ekonomicznym,
a nie całemu testowi — gdyby CAP-01 wpisało je w `required_by_test`, bramka wyprodukowałaby
status, którego karta zakazuje. Do tego czasu obowiązuje reguła: w `required_by_test` trafia
wyłącznie pole, bez którego test nie wyda **żadnego** twierdzenia. Test może wydać część
twierdzeń i wstrzymać się od reszty — `TEST_PARTIAL` zamiast `TEST_BLOCKED`. Żaden test nie
produkuje dziś twierdzeń, więc deklaracja na poziomie testu wystarcza. Patrz wpis DT-18
w notatce technicznej; wraca z pierwszym testem produkującym twierdzenia.

---

### B-09 — kształt predykatu filtra i słownik operatorów w `scope_definition`

**Dokument i miejsce:** ZOP-XR-FOUNDATION-BIND-01 v1.1 §10 SCOPE CONTRACT
(`decision_id = FB11-D02 / Q-6A`) i §7.1 (`scope_id` = `SCOPE-` + SHA256(canonical(
scope_definition)), „filters/population/aggregation/constraints/extensions; label
excluded"). Miejsce styku z kodem: `src/xray/canonical/scope.py`, pole
`ScopeDefinition.filters`.

**Na czym polega niejednoznaczność:** v1.1 i v1.2 wymagają, żeby filtry weszły do
`scope_id`, ale **nie podają kształtu pojedynczego predykatu** ani słownika operatorów.
v1.1 §10 mówi tylko: „Semantycznie równoważne sety/predykaty po legalnej canonicalization
dają ten sam `scope_id`; aliasy, case-folding i business-equivalence nie są inferowane".
Sprawdzone 2026-09-22 w obu dokumentach obowiązujących: w v1.2 nie ma ani jednego
wystąpienia słów `operator`, `predicate`, `NOT_IN`; w v1.1 słowo „predykaty" pada raz,
w zdaniu zacytowanym wyżej, bez definicji struktury.

Trójka `field / operator / value` i zamknięta lista `EQ, NE, IN, NOT_IN, LT, LTE, GT, GTE,
RANGE` pochodzą z **BIND-01 v1.0 §4.1**, czyli z wersji archiwalnej. v1.2 §3 wymienia jako
`VERIFIED HISTORICAL BYTES` v1.1, a v1.2 §17 przenosi bez zmiany wyłącznie profil
kanoniczny — nie strukturę predykatu. Przepisanie słownika z v1.0 byłoby wprowadzeniem
reguły z dokumentu wycofanego. Ten sam błąd już raz omal nie wszedł do kodu przy
`TEST_COMPLETE`: wartość z wycofanej wersji wygląda dokładnie jak obowiązująca.

**Dlaczego to nie jest kosmetyka:** dopóki kształt predykatu nie jest związany, dwie
implementacje zapiszą „jednostka równa się A" inaczej (`{"jednostka":"A"}` wobec
`{"field":"jednostka","operator":"EQ","value":"A"}`) i policzą **różne `scope_id` dla tego
samego zakresu** — a `scope_id` wchodzi do `XR_RESULT_IDENTITY_V2` (v1.2 §7.2). Profil
kanoniczny gwarantuje zgodność bajtową dla tej samej struktury; struktury nie wymyśla.

**Warianty interpretacji:**

- A — związać trójkę `field / operator / value` i zamkniętą listę operatorów z v1.0 §4.1,
  wskazując je jako nadal obowiązujące.
- B — związać trójkę `field / operator / value`, ale operator zostawić jako token
  source-defined, bez zamkniętej listy.
- C — nie wiązać kształtu: predykat jest dowolną wartością kanonizowalną, podaną przez
  wołającego (stan dzisiejszy).
- D — wyjąć filtry z `scope_definition` do czasu rozstrzygnięcia i liczyć `scope_id`
  z pozostałych czterech składników.

**Konsekwencja każdego wariantu dla kodu:**

- A — `scope_id` zgodny między implementacjami od razu; ryzyko: kontrakt przywrócony
  z wersji archiwalnej bez decyzji Controllingu, czyli dokładnie to, czego zakazuje
  zasada 1 z CLAUDE.md.
- B — struktura jedna, słownik otwarty: `EQ` i `EQUALS` dadzą różne `scope_id`. Zgodność
  między implementacjami zależy wtedy od karty testu, nie od fundamentu.
- C — zero wymyślania, ale zgodność `scope_id` gwarantowana wyłącznie dla zakresów
  o pustych albo strukturalnie identycznych filtrach. Wektory C-T06 („SAME DATA /
  DIFFERENT SCOPE") są wykonalne, bo porównują dwa zakresy zbudowane tym samym kodem.
- D — `scope_id` przestaje rozróżniać zakresy różniące się wyłącznie filtrem, czyli łamie
  „same_label + different_semantics → different_scope_id" z v1.1 §10. Odrzucone jako
  sprzeczne z kontraktem, wymienione dla kompletności.

**Propozycja robocza (do zatwierdzenia przez Michała):** wariant C jako **założenie
tymczasowe** na czas rundy V12-R1, oznaczony w kodzie `# ASSUMPTION: B-09`. Pakiet P2 idzie
dalej z okresem, zakresem i referencją; nic w P2–P4 nie wymaga rozstrzygnięcia kształtu
predykatu, bo wszystkie wektory budują oba porównywane zakresy tym samym kodem.

**Co blokuje:** zgodność bajtową `scope_id` między niezależnymi implementacjami dla
zakresów z filtrami; każdą przyszłą wymianę `scope_id` z systemem zewnętrznym.

**Czego nie blokuje:** `scope_id` dla zakresów bez filtrów, pozostałych czterech
składników `scope_definition`, `XR_PERIOD_CANONICAL_V1`, `reference_id` ani
`XR_RESULT_IDENTITY_V2` w zakresie pakietu P4.

**ROZSTRZYGNIĘCIE**

| | |
| --- | --- |
| Data | 2026-09-23 |
| Decydent | Controlling (V12-R1) |

**Treść decyzji:**

> „korzystaj z dziedziczonego frozen Scope Identity Contract v1.0; nie twórz nowego."

Wariant A zatwierdzony. Scope Identity Contract z BIND-01 **v1.0 §4 / §4.1** jest
dziedziczony i zamrożony: struktura predykatu `field / operator / value`, nieistotność
kolejności predykatów, sortowanie po canonical bytes, `scope_definition_hash` jako SHA-256
lowercase hex i `scope_id = "SCOPE-" + hash` obowiązują wprost z tego dokumentu. Pozostała
treść v1.0 zostaje archiwalna — rozstrzygnięcie dotyczy wyłącznie kontraktu zakresu.

Zrealizowane w pakiecie P6: `src/xray/canonical/scope.py` (klasy `ScopePredicate`,
`ScopeOperator`, przebudowane `ScopeDefinition.payload`), oznaczenie w kodzie zmienione
z `# ASSUMPTION: B-09` na `# DECYZJA (Controlling, 2026-09-23), wpis B-09:`. Pole
`semantic_extensions` zmieniło nazwę na `contract_scope_extensions` — tak nazywa je v1.0 §4.

**Czego rozstrzygnięcie nie domknęło:** v1.0 §4.1 pkt 3 poprzedza listę operatorów słowem
„np.", więc nie jest ona zamknięta; kontrakt nie ustala też semantyki kolekcji w `IN` /
`NOT_IN` ani kształtu wartości dla `RANGE`. Trzy te braki prowadzi dalej wpis **B-12**.

---

