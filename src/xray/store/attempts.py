# Implementuje ZOP-XR-V12-R1 kartę wykonawczą §9 (ExecutionAttemptRecord i bramka
# KNOWN/UNKNOWN) oraz ZOP-XR-FOUNDATION-BIND-01 v1.2 §7.4.2, przy rozstrzygnięciu
# Controllingu z 2026-09-23 w sprawie Q1 (semantic_run_id, wariant A).
"""Próba wykonania jako osobny, niezmienny byt.

## Po co to powstaje obok istniejących wykonań

Dzisiejszy magazyn scala dwie faktycznie wykonane próby w jeden wiersz: ten sam przebieg,
ten sam odcisk i ta sama treść dają ten sam ``execution_id``, więc druga próba znika
(`store/findings.py:117–120`). Karta §9 zakazuje tego wprost:
``IDENTICAL_ATTEMPT_MAY_NOT_BE_DROPPED_BY_STORAGE_DEDUPLICATION = true`` oraz
``EVERY_ACTUAL_EXECUTION_ATTEMPT_PERSISTED = true``.

Ten moduł buduje **strukturę** próby obok istniejącego mechanizmu. Przełączenie — zdjęcie
dedupu i ograniczenia ``UNIQUE (run_id, execution_fingerprint)`` — należy do pakietu P9,
gdy będzie już istniał rekord porównania. Wcześniej nie wolno, bo przez chwilę nie byłoby
ani starego zabezpieczenia, ani nowego.

## Dlaczego identyfikator próby jest losowy

``execution_attempt_id`` **nie może** pochodzić z treści. Karta §9:
``EXECUTION_FINGERPRINT_IS_NOT_EXECUTION_ATTEMPT_ID`` i
``RESULT_DIGEST_IS_NOT_EXECUTION_ATTEMPT_ID``. Gdyby był skrótem z przebiegu, odcisku
i wyniku, dwie identyczne próby dostałyby ten sam identyfikator i zlały się w jedną —
czyli dokładnie usterka, którą ta runda usuwa.

Wybór: UUID4. Jedno zdanie uzasadnienia: 122 losowe bity są unikalne bez żadnej
koordynacji — bez wspólnego licznika, bez zapytania do bazy i bez związku z treścią —
więc spełniają wymóg „bezpieczny przy concurrency" z §9 nawet wtedy, gdy dwie próby ruszają
równolegle w różnych procesach.

## semantic_run_id — wariant A z rozstrzygnięcia Q1

Controlling, 2026-09-23: „W R1 semantic_run_id wiąże istniejący exact run_id
w RUN_IDENTITY_VERSION='3' jako current semantic data-run reference. Rekord ma jawnie
zachować profil/version provenance. Nie wolno reinterpretować V3 jako
XR_SEMANTIC_RUN_PROFILE_01; R3 pozostaje poza zakresem. Canonical null jest niedozwolony."

Stąd **trzy** pola zamiast jednego: sama wartość (``semantic_run_id``) oraz jawna
deklaracja, co ją policzyło (``semantic_run_profile`` i ``semantic_run_identity_version``).
Bez tej deklaracji rekord niósłby „3" udające profil R3 — czyli właśnie cichą
reinterpretację, której rozstrzygnięcie zakazuje. Dlatego wartość
``XR_SEMANTIC_RUN_PROFILE_01`` jest tu jawnie odrzucana.

## Znaczniki czasu to proweniencja

v1.2 §7.4.2: „Timestampy są instance provenance i nie wchodzą do execution_fingerprint,
semantic_run_id ani result_identity". Rekord je niesie, ale nie liczy się z nich żaden
skrót — ani tutaj, ani nigdzie indziej.

## Jeden katalog stanu odcisku

``fingerprint_status`` bierzemy z istniejącego ``store/executions.py``, zamiast zakładać
drugi enum o tej samej nazwie. Karta §9 zapisuje te stany jako ``KNOWN | UNKNOWN``, a nasz
katalog niesie je jako ``"known"`` i ``"unknown"`` — to ta sama para stanów w zapisie, który
jest już związany ograniczeniem ``CHECK`` istniejącej tabeli. Dwa katalogi mogłyby się
rozjechać, a wtedy próba i wiersz wykonania mówiłyby o tym samym co innego.

## Czego rekord nie ma

Pola statusu równoważności. v1.2 §7.4.2: „Nie zawiera intrinsic scalar
execution_equivalence_status" — równoważność jest relacją pary, nie cechą próby, a jej
zapisanie na rekordzie byłoby przesłanką STOP R1-S13.
"""

