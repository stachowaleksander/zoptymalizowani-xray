# Sprawdza egzekwowanie par porównawczych: pola dzielące jedną kolumnę klienta.
"""Testy reguły „różnica między dwoma polami niesie sygnał".

Klasa błędu jest ta sama co w DT-07 — fałszywie przechodząca kontrola — tylko wpuszczona
przez konfigurację zamiast przez kod. Deklaruje kontrola, egzekwuje rejestr.
"""

from pathlib import Path

import pytest

from xray.ingest import load_table
from xray.model import ValidationStatus, get_table
from xray.validation import (
    NotAssessedReason,
    ValidationContext,
    get_declaration,
    run_check,
)
from xray.validation.base import Determines

ZBIOR = "klient-testowy"


def kontekst(tmp_path: Path, nazwa: str, tresc: str, tabela: str, mapa: dict):
    sciezka = tmp_path / nazwa
    sciezka.write_text(tresc, encoding="utf-8")
    wynik = load_table(sciezka, tabela, dataset_id=ZBIOR, column_map=mapa)
    return ValidationContext(
        table=get_table(tabela), frame=wynik.frame, import_reports=(wynik.report,)
    )


# --- wykrywanie wspólnego źródła ------------------------------------------------------


def test_kontekst_rozpoznaje_wspolne_zrodlo(tmp_path: Path) -> None:
    ctx = kontekst(
        tmp_path,
        "z.csv",
        "Miesiac,Komorka,Zasob,Godziny\n2026-01-01,Dział A,gabinet,160\n",
        "RESOURCE",
        {
            "date": "Miesiac",
            "unit": "Komorka",
            "resource": "Zasob",
            "available": "Godziny",
            "used": "Godziny",
        },
    )
    assert ctx.share_source("available", "used") == "Godziny"


def test_rozne_kolumny_nie_dziela_zrodla(tmp_path: Path) -> None:
    ctx = kontekst(
        tmp_path,
        "z.csv",
        "Miesiac,Komorka,Zasob,Dostepne,Uzyte\n2026-01-01,Dział A,gabinet,160,132\n",
        "RESOURCE",
        {
            "date": "Miesiac",
            "unit": "Komorka",
            "resource": "Zasob",
            "available": "Dostepne",
            "used": "Uzyte",
        },
    )
    assert ctx.share_source("available", "used") is None


def test_brak_wiedzy_o_imporcie_nie_jest_wspolnym_zrodlem() -> None:
    """Brak wiedzy nie jest wiedzą — nie orzekamy o wspólnym źródle bez podstawy."""
    import pandas as pd

    ctx = ValidationContext(table=get_table("RESOURCE"), frame=pd.DataFrame())
    assert ctx.column_sources() == {}
    assert ctx.share_source("available", "used") is None


# --- para STATUS: kontrola 7 ----------------------------------------------------------


def test_kontrola_7_deklaruje_pare_statusowa() -> None:
    para = get_declaration("TECH01-VAL-07").comparison_pairs[0]
    assert para.fields == ("available", "used")
    assert para.determines is Determines.STATUS


def test_wspolna_kolumna_uniewaznia_cala_kontrole_7(tmp_path: Path) -> None:
    """Bez tej różnicy kontrola 7 nie ma czego ogłosić — PASS byłby fałszywy."""
    ctx = kontekst(
        tmp_path,
        "z.csv",
        "Miesiac,Komorka,Zasob,Godziny\n2026-01-01,Dział A,gabinet,160\n",
        "RESOURCE",
        {
            "date": "Miesiac",
            "unit": "Komorka",
            "resource": "Zasob",
            "available": "Godziny",
            "used": "Godziny",
        },
    )
    wynik = run_check("TECH01-VAL-07", ctx)
    assert wynik.status is None
    assert wynik.not_assessed_reason is NotAssessedReason.INSUFFICIENT_BASIS
    assert "Godziny" in wynik.basis
    assert "fałszywym" in wynik.basis


