# Implementuje ZOP-TECH-01 v0.1 pkt 5.4 (trwały zapis FINDINGS) oraz konwencję z CLAUDE.md
# (SQLite jako magazyn kanoniczny).
"""Schemat magazynu i projekcja kolumn.

## Payload jest rekordem, kolumny są indeksem

Odczyt rekonstruuje ``FindingRecord`` **wyłącznie** z kolumny ``payload``
(``model_validate_json``), więc przechodzi przez ``_check_identity`` i przez wszystkie
walidatory kontraktu. Kolumny służą do filtrowania bez parsowania treści i **nigdy** nie
są źródłem prawdy.

Projekcja kolumn powstaje jedną funkcją, z rekordu — nigdy nie jest ustawiana niezależnie.
Przy odczycie przeliczamy ją z ``payload`` i porównujemy z zapisaną: indeks, który po cichu
kłamie, jest gorszy od braku indeksu, bo zapytanie o ``status = 'WARNING'`` zwróciłoby zły
zbiór i nikt by się nie dowiedział.

## Dlaczego nie kolumna na pole kontraktu

Kolumna na pole wymagałaby odwzorowania typów, spłaszczenia ``ScopeRef`` / ``PeriodRef``
/ ``ReferenceRef``, kodowania krotek oraz **migracji przy każdym polu, które doda karta**.
To jest właśnie ten równoległy DDL, którego nie utrzymujemy: kontrakt FINDINGS ma rosnąć
razem z kartami, a schemat nie może być drugim miejscem, w którym trzeba to powtórzyć.
Nowe pole ląduje w ``payload`` bez zmiany schematu.
"""

import sqlite3
from pathlib import Path
from typing import Any

from xray.model import FindingRecord
from xray.model.findings.identity import canonical_form

DDL_RUNS = """
CREATE TABLE IF NOT EXISTS runs (
    run_id                     TEXT PRIMARY KEY,
    dataset_id                 TEXT NOT NULL,
    contract_version           TEXT NOT NULL,
    identity_algorithm_version TEXT NOT NULL,
    input_digest               TEXT NOT NULL,
    provenance                 TEXT NOT NULL,
    executed_at                TEXT
)
"""

DDL_FINDINGS = """
CREATE TABLE IF NOT EXISTS findings (
    finding_id                 TEXT NOT NULL,
    run_id                     TEXT NOT NULL REFERENCES runs(run_id),
    test_id                    TEXT NOT NULL,
    scope_label                TEXT NOT NULL,
    period_start               TEXT NOT NULL,
    period_end                 TEXT NOT NULL,
    status                     TEXT NOT NULL,
    contract_version           TEXT NOT NULL,
    identity_algorithm_version TEXT NOT NULL,
    identity_canonical         TEXT NOT NULL,
    payload                    TEXT NOT NULL,
    PRIMARY KEY (finding_id, run_id)
)
"""

DDL_FINDINGS_INDEX = """
CREATE INDEX IF NOT EXISTS findings_by_test
    ON findings (test_id, period_start, period_end)
"""


def connect(path: str | Path) -> sqlite3.Connection:
    """Otwiera połączenie i zakłada schemat, jeżeli go nie ma.

    ``:memory:`` jest poprawną ścieżką i używamy go w testach.
    """
    polaczenie = sqlite3.connect(path)
    polaczenie.row_factory = sqlite3.Row
    # Klucz obcy findings → runs ma być egzekwowany: wynik bez przebiegu byłby wynikiem
    # bez śladu, na jakich danych powstał.
    polaczenie.execute("PRAGMA foreign_keys = ON")
    for ddl in (DDL_RUNS, DDL_FINDINGS, DDL_FINDINGS_INDEX):
        polaczenie.execute(ddl)
    polaczenie.commit()
    return polaczenie


def finding_columns(record: FindingRecord, run_id: str) -> dict[str, Any]:
    """Wylicza projekcję kolumn z rekordu.

    Jedyne miejsce, w którym powstają wartości kolumn. Dzięki temu kolumna nie może
    powiedzieć czegoś, czego nie mówi ``payload``.
    """
    return {
        "finding_id": record.finding_id,
        "run_id": run_id,
        "test_id": record.test_id,
        "scope_label": record.scope.scope_label,
        "period_start": record.period.period_start.isoformat(),
        "period_end": record.period.period_end.isoformat(),
        "status": record.status.value,
        "contract_version": record.contract_version,
        "identity_algorithm_version": record.identity_algorithm_version,
        "identity_canonical": canonical_form(
            FindingRecord.identity_of(
                test_id=record.test_id,
                scope=record.scope,
                period=record.period,
                contract_version=record.contract_version,
                identity_algorithm_version=record.identity_algorithm_version,
            )
        ),
        "payload": record.model_dump_json(),
    }
