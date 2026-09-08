# Implementuje ZOP-TECH-01 v0.1 pkt 5.3, kontrola 8 — zakres czasowy,
# zgodnie z rozstrzygnięciem A-01 (Michał, 2026-09-05).
"""Kontrola 8: zakres czasowy zbioru.

## Co wolno, a czego nie wolno — rozstrzygnięcie A-01

Podstawa przypisania procesu do miesiąca (``time_basis``) **nie jest rozstrzygnięta**
i będzie osobnym kontraktem globalnym. Kontrola nie ma prawa wybrać jej sobie sama.

**Wolno** — bo nie wymaga wyboru podstawy: granice zakresu danych, pokrycie miesięczne
dla tabel okresowych, liczenie po znacznikach czasu tam, gdzie znaczniki są.

**Nie wolno** — przypisywać sprawy (``case_id``) do miesiąca. Sprawa rozpoczęta w marcu
i zamknięta w maju nie należy do żadnego z nich, dopóki kontrakt globalny nie powie, jak
to liczyć. ``time_basis_used`` zwraca pustkę z jawną podstawą, nigdy wybraną wartość.

## Dlaczego dla tabeli zdarzeniowej liczymy dwie granice osobno

Wiersz PROCESS ma ``start`` i ``end`` — jest **odcinkiem, nie punktem**. „Własny znacznik
zdarzenia" nie istnieje bez wyboru jednego z nich, a wybór to dokładnie to, czego A-01
zakazuje. Liczymy więc obie granice osobno — ``months_with_stage_starts``
i ``months_with_stage_ends`` — i nie wybieramy. Przy etapach mieszczących się w jednym
miesiącu obie liczby są równe i pytanie nie powstaje; gdy się różnią, różnica sama jest
informacją, a nie artefaktem naszego wyboru.

## Miesiąc bez danych a miesiąc bez zdarzeń

Dla tabel okresowych brakujący miesiąc to **luka w danych** — WARNING.

Dla tabeli zdarzeniowej to **obserwacja**, nigdy WARNING ani CRITICAL: może być
miesiącem, w którym faktycznie nic nie przyszło, i bez referencji nie da się tych dwóch
sytuacji rozróżnić (zasada 5). Stąd ``max_status_by_time_grain = {EVENT: PASS}``.

## Typ kolumny źródłowej zostaje nietknięty

Kolumna ``date`` pozostaje obiektowa z ``datetime.date`` (wpis DT-08). Wszystko, czego
kontrola potrzebuje — granice, pokrycie, luki, licznik miesięczny — daje **kolumna
pochodna** budowana tutaj przez ``pd.PeriodIndex``. Kolumna pochodna żyje wewnątrz
kontroli i nie trafia do danych.
"""

from typing import ClassVar

import pandas as pd

from xray.model.enums import TimeGrain, ValidationStatus
from xray.validation.base import CheckDeclaration, ComparisonPair, DataCheck, Determines
from xray.validation.context import ValidationContext
from xray.validation.results import CheckObservation, CheckOutcome, cap_observations

PODSTAWA_TIME_BASIS_EVENT = (
    "Kontrakt globalny nierozstrzygnięty: podstawa przypisania zdarzenia do okresu "
    "(time_basis) będzie osobnym kontraktem — wpis A-01. Kontrola nie wybiera jej sama, "
    "więc wartość pozostaje pusta."
)
PODSTAWA_TIME_BASIS_PERIOD = (
    "Etykieta okresu pochodzi wprost z pola date, więc wybór podstawy nie jest potrzebny."
)


def _okresy(kolumna: pd.Series) -> pd.PeriodIndex:
    """Buduje pomocniczą kolumnę miesięcy z kolumny dat albo znaczników czasu.

    Kolumna pochodna, nie zmiana danych: powstaje tutaj i ginie wraz z kontrolą.
    """
    znane = kolumna[kolumna.notna()]
    return pd.PeriodIndex(pd.to_datetime(znane), freq="M")


