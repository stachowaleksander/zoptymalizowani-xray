# Implementuje ZOP-TECH-01 v0.1 pkt 5.2 — pięć bazowych tabel wspólnego modelu danych.
"""Pięć tabel wejściowych: ACTIVITY, COST, RESOURCE, PROCESS, PLAN.

Zbiór tych tabel jest zamknięty. Każda karta Core 10 powtarza to samo zastrzeżenie —
np. ZOP-XR-CAP-01 pkt 3.1: „rozszerzenia nie zmieniają bazowej struktury ZOP-TECH-01".
Rozszerzenia z kart (``capacity_unit``, ``labor_input``, ``portfolio_item`` i pozostałe)
dokładamy jako pola opcjonalne razem z kartą, która je wprowadza — nigdy zawczasu.
"""
