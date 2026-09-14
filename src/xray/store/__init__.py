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

Dowody, twierdzenia, klastry i sprawy dojdą razem z CONF-01, PRI-01 i ORCH-01 — tą samą
receptą: własna tabela, ten sam zestaw kolumn tożsamości, ``payload`` jako treść.
"""

from xray.store.executions import ExecutionRef, FingerprintStatus
from xray.store.findings import (
    ConflictingRun,
    FindingStore,
    ProjectionMismatch,
    StoredExecution,
)
from xray.store.runs import RunInput, RunRef
from xray.store.schema import connect, finding_columns

__all__ = [
    "ConflictingRun",
    "ExecutionRef",
    "FindingStore",
    "FingerprintStatus",
    "ProjectionMismatch",
    "RunInput",
    "RunRef",
    "StoredExecution",
    "connect",
    "finding_columns",
]
