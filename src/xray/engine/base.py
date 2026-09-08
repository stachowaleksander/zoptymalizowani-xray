# Implementuje konwencję wtyczki testu diagnostycznego z CLAUDE.md,
# ZOP-TECH-01 v0.1 pkt 10.5 (dokładanie testów bez przebudowy rdzenia)
# oraz rozstrzygnięcie B-06 z 2026-09-08 (egzekwowanie required_by_test).
"""Kontrakt wtyczki testu diagnostycznego.

Test diagnostyczny jest wtyczką: deklaruje ``test_id``, wymagane tabele i pola, wymagane
walidacje, produkowane pola FINDINGS i możliwe ``next_tests``. Dodanie testu to nowy plik
plus wpis w rejestrze — zero zmian w rdzeniu.

## Dlaczego deklaracja, a nie tylko funkcja

Deklaracja pozwala odpowiedzieć na pytania **przed** uruchomieniem testu: czy dane
zawierają wymagane tabele, czy wymagane walidacje zostały wykonane, co ten test
w ogóle może wyprodukować. Bez niej orkiestracja musiałaby uruchomić test, żeby się
dowiedzieć, że nie miała czym.

Do 2026-09-08 deklaracja była sprawdzana **wyłącznie wobec kontraktu danych**, przy
imporcie modułu: czy tabela istnieje i czy pole jest w kontrakcie. To sprawdzenie jest
prawdziwe zawsze, niezależnie od danych — więc zdanie „test nie może udawać wyniku"
nie było przez nic realizowane. Bramka gotowości niżej to domyka.

## Czego test nie robi

Nie zapisuje niczego. ``run`` zwraca rekordy; trwały zapis należy do ``store/``.
Nie liczy niczego „obok" FINDINGS — to jedyne miejsce zapisu wyników.
Nie decyduje, czy CRITICAL z walidacji go blokuje: deklaruje, których kontroli wymaga,
a interpretacja ich statusu należy do warstwy uruchamiającej.
"""

from abc import ABC, abstractmethod
from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict, model_validator

from xray.ingest.report import ImportReport
from xray.model import TABLES, FindingRecord, LogicalStatus, PeriodRef, ScopeRef

ImportKnowledge = Mapping[str, tuple[ImportReport, ...] | None]
"""Co wiadomo o imporcie każdej tabeli. Trzy stany, tak jak w ``ValidationContext``.

| Wartość | Znaczenie |
| --- | --- |
| tabeli nie ma w odwzorowaniu albo ma ``None`` | **nie wiadomo**, czy pole miało kolumnę |
| krotka raportów | wiadomo; obecność kolumn rozstrzygalna |
| ``()`` | niedozwolone — nie do odróżnienia od braku wiedzy |

Raporty trafiają do bramki, a nie do ``run``: autor wtyczki liczy na danych, nie na
metadanych. Wiedza o jednej tabeli nie rozpada się przy tym na dwa argumenty, które mogą
się rozjechać — bramka bierze ramki i raporty w jednym wywołaniu.
"""


