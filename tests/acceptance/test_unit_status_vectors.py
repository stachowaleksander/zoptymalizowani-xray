# Wektory odbiorowe T50 i T51 — granulacja wykonania (karta V12-R1 §16).
"""Dwa scenariusze odbiorowe rundy V12-R1 dotyczące statusów jednostek wykonania.

Kod scenariusza jest w nazwie testu, żeby handoff mógł wskazać exact test locator.
``NEW_ACCEPTANCE_SCENARIO_COUNT = 0``.

## Czego te wektory dowodzą, a czego nie

Karta §16 opisuje dowód dla T50 jako „source locators + unit status test/evidence", a dla
T51 jako „component output/status evidence". Oczekiwania mówią o **statusach jednostek**
i o tym, że wynik ekonomiczny jest ``null`` albo zablokowany — nie o wartościach miar.

Dlatego te wektory nie liczą **żadnej miary Core 10**. v1.2 §21, wiersz `V12-R1`, kolumna
„Nie dotyka": „Core10 formulas/results". Policzalność jednostki jest tu **faktem podanym
przez scenariusz** (co ma podstawę, a co nie), dokładnie tak, jak podaje ją zamrożona
karta w opisie przypadku. Sprawdzamy maszynerię statusów nad rejestrem komponentów z §6.1,
a nie arytmetykę.

Komponenty pochodzą wyłącznie z zamrożonego rejestru — każdy przechodzi przez
``check_component``, więc żadnego ``component_id`` nie dałoby się tu wymyślić.
"""

import pytest

from xray.canonical import ComponentRef, ComponentType
from xray.engine import ComponentNotInRegistry, check_component, components_for
from xray.engine.units import (
    CriticalFinding,
    DependencyScope,
    UnitDeclaration,
    UnitExecutionStatus,
    derive_test_status,
    evaluate_units,
)
from xray.model import LogicalStatus


def jednostka(
    test_id: str,
    component_id: str,
    *,
    applicable: bool = True,
    tabele: tuple[str, ...] = (),
    pola: dict[str, tuple[str, ...]] | None = None,
) -> UnitDeclaration:
    """Jednostka wykonania z komponentem **sprawdzonym wobec rejestru §6.1**."""
    ref = ComponentRef(ComponentType.EXECUTION_COMPONENT, component_id)
    check_component(test_id, ref)
    return UnitDeclaration(
        test_id=test_id,
        component_ref=ref,
        applicable=applicable,
        required_tables=tabele,
        required_fields=pola or {},
    )


# --- T50 --------------------------------------------------------------------


def test_t50_fin01_wykonanie_czesciowe():
    """T50 FIN-01 PARTIAL EXECUTION.

    Invariant (karta §16): „Source-derived FIN01 components; zero ad hoc module_id;
    selective execution przy resolved applicability".
    Expected: „wykonalne units EXECUTED; zależne BLOCKED; TEST_PARTIAL tylko zgodnie
    z frozen source".

    Scenariusz: dynamika i trend mają podstawę w ACTIVITY i COST; luka ekonomiczna zależy
    od referencji, której w tym przypadku nie ma — CRITICAL dotyka tabeli PLAN.
    """
    dynamika = jednostka(
        "FIN-01", "FIN01-EC-DYNAMICS", tabele=("ACTIVITY", "COST"),
        pola={"COST": ("amount",)},
    )
    trend = jednostka("FIN-01", "FIN01-EC-TREND", tabele=("COST",), pola={"COST": ("amount",)})
    luka = jednostka(
        "FIN-01", "FIN01-EC-ECONOMIC_GAP", tabele=("COST", "PLAN"),
        pola={"PLAN": ("metric",)},
    )

    brak_referencji = CriticalFinding(
        "FIN01-VAL-REF", DependencyScope.UNIT, "PLAN", ("metric",)
    )
    wyniki = evaluate_units(
        [dynamika, trend, luka],
        [brak_referencji],
        computed=[dynamika.unit_id, trend.unit_id],
    )
    statusy = {w.unit.unit_id[1]: w.status for w in wyniki}

    assert statusy["FIN01-EC-DYNAMICS"] is UnitExecutionStatus.UNIT_EXECUTED
    assert statusy["FIN01-EC-TREND"] is UnitExecutionStatus.UNIT_EXECUTED
    assert statusy["FIN01-EC-ECONOMIC_GAP"] is UnitExecutionStatus.UNIT_BLOCKED

    # każda jednostka ma własną, jawną podstawę
    assert all(w.basis for w in wyniki)
    assert "FIN01-VAL-REF" in next(
        w.basis for w in wyniki if w.unit.unit_id[1] == "FIN01-EC-ECONOMIC_GAP"
    )

    derywacja = derive_test_status(wyniki, [brak_referencji])
    assert derywacja.status is LogicalStatus.TEST_PARTIAL
    assert derywacja.defers_to_test_outcome is False
    assert "§7.1" in derywacja.basis


