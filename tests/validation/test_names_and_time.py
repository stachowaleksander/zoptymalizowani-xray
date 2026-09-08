# Sprawdza kontrole 6 i 8 z ZOP-TECH-01 v0.1 pkt 5.3 oraz rozstrzygnięcie A-01.
"""Testy kontroli 6 (niespójne nazwy) i 8 (zakres czasowy).

Obie są trudniejsze od pozostałych: kontrola 6 jako jedyna stawia hipotezę, a kontrola 8
działa inaczej dla danych okresowych i zdarzeniowych. Testy pilnują przede wszystkim
granic: co kontrola ma prawo powiedzieć, a czego nie.
"""

from pathlib import Path

import pandas as pd
import pytest

from xray.ingest import load_table
from xray.model import ValidationStatus, get_table
from xray.validation import (
    OBSERVATION_LIMIT,
    TEXT_VALUE_LIMIT,
    CheckObservation,
    CheckOutcome,
    ValidationContext,
    cap_observations,
    get_declaration,
    registered_check_ids,
    run_check,
)
from xray.validation.checks.inconsistent_names import comparison_key

ZBIOR = "firma-syntetyczna"


def zbuduj_kontekst(tmp_path: Path, tresc: str, tabela: str = "COST"):
    sciezka = tmp_path / f"{tabela.lower()}.csv"
    sciezka.write_text(tresc, encoding="utf-8")
    wynik = load_table(sciezka, tabela, dataset_id=ZBIOR)
    return ValidationContext(
        table=get_table(tabela), frame=wynik.frame, import_reports=(wynik.report,)
    )


def obserwacja(wynik, measure: str, subject: str | None = None) -> CheckObservation:
    for o in wynik.observations:
        if o.measure == measure and (subject is None or o.subject == subject):
            return o
    raise AssertionError(f"brak obserwacji {measure} / {subject}")


# --- kontrola 6: normalizacja porównawcza --------------------------------------------


def test_przyklad_z_karty_trafia_do_jednej_grupy() -> None:
    """ZOP-TECH-01 pkt 5.3 kontrola 6 podaje trzy wartości jednej rzeczy.

    Ten test wyłapał realny błąd: NFKD nie rozkłada litery ł, więc bez jawnej podmiany
    „Dział A" i „DZIAL_A" trafiały do dwóch różnych grup — czyli normalizacja nie
    spełniała przykładu, dla którego powstała.
    """
    warianty = ("Dział A", "dział A", "DZIAL_A")
    assert len({comparison_key(w) for w in warianty}) == 1
    assert comparison_key("Dział A") == "dzial a"


def test_normalizacja_nie_sklei_roznych_wartosci() -> None:
    assert comparison_key("Dział A") != comparison_key("Dział B")


def test_normalizacja_obejmuje_cztery_kroki() -> None:
    """Wielkość liter, diakrytyka, znaki rozdzielające, białe znaki."""
    assert comparison_key("DZIAŁ A") == comparison_key("dział a")  # wielkość liter
    assert comparison_key("Dział") == comparison_key("Dzial")  # diakrytyka
    assert comparison_key("dzial-a") == comparison_key("dzial_a")  # rozdzielające
    assert comparison_key("  dzial   a  ") == comparison_key("dzial a")  # białe znaki


def test_klucz_porownawczy_nie_trafia_do_danych(tmp_path: Path) -> None:
    """Kontrola niczego nie scala ani nie poprawia — ramka zostaje nietknięta."""
    tresc = (
        "date,unit,category,amount\n"
        "2026-01-01,Dział A,wyn,100\n"
        "2026-02-01,DZIAL_A,wyn,200\n"
    )
    ctx = zbuduj_kontekst(tmp_path, tresc)
    przed = ctx.frame.copy()
    run_check("TECH01-VAL-06", ctx)
    pd.testing.assert_frame_equal(ctx.frame, przed)
    assert set(ctx.frame["unit"]) == {"Dział A", "DZIAL_A"}


def test_wartosc_to_liczba_wariantow_a_nie_wierszy(tmp_path: Path) -> None:
    """To dwie różne wielkości; pomylenie ich dałoby liczbę bez znaczenia."""
    tresc = (
        "date,unit,category,amount\n"
        "2026-01-01,Dział A,wyn,100\n"
        "2026-02-01,Dział A,mat,150\n"
        "2026-03-01,DZIAL_A,wyn,200\n"
    )
    obs = obserwacja(
        run_check("TECH01-VAL-06", zbuduj_kontekst(tmp_path, tresc)),
        "similar_value_variants",
        "dzial a",
    )
    assert obs.value == 2.0  # dwa warianty
    assert len(obs.evidence_row_ids) == 3  # trzy wiersze


