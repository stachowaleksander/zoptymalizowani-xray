# Testy techniczne CalculationResultRecord (karta V12-R1 §10, BIND-01 v1.2 §7.4).
"""Techniczne testy regresyjne. Wektory C-T10…C-T16 leżą w ``tests/acceptance/``."""

import datetime as dt
import re
from decimal import Decimal

import pytest
from pydantic import ValidationError

from xray.canonical import (
    EMPTY_CONTEXT,
    CanonicalPeriod,
    ComponentRef,
    ComponentType,
    EffectiveExclusionContextV1,
    ExclusionApplication,
    ResultIdentityV2,
    ResultPayloadEnvelopeV1,
    ScopeDefinition,
    result_identity,
    result_payload_digest,
    scope_id,
)
from xray.store import (
    RECORD_IDENTITY_VERSION,
    CalculationResultRecord,
    ExecutionAttemptRecord,
    FingerprintStatus,
)

SCHEMAT = "ZOP-TECH-01/FINDINGS/v0.1"
MARZEC = CanonicalPeriod(start_inclusive=dt.date(2026, 3, 1), end_exclusive=dt.date(2026, 4, 1))
ZAKRES = scope_id(ScopeDefinition(population=["A"]))


def pytanie(**zmiany) -> ResultIdentityV2:
    pola = {
        "test_id": "CAP-01",
        "test_contract_version": "ZOP-XR-CAP-01 v1.0",
        "scope_id": ZAKRES,
        "analysis_period": MARZEC,
        "calculation_component_ref": ComponentRef(
            ComponentType.EXECUTION_COMPONENT, "CAP01-EC-ECONOMICS"
        ),
    }
    return ResultIdentityV2(**(pola | zmiany))


def proba(**zmiany) -> ExecutionAttemptRecord:
    pola = {
        "semantic_run_id": "RUN-" + "b" * 32,
        "execution_fingerprint": "FPR-" + "a" * 32,
        "fingerprint_status": FingerprintStatus.KNOWN,
        "execution_provenance_ref": "EXE-" + "c" * 32,
        "terminal_status": "COMPLETED",
    }
    return ExecutionAttemptRecord.create(**(pola | zmiany))


def digest(wartosc: str = "12.5") -> str:
    return result_payload_digest(
        ResultPayloadEnvelopeV1(
            result_payload_schema_version=SCHEMAT,
            payload={"metric_value": Decimal(wartosc)},
        )
    )


def rekord(**zmiany) -> CalculationResultRecord:
    pola = {
        "question": pytanie(),
        "attempt": proba(),
        "result_payload_digest": digest(),
        "result_payload_schema_version": SCHEMAT,
    }
    return CalculationResultRecord.create(**(pola | zmiany))


# --- tożsamość: dokładnie sześć składników ----------------------------------


def test_postac_identyfikatora():
    assert re.fullmatch(r"RREC-[0-9a-f]{64}", rekord().result_record_id)


def test_wersja_profilu_jest_skladnikiem_tozsamosci():
    assert rekord().record_identity_version == RECORD_IDENTITY_VERSION
    assert RECORD_IDENTITY_VERSION == "XR_CALCULATION_RESULT_RECORD_IDENTITY_V1"


def test_kazdy_z_szesciu_skladnikow_rozroznia():
    podstawa = CalculationResultRecord.identity_of(
        result_identity_value="RESULT-" + "1" * 64,
        semantic_run_id="RUN-" + "2" * 32,
        execution_attempt_id="ATTEMPT-" + "3" * 32,
        effective_exclusion_context_digest="4" * 64,
        result_payload_digest="5" * 64,
    )
    zmiany = [
        {"result_identity_value": "RESULT-" + "9" * 64},
        {"semantic_run_id": "RUN-" + "9" * 32},
        {"execution_attempt_id": "ATTEMPT-" + "9" * 32},
        {"effective_exclusion_context_digest": "9" * 64},
        {"result_payload_digest": "9" * 64},
    ]
    pola = {
        "result_identity_value": "RESULT-" + "1" * 64,
        "semantic_run_id": "RUN-" + "2" * 32,
        "execution_attempt_id": "ATTEMPT-" + "3" * 32,
        "effective_exclusion_context_digest": "4" * 64,
        "result_payload_digest": "5" * 64,
    }
    for zmiana in zmiany:
        assert CalculationResultRecord.identity_of(**(pola | zmiana)) != podstawa


def test_proweniencja_profilu_przebiegu_nie_wchodzi_do_tozsamosci():
    """Q1 dał rekordowi dwa pola proweniencji; siódmy składnik to R1-S06."""
    zapis = rekord()
    bez_proweniencji = CalculationResultRecord.identity_of(
        result_identity_value=zapis.result_identity,
        semantic_run_id=zapis.semantic_run_id,
        execution_attempt_id=zapis.execution_attempt_id,
        effective_exclusion_context_digest=zapis.effective_exclusion_context_digest,
        result_payload_digest=zapis.result_payload_digest,
    )
    assert zapis.result_record_id == bez_proweniencji
    assert zapis.semantic_run_profile == "CURRENT_RUN_IDENTITY_V3"
    assert zapis.semantic_run_identity_version == "3"


def test_znacznik_zapisu_nie_zmienia_tozsamosci():
    wczesny = rekord(recorded_at=dt.datetime(2026, 3, 1, tzinfo=dt.UTC))
    pozny = rekord(recorded_at=dt.datetime(2026, 9, 23, tzinfo=dt.UTC))
    assert wczesny.execution_attempt_id != pozny.execution_attempt_id  # inne próby
    assert CalculationResultRecord.identity_of(
        result_identity_value=wczesny.result_identity,
        semantic_run_id=wczesny.semantic_run_id,
        execution_attempt_id=wczesny.execution_attempt_id,
        effective_exclusion_context_digest=wczesny.effective_exclusion_context_digest,
        result_payload_digest=wczesny.result_payload_digest,
    ) == wczesny.result_record_id


