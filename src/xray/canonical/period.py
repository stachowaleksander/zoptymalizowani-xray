# Implementuje ZOP-XR-FOUNDATION-BIND-01 v1.1 §11 PERIOD CONTRACT — profil
# XR_PERIOD_CANONICAL_V1 (decision_id = FB11-D03 / Q-6B), przywołany przez v1.2 §7.2
# („| analysis_period | canonical XR_PERIOD object |").
"""Kanoniczny obiekt okresu.

Okres jest **semantyką wyniku**, a jego nazwa nie jest. v1.1 §11: „`period_label` jest
wyłącznie metadata" i w tabeli: „| period_label | Human-readable; identity-excluded. |".
Dlatego etykieta jest tu polem obiektu, ale nie wchodzi do ładunku, z którego liczy się
skrót — dokładnie tak samo jak `scope_label` w zakresie.

## Co niesie ten obiekt

Siedem elementów z tabeli v1.1 §11: przedział (`start_inclusive`, `end_exclusive`),
`horizon`, `time_bucket`, `time_basis`, `semantic_extensions` oraz etykieta poza
tożsamością. `analysis_period` i `reference_period` to **dwa różne pola semantyczne**
korzystające z tego samego profilu — stąd jedna klasa i dwa zastosowania.

## Czego ten obiekt nie robi

Nie wnioskuje `time_basis`. v1.1 §11: „Source-specific token (np. start/end/event basis)
tylko gdy frozen source go ustanawia. Brak reguły → canonical null; **nie inferuj dla
PROC**". Brak wartości zostaje `None` i trafia do ładunku jako `null`.

Nie zastępuje ``PeriodRef`` z ``model/findings/refs.py``. Tamten obiekt wchodzi dziś do
``finding_id`` przez ``identity_of``; karta V12-R1 §1 ustala
``HISTORICAL_IDENTITY_REWRITE = false``, więc jego kształt zostaje nietknięty aż do
przełączenia warstwy rekordów.

## Granice: daty czy znaczniki czasu

v1.1 §11 mówi „Jeżeli fixed interval: typed `start_inclusive` i `end_exclusive`; boundary
`[start,end)`" — wymaga wartości **typowanej**, ale typu nie przesądza. Przyjmujemy oba:
datę i znacznik czasu ze strefą. Konsekwencja, którą trzeba znać:

- granice **datowe** nie dotykają otwartego kontraktu B-08 — w ładunku nie ma wtedy
  żadnego znacznika czasu. Nasz dzisiejszy kontrakt danych (``PeriodRef``) używa wyłącznie
  ``datetime.date``, więc w praktyce B-08 nie blokuje niczego w tej warstwie,
- granica będąca **znacznikiem czasu** wciąga B-08: dopóki kontrakt okresu i czasu nie
  rozstrzygnie postaci RFC 3339, dwie implementacje mogą dla tego samego instantu policzyć
  różne bajty.
"""

import datetime as dt
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

PROFILE = "XR_PERIOD_CANONICAL_V1"
"""Nazwa profilu z v1.1 §11 i z planu rund („Identity primitives")."""


class PeriodContractError(ValueError):
    """Okres nie spełnia kontraktu v1.1 §11."""


@dataclass(frozen=True, slots=True)
class Horizon:
    """Rolling/lookback horizon.

    v1.1 §11: „Semantyczny rolling/lookback horizon **tylko gdy frozen card go definiuje**;
    reprezentacja `length`, `unit`, `anchor_semantics`". Obiekt nie sprawdza, czy karta go
    definiuje — to wie wołający; sprawdza wyłącznie kompletność trzech pól.
    """

    length: int
    unit: str
    anchor_semantics: str

    def payload(self) -> dict[str, Any]:
        return {
            "anchor_semantics": self.anchor_semantics,
            "length": self.length,
            "unit": self.unit,
        }


