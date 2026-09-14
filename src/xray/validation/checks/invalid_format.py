# Implementuje ZOP-TECH-01 v0.1 pkt 5.3, kontrola 2 — nieprawidłowy format.
"""Kontrola 2: wiersze utracone, bo wartości nie dało się przetłumaczyć na kontrakt.

Rozpoznanie należy do modelu — to on odrzuca tekst w polu liczbowym, datę podaną liczbą
i znacznik czasu ze strefą. **Raportowanie** należy tutaj, bo wynik odrzucenia żyje
w raporcie importu, a nie w ramce: wiersz odrzucony nigdy nie dostał ``row_id``.

Kategorię odrzucenia bierzemy z ``Rejection.category``, czyli z **kodu błędu**
podniesionego przez walidator kontraktu. Parsowanie polskiego komunikatu byłoby wiązaniem
kontroli z treścią, która nie jest kontraktem.

## Dwie miary, nie jedna

| Kategoria odrzucenia | Rozmowa z klientem |
| --- | --- |
| ``invalid_format`` | „popraw zapis wartości" |
| ``missing_timezone_declaration`` | „uzupełnij strefę w profilu" |

Miara obserwacji to ``rows_rejected_`` + kategoria.

Znacznik ze strefą bez deklaracji strefy nie jest błędem zapisu — wartość jest poprawna,
brakuje deklaracji, która pozwoliłaby ją przeliczyć (wpis DT-05). Dlatego osobna miara,
a nie wspólny worek. Ale **wiersz jest utracony** dokładnie tak samo, więc zgłasza go ta
sama kontrola: gdyby nie zgłaszała go żadna, raport jakości danych pokazywałby mniej
utraconych wierszy, niż jest.

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

_MIARY: dict[RejectionCategory, tuple[str, str]] = {
    RejectionCategory.INVALID_FORMAT: (
        "rows_rejected_invalid_format",
        "nie dała się przetłumaczyć na zadeklarowany typ",
    ),
    RejectionCategory.MISSING_TIMEZONE_DECLARATION: (
        "rows_rejected_missing_timezone_declaration",
        "jest znacznikiem czasu ze strefą, a profil nie zadeklarował strefy organizacji",
    ),
}
"""Kategoria odrzucenia → (miara, opis przyczyny). Kolejność jest kolejnością obserwacji."""


class InvalidFormat(DataCheck):
    """Zlicza wiersze odrzucone, bo wartości nie dało się przetłumaczyć na kontrakt."""

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
        obserwacje: list[CheckObservation] = []

        for kategoria, (miara, przyczyna) in _MIARY.items():
            # Grupujemy po polu, bo klient poprawia kolumnę, a nie pojedynczy wiersz.
            # Kolejność pól bierze się z kontraktu, a nie z kolejności napotkania — inaczej
            # dwa przebiegi na tych samych danych mogłyby dać inną kolejność obserwacji.
            adresy: dict[str, list[tuple[str, int]]] = {
                pole: [] for pole in context.table.model_fields
            }
            bez_pola: list[tuple[str, int]] = []
            for raport in raporty:
                for odrzucenie in raport.rejections:
                    if odrzucenie.category is not kategoria:
                        continue
                    adres = (raport.source.source_id, odrzucenie.file_row)
                    if odrzucenie.fields:
                        for pole in odrzucenie.fields:
                            adresy.setdefault(pole, []).append(adres)
                    else:
                        bez_pola.append(adres)

            obserwacje += [
                CheckObservation.create(
                    subject=pole,
                    measure=miara,
                    value=float(len(lista)),
                    basis=(
                        f"Wiersze odrzucone przy bramce kontraktu, bo wartość pola {pole} "
                        f"{przyczyna}."
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
                        measure=miara,
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
                    f"z powodu formatu wartości ani braku deklaracji strefy "
                    f"({len(raporty)} raport importu)."
                ),
            )

        return CheckOutcome(
            status=ValidationStatus.WARNING,
            basis=(
                f"{razem} wierszy tabeli {context.table_name} nie weszło do kontraktu "
                "z powodu formatu wartości albo braku deklaracji strefy organizacji. "
                "Rekordy te nie istnieją w danych; czy ich brak zatrzymuje analizę, "
                "rozstrzyga test."
            ),
            observations=tuple(obserwacje),
        )
