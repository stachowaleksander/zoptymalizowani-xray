# Sprawdza wymuszenie deklaracji metadanych z ZOP-TECH-01 pkt 5.2 oraz wspólne typy pól.
"""Testy klasy bazowej tabel.

Tabela, która nie zadeklaruje metadanych, ma się nie dać zaimportować. Bez tego brak
ujawniłby się dopiero przy kontroli 8 z pkt 5.3, czyli najpóźniej jak się da.
"""

import datetime as dt
from typing import ClassVar

import pytest

from xray.model.enums import TimeGrain
from xray.model.tables.base import KeyText, NumericValue, PeriodDate, TableRecord


def test_tabela_bez_metadanych_nie_powstaje() -> None:
    with pytest.raises(TypeError) as blad:

        class BrakMetadanych(TableRecord):
            date: PeriodDate

    komunikat = str(blad.value)
    assert "TABLE_NAME" in komunikat
    assert "NATURAL_KEY" in komunikat


def test_tabela_z_niepelnymi_metadanymi_nie_powstaje() -> None:
    with pytest.raises(TypeError) as blad:

        class BrakZiarna(TableRecord):
            TABLE_NAME: ClassVar[str] = "X"
            NATURAL_KEY: ClassVar[tuple[str, ...]] = ("date",)
            date: PeriodDate

    assert "TIME_GRAIN" in str(blad.value)


def test_klucz_naturalny_wskazujacy_nieistniejace_pole_nie_powstaje() -> None:
    """Klucz odwołujący się do pola spoza kontraktu psułby kontrolę 4 (duplikaty)."""
    with pytest.raises(TypeError) as blad:

        class ZlyKlucz(TableRecord):
            TABLE_NAME: ClassVar[str] = "X"
            NATURAL_KEY: ClassVar[tuple[str, ...]] = ("date", "nie_ma_takiego_pola")
            TIME_GRAIN: ClassVar[TimeGrain] = TimeGrain.PERIOD
            TIME_FIELDS: ClassVar[tuple[str, ...]] = ("date",)
            date: PeriodDate

    assert "nie_ma_takiego_pola" in str(blad.value)


def test_pola_czasu_wskazujace_nieistniejace_pole_nie_powstaja() -> None:
    """TIME_FIELDS spoza kontraktu psułoby kontrolę 8 (zakres czasowy)."""
    with pytest.raises(TypeError) as blad:

        class ZlyCzas(TableRecord):
            TABLE_NAME: ClassVar[str] = "X"
            NATURAL_KEY: ClassVar[tuple[str, ...]] = ("date",)
            TIME_GRAIN: ClassVar[TimeGrain] = TimeGrain.PERIOD
            TIME_FIELDS: ClassVar[tuple[str, ...]] = ("kiedys",)
            date: PeriodDate

    assert "kiedys" in str(blad.value)


def test_poprawna_tabela_powstaje() -> None:
    """Kontrola nie może blokować tabeli zadeklarowanej prawidłowo."""

    class Poprawna(TableRecord):
        TABLE_NAME: ClassVar[str] = "X"
        NATURAL_KEY: ClassVar[tuple[str, ...]] = ("date", "unit")
        TIME_GRAIN: ClassVar[TimeGrain] = TimeGrain.PERIOD
        TIME_FIELDS: ClassVar[tuple[str, ...]] = ("date",)
        date: PeriodDate
        unit: KeyText
        value: NumericValue

    rekord = Poprawna(date=dt.date(2026, 1, 1), unit="A", value=None)
    assert rekord.value is None
