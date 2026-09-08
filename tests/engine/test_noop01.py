# Sprawdza rejestr testów diagnostycznych i atrapę NOOP-01
# wobec ZOP-TECH-01 v0.1 kryterium odbioru 8.5 i pkt 10.5.
"""Testy szwu: rejestr → deklaracja → wykonanie → rekord FINDINGS.

NOOP-01 nie ma treści metodologicznej, więc te testy sprawdzają wyłącznie konstrukcję:
czy deklaracja jest weryfikowana wobec kontraktu danych, czy wynik przechodzi przez
kontrakt FINDINGS i czy identyfikator jest deterministyczny.
"""

import datetime as dt
from typing import ClassVar

import pandas as pd
import pytest
from pydantic import ValidationError

from xray.engine import (
    DiagnosticTest,
    DiagnosticTestDeclaration,
    get_declaration,
    get_test,
    registered_test_ids,
)
from xray.model import LogicalStatus, PeriodRef, ScopeRef

ZAKRES = ScopeRef(scope_label="cała firma")
OKRES = PeriodRef(period_start=dt.date(2026, 1, 1), period_end=dt.date(2026, 1, 31))


@pytest.fixture
def activity() -> pd.DataFrame:
    """Trzy wiersze ACTIVITY. Zawartość nie ma znaczenia — NOOP-01 liczy wiersze."""
    return pd.DataFrame(
        {
            "date": [dt.date(2026, 1, 1)] * 3,
            "unit": ["Dział A", "Dział A", "Dział B"],
            "product": ["usługa 1", "usługa 2", "usługa 1"],
            "volume": [10.0, 20.0, 30.0],
            "revenue": [100.0, 200.0, 300.0],
        }
    )


# --- rejestr -------------------------------------------------------------------------


def test_rejestr_zna_noop01() -> None:
    assert "NOOP-01" in registered_test_ids()


def test_deklaracje_da_sie_odczytac_bez_uruchamiania_testu() -> None:
    """Orkiestracja musi wiedzieć, czego test wymaga, zanim go uruchomi."""
    deklaracja = get_declaration("NOOP-01")
    assert deklaracja.required_tables == ("ACTIVITY",)
    assert "metric_value" in deklaracja.produced_fields


def test_nieznany_test_daje_czytelny_blad() -> None:
    with pytest.raises(KeyError) as blad:
        get_test("FIN-01")
    assert "NOOP-01" in str(blad.value)


# --- deklaracja sprawdzana wobec kontraktu danych -------------------------------------


def test_deklaracja_z_nieznana_tabela_jest_odrzucana() -> None:
    """Test odwołujący się do tabeli spoza pkt 5.2 nie da się zadeklarować."""
    with pytest.raises(ValidationError) as blad:
        DiagnosticTestDeclaration(test_id="X-01", required_tables=("KOSZTY",))
    assert "KOSZTY" in str(blad.value)


def test_deklaracja_z_nieznanym_polem_jest_odrzucana() -> None:
    with pytest.raises(ValidationError) as blad:
        DiagnosticTestDeclaration(
            test_id="X-01",
            required_tables=("COST",),
            required_by_test={"COST": ("amount", "nie_ma_takiego_pola")},
        )
    assert "nie_ma_takiego_pola" in str(blad.value)


def test_deklaracja_pol_z_niewymaganej_tabeli_jest_odrzucana() -> None:
    """Nie da się wymagać pola z tabeli, której test nie zadeklarował."""
    with pytest.raises(ValidationError):
        DiagnosticTestDeclaration(
            test_id="X-01",
            required_tables=("COST",),
            required_by_test={"ACTIVITY": ("revenue",)},
        )


def test_deklaracja_produkujaca_pole_spoza_findings_jest_odrzucana() -> None:
    with pytest.raises(ValidationError) as blad:
        DiagnosticTestDeclaration(
            test_id="X-01",
            required_tables=("COST",),
            produced_fields=("wymyslone_pole",),
        )
    assert "wymyslone_pole" in str(blad.value)


def test_wtyczka_bez_deklaracji_nie_powstaje() -> None:
    """Bez deklaracji orkiestracja nie wie, czego test wymaga ani co produkuje."""
    with pytest.raises(TypeError) as blad:

        class BezDeklaracji(DiagnosticTest):
            def run(self, data, *, scope, period):  # noqa: D102
                return ()

    assert "DECLARATION" in str(blad.value)


