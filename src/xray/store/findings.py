# Implementuje ZOP-TECH-01 v0.1 pkt 5.4 — trwały zapis struktury FINDINGS.
"""Magazyn wyników.

To jedyne miejsce zapisu wyników. Nikt nie liczy niczego obok.

## Idempotentność i sprzeczność

| Sytuacja | Zachowanie |
| --- | --- |
| ten sam ``run_id``, identyczna treść | brak operacji |
| ten sam ``run_id``, inna treść | **błąd**, nie nadpisanie |
| inny ``run_id`` | nowy zapis; poprzedni zostaje |

Drugi przypadek jest istotny: ten sam ``run_id`` znaczy ten sam skrót treści wejścia.
Inny wynik przy tym samym wejściu znaczyłby, że coś w przepływie **nie jest
deterministyczne** — a to błąd do naprawienia, nie stan do nadpisania.

Wiersz ``runs`` i jego wiersze ``findings`` zapisujemy w jednej transakcji. Wynik
zapisany częściowo byłby śladem, który kłamie o tym, co policzono.
"""

import sqlite3
from collections.abc import Sequence

from xray.model import FindingRecord
from xray.store.runs import RunRef
from xray.store.schema import finding_columns


class ProjectionMismatch(RuntimeError):
    """Kolumna indeksu mówi co innego niż ``payload``.

    Osobny wyjątek, bo to inna awaria niż niezgodność tożsamości: tam zmieniono treść
    rekordu, tu rozjechał się indeks. Zapytanie po takiej kolumnie zwracałoby zły zbiór
    i nikt by się nie dowiedział.
    """


class ConflictingRun(RuntimeError):
    """Ten sam ``run_id`` niesie inną treść wyników.

    Znaczy to, że ten sam skrót wejścia dał inny wynik — czyli że coś w przepływie nie
    jest deterministyczne.
    """


class FindingStore:
    """Zapis i odczyt wyników w SQLite."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._db = connection

    # --- zapis -----------------------------------------------------------------------

    def save_run(self, run: RunRef, findings: Sequence[FindingRecord]) -> bool:
        """Zapisuje przebieg wraz z jego wynikami. Zwraca, czy coś faktycznie zapisano.

        Powtórzenie tego samego przebiegu z identyczną treścią jest brakiem operacji.
        Powtórzenie z inną treścią podnosi ``ConflictingRun``.
        """
        istniejacy = self._db.execute(
            "SELECT run_id FROM runs WHERE run_id = ?", (run.run_id,)
        ).fetchone()

        if istniejacy is not None:
            zapisane = {f.finding_id: f for f in self.load_run(run.run_id)}
            nowe = {f.finding_id: f for f in findings}
            if zapisane == nowe:
                return False
            raise ConflictingRun(
                f"przebieg {run.run_id} jest już zapisany z inną treścią wyników. "
                "Ten sam skrót wejścia dał inny wynik, więc przepływ nie jest "
                "deterministyczny — to błąd do naprawienia, nie stan do nadpisania"
            )

        with self._db:  # transakcja: wszystko albo nic
            self._db.execute(
                "INSERT INTO runs (run_id, dataset_id, contract_version, "
                "identity_algorithm_version, input_digest, provenance, executed_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    run.run_id,
                    run.dataset_id,
                    run.contract_version,
                    run.identity_algorithm_version,
                    run.input_digest,
                    run.provenance,
                    run.executed_at.isoformat() if run.executed_at else None,
                ),
            )
            for record in findings:
                kolumny = finding_columns(record, run.run_id)
                self._db.execute(
                    "INSERT INTO findings ({}) VALUES ({})".format(
                        ", ".join(kolumny), ", ".join("?" * len(kolumny))
                    ),
                    tuple(kolumny.values()),
                )
        return True

    # --- odczyt ----------------------------------------------------------------------

    def _record_from_row(self, row: sqlite3.Row) -> FindingRecord:
        """Odtwarza rekord z ``payload`` i sprawdza, czy indeks się z nim zgadza.

        Odtworzenie idzie przez ``model_validate_json``, więc rekord przechodzi przez
        ``_check_identity``: sam potwierdza, że jego identyfikator prowadzi do jego
        własnych składników. Tu właśnie sprawdzenie tożsamości przy odczycie zaczyna coś
        robić — łapie ręczną poprawkę w bazie, błąd warstwy magazynu i uszkodzenie pliku.
        """
        record = FindingRecord.model_validate_json(row["payload"])
        oczekiwane = finding_columns(record, row["run_id"])
        rozne = [
            nazwa
            for nazwa, wartosc in oczekiwane.items()
            if nazwa != "payload" and row[nazwa] != wartosc
        ]
        if rozne:
            raise ProjectionMismatch(
                f"kolumny {', '.join(rozne)} wiersza {row['finding_id']} nie zgadzają "
                "się z treścią payload; indeks kłamie"
            )
        return record

    def load_run(self, run_id: str) -> tuple[FindingRecord, ...]:
        """Zwraca wyniki jednego przebiegu, w kolejności zapisu."""
        wiersze = self._db.execute(
            "SELECT * FROM findings WHERE run_id = ? ORDER BY rowid", (run_id,)
        ).fetchall()
        return tuple(self._record_from_row(w) for w in wiersze)

    def history(self, finding_id: str) -> tuple[tuple[str, FindingRecord], ...]:
        """Historia jednego wyniku przez kolejne przebiegi.

        Zwraca pary ``(run_id, rekord)``. To jest właściwość, dla której klucz jest parą:
        po ``finding_id`` widać, jak zmieniała się ta sama odpowiedź na to samo pytanie.
        """
        wiersze = self._db.execute(
            "SELECT * FROM findings WHERE finding_id = ? ORDER BY rowid", (finding_id,)
        ).fetchall()
        return tuple((w["run_id"], self._record_from_row(w)) for w in wiersze)

    def runs(self) -> tuple[str, ...]:
        """Identyfikatory zapisanych przebiegów, w kolejności zapisu."""
        wiersze = self._db.execute("SELECT run_id FROM runs ORDER BY rowid").fetchall()
        return tuple(w["run_id"] for w in wiersze)
