# Implementuje ZOP-TECH-01 v0.1 pkt 5.4 (struktura FINDINGS), z korektami z wpisów
# B-02 i B-03 oraz polami ochrony wpływu z ZOP-PRI-01 v1.0 rozdz. 5.
"""Rdzeń struktury FINDINGS — pojedynczy wynik diagnostyczny.

To jedyne miejsce zapisu wyników. Nikt nie liczy niczego obok.

## Zakres kontraktu na tym etapie (wariant B)

Kryterium przyjęcia pola: **czy jego wartość da się odtworzyć po fakcie.**

Wchodzą teraz wszystkie pola zapisujące kontekst chwili zapisu — tożsamość, wersja
kontraktu, przynależność do grupy wpływu, rola w rozliczeniu wpływu — nawet jeżeli żaden
kod ich jeszcze nie wypełnia. Ich nieobecność nie byłaby brakiem funkcji, tylko trwałą
utratą informacji: rekordom zapisanym bez nich trzeba by później przypisać wartość,
której nie mamy podstaw wypowiedzieć.

Zostają na później pola czysto opisowe — uzasadnienia, podsumowania, listy dopuszczalnych
ograniczeń. Te są rekonstruowalne albo nieistotne wstecz.

## Czego tu nie ma

Klas pewności per poziom (miara / wynik / mechanizm) — te mieszkają w ``ClaimRecord``,
bo ZOP-CONF-01 pkt 2.1 zakazuje przenoszenia klasy między poziomami, a jedna kolumna nie
pomieści trzech ocen, które z założenia mogą się różnić.
"""

from typing import Any, Self

from pydantic import BaseModel, ConfigDict, model_validator

from xray.model.enums import (
    ConfidenceClass,
    ConfidenceSourceLevel,
    ImpactAccountingRole,
    LogicalStatus,
)
from xray.model.findings.identity import (
    CONTRACT_VERSION,
    IDENTITY_ALGORITHM_VERSION,
    compute_id,
)
from xray.model.findings.refs import PeriodRef, ReferenceRef, ScopeRef

_ID_PREFIX = "FND"


