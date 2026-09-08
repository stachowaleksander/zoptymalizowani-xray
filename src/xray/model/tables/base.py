# Implementuje ZOP-TECH-01 v0.1 pkt 5.2 — wspólna podstawa pięciu tabel bazowych.
"""Klasa bazowa tabel i wspólne typy pól.

Trzy rzeczy mieszkają tutaj, żeby nie rozjechały się między pięcioma plikami:

1. konfiguracja modelu (``extra="forbid"``, ``frozen=True``),
2. **wymuszona** deklaracja metadanych tabeli — tabela, która ich nie poda, nie da się
   zaimportować,
3. typy pól z walidacją jednowierszową, wspólne dla wszystkich tabel.

## Reguła, według której działa cała ta warstwa

Model odrzuca wyłącznie to, co czyni rekord bezużytecznym **jako rekord**: wartość
nieprzetłumaczalną na zadeklarowany typ oraz pusty element klucza naturalnego. Nie
odrzuca niczego, co jest **faktem diagnostycznym o danych** — ujemnej kwoty, ujemnego
``used``, ``end`` wcześniejszego niż ``start``, braku wartości.

Powód: walidator ogłasza status, a test deklaruje, co ten status dla niego znaczy
(ZOP-XR-FIN-01 rozdz. 3, ZOP-XR-CAP-01 rozdz. 4). Rekord odrzucony przez model nigdy
nie dotrze do walidatora, więc model, który sam go odrzuca, odbiera decyzję zarówno
walidatorowi, jak i testowi — i robi to bez śladu w wynikach.

Patrz też: docs/notatka-techniczna.md, wpis DT-03.

## Dlaczego walidatory podnoszą PydanticCustomError, a nie ValueError

Odrzucenie musi dać się **zaklasyfikować** wyżej: kontrola 2 (nieprawidłowy format)
i kontrola 3 (brakujące wartości) z pkt 5.3 obie czytają odrzucenia i muszą je rozróżnić.
``PydanticCustomError`` niesie kod (``blank_key``, ``numeric_date``, ``aware_timestamp``,
``not_finite``), który ``ingest/`` mapuje na kategorię odrzucenia. Bez kodu jedyną drogą
byłoby parsowanie polskiego komunikatu — a treść komunikatu nie jest kontraktem
i zmienia się przy każdej poprawce redakcyjnej.
"""

import datetime as dt
import math
from typing import Annotated, Any, ClassVar, get_args

from pydantic import AfterValidator, BaseModel, BeforeValidator, ConfigDict
from pydantic_core import PydanticCustomError

from xray.model.enums import TimeGrain

# Metadane, które musi zadeklarować każda tabela. Brak którejkolwiek ujawniłby się
# dopiero przy kontroli 8 z pkt 5.3, czyli najpóźniej jak się da.
_REQUIRED_METADATA: tuple[str, ...] = (
    "TABLE_NAME",
    "NATURAL_KEY",
    "TIME_GRAIN",
    "TIME_FIELDS",
)


def declared_types(annotation: Any) -> set[type]:
    """Rozwija adnotację pola do zbioru typów prostych.

    Obsługuje sumy typów (``float | None``). Pracujemy na **typach**, a nie na tekstowej
    reprezentacji adnotacji: ``str(datetime.date)`` zawiera podłańcuch „datetime", więc
    dopasowanie tekstowe uznałoby każdą datę za znacznik czasu.

    Funkcja mieszka przy kontrakcie, bo odpowiada na pytanie o kontrakt. Korzystają z niej
    ``ingest/`` (typy kolumn ramki) i ``validation/`` (które pola są liczbowe, a które
    tekstowe) — gdyby każda warstwa miała własną kopię, rozjechałyby się.
    """
    argumenty = get_args(annotation)
    if not argumenty:
        return {annotation} if isinstance(annotation, type) else set()
    return {a for a in argumenty if isinstance(a, type)}


