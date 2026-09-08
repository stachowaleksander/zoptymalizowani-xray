# Implementuje ZOP-TECH-01 v0.1 pkt 5.3, kontrola 3 — brakujące wartości.
"""Kontrola 3: obraz braków w tabeli.

## Dwie liczby, których nie wolno zsumować

| Zjawisko | Miara | Skąd | Co znaczy |
| --- | --- | --- | --- |
| pusta komórka | ``missing_values`` | ramka | rekord istnieje, pole jest puste |
| wiersz utracony | ``rows_rejected_missing_key`` | raport importu | rekordu nie ma |

To nie są dwa pomiary tej samej rzeczy. „Trzydzieści braków", z czego dziesięć to puste
komórki, a dwadzieścia to utracone wiersze, wprowadzałoby w błąd bardziej niż brak liczby.
Dlatego są to dwie obserwacje o różnych nazwach, a w wyniku nie istnieje żadne pole
zbiorcze, w którym dałoby się je dodać. Ta sama zasada, co przy ``impact_group_id``
w ZOP-PRI-01: nie dodajemy rzeczy nieaddytywnych.

## Trzecia rzecz, której to nie jest

Kolumna **nieobecna** w pliku to kontrola 1 (``mapping/``, CRITICAL). Kolumna obecna
i pusta w całości to kontrola 3. Różne przyczyny i różne działania klienta: „dostarcz
kolumnę" wobec „wyjaśnij braki".

## Dlaczego status PASS

Sam brak wartości nie jest błędem — pole dopuszczające pustą wartość ma prawo być puste.
Kontrola zwraca **obraz braków z podstawą, a nie ocenę**. To test deklaruje, czy brak
w danym polu go blokuje: ZOP-XR-FIN-01 VAL-01 i VAL-02 mówią o braku danych przychodowych
i kosztowych, a nie o pustych komórkach w ogóle.
"""

from typing import ClassVar

from xray.ingest.report import RejectionCategory
from xray.model.enums import ValidationStatus
from xray.validation.base import CheckDeclaration, DataCheck
from xray.validation.context import ValidationContext
from xray.validation.results import CheckObservation, CheckOutcome


class MissingValues(DataCheck):
    """Zlicza puste wartości w polach i wiersze utracone z powodu braku w kluczu."""

    DECLARATION: ClassVar[CheckDeclaration] = CheckDeclaration(
        check_id="TECH01-VAL-03",
        control_number=3,
        title="Brakujące wartości",
        # Bez raportu importu widać wyłącznie braki w wierszach przyjętych — a wiersz
        # z pustym elementem klucza nigdy do ramki nie trafił.
        requires_import_report=True,
        # Kontrola liczy braki w każdym polu, więc nie wymaga żadnego konkretnego.
        required_fields=(),
        requires_natural_key=True,
        # Obraz braków nie jest oceną: to test rozstrzyga, czy brak go blokuje.
        max_status=ValidationStatus.PASS,
    )

    def run(self, context: ValidationContext) -> CheckOutcome:
        obserwacje: list[CheckObservation] = []
        ramka = context.frame
        klucz = set(context.table.NATURAL_KEY)

        # 1. Puste komórki w wierszach przyjętych — fakt o danych.
        for pole in context.table.model_fields:
            kolumna = ramka[pole]
            puste = kolumna.isna()
            liczba = int(puste.sum())
            wiersze = tuple(str(row_id) for row_id in ramka.index[puste])
            w_kluczu = pole in klucz
            obserwacje.append(
                CheckObservation.create(
                    subject=pole,
                    measure="missing_values",
                    value=float(liczba),
                    basis=(
                        f"Puste wartości pola {pole} wśród {len(ramka)} wierszy "
                        "przyjętych."
                        + (
                            " Pole należy do klucza naturalnego, więc pusta wartość nie "
                            "przeszłaby bramki kontraktu — brak tutaj oznaczałby błąd "
                            "bramki."
                            if w_kluczu
                            else ""
                        )
                    ),
                    evidence_row_ids=wiersze,
                )
            )

        # 2. Wiersze utracone przy bramce — fakt o imporcie, nie o danych w ramce.
        raporty = context.import_reports or ()
        utracone: list[tuple[str, int]] = []
        for raport in raporty:
            for odrzucenie in raport.rejections:
                if odrzucenie.category is RejectionCategory.MISSING_VALUE:
                    utracone.append((raport.source.source_id, odrzucenie.file_row))

        obserwacje.append(
            CheckObservation.create(
                subject=", ".join(context.table.NATURAL_KEY),
                measure="rows_rejected_missing_key",
                value=float(len(utracone)),
                basis=(
                    f"Wiersze odrzucone przy bramce kontraktu z powodu braku wartości, "
                    f"z {len(raporty)} raportu importu. Rekordy te nie istnieją "
                    "w kontrakcie i nie są tą samą wielkością co puste komórki."
                ),
                evidence_source_rows=tuple(utracone),
            )
        )

        return CheckOutcome(
            status=ValidationStatus.PASS,
            basis=(
                f"Obraz braków dla tabeli {context.table_name}: {len(ramka)} wierszy "
                f"przyjętych, {len(utracone)} odrzuconych z powodu braku wartości. "
                "Kontrola nie ocenia, czy brak jest dopuszczalny — to rozstrzyga test."
            ),
            observations=tuple(obserwacje),
        )
