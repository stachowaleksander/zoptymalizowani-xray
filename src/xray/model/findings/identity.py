# Implementuje zasadę 3 (determinizm) i zasadę 4 (audytowalność) z CLAUDE.md
# dla identyfikatorów rekordów FINDINGS.
"""Deterministyczne identyfikatory rekordów wynikowych.

## Dlaczego nie UUID

Zasada 3: te same dane plus ta sama wersja kodu równa się ten sam wynik. Losowy
identyfikator łamie to natychmiast — dwa przebiegi na tych samych danych dałyby różne
identyfikatory, więc nie dałoby się ani porównać przebiegów, ani odtworzyć śladu.

## Trzy warunki, które musi spełniać

**1. Kanoniczna serializacja przed skrótem.** Skrót liczymy z jawnie uporządkowanej
reprezentacji: posortowane klucze, zadeklarowane kodowanie, zero zależności od kolejności
iteracji po słowniku. Bez kanonizacji „deterministyczny" znaczyłoby tylko
„deterministyczny na tej wersji Pythona".

**2. Krotka tożsamości zapisywana obok skrótu.** Sam skrót jest ślepym zaułkiem dla
audytu — nie da się z niego odtworzyć, z czego powstał. Dlatego składniki tożsamości są
osobnymi polami rekordu, a rekord sprawdza przy powstaniu, że jego identyfikator zgadza
się ze skrótem tych pól. Zasada 4 wymaga, żeby każda liczba prowadziła do źródła;
identyfikator również.

**3. Wersja kontraktu w krotce tożsamości.** Zmiana kontraktu ma produkować nowe
identyfikatory, a nie po cichu nadpisywać stare rekordy inną treścią.
"""

import datetime as dt
import json
from collections.abc import Mapping
from hashlib import blake2b
from typing import Any

CONTRACT_VERSION = "ZOP-TECH-01/v0.1"
"""Wersja kontraktu FINDINGS wchodząca do krotki tożsamości.

Zmiana kontraktu (dodanie pola tożsamości, zmiana znaczenia istniejącego) wymaga zmiany
tej wartości. Wtedy rekordy policzone na nowym kontrakcie dostają nowe identyfikatory
i nie mieszają się ze starymi.
"""

IDENTITY_ALGORITHM_VERSION = "1"
"""Domyślna wersja tożsamości. **Należy do kształtu krotki, nie do systemu.**

Każdy rodzaj rekordu ma własną linię wersji, bo każdy ma własną krotkę tożsamości.
Zmiana krotki ``RunRef`` nie ma nic wspólnego z krotką ``FindingRecord`` — jedna wspólna
stała unieważniałaby weryfikację rekordów, których zmiana w ogóle nie dotyczyła.
Rekord deklaruje swoją wersję w polu ``identity_algorithm_version``, a rodzaj rekordu
podaje własną domyślną (patrz ``xray.store.runs``).

**Kiedy trzeba podnieść wersję danego rodzaju rekordu** — każda z tych zmian daje inny
skrót dla tej samej treści:

- dodanie albo usunięcie pola w krotce tożsamości **tego** rekordu (``identity_of``),
- zmiana kanonizacji (``_canonical``, ``canonical_form``): kolejność kluczy, format daty,
  separatory, kodowanie — ta dotyczy wszystkich rodzajów naraz,
- zmiana funkcji skrótu, jego długości albo sposobu budowania prefiksu.

**Dlaczego zapisana w rekordzie, a nie tylko w kodzie.** ``contract_version`` mówi, jakie
pola ma rekord; wersja tożsamości — jak z nich policzono skrót. Bez tej drugiej nie dałoby
się odróżnić rekordu policzonego starszą wersją od uszkodzonego, a jedynym wyjściem byłaby
migracja całego magazynu przy każdej zmianie.

## Czego ten mechanizm NIE robi

Rejestr ``_ALGORITHMS`` trzyma funkcje skrótu, ale **nie stare kształty krotek**. Rekord
zapisany z wersją ``"1"`` i odczytany kodem, w którym ``identity_of`` ma dodatkowe pole,
przejdzie przez **bieżącą** krotkę i zostanie odrzucony jako zmieniony.

Dziś potrafimy więc powiedzieć „nie znam wersji 2", ale **nie** potrafimy powiedzieć
„umiem odczytać wersję 1". Podniesienie wersji rodzaju rekordu wymaga migracji tego, co
już zapisano.

Mechanizm zgodności wstecz jest **świadomie odroczony** — patrz
docs/notatka-techniczna.md, wpis DT-14. Dopóki magazyn jest pusty, koszt podniesienia
wersji wynosi zero.
"""

