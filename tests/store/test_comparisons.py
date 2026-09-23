# Testy techniczne ExecutionComparisonRecord (karta V12-R1 §11 i §11.1).
"""Techniczne testy regresyjne. Wektory C-T14, C-T16, C-T22 i C-T23 leżą w ``tests/acceptance/``."""

import datetime as dt
from decimal import Decimal

import pytest
from pydantic import ValidationError

from xray.canonical import (
    CanonicalPeriod,
    ComponentRef,
    ComponentType,
    EffectiveExclusionContextV1,
    ExclusionApplication,
    ResultIdentityV2,
    ResultPayloadEnvelopeV1,
    ScopeDefinition,
    result_payload_digest,
    scope_id,
)
from xray.store import (
    COMPARISON_PROFILE_VERSION,
    CalculationResultRecord,
    ComparisonContextRef,
    ExecutionAttemptRecord,
    ExecutionComparisonRecord,
    ExecutionRelationStatus,
    FingerprintStatus,
    IncomparableExecutions,
    canonical_attempt_pair,
    check_comparable,
    classify,
)

SCHEMAT = "ZOP-TECH-01/FINDINGS/v0.1"
MARZEC = CanonicalPeriod(start_inclusive=dt.date(2026, 3, 1), end_exclusive=dt.date(2026, 4, 1))
ODCISK = "FPR-" + "a" * 32
INNY_ODCISK = "FPR-" + "d" * 32
PRZEBIEG = "RUN-" + "b" * 32


def pytanie(**zmiany) -> ResultIdentityV2:
    pola = {
        "test_id": "CAP-01",
        "test_contract_version": "ZOP-XR-CAP-01 v1.0",
        "scope_id": scope_id(ScopeDefinition(population=["A"])),
        "analysis_period": MARZEC,
        "calculation_component_ref": ComponentRef(
            ComponentType.EXECUTION_COMPONENT, "CAP01-EC-ECONOMICS"
        ),
    }
    return ResultIdentityV2(**(pola | zmiany))


def proba(run_id: str = PRZEBIEG, odcisk: str | None = ODCISK) -> ExecutionAttemptRecord:
    return ExecutionAttemptRecord.create(
        semantic_run_id=run_id,
        execution_fingerprint=odcisk,
        fingerprint_status=(
            FingerprintStatus.KNOWN if odcisk is not None else FingerprintStatus.UNKNOWN
        ),
        execution_provenance_ref="EXE-" + "c" * 32,
        terminal_status="COMPLETED",
    )


def digest(wartosc: str = "12.5") -> str:
    return result_payload_digest(
        ResultPayloadEnvelopeV1(
            result_payload_schema_version=SCHEMAT,
            payload={"metric_value": Decimal(wartosc)},
        )
    )


def rekord(attempt, *, question=None, wartosc="12.5", context=None) -> CalculationResultRecord:
    dodatkowe = {"context": context} if context is not None else {}
    return CalculationResultRecord.create(
        question=question or pytanie(),
        attempt=attempt,
        result_payload_digest=digest(wartosc),
        result_payload_schema_version=SCHEMAT,
        **dodatkowe,
    )


# --- porównywalność kontekstu: osobny krok, nie bramka ----------------------


def test_rozne_pytania_sa_odmowa_a_nie_niedeterminizmem():
    """Bramka odcisków nic o tym nie wie — sprawdzenie jest osobne i wcześniejsze."""
    a, b = proba(), proba()
    ra = rekord(a)
    rb = rekord(b, question=pytanie(test_id="FIN-01", test_contract_version="ZOP-XR-FIN-01 v1.0"))
    with pytest.raises(IncomparableExecutions, match="różne pytania"):
        classify(a, ra, b, rb)


def test_rozne_przebiegi_sa_odmowa():
    a, b = proba(run_id="RUN-" + "1" * 32), proba(run_id="RUN-" + "2" * 32)
    with pytest.raises(IncomparableExecutions, match="przebiegów"):
        classify(a, rekord(a), b, rekord(b))