def numeric_fields(table: type["TableRecord"]) -> tuple[str, ...]:
    """Pola liczbowe tabeli, w kolejności kontraktu.

    Używa jej kontrola 5 (wartości podejrzane): bada wszystkie pola liczbowe, a nie
    wybrane po nazwie. Deklarujemy właściwość, nie listę nazw.
    """
    return tuple(
        nazwa
        for nazwa, pole in table.model_fields.items()
        if float in declared_types(pole.annotation)
    )


def text_key_fields(table: type["TableRecord"]) -> tuple[str, ...]:
    """Tekstowe elementy klucza naturalnego, w kolejności kontraktu.

    Używa jej kontrola 6 (niespójne nazwy jednostek). To te pola niosą nazwy nadawane
    przez człowieka — a więc te, w których pojawia się „Dział A" obok „DZIAL_A".
    """
    return tuple(
        nazwa
        for nazwa in table.NATURAL_KEY
        if str in declared_types(table.model_fields[nazwa].annotation)
    )


def _reject_numeric_date(value: Any) -> Any:
    """Nie przyjmujemy daty ani znacznika czasu podanego liczbą.

    Pydantic w trybie łagodnym potraktowałby liczbę jako znacznik uniksowy, przez co
    surowy numer seryjny z arkusza XLSX (np. 45000) zamieniłby się po cichu w datę
    z zupełnie innego roku. Przeliczenie numeru seryjnego należy do ``ingest/``, gdzie
    wiadomo, z jakiego pliku i arkusza pochodzi wartość.
    """
    if isinstance(value, (bool, int, float)):
        raise PydanticCustomError(
            "numeric_date",
            "data podana jako liczba; numer seryjny z arkusza przelicza ingest/, "
            "model przyjmuje datę albo napis w formacie ISO",
        )
    return value


def _require_non_blank(value: str) -> str:
    """Element klucza naturalnego nie może być pusty ani złożony z samych spacji.

    Rekordu bez klucza nie da się przypisać do żadnego zakresu, okresu ani kategorii,
    więc nie mógłby uczestniczyć w audytowalnej agregacji.

    Wartości NIE przycinamy. Różnica między ``"Dział A"`` a ``"Dział A "`` jest dokładnie
    tym, co ma wykryć kontrola 6 z pkt 5.3 (niespójne nazwy jednostek). Ciche przycięcie
    usunęłoby dowód, zanim walidator go zobaczy.
    """
    if not value.strip():
        raise PydanticCustomError(
            "blank_key",
            "wartość pusta lub złożona wyłącznie ze znaków białych",
        )
    return value


def _normalize_missing_number(value: float | None) -> float | None:
    """Sprowadza brak wartości do jednej reprezentacji i odrzuca nieskończoność.

    ``NaN`` z pandas i ``None`` znaczą to samo — brak wartości. Kolumna liczbowa
    w pandas nie przechowa ``None``, więc ta sama pusta komórka wraca raz jako ``NaN``,
    raz jako ``None``, zależnie od drogi wejścia. Utrzymywanie dwóch reprezentacji
    sprawiłoby, że zliczanie braków (kontrola 3) dałoby dwa różne wyniki dla tych samych
    danych.

    To **kanonizacja, nie uzupełnianie braku**. Granicą jest pytanie, czy po operacji
    rekord mówi co innego niż przed. ``NaN`` → ``None`` zmienia zapis: przed i po rekord
    mówi „nie wiem". Zero, średnia, wartość z poprzedniego okresu albo interpolacja
    zmieniają treść: rekord przestaje mówić „nie wiem" i zaczyna mówić „było tyle".
    Tego zakazuje zasada 5.

    **Zero nie jest brakiem i nigdy nie staje się ``None``.** Koszt kategorii w danym
    miesiącu mógł realnie wynieść 0 zł. ZOP-XR-FIN-01 v1.0 rozdz. 6 rozróżnia te
    sytuacje wprost — „CI | R = 0 → null" opisuje przychód **równy zeru**, nie przychód
    nieznany, i jest to inna podstawa niż „mianownik 0 → null" przy braku danych. Obie
    drogi kończą się miarą ``null``, ale z innej podstawy, a podstawa trafia do
    ``validation_notes`` i do danych dla ZOP-CONF-01. Sklejenie zera z brakiem przy
    imporcie zniszczyłoby to rozróżnienie nieodwracalnie.

    ``inf`` nie jest wielkością o sensownej interpretacji — odrzucamy, żeby nie wszedł
    do agregatów.
    """
    if value is None:
        return None
    if math.isnan(value):
        return None
    if math.isinf(value):
        raise PydanticCustomError("not_finite", "wartość jest nieskończonością")
    return value


