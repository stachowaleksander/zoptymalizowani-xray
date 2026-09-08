# Sprawdza kontrakt tabeli ACTIVITY z ZOP-TECH-01 v0.1 pkt 5.2.
"""Ręczne rekordy testowe dla ACTIVITY (ZOP-TECH-01 pkt 9.2)."""

import datetime as dt

import pytest
from pydantic import ValidationError

from xray.model import ActivityRecord

POPRAWNY = {
    "date": dt.date(2026, 3, 1),
    "unit": "Dział A",
    "product": "usługa podstawowa",
    "volume": 1_240.0,
    "revenue": 318_000.0,
}


def test_rekord_minimalny_przechodzi() -> None:
    rekord = ActivityRecord(**POPRAWNY)
    assert rekord.product == "usługa podstawowa"
    assert rekord.volume == 1_240.0
    assert rekord.revenue == 318_000.0


def test_pusty_wolumen_i_przychod_sa_dopuszczalne() -> None:
    """Braku nie wypełniamy zerem — FIN-01 VAL-01 ogłasza go w validation/."""
    rekord = ActivityRecord(**{**POPRAWNY, "volume": None, "revenue": None})
    assert rekord.volume is None
    assert rekord.revenue is None


def test_ujemny_przychod_przechodzi_przez_model() -> None:
    """Kontrola 5 z pkt 5.3 należy do validation/ i zwraca sygnał, nie odrzucenie."""
    rekord = ActivityRecord(**{**POPRAWNY, "revenue": -12_000.0})
    assert rekord.revenue == -12_000.0


def test_pusty_produkt_jest_odrzucany() -> None:
    """product należy do klucza naturalnego (FIN-01 pkt 2.1)."""
    with pytest.raises(ValidationError):
        ActivityRecord(**{**POPRAWNY, "product": "  "})


def test_tekst_w_polu_wolumenu_jest_odrzucany() -> None:
    """Kontrola 5.3/2 — nieprawidłowy format."""
    with pytest.raises(ValidationError):
        ActivityRecord(**{**POPRAWNY, "volume": "tysiąc dwieście"})
