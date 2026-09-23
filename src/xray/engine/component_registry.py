# Implementuje ZOP-XR-V12-R1 kartę wykonawczą §6.1 (zamrożony registry kierunkowy Core 10)
# wraz z audytem źródeł z ZOP-XR-FOUNDATION-BIND-01 v1.2 §8 (CORE 10 — SOURCE AUDIT).
"""Zamrożony rejestr komponentów Core 10.

Rejestr odpowiada na jedno pytanie: **czy ta para (test, komponent) pochodzi z zamrożonego
źródła**. Nie liczy niczego, nie wykonuje testów i nie zna matematyki Core 10.

## Jeden test, jeden typ

Karta §6.1 przypisuje każdemu testowi dokładnie jeden `component_type`: `FIN-02` ma
`MODULE`, pozostałe dziewięć — `EXECUTION_COMPONENT`. Nie jest to arbitralne: v1.2 §8
klasyfikuje `FIN-02` jako `FORMAL_MODULES_EXPLICIT` („§10.5 »Dostępność modułów przy
niepełnych danych«… Exact source formalnie nazywa moduły i ich minimalne podstawy"),
a pozostałe jako `SOURCE_DEFINED_INDEPENDENT_OUTPUTS_BINDABLE` („Źródło ustanawia named
outputs i selective execution, ale nie formalną listę module_id").

Dlatego `FIN-01` z typem `MODULE` jest tu odmową, nawet gdy `component_id` się zgadza:
karta §6 stanowi `TECHNICAL_EXECUTION_COMPONENT_IS_METHODOLOGICAL_MODULE = false`.
Struktura samej referencji dopuszcza obie kombinacje — to rozdzielenie jest opisane
w ``xray.canonical.component``.

## Canonical null nie jest tu legalny dla żadnego testu

Karta §6: „Canonical null jest legalne wyłącznie dla rzeczywiście non-modular / no
independent component wynikającego z frozen source. **Nie używaj null jako zamiennika braku
zaimplementowanego registry**". Sprawdzone w v1.2 §8: **wszystkie dziesięć** testów Core 10
ma legalną granulację i kolumnę „TEST_PARTIAL reachable? = YES". Żaden nie jest
non-modular, więc `None` dla zarejestrowanego testu jest odmową, a nie skrótem.

Konsekwencja dla scenariusza C-T04 („NON-MODULAR TEST") jest opisana w handoffie: na
zamrożonym źródle nie ma dziś podmiotu tego scenariusza.

## MGT-01 jest parametryczny

Karta §6.1 podaje dla MGT-01 wzorzec `MGT01-EC-DIMENSION::<information_dimension_name>`.
Nazwy wymiarów **nie pochodzą stąd** — pochodzą z ZOP-XR-MGT-01 v1.0 §12.3 („Wymiary jakości
informacji", szesnaście wierszy) i §12.4, gdzie kontrakt pola brzmi: „information_dimension_name
| jeden z **co najmniej**: source_quality / definition_quality / scope_quality /
period_alignment / completeness_coverage / comparability / granularity / timeliness /
lineage / reproducibility / reconciliation / decision_fitness / ownership / stability /
unit_consistency / transformation_quality".

Zwrot „co najmniej" znaczy, że to karta MGT-01, a nie ten rejestr, decyduje o zamknięciu
listy. Nazwa spoza szesnastki jest tutaj odmawiana nie dlatego, że lista jest zamknięta,
tylko dlatego, że **nic w zamrożonym źródle takiego wymiaru nie ustanawia** — a to jest
przesłanka STOP R1-S03 („Source component boundary nie daje się wywieść z frozen source"),
nie miejsce na decyzję implementatora. Rozszerzenie listy = odczyt z MGT-01, nie zmiana
w kodzie „z rozsądku".
"""

from collections.abc import Mapping
from dataclasses import dataclass

from xray.canonical.component import ComponentRef, ComponentType

MGT01_DIMENSION_PREFIX = "MGT01-EC-DIMENSION::"
"""Wzorzec parametrycznego komponentu MGT-01 z karty §6.1."""

MGT01_DIMENSIONS: tuple[str, ...] = (
    # ZOP-XR-MGT-01 v1.0 §12.3 (tabela „Wymiary jakości informacji") i §12.4
    # (kontrakt pola ``information_dimension_name``). Kolejność jak w karcie.
    "source_quality",
    "definition_quality",
    "scope_quality",
    "period_alignment",
    "completeness_coverage",
    "comparability",
    "granularity",
    "timeliness",
    "lineage",
    "reproducibility",
    "reconciliation",
    "decision_fitness",
    "ownership",
    "stability",
    "unit_consistency",
    "transformation_quality",
)
"""Szesnaście wymiarów odczytanych z MGT-01. Lista jest otwarta po stronie karty („co
najmniej"), a nie po stronie kodu — patrz docstring modułu."""


