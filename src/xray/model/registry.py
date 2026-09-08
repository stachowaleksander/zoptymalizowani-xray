# Implementuje ZOP-TECH-01 v0.1 pkt 5.2 — rejestr pięciu tabel bazowych.
"""Rejestr tabel wspólnego modelu danych.

To **nie** jest rejestr wtyczek. Zbiór tabel jest zamknięty przez ZOP-TECH-01 pkt 5.2
i każda karta Core 10 to potwierdza („rozszerzenia nie zmieniają bazowej struktury
ZOP-TECH-01"). Nowa tabela nie jest rozszerzeniem, tylko zmianą kontraktu.

Rejestr istnieje po to, żeby ``ingest/`` i ``validation/`` mogły przejść po tabelach bez
wpisywania pięciu nazw w każdym module. Kryterium odbioru 8.2 wymaga mapowania do pięciu
struktur i sprawdzenia zakresu czasowego — pętla po tabelach powstałaby i tak.

Rejestr jest cienki celowo: metadane (klucz naturalny, ziarno czasowe, pola czasu)
mieszkają przy klasach tabel, bo to fakty o tabeli, a nie o rejestrze.
"""

from collections.abc import Mapping
from types import MappingProxyType

from xray.model.tables.activity import ActivityRecord
from xray.model.tables.base import TableRecord
from xray.model.tables.cost import CostRecord
from xray.model.tables.plan import PlanRecord
from xray.model.tables.process import ProcessRecord
from xray.model.tables.resource import ResourceRecord

# Kolejność jak w ZOP-TECH-01 pkt 5.2. Nazwy biorą się z samych klas, więc nie da się
# zarejestrować tabeli pod nazwą inną niż jej TABLE_NAME.
_TABLE_CLASSES: tuple[type[TableRecord], ...] = (
    ActivityRecord,
    CostRecord,
    ResourceRecord,
    ProcessRecord,
    PlanRecord,
)

TABLES: Mapping[str, type[TableRecord]] = MappingProxyType(
    {cls.TABLE_NAME: cls for cls in _TABLE_CLASSES}
)
"""Nazwa techniczna tabeli → klasa kontraktu. Odwzorowanie niezmienne."""


def table_names() -> tuple[str, ...]:
    """Nazwy pięciu tabel w kolejności z karty."""
    return tuple(cls.TABLE_NAME for cls in _TABLE_CLASSES)


def get_table(name: str) -> type[TableRecord]:
    """Zwraca klasę kontraktu dla nazwy tabeli.

    Podnosi ``KeyError`` z czytelnym komunikatem, bo nietrafiona nazwa tabeli to zwykle
    literówka w profilu mapowania klienta, a nie brak funkcjonalności.
    """
    try:
        return TABLES[name]
    except KeyError:
        raise KeyError(
            f"nieznana tabela {name!r}; ZOP-TECH-01 pkt 5.2 definiuje wyłącznie: "
            f"{', '.join(table_names())}"
        ) from None
