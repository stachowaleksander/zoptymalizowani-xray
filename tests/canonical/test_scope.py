# Testy techniczne tożsamości zakresu (BIND-01 v1.0 §4 / §4.1, v1.1 §10 i §7.1).
"""Dwa zdania zamykające v1.0 §4.1 mają tu po własnym teście:

    same_semantics → same_scope_id
    different_filters_or_population_or_aggregation_or_scope_constraints → different_scope_id

Kontrakt zakresu pochodzi z v1.0 mocą rozstrzygnięcia Controllingu z 2026-09-23 (wpis
B-09). Techniczne testy regresyjne, nie scenariusze odbiorowe (karta V12-R1 §16).
"""

import re
from decimal import Decimal

import pytest

from xray.canonical import (
    CanonicalSet,
    DuplicateSetMember,
    ScopeContractError,
    ScopeDefinition,
    ScopeOperator,
    ScopePredicate,
    scope_id,
)

CALA_FIRMA = ScopeDefinition(scope_label="cała firma")


def jednostka(wartosc: str = "A", operator: ScopeOperator = ScopeOperator.EQ) -> ScopePredicate:
    return ScopePredicate(field="jednostka", operator=operator, value=wartosc)


# --- struktura predykatu (v1.0 §4.1 pkt 3) ----------------------------------


def test_predykat_ma_dokladnie_trzy_pola():
    assert set(ScopePredicate.__dataclass_fields__) == {"field", "operator", "value"}
    assert set(jednostka().payload()) == {"field", "operator", "value"}


def test_dziewiec_operatorow_z_kontraktu():
    """v1.0 §4.1 pkt 3 wymienia dokładnie te dziewięć — ani jednego więcej nie dopisujemy."""
    assert [o.value for o in ScopeOperator] == [
        "EQ",
        "NE",
        "IN",
        "NOT_IN",
        "LT",
        "LTE",
        "GT",
        "GTE",
        "RANGE",
    ]


def test_operator_spoza_dziewiatki_odrzucony():
    """Nie dlatego, że lista jest zamknięta („np."), tylko dlatego, że nic w zamrożonym
    źródle innego operatora nie ustanawia — wpis B-12."""
    with pytest.raises(ScopeContractError):
        ScopePredicate(field="jednostka", operator="LIKE", value="A%")


def test_pusty_field_odrzucony():
    with pytest.raises(ScopeContractError):
        ScopePredicate(field="  ", operator=ScopeOperator.EQ, value="A")


def test_filtr_spoza_kontraktu_predykatu_odrzucony():
    """Surowe odwzorowanie nie jest kanonicznym predykatem."""
    with pytest.raises(ScopeContractError):
        ScopeDefinition(filters=[{"jednostka": "A"}])


def test_ten_sam_operator_inne_pole_to_inny_zakres():
    assert scope_id(ScopeDefinition(filters=[jednostka()])) != scope_id(
        ScopeDefinition(filters=[ScopePredicate("produkt", ScopeOperator.EQ, "A")])
    )


def test_to_samo_pole_i_wartosc_inny_operator_to_inny_zakres():
    """EQ i NE na tej samej wartości opisują rozłączne zakresy."""
    assert scope_id(ScopeDefinition(filters=[jednostka(operator=ScopeOperator.EQ)])) != (
        scope_id(ScopeDefinition(filters=[jednostka(operator=ScopeOperator.NE)]))
    )


def test_wartosci_zachowuja_typ():
    """v1.0 §4.1 pkt 5: „liczba, data, tekst i null nie są zamienne"."""
    liczba = ScopeDefinition(filters=[ScopePredicate("próg", ScopeOperator.GT, Decimal("10"))])
    tekst = ScopeDefinition(filters=[ScopePredicate("próg", ScopeOperator.GT, "10")])
    assert scope_id(liczba) != scope_id(tekst)


def test_operator_bez_wartosci_jest_dopuszczalny():
    """``value`` domyślnie ``None``; canonical null to poprawna wartość, nie brak pola."""
    assert "value" in ScopePredicate("aktywny", ScopeOperator.EQ).payload()


# --- dwa zdania z §4.1 ------------------------------------------------------


def test_inna_etykieta_ta_sama_semantyka_ten_sam_skrot():
    """different_label + same_semantics → same_scope_id (v1.1 §10)."""
    jeden = ScopeDefinition(filters=[jednostka()], aggregation_level="UNIT", scope_label="Dział A")
    drugi = ScopeDefinition(
        filters=[jednostka()], aggregation_level="UNIT", scope_label="oddział przy Kwiatowej"
    )
    assert scope_id(jeden) == scope_id(drugi)


def test_ta_sama_etykieta_inna_semantyka_inny_skrot():
    jeden = ScopeDefinition(filters=[jednostka("A")], scope_label="Dział A")
    drugi = ScopeDefinition(filters=[jednostka("B")], scope_label="Dział A")
    assert scope_id(jeden) != scope_id(drugi)


def test_etykieta_nie_wchodzi_do_ladunku():
    assert "scope_label" not in CALA_FIRMA.payload()


# --- równoważności strukturalne, i tylko one --------------------------------


def test_kolejnosc_predykatow_nie_ma_znaczenia():
    """v1.0 §4: „Kolejność predykatów jest nieistotna i po normalizacji sortowana"."""
    produkt = ScopePredicate("produkt", ScopeOperator.IN, CanonicalSet(["P1", "P2"]))
    jeden = ScopeDefinition(filters=[jednostka(), produkt])
    drugi = ScopeDefinition(filters=[produkt, jednostka()])
    assert scope_id(jeden) == scope_id(drugi)


