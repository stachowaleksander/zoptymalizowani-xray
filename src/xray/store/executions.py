# Implementuje rozdzielenie semantycznej tożsamości przebiegu od proweniencji wykonania
# (decyzja Michała, pakiet z 2026-09-14; wpisy DT-21 i DT-22) oraz zasadę 3 z CLAUDE.md.
"""Wykonanie przebiegu: odcisk kodu i środowiska — bez czasu.

## Dwie tożsamości, nie jedna

``run_id`` odpowiada na pytanie **„na jakich danych"** (``xray.store.runs``). Odcisk
wykonania odpowiada na pytanie **„jakim kodem i w jakim środowisku"**. Commit, drzewo gita,
wydanie i lock zależności to proweniencja wykonania — do ``run_id`` nie wchodzą.

Wykonanie jest **opisem**: ``execution_id`` powstaje z przebiegu, odcisku i skrótu treści,
więc ten sam identyfikator znaczy dosłownie ten sam opis.

| run_id | odcisk | wynik | skutek |
| --- | --- | --- | --- |
| ten sam | ten sam | ten sam | ten sam opis; próbę i tak zapisujemy osobno |
| ten sam | ten sam | inny | dwa opisy obok siebie; relację klasyfikuje porównanie par |
| ten sam | inny | dowolny | dwa legalne, niezmienne wykonania tego samego przebiegu |

Drugi wiersz był do rundy V12-R1 błędem odmawianym przez ``UNIQUE (run_id,
execution_fingerprint)``. Karta §9 każe najpierw zachować dowód, więc ograniczenie zniknęło,
a ocena przeniosła się do ``ExecutionComparisonRecord``.

## Pułapka, której ten moduł pilnuje konstrukcją

Do odcisku **nie wchodzi żaden znacznik czasu**. Gdyby wszedł, każde wykonanie miałoby inny
odcisk, wiersz „ten sam odcisk" nigdy by się nie ziścił, a kontrola determinizmu cicho
przestałaby działać — przy zielonych testach. Dlatego ``compute_fingerprint`` nie przyjmuje
żadnego argumentu, a ``executed_at`` jest polem audytowym poza odciskiem i poza
identyfikatorem wykonania.

## Co wchodzi do odcisku — i nic ponadto (wpis DT-22)

- skrót dokładnych bajtów plików ``*.py`` pakietu ``xray``, po ścieżkach **względnych**
  wobec katalogu pakietu, bez ``__pycache__`` i ``*.pyc``,
- platforma: implementacja i wersja Pythona, system, architektura,
- wersje dystrybucji z **domknięcia zależności runtime** pakietu.

Narzędzia deweloperskie i lock zależności trafiają do ``fingerprint_basis`` jako opis. Im
więcej wchodzi do odcisku, tym słabsza kontrola sprzeczności: ``pip install ruff`` zmieniłby
odcisk i dwa różne wyniki z tych samych danych stałyby się dwoma legalnymi wykonaniami
zamiast sprzecznością.

## Gdy odcisku nie da się ustalić

Odcisku nie zmyślamy. Jeżeli plików kodu nie da się przeczytać albo nie wiadomo, jakie są
zależności runtime, ``execution_fingerprint = None``, ``fingerprint_status = unknown``,
a ``fingerprint_basis`` mówi dlaczego. Kontrola determinizmu jest wtedy wyłączona — i rekord
to mówi wprost.

Git jest **opisem**, nie składnikiem odcisku. Przy brudnym drzewie roboczym zapisujemy commit
bazowy razem z tym faktem, bez udawania, że commit opisuje wykonany kod.
"""

import datetime as dt
import hashlib
import importlib.metadata as md
import platform
import subprocess
import sys
import tomllib
from collections.abc import Iterable, Sequence
from enum import StrEnum
from pathlib import Path
from typing import Any, Self

from packaging.requirements import InvalidRequirement, Requirement
from packaging.utils import canonicalize_name
from pydantic import BaseModel, ConfigDict, model_validator

import xray
from xray.model import FindingRecord
from xray.model.findings.identity import canonical_form, compute_id

