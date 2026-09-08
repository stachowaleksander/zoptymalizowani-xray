# Implementuje ZOP-TECH-01 v0.1 pkt 5.3 — rejestr kontroli danych.
"""Rejestr kontroli i uruchamianie ich na kontekście.

Dodanie kontroli to nowy plik plus jeden wpis tutaj. Jawna krotka, nie dekorator: kolejność
importów to ukryty stan, a przebieg ma być odtwarzalny (zasada 3).

## Co rejestr bierze na siebie zamiast kontroli

- **stosowalność** — kontrola, której pól tabela nie ma, nie jest uruchamiana; wynik mówi
  ``not_applicable``, a nie milczy, bo raport jakości danych ma pokryć wszystkie osiem
  kontroli dla każdej tabeli,
- **dostępność wejścia** — kontrola wymagająca raportu importu, która go nie dostanie,
  **nie liczy zera**: nie jest wywoływana, a wynik mówi ``missing_input``,
- **limit statusu** — status mocniejszy niż zadeklarowany ``max_status`` (z nadpisaniem
  po ziarnie czasowym) jest błędem implementacji kontroli, wyłapywanym tutaj,
- **pary porównawcze dzielące źródło** — gdy oba pola zadeklarowanej pary pochodzą
  z jednej kolumny klienta, ich różnicy nie da się zobaczyć; rejestr unieważnia wynik
  (``Determines.STATUS``) albo zeruje dotknięte obserwacje (``Determines.OBSERVATION``).

Gdyby każda kontrola robiła to sama, każda musiałaby powtarzać te same warunki i każda
mogłaby któryś zapomnieć.
"""

from collections.abc import Mapping
from types import MappingProxyType

from xray.validation.base import SEVERITY, CheckDeclaration, DataCheck, Determines
from xray.validation.checks.duplicates import DuplicateRows
from xray.validation.checks.inconsistent_names import InconsistentNames
from xray.validation.checks.invalid_format import InvalidFormat
from xray.validation.checks.missing_columns import MissingColumns
from xray.validation.checks.missing_values import MissingValues
from xray.validation.checks.resource_usage import ResourceUsage
from xray.validation.checks.suspicious_values import SuspiciousValues
from xray.validation.checks.time_range import TimeRange
from xray.validation.context import ValidationContext
from xray.validation.results import CheckObservation, CheckResult, NotAssessedReason

# Kolejność jak w ZOP-TECH-01 pkt 5.3 — komplet ośmiu kontroli.
_CHECK_CLASSES: tuple[type[DataCheck], ...] = (
    MissingColumns,
    InvalidFormat,
    MissingValues,
    DuplicateRows,
    SuspiciousValues,
    InconsistentNames,
    ResourceUsage,
    TimeRange,
)

CHECKS: Mapping[str, type[DataCheck]] = MappingProxyType(
    {cls.DECLARATION.check_id: cls for cls in _CHECK_CLASSES}
)
"""Identyfikator kontroli → klasa wtyczki. Odwzorowanie niezmienne."""

if len(CHECKS) != len(_CHECK_CLASSES):
    raise RuntimeError("dwie kontrole dzielą ten sam check_id")


def registered_check_ids() -> tuple[str, ...]:
    """Identyfikatory kontroli w kolejności rejestru."""
    return tuple(cls.DECLARATION.check_id for cls in _CHECK_CLASSES)


def get_check(check_id: str) -> type[DataCheck]:
    """Zwraca klasę kontroli."""
    try:
        return CHECKS[check_id]
    except KeyError:
        raise KeyError(
            f"nieznana kontrola {check_id!r}; zarejestrowane: "
            f"{', '.join(registered_check_ids())}"
        ) from None


def get_declaration(check_id: str) -> CheckDeclaration:
    """Zwraca deklarację kontroli bez jej uruchamiania."""
    return get_check(check_id).DECLARATION