def test_kolejnosc_populacji_nie_ma_znaczenia():
    assert scope_id(ScopeDefinition(population=["A", "B"])) == scope_id(
        ScopeDefinition(population=["B", "A"])
    )


def test_kolejnosc_wymiarow_agregacji_nie_ma_znaczenia():
    """v1.0 §4: „Dla zestawu wymiarów kolejność nie jest identity-defining"."""
    assert scope_id(ScopeDefinition(aggregation_level=["UNIT", "PRODUCT"])) == scope_id(
        ScopeDefinition(aggregation_level=["PRODUCT", "UNIT"])
    )


def test_pojedynczy_poziom_agregacji_to_nie_zestaw_jednoelementowy():
    assert scope_id(ScopeDefinition(aggregation_level="UNIT")) != scope_id(
        ScopeDefinition(aggregation_level=["UNIT"])
    )


def test_kolejnosc_ograniczen_nie_ma_znaczenia():
    assert scope_id(ScopeDefinition(constraints=["bez korekt", "bez kosztów wspólnych"])) == (
        scope_id(ScopeDefinition(constraints=["bez kosztów wspólnych", "bez korekt"]))
    )


def test_nfc_jest_normalizowane():
    zlozone = ScopeDefinition(filters=[ScopePredicate("dział", ScopeOperator.EQ, "ą")])
    rozlozone = ScopeDefinition(filters=[ScopePredicate("dział", ScopeOperator.EQ, "ą")])
    assert scope_id(zlozone) == scope_id(rozlozone)


def test_wielkosc_liter_nie_jest_zwijana():
    """v1.0 §4.1 pkt 1: „bez automatycznego case-folding, trim lub aliasing"."""
    assert scope_id(ScopeDefinition(filters=[jednostka("Dział A")])) != scope_id(
        ScopeDefinition(filters=[jednostka("dział a")])
    )


def test_biale_znaki_nie_sa_przycinane():
    assert scope_id(ScopeDefinition(filters=[jednostka(" A ")])) != scope_id(
        ScopeDefinition(filters=[jednostka("A")])
    )


def test_duplikat_predykatu_odrzucony():
    with pytest.raises(DuplicateSetMember):
        scope_id(ScopeDefinition(filters=[jednostka(), jednostka()]))


def test_kolekcja_w_operatorze_in_moze_byc_zadeklarowana_jako_zbior():
    """Kontrakt tego nie przesądza (B-12), więc deklaruje wołający — i wtedy działa."""
    jeden = ScopePredicate("produkt", ScopeOperator.IN, CanonicalSet(["P1", "P2"]))
    drugi = ScopePredicate("produkt", ScopeOperator.IN, CanonicalSet(["P2", "P1"]))
    assert scope_id(ScopeDefinition(filters=[jeden])) == scope_id(ScopeDefinition(filters=[drugi]))


def test_gola_lista_w_operatorze_in_jest_odrzucana():
    """Milcząca sekwencja dawałaby cicho niewłaściwy scope_id: ``IN [A,B]`` i ``IN [B,A]``
    to ten sam zakres semantyczny, a kontrakt nie rozstrzyga tego sam (B-12)."""
    with pytest.raises(ScopeContractError):
        ScopePredicate("produkt", ScopeOperator.IN, ["P1", "P2"])
    with pytest.raises(ScopeContractError):
        ScopePredicate("produkt", ScopeOperator.NOT_IN, ("P1", "P2"))


def test_lista_przy_innym_operatorze_przechodzi():
    """Odmowa dotyczy tylko IN i NOT_IN — przy RANGE kontrakt nie sugeruje zbioru."""
    ScopePredicate("okres", ScopeOperator.RANGE, ["2026-01", "2026-03"])


# --- każdy składnik rozróżnia -----------------------------------------------


def test_populacja_rozroznia():
    assert scope_id(ScopeDefinition(population=["A"])) != scope_id(CALA_FIRMA)


def test_poziom_agregacji_rozroznia():
    assert scope_id(ScopeDefinition(aggregation_level="UNIT")) != scope_id(
        ScopeDefinition(aggregation_level="PRODUCT")
    )


def test_ograniczenia_rozrozniaja():
    assert scope_id(ScopeDefinition(constraints=["bez korekt"])) != scope_id(CALA_FIRMA)


def test_rozszerzenia_kontraktowe_rozrozniaja():
    assert scope_id(ScopeDefinition(contract_scope_extensions={"payer": "NFZ"})) != scope_id(
        CALA_FIRMA
    )


def test_ten_sam_element_w_roznych_skladnikach_to_rozne_zakresy():
    assert scope_id(ScopeDefinition(population=["A"])) != scope_id(
        ScopeDefinition(constraints=["A"])
    )


# --- postać identyfikatora --------------------------------------------------


def test_postac_identyfikatora():
    """v1.0 §4: „SHA-256 lowercase hex" i „»SCOPE-« + scope_definition_hash"."""
    assert re.fullmatch(r"SCOPE-[0-9a-f]{64}", scope_id(CALA_FIRMA))


def test_zakres_pusty_jest_legalny_i_stabilny():
    assert scope_id(ScopeDefinition()) == scope_id(ScopeDefinition(scope_label="cokolwiek"))


def test_ladunek_ma_piec_skladnikow_z_kontraktu():
    assert set(CALA_FIRMA.payload()) == {
        "aggregation_level",
        "constraints",
        "contract_scope_extensions",
        "filters",
        "population",
    }