def test_rozny_kontekst_wylaczen_jest_odmowa_a_nie_konfliktem():
    """Karta §11.1: „Legalne odrębne result records; samo w sobie NOT_NONDETERMINISM"."""
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
    a, b = proba(), proba()
    ra = rekord(a, question=q, wartosc="12.5")
    rb = rekord(b, question=q, wartosc="11.0", context=kontekst)
    with pytest.raises(IncomparableExecutions, match="EffectiveExclusionContext"):
        classify(a, ra, b, rb)


def test_zgodny_kontekst_daje_referencje_z_trzema_osiami():
    a, b = proba(), proba()
    ref = check_comparable(rekord(a), rekord(b))
    assert set(ref.payload()) == {
        "result_identity",
        "semantic_run_id",
        "effective_exclusion_context_digest",
    }


def test_rekord_nie_moze_nalezec_do_innej_proby():
    a, b, obca = proba(), proba(), proba()
    with pytest.raises(IncomparableExecutions, match="rekord A"):
        classify(obca, rekord(a), b, rekord(b))


# --- klasyfikacja -----------------------------------------------------------


def test_rowny_odcisk_i_ten_sam_ladunek_to_idempotencja():
    a, b = proba(), proba()
    relacja = classify(a, rekord(a, wartosc="12.5"), b, rekord(b, wartosc="12.5"))
    assert relacja.execution_relation_status is ExecutionRelationStatus.IDEMPOTENT_EQUIVALENT
    assert relacja.payload_relation == "same"


def test_rowny_odcisk_i_rozny_ladunek_to_konflikt():
    a, b = proba(), proba()
    relacja = classify(a, rekord(a, wartosc="12.5"), b, rekord(b, wartosc="13.0"))
    assert relacja.execution_relation_status is ExecutionRelationStatus.NONDETERMINISM_CONFLICT
    assert relacja.payload_relation == "different"


def test_nieznany_odcisk_to_brak_oceny_niezaleznie_od_ladunku():
    a, b = proba(odcisk=None), proba(odcisk=None)
    for wartosc in ("12.5", "13.0"):
        relacja = classify(a, rekord(a, wartosc="12.5"), b, rekord(b, wartosc=wartosc))
        assert relacja.execution_relation_status is (
            ExecutionRelationStatus.DETERMINISM_NOT_ASSESSABLE
        )
        assert relacja.fingerprint_relation == "not_assessable"


def test_rozne_znane_odciski_nie_tworza_rekordu():
    """Karta §11.1: neutralny status nie jest wymagany — więc rekordu po prostu nie ma."""
    a, b = proba(odcisk=ODCISK), proba(odcisk=INNY_ODCISK)
    assert classify(a, rekord(a), b, rekord(b)) is None


def test_katalog_nie_zyskal_czwartej_wartosci():
    assert len(list(ExecutionRelationStatus)) == 3


# --- tożsamość relacji ------------------------------------------------------


def test_para_jest_sortowana_bajtowo():
    assert canonical_attempt_pair("ATTEMPT-b", "ATTEMPT-a") == ("ATTEMPT-a", "ATTEMPT-b")
    assert canonical_attempt_pair("ATTEMPT-a", "ATTEMPT-b") == ("ATTEMPT-a", "ATTEMPT-b")


def test_proba_nie_tworzy_pary_sama_ze_soba():
    with pytest.raises(IncomparableExecutions):
        canonical_attempt_pair("ATTEMPT-a", "ATTEMPT-a")


def test_czas_nie_wchodzi_do_tozsamosci_relacji():
    """v1.2 §7.4.3: ponowna ocena tej samej pary nie zmienia tożsamości relacji."""
    a, b = proba(), proba()
    ra, rb = rekord(a), rekord(b)
    rano = classify(a, ra, b, rb, assessed_at=dt.datetime(2026, 3, 1, tzinfo=dt.UTC))
    wieczorem = classify(a, ra, b, rb, assessed_at=dt.datetime(2026, 9, 23, tzinfo=dt.UTC))
    assert rano.execution_comparison_id == wieczorem.execution_comparison_id
    assert rano.assessed_at != wieczorem.assessed_at


