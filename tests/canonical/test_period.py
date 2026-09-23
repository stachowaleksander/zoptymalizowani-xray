# Testy techniczne profilu XR_PERIOD_CANONICAL_V1 (BIND-01 v1.1 §11).
"""Techniczne testy regresyjne, nie scenariusze odbiorowe (karta V12-R1 §16:
``NEW_ACCEPTANCE_SCENARIO_COUNT = 0``)."""

import datetime as dt

import pytest

from xray.canonical import (
    CanonicalPeriod,
    Horizon,
    PeriodContractError,
    TimeBucket,
    canonical_text,
    digest,
    period_payload,
)

MARZEC = CanonicalPeriod(
    start_inclusive=dt.date(2026, 3, 1),
    end_exclusive=dt.date(2026, 4, 1),
)


# --- etykieta poza tożsamością ----------------------------------------------


def test_etykieta_nie_wchodzi_do_ladunku():
    """v1.1 §11: „period_label | Human-readable; identity-excluded"."""
    assert "period_label" not in MARZEC.payload()


def test_inna_etykieta_ten_sam_okres_ten_sam_skrot():
    nazwany = CanonicalPeriod(
        start_inclusive=dt.date(2026, 3, 1),
        end_exclusive=dt.date(2026, 4, 1),
        period_label="marzec 2026",
    )
    inaczej_nazwany = CanonicalPeriod(
        start_inclusive=dt.date(2026, 3, 1),
        end_exclusive=dt.date(2026, 4, 1),
        period_label="III/2026",
    )
    assert digest(nazwany.payload()) == digest(inaczej_nazwany.payload())


# --- granice: daty, nie tekst -----------------------------------------------


def test_granice_datowe_sa_typowane():
    """To jest cała różnica między datą a ciągiem znaków o tych samych cyfrach."""
    tekst = canonical_text(MARZEC.payload())
    assert '"$type":"date"' in tekst


def test_okres_datowy_nie_zawiera_znacznika_czasu():
    """Dowód do W-2: przy granicach datowych w ładunku nie ma typu ``datetime``,
    więc otwarty kontrakt B-08 nie dotyka tej warstwy."""
    assert '"$type":"datetime"' not in canonical_text(MARZEC.payload())


def test_data_i_tekst_o_tych_samych_znakach_daja_rozne_okresy():
    podrobiony = {**MARZEC.payload(), "start_inclusive": "2026-03-01"}
    assert digest(MARZEC.payload()) != digest(podrobiony)


def test_granice_moga_byc_znacznikami_czasu_ze_strefa():
    okres = CanonicalPeriod(
        start_inclusive=dt.datetime(2026, 3, 1, tzinfo=dt.UTC),
        end_exclusive=dt.datetime(2026, 4, 1, tzinfo=dt.UTC),
    )
    assert '"$type":"datetime"' in canonical_text(okres.payload())


# --- kompletność i kierunek przedziału --------------------------------------


def test_polowa_przedzialu_odrzucona():
    with pytest.raises(PeriodContractError):
        CanonicalPeriod(start_inclusive=dt.date(2026, 3, 1))
    with pytest.raises(PeriodContractError):
        CanonicalPeriod(end_exclusive=dt.date(2026, 4, 1))


def test_koniec_przed_poczatkiem_odrzucony():
    with pytest.raises(PeriodContractError):
        CanonicalPeriod(
            start_inclusive=dt.date(2026, 4, 1),
            end_exclusive=dt.date(2026, 3, 1),
        )


def test_rowne_granice_odrzucone():
    """``[start,end)`` z równymi granicami nie obejmuje żadnej chwili."""
    with pytest.raises(PeriodContractError):
        CanonicalPeriod(
            start_inclusive=dt.date(2026, 3, 1),
            end_exclusive=dt.date(2026, 3, 1),
        )


def test_mieszanie_daty_i_znacznika_czasu_odrzucone():
    with pytest.raises(PeriodContractError):
        CanonicalPeriod(
            start_inclusive=dt.date(2026, 3, 1),
            end_exclusive=dt.datetime(2026, 4, 1, tzinfo=dt.UTC),
        )


def test_okres_bez_przedzialu_jest_legalny():
    """Kontrakt nie wymaga, żeby okres miał jednocześnie przedział, horyzont i kubełek."""
    okres = CanonicalPeriod(horizon=Horizon(length=12, unit="MONTH", anchor_semantics="END"))
    assert okres.payload()["start_inclusive"] is None


# --- pozostałe elementy z tabeli §11 ----------------------------------------


def test_horyzont_zmienia_skrot():
    z_horyzontem = CanonicalPeriod(
        start_inclusive=dt.date(2026, 3, 1),
        end_exclusive=dt.date(2026, 4, 1),
        horizon=Horizon(length=12, unit="MONTH", anchor_semantics="END"),
    )
    assert digest(z_horyzontem.payload()) != digest(MARZEC.payload())


def test_inna_dlugosc_horyzontu_to_inny_okres():
    dwanascie = CanonicalPeriod(horizon=Horizon(12, "MONTH", "END"))
    szesc = CanonicalPeriod(horizon=Horizon(6, "MONTH", "END"))
    assert digest(dwanascie.payload()) != digest(szesc.payload())


def test_kubelek_zmienia_skrot():
    z_kubelkiem = CanonicalPeriod(
        start_inclusive=dt.date(2026, 3, 1),
        end_exclusive=dt.date(2026, 4, 1),
        time_bucket=TimeBucket(bucket_unit="MONTH", bucket_key="2026-03"),
    )
    assert digest(z_kubelkiem.payload()) != digest(MARZEC.payload())


def test_time_basis_nie_jest_wnioskowany():
    """v1.1 §11: „Brak reguły → canonical null; nie inferuj dla PROC"."""
    assert MARZEC.payload()["time_basis"] is None


def test_time_basis_zmienia_skrot():
    z_podstawa = CanonicalPeriod(
        start_inclusive=dt.date(2026, 3, 1),
        end_exclusive=dt.date(2026, 4, 1),
        time_basis="EVENT",
    )
    assert digest(z_podstawa.payload()) != digest(MARZEC.payload())


def test_rozszerzenia_semantyczne_zmieniaja_skrot():
    z_rozszerzeniem = CanonicalPeriod(
        start_inclusive=dt.date(2026, 3, 1),
        end_exclusive=dt.date(2026, 4, 1),
        semantic_extensions={"fiscal_year": "2026"},
    )
    assert digest(z_rozszerzeniem.payload()) != digest(MARZEC.payload())


def test_kolejnosc_rozszerzen_nie_ma_znaczenia():
    jeden = CanonicalPeriod(semantic_extensions={"a": 1, "b": 2})
    drugi = CanonicalPeriod(semantic_extensions={"b": 2, "a": 1})
    assert digest(jeden.payload()) == digest(drugi.payload())


# --- brak okresu ------------------------------------------------------------


def test_brak_okresu_to_canonical_null():
    assert period_payload(None) is None


def test_brak_okresu_to_nie_to_samo_co_okres_pusty():
    assert digest({"okres": period_payload(None)}) != digest(
        {"okres": period_payload(CanonicalPeriod())}
    )
