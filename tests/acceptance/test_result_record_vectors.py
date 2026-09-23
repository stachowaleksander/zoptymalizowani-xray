# Wektory odbiorowe C-T10, C-T11, C-T12, C-T15 oraz części C-T14 i C-T16 (karta §16).
"""Scenariusze odbiorowe rundy V12-R1 dotyczące rekordu wyniku i kontekstu wyłączeń.

Kod scenariusza jest w nazwie testu, żeby handoff mógł wskazać exact test locator.
``NEW_ACCEPTANCE_SCENARIO_COUNT = 0``.

Wspólny motyw tych czterech wektorów: **pytanie zostaje, odpowiedzi się mnożą**.
``result_identity`` nie drgnie, gdy zmieni się przebieg danych, próba wykonania albo
kontekst wyłączeń — a każdy z tych trzech daje osobny, niezmienny ``CalculationResultRecord``.

C-T14 i C-T16 domykamy tu tylko w połowie „dwa rekordy istnieją i oba są zachowane".
Ich część parowa — klasyfikacja relacji w ``ExecutionComparisonRecord`` — czeka na P9.

Ładunki są typowane (``Decimal``): wydanie ``result_payload_digest`` dla treści z ``float``
pozostaje zablokowane wpisem B-11.
"""

import datetime as dt
from decimal import Decimal

from xray.canonical import (
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
    CalculationResultRecord,
    ExecutionAttemptRecord,
    FingerprintStatus,
    compare_fingerprints,
)

SCHEMAT = "ZOP-TECH-01/FINDINGS/v0.1"
MARZEC = CanonicalPeriod(start_inclusive=dt.date(2026, 3, 1), end_exclusive=dt.date(2026, 4, 1))
ZAKRES = scope_id(ScopeDefinition(population=["A"], scope_label="Dział A"))
ODCISK = "FPR-" + "a" * 32
INNY_ODCISK = "FPR-" + "d" * 32

PYTANIE = ResultIdentityV2(
    test_id="CAP-01",
    test_contract_version="ZOP-XR-CAP-01 v1.0",
    scope_id=ZAKRES,
    analysis_period=MARZEC,
    calculation_component_ref=ComponentRef(
        ComponentType.EXECUTION_COMPONENT, "CAP01-EC-ECONOMICS"
    ),
)


def proba(run_id: str = "RUN-" + "b" * 32, odcisk: str | None = ODCISK) -> ExecutionAttemptRecord:
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


def rekord(**zmiany) -> CalculationResultRecord:
    pola = {
        "question": PYTANIE,
        "attempt": proba(),
        "result_payload_digest": digest(),
        "result_payload_schema_version": SCHEMAT,
    }
    return CalculationResultRecord.create(**(pola | zmiany))


def kontekst(*podmioty: str) -> EffectiveExclusionContextV1:
    return EffectiveExclusionContextV1(
        [
            ExclusionApplication(
                exclusion_id="EXCL-remont",
                exclusion_subject_type="RESOURCE",
                exclusion_subject_id=podmiot,
                calculation_component_ref=PYTANIE.calculation_component_ref,
                scope_id=ZAKRES,
                period=MARZEC,
            )
            for podmiot in podmioty
        ]
    )


# --- C-T10 ------------------------------------------------------------------


def test_ct10_inny_efektywny_kontekst_wylaczen():
    """C-T10 DIFFERENT EXCLUSION EFFECT.

    Invariant: „exclusion effect excluded from result_identity; bound to
    CalculationResultRecord".
    Expected: „same result_identity; different result_record_id/records".

    Ta sama próba, ten sam przebieg, ten sam ładunek — różnią się wyłącznie wyłączenia,
    które faktycznie wpłynęły na obliczenie.
    """
    ta_sama_proba = proba()
    bez = rekord(attempt=ta_sama_proba, context=kontekst())
    z_jednym = rekord(attempt=ta_sama_proba, context=kontekst("ZAS-17"))
    z_dwoma = rekord(attempt=ta_sama_proba, context=kontekst("ZAS-17", "ZAS-18"))

    assert bez.result_identity == z_jednym.result_identity == z_dwoma.result_identity
    assert len({bez.result_record_id, z_jednym.result_record_id, z_dwoma.result_record_id}) == 3
    assert len(
        {
            bez.effective_exclusion_context_digest,
            z_jednym.effective_exclusion_context_digest,
            z_dwoma.effective_exclusion_context_digest,
        }
    ) == 3


def test_ct10_klucz_zastosowania_powstaje_po_tozsamosci():
    """Karta §10.1: kolejność jest niecykliczna — klucz zawiera result_identity."""
    tozsamosc = result_identity(PYTANIE)
    zastosowanie = kontekst("ZAS-17").applications[0]
    assert zastosowanie.application_key(tozsamosc).startswith("EXAPP-")
    assert result_identity(PYTANIE) == tozsamosc


# --- C-T11 ------------------------------------------------------------------


def test_ct11_to_samo_pytanie_inny_przebieg_danych():
    """C-T11 SAME RESULT QUESTION / DIFFERENT DATA RUN.

    Invariant: „semantic_run_id excluded from result_identity, required on result record".
    Expected: „same result_identity; different semantic_run_id; different immutable
    CalculationResultRecord".
    """
    marzec = rekord(attempt=proba(run_id="RUN-" + "1" * 32))
    kwiecien = rekord(attempt=proba(run_id="RUN-" + "2" * 32))

    assert marzec.result_identity == kwiecien.result_identity
    assert marzec.semantic_run_id != kwiecien.semantic_run_id
    assert marzec.result_record_id != kwiecien.result_record_id
    assert marzec.semantic_run_profile == kwiecien.semantic_run_profile == "CURRENT_RUN_IDENTITY_V3"


