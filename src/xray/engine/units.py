# Implementuje ZOP-XR-FOUNDATION-BIND-01 v1.2 §7 (tabela jednostki wykonania: wiersze
# applicability, execution_status, dependency_scope) i §7.1 (deterministyczny TEST_PARTIAL)
# oraz v1.2 §22, wiersze T01, T02 i T07 (wyprowadzenie statusu testu z legalnych jednostek).
"""Jednostki wykonania i wyprowadzanie statusu testu.

Jednostka wykonania to para ``(test_id, calculation_component_ref)`` — czyli dokładnie to,
co zamraża rejestr komponentów z karty §6.1. Ma **własny status** i **własną podstawę**.
Status całego testu nie jest nadawany wprost: jest **wyprowadzany** ze statusów jednostek.

## Co dokładnie mówi kontrakt (BIND-01 v1.2)

§7, wiersz tabeli (l. 233):

    | execution_status | UNIT_NOT_APPLICABLE | UNIT_READY | UNIT_BLOCKED | UNIT_EXECUTED |

§7, wiersz ``applicability`` (l. 231): „Source-defined; unresolved applicability nie może
być cicho uznana za N/A".

§7, wiersz ``dependency_scope`` (l. 237): „Powiązanie walidacji/structural/currency tylko do
tej legalnej jednostki albo GLOBAL_TEST" — to jest podstawa blokowania selektywnego.

§7.1 „Deterministyczny TEST_PARTIAL" (l. 253–261), pięć warunków:

    1. Wszystkie applicability legalnych execution units są rozstrzygnięte; nie ma
       UNIT_READY przy finalizacji.
    2. Co najmniej jedna applicable jednostka ma UNIT_EXECUTED.
    3. Co najmniej jedna inna applicable jednostka ma UNIT_BLOCKED albo source-defined
       not-computable outcome wpływający tylko na tę jednostkę.
    4. Executed + blocked obejmuje wszystkie applicable jednostki.
    5. Frozen card dopuszcza odpowiedzialne zachowanie częściowe dla takiego podziału.
       Jeżeli source nie ustanawia niezależności, TEST_PARTIAL nie jest tworzony przez samą
       implementację.

§22, wiersz T01 (l. 1213): „GLOBAL prerequisite CRITICAL → TEST_BLOCKED. | Bez zmiany."
§22, wiersz T02 (l. 1215): „A/B »modules«; local CRITICAL blocks A, B executes →
TEST_PARTIAL. | A/B = legal execution units … semantic outcome ten sam."
§22, wiersz T07 (l. 1219): „… test status derived z legal units."

## Czego ta warstwa jeszcze nie robi

**Nie jest podpięta do ``DiagnosticTest.execute``.** ``DiagnosticTestDeclaration`` przyjmuje
pole ``units`` i sprawdza je wobec zamrożonego rejestru §6.1, ale silnik nie wyprowadza
z nich statusu w trakcie przebiegu — bo **żaden test Core 10 nie deklaruje dziś jednostek**
(jedyną zarejestrowaną wtyczką jest atrapa ``NOOP-01``). Podpięcie ma sens dopiero wtedy,
gdy pierwszy test poda swoje jednostki; wcześniej byłoby maszynerią bez wejścia.

Skutek dla czytelnika wyniku: status testu nadal pochodzi z ``run`` wtyczki, tak jak przed
tą rundą. Maszyneria jednostek jest kompletna i sprawdzona wektorami T50 i T51, ale nie
uczestniczy w ścieżce wykonania.

## Czego kontrakt **nie** mówi

§7.1 podaje warunki wyłącznie dla ``TEST_PARTIAL``. Nie ustala, co ma wyjść, gdy:

- wszystkie applicable jednostki są ``UNIT_BLOCKED`` (warunek 2 nie jest spełniony, a T01
  dotyczy blokady **globalnej**, nie sumy blokad jednostkowych),
- żadna jednostka nie jest applicable.

Tych dwóch przypadków **nie interpretujemy**: funkcja odmawia wyprowadzenia i odsyła do
wpisu B-15. Wymyślenie statusu byłoby regułą bez źródła, a sięgnięcie po
``TEST_NOT_APPLICABLE`` z v1.1 — wprowadzeniem wartości spoza zamkniętego katalogu
``LogicalStatus``.

Trzeci przypadek — wszystkie jednostki wykonane — nie jest luką: status testu jest wtedy
zwykłym statusem diagnostycznym z zamrożonej karty, a jego wyliczenie to matematyka
Core 10, której runda V12-R1 nie dotyka (v1.2 §21, kolumna „Nie dotyka"). Wyprowadzenie
oddaje wtedy głos testowi i mówi o tym wprost.
"""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from enum import StrEnum

from xray.canonical.component import ComponentRef
from xray.model.enums import LogicalStatus


