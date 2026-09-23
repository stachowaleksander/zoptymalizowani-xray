# Testy techniczne tożsamości referencji (BIND-01 v1.1 §12 i §7.1).
"""Wiersz z v1.1 §12 „different reference_type/period/scope/logical source/semantic
extension → different reference_id" ma tu po teście na każde z pięciu pól.

Techniczne testy regresyjne, nie scenariusze odbiorowe (karta V12-R1 §16).
"""

import datetime as dt
import re

import pytest

from xray.canonical import (
    CanonicalPeriod,
    ReferenceContractError,
    ReferenceDefinition,
    ScopeDefinition,
    reference_id,
    scope_id,
)

MARZEC = CanonicalPeriod(
    start_inclusive=dt.date(2026, 3, 1),
    end_exclusive=dt.date(2026, 4, 1),
)
ZAKRES = scope_id(ScopeDefinition(population=["A"]))

PLAN = ReferenceDefinition(
    reference_type="PLAN",
    reference_period=MARZEC,
    reference_scope_id=ZAKRES,
    reference_source_logical_id="plan-2026",
)


# --- postać i brak referencji -----------------------------------------------


def test_postac_identyfikatora():
    assert re.fullmatch(r"REF-[0-9a-f]{64}", reference_id(PLAN))


def test_brak_referencji_to_canonical_null():
    """v1.1 §12: „reference_applicable=false | reference_id = canonical null"."""
    assert reference_id(None) is None


def test_ta_sama_referencja_daje_ten_sam_skrot():
    bliznjaczy = ReferenceDefinition(
        reference_type="PLAN",
        reference_period=CanonicalPeriod(
            start_inclusive=dt.date(2026, 3, 1),
            end_exclusive=dt.date(2026, 4, 1),
        ),
        reference_scope_id=ZAKRES,
        reference_source_logical_id="plan-2026",
    )
    assert reference_id(PLAN) == reference_id(bliznjaczy)


# --- pięć pól semantycznych rozróżnia ---------------------------------------


def test_inny_rodzaj_referencji_rozroznia():
    inny = ReferenceDefinition(
        reference_type="PEER",
        reference_period=MARZEC,
        reference_scope_id=ZAKRES,
        reference_source_logical_id="plan-2026",
    )
    assert reference_id(inny) != reference_id(PLAN)


def test_inny_okres_referencyjny_rozroznia():
    inny = ReferenceDefinition(
        reference_type="PLAN",
        reference_period=CanonicalPeriod(
            start_inclusive=dt.date(2026, 4, 1),
            end_exclusive=dt.date(2026, 5, 1),
        ),
        reference_scope_id=ZAKRES,
        reference_source_logical_id="plan-2026",
    )
    assert reference_id(inny) != reference_id(PLAN)


def test_inny_zakres_referencji_rozroznia():
    inny = ReferenceDefinition(
        reference_type="PLAN",
        reference_period=MARZEC,
        reference_scope_id=scope_id(ScopeDefinition(population=["B"])),
        reference_source_logical_id="plan-2026",
    )
    assert reference_id(inny) != reference_id(PLAN)


def test_inne_zrodlo_logiczne_rozroznia():
    inny = ReferenceDefinition(
        reference_type="PLAN",
        reference_period=MARZEC,
        reference_scope_id=ZAKRES,
        reference_source_logical_id="plan-2025",
    )
    assert reference_id(inny) != reference_id(PLAN)


def test_inne_rozszerzenie_semantyczne_rozroznia():
    inny = ReferenceDefinition(
        reference_type="PLAN",
        reference_period=MARZEC,
        reference_scope_id=ZAKRES,
        reference_source_logical_id="plan-2026",
        semantic_extensions={"wariant": "po korekcie"},
    )
    assert reference_id(inny) != reference_id(PLAN)


def test_brak_zrodla_logicznego_rozroznia_od_zrodla():
    bez_zrodla = ReferenceDefinition(
        reference_type="PLAN",
        reference_period=MARZEC,
        reference_scope_id=ZAKRES,
    )
    assert reference_id(bez_zrodla) != reference_id(PLAN)


def test_brak_okresu_rozroznia_od_okresu():
    bez_okresu = ReferenceDefinition(
        reference_type="PLAN",
        reference_scope_id=ZAKRES,
        reference_source_logical_id="plan-2026",
    )
    assert reference_id(bez_okresu) != reference_id(PLAN)


# --- granica semantyka / pochodzenie ----------------------------------------


def test_wartosc_referencji_nie_jest_polem_tozsamosci():
    """v1.1 §12: „reference_value domyślnie nie jest częścią reference_id".

    Klasa nie ma takiego pola, więc próba podania go kończy się błędem — a nie cichym
    zignorowaniem, po którym wołający myślałby, że wartość weszła do skrótu.
    """
    with pytest.raises(TypeError):
        ReferenceDefinition(reference_type="PLAN", reference_value=1000.0)


def test_poprawione_bajty_nie_zmieniaja_tozsamosci():
    """v1.1 §12: „same logical reference + corrected bytes → same reference_id".

    Skoro pochodzenia fizycznego nie da się tu w ogóle podać, poprawka pliku nie ma jak
    zmienić skrótu. Ten test pilnuje, żeby ktoś kiedyś nie dołożył takiego pola.
    """
    pola = set(ReferenceDefinition.__dataclass_fields__)
    assert pola == {
        "reference_type",
        "reference_period",
        "reference_scope_id",
        "reference_source_logical_id",
        "semantic_extensions",
    }


def test_zakres_referencji_musi_byc_identyfikatorem_zakresu():
    with pytest.raises(ReferenceContractError):
        ReferenceDefinition(reference_type="PLAN", reference_scope_id="cała firma")
