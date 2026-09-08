# Implementuje ZOP-TECH-01 v0.1 pkt 5.2, tabela PLAN (date, unit, metric, target).
"""Kontrakt tabeli PLAN — plan i wartości docelowe.

Rola tabeli wg kart: we wszystkich kartach Core 10, które ją wymieniają, PLAN jest
oznaczona jako **opcjonalna** i opisana jako „plan lub budżet jako referencja"
(ZOP-XR-FIN-01 pkt 2), „plan jako możliwa referencja" (ZOP-XR-CAP-01 pkt 3,
ZOP-XR-PORT-01 pkt 2.2, ZOP-XR-PROC-02 pkt 2.3), „referencja planowa dla kosztu,
nakładu, efektu lub wskaźnika" (ZOP-XR-HR-01 rozdz. 3).

Opcjonalność dotyczy **tabeli**, nie pól: jeżeli klient dostarczy PLAN, rekordy muszą
spełniać ten kontrakt. Brak całej tabeli jest osobnym faktem, który ogłasza
``validation/``.

Znaczenie pola ``metric`` jest jednym z miejsc, gdzie fundament styka się z otwartym
kontraktem — patrz docs/otwarte-kontrakty.md wpis B-04.
"""

from typing import ClassVar

from xray.model.enums import TimeGrain
from xray.model.tables.base import KeyText, NumericValue, PeriodDate, TableRecord


class PlanRecord(TableRecord):
    """Pojedyncza wartość docelowa dla jednostki i okresu.

    Klucz naturalny ``date + unit + metric``.
    """

    TABLE_NAME: ClassVar[str] = "PLAN"
    NATURAL_KEY: ClassVar[tuple[str, ...]] = ("date", "unit", "metric")
    TIME_GRAIN: ClassVar[TimeGrain] = TimeGrain.PERIOD
    TIME_FIELDS: ClassVar[tuple[str, ...]] = ("date",)

    date: PeriodDate
    """Okres, którego dotyczy plan."""

    unit: KeyText
    """Jednostka organizacyjna z danych klienta."""

    metric: KeyText
    """Nazwa planowanego wskaźnika.

    Karty nie rozstrzygają, czy jest to swobodny tekst klienta, czy słownik kontrolowany.
    Ma to znaczenie, bo test musi umieć odnaleźć właściwy ``target`` — patrz wpis B-04.
    Fundament przyjmuje wartość taką, jaka przyszła, i niczego nie tłumaczy.
    """

    target: NumericValue
    """Wartość docelowa.

    Model nie wie, w jakiej jednostce jest wyrażona — to zależy od ``metric``. Dlatego
    ``target`` nie jest porównywalny z niczym bez rozstrzygnięcia z wpisu B-04.
    """
