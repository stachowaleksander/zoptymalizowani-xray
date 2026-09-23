# Testy techniczne jednostek wykonania i wyprowadzania statusu testu (v1.2 §7, §7.1, §22).
"""Techniczne testy regresyjne. Wektory T50 i T51 leżą w ``tests/acceptance/``."""

import datetime as dt

import pytest

from xray.canonical import ComponentRef, ComponentType
from xray.engine import NOOP01_TEST_ID, DiagnosticTestDeclaration, run_test
from xray.engine.units import (
    CriticalFinding,
    DependencyScope,
    StatusDerivation,
    StatusNotDerivable,
    UnitDeclaration,
    UnitExecutionStatus,
    UnitOutcome,
    UnresolvedApplicability,
    derive_test_status,
    evaluate_units,
)
from xray.ingest import load_table
from xray.model import LogicalStatus, PeriodRef, ScopeRef


def jednostka(component_id: str, **zmiany) -> UnitDeclaration:
    pola = {
        "test_id": "CAP-01",
        "component_ref": ComponentRef(ComponentType.EXECUTION_COMPONENT, component_id),
        "applicable": True,
        "required_tables": ("RESOURCE",),
        "required_fields": {"RESOURCE": ("available_capacity",)},
    }
    return UnitDeclaration(**(pola | zmiany))


FIZYCZNA = jednostka("CAP01-EC-PHYSICAL_UTILIZATION")
EKONOMIA = jednostka(
    "CAP01-EC-ECONOMICS",
    required_tables=("RESOURCE", "COST"),
    required_fields={"COST": ("amount",)},
)


# --- katalog statusów jednostki ---------------------------------------------


def test_katalog_statusow_jednostki_dosłownie_z_kontraktu():
    """v1.2 §7: „UNIT_NOT_APPLICABLE | UNIT_READY | UNIT_BLOCKED | UNIT_EXECUTED"."""
    assert [s.value for s in UnitExecutionStatus] == [
        "UNIT_NOT_APPLICABLE",
        "UNIT_READY",
        "UNIT_BLOCKED",
        "UNIT_EXECUTED",
    ]


def test_zasieg_zaleznosci_ma_dwie_wartosci():
    """v1.2 §7: „tylko do tej legalnej jednostki albo GLOBAL_TEST"."""
    assert [s.value for s in DependencyScope] == ["UNIT", "GLOBAL_TEST"]


# --- applicability ----------------------------------------------------------


def test_nierozstrzygnieta_applicability_jest_bledem():
    """v1.2 §7: „unresolved applicability nie może być cicho uznana za N/A"."""
    with pytest.raises(UnresolvedApplicability):
        evaluate_units([jednostka("CAP01-EC-ECONOMICS", applicable=None)])


def test_jednostka_nieaplikowalna_dostaje_wlasna_podstawe():
    (wynik,) = evaluate_units([jednostka("CAP01-EC-ECONOMICS", applicable=False)])
    assert wynik.status is UnitExecutionStatus.UNIT_NOT_APPLICABLE
    assert wynik.basis


# --- blokowanie selektywne --------------------------------------------------


def test_critical_blokuje_tylko_jednostki_zalezne_od_dotknietego_pola():
    krytyczna = CriticalFinding("CAP01-VAL-10", DependencyScope.UNIT, "COST", ("amount",))
    wyniki = evaluate_units([FIZYCZNA, EKONOMIA], [krytyczna], computed=[FIZYCZNA.unit_id])
    statusy = {w.unit.unit_id[1]: w.status for w in wyniki}
    assert statusy["CAP01-EC-PHYSICAL_UTILIZATION"] is UnitExecutionStatus.UNIT_EXECUTED
    assert statusy["CAP01-EC-ECONOMICS"] is UnitExecutionStatus.UNIT_BLOCKED


def test_critical_w_tabeli_bez_wspolnych_pol_nie_blokuje():
    """Ta sama tabela, inne pole — jednostka liczy się dalej."""
    krytyczna = CriticalFinding("CAP01-VAL-02", DependencyScope.UNIT, "RESOURCE", ("unit_cost",))
    (wynik,) = evaluate_units([FIZYCZNA], [krytyczna], computed=[FIZYCZNA.unit_id])
    assert wynik.status is UnitExecutionStatus.UNIT_EXECUTED