class UnknownTest(LookupError):
    """Test nie występuje w zamrożonym rejestrze §6.1."""


class ComponentContractError(ValueError):
    """Referencja nie jest legalna dla tego testu wobec rejestru §6.1."""


class ComponentNotInRegistry(ComponentContractError):
    """Identyfikator komponentu spoza zamkniętej listy testu.

    Karta §6: „Nie wolno tworzyć ad hoc module_id ani nowej dekompozycji metodologicznej".
    """


class WrongComponentType(ComponentContractError):
    """Typ komponentu inny niż przypisany temu testowi przez §6.1."""


class NullComponentNotAllowed(ComponentContractError):
    """Canonical null dla testu, który ma w zamrożonym źródle legalną granulację."""


@dataclass(frozen=True, slots=True)
class TestComponents:
    """Wiersz rejestru: jeden test, jeden typ, zamknięta lista identyfikatorów."""

    test_id: str
    component_type: ComponentType
    component_ids: tuple[str, ...]
    classification: str
    """Klasyfikacja źródłowa z v1.2 §8."""

    source_locator: str
    """Miejsce w zamrożonej karcie, z którego wywiedziono granice (v1.2 §8)."""


def _mgt01_components() -> tuple[str, ...]:
    """Komponenty MGT-01: szesnaście wymiarów plus gotowość decyzyjna (karta §6.1)."""
    wymiary = tuple(MGT01_DIMENSION_PREFIX + nazwa for nazwa in MGT01_DIMENSIONS)
    return wymiary + ("MGT01-EC-DECISION_READINESS",)


_REGISTRY: tuple[TestComponents, ...] = (
    TestComponents(
        test_id="FIN-01",
        component_type=ComponentType.EXECUTION_COMPONENT,
        component_ids=(
            "FIN01-EC-DYNAMICS",
            "FIN01-EC-TREND",
            "FIN01-EC-LOCALIZATION",
            "FIN01-EC-DECOMPOSITION",
            "FIN01-EC-ECONOMIC_GAP",
        ),
        classification="SOURCE_DEFINED_INDEPENDENT_OUTPUTS_BINDABLE",
        source_locator="FIN-01 §1.1 chain; §2.1; §3 dependent CRITICAL; FIN01-T08 (v1.2 §8)",
    ),
    TestComponents(
        test_id="FIN-02",
        component_type=ComponentType.MODULE,
        component_ids=(
            "FIN02-M-CM1_AMOUNT",
            "FIN02-M-SM_AMOUNT",
            "FIN02-M-OPERATING_RESULT_AMOUNT",
            "FIN02-M-PROFITABILITY_RATE",
            "FIN02-M-RESULT_BRIDGE",
            "FIN02-M-MARGIN_BRIDGE",
            "FIN02-M-MATCHED_BRIDGE",
            "FIN02-M-ADJUSTED_VIEW",
        ),
        classification="FORMAL_MODULES_EXPLICIT",
        source_locator="FIN-02 §10.5; §2.4 layered result (v1.2 §8)",
    ),
    TestComponents(
        test_id="FIN-03",
        component_type=ComponentType.EXECUTION_COMPONENT,
        component_ids=(
            "FIN03-EC-CURRENT_METRIC",
            "FIN03-EC-REFERENCE_COMPARISON",
            "FIN03-EC-BRIDGE",
        ),
        classification="SOURCE_DEFINED_INDEPENDENT_OUTPUTS_BINDABLE",
        source_locator="FIN-03 §14; FIN03-T09 (v1.2 §8)",
    ),
    TestComponents(
        test_id="CAP-01",
        component_type=ComponentType.EXECUTION_COMPONENT,
        component_ids=(
            "CAP01-EC-PHYSICAL_UTILIZATION",
            "CAP01-EC-REFERENCE_GAP",
            "CAP01-EC-ECONOMICS",
        ),
        classification="SOURCE_DEFINED_INDEPENDENT_OUTPUTS_BINDABLE",
        source_locator="CAP-01 §3.1; §4; CAP01-VAL-01/02/10/14; §4.1; §5 (v1.2 §8)",
    ),
    TestComponents(
        test_id="CAP-02",
        component_type=ComponentType.EXECUTION_COMPONENT,
        component_ids=(
            "CAP02-EC-SIGNALS",
            "CAP02-EC-CAPACITY_BALANCE",
            "CAP02-EC-VERIFIED_SHORTAGE",
        ),
        classification="SOURCE_DEFINED_INDEPENDENT_OUTPUTS_BINDABLE",
        source_locator="CAP-02 §1.1 chain; §5; §20 VAL-40; §21 (v1.2 §8)",
    ),
    TestComponents(
        test_id="HR-01",
        component_type=ComponentType.EXECUTION_COMPONENT,
        component_ids=("HR01-EC-LR", "HR01-EC-LP", "HR01-EC-ULC"),
        classification="SOURCE_DEFINED_INDEPENDENT_OUTPUTS_BINDABLE",
        source_locator="HR-01 §13; HR01-T12 (v1.2 §8)",
    ),
    TestComponents(
        test_id="PORT-01",
        component_type=ComponentType.EXECUTION_COMPONENT,
        component_ids=(
            "PORT01-EC-CM1",
            "PORT01-EC-SM",
            "PORT01-EC-FULL_RESULT",
            "PORT01-EC-MIX_MARGIN_EFFECTS",
        ),
        classification="SOURCE_DEFINED_INDEPENDENT_OUTPUTS_BINDABLE",
        source_locator="PORT-01 §1.1; §3.3 hierarchy; §13 statusy (v1.2 §8)",
    ),
    TestComponents(
        test_id="PROC-01",
        component_type=ComponentType.EXECUTION_COMPONENT,
        component_ids=(
            "PROC01-EC-ELAPSED",
            "PROC01-EC-QUEUE_TIME",
            "PROC01-EC-TRANSITION_DELAY",
        ),
        classification="SOURCE_DEFINED_INDEPENDENT_OUTPUTS_BINDABLE",
        source_locator="PROC-01 PROC01-T03–T05; PROC01-T09 (v1.2 §8)",
    ),
    TestComponents(
        test_id="PROC-02",
        component_type=ComponentType.EXECUTION_COMPONENT,
        component_ids=(
            "PROC02-EC-THROUGHPUT",
            "PROC02-EC-QUEUE",
            "PROC02-EC-TIME",
            "PROC02-EC-CAPACITY_EVIDENCE",
            "PROC02-EC-CONSTRAINT_EVIDENCE",
        ),
        classification="SOURCE_DEFINED_INDEPENDENT_OUTPUTS_BINDABLE",
        source_locator="PROC-02 §15.2 groups; §16.1 (v1.2 §8)",
    ),
    TestComponents(
        test_id="MGT-01",
        component_type=ComponentType.EXECUTION_COMPONENT,
        component_ids=_mgt01_components(),
        classification="SOURCE_DEFINED_INDEPENDENT_OUTPUTS_BINDABLE",
        source_locator=(
            "MGT-01 §2.2 decision_partial; §12 dimension_status; §16 (v1.2 §8); "
            "nazwy wymiarów: MGT-01 §12.3 i §12.4"
        ),
    ),
)