def test_schemat_ladunku_jest_polem_a_nie_skladnikiem_tozsamosci():
    """Wersja schematu jest hashowana wewnątrz koperty (C-07), nie w tej krotce."""
    zapis = rekord()
    assert zapis.result_payload_schema_version == SCHEMAT
    assert zapis.result_record_id == CalculationResultRecord.identity_of(
        result_identity_value=zapis.result_identity,
        semantic_run_id=zapis.semantic_run_id,
        execution_attempt_id=zapis.execution_attempt_id,
        effective_exclusion_context_digest=zapis.effective_exclusion_context_digest,
        result_payload_digest=zapis.result_payload_digest,
    )


# --- spójność osi komponentu -------------------------------------------------


def test_komponent_rekordu_pochodzi_z_tego_samego_pytania():
    """Karta §10: „must equal component used in result_identity"."""
    q = pytanie()
    zapis = rekord(question=q)
    assert zapis.calculation_component_ref == q.calculation_component_ref
    assert zapis.matches_question(q)


def test_rekord_nie_pasuje_do_innego_pytania():
    inne = pytanie(
        calculation_component_ref=ComponentRef(
            ComponentType.EXECUTION_COMPONENT, "CAP01-EC-PHYSICAL_UTILIZATION"
        )
    )
    assert not rekord().matches_question(inne)


def test_komponentu_nie_da_sie_podac_obok_pytania():
    """Rozjazd nie jest wykrywany po fakcie — po prostu nie ma jak go wprowadzić."""
    with pytest.raises(TypeError):
        CalculationResultRecord.create(
            question=pytanie(),
            attempt=proba(),
            result_payload_digest=digest(),
            result_payload_schema_version=SCHEMAT,
            calculation_component_ref=ComponentRef(ComponentType.MODULE, "FIN02-M-CM1_AMOUNT"),
        )


# --- kolejność z karty §10.1 -------------------------------------------------


def test_kontekst_wylaczen_liczy_sie_z_tozsamosci_wyniku():
    q = pytanie()
    kontekst = EffectiveExclusionContextV1(
        [
            ExclusionApplication(
                exclusion_id="EXCL-remont",
                exclusion_subject_type="RESOURCE",
                exclusion_subject_id="ZAS-17",
                calculation_component_ref=q.calculation_component_ref,
            )
        ]
    )
    zapis = rekord(question=q, context=kontekst)
    assert zapis.effective_exclusion_context_digest == kontekst.digest(result_identity(q))


def test_wylaczenie_nie_zmienia_tozsamosci_wyniku():
    """v1.2 §7.3: kontekst zmienia rekord, nie pytanie."""
    q = pytanie()
    kontekst = EffectiveExclusionContextV1(
        [
            ExclusionApplication(
                exclusion_id="EXCL-remont",
                exclusion_subject_type="RESOURCE",
                exclusion_subject_id="ZAS-17",
            )
        ]
    )
    bez = rekord(question=q)
    z_wylaczeniem = rekord(question=q, context=kontekst)
    assert bez.result_identity == z_wylaczeniem.result_identity
    assert bez.result_record_id != z_wylaczeniem.result_record_id


def test_domyslny_kontekst_jest_pusty():
    assert rekord().effective_exclusion_context_digest == EMPTY_CONTEXT.digest(
        result_identity(pytanie())
    )


# --- proweniencja i niezmienność --------------------------------------------


def test_rekord_bierze_przebieg_i_odcisk_z_proby():
    p = proba()
    zapis = rekord(attempt=p)
    assert zapis.semantic_run_id == p.semantic_run_id
    assert zapis.execution_attempt_id == p.execution_attempt_id
    assert zapis.execution_fingerprint_reference == p.execution_fingerprint
    assert zapis.fingerprint_status is p.fingerprint_status


def test_proba_o_nieznanym_odcisku_daje_rekord_z_canonical_null():
    p = proba(fingerprint_status=FingerprintStatus.UNKNOWN, execution_fingerprint=None)
    zapis = rekord(attempt=p)
    assert zapis.execution_fingerprint_reference is None
    assert zapis.fingerprint_status is FingerprintStatus.UNKNOWN


def test_rekord_jest_niezmienny():
    with pytest.raises(ValidationError):
        rekord().result_payload_digest = "0" * 64


def test_pole_spoza_kontraktu_odrzucone():
    with pytest.raises(ValidationError):
        CalculationResultRecord(
            result_record_id="RREC-" + "0" * 64,
            result_identity="RESULT-" + "1" * 64,
            semantic_run_id="RUN-" + "2" * 32,
            execution_attempt_id="ATTEMPT-" + "3" * 32,
            effective_exclusion_context_digest="4" * 64,
            result_payload_digest="5" * 64,
            result_payload_schema_version=SCHEMAT,
            fingerprint_status=FingerprintStatus.UNKNOWN,
            foundation_bind_version="ZOP-XR-FOUNDATION-BIND-01 v1.2",
            execution_equivalence_status="IDEMPOTENT_EQUIVALENT",
        )


def test_rekord_nie_ma_statusu_rownowaznosci():
    """v1.2 §7.4.2 — równoważność jest relacją pary, nie polem rekordu (R1-S13)."""
    pola = set(CalculationResultRecord.model_fields)
    assert not [p for p in pola if "equivalence" in p]
