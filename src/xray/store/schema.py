# Implementuje ZOP-TECH-01 v0.1 pkt 5.4 (trwały zapis FINDINGS), konwencję z CLAUDE.md
# (SQLite jako magazyn kanoniczny) oraz ZOP-XR-V12-R1 kartę wykonawczą §9
# (EVERY_ACTUAL_EXECUTION_ATTEMPT_PERSISTED) — przełączenie opisane we wpisie DT-21.
"""Schemat magazynu i projekcja kolumn.

## Klucze wynikają z invariantu, nie odwrotnie

| Tabela | Klucz | Co z niego wynika |
| --- | --- | --- |
| ``runs`` | ``run_id`` | przebieg: na jakich danych; kolumny wyliczalne z ``run_id`` |
| ``executions`` | ``execution_id`` | **opis** wykonania: przebieg + odcisk + skrót treści |
| ``execution_attempts`` | ``execution_attempt_id`` | **zdarzenie**: jedna wykonana próba |
| ``findings`` | ``(execution_id, finding_id)`` | wynik należy do konkretnego wykonania |

## Co się zmieniło w rundzie V12-R1

Do tej rundy schemat **zabraniał sprzeczności**: ``UNIQUE (run_id, execution_fingerprint)``
sprawiał, że drugi, inny wynik tego samego przebiegu i odcisku po prostu nie dał się
zapisać. Wyglądało to na mocny invariant, a było utratą dowodu: przepływ niedeterministyczny
zostawiał po sobie **jeden** wynik i wyjątek, zamiast dwóch wyników do porównania.

Karta §9 stawia sprawę odwrotnie: ``EVERY_ACTUAL_EXECUTION_ATTEMPT_PERSISTED = true``
i ``IDENTICAL_ATTEMPT_MAY_NOT_BE_DROPPED_BY_STORAGE_DEDUPLICATION = true``. Najpierw
zachowujemy oba dowody, dopiero potem klasyfikujemy relację — w
``ExecutionComparisonRecord`` (karta §11). Dlatego:

- ``UNIQUE (run_id, execution_fingerprint)`` **zniknął**,
- każdy zapis dokłada wiersz do ``execution_attempts`` z własnym, losowym
  ``execution_attempt_id`` — dwie identyczne próby to dwa wiersze,
- ``executions`` zostaje tabelą **opisu**: ``execution_id`` powstaje z treści
  (``run_id + execution_fingerprint + result_digest``), więc ten sam identyfikator znaczy
  dosłownie ten sam opis. Powtórzenie opisu niczego nie gubi, bo zdarzenie zapisała próba.

**Nieznany odcisk** to ``NULL``; ``CHECK`` pilnuje, żeby status i obecność odcisku się nie
rozjechały. Porównywanie dwóch ``NULL``-i nigdy nie dowodzi tego samego wykonania — pilnuje
tego bramka ``compare_fingerprints`` z ``store/attempts.py``, a nie schemat.

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
    CHECK ((fingerprint_status = 'known') = (execution_fingerprint IS NOT NULL))
)
"""

DDL_ATTEMPTS = """
CREATE TABLE IF NOT EXISTS execution_attempts (
    execution_attempt_id          TEXT PRIMARY KEY,
    semantic_run_id               TEXT NOT NULL REFERENCES runs(run_id),
    semantic_run_profile          TEXT NOT NULL,
    semantic_run_identity_version TEXT NOT NULL,
    execution_id                  TEXT NOT NULL REFERENCES executions(execution_id),
    execution_fingerprint         TEXT,
    fingerprint_status            TEXT NOT NULL,
    execution_provenance_ref      TEXT NOT NULL,
    attempt_started_at            TEXT,
    attempt_completed_at          TEXT,
    terminal_status               TEXT NOT NULL,
    foundation_bind_version       TEXT NOT NULL,
    payload                       TEXT NOT NULL,
    CHECK ((fingerprint_status = 'known') = (execution_fingerprint IS NOT NULL))
)
"""

DDL_ATTEMPTS_INDEX = """
CREATE INDEX IF NOT EXISTS attempts_by_run
    ON execution_attempts (semantic_run_id, execution_fingerprint)
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
        DDL_ATTEMPTS,
        DDL_ATTEMPTS_INDEX,
    ):
        polaczenie.execute(ddl)
    migrate_executions(polaczenie)
    polaczenie.commit()
    return polaczenie


def migrate_executions(connection: sqlite3.Connection) -> bool:
    """Zdejmuje ``UNIQUE (run_id, execution_fingerprint)`` z istniejącej bazy.

    SQLite nie umie usunąć ograniczenia w miejscu, więc tabelę trzeba przebudować:
    nowa tabela, przepisanie **wszystkich** wierszy, podmiana nazwy. Zwraca, czy migracja
    była potrzebna.

    Zero utraty danych jest tu warunkiem, nie życzeniem: historyczne wykonania są dowodem
    i karta §1 zakazuje ich przeliczania (``HISTORICAL_IDENTITY_REWRITE = false``).
    Przepisujemy wiersze takimi, jakie są — żaden identyfikator nie jest liczony od nowa.
    """
    wiersz = connection.execute(
        "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = 'executions'"
    ).fetchone()
    if wiersz is None or "UNIQUE (run_id, execution_fingerprint)" not in wiersz[0]:
        return False

    connection.execute("PRAGMA foreign_keys = OFF")
    try:
        connection.execute(DDL_EXECUTIONS.replace("executions", "executions_bez_unique", 1))
        connection.execute(
            "INSERT INTO executions_bez_unique SELECT * FROM executions"
        )
        connection.execute("DROP TABLE executions")
        connection.execute("ALTER TABLE executions_bez_unique RENAME TO executions")
    finally:
        connection.execute("PRAGMA foreign_keys = ON")
    connection.commit()
    return True


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