@dataclass(frozen=True, slots=True)
class TimeBucket:
    """Kubełek czasu.

    v1.1 §11: „Bucket tylko gdy frozen card go definiuje; `bucket_unit`, `bucket_key` albo
    source-defined equivalent".
    """

    bucket_unit: str
    bucket_key: str

    def payload(self) -> dict[str, Any]:
        return {"bucket_key": self.bucket_key, "bucket_unit": self.bucket_unit}


@dataclass(frozen=True, slots=True)
class CanonicalPeriod:
    """Okres w postaci, z której liczy się tożsamość.

    Wszystkie pola są opcjonalne, bo kontrakt nie wymaga, żeby okres miał jednocześnie
    przedział, horyzont i kubełek — wymaga tylko, żeby to, co jest, było kompletne.
    """

    start_inclusive: dt.date | None = None
    end_exclusive: dt.date | None = None
    horizon: Horizon | None = None
    time_bucket: TimeBucket | None = None
    time_basis: str | None = None
    semantic_extensions: Mapping[str, Any] = field(default_factory=dict)

    period_label: str | None = None
    """Nazwa okresu. **Poza tożsamością** — v1.1 §11, wiersz `period_label`."""

    def __post_init__(self) -> None:
        self._check_interval()

    def _check_interval(self) -> None:
        """Przedział jest parą i ma dodatnią długość.

        Trzy reguły, wszystkie z jednego zdania v1.1 §11 („Jeżeli fixed interval: typed
        `start_inclusive` i `end_exclusive`; boundary `[start,end)`"):

        1. albo obie granice, albo żadna — połowa przedziału nie jest przedziałem,
        2. obie tego samego rodzaju; data i znacznik czasu leżą na różnych osiach
           i porównanie ich nie ma sensu,
        3. ``start < end`` — zapis ``[start,end)`` z równymi granicami nie obejmuje
           żadnej chwili.
        """
        ma_poczatek = self.start_inclusive is not None
        ma_koniec = self.end_exclusive is not None
        if ma_poczatek != ma_koniec:
            raise PeriodContractError(
                "przedział wymaga obu granic: start_inclusive i end_exclusive "
                "(v1.1 §11, wiersz interval)"
            )
        if not ma_poczatek:
            return
        poczatek_z_czasem = isinstance(self.start_inclusive, dt.datetime)
        koniec_z_czasem = isinstance(self.end_exclusive, dt.datetime)
        if poczatek_z_czasem != koniec_z_czasem:
            raise PeriodContractError(
                "granice przedziału muszą być tego samego rodzaju: albo obie datami, "
                "albo obie znacznikami czasu"
            )
        if self.start_inclusive >= self.end_exclusive:
            raise PeriodContractError(
                f"granice {self.start_inclusive} i {self.end_exclusive} nie tworzą "
                "przedziału [start,end): koniec musi leżeć po początku"
            )

    def payload(self) -> dict[str, Any]:
        """Ładunek kanoniczny okresu — bez etykiety.

        Wartości dat i znaczników czasu **nie są** tu zamieniane na tekst: przekazujemy je
        profilowi ``XR_IDENTITY_CANONICAL_JSON_V1``, który nada im postać typowaną. To jest
        cała różnica między „2026-09-01" jako datą a tym samym ciągiem znaków jako tekstem.
        """
        return {
            "end_exclusive": self.end_exclusive,
            "horizon": self.horizon.payload() if self.horizon is not None else None,
            "semantic_extensions": dict(self.semantic_extensions),
            "start_inclusive": self.start_inclusive,
            "time_basis": self.time_basis,
            "time_bucket": self.time_bucket.payload() if self.time_bucket is not None else None,
        }


def period_payload(period: CanonicalPeriod | None) -> dict[str, Any] | None:
    """Ładunek okresu albo ``None``, gdy okresu nie ma.

    Brak okresu to ``canonical null``, a nie pusty obiekt: obiekt o samych pustych polach
    znaczyłby „okres bez treści", a to jest co innego niż „okresu nie ma".
    """
    return None if period is None else period.payload()