def test_regula_normalizacji_jest_w_podstawie(tmp_path: Path) -> None:
    """Inaczej klient dostaje zarzut bez możliwości sprawdzenia, na jakiej podstawie."""
    tresc = (
        "date,unit,category,amount\n"
        "2026-01-01,Dział A,wyn,100\n"
        "2026-02-01,DZIAL_A,wyn,200\n"
    )
    obs = obserwacja(
        run_check("TECH01-VAL-06", zbuduj_kontekst(tmp_path, tresc)),
        "similar_value_variants",
    )
    for element in ("wielkość liter", "diakrytyka", "znaki rozdzielające", "białe znaki"):
        assert element in obs.basis
    assert "Dział A" in obs.basis and "DZIAL_A" in obs.basis
    assert "hipoteza" in obs.basis


def test_kontrola_6_obejmuje_case_id(tmp_path: Path) -> None:
    """Ta sama sprawa policzona dwa razy jest poważniejsza niż niespójna nazwa działu."""
    tresc = (
        "case_id,stage,start,end,unit\n"
        "SPR-001,rejestracja,2026-01-01T08:00:00,,A\n"
        "spr_001,wydanie,2026-01-02T08:00:00,,A\n"
    )
    wynik = run_check("TECH01-VAL-06", zbuduj_kontekst(tmp_path, tresc, "PROCESS"))
    assert wynik.status is ValidationStatus.WARNING
    assert obserwacja(wynik, "similar_value_variants", "spr 001").value == 2.0


def test_kontrola_6_nie_moze_nadac_critical() -> None:
    """Hipoteza tożsamości nie jest faktem (zasada 6)."""
    assert get_declaration("TECH01-VAL-06").max_status is ValidationStatus.WARNING


def test_spojne_nazwy_daja_pass(tmp_path: Path) -> None:
    tresc = (
        "date,unit,category,amount\n"
        "2026-01-01,Dział A,wyn,100\n"
        "2026-02-01,Dział B,wyn,200\n"
    )
    assert (
        run_check("TECH01-VAL-06", zbuduj_kontekst(tmp_path, tresc)).status
        is ValidationStatus.PASS
    )


# --- kontrola 8: tabele okresowe -----------------------------------------------------

LUKI = (
    "date,unit,category,amount\n"
    "2026-01-15,A,wyn,100\n"
    "2026-03-02,A,wyn,200\n"
    "2026-06-30,A,wyn,300\n"
)


def test_kontrola_8_opisuje_zakres_tabeli_okresowej(tmp_path: Path) -> None:
    wynik = run_check("TECH01-VAL-08", zbuduj_kontekst(tmp_path, LUKI))
    assert obserwacja(wynik, "period_min").text_value == "2026-01-15"
    assert obserwacja(wynik, "period_max").text_value == "2026-06-30"
    assert obserwacja(wynik, "months_in_range").value == 6.0
    assert obserwacja(wynik, "months_covered").value == 3.0
    assert obserwacja(wynik, "months_missing").value == 3.0


def test_brakujacy_miesiac_w_tabeli_okresowej_to_luka(tmp_path: Path) -> None:
    wynik = run_check("TECH01-VAL-08", zbuduj_kontekst(tmp_path, LUKI))
    assert wynik.status is ValidationStatus.WARNING
    puste = {o.subject for o in wynik.observations if o.measure == "month_without_data"}
    assert puste == {"2026-02", "2026-04", "2026-05"}


def test_zero_w_miesiacu_bez_danych_jest_wiedza(tmp_path: Path) -> None:
    """Wiemy, że nie ma tam ani jednego wiersza — to nie jest „nieznane"."""
    wynik = run_check("TECH01-VAL-08", zbuduj_kontekst(tmp_path, LUKI))
    for o in wynik.observations:
        if o.measure == "month_without_data":
            assert o.value == 0.0


def test_ciagly_szereg_daje_pass(tmp_path: Path) -> None:
    tresc = "date,unit,category,amount\n2026-01-01,A,wyn,100\n2026-02-01,A,wyn,200\n"
    assert (
        run_check("TECH01-VAL-08", zbuduj_kontekst(tmp_path, tresc)).status
        is ValidationStatus.PASS
    )


def test_typ_kolumny_zrodlowej_zostaje_nietkniety(tmp_path: Path) -> None:
    """Wpis DT-08: kolumna pochodna wystarcza, więc dat nie zamieniamy na znaczniki."""
    ctx = zbuduj_kontekst(tmp_path, LUKI)
    przed = ctx.frame.copy()
    run_check("TECH01-VAL-08", ctx)
    pd.testing.assert_frame_equal(ctx.frame, przed)
    assert ctx.frame["date"].dtype == "object"


# --- kontrola 8: tabela zdarzeniowa --------------------------------------------------

PROCES = (
    "case_id,stage,start,end,unit\n"
    "SPR-1,rejestracja,2026-03-01T08:00:00,2026-05-02T09:00:00,A\n"
    "SPR-2,rejestracja,2026-03-05T08:00:00,2026-03-05T09:00:00,A\n"
)


