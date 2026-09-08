# Sprawdza rejestr pięciu tabel z ZOP-TECH-01 v0.1 pkt 5.2 oraz kryterium odbioru 8.2.
"""Testy przekrojowe dla wszystkich zarejestrowanych tabel.

Te testy pilnują kontraktu jako całości: że tabel jest dokładnie pięć, że nazywają się
tak jak w karcie i że metadane każdej z nich są spójne z jej polami. Dzięki temu
dołożenie szóstej tabeli albo cicha zmiana klucza naturalnego nie przejdzie niezauważona.
"""

import pytest

from xray.model import TABLES, get_table, table_names
from xray.model.enums import TimeGrain

# Nazwy i pola dokładnie z ZOP-TECH-01 pkt 5.2, tabela w rozdziale 5.2.
POLA_Z_KARTY = {
    "ACTIVITY": {"date", "unit", "product", "volume", "revenue"},
    "COST": {"date", "unit", "category", "amount"},
    "RESOURCE": {"date", "unit", "resource", "available", "used", "cost"},
    "PROCESS": {"case_id", "stage", "start", "end", "unit"},
    "PLAN": {"date", "unit", "metric", "target"},
}


def test_rejestr_zna_dokladnie_piec_tabel() -> None:
    """Zbiór tabel jest zamknięty przez pkt 5.2."""
    assert set(table_names()) == set(POLA_Z_KARTY)
    assert len(table_names()) == 5


@pytest.mark.parametrize("nazwa", sorted(POLA_Z_KARTY))
def test_tabela_ma_dokladnie_pola_z_karty(nazwa: str) -> None:
    """Ani mniej, ani więcej. Rozszerzenia z kart dokładamy razem z kartą."""
    assert set(get_table(nazwa).model_fields) == POLA_Z_KARTY[nazwa]


@pytest.mark.parametrize("nazwa", sorted(POLA_Z_KARTY))
def test_klucz_naturalny_jest_podzbiorem_pol(nazwa: str) -> None:
    """Klucz nie może wskazywać pola, którego w kontrakcie nie ma (kontrola 4)."""
    tabela = get_table(nazwa)
    assert set(tabela.NATURAL_KEY) <= set(tabela.model_fields)
    assert tabela.NATURAL_KEY, "klucz naturalny nie może być pusty"


@pytest.mark.parametrize("nazwa", sorted(POLA_Z_KARTY))
def test_pola_czasu_sa_podzbiorem_pol(nazwa: str) -> None:
    """TIME_FIELDS zasila kontrolę 8 (zakres czasowy)."""
    tabela = get_table(nazwa)
    assert set(tabela.TIME_FIELDS) <= set(tabela.model_fields)
    assert tabela.TIME_FIELDS, "tabela bez pól czasu nie przejdzie kontroli 8"


@pytest.mark.parametrize("nazwa", sorted(POLA_Z_KARTY))
def test_nazwa_w_rejestrze_zgadza_sie_z_deklaracja_tabeli(nazwa: str) -> None:
    assert get_table(nazwa).TABLE_NAME == nazwa


def test_tylko_process_jest_tabela_zdarzeniowa() -> None:
    """Cztery tabele niosą agregaty okresowe, PROCESS zdarzenia — patrz wpis A-01."""
    zdarzeniowe = {n for n, c in TABLES.items() if c.TIME_GRAIN is TimeGrain.EVENT}
    assert zdarzeniowe == {"PROCESS"}


def test_tabele_okresowe_maja_pole_date_jako_czas() -> None:
    for nazwa, tabela in TABLES.items():
        if tabela.TIME_GRAIN is TimeGrain.PERIOD:
            assert tabela.TIME_FIELDS == ("date",), nazwa


def test_nieznana_nazwa_tabeli_daje_czytelny_blad() -> None:
    """Nietrafiona nazwa to zwykle literówka w profilu mapowania klienta."""
    with pytest.raises(KeyError) as blad:
        get_table("KOSZTY")
    assert "ACTIVITY" in str(blad.value)


def test_rejestru_nie_da_sie_zmodyfikowac() -> None:
    """Zbiór tabel jest zamknięty; nikt nie dokłada tabeli w czasie działania."""
    with pytest.raises(TypeError):
        TABLES["NOWA"] = object  # type: ignore[index]
