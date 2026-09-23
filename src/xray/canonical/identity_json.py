# Implementuje ZOP-XR-FOUNDATION-BIND-01 v1.1, §7 CANONICAL IDENTITY FRAMEWORK — profil
# XR_IDENTITY_CANONICAL_JSON_V1, przeniesiony bez zmiany przez v1.2 §17 (tabela WPŁYW NA
# IDENTITY VERSIONING, wiersz „Canonical JSON | XR_IDENTITY_CANONICAL_JSON_V1 | bez zmiany").
"""Kanoniczna postać JSON dla tożsamości — kontrakt międzyimplementacyjny.

## Czym to się różni od ``canonical_form``

``xray.model.findings.identity.canonical_form`` to **stabilny zapis naszych własnych
rekordów**: ma dawać ten sam wynik przy dwóch uruchomieniach tego samego kodu. Ten profil
to **kontrakt między implementacjami**: te same dane mają dać te same bajty w dowolnym
języku i dowolnej bibliotece, także u kogoś, kto sprawdza nas niezależnie. Stąd wszystkie
różnice:

- normalizacja Unicode NFC każdego klucza i każdego łańcucha — bez niej „ą" złożone
  i rozłożone dają różne bajty,
- **typy semantyczne**: data nie jest łańcuchem. ``canonical_form`` zapisuje datę przez
  ``isoformat()``, więc ``date(2026, 9, 1)`` i tekst ``"2026-09-01"`` mają dziś identyczną
  postać kanoniczną. Tutaj data to ``{"$type":"date","value":"2026-09-01"}`` i te dwie
  wartości nie mogą się zlać,
- **zbiór ≠ sekwencja**: sekwencja zachowuje kolejność, zbiór jest sortowany bajtowo,
- **liczby**: ``float`` jest odrzucany, bo z liczby binarnej nie da się zagwarantować
  postaci „plain-decimal bez zbędnych zer końcowych",
- **skrót**: SHA-256, 64 znaki lowercase hex, zamiast blake2b-128 (32 znaki).

Najważniejsza różnica jest jednak w postawie. ``canonical_form`` jest permisywny — musi
taki być, bo obsługuje generator syntetyczny i istniejące tożsamości. Ten profil jest
restrykcyjny: odrzuca wszystko, czego nie umie zapisać dokładnie. Każda cicha konwersja
znaczyłaby, że dwa różne wejścia mogą dostać jeden identyfikator.

## Dlaczego stary profil zostaje nietknięty

v1.1 §7 mówi wprost: „Profil nie zastępuje generatorów syntetycznych, content digestów,
profile_digest ani innych skrótów niezwiązanych z poniższymi identity". ``canonical_form``
napędza właśnie takie skróty — wartości generatora (``synth/values.py``), skrót treści
rekordu przy imporcie, odcisk kodu, tożsamość przebiegu. Zmiana kanonizacji zmieniłaby
wylosowane dane przy tym samym ziarnie. Do tego karta wykonawcza V12-R1 §1 ustala
``HISTORICAL_IDENTITY_REWRITE = false``, a v1.2 §7.2 —
``RESULT_IDENTITY_CROSS_VERSION_EQUIVALENCE_AUTOMATIC = false``: stary i nowy profil to
dwie domeny, nie dwie wersje tego samego.

## Czego tu nie ma

``XR_CANONICAL_MULTISET_V1`` należy do V12-R2 i karta zakazuje go w tej rundzie (§8, §13).
Profil zna **zbiór** i **sekwencję**; krotności nie zna.
"""

import datetime as dt
import hashlib
import json
import unicodedata
from collections.abc import Iterable, Mapping
from decimal import Decimal
from typing import Any

PROFILE = "XR_IDENTITY_CANONICAL_JSON_V1"
"""Nazwa profilu, którą kontrakt posługuje się we wszystkich formułach tożsamości."""

_TYPED_KEY = "$type"
"""Klucz zarezerwowany.

Gdyby wolno było podać go w zwykłym odwzorowaniu, dałoby się podrobić typowaną datę
słownikiem — i skrót przestałby rozróżniać dokładnie to, dla czego rozróżnienie
wprowadzono. Rezerwujemy sam ``$type``, a nie całą przestrzeń ``$``: kontrakt o niej nie
mówi, a szersza reguła byłaby regułą wymyśloną.
"""

