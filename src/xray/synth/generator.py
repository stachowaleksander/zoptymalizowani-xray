# Realizuje ZOP-TECH-01 v0.1 pkt 5.5 — generator firmy syntetycznej.
"""Generator zbioru syntetycznego.

## Zmienność wolno, problem nie

ZOP-TECH-01 pkt 5.5.4: na tym etapie **nie zaszywamy problemów biznesowych**, wystarczy
realistyczna struktura. Kryterium operacyjne: gdyby dziś istniał test diagnostyczny, czy
znalazłby finding **z konstrukcji generatora**? Jeżeli tak — to zaszyty problem, choćby
nikt go świadomie nie zaszywał.

| Zmienność (wolno) | Problem (nie wolno) |
| --- | --- |
| sezonowość powtarzalna rok do roku | trend kosztów szybszy niż przychodów |
| jednostki różnej wielkości | jednostka systematycznie odstająca |
| różne koszty zasobów | zasób chronicznie przeciążony |
| plan raz nad, raz pod wykonaniem | plan systematycznie po jednej stronie |

## Cztery ograniczenia wynikające z ośmiu kontroli

1. **Wiersz tabeli okresowej to agregat miesiąca**, nie zdarzenie — inaczej kontrola 4
   zapaliłaby duplikaty na kluczu ``date + unit + product``.
2. **Jeden słownik nazw** (``names.py``) — kontrola 6 pracuje w obrębie tabeli, więc
   niespójność między tabelami byłaby dla niej niewidoczna.
3. **``used <= available`` zawsze** — nadgodziny są w rzeczywistości prawdą i kiedyś wejdą
   do danych klienta, ale tutaj byłyby sygnałem kontroli 7.
4. **Bez korekt** — żadnych kwot ujemnych, bo to sygnał kontroli 5 (wpis B-01).

## Czego generator nie modeluje

Kalendarzy operacyjnych. ``available`` to stałe 160 godzin miesięcznie, a nie liczba dni
roboczych w miesiącu: kalendarze operacyjne są otwartym kontraktem ZOP-MASTER-01 rozdz. 17
i modelowanie ich tutaj byłoby wymyśleniem reguły, której karta nie ustanawia.

## Zapisane ograniczenie zbioru

Brak dryfu jest gwarantowany **z konstrukcji**: żadna wielkość nie zależy od numeru
miesiąca inaczej niż przez powtarzalny współczynnik sezonowy. Nie gwarantujemy natomiast,
że przy jakimś ziarnie szum nie ułoży się przypadkiem w coś, co wygląda jak trend — tego
zagwarantować się nie da i nie udajemy, że da.
"""

import calendar
import datetime as dt
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from xray.synth.names import (
    COST_CATEGORIES,
    EXTRA_COLUMNS,
    HEADERS,
    PLAN_METRICS,
    PRODUCTS,
    RECONCILED_CATEGORY,
    STAGES,
    UNITS,
    resource_name,
)
from xray.synth.values import pick, scaled, seasonal_factor, symmetric_noise, whole

FIRST_MONTH = dt.date(2025, 1, 1)
"""Pierwszy miesiąc szeregu. Stała, nie „dziś" — inaczej wynik zależałby od daty
uruchomienia, co łamie zasadę 3."""

DEFAULT_MONTHS = 24
DEFAULT_UNITS = 5
DEFAULT_RESOURCES_PER_UNIT = 20
DEFAULT_CASES_PER_UNIT_MONTH = 8

AVAILABLE_HOURS = 160
"""Zdolność miesięczna zasobu. Stała — patrz „czego generator nie modeluje"."""

UTILIZATION = (0.55, 0.92)
"""Przedział wykorzystania. Górna granica poniżej 1.0, więc ``used <= available``
wynika z **konstrukcji**, a nie z pilnowania."""


@dataclass(frozen=True, slots=True)
class GeneratedDataset:
    """Wygenerowany zbiór: ścieżki plików i użyte parametry."""

    directory: Path
    files: dict[str, Path]
    seed: int
    months: int
    units: tuple[str, ...]
    resources_per_unit: int


def _months(count: int) -> list[dt.date]:
    """Kolejne pierwsze dni miesiąca, bez luk."""
    wynik = []
    rok, miesiac = FIRST_MONTH.year, FIRST_MONTH.month
    for _ in range(count):
        wynik.append(dt.date(rok, miesiac, 1))
        miesiac += 1
        if miesiac > 12:
            miesiac = 1
            rok += 1
    return wynik


