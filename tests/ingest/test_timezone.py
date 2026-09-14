# Sprawdza wariant A wpisu DT-05 (konwersja znaczników ze strefą na czas lokalny
# organizacji) oraz założenie tymczasowe z wpisu B-07 (jesienna zmiana czasu).
"""Testy konwersji stref czasowych przy imporcie.

Generator firmy syntetycznej zostaje naiwny — konwersję pokrywa ta fixture: plik PROCESS
ze znacznikami ze strefą, pisany wprost w teście, żeby każdy przypadek był widoczny tam,
gdzie jest sprawdzany.
"""

import datetime as dt
from pathlib import Path

import pytest

from xray.ingest import LoadResult, RejectionCategory, load_table
from xray.ingest.timezone import load_organization_zone
from xray.mapping import MappingProfile, ProfileError
from xray.model import get_table
from xray.store import RunRef
from xray.validation import ValidationContext, run_check

ZBIOR = "klient-testowy"
STREFA = "Europe/Warsaw"
NAGLOWEK = "case_id,stage,start,end,unit\n"


def wczytaj(
    tmp_path: Path,
    wiersze: list[str],
    *,
    strefa: str | None = STREFA,
    nazwa: str = "proces.csv",
) -> LoadResult:
    sciezka = tmp_path / nazwa
    sciezka.write_text(NAGLOWEK + "".join(f"{w}\n" for w in wiersze), encoding="utf-8")
    return load_table(sciezka, "PROCESS", dataset_id=ZBIOR, organization_timezone=strefa)


def poczatki(wynik: LoadResult) -> list[dt.datetime]:
    return [wartosc.to_pydatetime() for wartosc in wynik.frame["start"]]


# --- granice po konwersji ------------------------------------------------------------------


def test_przejscie_przez_granice_dnia(tmp_path: Path) -> None:
    wynik = wczytaj(tmp_path, ["SPR-1,rej,2026-01-15T23:30:00Z,,A"])
    assert poczatki(wynik) == [dt.datetime(2026, 1, 16, 0, 30)]
    assert wynik.report.timestamps_converted == 1


def test_przejscie_przez_granice_miesiaca_widzi_kontrola_8(tmp_path: Path) -> None:
    """Instant z 31 stycznia UTC to 1 lutego w Warszawie — i kontrola 8 ma to zobaczyć."""
    wynik = wczytaj(tmp_path, ["SPR-1,rej,2026-01-31T23:30:00Z,,A"])
    assert poczatki(wynik) == [dt.datetime(2026, 2, 1, 0, 30)]

    kontekst = ValidationContext(
        table=get_table("PROCESS"), frame=wynik.frame, import_reports=(wynik.report,)
    )
    zakres = run_check("TECH01-VAL-08", kontekst)
    period_min = next(o for o in zakres.observations if o.measure == "period_min")
    assert period_min.text_value.startswith("2026-02-01")


def test_koniec_etapu_tez_jest_przeliczany(tmp_path: Path) -> None:
    wynik = wczytaj(tmp_path, ["SPR-1,rej,2026-07-01T08:00:00+00:00,2026-07-01T10:30:00+02:00,A"])
    assert poczatki(wynik) == [dt.datetime(2026, 7, 1, 10, 0)]
    assert wynik.frame["end"].iloc[0].to_pydatetime() == dt.datetime(2026, 7, 1, 10, 30)
    assert wynik.report.timestamps_converted == 2


# --- zmiana czasu ----------------------------------------------------------------------------


def test_wiosenna_zmiana_czasu_nie_produkuje_godziny_z_luki(tmp_path: Path) -> None:
    """Luka 02:00–02:59 nie istnieje lokalnie, a konwersja do czasu lokalnego jej nie tworzy."""
    wynik = wczytaj(
        tmp_path,
        ["SPR-1,rej,2026-03-29T00:30:00Z,,A", "SPR-2,rej,2026-03-29T01:30:00Z,,A"],
    )
    assert poczatki(wynik) == [
        dt.datetime(2026, 3, 29, 1, 30),
        dt.datetime(2026, 3, 29, 3, 30),
    ]
    assert wynik.report.ambiguous_local_time_count == 0


