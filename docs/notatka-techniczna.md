# Notatka techniczna — fundament X-Ray

Produkt 4 z ZOP-TECH-01 pkt 7. Dokument rośnie razem z kodem: każda decyzja
technologiczna, której nie da się odczytać wprost z karty, ma tu zapisane uzasadnienie
i odrzucone alternatywy.

Zasada porządkująca: decyzja techniczna nie może po cichu rozstrzygać pytania
metodologicznego. Gdy okazuje się, że rozstrzyga — trafia do
`docs/otwarte-kontrakty.md`, a nie tutaj.

---

## DT-01. Typ liczbowy kwot i wielkości: `float`, nie `Decimal`

**Decyzja:** wszystkie pola liczbowe pięciu tabel bazowych (`amount`, `revenue`,
`volume`, `available`, `used`, `cost`, `target`) mają typ `float | None`.

**Uzasadnienie:**

1. `float64` jest natywnym typem pandas, Parquet i SQLite. `Decimal` wymuszałby
   konwersję przy każdej agregacji, a agregaty są tym, co testy diagnostyczne robią
   najczęściej.
2. Błąd względny arytmetyki `float64` jest rzędu 1e-15 — o wiele rzędów wielkości
   poniżej jakiejkolwiek istotności zarządczej.
3. Dokładność `Decimal` byłaby na wejściu pozorna: XLSX przechowuje liczby jako
   dwukładne liczby zmiennoprzecinkowe IEEE 754, więc wartość jest już przybliżeniem,
   zanim dotrze do modelu. `Decimal` utrwaliłby to przybliżenie, nie usunął.

**Odrzucona alternatywa:** `Decimal` dla kwot, `float` dla wielkości. Daje dwa reżimy
arytmetyczne w jednym kontrakcie i konieczność rozstrzygania, czym jest `target` w PLAN,
którego znaczenie zależy od pola `metric`.

**Zastrzeżenie, którego ta decyzja NIE rozstrzyga:** tolerancja uzgodnienia.
ZOP-XR-MGT-01 posługuje się `reconciliation_status` o wartościach `reconciled`,
`reconciled_with_explanation`, `unreconciled`, `not_comparable`. Jeżeli uzgodnienie
polega na porównaniu sumy z X-Ray z sumą z systemu księgowego klienta, to pytanie
„od jakiej różnicy suma przestaje być uzgodniona" jest pytaniem **metodologicznym do
MGT-01**, a nie technicznym. Nie zakładamy tu żadnej tolerancji — ani zera, ani grosza.
Temat wraca przy implementacji MGT-01.

---

## DT-02. Model jako bramka, ramka jako reprezentacja robocza

**Decyzja:** model Pydantic waliduje rekord po rekordzie **raz**, w `ingest/`, i tam
produkuje komunikat wskazujący konkretny wiersz. Dalej przez `validation/` i `engine/`
płynie ramka pandas, a nie lista obiektów.

**Uzasadnienie:** kryterium odbioru 8.4 wymaga komunikatu wskazującego problem i jego
miejsce — to daje walidacja jednowierszowa. Testy diagnostyczne robią grupowania
i agregaty — to daje ramka. Noszenie dziesiątek tysięcy obiektów Pythona przez cały
przepływ nie służyłoby żadnemu z tych dwóch celów.

---

## DT-03. Co model odrzuca, a czego nie

**Decyzja:** model odrzuca wyłącznie to, co czyni rekord bezużytecznym **jako rekord** —
wartość nieprzetłumaczalną na zadeklarowany typ oraz pusty element klucza naturalnego.
Nie odrzuca niczego, co jest **faktem diagnostycznym o danych**.

**Konsekwencje:**

- ujemna kwota przechodzi (wpis B-01),
- ujemne `available` i `used` przechodzą, mimo że ZOP-XR-CAP-01 VAL-04 i VAL-05 nazywają
  je CRITICAL — bo to walidator ma **ogłosić** ten status, a rekord odrzucony przez model
  nigdy do walidatora nie dotrze,
- `end` wcześniejsze niż `start` w PROCESS przechodzi z tego samego powodu,
- brak wartości przechodzi zawsze: `null` jest poprawnym wynikiem.

**Uzasadnienie:** walidator ogłasza status, a test deklaruje, co ten status dla niego
znaczy. Model, który sam odrzuca rekord, odbiera tę decyzję zarówno walidatorowi, jak
i testowi — i robi to bez śladu w wynikach.

**Sprostowanie:** we wcześniejszej propozycji układu `model/` podano `available >= 0`
jako przykład kontroli dopuszczalnej w modelu. Jest to niezgodne z regułą przyjętą
później (o warstwie decyduje wymagana informacja, a walidator ogłasza status).
Obowiązuje treść tego punktu.

---

## DT-04. Instalacja edytowalna zamiast `PYTHONPATH`

**Decyzja:** `pip install -e .` z minimalną sekcją `[project]` w `pyproject.toml`.

**Uzasadnienie:** kryterium 8.1 mówi o uruchamianiu bez ręcznej ingerencji w kod przy
każdym uruchomieniu, a produkt 6 to demonstracja uruchomienia. `PYTHONPATH=src` jest
zaklęciem, które trzeba pamiętać i które inaczej zapisuje się w Git Bashu, a inaczej
w PowerShellu. `pythonpath = ["src"]` w konfiguracji pytest zostaje jako zabezpieczenie
na wypadek pominięcia instalacji.