DISTRIBUTION_NAME = "zoptymalizowani-xray"
"""Nazwa dystrybucji z ``pyproject.toml``. Od jej zależności zaczyna się domknięcie."""

LOCK_FILE_NAME = "pylock.toml"
"""Plik locka zależności w katalogu projektu. Opis tego, co zadeklarowano — nie odcisk."""

EXECUTION_IDENTITY_VERSION = "1"
"""Wersja kształtu krotek: odcisku, wykonania i zestawu wyników. Własna linia (DT-14)."""

_FINGERPRINT_PREFIX = "FPR"
_EXECUTION_PREFIX = "EXE"
_RESULT_SET_PREFIX = "RSET"

_GIT_CODE_PATHS = ("src", "pyproject.toml", LOCK_FILE_NAME)
"""Ścieżki, których stan w gicie opisujemy. Zmiana w ``docs/`` nie czyni kodu brudnym."""

_LIMITATIONS = (
    "Odcisk opisuje bajty plików kodu na dysku w chwili liczenia, a nie w chwili importu "
    "modułów: edycja pliku w trakcie działania procesu nie zostanie zauważona.",
    "Końce linii nie są normalizowane w kodzie tożsamości. LF w drzewie roboczym wymusza "
    ".gitattributes (*.py text eol=lf); plik zapisany z CRLF poza gitem da inny odcisk, "
    "bo to inne bajty.",
)


class FingerprintStatus(StrEnum):
    """Czy odcisk wykonania jest znany."""

    KNOWN = "known"
    """Odcisk policzony z bajtów kodu, platformy i zależności runtime."""

    UNKNOWN = "unknown"
    """Odcisku nie dało się ustalić. Kontrola determinizmu dla wykonania jest wyłączona."""


def package_dir() -> Path:
    """Katalog faktycznie importowanego pakietu ``xray``."""
    return Path(xray.__file__).resolve().parent


def code_files(directory: Path) -> dict[str, Path] | None:
    """Pliki kodu wchodzące do odcisku: ``*.py`` pakietu, bez ``__pycache__``.

    **Jedyne miejsce, które wyznacza tę listę.** Korzysta z niego ``code_manifest``
    i strażnik końców linii w testach — druga, równoległa lista mogłaby się rozjechać
    z tym, co faktycznie wchodzi do odcisku.

    Klucz to ścieżka **względna** wobec katalogu pakietu, zapisana z ukośnikami: ścieżka
    bezwzględna zmieniałaby odcisk po sklonowaniu repozytorium w inne miejsce.

    ``None``: katalogu nie ma albo nie zawiera żadnego pliku ``*.py``.
    """
    if not directory.is_dir():
        return None
    pliki = {
        sciezka.relative_to(directory).as_posix(): sciezka
        for sciezka in directory.rglob("*.py")
        if "__pycache__" not in sciezka.relative_to(directory).parts
    }
    return pliki or None


def code_manifest(directory: Path) -> tuple[tuple[str, str], ...] | None:
    """Pary ``(ścieżka względna, SHA-256 bajtów)`` dla plików z ``code_files``.

    Porządek po tekście ścieżki, a nie po ``Path`` — porównanie ścieżek na Windows ignoruje
    wielkość liter, więc kolejność zależałaby od systemu.

    ``None`` znaczy „nie da się ustalić" — nigdy pusty skrót udający znany kod.
    """
    try:
        pliki = code_files(directory)
        if pliki is None:
            return None
        return tuple(
            (wzgledna, hashlib.sha256(pliki[wzgledna].read_bytes()).hexdigest())
            for wzgledna in sorted(pliki)
        )
    except OSError:
        return None


def project_root(directory: Path) -> Path | None:
    """Katalog projektu z ``pyproject.toml`` tej dystrybucji, jeżeli pakiet w nim leży.

    Istnieje przy pracy z repozytorium (instalacja edytowalna, ``pythonpath`` w pytest).
    W pakiecie zainstalowanym z koła go nie ma — i to jest poprawny wynik, a nie błąd.
    """
    for katalog in directory.parents:
        plik = katalog / "pyproject.toml"
        if not plik.is_file():
            continue
        try:
            dane = tomllib.loads(plik.read_text(encoding="utf-8"))
        except (OSError, tomllib.TOMLDecodeError):
            return None
        return katalog if dane.get("project", {}).get("name") == DISTRIBUTION_NAME else None
    return None


