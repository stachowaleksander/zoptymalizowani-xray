# Implementuje ZOP-TECH-01 v0.1 pkt 5.1 (import XLSX/CSV), kryterium odbioru 8.4
# oraz zasadę 4 z CLAUDE.md (audytowalność).
"""Odczyt plików źródłowych i bramka kontraktu danych.

Odczyt XLSX i CSV jest zaimplementowany w ``reader.py``, a struktura raportu
w ``report.py``. Poniżej kontrakt, według którego obie powstały.

## Problem

Kryterium odbioru 8.4 wymaga, żeby komunikat wskazywał „problem i jego miejsce",
a zasada 4 z CLAUDE.md — żeby każda liczba prowadziła do rekordów źródłowych. Model
danych nie niesie jednak ani pliku, ani arkusza, ani numeru wiersza. I nie może:
poniżej kontraktu danych nic nie wie, z jakiego pliku przyszła liczba. To szew, którego
nie wolno naruszyć — pole `source_file` w `CostRecord` złamałoby go natychmiast.

## Rozstrzygnięcie

``ingest/`` zwraca **dwie** rzeczy, nie jedną:

1. **zwalidowaną ramkę** — dane w kontrakcie, bez śladu pochodzenia w polach,
2. **raport importu** — cały ślad pochodzenia, obok kontraktu, nie w nim.

### Zawartość raportu importu

| Element | Znaczenie |
| --- | --- |
| `source_file` | ścieżka lub nazwa pliku źródłowego |
| `source_sheet` | arkusz (XLSX) albo `null` dla CSV |
| `source_row_range` | zakres wierszy odczytanych z pliku, wraz z wierszem nagłówka |
| `records_accepted` | liczba rekordów, które przeszły bramkę kontraktu |
| `records_rejected` | liczba rekordów odrzuconych |
| `rejections` | dla każdego odrzucenia: numer wiersza w pliku i powód |
| `row_id_range` | zakres identyfikatorów nadanych rekordom przyjętym |

### Identyfikator wiersza

Każdy przyjęty rekord dostaje przy imporcie **stabilny identyfikator**, który żyje jako
indeks ramki, a **nie** jako pole modelu. Dzięki temu ślad prowadzi od liczby w FINDINGS
przez identyfikator wiersza i raport importu do konkretnego wiersza w pliku klienta,
a kontrakt danych pozostaje czysty.

Identyfikator musi być stabilny w sensie zasady 3 (determinizm): te same dane wczytane
tym samym kodem dają te same identyfikatory. Nie może więc zależeć od kolejności
iteracji po zbiorze ani od czasu wykonania.

## Podział ról przy imporcie

- ``mapping/`` — która kolumna klienta jest którym polem kontraktu; brak wymaganej
  kolumny to kontrola 1 z pkt 5.3 (CRITICAL),
- ``ingest/`` — odczyt, przeliczenie formatów zależnych od pliku (np. numer seryjny daty
  z arkusza XLSX), bramka kontraktu rekord po rekordzie, raport importu,
- ``model/`` — kontrakt: co jest poprawnym rekordem,
- ``validation/`` — wszystko, co wymaga widoku na cały zbiór.

Rekord odrzucony przez bramkę **nie znika po cichu**: trafia do `rejections` z numerem
wiersza i powodem. Odrzucenie jest informacją dla klienta o jakości jego danych,
a nie awarią importu.
"""

from xray.ingest.reader import LoadResult, load_table
from xray.ingest.report import (
    AmbiguousLocalTime,
    ImportReport,
    Rejection,
    RejectionCategory,
    SourceRef,
)

__all__ = [
    "AmbiguousLocalTime",
    "ImportReport",
    "LoadResult",
    "Rejection",
    "RejectionCategory",
    "SourceRef",
    "load_table",
]
