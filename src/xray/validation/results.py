# Implementuje ZOP-TECH-01 v0.1 pkt 5.3 (rejestr kontroli) oraz zasadę 4 z CLAUDE.md
# (każda liczba prowadzi do rekordów źródłowych).
"""Wynik kontroli danych.

Każda liczba w wyniku ma podstawę i dowód: albo identyfikatory wierszy przyjętych, albo
adresy wierszy odrzuconych. Bez tego kontrola produkowałaby liczbę, której nie da się
sprawdzić.
"""

from collections.abc import Sequence
from enum import StrEnum
from typing import Self

from pydantic import BaseModel, ConfigDict, model_validator

from xray.model.enums import ValidationStatus

EVIDENCE_LIMIT = 50
"""Ile pojedynczych dowodów najwyżej trafia do jednej obserwacji.

Kolumna z pięcioma tysiącami braków dałaby obserwację z pięcioma tysiącami
identyfikatorów: raport przestałby być czytelny, a magazyn urósłby o dane, których nikt
nie przeczyta. Firma syntetyczna — 24 miesiące razy sto zasobów — wywołałaby to od razu.

Liczba jest już w ``value``, więc dowód nie musi być kompletny. Musi być **reprezentatywny
i uczciwie oznaczony** przez ``evidence_truncated``.
"""


TEXT_VALUE_LIMIT = 200
"""Ile znaków najwyżej mieści ``text_value``.

``text_value`` niesie **fakt**, a nie zdanie: datę, kod, nazwę wariantu. Wyjaśnienie ma
swoje miejsce w ``basis``. Bez twardej granicy sprawdzanej w walidatorze za trzy miesiące
ktoś wstawi tam opis, a raport straci pole nadające się do odczytu maszynowego.
"""

OBSERVATION_LIMIT = 100
"""Ile obserwacji najwyżej mieści jeden wynik kontroli.

Ten sam problem co przy ``EVIDENCE_LIMIT``, o poziom wyżej: tysiąc grup duplikatów to
tysiąc obserwacji, a wysoka liczność ``case_id`` może dać setki grup wariantów. Wynik
przestałby być czytelny, a magazyn urósłby o dane, których nikt nie przeczyta.

Przycięcie jest **deterministyczne** (kolejność powstawania) i **uczciwie oznaczone**:
pominięte grupy zgłasza osobna obserwacja, a nie flaga na wyniku — bo to fakt o danych,
mierzalny liczbą, a nie właściwość raportu.
"""


class NotAssessedReason(StrEnum):
    """Dlaczego kontrola nie dała statusu.

    ``status = None`` powstaje z różnych powodów, a raport jakości danych ma odpowiedzieć
    na pytanie „ile kontroli nie dało wyniku i dlaczego". Na prozie z ``basis`` nie da się
    tego policzyć, więc powód ma zamknięty katalog.

    ``insufficient_basis`` jest zapożyczeniem terminu z ZOP-CONF-01 (tam: wartość
    ``management_attention_route``). Znaczenie jest pokrewne, ale rola inna — to powód
    braku statusu kontroli danych, a nie trasa uwagi zarządczej.
    """

    MISSING_INPUT = "missing_input"
    """Kontrola nie została uruchomiona: brakowało wymaganego wejścia (np. raportu
    importu). Nie znaczy to, że wynik jest zerowy — znaczy, że go nie ma."""

    INSUFFICIENT_BASIS = "insufficient_basis"
    """Kontrola została uruchomiona, ale dane nie pozwoliły odpowiedzialnie ocenić."""

    NOT_APPLICABLE = "not_applicable"
    """Kontrola nie dotyczy tej tabeli — brakuje pól, o których mówi."""