def _root_requirements(root: Path | None) -> tuple[tuple[str, ...] | None, str]:
    """Deklarowane zależności runtime pakietu i to, skąd je wzięto.

    Przy pracy z repozytorium źródłem jest ``pyproject.toml``: metadane instalacji
    edytowalnej powstają raz, przy ``pip install -e .``, i nie odświeżają się, gdy zmieni
    się lista zależności.
    """
    if root is not None:
        try:
            dane = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
        except (OSError, tomllib.TOMLDecodeError) as blad:
            return None, f"pyproject.toml nieczytelny: {type(blad).__name__}"
        return tuple(dane.get("project", {}).get("dependencies", ())), "pyproject.toml"
    try:
        wymagania = md.distribution(DISTRIBUTION_NAME).requires or ()
    except md.PackageNotFoundError:
        return None, (
            f"brak pyproject.toml projektu i brak metadanych dystrybucji {DISTRIBUTION_NAME}: "
            "zależności runtime nieznane"
        )
    return tuple(wymagania), "metadane dystrybucji"


def _installed() -> dict[str, md.Distribution]:
    """Zainstalowane dystrybucje po znormalizowanej nazwie; pierwsza na ścieżce wygrywa."""
    wynik: dict[str, md.Distribution] = {}
    for dystrybucja in md.distributions():
        nazwa = dystrybucja.metadata["Name"]
        if nazwa:
            wynik.setdefault(canonicalize_name(nazwa), dystrybucja)
    return wynik


def runtime_distributions(
    requirements: Iterable[str],
) -> tuple[tuple[tuple[str, str], ...], tuple[str, ...]]:
    """Domknięcie zależności runtime: ``(nazwa, wersja)`` zainstalowanych i brakujące.

    Idzie po wymaganiach kolejnych dystrybucji, obliczając markery dla bieżącego
    środowiska. Zależności dodatków (``extra == "test"``) są pomijane, chyba że samo
    wymaganie prosi o dodatek.
    """
    zainstalowane = _installed()
    wersje: dict[str, str] = {}
    brakujace: set[str] = set()
    odwiedzone: set[tuple[str, frozenset[str]]] = set()
    kolejka: list[tuple[str, frozenset[str]]] = [(r, frozenset()) for r in requirements]
    while kolejka:
        tekst, dodatki = kolejka.pop()
        try:
            wymaganie = Requirement(tekst)
        except InvalidRequirement:
            brakujace.add(f"nieczytelne wymaganie: {tekst}")
            continue
        if wymaganie.marker is not None and not any(
            wymaganie.marker.evaluate({"extra": dodatek}) for dodatek in dodatki | {""}
        ):
            continue
        nazwa = canonicalize_name(wymaganie.name)
        klucz = (nazwa, frozenset(wymaganie.extras))
        if klucz in odwiedzone:
            continue
        odwiedzone.add(klucz)
        dystrybucja = zainstalowane.get(nazwa)
        if dystrybucja is None:
            brakujace.add(nazwa)
            continue
        wersje[nazwa] = dystrybucja.version
        kolejka.extend(
            (r, frozenset(wymaganie.extras)) for r in dystrybucja.requires or ()
        )
    return tuple(sorted(wersje.items())), tuple(sorted(brakujace))


def platform_description() -> dict[str, str]:
    """Platforma wykonania. Należy do odcisku (decyzja D7): ten sam kod na dwóch systemach
    może dać inne wyniki zmiennoprzecinkowe, a to nie jest sprzeczność."""
    return {
        "python_implementation": sys.implementation.name,
        "python_version": platform.python_version(),
        "system": sys.platform,
        "machine": platform.machine(),
    }


