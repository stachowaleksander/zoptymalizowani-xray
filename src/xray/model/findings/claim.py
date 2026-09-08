# Implementuje ZOP-CONF-01 v1.0 rozdz. 3 (kontrakt twierdzenia diagnostycznego).
"""Twierdzenie diagnostyczne poddawane ocenie pewności.

## Dlaczego to osobny rekord, a nie kolumny w FINDINGS

ZOP-CONF-01 pkt 2.1 rozdziela pewność na trzy niezależne poziomy — miara, wynik,
mechanizm — i zakazuje przenoszenia klasy między nimi (QCONF01-183: „Klasa nie jest
kopiowana automatycznie między poziomami"). Karta podaje wprost przykład rozdzielenia:
``metric_confidence_class = well_supported``, ``finding_confidence_class =
well_supported``, ``mechanism_confidence_class = weakly_supported``.

Jedna kolumna ``confidence_class`` w FINDINGS nie pomieści trzech ocen, które
z założenia mogą się różnić. Jeden wynik daje więc od zera do wielu twierdzeń.

## Wersja jest częścią tożsamości, nie opisem

CONF-01 rozdz. 3: „claim_version — wersja treści twierdzenia; zmiana treści tworzy nową
wersję" oraz „Jedna ocena CONF-01 dotyczy jednego claim_id, claim_type, claim_scope,
claim_period i confidence_context. Rozszerzenie zakresu, zmiana okresu albo zmiana treści
nie dziedziczą automatycznie wcześniejszej klasy".

Wersjonowanie **zachowuje** poprzednią wersję jako osobny, rozróżnialny rekord — na tym
polega jego sens. Bez wersji w tożsamości nie dałoby się rozstrzygnąć, czy zapisana klasa
pewności nadal dotyczy aktualnej treści twierdzenia, więc zakaz dziedziczenia klasy
stałby się deklaracją bez mechanizmu.
"""

from typing import Any, Self

from pydantic import BaseModel, ConfigDict, model_validator

from xray.model.enums import ClaimType, ConfidenceClass, ConfidenceSourceLevel
from xray.model.findings.identity import (
    CONTRACT_VERSION,
    IDENTITY_ALGORITHM_VERSION,
    compute_id,
)
from xray.model.findings.refs import PeriodRef, ScopeRef

_ID_PREFIX = "CLM"

# Który poziom pewności odpowiada któremu rodzajowi twierdzenia.
# Źródło: ZOP-CONF-01 v1.0 rozdz. 3, tabela claim_type → confidence_class_source_level.
_LEVEL_FOR_TYPE: dict[ClaimType, ConfidenceSourceLevel] = {
    ClaimType.METRIC_CLAIM: ConfidenceSourceLevel.METRIC_CONFIDENCE,
    ClaimType.FINDING_CLAIM: ConfidenceSourceLevel.FINDING_CONFIDENCE,
    ClaimType.MECHANISM_CLAIM: ConfidenceSourceLevel.MECHANISM_CONFIDENCE,
}