class DiagnosticTestDeclaration(BaseModel):
    """Deklaracja wtyczki — co test wymaga i co produkuje.

    Deklaracja jest sprawdzana wobec kontraktu danych przy rejestracji, więc test
    odwołujący się do nieistniejącej tabeli albo pola nie da się zarejestrować.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    test_id: str
    """Kod testu, np. ``"FIN-01"``. Trafia do ``FindingRecord.test_id``."""

    required_tables: tuple[str, ...]
    """Tabele bazowe, bez których test nie ma podstawy."""

    required_by_test: Mapping[str, tuple[str, ...]] = {}
    """Pola, bez których **ten test** nie może wydać wyniku: nazwa tabeli → pola.

    Nazwa niesie swoje znaczenie celowo. ``required_fields`` było dwuznaczne dokładnie
    tak, jak ostrzega rozstrzygnięcie B-06: nie mówiło, **czyim** wymaganiem jest to pole.

    Rozstrzygnięcie rozdziela trzy stany:

    | Stan | Kto orzeka | Skutek braku |
    | --- | --- | --- |
    | wymagane strukturalnie | walidator | CRITICAL — element ``NATURAL_KEY`` |
    | ``required_by_test`` | **ten test** | test nie może udawać wyniku |
    | legalnie opcjonalne | nikt | dopuszczalny stan danych |

    Brak pola z tej listy **nie blokuje przebiegu** i nie znaczy, że tabela jest
    niepoprawna. Ogranicza **ten test**, a nie cały przebieg.

    ## Co wolno tu wpisać, dopóki nie ma ``required_by_claim``

    Wyłącznie pole, bez którego test nie wyda **żadnego** ze swoich twierdzeń. Pole
    potrzebne części twierdzeń zostaje poza deklaracją, a odmowę wydaje sam test
    w swoim wyniku.

    Powód jest konkretny, nie hipotetyczny. CAP-01 scenariusz CAP01-T10 mówi wprost:
    brak ``cost`` daje miary fizyczne i ``economic_gap = null``, „wg trendu; **nie
    TEST_BLOCKED**". Gdyby CAP-01 zadeklarowało ``cost`` w ``required_by_test``, bramka
    wyprodukowałaby status, którego karta zakazuje. Patrz wpis DT-18 — to jest pierwszy
    nazwany użytkownik odroczonej granulacji per twierdzenie.
    """

    required_validations: tuple[str, ...] = ()
    """Identyfikatory kontroli, których wykonania test wymaga.

    Walidator sam nic nie blokuje — ogłasza statusy. To test deklaruje, które kontrole
    są dla niego wymagane, a warstwa uruchamiająca rozstrzyga, czy ich CRITICAL oznacza
    ``TEST_BLOCKED``, czy ``TEST_PARTIAL``.
    """

    produced_fields: tuple[str, ...] = ()
    """Pola FINDINGS, które ten test wypełnia. Reszta pozostaje przy wartościach
    domyślnych — czyli zwykle ``None``, co jest poprawnym wynikiem."""

    possible_next_tests: tuple[str, ...] = ()
    """Testy, które ten test może wskazać w ``next_tests``.

    Zbiór możliwych kandydatów, a nie ścieżka. Ścieżkę wyznacza ZOP-ORCH-01, który nie
    jest jeszcze zaimplementowany.
    """

    @model_validator(mode="after")
    def _check_against_contract(self) -> "DiagnosticTestDeclaration":
        """Sprawdza deklarację wobec kontraktu danych i kontraktu FINDINGS.

        Sprawdzenie wobec **danych** to osobna sprawa i osobny moment — patrz
        ``DiagnosticTest.readiness``.
        """
        if not self.test_id.strip():
            raise ValueError("test_id nie może być pusty")

        nieznane = [t for t in self.required_tables if t not in TABLES]
        if nieznane:
            raise ValueError(
                f"test {self.test_id} wymaga nieznanych tabel: {', '.join(nieznane)}; "
                f"ZOP-TECH-01 pkt 5.2 definiuje wyłącznie: {', '.join(TABLES)}"
            )

        for tabela, pola in self.required_by_test.items():
            if tabela not in self.required_tables:
                raise ValueError(
                    f"test {self.test_id} wymaga pól z tabeli {tabela}, "
                    "której nie ma w required_tables"
                )
            dostepne = set(TABLES[tabela].model_fields)
            brakujace = [p for p in pola if p not in dostepne]
            if brakujace:
                raise ValueError(
                    f"test {self.test_id}: tabela {tabela} nie ma pól "
                    f"{', '.join(brakujace)}"
                )

        nieznane_pola = [
            p for p in self.produced_fields if p not in FindingRecord.model_fields
        ]
        if nieznane_pola:
            raise ValueError(
                f"test {self.test_id} deklaruje produkowanie pól spoza kontraktu "
                f"FINDINGS: {', '.join(nieznane_pola)}"
            )
        return self


class ReadinessReason(StrEnum):
    """Dlaczego test nie może wydać wyniku. Fakt o danych, nie ocena ich wagi."""

    MISSING_TABLE = "missing_table"
    """Tabela z ``required_tables`` nie została w ogóle podana."""

    MISSING_COLUMN = "missing_column"
    """Pole z ``required_by_test`` nie miało kolumny w żadnym pliku źródłowym."""

    UNKNOWN_IMPORT = "unknown_import"
    """Nie wiadomo, czy pole miało kolumnę — brak raportu importu dla tabeli.

    To **nie to samo** co brak kolumny i dlatego ma osobną wartość. „Nie wiem" nie jest
    podstawą do wydania wyniku, ale nie jest też stwierdzeniem, że kolumny nie było.
    Ta sama reguła, dla której kontrola 1 nie ogłasza PASS bez raportu importu.
    """


@dataclass(frozen=True, slots=True)
class MissingRequirement:
    """Jedno niespełnione wymaganie testu."""

    table_name: str
    reason: ReadinessReason
    field: str | None = None
    """Pole kontraktu; ``None``, gdy brakuje całej tabeli."""

    def describe(self) -> str:
        """Podstawa w jednym zdaniu — trafia do ``validation_notes``."""
        if self.reason is ReadinessReason.MISSING_TABLE:
            return f"tabela {self.table_name} nie została podana"
        if self.reason is ReadinessReason.UNKNOWN_IMPORT:
            return (
                f"nie wiadomo, czy tabela {self.table_name} miała kolumnę dla pola "
                f"{self.field}: brak raportu importu"
            )
        return f"tabela {self.table_name} nie miała kolumny dla pola {self.field}"


@dataclass(frozen=True, slots=True)
class TestReadiness:
    """Czy test ma z czego wydać wynik.

    Nie orzeka o wadze braku i nie proponuje kolejnego kroku — to należy do ZOP-PRI-01
    i ZOP-ORCH-01. Mówi wyłącznie, czego zabrakło.
    """

    test_id: str
    ready: bool
    missing: tuple[MissingRequirement, ...] = ()

    def basis(self) -> str:
        """Zdanie opisujące gotowość albo odmowę w całości."""
        if self.ready:
            return f"test {self.test_id} ma komplet zadeklarowanych tabel i pól"
        powody = "; ".join(m.describe() for m in self.missing)
        return (
            f"test {self.test_id} nie wydaje wyniku, bo zabrakło zadeklarowanych "
            f"wejść: {powody}"
        )


class DiagnosticTest(ABC):
    """Wspólna podstawa wtyczek testów diagnostycznych.

    Każda wtyczka musi zadeklarować ``DECLARATION``. Sprawdzenie odbywa się przy
    tworzeniu klasy — tak samo jak przy tabelach kontraktu danych.

    ## Bramka gotowości

    ``execute`` jest metodą szablonową: liczy gotowość wobec **rzeczywistych** raportów
    importu i dopiero wtedy woła ``run``. Wtyczka pisze ``run``; bramki nie widzi
    i nie może jej ominąć — ``__init_subclass__`` odrzuca podklasę nadpisującą
    ``execute`` albo ``readiness``.

    Ochrona nie jest przesadą. Deklaracja sprawdzana wyłącznie wobec kontraktu danych
    była martwa dokładnie dlatego, że nikt jej nie egzekwował na danych — a rejestr dawał
    się obejść jednym ``get_test(...)().run(...)``, co robiła nawet nasza własna
    demonstracja. Bramka, którą wolno nadpisać, jest konwencją; bramka, której nadpisać
    nie wolno, jest mechanizmem.

    ## Odmowa jest wynikiem, nie śmieciem

    Gdy gotowości brak, ``execute`` zwraca **jeden** ``FindingRecord`` ze statusem
    ``TEST_BLOCKED`` i bez ``metric_value``. Tożsamość wyniku to
    ``test_id + scope + period + contract_version``, więc odmowa i policzony wynik
    z późniejszego przebiegu mają **ten sam** ``finding_id`` i różne ``run_id``.
    ``FindingStore.history(finding_id)`` pokaże wtedy „przebieg 1: TEST_BLOCKED,
    przebieg 2: policzone".

    To pierwszy realny użytkownik decyzji DT-11 — klucza magazynu złożonego z **pary**
    ``(finding_id, run_id)``. Rekordów odmowy **nie wolno usuwać przy porządkowaniu
    magazynu**: bez nich ślad mówiłby, że test policzył wynik, i milczał o tym, że
    w poprzednim przebiegu nie miał czym.
    """

    DECLARATION: ClassVar[DiagnosticTestDeclaration]

    _CHRONIONE: ClassVar[tuple[str, ...]] = ("execute", "readiness")
    """Metody, których wtyczce nie wolno nadpisać. Patrz ``__init_subclass__``."""

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        if "DECLARATION" not in cls.__dict__:
            raise TypeError(
                f"test {cls.__name__} nie deklaruje DECLARATION; bez deklaracji "
                "orkiestracja nie wie, czego test wymaga ani co produkuje"
            )
        nadpisane = [m for m in cls._CHRONIONE if m in cls.__dict__]
        if nadpisane:
            raise TypeError(
                f"test {cls.__name__} nadpisuje: {', '.join(nadpisane)}. Bramka "
                "gotowości musi być nie do ominięcia, bo inaczej test może udawać "
                "wynik (rozstrzygnięcie B-06). Wtyczka implementuje wyłącznie run()"
            )

    @classmethod
    def readiness(
        cls,
        data: Mapping[str, Any],
        *,
        import_reports: ImportKnowledge,
    ) -> TestReadiness:
        """Sprawdza deklarację wobec rzeczywistych danych, **nie uruchamiając testu**.

        To jest sens deklaracji: orkiestracja pyta, zanim zdecyduje, czy ma czym
        uruchomić test. Metoda jest klasowa, bo korzysta wyłącznie z ``DECLARATION``.

        Bramka patrzy na **kolumny, a nie na wypełnienie**. Pole, które kolumnę miało,
        a jest w stu procentach puste, przechodzi — to sprawa kontroli 3 i samego testu.
        Rozszerzenie bramki na kompletność byłoby wymyśleniem progu (zasada 1).
        """
        deklaracja = cls.DECLARATION
        braki: list[MissingRequirement] = []

        for tabela in deklaracja.required_tables:
            if tabela not in data:
                braki.append(
                    MissingRequirement(
                        table_name=tabela, reason=ReadinessReason.MISSING_TABLE
                    )
                )

        for tabela, pola in deklaracja.required_by_test.items():
            if tabela not in data:
                # Brak całej tabeli jest już odnotowany; nie dublujemy powodu polami.
                continue
            raporty = import_reports.get(tabela)
            if raporty is not None and not raporty:
                raise ValueError(
                    f"import_reports[{tabela!r}] nie może być pustą krotką: byłaby nie "
                    "do odróżnienia od braku wiedzy. Przekaż None (nie wiadomo) albo "
                    "co najmniej jeden raport"
                )
            if raporty is None:
                braki += [
                    MissingRequirement(
                        table_name=tabela,
                        reason=ReadinessReason.UNKNOWN_IMPORT,
                        field=pole,
                    )
                    for pole in pola
                ]
                continue
            # Pole ma kolumnę, jeżeli miał ją choć jeden plik zasilający tabelę:
            # tabela z dwóch plików ma pełne pole, gdy tylko jeden z nich je przyniósł.
            bez_kolumny = set(raporty[0].fields_without_column)
            for raport in raporty[1:]:
                bez_kolumny &= set(raport.fields_without_column)
            braki += [
                MissingRequirement(
                    table_name=tabela,
                    reason=ReadinessReason.MISSING_COLUMN,
                    field=pole,
                )
                for pole in pola
                if pole in bez_kolumny
            ]

        return TestReadiness(
            test_id=deklaracja.test_id, ready=not braki, missing=tuple(braki)
        )

    def execute(
        self,
        data: Mapping[str, Any],
        *,
        import_reports: ImportKnowledge,
        scope: ScopeRef,
        period: PeriodRef,
    ) -> tuple[FindingRecord, ...]:
        """Jedyna droga uruchomienia testu w kodzie produkcyjnym.

        Albo deleguje do ``run``, albo zwraca jedną odmowę. ``import_reports`` jest
        argumentem wymaganym: przekazanie ``{}`` znaczy „nic nie wiadomo" i kończy się
        odmową, a nie wykonaniem. Bramka zamyka się w stronę bezpieczną.
        """
        gotowosc = self.readiness(data, import_reports=import_reports)
        if gotowosc.ready:
            return self.run(data, scope=scope, period=period)
        return (self._blocked(gotowosc, scope=scope, period=period),)

    def _blocked(
        self,
        gotowosc: TestReadiness,
        *,
        scope: ScopeRef,
        period: PeriodRef,
    ) -> FindingRecord:
        """Buduje rekord odmowy.

        ``TEST_BLOCKED``, a nie ``TEST_PARTIAL``: ``required_by_test`` jest deklaracją
        na poziomie **całego** testu, więc brak takiego pola znaczy, że test nie wyda
        żadnego ze swoich twierdzeń. ``TEST_PARTIAL`` stanie się osiągalny dopiero
        z ``required_by_claim``, odroczonym w B-06 (wpis DT-18). Bramka nie zgaduje
        wartości, której nie potrafi wywieść.
        """
        return FindingRecord.create(
            test_id=gotowosc.test_id,
            scope=scope,
            period=period,
            status=LogicalStatus.TEST_BLOCKED,
            finding=gotowosc.basis(),
            metric_value=None,
            # DECYZJA techniczna, do świadomego odwrócenia przez ZOP-PRI-01: bramka
            # ustawia tę flagę, bo „w danych nie było kolumny" jest faktem o danych,
            # a nie oceną wagi decyzji. PRI-01 mówi, że TEST_BLOCKED *może* generować
            # validate_now, jeżeli luka blokuje ważną decyzję — routing należy do PRI-01
            # i to on może flagę zdjąć.
            # Alternatywa odrzucona: zostawić False i czekać na PRI-01. Wtedy jedyny
            # ślad, że wynik wymaga uzupełnienia danych, żyłby w tekście komunikatu,
            # czyli w miejscu, którego nie da się odpytać.
            validation_required=True,
            validation_notes=tuple(m.describe() for m in gotowosc.missing),
        )

    @abstractmethod
    def run(
        self,
        data: Mapping[str, Any],
        *,
        scope: ScopeRef,
        period: PeriodRef,
    ) -> tuple[FindingRecord, ...]:
        """Wykonuje test i zwraca wyniki. Woła ją wyłącznie ``execute``.

        ``data`` to odwzorowanie nazwa tabeli → ramka pandas, zgodnie z decyzją DT-02
        (kontrakt w modelu, dane w ramce). Raportów importu ta metoda **nie dostaje**:
        autor wtyczki liczy na danych, a nie na metadanych, a sprawdzenie obecności
        kolumn odbyło się piętro wyżej.

        Metoda **nie zapisuje** wyników. Zwraca je; trwały zapis należy do ``store/``.
        """
