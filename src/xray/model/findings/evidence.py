# Implementuje ZOP-CONF-01 v1.0 rozdz. 4 (kontrakt dowodu) i pkt 4.1 (role dowodów).
"""Rekord dowodowy i jego powiązanie z twierdzeniem.

## Dlaczego dowód nie jest polem tekstowym w wyniku

ZOP-CONF-01 rozdz. 4 czyni z dowodu osobny byt z rolą, grupą i grupą źródła. Rola
rozstrzyga o sile wsparcia (pkt 4.1: ``supporting_evidence`` „nie działa jak kolejny głos
ani samodzielna podstawa, gdy wymagany jest primary_evidence"), a ``evidence_source_group_id``
chroni niezależność: CONF-01 rozdz. 9 — „Dwa źródła nie oznaczają automatycznie
well_supported". Tekstowy opis dowodu nie pozwoliłby tego sprawdzić.

## Kardynalność: wiele-do-wielu przez jawne powiązanie

CONF-01 definiuje ``evidence_id``, ale **nigdzie nie nazywa pola wiążącego dowód
z twierdzeniem** — patrz docs/otwarte-kontrakty.md wpis B-05.

DECYZJA (Michał, 2026-09-05), wpis B-05: relacja wiele-do-wielu zostaje jako architektura
bazowa. Dokładny kontrakt dowód–twierdzenie zostanie domknięty razem z implementacją
ZOP-CONF-01; architektura nie podlega wtedy ponownemu otwarciu.

Modelujemy relację jako wiele-do-wielu, przez ``ClaimEvidenceLink``, a nie przez
własność. Uzasadnienie jest asymetryczne: wiele-do-wielu degraduje się do jeden-do-wielu
bez żadnej zmiany kodu — relacja po prostu nigdy nie ma więcej niż jednego wiązania.
Odwrotnie się nie da. Przy nierozstrzygniętej karcie wybieramy wariant, który przetrwa
oba rozstrzygnięcia.

Dodatkowy argument merytoryczny: gdyby dowód należał na własność do jednego twierdzenia,
ten sam dowód użyty przy dwóch twierdzeniach trzeba by zduplikować — a wtedy
``evidence_source_group_id`` przestałby odróżniać duplikat od dwóch niezależnych źródeł,
czyli straciłby swoją jedyną funkcję.
"""

from typing import Any, Self

from pydantic import BaseModel, ConfigDict, model_validator

from xray.model.enums import EvidenceIndependenceStatus, EvidenceRole
from xray.model.findings.identity import (
    CONTRACT_VERSION,
    IDENTITY_ALGORITHM_VERSION,
    compute_id,
)
from xray.model.findings.refs import PeriodRef, ScopeRef

_EVIDENCE_PREFIX = "EVD"
_LINK_PREFIX = "LNK"


