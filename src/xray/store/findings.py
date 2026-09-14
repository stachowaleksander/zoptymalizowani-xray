# Implementuje ZOP-TECH-01 v0.1 pkt 5.4 — trwały zapis struktury FINDINGS —
# oraz invariant wykonań z wpisu DT-21.
"""Magazyn wyników.

To jedyne miejsce zapisu wyników. Nikt nie liczy niczego obok.

## Idempotentność i sprzeczność

| run_id | odcisk wykonania | treść wyników | zachowanie |
| --- | --- | --- | --- |
| ten sam | ten sam | ta sama | brak operacji |
| ten sam | ten sam | inna | ``ConflictingRun`` — **błąd**, nie nadpisanie |
| ten sam | inny | dowolna | nowe wykonanie; poprzednie zostaje |
| inny | dowolny | dowolna | nowy przebieg |

Rozstrzyga ograniczenie schematu (``xray.store.schema``), a nie porównanie w tym pliku.
``FindingStore`` tłumaczy jedynie naruszenie tego ograniczenia na wyjątek o znaczeniu
domenowym.

Przebieg, wykonanie i jego wyniki zapisujemy w jednej transakcji. Wynik zapisany częściowo
byłby śladem, który kłamie o tym, co policzono.
"""

import datetime as dt
import json
import sqlite3
from collections.abc import Sequence
from dataclasses import dataclass

from xray.model import FindingRecord
from xray.model.findings.identity import canonical_form
from xray.store.executions import ExecutionRef, FingerprintStatus, result_digest
from xray.store.runs import RunRef
from xray.store.schema import finding_columns


class ProjectionMismatch(RuntimeError):
    """Kolumna indeksu mówi co innego niż ``payload``.

    Osobny wyjątek, bo to inna awaria niż niezgodność tożsamości: tam zmieniono treść
    rekordu, tu rozjechał się indeks. Zapytanie po takiej kolumnie zwracałoby zły zbiór
    i nikt by się nie dowiedział.
    """


class ConflictingRun(RuntimeError):
    """Ten sam przebieg wykonany tym samym odciskiem dał inny wynik.

    Ten sam skrót wejścia, ten sam kod i to samo środowisko, inna treść — przepływ nie jest
    deterministyczny. Inny odcisk przy innej treści sprzecznością **nie jest**: to dwa
    legalne wykonania tego samego przebiegu.
    """


@dataclass(frozen=True, slots=True)
class StoredExecution:
    """Zapisane wykonanie przebiegu."""

    execution_id: str
    run_id: str
    result_digest: str
    execution: ExecutionRef


