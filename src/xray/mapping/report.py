# Implementuje ZOP-TECH-01 v0.1 pkt 5.3 kontrola 1 — raport mapowania profilu na plik.
"""Raport mapowania: co z deklaracji wyszło na konkretnym pliku.

Profil jest **wejściem**, ten raport **wyjściem**. Rozdzielenie ma znaczenie praktyczne:
profil mówi, co klient zadeklarował; raport mówi, co z tego dało się zastosować.

## Trzy przypadki, których nie wolno zlewać w jeden

| Sytuacja | Pozycja raportu | Rozmowa z klientem |
| --- | --- | --- |
| pole bez klucza w profilu | ``fields_without_mapping`` | „nie przypisałeś tego pola" |
| przypisanie do nieistniejącej kolumny | ``declared_missing_columns`` | „nie ma takiej kolumny" |
| kolumna bez miejsca w kontrakcie | ``unmapped_columns`` | to nie zarzut, tylko informacja |

Czwarty przypadek — **nieznane pole kontraktu w profilu** — nie jest pozycją raportu,
tylko błędem wczytania profilu (``ProfileError``). Gdyby przechodził, kontrola 1
zgłosiłaby CRITICAL przeciwko danym klienta za naszą literówkę, a klient poszedłby szukać
w swoim eksporcie kolumny, której nigdy nie miał mieć.
"""

from collections.abc import Sequence
from typing import Self

from pydantic import BaseModel, ConfigDict, model_validator

from xray.mapping.profile import MappingProfile
from xray.model import TABLES