---

## DT-05. Znaczniki czasu bez strefy; przeliczenie należy do `ingest/`

**Decyzja:** pola typu `EventTimestamp` (dziś `PROCESS.start` i `PROCESS.end`) przyjmują
wyłącznie znaczniki **bez strefy czasowej**. Znacznik ze strefą jest odrzucany
z komunikatem wskazującym `ingest/`.

**Problem:** Pydantic przyjmie bez zastrzeżeń zarówno `"2026-03-01T08:30:00"`, jak
i `"2026-03-01T08:30:00+01:00"`. W jednej kolumnie mogą wylądować oba, a wtedy pierwsze
porównanie w kontroli 8 z pkt 5.3 podniesie
`TypeError: can't compare offset-naive and offset-aware datetimes`. Systemy eksportujące
zdarzenia procesowe często podają offset, więc nie jest to przypadek teoretyczny.

**Uzasadnienie:** metodologia nie zna pojęcia strefy czasowej — żadna karta jej nie
wymienia. Konstrukcja jest identyczna z rozstrzygnięciem dla numeru seryjnego daty
(`_reject_numeric_date`): model odmawia przyjęcia wartości niejednoznacznej, a konwersję
świadomą kontekstu pliku wykonuje warstwa, która ten kontekst zna.

**Podział ról:**

- `ingest/` przelicza znacznik na czas lokalny organizacji, bo tylko tam wiadomo,
  z jakiego pliku i systemu pochodzi wartość,
- strefa organizacji jest jawnym elementem **profilu mapowania klienta** — dzięki temu
  jest udokumentowana i audytowalna, a nie zaszyta w kodzie.

**Odrzucona alternatywa:** przyjmować oba warianty i odrzucać różnicę w `validation/`.
Oznaczałoby to, że kontrakt danych dopuszcza dwa nieporównywalne typy w jednym polu,
a walidator musiałby naprawiać coś, czego kontrakt nie powinien był wpuścić.

---

## DT-06. Kanonizacja braku, ale nie zera

**Decyzja:** brak wartości ma w każdym polu dokładnie **jedną** reprezentację.
`NaN` staje się `None` (`_normalize_missing_number`), a `""` i napis ze samych spacji
stają się `None` w polach tekstowych spoza klucza (`_normalize_missing_text`).
Zero nie staje się `None` nigdy.

**Uzasadnienie:** ta sama pusta komórka wraca raz jako `NaN`, raz jako `None`, raz jako
`""` — zależnie od tego, czy dane weszły przez CSV, czy przez XLSX. Bez kanonizacji
zliczanie braków (kontrola 3 z pkt 5.3) dałoby dwa różne wyniki dla tych samych danych.

**Granica wobec zasady 5:** pytanie brzmi, czy po operacji rekord mówi co innego niż
przed. `NaN` → `None` zmienia zapis; rekord przed i po mówi „nie wiem". Zero, średnia,
wartość z poprzedniego okresu albo interpolacja zmieniają treść: rekord przestaje mówić
„nie wiem" i zaczyna mówić „było tyle". Tego zasada 5 zakazuje.

**Dlaczego zero nie jest brakiem:** koszt kategorii w danym miesiącu mógł realnie wynieść
0 zł. ZOP-XR-FIN-01 rozdz. 6 rozróżnia te sytuacje wprost — „CI | R = 0 → null" opisuje
przychód **równy zeru**, a nie przychód nieznany, i jest to inna podstawa niż
„mianownik 0 → null" przy braku danych. Obie drogi kończą się miarą `null`, ale z innej
podstawy, a podstawa trafia do `validation_notes` i do danych dla ZOP-CONF-01. Sklejenie
zera z brakiem przy imporcie zniszczyłoby to rozróżnienie nieodwracalnie.

**Wartości niepustych nie przycinamy.** `"Dział A "` zostaje ze spacją, bo to dowód dla
kontroli 6 (niespójne nazwy jednostek).

---

## DT-07. Nazwy warstwy `engine/` a reguły zbierania pytest

**Decyzja:** publiczne nazwy w `engine/` nie zaczynają się od `test` / `Test`.
Deklaracja wtyczki nazywa się `DiagnosticTestDeclaration`, a funkcja rejestru —
`registered_test_ids()`.

**Problem:** w tym projekcie słowo „test" ma dwa znaczenia — test diagnostyczny
(FIN-01, CAP-01) i test jednostkowy pytest. Domyślne reguły zbierania pytest to
`python_classes = Test*` i `python_functions = test*`, więc pierwotne nazwy
`TestDeclaration` i `test_ids` wpadały w zakres zbierania.

**Skutek, który to wywołało:** pytest **uruchomił** zaimportowaną w module testowym
funkcję `test_ids` jako test jednostkowy. Test „przeszedł", nie sprawdzając niczego —
i liczył się w podsumowaniu jako 132. pozycja. Nie było to widoczne poza ostrzeżeniem.

**Uzasadnienie wyboru:** alternatywą było wyłączenie zbierania znacznikiem
`__test__ = False` albo zmiana `python_classes` w konfiguracji. Obie działają, ale
zostawiają nazwę, która myli czytelnika i wymaga pamiętania o obejściu przy każdej nowej
wtyczce. Nazwa `DiagnosticTestDeclaration` jest przy okazji dokładniejsza: to deklaracja
testu **diagnostycznego**, w repozytorium, które zawiera także testy jednostkowe.