def test_inny_kontekst_daje_inna_tozsamosc_relacji():
    a, b = proba(), proba()
    para = canonical_attempt_pair(a.execution_attempt_id, b.execution_attempt_id)
    jeden = ExecutionComparisonRecord.identity_of(
        para,
        ComparisonContextRef(
            result_identity="RESULT-" + "1" * 64,
            semantic_run_id=PRZEBIEG,
            effective_exclusion_context_digest="4" * 64,
        ),
    )
    drugi = ExecutionComparisonRecord.identity_of(
        para,
        ComparisonContextRef(
            result_identity="RESULT-" + "2" * 64,
            semantic_run_id=PRZEBIEG,
            effective_exclusion_context_digest="4" * 64,
        ),
    )
    assert jeden != drugi


def test_profil_relacji_jest_w_tozsamosci():
    assert COMPARISON_PROFILE_VERSION == "XR_EXECUTION_COMPARISON_V1"
    a, b = proba(), proba()
    relacja = classify(a, rekord(a), b, rekord(b))
    assert relacja.comparison_profile_version == COMPARISON_PROFILE_VERSION
    assert relacja.execution_comparison_id.startswith("ECMP-")


# --- brak stanu skalarnego i niezmienność -----------------------------------


def test_proba_i_rekord_wyniku_nie_maja_statusu_relacji():
    """Karta §11: status jest cechą pary, nie próby ani rekordu (R1-S13).

    Lista **dozwolonych** pól, nie zakazanych podłańcuchów: każde nowe pole — o dowolnej
    nazwie — wywala ten test i każe autorowi świadomie zdecydować, czy nie jest to stan
    relacji przemycony na rekord.
    """
    assert set(ExecutionAttemptRecord.model_fields) == {
        "execution_attempt_id",
        "semantic_run_id",
        "semantic_run_profile",
        "semantic_run_identity_version",
        "execution_fingerprint",
        "fingerprint_status",
        "execution_provenance_ref",
        "attempt_started_at",
        "attempt_completed_at",
        "terminal_status",
        "result_record_ids",
        "comparison_evidence_refs",
        "failure_evidence_refs",
        "foundation_bind_version",
    }
    assert set(CalculationResultRecord.model_fields) == {
        "result_record_id",
        "record_identity_version",
        "result_identity",
        "semantic_run_id",
        "execution_attempt_id",
        "effective_exclusion_context_digest",
        "result_payload_digest",
        "calculation_component_ref",
        "result_payload_schema_version",
        "semantic_run_profile",
        "semantic_run_identity_version",
        "execution_fingerprint_reference",
        "fingerprint_status",
        "result_payload_ref",
        "source_input_evidence_refs",
        "recorded_at",
        "foundation_bind_version",
    }


def test_relacja_jest_niezmienna():
    a, b = proba(), proba()
    relacja = classify(a, rekord(a), b, rekord(b))
    with pytest.raises(ValidationError):
        relacja.execution_relation_status = ExecutionRelationStatus.NONDETERMINISM_CONFLICT


def test_para_spoza_postaci_kanonicznej_odrzucona():
    with pytest.raises(ValidationError):
        ExecutionComparisonRecord(
            execution_comparison_id="ECMP-" + "0" * 64,
            execution_attempt_id_a="ATTEMPT-b",
            execution_attempt_id_b="ATTEMPT-a",
            comparison_context_reference=ComparisonContextRef(
                result_identity="RESULT-" + "1" * 64,
                semantic_run_id=PRZEBIEG,
                effective_exclusion_context_digest="4" * 64,
            ),
            fingerprint_relation="same",
            payload_relation="same",
            effective_exclusion_context_relation="same",
            execution_relation_status=ExecutionRelationStatus.IDEMPOTENT_EQUIVALENT,
            basis="test",
            foundation_bind_version="ZOP-XR-FOUNDATION-BIND-01 v1.2",
        )


def test_relacja_wiaze_minimum_z_karty():
    assert set(ExecutionComparisonRecord.model_fields) >= {
        "execution_comparison_id",
        "execution_attempt_id_a",
        "execution_attempt_id_b",
        "comparison_context_reference",
        "fingerprint_relation",
        "payload_relation",
        "effective_exclusion_context_relation",
        "execution_relation_status",
        "basis",
        "created_at",
        "assessed_at",
        "foundation_bind_version",
    }