class TimeRange(DataCheck):
    """Opisuje zakres czasowy tabeli i jego pokrycie miesięczne."""

    DECLARATION: ClassVar[CheckDeclaration] = CheckDeclaration(
        check_id="TECH01-VAL-08",
        control_number=8,
        title="Zakres czasowy",
        requires_import_report=False,
        required_fields=(),
        requires_time_fields=True,
        max_status=ValidationStatus.WARNING,
        # A-01: w danych zdarzeniowych miesiąca bez zdarzeń nie da się odróżnić od braku
        # danych, więc kontrola może go najwyżej odnotować.
        max_status_by_time_grain={TimeGrain.EVENT: ValidationStatus.PASS},
        # Różnica między liczbą miesięcy z początkami a z końcami etapów jest informacją
        # (A-01). Przy jednej kolumnie klienta obie liczby są trywialnie równe, a czytający
        # wyciągnąłby wniosek „każdy etap kończy się w miesiącu, w którym się zaczął".
        # Reszta wyniku — granice zakresu, miesiące bez zdarzeń — zostaje prawdziwa.
        comparison_pairs=(
            ComparisonPair(
                fields=("start", "end"),
                determines=Determines.OBSERVATION,
                # Granice zakresu są prawdziwe niezależnie od tego, czy oba znaczniki
                # pochodzą z jednej kolumny: min i max nadal opisują rzeczywisty zakres
                # danych. A-01 wymienia je wprost jako to, co kontroli 8 WOLNO zwracać:
                # „period_min = min(start), period_max = max(end) oraz rozpiętość między
                # nimi — to jest zakres danych, a nie przypisanie". Wyjątek ma podstawę
                # w rozstrzygnięciu, nie w wygodzie.
                unaffected_measures=("period_min", "period_max"),
            ),
        ),
    )

    def run(self, context: ValidationContext) -> CheckOutcome:
        if context.frame.empty:
            return CheckOutcome(
                status=ValidationStatus.PASS,
                basis=(
                    f"Tabela {context.table_name} nie zawiera wierszy przyjętych, "
                    "więc nie ma zakresu do opisania."
                ),
                observations=(self._time_basis(context),),
            )
        if context.table.TIME_GRAIN is TimeGrain.EVENT:
            return self._zdarzeniowa(context)
        return self._okresowa(context)

    def _time_basis(self, context: ValidationContext) -> CheckObservation:
        """Obserwacja o podstawie przypisania — zawsze pusta, zawsze z podstawą."""
        zdarzeniowa = context.table.TIME_GRAIN is TimeGrain.EVENT
        return CheckObservation.create(
            subject=", ".join(context.table.TIME_FIELDS),
            measure="time_basis_used",
            text_value=None,
            basis=(
                PODSTAWA_TIME_BASIS_EVENT if zdarzeniowa else PODSTAWA_TIME_BASIS_PERIOD
            ),
        )

    # --- tabele okresowe -------------------------------------------------------------

    def _okresowa(self, context: ValidationContext) -> CheckOutcome:
        pole = context.table.TIME_FIELDS[0]
        kolumna = context.frame[pole]
        znane = kolumna[kolumna.notna()]
        if znane.empty:
            return CheckOutcome(
                status=ValidationStatus.WARNING,
                basis=(
                    f"Żaden wiersz tabeli {context.table_name} nie ma wartości pola "
                    f"{pole}, więc zakres czasowy jest nieznany."
                ),
                observations=(self._time_basis(context),),
            )

        okresy = _okresy(kolumna)
        pelny = pd.period_range(okresy.min(), okresy.max(), freq="M")
        pokryte = set(okresy.unique())
        brakujace = [okres for okres in pelny if okres not in pokryte]

        obserwacje = [
            CheckObservation.create(
                subject=pole,
                measure="period_min",
                text_value=str(znane.min()),
                basis=f"Najwcześniejsza wartość pola {pole} wśród wierszy przyjętych.",
            ),
            CheckObservation.create(
                subject=pole,
                measure="period_max",
                text_value=str(znane.max()),
                basis=f"Najpóźniejsza wartość pola {pole} wśród wierszy przyjętych.",
            ),
            CheckObservation.create(
                subject=pole,
                measure="months_in_range",
                value=float(len(pelny)),
                basis="Liczba miesięcy między najwcześniejszym a najpóźniejszym okresem.",
            ),
            CheckObservation.create(
                subject=pole,
                measure="months_covered",
                value=float(len(pokryte)),
                basis="Liczba miesięcy, w których jest co najmniej jeden wiersz.",
            ),
            CheckObservation.create(
                subject=pole,
                measure="months_missing",
                value=float(len(brakujace)),
                basis=(
                    "Miesiące w zakresie bez żadnego wiersza. W tabeli okresowej brak "
                    "miesiąca jest luką w danych, a nie miesiącem bez zdarzeń."
                ),
            ),
            self._time_basis(context),
        ]
        obserwacje += [
            CheckObservation.create(
                subject=str(okres),
                measure="month_without_data",
                # Zero jest tu wiedzą, a nie brakiem: wiemy, że w tym miesiącu nie ma
                # ani jednego wiersza przyjętego.
                value=0.0,
                basis=f"Miesiąc {okres} mieści się w zakresie, ale nie ma w nim wierszy.",
            )
            for okres in brakujace
        ]

        if not brakujace:
            return CheckOutcome(
                status=ValidationStatus.PASS,
                basis=(
                    f"Tabela {context.table_name} pokrywa {len(pokryte)} kolejnych "
                    f"miesięcy od {okresy.min()} do {okresy.max()}, bez luk."
                ),
                observations=cap_observations(
                    obserwacje, subject=pole, basis="Opis zakresu czasowego."
                ),
            )

        return CheckOutcome(
            status=ValidationStatus.WARNING,
            basis=(
                f"Tabela {context.table_name} obejmuje {len(pelny)} miesięcy od "
                f"{okresy.min()} do {okresy.max()}, z czego {len(brakujace)} nie ma "
                "żadnego wiersza. W tabeli okresowej brakujący miesiąc jest luką "
                "w danych."
            ),
            observations=cap_observations(
                obserwacje,
                subject="month_without_data",
                basis=f"Miesiące bez danych w tabeli {context.table_name}.",
            ),
        )

    # --- tabela zdarzeniowa ----------------------------------------------------------

    def _zdarzeniowa(self, context: ValidationContext) -> CheckOutcome:
        ramka = context.frame
        poczatki = ramka[context.table.TIME_FIELDS[0]]
        konce = ramka[context.table.TIME_FIELDS[1]]
        okresy_poczatkow = _okresy(poczatki)
        okresy_koncow = _okresy(konce)

        obserwacje: list[CheckObservation] = []
        if len(okresy_poczatkow):
            obserwacje.append(
                CheckObservation.create(
                    subject=context.table.TIME_FIELDS[0],
                    measure="period_min",
                    text_value=str(poczatki[poczatki.notna()].min()),
                    basis=(
                        "Najwcześniejszy znacznik początku etapu. To granica **zakresu "
                        "danych**, a nie przypisanie sprawy do okresu."
                    ),
                )
            )
        if len(okresy_koncow):
            obserwacje.append(
                CheckObservation.create(
                    subject=context.table.TIME_FIELDS[1],
                    measure="period_max",
                    text_value=str(konce[konce.notna()].max()),
                    basis=(
                        "Najpóźniejszy znacznik końca etapu. Granica zakresu danych, "
                        "nie przypisanie."
                    ),
                )
            )

        obserwacje.append(
            CheckObservation.create(
                subject=context.table.TIME_FIELDS[0],
                measure="months_with_stage_starts",
                value=float(okresy_poczatkow.nunique()),
                basis=(
                    "Miesiące, w których rozpoczął się co najmniej jeden etap. Liczone "
                    "po znaczniku początku, bez przypisywania sprawy do okresu."
                ),
            )
        )
        obserwacje.append(
            CheckObservation.create(
                subject=context.table.TIME_FIELDS[1],
                measure="months_with_stage_ends",
                value=float(okresy_koncow.nunique()),
                basis=(
                    "Miesiące, w których zakończył się co najmniej jeden etap. Liczone "
                    "osobno od początków: wiersz PROCESS jest odcinkiem, nie punktem, "
                    "więc wybór jednej z granic byłby wyborem podstawy zakazanym "
                    "przez A-01."
                ),
            )
        )
        obserwacje.append(self._time_basis(context))

        # Miesiące bez zdarzeń liczymy w zakresie wyznaczonym przez oba znaczniki.
        wszystkie = okresy_poczatkow.union(okresy_koncow)
        if len(wszystkie):
            pelny = pd.period_range(wszystkie.min(), wszystkie.max(), freq="M")
            puste = [okres for okres in pelny if okres not in set(wszystkie)]
            obserwacje.append(
                CheckObservation.create(
                    subject="zakres zdarzeń",
                    measure="months_without_events",
                    value=float(len(puste)),
                    basis=(
                        "Miesiące bez żadnego znacznika. W tabeli zdarzeniowej to "
                        "**obserwacja, nie luka**: może to być miesiąc, w którym "
                        "faktycznie nic nie przyszło, a bez referencji nie da się tych "
                        "dwóch sytuacji rozróżnić."
                    ),
                )
            )

        return CheckOutcome(
            status=ValidationStatus.PASS,
            basis=(
                f"Tabela {context.table_name} jest zdarzeniowa. Opisujemy zakres danych "
                "i pokrycie miesięczne obu znaczników osobno; sprawy nie są przypisywane "
                "do miesięcy, bo podstawa przypisania nie jest rozstrzygnięta (A-01)."
            ),
            observations=cap_observations(
                obserwacje,
                subject="zakres zdarzeń",
                basis=f"Opis zakresu czasowego tabeli {context.table_name}.",
            ),
        )
