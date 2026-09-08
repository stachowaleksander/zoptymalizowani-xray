# Implementuje ZOP-TECH-01 v0.1 pkt 5.3, kontrola 5 — wartości podejrzane.
"""Kontrola 5: wartości ujemne w polach liczbowych.

## Czego kontrola nie rozstrzyga

Kontrola 5 z pkt 5.3 mówi o wartości ujemnej „jeżeli nie została oznaczona jako korekta".
Kontrakt danych **nie ma pola pozwalającego na takie oznaczenie** — i decyzją Michała
z 2026-09-05 (wpis B-01) mieć go nie będzie. Kontrola nie może więc rozstrzygnąć, czy
ujemna kwota jest korektą, czy błędem, i tego nie udaje: zgłasza sygnał z jawną podstawą.

Stąd ``max_status = WARNING``. Ujemny koszt bywa poprawnym zapisem korekty w danych
klienta; uznanie go za CRITICAL byłoby regułą, której żadna karta nie stawia.

Ta sama zasada dotyczy ujemnego ``available`` i ``used``: ZOP-XR-CAP-01 VAL-04 i VAL-05
nazywają je CRITICAL, ale to CRITICAL **karty CAP-01**, nadawany z jej wiedzą. Fundament
ogłasza sygnał, a CAP-01 rozstrzygnie, co on dla niej znaczy.

## Dlaczego wszystkie pola liczbowe

Kontrola bada pola wybrane po **właściwości** (typ liczbowy), a nie po nazwie. Lista nazw
byłaby zapisaniem dzisiejszego kontraktu jako reguły i przegapiłaby pole dodane później.
"""

from typing import ClassVar

from xray.model.enums import ValidationStatus
from xray.model.tables.base import numeric_fields
from xray.validation.base import CheckDeclaration, DataCheck
from xray.validation.context import ValidationContext
from xray.validation.results import CheckObservation, CheckOutcome, NotAssessedReason


class SuspiciousValues(DataCheck):
    """Zgłasza wartości ujemne w polach liczbowych jako sygnał, nie jako błąd."""

    DECLARATION: ClassVar[CheckDeclaration] = CheckDeclaration(
        check_id="TECH01-VAL-05",
        control_number=5,
        title="Wartości podejrzane",
        requires_import_report=False,
        # Deklaracja nie umie powiedzieć „dowolne pole liczbowe" — umie wskazać pola po
        # nazwie. Stosowalność po typie rozstrzyga więc sama kontrola, poniżej.
        required_fields=(),
        max_status=ValidationStatus.WARNING,
    )

    def run(self, context: ValidationContext) -> CheckOutcome:
        pola = numeric_fields(context.table)
        if not pola:
            return CheckOutcome(
                status=None,
                basis=(
                    f"Tabela {context.table_name} nie ma pól liczbowych, więc nie ma "
                    "czego badać. To nie to samo co brak wartości podejrzanych."
                ),
                not_assessed_reason=NotAssessedReason.NOT_APPLICABLE,
            )

        ramka = context.frame
        obserwacje: list[CheckObservation] = []
        razem = 0
        for pole in pola:
            kolumna = ramka[pole]
            ujemne = kolumna.notna() & (kolumna < 0)
            liczba = int(ujemne.sum())
            razem += liczba
            if liczba:
                obserwacje.append(
                    CheckObservation.create(
                        subject=pole,
                        measure="negative_values",
                        value=float(liczba),
                        basis=(
                            f"Wartości ujemne pola {pole}. Kontrakt nie ma pola "
                            "oznaczenia korekty (wpis B-01), więc kontrola nie "
                            "rozstrzyga, czy to korekta, czy błąd."
                        ),
                        evidence_row_ids=tuple(str(i) for i in ramka.index[ujemne]),
                    )
                )

        if razem == 0:
            return CheckOutcome(
                status=ValidationStatus.PASS,
                basis=(
                    f"Żadne z pól liczbowych {', '.join(pola)} tabeli "
                    f"{context.table_name} nie zawiera wartości ujemnej."
                ),
            )

        return CheckOutcome(
            status=ValidationStatus.WARNING,
            basis=(
                f"{razem} wartości ujemnych w tabeli {context.table_name}. "
                "Sygnał do wyjaśnienia z klientem: wartość ujemna bywa poprawnym zapisem "
                "korekty. Kontrola nie klasyfikuje jej ani jako błędu, ani jako korekty."
            ),
            observations=tuple(obserwacje),
        )
