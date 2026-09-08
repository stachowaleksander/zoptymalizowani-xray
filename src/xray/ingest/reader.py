# Implementuje ZOP-TECH-01 v0.1 pkt 5.1 (import XLSX i CSV) oraz kryterium odbioru 8.1
# (przyjmowanie plików bez ręcznej ingerencji w kod przy każdym uruchomieniu).
"""Odczyt plików źródłowych i bramka kontraktu danych.

``load_table`` zwraca **dwie** rzeczy: zwalidowaną ramkę i raport importu. Dane
w kontrakcie nie niosą śladu pochodzenia w polach; ślad żyje obok, w raporcie.

## Co ta warstwa robi, a czego nie

Robi: odczyt pliku, przeliczenie formatów **zależnych od pliku** (numer seryjny daty
z arkusza XLSX), bramkę kontraktu wiersz po wierszu, nadanie identyfikatorów, raport.

Nie robi: decydowania, która kolumna klienta jest którym polem kontraktu — to
``mapping/``. Nie robi też niczego, co wymaga widoku na cały zbiór (duplikaty, spójność
nazw jednostek, zakres czasowy) — to ``validation/``.
"""

import datetime as dt
import math
from collections.abc import Mapping
from hashlib import blake2b
from pathlib import Path
from typing import Any

import pandas as pd
from pydantic import ValidationError

from xray.ingest.report import ImportReport, Rejection, RejectionCategory, SourceRef
from xray.model import TABLES, get_table
from xray.model.findings.identity import canonical_form
from xray.model.tables.base import declared_types

# Arkusze kalkulacyjne liczą daty jako liczbę dni od 1899-12-30 (system 1900 z błędem
# roku przestępnego, który Excel powiela celowo dla zgodności wstecznej).
_EXCEL_EPOCH = dt.datetime(1899, 12, 30)

# Poza tym zakresem liczba prawie na pewno nie jest datą, tylko kwotą albo wolumenem,
# który trafił do niewłaściwej kolumny. Odpowiada mniej więcej latom 1900–2149.
_EXCEL_SERIAL_MIN = 1
_EXCEL_SERIAL_MAX = 91_000

_CONTENT_DIGEST_BYTES = 16
"""128 bitów skrótu treści. Ta sama racja co przy identyfikatorach rekordów: chodzi
o stabilne rozróżnienie, nie o odporność na atak."""


class LoadResult:
    """Wynik importu jednej tabeli: ramka i raport.

    Zwykła klasa, nie model: ``frame`` jest ramką pandas, której nie chcemy walidować
    ani kopiować przy każdym przekazaniu.
    """

    __slots__ = ("frame", "report")

    def __init__(self, frame: pd.DataFrame, report: ImportReport) -> None:
        self.frame = frame
        self.report = report

    def __repr__(self) -> str:
        return (
            f"LoadResult(tabela={self.report.table_name!r}, "
            f"przyjete={self.report.records_accepted}, "
            f"odrzucone={self.report.records_rejected})"
        )


def _excel_serial_to_datetime(value: float) -> dt.datetime:
    """Przelicza numer seryjny arkusza na znacznik czasu.

    Konwersja należy tutaj, a nie do modelu: tylko ``ingest/`` wie, że wartość przyszła
    z arkusza XLSX. Ta sama liczba w pliku CSV nie jest numerem seryjnym i nie zostanie
    przeliczona — model ją odrzuci, co jest poprawnym wynikiem.
    """
    return _EXCEL_EPOCH + dt.timedelta(days=float(value))


