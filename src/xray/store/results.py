# Implementuje ZOP-XR-V12-R1 kartę wykonawczą §10 (CalculationResultRecord) oraz
# ZOP-XR-FOUNDATION-BIND-01 v1.2 §7.4 (profil XR_CALCULATION_RESULT_RECORD_IDENTITY_V1),
# przy rozstrzygnięciu Controllingu z 2026-09-23 w sprawie Q1.
"""Niezmienny rekord jednego policzonego wyniku.

    result_record_id = "RREC-" + SHA256(XR_IDENTITY_CANONICAL_JSON_V1({
        record_identity_version, result_identity, semantic_run_id,
        execution_attempt_id, effective_exclusion_context_digest, result_payload_digest }))

## Pytanie a odpowiedź

``result_identity`` to **pytanie** i jest stabilne przez kolejne przebiegi, wykonania
i konteksty wyłączeń (v1.2 §7.2: ``RESULT_IDENTITY_STABLE_ACROSS_SEMANTIC_RUNS = true``).
Ten rekord to **odpowiedź**: konkretna, policzona raz, w konkretnym przebiegu danych,
konkretną próbą i przy konkretnym kontekście wyłączeń. Karta §10: „Jeden result_identity
może mieć wiele records dla różnych semantic runs, attempts i effective exclusion contexts".

## Sześć składników tożsamości — i ani jednego więcej

Proweniencja profilu przebiegu z rozstrzygnięcia Q1 (``semantic_run_profile``,
``semantic_run_identity_version``) jest **polem rekordu obok tożsamości**, nie jej
składnikiem. Dopisanie jej do krotki dałoby siódmy element, czyli przesłankę STOP R1-S06
(„Poprawny result wymaga dodania nowego semantic ingredient"). To samo dotyczy znaczników
czasu, odcisku wykonania i schematu ładunku: są w rekordzie, nie w skrócie.

## Spójność osi komponentu

Karta §10: ``calculation_component_ref`` „must equal component used in result_identity".
Dlatego ``create`` przyjmuje **obiekt pytania** (``ResultIdentityV2``), a nie sam łańcuch
tożsamości — komponent i tożsamość biorą się z jednego źródła i nie mają jak się rozjechać.
Rekord, który mówi co innego niż jego własna tożsamość, nie może tu powstać.

## Kolejność z karty §10.1

Tożsamość → legalne wyłączenia → klucze zastosowań → kontekst → obliczenie → rekord.
Wymusza ją sygnatura: skrót kontekstu liczy się z ``result_identity``, a ``create`` żąda
już policzonego ``result_payload_digest``. Nie da się zbudować rekordu, odwracając te kroki.
"""

import datetime as dt

from pydantic import BaseModel, ConfigDict, model_validator

from xray.canonical.component import ComponentRef, component_ref_payload
from xray.canonical.exclusions import EMPTY_CONTEXT, EffectiveExclusionContextV1
from xray.canonical.identity_json import identity
from xray.canonical.result_identity import ResultIdentityV2, result_identity
from xray.store.attempts import (
    SEMANTIC_RUN_PROFILE,
    ExecutionAttemptRecord,
)
from xray.store.executions import FingerprintStatus
from xray.store.runs import RUN_IDENTITY_VERSION

RECORD_IDENTITY_VERSION = "XR_CALCULATION_RESULT_RECORD_IDENTITY_V1"
"""Profil tożsamości rekordu (karta §10, v1.2 §7.4).

Zamrożony: „nie twórz nowej wersji ani dodatkowych identity ingredients bez decyzji
Controllingu".
"""

_PREFIX = "RREC"


class ResultRecordError(ValueError):
    """Rekord nie spełnia kontraktu karty §10."""