COMPONENT_REGISTRY: Mapping[str, TestComponents] = {
    wiersz.test_id: wiersz for wiersz in _REGISTRY
}
"""Zamrożony rejestr z karty §6.1 — dziesięć testów Core 10."""


def components_for(test_id: str) -> TestComponents:
    """Wiersz rejestru dla testu.

    Brak testu w rejestrze to ``UnknownTest``, a nie pusta lista: „nie wiem" i „nie ma
    komponentów" to dwa różne stany, a drugi otwierałby drogę do canonical null bez
    podstawy w źródle.
    """
    try:
        return COMPONENT_REGISTRY[test_id]
    except KeyError:
        raise UnknownTest(
            f"test {test_id!r} nie występuje w zamrożonym rejestrze karty §6.1; "
            f"znane testy: {', '.join(sorted(COMPONENT_REGISTRY))}"
        ) from None


def check_component(test_id: str, ref: ComponentRef | None) -> None:
    """Sprawdza referencję wobec zamrożonego rejestru. Milczy, gdy jest legalna."""
    wiersz = components_for(test_id)
    if ref is None:
        raise NullComponentNotAllowed(
            f"test {test_id!r} ma w zamrożonym źródle legalną granulację "
            f"({len(wiersz.component_ids)} komponentów), więc canonical null nie jest dla "
            "niego legalny; karta §6: null nie zastępuje braku rejestru"
        )
    if ref.component_type is not wiersz.component_type:
        raise WrongComponentType(
            f"test {test_id!r} ma w §6.1 typ {wiersz.component_type}, a referencja niesie "
            f"{ref.component_type}; typ jest znaczący dla tożsamości"
        )
    if ref.component_id not in wiersz.component_ids:
        raise ComponentNotInRegistry(
            f"komponent {ref.component_id!r} nie należy do zamkniętej listy testu "
            f"{test_id!r}; karta §6 zakazuje tworzenia ad hoc komponentów"
        )
