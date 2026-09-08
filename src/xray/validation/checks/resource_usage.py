# Implementuje ZOP-TECH-01 v0.1 pkt 5.3, kontrola 7 — nielogiczne wykorzystanie zasobu.
"""Kontrola 7: ``used`` większe od ``available``.

## Dlaczego to sygnał, a nie błąd

ZOP-XR-CAP-01 v1.0 rozdz. 5 jest tu jednoznaczna: **„Przekroczenie nie jest automatycznie
błędem logicznym."** Najpierw sprawdza się udokumentowaną dodatkową zdolność — nadgodziny,
dodatkową zmianę, pracę ponad plan, czasowo uruchomiony zasób lub inną udokumentowaną
przyczynę.

Tej informacji **w wierszu nie ma**: mieszka w rozszerzeniu ``documented_extra_capacity``,
którego kontrakt bazowy nie zawiera. Kontrola nie może więc rozstrzygnąć, czy przekroczenie
jest błędem, i tego nie udaje.

Karta przewiduje dwie drogi (CAP-01 rozdz. 5):

- dodatkowa zdolność udokumentowana → ``effective_available = available_source +
  documented_extra_capacity``, czyli przekroczenia w ogóle nie ma,
- przyczyna nieudokumentowana → **nie korygować po cichu**; ``validation_required = true``
  i skierowanie do CAP-02.

Fundament ogłasza sygnał z podstawą, a rozstrzygnięcie zostawia karcie, która zna
``documented_extra_capacity``. Stąd ``max_status = WARNING``; wariant CRITICAL pojawia się
dopiero w CAP-01 VAL-13.
"""

from typing import ClassVar

from xray.model.enums import ValidationStatus
from xray.validation.base import CheckDeclaration, ComparisonPair, DataCheck, Determines
from xray.validation.context import ValidationContext
from xray.validation.results import CheckObservation, CheckOutcome


class ResourceUsage(DataCheck):
    """Zgłasza wiersze, w których wykorzystanie przekracza dostępność."""

    DECLARATION: ClassVar[CheckDeclaration] = CheckDeclaration(
        check_id="TECH01-VAL-07",
        control_number=7,
        title="Nielogiczne wykorzystanie zasobu",
        requires_import_report=False,
        # Kontrola dotyczy tych pól, a nie „tabeli RESOURCE". Gdyby rozszerzenie z karty
        # wprowadziło je gdzie indziej, zadziała bez zmiany.
        required_fields=("available", "used"),
        max_status=ValidationStatus.WARNING,
        # Różnica tych dwóch pól JEST tą kontrolą. Gdy pochodzą z jednej kolumny klienta,
        # są sobie zawsze równe i kontrola wypisywałaby PASS przy każdym przebiegu —
        # fałszywe przejście wpuszczone przez konfigurację.
        comparison_pairs=(
            ComparisonPair(fields=("available", "used"), determines=Determines.STATUS),
        ),
    )

    def run(self, context: ValidationContext) -> CheckOutcome:
        ramka = context.frame
        dostepne = ramka["available"]
        uzyte = ramka["used"]

        # Porównujemy wyłącznie wiersze, w których obie wartości są znane. Brak jednej
        # z nich nie jest przekroczeniem — jest brakiem, który zgłasza kontrola 3.
        porownywalne = dostepne.notna() & uzyte.notna()
        przekroczone = porownywalne & (uzyte > dostepne)
        liczba = int(przekroczone.sum())
        nieporownywalne = int((~porownywalne).sum())

        obserwacje: list[CheckObservation] = []
        if liczba:
            obserwacje.append(
                CheckObservation.create(
                    subject="used > available",
                    measure="usage_above_capacity",
                    value=float(liczba),
                    basis=(
                        "Wiersze, w których wykorzystanie przekracza dostępność. "
                        "ZOP-XR-CAP-01 rozdz. 5: przekroczenie nie jest automatycznie "
                        "błędem logicznym — mogła istnieć udokumentowana dodatkowa "
                        "zdolność, o której wiersz nic nie wie."
                    ),
                    evidence_row_ids=tuple(str(i) for i in ramka.index[przekroczone]),
                )
            )
        if nieporownywalne:
            obserwacje.append(
                CheckObservation.create(
                    subject="available albo used",
                    measure="rows_not_comparable",
                    value=float(nieporownywalne),
                    basis=(
                        "Wiersze, w których brakuje jednej z wartości, więc porównanie "
                        "nie było możliwe. Brak nie jest przekroczeniem — zgłasza go "
                        "kontrola 3."
                    ),
                    evidence_row_ids=tuple(str(i) for i in ramka.index[~porownywalne]),
                )
            )

        if liczba == 0:
            return CheckOutcome(
                status=ValidationStatus.PASS,
                basis=(
                    f"W tabeli {context.table_name} wykorzystanie nie przekracza "
                    f"dostępności w żadnym z {int(porownywalne.sum())} porównywalnych "
                    "wierszy."
                ),
                observations=tuple(obserwacje),
            )

        return CheckOutcome(
            status=ValidationStatus.WARNING,
            basis=(
                f"{liczba} wierszy tabeli {context.table_name} ma wykorzystanie powyżej "
                "dostępności. Sygnał do wyjaśnienia: udokumentowana dodatkowa zdolność "
                "znosi przekroczenie, a nieudokumentowana kieruje do CAP-02. Fundament "
                "nie koryguje wartości po cichu."
            ),
            observations=tuple(obserwacje),
        )
