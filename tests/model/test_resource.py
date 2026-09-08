# Sprawdza kontrakt tabeli RESOURCE z ZOP-TECH-01 v0.1 pkt 5.2
# oraz rozstrzygnięcia ZOP-XR-CAP-01 v1.0 rozdz. 4 i 5.
"""Ręczne rekordy testowe dla RESOURCE (ZOP-TECH-01 pkt 9.2).

Najważniejsze testy w tym pliku to te, które sprawdzają, czego model **nie** robi.
Podział ról: model przyjmuje rekord, walidator ogłasza status, test decyduje, co ten
status dla niego znaczy.
"""

import datetime as dt

import pytest
from pydantic import ValidationError

from xray.model import ResourceRecord

POPRAWNY = {
    "date": dt.date(2026, 3, 1),
    "unit": "Dział A",
    "resource": "gabinet 1",
    "available": 160.0,
    "used": 132.0,
    "cost": 24_000.0,
}


def test_rekord_minimalny_przechodzi() -> None:
    rekord = ResourceRecord(**POPRAWNY)
    assert rekord.resource == "gabinet 1"
    assert rekord.available == 160.0
    assert rekord.used == 132.0


def test_wykorzystanie_wieksze_od_dostepnosci_przechodzi() -> None:
    """ZOP-XR-CAP-01 rozdz. 5: „przekroczenie nie jest automatycznie błędem logicznym".

    Rozstrzygnięcie wymaga wiedzy o udokumentowanej dodatkowej zdolności — nadgodzinach,
    dodatkowej zmianie, czasowo uruchomionym zasobie. Tej informacji w jednym wierszu
    nie ma, więc kontrola 7 z pkt 5.3 należy do validation/ i zwraca sygnał z podstawą.
    """
    rekord = ResourceRecord(**{**POPRAWNY, "used": 190.0})
    assert rekord.used == 190.0
    assert rekord.available == 160.0


def test_ujemna_dostepnosc_przechodzi_przez_model() -> None:
    """CAP-01 VAL-04 nadaje temu CRITICAL — ale to walidator ma go ogłosić.

    Rekord odrzucony przez model nigdy nie dotarłby do walidatora, więc status nie
    miałby gdzie powstać. Patrz docs/notatka-techniczna.md wpis DT-03.
    """
    rekord = ResourceRecord(**{**POPRAWNY, "available": -8.0})
    assert rekord.available == -8.0


def test_brak_kosztu_jest_dopuszczalny() -> None:
    """CAP-01 pkt 4.1: „brak cost: miary fizyczne działają; economic_gap = null"."""
    rekord = ResourceRecord(**{**POPRAWNY, "cost": None})
    assert rekord.cost is None
    assert rekord.used == 132.0


def test_pusta_nazwa_zasobu_jest_odrzucana() -> None:
    """resource należy do klucza naturalnego."""
    with pytest.raises(ValidationError):
        ResourceRecord(**{**POPRAWNY, "resource": ""})
