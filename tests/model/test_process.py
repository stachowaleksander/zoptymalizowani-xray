# Sprawdza kontrakt tabeli PROCESS z ZOP-TECH-01 v0.1 pkt 5.2
# oraz rozstrzygnięcie z docs/otwarte-kontrakty.md wpis A-01.
"""Ręczne rekordy testowe dla PROCESS (ZOP-TECH-01 pkt 9.2).

PROCESS jest jedyną tabelą zdarzeniową. Testy pilnują trzech rzeczy: że nie ma tu pola
``date``, że oba znaczniki czasu mogą być puste i że model nie rozstrzyga niczego, co
należy do walidatora.
"""

import datetime as dt

import pytest
from pydantic import ValidationError

from xray.model import ProcessRecord
from xray.model.enums import TimeGrain

POPRAWNY = {
    "case_id": "SPR-000123",
    "stage": "rejestracja",
    "start": dt.datetime(2026, 3, 1, 8, 30),
    "end": dt.datetime(2026, 3, 1, 8, 52),
    "unit": "Dział A",
}


def test_rekord_minimalny_przechodzi() -> None:
    rekord = ProcessRecord(**POPRAWNY)
    assert rekord.case_id == "SPR-000123"
    assert rekord.stage == "rejestracja"


def test_tabela_nie_ma_pola_date() -> None:
    """Etykieta okresu jest wyliczalna z start/end, a podstawa wyliczenia to reguła
    metodologiczna, której TECH-01 nie rozstrzyga — patrz wpis A-01."""
    assert "date" not in ProcessRecord.model_fields


def test_ziarno_jest_zdarzeniowe_a_czas_niosa_start_i_end() -> None:
    assert ProcessRecord.TIME_GRAIN is TimeGrain.EVENT
    assert ProcessRecord.TIME_FIELDS == ("start", "end")


def test_klucz_naturalny_to_case_id_i_stage() -> None:
    """PROC-01 pkt 2.3 i PROC-02 pkt 2.3 wskazują przypadek i etap; unit nie jest kluczem."""
    assert ProcessRecord.NATURAL_KEY == ("case_id", "stage")


def test_etap_bez_konca_jest_dopuszczalny() -> None:
    """Pusty end to normalny stan etapu jeszcze trwającego."""
    rekord = ProcessRecord(**{**POPRAWNY, "end": None})
    assert rekord.end is None
    assert rekord.start is not None


def test_etap_bez_obu_znacznikow_jest_dopuszczalny() -> None:
    """Rekord bez czasu jest faktem o jakości danych, który ogłasza validation/."""
    rekord = ProcessRecord(**{**POPRAWNY, "start": None, "end": None})
    assert rekord.start is None
    assert rekord.end is None


def test_pusta_jednostka_jest_dopuszczalna() -> None:
    """unit nie należy do klucza naturalnego PROCESS — jedyne takie miejsce w modelu."""
    rekord = ProcessRecord(**{**POPRAWNY, "unit": None})
    assert rekord.unit is None


def test_koniec_wczesniejszy_niz_poczatek_przechodzi_przez_model() -> None:
    """To kontrola jednowierszowa, ale jej wynikiem ma być status z validation/.

    Rekord odrzucony przez model nigdy nie dotarłby do walidatora, więc niespójność
    czasu zniknęłaby z raportu jakości danych zamiast się w nim pojawić.
    """
    rekord = ProcessRecord(
        **{
            **POPRAWNY,
            "start": dt.datetime(2026, 3, 1, 9, 0),
            "end": dt.datetime(2026, 3, 1, 8, 0),
        }
    )
    assert rekord.end < rekord.start


def test_pusty_identyfikator_przypadku_jest_odrzucany() -> None:
    """case_id należy do klucza naturalnego."""
    with pytest.raises(ValidationError):
        ProcessRecord(**{**POPRAWNY, "case_id": ""})


def test_znacznik_czasu_z_napisu_iso_jest_przyjmowany() -> None:
    rekord = ProcessRecord(**{**POPRAWNY, "start": "2026-03-01T08:30:00"})
    assert rekord.start == dt.datetime(2026, 3, 1, 8, 30)


def test_znacznik_czasu_podany_liczba_jest_odrzucany() -> None:
    """Surowy numer seryjny z XLSX nie może po cichu stać się znacznikiem uniksowym."""
    with pytest.raises(ValidationError) as blad:
        ProcessRecord(**{**POPRAWNY, "start": 45000})
    assert "ingest" in str(blad.value)


# --- kanonizacja braku tekstu (wpis DT-06) ------------------------------------------


def test_pusty_napis_w_jednostce_staje_sie_none() -> None:
    """CSV z pustą komórką da "", XLSX da None. Brak ma mieć jedną reprezentację."""
    rekord = ProcessRecord(**{**POPRAWNY, "unit": ""})
    assert rekord.unit is None


def test_jednostka_ze_samych_spacji_staje_sie_none() -> None:
    rekord = ProcessRecord(**{**POPRAWNY, "unit": "   "})
    assert rekord.unit is None


def test_jednostka_niepusta_nie_jest_przycinana() -> None:
    """„Dział A " zostaje ze spacją — to dowód dla kontroli 6."""
    rekord = ProcessRecord(**{**POPRAWNY, "unit": "Dział A "})
    assert rekord.unit == "Dział A "


# --- strefa czasowa (wpis DT-05) ----------------------------------------------------


def test_znacznik_ze_strefa_jest_odrzucany() -> None:
    """Dwa nieporównywalne typy w jednym polu rozsypałyby kontrolę 8.

    Porównanie znacznika ze strefą ze znacznikiem bez strefy podnosi TypeError, więc
    kontrakt nie może wpuścić obu. Przeliczenie należy do ingest/.
    """
    with pytest.raises(ValidationError) as blad:
        ProcessRecord(**{**POPRAWNY, "start": "2026-03-01T08:30:00+01:00"})
    assert "ingest" in str(blad.value)


def test_znacznik_ze_strefa_utc_tez_jest_odrzucany() -> None:
    """Także UTC — model nie zna pojęcia strefy, więc nie ma wyjątków."""
    with pytest.raises(ValidationError):
        ProcessRecord(
            **{**POPRAWNY, "end": dt.datetime(2026, 3, 1, 8, 52, tzinfo=dt.UTC)}
        )


def test_znacznik_bez_strefy_przechodzi() -> None:
    rekord = ProcessRecord(**{**POPRAWNY, "start": dt.datetime(2026, 3, 1, 8, 30)})
    assert rekord.start is not None
    assert rekord.start.tzinfo is None


# --- rozstrzygnięcie A-01 (Michał, 2026-09-05) ---------------------------------------


def test_modul_nie_ma_domyslnej_podstawy_czasu() -> None:
    """Nie ma domyślnej podstawy przypisania procesu do miesiąca.

    Robocze `DEFAULT_TIME_BASIS = "stage_start"` zostało wycofane: nie zostaje nawet jako
    założenie. Kontrola 8 nie ma prawa wybrać sobie podstawy — `time_basis_used` zwraca
    null z podstawą „kontrakt globalny nierozstrzygnięty". Ten test pilnuje, żeby
    domyślna wartość nie wróciła jako wygodne uproszczenie.
    """
    from xray.model.tables import process

    assert not hasattr(process, "DEFAULT_TIME_BASIS")
    assert not any("TIME_BASIS" in nazwa for nazwa in dir(process))
