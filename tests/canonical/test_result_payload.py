# Testy techniczne koperty ładunku wyniku (karta V12-R1 §8, BIND-01 v1.2 §7.4.1).
"""Techniczne testy regresyjne. Wektory C-T17, C-T20 i C-T21 leżą w ``tests/acceptance/``."""

import datetime as dt
import re
from decimal import Decimal

import pytest

from xray.canonical import (
    ENVELOPE_KEYS,
    RESULT_PAYLOAD_PROFILE,
    CanonicalSet,
    ResultPayloadEnvelopeV1,
    ResultPayloadError,
    UnsupportedType,
    artifact_sha256,
    canonical_text,
    result_payload_digest,
)

SCHEMAT = "ZOP-TECH-01/FINDINGS/v0.1"


def koperta(payload=None, wersja: str = SCHEMAT) -> ResultPayloadEnvelopeV1:
    if payload is None:
        payload = {"status": "ADVERSE_SIGNAL", "metric_value": Decimal("1250.50")}
    return ResultPayloadEnvelopeV1(result_payload_schema_version=wersja, payload=payload)


# --- kształt koperty --------------------------------------------------------


def test_koperta_ma_dokladnie_trzy_klucze():
    """Karta §8: „Envelope ma dokładnie trzy obowiązkowe klucze"."""
    assert set(koperta().envelope()) == ENVELOPE_KEYS
    assert len(ENVELOPE_KEYS) == 3


def test_profil_kanoniczny_jest_wewnatrz_koperty():
    assert koperta().envelope()["canonical_profile"] == RESULT_PAYLOAD_PROFILE
    assert RESULT_PAYLOAD_PROFILE == "XR_RESULT_PAYLOAD_CANONICAL_V1"


def test_wersja_schematu_jest_wewnatrz_hashowanej_koperty():
    """Cały sens korekty C-07: wersja wchodzi do skrótu, a nie leży obok niego."""
    assert "result_payload_schema_version" in canonical_text(koperta().envelope())


def test_pusta_wersja_schematu_odrzucona():
    with pytest.raises(ResultPayloadError):
        koperta(wersja="   ")


def test_wersja_schematu_musi_byc_lancuchem():
    with pytest.raises(ResultPayloadError):
        koperta(wersja=1)


# --- skrót ------------------------------------------------------------------


def test_skrot_ma_64_znaki_lowercase_hex_bez_prefiksu():
    assert re.fullmatch(r"[0-9a-f]{64}", result_payload_digest(koperta()))


def test_ta_sama_tresc_daje_ten_sam_skrot():
    assert result_payload_digest(koperta()) == result_payload_digest(koperta())


def test_inna_tresc_daje_inny_skrot():
    assert result_payload_digest(koperta()) != result_payload_digest(
        koperta({"status": "NO_ADVERSE_SIGNAL", "metric_value": Decimal("1250.50")})
    )


def test_skrot_liczy_sie_przez_profil_z_p1():
    """Nie ma drugiego serializatora: bajty koperty to bajty profilu."""
    from xray.canonical import canonical_bytes

    assert koperta().canonical_bytes() == canonical_bytes(koperta().envelope())


# --- typy w ładunku ---------------------------------------------------------


def test_float_w_ladunku_odrzucony():
    """Koperta dziedziczy odmowę z profilu — konwersji tu nie ma (wpis B-11)."""
    with pytest.raises(UnsupportedType):
        result_payload_digest(koperta({"metric_value": 1250.5}))


def test_liczba_dziesietna_przechodzi():
    assert result_payload_digest(koperta({"metric_value": Decimal("1250.50")})) == (
        result_payload_digest(koperta({"metric_value": Decimal("1250.5")}))
    )


def test_data_w_ladunku_zostaje_data():
    assert '"$type":"date"' in canonical_text(koperta({"okres": dt.date(2026, 3, 1)}).envelope())


def test_null_jest_poprawna_trescia():
    """Zasada 5: brak informacji to pełnoprawny wynik diagnostyczny."""
    assert result_payload_digest(koperta({"metric_value": None})) != result_payload_digest(
        koperta({"metric_value": Decimal(0)})
    )


# --- sekwencja i zbiór ------------------------------------------------------


def test_lista_pozostaje_sekwencja():
    """Semantyki zbioru się nie wnioskuje: kolejność ma znaczenie, dopóki schemat
    ładunku jawnie nie nada liście semantyki zbioru."""
    assert result_payload_digest(koperta({"kroki": ["a", "b"]})) != result_payload_digest(
        koperta({"kroki": ["b", "a"]})
    )


def test_zbior_dopiero_gdy_schemat_go_zadeklaruje():
    assert result_payload_digest(koperta({"kroki": CanonicalSet(["a", "b"])})) == (
        result_payload_digest(koperta({"kroki": CanonicalSet(["b", "a"])}))
    )


# --- artefakt fizyczny ------------------------------------------------------


def test_skrot_artefaktu_rowny_digestowi_gdy_artefakt_jest_postacia_kanoniczna():
    """Zbiegają się tylko wtedy, gdy zapisano dokładnie postać kanoniczną; każda inna
    serializacja tej samej treści rozjedzie je — to pokazuje wektor C-T17."""
    envelope = koperta()
    assert artifact_sha256(envelope.canonical_bytes()) == result_payload_digest(envelope)


def test_skrot_artefaktu_liczy_dokladne_bajty():
    assert artifact_sha256(b"{}") != artifact_sha256(b"{ }")
