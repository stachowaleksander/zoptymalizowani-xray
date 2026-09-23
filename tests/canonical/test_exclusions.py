# Testy techniczne EffectiveExclusionContextV1 (karta V12-R1 §10.1, BIND-01 v1.2 §7.3).
"""Techniczne testy regresyjne. Wektory C-T10 i C-T15 leżą w ``tests/acceptance/``."""

import datetime as dt
import re

import pytest

from xray.canonical import (
    CONTEXT_VERSION,
    EMPTY_CONTEXT,
    CanonicalPeriod,
    ComponentRef,
    ComponentType,
    EffectiveExclusionContextV1,
    ExclusionApplication,
    ExclusionContractError,
    ResultIdentityV2,
    ScopeDefinition,
    result_identity,
    scope_id,
)

ZAKRES = scope_id(ScopeDefinition(population=["A"]))
MARZEC = CanonicalPeriod(start_inclusive=dt.date(2026, 3, 1), end_exclusive=dt.date(2026, 4, 1))
PYTANIE = ResultIdentityV2(
    test_id="CAP-01",
    test_contract_version="ZOP-XR-CAP-01 v1.0",
    scope_id=ZAKRES,
    analysis_period=MARZEC,
    calculation_component_ref=ComponentRef(
        ComponentType.EXECUTION_COMPONENT, "CAP01-EC-ECONOMICS"
    ),
)
TOZSAMOSC = result_identity(PYTANIE)


def wylaczenie(subject_id: str = "ZAS-17", **zmiany) -> ExclusionApplication:
    pola = {
        "exclusion_id": "EXCL-remont",
        "exclusion_subject_type": "RESOURCE",
        "exclusion_subject_id": subject_id,
        "calculation_component_ref": PYTANIE.calculation_component_ref,
        "scope_id": ZAKRES,
        "period": MARZEC,
    }
    return ExclusionApplication(**(pola | zmiany))


# --- klucz zastosowania ------------------------------------------------------


def test_postac_klucza():
    assert re.fullmatch(r"EXAPP-[0-9a-f]{64}", wylaczenie().application_key(TOZSAMOSC))


def test_ten_sam_podmiot_i_ta_sama_tozsamosc_daja_ten_sam_klucz():
    assert wylaczenie().application_key(TOZSAMOSC) == wylaczenie().application_key(TOZSAMOSC)


def test_inny_podmiot_daje_inny_klucz():
    assert wylaczenie("ZAS-17").application_key(TOZSAMOSC) != wylaczenie("ZAS-18").application_key(
        TOZSAMOSC
    )


def test_inny_typ_podmiotu_daje_inny_klucz():
    assert wylaczenie().application_key(TOZSAMOSC) != wylaczenie(
        exclusion_subject_type="UNIT"
    ).application_key(TOZSAMOSC)


def test_inny_komponent_daje_inny_klucz():
    inny = wylaczenie(
        calculation_component_ref=ComponentRef(
            ComponentType.EXECUTION_COMPONENT, "CAP01-EC-PHYSICAL_UTILIZATION"
        )
    )
    assert wylaczenie().application_key(TOZSAMOSC) != inny.application_key(TOZSAMOSC)


def test_inna_tozsamosc_wyniku_daje_inny_klucz():
    inne_pytanie = ResultIdentityV2(
        test_id="CAP-01",
        test_contract_version="ZOP-XR-CAP-01 v1.0",
        scope_id=scope_id(ScopeDefinition(population=["B"])),
        analysis_period=MARZEC,
        calculation_component_ref=PYTANIE.calculation_component_ref,
    )
    assert wylaczenie().application_key(TOZSAMOSC) != wylaczenie().application_key(
        result_identity(inne_pytanie)
    )


def test_identyfikator_wylaczenia_i_okres_nie_wchodza_do_klucza():
    """Karta §10.1: klucz liczy się z czterech elementów, reszta jest wiązaniem rekordu."""
    inny = wylaczenie(exclusion_id="EXCL-inne", period=None)
    assert wylaczenie().application_key(TOZSAMOSC) == inny.application_key(TOZSAMOSC)
    assert inny.binding(TOZSAMOSC)["exclusion_id"] == "EXCL-inne"


# --- kolejność wymuszona konstrukcją ----------------------------------------


def test_klucz_nie_powstanie_bez_tozsamosci_wyniku():
    """Krok 1 przed krokiem 3 — kolejność z karty §10.1 jest niecykliczna."""
    with pytest.raises(TypeError):
        wylaczenie().application_key()


def test_lancuch_ktory_nie_jest_tozsamoscia_wyniku_odrzucony():
    with pytest.raises(ExclusionContractError):
        wylaczenie().application_key("CAP-01/marzec")


def test_skrot_kontekstu_tez_wymaga_tozsamosci():
    with pytest.raises(TypeError):
        EffectiveExclusionContextV1([wylaczenie()]).digest()