def test_rozne_kolumny_pozwalaja_kontroli_7_dzialac(tmp_path: Path) -> None:
    ctx = kontekst(
        tmp_path,
        "z.csv",
        "Miesiac,Komorka,Zasob,Dostepne,Uzyte\n2026-01-01,Dział A,gabinet,160,190\n",
        "RESOURCE",
        {
            "date": "Miesiac",
            "unit": "Komorka",
            "resource": "Zasob",
            "available": "Dostepne",
            "used": "Uzyte",
        },
    )
    assert run_check("TECH01-VAL-07", ctx).status is ValidationStatus.WARNING


# --- para OBSERVATION: kontrola 8 -----------------------------------------------------


def test_kontrola_8_deklaruje_pare_obserwacyjna() -> None:
    para = get_declaration("TECH01-VAL-08").comparison_pairs[0]
    assert para.fields == ("start", "end")
    assert para.determines is Determines.OBSERVATION


def test_wspolna_kolumna_zeruje_tylko_dotkniete_obserwacje(tmp_path: Path) -> None:
    """Reszta wyniku zostaje prawdziwa: kasowanie całości odejmowałoby informację."""
    ctx = kontekst(
        tmp_path,
        "p.csv",
        "Nr,Etap,Czas,Komorka\nSPR-1,rej,2026-03-01T08:00:00,A\n"
        "SPR-2,rej,2026-05-04T08:00:00,A\n",
        "PROCESS",
        {"case_id": "Nr", "stage": "Etap", "start": "Czas", "end": "Czas", "unit": "Komorka"},
    )
    wynik = run_check("TECH01-VAL-08", ctx)

    # Status zostaje — kontrola 8 dla tabeli zdarzeniowej i tak ogłasza PASS (A-01).
    assert wynik.status is ValidationStatus.PASS

    dotkniete = {
        o.measure: o
        for o in wynik.observations
        if o.measure in ("months_with_stage_starts", "months_with_stage_ends")
    }
    assert len(dotkniete) == 2
    for obserwacja in dotkniete.values():
        assert obserwacja.is_unknown
        assert "artefaktem konfiguracji" in obserwacja.basis

    nietkniete = {o.measure for o in wynik.observations if not o.is_unknown}
    assert "months_without_events" in nietkniete


def test_rozne_kolumny_zostawiaja_obserwacje_kontroli_8(tmp_path: Path) -> None:
    ctx = kontekst(
        tmp_path,
        "p.csv",
        "Nr,Etap,Poczatek,Koniec,Komorka\n"
        "SPR-1,rej,2026-03-01T08:00:00,2026-05-02T09:00:00,A\n",
        "PROCESS",
        {
            "case_id": "Nr",
            "stage": "Etap",
            "start": "Poczatek",
            "end": "Koniec",
            "unit": "Komorka",
        },
    )
    wynik = run_check("TECH01-VAL-08", ctx)
    miary = {o.measure: o.value for o in wynik.observations}
    assert miary["months_with_stage_starts"] == 1.0
    assert miary["months_with_stage_ends"] == 1.0


def test_para_nieobecna_w_tabeli_jest_pomijana(tmp_path: Path) -> None:
    """start i end nie istnieją w tabeli okresowej — para nie ma zastosowania."""
    ctx = kontekst(
        tmp_path,
        "k.csv",
        "Miesiac,Komorka,Rodzaj,Kwota\n2026-01-01,Dział A,wyn,100\n",
        "COST",
        {"date": "Miesiac", "unit": "Komorka", "category": "Rodzaj", "amount": "Kwota"},
    )
    assert run_check("TECH01-VAL-08", ctx).status is ValidationStatus.PASS


# --- pozostałe kontrole nie są dotknięte ----------------------------------------------