def _unit_scale(seed: int, unit: str) -> float:
    """Wielkość jednostki. Stała w czasie, więc różnicuje bez tworzenia trendu."""
    return pick(seed, (0.7, 1.3), "unit_scale", unit)


def _activity(seed: int, months: Sequence[dt.date], units: Sequence[str]) -> pd.DataFrame:
    wiersze = []
    for miesiac in months:
        sezon = seasonal_factor(miesiac.month)
        for jednostka in units:
            skala = _unit_scale(seed, jednostka)
            for produkt in PRODUCTS:
                baza = pick(seed, (60.0, 240.0), "volume_base", jednostka, produkt)
                wolumen = whole(
                    scaled(
                        seed,
                        baza * skala * sezon,
                        0.08,
                        "volume",
                        miesiac,
                        jednostka,
                        produkt,
                    )
                )
                # Cena jednostkowa jest stała dla produktu: przychód jest wprost
                # proporcjonalny do wolumenu, więc relacja przychód/wolumen nie dryfuje.
                cena = whole(pick(seed, (120.0, 900.0), "price", produkt))
                wiersze.append(
                    {
                        "date": miesiac,
                        "unit": jednostka,
                        "product": produkt,
                        "volume": wolumen,
                        "revenue": wolumen * cena,
                    }
                )
    return pd.DataFrame(wiersze)


def _resource(
    seed: int, months: Sequence[dt.date], units: Sequence[str], per_unit: int
) -> pd.DataFrame:
    wiersze = []
    for miesiac in months:
        sezon = seasonal_factor(miesiac.month)
        for jednostka in units:
            skala = _unit_scale(seed, jednostka)
            for numer in range(1, per_unit + 1):
                zasob = resource_name(jednostka, numer)
                wykorzystanie = pick(seed, UTILIZATION, "utilization", miesiac, zasob)
                baza = pick(seed, (4000.0, 9000.0), "resource_cost_base", zasob)
                wiersze.append(
                    {
                        "date": miesiac,
                        "unit": jednostka,
                        "resource": zasob,
                        "available": AVAILABLE_HOURS,
                        # used <= available z konstrukcji: wykorzystanie < 1.0.
                        "used": whole(AVAILABLE_HOURS * wykorzystanie),
                        "cost": whole(
                            scaled(
                                seed,
                                baza * skala * sezon,
                                0.06,
                                "resource_cost",
                                miesiac,
                                zasob,
                            )
                        ),
                    }
                )
    return pd.DataFrame(wiersze)


def _cost(
    seed: int,
    months: Sequence[dt.date],
    units: Sequence[str],
    resource_frame: pd.DataFrame,
) -> pd.DataFrame:
    # Uzgodnienie: kategoria RECONCILED_CATEGORY równa się sumie kosztów zasobów
    # jednostki w miesiącu. Bez tego ZOP-XR-MGT-01 znalazłaby `unreconciled`
    # z konstrukcji generatora — czyli zaszyty problem wg pkt 5.5.4.
    sumy = (
        resource_frame.groupby(["date", "unit"], sort=True)["cost"].sum().to_dict()
    )
    wiersze = []
    for miesiac in months:
        sezon = seasonal_factor(miesiac.month)
        for jednostka in units:
            skala = _unit_scale(seed, jednostka)
            for kategoria in COST_CATEGORIES:
                if kategoria == RECONCILED_CATEGORY:
                    kwota = whole(sumy[(miesiac, jednostka)])
                else:
                    baza = pick(
                        seed, (20000.0, 90000.0), "cost_base", jednostka, kategoria
                    )
                    kwota = whole(
                        scaled(
                            seed,
                            baza * skala * sezon,
                            0.07,
                            "cost",
                            miesiac,
                            jednostka,
                            kategoria,
                        )
                    )
                wiersze.append(
                    {
                        "date": miesiac,
                        "unit": jednostka,
                        "category": kategoria,
                        "amount": kwota,
                    }
                )
    return pd.DataFrame(wiersze)