class CheckObservation(BaseModel):
    """Pojedyncza zmierzona rzecz wraz z dowodem.

    Obserwacje są **rozłączne i nieaddytywne**. Dwie obserwacje o różnym ``measure`` mierzą
    różne zjawiska i ich suma nie znaczy nic — dlatego w wyniku nie ma żadnego pola
    zbiorczego, w którym dałoby się je dodać.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    subject: str
    """Czego dotyczy pomiar: pole, wartość klucza albo okres."""

    measure: str
    """Co zmierzono, np. ``"missing_values"``. Nazwa rozstrzyga o rozłączności."""

    value: float | None = None
    """Zmierzona wielkość. Dla miary będącej wielkością ``None`` znaczy **nieznana**,
    nigdy zero."""

    text_value: str | None = None
    """Fakt, który nie jest wielkością: granica okresu w ISO, kod, nazwa wariantu.

    Obserwacja niesie **albo** wielkość, **albo** fakt tekstowy — nigdy oba. Dla miary
    niebędącej wielkością ``value`` po prostu nie jest używane.

    Obie wartości puste są dopuszczalne i znaczą „nieznane" — tak wygląda
    ``time_basis_used`` po rozstrzygnięciu A-01. Wtedy ``basis`` musi powiedzieć dlaczego.
    """

    basis: str
    """Na jakiej podstawie policzono tę wartość. Wymagana, niepusta."""

    evidence_row_ids: tuple[str, ...] = ()
    """Identyfikatory wierszy przyjętych, których dotyczy pomiar."""

    evidence_source_rows: tuple[tuple[str, int], ...] = ()
    """Adresy wierszy odrzuconych jako pary ``(source_id, numer wiersza w pliku)``.

    Wiersz odrzucony nigdy nie dostał ``row_id`` — istnieje wyłącznie jako pozycja
    w raporcie importu. Sam numer wiersza nie byłby adresem: tabela może być zasilona
    z kilku plików i „wiersz 7" nie mówi, w którym. Para mówi: ten plik, ten wiersz.
    """

    evidence_truncated: bool = False
    """Czy dowód jest próbką, a nie kompletem.

    Bez tego pola skrócona lista wyglądałaby identycznie jak pełna — czyli wynik mówiłby
    coś innego, niż jest. Ten sam błąd co zero w miejscu braku.
    """

    @property
    def is_unknown(self) -> bool:
        """Czy obserwacja mówi „nieznane".

        Kontrakt zna tę definicję — obie wartości puste — ale dopóki siedziała wyłącznie
        w docstringu, każdy test odtwarzał ją ręcznie i mógł odtworzyć niepełnie. Trzy
        fałszywie przechodzące testy z rzędu przestały być kwestią uwagi, a stały się
        kwestią narzędzia: definicja ma być jedna i wystawiona.
        """
        return self.value is None and self.text_value is None

    @model_validator(mode="after")
    def _check_basis_and_limits(self) -> Self:
        if not self.basis.strip():
            raise ValueError("basis jest wymagana: liczba bez podstawy nie jest dowodem")
        if not self.subject.strip() or not self.measure.strip():
            raise ValueError("subject i measure nie mogą być puste")
        if self.value is not None and self.text_value is not None:
            raise ValueError(
                "obserwacja niesie albo wielkość, albo fakt tekstowy — nigdy oba; "
                "wyjaśnienie należy do basis"
            )
        if self.text_value is not None and len(self.text_value) > TEXT_VALUE_LIMIT:
            raise ValueError(
                f"text_value przekracza {TEXT_VALUE_LIMIT} znaków; niesie fakt "
                "(datę, kod, nazwę), a nie zdanie — wyjaśnienie należy do basis"
            )
        if len(self.evidence_row_ids) > EVIDENCE_LIMIT:
            raise ValueError(
                f"dowód przekracza granicę {EVIDENCE_LIMIT}; użyj CheckObservation.create, "
                "które przycina próbkę deterministycznie i oznacza ją jako skróconą"
            )
        if len(self.evidence_source_rows) > EVIDENCE_LIMIT:
            raise ValueError(f"dowód przekracza granicę {EVIDENCE_LIMIT}")
        return self

    @classmethod
    def create(
        cls,
        *,
        subject: str,
        measure: str,
        basis: str,
        value: float | None = None,
        text_value: str | None = None,
        evidence_row_ids: tuple[str, ...] = (),
        evidence_source_rows: tuple[tuple[str, int], ...] = (),
    ) -> "CheckObservation":
        """Buduje obserwację, przycinając dowód do granicy i oznaczając skrócenie.

        Próbka to **pierwsze N w podanej kolejności**, a kolejność pochodzi z indeksu
        ramki. Wybór losowy dałby różne dowody dla tych samych danych w dwóch przebiegach,
        co łamie zasadę 3.
        """
        przyciete = (
            len(evidence_row_ids) > EVIDENCE_LIMIT
            or len(evidence_source_rows) > EVIDENCE_LIMIT
        )
        return cls(
            subject=subject,
            measure=measure,
            value=value,
            text_value=text_value,
            basis=basis,
            evidence_row_ids=tuple(evidence_row_ids[:EVIDENCE_LIMIT]),
            evidence_source_rows=tuple(evidence_source_rows[:EVIDENCE_LIMIT]),
            evidence_truncated=przyciete,
        )


def cap_observations(
    observations: Sequence[CheckObservation],
    *,
    subject: str,
    basis: str,
) -> tuple[CheckObservation, ...]:
    """Przycina listę obserwacji do granicy i dopisuje obserwację o pominiętych.

    Przycięcie zachowuje **pierwsze** obserwacje w kolejności powstawania, bo kolejność
    powstawania pochodzi z indeksu ramki i jest deterministyczna. Wybór losowy albo
    sortowanie po wartości dałyby różny wynik dla tych samych danych.

    Pominięcie zgłasza **obserwacja**, a nie flaga na wyniku: liczba pominiętych grup
    jest faktem o danych, mierzalnym liczbą.
    """
    if len(observations) <= OBSERVATION_LIMIT:
        return tuple(observations)

    zachowane = tuple(observations[: OBSERVATION_LIMIT - 1])
    pominiete = len(observations) - len(zachowane)
    return zachowane + (
        CheckObservation.create(
            subject=subject,
            measure="observations_omitted",
            value=float(pominiete),
            basis=(
                f"{basis} Wynik pokazuje pierwsze {len(zachowane)} z "
                f"{len(observations)} w kolejności powstawania; pozostałe pominięto, "
                f"żeby raport pozostał czytelny."
            ),
        ),
    )


class CheckOutcome(BaseModel):
    """To, co zwraca sama kontrola.

    Kontrola nie buduje pełnego ``CheckResult``: swojego ``check_id`` ani nazwy tabeli nie
    przepisuje, bo przepisywanie daje okazję do pomyłki. Składa je rejestr.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    status: ValidationStatus | None
    basis: str
    observations: tuple[CheckObservation, ...] = ()
    not_assessed_reason: NotAssessedReason | None = None

    @model_validator(mode="after")
    def _check_consistency(self) -> Self:
        if not self.basis.strip():
            raise ValueError("basis jest wymagana zawsze, także przy braku statusu")
        if self.status is None and self.not_assessed_reason is None:
            raise ValueError(
                "brak statusu wymaga powodu z katalogu NotAssessedReason; "
                "sama proza w basis nie da się policzyć w raporcie jakości danych"
            )
        if self.status is not None and self.not_assessed_reason is not None:
            raise ValueError("status i powód braku statusu wykluczają się")
        if len(self.observations) > OBSERVATION_LIMIT:
            raise ValueError(
                f"wynik zawiera {len(self.observations)} obserwacji przy granicy "
                f"{OBSERVATION_LIMIT}; użyj cap_observations, które przycina "
                "deterministycznie i zgłasza pominięte osobną obserwacją"
            )
        return self


class CheckResult(BaseModel):
    """Wynik jednej kontroli dla jednej tabeli.

    ``status = None`` znaczy „nieoznaczony". Nie dopisujemy czwartej wartości do
    ``ValidationStatus``, bo karty mówią wprost, że kontrola zwraca PASS, WARNING albo
    CRITICAL (ZOP-XR-FIN-01 rozdz. 3, ZOP-XR-CAP-01 rozdz. 4). Kontrola bez podstawy nie
    zwróciła statusu, a ``null`` jest u nas poprawnym wynikiem (zasada 5).
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    check_id: str
    control_number: int
    """Numer kontroli z ZOP-TECH-01 pkt 5.3, żeby wynik dało się przypisać do karty."""

    table_name: str
    status: ValidationStatus | None
    basis: str
    observations: tuple[CheckObservation, ...] = ()
    not_assessed_reason: NotAssessedReason | None = None

    @property
    def assessed(self) -> bool:
        """Czy kontrola dała status."""
        return self.status is not None
