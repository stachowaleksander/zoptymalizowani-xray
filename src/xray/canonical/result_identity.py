# Implementuje ZOP-XR-V12-R1 kartę wykonawczą §7 (XR_RESULT_IDENTITY_V2) oraz
# ZOP-XR-FOUNDATION-BIND-01 v1.2 §7.2 (tabela pól i formuła result_identity).
"""Tożsamość wyniku — pytanie diagnostyczne, nie egzemplarz wyniku.

    result_identity = "RESULT-" + SHA256(XR_IDENTITY_CANONICAL_JSON_V1(payload))

Payload ma **dokładnie siedem** składników i żadnych innych (karta §7, v1.2 §7.2):
`result_identity_version`, `test_id`, `test_contract_version`, `calculation_component_ref`,
`scope_id`, `analysis_period`, `reference_id`.

## Co to znaczy „pytanie, a nie egzemplarz"

Karta §7 wylicza wprost, czego do tożsamości włożyć **nie wolno**: `semantic_run_id`,
efektu wyłączeń, `execution_attempt_id`, odcisku wykonania, fizycznego record id, bajtów
źródła, tożsamości parsera, ścieżki i znaczników czasu. Skutek jest celowy i zapisany
w v1.2 §7.2 jako `RESULT_IDENTITY_STABLE_ACROSS_SEMANTIC_RUNS = true`: to samo pytanie
zadane na kolejnym imporcie tych samych danych ma **tę samą** tożsamość wyniku. Rozróżnia
je dopiero `CalculationResultRecord` (v1.2 §7.4), którego ta runda jeszcze nie buduje.

Dlatego payload nie przyjmuje niczego spoza siedmiu pól — nie przez dyscyplinę wołającego,
tylko przez kształt klasy. Gdyby poprawny wynik wymagał ósmego składnika, kontrakt zakazuje
rozszerzania V2 (`XR_RESULT_IDENTITY_V2_OPEN_SEMANTIC_EXTENSIONS_ALLOWED = false`) i każe
zatrzymać się na STOP R1-S06.

## Dwie mylące nazwy

``test_contract_version`` to **wersja zamrożonej karty testu** (v1.2 §7.2: „string; exact
semantic test version"), a nie stała ``CONTRACT_VERSION = "ZOP-TECH-01/v0.1"``
z ``model/findings/identity.py``, która opisuje wersję kontraktu FINDINGS. Dokumenty
obowiązujące nie ustalają, skąd wołający bierze tę wartość ani w jakim formacie ją zapisuje
— nie ma rejestru „test → wersja karty". Dlatego jest tu **jawnym argumentem**, a nie
wartością domyślną: wartość domyślna byłaby regułą, której nikt nie ustanowił.

``result_identity_version`` to literalny łańcuch ``"XR_RESULT_IDENTITY_V2"``, a nie numer
i nie ``IDENTITY_ALGORITHM_VERSION`` starego profilu. Historyczny profil i V2 nie są tym
samym kluczem semantycznym — v1.2 §7.2:
``RESULT_IDENTITY_CROSS_VERSION_EQUIVALENCE_AUTOMATIC = false``.

## Co zostaje nietknięte

``FindingRecord.identity_of`` i ``compute_id`` liczą dalej po staremu. Karta §1 ustala
``HISTORICAL_IDENTITY_REWRITE = false``; ta tożsamość powstaje **obok** i będzie użyta
dopiero przez warstwę rekordów.
"""

from dataclasses import dataclass
from typing import Any

from xray.canonical.component import ComponentRef, component_ref_payload
from xray.canonical.identity_json import identity
from xray.canonical.period import CanonicalPeriod

RESULT_IDENTITY_VERSION = "XR_RESULT_IDENTITY_V2"
"""Literalna wartość pola ``result_identity_version`` (karta §7)."""

_PREFIX = "RESULT"
_SCOPE_PREFIX = "SCOPE-"
_REFERENCE_PREFIX = "REF-"

PAYLOAD_KEYS: frozenset[str] = frozenset(
    {
        "analysis_period",
        "calculation_component_ref",
        "reference_id",
        "result_identity_version",
        "scope_id",
        "test_contract_version",
        "test_id",
    }
)
"""Zamknięty zestaw siedmiu kluczy. Służy też za asercję w testach."""


class ResultIdentityError(ValueError):
    """Ładunek nie spełnia kontraktu karty §7."""


@dataclass(frozen=True, slots=True)
class ResultIdentityV2:
    """Siedem składników pytania diagnostycznego.

    ``analysis_period`` jest wymagany: v1.2 §7.2 opisuje go jako „canonical XR_PERIOD
    object", bez wariantu null. ``calculation_component_ref`` i ``reference_id`` mogą być
    canonical null — pierwszy dla testu bez niezależnych komponentów (karta §6), drugi gdy
    referencja nie dotyczy (v1.1 §12).
    """

    test_id: str
    test_contract_version: str
    scope_id: str
    analysis_period: CanonicalPeriod
    calculation_component_ref: ComponentRef | None = None
    reference_id: str | None = None

    def __post_init__(self) -> None:
        if not self.test_id.strip():
            raise ResultIdentityError("test_id nie może być pusty")
        if not self.test_contract_version.strip():
            raise ResultIdentityError(
                "test_contract_version nie może być pusty; to wersja zamrożonej karty "
                "testu, nie wersja kontraktu FINDINGS"
            )
        if not self.scope_id.startswith(_SCOPE_PREFIX):
            raise ResultIdentityError(
                f"scope_id {self.scope_id!r} nie wygląda na identyfikator zakresu; "
                f"oczekiwany prefiks {_SCOPE_PREFIX!r} (v1.1 §7.1)"
            )
        if not isinstance(self.analysis_period, CanonicalPeriod):
            raise ResultIdentityError(
                "analysis_period musi być kanonicznym obiektem okresu — v1.2 §7.2 "
                "opisuje go jako canonical XR_PERIOD object, bez wariantu null"
            )
        if self.reference_id is not None and not self.reference_id.startswith(_REFERENCE_PREFIX):
            raise ResultIdentityError(
                f"reference_id {self.reference_id!r} nie wygląda na identyfikator "
                f"referencji; oczekiwany prefiks {_REFERENCE_PREFIX!r} (v1.1 §7.1)"
            )

    def payload(self) -> dict[str, Any]:
        """Ładunek kanoniczny — dokładnie siedem kluczy."""
        return {
            "analysis_period": self.analysis_period.payload(),
            "calculation_component_ref": component_ref_payload(self.calculation_component_ref),
            "reference_id": self.reference_id,
            "result_identity_version": RESULT_IDENTITY_VERSION,
            "scope_id": self.scope_id,
            "test_contract_version": self.test_contract_version,
            "test_id": self.test_id,
        }


def result_identity(question: ResultIdentityV2) -> str:
    """``"RESULT-" + SHA256(XR_IDENTITY_CANONICAL_JSON_V1(payload))`` — karta §7."""
    return identity(_PREFIX, question.payload())
