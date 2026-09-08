# Implementuje ZOP-TECH-01 v0.1 pkt 5.3 — rejestr kontroli danych wejściowych.
"""Warstwa kontroli danych.

Walidator sam nic nie blokuje — ogłasza statusy. To test deklaruje, które kontrole są dla
niego wymagane i co oznacza ich CRITICAL (``TEST_BLOCKED`` / ``TEST_PARTIAL``).

Wejściem kontroli jest ``ValidationContext``, a nie ramka: stan wiedzy o tabeli obejmuje
dane, to, co wiadomo o ich imporcie, i kontrakt, według którego powstały.
"""

from xray.validation.base import CheckDeclaration, DataCheck
from xray.validation.context import ValidationContext
from xray.validation.registry import (
    CHECKS,
    get_check,
    get_declaration,
    registered_check_ids,
    run_check,
    run_checks,
)
from xray.validation.results import (
    EVIDENCE_LIMIT,
    OBSERVATION_LIMIT,
    TEXT_VALUE_LIMIT,
    CheckObservation,
    CheckOutcome,
    CheckResult,
    NotAssessedReason,
    cap_observations,
)

__all__ = [
    "CHECKS",
    "EVIDENCE_LIMIT",
    "OBSERVATION_LIMIT",
    "TEXT_VALUE_LIMIT",
    "CheckDeclaration",
    "CheckObservation",
    "CheckOutcome",
    "CheckResult",
    "DataCheck",
    "NotAssessedReason",
    "ValidationContext",
    "cap_observations",
    "get_check",
    "get_declaration",
    "registered_check_ids",
    "run_check",
    "run_checks",
]