def _plan(
    seed: int,
    months: Sequence[dt.date],
    units: Sequence[str],
    activity_frame: pd.DataFrame,
    cost_frame: pd.DataFrame,
) -> pd.DataFrame:
    """Plan wywiedziony z tej samej wielkości bazowej co wykonanie.

    Szum jest **symetryczny**: realizacje wypadają raz nad planem, raz pod, bez kierunku.
    Plan powstający niezależnie od wykonania byłby systematycznie nad albo pod — luka
    planistyczna zaszyta w danych, którą FIN-01 znalazłby w pierwszym uruchomieniu.
    """
    przychody = activity_frame.groupby(["date", "unit"], sort=True)["revenue"].sum().to_dict()
    wolumeny = activity_frame.groupby(["date", "unit"], sort=True)["volume"].sum().to_dict()
    koszty = cost_frame.groupby(["date", "unit"], sort=True)["amount"].sum().to_dict()
    baza_dla = {
        "Koszt calkowity": koszty,
        "Przychod calkowity": przychody,
        "Liczba wykonan": wolumeny,
    }

    wiersze = []
    for miesiac in months:
        for jednostka in units:
            for wskaznik in PLAN_METRICS:
                wykonanie = baza_dla[wskaznik][(miesiac, jednostka)]
                odchylenie = symmetric_noise(seed, 0.05, "plan", miesiac, jednostka, wskaznik)
                wiersze.append(
                    {
                        "date": miesiac,
                        "unit": jednostka,
                        "metric": wskaznik,
                        "target": whole(wykonanie * (1.0 + odchylenie)),
                    }
                )
    return pd.DataFrame(wiersze)


def _process(
    seed: int, months: Sequence[dt.date], units: Sequence[str], cases_per_unit_month: int
) -> pd.DataFrame:
    """Sprawy i etapy.

    Dwie własności zagwarantowane **konstrukcją**, nie ziarnem:

    - **etap zaczyna się nie wcześniej, niż kończy się poprzedni**, a ``end >= start``
      w każdym wierszu — następstwa etapów nie sprawdza żadna z ośmiu kontroli (klucz to
      ``case_id + stage``), więc odwrócona kolejność byłaby dziś niewidoczna,
      a ZOP-XR-PROC-01 znalazłaby ją jako pierwszą rzecz,
    - **w każdym miesiącu co najmniej jedna sprawa przekracza granicę miesiąca** —
      startuje ostatniego dnia o 20:00 z czasem trwania ponad 30 godzin, więc musi się
      przelać. Własność probabilistyczna zanikłaby po cichu przy zmianie parametrów;
      strukturalna nie może.

    Przekroczenie **nie jest sygnałem**: A-01 traktuje różnicę między miesiącami startów
    a miesiącami końców jako informację, nie jako lukę.
    """
    wiersze = []
    for miesiac in months:
        ostatni_dzien = calendar.monthrange(miesiac.year, miesiac.month)[1]
        for indeks_jednostki, jednostka in enumerate(units):
            for numer in range(cases_per_unit_month):
                case_id = (
                    f"SPR-{miesiac.year}{miesiac.month:02d}-"
                    f"{indeks_jednostki + 1}{numer:02d}"
                )
                if numer == 0:
                    # Sprawa przelewająca się na kolejny miesiąc — z konstrukcji.
                    #
                    # Przelewa się WYŁĄCZNIE ostatni etap. Gdyby przelewał się pierwszy,
                    # kolejne etapy ZACZYNAŁYBY się już w następnym miesiącu i miesiące
                    # startów zrównałyby się z miesiącami końców — rozróżnienie z A-01
                    # znów byłoby niewidoczne, tak samo jak przy wspólnej kolumnie.
                    #
                    # Dlatego układamy etapy wstecz od ostatniego: ostatni startuje
                    # ostatniego dnia o 20:00 i trwa 9 godzin, więc kończy się nazajutrz.
                    godziny_etapu = 9.0
                    ostatni_start = dt.datetime(
                        miesiac.year, miesiac.month, ostatni_dzien, 20, 0
                    )
                    poczatek = ostatni_start - dt.timedelta(
                        hours=godziny_etapu * (len(STAGES) - 1)
                    )
                else:
                    dzien = 1 + int(
                        pick(seed, (0.0, 19.99), "case_day", miesiac, jednostka, numer)
                    )
                    godzina = 7 + int(
                        pick(seed, (0.0, 9.99), "case_hour", miesiac, jednostka, numer)
                    )
                    poczatek = dt.datetime(miesiac.year, miesiac.month, dzien, godzina, 0)
                    godziny_etapu = pick(
                        seed, (2.0, 20.0), "stage_hours", miesiac, jednostka, numer
                    )

                kursor = poczatek
                for etap in STAGES:
                    trwanie = dt.timedelta(hours=godziny_etapu)
                    koniec = kursor + trwanie
                    wiersze.append(
                        {
                            "case_id": case_id,
                            "stage": etap,
                            "start": kursor,
                            "end": koniec,
                            "unit": jednostka,
                        }
                    )
                    # Kolejny etap zaczyna się dokładnie tam, gdzie skończył poprzedni.
                    kursor = koniec
    return pd.DataFrame(wiersze)