class FindingStore:
    """Zapis i odczyt wyników w SQLite."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._db = connection

    # --- zapis -----------------------------------------------------------------------

    def save_run(
        self,
        run: RunRef,
        findings: Sequence[FindingRecord],
        execution: ExecutionRef,
    ) -> bool:
        """Zapisuje wykonanie przebiegu wraz z wynikami. Zwraca, czy coś zapisano.

        ``False`` — to samo wykonanie z tą samą treścią już jest. ``ConflictingRun`` — ten
        sam przebieg i odcisk z inną treścią.
        """
        skrot_wyniku = result_digest(findings)
        execution_id = execution.execution_id(run.run_id, skrot_wyniku)
        try:
            with self._db:  # transakcja: wszystko albo nic
                self._db.execute(
                    "INSERT INTO runs (run_id, dataset_id, contract_version, "
                    "identity_algorithm_version, input_digest) VALUES (?, ?, ?, ?, ?) "
                    "ON CONFLICT(run_id) DO NOTHING",
                    (
                        run.run_id,
                        run.dataset_id,
                        run.contract_version,
                        run.identity_algorithm_version,
                        run.input_digest,
                    ),
                )
                kursor = self._db.execute(
                    "INSERT INTO executions (execution_id, run_id, execution_fingerprint, "
                    "fingerprint_status, result_digest, fingerprint_basis, code_provenance, "
                    "input_provenance, executed_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?) "
                    "ON CONFLICT(execution_id) DO NOTHING",
                    (
                        execution_id,
                        run.run_id,
                        execution.execution_fingerprint,
                        execution.fingerprint_status.value,
                        skrot_wyniku,
                        canonical_form(execution.fingerprint_basis),
                        canonical_form(execution.code_provenance),
                        run.provenance,
                        execution.executed_at.isoformat() if execution.executed_at else None,
                    ),
                )
                if kursor.rowcount == 0:
                    # To wykonanie — ten sam przebieg, odcisk i treść — już jest zapisane.
                    # Wyników nie wstawiamy drugi raz: należą do istniejącego wykonania.
                    return False
                for record in findings:
                    kolumny = finding_columns(record, run.run_id, execution_id)
                    self._db.execute(
                        "INSERT INTO findings ({}) VALUES ({})".format(
                            ", ".join(kolumny), ", ".join("?" * len(kolumny))
                        ),
                        tuple(kolumny.values()),
                    )
        except sqlite3.IntegrityError as blad:
            # Jedynym ograniczeniem UNIQUE poza kluczami głównymi jest
            # UNIQUE (run_id, execution_fingerprint). Pozostałe naruszenia (np. dwa wyniki
            # o tym samym finding_id w jednym wykonaniu) nie są sprzecznością przebiegu
            # i nie wolno ich tak nazwać.
            if blad.sqlite_errorname != "SQLITE_CONSTRAINT_UNIQUE":
                raise
            raise ConflictingRun(
                f"przebieg {run.run_id} ma już zapisane wykonanie z odciskiem "
                f"{execution.execution_fingerprint} i inną treścią wyników. Ten sam przebieg, "
                "ten sam kod i to samo środowisko dały inny wynik, więc przepływ nie jest "
                "deterministyczny — to błąd do naprawienia, nie stan do nadpisania"
            ) from blad
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
        oczekiwane = finding_columns(record, row["run_id"], row["execution_id"])
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

    def executions(self, run_id: str) -> tuple[StoredExecution, ...]:
        """Wszystkie wykonania jednego przebiegu, w kolejności zapisu."""
        wiersze = self._db.execute(
            "SELECT * FROM executions WHERE run_id = ? ORDER BY rowid", (run_id,)
        ).fetchall()
        return tuple(
            StoredExecution(
                execution_id=w["execution_id"],
                run_id=w["run_id"],
                result_digest=w["result_digest"],
                execution=ExecutionRef(
                    execution_fingerprint=w["execution_fingerprint"],
                    fingerprint_status=FingerprintStatus(w["fingerprint_status"]),
                    fingerprint_basis=json.loads(w["fingerprint_basis"]),
                    code_provenance=json.loads(w["code_provenance"]),
                    executed_at=(
                        dt.datetime.fromisoformat(w["executed_at"])
                        if w["executed_at"]
                        else None
                    ),
                ),
            )
            for w in wiersze
        )

    def load_execution(self, execution_id: str) -> tuple[FindingRecord, ...]:
        """Wyniki jednego wykonania, w kolejności zapisu."""
        wiersze = self._db.execute(
            "SELECT * FROM findings WHERE execution_id = ? ORDER BY rowid", (execution_id,)
        ).fetchall()
        return tuple(self._record_from_row(w) for w in wiersze)

    def load_run(self, run_id: str) -> tuple[FindingRecord, ...]:
        """Wyniki przebiegu, który ma **jedno** wykonanie.

        Przy kilku wykonaniach nie wybieramy żadnego — wybór byłby zgadywaniem. Wtedy
        trzeba wskazać wykonanie przez ``executions`` i ``load_execution``.
        """
        wykonania = self.executions(run_id)
        if len(wykonania) > 1:
            raise ValueError(
                f"przebieg {run_id} ma {len(wykonania)} wykonań "
                f"({', '.join(w.execution_id for w in wykonania)}); wskaż wykonanie przez "
                "load_execution — wybór jednego z nich byłby zgadywaniem"
            )
        return self.load_execution(wykonania[0].execution_id) if wykonania else ()

    def history(self, finding_id: str) -> tuple[tuple[str, str, FindingRecord], ...]:
        """Historia jednego wyniku przez wszystkie przebiegi i wykonania.

        Zwraca trójki ``(run_id, execution_id, rekord)``. Po ``finding_id`` widać, jak
        zmieniała się ta sama odpowiedź na to samo pytanie — na innych danych (inny
        ``run_id``) albo innym kodem i środowiskiem (inne wykonanie).
        """
        wiersze = self._db.execute(
            "SELECT * FROM findings WHERE finding_id = ? ORDER BY rowid", (finding_id,)
        ).fetchall()
        return tuple(
            (w["run_id"], w["execution_id"], self._record_from_row(w)) for w in wiersze
        )

    def runs(self) -> tuple[str, ...]:
        """Identyfikatory zapisanych przebiegów, w kolejności zapisu."""
        wiersze = self._db.execute("SELECT run_id FROM runs ORDER BY rowid").fetchall()
        return tuple(w["run_id"] for w in wiersze)
