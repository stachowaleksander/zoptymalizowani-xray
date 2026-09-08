# Implementuje ZOP-TECH-01 v0.1 pkt 5.4 — trwały zapis wyników.
"""Magazyn: findings i ślad przebiegu.

Szew: ``model/findings`` to kontrakt, ``store/`` to zapis. FINDINGS jest jedynym miejscem
zapisu wyników — nikt nie liczy niczego obok.

Wynik jest kluczowany parą ``(finding_id, run_id)``. Dwa wiersze o tym samym
``finding_id`` i różnym ``run_id`` to dwie odpowiedzi na to samo pytanie, dane na różnych
danych — po ``finding_id`` da się prześledzić historię jednego wyniku przez kolejne
przebiegi. Patrz ``xray.store.runs``.

Dowody, twierdzenia, klastry i sprawy dojdą razem z CONF-01, PRI-01 i ORCH-01 — tą samą
receptą: własna tabela, ten sam zestaw kolumn tożsamości, ``payload`` jako treść.
"""

from xray.store.findings import ConflictingRun, FindingStore, ProjectionMismatch
from xray.store.runs import RunInput, RunRef
from xray.store.schema import connect, finding_columns

__all__ = [
    "ConflictingRun",
    "FindingStore",
    "ProjectionMismatch",
    "RunInput",
    "RunRef",
    "connect",
    "finding_columns",
]