def test_jesienna_zmiana_czasu_scala_w_ramce_i_zapisuje_przesuniecie(tmp_path: Path) -> None:
    """B-07, wariant D: dwa instanty, jedna wartość w ramce, rozróżnienie w raporcie."""
    wynik = wczytaj(
        tmp_path,
        ["SPR-1,rej,2026-10-25T00:30:00Z,,A", "SPR-2,rej,2026-10-25T01:30:00Z,,A"],
    )
    assert poczatki(wynik) == [dt.datetime(2026, 10, 25, 2, 30)] * 2

    wpisy = wynik.report.ambiguous_local_times
    assert wynik.report.ambiguous_local_time_count == 2
    assert [w.local_utc_offset for w in wpisy] == ["+02:00", "+01:00"]
    assert [w.source_value for w in wpisy] == ["2026-10-25T00:30:00Z", "2026-10-25T01:30:00Z"]
    assert [w.field for w in wpisy] == ["start", "start"]
    assert [w.file_row for w in wpisy] == [2, 3]
    assert [w.row_id for w in wpisy] == list(wynik.frame.index)


def test_instant_jest_odtwarzalny_z_raportu(tmp_path: Path) -> None:
    """Scalenie w ramce nie jest utratą, dopóki raport pozwala odtworzyć instant."""
    zrodla = ["2026-10-25T00:30:00Z", "2026-10-25T01:30:00Z"]
    wynik = wczytaj(tmp_path, [f"SPR-{i},rej,{z},,A" for i, z in enumerate(zrodla)])
    for wpis, zrodlo in zip(wynik.report.ambiguous_local_times, zrodla, strict=True):
        godziny, minuty = wpis.local_utc_offset[1:].split(":")
        przesuniecie = dt.timedelta(hours=int(godziny), minutes=int(minuty))
        odtworzony = (wpis.local_value - przesuniecie).replace(tzinfo=dt.UTC)
        assert odtworzony == dt.datetime.fromisoformat(zrodlo)


def test_godzina_niejednoznaczna_zapisana_z_lokalnym_przesunieciem(tmp_path: Path) -> None:
    """Źródło może już podawać czas lokalny z przesunięciem — scalenie jest to samo."""
    wynik = wczytaj(
        tmp_path,
        ["SPR-1,rej,2026-10-25T02:30:00+02:00,,A", "SPR-2,rej,2026-10-25T02:30:00+01:00,,A"],
    )
    assert poczatki(wynik) == [dt.datetime(2026, 10, 25, 2, 30)] * 2
    assert [w.local_utc_offset for w in wynik.report.ambiguous_local_times] == [
        "+02:00",
        "+01:00",
    ]


def test_licznik_niejednoznacznych_jest_ogloszony_takze_gdy_zero(tmp_path: Path) -> None:
    """Brak pola znaczyłby jednocześnie „nie było" i „nie sprawdzaliśmy"."""
    z_deklaracja = wczytaj(tmp_path, ["SPR-1,rej,2026-03-01T08:30:00+01:00,,A"], nazwa="a.csv")
    bez_deklaracji = wczytaj(
        tmp_path, ["SPR-1,rej,2026-03-01T08:30:00,,A"], strefa=None, nazwa="b.csv"
    )
    for wynik in (z_deklaracja, bez_deklaracji):
        assert wynik.report.ambiguous_local_time_count == 0
        assert wynik.report.model_dump()["ambiguous_local_time_count"] == 0


def test_raport_bez_licznikow_nie_powstaje() -> None:
    """Wartości domyślnej nie ma celowo: raport musi powiedzieć, co sprawdził."""
    from xray.ingest import ImportReport, SourceRef

    with pytest.raises(ValueError):
        ImportReport(
            table_name="PROCESS",
            source=SourceRef.create(dataset_id=ZBIOR, source_file="x.csv", source_path="x"),
            content_digest="0" * 32,
        )


# --- wartości, których konwersja nie dotyczy -------------------------------------------------


def test_znacznik_bez_strefy_zostaje_bez_zmian(tmp_path: Path) -> None:
    wynik = wczytaj(tmp_path, ["SPR-1,rej,2026-03-01T08:30:00,,A"])
    assert poczatki(wynik) == [dt.datetime(2026, 3, 1, 8, 30)]
    assert wynik.report.timestamps_converted == 0


