# Implementuje wpis DT-05, wariant A (zatwierdzony 2026-09-14): przeliczenie znaczników
# czasu ze strefą na czas lokalny organizacji; oraz założenie tymczasowe z wpisu B-07.
"""Strefa organizacji i konwersja znaczników czasu.

## Skąd reguły strefy

Strefę wczytujemy **wprost z pakietu ``tzdata``**, a nie przez ``ZoneInfo(nazwa)``.
``ZoneInfo`` najpierw szuka systemowej bazy stref: na Linuksie reguły zmiany czasu
pochodziłyby wtedy z systemu operacyjnego, którego odcisk wykonania nie widzi (DT-22).
``tzdata`` jest zależnością runtime, więc jego wersja należy do odcisku — ta sama wersja
kodu i ta sama wersja ``tzdata`` dają tę samą konwersję na każdym systemie.

## Co wolno, a czego nie

| Wartość | Strefa zadeklarowana | Skutek |
| --- | --- | --- |
| znacznik ze strefą | tak | przeliczenie na naiwny czas lokalny organizacji |
| znacznik bez strefy | dowolnie | bez zmian — to już jest czas lokalny w rozumieniu danych |
| znacznik ze strefą | nie | bez zmian; model go odrzuci jako ``missing_timezone_declaration`` |

Strefy nie zgadujemy: brak deklaracji nie jest „pewnie czas polski".
"""

import datetime as dt
from dataclasses import dataclass
from importlib import resources
from typing import Any
from zoneinfo import ZoneInfo

import pandas as pd


def load_organization_zone(name: str) -> ZoneInfo:
    """Wczytuje strefę organizacji z pakietu ``tzdata``.

    Nieznana albo niepoprawna nazwa podnosi ``ValueError`` — deklaracja, z której nie da się
    przeliczyć żadnej wartości, jest błędem deklaracji, a nie stanem danych.
    """
    czesci = name.split("/")
    if not name or any(czesc in ("", ".", "..") for czesc in czesci):
        raise ValueError(f"niepoprawna nazwa strefy czasowej {name!r}")
    try:
        with resources.files("tzdata").joinpath("zoneinfo", *czesci).open("rb") as plik:
            return ZoneInfo.from_file(plik, key=name)
    except ModuleNotFoundError as blad:
        raise ValueError(
            "brak pakietu tzdata: reguły stref pochodzą wyłącznie z niego (wpis DT-05)"
        ) from blad
    except (OSError, ValueError) as blad:
        raise ValueError(
            f"nieznana strefa czasowa {name!r}: brak jej w pakiecie tzdata "
            f"({type(blad).__name__})"
        ) from blad


@dataclass(frozen=True, slots=True)
class LocalConversion:
    """Wynik przygotowania jednej wartości czasowej."""

    value: Any
    """Wartość do przekazania modelowi: przeliczona albo nietknięta."""

    converted: bool = False
    """Czy wartość była znacznikiem ze strefą i została przeliczona."""

    local_utc_offset: str | None = None
    """Przesunięcie UTC czasu lokalnego — **wyłącznie** dla godziny niejednoznacznej."""


def _offset_text(offset: dt.timedelta) -> str:
    """Przesunięcie w zapisie ``±HH:MM``."""
    minuty = int(offset.total_seconds() // 60)
    znak = "+" if minuty >= 0 else "-"
    minuty = abs(minuty)
    return f"{znak}{minuty // 60:02d}:{minuty % 60:02d}"


def to_organization_local(value: Any, zone: ZoneInfo | None) -> LocalConversion:
    """Przelicza znacznik ze strefą na naiwny czas lokalny organizacji.

    Wartości bez strefy, nieczytelne i przy braku deklaracji wracają **nietknięte** — idą
    dokładnie tą samą drogą co przed wprowadzeniem konwersji, a rozstrzyga o nich model.
    """
    if zone is None:
        return LocalConversion(value)

    kandydat = value
    if isinstance(kandydat, str):
        try:
            kandydat = dt.datetime.fromisoformat(kandydat)
        except ValueError:
            return LocalConversion(value)
    elif isinstance(kandydat, pd.Timestamp):
        kandydat = kandydat.to_pydatetime()
    if not isinstance(kandydat, dt.datetime) or kandydat.tzinfo is None:
        return LocalConversion(value)

    lokalny = kandydat.astimezone(zone)
    # Konwersja DO czasu lokalnego nigdy nie trafia w wiosenną lukę 02:00–02:59, więc różne
    # przesunięcia dla fold=0 i fold=1 znaczą tu wyłącznie godzinę powtórzoną jesienią.
    naiwny = lokalny.replace(tzinfo=None, fold=0)
    niejednoznaczny = (
        naiwny.replace(tzinfo=zone).utcoffset()
        != naiwny.replace(tzinfo=zone, fold=1).utcoffset()
    )
    # ASSUMPTION: B-07 (wariant D, założenie tymczasowe z 2026-09-14, do zatwierdzenia przez
    # Michała). Godzina powtórzona jesienią jest SCALANA w ramce: dwa różne instanty dają
    # tę samą naiwną wartość lokalną, bo kolumna datetime64[ns] (DT-08) nie przechowuje
    # `fold`. Przesunięcie UTC czasu lokalnego wraca do wywołującego i ląduje w raporcie
    # importu (ImportReport.ambiguous_local_times), więc instant pozostaje odtwarzalny.
    return LocalConversion(
        naiwny,
        converted=True,
        local_utc_offset=_offset_text(lokalny.utcoffset()) if niejednoznaczny else None,
    )
