# Realizuje zasadę 3 (determinizm) w generatorze — ZOP-TECH-01 v0.1 pkt 5.5.
"""Wartości wyprowadzane ze skrótu współrzędnych, a nie ze strumienia losowego.

## Dlaczego nie ``random.Random(seed)``

Strumień losowy ma stan, więc wartość zależy od **kolejności wywołań**. Python losuje
ziarno haszowania łańcuchów przy każdym uruchomieniu procesu, więc iteracja po zbiorze
nazw daje inną kolejność w kolejnym uruchomieniu — te same parametry, inne pliki, inny
``content_digest``. Objawiłoby się jako test przechodzący dziesięć razy i padający za
jedenastym.

Skrót współrzędnych daje trzy własności, których strumień nie ma:

1. **niezależność od kolejności z konstrukcji** — nie ma stanu, więc iteracja po zbiorze
   nie może zmienić wyniku; reguła „nic bez ``sorted``" przestaje być potrzebna jako
   dyscyplina, bo problem znika,
2. **stabilność między wydaniami Pythona** — ``random.shuffle`` i ``sample`` nie
   gwarantują tej samej sekwencji między wersjami, ``blake2b`` gwarantuje,
3. **rozłączność** — dodanie kolumny do PLAN nie przesuwa wartości w COST, bo każda
   komórka ma własne współrzędne.

Ta sama machineria, której używamy do tożsamości rekordów: kanoniczna postać, potem skrót.
"""

import math
from hashlib import blake2b
from typing import Any

from xray.model.findings.identity import canonical_form

_DIGEST_BYTES = 8
_SKALA = float(1 << (8 * _DIGEST_BYTES))


def unit_interval(seed: int, *coords: Any) -> float:
    """Liczba z przedziału [0, 1) wyprowadzona ze współrzędnych.

    Ta sama krotka współrzędnych zawsze daje tę samą wartość, niezależnie od tego, kiedy
    i w jakiej kolejności o nią zapytano.
    """
    postac = canonical_form({"seed": seed, "coords": list(coords)})
    skrot = blake2b(postac.encode("utf-8"), digest_size=_DIGEST_BYTES).digest()
    return int.from_bytes(skrot, "big") / _SKALA


def symmetric_noise(seed: int, amplitude: float, *coords: Any) -> float:
    """Szum symetryczny wokół zera, w przedziale [-amplitude, +amplitude].

    Symetryczny **z konstrukcji**: rozkład jednostajny wyśrodkowany na zerze. Szum
    z kierunkiem tworzyłby systematyczną lukę — a luka planistyczna albo kosztowa
    zaszyta w danych to problem, którego pkt 5.5.4 zakazuje.
    """
    return (unit_interval(seed, *coords) - 0.5) * 2.0 * amplitude


def scaled(seed: int, base: float, amplitude: float, *coords: Any) -> float:
    """Wielkość bazowa z symetrycznym szumem."""
    return base * (1.0 + symmetric_noise(seed, amplitude, *coords))


def whole(value: float) -> int:
    """Zaokrągla do pełnej jednostki.

    Wszystkie kwoty generujemy jako **pełne złote**. Gdyby były ułamkowe, suma dwudziestu
    kosztów zasobów nie równałaby się dokładnie zapisanej kwocie w ``float64``, a test
    uzgodnienia potrzebowałby **tolerancji** — czyli dokładnie tego, co wpis DT-01 parkuje
    jako pytanie metodologiczne do ZOP-XR-MGT-01. Liczby całkowite do 2^53 sumują się
    w ``float64`` dokładnie, więc uzgodnienie jest sprawdzalne bez wymyślania progu.
    """
    return int(round(value))


def seasonal_factor(month_of_year: int, amplitude: float = 0.15) -> float:
    """Współczynnik sezonowy zależny **wyłącznie** od numeru miesiąca w roku.

    Powtarza się identycznie w obu latach, więc nie wprowadza dryfu: żadna wielkość nie
    rośnie z numerem miesiąca. Sezonowość jest **zmiennością**, a nie problemem — problemem
    byłby kierunek.
    """
    return 1.0 + amplitude * math.cos(2.0 * math.pi * (month_of_year - 1) / 12.0)


def pick(seed: int, options: tuple[float, float], *coords: Any) -> float:
    """Wartość z przedziału ``options`` wyprowadzona ze współrzędnych."""
    dolna, gorna = options
    return dolna + (gorna - dolna) * unit_interval(seed, *coords)
