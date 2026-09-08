# Implementuje ZOP-TECH-01 v0.1 pkt 5.3 — wspólne wejście warstwy kontroli danych.
"""Kontekst kontroli — stan wiedzy o tabeli.

Wejściem kontroli nie jest ramka, tylko **stan wiedzy o tabeli**: dane, to, co wiadomo
o ich imporcie, i kontrakt, według którego powstały.

Gdyby wejściem była sama ramka, pierwsza kontrola o innych potrzebach (a jest nią już
kontrola 3, która musi znać odrzucenia) wymusiłaby wyjątek w sygnaturze, druga kolejny,
a warstwa skończyłaby jak kaskada ``if nazwa ==``, której uniknęliśmy przy metadanych
tabel.

Dopisanie nowego rodzaju wiedzy — raportu mapowania dla kontroli 1, gdy powstanie
``mapping/`` — **nie zmieni sygnatury żadnej kontroli**. To jest właściwość, dla której
warto ponieść koszt kontekstu.
"""

from dataclasses import dataclass

import pandas as pd

from xray.ingest.report import ImportReport
from xray.mapping.report import MappingReport
from xray.model.tables.base import TableRecord


@dataclass(frozen=True, slots=True)
class ValidationContext:
    """Wszystko, co kontrola może wiedzieć o jednej tabeli.

    Zwykła klasa danych, nie model Pydantic: ``frame`` jest ramką pandas, której nie
    chcemy walidować ani kopiować przy każdym przekazaniu.
    """

    table: type[TableRecord]
    """Klasa kontraktu tabeli. Niesie ``NATURAL_KEY``, ``TIME_GRAIN`` i ``TIME_FIELDS``.

    ``table_name`` nie jest osobnym polem — wynika z ``table.TABLE_NAME``. Jedno źródło
    prawdy zamiast dwóch, które mogą się rozjechać.
    """

    frame: pd.DataFrame
    """Wiersze **przyjęte** przez bramkę kontraktu, indeksowane ``row_id``.

    Wierszy odrzuconych tu nie ma i nigdy nie będzie — istnieją wyłącznie w raportach
    importu. Kontrola licząca braki wyłącznie na ramce pokazałaby więc mniej, niż jest
    w danych klienta.
    """

    import_reports: tuple[ImportReport, ...] | None = None
    """Co wiadomo o imporcie tej tabeli. **Trzy stany, nie dwa.**

    | Wartość | Znaczenie |
    | --- | --- |
    | ``None`` | nie wiadomo, czy i jak importowano; liczba odrzuceń **nieznana** |
    | krotka z raportami | wiadomo; odrzucenia policzalne |
    | ``()`` | niedozwolone — patrz niżej |

    Krotka, a nie jeden raport, bo tabela może być zasilona z kilku plików
    (``koszty_2025.csv`` + ``koszty_2026.csv``). Kształt kontekstu jest częścią
    nieodwracalną: wiele degraduje się do jednego bez zmiany kodu, odwrotnie nie.

    Pusta krotka jest zakazana, bo byłaby dwuznaczna — „zadeklarowano brak importów"
    wyglądałoby identycznie jak „zapomniano przekazać". Kto chce zadeklarować brak
    odrzuceń (np. generator firmy syntetycznej, który produkuje ramki bez przechodzenia
    przez ``ingest/``), przekazuje **raport** z ``records_rejected = 0`` i ``SourceRef``
    opisującym siebie. Deklaracja ma mieć autora.
    """

    mapping_reports: tuple[MappingReport, ...] | None = None
    """Co profil mapowania zapowiedział dla tej tabeli. ``None`` = nie wiadomo.

    **To pole jest sprawdzianem tezy, dla której kontekst w ogóle powstał.** Dopisanie
    nowego rodzaju wiedzy nie zmieniło sygnatury żadnej z siedmiu istniejących kontroli —
    każda bierze z kontekstu to, czego potrzebuje, a reszta nawet nie wie, że przybyło
    pole.

    Kontrola 1 **nie wymaga** tej wiedzy: status wywodzi z raportu importu, więc działa
    także przy mapowaniu tożsamościowym. Raport mapowania wzbogaca podstawę o to, jaką
    kolumnę profil zapowiadał — ale nie warunkuje jej istnienia.
    """

    def __post_init__(self) -> None:
        if self.import_reports is not None and not self.import_reports:
            raise ValueError(
                "import_reports nie może być pustą krotką: byłaby nie do odróżnienia od "
                "braku wiedzy. Przekaż None (nie wiadomo) albo raport z zerem odrzuceń "
                "(zadeklarowany brak)"
            )
        if self.mapping_reports is not None and not self.mapping_reports:
            raise ValueError(
                "mapping_reports nie może być pustą krotką: byłaby nie do odróżnienia od "
                "braku wiedzy. Przekaż None albo co najmniej jeden raport"
            )
        if self.mapping_reports is not None:
            obce_mapowanie = [
                r.table_name
                for r in self.mapping_reports
                if r.table_name != self.table.TABLE_NAME
            ]
            if obce_mapowanie:
                raise ValueError(
                    f"kontekst tabeli {self.table.TABLE_NAME} dostał raporty mapowania "
                    f"innych tabel: {', '.join(sorted(set(obce_mapowanie)))}"
                )
        if self.import_reports is not None:
            obce = [
                r.table_name
                for r in self.import_reports
                if r.table_name != self.table.TABLE_NAME
            ]
            if obce:
                raise ValueError(
                    f"kontekst tabeli {self.table.TABLE_NAME} dostał raporty importu "
                    f"innych tabel: {', '.join(sorted(set(obce)))}"
                )

    @property
    def table_name(self) -> str:
        """Nazwa tabeli kontraktu."""
        return self.table.TABLE_NAME

    @property
    def mapping_known(self) -> bool:
        """Czy wiadomo cokolwiek o mapowaniu tej tabeli."""
        return self.mapping_reports is not None

    @property
    def import_known(self) -> bool:
        """Czy w ogóle wiadomo cokolwiek o imporcie tej tabeli."""
        return self.import_reports is not None

    def column_sources(self) -> dict[str, frozenset[str]]:
        """Pole kontraktu → kolumny klienta, z których faktycznie je zasilono.

        Zbiór, a nie pojedyncza nazwa, bo tabela może być zasilona z kilku plików
        i w każdym kolumna może nazywać się inaczej.

        Puste odwzorowanie znaczy **nie wiadomo**, a nie „każde pole ma własną kolumnę".
        Brak wiedzy nie jest wiedzą — ta sama zasada, co przy liczbie odrzuceń.
        """
        zrodla: dict[str, set[str]] = {}
        for raport in self.import_reports or ():
            for pole, kolumna in raport.applied_columns:
                zrodla.setdefault(pole, set()).add(kolumna)
        return {pole: frozenset(kolumny) for pole, kolumny in zrodla.items()}

    def share_source(self, first: str, second: str) -> str | None:
        """Zwraca nazwę wspólnej kolumny, jeżeli oba pola pochodzą z tej samej.

        ``None`` znaczy „nie dzielą" **albo** „nie wiadomo" — rozróżnia je
        ``import_known``. Nie orzekamy o wspólnym źródle bez podstawy.
        """
        zrodla = self.column_sources()
        a = zrodla.get(first)
        b = zrodla.get(second)
        if not a or not b or a != b or len(a) != 1:
            return None
        return next(iter(a))