def test_puste_pola_zastosowania_odrzucone():
    with pytest.raises(ExclusionContractError):
        wylaczenie(exclusion_id="  ")
    with pytest.raises(ExclusionContractError):
        wylaczenie(exclusion_subject_id="")


# --- skrót kontekstu ---------------------------------------------------------


def test_pusty_kontekst_ma_pusta_liste_kluczy():
    """Karta §10.1: ``no_effective_exclusions => effective_application_keys = []``."""
    ladunek = EMPTY_CONTEXT.payload(TOZSAMOSC)
    assert ladunek["context_version"] == CONTEXT_VERSION == "EffectiveExclusionContextV1"
    assert ladunek["effective_application_keys"].elements == ()


def test_skrot_pustego_kontekstu_nie_zalezy_od_tozsamosci():
    inna = "RESULT-" + "f" * 64
    assert EMPTY_CONTEXT.digest(TOZSAMOSC) == EMPTY_CONTEXT.digest(inna)


def test_pusty_kontekst_rozni_sie_od_niepustego():
    z_wylaczeniem = EffectiveExclusionContextV1([wylaczenie()])
    assert EMPTY_CONTEXT.digest(TOZSAMOSC) != z_wylaczeniem.digest(TOZSAMOSC)


def test_kolejnosc_wylaczen_nie_zmienia_skrotu():
    jeden = EffectiveExclusionContextV1([wylaczenie("ZAS-17"), wylaczenie("ZAS-18")])
    drugi = EffectiveExclusionContextV1([wylaczenie("ZAS-18"), wylaczenie("ZAS-17")])
    assert jeden.digest(TOZSAMOSC) == drugi.digest(TOZSAMOSC)


def test_dodanie_wylaczenia_zmienia_skrot():
    jeden = EffectiveExclusionContextV1([wylaczenie("ZAS-17")])
    dwa = EffectiveExclusionContextV1([wylaczenie("ZAS-17"), wylaczenie("ZAS-18")])
    assert jeden.digest(TOZSAMOSC) != dwa.digest(TOZSAMOSC)


def test_t15_dwa_powody_na_tym_samym_podmiocie_daja_jeden_klucz():
    """BIND-01 v1.1, scenariusz T15: „same subject/component | two exclusion_code |
    **two exclusion_id / one EXAPP** | one effective exclusion | per test | both reasons
    + one application".

    Wygląda jak kolizja, a jest zamierzone: klucz zastosowania liczy się z tożsamości
    wyniku, komponentu, typu i identyfikatora podmiotu — ``exclusion_id`` do niego nie
    wchodzi. Dwa powody wyłączenia tego samego zasobu w tym samym komponencie to **jedno**
    efektywne wyłączenie, a nie dwa.
    """
    remont = wylaczenie(exclusion_id="EXCL-remont")
    przeglad = wylaczenie(exclusion_id="EXCL-przeglad")
    assert remont.exclusion_id != przeglad.exclusion_id
    assert remont.application_key(TOZSAMOSC) == przeglad.application_key(TOZSAMOSC)

    # jedno zastosowanie w kontekście = jeden klucz efektywny
    kontekst = EffectiveExclusionContextV1([remont])
    assert len(kontekst.application_keys(TOZSAMOSC)) == 1
    assert kontekst.digest(TOZSAMOSC) == EffectiveExclusionContextV1([przeglad]).digest(TOZSAMOSC)


def test_t15_dwa_zastosowania_o_tym_samym_kluczu_odrzucone():
    """Kontekst z dwoma opisami jednego wyłączenia **nie powstaje**.

    Sprawdzenie jest przy konstrukcji, nie przy hashowaniu: obiekt opisujący jedno
    efektywne wyłączenie dwa razy jest błędny niezależnie od tego, czy ktoś policzy z niego
    skrót. „One effective exclusion" materializuje wołający, zachowując oba powody
    w dowodzie audytowym.
    """
    with pytest.raises(ExclusionContractError, match="T15"):
        EffectiveExclusionContextV1(
            [wylaczenie(exclusion_id="EXCL-remont"), wylaczenie(exclusion_id="EXCL-przeglad")]
        )


def test_powtorzone_to_samo_zastosowanie_odrzucone():
    """Dwa identyczne zastosowania też nie zbudują kontekstu."""
    with pytest.raises(ExclusionContractError):
        EffectiveExclusionContextV1([wylaczenie("ZAS-17"), wylaczenie("ZAS-17")])


def test_skrot_ma_64_znaki_lowercase_hex_bez_prefiksu():
    assert re.fullmatch(r"[0-9a-f]{64}", EMPTY_CONTEXT.digest(TOZSAMOSC))


# --- granica z tożsamością wyniku -------------------------------------------


def test_wylaczenie_nie_zmienia_tozsamosci_wyniku():
    """v1.2 §7.3: ``EXCLUSION_EFFECT_IN_RESULT_IDENTITY = false``."""
    przed = result_identity(PYTANIE)
    EffectiveExclusionContextV1([wylaczenie()]).digest(przed)
    assert result_identity(PYTANIE) == przed