def test_wtyczka_z_deklaracja_powstaje() -> None:
    class Poprawna(DiagnosticTest):
        DECLARATION: ClassVar[DiagnosticTestDeclaration] = DiagnosticTestDeclaration(
            test_id="X-01", required_tables=("COST",)
        )

        def run(self, data, *, scope, period):  # noqa: D102
            return ()

    assert Poprawna.DECLARATION.test_id == "X-01"


# --- wykonanie -----------------------------------------------------------------------


def test_noop01_zwraca_jeden_wynik(activity: pd.DataFrame) -> None:
    wyniki = get_test("NOOP-01")().run({"ACTIVITY": activity}, scope=ZAKRES, period=OKRES)
    assert len(wyniki) == 1


def test_noop01_liczy_wiersze_activity(activity: pd.DataFrame) -> None:
    wynik = get_test("NOOP-01")().run(
        {"ACTIVITY": activity}, scope=ZAKRES, period=OKRES
    )[0]
    assert wynik.metric_value == 3.0


def test_noop01_ma_status_bez_sygnalu(activity: pd.DataFrame) -> None:
    """NO_ADVERSE_SIGNAL to jedyna wartość występująca w każdej karcie bez wyjątku."""
    wynik = get_test("NOOP-01")().run(
        {"ACTIVITY": activity}, scope=ZAKRES, period=OKRES
    )[0]
    assert wynik.status is LogicalStatus.NO_ADVERSE_SIGNAL


def test_noop01_nie_wskazuje_kolejnych_testow(activity: pd.DataFrame) -> None:
    """Wskazanie kolejnego testu jest decyzją metodologiczną, a NOOP-01 żadnej nie
    podejmuje."""
    wynik = get_test("NOOP-01")().run(
        {"ACTIVITY": activity}, scope=ZAKRES, period=OKRES
    )[0]
    assert wynik.next_tests == ()
    assert get_declaration("NOOP-01").possible_next_tests == ()


def test_noop01_nie_wyznacza_luki_ani_wplywu(activity: pd.DataFrame) -> None:
    """Bez referencji gap i wpływ pozostają null (FIN-01 rozdz. 6)."""
    wynik = get_test("NOOP-01")().run(
        {"ACTIVITY": activity}, scope=ZAKRES, period=OKRES
    )[0]
    assert wynik.reference is None
    assert wynik.gap is None
    assert wynik.impact_low is None
    assert wynik.impact_high is None


def test_noop01_pozostawia_pewnosc_pusta(activity: pd.DataFrame) -> None:
    """CONF-01 nie jest zaimplementowany, więc klasy pewności pozostają null."""
    wynik = get_test("NOOP-01")().run(
        {"ACTIVITY": activity}, scope=ZAKRES, period=OKRES
    )[0]
    assert wynik.confidence_score is None
    assert wynik.confidence_class is None


def test_noop01_niesie_krotke_tozsamosci_i_wersje_kontraktu(
    activity: pd.DataFrame,
) -> None:
    """To ta część szwu, której nie sprawdzi nic innego."""
    wynik = get_test("NOOP-01")().run(
        {"ACTIVITY": activity}, scope=ZAKRES, period=OKRES
    )[0]
    assert wynik.test_id == "NOOP-01"
    assert wynik.scope == ZAKRES
    assert wynik.period == OKRES
    assert wynik.contract_version


# --- determinizm (zasada 3) ----------------------------------------------------------


def test_dwa_przebiegi_na_tym_samym_zbiorze_daja_ten_sam_identyfikator(
    activity: pd.DataFrame,
) -> None:
    """Te same dane plus ta sama wersja kodu = ten sam wynik."""
    test = get_test("NOOP-01")()
    pierwszy = test.run({"ACTIVITY": activity}, scope=ZAKRES, period=OKRES)[0]
    drugi = test.run({"ACTIVITY": activity}, scope=ZAKRES, period=OKRES)[0]
    assert pierwszy.finding_id == drugi.finding_id
    assert pierwszy == drugi


def test_inny_zakres_daje_inny_identyfikator(activity: pd.DataFrame) -> None:
    test = get_test("NOOP-01")()
    a = test.run({"ACTIVITY": activity}, scope=ZAKRES, period=OKRES)[0]
    b = test.run(
        {"ACTIVITY": activity},
        scope=ScopeRef(scope_label="Dział A", units=("Dział A",)),
        period=OKRES,
    )[0]
    assert a.finding_id != b.finding_id
