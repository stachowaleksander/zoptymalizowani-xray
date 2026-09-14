# Implementuje ZOP-TECH-01 v0.1 kryterium odbioru 8.4 (komunikat wskazuje problem
# i jego miejsce) oraz zasadę 4 z CLAUDE.md (audytowalność).
"""Raport importu — ślad pochodzenia rekordu.

Model danych nie niesie ani pliku, ani arkusza, ani numeru wiersza. I nie może: poniżej
kontraktu danych nic nie wie, z jakiego pliku przyszła liczba. Ślad pochodzenia żyje
więc **obok** kontraktu, w tym raporcie.

Droga śladu: liczba w FINDINGS → identyfikator wiersza → raport importu → konkretny
wiersz w pliku klienta.
"""

import datetime as dt
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, computed_field

from xray.model.findings.identity import IDENTITY_ALGORITHM_VERSION, compute_id

_SOURCE_PREFIX = "SRC"


class SourceRef(BaseModel):
    """Opis źródła, z którego przyszły dane.

    ``source_id`` jest wyliczany deterministycznie z opisu źródła — ten sam zbiór danych,
    nazwa pliku i arkusz dają zawsze ten sam identyfikator, niezależnie od tego, kiedy
    i na jakiej maszynie odbył się import (zasada 3).

    Do skrótu wchodzi **nazwa** pliku, a nie pełna ścieżka: ten sam plik wczytany
    z innego katalogu jest tym samym źródłem, a ścieżka bezwzględna zależy od maszyny.
    Pełna ścieżka pozostaje zapisana w ``source_path`` dla audytu.

    Do skrótu wchodzi natomiast ``dataset_id``. Bez niego dwóch klientów przysyłających
    plik o nazwie ``koszty.csv`` dostałoby ten sam ``source_id``, a więc te same
    identyfikatory wierszy dla tych samych numerów — i w magazynie obejmującym więcej niż
    jeden zbiór ślad wskazywałby nie ten plik.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    source_id: str
    """Krótki, deterministyczny identyfikator źródła."""

    dataset_id: str
    """Identyfikator zbioru danych: jeden profil mapowania = jeden klient = jeden zbiór.

    Wartość jest **zadeklarowana**, a nie wyprowadzana ze ścieżki katalogu ani z nazwy
    pliku — wyprowadzana byłaby zgadywana. Docelowo pochodzi z profilu mapowania.
    """

    source_file: str
    """Nazwa pliku źródłowego."""

    source_path: str
    """Ścieżka, z której faktycznie wczytano plik. Do audytu, nie do tożsamości."""

    source_sheet: str | None = None
    """Arkusz (XLSX) albo ``None`` dla CSV."""

    header_row: int
    """Numer wiersza nagłówka w pliku, licząc od 1."""

    identity_algorithm_version: str = IDENTITY_ALGORITHM_VERSION
    """Wersja algorytmu, którym policzono ``source_id``. Składnik tożsamości."""

    @classmethod
    def create(
        cls,
        *,
        dataset_id: str,
        source_file: str,
        source_path: str,
        source_sheet: str | None = None,
        header_row: int = 1,
        identity_algorithm_version: str = IDENTITY_ALGORITHM_VERSION,
    ) -> "SourceRef":
        """Buduje opis źródła z wyliczonym identyfikatorem."""
        if not dataset_id.strip():
            raise ValueError(
                "dataset_id nie może być pusty; bez niego dwa zbiory danych o plikach "
                "tej samej nazwy skleiłyby identyfikatory wierszy"
            )
        source_id = compute_id(
            _SOURCE_PREFIX,
            {
                "dataset_id": dataset_id,
                "source_file": source_file,
                "source_sheet": source_sheet,
                "header_row": header_row,
                "identity_algorithm_version": identity_algorithm_version,
            },
            algorithm_version=identity_algorithm_version,
        )
        return cls(
            source_id=source_id,
            dataset_id=dataset_id,
            source_file=source_file,
            source_path=source_path,
            source_sheet=source_sheet,
            header_row=header_row,
            identity_algorithm_version=identity_algorithm_version,
        )


class RejectionCategory(StrEnum):
    """Dlaczego wiersz nie przeszedł bramki kontraktu.

    Katalog istnieje, bo odrzucenia czytają dwie różne kontrole z ZOP-TECH-01 pkt 5.3:
    kontrola 2 (nieprawidłowy format) i kontrola 3 (brakujące wartości). Bez kategorii
    jedyną drogą byłoby parsowanie polskiego komunikatu, a treść komunikatu nie jest
    kontraktem.

    Kategoria wynika z **kodu błędu** podniesionego przez walidator kontraktu, a nie
    z jego treści. Od chwili, gdy zestawienie odrzuceń wchodzi do tożsamości przebiegu,
    każda wartość tego katalogu jest częścią kontraktu, a nie opisem.

    Wiersz z kilkoma wadami dostaje jedną kategorię: wygrywa wada bardziej podstawowa —
    ta, która uniemożliwia stwierdzenie następnej. Kryterium i kolejność:
    ``xray.ingest.reader._PIERWSZENSTWO``.
    """

    MISSING_VALUE = "missing_value"
    """Pole wymagane nieobecne albo puste w elemencie klucza naturalnego.

    Rekord w kontrakcie **nie istnieje** — to inny fakt niż pusta komórka w wierszu
    przyjętym i nie wolno go z nią sumować.
    """

    INVALID_FORMAT = "invalid_format"
    """Wartość nieprzetłumaczalna na zadeklarowany typ albo niejednoznaczna:
    tekst w polu liczbowym, data podana liczbą, nieskończoność, znacznik czasu ze strefą,
    którego nie dało się przeliczyć mimo zadeklarowanej strefy."""

    MISSING_TIMEZONE_DECLARATION = "missing_timezone_declaration"
    """Znacznik czasu ze strefą, a profil nie zadeklarował strefy organizacji.

    Osobna kategoria, a nie wspólny worek z błędami parsowania: wartość jest poprawnym
    zapisem, brakuje deklaracji, która pozwoliłaby ją przeliczyć (wpis DT-05). Rozmowa
    z klientem jest inna — „uzupełnij profil", a nie „popraw dane".
    """

    OUT_OF_CONTRACT = "out_of_contract"
    """Wiersz niósł pole spoza kontraktu. Nie powinno się zdarzyć, bo ``mapping/``
    decyduje wcześniej — to siatka bezpieczeństwa."""

    OTHER = "other"
    """Pozostałe. Powód zostaje w ``reason`` wraz z kodem błędu."""


class Rejection(BaseModel):
    """Pojedynczy wiersz odrzucony przez bramkę kontraktu.

    Rekord odrzucony **nie znika po cichu**. Odrzucenie jest informacją dla klienta
    o jakości jego danych, a nie awarią importu.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    file_row: int
    """Numer wiersza w pliku źródłowym, licząc od 1 wraz z nagłówkiem.

    To jest „miejsce problemu" z kryterium odbioru 8.4 — numer, który klient znajdzie
    w swoim arkuszu, a nie pozycja w ramce.
    """

    reason: str
    """Powód odrzucenia, w postaci nadającej się do pokazania człowiekowi."""

    category: RejectionCategory = RejectionCategory.OTHER
    """Maszynowo rozpoznawalny rodzaj odrzucenia. Czytają go kontrole 2 i 3."""

    fields: tuple[str, ...] = ()
    """Pola kontraktu, których dotyczy problem."""


