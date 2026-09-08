# Test przypinający: zapowiedź mapowania i zapis importu muszą się zgadzać.
"""Zgodność ``MappingReport.mapped`` z ``ImportReport.applied_columns``.

Obie wielkości mówią o tym samym — które pole kontraktu zasila która kolumna klienta —
ale powstają **osobno i z osobnych źródeł wiedzy o dostępnych kolumnach**:

- ``MappingReport.mapped`` **przewiduje**: zestawia profil z listą kolumn podaną z zewnątrz,
- ``ImportReport.applied_columns`` **zapisuje**: mówi, co import faktycznie zrobił z plikiem.

Do skrótu znaczącej treści profilu wchodzi to drugie i tak ma być — liczy się to, co się
wydarzyło. Ale nic samo z siebie nie pilnuje, żeby zapowiedź i wykonanie się zgadzały.
Rozjazd byłby cichy: mapowanie zapowiedziałoby pięć przypisań, import wykonał cztery,
a raport dla klienta mówiłby co innego niż tożsamość przebiegu.
"""

from pathlib import Path

import pandas as pd
import pytest

from xray.ingest import load_table
from xray.mapping import MappingProfile, apply_profile

PROFIL = "profiles/firma-syntetyczna.yaml"
ZBIOR = "firma-syntetyczna"

PLIKI = {
    "ACTIVITY": {
        "Miesiac": ["2026-01-01"],
        "Komorka": ["Dział A"],
        "Usluga": ["usługa podstawowa"],
        "Liczba_wykonan": ["120"],
        "Przychod_netto": ["36000"],
    },
    "COST": {
        "Miesiac": ["2026-01-01"],
        "Komorka": ["Dział A"],
        "Rodzaj_kosztu": ["wynagrodzenia"],
        "Kwota": ["125400"],
    },
    "RESOURCE": {
        "Miesiac": ["2026-01-01"],
        "Komorka": ["Dział A"],
        "Zasob": ["gabinet 1"],
        "Godziny_dostepne": ["160"],
        "Godziny_wykorzystane": ["132"],
        "Koszt_zasobu": ["24000"],
        "Kod_MPK": ["MPK-11"],
    },
    "PROCESS": {
        "Nr_sprawy": ["SPR-1"],
        "Etap": ["rejestracja"],
        "Poczatek": ["2026-01-01T08:00:00"],
        "Koniec": ["2026-01-01T08:20:00"],
        "Komorka": ["Dział A"],
    },
    "PLAN": {
        "Miesiac": ["2026-01-01"],
        "Komorka": ["Dział A"],
        "Wskaznik": ["koszt_calkowity"],
        "Wartosc_planu": ["250000"],
    },
}


@pytest.mark.parametrize("tabela", sorted(PLIKI))
def test_zapowiedz_mapowania_zgadza_sie_z_zapisem_importu(
    tmp_path: Path, tabela: str
) -> None:
    """Dla tego samego profilu i tego samego pliku obie listy muszą być identyczne."""
    profil = MappingProfile.load(PROFIL)
    sciezka = tmp_path / f"{tabela.lower()}.csv"
    dane = pd.DataFrame(PLIKI[tabela])
    dane.to_csv(sciezka, index=False, encoding="utf-8")

    raport_mapowania = apply_profile(profil, tabela, list(dane.columns))
    wynik = load_table(
        sciezka, tabela, dataset_id=ZBIOR, column_map=raport_mapowania.column_map
    )

    assert wynik.report.applied_columns == raport_mapowania.mapped


@pytest.mark.parametrize("tabela", sorted(PLIKI))
def test_niezmapowane_kolumny_zgadzaja_sie_z_pominietymi(
    tmp_path: Path, tabela: str
) -> None:
    """Kolumna bez miejsca w kontrakcie ma być tą samą kolumną w obu raportach."""
    profil = MappingProfile.load(PROFIL)
    sciezka = tmp_path / f"{tabela.lower()}.csv"
    dane = pd.DataFrame(PLIKI[tabela])
    dane.to_csv(sciezka, index=False, encoding="utf-8")

    raport_mapowania = apply_profile(profil, tabela, list(dane.columns))
    wynik = load_table(
        sciezka, tabela, dataset_id=ZBIOR, column_map=raport_mapowania.column_map
    )

    assert set(wynik.report.dropped_columns) == set(raport_mapowania.unmapped_columns)


def test_zapowiedz_i_zapis_zgadzaja_sie_takze_przy_brakujacej_kolumnie(
    tmp_path: Path,
) -> None:
    """Rozjazd najłatwiej powstaje tam, gdzie profil zapowiada więcej, niż plik ma."""
    profil = MappingProfile.load(PROFIL)
    sciezka = tmp_path / "resource.csv"
    dane = pd.DataFrame(
        {k: v for k, v in PLIKI["RESOURCE"].items() if k != "Koszt_zasobu"}
    )
    dane.to_csv(sciezka, index=False, encoding="utf-8")

    raport_mapowania = apply_profile(profil, "RESOURCE", list(dane.columns))
    wynik = load_table(
        sciezka, "RESOURCE", dataset_id=ZBIOR, column_map=raport_mapowania.column_map
    )

    assert raport_mapowania.declared_missing_columns == (("cost", "Koszt_zasobu"),)
    assert wynik.report.applied_columns == raport_mapowania.mapped
    assert wynik.report.materialized_empty == raport_mapowania.materialized_empty
    assert wynik.report.missing_key_columns == raport_mapowania.missing_key_fields
