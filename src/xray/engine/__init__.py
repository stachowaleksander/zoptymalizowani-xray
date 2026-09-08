# Implementuje ZOP-TECH-01 v0.1 pkt 10.5 — rejestr testów diagnostycznych jako wtyczek.
"""Silnik diagnostyczny: rejestr testów i kontrakt wtyczki.

Publiczny punkt importu warstwy. Test diagnostyczny deklaruje, czego wymaga i co
produkuje, a rejestr sprawdza tę deklarację wobec kontraktu danych przy imporcie.
"""

from xray.engine.base import (
    DiagnosticTest,
    DiagnosticTestDeclaration,
    ImportKnowledge,
    MissingRequirement,
    ReadinessReason,
    TestReadiness,
)
from xray.engine.noop01 import TEST_ID as NOOP01_TEST_ID
from xray.engine.noop01 import Noop01
from xray.engine.registry import (
    TESTS,
    check_readiness,
    get_declaration,
    get_test,
    registered_test_ids,
    run_test,
)

__all__ = [
    "NOOP01_TEST_ID",
    "TESTS",
    "DiagnosticTest",
    "Noop01",
    "DiagnosticTestDeclaration",
    "ImportKnowledge",
    "MissingRequirement",
    "ReadinessReason",
    "TestReadiness",
    "check_readiness",
    "get_declaration",
    "get_test",
    "registered_test_ids",
    "run_test",
]