**Zasada na przyszłość:** przy dokładaniu wtyczek nazwa publiczna nie może zaczynać się
od `test`. Fałszywie przechodzący test jest gorszy od braku testu, bo daje pokrycie,
którego nie ma.

---

## DT-08. Typy kolumn ramki pochodzą z kontraktu, nie z zawartości pliku

**Decyzja:** po przejściu bramki kontraktu każda kolumna ramki dostaje typ wyliczony
z **kontraktu danych**, a nie z tego, jakie wiersze akurat trafiły do pliku.

| Rodzaj pola | Typ kolumny | Zapis braku |
| --- | --- | --- |
| `datetime` (`PROCESS.start`, `PROCESS.end`) | `datetime64[ns]` | `NaT` |
| `date` (`ACTIVITY`, `COST`, `RESOURCE`, `PLAN`) | `object` z `datetime.date` | nie dotyczy — pole klucza |
| liczbowe | `float64` | `NaN` |
| tekstowe | `object` | `None` |

**Problem, który to rozwiązuje:** konstruktor pandas zgaduje typ z zawartości. Kolumna
`PROCESS.end` z samymi brakami wychodziła obiektowa (brak jako `None`), a z jednym
znacznikiem — czasowa (brak jako `NaT`). Sposób sprawdzania braku zależałby więc od tego,
co klient akurat przysłał. To ten sam problem, który DT-06 rozwiązuje na granicy modelu,
tylko przesunięty o warstwę wyżej.

**Reguła dla warstw wyższych:** wewnątrz modelu brak ma jedną reprezentację — `None`.
W ramce brakiem rządzą znaczniki pandas właściwe dla typu kolumny, a jedynym poprawnym
sposobem sprawdzenia braku jest `pd.isna()`. Obie warstwy są spójne wewnętrznie; `pd.isna`
jest mostem między nimi.

**Dlaczego `date` zostaje kolumną obiektową:** pandas nie ma typu daty bez czasu.
Zamiana na `datetime64[ns]` dokładałaby północ, której w danych nie było, i `datetime.date`
z kontraktu zamieniałby się w `Timestamp`.

**ROZSTRZYGNIĘTE przy kontroli 8 (2026-09-06): typ kolumny źródłowej zostaje nietknięty.**

Sprawdzenie było warunkiem, który postawił Michał: czy kolumna pochodna z okresem
wystarcza do wszystkiego, czego kontrola 8 potrzebuje. Wystarcza.
`pd.PeriodIndex(pd.to_datetime(kolumna), freq="M")` zbudowana wewnątrz kontroli daje:

| Potrzeba kontroli 8 | Z kolumny pochodnej |
| --- | --- |
| `period_min` / `period_max` | `min()` / `max()` kolumny źródłowej |
| `months_in_range` | `period_range(min, max)` |
| `months_covered` | `nunique()` |
| brakujące miesiące | różnica zbiorów |
| licznik na miesiąc | `groupby` po okresie |

Kolumna pochodna powstaje w kontroli i ginie wraz z nią — do danych nie trafia. Koszt to
jedna linia w kontroli; korzyścią jest to, że ramka niesie dokładnie ten typ, który
deklaruje kontrakt. Wierność kontraktowi wygrywa i temat jest zamknięty.

**Znaleziona przy okazji pułapka:** rozpoznawanie typu pola po tekstowej reprezentacji
adnotacji jest wadliwe — `str(datetime.date)` zawiera podłańcuch „datetime", więc
dopasowanie tekstowe uznawało każdą datę za znacznik czasu. Rozpoznajemy po typach
(`get_args`), sprawdzając `datetime.datetime` przed `datetime.date`, bo pierwszy dziedziczy
po drugim.

---

## DT-09. Wersja algorytmu tożsamości zapisywana w rekordzie

**Decyzja:** każdy rekord niosący wyliczany identyfikator — `FindingRecord`,
`ClaimRecord`, `EvidenceRecord`, `ClaimEvidenceLink`, `SourceRef` — ma pole
`identity_algorithm_version`. Pole wchodzi do krotki tożsamości, a sprawdzenie przy
odczycie przelicza skrót **algorytmem wskazanym przez rekord**, nie bieżącym.

**Problem:** `contract_version` mówi, jakie pola ma rekord. Nie mówi, jak z nich policzono
skrót. Zmiana krotki tożsamości, kanonizacji, funkcji skrótu, jego długości albo prefiksu
daje inny skrót dla tej samej treści — więc po takiej zmianie **każdy** wcześniej zapisany
rekord zaczyna być odrzucany przy odczycie, i nie ma sposobu, żeby odróżnić rekord
policzony starym algorytmem od uszkodzonego. Jedyną drogą byłaby migracja całego magazynu
przy każdej zmianie.

**Kryterium z wariantu B stosuje się wprost:** wartość istnieje wyłącznie w chwili zapisu
i po niej nie da się jej odtworzyć. Dlatego wchodzi teraz, dopóki magazyn jest pusty.

**Dwa rodzaje niepowodzenia, których nie wolno mylić:**

| Sytuacja | Wyjątek | Znaczenie |
| --- | --- | --- |
| skrót nie zgadza się z krotką tożsamości | `ValueError` z walidacji | rekord zmieniono po zapisie |
| nieznana wersja algorytmu | `UnknownIdentityAlgorithm` | rekord zapisano innym wydaniem systemu; **nie jest uszkodzony** |

