# Implementuje ZOP-XR-V12-R1 kartę wykonawczą §8 (XR_RESULT_PAYLOAD_CANONICAL_V1
# i ResultPayloadEnvelopeV1) oraz ZOP-XR-FOUNDATION-BIND-01 v1.2 §7.4.1 (korekta C-07).
"""Koperta ładunku wyniku i jego skrót semantyczny.

    ResultPayloadEnvelopeV1 = {"canonical_profile": "XR_RESULT_PAYLOAD_CANONICAL_V1",
                               "result_payload_schema_version": "<wersja>",
                               "payload": <typowana treść>}

    result_payload_digest = SHA256(XR_RESULT_PAYLOAD_CANONICAL_V1(ResultPayloadEnvelopeV1))

## Po co koperta, skoro payload i tak się kanonizuje

To jest sedno korekty C-07. Wersja schematu ładunku siedzi **wewnątrz** hashowanej koperty,
a nie obok niej jako osobne pole rekordu. Skutek nazywa v1.2 §7.4.1 wprost: „ten sam typed
payload content pod `result_payload_schema_version=A` oraz `result_payload_schema_version=B`
tworzy różne ResultPayloadEnvelopeV1 i różne `result_payload_digest`, **nawet gdy wartości
payload są identyczne**". Bez koperty ta sama liczba pod dwoma różnymi znaczeniami dałaby
jeden skrót — i nikt by się nie dowiedział, że porównał jabłka z gruszkami.

Karta §8: koperta ma **dokładnie trzy** obowiązkowe klucze, a
`RESULT_PAYLOAD_SCHEMA_VERSION_HASHED = true`.

## Serializator jest jeden

`XR_RESULT_PAYLOAD_CANONICAL_V1` nie jest osobnym serializatorem. Karta §8: „używa bez
zmiany primitive/type serialization rules zamrożonego XR_IDENTITY_CANONICAL_JSON_V1. Nie
twórz drugiego canonical JSON serializer ani lokalnego wariantu". Ten moduł tylko buduje
kopertę i woła profil z ``identity_json``; własnej kanonizacji nie ma ani jednej linijki.

Stąd też: `RESULT_PAYLOAD_DIGEST_USES_RAW_SERIALIZED_BYTES = false` i
`RESULT_PAYLOAD_SERIALIZATION_INDEPENDENT = true` (karta §8) — dwie fizycznie różne
serializacje tej samej treści dają ten sam skrót, bo liczy się postać kanoniczna, nie bajty
pliku.

## Artefakt fizyczny to osobna warstwa

`result_payload_artifact_SHA256` jest proweniencją: „Może różnić się dla dwóch semantycznie
równoważnych serializacji i nie wpływa na result_payload_digest ani result_identity"
(karta §8). Funkcja ``artifact_sha256`` jest tu wyłącznie po to, żeby tę granicę dało się
pokazać — nie jest częścią żadnej tożsamości.

## Sekwencja, zbiór, multiset

Nic nie jest wnioskowane. Lista pozostaje **sekwencją**, dopóki schemat ładunku jawnie nie
nada jej semantyki zbioru (v1.1 §7) — wtedy wołający opakowuje ją w ``CanonicalSet``.
Krotności profil nie zna: gdyby schemat zażądał multisetu, właściwą odpowiedzią jest STOP,
bo `XR_CANONICAL_MULTISET_V1` należy do V12-R2 (karta §8 i §13).

## Czego ta koperta nie przyjmie

Wartości ``float`` — odmawia ich profil z P1, bo z liczby binarnej nie da się zagwarantować
postaci „plain-decimal bez zbędnych zer końcowych". Dzisiejsza treść diagnostyczna
(``metric_value``, ``gap``, ``impact_low``, ``impact_high`` w ``model/findings/finding.py``)
jest właśnie ``float | None``, więc **wpuszczenie jej do koperty wymaga wcześniejszego
rozstrzygnięcia wpisu B-11** (sposób przejścia z liczby binarnej na kanoniczną dziesiętną).
To nie jest ``RESULT_PAYLOAD_CANONICAL_TYPE_GAP``: profil ma typ dziesiętny, a v1.2 §7.4.1
ustala `RESULT_PAYLOAD_CANONICAL_TYPE_GAP = false`. Brakuje wiązania, nie typu — i dlatego
koperta niczego tu po cichu nie konwertuje.
"""

import hashlib
from dataclasses import dataclass
from typing import Any

from xray.canonical.identity_json import canonical_bytes, digest

RESULT_PAYLOAD_PROFILE = "XR_RESULT_PAYLOAD_CANONICAL_V1"
"""Wartość pola ``canonical_profile`` — karta §8."""

ENVELOPE_KEYS: frozenset[str] = frozenset(
    {"canonical_profile", "result_payload_schema_version", "payload"}
)
"""Zamknięty zestaw trzech kluczy koperty. Służy też za asercję w testach."""


class ResultPayloadError(ValueError):
    """Koperta nie spełnia kontraktu karty §8."""


@dataclass(frozen=True, slots=True)
class ResultPayloadEnvelopeV1:
    """Koperta ładunku wyniku.

    ``payload`` jest typowaną treścią semantyczną — tym, co dany schemat uznaje za wynik.
    Koperta nie zagląda w jego strukturę i nie nadaje jej znaczenia; pilnuje tylko, żeby
    wersja schematu była obecna i żeby cała trójka weszła do skrótu razem.
    """

    result_payload_schema_version: str
    payload: Any

    def __post_init__(self) -> None:
        if not isinstance(self.result_payload_schema_version, str):
            raise ResultPayloadError(
                "result_payload_schema_version musi być łańcuchem — to wersja semantyczna "
                "schematu ładunku (karta §8: RESULT_PAYLOAD_SCHEMA_VERSION_IS_SEMANTIC)"
            )
        if not self.result_payload_schema_version.strip():
            raise ResultPayloadError(
                "result_payload_schema_version nie może być pusty; bez niego dwa różne "
                "znaczenia tej samej wartości dałyby jeden skrót"
            )

    def envelope(self) -> dict[str, Any]:
        """Koperta jako odwzorowanie — dokładnie trzy klucze."""
        return {
            "canonical_profile": RESULT_PAYLOAD_PROFILE,
            "payload": self.payload,
            "result_payload_schema_version": self.result_payload_schema_version,
        }

    def canonical_bytes(self) -> bytes:
        """Kanoniczne bajty koperty — przez profil z P1, bez lokalnego wariantu."""
        return canonical_bytes(self.envelope())


def result_payload_digest(envelope: ResultPayloadEnvelopeV1) -> str:
    """``SHA256(XR_RESULT_PAYLOAD_CANONICAL_V1(ResultPayloadEnvelopeV1))``.

    Bez prefiksu: karta §8 podaje sam skrót, lowercase hex. Prefiksy z rejestru profilu
    należą do identyfikatorów (``SCOPE-``, ``RESULT-``, …), a to jest skrót treści.
    """
    return digest(envelope.envelope())


def artifact_sha256(data: bytes) -> str:
    """``result_payload_artifact_SHA256`` — skrót **dokładnych bajtów fizycznych**.

    Proweniencja, nie semantyka. Karta §8:
    ``RESULT_PAYLOAD_ARTIFACT_SHA_AFFECTS_RESULT_PAYLOAD_DIGEST = false`` oraz
    ``RESULT_PAYLOAD_ARTIFACT_SHA_AFFECTS_RESULT_IDENTITY = false``. Dwie różne
    serializacje tej samej treści mają różny skrót artefaktu i **ten sam** digest.
    """
    return hashlib.sha256(data).hexdigest()