def _prepare_value(value: Any, *, field_type: str, from_xlsx: bool) -> Any:
    """Przygotowuje pojedynczą wartość do przekazania bramce kontraktu.

    Zamienia braki pandas na ``None`` i — wyłącznie dla źródeł XLSX — przelicza numery
    seryjne w polach czasowych. Nie robi nic poza tym: reszta rozstrzygnięć należy do
    kontraktu.
    """
    if value is None:
        return None
    if isinstance(value, float) and math.isnan(value):
        return None
    if value is pd.NaT:
        return None

    if field_type in ("date", "datetime"):
        if isinstance(value, pd.Timestamp):
            value = value.to_pydatetime()
        if from_xlsx and isinstance(value, (int, float)) and not isinstance(value, bool):
            if _EXCEL_SERIAL_MIN <= value <= _EXCEL_SERIAL_MAX:
                value = _excel_serial_to_datetime(value)
        if field_type == "date" and isinstance(value, dt.datetime):
            value = value.date()
    return value


def _field_types(table_name: str) -> dict[str, str]:
    """Zwraca rodzaj każdego pola kontraktu: ``date``, ``datetime`` lub ``other``.

    Rozpoznajemy po adnotacji, a nie po nazwie pola — nazwa ``date`` w PLAN i brak takiej
    nazwy w PROCESS pokazują, że nazwa nie jest wiarygodną wskazówką.

    Kolejność sprawdzania ma znaczenie: ``datetime.datetime`` dziedziczy po
    ``datetime.date``, więc znacznik czasu trzeba rozpoznać pierwszy.
    """
    rodzaje: dict[str, str] = {}
    for nazwa, pole in TABLES[table_name].model_fields.items():
        typy = declared_types(pole.annotation)
        if dt.datetime in typy:
            rodzaje[nazwa] = "datetime"
        elif dt.date in typy:
            rodzaje[nazwa] = "date"
        else:
            rodzaje[nazwa] = "other"
    return rodzaje


def _frame_dtypes(table_name: str) -> dict[str, str]:
    """Zwraca typ kolumny ramki dla każdego pola kontraktu.

    Typ bierze się z **kontraktu**, a nie z tego, jakie wiersze akurat trafiły do pliku.
    Bez tego dtype zależałby od próbki danych: kolumna ``end`` z samymi brakami byłaby
    obiektowa, a z jednym znacznikiem — czasowa, i brak raz byłby ``None``, raz ``NaT``.
    Znaczyłoby to, że sposób sprawdzania braku zależy od zawartości pliku.

    ``date`` zostaje kolumną obiektową z ``datetime.date``: pandas nie ma typu daty bez
    czasu, a zamiana na znacznik czasu dokładałaby północ, której w danych nie było.
    Pola ``date`` należą w czterech tabelach do klucza naturalnego, więc i tak nie mogą
    być puste.

    Patrz docs/notatka-techniczna.md wpis DT-08.
    """
    typy: dict[str, str] = {}
    for nazwa, rodzaj in _field_types(table_name).items():
        if rodzaj == "datetime":
            typy[nazwa] = "datetime64[ns]"
        elif rodzaj == "date":
            typy[nazwa] = "object"
        else:
            deklarowane = declared_types(
                TABLES[table_name].model_fields[nazwa].annotation
            )
            typy[nazwa] = "float64" if float in deklarowane else "object"
    return typy


def _row_id(table_name: str, source: SourceRef, file_row: int) -> str:
    """Buduje stabilny identyfikator wiersza.

    Identyfikator jest deterministyczny w sensie zasady 3: nie zależy od kolejności
    iteracji ani od czasu wykonania, tylko od źródła i numeru wiersza w pliku. Te same
    dane wczytane tym samym kodem dają te same identyfikatory.

    Żyje jako **indeks ramki**, a nie jako pole modelu — inaczej kontrakt danych
    wiedziałby, z jakiego pliku przyszła liczba.
    """
    return f"{table_name}:{source.source_id}:{file_row:06d}"