class EvidenceRecord(BaseModel):
    """Pojedynczy rekord dowodowy. Pola z ZOP-CONF-01 v1.0 rozdz. 4."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    evidence_id: str
    """Jednoznaczny identyfikator rekordu dowodowego."""

    evidence_type: str
    """Rodzaj informacji lub wyniku stanowiącego dowód."""

    evidence_source: str
    """Źródło z zachowaniem identyfikatora i wersji.

    CONF-01 wymaga wersji źródła: ten sam raport w dwóch wydaniach to dwa różne dowody.
    """

    evidence_scope: ScopeRef | None = None
    """Zakres objęty dowodem."""

    evidence_period: PeriodRef | None = None
    """Okres objęty dowodem."""

    evidence_group_id: str | None = None
    """Grupa rekordów opisujących ten sam dowód lub zdarzenie.

    Pole zapisuje fakt o chwili zapisu — po fakcie nie da się odtworzyć, że dwa rekordy
    opisywały to samo zdarzenie.
    """

    evidence_source_group_id: str | None = None
    """Grupa wspólnego źródła, używana do ochrony niezależności.

    Wspólne pochodzenie dowodów jest faktem o momencie zapisu; po fakcie nie da się go
    odtworzyć, a bez niego „dwa źródła" nie różnią się od dwóch niezależnych źródeł.
    Dlatego pole wchodzi do kontraktu teraz, mimo że żaden kod go jeszcze nie wypełnia.
    """

    evidence_independence_status: EvidenceIndependenceStatus | None = None
    """Status niezależności pochodzenia (ZOP-PRI-01 pkt 5.2)."""

    evidence_traceability_status: str | None = None
    """Status możliwości prześledzenia dowodu do źródła i transformacji."""

    contract_version: str = CONTRACT_VERSION

    identity_algorithm_version: str = IDENTITY_ALGORITHM_VERSION
    """Wersja algorytmu, którym policzono identyfikator. Składnik tożsamości."""

    @classmethod
    def identity_of(
        cls,
        *,
        evidence_type: str,
        evidence_source: str,
        evidence_scope: ScopeRef | None = None,
        evidence_period: PeriodRef | None = None,
        contract_version: str = CONTRACT_VERSION,
        identity_algorithm_version: str = IDENTITY_ALGORITHM_VERSION,
    ) -> dict[str, Any]:
        """Krotka tożsamości dowodu."""
        return {
            "evidence_type": evidence_type,
            "evidence_source": evidence_source,
            "evidence_scope": (
                evidence_scope.model_dump(mode="python") if evidence_scope else None
            ),
            "evidence_period": (
                evidence_period.model_dump(mode="python") if evidence_period else None
            ),
            "contract_version": contract_version,
            "identity_algorithm_version": identity_algorithm_version,
        }

    @classmethod
    def create(
        cls,
        *,
        evidence_type: str,
        evidence_source: str,
        evidence_scope: ScopeRef | None = None,
        evidence_period: PeriodRef | None = None,
        contract_version: str = CONTRACT_VERSION,
        identity_algorithm_version: str = IDENTITY_ALGORITHM_VERSION,
        **pola: Any,
    ) -> "EvidenceRecord":
        """Buduje dowód z wyliczonym deterministycznie identyfikatorem."""
        identity = cls.identity_of(
            evidence_type=evidence_type,
            evidence_source=evidence_source,
            evidence_scope=evidence_scope,
            evidence_period=evidence_period,
            contract_version=contract_version,
            identity_algorithm_version=identity_algorithm_version,
        )
        return cls(
            evidence_id=compute_id(
                _EVIDENCE_PREFIX,
                identity,
                algorithm_version=identity_algorithm_version,
            ),
            evidence_type=evidence_type,
            evidence_source=evidence_source,
            evidence_scope=evidence_scope,
            evidence_period=evidence_period,
            contract_version=contract_version,
            identity_algorithm_version=identity_algorithm_version,
            **pola,
        )

    @model_validator(mode="after")
    def _check_identity(self) -> Self:
        expected = compute_id(
            _EVIDENCE_PREFIX,
            self.identity_of(
                evidence_type=self.evidence_type,
                evidence_source=self.evidence_source,
                evidence_scope=self.evidence_scope,
                evidence_period=self.evidence_period,
                contract_version=self.contract_version,
                identity_algorithm_version=self.identity_algorithm_version,
            ),
            algorithm_version=self.identity_algorithm_version,
        )
        if self.evidence_id != expected:
            raise ValueError(
                f"evidence_id nie zgadza się z krotką tożsamości; oczekiwano {expected}. "
                "Rekord buduj przez EvidenceRecord.create"
            )
        return self


class ClaimEvidenceLink(BaseModel):
    """Powiązanie dowodu z konkretną wersją twierdzenia.

    Rola dowodu należy do **powiązania**, a nie do dowodu: ten sam rekord dowodowy może
    być dowodem głównym dla jednego twierdzenia i kontekstem dla drugiego. CONF-01
    pkt 4.1 opisuje role jako relację wobec twierdzenia, nie jako właściwość dowodu.

    Powiązanie wskazuje twierdzenie razem z jego wersją, bo wersja jest składnikiem
    tożsamości twierdzenia — dowód przypisany do wersji 1 nie przechodzi automatycznie
    na wersję 2, tak samo jak nie przechodzi klasa pewności.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    link_id: str
    claim_id: str
    claim_version: int
    evidence_id: str

    evidence_role: EvidenceRole
    """Rola tego dowodu wobec tego twierdzenia (CONF-01 pkt 4.1)."""

    contract_version: str = CONTRACT_VERSION

    identity_algorithm_version: str = IDENTITY_ALGORITHM_VERSION
    """Wersja algorytmu, którym policzono identyfikator. Składnik tożsamości."""

    @classmethod
    def identity_of(
        cls,
        *,
        claim_id: str,
        claim_version: int,
        evidence_id: str,
        evidence_role: EvidenceRole,
        contract_version: str = CONTRACT_VERSION,
        identity_algorithm_version: str = IDENTITY_ALGORITHM_VERSION,
    ) -> dict[str, Any]:
        return {
            "claim_id": claim_id,
            "claim_version": claim_version,
            "evidence_id": evidence_id,
            "evidence_role": evidence_role.value,
            "contract_version": contract_version,
            "identity_algorithm_version": identity_algorithm_version,
        }

    @classmethod
    def create(
        cls,
        *,
        claim_id: str,
        claim_version: int,
        evidence_id: str,
        evidence_role: EvidenceRole,
        contract_version: str = CONTRACT_VERSION,
        identity_algorithm_version: str = IDENTITY_ALGORITHM_VERSION,
    ) -> "ClaimEvidenceLink":
        identity = cls.identity_of(
            claim_id=claim_id,
            claim_version=claim_version,
            evidence_id=evidence_id,
            evidence_role=evidence_role,
            contract_version=contract_version,
            identity_algorithm_version=identity_algorithm_version,
        )
        return cls(
            link_id=compute_id(
                _LINK_PREFIX, identity, algorithm_version=identity_algorithm_version
            ),
            claim_id=claim_id,
            claim_version=claim_version,
            evidence_id=evidence_id,
            evidence_role=evidence_role,
            contract_version=contract_version,
            identity_algorithm_version=identity_algorithm_version,
        )

    @model_validator(mode="after")
    def _check_identity(self) -> Self:
        expected = compute_id(
            _LINK_PREFIX,
            self.identity_of(
                claim_id=self.claim_id,
                claim_version=self.claim_version,
                evidence_id=self.evidence_id,
                evidence_role=self.evidence_role,
                contract_version=self.contract_version,
                identity_algorithm_version=self.identity_algorithm_version,
            ),
            algorithm_version=self.identity_algorithm_version,
        )
        if self.link_id != expected:
            raise ValueError(
                f"link_id nie zgadza się z krotką tożsamości; oczekiwano {expected}. "
                "Rekord buduj przez ClaimEvidenceLink.create"
            )
        return self
