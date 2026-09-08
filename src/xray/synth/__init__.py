# Realizuje ZOP-TECH-01 v0.1 pkt 5.5 — generator firmy syntetycznej.
"""Generator zbioru syntetycznego.

Wyłącznie dane syntetyczne. Nic z SPZOZ, nic o pacjentach, nic z realnej organizacji.

Generator **zapisuje pliki**, a nie oddaje ramki. Gdyby oddawał ramki, demonstracja
ominęłaby ``ingest/`` i nie dowiodła kryterium odbioru 8.1 — dane syntetyczne mają
przechodzić tę samą drogę co dane klienta.
"""

from xray.synth.generator import GeneratedDataset, generate
from xray.synth.names import HEADERS, UNITS

__all__ = ["HEADERS", "UNITS", "GeneratedDataset", "generate"]
