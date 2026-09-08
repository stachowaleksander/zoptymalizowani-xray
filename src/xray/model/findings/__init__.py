# Implementuje ZOP-TECH-01 v0.1 pkt 5.4 (FINDINGS) wraz z kontraktami
# ZOP-CONF-01 v1.0 rozdz. 3–4 i ZOP-PRI-01 v1.0 rozdz. 5 i 8.
"""Struktura wynikowa X-Ray.

FINDINGS nie jest jedną tabelą. ZOP-TECH-01 pkt 5.4 opisuje jedną płaską strukturę,
ale karty zamrożone wymagają małego grafu — i każde spłaszczenie łamie konkretny zapis:

| Relacja | Krotność | Źródło |
| --- | --- | --- |
| FindingRecord → ClaimRecord | 1 → 0..n | CONF-01 rozdz. 3, ``claim_source_finding_id`` |
| ClaimRecord ↔ EvidenceRecord | n ↔ n przez ``ClaimEvidenceLink`` | CONF-01 rozdz. 4, wpis B-05 |
| FindingRecord → PriorityRecord | 1 → 0..n (jedna na kontekst) | PRI-01 rozdz. 3 |
| FindingRecord → ClusterPriorityRecord | n → 0..1 | PRI-01 pkt 5.3 |

Kryterium doboru pól na tym etapie: **czy wartość da się odtworzyć po fakcie.**
Pola zapisujące kontekst chwili zapisu — tożsamość, wersja, kontekst kwalifikacji,
grupa wpływu, wspólne źródło dowodu — wchodzą teraz, nawet jeżeli żaden kod ich nie
wypełnia. Ich brak nie byłby brakiem funkcji, tylko trwałą utratą informacji. Pola
czysto opisowe wchodzą razem z kartą, która je wypełni.

Szew: to jest kontrakt. Trwały zapis mieszka w ``xray.store``, a nie tutaj.
"""

from xray.model.findings.claim import ClaimRecord
from xray.model.findings.evidence import ClaimEvidenceLink, EvidenceRecord
from xray.model.findings.finding import FindingRecord
from xray.model.findings.identity import CONTRACT_VERSION, canonical_form, compute_id
from xray.model.findings.priority import ClusterPriorityRecord, PriorityRecord
from xray.model.findings.refs import PeriodRef, ReferenceRef, ScopeRef

__all__ = [
    "CONTRACT_VERSION",
    "ClaimEvidenceLink",
    "ClaimRecord",
    "ClusterPriorityRecord",
    "EvidenceRecord",
    "FindingRecord",
    "PeriodRef",
    "PriorityRecord",
    "ReferenceRef",
    "ScopeRef",
    "canonical_form",
    "compute_id",
]