import datetime as dt
from dataclasses import dataclass
from enum import StrEnum
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, model_validator

from xray.store.executions import FingerprintStatus
from xray.store.runs import RUN_IDENTITY_VERSION

ATTEMPT_ID_PREFIX = "ATTEMPT-"
"""Prefiks identyfikatora próby.

Świadomie **spoza** rejestru prefiksów profilu kanonicznego (``SCOPE-``, ``RESULT-``, …):
tamte oznaczają identyfikatory wyprowadzone z treści, a ten z treści nie pochodzi i nie
wolno go tak czytać.
"""

SEMANTIC_RUN_PROFILE = "CURRENT_RUN_IDENTITY_V3"
"""Deklaracja profilu, który policzył ``semantic_run_id``.

Nazwa wprost z v1.2 §17 i §18: ``CURRENT_RUN_IDENTITY_V3 =
HISTORICAL_CURRENT_IMPLEMENTATION_BASELINE``. To **nie jest**
``XR_SEMANTIC_RUN_PROFILE_01`` — tamten należy do rundy V12-R3.
"""

FORBIDDEN_RUN_PROFILE = "XR_SEMANTIC_RUN_PROFILE_01"
"""Profil rundy R3. Zapisanie go dziś byłoby reinterpretacją V3, zakazaną w Q1."""

DEFAULT_TERMINAL_STATUS = "COMPLETED"
"""Status terminalny zapisywany, gdy wołający go nie poda.

Kontrakt wymaga pola i **nie podaje katalogu** wartości (wpis B-13), więc to jest nasz
token, a nie słownik związany kartą. Nie wchodzi do żadnej tożsamości: identyfikator próby
jest losowy.
"""

FOUNDATION_BIND_VERSION = "ZOP-XR-FOUNDATION-BIND-01 v1.2"
"""Wersja kontraktu fundamentu, przy której próba powstała (karta §9).

Accepted SHA-256 tych bajtów: 508648d7054d28f45aa77ec3ca315a594d0de79589c867b2cbed48fad7d8fb43
(karta §1 i §22).
"""


class ExecutionRelationStatus(StrEnum):
    """Zamknięty zbiór trzech statusów relacji pary (karta §11.1).

    Czwartej wartości nie ma i nie wolno jej dopisać: dla pary o **różnych** znanych
    odciskach karta stanowi „Nie wymyślaj nowego statusu; neutralny status nie jest wymagany
    przez v1.2" — wtedy rekord porównania po prostu nie powstaje.
    """

    IDEMPOTENT_EQUIVALENT = "IDEMPOTENT_EQUIVALENT"
    NONDETERMINISM_CONFLICT = "NONDETERMINISM_CONFLICT"
    DETERMINISM_NOT_ASSESSABLE = "DETERMINISM_NOT_ASSESSABLE"


@dataclass(frozen=True, slots=True)
class GateDecision:
    """Wynik bramki: czy para w ogóle tworzy rekord porównania i z jakim skutkiem."""

    fingerprint_evidence_sufficient: bool
    """Czy **sam dowód z odcisków** wystarcza, żeby rozstrzygać determinizm tej pary.

    Bramka patrzy wyłącznie na odciski i ich status. Nie wie nic o porównywalności
    kontekstu — ani o ``result_identity``, ani o przebiegu, ani o efektywnych wyłączeniach —
    więc **nie wolno** czytać jej odpowiedzi jako „twórz rekord porównania". O tym, czy
    porównanie w ogóle ma sens, decyduje warstwa wyżej, na podstawie
    ``comparison_context_reference`` (karta §11).
    """

    relation_status: ExecutionRelationStatus | None
    """Status, jeżeli wynika z **samej** bramki.

    ``None`` znaczy „odciski niczego tu nie przesądzają" — a nie „status neutralny".
    """

    basis: str
    """Podstawa decyzji, zapisywalna w dowodzie."""


