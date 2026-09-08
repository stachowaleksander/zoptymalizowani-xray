# Implementuje ZOP-TECH-01 v0.1 kryterium odbioru 8.5 (działająca struktura FINDINGS).
# NOOP-01 nie implementuje żadnej karty metodologicznej i celowo nie ma żadnej treści
# diagnostycznej.
"""NOOP-01 — atrapa testu diagnostycznego.

## Po co istnieje

Kryterium odbioru 8.5 mówi o **działającej** strukturze FINDINGS gotowej do przyjmowania
wyników, a nie o samej definicji. NOOP-01 jest dowodem, że rejestr testów, kontrakt
FINDINGS, tożsamość rekordu i ślad audytowy działają razem.

## Czego NOOP-01 nie robi

Nie zawiera żadnej treści metodologicznej. Nie ma progu, wagi, klasyfikacji ani wzoru
pochodzącego z jakiejkolwiek karty. Liczy wiersze w tabeli ACTIVITY i tyle.

Nie wolno rozwijać go w kierunku diagnostyki. Pierwszym prawdziwym testem będzie FIN-01,
budowany na własnej karcie.

## Dlaczego status NO_ADVERSE_SIGNAL

To jedyna wartość statusu logicznego występująca w **każdej** karcie Core 10 bez wyjątku.
NOOP-01 nie ma podstaw do stwierdzenia czegokolwiek innego, a status musi być jawny.
"""

from collections.abc import Mapping
from typing import Any, ClassVar

from xray.engine.base import DiagnosticTest, DiagnosticTestDeclaration
from xray.model import FindingRecord, LogicalStatus, PeriodRef, ScopeRef

TEST_ID = "NOOP-01"


class Noop01(DiagnosticTest):
    """Liczy wiersze w ACTIVITY i zapisuje jeden wynik bez treści diagnostycznej."""

    DECLARATION: ClassVar[DiagnosticTestDeclaration] = DiagnosticTestDeclaration(
        test_id=TEST_ID,
        required_tables=("ACTIVITY",),
        required_by_test={"ACTIVITY": ("date", "unit", "product")},
        # Celowo pusta: NOOP-01 nie stawia żadnej tezy, więc żadna kontrola danych nie
        # jest warunkiem jego odpowiedzialnego wykonania. Prawdziwy test taką listę ma.
        required_validations=(),
        produced_fields=("status", "finding", "metric_value"),
        # Celowo pusta: wskazanie kolejnego testu jest decyzją metodologiczną,
        # a NOOP-01 żadnej nie podejmuje. Ścieżkę wyznacza ZOP-ORCH-01.
        possible_next_tests=(),
    )

    def run(
        self,
        data: Mapping[str, Any],
        *,
        scope: ScopeRef,
        period: PeriodRef,
    ) -> tuple[FindingRecord, ...]:
        """Zwraca jeden wynik z liczbą wierszy ACTIVITY jako miarą.

        Wynik niesie krotkę tożsamości i wersję kontraktu, mimo że nie niesie żadnej
        treści metodologicznej — to właśnie ta część szwu, której nie sprawdzi nic innego.
        """
        activity = data["ACTIVITY"]
        liczba_wierszy = float(len(activity))

        komunikat = (
            f"Tabela ACTIVITY zawiera {int(liczba_wierszy)} wierszy w zakresie "
            f"{scope.scope_label} i okresie {period.period_start.isoformat()} "
            f"do {period.period_end.isoformat()}. "
            "NOOP-01 nie ocenia tej liczby i nie formułuje wniosku."
        )

        return (
            FindingRecord.create(
                test_id=TEST_ID,
                scope=scope,
                period=period,
                status=LogicalStatus.NO_ADVERSE_SIGNAL,
                finding=komunikat,
                metric_value=liczba_wierszy,
            ),
        )