class UnitExecutionStatus(StrEnum):
    """Katalog statusu jednostki — dosłownie z v1.2 §7, wiersz ``execution_status``."""

    UNIT_NOT_APPLICABLE = "UNIT_NOT_APPLICABLE"
    UNIT_READY = "UNIT_READY"
    UNIT_BLOCKED = "UNIT_BLOCKED"
    UNIT_EXECUTED = "UNIT_EXECUTED"


class DependencyScope(StrEnum):
    """Zasięg wiązania walidacji (v1.2 §7, wiersz ``dependency_scope``)."""

    UNIT = "UNIT"
    GLOBAL_TEST = "GLOBAL_TEST"


class UnresolvedApplicability(ValueError):
    """Applicability jednostki nie została rozstrzygnięta.

    v1.2 §7: „unresolved applicability nie może być cicho uznana za N/A". Milczenie
    zamieniłoby brak wiedzy w decyzję metodologiczną.
    """


class StatusNotDerivable(ValueError):
    """Kontrakt nie ustala statusu testu dla tego układu jednostek — patrz wpis B-15."""


@dataclass(frozen=True, slots=True)
class UnitDeclaration:
    """Jedna jednostka wykonania: ``(test_id, calculation_component_ref)`` plus podstawy."""

    test_id: str
    component_ref: ComponentRef | None
    applicable: bool | None = None
    """``None`` oznacza **nierozstrzygnięte**, a nie „nie dotyczy" (v1.2 §7)."""

    required_tables: tuple[str, ...] = ()
    required_fields: Mapping[str, tuple[str, ...]] = field(default_factory=dict)
    """Tabele i pola, od których zależy **ta** jednostka — nie cały test."""

    @property
    def unit_id(self) -> tuple[str, str | None]:
        return (
            self.test_id,
            None if self.component_ref is None else self.component_ref.component_id,
        )


@dataclass(frozen=True, slots=True)
class CriticalFinding:
    """Kontrola o wyniku CRITICAL wraz z zasięgiem zależności."""

    check_id: str
    scope: DependencyScope
    table: str | None = None
    fields: tuple[str, ...] = ()

    def touches(self, unit: UnitDeclaration) -> bool:
        """Czy ta luka dotyka tej jednostki.

        Blokowanie jest **selektywne**: jednostka niezależna od dotkniętej tabeli i pola
        liczy się dalej. Blokowanie całego testu „bo prościej" jest tym, czego zakazuje
        wiersz T02 z §22.
        """
        if self.scope is DependencyScope.GLOBAL_TEST:
            return True
        if self.table is None or self.table not in unit.required_tables:
            return False
        if not self.fields:
            return True
        wymagane = set(unit.required_fields.get(self.table, ()))
        return bool(wymagane & set(self.fields))


@dataclass(frozen=True, slots=True)
class UnitOutcome:
    """Status jednostki wraz z jawną podstawą."""

    unit: UnitDeclaration
    status: UnitExecutionStatus
    basis: str


@dataclass(frozen=True, slots=True)
class StatusDerivation:
    """Wynik wyprowadzenia statusu testu ze statusów jednostek."""

    status: LogicalStatus | None
    """``None`` znaczy „wyprowadzenie oddaje głos testowi", a nie „brak statusu"."""

    defers_to_test_outcome: bool
    basis: str


def _opis_blokady(krytyczna: "CriticalFinding") -> str:
    """Czytelna podstawa blokady: kontrola, a przy zasięgu jednostkowym też tabela i pola."""
    if krytyczna.table is None:
        return krytyczna.check_id
    pola = "." + "/".join(krytyczna.fields) if krytyczna.fields else ""
    return f"{krytyczna.check_id} ({krytyczna.table}{pola})"


def evaluate_units(
    declarations: Sequence[UnitDeclaration],
    criticals: Sequence[CriticalFinding] = (),
    computed: Sequence[tuple[str, str | None]] = (),
) -> tuple[UnitOutcome, ...]:
    """Nadaje status każdej jednostce osobno.

    ``computed`` to jednostki, których obliczenie **faktycznie** się wykonało — podaje je
    warstwa uruchamiająca, bo to ona wie, co policzyła. Jednostka rozstrzygnięta, wolna od
    blokad, ale niepoliczona, zostaje ``UNIT_READY`` — i taki stan nie może dotrwać do
    finalizacji (§7.1 pkt 1).
    """
    policzone = set(computed)
    wyniki: list[UnitOutcome] = []
    for jednostka in declarations:
        if jednostka.applicable is None:
            raise UnresolvedApplicability(
                f"jednostka {jednostka.unit_id} ma nierozstrzygniętą applicability; "
                "v1.2 §7 zakazuje uznania jej po cichu za N/A"
            )
        if not jednostka.applicable:
            wyniki.append(
                UnitOutcome(
                    jednostka,
                    UnitExecutionStatus.UNIT_NOT_APPLICABLE,
                    "applicability rozstrzygnięta przez źródło: jednostka nie dotyczy",
                )
            )
            continue
        blokady = [krytyczna for krytyczna in criticals if krytyczna.touches(jednostka)]
        if blokady:
            powody = ", ".join(_opis_blokady(k) for k in blokady)
            wyniki.append(
                UnitOutcome(
                    jednostka,
                    UnitExecutionStatus.UNIT_BLOCKED,
                    f"CRITICAL dotyka podstawy tej jednostki: {powody}",
                )
            )
            continue
        if jednostka.unit_id in policzone:
            wyniki.append(
                UnitOutcome(
                    jednostka,
                    UnitExecutionStatus.UNIT_EXECUTED,
                    "podstawa kompletna, obliczenie jednostki wykonane",
                )
            )
            continue
        wyniki.append(
            UnitOutcome(
                jednostka,
                UnitExecutionStatus.UNIT_READY,
                "podstawa kompletna, obliczenie jednostki jeszcze nie wykonane",
            )
        )
    return tuple(wyniki)