Osobny wyjątek jest tu istotą rzeczy: gdyby oba przypadki dawały ten sam błąd, poprawne
dane zapisane nowszą wersją byłyby raportowane jako uszkodzone.

**Zasada na przyszłość:** zmiana którejkolwiek z rzeczy wymienionych wyżej wymaga
podniesienia `IDENTITY_ALGORITHM_VERSION` i dopisania nowej funkcji do rejestru
`_ALGORITHMS`. Stare wersje **zostają** — usunięcie wersji z rejestru unieruchamia odczyt
rekordów, które ją wskazują.

---

## DT-10. `dataset_id` w tożsamości źródła

**Decyzja:** `ingest.load_table` wymaga `dataset_id`, a wartość wchodzi do skrótu
`SourceRef.source_id`. Argument jest obowiązkowy — bez wartości domyślnej.

**Problem:** `source_id` liczony z nazwy pliku, arkusza i wiersza nagłówka jest ten sam
dla dwóch różnych klientów przysyłających `koszty.csv`. Wtedy te same numery wierszy dają
te same `row_id`, a w magazynie obejmującym więcej niż jeden zbiór ślad wskazuje nie ten
plik. Nie jest to problem teoretyczny nawet na etapie fundamentu: firma syntetyczna
i pierwszy plik testowy klienta mogą trafić do jednego magazynu.

**Dlaczego zadeklarowany, a nie wyprowadzony:** wyprowadzenie ze ścieżki katalogu albo
z nazwy pliku byłoby zgadywaniem — ten sam klient może trzymać pliki w różnych katalogach,
a dwóch klientów w katalogach o tej samej nazwie. Docelowo wartość pochodzi z profilu
mapowania (piąty element kontraktu `mapping/`): jeden profil = jeden klient = jeden zbiór.

**Dlaczego argument obowiązkowy:** wartość domyślna byłaby założeniem, a nie deklaracją,
i przy pierwszym drugim zbiorze cicho skleiłaby identyfikatory.

Ścieżka bezwzględna nadal **nie** wchodzi do tożsamości — zależy od maszyny. Pozostaje
zapisana w `source_path` dla audytu.

---

## DT-11. Wynik kluczowany parą `(finding_id, run_id)`

**Problem:** `finding_id` powstaje z `test_id + scope + period + wersje`. Dane wejściowe
nie wchodzą do tożsamości wyniku. Klient przysyła poprawiony plik, uruchamiamy przebieg
ponownie — ten sam test na tym samym zakresie i okresie daje **ten sam `finding_id`
przy innej treści**. Dwie różne odpowiedzi na to samo pytanie.

| Wariant | Zachowanie | Ocena |
| --- | --- | --- |
| klucz `finding_id`, nadpisanie | ostatni wygrywa | Kasuje ślad. ZOP-PRI-01 rozdz. 3: „nie nadpisuje śladu wcześniejszej oceny". |
| klucz `finding_id`, konflikt = błąd | ponowny zapis odrzucony | Blokuje uprawniony przypadek: poprawione dane klienta. |
| **klucz `(finding_id, run_id)`** | obie odpowiedzi zostają | **Przyjęte.** |

**Główny zysk, którego nie wolno zepsuć:** dwa wiersze o tym samym `finding_id` i różnym
`run_id` to dwie odpowiedzi na to samo pytanie, dane na różnych danych. Po `finding_id`
da się prześledzić **historię jednego wyniku przez kolejne przebiegi** — jak zmieniała się
luka, kiedy status przestał być `NO_ADVERSE_SIGNAL`. Najłatwiej to zepsuć przy pierwszej
„optymalizacji" schematu, zwężając klucz do samego `finding_id`. Historii, raz utraconej,
nikt później nie odtworzy.

**Idempotentność:** ten sam `run_id` z identyczną treścią to brak operacji; z inną treścią
to `ConflictingRun`, a nie nadpisanie — bo znaczyłby, że ten sam skrót wejścia dał inny
wynik, czyli że coś w przepływie nie jest deterministyczne.

---

## DT-12. Skrót treści liczony przy imporcie, z treści rekordów

**Decyzja:** `ImportReport.content_digest` jest liczony **przyrostowo w pętli importu**,
z kanonicznej treści przyjętych rekordów.

**Dlaczego przy imporcie, a nie w magazynie:** przy milionie wierszy drogą częścią nie jest
skrót, tylko walidacja rekord po rekordzie — a ta praca jest już wykonana. Liczenie skrótu
w `store/` wymagałoby drugiego przejścia po tych samych danych tylko dlatego, że policzono
by go w niewłaściwym miejscu. Skrót zawartości jest faktem o tym, co wczytano, więc należy
do raportu importu.

**Dlaczego z treści rekordów, a nie z bajtów pliku:** ten sam zbiór w CSV i XLSX daje
identyczną ramkę, więc musi dać ten sam `run_id`. Zmiana formatu zapisu nie jest zmianą
danych. Skutek uboczny jest pożądany: przeformatowanie pliku bez zmiany wartości nie tworzy
nowego przebiegu, a zapis pozostaje idempotentny.

**Znaleziona przy okazji pułapka:** pierwsza wersja wciągała do skrótu `row_id`, a ten
niesie `source_id`, czyli nazwę pliku. `koszty.csv` i `koszty.xlsx` o identycznej treści
dostawały dwa różne skróty — czyli dokładnie ten błąd, którego skrót z treści miał uniknąć.
Do skrótu wchodzi wyłącznie treść rekordu.

