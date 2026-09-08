# Sprawdza kontrakt tabeli PLAN z ZOP-TECH-01 v0.1 pkt 5.2.
"""Ręczne rekordy testowe dla PLAN (ZOP-TECH-01 pkt 9.2).

PLAN jest we wszystkich kartach tabelą opcjonalną, ale opcjonalność dotyczy tabeli,
nie pól: dostarczony rekord musi spełniać kontrakt.
"""

import datetime as dt

import pytest
from pydantic import ValidationError

from xray.model import PlanRecord

POPRAWNY = {
    "date": dt.date(2026, 3, 1),
    "unit": "Dział A",
    "metric": "koszt_calkowity",
    "target": 250_000.0,
}


def test_rekord_minimalny_przechodzi() -> None:
    rekord = PlanRecord(**POPRAWNY)
    assert rekord.metric == "koszt_calkowity"
    assert rekord.target == 250_000.0


def test_pusta_wartosc_docelowa_jest_dopuszczalna() -> None:
    """Plan bez wartości to fakt o danych, który ogłasza validation/."""
    rekord = PlanRecord(**{**POPRAWNY, "target": None})
    assert rekord.target is None


def test_pusta_nazwa_wskaznika_jest_odrzucana() -> None:
    """metric należy do klucza naturalnego."""
    with pytest.raises(ValidationError):
        PlanRecord(**{**POPRAWNY, "metric": "   "})


def test_nazwa_wskaznika_nie_jest_tlumaczona() -> None:
    """Fundament nie dopasowuje metric do miar testów — patrz wpis B-04.

    Wartość przechodzi taka, jaka przyszła z danych klienta, bez normalizacji nazwy.
    """
    rekord = PlanRecord(**{**POPRAWNY, "metric": "Koszt Całkowity (PLN)"})
    assert rekord.metric == "Koszt Całkowity (PLN)"
