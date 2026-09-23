# Implementuje ZOP-XR-FOUNDATION-BIND-01 v1.0 §4 (C — SCOPE IDENTITY CONTRACT) i §4.1
# (kanoniczna serializacja scope), dziedziczone i zamrożone rozstrzygnięciem Controllingu
# z 2026-09-23 (wpis B-09), oraz v1.1 §10 i §7.1 (formuła scope_id).
"""Tożsamość zakresu — bez etykiety, z kanonicznym predykatem.

## Dlaczego sięgamy do dokumentu oznaczonego jako archiwalny

Reguła projektu mówi: nie przepisujemy wartości z wersji wycofanych. Tu robimy inaczej
i dlatego to zdanie jest w kodzie, a nie tylko w rozmowie: **Controlling rozstrzygnięciem
z 2026-09-23 (wpis B-09) uznał Scope Identity Contract z BIND-01 v1.0 §4 / §4.1 za
dziedziczony i zamrożony** — „korzystaj z dziedziczonego frozen Scope Identity Contract
v1.0; nie twórz nowego". Ten jeden kontrakt obowiązuje więc wprost z v1.0; reszta v1.0
pozostaje archiwalna i nadal nie wolno z niej nic przepisywać.

Powód, dla którego to w ogóle było pytaniem: v1.1 §10 i v1.2 wymagają, żeby filtry weszły
do `scope_id`, ale ani jeden, ani drugi nie podaje kształtu predykatu — robi to wyłącznie
v1.0 §4.1.

## Co ustala v1.0 §4 (cytaty)

- `scope_label` — „Opis użytkowy. **Wykluczony z identity**".
- `scope_definition.filters` — „Kanoniczne predicates: **field, operator, value**.
  Kolejność predykatów jest **nieistotna** i po normalizacji sortowana po canonical bytes".
- `scope_definition.population` — „Jawny selektor/populacja jednostek lub obiektów. **Zbiór
  sortowany**, jeżeli karta nie nadaje kolejności semantycznego znaczenia".
- `scope_definition.aggregation_level` — „Jawny poziom agregacji. **Dla zestawu wymiarów
  kolejność nie jest identity-defining**".
- `scope_definition.constraints` — „Inne jawne ograniczenia zakresu wymagane przez kartę.
  Kolejność nieistotna, chyba że source contract stanowi inaczej".
- `scope_definition.contract_scope_extensions` — „Dodatkowe scope-defining pola z frozen
  test contract, włączone pod ich technicznymi nazwami".
- `scope_definition_hash` — „SHA-256 lowercase hex z canonical UTF-8 JSON scope_definition";
  `scope_id` — „»SCOPE-« + scope_definition_hash".

§4.1 dokłada sześć reguł serializacji (NFC bez case-foldingu i przycinania; sortowanie
kluczy bez zbędnych białych znaków; predykaty jako field/operator/value; listy zbiorowe
sortowane, sekwencyjne zachowujące kolejność; wartości zachowują typ; etykieta i kolejności
nie wpływają na tożsamość) oraz dwa zdania zamykające:

    same_semantics → same_scope_id
    different_filters_or_population_or_aggregation_or_scope_constraints → different_scope_id

Wszystkie sześć reguł realizuje profil ``XR_IDENTITY_CANONICAL_JSON_V1`` z pakietu
``canonical`` — ten moduł nie ma własnego serializatora i mieć go nie może.

## Operatory

§4.1 pkt 3: „dozwolony operator musi być technicznie jednoznaczny (**np.** EQ, NE, IN,
NOT_IN, LT, LTE, GT, GTE, RANGE)". Dziewięć nazw poniżej to dokładnie te z kontraktu —
ani jednej więcej. Słowo „np." znaczy jednak, że kontrakt listy **nie zamyka**: wiążącym
kryterium jest jednoznaczność techniczna, a nie ta wyliczanka. Operator spoza dziewiątki
jest tu odmawiany nie dlatego, że lista jest zamknięta, tylko dlatego, że nic w zamrożonym
źródle takiego operatora nie ustanawia. To samo rozumowanie co przy wymiarach MGT-01.
Szczegóły i dwie dalsze niejednoznaczności predykatu — wpis B-12.
"""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from xray.canonical.identity_json import CanonicalSet, identity

_PREFIX = "SCOPE"


class ScopeOperator(StrEnum):
    """Operatory predykatu wymienione w BIND-01 v1.0 §4.1 pkt 3.

    Kolejność jak w kontrakcie. Lista jest tam poprzedzona słowem „np.", więc pozostaje
    otwarta po stronie kontraktu — patrz docstring modułu i wpis B-12.
    """

    EQ = "EQ"
    NE = "NE"
    IN = "IN"
    NOT_IN = "NOT_IN"
    LT = "LT"
    LTE = "LTE"
    GT = "GT"
    GTE = "GTE"
    RANGE = "RANGE"


class ScopeContractError(ValueError):
    """Zakres nie spełnia kontraktu v1.0 §4."""


