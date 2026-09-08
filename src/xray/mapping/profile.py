# Implementuje ZOP-TECH-01 v0.1 pkt 10.3 (mapowanie kolumn klienta) oraz rozstrzygnięcia
# B-04 (jawne mapowanie miar planu), DT-05 (strefa organizacji) i DT-10 (dataset_id).
"""Profil mapowania: wczytanie i znacząca treść.

Profil jest **wejściem** — deklaracją klienta. To, co z niej wyszło na konkretnych
plikach, opisuje ``MappingReport`` w ``xray.mapping.report``.

## Bezpieczne wczytanie

``yaml.load`` z domyślnym loaderem buduje z treści pliku dowolne obiekty Pythona, a plik
przychodzi od klienta. Używamy ``_StrictLoader`` — podklasy ``SafeLoader``, która czyta
wyłącznie typy proste, a dodatkowo odrzuca powtórzony klucz.

## Dlaczego duplikat klucza jest błędem, a nie ostatnim wpisem

PyYAML przy powtórzonym kluczu **po cichu bierze ostatni**. Profil z dwoma wpisami
``unit:`` wyglądałby jak poprawny, a jedno z przypisań zniknęłoby bez śladu. To ta sama
klasa cichej utraty, przed którą broni ``ConflictingRun`` — więc odrzucamy jawnie.

## Kierunek zapisu: pole kontraktu → kolumna klienta

Kierunek nie jest kwestią gustu. Przy zapisie ``pole: kolumna`` niewyrażalne staje się
przypisanie **dwóch kolumn do jednego pola** — czyli przypadek zakazany decyzją D-B,
bo zsumowanie albo wybór byłyby regułą biznesową ukrytą w konfiguracji. Naturalne
pozostaje **jedna kolumna do dwóch pól** (D-C), bywające uprawnionym.
"""

import datetime as dt
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, Self

import yaml
from pydantic import BaseModel, ConfigDict, model_validator

from xray.model import TABLES
from xray.model.findings.identity import compute_id

_PROFILE_PREFIX = "PRF"


class ProfileError(ValueError):
    """Profil jest niepoprawny i nie da się go wczytać.

    Osobny wyjątek, bo to **nasza albo klienta pomyłka w deklaracji**, a nie problem
    z danymi. Rozróżnienie ma znaczenie praktyczne: literówka w nazwie pola kontraktu
    zgłoszona jako problem danych wysłałaby klienta na poszukiwanie kolumny, której
    nigdy nie miał mieć.
    """