def _zapisz(frame: pd.DataFrame, table: str, directory: Path, *, xlsx: bool) -> Path:
    """Zapisuje ramkę pod klienckimi nagłówkami."""
    naglowki = HEADERS[table]
    do_zapisu = frame.rename(columns=naglowki)[list(naglowki.values())]
    for dodatkowa in EXTRA_COLUMNS.get(table, ()):
        # Kolumna spoza kontraktu — ćwiczy pozycję „niezmapowane" raportu mapowania.
        do_zapisu[dodatkowa] = [
            f"MPK-{i % 7 + 1:02d}" for i in range(len(do_zapisu))
        ]

    if xlsx:
        sciezka = directory / f"{table.lower()}.xlsx"
        do_zapisu.to_excel(sciezka, index=False)
    else:
        sciezka = directory / f"{table.lower()}.csv"
        do_zapisu.to_csv(sciezka, index=False, encoding="utf-8", lineterminator="\n")
    return sciezka


def generate(
    directory: str | Path,
    *,
    seed: int,
    months: int = DEFAULT_MONTHS,
    units: int = DEFAULT_UNITS,
    resources_per_unit: int = DEFAULT_RESOURCES_PER_UNIT,
    cases_per_unit_month: int = DEFAULT_CASES_PER_UNIT_MONTH,
) -> GeneratedDataset:
    """Generuje komplet pięciu tabel i zapisuje je jako pliki.

    ``seed`` jest wymagany i nie ma wartości domyślnej — domyślna byłaby założeniem,
    tak samo jak przy ``dataset_id``.

    COST zapisujemy jako **XLSX**, resztę jako CSV. COST jest tabelą okresową, więc daty
    idą przez ścieżkę numeru seryjnego arkusza — tę, w której siedział błąd z klasyfikacją
    ``datetime.date`` jako znacznika czasu. Demonstracja ma przez tę ścieżkę przechodzić,
    a nie ją omijać. PROCESS zostaje w CSV, bo jest tabelą zdarzeniową.
    """
    katalog = Path(directory)
    katalog.mkdir(parents=True, exist_ok=True)

    lista_miesiecy = _months(months)
    lista_jednostek = UNITS[:units]
    if len(lista_jednostek) < units:
        raise ValueError(
            f"słownik zna {len(UNITS)} jednostek, a poproszono o {units}; "
            "nazwy pochodzą z jednego kanonicznego słownika i nie są dogenerowywane"
        )

    activity = _activity(seed, lista_miesiecy, lista_jednostek)
    resource = _resource(seed, lista_miesiecy, lista_jednostek, resources_per_unit)
    cost = _cost(seed, lista_miesiecy, lista_jednostek, resource)
    plan = _plan(seed, lista_miesiecy, lista_jednostek, activity, cost)
    process = _process(seed, lista_miesiecy, lista_jednostek, cases_per_unit_month)

    pliki = {
        "ACTIVITY": _zapisz(activity, "ACTIVITY", katalog, xlsx=False),
        "COST": _zapisz(cost, "COST", katalog, xlsx=True),
        "RESOURCE": _zapisz(resource, "RESOURCE", katalog, xlsx=False),
        "PROCESS": _zapisz(process, "PROCESS", katalog, xlsx=False),
        "PLAN": _zapisz(plan, "PLAN", katalog, xlsx=False),
    }

    return GeneratedDataset(
        directory=katalog,
        files=pliki,
        seed=seed,
        months=months,
        units=lista_jednostek,
        resources_per_unit=resources_per_unit,
    )