def test_brak_deklaracji_strefy_to_wlasna_kategoria_odrzucenia(tmp_path: Path) -> None:
    """D2: nie wspólny worek z błędami parsowania."""
    wynik = wczytaj(tmp_path, ["SPR-1,rej,2026-03-01T08:30:00+01:00,,A"], strefa=None)
    assert wynik.report.records_rejected == 1
    assert wynik.report.organization_timezone is None
    odrzucenie = wynik.report.rejections[0]
    assert odrzucenie.category is RejectionCategory.MISSING_TIMEZONE_DECLARATION
    assert odrzucenie.fields == ("start",)


def test_brak_deklaracji_strefy_zglasza_kontrola_2_osobna_miara(tmp_path: Path) -> None:
    wynik = wczytaj(tmp_path, ["SPR-1,rej,2026-03-01T08:30:00+01:00,,A"], strefa=None)
    kontekst = ValidationContext(
        table=get_table("PROCESS"), frame=wynik.frame, import_reports=(wynik.report,)
    )
    kontrola = run_check("TECH01-VAL-02", kontekst)
    assert {o.measure for o in kontrola.observations} == {
        "rows_rejected_missing_timezone_declaration"
    }
    assert kontrola.status.value == "WARNING"


def test_kategoria_braku_deklaracji_wchodzi_do_tozsamosci_przebiegu(tmp_path: Path) -> None:
    """Od D1 kategoria jest częścią kontraktu: widać ją w podstawie run_id."""
    bez = wczytaj(
        tmp_path, ["SPR-1,rej,2026-03-01T08:30:00+01:00,,A"], strefa=None, nazwa="a.csv"
    )
    z = wczytaj(tmp_path, ["SPR-1,rej,2026-03-01T08:30:00+01:00,,A"], nazwa="b.csv")
    przebieg_bez = RunRef.create(dataset_id=ZBIOR, reports=[bez.report])
    przebieg_z = RunRef.create(dataset_id=ZBIOR, reports=[z.report])
    assert "missing_timezone_declaration" in przebieg_bez.input_digest
    assert przebieg_bez.run_id != przebieg_z.run_id


def test_konwersja_jest_deterministyczna(tmp_path: Path) -> None:
    wiersze = ["SPR-1,rej,2026-10-25T00:30:00Z,2026-10-25T01:30:00Z,A"]
    a = wczytaj(tmp_path, wiersze, nazwa="a.csv")
    b = wczytaj(tmp_path, wiersze, nazwa="b.csv")
    assert a.report.content_digest == b.report.content_digest

    def istota(wynik: LoadResult) -> list[tuple[str, dt.datetime, str]]:
        return [
            (w.field, w.local_value, w.local_utc_offset)
            for w in wynik.report.ambiguous_local_times
        ]

    assert istota(a) == istota(b) == [
        ("start", dt.datetime(2026, 10, 25, 2, 30), "+02:00"),
        ("end", dt.datetime(2026, 10, 25, 2, 30), "+01:00"),
    ]


# --- deklaracja strefy -------------------------------------------------------------------------


def test_nieznana_strefa_jest_bledem_przed_odczytem(tmp_path: Path) -> None:
    with pytest.raises(ValueError) as blad:
        wczytaj(tmp_path, ["SPR-1,rej,2026-03-01T08:30:00Z,,A"], strefa="Europe/Atlantyda")
    assert "Europe/Atlantyda" in str(blad.value)


@pytest.mark.parametrize("nazwa", ["", "../tzdata", "Europe/", "/Europe/Warsaw"])
def test_niepoprawna_nazwa_strefy_jest_odrzucana(nazwa: str) -> None:
    with pytest.raises(ValueError):
        load_organization_zone(nazwa)


def test_profil_z_nieznana_strefa_jest_bledny(tmp_path: Path) -> None:
    sciezka = tmp_path / "profil.yaml"
    sciezka.write_text(
        "profile_id: p\nprofile_version: 1\ndataset_id: d\n"
        "organization_timezone: Nie/Istnieje\ncolumns: {}\nplan_metrics: []\n",
        encoding="utf-8",
    )
    with pytest.raises(ProfileError) as blad:
        MappingProfile.load(sciezka)
    assert "Nie/Istnieje" in str(blad.value)
