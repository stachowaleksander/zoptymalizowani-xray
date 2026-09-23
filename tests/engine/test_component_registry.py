# Testy techniczne zamrożonego rejestru komponentów (karta V12-R1 §6.1, BIND-01 v1.2 §8).
"""Rejestr wobec karty: jeden test — jeden typ — zamknięta lista.

Techniczne testy regresyjne, nie scenariusze odbiorowe (karta V12-R1 §16).
"""

import pytest

from xray.canonical import ComponentRef, ComponentType
from xray.engine import (
    COMPONENT_REGISTRY,
    MGT01_DIMENSION_PREFIX,
    MGT01_DIMENSIONS,
    ComponentNotInRegistry,
    NullComponentNotAllowed,
    UnknownTest,
    WrongComponentType,
    check_component,
    components_for,
)

# --- kształt rejestru -------------------------------------------------------


def test_rejestr_obejmuje_dziesiec_testow_core_10():
    assert set(COMPONENT_REGISTRY) == {
        "FIN-01",
        "FIN-02",
        "FIN-03",
        "CAP-01",
        "CAP-02",
        "HR-01",
        "PORT-01",
        "PROC-01",
        "PROC-02",
        "MGT-01",
    }


def test_fin_02_jest_jedynym_testem_modulowym():
    """v1.2 §8: FIN-02 = FORMAL_MODULES_EXPLICIT, pozostałe = SOURCE_DEFINED_…_BINDABLE."""
    modulowe = [
        test_id
        for test_id, wiersz in COMPONENT_REGISTRY.items()
        if wiersz.component_type is ComponentType.MODULE
    ]
    assert modulowe == ["FIN-02"]


def test_kazdy_test_ma_niepusta_liste_i_lokator_zrodla():
    for wiersz in COMPONENT_REGISTRY.values():
        assert wiersz.component_ids, wiersz.test_id
        assert wiersz.source_locator, wiersz.test_id


def test_identyfikatory_sa_unikalne_w_calym_rejestrze():
    wszystkie = [
        component_id
        for wiersz in COMPONENT_REGISTRY.values()
        for component_id in wiersz.component_ids
    ]
    assert len(wszystkie) == len(set(wszystkie))


def test_nieznany_test_to_blad_a_nie_pusta_lista():
    """„Nie wiem" i „nie ma komponentów" to dwa różne stany."""
    with pytest.raises(UnknownTest):
        components_for("FIN-99")


def test_noop01_nie_jest_w_rejestrze():
    """Atrapa silnika nie jest zamrożonym źródłem metodologicznym."""
    assert "NOOP-01" not in COMPONENT_REGISTRY


# --- walidacja referencji ---------------------------------------------------


def test_komponent_z_listy_przechodzi():
    check_component("CAP-01", ComponentRef(ComponentType.EXECUTION_COMPONENT, "CAP01-EC-ECONOMICS"))


def test_komponent_spoza_listy_odrzucony():
    with pytest.raises(ComponentNotInRegistry):
        check_component(
            "CAP-01", ComponentRef(ComponentType.EXECUTION_COMPONENT, "CAP01-EC-WYMYSLONY")
        )


def test_komponent_innego_testu_odrzucony():
    with pytest.raises(ComponentNotInRegistry):
        check_component("CAP-01", ComponentRef(ComponentType.EXECUTION_COMPONENT, "HR01-EC-LR"))


def test_zly_typ_odrzucony_mimo_poprawnego_identyfikatora():
    """Karta §6: TECHNICAL_EXECUTION_COMPONENT_IS_METHODOLOGICAL_MODULE = false."""
    with pytest.raises(WrongComponentType):
        check_component("FIN-01", ComponentRef(ComponentType.MODULE, "FIN01-EC-DYNAMICS"))
    with pytest.raises(WrongComponentType):
        check_component(
            "FIN-02", ComponentRef(ComponentType.EXECUTION_COMPONENT, "FIN02-M-CM1_AMOUNT")
        )


def test_canonical_null_odrzucony_dla_kazdego_zarejestrowanego_testu():
    """Żaden z dziesięciu testów nie jest non-modular (v1.2 §8), więc null nie ma podstawy."""
    for test_id in COMPONENT_REGISTRY:
        with pytest.raises(NullComponentNotAllowed):
            check_component(test_id, None)


def test_kazdy_zadeklarowany_komponent_przechodzi_wlasna_walidacje():
    """Rejestr musi być spójny sam ze sobą: to, co deklaruje, ma być legalne."""
    for test_id, wiersz in COMPONENT_REGISTRY.items():
        for component_id in wiersz.component_ids:
            check_component(test_id, ComponentRef(wiersz.component_type, component_id))


# --- MGT-01: postać parametryczna -------------------------------------------


def test_mgt01_ma_szesnascie_wymiarow_i_gotowosc_decyzyjna():
    """Nazwy z ZOP-XR-MGT-01 v1.0 §12.3; liczba potwierdzona w MGT01-ACC-75 („16 wymiary")."""
    wiersz = components_for("MGT-01")
    assert len(MGT01_DIMENSIONS) == 16
    assert len(wiersz.component_ids) == 17
    assert "MGT01-EC-DECISION_READINESS" in wiersz.component_ids


def test_wymiar_z_karty_jest_legalnym_komponentem():
    check_component(
        "MGT-01",
        ComponentRef(ComponentType.EXECUTION_COMPONENT, MGT01_DIMENSION_PREFIX + "comparability"),
    )


def test_wymiar_spoza_karty_odrzucony():
    """Nie dlatego, że lista jest zamknięta, tylko dlatego, że nic w źródle takiego
    wymiaru nie ustanawia — przesłanka STOP R1-S03."""
    with pytest.raises(ComponentNotInRegistry):
        check_component(
            "MGT-01",
            ComponentRef(
                ComponentType.EXECUTION_COMPONENT, MGT01_DIMENSION_PREFIX + "jakosc_ogolna"
            ),
        )


def test_sam_wzorzec_bez_nazwy_wymiaru_odrzucony():
    with pytest.raises(ComponentNotInRegistry):
        check_component(
            "MGT-01", ComponentRef(ComponentType.EXECUTION_COMPONENT, MGT01_DIMENSION_PREFIX)
        )


def test_nazwa_wymiaru_bez_wzorca_odrzucona():
    with pytest.raises(ComponentNotInRegistry):
        check_component("MGT-01", ComponentRef(ComponentType.EXECUTION_COMPONENT, "comparability"))