def git_description(root: Path | None) -> dict[str, Any]:
    """Commit i stan drzewa roboczego — **opis** kodu, nie składnik odcisku.

    ``unavailable`` z przyczyną, gdy nie ma katalogu projektu, gita albo repozytorium.
    ``dirty``, gdy sprawdzane ścieżki różnią się od HEAD: commit jest wtedy bazą, a nie
    opisem wykonanego kodu, i rekord mówi to wprost.
    """
    if root is None:
        return {
            "git_status": "unavailable",
            "reason": "pakiet nie leży w katalogu projektu z pyproject.toml tej dystrybucji",
        }

    def git(*argumenty: str) -> str:
        return subprocess.run(
            ["git", "-C", str(root), *argumenty],
            capture_output=True,
            text=True,
            timeout=10,
            check=True,
        ).stdout.strip()

    try:
        commit = git("rev-parse", "HEAD")
        drzewo = git("rev-parse", "HEAD^{tree}")
        zmiany = git("status", "--porcelain", "--", *_GIT_CODE_PATHS)
    except (OSError, subprocess.SubprocessError) as blad:
        return {"git_status": "unavailable", "reason": f"git: {type(blad).__name__}"}
    brudne = bool(zmiany)
    return {
        "git_status": "dirty" if brudne else "clean",
        "head_commit": commit,
        "head_tree": drzewo,
        "checked_paths": list(_GIT_CODE_PATHS),
        "note": (
            "sprawdzane ścieżki różnią się od HEAD: commit jest bazą, nie opisem kodu"
            if brudne
            else "sprawdzane ścieżki zgodne z HEAD"
        ),
    }


def declared_lock(root: Path | None) -> dict[str, str]:
    """Skrót pliku locka — to, co **zadeklarowano**. To, co działa, opisuje odcisk."""
    if root is None:
        return {"status": "unavailable", "file": LOCK_FILE_NAME}
    try:
        bajty = (root / LOCK_FILE_NAME).read_bytes()
    except FileNotFoundError:
        return {"status": "not_found", "file": LOCK_FILE_NAME}
    except OSError as blad:
        return {"status": "unreadable", "file": LOCK_FILE_NAME, "reason": type(blad).__name__}
    return {
        "status": "found",
        "file": LOCK_FILE_NAME,
        "sha256": hashlib.sha256(bajty).hexdigest(),
    }


def compute_fingerprint() -> tuple[str | None, dict[str, Any]]:
    """Odcisk wykonania i jego podstawa.

    **Bez żadnego argumentu** — w szczególności bez czasu. Patrz nagłówek modułu.
    """
    katalog = package_dir()
    root = project_root(katalog)
    manifest = code_manifest(katalog)
    wymagania, zrodlo_wymagan = _root_requirements(root)
    runtime, brakujace = runtime_distributions(wymagania or ())
    poza_odciskiem = {nazwa for nazwa, _ in runtime} | {canonicalize_name(DISTRIBUTION_NAME)}
    pozostale = sorted(
        (nazwa, dystrybucja.version)
        for nazwa, dystrybucja in _installed().items()
        if nazwa not in poza_odciskiem
    )

    podstawa: dict[str, Any] = {
        "scope": (
            "odcisk = bajty *.py pakietu xray (ścieżki względne) + platforma + wersje "
            "dystrybucji z domknięcia zależności runtime; nic ponadto (DT-22)"
        ),
        "code_files": [list(para) for para in manifest] if manifest else None,
        "platform": platform_description(),
        "runtime_requirements_source": zrodlo_wymagan,
        "runtime_distributions": [list(para) for para in runtime],
        "missing_runtime_distributions": list(brakujace),
        "other_distributions": [list(para) for para in pozostale],
        "declared_lock": declared_lock(root),
        "limitations": list(_LIMITATIONS),
    }

    przyczyny = []
    if manifest is None:
        przyczyny.append(f"nie da się przeczytać plików *.py pakietu w {katalog}")
    if wymagania is None:
        przyczyny.append(zrodlo_wymagan)
    if przyczyny:
        podstawa["unknown_reason"] = przyczyny
        return None, podstawa

    podstawa["code_digest"] = hashlib.sha256(
        canonical_form({"files": manifest}).encode("utf-8")
    ).hexdigest()
    skladniki = {
        "code_digest": podstawa["code_digest"],
        "platform": podstawa["platform"],
        "runtime_distributions": podstawa["runtime_distributions"],
        "missing_runtime_distributions": podstawa["missing_runtime_distributions"],
        "identity_algorithm_version": EXECUTION_IDENTITY_VERSION,
    }
    odcisk = compute_id(
        _FINGERPRINT_PREFIX, skladniki, algorithm_version=EXECUTION_IDENTITY_VERSION
    )
    return odcisk, podstawa