def test_tabela_zdarzeniowa_nigdy_nie_daje_ostrzezenia(tmp_path: Path) -> None:
    """A-01: miesiąca bez zdarzeń nie da się odróżnić od braku danych."""
    wynik = run_check("TECH01-VAL-08", zbuduj_kontekst(tmp_path, PROCES, "PROCESS"))
    assert wynik.status is ValidationStatus.PASS
    assert (
        get_declaration("TECH01-VAL-08").effective_max_status(get_table("PROCESS"))
        is ValidationStatus.PASS
    )


def test_granice_zdarzeniowe_liczone_osobno(tmp_path: Path) -> None:
    """Wiersz PROCESS jest odcinkiem, nie punktem.

    SPR-1 zaczyna się w marcu i kończy w maju. Wybór jednej z granic byłby wyborem
    podstawy, którego A-01 zakazuje — więc liczymy obie i nie wybieramy.
    """
    wynik = run_check("TECH01-VAL-08", zbuduj_kontekst(tmp_path, PROCES, "PROCESS"))
    assert obserwacja(wynik, "months_with_stage_starts").value == 1.0
    assert obserwacja(wynik, "months_with_stage_ends").value == 2.0


def test_sprawa_nie_jest_przypisywana_do_miesiaca(tmp_path: Path) -> None:
    """Sprawa rozpoczęta w marcu i zamknięta w maju nie należy do żadnego z nich."""
    wynik = run_check("TECH01-VAL-08", zbuduj_kontekst(tmp_path, PROCES, "PROCESS"))
    miary = {o.measure for o in wynik.observations}
    assert "months_covered" not in miary
    assert "month_without_data" not in miary
    assert "months_without_events" in miary


def test_time_basis_used_zwraca_pustke_z_podstawa(tmp_path: Path) -> None:
    """Nigdy wybraną wartość, nigdy zero."""
    wynik = run_check("TECH01-VAL-08", zbuduj_kontekst(tmp_path, PROCES, "PROCESS"))
    obs = obserwacja(wynik, "time_basis_used")
    assert obs.is_unknown
    assert "nierozstrzygnięty" in obs.basis


def test_tabela_okresowa_tez_deklaruje_podstawe_czasu(tmp_path: Path) -> None:
    """Odpowiedź jest inna, ale zawsze jawna."""
    obs = obserwacja(
        run_check("TECH01-VAL-08", zbuduj_kontekst(tmp_path, LUKI)), "time_basis_used"
    )
    assert obs.is_unknown
    assert "pola date" in obs.basis
    assert "nierozstrzygnięty" not in obs.basis


# --- text_value i granica obserwacji -------------------------------------------------


def test_obserwacja_nie_niesie_obu_wartosci_naraz() -> None:
    with pytest.raises(ValueError) as blad:
        CheckObservation(subject="a", measure="m", value=1.0, text_value="x", basis="b")
    assert "albo" in str(blad.value)


def test_text_value_ma_twarda_granice_dlugosci() -> None:
    """Niesie fakt, nie zdanie — inaczej za trzy miesiące ktoś wstawi tam opis."""
    with pytest.raises(ValueError):
        CheckObservation(
            subject="a", measure="m", text_value="x" * (TEXT_VALUE_LIMIT + 1), basis="b"
        )


def test_obie_wartosci_puste_znacza_nieznane() -> None:
    """Tak wygląda time_basis_used po rozstrzygnięciu A-01."""
    obs = CheckObservation.create(
        subject="start", measure="time_basis_used", basis="kontrakt nierozstrzygnięty"
    )
    assert obs.is_unknown


def test_obserwacje_ponad_granica_sa_przycinane_i_zgloszone() -> None:
    wejscie = [
        CheckObservation.create(subject=f"g{i}", measure="m", value=1.0, basis="b")
        for i in range(250)
    ]
    wynik = cap_observations(wejscie, subject="m", basis="Grupy.")
    assert len(wynik) == OBSERVATION_LIMIT
    assert wynik[-1].measure == "observations_omitted"
    assert wynik[-1].value == 250 - (OBSERVATION_LIMIT - 1)


def test_przyciecie_obserwacji_jest_deterministyczne() -> None:
    wejscie = [
        CheckObservation.create(subject=f"g{i}", measure="m", value=1.0, basis="b")
        for i in range(150)
    ]
    assert cap_observations(wejscie, subject="m", basis="x") == cap_observations(
        wejscie, subject="m", basis="x"
    )


def test_wynik_ponad_granica_obserwacji_jest_odrzucany() -> None:
    with pytest.raises(ValueError) as blad:
        CheckOutcome(
            status=ValidationStatus.PASS,
            basis="x",
            observations=tuple(
                CheckObservation.create(
                    subject=f"g{i}", measure="m", value=1.0, basis="b"
                )
                for i in range(OBSERVATION_LIMIT + 1)
            ),
        )
    assert "cap_observations" in str(blad.value)


def test_osiem_kontroli_z_karty() -> None:
    """Kryterium odbioru 8.3: walidator wykrywa co najmniej osiem kategorii błędów."""
    numery = {get_declaration(c).control_number for c in registered_check_ids()}
    assert numery == {1, 2, 3, 4, 5, 6, 7, 8}
