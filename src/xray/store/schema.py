# Implementuje ZOP-TECH-01 v0.1 pkt 5.4 (trwały zapis FINDINGS), konwencję z CLAUDE.md
# (SQLite jako magazyn kanoniczny) oraz invariant wykonań z wpisu DT-21.
"""Schemat magazynu i projekcja kolumn.

## Klucze wynikają z invariantu, nie odwrotnie

| Tabela | Klucz | Co z niego wynika |
| --- | --- | --- |
| ``runs`` | ``run_id`` | przebieg: na jakich danych; kolumny wyliczalne z ``run_id`` |
| ``executions`` | ``execution_id``, ``UNIQUE (run_id, execution_fingerprint)`` | invariant |
| ``findings`` | ``(execution_id, finding_id)`` | wynik należy do konkretnego wykonania |

``execution_id`` powstaje z ``run_id + execution_fingerprint + result_digest``. Zapis
wykonania to ``INSERT … ON CONFLICT(execution_id) DO NOTHING``:

- ten sam odcisk i ta sama treść → ten sam ``execution_id`` → brak operacji,
- ten sam odcisk i inna treść → nowy ``execution_id``, ale naruszone
  ``UNIQUE (run_id, execution_fingerprint)`` → błąd ograniczenia, czyli sprzeczność,
- inny odcisk → nowy wiersz.

Rozstrzyga **baza**, a nie ``if`` w kodzie: nie da się zapisać dwóch różnych wyników dla tego
samego przebiegu i odcisku, nawet omijając ``FindingStore``.

**Nieznany odcisk** to ``NULL``. SQLite traktuje ``NULL``-e w ``UNIQUE`` jako różne, więc
wiele wykonań o nieznanym odcisku współistnieje — kontrola determinizmu jest dla nich
wyłączona, a ``fingerprint_status = 'unknown'`` mówi to wprost. ``CHECK`` pilnuje, żeby
status i obecność odcisku się nie rozjechały.

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
    input_digest               TEXT NOT NULL
)
"""

DDL_EXECUTIONS = """
CREATE TABLE IF NOT EXISTS executions (
    execution_id               TEXT PRIMARY KEY,
    run_id                     TEXT NOT NULL REFERENCES runs(run_id),
    execution_fingerprint      TEXT,
    fingerprint_status         TEXT NOT NULL,
    result_digest              TEXT NOT NULL,
    fingerprint_basis          TEXT NOT NULL,
    code_provenance            TEXT NOT NULL,
    input_provenance           TEXT NOT NULL,
    executed_at                TEXT,
    UNIQUE (run_id, execution_fingerprint),
    CHECK ((fingerprint_status = 'known') = (execution_fingerprint IS NOT NULL))
)
"""

DDL_FINDINGS = """
CREATE TABLE IF NOT EXISTS findings (
    execution_id               TEXT NOT NULL REFERENCES executions(execution_id),
    finding_id                 TEXT NOT NULL,
    run_id                     TEXT NOT NULL,
    test_id                    TEXT NOT NULL,
    scope_label                TEXT NOT NULL,
    period_start               TEXT NOT NULL,
    period_end                 TEXT NOT NULL,
    status                     TEXT NOT NULL,
    contract_version           TEXT NOT NULL,
    identity_algorithm_version TEXT NOT NULL,
    identity_canonical         TEXT NOT NULL,
    payload                    TEXT NOT NULL,
    PRIMARY KEY (execution_id, finding_id)
)
"""

DDL_FINDINGS_INDEX = """
CREATE INDEX IF NOT EXISTS findings_by_test
    ON findings (test_id, period_start, period_end)
"""

DDL_FINDINGS_BY_FINDING = """
CREATE INDEX IF NOT EXISTS findings_by_finding
    ON findings (finding_id)
"""


def connect(path: str | Path) -> sqlite3.Connection:
    """Otwiera połączenie i zakłada schemat, jeżeli go nie ma.

    ``:memory:`` jest poprawną ścieżką i używamy go w testach.
    """
    polaczenie = sqlite3.connect(path)
    polaczenie.row_factory = sqlite3.Row
    # Klucze obce findings → executions → runs mają być egzekwowane: wynik bez wykonania
    # i wykonanie bez przebiegu byłyby śladem bez odpowiedzi, na jakich danych i jakim
    # kodem powstały.
    polaczenie.execute("PRAGMA foreign_keys = ON")
    for ddl in (
        DDL_RUNS,
        DDL_EXECUTIONS,
        DDL_FINDINGS,
        DDL_FINDINGS_INDEX,
        DDL_FINDINGS_BY_FINDING,
    ):
        polaczenie.execute(ddl)
    polaczenie.commit()
    return polaczenie


def finding_columns(
    record: FindingRecord, run_id: str, execution_id: str
) -> dict[str, Any]:
    """Wylicza projekcję kolumn z rekordu.

    Jedyne miejsce, w którym powstają wartości kolumn. Dzięki temu kolumna nie może
    powiedzieć czegoś, czego nie mówi ``payload``.
    """
    return {
        "execution_id": execution_id,
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
