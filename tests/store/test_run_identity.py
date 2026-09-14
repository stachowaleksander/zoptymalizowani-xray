# Sprawdza tożsamość przebiegu po korekcie: jawne zestawienie odrzuceń i pełny klucz
# porządkowania wejść (RUN_IDENTITY_VERSION "3").
"""Testy regresyjne tożsamości przebiegu.

Raporty importu są tu budowane wprost, a nie przez ``load_table``: każdy test ma zmienić
**jedną** cechę odrzuceń i trzymać resztę stałą. Plik z danymi zmieniałby przy okazji
treść przyjętych rekordów i test przechodziłby z niewłaściwego powodu (DT-16).
"""

from pathlib import Path

from xray.ingest import load_table
from xray.ingest.report import ImportReport, Rejection, RejectionCategory, SourceRef
from xray.store import RunRef

ZBIOR = "klient-testowy"
SKROT_PUSTEGO_STRUMIENIA = "cae66941d9efbd404e4d88758ea67670"


def odrzucenie(
    kategoria: RejectionCategory = RejectionCategory.MISSING_VALUE,
    pola: tuple[str, ...] = ("unit",),
    wiersz: int = 2,
    powod: str = "unit: pole wymagane",
) -> Rejection:
    return Rejection(file_row=wiersz, reason=powod, category=kategoria, fields=pola)


def raport(*odrzucenia: Rejection, plik: str = "koszty.csv") -> ImportReport:
    """Raport tabeli COST w całości odrzuconej — przyjętej treści brak."""
    return ImportReport(
        table_name="COST",
        source=SourceRef.create(dataset_id=ZBIOR, source_file=plik, source_path=plik),
        records_accepted=0,
        records_rejected=len(odrzucenia),
        content_digest=SKROT_PUSTEGO_STRUMIENIA,
        rejections=odrzucenia,
        timestamps_converted=0,
        ambiguous_local_times=(),
    )


def przebieg(*raporty: ImportReport) -> RunRef:
    return RunRef.create(dataset_id=ZBIOR, reports=list(raporty))


# --- co wchodzi do tożsamości ---------------------------------------------------------


def test_inna_kategoria_odrzucenia_daje_inny_przebieg() -> None:
    """Ta sama liczba odrzuceń, te same pola, inny powód — inny obraz jakości danych.

    Przed korektą oba przebiegi miały ten sam run_id, bo do tożsamości wchodziła tylko
    liczba odrzuconych wierszy.
    """
    brak = przebieg(raport(odrzucenie(RejectionCategory.MISSING_VALUE, ("amount",))))
    format_ = przebieg(raport(odrzucenie(RejectionCategory.INVALID_FORMAT, ("amount",))))
    assert brak.run_id != format_.run_id


def test_inne_pola_odrzucenia_daja_inny_przebieg() -> None:
    """Ta sama kategoria na innym polu to inna semantyka odrzucenia."""
    na_unit = przebieg(raport(odrzucenie(pola=("unit",))))
    na_date = przebieg(raport(odrzucenie(pola=("date",))))
    assert na_unit.run_id != na_date.run_id


def test_inna_licznosc_tego_samego_odrzucenia_daje_inny_przebieg() -> None:
    jedno = przebieg(raport(odrzucenie(wiersz=2)))
    dwa = przebieg(raport(odrzucenie(wiersz=2), odrzucenie(wiersz=3)))
    assert jedno.run_id != dwa.run_id


# --- czego do tożsamości świadomie nie wpuszczamy -------------------------------------


def test_proza_komunikatu_nie_zmienia_przebiegu() -> None:
    """Poprawka literówki w komunikacie nie może tworzyć nowego przebiegu."""
    a = przebieg(raport(odrzucenie(powod="unit: pole wymagane")))
    b = przebieg(raport(odrzucenie(powod="unit: pole wymagane (poprawiony opis)")))
    assert a.run_id == b.run_id


