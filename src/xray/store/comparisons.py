# Implementuje ZOP-XR-V12-R1 kartę wykonawczą §11 i §11.1 (ExecutionComparisonRecord,
# pairwise relation only) oraz ZOP-XR-FOUNDATION-BIND-01 v1.2 §7.4.3 i korektę C-09.
"""Relacja między dwiema próbami — parowa, niezmienna i bez stanu skalarnego.

## Dwa różne pytania, które łatwo pomylić

**Bramka z P7** (``compare_fingerprints``) odpowiada wyłącznie na pytanie o **odciski**:
czy z dowodu wykonania wynika, że to było to samo kodowo i środowiskowo uruchomienie.

**Porównywalność kontekstu** to osobne pytanie, którego bramka nie zna: czy te dwie próby
w ogóle liczyły **to samo**. Karta §11: „comparison_context_reference musi wykazać
porównywalność co najmniej result_identity, semantic_run_id, EffectiveExclusionContext oraz
fingerprint evidence".

Dlatego kontekst sprawdzamy **przed** bramką, osobnym krokiem, i przy rozjeździe
**odmawiamy porównania** zamiast je klasyfikować. Inaczej ``NONDETERMINISM_CONFLICT``
pojawiłby się tam, gdzie po prostu policzono dwie różne rzeczy — a to jest zarzut
najcięższego kalibru: mówi „ten sam kod dał dwa różne wyniki".

Szczególny przypadek jest wprost w karcie §11.1: różny ``EffectiveExclusionContext`` to
„Legalne odrębne result records; **samo w sobie NOT_NONDETERMINISM**".

## Trzy statusy i przypadek bez rekordu

Katalog ``ExecutionRelationStatus`` ma trzy wartości i czwartej nie dostanie. Para o obu
odciskach znanych, ale **różnych**, nie dostaje rekordu w ogóle — karta §11.1: „Nie
kwalifikuj jako idempotence ani nondeterminism tego samego exact execution. Nie wymyślaj
nowego statusu; neutralny status nie jest wymagany przez v1.2". ``classify`` zwraca wtedy
``None``.

## Tożsamość niezależna od kolejności i od czasu

    comparison_pair = sort_bytewise([execution_attempt_id_A, execution_attempt_id_B])
    execution_comparison_id = "ECMP-" + SHA256(XR_IDENTITY_CANONICAL_JSON_V1({
        comparison_profile_version, canonical_attempt_pair, comparison_context_reference }))

``EXECUTION_COMPARISON_ID_ORDER_INDEPENDENT = true`` (karta §11), więc para jest sortowana
bajtowo, zanim wejdzie do skrótu. Znacznik czasu **nie jest składnikiem** — v1.2 §7.4.3:
„Timestamp nie jest składnikiem canonical relation identity. Ponowna ocena tej samej
pair/context nie może tworzyć odmiennej semantic relation identity wyłącznie przez czas".

## Zero nadpisania i zero stanu skalarnego

Rekord porównania niczego nie zastępuje: obie próby, oba rekordy wyniku i oba skróty
ładunku zostają. Status relacji mieszka **wyłącznie** tutaj —
``EXECUTION_EQUIVALENCE_STATUS_IS_INTRINSIC_RESULT_RECORD_FIELD = false`` i
``…_ATTEMPT_FIELD = false`` (karta §11); zapisanie go na próbie albo na rekordzie wyniku
byłoby przesłanką STOP R1-S13. Jedna próba może uczestniczyć w wielu niezależnych
relacjach (``ONE_ATTEMPT_MAY_HAVE_MULTIPLE_COMPARISON_RELATIONS = true``) i żadna z nich
nie jest jej „statusem globalnym".
"""

import datetime as dt
from typing import Any

from pydantic import BaseModel, ConfigDict, model_validator

from xray.canonical.identity_json import CanonicalSet, identity
from xray.store.attempts import (
    ExecutionAttemptRecord,
    ExecutionRelationStatus,
    compare_fingerprints,
)
from xray.store.results import CalculationResultRecord

COMPARISON_PROFILE_VERSION = "XR_EXECUTION_COMPARISON_V1"
"""Profil relacji (karta §11: ``COMPARISON_PROFILE_VERSION``)."""

