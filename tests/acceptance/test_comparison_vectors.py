# Wektory odbiorowe C-T14, C-T16, C-T22, C-T23 — relacja parowa (karta V12-R1 §16).
"""Scenariusze odbiorowe rundy V12-R1 dotyczące porównania wykonań.

Kod scenariusza jest w nazwie testu, żeby handoff mógł wskazać exact test locator.
``NEW_ACCEPTANCE_SCENARIO_COUNT = 0``.

C-T14 i C-T16 domykają tu swoją część parową; część „oba rekordy zachowane" była już
wykazana w wektorach rekordu wyniku (pakiet P8) i jest tu powtórzona na parze.

Ładunki są typowane (``Decimal``) — wydanie skrótu dla treści z ``float`` pozostaje
zablokowane wpisem B-11.
"""

import datetime as dt
from decimal import Decimal

from xray.canonical import (
    CanonicalPeriod,
    ComponentRef,
    ComponentType,
    ResultIdentityV2,
    ResultPayloadEnvelopeV1,
    ScopeDefinition,
    result_payload_digest,
    scope_id,
)
from xray.store import (
    CalculationResultRecord,
    ExecutionAttemptRecord,
    ExecutionRelationStatus,
    FingerprintStatus,
    canonical_attempt_pair,
    classify,
)

SCHEMAT = "ZOP-TECH-01/FINDINGS/v0.1"
MARZEC = CanonicalPeriod(start_inclusive=dt.date(2026, 3, 1), end_exclusive=dt.date(2026, 4, 1))
PRZEBIEG = "RUN-" + "b" * 32
ODCISK = "FPR-" + "a" * 32
INNY_ODCISK = "FPR-" + "d" * 32

PYTANIE = ResultIdentityV2(
    test_id="CAP-01",
    test_contract_version="ZOP-XR-CAP-01 v1.0",
    scope_id=scope_id(ScopeDefinition(population=["A"], scope_label="Dział A")),
    analysis_period=MARZEC,
    calculation_component_ref=ComponentRef(
        ComponentType.EXECUTION_COMPONENT, "CAP01-EC-ECONOMICS"
    ),
)


def proba(odcisk: str | None = ODCISK) -> ExecutionAttemptRecord:
    return ExecutionAttemptRecord.create(
        semantic_run_id=PRZEBIEG,
        execution_fingerprint=odcisk,
        fingerprint_status=(
            FingerprintStatus.KNOWN if odcisk is not None else FingerprintStatus.UNKNOWN
        ),
        execution_provenance_ref="EXE-" + "c" * 32,
        terminal_status="COMPLETED",
    )


def rekord(attempt: ExecutionAttemptRecord, wartosc: str) -> CalculationResultRecord:
    return CalculationResultRecord.create(
        question=PYTANIE,
        attempt=attempt,
        result_payload_digest=result_payload_digest(
            ResultPayloadEnvelopeV1(
                result_payload_schema_version=SCHEMAT,
                payload={"metric_value": Decimal(wartosc)},
            )
        ),
        result_payload_schema_version=SCHEMAT,
    )


# --- C-T14 ------------------------------------------------------------------


def test_ct14_niedeterminizm_przy_pelnym_kontekscie_obliczenia():
    """C-T14 NONDETERMINISM AT FULL CALCULATION CONTEXT.

    Invariant: „KNOWN+equal fingerprint gate; different canonical payload; pairwise relation".
    Expected: „NONDETERMINISM_CONFLICT in immutable ExecutionComparisonRecord; both
    attempts/results preserved".
    """
    pierwsza, druga = proba(), proba()
    wynik_a, wynik_b = rekord(pierwsza, "12.5"), rekord(druga, "13.0")

    relacja = classify(pierwsza, wynik_a, druga, wynik_b)
    assert relacja.execution_relation_status is ExecutionRelationStatus.NONDETERMINISM_CONFLICT

    # zero nadpisania: obie próby, oba rekordy, oba skróty ładunku zostają
    assert pierwsza.execution_attempt_id != druga.execution_attempt_id
    assert wynik_a.result_record_id != wynik_b.result_record_id
    assert wynik_a.result_payload_digest != wynik_b.result_payload_digest
    assert wynik_a.result_identity == wynik_b.result_identity
    assert relacja.payload_relation == "different"
    assert relacja.fingerprint_relation == "same"


# --- C-T16 ------------------------------------------------------------------


