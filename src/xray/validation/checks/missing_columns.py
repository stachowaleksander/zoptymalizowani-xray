# Implementuje ZOP-TECH-01 v0.1 pkt 5.3, kontrola 1 — brak wymaganej kolumny.
"""Kontrola 1: pola kontraktu, dla których w pliku nie było kolumny.

## Dwa stany, nie trzy

| Czego brakuje | Status | Dlaczego |
| --- | --- | --- |
| element ``NATURAL_KEY`` | CRITICAL | bez niego nie da się odpowiedzialnie zidentyfikować rekordu |
| dowolne inne pole | PASS + obserwacja | walidator nie wie, który test się uruchomi |

**Nie ma gałęzi WARNING** — i to jest rozstrzygnięcie, nie uproszczenie.

Wcześniejsza wersja dawała WARNING za brak każdego pola spoza klucza. Michał to odrzucił
(rozstrzygnięcie B-06): to, czy brak pola jest ograniczeniem, zależy od tego, **który test
się uruchomi**. Walidator tego nie wie, więc nadając WARNING orzekałby o ciężarze, którego
nie zna.

> „Walidator danych ogłasza stan danych, ale nie przejmuje metodologicznej
> odpowiedzialności testu diagnostycznego. To konsument informacji wie, czy dane pole jest
> konieczne do wydania określonego twierdzenia."

**PASS nie jest tu fałszywym przejściem.** Fakt braku kolumny jest w wyniku — jako
obserwacja z podstawą, tylko nie jako status. To sprowadza kontrolę 1 do tego samego
gatunku co kontrola 3: **obraz, nie werdykt**.

Ciężar nadaje odbiorca. Test, który potrzebuje brakującego pola, **nie może udawać
wyniku** — zwraca ``not_assessable`` albo ``TEST_PARTIAL`` / ``TEST_BLOCKED``. Brak
ogranicza ten test, a nie cały przebieg.

**Odczytanie kryterium strukturalnego:** Michał pisze „nie potrafimy odpowiedzialnie
zidentyfikować rekordu **albo** zachować podstawowego kontraktu tabeli". Przykładamy to
tak: COST bez kolumny ``amount`` **nie** łamie podstawowego kontraktu tabeli — wiersz nadal
identyfikuje komórkę (miesiąc, jednostka, kategoria), której wartość jest nieznana,
a ``null`` jest poprawnym wynikiem (zasada 5). Strukturalnie wymagany = element klucza
naturalnego i nic ponadto. Patrz wpis B-06 w sekcji C.

## Skąd bierze podstawę

Z **raportu importu** — ``missing_key_columns`` i ``materialized_empty`` razem opisują
komplet pól bez kolumny. Dzięki temu kontrola działa także przy mapowaniu tożsamościowym,
bez profilu.

Raport mapowania, jeżeli jest, **wzbogaca** podstawę: mówi, jaką kolumnę profil zapowiadał
dla brakującego pola. „Nie przypisałeś tego pola" i „przypisałeś do kolumny, której nie ma"
to dwie różne rozmowy z klientem, ale obie kończą się tak samo w danych.

## Czego kontrola nie robi

Nie ogłasza PASS **bez podstawy**. Brak wiedzy o imporcie nie jest brakiem brakujących
kolumn — kontrola nie zostaje wtedy uruchomiona, a rejestr zwraca wynik nieoznaczony
(``missing_input``). PASS bez podstawy byłby fałszywym przejściem; PASS z obserwacją
opisującą brak — nie jest.
"""

from typing import ClassVar

from xray.ingest.report import ImportReport
from xray.mapping.report import MappingReport
from xray.model.enums import ValidationStatus
from xray.validation.base import CheckDeclaration, DataCheck
from xray.validation.context import ValidationContext
from xray.validation.results import CheckObservation, CheckOutcome, cap_observations