**Co wchodzi do tożsamości przebiegu, a co nie:**

| Element | W skrócie | Powód |
| --- | --- | --- |
| `dataset_id` | tak | inny klient to inne dane |
| `content_digest` | tak | treść wyniku od niej zależy |
| `records_rejected` | tak | odrzucenia czyta kontrola 2 i 3; wpływają na obraz jakości |
| `source_id` | **nie** | niesie nazwę pliku; nie wpływa na wynik |
| `executed_at` | **nie** | pole audytowe; w skrócie łamałoby zasadę 3 |

`source_id` jest zapisany obok, w kolumnie `provenance` — audyt go potrzebuje, tożsamość
nie.

---

## DT-13. `definition_match_basis` wchodzi do skrótu znaczącej treści profilu

**Decyzja (Michał, 2026-09-07):** podstawa zgodności definicji miary planu wchodzi do
skrótu profilu, a przez to do `run_id`. `declared_by` i `declared_at` zostają poza —
mówią **kto**, nie **dlaczego to wolno**.

**Dlaczego to nie jest oczywiste.** Argument za wyłączeniem: samo dopasowanie niosą
`plan_metric` i `target_measure`, a poprawka redakcyjna uzasadnienia nie zmienia
odpowiedzi. Ten argument jest poprawny **dla poprawki redakcyjnej**.

