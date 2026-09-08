# Implementuje ZOP-TECH-01 v0.1 pkt 10.5 — dokładanie testów bez przebudowy rdzenia.
"""Rejestr testów diagnostycznych.

Dodanie testu to nowy plik plus jeden wpis tutaj. Rdzeń się nie zmienia.

## Dlaczego jawna krotka, a nie dekorator rejestrujący

Rejestracja przez dekorator zależy od tego, które moduły zostały zaimportowane i w jakiej
kolejności. To wprowadza ukryty stan i zależność od kolejności — czyli łamie zasadę 3
(determinizm). Jawna krotka daje zawsze ten sam zestaw testów w tej samej kolejności,
niezależnie od drogi importu.

Cena jest jedna linia przy dodaniu testu. Korzyść: przebieg jest odtwarzalny.
"""

from collections.abc import Mapping
from types import MappingProxyType
from typing import Any

from xray.engine.base import (
    DiagnosticTest,
    DiagnosticTestDeclaration,
    ImportKnowledge,
    TestReadiness,
)
from xray.engine.noop01 import Noop01
from xray.model import FindingRecord, PeriodRef, ScopeRef

_TEST_CLASSES: tuple[type[DiagnosticTest], ...] = (Noop01,)

TESTS: Mapping[str, type[DiagnosticTest]] = MappingProxyType(
    {cls.DECLARATION.test_id: cls for cls in _TEST_CLASSES}
)
"""Kod testu → klasa wtyczki. Odwzorowanie niezmienne."""

if len(TESTS) != len(_TEST_CLASSES):
    raise RuntimeError(
        "dwa testy dzielą ten sam test_id; kod testu musi być jednoznaczny, "
        "bo trafia do FindingRecord.test_id i wchodzi do tożsamości wyniku"
    )


def registered_test_ids() -> tuple[str, ...]:
    """Kody zarejestrowanych testów w kolejności rejestracji."""
    return tuple(cls.DECLARATION.test_id for cls in _TEST_CLASSES)


def get_test(test_id: str) -> type[DiagnosticTest]:
    """Zwraca klasę wtyczki dla kodu testu."""
    try:
        return TESTS[test_id]
    except KeyError:
        raise KeyError(
            f"nieznany test {test_id!r}; zarejestrowane: {', '.join(registered_test_ids())}"
        ) from None


def get_declaration(test_id: str) -> DiagnosticTestDeclaration:
    """Zwraca deklarację testu bez jego uruchamiania.

    To jest sens deklaracji: orkiestracja może sprawdzić, czego test wymaga, zanim
    zdecyduje, czy ma go czym uruchomić.
    """
    return get_test(test_id).DECLARATION


def run_test(
    test_id: str,
    data: Mapping[str, Any],
    *,
    import_reports: ImportKnowledge,
    scope: ScopeRef,
    period: PeriodRef,
) -> tuple[FindingRecord, ...]:
    """Uruchamia test przez bramkę gotowości. Wejście warstwy dla przebiegu.

    Cienka funkcja: mechanizm siedzi w ``DiagnosticTest.execute``, bo rejestr jest złym
    punktem egzekwowania — ``get_test(...)().run(...)`` go omija, i tak właśnie robiła
    do 2026-09-08 nasza własna demonstracja. Rozstrzygnięcie B-06 mówi „rejestr testów
    egzekwuje ``required_by_test``"; egzekwowanie stoi piętro niżej, żeby nie dało się
    obejść, a rejestr zostaje adresem, pod który się po to przychodzi.
    """
    return get_test(test_id)().execute(
        data, import_reports=import_reports, scope=scope, period=period
    )


def check_readiness(
    test_id: str,
    data: Mapping[str, Any],
    *,
    import_reports: ImportKnowledge,
) -> TestReadiness:
    """Pyta o gotowość testu, nie uruchamiając go.

    Dla orkiestracji, która chce wiedzieć, zanim zdecyduje — ZOP-ORCH-01.
    """
    return get_test(test_id).readiness(data, import_reports=import_reports)