def test_ct16_powtorzona_proba_rownowazna():
    """C-T16 REPEATED IDEMPOTENT-EQUIVALENT ACTUAL ATTEMPT.

    Invariant: „actual repeated attempt persistence; pairwise status only".
    Expected: „two attempts + two result records; pairwise IDEMPOTENT_EQUIVALENT; no loss".
    """
    pierwsza, druga = proba(), proba()
    wynik_a, wynik_b = rekord(pierwsza, "12.5"), rekord(druga, "12.5")

    relacja = classify(pierwsza, wynik_a, druga, wynik_b)
    assert relacja.execution_relation_status is ExecutionRelationStatus.IDEMPOTENT_EQUIVALENT

    assert pierwsza.execution_attempt_id != druga.execution_attempt_id
    assert wynik_a.result_record_id != wynik_b.result_record_id
    assert wynik_a.result_payload_digest == wynik_b.result_payload_digest


# --- C-T22 ------------------------------------------------------------------


def test_ct22_wiele_niezaleznych_relacji_dla_jednej_proby():
    """C-T22 MULTIPLE PAIRWISE EXECUTION RELATIONS.

    Invariant: „one attempt may participate in multiple independent immutable relations".
    Expected: „A↔B IDEMPOTENT_EQUIVALENT; A↔C NONDETERMINISM_CONFLICT;
    A↔D DETERMINISM_NOT_ASSESSABLE; all coexist".
    """
    a, b, c = proba(), proba(), proba()
    d = proba(odcisk=None)
    wynik_a = rekord(a, "12.5")
    wynik_b, wynik_c, wynik_d = rekord(b, "12.5"), rekord(c, "13.0"), rekord(d, "12.5")

    ab = classify(a, wynik_a, b, wynik_b)
    ac = classify(a, wynik_a, c, wynik_c)
    ad = classify(a, wynik_a, d, wynik_d)

    assert ab.execution_relation_status is ExecutionRelationStatus.IDEMPOTENT_EQUIVALENT
    assert ac.execution_relation_status is ExecutionRelationStatus.NONDETERMINISM_CONFLICT
    assert ad.execution_relation_status is ExecutionRelationStatus.DETERMINISM_NOT_ASSESSABLE

    # trzy niezależne relacje, trzy różne tożsamości — wszystkie współistnieją
    tozsamosci = {
        ab.execution_comparison_id,
        ac.execution_comparison_id,
        ad.execution_comparison_id,
    }
    assert len(tozsamosci) == 3

    # A nie ma żadnego statusu globalnego: status mieszka wyłącznie w relacjach
    assert not [p for p in ExecutionAttemptRecord.model_fields if "relation" in p]
    assert a.execution_attempt_id in (ab.execution_attempt_id_a, ab.execution_attempt_id_b)
    assert a.execution_attempt_id in (ac.execution_attempt_id_a, ac.execution_attempt_id_b)
    assert a.execution_attempt_id in (ad.execution_attempt_id_a, ad.execution_attempt_id_b)


# --- C-T23 ------------------------------------------------------------------


def test_ct23_kolejnosc_pary_nie_ma_znaczenia():
    """C-T23 PAIR ORDER INDEPENDENCE.

    Invariant: „bytewise canonical attempt pair; order-independent comparison identity".
    Expected: „(A,B) and (B,A) => same execution_comparison_id and same relation; no
    duplicate semantic comparison".
    """
    a, b = proba(), proba()
    wynik_a, wynik_b = rekord(a, "12.5"), rekord(b, "13.0")

    w_przod = classify(a, wynik_a, b, wynik_b)
    w_tyl = classify(b, wynik_b, a, wynik_a)

    assert w_przod.execution_comparison_id == w_tyl.execution_comparison_id
    assert w_przod.execution_relation_status is w_tyl.execution_relation_status
    assert (w_przod.execution_attempt_id_a, w_przod.execution_attempt_id_b) == (
        w_tyl.execution_attempt_id_a,
        w_tyl.execution_attempt_id_b,
    )
    assert (w_przod.execution_attempt_id_a, w_przod.execution_attempt_id_b) == (
        canonical_attempt_pair(a.execution_attempt_id, b.execution_attempt_id)
    )

    # „no duplicate semantic comparison": rejestr po tożsamości ma jeden wpis
    rejestr = {
        w_przod.execution_comparison_id: w_przod,
        w_tyl.execution_comparison_id: w_tyl,
    }
    assert len(rejestr) == 1