class RejectionCount(BaseModel):
    """Liczność odrzuceń jednego rodzaju: kategoria i dotknięte pola.

    Semantyczne zestawienie odrzuceń wchodzi **jawnie** do tożsamości przebiegu
    (``xray.store.runs.RunRef``) — jawnie, a nie jako skrót, bo przy sprzeczności dwóch
    przebiegów ma dać się odczytać, czym się różniły.

    Czego tu świadomie nie ma:

    - ``reason`` — proza dla człowieka; poprawka literówki w komunikacie zmieniłaby
      ``run_id`` przy tych samych danych,
    - ``file_row`` — pozycja wiersza nie jest semantyką odrzucenia, a dziś w dodatku nie
      wskazuje fizycznej linii CSV (docs/analiza-wplywu-BIND-01.md, pozycja Z-3).
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    category: RejectionCategory
    """Kategoria odrzucenia. Od chwili, gdy wchodzi do tożsamości przebiegu, jest częścią
    kontraktu, a nie opisem."""

    fields: tuple[str, ...]
    """Dotknięte pola kontraktu, posortowane: kolejność, w jakiej walidator zgłosił błędy,
    nie jest cechą danych."""

    count: int
    """Ile wierszy odpadło z tego powodu na tych polach."""


class AmbiguousLocalTime(BaseModel):
    """Znacznik, który po przeliczeniu trafił w godzinę powtórzoną przy zmianie czasu.

    # ASSUMPTION: B-07 (wariant D, założenie tymczasowe z 2026-09-14). W ramce oba instanty
    # godziny powtórzonej mają tę samą naiwną wartość lokalną; rozróżnienie żyje tutaj,
    # obok kontraktu — tak jak pochodzenie rekordu.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    field: str
    """Pole kontraktu, np. ``start``."""

    file_row: int
    """Numer wiersza w pliku, jak w ``Rejection.file_row``."""

    row_id: str | None
    """Identyfikator wiersza w ramce albo ``None``, gdy wiersz odrzucono z innego powodu."""

    source_value: str
    """Wartość tak, jak przyszła z pliku — z pierwotnym zapisem przesunięcia."""

    local_value: dt.datetime
    """Naiwny czas lokalny, który trafił do ramki. Dla obu instantów ten sam."""

    local_utc_offset: str
    """Przesunięcie UTC czasu lokalnego w tym instancie, np. ``+02:00`` albo ``+01:00``.

    Z nim instant jest odtwarzalny: ``local_value - local_utc_offset`` daje czas UTC.
    """