class FindingRecord(BaseModel):
    """Pojedynczy wynik diagnostyczny zapisany przez test.

    Tożsamość: ``test_id + scope + period + contract_version``. Identyfikator jest z niej
    wyliczany deterministycznie, a rekord sprawdza przy powstaniu, że się zgadza — dzięki
    temu nie da się zapisać rekordu, którego identyfikator nie prowadzi do jego własnych
    składników.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    # --- tożsamość ------------------------------------------------------------------
    finding_id: str
    """Deterministyczny identyfikator. Buduj przez ``FindingRecord.create``."""

    test_id: str
    """Kod testu, np. ``"FIN-01"``. Składnik tożsamości."""

    scope: ScopeRef
    """Zakres analizy. Składnik tożsamości — patrz ``ScopeRef``."""

    period: PeriodRef
    """Okres wyniku. Składnik tożsamości."""

    contract_version: str = CONTRACT_VERSION
    """Wersja kontraktu FINDINGS. Składnik tożsamości.

    Zmiana kontraktu produkuje nowe identyfikatory zamiast po cichu nadpisywać stare
    rekordy inną treścią.
    """

    identity_algorithm_version: str = IDENTITY_ALGORITHM_VERSION
    """Wersja algorytmu, którym policzono identyfikator. Składnik tożsamości.

    Przy sprawdzaniu przeliczamy skrót algorytmem wskazanym przez **rekord**, a nie
    bieżącym — dzięki temu zmiana algorytmu nie zamienia poprawnych starych rekordów
    w rzekomo uszkodzone.
    """


    # --- treść wyniku (ZOP-TECH-01 pkt 5.4) -----------------------------------------
    status: LogicalStatus
    """Status logiczny testu.

    # DECYZJA (Michał, 2026-09-05), wpis B-02: pole niesie status logiczny testu.
    # Słownik STANDARD / MEDIUM / HIGH / CRITICAL z ZOP-TECH-01 pkt 5.4 jest zapisem
    # historycznym i został wycofany — nie implementujemy go jako priorytetu. Priorytet
    # mieszka w PriorityRecord wg ZOP-PRI-01.
    """

    finding: str
    """Komunikat faktograficzny o wykrytym zjawisku. Bez tezy o przyczynie."""

    metric_value: float | None = None
    """Wartość badanego wskaźnika. ``None`` jest poprawnym wynikiem."""

    reference: ReferenceRef | None = None
    """Wartość odniesienia wraz z pochodzeniem (FIN-01 pkt 6.1).

    ``None`` oznacza brak referencji — wtedy ``gap``, ``impact_low`` i ``impact_high``
    również pozostają ``None``, a ograniczenie trafia do ``validation_notes``.
    """

    gap: float | None = None
    """Luka ekonomiczna względem przyjętej relacji referencyjnej.

    FIN-01 pkt 12.1: gap to „luka ekonomiczna względem przyjętej relacji referencyjnej",
    nigdy „oszczędność" ani „potencjał".
    """

    impact_low: float | None = None
    """Dolna granica odpowiedzialnego przedziału wpływu ekonomicznego."""

    impact_high: float | None = None
    """Górna granica odpowiedzialnego przedziału wpływu ekonomicznego."""

    next_tests: tuple[str, ...] = ()
    """Kolejne testy sugerowane przez ścieżkę diagnostyczną. Pusta krotka = brak."""

    validation_required: bool = False
    """Czy wniosek wymaga ręcznej weryfikacji."""

    validation_notes: tuple[str, ...] = ()
    """Ograniczenia i ostrzeżenia walidacji mające wpływ na ten wynik."""

    # --- pewność (projekcja; wartości mieszkają w ClaimRecord) -----------------------
    confidence_score: None = None
    """Zawsze ``None``.

    ZOP-CONF-01 pkt 2.2 zawiera dosłowny zakaz: „confidence_score = null. CONF-01 nie
    tworzy wyniku 0–100, wag, średniej ważonej, arbitralnych progów ani katalogu
    HIGH/MEDIUM/LOW". Pole istnieje w strukturze, bo wymienia je ZOP-TECH-01 pkt 5.4,
    ale typ dopuszcza wyłącznie ``None`` — inna wartość nie przejdzie walidacji.
    """

    confidence_class: ConfidenceClass | None = None
    """Klasa pewności przeniesiona z twierdzenia.

    # DECYZJA (Michał, 2026-09-05), wpis B-03: klas „A / B / C" z ZOP-TECH-01 pkt 5.4
    # nie implementujemy. Obowiązuje katalog z CONF-01 pkt 2.2, a rozdzielenie pewności
    # na miarę, wynik i mechanizm zostaje w ClaimRecord. Pole pozostaje `None`
    # do czasu implementacji CONF-01.
    """

    confidence_class_source_level: ConfidenceSourceLevel | None = None
    """Poziom, z którego pochodzi ``confidence_class``.

    CONF-01: „confidence_class przekazywana dalej musi odpowiadać
    confidence_class_source_level. Nie wolno przepisywać klasy z jednego poziomu na
    drugi". Bez tego pola przeniesiona klasa nie miałaby jak powiedzieć, czego dotyczy.
    """

    # --- ochrona wpływu i klaster (ZOP-PRI-01 v1.0 rozdz. 5) ------------------------
    impact_group_id: str | None = None
    """Identyfikator grupy wpływu — „ta sama złotówka, luka lub skutek nie zwiększa
    priorytetu wielokrotnie" (PRI-01 rozdz. 5).

    Pole wchodzi do kontraktu teraz, mimo że żaden kod go nie wypełnia: bez niego nie da
    się **wstecz** ustalić, które wyniki opisywały ten sam wpływ, więc ochrona przed
    podwójnym liczeniem przestałaby działać na danych historycznych.
    """

    impact_accounting_role: ImpactAccountingRole | None = None
    """Rola wyniku w rozliczeniu wpływu. Tylko poprawnie wskazany ``primary_impact``
    może wejść do podstawy ekonomicznej (PRI-01 rozdz. 5)."""

    finding_cluster_id: str | None = None
    """Przynależność do klastra powiązanych wyników.

    PRI-01 pkt 5.3: klaster „nie oznacza wspólnej przyczyny".
    """

    # --- spójność tożsamości ---------------------------------------------------------

    @classmethod
    def identity_of(
        cls,
        *,
        test_id: str,
        scope: ScopeRef,
        period: PeriodRef,
        contract_version: str = CONTRACT_VERSION,
        identity_algorithm_version: str = IDENTITY_ALGORITHM_VERSION,
    ) -> dict[str, Any]:
        """Zwraca krotkę tożsamości wyniku w postaci nadającej się do skrótu."""
        return {
            "test_id": test_id,
            "scope": scope.model_dump(mode="python"),
            "period": period.model_dump(mode="python"),
            "contract_version": contract_version,
            "identity_algorithm_version": identity_algorithm_version,
        }

    @classmethod
    def create(
        cls,
        *,
        test_id: str,
        scope: ScopeRef,
        period: PeriodRef,
        contract_version: str = CONTRACT_VERSION,
        identity_algorithm_version: str = IDENTITY_ALGORITHM_VERSION,
        **pola: Any,
    ) -> "FindingRecord":
        """Buduje wynik z wyliczonym deterministycznie identyfikatorem.

        Jedyna droga tworzenia rekordu w kodzie produkcyjnym. Konstruktor pozostaje
        dostępny, bo musi działać przy odczycie z magazynu — ale wtedy identyfikator
        jest już znany i sprawdzany.
        """
        identity = cls.identity_of(
            test_id=test_id,
            scope=scope,
            period=period,
            contract_version=contract_version,
            identity_algorithm_version=identity_algorithm_version,
        )
        return cls(
            finding_id=compute_id(
                _ID_PREFIX, identity, algorithm_version=identity_algorithm_version
            ),
            test_id=test_id,
            scope=scope,
            period=period,
            contract_version=contract_version,
            identity_algorithm_version=identity_algorithm_version,
            **pola,
        )

    @model_validator(mode="after")
    def _check_identity(self) -> Self:
        """Sprawdza, że identyfikator prowadzi do własnych składników rekordu.

        Bez tego identyfikator byłby dowolnym napisem, a ślad audytowy urwałby się
        w miejscu, w którym miał się zaczynać.
        """
        expected = compute_id(
            _ID_PREFIX,
            self.identity_of(
                test_id=self.test_id,
                scope=self.scope,
                period=self.period,
                contract_version=self.contract_version,
                identity_algorithm_version=self.identity_algorithm_version,
            ),
            algorithm_version=self.identity_algorithm_version,
        )
        if self.finding_id != expected:
            raise ValueError(
                f"finding_id nie zgadza się z krotką tożsamości; oczekiwano {expected}. "
                "Rekord buduj przez FindingRecord.create"
            )
        return self

    @model_validator(mode="after")
    def _check_reference_consistency(self) -> Self:
        """Bez referencji nie ma luki ani wpływu.

        ZOP-XR-FIN-01 rozdz. 6: „FIN-01 może opisać trend i dekompozycję, ale nie
        wyznacza Gap. Pola gap, impact_low i impact_high pozostają null, a ograniczenie
        trafia do validation_notes". Ta sama zasada obowiązuje w PORT-01 pkt 13.1
        i FIN-03 rozdz. 14 — luka bez referencji byłaby liczbą bez znaczenia.
        """
        if self.reference is None:
            puste = [
                nazwa
                for nazwa, wartosc in (
                    ("gap", self.gap),
                    ("impact_low", self.impact_low),
                    ("impact_high", self.impact_high),
                )
                if wartosc is not None
            ]
            if puste:
                raise ValueError(
                    f"brak referencji, a pola {', '.join(puste)} mają wartość; "
                    "bez wartości odniesienia luka i wpływ pozostają null"
                )
        return self
