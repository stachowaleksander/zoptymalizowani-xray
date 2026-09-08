# Realizuje produkt 6 z ZOP-TECH-01 v0.1 rozdz. 7 — demonstracja uruchomienia importu,
# walidacji i zapisu wyniku.
"""Demonstracja pełnego przebiegu na firmie syntetycznej.

Każdy element łańcucha był przetestowany osobno; ta demonstracja składa go w całość
i pokazuje, że przepływ się spina:

```
generator → pięć plików → mapping → ingest → osiem kontroli → NOOP-01 → FindingStore
```

Uruchomienie: ``python -m xray.demo``.

Demonstracja **nie zawiera żadnej treści metodologicznej**. Liczy wiersze, ogłasza statusy
kontroli i zapisuje jeden wynik bez tezy. Jej celem jest dowieść, że warstwy działają
razem — kryterium odbioru 8.5 mówi o **działającej** strukturze FINDINGS, a nie o samej
definicji.

Dane **powstają w trakcie**, w katalogu tymczasowym, z jawnym ziarnem. Czytanie z ``data/``
dałoby demonstrację, która u kogoś innego nie ruszy: ``data/`` jest w ``.gitignore``.
"""

from xray.demo.run import DemoResult, TableRun, opisz, run_demo

__all__ = ["DemoResult", "TableRun", "opisz", "run_demo"]
