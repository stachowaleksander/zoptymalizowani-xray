# Implementuje ZOP-XR-FOUNDATION-BIND-01 v1.1 §12 REFERENCE IDENTITY I PROVENANCE
# (decision_id = FB11-D08) oraz §7.1 (formuła reference_id = "REF-" + SHA256(canonical({...}))).
"""Tożsamość referencji — logiczna, nie fizyczna.

v1.1 §12 otwiera zdaniem, które wyznacza całą granicę: „Reference identity jest logiczna.
Physical source bytes pozostają provenance. `reference_value` **domyślnie nie jest częścią
reference_id**".

Do tożsamości wchodzi pięć pól warstwy semantycznej (v1.1 §12, wiersz „Semantic
reference"): `reference_type`, `reference_period`, `reference_scope_id`,
`reference_source_logical_id`/null, `reference_semantic_extensions`. Wszystko pozostałe —
wartość referencji, identyfikator artefaktu, SHA-256 pliku, ścieżka, znacznik pobrania —
jest pochodzeniem i leży poza tym obiektem. Dlatego klasa **nie ma** pola na wartość:
próba jej podania kończy się błędem konstruktora, a nie cichym zignorowaniem.

Dwa skutki, które v1.1 §12 wymienia wprost:

- „same logical reference + corrected bytes → same reference_id; new immutable
  execution/result record + new SHA/value provenance" — poprawiony plik nie zmienia
  tożsamości referencji, tylko dokłada nowy ślad wykonania,
- „different reference_type/period/scope/logical source/semantic extension → different
  reference_id" — każde z pięciu pól semantycznych rozróżnia.

Gdy referencji nie ma: „reference_applicable=false | reference_id = canonical null;
technical execution record zachowuje basis tej nieaplikowalności". Stąd ``reference_id``
zwraca ``None``, a nie skrót z pustego obiektu — brak referencji to brak wartości, a nie
referencja pusta.

Ten moduł nie zastępuje ``ReferenceRef`` z ``model/findings/refs.py``: tamten niesie także
``reference_value``, ``reference_quality`` i ``reference_source`` z FIN-01 pkt 6.1, czyli
warstwę pochodzenia, i nie wchodzi dziś do żadnej tożsamości.
"""

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from xray.canonical.identity_json import identity
from xray.canonical.period import CanonicalPeriod, period_payload

_PREFIX = "REF"
_SCOPE_PREFIX = "SCOPE-"


class ReferenceContractError(ValueError):
    """Referencja nie spełnia kontraktu v1.1 §12."""


@dataclass(frozen=True, slots=True)
class ReferenceDefinition:
    """Semantyczna warstwa referencji — pięć pól z v1.1 §12."""

    reference_type: str
    """Rodzaj referencji, tokenem z zamrożonej karty testu."""

    reference_period: CanonicalPeriod | None = None
    """Okres referencyjny. Osobne pole semantyczne od ``analysis_period`` (v1.1 §11)."""

    reference_scope_id: str | None = None
    """Tożsamość zakresu referencji — gotowy ``scope_id``, nie sama definicja zakresu.

    Kontrakt wymienia tu `reference_scope_id`, czyli identyfikator. Zakres liczy się raz
    i wchodzi do referencji jako wartość, dzięki czemu dwie referencje o tym samym
    zakresie nie mogą się rozjechać przez różnicę w budowie definicji.
    """

    reference_source_logical_id: str | None = None
    """Logiczny identyfikator źródła referencji albo canonical null."""

    semantic_extensions: Mapping[str, Any] = field(default_factory=dict)
    """`reference_semantic_extensions` — wyłącznie jawne pola z zamrożonej karty."""

    def __post_init__(self) -> None:
        if self.reference_scope_id is not None and not self.reference_scope_id.startswith(
            _SCOPE_PREFIX
        ):
            raise ReferenceContractError(
                f"reference_scope_id {self.reference_scope_id!r} nie wygląda na scope_id; "
                f"oczekiwany prefiks {_SCOPE_PREFIX!r} (v1.1 §7.1)"
            )

    def payload(self) -> dict[str, Any]:
        """Ładunek kanoniczny referencji — wyłącznie warstwa semantyczna."""
        return {
            "reference_period": period_payload(self.reference_period),
            "reference_scope_id": self.reference_scope_id,
            "reference_semantic_extensions": dict(self.semantic_extensions),
            "reference_source_logical_id": self.reference_source_logical_id,
            "reference_type": self.reference_type,
        }


def reference_id(reference: ReferenceDefinition | None) -> str | None:
    """``"REF-" + SHA256(canonical({...}))`` albo ``None``, gdy referencja nie dotyczy.

    ``None`` na wejściu to `reference_applicable = false` z v1.1 §12 — wynik jest wtedy
    canonical null. Podstawę nieaplikowalności zapisuje rekord wykonania, nie ten moduł.
    """
    if reference is None:
        return None
    return identity(_PREFIX, reference.payload())
