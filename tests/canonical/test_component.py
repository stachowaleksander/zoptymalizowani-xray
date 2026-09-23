# Testy techniczne osi komponentu wyniku (karta V12-R1 §6, BIND-01 v1.2 §7.2).
"""Struktura ``calculation_component_ref`` — bez udziału rejestru.

Techniczne testy regresyjne, nie scenariusze odbiorowe (karta V12-R1 §16:
``NEW_ACCEPTANCE_SCENARIO_COUNT = 0``). Wektor „MODULE:X vs EXECUTION_COMPONENT:X" jest tu
sprawdzany jako **własność kanonizacji**; scenariusz odbiorowy C-T03 powstanie w pakiecie,
który wyda ``XR_RESULT_IDENTITY_V2``.
"""

import pytest

from xray.canonical import (
    ComponentRef,
    ComponentRefError,
    ComponentType,
    canonical_text,
    component_ref_payload,
    digest,
)

MODUL = ComponentRef(ComponentType.MODULE, "FIN02-M-CM1_AMOUNT")
KOMPONENT = ComponentRef(ComponentType.EXECUTION_COMPONENT, "CAP01-EC-ECONOMICS")


def test_ten_sam_ref_daje_ten_sam_skrot():
    bliznjaczy = ComponentRef(ComponentType.MODULE, "FIN02-M-CM1_AMOUNT")
    assert digest(component_ref_payload(MODUL)) == digest(component_ref_payload(bliznjaczy))


def test_inny_identyfikator_daje_inny_skrot():
    inny = ComponentRef(ComponentType.MODULE, "FIN02-M-SM_AMOUNT")
    assert digest(component_ref_payload(MODUL)) != digest(component_ref_payload(inny))


def test_ten_sam_identyfikator_inny_typ_daje_inny_skrot():
    """v1.2 §7.2: „component_type jest częścią canonical payload"."""
    jako_modul = ComponentRef(ComponentType.MODULE, "X")
    jako_komponent = ComponentRef(ComponentType.EXECUTION_COMPONENT, "X")
    assert digest(component_ref_payload(jako_modul)) != digest(
        component_ref_payload(jako_komponent)
    )


def test_struktura_dopuszcza_obie_kombinacje_niezaleznie_od_rejestru():
    """Rejestr §6.1 nie daje żadnemu testowi obu typów naraz, a mimo to obie wartości
    muszą dać się zbudować — inaczej wektora C-T03 nie byłoby jak wykazać."""
    assert ComponentRef(ComponentType.MODULE, "CAP01-EC-ECONOMICS").component_id == (
        ComponentRef(ComponentType.EXECUTION_COMPONENT, "CAP01-EC-ECONOMICS").component_id
    )


def test_postac_ladunku():
    assert canonical_text(component_ref_payload(KOMPONENT)) == (
        '{"component_id":"CAP01-EC-ECONOMICS","component_type":"EXECUTION_COMPONENT"}'
    )


def test_canonical_null_ma_stabilna_postac():
    assert component_ref_payload(None) is None
    assert canonical_text(component_ref_payload(None)) == "null"


def test_canonical_null_rozni_sie_od_kazdego_komponentu():
    assert digest({"ref": component_ref_payload(None)}) != digest(
        {"ref": component_ref_payload(MODUL)}
    )


def test_pusty_identyfikator_odrzucony():
    with pytest.raises(ComponentRefError):
        ComponentRef(ComponentType.MODULE, "")
    with pytest.raises(ComponentRefError):
        ComponentRef(ComponentType.MODULE, "   ")


def test_typ_spoza_katalogu_odrzucony():
    with pytest.raises(ComponentRefError):
        ComponentRef("MODUŁ", "FIN02-M-CM1_AMOUNT")


def test_ref_ma_dokladnie_dwa_pola():
    """Trzecie pole zmieniłoby tożsamość każdego wyniku — karta §6 podaje zamknięty kształt."""
    assert set(ComponentRef.__dataclass_fields__) == {"component_type", "component_id"}
    assert set(MODUL.payload()) == {"component_type", "component_id"}
