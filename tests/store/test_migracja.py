# Sprawdza przebudowę tabeli executions przy przełączeniu z rundy V12-R1.
"""Zero utraty danych przy zdejmowaniu ``UNIQUE (run_id, execution_fingerprint)``.

SQLite nie umie usunąć ograniczenia w miejscu, więc ``connect`` przebudowuje tabelę:
nowa, przepisanie wierszy, podmiana nazwy. Historyczne wykonania są dowodem, a karta §1
ustala ``HISTORICAL_IDENTITY_REWRITE = false`` — więc przepisujemy je takimi, jakie są,
bez liczenia czegokolwiek od nowa.
"""

import sqlite3
from pathlib import Path

import pytest

from xray.store.schema import connect, migrate_executions

STARY_SCHEMAT = """
CREATE TABLE runs (
    run_id                     TEXT PRIMARY KEY,
    dataset_id                 TEXT NOT NULL,
    contract_version           TEXT NOT NULL,
    identity_algorithm_version TEXT NOT NULL,
    input_digest               TEXT NOT NULL
);
CREATE TABLE executions (
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
);
INSERT INTO runs VALUES ('RUN-historyczny', 'klient', 'ZOP-TECH-01/v0.1', '3', '{}');
INSERT INTO executions VALUES
    ('EXE-pierwsze', 'RUN-historyczny', 'FPR-a', 'known', 'RSET-1', '{}', '{}', '{}', NULL),
    ('EXE-drugie', 'RUN-historyczny', 'FPR-b', 'known', 'RSET-2', '{}', '{}', '{}', NULL);
"""


@pytest.fixture
def stara_baza(tmp_path: Path) -> Path:
    sciezka = tmp_path / "stara.sqlite"
    polaczenie = sqlite3.connect(sciezka)
    polaczenie.executescript(STARY_SCHEMAT)
    polaczenie.commit()
    polaczenie.close()
    return sciezka


def test_wiersze_przezywaja_przebudowe(stara_baza: Path) -> None:
    """Warunek twardy przełączenia: zero utraty danych."""
    polaczenie = connect(stara_baza)
    wiersze = polaczenie.execute(
        "SELECT execution_id, run_id, execution_fingerprint, result_digest "
        "FROM executions ORDER BY execution_id"
    ).fetchall()
    assert [tuple(w) for w in wiersze] == [
        ("EXE-drugie", "RUN-historyczny", "FPR-b", "RSET-2"),
        ("EXE-pierwsze", "RUN-historyczny", "FPR-a", "RSET-1"),
    ]


def test_ograniczenie_znika(stara_baza: Path) -> None:
    polaczenie = connect(stara_baza)
    definicja = polaczenie.execute(
        "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = 'executions'"
    ).fetchone()[0]
    assert "UNIQUE (run_id, execution_fingerprint)" not in definicja
    assert "CHECK" in definicja


def test_po_migracji_da_sie_zapisac_to_co_stary_schemat_odrzucal(stara_baza: Path) -> None:
    """Sedno przełączenia: drugi, inny wynik tego samego odcisku ma prawo istnieć."""
    polaczenie = connect(stara_baza)
    polaczenie.execute(
        "INSERT INTO executions (execution_id, run_id, execution_fingerprint, "
        "fingerprint_status, result_digest, fingerprint_basis, code_provenance, "
        "input_provenance) VALUES ('EXE-trzecie', 'RUN-historyczny', 'FPR-a', 'known', "
        "'RSET-3', '{}', '{}', '{}')"
    )
    assert polaczenie.execute("SELECT COUNT(*) FROM executions").fetchone()[0] == 3


def test_migracja_jest_idempotentna(stara_baza: Path) -> None:
    """Drugie otwarcie nie przebudowuje niczego — i nie rusza wierszy."""
    connect(stara_baza)
    polaczenie = connect(stara_baza)
    assert migrate_executions(polaczenie) is False
    assert polaczenie.execute("SELECT COUNT(*) FROM executions").fetchone()[0] == 2


def test_nowa_baza_nie_wymaga_migracji(tmp_path: Path) -> None:
    polaczenie = connect(tmp_path / "nowa.sqlite")
    assert migrate_executions(polaczenie) is False
    assert polaczenie.execute(
        "SELECT COUNT(*) FROM sqlite_master WHERE name = 'execution_attempts'"
    ).fetchone()[0] == 1