def _normalize_missing_text(value: str | None) -> str | None:
    """Sprowadza brak tekstu do jednej reprezentacji.

    Ten sam problem co przy liczbach, tylko dla tekstu: CSV z pustą komórką da ``""``,
    a XLSX z pustą komórką da ``None``. Bez kanonizacji zliczanie braków zależałoby od
    tego, którą drogą dane weszły do systemu.

    Rekord przed i po nadal mówi „nie wiem" — zmienia się zapis, nie treść.

    Wartości niepustych NIE przycinamy: ``"Dział A "`` zostaje ze spacją, bo to dowód
    dla kontroli 6 (niespójne nazwy jednostek).
    """
    if value is None:
        return None
    if not value.strip():
        return None
    return value


def _reject_aware_timestamp(value: dt.datetime | None) -> dt.datetime | None:
    """Nie przyjmujemy znacznika czasu ze strefą.

    W jednej kolumnie mogłyby wylądować znaczniki ze strefą i bez, a wtedy pierwsze
    porównanie w kontroli 8 podniosłoby ``TypeError: can't compare offset-naive and
    offset-aware datetimes``. Systemy eksportujące zdarzenia procesowe często podają
    offset, więc nie jest to przypadek teoretyczny.

    Konstrukcja jest ta sama co przy numerze seryjnym daty: model odmawia przyjęcia
    wartości niejednoznacznej, a konwersję świadomą kontekstu pliku robi ``ingest/`` —
    warstwa, która wie, z jakiego systemu wartość pochodzi. Strefa organizacji jest
    jawnym elementem profilu mapowania klienta, a nie założeniem zaszytym w kodzie.

    Patrz docs/notatka-techniczna.md wpis DT-05.
    """
    if value is not None and value.tzinfo is not None:
        raise PydanticCustomError(
            "aware_timestamp",
            "znacznik czasu ze strefą; przeliczenie na czas lokalny organizacji wykonuje "
            "ingest/ na podstawie strefy z profilu mapowania klienta",
        )
    return value


# --- wspólne typy pól ---------------------------------------------------------------

KeyText = Annotated[str, AfterValidator(_require_non_blank)]
"""Tekstowy element klucza naturalnego: wymagany, niepusty, nieprzycinany."""

OptionalKeyText = Annotated[str | None, AfterValidator(_normalize_missing_text)]
"""Tekst spoza klucza naturalnego: może być pusty, brak ma jedną reprezentację.

``""`` i napis ze samych spacji stają się ``None``. Wartości niepustych nie przycinamy.
"""

PeriodDate = Annotated[dt.date, BeforeValidator(_reject_numeric_date)]
"""Etykieta okresu. Granularność podstawowa jest miesięczna (FIN-01 pkt 2.1)."""

EventTimestamp = Annotated[
    dt.datetime | None,
    BeforeValidator(_reject_numeric_date),
    AfterValidator(_reject_aware_timestamp),
]
"""Znacznik czasu zdarzenia bez strefy. Może być pusty — patrz PROCESS.

Znacznik ze strefą jest odrzucany: metodologia nie zna pojęcia strefy czasowej, a dwa
nieporównywalne typy w jednym polu rozsypałyby kontrolę 8. Patrz wpis DT-05.
"""