**Dlaczego jednak wchodzi.** `definition_match_basis` to osąd, nie wyprowadzenie. Zmiana
z „obie miary liczą koszt osobodni tak samo" na „miary różnią się ujęciem VAT, przyjęto
przybliżenie" nie rusza ani `plan_metric`, ani `target_measure`, a zmienia to, czy warunek
ZOP-XR-FIN-01 rozdz. 6 („zgodna definicja miary") jest spełniony. Dziś nic tego nie czyta;
ZOP-CONF-01 będzie — to dowód dla twierdzenia w znaczeniu z karty.

**Koszty pomyłki są asymetryczne:**

| Gdyby pomylić się | Skutek |
| --- | --- |
| poza skrótem, a okazałaby się znacząca | ten sam `run_id`, inna treść → `ConflictingRun` z komunikatem „przepływ nie jest deterministyczny". A jest. **Magazyn kłamie o samym sobie.** |
| w skrócie, a okazałaby się nieznacząca | szum w historii przebiegów; nic nie twierdzi nieprawdy |

**Tekstu nie normalizujemy przed hashowaniem.** Normalizacja byłaby decyzją, które różnice
w uzasadnieniu są nieistotne — a tego rozstrzygnięcia nie robi żadna karta.

Zapisane, żeby dało się to odwrócić świadomie, a nie przez przeoczenie.

---

## DT-14. Zgodność wstecz weryfikacji tożsamości — świadomie odroczona

**Stan faktyczny:** rejestr `_ALGORITHMS` trzyma funkcje skrótu, ale nie stare kształty
krotek tożsamości. Rekord zapisany z wersją `"1"`, odczytany kodem o zmienionej krotce,
przejdzie przez **bieżącą** krotkę i zostanie odrzucony jako zmieniony. Docstring
`identity.py` obiecywał zgodność wstecz, której nie ma — obietnica została usunięta.

**Dlaczego „migracja magazynu" jest droższa, niż brzmi.** Migracja znaczy przeliczenie
tożsamości, a tożsamość wyznacza `finding_id`. Przenumerowanie kasuje **historię wyniku
przez przebiegi** (DT-11) i wymagałoby tablicy stary → nowy, żeby cokolwiek z niej
uratować.

**Droga, gdy stanie się potrzebna:** weryfikacja przy odczycie może korzystać z **zapisanej
postaci kanonicznej** — mamy ją w `findings.identity_canonical` i `runs.input_digest`,
a jej klucze **są** zbiorem pól tamtej wersji. Stary rekord da się wtedy sprawdzić bez
starego budowniczego krotki: skrót wobec zapisanej postaci, wartości pod jej kluczami wobec
bieżącego rekordu.

**Ograniczenie tej drogi:** nie obejmie pola **usuniętego** z modelu — zapisana postać
będzie miało klucz, którego rekord już nie ma.

**Nie implementujemy tego teraz.** Magazyn jest pusty, nic nie wymusza wyboru, a decyzja ma
zapaść, gdy będzie co migrować.

**Reguła obowiązująca do tego czasu:** wersja należy do kształtu krotki **danego rodzaju
rekordu**, nie do systemu. Zmiana krotki `RunRef` podnosi wersję przebiegu; krotka
`FindingRecord` się nie rusza i jej wersja zostaje `"1"`. Jedna wspólna stała unieważniałaby
weryfikację rekordów, których zmiana nie dotyczyła.

---

## DT-15. Dwa rodzaje pustki w `time_basis_used` — odroczone

Obie gałęzie kontroli 8 zwracają `time_basis_used` jako `is_unknown`, a różni je wyłącznie
proza w `basis`: „kontrakt globalny nierozstrzygnięty" (tabela zdarzeniowa) wobec „etykieta
okresu pochodzi wprost z pola `date`" (tabela okresowa). To **dwa różne stany**: tam nie ma
czego rozstrzygać, tu jest i świadomie tego nie robimy.

Na poziomie kontroli mamy na to słownik — `not_applicable` wobec `insufficient_basis`.
Na poziomie obserwacji mamy tylko `is_unknown`, więc rozróżnienie niesie proza — ten sam
kształt, który odrzuciliśmy przy `not_assessed_reason` i przy klasyfikacji odrzuceń.

**Nie domykamy tego teraz.** Żadna karta tego nie wymaga, nikt tego dziś nie czyta,
a czwarte zastosowanie tej samej reguły bez realnego użytkownika byłoby domykaniem dla
kompletności (MASTER v1.2 pkt 17.1). Wraca razem z domknięciem kontraktu globalnego
`time_basis`, kiedy `time_basis_used` zacznie nieść wartość.

**Reguła, którą przy okazji ustaliliśmy:** stała jest szumem, gdy powtarza coś powiedziane
gdzie indziej; stała jest **informacją**, gdy jest jedynym miejscem, w którym zadeklarowany
jest wymagany brak. `null` jest poprawnym wynikiem — ale wynikiem jest tylko wtedy, gdy
jest **ogłoszony**. Skasowanie zamienia „null z podstawą" w „nic".

---

## DT-16. Asercja na obserwowalnym skutku, nie na mechanizmie

**Reguła:** gdy własność jest „zagwarantowana konstrukcją", test ma sprawdzać
**obserwowalny skutek**, dla którego gwarancję wprowadzono — nie sam mechanizm.

**Dlaczego to nie jest oczywiste:** mechanizm bywa poprawny, a mimo to nie daje skutku,
o który chodziło. Trzy wystąpienia tej samej figury:

| Kiedy | Mechanizm działał | Nazwana własność była nie ta | Skutek |
| --- | --- | --- | --- |
| DT-07 | test przechodził | „test przechodzi" zamiast „pytest zbiera tę funkcję" | `test_ids` uruchamiane jako test, nie sprawdzało niczego |
| pary porównawcze | kontrola 7 zwracała PASS | „kontrola daje PASS" zamiast „kontrola mogła zobaczyć różnicę" | PASS był jedyną możliwością przy wspólnej kolumnie |
| generator | sprawa **faktycznie** przekraczała granicę miesiąca | „sprawa przekracza granicę" zamiast „zbiór miesięcy startów różni się od zbioru miesięcy końców" | `months_with_stage_starts` = `months_with_stage_ends` = 25 |

Trzeci przypadek jest najczystszy, bo gwarancja **nie była wadliwa**: sprawa startowała
ostatniego dnia o 20:00 i naprawdę kończyła się w następnym miesiącu. Wadliwe było
przełożenie gwarancji na obserwację — skoro przelewał się **pierwszy** etap, kolejne
etapy **zaczynały się** już w następnym miesiącu, więc oba zbiory miesięcy zrównały się
mimo działającego mechanizmu. Naprawa: przelewa się **ostatni** etap.

**Środek zaradczy, który zadziałał za każdym razem:** asercja na wielkości, którą czyta
odbiorca. Nie „jakaś sprawa przekracza granicę", tylko `months_with_stage_starts == 24`
i `months_with_stage_ends == 25`.

Reguła wróci przy każdym module, w którym coś jest „zagwarantowane konstrukcją".

---

## DT-17. Zapisane ograniczenia zbioru syntetycznego

Trzy uproszczenia firmy syntetycznej. Zebrane tutaj, a nie rozproszone po docstringach
trzech modułów, żeby dało się je przeczytać razem — i żeby nikt nie wziął ich za
własności danych.

**1. Brak kalendarzy operacyjnych.** `available` to stałe 160 godzin miesięcznie, a nie
liczba dni roboczych. Kalendarze operacyjne i `time_basis` są otwartym kontraktem
ZOP-MASTER-01 rozdz. 17; modelowanie ich w generatorze byłoby wymyśleniem reguły, której
karta nie ustanawia. Skutek: miesiące różnią się sezonowością, ale nie liczbą dni pracy.

**2. Brak dryfu — gwarantowany, ale nie absolutny.** Żadna wielkość nie zależy od numeru
miesiąca inaczej niż przez powtarzalny współczynnik sezonowy, więc z konstrukcji nie ma
trendu. **Nie gwarantujemy**, że przy jakimś ziarnie szum nie ułoży się przypadkiem
w coś, co wygląda jak trend — tego zagwarantować się nie da i nie udajemy, że da.

**3. Przychód jest iloczynem wolumenu i stałej ceny produktu.** Relacja przychód/wolumen
ma więc **zerową wariancję**: cena jednostkowa nie drga wcale. To uproszczenie chroniące
przed przypadkowym dryfem ceny, a nie własność realnych danych. Test badający stabilność
ceny jednostkowej dostałby na tym zbiorze wynik idealny, który nic nie znaczy.

Ograniczenia 1 i 3 znikną, gdy powstanie wersja zbioru z celowo wprowadzonymi
odchyleniami (ZOP-TECH-01 pkt 5.5.5). Ograniczenie 2 zostaje na zawsze.

---

## DT-18. Granulacja per twierdzenie — odroczona

**Stan:** deklaracja testu wymaga pól na poziomie **całego testu**
(`DiagnosticTestDeclaration.required_by_test`). Rozstrzygnięcie B-06 rozróżnia jednak
dwa poziomy: `required_by_test` i `required_by_claim`.

**Na czym polega różnica.** Test może wydać **część** twierdzeń i wstrzymać się od reszty.
Brak pola potrzebnego jednemu twierdzeniu nie musi unieważniać pozostałych — to jest
dokładnie różnica między `TEST_PARTIAL` a `TEST_BLOCKED` z katalogu statusów logicznych.
Przy deklaracji na poziomie testu każdy brak prowadzi do jednego wyniku dla całego testu.

**Nie budujemy tego teraz.** Żaden test nie produkuje dziś twierdzeń — `ClaimRecord`
istnieje w kontrakcie, ale nikt go nie wypełnia. Deklaracja per twierdzenie byłaby
mechanizmem bez użytkownika, czyli domykaniem dla kompletności (MASTER v1.2 pkt 17.1).

**Miejsce jest przewidziane:** nazwa `required_by_test` niesie swój poziom, więc dołożenie
`required_by_claim` obok niej nie wymaga przemianowania niczego. To jedyny koszt, który
warto ponieść zawczasu — nazwa, nie mechanizm.

**Wraca:** z **CAP-01**, i to jest termin wcześniejszy, niż zapisano tu pierwotnie
(było: „razem z ZOP-CONF-01"). Karta CAP-01 zawiera już dowód, że rozróżnienie będzie
potrzebne — CAP01-T10:

> „Brak `cost` | `available` i `used` poprawne, `cost` null | U, UC, UCR, UG i luka
> fizyczna; ekonomika null | wg trendu; **nie TEST_BLOCKED** | `economic_gap=null`; jawne
> ograniczenie"

Czyli: `cost` jest wymagane **twierdzeniom ekonomicznym** CAP-01, a nie całemu testowi.
Test ma dalej wydać miary fizyczne i ustawić `economic_gap = null`.

**Konsekwencja operacyjna, obowiązująca od dziś:** przy samej deklaracji na poziomie testu
CAP-01 **nie może umieścić `cost` w `required_by_test`** — bramka wyprodukowałaby wtedy
`TEST_BLOCKED`, czyli status, którego karta zakazuje wprost. Do czasu zbudowania
`required_by_claim` obowiązuje więc reguła: w `required_by_test` trafia wyłącznie pole,
bez którego test nie wydaje **żadnego** twierdzenia. Pole potrzebne części twierdzeń
zostaje poza deklaracją, a odmowę wydaje sam test w swoim wyniku.

**Skutek dla katalogu statusów:** `LogicalStatus.TEST_PARTIAL` pozostaje wartością
**nieosiągalną w kodzie** do czasu zamknięcia tego odroczenia. Bramka zna jedną wartość —
`TEST_BLOCKED` — i nie zgaduje drugiej.

**Pierwszy użytkownik:** CAP-01, moduł ekonomiczny (`economic_gap`, `UG`).

---

## DT-19. Kontrola 1 ogłasza stan, nie orzeka o ciężarze

**Decyzja (Michał, 2026-09-08, wpis B-06):** kontrola 1 ma dwa stany, nie trzy.

| Czego brakuje | Status |
| --- | --- |
| element `NATURAL_KEY` | CRITICAL |
| dowolne inne pole | **PASS z obserwacją** |

Gałąź WARNING **nie istnieje**.

**Dlaczego to nie jest rozluźnienie.** Wcześniejsza wersja dawała WARNING za brak każdego
pola spoza klucza. To orzeczenie o ciężarze, którego walidator nie zna: czy brak pola
ogranicza wnioskowanie, zależy od tego, **który test się uruchomi**.

> „Walidator danych ogłasza stan danych, ale nie przejmuje metodologicznej
> odpowiedzialności testu diagnostycznego."

**Dlaczego PASS nie jest fałszywym przejściem.** Fakt braku kolumny jest w wyniku — jako
obserwacja z podstawą, tylko nie jako status. Rozróżnienie jest to samo co przy kontroli 3:
**obraz, nie werdykt**. Kontrola 1 i 3 należą teraz do jednego gatunku.

**Gdzie przenosi się odpowiedzialność.** Test, który potrzebuje brakującego pola, nie może
udawać wyniku — zwraca `not_assessable` albo `TEST_PARTIAL` / `TEST_BLOCKED`. Egzekwuje to
rejestr testów wobec rzeczywistych raportów importu, tak jak rejestr kontroli egzekwuje
`max_status` i `comparison_pairs`.

**Warunek, bez którego ta decyzja byłaby luką:** dopóki rejestr testów nie egzekwuje
`required_by_test`, PASS kontroli 1 przy braku pola **nie ma odbiorcy**, który by ten brak
podniósł. Deklaracja bez egzekucji to deklaracja, a nie mechanizm — ta sama figura co
w DT-16.

**Warunek spełniony 2026-09-08:** bramka gotowości istnieje — wpis DT-20. PASS kontroli 1
ma odbiorcę.

---

## DT-20. Bramka gotowości testu — gdzie stoi i dlaczego nie w rejestrze

**Problem.** Deklaracja testu była sprawdzana wyłącznie wobec **kontraktu danych**, przy
imporcie modułu: czy tabela istnieje w `TABLES` i czy pole jest w `model_fields`. To
sprawdzenie jest prawdziwe zawsze, niezależnie od tego, co przyszło w pliku. Zdanie „test
nie może udawać wyniku" z rozstrzygnięcia B-06 nie było więc przez nic realizowane.

**Rozstrzygnięcie B-06 mówi „rejestr testów egzekwuje". Egzekwowanie stoi piętro niżej.**
Rejestr jest złym punktem egzekwowania, bo `get_test(...)().run(...)` go omija — i tak
właśnie robiła **nasza własna demonstracja**. Bramka siedzi w metodzie szablonowej
`DiagnosticTest.execute`: liczy gotowość i dopiero wtedy woła `run`. `engine.run_test()`
zostaje cienką funkcją rejestru, więc literalne brzmienie rozstrzygnięcia jest spełnione,
a mechanizmu nie da się ominąć.

**Ochrona metody szablonowej.** `__init_subclass__` odrzuca podklasę nadpisującą `execute`
albo `readiness` — ta sama technika, którą `model/tables/base.py` wymusza metadane tabel.
Bez niej wtyczka mogłaby obejść bramkę dokładnie tak, jak dziś omijało się rejestr. Bramka,
którą wolno nadpisać, jest konwencją; bramka, której nadpisać nie wolno, jest mechanizmem.

**Skąd bierze fakty.** Z `ImportReport.fields_without_column` — unii `missing_key_columns`
i `materialized_empty`. Kontrola 1 potrzebuje **rozdziału** obu krotek (klucz → CRITICAL,
reszta → PASS), bramka potrzebuje **unii**. Jedna własność na raporcie zamiast dwóch
składań w dwóch warstwach.

**Trzy stany wiedzy, nie dwa.** `import_reports` jest odwzorowaniem tabela → krotka
raportów albo `None`. Brak tabeli w odwzorowaniu i `None` znaczą „nie wiadomo" i też
kończą się odmową — z osobnym powodem `UNKNOWN_IMPORT`. Pusta krotka jest zakazana. To ta
sama reguła, dla której kontrola 1 nie ogłasza PASS bez raportu importu: „nie wiem" nie
jest podstawą do wydania wyniku. Bramka zamyka się w stronę bezpieczną — `{}` daje odmowę,
a nie wykonanie.

**Odmowa jest wynikiem, nie śmieciem.** Brak gotowości daje **jeden** `FindingRecord` ze
statusem `TEST_BLOCKED`, bez `metric_value`, z podstawą w `validation_notes`. Wyjątek
odpadł, bo B-06 mówi wprost, że brak pola **nie blokuje przebiegu**; osobny obiekt
gotowości bez zapisu odpadł, bo byłby odmową, której nikt nie widzi — czyli tą samą
nieobecnością odbiorcy, którą naprawiamy.

**Pierwszy realny użytkownik klucza złożonego z pary (DT-11).** Tożsamość wyniku to
`test_id + scope + period + contract_version`, więc odmowa i policzony wynik z późniejszego
przebiegu mają **ten sam** `finding_id` i różne `run_id`. `FindingStore.history()` pokazuje
„przebieg 1: TEST_BLOCKED, przebieg 2: policzone". Rekordów odmowy **nie wolno usuwać przy
porządkowaniu magazynu**: bez nich ślad mówiłby, że test policzył wynik, i milczał o tym,
że wcześniej nie miał czym.

**Decyzja: bramka ustawia `validation_required = True`.** ZOP-PRI-01 mówi, że
`TEST_BLOCKED` *może* generować `validate_now`, jeżeli luka blokuje ważną decyzję — routing
należy do PRI-01. Bramka flagę ustawia, bo „w danych nie było kolumny" jest **faktem
o danych**, a nie oceną wagi decyzji.
*Alternatywa odrzucona:* zostawić `False` i czekać na PRI-01. Wtedy jedyny ślad, że wynik
wymaga uzupełnienia danych, żyłby w tekście komunikatu, czyli w miejscu, którego nie da się
odpytać. Decyzja jest techniczna i PRI-01 może ją **świadomie odwrócić** — zapisana tu po
to, żeby odwrócenie było decyzją, a nie odkryciem.

**Granica bramki: kolumny, nie wypełnienie.** Pole, które kolumnę miało, a jest w stu
procentach puste, przechodzi — to sprawa kontroli 3 i samego testu. Rozszerzenie bramki na
kompletność byłoby wymyśleniem progu (zasada 1).

**Luka, którą znalazł własny test, i której bramka nie zamyka.** ACTIVITY bez kolumny
`unit` jest tabelą rozbitą strukturalnie: kontrola 1 daje CRITICAL, wszystkie wiersze są
odrzucane, ramka jest pusta. Mimo to test wymagający **wyłącznie** `revenue` przechodzi
bramkę i liczy na pustej ramce.

To nie jest wada bramki — odpowiada ona na jedno pytanie: czy pole z `required_by_test`
miało kolumnę. Egzekwowanie CRITICAL **wymaganych kontroli** to osobny mechanizm
(`required_validations`), którego B-06 nie dotyczy i którego jeszcze nie ma: deklaracja
istnieje, `run_checks` zwraca statusy, ale nic nie łączy jednego z drugim. To ta sama
figura co przed DT-20 — deklaracja bez egzekucji. Zamknięcie wymaga rozstrzygnięcia
metodologicznego (co CRITICAL wymaganej kontroli oznacza dla testu: `TEST_BLOCKED`
czy `TEST_PARTIAL`), więc nie domykamy go technicznie z własnej inicjatywy.

**Skutek dla katalogu statusów.** `LogicalStatus.TEST_PARTIAL` pozostaje wartością
**nieosiągalną w kodzie** do czasu zbudowania `required_by_claim` (DT-18). Bramka zna jedną
wartość i nie zgaduje drugiej.
