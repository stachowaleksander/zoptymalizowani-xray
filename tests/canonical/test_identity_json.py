# Testy techniczne profilu XR_IDENTITY_CANONICAL_JSON_V1 (BIND-01 v1.1 §7).
"""Każda reguła z tabeli profilu ma tu własny test.

To są **techniczne testy regresyjne**, a nie scenariusze odbiorowe: karta V12-R1 §16
ustala ``NEW_ACCEPTANCE_SCENARIO_COUNT = 0``. Scenariusze T50, T51 i C-T01–C-T23 powstaną
w swoich pakietach i będą wskazane w handoffie osobno.
"""

import datetime as dt
import re
from decimal import Decimal

import pytest

from xray.canonical import (
    PREFIXES,
    CanonicalizationError,
    CanonicalSet,
    DuplicateKey,
    DuplicateSetMember,
    ReservedKey,
    UnknownPrefix,
    UnsupportedType,
    canonical_bytes,
    canonical_text,
    digest,
    identity,
)

# --- 1. Unicode NFC ---------------------------------------------------------


def test_nfd_i_nfc_daja_te_same_bajty():
    """„ą" złożone i rozłożone to ta sama treść, więc ten sam skrót."""
    zlozone = "ą"  # ą
    rozlozone = "ą"  # a + ogonek
    assert zlozone != rozlozone
    assert canonical_bytes({"pole": zlozone}) == canonical_bytes({"pole": rozlozone})


def test_normalizacja_obejmuje_takze_klucze():
    zlozone = {"ząb": 1}
    rozlozone = {"ząb": 1}
    assert digest(zlozone) == digest(rozlozone)


def test_normalizacja_nie_zwija_wielkosci_liter():
    """NFC to nie case-folding: „ABC" i „abc" zostają różne."""
    assert digest({"pole": "ABC"}) != digest({"pole": "abc"})


def test_normalizacja_nie_przycina_bialych_znakow():
    assert digest({"pole": " x "}) != digest({"pole": "x"})


# --- 2. Typy semantyczne: data to nie łańcuch -------------------------------


def test_typowana_data_i_lancuch_o_tych_samych_znakach_daja_rozne_skroty():
    data = dt.date(2026, 9, 1)
    assert digest({"pole": data}) != digest({"pole": "2026-09-01"})


def test_data_ma_postac_typowana():
    assert canonical_text(dt.date(2026, 9, 1)) == '{"$type":"date","value":"2026-09-01"}'


def test_znacznik_czasu_ma_wlasny_typ():
    chwila = dt.datetime(2026, 9, 1, 12, 0, tzinfo=dt.UTC)
    assert canonical_text(chwila).startswith('{"$type":"datetime","value":')


def test_znacznik_bez_strefy_odrzucony():
    """Kontrakt odsyła do period/time contract, którego nie ma — patrz B-08."""
    with pytest.raises(UnsupportedType):
        canonical_text(dt.datetime(2026, 9, 1, 12, 0))


def test_prawda_to_nie_jedynka():
    assert canonical_text(True) == "true"
    assert digest({"pole": True}) != digest({"pole": 1})


def test_klucz_type_jest_zarezerwowany():
    """Bez tej reguły dałoby się podrobić typowaną datę zwykłym słownikiem."""
    with pytest.raises(ReservedKey):
        canonical_text({"$type": "date", "value": "2026-09-01"})


# --- 3. Zbiór a sekwencja ---------------------------------------------------


def test_permutacja_zbioru_nie_zmienia_skrotu():
    assert digest(CanonicalSet(["b", "a", "c"])) == digest(CanonicalSet(["c", "b", "a"]))


def test_permutacja_sekwencji_zmienia_skrot():
    assert digest(["b", "a", "c"]) != digest(["c", "b", "a"])


def test_zbior_i_sekwencja_o_tych_samych_elementach_to_nie_to_samo_wejscie():
    """Zbiór jest sortowany, więc zgadza się z sekwencją tylko wtedy, gdy ta już była
    posortowana — kolejność sekwencji ma znaczenie z samej definicji."""
    assert digest(CanonicalSet(["a", "b"])) == digest(["a", "b"])
    assert digest(CanonicalSet(["b", "a"])) != digest(["b", "a"])


def test_zbior_sortuje_bajtowo_a_nie_po_kolejnosci_wejscia():
    assert canonical_text(CanonicalSet(["z", "a"])) == '["a","z"]'


def test_zwykly_zbior_pythona_odrzucony():
    """Semantyki zbioru nie zgadujemy z typu — v1.1 §7 wymaga jawnego kontraktu pola."""
    with pytest.raises(UnsupportedType):
        canonical_text({"a", "b"})


# --- 4. Duplikat w zbiorze --------------------------------------------------


def test_duplikat_w_zbiorze_jest_odrzucany():
    """Cicha deduplikacja to defekt U-2: krotność ginęłaby bez śladu."""
    with pytest.raises(DuplicateSetMember):
        canonical_text(CanonicalSet(["a", "a"]))


def test_duplikatem_jest_rownosc_kanoniczna_a_nie_rownosc_pythona():
    """``7`` i ``Decimal("7.0")`` to różne obiekty i ta sama postać kanoniczna."""
    with pytest.raises(DuplicateSetMember):
        canonical_text(CanonicalSet([7, Decimal("7.0")]))


def test_duplikat_zagniezdzonego_odwzorowania_tez_odrzucony():
    with pytest.raises(DuplicateSetMember):
        canonical_text(CanonicalSet([{"a": 1, "b": 2}, {"b": 2, "a": 1}]))


# --- 5. null a pusty łańcuch ------------------------------------------------


