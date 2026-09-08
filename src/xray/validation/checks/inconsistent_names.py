# Implementuje ZOP-TECH-01 v0.1 pkt 5.3, kontrola 6 — niespójne nazwy jednostek.
"""Kontrola 6: wartości podejrzanie podobne w tekstowych polach klucza.

Przykład z karty: „Dział A", „dział A" i „DZIAL_A" jako trzy wartości jednej rzeczy.
To wyznacza zakres normalizacji **porównawczej**: wielkość liter, białe znaki, znaki
rozdzielające i diakrytyka.

## Trzy rzeczy, których kontrola nie robi

**Nie scala i nie poprawia.** Zgłasza grupy wartości podejrzanie podobnych wraz z dowodem.
Czy „Dział A" i „DZIAL_A" to ta sama jednostka, rozstrzyga klient — fundament nie ma
podstawy, żeby wskazać wariant „właściwy". Klucz porównawczy powstaje wewnątrz kontroli,
służy wyłącznie do zgrupowania i **nie trafia do danych**; ramka zostaje nietknięta.

**Nie ukrywa reguły.** Cztery kroki normalizacji i wszystkie warianty surowe są wypisane
w ``basis``. Bez tego klient dostawałby zarzut bez możliwości sprawdzenia, na jakiej
podstawie go postawiono.

**Nie orzeka.** ``max_status = WARNING``, bo to **hipoteza tożsamości**, a hipoteza nie
jest faktem (zasada 6).

## Które pola

Wszystkie tekstowe elementy klucza naturalnego — czyli to, co zwraca ``text_key_fields()``:
``unit``, ``category``, ``product``, ``resource``, ``metric``, ``stage`` oraz ``case_id``.

``case_id`` wchodzi celowo. Wyłączenie go wymagałoby reguły „identyfikator techniczny",
której z kontraktu odczytać się nie da — dla modelu ``resource`` i ``case_id`` są tym
samym rodzajem pola, a wymyślenie takiej reguły łamie zasadę 1. Zjawisko jest przy tym
poważniejsze niż przy nazwie działu: „SPR-001" i „spr_001" w jednym zbiorze znaczyłyby tę
samą sprawę policzoną dwa razy w miarach procesowych.
"""

import unicodedata
from typing import ClassVar

from xray.model.enums import ValidationStatus
from xray.model.tables.base import text_key_fields
from xray.validation.base import CheckDeclaration, DataCheck
from xray.validation.context import ValidationContext
from xray.validation.results import CheckObservation, CheckOutcome, cap_observations

_SEPARATORY = "_-./:\\|"

_LITERY_NIEROZKLADALNE = {
    "ł": "l",
    "Ł": "L",
}
"""Litery, których rozkład NFKD **nie** zdejmuje.

NFKD rozkłada literę z diakrytykiem na literę bazową plus znak łączący — działa dla
``ą``, ``ć``, ``ę``, ``ń``, ``ó``, ``ś``, ``ź`` i ``ż``. Nie działa dla ``ł``, bo kreska
jest częścią samego znaku, a nie osobnym znakiem łączącym.

Bez tej podmiany przykład **z karty** nie przechodzi: ``Dział A`` dawałoby klucz
``dział a``, a ``DZIAL_A`` — ``dzial a``, czyli dwie różne grupy zamiast jednej.

Tabela jest celowo minimalna: zawiera to, czego wymaga przykład z karty. Inne alfabety
mają własne litery nierozkładalne (duńskie ``ø``, chorwackie ``đ``, niemieckie ``ß``) —
dokładamy je, gdy pojawi się przypadek, a nie zawczasu.
"""

OPIS_NORMALIZACJI = "wielkość liter, diakrytyka, znaki rozdzielające, białe znaki"
"""Reguła normalizacji w jednym zdaniu, wypisywana w podstawie każdej obserwacji."""


