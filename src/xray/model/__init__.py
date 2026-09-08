# Implementuje ZOP-TECH-01 v0.1 pkt 5.2 i 5.4 — kontrakt danych X-Ray.
"""Kontrakt danych: pięć tabel wejściowych, FINDINGS i wspólne słowniki.

To jedyny publiczny punkt importu warstwy modelu. Wyższe warstwy (``ingest``,
``mapping``, ``validation``, ``engine``, ``store``) importują stąd, a nie z modułów
wewnętrznych — dzięki temu przeniesienie pliku wewnątrz ``model/`` nie rozsypuje reszty.

Szew, którego nie wolno naruszyć: poniżej kontraktu danych nic nie wie, z jakiego pliku
przyszła liczba. W ``model/`` nie ma odczytu plików, pandas ani logiki liczącej.
Pochodzenie rekordu (plik, arkusz, numer wiersza) żyje w raporcie importu obok kontraktu,
a nie w jego polach — patrz ``xray.ingest``.
"""

from xray.model.enums import (
    ClaimType,
    ConfidenceClass,
    ConfidenceSourceLevel,
    EvidenceIndependenceStatus,
    EvidenceRole,
    ImpactAccountingRole,
    LogicalStatus,
    ManagementAttentionRoute,
    PriorityBasisStatus,
    ProblemPriorityAction,
    ReferenceType,
    TimeGrain,
    ValidationPriorityAction,
    ValidationStatus,
)
from xray.model.findings import (
    CONTRACT_VERSION,
    ClaimEvidenceLink,
    ClaimRecord,
    ClusterPriorityRecord,
    EvidenceRecord,
    FindingRecord,
    PeriodRef,
    PriorityRecord,
    ReferenceRef,
    ScopeRef,
)
from xray.model.registry import TABLES, get_table, table_names
from xray.model.tables.activity import ActivityRecord
from xray.model.tables.base import TableRecord
from xray.model.tables.cost import CostRecord
from xray.model.tables.plan import PlanRecord
from xray.model.tables.process import ProcessRecord
from xray.model.tables.resource import ResourceRecord

__all__ = [
    "CONTRACT_VERSION",
    "TABLES",
    "ActivityRecord",
    "ClaimEvidenceLink",
    "ClaimRecord",
    "ClaimType",
    "ClusterPriorityRecord",
    "ConfidenceClass",
    "ConfidenceSourceLevel",
    "CostRecord",
    "EvidenceIndependenceStatus",
    "EvidenceRecord",
    "EvidenceRole",
    "FindingRecord",
    "ImpactAccountingRole",
    "LogicalStatus",
    "ManagementAttentionRoute",
    "PeriodRef",
    "PlanRecord",
    "PriorityBasisStatus",
    "PriorityRecord",
    "ProblemPriorityAction",
    "ProcessRecord",
    "ReferenceRef",
    "ReferenceType",
    "ResourceRecord",
    "ScopeRef",
    "TableRecord",
    "TimeGrain",
    "ValidationPriorityAction",
    "ValidationStatus",
    "get_table",
    "table_names",
]