def test_critical_bez_wskazania_pol_blokuje_cala_tabele():
    krytyczna = CriticalFinding("CAP01-VAL-01", DependencyScope.UNIT, "RESOURCE")
    (wynik,) = evaluate_units([FIZYCZNA], [krytyczna])
    assert wynik.status is UnitExecutionStatus.UNIT_BLOCKED


def test_podstawa_blokady_nazywa_kontrole_i_miejsce():
    krytyczna = CriticalFinding("CAP01-VAL-10", DependencyScope.UNIT, "COST", ("amount",))
    (wynik,) = evaluate_units([EKONOMIA], [krytyczna])
    assert "CAP01-VAL-10" in wynik.basis
    assert "COST.amount" in wynik.basis


def test_critical_globalny_dotyka_kazdej_jednostki():
    krytyczna = CriticalFinding("VAL-00", DependencyScope.GLOBAL_TEST)
    wyniki = evaluate_units([FIZYCZNA, EKONOMIA], [krytyczna])
    assert {w.status for w in wyniki} == {UnitExecutionStatus.UNIT_BLOCKED}


# --- wyprowadzenie statusu testu --------------------------------------------


def test_global_critical_daje_test_blocked():
    """v1.2 §22, T01: „GLOBAL prerequisite CRITICAL → TEST_BLOCKED. Bez zmiany"."""
    krytyczna = CriticalFinding("VAL-00", DependencyScope.GLOBAL_TEST)
    wyniki = evaluate_units([FIZYCZNA, EKONOMIA], [krytyczna])
    derywacja = derive_test_status(wyniki, [krytyczna])
    assert derywacja.status is LogicalStatus.TEST_BLOCKED
    assert "T01" in derywacja.basis


def test_wykonana_i_zablokowana_daja_test_partial():
    """v1.2 §7.1 pkt 2–4 i §22 T02."""
    krytyczna = CriticalFinding("CAP01-VAL-10", DependencyScope.UNIT, "COST", ("amount",))
    wyniki = evaluate_units([FIZYCZNA, EKONOMIA], [krytyczna], computed=[FIZYCZNA.unit_id])
    derywacja = derive_test_status(wyniki, [krytyczna])
    assert derywacja.status is LogicalStatus.TEST_PARTIAL
    assert derywacja.defers_to_test_outcome is False


def test_jednostka_ready_blokuje_finalizacje():
    """v1.2 §7.1 pkt 1: „nie ma UNIT_READY przy finalizacji"."""
    wyniki = evaluate_units([FIZYCZNA, EKONOMIA], computed=[FIZYCZNA.unit_id])
    with pytest.raises(StatusNotDerivable, match="UNIT_READY"):
        derive_test_status(wyniki)


def test_wszystkie_wykonane_oddaja_glos_testowi():
    wyniki = evaluate_units(
        [FIZYCZNA, EKONOMIA], computed=[FIZYCZNA.unit_id, EKONOMIA.unit_id]
    )
    derywacja = derive_test_status(wyniki)
    assert derywacja.status is None
    assert derywacja.defers_to_test_outcome is True


def test_wszystkie_zablokowane_to_odmowa_wyprowadzenia():
    """§7.1 wymaga dla TEST_PARTIAL co najmniej jednej wykonanej — wpis B-15."""
    krytyczna = CriticalFinding("CAP01-VAL-01", DependencyScope.UNIT, "RESOURCE")
    wyniki = evaluate_units([FIZYCZNA], [krytyczna])
    with pytest.raises(StatusNotDerivable, match="B-15"):
        derive_test_status(wyniki, [krytyczna])


def test_brak_jednostek_applicable_to_odmowa_wyprowadzenia():
    """TEST_NOT_APPLICABLE z v1.1 nie należy do katalogu LogicalStatus — wpis B-15."""
    wyniki = evaluate_units([jednostka("CAP01-EC-ECONOMICS", applicable=False)])
    with pytest.raises(StatusNotDerivable, match="B-15"):
        derive_test_status(wyniki)


