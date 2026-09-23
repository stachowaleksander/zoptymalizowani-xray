# Testy techniczne XR_RESULT_IDENTITY_V2 (karta V12-R1 §7, BIND-01 v1.2 §7.2).
"""Techniczne testy regresyjne kształtu i granic ładunku.

Wektory odbiorowe C-T01–C-T07 leżą osobno, w ``tests/acceptance/``, żeby handoff mógł
wskazać ich lokator bez przeszukiwania testów technicznych. Karta §16:
``NEW_ACCEPTANCE_SCENARIO_COUNT = 0`` — ten plik żadnego scenariusza nie tworzy.
"""

import datetime as dt

import pytest

from xray.canonical import (
    PAYLOAD_KEYS,
    RESULT_IDENTITY_VERSION,
    CanonicalPeriod,
    ComponentRef,
    ComponentType,
    ResultIdentityError,
    ResultIdentityV2,
    ScopeDefinition,
    canonical_text,
    result_identity,
    scope_id,
)

MARZEC = CanonicalPeriod(
    start_inclusive=dt.date(2026, 3, 1),
    end_exclusive=dt.date(2026, 4, 1),
)
ZAKRES = scope_id(ScopeDefinition(population=["A"]))


def pytanie(**zmiany) -> ResultIdentityV2:
    """Pytanie diagnostyczne o ustalonej treści; zmieniamy po jednym składniku."""
    pola = {
        "test_id": "FIN-01",
        "test_contract_version": "ZOP-XR-FIN-01 v1.0",
        "scope_id": ZAKRES,
        "analysis_period": MARZEC,
        "calculation_component_ref": ComponentRef(
            ComponentType.EXECUTION_COMPONENT, "FIN01-EC-DYNAMICS"
        ),
    }
    return ResultIdentityV2(**(pola | zmiany))


# --- kształt ładunku --------------------------------------------------------


def test_ladunek_ma_dokladnie_siedem_skladnikow():
    """Karta §7: „Payload ma zawierać dokładnie siedem składników i żadnych innych"."""
    assert set(pytanie().payload()) == PAYLOAD_KEYS
    assert len(PAYLOAD_KEYS) == 7


def test_wersja_tozsamosci_jest_literalnym_lancuchem():
    assert RESULT_IDENTITY_VERSION == "XR_RESULT_IDENTITY_V2"
    assert pytanie().payload()["result_identity_version"] == "XR_RESULT_IDENTITY_V2"


def test_wersja_kontraktu_testu_to_wersja_karty_a_nie_kontraktu_findings():
    """Pułapka nazewnicza: ``CONTRACT_VERSION`` z identity.py opisuje FINDINGS."""
    from xray.model.findings.identity import CONTRACT_VERSION

    assert pytanie().payload()["test_contract_version"] != CONTRACT_VERSION
    assert CONTRACT_VERSION == "ZOP-TECH-01/v0.1"


def test_postac_identyfikatora():
    import re

    assert re.fullmatch(r"RESULT-[0-9a-f]{64}", result_identity(pytanie()))


def test_ladunek_nie_niesie_zadnego_ze_skladnikow_zakazanych():
    """Karta §7 wylicza dziewięć rzeczy, których w tożsamości być nie może."""
    tekst = canonical_text(pytanie().payload())
    for zakazane in (
        "semantic_run_id",
        "exclusion",
        "execution_attempt_id",
        "execution_fingerprint",
        "record_id",
        "source_artifact",
        "parse_contract",
        "path",
        "timestamp",
    ):
        assert zakazane not in tekst


# --- każdy z siedmiu składników rozróżnia -----------------------------------


def test_inny_test_daje_inna_tozsamosc():
    assert result_identity(pytanie(test_id="FIN-03")) != result_identity(pytanie())


def test_inna_wersja_karty_daje_inna_tozsamosc():
    """v1.1 N-08: „New contract version changes result identity"."""
    assert result_identity(pytanie(test_contract_version="ZOP-XR-FIN-01 v1.1")) != (
        result_identity(pytanie())
    )


def test_inny_zakres_daje_inna_tozsamosc():
    inny = scope_id(ScopeDefinition(population=["B"]))
    assert result_identity(pytanie(scope_id=inny)) != result_identity(pytanie())


def test_inny_okres_daje_inna_tozsamosc():
    kwiecien = CanonicalPeriod(
        start_inclusive=dt.date(2026, 4, 1),
        end_exclusive=dt.date(2026, 5, 1),
    )
    assert result_identity(pytanie(analysis_period=kwiecien)) != result_identity(pytanie())


def test_inna_referencja_daje_inna_tozsamosc():
    z_referencja = pytanie(reference_id="REF-" + "0" * 64)
    assert result_identity(z_referencja) != result_identity(pytanie())


def test_brak_referencji_to_canonical_null():
    assert pytanie().payload()["reference_id"] is None


def test_etykieta_zakresu_i_okresu_nie_dociera_do_tozsamosci():
    """Zakres wchodzi jako ``scope_id``, a nie jako struktura z etykietą."""
    nazwany = scope_id(ScopeDefinition(population=["A"], scope_label="Dział A"))
    assert result_identity(pytanie(scope_id=nazwany)) == result_identity(pytanie())


# --- granice konstruktora ---------------------------------------------------


def test_zakres_musi_byc_identyfikatorem():
    with pytest.raises(ResultIdentityError):
        pytanie(scope_id="cała firma")


def test_referencja_musi_byc_identyfikatorem():
    with pytest.raises(ResultIdentityError):
        pytanie(reference_id="plan 2026")


def test_okres_musi_byc_obiektem_kanonicznym():
    with pytest.raises(ResultIdentityError):
        pytanie(analysis_period="marzec 2026")


def test_pusta_wersja_karty_odrzucona():
    with pytest.raises(ResultIdentityError):
        pytanie(test_contract_version="  ")


def test_osmy_skladnik_nie_da_sie_dolozyc():
    """Karta §7: ósmy składnik to STOP R1-S06, a nie rozszerzenie V2."""
    with pytest.raises(TypeError):
        ResultIdentityV2(
            test_id="FIN-01",
            test_contract_version="ZOP-XR-FIN-01 v1.0",
            scope_id=ZAKRES,
            analysis_period=MARZEC,
            semantic_run_id="RUN-cokolwiek",
        )
