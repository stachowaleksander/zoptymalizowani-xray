# Implementuje ślad przebiegu diagnostycznego (CLAUDE.md: store/ — findings i ślad)
# oraz zasadę 3 (determinizm) i 4 (audytowalność).
"""Przebieg: tożsamość wyliczana z tego, co weszło.

## Po co przebieg ma własną tożsamość

``finding_id`` powstaje z ``test_id + scope + period + wersje``. **Dane wejściowe nie
wchodzą do tożsamości wyniku.** Klient przysyła poprawiony plik, uruchamiamy przebieg
ponownie — ten sam test na tym samym zakresie i okresie daje ten sam ``finding_id``
przy innej treści. Dwie różne odpowiedzi na to samo pytanie.

Nadpisanie kasowałoby ślad, czego ZOP-PRI-01 rozdz. 3 zakazuje wprost dla ewaluacji
(„nie nadpisuje śladu wcześniejszej oceny"). Odrzucenie blokowałoby uprawniony przypadek.
Dlatego wynik jest kluczowany parą ``(finding_id, run_id)``.

## Co z tego wynika i czego nie wolno zepsuć

Dwa wiersze o tym samym ``finding_id`` i różnym ``run_id`` to **dwie odpowiedzi na to samo
pytanie**, dane w różnych momentach na różnych danych. Znaczy to, że po ``finding_id`` da
się prześledzić **historię jednego wyniku przez kolejne przebiegi**: jak zmieniała się
luka, kiedy status przestał być ``NO_ADVERSE_SIGNAL``.

Ta właściwość jest głównym zyskiem z takiego klucza i najłatwiej ją zepsuć przy pierwszej
„optymalizacji" schematu — na przykład zwężając klucz do samego ``finding_id``, żeby
uniknąć duplikatów. Historii, raz utraconej, nikt później nie odtworzy.

## Tożsamość przebiegu

``run_id`` liczymy ze **skrótów treści przyjętych rekordów** dostarczonych przez raporty
importu, liczby przyjętych i odrzuconych wierszy oraz wersji kontraktu i algorytmu
tożsamości. Identyfikator źródła (nazwa pliku) **nie wchodzi** — patrz ``identity_of``.

Skutek jest dokładnie taki, jakiego chcemy:

- ten sam plik dwa razy → ten sam ``run_id`` → zapis jest **idempotentny**,
- poprawiony plik → inny ``run_id`` → **obie odpowiedzi zostają** i dają się porównać,
- przeformatowanie pliku (CSV → XLSX) bez zmiany wartości → **ten sam** ``run_id``,
  bo skrót liczy się z treści rekordów, a nie z bajtów pliku.

``executed_at`` jest polem audytowym **poza tożsamością** — tak jak ``imported_at``
w raporcie importu. Gdyby weszło do skrótu, dwa przebiegi na tych samych danych dałyby
różne identyfikatory, co łamie zasadę 3.
"""

import datetime as dt
from collections.abc import Sequence

from pydantic import BaseModel, ConfigDict

from xray.ingest.report import ImportReport
from xray.mapping.profile import MappingProfile
from xray.model.findings.identity import (
    CONTRACT_VERSION,
    canonical_form,
    compute_id,
)

_RUN_PREFIX = "RUN"

RUN_IDENTITY_VERSION = "2"
"""Wersja tożsamości przebiegu. **Własna, nie wspólna z rekordami FINDINGS.**

Podniesiona z ``"1"`` na ``"2"``, gdy krotka tożsamości przebiegu zyskała
``profile_digest``. Krotka ``FindingRecord`` się nie zmieniła, więc jej wersja **zostaje**
``"1"``: jedna wspólna stała unieważniałaby weryfikację rekordów, których zmiana w ogóle
nie dotyczyła.

Dodanie pola do krotki i podniesienie wersji weszły **jedną zmianą**. W dwóch podejściach,
z czymkolwiek uruchomionym pomiędzy, powstałyby rekordy deklarujące wersję ``"1"``, a
policzone krotką wersji ``"2"`` — i nic nie odróżniłoby ich później od uszkodzonych. Ta
sama klasa błędu, przed którą wersjonowanie ma chronić, wpuszczona przez kolejność kroków.
"""