_DIGEST_BYTES = 16
"""128 bitów skrótu. Nie jest to zabezpieczenie kryptograficzne, tylko stabilna
tożsamość — chodzi o brak kolizji przy rozsądnej liczbie rekordów, nie o odporność
na atak."""


class UnknownIdentityAlgorithm(LookupError):
    """Rekord wskazuje wersję algorytmu, której ta wersja kodu nie zna.

    Osobny wyjątek, a nie ``ValueError``, bo to **inna sytuacja niż niezgodność
    identyfikatora**: tam rekord został po zapisie zmieniony, tu jest w porządku, tylko
    czyta go starsze wydanie systemu. Mylenie tych dwóch przypadków kazałoby uznać
    poprawne dane za uszkodzone.
    """


def _canonical(value: Any) -> Any:
    """Sprowadza wartość do postaci, którą JSON serializuje jednoznacznie.

    Daty i znaczniki czasu zapisujemy w ISO 8601, bo ich domyślna reprezentacja
    w ``json`` nie istnieje, a ``str()`` zależy od implementacji. Krotki i listy dają ten
    sam zapis, bo różnica między nimi jest techniczna, a nie znaczeniowa.
    """
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, (dt.datetime, dt.date)):
        return value.isoformat()
    if isinstance(value, Mapping):
        return {str(k): _canonical(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_canonical(v) for v in value]
    raise TypeError(
        f"wartość typu {type(value).__name__} nie ma kanonicznej reprezentacji; "
        "krotka tożsamości może zawierać wyłącznie wartości proste, daty, "
        "odwzorowania i sekwencje"
    )


def canonical_form(identity: Mapping[str, Any]) -> str:
    """Zwraca kanoniczny zapis krotki tożsamości.

    Funkcja jest publiczna celowo: to ona, a nie sam skrót, jest tym, co da się obejrzeć
    przy audycie i porównać między przebiegami.
    """
    return json.dumps(
        _canonical(identity),
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    )


def _compute_id_v1(prefix: str, identity: Mapping[str, Any]) -> str:
    """Algorytm tożsamości w wersji 1: blake2b-128 nad kanonicznym JSON-em."""
    digest = blake2b(
        canonical_form(identity).encode("utf-8"), digest_size=_DIGEST_BYTES
    ).hexdigest()
    return f"{prefix}-{digest}"


_ALGORITHMS: dict[str, Any] = {
    "1": _compute_id_v1,
    # Wersja 2 to inny KSZTAŁT KROTKI (RunRef zyskał profile_digest), a nie inna funkcja
    # skrótu — dlatego wskazuje tę samą. Wersja mówi „jak policzono tożsamość tego
    # rodzaju rekordu", a na to składa się i co hashujemy, i czym.
    "2": _compute_id_v1,
}
"""Rejestr wersji algorytmu tożsamości.

Dziś jest jedna wersja, więc rozgałęzienia faktycznie nie ma. Jest natomiast **miejsce**,
w którym powstanie: gdy dojdzie wersja 2, stare rekordy nadal będą sprawdzane wersją 1,
którą same wskazują, zamiast być masowo odrzucane.
"""


def compute_id(
    prefix: str,
    identity: Mapping[str, Any],
    *,
    algorithm_version: str = IDENTITY_ALGORITHM_VERSION,
) -> str:
    """Liczy deterministyczny identyfikator z krotki tożsamości.

    ``algorithm_version`` wskazuje, którym algorytmem liczyć. Przy sprawdzaniu rekordu
    przekazujemy wersję **z rekordu**, a nie bieżącą stałą — dzięki temu rekord zapisany
    starszym algorytmem nadal się zgadza.

    Prefiks (np. ``"FND"``) nie wchodzi do skrótu — służy wyłącznie temu, żeby po samym
    identyfikatorze było widać, jakiego rekordu dotyczy. Dwa rekordy różnych typów
    o przypadkowo identycznej krotce tożsamości nadal dostaną różne identyfikatory,
    bo krotka zawiera pola właściwe dla typu.

    Nieznana wersja algorytmu podnosi ``UnknownIdentityAlgorithm``, a nie zwykły błąd
    niezgodności: rekord zapisany nowszą wersją kodu **nie jest uszkodzony** i komunikat
    musi to rozróżniać.
    """
    try:
        algorytm = _ALGORITHMS[algorithm_version]
    except KeyError:
        raise UnknownIdentityAlgorithm(
            f"nieznana wersja algorytmu tożsamości {algorithm_version!r}; "
            f"ta wersja kodu zna: {', '.join(sorted(_ALGORITHMS))}. "
            "Rekord nie jest uszkodzony — został zapisany innym wydaniem systemu"
        ) from None
    return algorytm(prefix, identity)