class CalculationResultRecord(BaseModel):
    """Jedna policzona odpowiedź, zapisana raz i niezmienna."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    # --- tożsamość (sześć składników) ------------------------------------------------
    result_record_id: str
    record_identity_version: str = RECORD_IDENTITY_VERSION
    result_identity: str
    semantic_run_id: str
    execution_attempt_id: str
    effective_exclusion_context_digest: str
    result_payload_digest: str

    # --- wiązania semantyczne obok tożsamości ----------------------------------------
    calculation_component_ref: ComponentRef | None = None
    """Ten sam komponent, którego użyła ``result_identity`` (karta §10)."""

    result_payload_schema_version: str
    """Wersja schematu ładunku. Hashowana **wewnątrz koperty**, nie w tej krotce."""

    # --- proweniencja ----------------------------------------------------------------
    semantic_run_profile: str = SEMANTIC_RUN_PROFILE
    semantic_run_identity_version: str = RUN_IDENTITY_VERSION
    """Proweniencja profilu przebiegu (Q1). Pole rekordu — **poza** tożsamością."""

    execution_fingerprint_reference: str | None = None
    fingerprint_status: FingerprintStatus
    result_payload_ref: str | None = None
    source_input_evidence_refs: tuple[str, ...] = ()
    recorded_at: dt.datetime | None = None
    """Znacznik zapisu. Proweniencja — nie wchodzi do żadnego skrótu (v1.2 §7.4.2)."""

    foundation_bind_version: str

    @model_validator(mode="after")
    def _check_referencje(self) -> "CalculationResultRecord":
        if not self.result_identity.startswith("RESULT-"):
            raise ValueError(f"result_identity {self.result_identity!r} ma zły prefiks")
        if not self.semantic_run_id.strip():
            raise ValueError("semantic_run_id jest obowiązkowy na rekordzie (Q1)")
        if not self.execution_attempt_id.strip():
            raise ValueError("execution_attempt_id jest obowiązkowy (karta §10)")
        if self.fingerprint_status is FingerprintStatus.KNOWN and (
            self.execution_fingerprint_reference is None
        ):
            raise ValueError("status KNOWN wymaga niepustej referencji odcisku (karta §9)")
        if self.fingerprint_status is FingerprintStatus.UNKNOWN and (
            self.execution_fingerprint_reference is not None
        ):
            raise ValueError("status UNKNOWN wymaga canonical null (karta §9)")
        return self

    @classmethod
    def identity_of(
        cls,
        *,
        result_identity_value: str,
        semantic_run_id: str,
        execution_attempt_id: str,
        effective_exclusion_context_digest: str,
        result_payload_digest: str,
    ) -> str:
        """Skrót rekordu z **dokładnie sześciu** składników (karta §10)."""
        return identity(
            _PREFIX,
            {
                "effective_exclusion_context_digest": effective_exclusion_context_digest,
                "execution_attempt_id": execution_attempt_id,
                "record_identity_version": RECORD_IDENTITY_VERSION,
                "result_identity": result_identity_value,
                "result_payload_digest": result_payload_digest,
                "semantic_run_id": semantic_run_id,
            },
        )

    @classmethod
    def create(
        cls,
        *,
        question: ResultIdentityV2,
        attempt: ExecutionAttemptRecord,
        result_payload_digest: str,
        result_payload_schema_version: str,
        context: EffectiveExclusionContextV1 = EMPTY_CONTEXT,
        result_payload_ref: str | None = None,
        source_input_evidence_refs: tuple[str, ...] = (),
        recorded_at: dt.datetime | None = None,
    ) -> "CalculationResultRecord":
        """Buduje rekord z pytania i z faktycznie wykonanej próby.

        Przyjmuje **obiekty**, a nie łańcuchy, i stąd biorą się dwie gwarancje z karty §10,
        których nie da się tu obejść:

        1. ``calculation_component_ref`` rekordu pochodzi z tego samego pytania, z którego
           policzono ``result_identity`` — nie mogą się rozjechać,
        2. proweniencja przebiegu (``semantic_run_id`` i deklaracja profilu) pochodzi
           z próby, więc rekord nie może twierdzić, że powstał w innym przebiegu niż ta
           próba.
        """
        tozsamosc = result_identity(question)
        skrot_kontekstu = context.digest(tozsamosc)
        return cls(
            result_record_id=cls.identity_of(
                result_identity_value=tozsamosc,
                semantic_run_id=attempt.semantic_run_id,
                execution_attempt_id=attempt.execution_attempt_id,
                effective_exclusion_context_digest=skrot_kontekstu,
                result_payload_digest=result_payload_digest,
            ),
            result_identity=tozsamosc,
            semantic_run_id=attempt.semantic_run_id,
            execution_attempt_id=attempt.execution_attempt_id,
            effective_exclusion_context_digest=skrot_kontekstu,
            result_payload_digest=result_payload_digest,
            calculation_component_ref=question.calculation_component_ref,
            result_payload_schema_version=result_payload_schema_version,
            semantic_run_profile=attempt.semantic_run_profile,
            semantic_run_identity_version=attempt.semantic_run_identity_version,
            execution_fingerprint_reference=attempt.execution_fingerprint,
            fingerprint_status=attempt.fingerprint_status,
            result_payload_ref=result_payload_ref,
            source_input_evidence_refs=source_input_evidence_refs,
            recorded_at=recorded_at,
            foundation_bind_version=attempt.foundation_bind_version,
        )

    def matches_question(self, question: ResultIdentityV2) -> bool:
        """Czy rekord mówi to samo, co jego własna tożsamość.

        Karta §10 wymaga, żeby komponent rekordu był identyczny z tym użytym
        w ``result_identity``. Sprawdzamy oba warunki naraz: zgodność skrótu i zgodność osi
        komponentu.
        """
        return self.result_identity == result_identity(question) and component_ref_payload(
            self.calculation_component_ref
        ) == component_ref_payload(question.calculation_component_ref)
