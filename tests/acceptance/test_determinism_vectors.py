# Wektory odbiorowe C-T18 i C-T19 — bramka KNOWN/UNKNOWN (karta V12-R1 §16).
"""Scenariusze odbiorowe rundy V12-R1 dotyczące oceny determinizmu.

Kod scenariusza jest w nazwie testu, żeby handoff mógł wskazać exact test locator.
``NEW_ACCEPTANCE_SCENARIO_COUNT = 0``.

Oba wektory dotyczą tego samego: **UNKNOWN nigdy nie dowodzi tego samego wykonania**.
Ładunek — identyczny czy różny — niczego tu nie zmienia, bo bramka rozstrzyga **przed**
porównaniem treści. Pozostałe wektory wykonań (C-T12, C-T14, C-T16, C-T22, C-T23) czekają
na rekord porównania z pakietu P9.
"""

from decimal import Decimal

from xray.canonical import ResultPayloadEnvelopeV1, result_payload_digest
from xray.store import FingerprintStatus
from xray.store.attempts import (
    ExecutionAttemptRecord,
    ExecutionRelationStatus,
    compare_fingerprints,
)

PRZEBIEG = "RUN-" + "b" * 32
SCHEMAT = "ZOP-TECH-01/FINDINGS/v0.1"


def proba_bez_odcisku(**zmiany) -> ExecutionAttemptRecord:
    """Próba, dla której nie udało się ustalić odcisku kodu i środowiska."""
    pola = {
        "semantic_run_id": PRZEBIEG,
        "execution_fingerprint": None,
        "fingerprint_status": FingerprintStatus.UNKNOWN,
        "execution_provenance_ref": "EXE-" + "c" * 32,
        "terminal_status": "COMPLETED",
    }
    return ExecutionAttemptRecord.create(**(pola | zmiany))


def digest(wartosc: Decimal) -> str:
    return result_payload_digest(
        ResultPayloadEnvelopeV1(
            result_payload_schema_version=SCHEMAT,
            payload={"metric_value": wartosc},
        )
    )


def decyzja(pierwsza: ExecutionAttemptRecord, druga: ExecutionAttemptRecord):
    return compare_fingerprints(
        pierwsza.fingerprint_status,
        pierwsza.execution_fingerprint,
        druga.fingerprint_status,
        druga.execution_fingerprint,
    )


# --- C-T18 ------------------------------------------------------------------


def test_ct18_nieznany_odcisk_ten_sam_ladunek():
    """C-T18 UNKNOWN FINGERPRINT / SAME PAYLOAD.

    Invariant: „UNKNOWN cannot satisfy equal-fingerprint guard".
    Expected: „DETERMINISM_NOT_ASSESSABLE; **not IDEMPOTENT_EQUIVALENT**".

    Dwie faktycznie wykonane próby, oba odciski nieznane, identyczny
    ``result_payload_digest``. Zgodność treści kusi, żeby uznać je za równoważne — karta §9
    tego zakazuje: „UNKNOWN jest brakiem evidence, nie wspólnym fingerprintem".
    """
    pierwsza, druga = proba_bez_odcisku(), proba_bez_odcisku()
    assert pierwsza.execution_attempt_id != druga.execution_attempt_id
    assert digest(Decimal("1250.50")) == digest(Decimal("1250.5"))

    wynik = decyzja(pierwsza, druga)
    assert wynik.relation_status is ExecutionRelationStatus.DETERMINISM_NOT_ASSESSABLE
    assert wynik.relation_status is not ExecutionRelationStatus.IDEMPOTENT_EQUIVALENT
    assert wynik.fingerprint_evidence_sufficient is False


# --- C-T19 ------------------------------------------------------------------


def test_ct19_nieznany_odcisk_rozny_ladunek():
    """C-T19 UNKNOWN FINGERPRINT / DIFFERENT PAYLOAD.

    Invariant: „UNKNOWN blocks proof of same exact execution fingerprint".
    Expected: „DETERMINISM_NOT_ASSESSABLE; **not NONDETERMINISM_CONFLICT**".

    Ta sama para co w C-T18, tylko ładunki różne. Rozbieżność treści kusi, żeby ogłosić
    niedeterminizm — ale bez znanych i równych odcisków nie wiadomo, czy to w ogóle było to
    samo wykonanie. Różnica może brać się z innego kodu, nie z niedeterminizmu.
    """
    pierwsza, druga = proba_bez_odcisku(), proba_bez_odcisku()
    assert digest(Decimal("1250.50")) != digest(Decimal("1300.00"))

    wynik = decyzja(pierwsza, druga)
    assert wynik.relation_status is ExecutionRelationStatus.DETERMINISM_NOT_ASSESSABLE
    assert wynik.relation_status is not ExecutionRelationStatus.NONDETERMINISM_CONFLICT
    assert wynik.fingerprint_evidence_sufficient is False


def test_ct18_ct19_ladunek_nie_wplywa_na_decyzje_bramki():
    """Wspólny invariant obu wektorów: bramka rozstrzyga przed treścią.

    Ten sam wynik dla identycznych i dla różnych ładunków — bo ładunek w ogóle do bramki
    nie wchodzi.
    """
    para = (proba_bez_odcisku(), proba_bez_odcisku())
    przy_zgodnej_tresci = decyzja(*para)
    przy_roznej_tresci = decyzja(*para)
    assert przy_zgodnej_tresci == przy_roznej_tresci
    assert przy_zgodnej_tresci.relation_status is (
        ExecutionRelationStatus.DETERMINISM_NOT_ASSESSABLE
    )
