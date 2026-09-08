# Sprawdza kontrolę 1 z ZOP-TECH-01 v0.1 pkt 5.3 oraz wpis B-06.
"""Testy kontroli 1 — brak wymaganej kolumny.

Najważniejsze są tu trzy rzeczy: dwa stany zamiast trzech (rozstrzygnięcie B-06),
działanie bez profilu (podstawa z raportu importu) oraz zakaz ogłaszania PASS **bez
podstawy** — co jest czym innym niż PASS z obserwacją opisującą brak.
"""

from pathlib import Path

import pandas as pd
import pytest

from xray.ingest import load_table
from xray.mapping import MappingProfile, apply_profile
from xray.model import ValidationStatus, get_table
from xray.validation import (
    NotAssessedReason,
    ValidationContext,
    get_declaration,
    run_check,
)

PROFIL = "profiles/firma-syntetyczna.yaml"
ZBIOR = "firma-syntetyczna"

PELNY = (
    "Miesiac,Komorka,Zasob,Godziny_dostepne,Godziny_wykorzystane,Koszt_zasobu\n"
    "2026-01-01,Dział A,gabinet 1,160,132,24000\n"
)


def kontekst(tmp_path: Path, tresc: str, *, z_profilem: bool = True):
    """Buduje kontekst RESOURCE z pliku o zadanych kolumnach."""
    sciezka = tmp_path / "resource.csv"
    sciezka.write_text(tresc, encoding="utf-8")
    kolumny = tresc.splitlines()[0].split(",")

    if z_profilem:
        profil = MappingProfile.load(PROFIL)
        raport_mapowania = apply_profile(profil, "RESOURCE", kolumny)
        wynik = load_table(
            sciezka, "RESOURCE", dataset_id=ZBIOR, column_map=raport_mapowania.column_map
        )
        mapowanie = (raport_mapowania,)
    else:
        # Mapowanie tożsamościowe: nazwy kolumn są nazwami pól kontraktu.
        wynik = load_table(sciezka, "RESOURCE", dataset_id=ZBIOR)
        mapowanie = None

    return ValidationContext(
        table=get_table("RESOURCE"),
        frame=wynik.frame,
        import_reports=(wynik.report,),
        mapping_reports=mapowanie,
    )


# --- dwa stany, nie trzy --------------------------------------------------------------


def test_komplet_kolumn_daje_pass(tmp_path: Path) -> None:
    assert run_check("TECH01-VAL-01", kontekst(tmp_path, PELNY)).status is (
        ValidationStatus.PASS
    )


BEZ_KOSZTU = (
    "Miesiac,Komorka,Zasob,Godziny_dostepne,Godziny_wykorzystane\n"
    "2026-01-01,Dział A,gabinet 1,160,132\n"
)


def test_brak_pola_spoza_klucza_daje_pass_z_obserwacja(tmp_path: Path) -> None:
    """Rozstrzygnięcie B-06: walidator ogłasza stan danych, nie orzeka o jego ciężarze.

    Czy brak pola ogranicza wnioskowanie, zależy od tego, który test się uruchomi —
    a tego walidator nie wie. WARNING byłby orzeczeniem o ciężarze, którego nie zna.
    """
    wynik = run_check("TECH01-VAL-01", kontekst(tmp_path, BEZ_KOSZTU))
    assert wynik.status is ValidationStatus.PASS
    assert wynik.observations[0].subject == "cost"
    assert wynik.observations[0].measure == "materialized_empty_column"


def test_pass_przy_braku_pola_nie_jest_falszywym_przejsciem(tmp_path: Path) -> None:
    """Fakt jest w wyniku — jako obserwacja z podstawą, tylko nie jako status."""
    wynik = run_check("TECH01-VAL-01", kontekst(tmp_path, BEZ_KOSZTU))
    assert wynik.observations, "brak kolumny musi być widoczny w wyniku"
    assert "cost" in wynik.basis
    assert "nie orzeka o jego ciężarze" in wynik.basis


def test_brak_elementu_klucza_daje_critical(tmp_path: Path) -> None:
    bez_komorki = (
        "Miesiac,Zasob,Godziny_dostepne,Godziny_wykorzystane,Koszt_zasobu\n"
        "2026-01-01,gabinet 1,160,132,24000\n"
    )
    wynik = run_check("TECH01-VAL-01", kontekst(tmp_path, bez_komorki))
    assert wynik.status is ValidationStatus.CRITICAL
    assert wynik.observations[0].subject == "unit"
    assert wynik.observations[0].measure == "missing_key_column"


def test_brak_klucza_wygrywa_nad_brakiem_pola_spoza(tmp_path: Path) -> None:
    """Brak elementu klucza jest jedynym brakiem, który wyznacza status."""
    tylko_zasob = "Miesiac,Zasob,Godziny_dostepne\n2026-01-01,gabinet 1,160\n"
    wynik = run_check("TECH01-VAL-01", kontekst(tmp_path, tylko_zasob))
    assert wynik.status is ValidationStatus.CRITICAL
    miary = {o.measure for o in wynik.observations}
    assert miary == {"missing_key_column", "materialized_empty_column"}


