# Implementuje ZOP-PRI-01 v1.0 rozdz. 3 (kontekst), rozdz. 8 (kwalifikacja)
# i pkt 5.3 (klaster i główna podstawa wpływu).
"""Kwalifikacja priorytetu wyniku i klastra.

## Priorytet nie jest polem wyniku

ZOP-PRI-01 rozdz. 3: „Połączenie ``finding_id + priority_context_id +
priority_evaluation_date + priority_basis_version`` identyfikuje pojedynczą
kwalifikację. Zmiana podstawy lub kontekstu tworzy nową ewaluację, **nie nadpisuje
śladu** wcześniejszej oceny."

Ten sam wynik może więc mieć wiele kwalifikacji — po jednej na kontekst i wersję
podstawy. Gdyby priorytet był kolumną w FINDINGS, każda ponowna ocena kasowałaby
poprzednią, a PRI-01 wprost tego zakazuje.

## Kontekst jest warunkiem sensowności

PRI-01 rozdz. 3: „wyników nie porównuje się poza kontekstem użycia". ``priority_context_id``
zapisuje fakt o chwili kwalifikacji — bez niego zapisany priorytet nie znaczy nic i nie
da się tego naprawić po fakcie. Dlatego pole wchodzi do kontraktu teraz, mimo że żaden
kod go jeszcze nie wypełnia.

## Czego tu nie ma

Pól opisowych: ``problem_priority_basis``, ``validation_priority_basis``,
``cluster_priority_basis_summary``, ``cluster_basis``, ``impact_overlap_basis``.
To uzasadnienia tekstowe — rekonstruowalne, więc dokładamy je razem z implementacją
PRI-01. Zostają natomiast pola statusu wystarczalności podstawy, bo one należą do
kwalifikacji, a nie do jej opisu.
"""

import datetime as dt
from typing import Self

from pydantic import BaseModel, ConfigDict, model_validator

from xray.model.enums import (
    ManagementAttentionRoute,
    PriorityBasisStatus,
    ProblemPriorityAction,
    ValidationPriorityAction,
)
from xray.model.findings.identity import CONTRACT_VERSION
from xray.model.findings.refs import PeriodRef, ScopeRef


class PriorityRecord(BaseModel):
    """Pojedyncza kwalifikacja priorytetu dla jednego wyniku w jednym kontekście.

    Tożsamość wg ZOP-PRI-01 rozdz. 3: ``finding_id + priority_context_id +
    priority_evaluation_date + priority_basis_version``.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    # --- tożsamość kwalifikacji ------------------------------------------------------
    finding_id: str
    """Wynik, którego dotyczy kwalifikacja."""

    priority_context_id: str
    """Kontekst użycia. „Wyników nie porównuje się poza kontekstem użycia"."""

    priority_evaluation_date: dt.date
    """Data wykonania kwalifikacji."""

    priority_basis_version: str
    """Wersja podstawy kwalifikacji. Zmiana tworzy nową ewaluację, nie nadpisuje."""

    contract_version: str = CONTRACT_VERSION

    # --- kontekst --------------------------------------------------------------------
    priority_scope: ScopeRef | None = None
    priority_period: PeriodRef | None = None
    priority_decision_context: str | None = None
    """Decyzja, wobec której oceniany jest priorytet."""

    # --- wynik kwalifikacji (katalogi zamknięte, ZOP-PRI-01 rozdz. 8) ----------------
    problem_priority_action: ProblemPriorityAction | None = None
    """Kolejność uwagi zarządczej wobec samego problemu."""

    problem_priority_basis_status: PriorityBasisStatus | None = None
    """Wystarczalność podstawy kwalifikacji problemu (PRI-01 pkt 8.1)."""

    validation_priority_action: ValidationPriorityAction | None = None
    """Pilność uzupełnienia, uzgodnienia lub weryfikacji informacji."""

    management_attention_route: ManagementAttentionRoute | None = None
    """Syntetyczna trasa dalszego postępowania, bez decyzji wykonawczej."""

    @model_validator(mode="after")
    def _check_basis_status(self) -> Self:
        """``insufficient`` prowadzi do ``not_assessable``, i tylko do niego.

        ZOP-PRI-01 pkt 8.1: „Pierwsze cztery działania wymagają sufficient; insufficient
        prowadzi do not_assessable". To jedyne miejsce, w którym ta reguła jest
        egzekwowana — jest deterministyczna i nie wprowadza żadnego progu.
        """
        if (
            self.problem_priority_basis_status is PriorityBasisStatus.INSUFFICIENT
            and self.problem_priority_action is not None
            and self.problem_priority_action is not ProblemPriorityAction.NOT_ASSESSABLE
        ):
            raise ValueError(
                "problem_priority_basis_status=insufficient dopuszcza wyłącznie "
                f"problem_priority_action=not_assessable, podano "
                f"{self.problem_priority_action.value}"
            )
        return self


class ClusterPriorityRecord(BaseModel):
    """Kwalifikacja priorytetu dla klastra powiązanych wyników.

    Pola z ZOP-PRI-01 v1.0 pkt 5.3, wiersz ``cluster_priority_record``.

    Klaster istnieje po to, żeby ta sama złotówka nie zwiększyła priorytetu wielokrotnie:
    „Jeżeli trzy testy opisują ten sam zakres i mechanizm ekonomiczny, jedna wartość może
    być primary_impact, a pozostałe są supporting_evidence albo non_additive_context.
    PRI-01 nie sumuje trzech wartości."

    Klaster **nie oznacza wspólnej przyczyny** (PRI-01 pkt 5.3). Powiązanie wyników to
    nie wspólny mechanizm.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    finding_cluster_id: str
    """Identyfikator grupy powiązanych wyników."""

    cluster_priority_action: ProblemPriorityAction | None = None
    cluster_validation_priority_action: ValidationPriorityAction | None = None
    cluster_management_attention_route: ManagementAttentionRoute | None = None

    primary_impact_finding_id: str | None = None
    """Wynik wskazany jako główna podstawa wpływu.

    Tylko on może wejść do podstawy ekonomicznej klastra. Pozostałe wyniki klastra są
    dowodem wspierającym albo kontekstem nieaddytywnym.
    """

    impact_group_id: str | None = None
    """Grupa wpływu chroniona przed podwójnym liczeniem."""

    contract_version: str = CONTRACT_VERSION