def test_null_i_pusty_lancuch_to_rozne_wartosci():
    assert canonical_text(None) == "null"
    assert canonical_text("") == '""'
    assert digest({"pole": None}) != digest({"pole": ""})


def test_brak_klucza_to_nie_to_samo_co_klucz_z_nullem():
    assert digest({"a": 1}) != digest({"a": 1, "b": None})


# --- 6. Klucze obiektu ------------------------------------------------------


def test_kolejnosc_kluczy_wejsciowych_nie_zmienia_wyniku():
    assert canonical_text({"b": 1, "a": 2}) == canonical_text({"a": 2, "b": 1})
    assert canonical_text({"b": 1, "a": 2}) == '{"a":2,"b":1}'


def test_duplikat_klucza_po_normalizacji_odrzucony():
    """Dwa różne klucze Pythona, jeden klucz po NFC — scalenie zgubiłoby wartość."""
    with pytest.raises(DuplicateKey):
        canonical_text({"ząb": 1, "ząb": 2})


def test_klucz_nielancuchowy_odrzucony():
    with pytest.raises(UnsupportedType):
        canonical_text({1: "x"})


def test_bez_nieistotnych_bialych_znakow():
    assert canonical_text({"a": [1, 2], "b": {"c": 3}}) == '{"a":[1,2],"b":{"c":3}}'


# --- 7. Liczby: zero, NaN, Inf, float ---------------------------------------


def test_minus_zero_kanonizuje_sie_do_zera():
    assert canonical_text(Decimal("-0")) == "0"
    assert canonical_text(Decimal("-0.00")) == "0"
    assert digest(Decimal("-0")) == digest(0)


@pytest.mark.parametrize("wartosc", ["NaN", "Infinity", "-Infinity"])
def test_nan_i_nieskonczonosc_odrzucone(wartosc):
    with pytest.raises(CanonicalizationError):
        canonical_text(Decimal(wartosc))


def test_float_odrzucony():
    """Z liczby binarnej nie da się zagwarantować postaci plain-decimal."""
    with pytest.raises(UnsupportedType):
        canonical_text(0.1)


# --- 8. Postać liczby: zera wiodące i końcowe -------------------------------


def test_zera_wiodace_nie_zmieniaja_postaci_kanonicznej():
    """v1.1 §7: „base-10, bez +, bez leading zeros" opisuje postać **wyjściową**."""
    assert canonical_text(Decimal("007")) == "7"
    assert canonical_text(7) == "7"
    assert digest(Decimal("007")) == digest(7)


def test_lancuch_007_to_nie_liczba_siedem():
    """Konwersja tekstu na liczbę byłaby aliasowaniem, którego v1.1 §7 zakazuje."""
    assert digest("007") != digest(7)


def test_decimal_siedem_zero_i_integer_siedem_daja_te_same_bajty():
    """„number" jest jednym typem semantycznym: dwie równe liczby, jedna tożsamość."""
    assert canonical_bytes(Decimal("7.0")) == canonical_bytes(7)
    assert canonical_text(Decimal("7.000")) == "7"


def test_zera_koncowe_po_przecinku_nie_zmieniaja_postaci():
    assert canonical_text(Decimal("1.500")) == "1.5"
    assert canonical_text(Decimal("0.10")) == "0.1"


def test_brak_postaci_wykladniczej():
    assert canonical_text(Decimal("1E+2")) == "100"
    assert canonical_text(Decimal("1E-3")) == "0.001"
    assert digest(Decimal("1E+2")) == digest(100)


def test_dlugie_liczby_nie_sa_zaokraglane():
    """Kanonizacja nie przechodzi przez kontekst dziesiętny, więc 40 cyfr przeżywa."""
    dluga = "1." + "1" * 40
    assert canonical_text(Decimal(dluga)) == dluga


def test_liczba_ujemna_zachowuje_znak():
    assert canonical_text(Decimal("-12.50")) == "-12.5"
    assert canonical_text(-7) == "-7"


# --- 9. Skrót i prefiksy ----------------------------------------------------


def test_skrot_ma_64_znaki_lowercase_hex():
    assert re.fullmatch(r"[0-9a-f]{64}", digest({"pole": "wartość"}))


def test_identyfikator_sklada_sie_z_prefiksu_i_skrotu():
    wartosc = {"pole": 1}
    assert identity("SCOPE", wartosc) == "SCOPE-" + digest(wartosc)


def test_prefiks_nie_wchodzi_do_skrotu():
    wartosc = {"pole": 1}
    assert identity("SCOPE", wartosc)[6:] == identity("REF", wartosc)[4:]


def test_prefiks_spoza_rejestru_odrzucony():
    with pytest.raises(UnknownPrefix):
        identity("FND", {"pole": 1})


def test_rejestr_prefiksow_obejmuje_dziesiec_z_v1_1_i_dwa_z_v1_2():
    z_v1_1 = {
        "SCOPE",
        "REF",
        "RESULT",
        "REC",
        "SRCROW",
        "PARSE",
        "EXCL",
        "EXAPP",
        "RUN",
        "EXECFP",
    }
    z_v1_2 = {"RREC", "ECMP"}
    assert set(PREFIXES) == z_v1_1 | z_v1_2


def test_bajty_sa_utf8_bez_bom():
    bajty = canonical_bytes({"pole": "ą"})
    assert not bajty.startswith(b"\xef\xbb\xbf")
    assert bajty == '{"pole":"ą"}'.encode()


# --- Zamknięcie profilu -----------------------------------------------------


def test_typ_bez_reprezentacji_odrzucony():
    with pytest.raises(UnsupportedType):
        canonical_text({"pole": object()})


def test_bajty_odrzucone():
    with pytest.raises(UnsupportedType):
        canonical_text(b"abc")
