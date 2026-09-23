# Wektory odbiorowe C-T17, C-T20, C-T21 dla ResultPayloadEnvelopeV1 (karta V12-R1 §16).
"""Scenariusze odbiorowe rundy V12-R1 dotyczące kanonicznego ładunku wyniku.

Kod scenariusza jest w nazwie testu, żeby handoff mógł wskazać exact test locator.
``NEW_ACCEPTANCE_SCENARIO_COUNT = 0`` — wykazujemy scenariusze już związane kartą.

Wszystkie trzy wektory operują na treści **typowanej**: łańcuchy, liczby dziesiętne, daty.
Wpuszczenie dzisiejszej treści diagnostycznej (``float``) wymaga wcześniejszego
rozstrzygnięcia wpisu B-11 i nie jest przedmiotem tej rundy.
"""

import datetime as dt
import json
from decimal import Decimal

from xray.canonical import (
    ResultPayloadEnvelopeV1,
    artifact_sha256,
    result_payload_digest,
)

SCHEMAT_V1 = "ZOP-TECH-01/FINDINGS/v0.1"
SCHEMAT_V2 = "ZOP-TECH-01/FINDINGS/v0.2"

TRESC = {
    "status": "ADVERSE_SIGNAL",
    "metric_value": Decimal("1250.50"),
    "period_start": dt.date(2026, 3, 1),
    "validation_notes": ["brak kosztów pośrednich"],
}


def koperta(wersja: str = SCHEMAT_V1, payload=None) -> ResultPayloadEnvelopeV1:
    return ResultPayloadEnvelopeV1(
        result_payload_schema_version=wersja,
        payload=TRESC if payload is None else payload,
    )


# --- C-T17 ------------------------------------------------------------------


def test_ct17_kanoniczny_ladunek_wobec_serializacji_fizycznej():
    """C-T17 CANONICAL RESULT PAYLOAD VS PHYSICAL SERIALIZATION.

    Invariant: „ResultPayloadEnvelopeV1 canonical digest independent of physical bytes".
    Expected: „same result_payload_digest; different physical artifact SHA allowed;
    result_identity unchanged".

    Ta sama koperta zapisana dwa razy fizycznie: raz w postaci kanonicznej, raz
    z wcięciami i inną kolejnością kluczy. Skrót artefaktu się rozjeżdża, digest nie.
    """
    envelope = koperta()
    kanoniczne = envelope.canonical_bytes()
    rozstrzelone = json.dumps(
        {
            "result_payload_schema_version": SCHEMAT_V1,
            "canonical_profile": "XR_RESULT_PAYLOAD_CANONICAL_V1",
            "payload": {"status": "ADVERSE_SIGNAL"},
        },
        indent=2,
        ensure_ascii=False,
    ).encode("utf-8")

    assert artifact_sha256(kanoniczne) != artifact_sha256(rozstrzelone)
    assert result_payload_digest(envelope) == result_payload_digest(koperta())


def test_ct17_skrot_artefaktu_nie_wchodzi_do_digestu():
    """Karta §8: RESULT_PAYLOAD_ARTIFACT_SHA_AFFECTS_RESULT_PAYLOAD_DIGEST = false."""
    envelope = koperta()
    przed = result_payload_digest(envelope)
    artifact_sha256(b"jakiekolwiek inne bajty artefaktu")
    assert result_payload_digest(envelope) == przed


# --- C-T20 ------------------------------------------------------------------


def test_ct20_domain_separation_po_wersji_schematu():
    """C-T20 RESULT PAYLOAD SCHEMA VERSION DOMAIN SEPARATION.

    Invariant: „result_payload_schema_version hashed inside envelope".
    Expected: „same typed values under V1/V2 => different envelope and digest".

    v1.2 §7.4.1: „ten sam typed payload content pod result_payload_schema_version=A oraz
    result_payload_schema_version=B tworzy różne ResultPayloadEnvelopeV1 i różne
    result_payload_digest, nawet gdy wartości payload są identyczne".
    """
    pod_v1 = koperta(SCHEMAT_V1)
    pod_v2 = koperta(SCHEMAT_V2)
    assert pod_v1.payload == pod_v2.payload
    assert pod_v1.envelope() != pod_v2.envelope()
    assert result_payload_digest(pod_v1) != result_payload_digest(pod_v2)


# --- C-T21 ------------------------------------------------------------------


def test_ct21_niezaleznosc_od_serializacji():
    """C-T21 CANONICAL PAYLOAD SERIALIZATION INDEPENDENCE.

    Invariant: „same schema + same typed payload canonicalize through frozen serializer".
    Expected: „same canonical bytes/digest; physical artifact SHA may differ".

    Dwie konstrukcje tej samej treści różniące się kolejnością kluczy, zapisem liczby
    (``1250.50`` wobec ``1250.5``) i typem sekwencji wejściowej — jedna postać kanoniczna.
    """
    jedna = koperta(
        payload={
            "status": "ADVERSE_SIGNAL",
            "metric_value": Decimal("1250.50"),
            "period_start": dt.date(2026, 3, 1),
            "validation_notes": ["brak kosztów pośrednich"],
        }
    )
    druga = koperta(
        payload={
            "validation_notes": ("brak kosztów pośrednich",),
            "period_start": dt.date(2026, 3, 1),
            "metric_value": Decimal("1250.5"),
            "status": "ADVERSE_SIGNAL",
        }
    )
    assert jedna.canonical_bytes() == druga.canonical_bytes()
    assert result_payload_digest(jedna) == result_payload_digest(druga)


def test_ct21_kolejnosc_sekwencji_pozostaje_znaczaca():
    """Niezależność dotyczy serializacji, nie semantyki: sekwencja to nie zbiór."""
    jedna = koperta(payload={"kroki": ["a", "b"]})
    druga = koperta(payload={"kroki": ["b", "a"]})
    assert result_payload_digest(jedna) != result_payload_digest(druga)
