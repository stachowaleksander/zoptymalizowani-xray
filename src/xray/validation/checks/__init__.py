# Implementuje ZOP-TECH-01 v0.1 pkt 5.3 — osiem kontroli danych wejściowych.
"""Kontrole danych, po jednej na plik.

Mapa warstw: o tym, gdzie mieszka kontrola, decyduje **wymagana informacja**.

| Lp. | Kontrola | Warstwa |
| --- | --- | --- |
| 1 | brak wymaganej kolumny | ``validation/`` z raportu importu; ``mapping/`` wzbogaca |
| 2 | nieprawidłowy format | ``model/`` wykrywa, ``validation/`` raportuje z odrzuceń |
| 3 | brakujące wartości | ``model/`` wykrywa, ``validation/`` zlicza |
| 4 | duplikaty | ``validation/`` — wymaga całego zbioru |
| 5 | wartości podejrzane | ``validation/`` — sygnał, nigdy CRITICAL samodzielnie |
| 6 | niespójne nazwy jednostek | ``validation/`` — wymaga całego zbioru |
| 7 | ``used`` > ``available`` | ``validation/`` — sygnał; rozstrzyga CAP-01 |
| 8 | zakres czasowy | ``validation/`` — wymaga całego zbioru |

Zaimplementowane: wszystkie osiem.
"""