def result_digest(findings: Sequence[FindingRecord]) -> str:
    """Skrót pełnej treści wyników jednego wykonania, niezależny od kolejności ich zwrócenia.

    Wyniki są porządkowane po pełnej postaci kanonicznej, więc dwa wyniki o tym samym
    kluczu są identyczne i ich kolejność niczego nie zmienia.
    """
    return compute_id(
        _RESULT_SET_PREFIX,
        {
            "findings": sorted(canonical_form(f.model_dump(mode="json")) for f in findings),
            "identity_algorithm_version": EXECUTION_IDENTITY_VERSION,
        },
        algorithm_version=EXECUTION_IDENTITY_VERSION,
    )


class ExecutionRef(BaseModel):
    """Jedno wykonanie przebiegu: odcisk, jego podstawa i opis kodu."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    execution_fingerprint: str | None
    """Odcisk kodu i środowiska albo ``None``, gdy nie da się go ustalić."""

    fingerprint_status: FingerprintStatus

    fingerprint_basis: dict[str, Any]
    """Z czego policzono odcisk albo dlaczego się nie dało. Wymagana, niepusta."""

    code_provenance: dict[str, Any]
    """Opis kodu z gita: commit, drzewo, stan. Nie wchodzi do żadnej tożsamości."""

    executed_at: dt.datetime | None = None
    """Kiedy wykonano. Pole audytowe **poza** odciskiem i identyfikatorem wykonania."""

    @model_validator(mode="after")
    def _check_status(self) -> Self:
        znany = self.execution_fingerprint is not None
        if znany != (self.fingerprint_status is FingerprintStatus.KNOWN):
            raise ValueError(
                "fingerprint_status=known wymaga odcisku, a unknown — jego braku; "
                "odcisku nie zmyślamy i nie ukrywamy"
            )
        if not self.fingerprint_basis:
            raise ValueError(
                "fingerprint_basis jest wymagana: odcisk bez podstawy, a jego brak bez "
                "przyczyny, nie jest dowodem"
            )
        return self

    @classmethod
    def capture(cls, *, executed_at: dt.datetime | None = None) -> "ExecutionRef":
        """Ustala odcisk bieżącego wykonania. Czas zapisuje wyłącznie jako pole audytowe."""
        odcisk, podstawa = compute_fingerprint()
        return cls(
            execution_fingerprint=odcisk,
            fingerprint_status=(
                FingerprintStatus.KNOWN if odcisk is not None else FingerprintStatus.UNKNOWN
            ),
            fingerprint_basis=podstawa,
            code_provenance=git_description(project_root(package_dir())),
            executed_at=executed_at,
        )

    def execution_id(self, run_id: str, digest: str) -> str:
        """Identyfikator wykonania: przebieg + odcisk + treść wyników.

        Bez czasu, bez opisu gita i bez pochodzenia plików wejściowych: żadne z nich nie
        wpływa na wynik, więc wpuszczone do tożsamości byłoby fałszywym zróżnicowaniem.
        Objaw zależy od miejsca. W odcisku — CSV i XLSX stałyby się dwoma legalnymi
        wykonaniami. Wyłącznie tutaj — dwa identyfikatory przy tej samej parze
        ``(run_id, execution_fingerprint)``, a ``UNIQUE`` na tej parze zgłosiłby
        sprzeczność przy identycznych wynikach. Wpis DT-21.
        """
        return compute_id(
            _EXECUTION_PREFIX,
            {
                "run_id": run_id,
                "execution_fingerprint": self.execution_fingerprint,
                "result_digest": digest,
                "identity_algorithm_version": EXECUTION_IDENTITY_VERSION,
            },
            algorithm_version=EXECUTION_IDENTITY_VERSION,
        )
