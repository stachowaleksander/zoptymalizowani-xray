# Implementuje ZOP-XR-V12-R1 kartę wykonawczą §10.1 (minimalne R1 binding wyłączeń)
# oraz ZOP-XR-FOUNDATION-BIND-01 v1.2 §7.3 i §7.5 (EffectiveExclusionContextV1).
"""Efektywny kontekst wyłączeń — semantyka **konkretnego obliczenia**.

v1.2 §7.3 stawia granicę, z której wynika cały ten moduł: „Exclusion effect jest semantyką
konkretnego obliczenia, **nie semantic data run i nie semantic result identity**" oraz
``EXCLUSION_EFFECT_IN_RESULT_IDENTITY = false``. Wyłączenie nie zmienia więc pytania
diagnostycznego — zmienia konkretną odpowiedź, a ta mieszka w ``CalculationResultRecord``.

## Kolejność jest wymuszona konstrukcją, nie komentarzem

Karta §10.1 podaje sześć kroków: ustal ``result_identity`` → ustal legalne stosowalne
wyłączenia → zmaterializuj ``exclusion_application_key`` → zbuduj kontekst → wykonaj
obliczenie → zapisz niezmienny rekord. Kolejność jest **niecykliczna**, bo klucz
zastosowania zawiera ``result_identity``:

    exclusion_application_key = "EXAPP-" + SHA256(canonical{result_identity,
        calculation_component_ref, exclusion_subject_type, exclusion_subject_id})

Dlatego ``result_identity`` nie jest tu polem obiektu, tylko **argumentem** metod
liczących skróty. Nie da się policzyć klucza ani skrótu kontekstu, nie mając wcześniej
tożsamości wyniku — a to znaczy, że wyłączenie nigdy nie zdąży jej przedefiniować.

## Co znaczy „efektywne"

Karta §10.1: „EffectiveExclusionContextV1 opisuje wyłącznie wyłączenia, które **faktycznie
wpłynęły** na konkretne obliczenie. … Non-effective candidate exclusions mogą pozostać
w audit evidence, ale nie należą do effective_application_keys". Kandydat, który nic nie
zmienił, nie wchodzi do skrótu — inaczej dwa identyczne obliczenia różniłyby się rekordem
tylko dlatego, że komuś przyszło do głowy rozważyć dodatkowe wyłączenie.

Brak efektywnych wyłączeń to **pusta lista**, nie brak kontekstu:
``no_effective_exclusions => effective_application_keys = []``.

## Czego tu nie ma

Rejestru wyłączeń. ``exclusion_id`` i identyfikator podmiotu są **wejściem** — ten moduł
wiąże je z obliczeniem, ale nie wydaje. Kto i jak nadaje ``exclusion_id``, pozostaje poza
zakresem V12-R1; obserwowalność osieroconych wyłączeń to V12-R6 (karta §10.1: „R1 nie
implementuje RECORD_EXCLUSION_ORPHANED ani cross-import orphan observability").
"""

import hashlib
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from xray.canonical.component import ComponentRef, component_ref_payload
from xray.canonical.identity_json import CanonicalSet, canonical_bytes, identity
from xray.canonical.period import CanonicalPeriod, period_payload

CONTEXT_VERSION = "EffectiveExclusionContextV1"
"""Wartość pola ``context_version`` w skrócie kontekstu (karta §10.1)."""

_PREFIX = "EXAPP"
_RESULT_PREFIX = "RESULT-"
_SCOPE_PREFIX = "SCOPE-"


class ExclusionContractError(ValueError):
    """Zastosowanie wyłączenia nie spełnia kontraktu karty §10.1."""


