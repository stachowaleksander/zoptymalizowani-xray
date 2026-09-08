# Implementuje ZOP-TECH-01 v0.1 pkt 5.2, tabela ACTIVITY
# (date, unit, product, volume, revenue).
"""Kontrakt tabeli ACTIVITY — aktywność i przychód w ujęciu okresowym.

Rola tabeli wg kart: ZOP-XR-FIN-01 v1.0 pkt 2 („czas, lokalizacja, portfel, aktywność
i przychód"), ZOP-XR-PORT-01 pkt 2.2 (element, aktywność i przychód), ZOP-XR-CAP-01
pkt 3 (wolumen i opcjonalny sygnał przychodowy), ZOP-XR-HR-01 rozdz. 3 (efekt
działalności; ``revenue`` wyłącznie pomocniczo).

ACTIVITY jest tabelą, którą karty rozszerzają najmocniej — ZOP-XR-PORT-01 pkt 2.3
wymienia ponad dwadzieścia pól opcjonalnych (``portfolio_item``, ``net_revenue``,
``allocation_basis`` i dalsze). Żadnego z nich tu nie ma i mieć nie powinno: dokładamy
je razem z kartą, która je wprowadza.
"""

from typing import ClassVar

from xray.model.enums import TimeGrain
from xray.model.tables.base import KeyText, NumericValue, PeriodDate, TableRecord


class ActivityRecord(TableRecord):
    """Pojedynczy rekord aktywności i przychodu.

    Klucz naturalny ``date + unit + product`` — ZOP-XR-FIN-01 pkt 2.1 wymaga jawnych
    kluczy ``date + unit + product/category`` jako ochrony przed podwójnym liczeniem.
    """

    TABLE_NAME: ClassVar[str] = "ACTIVITY"
    NATURAL_KEY: ClassVar[tuple[str, ...]] = ("date", "unit", "product")
    TIME_GRAIN: ClassVar[TimeGrain] = TimeGrain.PERIOD
    TIME_FIELDS: ClassVar[tuple[str, ...]] = ("date",)

    date: PeriodDate
    """Etykieta okresu."""

    unit: KeyText
    """Jednostka organizacyjna z danych klienta."""

    product: KeyText
    """Produkt, usługa albo element portfela — nazwa z danych klienta."""

    volume: NumericValue
    """Wolumen działalności.

    Model nie wie, czym jest jedna jednostka wolumenu. ``activity_unit`` i
    ``weighted_volume`` są otwartym kontraktem MASTER v1.2 rozdz. 17 — wagi muszą mieć
    źródło i znaczenie branżowe, więc fundament ich nie zakłada.
    """

    revenue: NumericValue
    """Przychód.

    Rozróżnienie ``gross_revenue`` / ``net_revenue`` i reguły rozpoznania przychodu
    wprowadza dopiero ZOP-XR-PORT-01 pkt 3.1 jako rozszerzenia. Tu jest jedna wartość
    w konwencji dostarczonej przez klienta.
    """