def test_sufit_jest_zadeklarowany_jako_critical() -> None:
    """Sufit zostaje CRITICAL — używa go wyłącznie gałąź klucza naturalnego."""
    assert get_declaration("TECH01-VAL-01").max_status is ValidationStatus.CRITICAL
    assert get_declaration("TECH01-VAL-01").control_number == 1


def test_kontrola_1_nigdy_nie_zwraca_warning(tmp_path: Path) -> None:
    """Gałąź WARNING nie istnieje — B-06 odrzuca orzekanie o ciężarze braku."""
    warianty = (
        PELNY,
        BEZ_KOSZTU,
        "Miesiac,Zasob,Godziny_dostepne\n2026-01-01,gabinet 1,160\n",
    )
    for tresc in warianty:
        wynik = run_check("TECH01-VAL-01", kontekst(tmp_path, tresc))
        assert wynik.status is not ValidationStatus.WARNING, tresc


# --- działa bez profilu ---------------------------------------------------------------


def test_kontrola_dziala_bez_profilu(tmp_path: Path) -> None:
    """Status wywodzi się z raportu importu, więc mapowanie tożsamościowe wystarcza.

    Gdyby kontrola wymagała profilu, ogłaszałaby not_assessable na obecnej demonstracji.
    """
    bez_kosztu = (
        "date,unit,resource,available,used\n2026-01-01,Dział A,gabinet 1,160,132\n"
    )
    ctx = kontekst(tmp_path, bez_kosztu, z_profilem=False)
    assert ctx.mapping_known is False
    wynik = run_check("TECH01-VAL-01", ctx)
    assert wynik.status is ValidationStatus.PASS
    assert wynik.observations[0].subject == "cost"


def test_raport_mapowania_wzbogaca_podstawe(tmp_path: Path) -> None:
    """„Nie przypisałeś" i „przypisałeś do nieistniejącej kolumny" to dwie różne rozmowy."""
    bez_kosztu = (
        "Miesiac,Komorka,Zasob,Godziny_dostepne,Godziny_wykorzystane\n"
        "2026-01-01,Dział A,gabinet 1,160,132\n"
    )
    z_profilem = run_check("TECH01-VAL-01", kontekst(tmp_path, bez_kosztu))
    assert "Koszt_zasobu" in z_profilem.observations[0].basis

    bez_profilu = run_check(
        "TECH01-VAL-01",
        kontekst(
            tmp_path,
            "date,unit,resource,available,used\n2026-01-01,Dział A,gabinet 1,160,132\n",
            z_profilem=False,
        ),
    )
    assert "nie przypisał" in bez_profilu.observations[0].basis


# --- zakaz PASS bez podstawy ----------------------------------------------------------


def test_brak_wiedzy_o_imporcie_nie_daje_pass(tmp_path: Path) -> None:
    """PASS bez podstawy to fałszywe przejście."""
    ctx = ValidationContext(table=get_table("RESOURCE"), frame=pd.DataFrame())
    wynik = run_check("TECH01-VAL-01", ctx)
    assert wynik.status is None
    assert wynik.not_assessed_reason is NotAssessedReason.MISSING_INPUT
    assert wynik.status is not ValidationStatus.PASS


def test_kontrola_1_wymaga_raportu_importu() -> None:
    """Brak kolumny widać wyłącznie w raporcie: w ramce pole zawsze jest, tylko puste."""
    assert get_declaration("TECH01-VAL-01").requires_import_report is True


# --- kontekst: dopisanie wiedzy nie zmienia sygnatur ----------------------------------


def test_pozostale_kontrole_dzialaja_bez_raportu_mapowania(tmp_path: Path) -> None:
    """Teza, dla której kontekst powstał: dopisanie pola nie rusza istniejących kontroli."""
    from xray.validation import registered_check_ids, run_checks

    ctx = kontekst(tmp_path, PELNY, z_profilem=False)
    assert ctx.mapping_reports is None
    wyniki = run_checks(ctx)
    assert len(wyniki) == len(registered_check_ids())
    assert all(
        w.status is not None or w.not_assessed_reason is not None for w in wyniki
    )


def test_pusta_krotka_raportow_mapowania_jest_zakazana() -> None:
    """Ta sama racja co przy raportach importu: byłaby nie do odróżnienia od braku."""
    with pytest.raises(ValueError):
        ValidationContext(
            table=get_table("RESOURCE"), frame=pd.DataFrame(), mapping_reports=()
        )


def test_raport_mapowania_obcej_tabeli_jest_odrzucany(tmp_path: Path) -> None:
    profil = MappingProfile.load(PROFIL)
    obcy = apply_profile(profil, "COST", ["Miesiac", "Komorka", "Rodzaj_kosztu", "Kwota"])
    with pytest.raises(ValueError) as blad:
        ValidationContext(
            table=get_table("RESOURCE"), frame=pd.DataFrame(), mapping_reports=(obcy,)
        )
    assert "COST" in str(blad.value)
