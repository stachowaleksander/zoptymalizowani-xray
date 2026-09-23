# Implementuje ZOP-TECH-01 v0.1 pkt 5.4 — trwały zapis struktury FINDINGS —
# oraz invariant wykonań z wpisu DT-21.
"""Magazyn wyników.

To jedyne miejsce zapisu wyników. Nikt nie liczy niczego obok.

## Idempotentność i sprzeczność

| run_id | odcisk wykonania | treść wyników | zachowanie |
| --- | --- | --- | --- |
| ten sam | ten sam | ta sama | **nowa próba**; opis wykonania i wyniki już są |
| ten sam | ten sam | inna | **nowa próba i nowy opis**; relację klasyfikuje porównanie |
| ten sam | inny | dowolna | nowa próba i nowe wykonanie; poprzednie zostaje |
| inny | dowolny | dowolna | nowy przebieg |

Drugi wiersz to zmiana z rundy V12-R1. Wcześniej ta sytuacja kończyła się wyjątkiem
``ConflictingRun`` i **utratą drugiego wyniku**; teraz zostają oba, a to, czy jest to
niedeterminizm, rozstrzyga ``classify`` z ``store/comparisons.py`` — po zapisaniu dowodu,
nie zamiast niego (karta §9 i §11).

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
from xray.store.attempts import DEFAULT_TERMINAL_STATUS, ExecutionAttemptRecord
from xray.store.executions import ExecutionRef, FingerprintStatus, result_digest
from xray.store.runs import RunRef
from xray.store.schema import finding_columns


class ProjectionMismatch(RuntimeError):
    """Kolumna indeksu mówi co innego niż ``payload``.

    Osobny wyjątek, bo to inna awaria niż niezgodność tożsamości: tam zmieniono treść
    rekordu, tu rozjechał się indeks. Zapytanie po takiej kolumnie zwracałoby zły zbiór
    i nikt by się nie dowiedział.
    """


@dataclass(frozen=True, slots=True)
class StoredExecution:
    """Zapisane wykonanie przebiegu."""

    execution_id: str
    run_id: str
    result_digest: str
    execution: ExecutionRef


@dataclass(frozen=True, slots=True)
class SaveOutcome:
    """Co dokładnie zrobił zapis — zamiast dawnego ``bool``.

    Dawne ``False`` znaczyło „pominięto", i to było jedyne, czego wołający się dowiadywał.
    Teraz każdy zapis **coś** zostawia (zawsze próbę) i mówi wprost, co jeszcze doszło.
    """

    execution_attempt_id: str
    """Zawsze nowy: każda faktycznie wykonana próba ma własny ślad (karta §9)."""

    execution_id: str
    execution_described_now: bool
    """Czy opis wykonania powstał teraz, czy był już zapisany z poprzedniej próby.

    ``False`` **nie znaczy** „pominięto zapis": ``execution_id`` powstaje z treści, więc ten
    sam identyfikator to dosłownie ten sam opis. Zdarzenie zapisała próba.
    """

    findings_written: int


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
        *,
        attempt: ExecutionAttemptRecord | None = None,
    ) -> SaveOutcome:
        """Zapisuje **faktycznie wykonaną próbę** wraz z wykonaniem i wynikami.

        Do rundy V12-R1 ta metoda potrafiła nie zapisać: ``ON CONFLICT DO NOTHING`` i zwrotka
        ``False`` oznaczały „to już jest, pomijam", a ``UNIQUE (run_id, execution_fingerprint)``
        zamieniał drugi, inny wynik tego samego odcisku w wyjątek. Karta §9 zabrania obu
        rzeczy: ``EVERY_ACTUAL_EXECUTION_ATTEMPT_PERSISTED`` i
        ``IDENTICAL_ATTEMPT_MAY_NOT_BE_DROPPED_BY_STORAGE_DEDUPLICATION``.

        Teraz każde wywołanie dokłada wiersz do ``execution_attempts`` — zawsze, także gdy
        opis wykonania i wyniki są co do bajtu te same. Sprzeczność nie jest już odmową
        zapisu, tylko materiałem do klasyfikacji: dwie próby, dwa opisy, a relację między
        nimi rozstrzyga ``classify`` z ``store/comparisons.py``.

        Wołający, który **nie** uruchomił obliczenia (trafienie w cache przed wykonaniem),
        nie ma prawa tu wejść — patrz ``attempt_required`` w ``store/attempts.py``.
        """
        skrot_wyniku = result_digest(findings)
        execution_id = execution.execution_id(run.run_id, skrot_wyniku)
        proba = attempt or ExecutionAttemptRecord.create(
            semantic_run_id=run.run_id,
            execution_fingerprint=execution.execution_fingerprint,
            fingerprint_status=execution.fingerprint_status,
            execution_provenance_ref=execution_id,
            attempt_completed_at=execution.executed_at,
            terminal_status=DEFAULT_TERMINAL_STATUS,
        )

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
            opisane_teraz = self._describe_execution(
                run, execution, execution_id, skrot_wyniku
            )
            zapisane_wyniki = 0
            if opisane_teraz:
                for record in findings:
                    kolumny = finding_columns(record, run.run_id, execution_id)
                    self._db.execute(
                        "INSERT INTO findings ({}) VALUES ({})".format(
                            ", ".join(kolumny), ", ".join("?" * len(kolumny))
                        ),
                        tuple(kolumny.values()),
                    )
                    zapisane_wyniki += 1
            # ASSUMPTION: B-16 — próba zapisuje się w tej samej transakcji co wyniki,
            # więc błąd ich zapisu cofa także ślad faktycznie wykonanej próby. Karta §9
            # (EVERY_ACTUAL_EXECUTION_ATTEMPT_PERSISTED) mówi co innego niż zasada
            # atomowości z nagłówka tego modułu; rozbieżność jest zadeklarowana, nie
            # rozstrzygnięta.
            self._save_attempt(proba, execution_id)

        return SaveOutcome(
            execution_attempt_id=proba.execution_attempt_id,
            execution_id=execution_id,
            execution_described_now=opisane_teraz,
            findings_written=zapisane_wyniki,
        )

    def _describe_execution(
        self,
        run: RunRef,
        execution: ExecutionRef,
        execution_id: str,
        skrot_wyniku: str,
    ) -> bool:
        """Dokłada opis wykonania, jeżeli tego opisu jeszcze nie ma.

        To nie jest deduplikacja zdarzeń: ``execution_id`` powstaje z ``run_id``, odcisku
        i skrótu treści, więc istniejący wiersz o tym identyfikatorze niesie **dokładnie
        tę samą** treść. Zdarzenie — czyli fakt, że obliczenie ruszyło jeszcze raz —
        zapisuje próba, i ona powstaje zawsze.
        """
        istnieje = self._db.execute(
            "SELECT 1 FROM executions WHERE execution_id = ?", (execution_id,)
        ).fetchone()
        if istnieje is not None:
            return False
        self._db.execute(
            "INSERT INTO executions (execution_id, run_id, execution_fingerprint, "
            "fingerprint_status, result_digest, fingerprint_basis, code_provenance, "
            "input_provenance, executed_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
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
        return True

    def _save_attempt(self, attempt: ExecutionAttemptRecord, execution_id: str) -> None:
        """Zapisuje próbę. Bez ``ON CONFLICT``: identyfikator jest losowy, więc kolizja
        oznaczałaby błąd generatora, a nie powtórzenie — i ma wybuchnąć."""
        self._db.execute(
            "INSERT INTO execution_attempts (execution_attempt_id, semantic_run_id, "
            "semantic_run_profile, semantic_run_identity_version, execution_id, "
            "execution_fingerprint, fingerprint_status, execution_provenance_ref, "
            "attempt_started_at, attempt_completed_at, terminal_status, "
            "foundation_bind_version, payload) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                attempt.execution_attempt_id,
                attempt.semantic_run_id,
                attempt.semantic_run_profile,
                attempt.semantic_run_identity_version,
                execution_id,
                attempt.execution_fingerprint,
                attempt.fingerprint_status.value,
                attempt.execution_provenance_ref,
                attempt.attempt_started_at.isoformat() if attempt.attempt_started_at else None,
                (
                    attempt.attempt_completed_at.isoformat()
                    if attempt.attempt_completed_at
                    else None
                ),
                attempt.terminal_status,
                attempt.foundation_bind_version,
                attempt.model_dump_json(),
            ),
        )

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

    def attempts(self, run_id: str) -> tuple[ExecutionAttemptRecord, ...]:
        """Wszystkie faktycznie wykonane próby tego przebiegu, w kolejności zapisu.

        Dwie identyczne próby to dwa wpisy — na tym polega różnica wobec stanu sprzed
        rundy V12-R1.
        """
        wiersze = self._db.execute(
            "SELECT payload FROM execution_attempts WHERE semantic_run_id = ? ORDER BY rowid",
            (run_id,),
        ).fetchall()
        return tuple(ExecutionAttemptRecord.model_validate_json(w["payload"]) for w in wiersze)

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