@dataclass(frozen=True, slots=True)
class ScopePredicate:
    """Predykat filtra: ``field`` / ``operator`` / ``value`` (v1.0 §4.1 pkt 3).

    Trzy pola i nic więcej — dopisanie czwartego zmieniłoby tożsamość każdego zakresu.

    Dla ``IN`` i ``NOT_IN`` goła lista jest **odrzucana**. Kontrakt nie przesądza, czy
    kolekcja w tych operatorach ma semantykę zbioru (wpis B-12), a semantyki zbioru nie
    zgaduje się z typu — to ta sama reguła, która w profilu każe deklarować
    ``CanonicalSet`` zamiast polegać na liście. Gdyby goła lista cicho przechodziła jako
    sekwencja, najbardziej naturalny sposób zbudowania filtru dawałby **cicho niewłaściwy**
    ``scope_id``: ``IN [A, B]`` i ``IN [B, A]`` to ten sam zakres semantyczny.
    """

    field: str
    operator: ScopeOperator
    value: Any = None

    def __post_init__(self) -> None:
        if not isinstance(self.operator, ScopeOperator):
            raise ScopeContractError(
                f"operator {self.operator!r} nie należy do dziewięciu wymienionych "
                "w v1.0 §4.1 pkt 3; nic w zamrożonym źródle nie ustanawia innego (B-12)"
            )
        if not isinstance(self.field, str) or not self.field.strip():
            raise ScopeContractError("pole predykatu musi być niepustym łańcuchem")
        if self.operator in (ScopeOperator.IN, ScopeOperator.NOT_IN) and isinstance(
            self.value, (list, tuple)
        ):
            raise ScopeContractError(
                f"operator {self.operator} dostał gołą listę; kontrakt nie przesądza, czy "
                "kolekcja w IN/NOT_IN ma semantykę zbioru (wpis B-12), a semantyki zbioru "
                "nie zgadujemy z typu — zadeklaruj ją przez CanonicalSet"
            )

    def payload(self) -> dict[str, Any]:
        return {
            "field": self.field,
            "operator": str(self.operator),
            "value": self.value,
        }


def _set_or_scalar(value: Any) -> Any:
    """Zestaw wymiarów sortujemy, pojedynczy poziom zostawiamy jak jest.

    v1.0 §4: „Dla zestawu wymiarów kolejność nie jest identity-defining". Poziom agregacji
    bywa jedną nazwą albo zestawem wymiarów; w drugim przypadku kolejność wymienienia nie
    jest informacją.
    """
    if isinstance(value, (list, tuple)):
        return CanonicalSet(value)
    return value


@dataclass(frozen=True, slots=True)
class ScopeDefinition:
    """Pięć składników ``scope_definition`` z v1.0 §4 plus etykieta poza tożsamością."""

    filters: Sequence[ScopePredicate] = ()
    """Kanoniczne predykaty. Zbiór — „Kolejność predykatów jest nieistotna"."""

    population: Sequence[Any] = ()
    """Jawny selektor/populacja. Zbiór sortowany (v1.0 §4).

    Kontrakt dopuszcza wyjątek — „jeżeli karta nie nadaje kolejności semantycznego
    znaczenia". Żadna zamrożona karta takiej kolejności dziś nie nadaje; gdy nada, trzeba
    będzie dodać jawną deklarację sekwencji, a nie domyślać się jej z typu.
    """

    aggregation_level: Any = None
    """Poziom agregacji: jedna nazwa albo zestaw wymiarów (wtedy kolejność nieistotna)."""

    constraints: Sequence[Any] = ()
    """Inne jawne ograniczenia zakresu wymagane przez kartę. Kolejność nieistotna."""

    contract_scope_extensions: Mapping[str, Any] = field(default_factory=dict)
    """„Dodatkowe scope-defining pola z frozen test contract, włączone pod ich technicznymi
    nazwami" (v1.0 §4). Struktura pozostaje otwarta — wpis B-10."""

    scope_label: str | None = None
    """Opis użytkowy. **Poza tożsamością** — v1.0 §4 i §4.1 pkt 6."""

    def __post_init__(self) -> None:
        obce = [f for f in self.filters if not isinstance(f, ScopePredicate)]
        if obce:
            raise ScopeContractError(
                "filtry muszą być kanonicznymi predykatami field/operator/value "
                f"(v1.0 §4.1 pkt 3); dostałem: {obce[0]!r}"
            )

    def payload(self) -> dict[str, Any]:
        """Ładunek kanoniczny zakresu — pięć składników, bez etykiety."""
        return {
            "aggregation_level": _set_or_scalar(self.aggregation_level),
            "constraints": CanonicalSet(self.constraints),
            "contract_scope_extensions": dict(self.contract_scope_extensions),
            "filters": CanonicalSet(predykat.payload() for predykat in self.filters),
            "population": CanonicalSet(self.population),
        }


def scope_id(scope: ScopeDefinition) -> str:
    """``"SCOPE-" + SHA256(canonical(scope_definition))`` — v1.0 §4, v1.1 §7.1.

    # DECYZJA (Controlling, 2026-09-23), wpis B-09: struktura predykatu i lista operatorów
    # pochodzą z dziedziczonego, zamrożonego Scope Identity Contract v1.0 §4 / §4.1.
    """
    return identity(_PREFIX, scope.payload())