class ClaimRecord(BaseModel):
    """Pojedyncze twierdzenie diagnostyczne w jednej wersji.

    Tożsamość: ``claim_type + claim_scope + claim_period + confidence_context +
    claim_version + contract_version``, uzupełniona o test źródłowy.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    # --- tożsamość ------------------------------------------------------------------
    claim_id: str
    """Trwały identyfikator twierdzenia. Buduj przez ``ClaimRecord.create``."""

    claim_type: ClaimType
    """Poziom twierdzenia: miara, wynik albo mechanizm. Składnik tożsamości."""

    claim_scope: ScopeRef
    """Zakres, którego dotyczy twierdzenie. Składnik tożsamości."""

    claim_period: PeriodRef
    """Okres właściwy dla twierdzenia. Składnik tożsamości."""

    confidence_context: str
    """Kontekst użycia, w którym oceniana jest siła wsparcia. Składnik tożsamości.

    CONF-01 rozdz. 3 czyni go wymaganym: ta sama treść oceniana w innym kontekście
    użycia jest innym twierdzeniem, nie tym samym.
    """

    claim_version: int = 1
    """Wersja treści twierdzenia. Składnik tożsamości, nie opis.

    Zmiana treści tworzy **nową wersję**, a poprzednia zostaje jako osobny rekord.
    """

    contract_version: str = CONTRACT_VERSION

    identity_algorithm_version: str = IDENTITY_ALGORITHM_VERSION
    """Wersja algorytmu, którym policzono identyfikator. Składnik tożsamości."""

    # --- powiązania -----------------------------------------------------------------
    claim_source_test: str
    """Identyfikator testu źródłowego."""

    claim_source_finding_id: str | None = None
    """Wynik źródłowy, jeżeli twierdzenie powstało z FINDINGS (CONF-01: conditional)."""

    # --- treść ----------------------------------------------------------------------
    claim_text: str
    """Oryginalna treść ocenianego twierdzenia.

    CONF-01 rozdz. 3: „nie jest nadpisywana przy zawężeniu". Zawężenie twierdzenia
    tworzy nową wersję z własną treścią, a nie modyfikuje tej.
    """

    # --- ocena pewności --------------------------------------------------------------
    confidence_score: None = None
    """Zawsze ``None`` — ZOP-CONF-01 pkt 2.2 („ZAKAZ WSKAŹNIKA")."""

    confidence_class: ConfidenceClass | None = None
    """Klasa pewności tego twierdzenia. ``None`` do czasu implementacji CONF-01."""

    confidence_class_source_level: ConfidenceSourceLevel | None = None
    """Poziom, z którego pochodzi klasa. Musi odpowiadać ``claim_type``."""

    # --- spójność --------------------------------------------------------------------

    @classmethod
    def identity_of(
        cls,
        *,
        claim_type: ClaimType,
        claim_scope: ScopeRef,
        claim_period: PeriodRef,
        confidence_context: str,
        claim_source_test: str,
        claim_version: int = 1,
        contract_version: str = CONTRACT_VERSION,
        identity_algorithm_version: str = IDENTITY_ALGORITHM_VERSION,
    ) -> dict[str, Any]:
        """Krotka tożsamości twierdzenia."""
        return {
            "claim_type": claim_type.value,
            "claim_scope": claim_scope.model_dump(mode="python"),
            "claim_period": claim_period.model_dump(mode="python"),
            "confidence_context": confidence_context,
            "claim_source_test": claim_source_test,
            "claim_version": claim_version,
            "contract_version": contract_version,
            "identity_algorithm_version": identity_algorithm_version,
        }

    @classmethod
    def create(
        cls,
        *,
        claim_type: ClaimType,
        claim_scope: ScopeRef,
        claim_period: PeriodRef,
        confidence_context: str,
        claim_source_test: str,
        claim_version: int = 1,
        contract_version: str = CONTRACT_VERSION,
        identity_algorithm_version: str = IDENTITY_ALGORITHM_VERSION,
        **pola: Any,
    ) -> "ClaimRecord":
        """Buduje twierdzenie z wyliczonym deterministycznie identyfikatorem."""
        identity = cls.identity_of(
            claim_type=claim_type,
            claim_scope=claim_scope,
            claim_period=claim_period,
            confidence_context=confidence_context,
            claim_source_test=claim_source_test,
            claim_version=claim_version,
            contract_version=contract_version,
            identity_algorithm_version=identity_algorithm_version,
        )
        return cls(
            claim_id=compute_id(
                _ID_PREFIX, identity, algorithm_version=identity_algorithm_version
            ),
            claim_type=claim_type,
            claim_scope=claim_scope,
            claim_period=claim_period,
            confidence_context=confidence_context,
            claim_source_test=claim_source_test,
            claim_version=claim_version,
            contract_version=contract_version,
            identity_algorithm_version=identity_algorithm_version,
            **pola,
        )

    @model_validator(mode="after")
    def _check_identity(self) -> Self:
        expected = compute_id(
            _ID_PREFIX,
            self.identity_of(
                claim_type=self.claim_type,
                claim_scope=self.claim_scope,
                claim_period=self.claim_period,
                confidence_context=self.confidence_context,
                claim_source_test=self.claim_source_test,
                claim_version=self.claim_version,
                contract_version=self.contract_version,
                identity_algorithm_version=self.identity_algorithm_version,
            ),
            algorithm_version=self.identity_algorithm_version,
        )
        if self.claim_id != expected:
            raise ValueError(
                f"claim_id nie zgadza się z krotką tożsamości; oczekiwano {expected}. "
                "Rekord buduj przez ClaimRecord.create"
            )
        return self

    @model_validator(mode="after")
    def _check_level_matches_type(self) -> Self:
        """Poziom klasy pewności musi odpowiadać rodzajowi twierdzenia.

        CONF-01: „confidence_class przekazywana dalej musi odpowiadać
        confidence_class_source_level. Nie wolno przepisywać klasy z jednego poziomu
        na drugi". Ta kontrola jest jedynym mechanizmem, który to egzekwuje.
        """
        oczekiwany = _LEVEL_FOR_TYPE[self.claim_type]
        if (
            self.confidence_class_source_level is not None
            and self.confidence_class_source_level is not oczekiwany
        ):
            raise ValueError(
                f"twierdzenie {self.claim_type.value} nie może nieść klasy z poziomu "
                f"{self.confidence_class_source_level.value}; oczekiwano "
                f"{oczekiwany.value}"
            )
        if self.confidence_class is not None and self.confidence_class_source_level is None:
            raise ValueError(
                "podano confidence_class bez confidence_class_source_level; "
                "klasa bez wskazania poziomu nie mówi, czego dotyczy"
            )
        return self