@dataclass(frozen=True, slots=True)
class ExclusionApplication:
    """Jedno wyłączenie, które faktycznie wpłynęło na obliczenie.

    Karta §10.1: „Każda effective application wiąże co najmniej exclusion_application_key,
    exclusion_id, subject_type, subject_technical_identity, calculation_component_ref,
    scope_id i period". Klucz liczy się z **czterech** z tych elementów — reszta jest
    wiązaniem rekordu, nie składnikiem skrótu.
    """

    exclusion_id: str
    exclusion_subject_type: str
    exclusion_subject_id: str
    """``subject_technical_identity`` — identyfikator techniczny podmiotu wyłączenia."""

    calculation_component_ref: ComponentRef | None = None
    scope_id: str | None = None
    period: CanonicalPeriod | None = None

    def __post_init__(self) -> None:
        for nazwa, wartosc in (
            ("exclusion_id", self.exclusion_id),
            ("exclusion_subject_type", self.exclusion_subject_type),
            ("exclusion_subject_id", self.exclusion_subject_id),
        ):
            if not isinstance(wartosc, str) or not wartosc.strip():
                raise ExclusionContractError(f"{nazwa} nie może być pusty (karta §10.1)")
        if self.scope_id is not None and not self.scope_id.startswith(_SCOPE_PREFIX):
            raise ExclusionContractError(
                f"scope_id {self.scope_id!r} nie wygląda na identyfikator zakresu"
            )

    def application_key(self, result_identity: str) -> str:
        """``"EXAPP-" + SHA256(canonical{result_identity, component, subject_type, subject_id})``.

        ``result_identity`` jest argumentem, a nie polem: klucz **nie może** powstać przed
        tożsamością wyniku (karta §10.1, krok 1 przed krokiem 3).
        """
        _check_result_identity(result_identity)
        return identity(
            _PREFIX,
            {
                "calculation_component_ref": component_ref_payload(
                    self.calculation_component_ref
                ),
                "exclusion_subject_id": self.exclusion_subject_id,
                "exclusion_subject_type": self.exclusion_subject_type,
                "result_identity": result_identity,
            },
        )

    def binding(self, result_identity: str) -> dict[str, Any]:
        """Pełne wiązanie zastosowania — do zapisu w dowodzie, nie do skrótu."""
        return {
            "calculation_component_ref": component_ref_payload(self.calculation_component_ref),
            "exclusion_application_key": self.application_key(result_identity),
            "exclusion_id": self.exclusion_id,
            "exclusion_subject_id": self.exclusion_subject_id,
            "exclusion_subject_type": self.exclusion_subject_type,
            "period": period_payload(self.period),
            "scope_id": self.scope_id,
        }


@dataclass(frozen=True, slots=True)
class EffectiveExclusionContextV1:
    """Zbiór wyłączeń, które faktycznie wpłynęły na to jedno obliczenie."""

    applications: Sequence[ExclusionApplication] = ()

    def __post_init__(self) -> None:
        """Dwa zastosowania o tej samej **czwórce** to jedno efektywne wyłączenie (v1.1 T15).

        Sprawdzamy to już przy konstrukcji, bo kontekst opisujący jedno wyłączenie dwa razy
        jest błędny niezależnie od tego, czy ktoś policzy z niego skrót. Klucz zależy od
        ``result_identity``, ale **równość** kluczy już nie: dwa zastosowania dają ten sam
        klucz dla każdej tożsamości wtedy i tylko wtedy, gdy zgadzają się na komponencie,
        typie i identyfikatorze podmiotu.
        """
        widziane: set[tuple[Any, ...]] = set()
        for zastosowanie in self.applications:
            czworka = (
                component_ref_payload(zastosowanie.calculation_component_ref) is None,
                str(component_ref_payload(zastosowanie.calculation_component_ref)),
                zastosowanie.exclusion_subject_type,
                zastosowanie.exclusion_subject_id,
            )
            if czworka in widziane:
                raise ExclusionContractError(
                    "dwa zastosowania dadzą ten sam exclusion_application_key, czyli opisują "
                    "to samo efektywne wyłączenie (v1.1 T15: „two exclusion_id / one "
                    "EXAPP | one effective exclusion”); zmaterializuj jedno zastosowanie "
                    "i zachowaj oba powody w dowodzie audytowym"
                )
            widziane.add(czworka)

    def application_keys(self, result_identity: str) -> tuple[str, ...]:
        """Klucze zastosowań, posortowane kanonicznie przez profil przy liczeniu skrótu."""
        return tuple(
            zastosowanie.application_key(result_identity) for zastosowanie in self.applications
        )

    def payload(self, result_identity: str) -> dict[str, Any]:
        """Ładunek kontekstu: wersja i **zbiór** kluczy zastosowań."""
        return {
            "context_version": CONTEXT_VERSION,
            "effective_application_keys": CanonicalSet(self.application_keys(result_identity)),
        }

    def digest(self, result_identity: str) -> str:
        """``SHA256(XR_IDENTITY_CANONICAL_JSON_V1({context_version, effective_application_keys}))``.

        Bez prefiksu — karta §10.1 podaje sam skrót, tak jak przy ``result_payload_digest``.

        Kontekst z dwoma zastosowaniami o tym samym kluczu w ogóle nie powstanie — patrz
        ``__post_init__`` i scenariusz T15 z v1.1.
        """
        return hashlib.sha256(canonical_bytes(self.payload(result_identity))).hexdigest()


EMPTY_CONTEXT = EffectiveExclusionContextV1()
"""Kontekst bez efektywnych wyłączeń — ``effective_application_keys = []``.

Jego skrót nie zależy od ``result_identity``, bo nie ma w nim żadnego klucza. To nie jest
brak kontekstu: obliczenie bez wyłączeń ma pusty kontekst, a nie żaden.
"""


def _check_result_identity(result_identity: str) -> None:
    if not isinstance(result_identity, str) or not result_identity.startswith(_RESULT_PREFIX):
        raise ExclusionContractError(
            f"result_identity {result_identity!r} nie wygląda na tożsamość wyniku; "
            f"oczekiwany prefiks {_RESULT_PREFIX!r} — klucz zastosowania nie może powstać "
            "przed tożsamością (karta §10.1)"
        )