def derive_test_status(
    outcomes: Sequence[UnitOutcome],
    criticals: Sequence[CriticalFinding] = (),
) -> StatusDerivation:
    """Wyprowadza status testu ze statusów jednostek. Nigdy go nie nadaje z zewnątrz.

    Kolejność rozstrzygania idzie za kontraktem:

    1. CRITICAL o zasięgu ``GLOBAL_TEST`` → ``TEST_BLOCKED`` (§22, T01),
    2. jakikolwiek ``UNIT_READY`` → odmowa: finalizacja z nierozstrzygniętą jednostką
       łamie §7.1 pkt 1,
    3. brak jednostek applicable → **odmowa wyprowadzenia** (B-15),
    4. executed + blocked pokrywa wszystkie applicable, przy co najmniej jednej z każdej
       grupy → ``TEST_PARTIAL`` (§7.1 pkt 2–4),
    5. wszystkie applicable wykonane → wyprowadzenie oddaje głos testowi: status jest
       wtedy zwykłym wynikiem diagnostycznym z karty,
    6. wszystkie applicable zablokowane → **odmowa wyprowadzenia** (B-15).
    """
    globalne = [k for k in criticals if k.scope is DependencyScope.GLOBAL_TEST]
    if globalne:
        return StatusDerivation(
            status=LogicalStatus.TEST_BLOCKED,
            defers_to_test_outcome=False,
            basis=(
                "CRITICAL o zasięgu GLOBAL_TEST: "
                + ", ".join(k.check_id for k in globalne)
                + " (v1.2 §22, T01)"
            ),
        )

    gotowe = [w for w in outcomes if w.status is UnitExecutionStatus.UNIT_READY]
    if gotowe:
        raise StatusNotDerivable(
            "przy finalizacji nie może być jednostek UNIT_READY (v1.2 §7.1 pkt 1); "
            f"nierozstrzygnięte: {', '.join(str(w.unit.unit_id) for w in gotowe)}"
        )

    applicable = [
        w for w in outcomes if w.status is not UnitExecutionStatus.UNIT_NOT_APPLICABLE
    ]
    if not applicable:
        raise StatusNotDerivable(
            "żadna jednostka nie jest applicable; v1.2 §7.1 nie ustala statusu dla tego "
            "układu, a TEST_NOT_APPLICABLE nie należy do katalogu LogicalStatus — wpis B-15"
        )

    wykonane = [w for w in applicable if w.status is UnitExecutionStatus.UNIT_EXECUTED]
    zablokowane = [w for w in applicable if w.status is UnitExecutionStatus.UNIT_BLOCKED]

    if wykonane and zablokowane:
        return StatusDerivation(
            status=LogicalStatus.TEST_PARTIAL,
            defers_to_test_outcome=False,
            basis=(
                f"wykonane jednostki: {', '.join(str(w.unit.unit_id) for w in wykonane)}; "
                f"zablokowane: {', '.join(str(w.unit.unit_id) for w in zablokowane)}; "
                "executed + blocked pokrywa wszystkie applicable (v1.2 §7.1 pkt 2–4)"
            ),
        )
    if wykonane:
        return StatusDerivation(
            status=None,
            defers_to_test_outcome=True,
            basis=(
                "wszystkie applicable jednostki wykonane; status testu jest zwykłym "
                "wynikiem diagnostycznym z zamrożonej karty, a jego wyliczenie leży poza "
                "zakresem V12-R1 (v1.2 §21, kolumna „Nie dotyka”)"
            ),
        )
    raise StatusNotDerivable(
        "wszystkie applicable jednostki są UNIT_BLOCKED; §7.1 wymaga dla TEST_PARTIAL co "
        "najmniej jednej wykonanej, a T01 dotyczy blokady globalnej, nie sumy blokad "
        "jednostkowych — wpis B-15"
    )