class ImportReport(BaseModel):
    """Wynik importu jednej tabeli z jednego źródła.

    Zwracany zawsze razem ze zwalidowaną ramką — import produkuje **dwie** rzeczy,
    nie jedną.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    table_name: str
    """Nazwa tabeli kontraktu, do której trafiły dane."""

    source: SourceRef

    imported_at: dt.datetime | None = None
    """Kiedy wykonano import. Pole audytowe i **celowo nieużywane w tożsamości**:
    gdyby weszło do identyfikatorów, dwa przebiegi na tych samych danych dałyby różne
    wyniki, co łamie zasadę 3."""

    source_row_range: tuple[int, int] | None = None
    """Zakres odczytanych wierszy pliku (pierwszy, ostatni), licząc od 1.
    ``None``, gdy plik nie zawierał żadnego wiersza danych."""

    records_accepted: int = 0
    records_rejected: int = 0

    rejections: tuple[Rejection, ...] = ()
    """Dla każdego odrzucenia: numer wiersza i powód."""

    row_id_range: tuple[str, str] | None = None
    """Pierwszy i ostatni identyfikator nadany rekordom przyjętym."""

    content_digest: str
    """Skrót kanonicznej treści przyjętych rekordów.

    **Liczony przyrostowo w trakcie importu**, gdy rekord i tak przechodzi przez bramkę
    kontraktu — bez drugiego przejścia po danych. Przy milionie wierszy drogą częścią jest
    walidacja rekord po rekordzie, a nie skrót; ta praca jest już wykonana.

    Liczony z **treści rekordów**, nie z bajtów pliku. Ten sam zbiór w CSV i XLSX daje
    identyczną ramkę, więc musi dać ten sam skrót — zmiana formatu zapisu nie jest zmianą
    danych. Skutek uboczny jest pożądany: przeformatowanie pliku bez zmiany wartości nie
    tworzy nowego przebiegu, a zapis pozostaje idempotentny.

    Skrót jest faktem o tym, co wczytano, więc mieszka w raporcie importu, a nie
    w magazynie. Wchodzi do tożsamości przebiegu (``run_id``).
    """

    dropped_columns: tuple[str, ...] = ()
    """Kolumny obecne w pliku, których import nie przekazał do kontraktu.

    To zapis tego, co ``ingest/`` faktycznie zrobił — a nie ocena mapowania. Decyzja,
    która kolumna jest którym polem, i raport kolumn niezmapowanych należą do
    ``mapping/``.
    """

    applied_columns: tuple[tuple[str, str], ...] = ()
    """Faktycznie użyte przypisania jako pary ``(pole kontraktu, kolumna klienta)``.

    Nie to, co profil deklarował, tylko to, co import **wykonał** na tym pliku.
    Uporządkowane wg kolejności pól w kontrakcie, żeby zapis nie zależał od kolejności
    iteracji.

    Dwa zastosowania:

    1. wchodzi do skrótu znaczącej treści profilu, a przez to do ``run_id``,
    2. pozwala rozpoznać, że dwa pola kontraktu pochodzą z **jednej** kolumny klienta —
       a wtedy kontrola, dla której sygnałem jest różnica między tymi polami, nie może
       tej różnicy zobaczyć i nie wolno jej wypisać PASS.
    """

    missing_key_columns: tuple[str, ...] = ()
    """Elementy klucza naturalnego, dla których w pliku **nie było kolumny**.

    Dopełnienie ``materialized_empty``: tamto obejmuje pola spoza klucza, to — pola
    klucza. Razem opisują komplet pól kontraktu bez kolumny w pliku.

    Bez tego pola nie dałoby się odróżnić **braku kolumny** ``unit`` od kolumny ``unit``
    **obecnej, ale pustej**: obie dają odrzucenie z kategorią ``missing_value`` i tym samym
    polem. B-06 każe uczynić to rozróżnienie widocznym, a nie domyślanym.

    Skutek szerszy niż wygoda: status kontroli 1 wywodzi się z raportu importu, więc
    kontrola działa **także bez profilu** (przy mapowaniu tożsamościowym). Raport mapowania
    wzbogaca podstawę, ale nie warunkuje jej istnienia.
    """

    materialized_empty: tuple[str, ...] = ()
    """Pola kontraktu, dla których w pliku nie było kolumny i które wypełniono pustką.

    ``None`` oznacza tu **nieobecność kolumny**, a nie wartość zastępczą wstawioną
    w miejsce danych — zasada 5 nie jest naruszona. Ale rozróżnienie musi być widoczne:
    bez tego wpisu „100% braków w polu ``cost``" wyglądałoby identycznie jak „kolumna
    była, ale pusta", a to dwie różne rozmowy z klientem.

    Materializujemy wyłącznie pola **spoza** klucza naturalnego. Brak kolumny klucza
    znaczy, że rekordu nie da się przypisać do zakresu ani okresu — takie wiersze są
    odrzucane, a nie uzupełniane.

    # DECYZJA (Michał, 2026-09-08), wpis B-06: strukturalnie wymagany jest wyłącznie
    # element klucza naturalnego. Materializacja pozostałych pól jest stanem danych,
    # a nie wadą tabeli — o ciężarze braku orzeka test, który tego pola potrzebuje.
    """

    organization_timezone: str | None = None
    """Strefa organizacji, według której przeliczono znaczniki ze strefą (wpis DT-05).

    ``None`` znaczy „nie zadeklarowano": znaczniki ze strefą są wtedy odrzucane z kategorią
    ``missing_timezone_declaration``, a nie przeliczane według zgadniętej strefy.
    """

    timestamps_converted: int
    """Ile wartości czasowych przeliczono ze strefy na czas lokalny organizacji, licząc
    także wiersze odrzucone później z innego powodu.

    Bez wartości domyślnej celowo: raport, który jej nie poda, nie powstanie.
    """

    ambiguous_local_times: tuple[AmbiguousLocalTime, ...]
    """Znaczniki, które po przeliczeniu trafiły w godzinę powtórzoną jesienią (B-07).

    Bez wartości domyślnej celowo: brak pola znaczyłby jednocześnie „nie było"
    i „nie sprawdzaliśmy".
    """

    @computed_field
    @property
    def ambiguous_local_time_count(self) -> int:
        """Licznik godzin niejednoznacznych — ogłaszany zawsze, także gdy wynosi 0."""
        return len(self.ambiguous_local_times)

    @property
    def fields_without_column(self) -> tuple[str, ...]:
        """Komplet pól kontraktu, dla których w pliku **nie było kolumny**.

        Unia ``missing_key_columns`` i ``materialized_empty``, posortowana. Istnieje po to,
        żeby dwaj odbiorcy tego samego faktu czytali go z jednego miejsca:

        - kontrola 1 potrzebuje **rozdziału** obu krotek, bo z niego wywodzi swoje dwa
          stany (klucz → CRITICAL, reszta → PASS z obserwacją),
        - bramka gotowości testu potrzebuje **unii**, bo dla niej liczy się jedno pytanie:
          czy pole z ``required_by_test`` w ogóle miało kolumnę.

        Gdyby unię składał sobie każdy odbiorca osobno, dołożenie trzeciej kategorii pól
        bez kolumny wymagałoby poprawki w każdym z nich.
        """
        return tuple(sorted(set(self.missing_key_columns) | set(self.materialized_empty)))

    @property
    def rows_read(self) -> int:
        """Liczba wierszy danych odczytanych z pliku."""
        return self.records_accepted + self.records_rejected

    @property
    def rejection_summary(self) -> tuple[RejectionCount, ...]:
        """Semantyczne zestawienie odrzuceń: ile, z jakiego powodu, na jakich polach.

        Porządek po kategorii i polach, żeby zapis nie zależał od kolejności wierszy
        w pliku. Wchodzi jawnie do tożsamości przebiegu — patrz ``RejectionCount``.
        """
        liczniki: dict[tuple[RejectionCategory, tuple[str, ...]], int] = {}
        for odrzucenie in self.rejections:
            klucz = (odrzucenie.category, tuple(sorted(set(odrzucenie.fields))))
            liczniki[klucz] = liczniki.get(klucz, 0) + 1
        return tuple(
            RejectionCount(category=kategoria, fields=pola, count=liczba)
            for (kategoria, pola), liczba in sorted(
                liczniki.items(), key=lambda wpis: (wpis[0][0].value, wpis[0][1])
            )
        )