def compare_fingerprints(
    status_a: FingerprintStatus,
    fingerprint_a: str | None,
    status_b: FingerprintStatus,
    fingerprint_b: str | None,
) -> GateDecision:
    """Bramka KNOWN/UNKNOWN dla pary prób (karta §9 i §11.1).

    Czysta funkcja: nie potrzebuje rekordów, magazynu ani kolejności prób.

    Trzy wyjścia:

    1. oba ``KNOWN`` i odciski **równe** → dowód z odcisków wystarcza; o tym, czy będzie to
       ``IDEMPOTENT_EQUIVALENT``, czy ``NONDETERMINISM_CONFLICT``, decyduje dopiero
       ``result_payload_digest``,
    2. co najmniej jeden ``UNKNOWN`` → dowód **nie** wystarcza, a sama bramka wydaje
       ``DETERMINISM_NOT_ASSESSABLE``. „UNKNOWN jest brakiem evidence, nie wspólnym
       fingerprintem" (§9); ``None == None`` niczego nie dowodzi,
    3. oba ``KNOWN``, odciski **różne** → dowód nie wystarcza do oceny determinizmu, bo to
       nie jest to samo exact execution. Bramka nie nadaje tu żadnego statusu — czwartej
       wartości katalog nie ma (§11.1).

    Ostatni przypadek nie znaczy „nie twórz rekordu": bramka nie zna kontekstu porównania
    i takiej decyzji nie podejmuje.
    """
    _check_spojnosc(status_a, fingerprint_a, "A")
    _check_spojnosc(status_b, fingerprint_b, "B")

    if FingerprintStatus.UNKNOWN in (status_a, status_b):
        return GateDecision(
            fingerprint_evidence_sufficient=False,
            relation_status=ExecutionRelationStatus.DETERMINISM_NOT_ASSESSABLE,
            basis=(
                "co najmniej jedna próba ma fingerprint_status=UNKNOWN; brak evidence nie "
                "dowodzi tego samego wykonania (karta §9)"
            ),
        )
    if fingerprint_a == fingerprint_b:
        return GateDecision(
            fingerprint_evidence_sufficient=True,
            relation_status=None,
            basis=(
                "oba odciski znane i równe; klasyfikację rozstrzyga porównanie "
                "result_payload_digest (karta §11.1)"
            ),
        )
    return GateDecision(
        fingerprint_evidence_sufficient=False,
        relation_status=None,
        basis=(
            "oba odciski znane i różne — to nie jest to samo exact execution; karta §11.1: "
            "„Nie wymyślaj nowego statusu; neutralny status nie jest wymagany przez v1.2"
        ),
    )


def _check_spojnosc(status: FingerprintStatus, fingerprint: str | None, etykieta: str) -> None:
    """Karta §9: ``KNOWN => fingerprint != null``; ``UNKNOWN => fingerprint = null``."""
    if status is FingerprintStatus.KNOWN and fingerprint is None:
        raise ValueError(f"próba {etykieta}: status KNOWN wymaga niepustego odcisku (karta §9)")
    if status is FingerprintStatus.UNKNOWN and fingerprint is not None:
        raise ValueError(
            f"próba {etykieta}: status UNKNOWN wymaga canonical null jako odcisku (karta §9)"
        )


