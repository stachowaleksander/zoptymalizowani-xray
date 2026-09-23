# Testy techniczne rekordu próby wykonania i bramki KNOWN/UNKNOWN (karta V12-R1 §9, §11.1).
"""Techniczne testy regresyjne. Wektory C-T18 i C-T19 leżą w ``tests/acceptance/``."""

import datetime as dt

import pytest
from pydantic import ValidationError

from xray.store import FingerprintStatus
from xray.store.attempts import (
    FORBIDDEN_RUN_PROFILE,
    SEMANTIC_RUN_PROFILE,
    ExecutionAttemptRecord,
    ExecutionRelationStatus,
    attempt_required,
    compare_fingerprints,
)
from xray.store.runs import RUN_IDENTITY_VERSION

ODCISK = "FPR-" + "a" * 32
PRZEBIEG = "RUN-" + "b" * 32


def proba(**zmiany) -> ExecutionAttemptRecord:
    pola = {
        "semantic_run_id": PRZEBIEG,
        "execution_fingerprint": ODCISK,
        "fingerprint_status": FingerprintStatus.KNOWN,
        "execution_provenance_ref": "EXE-" + "c" * 32,
        "terminal_status": "COMPLETED",
    }
    return ExecutionAttemptRecord.create(**(pola | zmiany))


# --- tożsamość próby (T-1) --------------------------------------------------


def test_dwie_identyczne_proby_maja_rozne_identyfikatory():
    """Karta §9: identyczna druga próba nie może zniknąć ani zlać się z pierwszą."""
    pierwsza = proba()
    druga = proba()
    assert pierwsza.execution_attempt_id != druga.execution_attempt_id
    assert pierwsza.model_dump(exclude={"execution_attempt_id"}) == druga.model_dump(
        exclude={"execution_attempt_id"}
    )


def test_identyfikator_nie_pochodzi_z_odcisku_ani_z_wyniku():
    """EXECUTION_FINGERPRINT_IS_NOT_EXECUTION_ATTEMPT_ID i RESULT_DIGEST_IS_NOT_…"""
    zapis = proba().execution_attempt_id
    assert ODCISK not in zapis
    assert zapis.startswith("ATTEMPT-")


def test_rekord_jest_niezmienny():
    with pytest.raises(ValidationError):
        proba().terminal_status = "FAILED"


# --- semantic_run_id wg Q1 (T-2) --------------------------------------------


def test_rekord_niesie_wartosc_przebiegu_i_deklaracje_profilu():
    zapis = proba()
    assert zapis.semantic_run_id == PRZEBIEG
    assert zapis.semantic_run_profile == SEMANTIC_RUN_PROFILE == "CURRENT_RUN_IDENTITY_V3"
    assert zapis.semantic_run_identity_version == RUN_IDENTITY_VERSION == "3"


def test_profil_rundy_r3_odrzucony():
    """Cicha reinterpretacja V3 jako XR_SEMANTIC_RUN_PROFILE_01 jest zakazana wprost."""
    with pytest.raises(ValidationError):
        proba(semantic_run_profile=FORBIDDEN_RUN_PROFILE)


def test_brak_przebiegu_odrzucony():
    """Q1: „Canonical null jest niedozwolony"."""
    with pytest.raises(ValidationError):
        proba(semantic_run_id="   ")
    with pytest.raises(ValidationError):
        proba(semantic_run_id=None)


# --- bramka spójności odcisku ------------------------------------------------


def test_known_wymaga_odcisku():
    with pytest.raises(ValidationError):
        proba(fingerprint_status=FingerprintStatus.KNOWN, execution_fingerprint=None)


def test_unknown_wymaga_canonical_null():
    with pytest.raises(ValidationError):
        proba(fingerprint_status=FingerprintStatus.UNKNOWN, execution_fingerprint=ODCISK)


def test_proba_o_nieznanym_odcisku_jest_legalna():
    zapis = proba(fingerprint_status=FingerprintStatus.UNKNOWN, execution_fingerprint=None)
    assert zapis.execution_fingerprint is None


# --- znaczniki czasu to proweniencja (T-3) ----------------------------------


def test_znaczniki_czasu_nie_wchodza_do_zadnego_skrotu():
    """Dwie próby różniące się wyłącznie czasem mają ten sam przebieg i ten sam odcisk."""
    wczesna = proba(
        attempt_started_at=dt.datetime(2026, 3, 1, 8, 0, tzinfo=dt.UTC),
        attempt_completed_at=dt.datetime(2026, 3, 1, 8, 5, tzinfo=dt.UTC),
    )
    pozna = proba(
        attempt_started_at=dt.datetime(2026, 9, 23, 20, 0, tzinfo=dt.UTC),
        attempt_completed_at=dt.datetime(2026, 9, 23, 20, 5, tzinfo=dt.UTC),
    )
    assert wczesna.semantic_run_id == pozna.semantic_run_id
    assert wczesna.execution_fingerprint == pozna.execution_fingerprint
    assert compare_fingerprints(
        wczesna.fingerprint_status,
        wczesna.execution_fingerprint,
        pozna.fingerprint_status,
        pozna.execution_fingerprint,
    ).relation_status is None


