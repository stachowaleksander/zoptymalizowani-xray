# Implementuje ZOP-TECH-01 v0.1 pkt 5.4 — trwały zapis wyników.
"""Magazyn: findings, przebiegi i wykonania.

Szew: ``model/findings`` to kontrakt, ``store/`` to zapis. FINDINGS jest jedynym miejscem
zapisu wyników — nikt nie liczy niczego obok.

Trzy poziomy, każdy z własną tożsamością:

- **przebieg** (``RunRef``) — na jakich danych; ``run_id`` z treści wejścia,
- **wykonanie** (``ExecutionRef``) — jakim kodem i w jakim środowisku; odcisk bez czasu,
- **wynik** (``FindingRecord``) — odpowiedź na pytanie; ``finding_id`` z tożsamości wyniku.

Po ``finding_id`` da się prześledzić historię jednego wyniku przez kolejne przebiegi
i wykonania. Patrz ``xray.store.runs`` i ``xray.store.executions``.

Czwarty poziom powstaje obok trzech powyższych: **próba wykonania**
(``ExecutionAttemptRecord`` w ``xray.store.attempts``) — każde faktyczne uruchomienie
obliczenia z własnym, losowym identyfikatorem, tak żeby druga identyczna próba nie zniknęła
w deduplikacji. Przełączenie magazynu na ten poziom należy do pakietu P9.

Dowody, twierdzenia, klastry i sprawy dojdą razem z CONF-01, PRI-01 i ORCH-01 — tą samą
receptą: własna tabela, ten sam zestaw kolumn tożsamości, ``payload`` jako treść.
"""

from xray.store.attempts import (
    ExecutionAttemptRecord,
    ExecutionRelationStatus,
    GateDecision,
    attempt_required,
    compare_fingerprints,
)
from xray.store.comparisons import (
    COMPARISON_PROFILE_VERSION,
    ComparisonContextRef,
    ExecutionComparisonRecord,
    IncomparableExecutions,
    canonical_attempt_pair,
    check_comparable,
    classify,
)
from xray.store.executions import ExecutionRef, FingerprintStatus
from xray.store.findings import (
    FindingStore,
    ProjectionMismatch,
    SaveOutcome,
    StoredExecution,
)
from xray.store.results import (
    RECORD_IDENTITY_VERSION,
    CalculationResultRecord,
    ResultRecordError,
)
from xray.store.runs import RunInput, RunRef
from xray.store.schema import connect, finding_columns

__all__ = [
    "COMPARISON_PROFILE_VERSION",
    "CalculationResultRecord",
    "ComparisonContextRef",
    "ExecutionAttemptRecord",
    "ExecutionComparisonRecord",
    "ExecutionRef",
    "ExecutionRelationStatus",
    "FindingStore",
    "FingerprintStatus",
    "GateDecision",
    "IncomparableExecutions",
    "ProjectionMismatch",
    "RECORD_IDENTITY_VERSION",
    "ResultRecordError",
    "RunInput",
    "RunRef",
    "SaveOutcome",
    "StoredExecution",
    "attempt_required",
    "canonical_attempt_pair",
    "check_comparable",
    "classify",
    "compare_fingerprints",
    "connect",
    "finding_columns",
]
