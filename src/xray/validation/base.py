# Implementuje ZOP-TECH-01 v0.1 pkt 5.3 — kontrakt wtyczki kontroli danych.
"""Deklaracja kontroli i jej wspólna podstawa.

Kontrola jest wtyczką tak samo jak test diagnostyczny: deklaruje, czego wymaga i jak
mocny status wolno jej nadać. Dodanie kontroli to nowy plik plus wpis w rejestrze.

## Walidator ogłasza, nie blokuje

Walidator sam nic nie blokuje — ogłasza statusy. To test deklaruje, które kontrole są dla
niego wymagane i co oznacza ich CRITICAL (``TEST_BLOCKED`` / ``TEST_PARTIAL``).
"""

from abc import ABC, abstractmethod
from collections.abc import Mapping
from enum import StrEnum
from typing import Any, ClassVar, Self

from pydantic import BaseModel, ConfigDict, model_validator

from xray.model.enums import TimeGrain, ValidationStatus
from xray.model.tables.base import TableRecord
from xray.validation.context import ValidationContext
from xray.validation.results import CheckOutcome

SEVERITY: dict[ValidationStatus, int] = {
    ValidationStatus.PASS: 0,
    ValidationStatus.WARNING: 1,
    ValidationStatus.CRITICAL: 2,
}
"""Porządek surowości statusów.

Służy **wyłącznie** do sprawdzenia, czy kontrola nie przekroczyła zadeklarowanego limitu.
Nie jest skalą, po której wolno agregować, uśredniać ani sortować wyników.
"""


class Determines(StrEnum):
    """Czym dla kontroli jest różnica między parą pól."""

    STATUS = "status"
    """Bez tej różnicy kontrola nie ma czego ogłosić — cały wynik jest nieoznaczony.

    Kontrola 7: gdy ``available`` i ``used`` pochodzą z jednej kolumny klienta, są sobie
    zawsze równe, więc kontrola nigdy nie zgłosi sygnału i wypisze PASS przy każdym
    przebiegu. To **fałszywie przechodząca kontrola** — ta sama klasa błędu co w DT-07,
    tylko wpuszczona przez konfigurację zamiast przez kod.
    """

    OBSERVATION = "observation"
    """Różnica jest treścią obserwacji, ale nie warunkiem wykonania kontroli.

    Kontrola 8: gdy ``start`` i ``end`` pochodzą z jednej kolumny,
    ``months_with_stage_starts`` i ``months_with_stage_ends`` są trywialnie równe,
    a czytający wyciągnie wniosek „każdy etap kończy się w miesiącu, w którym się zaczął".
    Wniosek fałszywy i pochodzący z konfiguracji. Ale ``period_min``, ``period_max``
    i ``months_without_events`` pozostają prawdziwe, więc kasowanie całego wyniku
    odejmowałoby informację bez powodu.
    """