def test_wspolne_zrodlo_nie_psuje_kontroli_6(tmp_path: Path) -> None:
    """Kontrola 6 szuka wariantów WEWNĄTRZ pola, nie porównuje pól ze sobą.

    Uprawniony przykład z D-C: jedna kolumna zasila unit i resource.
    """
    ctx = kontekst(
        tmp_path,
        "z.csv",
        "Miesiac,Nazwa,Dostepne,Uzyte\n2026-01-01,Dział A,160,132\n"
        "2026-02-01,DZIAL_A,160,140\n",
        "RESOURCE",
        {
            "date": "Miesiac",
            "unit": "Nazwa",
            "resource": "Nazwa",
            "available": "Dostepne",
            "used": "Uzyte",
        },
    )
    wynik = run_check("TECH01-VAL-06", ctx)
    assert wynik.status is ValidationStatus.WARNING
    assert any(o.value == 2.0 for o in wynik.observations)


@pytest.mark.parametrize(
    "check_id", ["TECH01-VAL-02", "TECH01-VAL-03", "TECH01-VAL-04", "TECH01-VAL-05"]
)
def test_kontrole_bez_par_nie_deklaruja_ich(check_id: str) -> None:
    """Wśród siedmiu tylko 7 i 8 mają sygnał w różnicy między polami."""
    assert get_declaration(check_id).comparison_pairs == ()


# --- wyłączenia miar (unaffected_measures) --------------------------------------------


def test_granice_zakresu_przezywaja_wspolna_kolumne(tmp_path: Path) -> None:
    """Test strażniczy: min i max nadal opisują rzeczywisty zakres danych.

    A-01 wymienia granice wprost jako to, co kontroli 8 WOLNO zwracać: „period_min =
    min(start), period_max = max(end) oraz rozpiętość między nimi — to jest zakres danych,
    a nie przypisanie". Zerowanie ich kasowałoby część wyniku, którą rozstrzygnięcie
    jawnie dopuszcza.
    """
    ctx = kontekst(
        tmp_path,
        "p.csv",
        "Nr,Etap,Czas,Komorka\nSPR-1,rej,2026-03-01T08:00:00,A\n"
        "SPR-2,rej,2026-05-04T08:00:00,A\n",
        "PROCESS",
        {"case_id": "Nr", "stage": "Etap", "start": "Czas", "end": "Czas", "unit": "Komorka"},
    )
    wynik = run_check("TECH01-VAL-08", ctx)
    granice = {
        o.measure: o for o in wynik.observations if o.measure in ("period_min", "period_max")
    }
    assert len(granice) == 2
    for obserwacja in granice.values():
        assert not obserwacja.is_unknown, obserwacja.measure
    assert granice["period_min"].text_value.startswith("2026-03-01")
    assert granice["period_max"].text_value.startswith("2026-05-04")


def test_wylaczenie_jest_zadeklarowane_a_nie_domyslne() -> None:
    """Domyślna ostrożność jest po stronie zerowania: wyjątek trzeba zadeklarować."""
    para = get_declaration("TECH01-VAL-08").comparison_pairs[0]
    assert para.unaffected_measures == ("period_min", "period_max")
    assert get_declaration("TECH01-VAL-07").comparison_pairs[0].unaffected_measures == ()


def test_wylaczenia_nie_maja_sensu_przy_parze_statusowej() -> None:
    """Para STATUS unieważnia cały wynik, więc nie ma czego wyłączać."""
    from xray.validation.base import ComparisonPair, Determines

    with pytest.raises(ValueError) as blad:
        ComparisonPair(
            fields=("a", "b"),
            determines=Determines.STATUS,
            unaffected_measures=("cokolwiek",),
        )
    assert "STATUS" in str(blad.value)


def test_is_unknown_jest_definicja_kontraktu() -> None:
    """Definicja „nieznane" ma być jedna i wystawiona, a nie odtwarzana w każdym teście."""
    from xray.validation import CheckObservation

    nieznana = CheckObservation.create(subject="x", measure="m", basis="b")
    liczbowa = CheckObservation.create(subject="x", measure="m", value=0.0, basis="b")
    tekstowa = CheckObservation.create(subject="x", measure="m", text_value="a", basis="b")
    assert nieznana.is_unknown
    assert not liczbowa.is_unknown  # zero jest wiedzą, nie brakiem
    assert not tekstowa.is_unknown
