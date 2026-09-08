# Implementuje ZOP-TECH-01 v0.1 pkt 5.2, tabela PROCESS (case_id, stage, start, end, unit).
"""Kontrakt tabeli PROCESS — przebieg procesu.

Rola tabeli wg kart: ZOP-XR-PROC-01 v1.0 pkt 2.3 („oś czasu przypadku i przejścia przez
etapy"), ZOP-XR-PROC-02 pkt 2.3 („zdarzenia przejścia przypadków przez proces").

## Czym ta tabela różni się od pozostałych czterech

PROCESS jest **jedyną tabelą zdarzeniową**. Pozostałe cztery niosą agregaty okresowe
i mają ``date`` jako etykietę okresu. PROCESS niesie zdarzenia i ma czas rzeczywisty
w ``start`` i ``end``.

Czasu tu nie brakuje — brakuje **etykiety okresu**, a ta jest wyliczalna na kilka
sposobów, z których każdy daje inny wynik. Przypadek rozpoczęty w marcu i zamknięty
w maju należy do marca albo do maja, zależnie od tego, czy podstawą jest start sprawy,
start etapu, koniec etapu, czy zamknięcie sprawy. To decyzja metodologiczna, nie
techniczna, i fundament jej nie podejmuje: pola ``date`` tu nie ma, bo byłoby
redundantne wobec ``start`` / ``end`` i zamrażałoby regułę, której TECH-01 nie
rozstrzyga.

## Co wolno, a czego nie wolno kontroli 8 (rozstrzygnięcie z 2026-09-05)

**Wolno** — bo nie wymaga wyboru podstawy przypisania:

- ``period_min`` = min(``start``), ``period_max`` = max(``end``) i rozpiętość między
  nimi; to jest **zakres danych**, a nie przypisanie,
- liczba **zdarzeń** w miesiącu, liczona po własnym znaczniku czasu zdarzenia —
  zdarzenie ma jeden moment i nie wymaga rozstrzygnięcia,
- ``months_without_events``: miesiące bez zdarzeń.

**Nie wolno** — przypisywać **sprawy** (``case_id``) do miesiąca. Sprawa rozpoczęta
w marcu i zamknięta w maju nie należy do żadnego z nich, dopóki kontrakt globalny nie
powie, jak to liczyć. ``time_basis_used`` zwraca ``null`` z jawną podstawą
„kontrakt globalny nierozstrzygnięty", nigdy wybraną wartość.

Miesiąc bez zdarzeń **nie jest błędem**. W pozostałych tabelach brakujący miesiąc to
luka w danych; w PROCESS może być miesiącem, w którym faktycznie nic nie przyszło,
i bez referencji nie da się tych dwóch sytuacji rozróżnić. Walidator raportuje to jako
obserwację, nie jako WARNING ani CRITICAL.

Patrz: docs/otwarte-kontrakty.md wpis A-01 (sekcja C, rozstrzygnięty), odwołujący się do
kontraktu ``kalendarze operacyjne / time_basis`` z ZOP-MASTER-01 v1.2 rozdz. 17.
"""

from typing import ClassVar

from xray.model.enums import TimeGrain
from xray.model.tables.base import (
    EventTimestamp,
    KeyText,
    OptionalKeyText,
    TableRecord,
)

# DECYZJA (Michał, 2026-09-05), wpis A-01: nie rozstrzygamy teraz `time_basis`.
# Przechowujemy znaczniki czasu i NIE przypisujemy procesu arbitralnie do miesiąca.
# Nie ma domyślnej podstawy przypisania — wcześniejsze robocze `stage_start` zostało
# wycofane i nie zostaje nawet jako założenie. Kontrola 8 nie ma prawa wybrać sobie
# podstawy; `time_basis_used` zwraca null z podstawą „kontrakt globalny
# nierozstrzygnięty". Podstawa przypisania będzie osobnym kontraktem globalnym.


class ProcessRecord(TableRecord):
    """Pojedyncze przejście przypadku przez etap procesu.

    Klucz naturalny ``case_id + stage``. ZOP-XR-PROC-02 pkt 2.4 wprowadza rozszerzenie
    ``repeat_visit`` na powroty do tego samego etapu — od tego momentu klucz przestanie
    być unikalny bez tego pola. Do czasu implementacji PROC-02 powtórzone przejście przez
    ten sam etap zobaczy kontrola 4 (duplikaty) i ogłosi je jako sygnał; nie jest to
    automatycznie błąd danych.
    """

    TABLE_NAME: ClassVar[str] = "PROCESS"
    NATURAL_KEY: ClassVar[tuple[str, ...]] = ("case_id", "stage")
    TIME_GRAIN: ClassVar[TimeGrain] = TimeGrain.EVENT
    TIME_FIELDS: ClassVar[tuple[str, ...]] = ("start", "end")

    case_id: KeyText
    """Identyfikator przypadku — sprawy przechodzącej przez proces."""

    stage: KeyText
    """Etap procesu."""

    start: EventTimestamp
    """Znacznik początku etapu. Może być pusty.

    Pustego znacznika nie odrzucamy: rekord bez czasu jest faktem o jakości danych
    klienta, który ma ogłosić walidator, a nie cichym powodem do wyrzucenia wiersza.
    Kontrola 8 pomija puste znaczniki przy wyliczaniu zakresu.
    """

    end: EventTimestamp
    """Znacznik końca etapu. Może być pusty.

    Pusty ``end`` jest normalnym stanem etapu jeszcze trwającego. ZOP-XR-PROC-01 pkt 2.4
    wprowadza ``case_status`` i ``case_completed_at`` jako rozszerzenia, które pozwolą
    odróżnić etap trwający od etapu bez danych — do tego czasu rozróżnienia nie ma
    i model go nie udaje.
    """

    unit: OptionalKeyText
    """Jednostka organizacyjna. Może być pusta.

    ``unit`` nie należy do klucza naturalnego PROCESS — karty PROC-01 pkt 2.3 i PROC-02
    pkt 2.3 wskazują jako klucz ``case_id`` i ``stage``. Dopisanie ``unit`` do klucza
    byłoby kluczem, którego żadna karta nie stawia.

    Wymaganie ``unit`` bez dodania go do klucza byłoby jeszcze gorsze: rekord bez
    jednostki zostałby odrzucony przez model i nigdy nie dotarłby do walidatora, więc
    brak jednostki zniknąłby z raportu jakości danych, zamiast się w nim pojawić.
    To ta sama pułapka co w DT-03.

    Skutek braku jest już przewidziany przez karty: brak jednostki ogranicza zakres
    analizy, a ZOP-XR-PROC-01 pkt 12.1 i ZOP-XR-PROC-02 pkt 16.1 mają na to
    ``TEST_PARTIAL`` — „część modułów możliwa do odpowiedzialnego wykonania".
    Wzorzec jest wprost w scenariuszu PROC01-T09: brak ``ready_at`` daje
    ``queue_time = null`` i ``TEST_PARTIAL``, a nie odrzucenie danych.

    To jedyne miejsce, gdzie ``unit`` jest nullowalne — w pozostałych czterech tabelach
    należy do klucza naturalnego i jest wymagane. Pusty napis i napis ze samych spacji
    stają się ``None``, żeby brak miał jedną reprezentację.
    """

    # UWAGA: model nie sprawdza, czy ``end`` jest późniejsze niż ``start``. To kontrola
    # jednowierszowa, ale jej wynikiem ma być status ogłoszony przez validation/, a nie
    # odrzucenie rekordu — rekord odrzucony nigdy nie dotarłby do walidatora.
    # Patrz docs/notatka-techniczna.md wpis DT-03.