def _read_raw(path: Path, sheet: str | None) -> tuple[pd.DataFrame, bool]:
    """Odczytuje surową ramkę z pliku. Zwraca ramkę i informację, czy źródłem jest XLSX."""
    suffix = path.suffix.lower()
    if suffix in (".xlsx", ".xlsm"):
        # dtype=object: nie pozwalamy pandas zgadywać typów. Rozstrzyga kontrakt,
        # a nie heurystyka biblioteki.
        frame = pd.read_excel(path, sheet_name=sheet or 0, dtype=object)
        return frame, True
    if suffix == ".csv":
        frame = pd.read_csv(path, dtype=object, keep_default_na=True)
        return frame, False
    raise ValueError(
        f"nieobsługiwane rozszerzenie {path.suffix!r}; ZOP-TECH-01 pkt 5.1 obejmuje "
        "XLSX i CSV"
    )


def load_table(
    path: str | Path,
    table_name: str,
    *,
    dataset_id: str,
    sheet: str | None = None,
    column_map: Mapping[str, str] | None = None,
) -> LoadResult:
    """Wczytuje jedną tabelę kontraktu z jednego pliku.

    ``dataset_id`` jest **wymagany**: jeden profil mapowania = jeden klient = jeden zbiór
    danych. Bez niego dwóch klientów przysyłających plik o nazwie ``koszty.csv``
    dostałoby te same identyfikatory wierszy, a w magazynie obejmującym więcej niż jeden
    zbiór ślad wskazywałby nie ten plik. Wartość jest zadeklarowana, a nie wyprowadzana
    ze ścieżki ani z nazwy pliku — wyprowadzana byłaby zgadywana.

    ``column_map`` odwzorowuje **pole kontraktu → kolumnę klienta** — w tę samą stronę,
    co profil mapowania. Kierunek nie jest kwestią gustu: przy zapisie odwrotnym jedna
    kolumna klienta nie mogłaby zasilić dwóch pól kontraktu (kolizja klucza), a to jest
    przypadek dopuszczony decyzją D-C. Zapis w tę stronę czyni natomiast trudnym do
    wyrażenia przypadek zakazany — dwie kolumny na jedno pole.

    Docelowo mapę dostarcza ``mapping/``; przy jej braku zakładamy, że nazwy kolumn już
    odpowiadają polom kontraktu — wygoda dla danych syntetycznych, nie reguła dla danych
    klienta.

    Kolumny spoza mapy są pomijane i wypisane w raporcie jako ``dropped_columns``. To
    zapis tego, co import zrobił; ocena mapowania należy do ``mapping/``.
    """
    path = Path(path)
    tabela = get_table(table_name)
    surowa, from_xlsx = _read_raw(path, sheet)

    source = SourceRef.create(
        dataset_id=dataset_id,
        source_file=path.name,
        source_path=str(path),
        source_sheet=sheet,
        header_row=1,
    )

    # Mapa idzie pole kontraktu → kolumna klienta. Jedno pole ma najwyżej jedną kolumnę
    # (zakaz D-B wynika z samego kształtu), jedna kolumna może zasilić kilka pól (D-C).
    mapa = (
        dict(column_map)
        if column_map
        else {pole: pole for pole in tabela.model_fields if pole in surowa.columns}
    )
    pola_kontraktu = set(tabela.model_fields)
    uzyte = {
        pole: kolumna
        for pole, kolumna in mapa.items()
        if pole in pola_kontraktu and kolumna in surowa.columns
    }
    wykorzystane_kolumny = set(uzyte.values())
    pominiete = tuple(k for k in surowa.columns if k not in wykorzystane_kolumny)

    # Pole kontraktu, dla którego w pliku nie ma kolumny. Spoza klucza — materializujemy
    # jako w całości puste (wpis B-06). Z klucza — nie materializujemy: rekordu bez klucza
    # nie da się przypisać do zakresu ani okresu, więc wiersz ma zostać odrzucony.
    zmaterializowane = tuple(
        pole
        for pole in tabela.model_fields
        if pole not in uzyte and pole not in tabela.NATURAL_KEY
    )
    # Dopełnienie powyższego: pola klucza bez kolumny. Razem opisują komplet pól
    # kontraktu, dla których w pliku nie było kolumny — bez tego „brak kolumny unit"
    # byłby nie do odróżnienia od „kolumna unit obecna, ale pusta" (wpis B-06).
    brak_kolumn_klucza = tuple(
        pole for pole in tabela.NATURAL_KEY if pole not in uzyte
    )
    # Kolejność wg kontraktu, nie wg iteracji po mapie.
    zastosowane = tuple(
        (pole, uzyte[pole]) for pole in tabela.model_fields if pole in uzyte
    )

    rodzaje = _field_types(table_name)
    przyjete: list[dict[str, Any]] = []
    identyfikatory: list[str] = []
    odrzucenia: list[Rejection] = []

    # Skrót treści liczymy przyrostowo, w tej samej pętli, w której rekord i tak
    # przechodzi przez bramkę kontraktu. Drugie przejście po danych byłoby pracą
    # wykonaną tylko dlatego, że policzylibyśmy skrót w niewłaściwym miejscu.
    # Kolejność jest kolejnością wierszy w pliku, czyli rosnącą kolejnością row_id —
    # nie zależy od kolejności iteracji po żadnym słowniku. Sam row_id do skrótu nie
    # wchodzi: patrz komentarz przy update.
    skrot = blake2b(digest_size=_CONTENT_DIGEST_BYTES)

    for pozycja, (_, wiersz) in enumerate(surowa.iterrows()):
        # Wiersz 1 to nagłówek, więc pierwszy wiersz danych ma w pliku numer 2.
        # Ten numer klient znajdzie w swoim arkuszu — pozycja w ramce nie.
        numer_w_pliku = source.header_row + 1 + pozycja

        dane = {
            pole: _prepare_value(
                wiersz[kolumna], field_type=rodzaje[pole], from_xlsx=from_xlsx
            )
            for pole, kolumna in uzyte.items()
        }
        dane.update({pole: None for pole in zmaterializowane})
        try:
            rekord = tabela(**dane)
        except ValidationError as blad:
            odrzucenia.append(
                Rejection(
                    file_row=numer_w_pliku,
                    reason=_opisz_blad(blad),
                    category=_kategoria_bledu(blad),
                    fields=_pola_bledu(blad),
                )
            )
            continue

        row_id = _row_id(table_name, source, numer_w_pliku)
        dane_rekordu = rekord.model_dump()
        przyjete.append(dane_rekordu)
        identyfikatory.append(row_id)
        # Do skrótu wchodzi WYŁĄCZNIE treść rekordu. row_id niesie tożsamość źródła
        # (nazwę pliku), więc ten sam zbiór zapisany jako CSV i jako XLSX dałby dwa
        # różne skróty — a zmiana formatu zapisu nie jest zmianą danych.
        skrot.update(canonical_form(dane_rekordu).encode("utf-8"))

    # Ramkę budujemy kolumna po kolumnie z jawnym typem, a nie z listy słowników.
    # Konstruktor pandas zgadywałby typ z zawartości: kolumna dat stałaby się czasowa
    # i `datetime.date` z kontraktu zamieniłby się w `Timestamp` z dorobioną północą.
    # Pusta ramka nadal musi mieć kolumny kontraktu, żeby validation/ i engine/ nie
    # musiały rozróżniać „brak danych" od „inna struktura".
    indeks = pd.Index(identyfikatory, name="row_id")
    typy = _frame_dtypes(table_name)
    ramka = pd.DataFrame(
        {
            pole: pd.Series(
                [rekord[pole] for rekord in przyjete], index=indeks, dtype=typy[pole]
            )
            for pole in tabela.model_fields
        },
        index=indeks,
    )

    liczba_wierszy = len(surowa)
    raport = ImportReport(
        table_name=table_name,
        source=source,
        source_row_range=(
            (source.header_row + 1, source.header_row + liczba_wierszy)
            if liczba_wierszy
            else None
        ),
        records_accepted=len(przyjete),
        records_rejected=len(odrzucenia),
        content_digest=skrot.hexdigest(),
        rejections=tuple(odrzucenia),
        row_id_range=(
            (identyfikatory[0], identyfikatory[-1]) if identyfikatory else None
        ),
        dropped_columns=pominiete,
        applied_columns=zastosowane,
        materialized_empty=zmaterializowane,
        missing_key_columns=brak_kolumn_klucza,
    )
    return LoadResult(ramka, raport)


