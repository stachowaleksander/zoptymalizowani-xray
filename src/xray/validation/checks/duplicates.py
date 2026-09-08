# Implementuje ZOP-TECH-01 v0.1 pkt 5.3, kontrola 4 — duplikaty.
"""Kontrola 4: powtórzone wartości klucza naturalnego.

Klucz naturalny chroni przed podwójnym liczeniem — ZOP-XR-FIN-01 pkt 2.1: „revenue
i amount są sumowane wyłącznie po poprawnie zdefiniowanych kluczach". Powtórzona wartość
klucza znaczy, że ta sama rzecz może wejść do sumy dwa razy.

## Dlaczego dla tabel zdarzeniowych limit jest łagodniejszy

Dla tabel okresowych powtórzony klucz jest wprost zagrożeniem: ``date + unit + category``
ma wskazywać jeden rekord. Dla tabeli zdarzeniowej jest inaczej — ZOP-XR-PROC-02 pkt 2.4
wprowadza rozszerzenie ``repeat_visit`` na powroty przypadku do tego samego etapu.
Do czasu implementacji PROC-02 powtórzone przejście przez ten sam etap jest **oczekiwane**,
a nie błędne, więc kontrola może je najwyżej zgłosić jako sygnał.

Limit jest modulowany po ``TIME_GRAIN``, a nie po nazwie tabeli: gdyby powstała druga
tabela zdarzeniowa, odwzorowanie po nazwie po cichu nadałoby jej CRITICAL.

## Czego kontrola nie robi

Nie usuwa duplikatów, nie scala ich i nie wybiera „właściwego" wiersza. Ogłasza status
i pokazuje dowód; co z tym zrobić, rozstrzyga test albo klient.
"""

from typing import ClassVar

from xray.model.enums import TimeGrain, ValidationStatus
from xray.validation.base import CheckDeclaration, DataCheck
from xray.validation.context import ValidationContext
from xray.validation.results import CheckObservation, CheckOutcome, cap_observations


class DuplicateRows(DataCheck):
    """Wykrywa powtórzone wartości klucza naturalnego."""

    DECLARATION: ClassVar[CheckDeclaration] = CheckDeclaration(
        check_id="TECH01-VAL-04",
        control_number=4,
        title="Duplikaty",
        requires_import_report=False,
        required_fields=(),
        requires_natural_key=True,
        max_status=ValidationStatus.CRITICAL,
        # Rozstrzygnięcie A-01 i ZOP-XR-PROC-02 pkt 2.4: w danych zdarzeniowych powrót
        # do tego samego etapu jest oczekiwany do czasu wprowadzenia repeat_visit.
        max_status_by_time_grain={TimeGrain.EVENT: ValidationStatus.WARNING},
    )

    def run(self, context: ValidationContext) -> CheckOutcome:
        ramka = context.frame
        klucz = list(context.table.NATURAL_KEY)
        limit = self.DECLARATION.effective_max_status(context.table)

        if ramka.empty:
            return CheckOutcome(
                status=ValidationStatus.PASS,
                basis=(
                    f"Tabela {context.table_name} nie zawiera wierszy przyjętych, "
                    "więc nie ma czego porównywać."
                ),
            )

        # Klucz porównujemy jako napisy: kolumny klucza mogą mieć różne typy (data,
        # tekst), a chodzi o tożsamość wartości, nie o arytmetykę.
        zestaw = ramka[klucz].astype(str)
        powtorzone = zestaw.duplicated(keep=False)
        liczba_wierszy = int(powtorzone.sum())

        if liczba_wierszy == 0:
            return CheckOutcome(
                status=ValidationStatus.PASS,
                basis=(
                    f"Żadna wartość klucza {' + '.join(klucz)} nie powtarza się wśród "
                    f"{len(ramka)} wierszy przyjętych."
                ),
            )

        obserwacje: list[CheckObservation] = []
        # Kolejność grup bierze się z kolejności pierwszego wystąpienia w indeksie —
        # deterministycznie, bez sortowania zależnego od zawartości.
        grupy = zestaw[powtorzone].groupby(klucz, sort=False)
        for wartosc, grupa in grupy:
            etykieta = " | ".join(str(czesc) for czesc in wartosc)
            obserwacje.append(
                CheckObservation.create(
                    subject=etykieta,
                    measure="duplicate_rows",
                    value=float(len(grupa)),
                    basis=(
                        f"Wartość klucza {' + '.join(klucz)} występuje {len(grupa)} razy."
                    ),
                    evidence_row_ids=tuple(str(row_id) for row_id in grupa.index),
                )
            )

        if context.table.TIME_GRAIN is TimeGrain.EVENT:
            podstawa = (
                f"{liczba_wierszy} z {len(ramka)} wierszy dzieli wartość klucza "
                f"{' + '.join(klucz)} w {len(obserwacje)} grupach. Tabela jest "
                "zdarzeniowa: powrót do tego samego etapu jest oczekiwany do czasu "
                "wprowadzenia repeat_visit z ZOP-XR-PROC-02 pkt 2.4, więc kontrola "
                "zgłasza sygnał, a nie błąd."
            )
        else:
            podstawa = (
                f"{liczba_wierszy} z {len(ramka)} wierszy dzieli wartość klucza "
                f"{' + '.join(klucz)} w {len(obserwacje)} grupach. Klucz ma wskazywać "
                "jeden rekord, więc powtórzenie grozi podwójnym liczeniem "
                "(ZOP-XR-FIN-01 pkt 2.1)."
            )

        return CheckOutcome(
            status=limit,
            basis=podstawa,
            observations=cap_observations(
                obserwacje,
                subject="duplicate_rows",
                basis=(
                    f"Grupy powtórzonych wartości klucza {' + '.join(klucz)} w tabeli "
                    f"{context.table_name}."
                ),
            ),
        )
