# Implementuje ZOP-XR-FIN-01 v1.0 pkt 2.1 (scope) i pkt 6.1 (zapis referencji).
"""Struktury opisujące zakres, okres i wartość odniesienia.

Te trzy rzeczy są w ZOP-TECH-01 pkt 5.4 pojedynczymi polami, ale karty wymagają od nich
więcej, niż zmieści napis.

``scope`` — ZOP-XR-FIN-01 pkt 2.1: „scope zapisuje filtry, populację jednostek, okres
i poziom agregacji". Napis tego nie pomieści w sposób audytowalny, a bez tego nie da się
odtworzyć, na jakim zbiorze policzono liczbę (zasada 4).

``reference_value`` — ZOP-XR-FIN-01 pkt 6.1 podaje pełny kontrakt zapisu referencji
w sześciu polach. Sama wartość odniesienia bez informacji, skąd pochodzi, nie prowadzi
do rekordów źródłowych.
"""

import datetime as dt

from pydantic import BaseModel, ConfigDict

from xray.model.enums import ReferenceType

_FROZEN = ConfigDict(extra="forbid", frozen=True)


class ScopeRef(BaseModel):
    """Zakres analizy, którego dotyczy wynik.

    Wchodzi do krotki tożsamości wyniku, więc to ta struktura rozróżnia wyniki
    policzone w jednym przebiegu: FIN-01 produkuje wyniki per jednostka i per kategoria,
    a bez tego rozróżnienia ich identyfikatory skleiłyby się w jeden.
    """

    model_config = _FROZEN

    scope_label: str
    """Czytelna nazwa zakresu, np. „cała firma", „Dział A", „usługa podstawowa"."""

    units: tuple[str, ...] = ()
    """Populacja jednostek objętych wynikiem. Pusta krotka oznacza brak zawężenia."""

    filters: tuple[tuple[str, str], ...] = ()
    """Filtry zastosowane przy liczeniu, jako uporządkowane pary pole–wartość.

    Krotka par, a nie odwzorowanie: kolejność musi być stabilna, bo ta struktura wchodzi
    do skrótu tożsamości. Odwzorowanie dałoby ten sam zakres w dwóch zapisach.
    """

    aggregation_level: str | None = None
    """Poziom agregacji, na którym policzono wynik (FIN-01 pkt 2.1)."""


class PeriodRef(BaseModel):
    """Okres, którego dotyczy wynik.

    Granice zapisujemy jawnie zamiast etykiety typu „marzec 2026", bo etykieta wymaga
    znajomości kalendarza, a ten jest otwartym kontraktem MASTER v1.2 rozdz. 17
    (kalendarze operacyjne / ``time_basis``). Etykieta jest opcjonalnym dodatkiem
    do granic, nie ich zamiennikiem.
    """

    model_config = _FROZEN

    period_start: dt.date
    period_end: dt.date

    period_label: str | None = None
    """Nazwa okresu z danych klienta, jeżeli była. Nie zastępuje granic."""


class ReferenceRef(BaseModel):
    """Wartość odniesienia wraz z jej pochodzeniem.

    Sześć pól dokładnie z ZOP-XR-FIN-01 v1.0 pkt 6.1 („Zapis referencji").

    Gdy referencji nie ma, całe pole ``reference`` wyniku jest ``None`` — FIN-01 rozdz. 6:
    „FIN-01 może opisać trend i dekompozycję, ale nie wyznacza Gap. Pola gap, impact_low
    i impact_high pozostają null, a ograniczenie trafia do validation_notes".
    """

    model_config = _FROZEN

    reference_type: ReferenceType
    """Rodzaj referencji z katalogu FIN-01 pkt 6.1."""

    reference_period: PeriodRef | None = None
    """Okres lub data planu, z którego pochodzi wartość."""

    reference_scope: ScopeRef | None = None
    """Zakres jednostek i produktów objętych referencją."""

    reference_value: float | None = None
    """Wartość użyta w obliczeniu. ``None``, gdy referencji nie udało się wyznaczyć."""

    reference_quality: str | None = None
    """Opis jakości referencji.

    FIN-01 pkt 6.1: „dane dla ZOP-CONF-01, bez lokalnego score". Pole jest opisem
    przekazywanym dalej, a nie oceną punktową liczoną tutaj.
    """

    reference_source: str | None = None
    """Założenia, korekty, ograniczenia i źródło (FIN-01 pkt 6.1: ``reference_notes /
    source``)."""
