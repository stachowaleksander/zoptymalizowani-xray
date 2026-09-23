# Implementuje ZOP-XR-FOUNDATION-BIND-01 v1.1, §7 (CANONICAL IDENTITY FRAMEWORK),
# §7.1 (identity payloads), §10 (scope), §11 (period), §12 (reference).
"""Profile kanoniczne i prymitywy tożsamości zbudowane wprost na nich.

Pakiet leży **poniżej** wszystkich warstw dziedzinowych: nie wie nic o tabelach, wynikach
ani przebiegach, a korzystać z niego będą `model/`, `store/` i `engine/`. Nazwa jest
`canonical`, a nie `identity`, bo kontrakt przewiduje cztery profile kanoniczne, z których
trzy nie są tożsamościami: `XR_IDENTITY_CANONICAL_JSON_V1` (`identity_json`),
`XR_PERIOD_CANONICAL_V1` (`period`), `XR_RESULT_PAYLOAD_CANONICAL_V1` (pakiet P5) oraz
`XR_CANONICAL_MULTISET_V1` (V12-R2, poza zakresem tej rundy).

Obok profili mieszkają tu prymitywy tożsamości z v1.1 §7.1, które są z nich złożone
i niczego więcej nie potrzebują: `scope_id` (`scope`) i `reference_id` (`reference`).
Wszystkie liczą się **tym samym** serializatorem — drugiego nie ma i mieć nie będzie
(karta V12-R1 §8: „Nie twórz drugiego canonical JSON serializer ani lokalnego wariantu").
"""

from xray.canonical.component import (
    ComponentRef,
    ComponentRefError,
    ComponentType,
    component_ref_payload,
)
from xray.canonical.exclusions import (
    CONTEXT_VERSION,
    EMPTY_CONTEXT,
    EffectiveExclusionContextV1,
    ExclusionApplication,
    ExclusionContractError,
)
from xray.canonical.identity_json import (
    PREFIXES,
    PROFILE,
    CanonicalizationError,
    CanonicalSet,
    DuplicateKey,
    DuplicateSetMember,
    ReservedKey,
    UnknownPrefix,
    UnsupportedType,
    canonical_bytes,
    canonical_text,
    digest,
    identity,
)
from xray.canonical.period import (
    CanonicalPeriod,
    Horizon,
    PeriodContractError,
    TimeBucket,
    period_payload,
)
from xray.canonical.reference import (
    ReferenceContractError,
    ReferenceDefinition,
    reference_id,
)
from xray.canonical.result_identity import (
    PAYLOAD_KEYS,
    RESULT_IDENTITY_VERSION,
    ResultIdentityError,
    ResultIdentityV2,
    result_identity,
)
from xray.canonical.result_payload import (
    ENVELOPE_KEYS,
    RESULT_PAYLOAD_PROFILE,
    ResultPayloadEnvelopeV1,
    ResultPayloadError,
    artifact_sha256,
    result_payload_digest,
)
from xray.canonical.scope import (
    ScopeContractError,
    ScopeDefinition,
    ScopeOperator,
    ScopePredicate,
    scope_id,
)

__all__ = [
    "CONTEXT_VERSION",
    "CanonicalPeriod",
    "CanonicalSet",
    "CanonicalizationError",
    "ComponentRef",
    "ComponentRefError",
    "ComponentType",
    "DuplicateKey",
    "DuplicateSetMember",
    "EMPTY_CONTEXT",
    "ENVELOPE_KEYS",
    "EffectiveExclusionContextV1",
    "ExclusionApplication",
    "ExclusionContractError",
    "Horizon",
    "PAYLOAD_KEYS",
    "PREFIXES",
    "PROFILE",
    "PeriodContractError",
    "RESULT_IDENTITY_VERSION",
    "RESULT_PAYLOAD_PROFILE",
    "ReferenceContractError",
    "ReferenceDefinition",
    "ReservedKey",
    "ResultIdentityError",
    "ResultIdentityV2",
    "ResultPayloadEnvelopeV1",
    "ResultPayloadError",
    "ScopeContractError",
    "ScopeDefinition",
    "ScopeOperator",
    "ScopePredicate",
    "TimeBucket",
    "UnknownPrefix",
    "UnsupportedType",
    "artifact_sha256",
    "canonical_bytes",
    "canonical_text",
    "component_ref_payload",
    "digest",
    "identity",
    "period_payload",
    "reference_id",
    "result_identity",
    "result_payload_digest",
    "scope_id",
]