_PREFIX = "ECMP"

RELATION_SAME = "same"
RELATION_DIFFERENT = "different"
RELATION_NOT_ASSESSABLE = "not_assessable"
"""Trzy słowa, którymi opisujemy pojedynczą oś porównania.

Karta §11 wymaga pól ``fingerprint_relation``, ``payload_relation``
i ``effective_exclusion_context_relation``, ale **nie podaje dla nich katalogu** — tak samo
jak dla ``terminal_status`` próby. To są więc nasze opisy wyprowadzone z faktów, nie
związany słownik; patrz wpis B-14.
"""


class IncomparableExecutions(ValueError):
    """Prób nie wolno porównać, bo nie liczyły tego samego.

    To **nie jest** wynik porównania ani czwarty status — to odmowa jego wykonania.
    """


class ComparisonContextRef(BaseModel):
    """Dowód porównywalności kontekstu (karta §11).

    Trzy rzeczy, które muszą się zgadzać, zanim w ogóle wolno mówić o determinizmie:
    to samo pytanie diagnostyczne, ten sam przebieg danych i zgodny kontekst wyłączeń.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    result_identity: str
    semantic_run_id: str
    effective_exclusion_context_digest: str

    def payload(self) -> dict[str, Any]:
        return {
            "effective_exclusion_context_digest": self.effective_exclusion_context_digest,
            "result_identity": self.result_identity,
            "semantic_run_id": self.semantic_run_id,
        }


def canonical_attempt_pair(first: str, second: str) -> tuple[str, str]:
    """Para posortowana bajtowo (karta §11: ``sort_bytewise``).

    Dzięki temu ``(A, B)`` i ``(B, A)`` to ta sama para — i ten sam identyfikator relacji.
    """
    if first == second:
        raise IncomparableExecutions(
            f"próba {first!r} nie tworzy pary sama ze sobą; relacja jest między dwiema "
            "faktycznie wykonanymi próbami"
        )
    return tuple(sorted((first, second), key=lambda wartosc: wartosc.encode("utf-8")))


def check_comparable(
    first: CalculationResultRecord, second: CalculationResultRecord
) -> ComparisonContextRef:
    """Osobny krok **przed** bramką odcisków: czy te dwa obliczenia są porównywalne.

    Przy rozjeździe którejkolwiek z trzech osi podnosi ``IncomparableExecutions``. Odmowa,
    a nie status: para z różnych pytań diagnostycznych nie jest „niedeterministyczna",
    tylko niezestawialna.
    """
    if first.result_identity != second.result_identity:
        raise IncomparableExecutions(
            "rekordy odpowiadają na różne pytania diagnostyczne "
            f"({first.result_identity} vs {second.result_identity}); porównanie "
            "determinizmu nie ma tu sensu"
        )
    if first.semantic_run_id != second.semantic_run_id:
        raise IncomparableExecutions(
            "rekordy pochodzą z różnych przebiegów danych "
            f"({first.semantic_run_id} vs {second.semantic_run_id}); różnica wyniku może "
            "brać się z danych, nie z wykonania"
        )
    if (
        first.effective_exclusion_context_digest != second.effective_exclusion_context_digest
    ):
        raise IncomparableExecutions(
            "rekordy mają różny EffectiveExclusionContext; karta §11.1: legalne odrębne "
            "result records, samo w sobie NOT_NONDETERMINISM"
        )
    return ComparisonContextRef(
        result_identity=first.result_identity,
        semantic_run_id=first.semantic_run_id,
        effective_exclusion_context_digest=first.effective_exclusion_context_digest,
    )


class ExecutionComparisonRecord(BaseModel):
    """Niezmienna relacja między dwiema próbami (karta §11)."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    execution_comparison_id: str
    comparison_profile_version: str = COMPARISON_PROFILE_VERSION

    execution_attempt_id_a: str
    execution_attempt_id_b: str
    """Para w postaci kanonicznej: posortowana bajtowo."""

    comparison_context_reference: ComparisonContextRef

    fingerprint_relation: str
    payload_relation: str
    effective_exclusion_context_relation: str

    execution_relation_status: ExecutionRelationStatus
    basis: str

    created_at: dt.datetime | None = None
    assessed_at: dt.datetime | None = None
    """Proweniencja oceny. **Poza** tożsamością relacji (v1.2 §7.4.3)."""

    foundation_bind_version: str

    @model_validator(mode="after")
    def _check_para(self) -> "ExecutionComparisonRecord":
        if (self.execution_attempt_id_a, self.execution_attempt_id_b) != canonical_attempt_pair(
            self.execution_attempt_id_a, self.execution_attempt_id_b
        ):
            raise ValueError(
                "para prób nie jest w postaci kanonicznej; identyfikator relacji ma być "
                "niezależny od kolejności (karta §11)"
            )
        if not self.basis.strip():
            raise ValueError("basis nie może być pusty (karta §11)")
        return self

    @classmethod
    def identity_of(
        cls, pair: tuple[str, str], context: ComparisonContextRef
    ) -> str:
        """``"ECMP-" + SHA256(…{profil, kanoniczna para, referencja kontekstu})``."""
        return identity(
            _PREFIX,
            {
                "canonical_attempt_pair": CanonicalSet(pair),
                "comparison_context_reference": context.payload(),
                "comparison_profile_version": COMPARISON_PROFILE_VERSION,
            },
        )


