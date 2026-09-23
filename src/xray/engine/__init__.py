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
from xray.engine.component_registry import (
    COMPONENT_REGISTRY,
    MGT01_DIMENSION_PREFIX,
    MGT01_DIMENSIONS,
    ComponentContractError,
    ComponentNotInRegistry,
    NullComponentNotAllowed,
    TestComponents,
    UnknownTest,
    WrongComponentType,
    check_component,
    components_for,
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
from xray.engine.units import (
    CriticalFinding,
    DependencyScope,
    StatusDerivation,
    StatusNotDerivable,
    UnitDeclaration,
    UnitExecutionStatus,
    UnitOutcome,
    UnresolvedApplicability,
    derive_test_status,
    evaluate_units,
)

__all__ = [
    "COMPONENT_REGISTRY",
    "ComponentContractError",
    "ComponentNotInRegistry",
    "CriticalFinding",
    "DependencyScope",
    "DiagnosticTest",
    "DiagnosticTestDeclaration",
    "ImportKnowledge",
    "MGT01_DIMENSIONS",
    "MGT01_DIMENSION_PREFIX",
    "MissingRequirement",
    "NOOP01_TEST_ID",
    "Noop01",
    "NullComponentNotAllowed",
    "ReadinessReason",
    "StatusDerivation",
    "StatusNotDerivable",
    "TESTS",
    "TestComponents",
    "TestReadiness",
    "UnitDeclaration",
    "UnitExecutionStatus",
    "UnitOutcome",
    "UnknownTest",
    "UnresolvedApplicability",
    "WrongComponentType",
    "check_component",
    "check_readiness",
    "components_for",
    "derive_test_status",
    "evaluate_units",
    "get_declaration",
    "get_test",
    "registered_test_ids",
    "run_test",
]