class RunInput(BaseModel):
    """Opis jednego wejścia przebiegu: co wczytano i z czego.

    Zapisujemy **z czego** powstał skrót, a nie tylko sam skrót. Skrót w izolacji jest
    ślepym zaułkiem — ten sam zarzut, który postawiliśmy przy ``finding_id``. Na pytanie
    „dlaczego ten przebieg dostał ten identyfikator" ma dać się odpowiedzieć bez zgadywania.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    table_name: str
    source_id: str
    content_digest: str
    records_accepted: int
    records_rejected: int


class RunRef(BaseModel):
    """Przebieg diagnostyczny wraz z tożsamością wyliczoną z wejścia."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    run_id: str
    dataset_id: str
    inputs: tuple[RunInput, ...]
    profile_digest: str | None = None
    """Skrót znaczącej treści profilu mapowania. ``None`` = przebieg bez profilu.

    Bez tego pola ``plan_metrics`` byłyby niewidoczne dla tożsamości: nie zmieniają treści
    żadnego rekordu, więc nie zmieniają ``content_digest`` — a zmieniają wynik, bo dopiero
    z nimi PLAN może służyć jako ``reference_type = plan_budget``. Skutkiem byłby ten sam
    ``run_id`` przy innej treści, czyli ``ConflictingRun`` z komunikatem „przepływ nie jest
    deterministyczny", choć jest.
    """

    contract_version: str = CONTRACT_VERSION
    identity_algorithm_version: str = RUN_IDENTITY_VERSION

    executed_at: dt.datetime | None = None
    """Kiedy wykonano przebieg. Pole audytowe, **poza tożsamością**."""

    @classmethod
    def identity_of(
        cls,
        *,
        dataset_id: str,
        inputs: Sequence[RunInput],
        profile_digest: str | None = None,
        contract_version: str = CONTRACT_VERSION,
        identity_algorithm_version: str = RUN_IDENTITY_VERSION,
    ) -> dict[str, object]:
        """Krotka tożsamości przebiegu.

        **Do skrótu wchodzi to, co wpływa na wynik**, a nie wszystko, co wiemy o wejściu.

        ``source_id`` niesie nazwę pliku i **celowo nie wchodzi**: ten sam zbiór zapisany
        jako ``koszty.csv`` i jako ``koszty.xlsx`` musi dać ten sam ``run_id``, bo zmiana
        formatu zapisu nie jest zmianą danych. Pochodzenie zostaje zapisane obok, w polu
        ``inputs``, i jest dostępne przy audycie.

        ``records_rejected`` wchodzi, bo wpływa: odrzucenia czyta kontrola 2 i kontrola 3,
        a ich wynik może zablokować test. Dwa pliki o identycznej treści przyjętej, ale
        różnej liczbie odrzuceń, dają inny obraz jakości danych.

        Wejścia porządkujemy po nazwie tabeli i skrócie treści, żeby kolejność wywołań
        importu nie zmieniała ``run_id``.
        """
        uporzadkowane = sorted(
            (
                {
                    "table_name": wejscie.table_name,
                    "content_digest": wejscie.content_digest,
                    "records_accepted": wejscie.records_accepted,
                    "records_rejected": wejscie.records_rejected,
                }
                for wejscie in inputs
            ),
            key=lambda w: (w["table_name"], w["content_digest"]),
        )
        return {
            "dataset_id": dataset_id,
            "inputs": uporzadkowane,
            "profile_digest": profile_digest,
            "contract_version": contract_version,
            "identity_algorithm_version": identity_algorithm_version,
        }

    @classmethod
    def create(
        cls,
        *,
        dataset_id: str,
        reports: Sequence[ImportReport],
        profile: MappingProfile | None = None,
        executed_at: dt.datetime | None = None,
        contract_version: str = CONTRACT_VERSION,
        identity_algorithm_version: str = RUN_IDENTITY_VERSION,
    ) -> "RunRef":
        """Buduje przebieg z raportów importu.

        Skróty treści są już policzone — powstały przyrostowo przy imporcie, gdy każdy
        rekord i tak przechodził przez bramkę kontraktu. Drugiego przejścia po danych nie
        ma.

        **Skrót profilu składamy tutaj, z raportów, które i tak dostajemy.** Przyjmowanie
        gotowego ``profile_digest`` znaczyłoby, że kompletność ``applied_columns`` zależy
        od pamięci wywołującego: skrót złożony z czterech tabel zamiast pięciu daje inny
        wynik i **żaden błąd nie powstaje**. To ta sama klasa co „pole i wersja w dwóch
        krokach", przesunięta o jedno wywołanie dalej. Kompletność ma wynikać
        z konstrukcji, nie z uwagi.
        """
        if not reports:
            raise ValueError(
                "przebieg bez raportów importu nie ma z czego wyliczyć tożsamości; "
                "nie da się wtedy powiedzieć, na jakich danych powstał wynik"
            )
        obce = {r.source.dataset_id for r in reports} - {dataset_id}
        if obce:
            raise ValueError(
                f"raporty importu pochodzą z innych zbiorów danych: {', '.join(sorted(obce))}"
            )

        inputs = tuple(
            RunInput(
                table_name=raport.table_name,
                source_id=raport.source.source_id,
                content_digest=raport.content_digest,
                records_accepted=raport.records_accepted,
                records_rejected=raport.records_rejected,
            )
            for raport in reports
        )
        profile_digest = (
            profile.semantic_digest(_applied_by_table(reports))
            if profile is not None
            else None
        )
        identity = cls.identity_of(
            dataset_id=dataset_id,
            inputs=inputs,
            profile_digest=profile_digest,
            contract_version=contract_version,
            identity_algorithm_version=identity_algorithm_version,
        )
        return cls(
            run_id=compute_id(
                _RUN_PREFIX, identity, algorithm_version=identity_algorithm_version
            ),
            dataset_id=dataset_id,
            inputs=inputs,
            profile_digest=profile_digest,
            contract_version=contract_version,
            identity_algorithm_version=identity_algorithm_version,
            executed_at=executed_at,
        )

    @property
    def input_digest(self) -> str:
        """Kanoniczny opis wejścia — dokładnie to, z czego policzono ``run_id``.

        Zapisywany obok skrótu, żeby na pytanie „dlaczego ten przebieg dostał ten
        identyfikator" dało się odpowiedzieć bez zgadywania. Skrót sam w sobie jest
        ślepym zaułkiem.
        """
        return canonical_form(
            self.identity_of(
                dataset_id=self.dataset_id,
                inputs=self.inputs,
                profile_digest=self.profile_digest,
                contract_version=self.contract_version,
                identity_algorithm_version=self.identity_algorithm_version,
            )
        )

    @property
    def provenance(self) -> str:
        """Pełne pochodzenie wejścia, wraz z identyfikatorami źródeł.

        Szersze niż ``input_digest``: zawiera ``source_id``, czyli to, z jakich plików
        dane przyszły. Nie wchodzi do skrótu — służy audytowi, nie tożsamości.
        """
        return canonical_form(
            {"inputs": [wejscie.model_dump() for wejscie in self.inputs]}
        )


def _applied_by_table(
    reports: Sequence[ImportReport],
) -> dict[str, tuple[tuple[str, str], ...]]:
    """Zbiera faktycznie użyte przypisania ze wszystkich raportów, tabela po tabeli.

    Tabela może być zasilona z kilku plików, a w każdym kolumna może nazywać się inaczej —
    zbieramy komplet i porządkujemy, żeby kolejność wywołań importu nie zmieniała skrótu.
    """
    zebrane: dict[str, set[tuple[str, str]]] = {}
    for raport in reports:
        zebrane.setdefault(raport.table_name, set()).update(raport.applied_columns)
    return {tabela: tuple(sorted(pary)) for tabela, pary in zebrane.items()}