class ComparisonPair(BaseModel):
    """Para pól, których **różnica** niesie sygnał.

    Deklaruje kontrola, egzekwuje rejestr — tak samo jak przy ``max_status``
    i ``required_fields``. Heurystyka w rejestrze („dwa pola z jednego źródła")
    byłaby pierwszą regułą, której nikt nie zadeklarował, a przy tym zbyt szeroką:
    kontrola 6 pracuje w obrębie jednego pola i wspólne źródło jej nie psuje.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    fields: tuple[str, str]
    determines: Determines

    unaffected_measures: tuple[str, ...] = ()
    """Miary, których zlanie pary **nie** unieważnia, mimo że ich podmiotem jest pole pary.

    Lista **wyłączeń**, nie włączeń — i to jest istotne. Zapomniane wyłączenie odejmuje
    prawdziwą informację; zapomniane włączenie **zostawiłoby kłamstwo**. Domyślna
    ostrożność musi być po stronie zerowania, więc wyjątek trzeba zadeklarować, a nie
    regułę.

    Wyjątek kluczujemy po ``measure``, czyli po identyfikatorze miary, a nie po prozie.
    Sam wyjątek ma mieć podstawę w karcie — nie w wygodzie.
    """

    @model_validator(mode="after")
    def _check_pair(self) -> Self:
        if self.fields[0] == self.fields[1]:
            raise ValueError("para porównawcza musi wskazywać dwa różne pola")
        if self.unaffected_measures and self.determines is not Determines.OBSERVATION:
            raise ValueError(
                "wyłączenia miar mają sens tylko przy parze OBSERVATION; para STATUS "
                "unieważnia cały wynik, więc nie ma czego wyłączać"
            )
        return self


class CheckDeclaration(BaseModel):
    """Co kontrola wymaga i jak mocny status wolno jej nadać."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    check_id: str
    """Identyfikator kontroli, np. ``"TECH01-VAL-03"``."""

    control_number: int
    """Numer kontroli z ZOP-TECH-01 pkt 5.3 (1–8)."""

    title: str
    """Krótka nazwa, zgodna z brzmieniem z karty."""

    requires_import_report: bool = False
    """Czy kontrola potrzebuje wiedzy o imporcie.

    Sprawdzenie należy do **rejestru**, nie do kontroli: gdyby każda sprawdzała to sama,
    każda musiałaby powtarzać ten sam warunek i każda mogłaby go zapomnieć. Kontrola
    uruchomiona bez wymaganego wejścia nie liczy zera — nie jest uruchamiana wcale.
    """

    required_fields: tuple[str, ...] = ()
    """Pola, bez których kontrola nie ma sensu.

    Deklarujemy **pola, nie tabele**. Kontrola 7 dotyczy ``available`` i ``used``, a nie
    „tabeli RESOURCE"; gdyby rozszerzenie z karty wprowadziło te pola gdzie indziej,
    kontrola zadziała bez zmiany. Lista tabel byłaby zapisaniem dzisiejszego stanu jako
    reguły.
    """

    requires_natural_key: bool = False
    """Czy kontrola czyta ``NATURAL_KEY`` tabeli."""

    requires_time_fields: bool = False
    """Czy kontrola czyta ``TIME_FIELDS`` tabeli."""

    max_status: ValidationStatus = ValidationStatus.CRITICAL
    """Najmocniejszy status, jaki ta kontrola może nadać **samodzielnie**.

    Kontrole 5 (wartości podejrzane) i 7 (``used > available``) deklarują ``WARNING``:
    ich rozstrzygnięcie należy do karty, nie do fundamentu. ZOP-XR-CAP-01 rozdz. 5 mówi
    wprost, że przekroczenie „nie jest automatycznie błędem logicznym", a wariant CRITICAL
    pojawia się dopiero w CAP-01 VAL-13, które zna ``documented_extra_capacity``.

    Limit jest **egzekwowany** przez rejestr, a nie tylko opisany.
    """

    max_status_by_time_grain: Mapping[TimeGrain, ValidationStatus] = {}
    """Nadpisanie limitu dla tabel o danym ziarnie czasowym.

    Puste odwzorowanie znaczy „domyślny wszędzie".

    Modulujemy po **właściwości** tabeli, a nie po jej nazwie. Odwzorowanie
    ``{"PROCESS": PASS}`` mówiłoby która tabela, a nie dlaczego — i po cichu nadałoby
    WARNING drugiej tabeli zdarzeniowej, gdyby taka powstała. Rozstrzygnięcie A-01 nie
    mówi nic o nazwie „PROCESS": mówi o danych zdarzeniowych, w których miesiąca bez
    zdarzeń nie da się odróżnić od braku danych.
    """

    comparison_pairs: tuple[ComparisonPair, ...] = ()
    """Pary pól, których różnica niesie sygnał tej kontroli.

    Gdy oba pola pary pochodzą z **jednej kolumny klienta**, różnicy nie da się
    zobaczyć — i rejestr nie pozwala kontroli udawać, że ją zbadał. Skutek zależy
    od roli pary: ``STATUS`` unieważnia cały wynik, ``OBSERVATION`` zeruje dotknięte
    obserwacje.

    Para nieobecna w danej tabeli (np. ``start``/``end`` w tabeli okresowej) jest
    po prostu pomijana.
    """

    @model_validator(mode="after")
    def _check_declaration(self) -> Self:
        if not self.check_id.strip():
            raise ValueError("check_id nie może być pusty")
        if not self.title.strip():
            raise ValueError("title nie może być pusty")
        if not 1 <= self.control_number <= 8:
            raise ValueError(
                f"control_number {self.control_number} poza zakresem 1–8; "
                "ZOP-TECH-01 pkt 5.3 definiuje osiem kontroli"
            )
        return self

    def effective_max_status(self, table: type[TableRecord]) -> ValidationStatus:
        """Limit obowiązujący dla konkretnej tabeli."""
        return self.max_status_by_time_grain.get(table.TIME_GRAIN, self.max_status)

    def applies_to(self, table: type[TableRecord]) -> bool:
        """Czy kontrola ma sens dla tej tabeli."""
        pola = set(table.model_fields)
        if not set(self.required_fields) <= pola:
            return False
        if self.requires_natural_key and not table.NATURAL_KEY:
            return False
        if self.requires_time_fields and not table.TIME_FIELDS:
            return False
        return True


class DataCheck(ABC):
    """Wspólna podstawa wtyczek kontroli danych.

    Każda wtyczka musi zadeklarować ``DECLARATION``. Sprawdzenie odbywa się przy tworzeniu
    klasy — tak samo jak przy tabelach kontraktu i testach diagnostycznych.
    """

    DECLARATION: ClassVar[CheckDeclaration]

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        if "DECLARATION" not in cls.__dict__:
            raise TypeError(
                f"kontrola {cls.__name__} nie deklaruje DECLARATION; bez deklaracji "
                "rejestr nie wie, czego kontrola wymaga ani jak mocny status wolno jej "
                "nadać"
            )

    @abstractmethod
    def run(self, context: ValidationContext) -> CheckOutcome:
        """Wykonuje kontrolę na jednej tabeli.

        Zwraca ``CheckOutcome``, a nie pełny wynik: ``check_id`` i nazwy tabeli kontrola
        nie przepisuje, bo przepisywanie daje okazję do pomyłki. Składa je rejestr.
        """
