# Sprawdza kontrakt tabeli COST z ZOP-TECH-01 v0.1 pkt 5.2 oraz kontrole z pkt 5.3,
# które da się rozstrzygnąć na pojedynczym wierszu.
"""Ręczne rekordy testowe dla COST (ZOP-TECH-01 pkt 9.2).

Podział ról jest tu celowy i pilnowany testami: model rozstrzyga to, co widać w jednym
wierszu (kontrola 2 — format, kontrola 3 — wykrycie braku). Duplikaty, spójność nazw
jednostek i zakres czasowy wymagają całego zbioru i należą do ``validation/``.
"""

import datetime as dt
import math

import pytest
from pydantic import ValidationError

from xray.model import CostRecord, TimeGrain

POPRAWNY = {
    "date": dt.date(2026, 3, 1),
    "unit": "Dział A",
    "category": "wynagrodzenia",
    "amount": 125_400.50,
}


def test_rekord_minimalny_przechodzi() -> None:
    """Cztery pola z pkt 5.2 wystarczą do zbudowania rekordu."""
    rekord = CostRecord(**POPRAWNY)
    assert rekord.date == dt.date(2026, 3, 1)
    assert rekord.unit == "Dział A"
    assert rekord.category == "wynagrodzenia"
    assert rekord.amount == 125_400.50


# --- metadane tabeli ---------------------------------------------------------------


def test_metadane_tabeli_sa_dostepne_bez_tworzenia_rekordu() -> None:
    """Walidator potrzebuje tych faktów, zanim powstanie jakikolwiek rekord."""
    assert CostRecord.TABLE_NAME == "COST"
    assert CostRecord.NATURAL_KEY == ("date", "unit", "category")
    assert CostRecord.TIME_GRAIN is TimeGrain.PERIOD
    assert CostRecord.TIME_FIELDS == ("date",)


def test_klucz_naturalny_pokrywa_sie_z_polami_modelu() -> None:
    """Klucz nie może wskazywać pola, którego w kontrakcie nie ma."""
    assert set(CostRecord.NATURAL_KEY) <= set(CostRecord.model_fields)


def test_kontrakt_ma_dokladnie_pola_z_karty() -> None:
    """Pkt 5.2: COST to date, unit, category, amount. Ani mniej, ani więcej."""
    assert set(CostRecord.model_fields) == {"date", "unit", "category", "amount"}


# --- brak wartości: zasada „null jest poprawnym wynikiem" --------------------------


def test_pusta_kwota_jest_dopuszczalna() -> None:
    """Braku nie wypełniamy zerem ani średnią — skalę braków zlicza validation/."""
    rekord = CostRecord(**{**POPRAWNY, "amount": None})
    assert rekord.amount is None


def test_nan_staje_sie_none() -> None:
    """NaN z pandas i None znaczą to samo; trzymamy jedną reprezentację braku."""
    rekord = CostRecord(**{**POPRAWNY, "amount": math.nan})
    assert rekord.amount is None


def test_zero_pozostaje_zerem() -> None:
    """Zero nie jest brakiem i nigdy nie staje się None.

    Koszt kategorii w danym miesiącu mógł realnie wynieść 0 zł. ZOP-XR-FIN-01 rozdz. 6
    rozróżnia te sytuacje wprost: „CI | R = 0 → null" opisuje przychód równy zeru, a nie
    przychód nieznany, i jest to inna podstawa niż „mianownik 0 → null" przy braku
    danych. Obie drogi kończą się miarą null, ale podstawa trafia do validation_notes
    i do danych dla ZOP-CONF-01, więc sklejenie ich zniszczyłoby to rozróżnienie.
    """
    rekord = CostRecord(**{**POPRAWNY, "amount": 0.0})
    assert rekord.amount == 0.0
    assert rekord.amount is not None


def test_brak_pola_amount_jest_bledem() -> None:
    """Pole jest wymagane, choć jego wartość może być pusta. To nie to samo."""
    dane = {k: v for k, v in POPRAWNY.items() if k != "amount"}
    with pytest.raises(ValidationError):
        CostRecord(**dane)


# --- kontrola 2: nieprawidłowy format ----------------------------------------------


def test_tekst_w_polu_liczbowym_jest_odrzucany() -> None:
    """Kontrola 5.3/2 — tekst w polu liczbowym."""
    with pytest.raises(ValidationError):
        CostRecord(**{**POPRAWNY, "amount": "sto tysięcy"})


def test_data_z_napisu_iso_jest_przyjmowana() -> None:
    """Ścieżka z CSV podaje datę napisem."""
    rekord = CostRecord(**{**POPRAWNY, "date": "2026-03-01"})
    assert rekord.date == dt.date(2026, 3, 1)


def test_data_podana_liczba_jest_odrzucana() -> None:
    """Surowy numer seryjny z XLSX nie może po cichu stać się znacznikiem uniksowym."""
    with pytest.raises(ValidationError) as blad:
        CostRecord(**{**POPRAWNY, "date": 45000})
    assert "ingest" in str(blad.value)


def test_nieskonczonosc_w_kwocie_jest_odrzucana() -> None:
    """inf nie jest kwotą i nie może wejść do agregatów."""
    with pytest.raises(ValidationError):
        CostRecord(**{**POPRAWNY, "amount": math.inf})


# --- klucz naturalny ----------------------------------------------------------------


def test_pusta_jednostka_jest_odrzucana() -> None:
    """Rekord bez klucza nie da się przypisać do żadnego zakresu."""
    with pytest.raises(ValidationError):
        CostRecord(**{**POPRAWNY, "unit": ""})


def test_jednostka_z_samych_spacji_jest_odrzucana() -> None:
    with pytest.raises(ValidationError):
        CostRecord(**{**POPRAWNY, "category": "   "})


def test_biale_znaki_nie_sa_przycinane() -> None:
    """Dowód dla kontroli 6 (niespójne nazwy jednostek) musi przetrwać do validation/.

    „Dział A" i „Dział A " mają zostać dwiema różnymi wartościami, bo dokładnie taką
    niespójność ma wykryć walidator na całym zbiorze.
    """
    rekord = CostRecord(**{**POPRAWNY, "unit": "Dział A "})
    assert rekord.unit == "Dział A "


# --- wpis B-01: wartość ujemna ------------------------------------------------------


def test_ujemna_kwota_jest_dopuszczalna_w_modelu() -> None:
    """Kontrakt COST nie ma pola oznaczenia korekty — patrz wpis B-01.

    Model nie może rozstrzygnąć, czy ujemna kwota to korekta, czy błąd, więc jej nie
    blokuje. Sygnał z podstawą wystawia validation/, bez klasyfikowania jako błąd.
    """
    rekord = CostRecord(**{**POPRAWNY, "amount": -4_200.0})
    assert rekord.amount == -4_200.0


# --- szczelność kontraktu -----------------------------------------------------------


def test_nieznana_kolumna_jest_odrzucana() -> None:
    """Do modelu nie powinna dojść — mapping/ decyduje wcześniej. To siatka bezpieczeństwa."""
    with pytest.raises(ValidationError):
        CostRecord(**{**POPRAWNY, "koszt_dodatkowy": 10.0})


def test_rekord_jest_niezmienny() -> None:
    """Determinizm: nikt nie „poprawia" rekordu po walidacji."""
    rekord = CostRecord(**POPRAWNY)
    with pytest.raises(ValidationError):
        rekord.amount = 1.0