NumericValue = Annotated[float | None, AfterValidator(_normalize_missing_number)]
"""Wielkość liczbowa: kwota, wolumen, zdolność.

Typ nie niesie jednostki miary. Czym jest jedna jednostka ``volume`` albo ``available``,
rozstrzygają karty przez ``activity_unit`` i ``capacity_unit`` — a oba są otwartymi
kontraktami MASTER v1.2. Model nie może tego założyć za nie.

Znak nie jest ograniczony. Ujemna kwota i ujemne ``used`` przechodzą, bo to walidator ma
ogłosić ich status (wpis B-01, ZOP-XR-CAP-01 VAL-04/VAL-05).
"""


class TableRecord(BaseModel):
    """Wspólna podstawa pięciu tabel bazowych z ZOP-TECH-01 pkt 5.2.

    Każda tabela dziedzicząca musi zadeklarować cztery metadane. Sprawdzenie odbywa się
    przy tworzeniu klasy, czyli przy imporcie modułu — najwcześniej, jak się da.
    """

    model_config = ConfigDict(
        # Nieznana kolumna nigdy nie powinna dojść do modelu: mapping/ decyduje wcześniej,
        # co gdzie trafia, i wypisuje niezmapowane kolumny w raporcie mapowania.
        # extra="forbid" jest siatką bezpieczeństwa, a nie mechanizmem obsługi.
        extra="forbid",
        # Rekord po walidacji jest niezmienny. Ten sam zestaw danych ma dawać ten sam
        # wynik (zasada determinizmu), więc nikt nie „poprawia" rekordu po drodze.
        frozen=True,
    )

    TABLE_NAME: ClassVar[str]
    """Nazwa techniczna tabeli z pkt 5.2, np. ``"COST"``."""

    NATURAL_KEY: ClassVar[tuple[str, ...]]
    """Pola, których komplet jednoznacznie wskazuje rekord.

    Chroni przed podwójnym liczeniem — ZOP-XR-FIN-01 pkt 2.1: „revenue i amount są
    sumowane wyłącznie po poprawnie zdefiniowanych kluczach". Używa go kontrola 4
    (duplikaty) z pkt 5.3.
    """

    TIME_GRAIN: ClassVar[TimeGrain]
    """Czy tabela niesie agregaty okresowe, czy zdarzenia. Patrz wpis A-01."""

    TIME_FIELDS: ClassVar[tuple[str, ...]]
    """Pola niosące czas. Używa ich kontrola 8 (zakres czasowy) z pkt 5.3."""

    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs: Any) -> None:
        """Sprawdza deklarację metadanych w chwili tworzenia klasy tabeli.

        Hook Pydantic uruchamiany po zbudowaniu modelu, więc ``model_fields`` jest już
        kompletne i można porównać klucz naturalny z rzeczywistymi polami.
        """
        super().__pydantic_init_subclass__(**kwargs)

        missing = [name for name in _REQUIRED_METADATA if name not in cls.__dict__]
        if missing:
            raise TypeError(
                f"tabela {cls.__name__} nie deklaruje metadanych: {', '.join(missing)}; "
                "bez nich kontrole 1, 4 i 8 z ZOP-TECH-01 pkt 5.3 nie mają na czym pracować"
            )

        fields = set(cls.model_fields)

        unknown_key = [name for name in cls.NATURAL_KEY if name not in fields]
        if unknown_key:
            raise TypeError(
                f"tabela {cls.__name__}: NATURAL_KEY wskazuje pola spoza kontraktu: "
                f"{', '.join(unknown_key)}"
            )

        unknown_time = [name for name in cls.TIME_FIELDS if name not in fields]
        if unknown_time:
            raise TypeError(
                f"tabela {cls.__name__}: TIME_FIELDS wskazuje pola spoza kontraktu: "
                f"{', '.join(unknown_time)}"
            )

        if not cls.NATURAL_KEY:
            raise TypeError(f"tabela {cls.__name__}: NATURAL_KEY nie może być pusty")
        if not cls.TIME_FIELDS:
            raise TypeError(f"tabela {cls.__name__}: TIME_FIELDS nie może być pusty")