def test_t50_zaden_komponent_nie_jest_ad_hoc():
    """„zero ad hoc module_id": komponent spoza rejestru §6.1 nie przejdzie."""
    dozwolone = set(components_for("FIN-01").component_ids)
    assert {"FIN01-EC-DYNAMICS", "FIN01-EC-TREND", "FIN01-EC-ECONOMIC_GAP"} <= dozwolone
    with pytest.raises(ComponentNotInRegistry):
        jednostka("FIN-01", "FIN01-EC-WYMYSLONA")


def test_t50_test_partial_wymaga_rozstrzygnietej_applicability():
    """„TEST_PARTIAL tylko zgodnie z frozen source" — i tylko przy pełnym rozstrzygnięciu.

    Jednostka policzalna, ale niepoliczona, zostaje UNIT_READY i blokuje finalizację
    (v1.2 §7.1 pkt 1), zamiast po cichu dać TEST_PARTIAL.
    """
    from xray.engine.units import StatusNotDerivable

    dynamika = jednostka("FIN-01", "FIN01-EC-DYNAMICS", tabele=("COST",))
    trend = jednostka("FIN-01", "FIN01-EC-TREND", tabele=("COST",))
    luka = jednostka("FIN-01", "FIN01-EC-ECONOMIC_GAP", tabele=("PLAN",))
    krytyczna = CriticalFinding("FIN01-VAL-REF", DependencyScope.UNIT, "PLAN")

    wyniki = evaluate_units([dynamika, trend, luka], [krytyczna], computed=[dynamika.unit_id])
    with pytest.raises(StatusNotDerivable, match="UNIT_READY"):
        derive_test_status(wyniki, [krytyczna])


# --- T51 --------------------------------------------------------------------


def test_t51_cap01_blokowanie_selektywne():
    """T51 CAP-01 SELECTIVE BLOCKING.

    Invariant (karta §16): „CAP01 physical vs economics component separation".
    Expected: „physical outputs retained; economics null/blocked; TEST_PARTIAL zgodnie
    z source-derived granularity".

    v1.2 §23 dopowiada przypadek: „available/used poprawne; ekonomika bez wiarygodnego
    cost basis" oraz „CAP01-EC-PHYSICAL_UTILIZATION ma podstawę; CAP01-EC-ECONOMICS nie".
    """
    fizyczna = jednostka(
        "CAP-01", "CAP01-EC-PHYSICAL_UTILIZATION",
        tabele=("RESOURCE",),
        pola={"RESOURCE": ("available_capacity", "used_capacity")},
    )
    ekonomia = jednostka(
        "CAP-01", "CAP01-EC-ECONOMICS",
        tabele=("RESOURCE", "COST"),
        pola={"COST": ("amount",)},
    )

    brak_kosztu = CriticalFinding("CAP01-VAL-10", DependencyScope.UNIT, "COST", ("amount",))
    wyniki = evaluate_units(
        [fizyczna, ekonomia], [brak_kosztu], computed=[fizyczna.unit_id]
    )
    statusy = {w.unit.unit_id[1]: w.status for w in wyniki}

    # physical outputs retained
    assert statusy["CAP01-EC-PHYSICAL_UTILIZATION"] is UnitExecutionStatus.UNIT_EXECUTED
    # economics blocked
    assert statusy["CAP01-EC-ECONOMICS"] is UnitExecutionStatus.UNIT_BLOCKED

    derywacja = derive_test_status(wyniki, [brak_kosztu])
    assert derywacja.status is LogicalStatus.TEST_PARTIAL


def test_t51_luka_w_kosztach_nie_zdejmuje_jednostki_fizycznej():
    """Sedno blokowania selektywnego: CRITICAL w COST nie dotyka jednostki, która COST
    nie wymaga. Zablokowanie całego testu „bo prościej" produkowałoby status, którego
    zamrożona karta zakazuje (CAP01-T10)."""
    fizyczna = jednostka(
        "CAP-01", "CAP01-EC-PHYSICAL_UTILIZATION",
        tabele=("RESOURCE",),
        pola={"RESOURCE": ("available_capacity",)},
    )
    brak_kosztu = CriticalFinding("CAP01-VAL-10", DependencyScope.UNIT, "COST", ("amount",))
    (wynik,) = evaluate_units([fizyczna], [brak_kosztu], computed=[fizyczna.unit_id])
    assert wynik.status is UnitExecutionStatus.UNIT_EXECUTED


def test_t51_krytyczna_globalna_zdejmuje_caly_test():
    """Granica w drugą stronę: zasięg GLOBAL_TEST blokuje test w całości (§22, T01).

    Selektywność nie znaczy, że nic nie blokuje wszystkiego — znaczy, że blokuje to, co
    zadeklarowano jako globalne.
    """
    fizyczna = jednostka("CAP-01", "CAP01-EC-PHYSICAL_UTILIZATION", tabele=("RESOURCE",))
    ekonomia = jednostka("CAP-01", "CAP01-EC-ECONOMICS", tabele=("COST",))
    globalna = CriticalFinding("VAL-01", DependencyScope.GLOBAL_TEST)

    wyniki = evaluate_units([fizyczna, ekonomia], [globalna])
    assert {w.status for w in wyniki} == {UnitExecutionStatus.UNIT_BLOCKED}
    assert derive_test_status(wyniki, [globalna]).status is LogicalStatus.TEST_BLOCKED