PREFIXES: Mapping[str, str] = {
    # v1.1 §7, tabela profilu, wiersz „Prefix".
    "SCOPE": "BIND-01 v1.1 §7 (Prefix)",
    "REF": "BIND-01 v1.1 §7 (Prefix)",
    "RESULT": "BIND-01 v1.1 §7 (Prefix)",
    "REC": "BIND-01 v1.1 §7 (Prefix)",
    "SRCROW": "BIND-01 v1.1 §7 (Prefix)",
    "PARSE": "BIND-01 v1.1 §7 (Prefix)",
    "EXCL": "BIND-01 v1.1 §7 (Prefix)",
    "EXAPP": "BIND-01 v1.1 §7 (Prefix)",
    "RUN": "BIND-01 v1.1 §7 (Prefix)",
    "EXECFP": "BIND-01 v1.1 §7 (Prefix)",
    # Dwa prefiksy wprowadzone przez v1.2 — obowiązujący kontrakt, więc należą do
    # rejestru od razu. Rekordów, które ich używają, ta runda nie tworzy (P7 i P8).
    "RREC": 'BIND-01 v1.2 §7.4 (result_record_id = "RREC-" + SHA256(...))',
    "ECMP": 'BIND-01 v1.2 §7.4 (execution_comparison_id = "ECMP-" + SHA256(...))',
}
"""Zamknięty rejestr prefiksów wraz ze źródłem każdego.

Rejestr jest zamknięty celowo: prefiks nie wchodzi do skrótu, więc jest jedyną częścią
identyfikatora, której literówki nic nie wykryje.
"""


class CanonicalizationError(ValueError):
    """Wartości nie da się zapisać w tym profilu.

    Jeden wspólny przodek, żeby wołający mógł złapać „cokolwiek niekanonicznego", i pięć
    podklas, żeby test mógł sprawdzić **która** reguła zadziałała.
    """


class UnsupportedType(CanonicalizationError):
    """Typ wartości albo klucza nie ma reprezentacji w profilu."""


class DuplicateKey(CanonicalizationError):
    """Dwa klucze odwzorowania po normalizacji NFC są tym samym kluczem.

    v1.1 §7 wymaga kluczy unikalnych po normalizacji. Scalenie takich kluczy oznaczałoby
    cichą utratę jednej z wartości.
    """


class ReservedKey(CanonicalizationError):
    """Odwzorowanie użyło klucza zarezerwowanego dla postaci typowanej."""


class DuplicateSetMember(CanonicalizationError):
    """Zbiór zawiera dwa elementy o identycznej postaci kanonicznej.

    v1.1 §7: „canonical duplicates odrzucane jako duplicate set members". Czytamy to jako
    **odmowę**, nie jako deduplikację — i to nie z ostrożności, tylko z własnego
    doświadczenia. Cicha deduplikacja zbioru to dokładnie defekt U-2 zgłoszony do v1.1:
    jedno odrzucenie i pięć identycznych odrzuceń dawały ten sam skrót, bo krotność ginęła
    w zbiorze. Dla tej krotności powstał osobny profil ``XR_CANONICAL_MULTISET_V1``
    (v1.2 §9, runda V12-R2).

    Duplikat w zbiorze znaczy więc jedno z dwojga: albo pole naprawdę jest zbiorem i błąd
    jest po stronie wołającego, albo pole powinno być multisetem i krotność ma znaczenie.
    Odmowa obsługuje oba przypadki poprawnie; deduplikacja cicho niszczy drugi.
    """


class UnknownPrefix(LookupError):
    """Prefiks spoza rejestru z v1.1 §7 i v1.2 §7.4."""


class CanonicalSet:
    """Jawny znacznik semantyki zbioru.

    Zwykła lista jest **sekwencją**, bo v1.1 §7 stanowi: „Lista zostaje setem wyłącznie
    wtedy, gdy kontrakt pola jawnie nadaje jej set semantics. W przeciwnym razie jest
    sekwencją". Semantyki zbioru nie da się więc zgadnąć z typu Pythona — trzeba ją
    zadeklarować.

    Dlaczego własna klasa, a nie ``frozenset``: elementami bywają odwzorowania, a te nie
    są haszowalne. Do tego ``frozenset`` usunąłby duplikat, zanim zdążylibyśmy go
    zgłosić — patrz ``DuplicateSetMember``.
    """

    __slots__ = ("elements",)

    def __init__(self, elements: Iterable[Any]) -> None:
        self.elements: tuple[Any, ...] = tuple(elements)

    def __repr__(self) -> str:
        return f"CanonicalSet({list(self.elements)!r})"


def _string(value: str) -> str:
    """Łańcuch: najpierw NFC, potem standardowe escapowanie JSON.

    ``ensure_ascii=False`` zostawia znaki spoza ASCII w postaci surowej — profil mówi
    o bajtach UTF-8, a nie o sekwencjach ``\\uXXXX``.
    """
    return json.dumps(unicodedata.normalize("NFC", value), ensure_ascii=False)