# --- C-T12 ------------------------------------------------------------------


def test_ct12_to_samo_pytanie_dwa_rozne_odciski():
    """C-T12 SAME RESULT QUESTION / DIFFERENT EXECUTION.

    Invariant: „execution fingerprint/attempt are provenance, not result identity".
    Expected: „same result_identity; distinct attempts and bound result records".
    """
    stara = proba(odcisk=ODCISK)
    nowa = proba(odcisk=INNY_ODCISK)
    pierwszy = rekord(attempt=stara)
    drugi = rekord(attempt=nowa)

    assert pierwszy.result_identity == drugi.result_identity
    assert stara.execution_attempt_id != nowa.execution_attempt_id
    assert pierwszy.result_record_id != drugi.result_record_id
    assert pierwszy.execution_fingerprint_reference != drugi.execution_fingerprint_reference

    bramka = compare_fingerprints(
        stara.fingerprint_status, stara.execution_fingerprint,
        nowa.fingerprint_status, nowa.execution_fingerprint,
    )
    assert bramka.fingerprint_evidence_sufficient is False
    assert bramka.relation_status is None


# --- C-T15 ------------------------------------------------------------------


def test_ct15_inny_kontekst_wylaczen_to_nie_niedeterminizm():
    """C-T15 DIFFERENT EXCLUSION CONTEXT IS NOT NONDETERMINISM.

    Invariant: „different EffectiveExclusionContext separates calculation context".
    Expected: „two legal result records; not NONDETERMINISM_CONFLICT".

    Ten sam przebieg, ta sama próba, **ten sam znany odcisk**, a mimo różnych ładunków to
    nie jest niedeterminizm: obliczenia miały różny kontekst wyłączeń, więc karta §11.1
    kwalifikuje je jako „Legalne odrębne result records; samo w sobie NOT_NONDETERMINISM".
    """
    ta_sama_proba = proba()
    bez_wylaczen = rekord(
        attempt=ta_sama_proba, context=kontekst(), result_payload_digest=digest("12.5")
    )
    z_wylaczeniem = rekord(
        attempt=ta_sama_proba, context=kontekst("ZAS-17"), result_payload_digest=digest("11.0")
    )

    assert bez_wylaczen.result_identity == z_wylaczeniem.result_identity
    assert bez_wylaczen.result_record_id != z_wylaczeniem.result_record_id
    assert bez_wylaczen.result_payload_digest != z_wylaczeniem.result_payload_digest
    assert (
        bez_wylaczen.effective_exclusion_context_digest
        != z_wylaczeniem.effective_exclusion_context_digest
    )
    # Oba rekordy istnieją i żaden nie zastępuje drugiego.
    assert bez_wylaczen.execution_attempt_id == z_wylaczeniem.execution_attempt_id


# --- C-T14 i C-T16: połowa „oba zachowane" ----------------------------------


def test_ct14_czesc_oba_wyniki_zachowane_przy_roznej_tresci():
    """C-T14 NONDETERMINISM AT FULL CALCULATION CONTEXT — część zachowania dowodu.

    Ten sam przebieg, ten sam znany odcisk, ten sam kontekst, **różne** ładunki: dwie
    faktycznie wykonane próby i dwa rekordy współistnieją. Klasyfikacja relacji
    (``NONDETERMINISM_CONFLICT`` w ``ExecutionComparisonRecord``) należy do P9 — tu
    wykazujemy wyłącznie, że nic nie ginie.
    """
    pierwsza, druga = proba(), proba()
    jeden = rekord(attempt=pierwsza, result_payload_digest=digest("12.5"))
    dwa = rekord(attempt=druga, result_payload_digest=digest("13.0"))

    assert pierwsza.execution_attempt_id != druga.execution_attempt_id
    assert jeden.result_record_id != dwa.result_record_id
    assert jeden.result_identity == dwa.result_identity

    bramka = compare_fingerprints(
        pierwsza.fingerprint_status, pierwsza.execution_fingerprint,
        druga.fingerprint_status, druga.execution_fingerprint,
    )
    assert bramka.fingerprint_evidence_sufficient is True
    assert bramka.relation_status is None  # rozstrzyga dopiero porównanie ładunków (P9)


def test_ct16_czesc_powtorzona_identyczna_proba_nie_ginie():
    """C-T16 REPEATED IDEMPOTENT-EQUIVALENT ACTUAL ATTEMPT — część trwałości.

    Dwie faktycznie wykonane, identyczne próby przy identycznym wyniku. Expected z karty:
    „two attempts + two result records; pairwise IDEMPOTENT_EQUIVALENT; **no loss**".
    Tutaj wykazujemy brak utraty; status pary powstaje w P9.
    """
    pierwsza, druga = proba(), proba()
    jeden = rekord(attempt=pierwsza)
    dwa = rekord(attempt=druga)

    assert pierwsza.execution_attempt_id != druga.execution_attempt_id
    assert jeden.result_payload_digest == dwa.result_payload_digest
    assert jeden.result_identity == dwa.result_identity
    assert jeden.result_record_id != dwa.result_record_id
    assert len({jeden.result_record_id, dwa.result_record_id}) == 2