# Kody błędów Pydantic i naszych walidatorów kontraktu → kategoria odrzucenia.
# Kody pochodzą z model/tables/base.py oraz z rdzenia Pydantic; klasyfikujemy po kodzie,
# nigdy po treści komunikatu.
_KATEGORIE_BLEDOW: dict[str, RejectionCategory] = {
    "missing": RejectionCategory.MISSING_VALUE,
    "blank_key": RejectionCategory.MISSING_VALUE,
    "numeric_date": RejectionCategory.INVALID_FORMAT,
    "aware_timestamp": RejectionCategory.INVALID_FORMAT,
    "not_finite": RejectionCategory.INVALID_FORMAT,
    "extra_forbidden": RejectionCategory.OUT_OF_CONTRACT,
}


def _kategoria_bledu(blad: ValidationError) -> RejectionCategory:
    """Rozpoznaje rodzaj odrzucenia po kodach błędów.

    Gdy wiersz ma kilka problemów naraz, pierwszeństwo ma brak wartości: klient najpierw
    musi mieć co poprawiać.

    Rozstrzygnięcie po **wartości wejściowej**, a nie po samym kodzie: pusta komórka
    w polu, które nie dopuszcza pustej wartości, daje kod typu (``string_type``,
    ``date_type``), bo Pydantic widzi ``None`` tam, gdzie oczekuje napisu. To nadal jest
    brak wartości, a nie nieprawidłowy format — i klient ma dostać „uzupełnij", a nie
    „popraw zapis". Pozostałe kody parsowania i typu oznaczają format.
    """
    kategorie = set()
    for szczegol in blad.errors():
        kod = str(szczegol.get("type", ""))
        if kod in _KATEGORIE_BLEDOW:
            kategorie.add(_KATEGORIE_BLEDOW[kod])
        elif szczegol.get("input", "") is None:
            kategorie.add(RejectionCategory.MISSING_VALUE)
        elif kod.endswith(("_parsing", "_type")):
            kategorie.add(RejectionCategory.INVALID_FORMAT)
        else:
            kategorie.add(RejectionCategory.OTHER)
    for pierwszenstwo in (
        RejectionCategory.MISSING_VALUE,
        RejectionCategory.INVALID_FORMAT,
        RejectionCategory.OUT_OF_CONTRACT,
    ):
        if pierwszenstwo in kategorie:
            return pierwszenstwo
    return RejectionCategory.OTHER


def _pola_bledu(blad: ValidationError) -> tuple[str, ...]:
    """Wyciąga nazwy pól, których dotyczy błąd walidacji."""
    pola = []
    for szczegol in blad.errors():
        lokalizacja = szczegol.get("loc") or ()
        if lokalizacja:
            pola.append(str(lokalizacja[0]))
    return tuple(dict.fromkeys(pola))


def _opisz_blad(blad: ValidationError) -> str:
    """Zamienia błąd walidacji na komunikat dla człowieka.

    Kryterium odbioru 8.4 wymaga, żeby komunikat wskazywał problem i jego miejsce.
    Miejsce niesie ``Rejection.file_row``; tutaj powstaje opis problemu.
    """
    czesci = []
    for szczegol in blad.errors():
        lokalizacja = szczegol.get("loc") or ()
        pole = str(lokalizacja[0]) if lokalizacja else "rekord"
        czesci.append(f"{pole}: {szczegol.get('msg', 'wartość niezgodna z kontraktem')}")
    return "; ".join(czesci)
