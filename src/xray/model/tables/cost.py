# Implementuje ZOP-TECH-01 v0.1 pkt 5.2, tabela COST (date, unit, category, amount).
"""Kontrakt tabeli COST — koszty w ujęciu okresowym.

Rola tabeli wg kart: ZOP-XR-FIN-01 v1.0 pkt 2 („czas, lokalizacja, kategoria i koszt"),
ZOP-XR-PORT-01 pkt 2.2 (źródło kosztu i uzgodnienie), ZOP-XR-HR-01 rozdz. 3 (składniki
kosztu pracy).

Kategorie kosztów pochodzą z danych klienta. FIN-01 pkt 2.2: test nie wymusza planu kont
ani branżowej klasyfikacji.
"""

from typing import ClassVar

from xray.model.enums import TimeGrain
from xray.model.tables.base import KeyText, NumericValue, PeriodDate, TableRecord


class CostRecord(TableRecord):
    """Pojedynczy rekord kosztowy.

    Klucz naturalny ``date + unit + category`` chroni przed podwójnym liczeniem —
    ZOP-XR-FIN-01 pkt 2.1: „revenue i amount są sumowane wyłącznie po poprawnie
    zdefiniowanych kluczach".
    """

    TABLE_NAME: ClassVar[str] = "COST"
    NATURAL_KEY: ClassVar[tuple[str, ...]] = ("date", "unit", "category")
    TIME_GRAIN: ClassVar[TimeGrain] = TimeGrain.PERIOD
    TIME_FIELDS: ClassVar[tuple[str, ...]] = ("date",)

    date: PeriodDate
    """Etykieta okresu."""

    unit: KeyText
    """Jednostka organizacyjna z danych klienta."""

    category: KeyText
    """Kategoria kosztu z danych klienta."""

    amount: NumericValue
    """Kwota kosztu. Pole wymagane, wartość może być pusta.

    Wartość ujemna jest dopuszczalna na poziomie modelu.

    # DECYZJA (Michał, 2026-09-05), wpis B-01: ujemny koszt pozostaje sygnałem
    # walidacyjnym z jawną podstawą. Bez jawnego oznaczenia w danych nie klasyfikujemy
    # go ani jako błędu, ani jako korekty. Kontrakt COST nie zyskuje pola korekty.
    """