def comparison_key(value: str) -> str:
    """Sprowadza wartość do klucza porównawczego.

    Cztery kroki, dokładnie w zakresie wyznaczonym przez przykład z karty:

    1. ``casefold()`` — nie ``lower()``, bo ``casefold`` działa poprawnie poza ASCII,
    2. podmiana liter nierozkładalnych (``ł`` → ``l``) i rozkład NFKD z usunięciem znaków
       łączących — razem zdejmują diakrytykę,
    3. znaki rozdzielające (``_ - . / : \\ |``) i białe znaki → pojedyncza spacja,
    4. zwinięcie spacji i obcięcie brzegowych.

    ``Dział A``, ``dział A`` i ``DZIAL_A`` dają ten sam klucz ``dzial a`` — to jest
    dokładnie przykład z ZOP-TECH-01 pkt 5.3, kontrola 6.

    Wynik **nie trafia do danych**. Służy wyłącznie do zgrupowania wewnątrz kontroli.
    """
    tekst = value.casefold()
    podmienione = "".join(_LITERY_NIEROZKLADALNE.get(z, z) for z in tekst)
    rozlozony = unicodedata.normalize("NFKD", podmienione)
    bez_diakrytyki = "".join(z for z in rozlozony if not unicodedata.combining(z))
    zamienione = "".join(
        " " if z in _SEPARATORY or z.isspace() else z for z in bez_diakrytyki
    )
    return " ".join(zamienione.split())


class InconsistentNames(DataCheck):
    """Grupuje wartości sprowadzające się do wspólnego klucza porównawczego."""

    DECLARATION: ClassVar[CheckDeclaration] = CheckDeclaration(
        check_id="TECH01-VAL-06",
        control_number=6,
        title="Niespójne nazwy jednostek",
        requires_import_report=False,
        required_fields=(),
        requires_natural_key=True,
        # Hipoteza tożsamości, nie ustalenie. Zasada 6.
        max_status=ValidationStatus.WARNING,
    )

    def run(self, context: ValidationContext) -> CheckOutcome:
        pola = text_key_fields(context.table)
        ramka = context.frame
        obserwacje: list[CheckObservation] = []
        grup_razem = 0

        for pole in pola:
            kolumna = ramka[pole]
            znane = kolumna[kolumna.notna()]
            if znane.empty:
                continue

            # Kolejność grup i wariantów bierze się z kolejności wystąpienia w indeksie,
            # a nie z sortowania po wartości — dwa przebiegi mają dać ten sam wynik.
            warianty: dict[str, list[str]] = {}
            for wartosc in znane.astype(str):
                warianty.setdefault(comparison_key(wartosc), []).append(wartosc)

            for klucz, wystapienia in warianty.items():
                rozne = list(dict.fromkeys(wystapienia))
                if len(rozne) < 2:
                    continue
                grup_razem += 1
                # Warianty surowe wypisujemy dosłownie, wraz z liczbą wierszy każdego —
                # klient ma zobaczyć dokładnie to, co ma w danych.
                liczniki = ", ".join(
                    f"{w!r} ({wystapienia.count(w)} wierszy)" for w in rozne
                )
                nalezy = znane.astype(str).map(comparison_key) == klucz
                obserwacje.append(
                    CheckObservation.create(
                        subject=klucz,
                        measure="similar_value_variants",
                        # Liczba wariantów, nie wierszy: to dwie różne wielkości.
                        value=float(len(rozne)),
                        basis=(
                            f"Pole {pole}: {len(rozne)} warianty sprowadzają się do "
                            f"wspólnego klucza porównawczego {klucz!r}: {liczniki}. "
                            f"Normalizacja: {OPIS_NORMALIZACJI}. To hipoteza tożsamości, "
                            "nie ustalenie — czy to ta sama wartość, rozstrzyga klient."
                        ),
                        evidence_row_ids=tuple(str(i) for i in znane.index[nalezy]),
                    )
                )

        if not pola:
            return CheckOutcome(
                status=ValidationStatus.PASS,
                basis=(
                    f"Tabela {context.table_name} nie ma tekstowych pól klucza "
                    "naturalnego."
                ),
            )

        if grup_razem == 0:
            return CheckOutcome(
                status=ValidationStatus.PASS,
                basis=(
                    f"W polach {', '.join(pola)} tabeli {context.table_name} żadne dwie "
                    f"różne wartości nie sprowadzają się do wspólnego klucza "
                    f"porównawczego. Normalizacja: {OPIS_NORMALIZACJI}."
                ),
            )

        return CheckOutcome(
            status=ValidationStatus.WARNING,
            basis=(
                f"{grup_razem} grup wartości podejrzanie podobnych w polach "
                f"{', '.join(pola)} tabeli {context.table_name}. Normalizacja "
                f"porównawcza: {OPIS_NORMALIZACJI}. Kontrola niczego nie scala ani nie "
                "poprawia — wskazanie wariantu właściwego należy do klienta."
            ),
            observations=cap_observations(
                obserwacje,
                subject="similar_value_variants",
                basis=(
                    f"Grupy wartości podejrzanie podobnych w tabeli {context.table_name}."
                ),
            ),
        )