class MappingReport(BaseModel):
    """Wynik zastosowania profilu do jednej tabeli i jednego zestawu kolumn."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    table_name: str
    dataset_id: str
    profile_id: str
    profile_version: int

    mapped: tuple[tuple[str, str], ...] = ()
    """Przypisania, które dało się zastosować: ``(pole kontraktu, kolumna klienta)``."""

    unmapped_columns: tuple[str, ...] = ()
    """Kolumny obecne w pliku, dla których nie ma miejsca w kontrakcie.

    Pozycja w raporcie, **nie awaria**. Karty Core 10 definiują dziesiątki pól
    opcjonalnych, których kontrakt bazowy nie ma — kolumna dziś niezmapowana jutro może
    być polem rozszerzenia.
    """

    fields_without_mapping: tuple[str, ...] = ()
    """Pola kontraktu, których profil w ogóle nie przypisał."""

    declared_missing_columns: tuple[tuple[str, str], ...] = ()
    """Przypisania do kolumn, których w pliku nie było: ``(pole, deklarowana kolumna)``.

    Osobno od ``fields_without_mapping``, bo „nie przypisałeś" i „przypisałeś do
    nieistniejącej kolumny" to dwie różne rozmowy z klientem.
    """

    materialized_empty: tuple[str, ...] = ()
    """Pola spoza klucza naturalnego, które będą w całości puste.

    Skutek obu powyższych przyczyn łącznie. ``None`` oznacza tu **nieobecność kolumny**,
    a nie wartość zastępczą wstawioną w miejsce danych — patrz wpis B-06.
    """

    missing_key_fields: tuple[str, ...] = ()
    """Elementy klucza naturalnego bez kolumny w pliku.

    # ASSUMPTION: kryterium „kolumna wymagana" czeka na Michała — wpis B-06. Propozycja
    # robocza: element NATURAL_KEY → CRITICAL, pole spoza klucza → WARNING.
    """

    shared_source_columns: tuple[tuple[str, tuple[str, ...]], ...] = ()
    """Kolumny klienta zasilające więcej niż jedno pole: ``(kolumna, pola)``.

    Decyzja D-C dopuszcza to jako uprawnione (plik, w którym nazwa zasobu jest zarazem
    nazwą jednostki), ale ciche dopuszczenie ukrywałoby częstą pomyłkę w profilu.
    Odnotowujemy fakt; skutek dla kontroli, których sygnałem jest różnica między takimi
    polami, egzekwuje rejestr kontroli.
    """

    plan_metrics_declared: int = 0
    """Ile deklaracji zgodności miar planu niesie profil."""

    @model_validator(mode="after")
    def _check_raport(self) -> Self:
        if self.table_name not in TABLES:
            raise ValueError(f"nieznana tabela {self.table_name!r}")
        return self

    @property
    def column_map(self) -> dict[str, str]:
        """Przypisania do przekazania do ``ingest.load_table``."""
        return dict(self.mapped)

    @property
    def plan_budget_available(self) -> bool:
        """Czy PLAN może posłużyć jako ``reference_type = plan_budget``.

        Rozstrzygnięcie B-04: bez jawnej deklaracji zgodności definicji — nie może.
        """
        return self.plan_metrics_declared > 0

    def plan_budget_note(self) -> str:
        """Ogłoszenie stanu deklaracji miar planu.

        **Ogłaszane, a nie wywnioskowane** z pustej listy — ta sama racja, dla której
        „zmaterializowana jako pusta" jest oddzielona od „była, ale pusta". Czytający ma
        zobaczyć zdanie, a nie wnioskować z nieobecności.
        """
        if self.plan_budget_available:
            return (
                f"Profil deklaruje {self.plan_metrics_declared} zgodności definicji miar "
                "planu; PLAN może posłużyć jako reference_type = plan_budget dla "
                "zadeklarowanych miar."
            )
        return (
            "Profil nie deklaruje żadnej zgodności definicji miar planu (rozstrzygnięcie "
            "B-04), więc dla żadnej miary PLAN nie może posłużyć jako "
            "reference_type = plan_budget."
        )


def apply_profile(
    profile: MappingProfile, table_name: str, available_columns: Sequence[str]
) -> MappingReport:
    """Zestawia deklarację profilu z kolumnami, które faktycznie są w pliku."""
    if table_name not in TABLES:
        raise ValueError(f"nieznana tabela {table_name!r}")

    tabela = TABLES[table_name]
    zadeklarowane = profile.column_map(table_name)
    obecne = list(available_columns)
    obecne_zbior = set(obecne)

    # Kolejność wg kontraktu, nie wg iteracji po deklaracji.
    zastosowane = tuple(
        (pole, zadeklarowane[pole])
        for pole in tabela.model_fields
        if pole in zadeklarowane and zadeklarowane[pole] in obecne_zbior
    )
    brak_kolumny = tuple(
        (pole, zadeklarowane[pole])
        for pole in tabela.model_fields
        if pole in zadeklarowane and zadeklarowane[pole] not in obecne_zbior
    )
    bez_przypisania = tuple(
        pole for pole in tabela.model_fields if pole not in zadeklarowane
    )

    uzyte_kolumny = {kolumna for _, kolumna in zastosowane}
    niezmapowane = tuple(k for k in obecne if k not in uzyte_kolumny)

    puste_pola = {pole for pole, _ in brak_kolumny} | set(bez_przypisania)
    zmaterializowane = tuple(
        pole
        for pole in tabela.model_fields
        if pole in puste_pola and pole not in tabela.NATURAL_KEY
    )
    brakujacy_klucz = tuple(pole for pole in tabela.NATURAL_KEY if pole in puste_pola)

    wspolne: dict[str, list[str]] = {}
    for pole, kolumna in zastosowane:
        wspolne.setdefault(kolumna, []).append(pole)
    dzielone = tuple(
        (kolumna, tuple(pola)) for kolumna, pola in wspolne.items() if len(pola) > 1
    )

    return MappingReport(
        table_name=table_name,
        dataset_id=profile.dataset_id,
        profile_id=profile.profile_id,
        profile_version=profile.profile_version,
        mapped=zastosowane,
        unmapped_columns=niezmapowane,
        fields_without_mapping=bez_przypisania,
        declared_missing_columns=brak_kolumny,
        materialized_empty=zmaterializowane,
        missing_key_fields=brakujacy_klucz,
        shared_source_columns=dzielone,
        plan_metrics_declared=len(profile.plan_metrics),
    )
