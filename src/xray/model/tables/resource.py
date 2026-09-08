# Implementuje ZOP-TECH-01 v0.1 pkt 5.2, tabela RESOURCE
# (date, unit, resource, available, used, cost).
"""Kontrakt tabeli RESOURCE — zasoby i ich wykorzystanie w ujęciu okresowym.

Rola tabeli wg kart: ZOP-XR-CAP-01 v1.0 pkt 3 („zdolność, wykorzystanie, koszt"),
ZOP-XR-CAP-02 (bilans zdolności), ZOP-XR-HR-01 rozdz. 3 (zasób, zdolność, wykorzystanie
i koszt — z zastrzeżeniem, że ``used`` jest sygnałem CAP-01, a nie automatycznym
``labor_input``), ZOP-XR-PORT-01 i ZOP-XR-PROC-01/02 jako tabela opcjonalna.

## Dwie rzeczy, których model tu świadomie nie robi

**Nie odrzuca ``used`` większego od ``available``.** ZOP-XR-CAP-01 rozdz. 5 jest tu
jednoznaczna: „przekroczenie nie jest automatycznie błędem logicznym". Najpierw sprawdza
się udokumentowaną dodatkową zdolność — nadgodziny, dodatkową zmianę, czasowo uruchomiony
zasób. Tej informacji w pojedynczym wierszu nie ma (mieszka w rozszerzeniu
``documented_extra_capacity``), więc kontrola 7 z ZOP-TECH-01 pkt 5.3 należy do
``validation/`` i zwraca sygnał z podstawą, a nie CRITICAL nadany samodzielnie.

**Nie odrzuca wartości ujemnych.** ZOP-XR-CAP-01 VAL-04 i VAL-05 (``available >= 0``,
``used >= 0``) to kontrole walidacyjne, których statusem jest CRITICAL. Rekord odrzucony
przez model nigdy nie dotarłby do walidatora, więc ten CRITICAL nie miałby gdzie zostać
ogłoszony. Patrz docs/notatka-techniczna.md wpis DT-03.
"""

from typing import ClassVar

from xray.model.enums import TimeGrain
from xray.model.tables.base import KeyText, NumericValue, PeriodDate, TableRecord


class ResourceRecord(TableRecord):
    """Pojedynczy rekord zasobu w okresie.

    Klucz naturalny ``date + unit + resource``. ZOP-XR-CAP-01 pkt 3.1 dokłada do klucza
    ``capacity_unit``, ale to pole rozszerzenia — wchodzi razem z implementacją CAP-01,
    nie wcześniej.
    """

    TABLE_NAME: ClassVar[str] = "RESOURCE"
    NATURAL_KEY: ClassVar[tuple[str, ...]] = ("date", "unit", "resource")
    TIME_GRAIN: ClassVar[TimeGrain] = TimeGrain.PERIOD
    TIME_FIELDS: ClassVar[tuple[str, ...]] = ("date",)

    date: PeriodDate
    """Etykieta okresu."""

    unit: KeyText
    """Jednostka organizacyjna z danych klienta."""

    resource: KeyText
    """Zasób albo grupa zasobów — nazwa z danych klienta."""

    available: NumericValue
    """Zdolność dostępna.

    ZOP-XR-CAP-01 rozdz. 5 rozróżnia ``available_source`` i ``effective_available``;
    oba są rozszerzeniami. Tu jest wartość taka, jaką dostarczył klient.
    """

    used: NumericValue
    """Zdolność wykorzystana. Może przekraczać ``available`` — patrz nagłówek modułu."""

    cost: NumericValue
    """Koszt zasobu.

    Brak kosztu nie unieruchamia tabeli: ZOP-XR-CAP-01 pkt 4.1 — „brak cost: miary
    fizyczne działają; economic_gap = null".
    """