def run_check(check_id: str, context: ValidationContext) -> CheckResult:
    """Uruchamia jedną kontrolę na jednej tabeli.

    Zawsze zwraca wynik — także wtedy, gdy kontrola nie została uruchomiona. Milczenie
    byłoby nie do odróżnienia od pominięcia.
    """
    klasa = get_check(check_id)
    deklaracja = klasa.DECLARATION

    def zbuduj(outcome) -> CheckResult:  # noqa: ANN001 — typ z CheckOutcome
        return CheckResult(
            check_id=deklaracja.check_id,
            control_number=deklaracja.control_number,
            table_name=context.table_name,
            status=outcome.status,
            basis=outcome.basis,
            observations=outcome.observations,
            not_assessed_reason=outcome.not_assessed_reason,
        )

    if not deklaracja.applies_to(context.table):
        brakujace = [
            p for p in deklaracja.required_fields if p not in context.table.model_fields
        ]
        return CheckResult(
            check_id=deklaracja.check_id,
            control_number=deklaracja.control_number,
            table_name=context.table_name,
            status=None,
            basis=(
                f"Kontrola nie dotyczy tabeli {context.table_name}: brak pól "
                f"{', '.join(brakujace) if brakujace else 'wymaganych przez deklarację'}."
            ),
            not_assessed_reason=NotAssessedReason.NOT_APPLICABLE,
        )

    if deklaracja.requires_import_report and not context.import_known:
        return CheckResult(
            check_id=deklaracja.check_id,
            control_number=deklaracja.control_number,
            table_name=context.table_name,
            status=None,
            basis=(
                "Kontrola wymaga wiedzy o imporcie, a kontekst jej nie niesie "
                "(import_reports = None). Liczba odrzuceń jest nieznana, a nie zerowa."
            ),
            not_assessed_reason=NotAssessedReason.MISSING_INPUT,
        )

    # Pary porównawcze dzielące jedną kolumnę klienta. Sprawdzamy PRZED uruchomieniem,
    # bo kontrola z parą STATUS nie ma czego ogłosić.
    wspolne = _pary_dzielace_zrodlo(deklaracja, context)
    krytyczne = [
        (para, kolumna)
        for para, kolumna in wspolne
        if para.determines is Determines.STATUS
    ]
    if krytyczne:
        para, kolumna = krytyczne[0]
        return CheckResult(
            check_id=deklaracja.check_id,
            control_number=deklaracja.control_number,
            table_name=context.table_name,
            status=None,
            basis=(
                f"Pola {para.fields[0]} i {para.fields[1]} pochodzą z jednej kolumny "
                f"klienta ({kolumna}), więc ich różnica nie niesie informacji. Kontrola "
                "nie może orzec ani sygnału, ani jego braku — PASS byłby fałszywym "
                "przejściem wpuszczonym przez konfigurację."
            ),
            not_assessed_reason=NotAssessedReason.INSUFFICIENT_BASIS,
        )

    outcome = klasa().run(context)
    limit = deklaracja.effective_max_status(context.table)
    if outcome.status is not None and SEVERITY[outcome.status] > SEVERITY[limit]:
        raise RuntimeError(
            f"kontrola {deklaracja.check_id} zwróciła {outcome.status.value} dla tabeli "
            f"{context.table_name}, a deklaruje najwyżej {limit.value}. "
            "Rozstrzygnięcie mocniejsze niż zadeklarowane należy do karty, "
            "nie do fundamentu"
        )
    obserwacyjne = [
        (para, kolumna)
        for para, kolumna in wspolne
        if para.determines is Determines.OBSERVATION
    ]
    if obserwacyjne:
        outcome = outcome.model_copy(
            update={"observations": _zeruj_dotkniete(outcome.observations, obserwacyjne)}
        )
    return zbuduj(outcome)


def _pary_dzielace_zrodlo(
    deklaracja: CheckDeclaration, context: ValidationContext
) -> list[tuple[object, str]]:
    """Zadeklarowane pary, których oba pola pochodzą z jednej kolumny klienta.

    Para nieobecna w tabeli jest pomijana. Brak wiedzy o źródłach (kontekst bez raportów
    importu) **nie jest** wspólnym źródłem — nie orzekamy bez podstawy.
    """
    pola = set(context.table.model_fields)
    wynik = []
    for para in deklaracja.comparison_pairs:
        pierwsze, drugie = para.fields
        if pierwsze not in pola or drugie not in pola:
            continue
        kolumna = context.share_source(pierwsze, drugie)
        if kolumna is not None:
            wynik.append((para, kolumna))
    return wynik


def _zeruj_dotkniete(
    observations: tuple[CheckObservation, ...],
    pary: list[tuple[object, str]],
) -> tuple[CheckObservation, ...]:
    """Zeruje obserwacje, których podmiotem jest pole z pary dzielącej źródło.

    Obserwacje niosą ``subject`` równy nazwie pola kontraktu, więc dopasowanie idzie po
    nim. Nadmiar zerowania jest bezpieczny: **odejmuje twierdzenie, nie dodaje**.
    Rejestr i tak modyfikuje wynik, bo egzekwuje ``max_status``.
    """
    # Pole → (kolumna, miary wyłączone dla tej pary). Dopasowanie po nazwie pola
    # kontraktu, wyłączenie po identyfikatorze miary — nigdy po prozie.
    dotkniete = {
        pole: (kolumna, set(para.unaffected_measures))
        for para, kolumna in pary
        for pole in para.fields
    }
    if not dotkniete:
        return observations
    zmienione = []
    for obserwacja in observations:
        wpis = dotkniete.get(obserwacja.subject)
        if wpis is None or obserwacja.is_unknown:
            zmienione.append(obserwacja)
            continue
        kolumna, wylaczone = wpis
        if obserwacja.measure in wylaczone:
            zmienione.append(obserwacja)
            continue
        zmienione.append(
            obserwacja.model_copy(
                update={
                    "value": None,
                    "text_value": None,
                    "basis": (
                        f"{obserwacja.basis} Wartość unieważniona: pole "
                        f"{obserwacja.subject} pochodzi z tej samej kolumny klienta "
                        f"({kolumna}) co pole porównywane, więc różnica między nimi "
                        "byłaby artefaktem konfiguracji, a nie faktem o danych."
                    ),
                }
            )
        )
    return tuple(zmienione)


def run_checks(context: ValidationContext) -> tuple[CheckResult, ...]:
    """Uruchamia wszystkie zarejestrowane kontrole w kolejności rejestru."""
    return tuple(run_check(check_id, context) for check_id in registered_check_ids())
