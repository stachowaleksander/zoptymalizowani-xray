# Implementuje ZOP-TECH-01 v0.1 pkt 5.3, kontrola 2 — nieprawidłowy format.
"""Kontrola 2: wiersze utracone z powodu wartości nieprzetłumaczalnej na typ.

Rozpoznanie należy do modelu — to on odrzuca tekst w polu liczbowym, datę podaną liczbą
i znacznik czasu ze strefą. **Raportowanie** należy tutaj, bo wynik odrzucenia żyje
w raporcie importu, a nie w ramce: wiersz odrzucony nigdy nie dostał ``row_id``.

Kategorię odrzucenia bierzemy z ``Rejection.category``, czyli z **kodu błędu**
podniesionego przez walidator kontraktu. Parsowanie polskiego komunikatu byłoby wiązaniem
kontroli z treścią, która nie jest kontraktem.

## Dlaczego WARNING, a nie CRITICAL

Utrata wierszy jest faktem wartym zgłoszenia, ale czy zatrzymuje analizę, rozstrzyga test.
Dziesięć wierszy o złym formacie daty zatrzyma test badający trend miesięczny i nie
zmieni nic dla testu liczącego udziały w jednym okresie.
"""

from typing import ClassVar

from xray.ingest.report import RejectionCategory
from xray.model.enums import ValidationStatus
from xray.validation.base import CheckDeclaration, DataCheck
from xray.validation.context import ValidationContext
from xray.validation.results import CheckObservation, CheckOutcome


class InvalidFormat(DataCheck):
    """Zlicza wiersze odrzucone z powodu nieprawidłowego formatu wartości."""

    DECLARATION: ClassVar[CheckDeclaration] = CheckDeclaration(
        check_id="TECH01-VAL-02",
        control_number=2,
        title="Nieprawidłowy format danych",
        # Odrzucenia istnieją wyłącznie w raporcie importu — w ramce ich nie ma.
        requires_import_report=True,
        max_status=ValidationStatus.WARNING,
    )

    def run(self, context: ValidationContext) -> CheckOutcome:
        raporty = context.import_reports or ()

        # Grupujemy po polu, bo klient poprawia kolumnę, a nie pojedynczy wiersz.
        # Kolejność pól bierze się z kontraktu, a nie z kolejności napotkania — inaczej
        # dwa przebiegi na tych samych danych mogłyby dać inną kolejność obserwacji.
        adresy: dict[str, list[tuple[str, int]]] = {
            pole: [] for pole in context.table.model_fields
        }
        bez_pola: list[tuple[str, int]] = []
        for raport in raporty:
            for odrzucenie in raport.rejections:
                if odrzucenie.category is not RejectionCategory.INVALID_FORMAT:
                    continue
                adres = (raport.source.source_id, odrzucenie.file_row)
                if odrzucenie.fields:
                    for pole in odrzucenie.fields:
                        adresy.setdefault(pole, []).append(adres)
                else:
                    bez_pola.append(adres)

        obserwacje = [
            CheckObservation.create(
                subject=pole,
                measure="rows_rejected_invalid_format",
                value=float(len(lista)),
                basis=(
                    f"Wiersze odrzucone przy bramce kontraktu, bo wartość pola {pole} "
                    "nie dała się przetłumaczyć na zadeklarowany typ."
                ),
                evidence_source_rows=tuple(lista),
            )
            for pole, lista in adresy.items()
            if lista
        ]
        if bez_pola:
            obserwacje.append(
                CheckObservation.create(
                    subject="rekord",
                    measure="rows_rejected_invalid_format",
                    value=float(len(bez_pola)),
                    basis="Wiersze odrzucone bez wskazania konkretnego pola.",
                    evidence_source_rows=tuple(bez_pola),
                )
            )

        razem = sum(int(o.value or 0) for o in obserwacje)
        if razem == 0:
            return CheckOutcome(
                status=ValidationStatus.PASS,
                basis=(
                    f"Żaden wiersz tabeli {context.table_name} nie został odrzucony "
                    f"z powodu formatu wartości ({len(raporty)} raport importu)."
                ),
            )

        return CheckOutcome(
            status=ValidationStatus.WARNING,
            basis=(
                f"{razem} wierszy tabeli {context.table_name} nie weszło do kontraktu "
                "z powodu formatu wartości. Rekordy te nie istnieją w danych; czy ich "
                "brak zatrzymuje analizę, rozstrzyga test."
            ),
            observations=tuple(obserwacje),
        )