def classify(
    attempt_a: ExecutionAttemptRecord,
    record_a: CalculationResultRecord,
    attempt_b: ExecutionAttemptRecord,
    record_b: CalculationResultRecord,
    *,
    assessed_at: dt.datetime | None = None,
) -> ExecutionComparisonRecord | None:
    """Kwalifikuje parę prób — albo stwierdza, że rekord relacji nie powstaje.

    Kolejność kroków jest częścią kontraktu:

    1. **porównywalność kontekstu** (``check_comparable``) — przy rozjeździe odmowa,
    2. **bramka odcisków** (``compare_fingerprints``) — czy dowód wykonania cokolwiek
       przesądza,
    3. **porównanie treści** — dopiero gdy odciski są znane i równe.

    Zwraca ``None``, gdy oba odciski są znane i różne: to nie to samo exact execution,
    a czwartego statusu katalog nie ma (karta §11.1).
    """
    if record_a.execution_attempt_id != attempt_a.execution_attempt_id:
        raise IncomparableExecutions("rekord A nie należy do próby A")
    if record_b.execution_attempt_id != attempt_b.execution_attempt_id:
        raise IncomparableExecutions("rekord B nie należy do próby B")

    context = check_comparable(record_a, record_b)
    para = canonical_attempt_pair(
        attempt_a.execution_attempt_id, attempt_b.execution_attempt_id
    )
    bramka = compare_fingerprints(
        attempt_a.fingerprint_status,
        attempt_a.execution_fingerprint,
        attempt_b.fingerprint_status,
        attempt_b.execution_fingerprint,
    )
    ten_sam_ladunek = record_a.result_payload_digest == record_b.result_payload_digest
    payload_relation = RELATION_SAME if ten_sam_ladunek else RELATION_DIFFERENT

    if bramka.relation_status is ExecutionRelationStatus.DETERMINISM_NOT_ASSESSABLE:
        status = ExecutionRelationStatus.DETERMINISM_NOT_ASSESSABLE
        fingerprint_relation = RELATION_NOT_ASSESSABLE
    elif not bramka.fingerprint_evidence_sufficient:
        # Oba odciski znane i różne — rekord relacji nie powstaje.
        return None
    else:
        fingerprint_relation = RELATION_SAME
        status = (
            ExecutionRelationStatus.IDEMPOTENT_EQUIVALENT
            if ten_sam_ladunek
            else ExecutionRelationStatus.NONDETERMINISM_CONFLICT
        )

    return ExecutionComparisonRecord(
        execution_comparison_id=ExecutionComparisonRecord.identity_of(para, context),
        execution_attempt_id_a=para[0],
        execution_attempt_id_b=para[1],
        comparison_context_reference=context,
        fingerprint_relation=fingerprint_relation,
        payload_relation=payload_relation,
        effective_exclusion_context_relation=RELATION_SAME,
        execution_relation_status=status,
        basis=bramka.basis,
        created_at=assessed_at,
        assessed_at=assessed_at,
        foundation_bind_version=attempt_a.foundation_bind_version,
    )