def test_wyprowadzenie_nie_zna_wartosci_spoza_katalogu():
    """Wyprowadzenie może zwrócić wyłącznie TEST_BLOCKED, TEST_PARTIAL albo oddać głos."""
    dozwolone = {LogicalStatus.TEST_BLOCKED, LogicalStatus.TEST_PARTIAL, None}
    krytyczna = CriticalFinding("CAP01-VAL-10", DependencyScope.UNIT, "COST", ("amount",))
    ukladki = [
        (evaluate_units([FIZYCZNA], computed=[FIZYCZNA.unit_id]), []),
        (evaluate_units([FIZYCZNA, EKONOMIA], [krytyczna], computed=[FIZYCZNA.unit_id]),
         [krytyczna]),
    ]
    for wyniki, krytyczne in ukladki:
        assert derive_test_status(wyniki, krytyczne).status in dozwolone


# --- zgodność wsteczna -------------------------------------------------------


def test_jedna_jednostka_bez_blokad_zwraca_status_dzisiejszego_silnika(tmp_path):
    """Warunek twardy pakietu: dla testu o jednej jednostce i bez blokad status
    wyprowadzony musi być równy temu, który silnik daje dzisiaj.

    Wyprowadzenie **oddaje głos** testowi, więc status pozostaje dokładnie ten sam.
    Porównujemy z prawdziwym przebiegiem ``NOOP-01`` przez istniejący rejestr — nie
    z zapamiętaną wartością.
    """
    sciezka = tmp_path / "activity.csv"
    wiersze = [
        "date,unit,product,volume,revenue",
        "2026-01-01,Dział A,porada,10,1000",
        "",
    ]
    sciezka.write_text("\n".join(wiersze), encoding="utf-8")
    wynik_importu = load_table(sciezka, "ACTIVITY", dataset_id="firma-syntetyczna")

    dzisiejsze = run_test(
        NOOP01_TEST_ID,
        {"ACTIVITY": wynik_importu.frame},
        import_reports={"ACTIVITY": (wynik_importu.report,)},
        scope=ScopeRef(scope_label="cała firma"),
        period=PeriodRef(period_start=dt.date(2026, 1, 1), period_end=dt.date(2026, 1, 1)),
    )
    dzisiejszy_status = dzisiejsze[0].status

    jedna = UnitDeclaration(test_id=NOOP01_TEST_ID, component_ref=None, applicable=True)
    derywacja = derive_test_status(evaluate_units([jedna], computed=[jedna.unit_id]))

    assert derywacja.defers_to_test_outcome is True
    assert derywacja.status is None
    # „oddaje głos" znaczy: obowiązuje status testu, bez żadnej korekty
    assert (derywacja.status or dzisiejszy_status) == dzisiejszy_status
    assert dzisiejszy_status is LogicalStatus.NO_ADVERSE_SIGNAL


# --- deklaracja testu --------------------------------------------------------


def test_deklaracja_bez_jednostek_dziala_jak_dotad():
    deklaracja = DiagnosticTestDeclaration(test_id="NOOP-01", required_tables=("COST",))
    assert deklaracja.units == ()


def test_deklaracja_odrzuca_komponent_spoza_rejestru():
    with pytest.raises(ValueError, match="CAP01-EC-WYMYSLONY"):
        DiagnosticTestDeclaration(
            test_id="CAP-01",
            required_tables=("RESOURCE",),
            units=(jednostka("CAP01-EC-WYMYSLONY"),),
        )


def test_deklaracja_odrzuca_jednostke_innego_testu():
    with pytest.raises(ValueError, match="inny test"):
        DiagnosticTestDeclaration(
            test_id="FIN-01",
            required_tables=("RESOURCE",),
            units=(FIZYCZNA,),
        )


def test_deklaracja_odrzuca_nieznane_pole_jednostki():
    with pytest.raises(ValueError, match="nie ma pól"):
        DiagnosticTestDeclaration(
            test_id="CAP-01",
            required_tables=("RESOURCE",),
            units=(
                jednostka(
                    "CAP01-EC-ECONOMICS",
                    required_tables=("RESOURCE",),
                    required_fields={"RESOURCE": ("wymyslone_pole",)},
                ),
            ),
        )


def test_wynik_jednostki_niesie_deklaracje_i_podstawe():
    (wynik,) = evaluate_units([FIZYCZNA], computed=[FIZYCZNA.unit_id])
    assert isinstance(wynik, UnitOutcome)
    assert wynik.unit is FIZYCZNA
    assert wynik.basis
    assert isinstance(derive_test_status([wynik]), StatusDerivation)
