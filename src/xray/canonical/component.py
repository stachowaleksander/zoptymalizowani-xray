# Implementuje ZOP-XR-V12-R1 kartę wykonawczą §6 (calculation_component_ref) oraz
# ZOP-XR-FOUNDATION-BIND-01 v1.2 §7.2 („component_type jest częścią canonical payload").
"""Oś komponentu wyniku — sama struktura, bez wiedzy o rejestrze.

``calculation_component_ref`` ma trzy legalne postaci (karta §6):

    canonical null
    | {component_type:"MODULE", component_id:<module_id>}
    | {component_type:"EXECUTION_COMPONENT", component_id:<execution_component_id>}

## Dlaczego struktura nie sprawdza rejestru

Rozdzielenie jest celowe i wymuszone przez kontrakt. v1.2 §7.2: „Formalny moduł i techniczny
execution component o identycznym `component_id` pozostają różnymi semantic refs, **ponieważ
component_type jest częścią canonical payload**". To jest własność **kanonizacji**, którą
trzeba móc wykazać niezależnie od tego, czy dana para (typ, id) jest legalna dla jakiegoś
testu — scenariusz C-T03 buduje `MODULE:X` i `EXECUTION_COMPONENT:X` z tym samym `X`
i żąda dwóch różnych tożsamości.

Gdyby struktura walidowała się wobec rejestru, tego wektora nie dałoby się w ogóle zbudować,
bo rejestr §6.1 nie przypisuje żadnemu testowi obu typów naraz. Dlatego:

- tutaj: co jest **dobrze zbudowaną** wartością (dwa typy, niepusty identyfikator),
- w ``xray.engine.component_registry``: co jest **legalne dla danego testu** wobec
  zamrożonego rejestru karty §6.1.

## Czego tu nie ma

Żadnej listy dozwolonych identyfikatorów. Ten moduł nie zna Core 10 i nie ma prawa go znać
— dzięki temu nie da się przez niego przemycić komponentu wymyślonego.
"""

from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class ComponentType(StrEnum):
    """Dwa typy osi komponentu (karta §6, v1.2 §7).

    ``MODULE`` — formalny moduł metodologiczny, gdy zamrożona karta nazywa moduły wprost
    (v1.2 §8: klasyfikacja ``FORMAL_MODULES_EXPLICIT``).
    ``EXECUTION_COMPONENT`` — techniczna jednostka wykonania dla części, których niezależność
    i outputy karta już ustanawia, ale bez formalnej listy modułów
    (``SOURCE_DEFINED_INDEPENDENT_OUTPUTS_BINDABLE``).

    Karta §6: ``TECHNICAL_EXECUTION_COMPONENT_IS_METHODOLOGICAL_MODULE = false`` — typ nie
    jest szczegółem technicznym, tylko rozróżnieniem semantycznym.
    """

    MODULE = "MODULE"
    EXECUTION_COMPONENT = "EXECUTION_COMPONENT"


class ComponentRefError(ValueError):
    """Wartość nie jest dobrze zbudowanym ``calculation_component_ref``."""


@dataclass(frozen=True, slots=True)
class ComponentRef:
    """Referencja do komponentu wyniku.

    Dwa pola i nic więcej: ładunek kanoniczny ma dokładnie taki kształt, jaki podaje
    karta §6. Dopisanie trzeciego pola zmieniłoby tożsamość każdego wyniku.
    """

    component_type: ComponentType
    component_id: str

    def __post_init__(self) -> None:
        if not isinstance(self.component_type, ComponentType):
            raise ComponentRefError(
                f"component_type {self.component_type!r} nie jest jednym z dwóch typów karty §6"
            )
        if not self.component_id or not self.component_id.strip():
            raise ComponentRefError("component_id nie może być pusty")

    def payload(self) -> dict[str, Any]:
        """Ładunek kanoniczny referencji.

        ``component_type`` idzie do ładunku jako wartość napisowa, więc wchodzi do skrótu
        na równi z identyfikatorem — to właśnie czyni go „identity-significant".
        """
        return {
            "component_id": self.component_id,
            "component_type": str(self.component_type),
        }


def component_ref_payload(ref: ComponentRef | None) -> dict[str, Any] | None:
    """Ładunek referencji albo ``None`` dla canonical null.

    Karta §6: canonical null jest legalne „wyłącznie dla rzeczywiście non-modular / no
    independent component wynikającego z frozen source. **Nie używaj null jako zamiennika
    braku zaimplementowanego registry**". Ta funkcja go nie ocenia — ocenia rejestr.
    """
    return None if ref is None else ref.payload()