def _integer(value: int) -> str:
    """Liczba całkowita w postaci base-10.

    ``str(int)`` w Pythonie nigdy nie da ani ``+``, ani zer wiodących, ani ``-0``, więc
    reguła „bez +, bez leading zeros; 0 jedyną reprezentacją zera" jest spełniona
    z konstrukcji.
    """
    return str(int(value))


def _decimal(value: Decimal) -> str:
    """Liczba dziesiętna: plain-decimal, bez wykładnika, bez zbędnych zer końcowych.

    Nie używamy ``Decimal.normalize()``: ta operacja przechodzi przez kontekst dziesiętny
    (domyślnie 28 cyfr znaczących) i potrafi zaokrąglić długą wartość, a dla ``100`` daje
    postać wykładniczą ``1E+2``. Działamy więc na krotce z ``as_tuple()``, gdzie żadna
    z tych rzeczy nie może się zdarzyć.

    Skutek, który jest tu istotny: ``Decimal("7.0")`` i ``7`` dają ten sam zapis ``7``.
    W profilu „number" to **jeden** typ semantyczny, więc dwie równe liczby muszą dać ten
    sam skrót — inaczej ta sama wartość wyprodukowałaby dwie tożsamości.
    """
    if not value.is_finite():
        raise CanonicalizationError(
            f"wartość {value!r} nie jest skończona; NaN i Inf są zabronione "
            "(v1.1 §7, wiersz Decimal)"
        )
    znak, cyfry, wykladnik = value.as_tuple()
    cyfry = list(cyfry)
    # Zera końcowe po przecinku nie zmieniają wartości, a zmieniłyby bajty.
    while wykladnik < 0 and cyfry and cyfry[-1] == 0:
        cyfry.pop()
        wykladnik += 1
    if not cyfry or set(cyfry) == {0}:
        # Zero ma jedną postać, także gdy przyszło jako -0.
        return "0"
    mantysa = "".join(str(cyfra) for cyfra in cyfry)
    if wykladnik >= 0:
        tekst = mantysa + "0" * wykladnik
    else:
        miejsca = -wykladnik
        if len(mantysa) <= miejsca:
            tekst = "0." + "0" * (miejsca - len(mantysa)) + mantysa
        else:
            tekst = mantysa[:-miejsca] + "." + mantysa[-miejsca:]
    return ("-" if znak else "") + tekst


def _typed(nazwa: str, wartosc: str) -> str:
    """Obiekt typowany ``{"$type": …, "value": …}``.

    Klucze są już w kolejności kanonicznej: ``$`` ma kod 0x24, ``v`` — 0x76.
    """
    return "{" + _string(_TYPED_KEY) + ":" + _string(nazwa) + ',"value":' + _string(wartosc) + "}"


def _rfc3339(value: dt.datetime) -> str:
    """Znacznik czasu ze świadomym przesunięciem.

    Znacznik naiwny jest odrzucany. v1.1 §7 dopuszcza „RFC3339 canonical instant/local
    form **wg period/time contract**", a kontraktu okresu i czasu jeszcze nie ma — wybór
    formy lokalnej byłby wymyśleniem reguły, której kontrakt nie ustala.

    # ASSUMPTION: B-08 — kontrakt nie rozstrzyga, czy ten sam instant zapisany jako
    # ``…+00:00`` i ``…Z`` ma dać te same bajty, ani czy część ułamkowa sekundy jest
    # normalizowana. Zapisujemy to, co daje ``isoformat()`` dla danej wartości: jest
    # deterministyczne dla naszego kodu, ale dwie implementacje mogą się tu rozjechać.
    """
    if value.tzinfo is None or value.utcoffset() is None:
        raise UnsupportedType(
            "znacznik czasu bez strefy nie ma postaci kanonicznej w tym profilu; "
            "v1.1 §7 odsyła do period/time contract, którego jeszcze nie ma (B-08)"
        )
    return value.isoformat()