def attempt_required(*, computation_started: bool) -> bool:
    """Czy dla tego zdarzenia powstaje rekord próby (karta §9, zdanie końcowe).

    „Pre-execution cache hit, który zwraca istniejący wynik bez faktycznego uruchomienia
    obliczenia, **nie tworzy nowej próby**". Odwrotnie: jeżeli obliczenie faktycznie
    ruszyło, rekord jest obowiązkowy — niezależnie od tego, czy wynik okaże się identyczny
    z poprzednim.

    Reguła jest funkcją, a nie tylko zdaniem w dokumentacji, żeby dało się ją wskazać
    lokatorem i przetestować.
    """
    return computation_started


class ExecutionAttemptRecord(BaseModel):
    """Niezmienny ślad jednej faktycznie wykonanej próby (karta §9)."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    execution_attempt_id: str
    """Unikalny dla każdej faktycznie wykonanej próby. Nie pochodzi z treści."""

    semantic_run_id: str
    """Istniejący ``run_id``. Canonical null niedozwolony (Q1)."""

    semantic_run_profile: str = SEMANTIC_RUN_PROFILE
    semantic_run_identity_version: str = RUN_IDENTITY_VERSION
    """Jawna proweniencja profilu — druga połowa wariantu A z Q1."""

    execution_fingerprint: str | None = None
    fingerprint_status: FingerprintStatus

    execution_provenance_ref: str
    """Odesłanie do zapisanej proweniencji wykonania, a nie jej kopia."""

    attempt_started_at: dt.datetime | None = None
    attempt_completed_at: dt.datetime | None = None
    """Dowód czasu albo ``None``. Proweniencja — nie wchodzi do żadnego skrótu."""

    terminal_status: str
    """Status końcowy próby.

    Typ jest łańcuchem, a nie zamkniętym katalogiem, bo **żaden dokument obowiązujący go
    nie ustanawia**: karta §9 i v1.2 §7.4.2 wymagają pola „terminal status" i nie podają
    wartości. Wymyślenie katalogu byłoby regułą bez źródła — patrz wpis B-13.
    """

    result_record_ids: tuple[str, ...] = ()
    """Wiązania do ``CalculationResultRecord``. Puste, dopóki ten rekord nie istnieje."""

    comparison_evidence_refs: tuple[str, ...] = ()
    failure_evidence_refs: tuple[str, ...] = ()
    """Odesłania do właściwego dowodu porównania albo niepowodzenia (karta §9)."""

    foundation_bind_version: str = FOUNDATION_BIND_VERSION

    @model_validator(mode="after")
    def _check_fingerprint(self) -> "ExecutionAttemptRecord":
        _check_spojnosc(self.fingerprint_status, self.execution_fingerprint, "tej próby")
        return self

    @model_validator(mode="after")
    def _check_run_reference(self) -> "ExecutionAttemptRecord":
        """Q1: wartość przebiegu jest obowiązkowa, a profil nie może udawać R3."""
        if not self.semantic_run_id.strip():
            raise ValueError(
                "semantic_run_id jest obowiązkowy; canonical null jest niedozwolony "
                "(rozstrzygnięcie Q1 z 2026-09-23)"
            )
        if self.semantic_run_profile == FORBIDDEN_RUN_PROFILE:
            raise ValueError(
                f"{FORBIDDEN_RUN_PROFILE} należy do rundy V12-R3; zapisanie go dla wartości "
                f"z wersji {RUN_IDENTITY_VERSION!r} byłoby reinterpretacją V3, zakazaną w Q1"
            )
        if not self.terminal_status.strip():
            raise ValueError("terminal_status nie może być pusty (karta §9)")
        if not self.execution_provenance_ref.strip():
            raise ValueError("execution_provenance_ref nie może być pusty (karta §9)")
        return self

    @classmethod
    def create(cls, **pola: object) -> "ExecutionAttemptRecord":
        """Tworzy rekord z nowym, losowym identyfikatorem próby.

        Wołane **tylko** wtedy, gdy obliczenie faktycznie ruszyło — patrz
        ``attempt_required``. Trafienie w cache przed wykonaniem rekordu nie tworzy.
        """
        return cls(execution_attempt_id=ATTEMPT_ID_PREFIX + uuid4().hex, **pola)