def test_brak_znacznikow_jest_legalny():
    """Karta §9: „attempt_started_at / attempt_completed_at evidence **albo null**"."""
    zapis = proba()
    assert zapis.attempt_started_at is None
    assert zapis.attempt_completed_at is None


# --- czego rekord nie ma -----------------------------------------------------


def test_rekord_nie_ma_statusu_rownowaznosci():
    """v1.2 §7.4.2: „Nie zawiera intrinsic scalar execution_equivalence_status" (R1-S13)."""
    pola = set(ExecutionAttemptRecord.model_fields)
    assert "execution_equivalence_status" not in pola
    assert not [p for p in pola if "equivalence" in p or "relation_status" in p]


def test_pole_spoza_kontraktu_odrzucone():
    with pytest.raises(ValidationError):
        proba(execution_equivalence_status="IDEMPOTENT_EQUIVALENT")


def test_rekord_wiaze_minimum_z_karty():
    assert set(ExecutionAttemptRecord.model_fields) >= {
        "execution_attempt_id",
        "semantic_run_id",
        "execution_fingerprint",
        "fingerprint_status",
        "execution_provenance_ref",
        "attempt_started_at",
        "attempt_completed_at",
        "terminal_status",
        "result_record_ids",
        "foundation_bind_version",
    }


def test_puste_pola_obowiazkowe_odrzucone():
    with pytest.raises(ValidationError):
        proba(terminal_status="  ")
    with pytest.raises(ValidationError):
        proba(execution_provenance_ref="")


# --- trafienie w cache (T-4) -------------------------------------------------


def test_cache_przed_wykonaniem_nie_tworzy_proby():
    """Karta §9: „Pre-execution cache hit… nie tworzy nowej próby"."""
    assert attempt_required(computation_started=False) is False


def test_faktyczne_obliczenie_wymaga_rekordu_nawet_przy_identycznym_wyniku():
    assert attempt_required(computation_started=True) is True


# --- bramka KNOWN/UNKNOWN ----------------------------------------------------


def test_oba_znane_i_rowne_kwalifikuja_sie_do_klasyfikacji():
    decyzja = compare_fingerprints(
        FingerprintStatus.KNOWN, ODCISK, FingerprintStatus.KNOWN, ODCISK
    )
    assert decyzja.fingerprint_evidence_sufficient is True
    assert decyzja.relation_status is None


def test_jeden_nieznany_daje_determinism_not_assessable():
    decyzja = compare_fingerprints(
        FingerprintStatus.KNOWN, ODCISK, FingerprintStatus.UNKNOWN, None
    )
    assert decyzja.fingerprint_evidence_sufficient is False
    assert decyzja.relation_status is ExecutionRelationStatus.DETERMINISM_NOT_ASSESSABLE


def test_oba_nieznane_nie_sa_rowne():
    """UNKNOWN_FINGERPRINT_EQUALS_UNKNOWN_FINGERPRINT = false; None == None nic nie dowodzi."""
    decyzja = compare_fingerprints(
        FingerprintStatus.UNKNOWN, None, FingerprintStatus.UNKNOWN, None
    )
    assert decyzja.relation_status is ExecutionRelationStatus.DETERMINISM_NOT_ASSESSABLE


def test_oba_znane_i_rozne_nie_daja_podstawy_do_oceny_determinizmu():
    """To nie jest to samo exact execution, a czwartej wartości katalog nie ma (§11.1).

    Bramka mówi tylko „z odcisków to nie wynika" — nie mówi „nie twórz rekordu".
    """
    decyzja = compare_fingerprints(
        FingerprintStatus.KNOWN, ODCISK, FingerprintStatus.KNOWN, "FPR-" + "d" * 32
    )
    assert decyzja.fingerprint_evidence_sufficient is False
    assert decyzja.relation_status is None


def test_bramka_jest_symetryczna():
    lewa = compare_fingerprints(FingerprintStatus.UNKNOWN, None, FingerprintStatus.KNOWN, ODCISK)
    prawa = compare_fingerprints(FingerprintStatus.KNOWN, ODCISK, FingerprintStatus.UNKNOWN, None)
    assert lewa.relation_status is prawa.relation_status
    assert lewa.fingerprint_evidence_sufficient == prawa.fingerprint_evidence_sufficient


def test_katalog_statusow_ma_dokladnie_trzy_wartosci():
    assert [s.value for s in ExecutionRelationStatus] == [
        "IDEMPOTENT_EQUIVALENT",
        "NONDETERMINISM_CONFLICT",
        "DETERMINISM_NOT_ASSESSABLE",
    ]


def test_niespojne_wejscie_bramki_odrzucone():
    with pytest.raises(ValueError):
        compare_fingerprints(FingerprintStatus.KNOWN, None, FingerprintStatus.KNOWN, ODCISK)
    with pytest.raises(ValueError):
        compare_fingerprints(FingerprintStatus.UNKNOWN, ODCISK, FingerprintStatus.KNOWN, ODCISK)