def _mapping(value: Mapping[Any, Any]) -> str:
    """Obiekt: klucze po NFC, unikalne, sortowane po bajtach UTF-8."""
    fragmenty: dict[str, str] = {}
    for klucz, wartosc in value.items():
        if not isinstance(klucz, str):
            raise UnsupportedType(
                f"klucz {klucz!r} nie jest łańcuchem; profil nie przewiduje konwersji kluczy"
            )
        znormalizowany = unicodedata.normalize("NFC", klucz)
        if znormalizowany == _TYPED_KEY:
            raise ReservedKey(
                f"klucz {_TYPED_KEY!r} jest zarezerwowany dla wartości typowanych "
                "(data, znacznik czasu) i nie może wystąpić w zwykłym odwzorowaniu"
            )
        if znormalizowany in fragmenty:
            raise DuplicateKey(
                f"klucz {znormalizowany!r} występuje dwa razy po normalizacji NFC; "
                "v1.1 §7 wymaga kluczy unikalnych"
            )
        fragmenty[znormalizowany] = _fragment(wartosc)
    pary = sorted(fragmenty.items(), key=lambda para: para[0].encode("utf-8"))
    return "{" + ",".join(f"{_string(klucz)}:{tresc}" for klucz, tresc in pary) + "}"


def _sequence(value: Iterable[Any]) -> str:
    """Sekwencja: kolejność zachowana dokładnie."""
    return "[" + ",".join(_fragment(element) for element in value) + "]"


def _set(value: CanonicalSet) -> str:
    """Zbiór: elementy kanonizowane osobno, sortowane bajtowo, duplikat odrzucany."""
    fragmenty = [_fragment(element) for element in value.elements]
    widziane: set[str] = set()
    for fragment in fragmenty:
        if fragment in widziane:
            raise DuplicateSetMember(
                f"element {fragment} występuje w zbiorze dwa razy; jeżeli krotność ma "
                "znaczenie, pole jest multisetem (XR_CANONICAL_MULTISET_V1, V12-R2), a nie zbiorem"
            )
        widziane.add(fragment)
    return "[" + ",".join(sorted(fragmenty, key=lambda fragment: fragment.encode("utf-8"))) + "]"


def _fragment(value: Any) -> str:
    """Kanoniczny zapis pojedynczej wartości.

    Kolejność sprawdzeń nie jest przypadkowa: ``bool`` jest podklasą ``int``, a
    ``datetime`` podklasą ``date`` — odwrotna kolejność zamieniłaby prawdę w ``1``,
    a znacznik czasu w datę.
    """
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return _integer(value)
    if isinstance(value, Decimal):
        return _decimal(value)
    if isinstance(value, float):
        raise UnsupportedType(
            f"wartość {value!r} jest typu float; profil wymaga postaci plain-decimal, "
            "której z liczby binarnej nie da się zagwarantować — użyj int albo Decimal"
        )
    if isinstance(value, str):
        return _string(value)
    if isinstance(value, dt.datetime):
        return _typed("datetime", _rfc3339(value))
    if isinstance(value, dt.date):
        return _typed("date", value.isoformat())
    if isinstance(value, CanonicalSet):
        return _set(value)
    if isinstance(value, Mapping):
        return _mapping(value)
    if isinstance(value, (set, frozenset)):
        raise UnsupportedType(
            "zbiór Pythona nie niesie informacji, czy kontrakt pola nadaje mu semantykę "
            "zbioru; zadeklaruj ją przez CanonicalSet albo przekaż sekwencję"
        )
    if isinstance(value, (list, tuple)):
        return _sequence(value)
    raise UnsupportedType(
        f"wartość typu {type(value).__name__} nie ma reprezentacji w profilu {PROFILE}"
    )


def canonical_text(value: Any) -> str:
    """Kanoniczny tekst JSON.

    Publiczny celowo, tak jak ``canonical_form``: przy audycie ogląda się postać, a nie
    skrót. Bajtami kontraktu jest jednak ``canonical_bytes`` — to z nich liczy się SHA-256.
    """
    return _fragment(value)


def canonical_bytes(value: Any) -> bytes:
    """Kanoniczne bajty: UTF-8 bez BOM.

    Brak BOM wynika z samego kodowania — ``str.encode("utf-8")`` nigdy go nie dopisuje.
    """
    return canonical_text(value).encode("utf-8")


def digest(value: Any) -> str:
    """SHA-256 z dokładnych bajtów kanonicznych: 64 znaki lowercase hex."""
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def identity(prefix: str, value: Any) -> str:
    """Identyfikator ``PREFIX-<skrót>``.

    Prefiks jest **poza** skrótem — tak samo jak w formułach kontraktu
    (``scope_id = "SCOPE-" + SHA256(canonical(scope_definition))``) i tak samo jak
    w istniejącym ``compute_id``. Dlatego musi pochodzić z zamkniętego rejestru: nic
    innego nie wykryłoby tu literówki.
    """
    if prefix not in PREFIXES:
        raise UnknownPrefix(
            f"prefiks {prefix!r} nie należy do rejestru profilu; dozwolone: "
            + ", ".join(sorted(PREFIXES))
        )
    return f"{prefix}-{digest(value)}"