def test_numer_wiersza_nie_zmienia_przebiegu() -> None:
    """Pozycja wiersza nie jest semantyką odrzucenia."""
    a = przebieg(raport(odrzucenie(wiersz=2)))
    b = przebieg(raport(odrzucenie(wiersz=40)))
    assert a.run_id == b.run_id


def test_kolejnosc_pol_w_odrzuceniu_nie_zmienia_przebiegu() -> None:
    """Kolejność, w jakiej walidator zgłosił błędy, nie jest cechą danych."""
    a = przebieg(raport(odrzucenie(pola=("unit", "amount"))))
    b = przebieg(raport(odrzucenie(pola=("amount", "unit"))))
    assert a.run_id == b.run_id


# --- porządek wejść ----------------------------------------------------------------------


def test_kolejnosc_wejsc_przy_remisie_nie_zmienia_przebiegu() -> None:
    """Przypadek, którego nie domykał dawny klucz (table_name, content_digest).

    Jedna tabela z dwóch plików, oba w całości odrzucone: ta sama nazwa tabeli, ten sam
    skrót pustego strumienia, różne odrzucenia. Sortowanie stabilne przenosiło kolejność
    wywołań importu do run_id.
    """
    a = raport(odrzucenie(pola=("unit",)), plik="koszty_2025.csv")
    b = raport(
        odrzucenie(RejectionCategory.INVALID_FORMAT, ("amount",)),
        odrzucenie(RejectionCategory.INVALID_FORMAT, ("amount",), wiersz=3),
        plik="koszty_2026.csv",
    )
    assert a.content_digest == b.content_digest
    assert przebieg(a, b).run_id == przebieg(b, a).run_id


# --- identyczne wejście ---------------------------------------------------------------


def test_identyczne_wejscie_daje_identyczny_przebieg(tmp_path: Path) -> None:
    """Na prawdziwym imporcie: dwa niezależne wczytania pliku z odrzuceniami."""
    tresc = (
        "date,unit,category,amount\n"
        "2026-01-01,Dział A,wynagrodzenia,100\n"
        "2026-02-01,,materiały,200\n"
        "2026-03-01,Dział A,materiały,sto\n"
    )
    raporty = []
    for katalog in ("a", "b"):
        (tmp_path / katalog).mkdir()
        sciezka = tmp_path / katalog / "koszty.csv"
        sciezka.write_text(tresc, encoding="utf-8")
        raporty.append(load_table(sciezka, "COST", dataset_id=ZBIOR).report)
    assert przebieg(raporty[0]).run_id == przebieg(raporty[1]).run_id


# --- jawność ----------------------------------------------------------------------------


def test_zestawienie_odrzucen_jest_jawne_w_podstawie_identyfikatora() -> None:
    """Przy sprzeczności ma dać się odczytać, czym różniły się przebiegi — nie tylko że się
    różniły."""
    run = przebieg(raport(odrzucenie(RejectionCategory.INVALID_FORMAT, ("amount",))))
    assert '"category":"invalid_format"' in run.input_digest
    assert '"fields":["amount"]' in run.input_digest
    assert "file_row" not in run.input_digest
    assert "reason" not in run.input_digest


def test_zestawienie_jest_uporzadkowane_i_zlicza_powtorzenia() -> None:
    zestawienie = raport(
        odrzucenie(RejectionCategory.MISSING_VALUE, ("unit",), wiersz=5),
        odrzucenie(RejectionCategory.INVALID_FORMAT, ("amount",), wiersz=3),
        odrzucenie(RejectionCategory.MISSING_VALUE, ("unit",), wiersz=2),
    ).rejection_summary
    assert [(z.category, z.fields, z.count) for z in zestawienie] == [
        (RejectionCategory.INVALID_FORMAT, ("amount",), 1),
        (RejectionCategory.MISSING_VALUE, ("unit",), 2),
    ]