class PlanMetricDeclaration(BaseModel):
    """Zadeklarowana zgodność miary planu z miarą testu (rozstrzygnięcie B-04)."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    plan_metric: str
    """Wartość ``PLAN.metric`` z danych klienta, bez normalizacji."""

    target_measure: str
    """Miara testu, której ta wartość odpowiada."""

    definition_match_basis: str
    """Na czym polega zgodność definicji obu miar.

    Wchodzi do skrótu znaczącej treści profilu — patrz wpis DT-13. To osąd, nie
    wyprowadzenie: zmiana z „obie miary liczą koszt osobodni tak samo" na „miary różnią
    się ujęciem VAT, przyjęto przybliżenie" nie rusza ani ``plan_metric``, ani
    ``target_measure``, a zmienia to, czy warunek ZOP-XR-FIN-01 rozdz. 6 jest spełniony.
    """

    declared_by: str
    declared_at: dt.date

    @model_validator(mode="after")
    def _check_wypelnione(self) -> Self:
        for nazwa in ("plan_metric", "target_measure", "definition_match_basis", "declared_by"):
            if not getattr(self, nazwa).strip():
                raise ValueError(f"{nazwa} nie może być puste")
        return self


class MappingProfile(BaseModel):
    """Profil mapowania jednego zbioru danych."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    profile_id: str
    profile_version: int
    dataset_id: str
    organization_timezone: str

    columns: Mapping[str, Mapping[str, str]]
    """Nazwa tabeli → (pole kontraktu → kolumna klienta)."""

    plan_metrics: tuple[PlanMetricDeclaration, ...] = ()

    @model_validator(mode="after")
    def _check_profil(self) -> Self:
        if not self.dataset_id.strip():
            raise ValueError("dataset_id nie może być pusty")

        nieznane_tabele = [t for t in self.columns if t not in TABLES]
        if nieznane_tabele:
            raise ValueError(
                f"profil odwołuje się do nieznanych tabel: {', '.join(sorted(nieznane_tabele))}; "
                f"ZOP-TECH-01 pkt 5.2 definiuje: {', '.join(TABLES)}"
            )

        for tabela, mapa in self.columns.items():
            pola = set(TABLES[tabela].model_fields)
            nieznane = [p for p in mapa if p not in pola]
            if nieznane:
                raise ValueError(
                    f"tabela {tabela}: profil przypisuje nieznane pola kontraktu "
                    f"{', '.join(sorted(nieznane))}. To pomyłka w deklaracji, a nie problem "
                    "z danymi klienta — gdyby przeszła, kontrola 1 zgłosiłaby CRITICAL "
                    "przeciwko danym za naszą literówkę"
                )
            puste = [p for p, k in mapa.items() if not str(k).strip()]
            if puste:
                raise ValueError(
                    f"tabela {tabela}: puste przypisanie dla pól {', '.join(sorted(puste))}; "
                    "brak przypisania wyraża się pominięciem klucza, nie pustą wartością"
                )
        return self

    # --- wczytanie -------------------------------------------------------------------

    @classmethod
    def load(cls, path: str | Path) -> "MappingProfile":
        """Wczytuje profil z pliku YAML."""
        sciezka = Path(path)
        try:
            tekst = sciezka.read_text(encoding="utf-8")
        except OSError as blad:
            raise ProfileError(f"nie da się odczytać profilu {sciezka}: {blad}") from blad

        try:
            surowy = yaml.load(tekst, Loader=_StrictLoader)  # noqa: S506 — własny loader oparty na SafeLoader
        except yaml.YAMLError as blad:
            raise ProfileError(f"profil {sciezka} nie jest poprawnym YAML-em: {blad}") from blad

        if not isinstance(surowy, dict):
            raise ProfileError(f"profil {sciezka} musi być odwzorowaniem na najwyższym poziomie")

        try:
            return cls.model_validate(surowy)
        except Exception as blad:
            raise ProfileError(f"profil {sciezka} jest niepoprawny: {blad}") from blad

    # --- znacząca treść ---------------------------------------------------------------

    def semantic_digest(
        self, applied_columns: Mapping[str, Sequence[tuple[str, str]]]
    ) -> str:
        """Skrót **znaczącej** treści profilu — wchodzi do tożsamości przebiegu.

        Bierze faktycznie użyte przypisania (z raportów importu), deklaracje miar planu
        i strefę organizacji.

        **Dlaczego użyte, a nie zadeklarowane:** profil może deklarować przypisania do
        kolumn, których w plikach nie było — te niczego nie zmieniły. Ta sama zasada,
        dla której ``source_id`` nie wchodzi do tożsamości przebiegu: liczy się to, co
        się wydarzyło.

        **Co świadomie zostaje poza skrótem:** ``profile_id`` i ``profile_version``
        (podniesienie numeru bez zmiany znaczenia tworzyłoby nowy przebieg — problem
        bajtów o poziom wyżej), komentarze i formatowanie pliku, ``declared_by``
        i ``declared_at`` (mówią kto, nie dlaczego to wolno).

        **Dlaczego skrót w ogóle istnieje:** ``plan_metrics`` nie zmienia treści żadnego
        rekordu, więc nie zmienia ``content_digest``, więc bez tego skrótu nie zmieniałaby
        ``run_id`` — a zmienia wynik, bo dopiero z nią PLAN może służyć jako
        ``reference_type = plan_budget``. Bez tego ten sam ``run_id`` niósłby inną treść
        i magazyn ogłosiłby ``ConflictingRun`` z komunikatem „przepływ nie jest
        deterministyczny", choć jest.
        """
        return compute_id(
            _PROFILE_PREFIX,
            {
                "applied_columns": {
                    tabela: [list(para) for para in sorted(pary)]
                    for tabela, pary in sorted(applied_columns.items())
                },
                "plan_metrics": sorted(
                    (
                        {
                            "plan_metric": d.plan_metric,
                            "target_measure": d.target_measure,
                            "definition_match_basis": d.definition_match_basis,
                        }
                        for d in self.plan_metrics
                    ),
                    key=lambda d: (d["plan_metric"], d["target_measure"]),
                ),
                "organization_timezone": self.organization_timezone,
            },
        )

    def column_map(self, table_name: str) -> dict[str, str]:
        """Przypisania zadeklarowane dla tabeli, w postaci przyjmowanej przez ``ingest``."""
        return dict(self.columns.get(table_name, {}))


class _StrictLoader(yaml.SafeLoader):
    """``SafeLoader`` odrzucający powtórzony klucz w tym samym odwzorowaniu.

    PyYAML domyślnie bierze po cichu ostatni wpis. Profil z dwoma wpisami ``unit:``
    wyglądałby jak poprawny, a jedno z przypisań zniknęłoby bez śladu — ta sama klasa
    cichej utraty, przed którą broni ``ConflictingRun``.

    Powtórzenie liczy się **w obrębie jednego odwzorowania**: ``unit`` występujące w mapie
    każdej tabeli jest w porządku.
    """


def _construct_mapping(loader: yaml.SafeLoader, node: yaml.MappingNode, deep: bool = False):
    widziane: set[Any] = set()
    for wezel_klucza, _ in node.value:
        klucz = loader.construct_object(wezel_klucza, deep=deep)
        if klucz in widziane:
            raise ProfileError(
                f"klucz {klucz!r} powtarza się w tym samym odwzorowaniu profilu "
                f"(linia {wezel_klucza.start_mark.line + 1}). PyYAML wziąłby po cichu "
                "ostatni wpis, a jedno z przypisań zniknęłoby bez śladu"
            )
        widziane.add(klucz)
    return yaml.SafeLoader.construct_mapping(loader, node, deep)


_StrictLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_mapping
)