class MissingColumns(DataCheck):
    """Zgłasza pola kontraktu, dla których w pliku nie było kolumny."""

    DECLARATION: ClassVar[CheckDeclaration] = CheckDeclaration(
        check_id="TECH01-VAL-01",
        control_number=1,
        title="Brak wymaganej kolumny",
        # Brak kolumny widać wyłącznie w raporcie importu: w ramce pole zawsze jest,
        # tylko puste. Bez tej wiedzy kontrola nie ma czego badać.
        requires_import_report=True,
        requires_natural_key=True,
        max_status=ValidationStatus.CRITICAL,
    )

    def run(self, context: ValidationContext) -> CheckOutcome:
        raporty: tuple[ImportReport, ...] = context.import_reports or ()

        brak_klucza: dict[str, set[str]] = {}
        zmaterializowane: dict[str, set[str]] = {}
        for raport in raporty:
            for pole in raport.missing_key_columns:
                brak_klucza.setdefault(pole, set()).add(raport.source.source_id)
            for pole in raport.materialized_empty:
                zmaterializowane.setdefault(pole, set()).add(raport.source.source_id)

        zapowiedziane = _zapowiedziane_kolumny(context.mapping_reports)

        obserwacje: list[CheckObservation] = []
        # Kolejność wg kontraktu, nie wg iteracji po zbiorach.
        for pole in context.table.model_fields:
            if pole in brak_klucza:
                obserwacje.append(
                    _obserwacja(
                        pole,
                        "missing_key_column",
                        brak_klucza[pole],
                        zapowiedziane,
                        (
                            f"Pole {pole} należy do klucza naturalnego "
                            f"({' + '.join(context.table.NATURAL_KEY)}), a w pliku nie ma "
                            "dla niego kolumny. Rekordu bez klucza nie da się przypisać "
                            "do zakresu ani okresu, więc nie może uczestniczyć "
                            "w audytowalnej agregacji."
                        ),
                    )
                )
            elif pole in zmaterializowane:
                obserwacje.append(
                    _obserwacja(
                        pole,
                        "materialized_empty_column",
                        zmaterializowane[pole],
                        zapowiedziane,
                        (
                            f"Pole {pole} nie ma kolumny w pliku i zostało wypełnione "
                            "pustką. To nieobecność kolumny, a nie wartość zastępcza "
                            "wstawiona w miejsce danych. Pole nie jest wymagane "
                            "strukturalnie, więc jego brak nie czyni tabeli niepoprawną "
                            "— ale test, który go potrzebuje, nie może udawać wyniku "
                            "(rozstrzygnięcie B-06)."
                        ),
                    )
                )

        if brak_klucza:
            return CheckOutcome(
                status=ValidationStatus.CRITICAL,
                basis=(
                    f"W tabeli {context.table_name} brakuje kolumn dla elementów klucza "
                    f"naturalnego: {', '.join(sorted(brak_klucza))}. Bez nich rekord nie "
                    "istnieje w kontrakcie."
                ),
                observations=cap_observations(
                    obserwacje,
                    subject="missing_key_column",
                    basis=f"Pola bez kolumny w tabeli {context.table_name}.",
                ),
            )

        if zmaterializowane:
            # PASS, nie WARNING: brak pola spoza klucza jest faktem o danych, a nie
            # oceną ich przydatności. Czy ogranicza wnioskowanie, wie dopiero test —
            # rozstrzygnięcie B-06.
            return CheckOutcome(
                status=ValidationStatus.PASS,
                basis=(
                    f"W tabeli {context.table_name} nie ma kolumn dla pól spoza klucza: "
                    f"{', '.join(sorted(zmaterializowane))}. Rekordy przechodzą, a pola są "
                    "w całości puste. Kontrola ogłasza ten stan, ale nie orzeka o jego "
                    "ciężarze: czy brak ogranicza wnioskowanie, wie test, który tego pola "
                    "potrzebuje — i to on odmawia wyniku, a nie walidator."
                ),
                observations=cap_observations(
                    obserwacje,
                    subject="materialized_empty_column",
                    basis=f"Pola bez kolumny w tabeli {context.table_name}.",
                ),
            )

        return CheckOutcome(
            status=ValidationStatus.PASS,
            basis=(
                f"Każde pole kontraktu tabeli {context.table_name} ma kolumnę "
                f"w danych ({len(raporty)} raport importu)."
            ),
        )


def _zapowiedziane_kolumny(
    reports: tuple[MappingReport, ...] | None,
) -> dict[str, str]:
    """Pole → kolumna, którą profil dla niego zapowiadał, choć jej w pliku nie było.

    Wzbogaca podstawę, nie warunkuje jej. Bez raportu mapowania kontrola nadal wie,
    **że** kolumny brakuje — nie wie tylko, jak miała się nazywać.
    """
    zapowiedziane: dict[str, str] = {}
    for raport in reports or ():
        for pole, kolumna in raport.declared_missing_columns:
            zapowiedziane[pole] = kolumna
    return zapowiedziane


def _obserwacja(
    pole: str,
    measure: str,
    zrodla: set[str],
    zapowiedziane: dict[str, str],
    podstawa: str,
) -> CheckObservation:
    """Buduje obserwację o brakującej kolumnie, dopisując zapowiedź profilu, jeśli jest."""
    kolumna = zapowiedziane.get(pole)
    if kolumna is not None:
        podstawa += (
            f" Profil zapowiadał dla tego pola kolumnę {kolumna!r}, której w pliku nie ma."
        )
    else:
        podstawa += " Profil nie przypisał temu polu żadnej kolumny."
    return CheckObservation.create(
        subject=pole,
        measure=measure,
        # Liczba źródeł, w których pola zabrakło — tabela może pochodzić z kilku plików.
        value=float(len(zrodla)),
        basis=podstawa,
    )
