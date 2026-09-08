# Sprawdza kontrakt FINDINGS z ZOP-TECH-01 v0.1 pkt 5.4, ZOP-CONF-01 v1.0 rozdz. 3–4
# oraz ZOP-PRI-01 v1.0 rozdz. 5 i 8.
"""Testy struktury wynikowej.

Największa wartość tych testów leży w regułach, których złamania nie widać gołym okiem:
determinizmie identyfikatorów, zakazie przenoszenia klasy pewności między poziomami
i zakazie wyznaczania luki bez referencji.
"""

import datetime as dt

import pytest
from pydantic import ValidationError

from xray.model import (
    ClaimEvidenceLink,
    ClaimRecord,
    ClaimType,
    ConfidenceClass,
    ConfidenceSourceLevel,
    EvidenceRecord,
    EvidenceRole,
    FindingRecord,
    LogicalStatus,
    PeriodRef,
    PriorityBasisStatus,
    PriorityRecord,
    ProblemPriorityAction,
    ReferenceRef,
    ReferenceType,
    ScopeRef,
)
from xray.model.findings.identity import (
    IDENTITY_ALGORITHM_VERSION,
    UnknownIdentityAlgorithm,
    canonical_form,
    compute_id,
)

ZAKRES = ScopeRef(scope_label="Dział A", units=("Dział A",), aggregation_level="unit")
OKRES = PeriodRef(period_start=dt.date(2026, 1, 1), period_end=dt.date(2026, 3, 31))


def zbuduj_wynik(**pola) -> FindingRecord:
    domyslne = {
        "test_id": "NOOP-01",
        "scope": ZAKRES,
        "period": OKRES,
        "status": LogicalStatus.NO_ADVERSE_SIGNAL,
        "finding": "Brak sygnału niekorzystnego.",
    }
    return FindingRecord.create(**{**domyslne, **pola})


# --- determinizm identyfikatorów (zasada 3) -----------------------------------------


def test_dwa_przebiegi_daja_ten_sam_identyfikator() -> None:
    """Te same dane plus ta sama wersja kodu = ten sam wynik."""
    assert zbuduj_wynik().finding_id == zbuduj_wynik().finding_id


def test_inny_zakres_daje_inny_identyfikator() -> None:
    """FIN-01 produkuje wyniki per jednostka i per kategoria — bez rozróżnienia
    zakresu identyfikatory skleiłyby się w jeden."""
    inny = ScopeRef(scope_label="Dział B", units=("Dział B",), aggregation_level="unit")
    assert zbuduj_wynik().finding_id != zbuduj_wynik(scope=inny).finding_id


def test_inna_wersja_kontraktu_daje_inny_identyfikator() -> None:
    """Zmiana kontraktu produkuje nowe identyfikatory zamiast nadpisywać stare rekordy."""
    assert (
        zbuduj_wynik().finding_id
        != zbuduj_wynik(contract_version="ZOP-TECH-01/v0.2").finding_id
    )


def test_identyfikator_nie_zalezy_od_kolejnosci_kluczy() -> None:
    """Kanonizacja sortuje klucze, więc kolejność zapisu nie zmienia skrótu."""
    assert canonical_form({"b": 1, "a": 2}) == canonical_form({"a": 2, "b": 1})


def test_krotka_tozsamosci_jest_odczytywalna() -> None:
    """Sam skrót jest ślepym zaułkiem dla audytu; składniki muszą być widoczne."""
    wynik = zbuduj_wynik()
    assert wynik.test_id == "NOOP-01"
    assert wynik.scope == ZAKRES
    assert wynik.period == OKRES
    assert wynik.contract_version


def test_podmieniony_identyfikator_jest_odrzucany() -> None:
    """Rekord sprawdza, że jego identyfikator prowadzi do jego własnych składników."""
    wynik = zbuduj_wynik()
    dane = wynik.model_dump()
    dane["finding_id"] = "FND-0000000000000000"
    with pytest.raises(ValidationError):
        FindingRecord(**dane)


# --- zakaz score'u i katalog klas ----------------------------------------------------


def test_confidence_score_nie_przyjmuje_liczby() -> None:
    """CONF-01 pkt 2.2: „ZAKAZ WSKAŹNIKA confidence_score = null"."""
    with pytest.raises(ValidationError):
        zbuduj_wynik(confidence_score=0.8)


def test_confidence_score_domyslnie_jest_none() -> None:
    assert zbuduj_wynik().confidence_score is None


# --- luka bez referencji (FIN-01 rozdz. 6) -------------------------------------------


def test_luka_bez_referencji_jest_odrzucana() -> None:
    """FIN-01 rozdz. 6: bez referencji gap, impact_low i impact_high pozostają null."""
    with pytest.raises(ValidationError) as blad:
        zbuduj_wynik(gap=-12_000.0)
    assert "referencji" in str(blad.value)


def test_wplyw_bez_referencji_jest_odrzucany() -> None:
    with pytest.raises(ValidationError):
        zbuduj_wynik(impact_low=1_000.0, impact_high=5_000.0)


def test_luka_z_referencja_przechodzi() -> None:
    referencja = ReferenceRef(
        reference_type=ReferenceType.OWN_HISTORY,
        reference_period=PeriodRef(
            period_start=dt.date(2025, 1, 1), period_end=dt.date(2025, 3, 31)
        ),
        reference_value=300_000.0,
    )
    wynik = zbuduj_wynik(reference=referencja, gap=-12_000.0)
    assert wynik.gap == -12_000.0
    assert wynik.reference is not None
    assert wynik.reference.reference_type is ReferenceType.OWN_HISTORY


def test_wynik_bez_referencji_moze_miec_miare() -> None:
    """Brak referencji nie unieważnia samej miary — znika tylko luka."""
    wynik = zbuduj_wynik(metric_value=318_000.0)
    assert wynik.metric_value == 318_000.0
    assert wynik.gap is None


# --- twierdzenia: CONF-01 rozdz. 3 ---------------------------------------------------


def zbuduj_twierdzenie(**pola) -> ClaimRecord:
    domyslne = {
        "claim_type": ClaimType.FINDING_CLAIM,
        "claim_scope": ZAKRES,
        "claim_period": OKRES,
        "confidence_context": "przegląd kwartalny",
        "claim_source_test": "NOOP-01",
        "claim_text": "Brak sygnału niekorzystnego w badanym zakresie.",
    }
    return ClaimRecord.create(**{**domyslne, **pola})


def test_wersja_twierdzenia_zmienia_tozsamosc() -> None:
    """claim_version należy do tożsamości, nie do opisu.

    Poprzednia wersja zostaje osobnym, rozróżnialnym rekordem — na tym polega
    wersjonowanie.
    """
    assert zbuduj_twierdzenie().claim_id != zbuduj_twierdzenie(claim_version=2).claim_id


def test_kontekst_pewnosci_zmienia_tozsamosc() -> None:
    """Ta sama treść oceniana w innym kontekście użycia jest innym twierdzeniem."""
    assert (
        zbuduj_twierdzenie().claim_id
        != zbuduj_twierdzenie(confidence_context="decyzja inwestycyjna").claim_id
    )


def test_typ_twierdzenia_zmienia_tozsamosc() -> None:
    assert (
        zbuduj_twierdzenie().claim_id
        != zbuduj_twierdzenie(claim_type=ClaimType.MECHANISM_CLAIM).claim_id
    )


def test_klasa_z_niewlasciwego_poziomu_jest_odrzucana() -> None:
    """CONF-01: „Nie wolno przepisywać klasy z jednego poziomu na drugi"."""
    with pytest.raises(ValidationError) as blad:
        zbuduj_twierdzenie(
            claim_type=ClaimType.MECHANISM_CLAIM,
            confidence_class=ConfidenceClass.WELL_SUPPORTED,
            confidence_class_source_level=ConfidenceSourceLevel.FINDING_CONFIDENCE,
        )
    assert "poziomu" in str(blad.value)


def test_klasa_bez_wskazania_poziomu_jest_odrzucana() -> None:
    """Klasa bez poziomu nie mówi, czego dotyczy."""
    with pytest.raises(ValidationError):
        zbuduj_twierdzenie(confidence_class=ConfidenceClass.WELL_SUPPORTED)


def test_klasa_ze_zgodnego_poziomu_przechodzi() -> None:
    twierdzenie = zbuduj_twierdzenie(
        claim_type=ClaimType.METRIC_CLAIM,
        confidence_class=ConfidenceClass.SUPPORTED_WITH_LIMITATIONS,
        confidence_class_source_level=ConfidenceSourceLevel.METRIC_CONFIDENCE,
    )
    assert twierdzenie.confidence_class is ConfidenceClass.SUPPORTED_WITH_LIMITATIONS


# --- dowody i powiązania: CONF-01 rozdz. 4, wpis B-05 --------------------------------


def test_ten_sam_dowod_moze_wspierac_dwa_twierdzenia() -> None:
    """Relacja jest wiele-do-wielu — patrz wpis B-05.

    Gdyby dowód należał na własność do twierdzenia, ten sam dowód trzeba by zduplikować,
    a evidence_source_group_id przestałby odróżniać duplikat od dwóch niezależnych źródeł.
    """
    dowod = EvidenceRecord.create(
        evidence_type="zestawienie kosztów",
        evidence_source="plik klienta v1",
    )
    a = ClaimEvidenceLink.create(
        claim_id="CLM-a",
        claim_version=1,
        evidence_id=dowod.evidence_id,
        evidence_role=EvidenceRole.PRIMARY_EVIDENCE,
    )
    b = ClaimEvidenceLink.create(
        claim_id="CLM-b",
        claim_version=1,
        evidence_id=dowod.evidence_id,
        evidence_role=EvidenceRole.CONTEXTUAL_EVIDENCE,
    )
    assert a.evidence_id == b.evidence_id
    assert a.link_id != b.link_id


def test_rola_dowodu_nalezy_do_powiazania_nie_do_dowodu() -> None:
    """Ten sam dowód może być główny dla jednego twierdzenia i kontekstem dla drugiego."""
    assert "evidence_role" not in EvidenceRecord.model_fields
    assert "evidence_role" in ClaimEvidenceLink.model_fields


def test_powiazanie_wskazuje_wersje_twierdzenia() -> None:
    """Dowód przypisany do wersji 1 nie przechodzi automatycznie na wersję 2."""
    w1 = ClaimEvidenceLink.create(
        claim_id="CLM-a",
        claim_version=1,
        evidence_id="EVD-x",
        evidence_role=EvidenceRole.PRIMARY_EVIDENCE,
    )
    w2 = ClaimEvidenceLink.create(
        claim_id="CLM-a",
        claim_version=2,
        evidence_id="EVD-x",
        evidence_role=EvidenceRole.PRIMARY_EVIDENCE,
    )
    assert w1.link_id != w2.link_id


# --- priorytet: PRI-01 rozdz. 3 i 8 --------------------------------------------------


def test_niewystarczajaca_podstawa_dopuszcza_tylko_not_assessable() -> None:
    """PRI-01 pkt 8.1: „insufficient prowadzi do not_assessable"."""
    with pytest.raises(ValidationError) as blad:
        PriorityRecord(
            finding_id="FND-x",
            priority_context_id="przeglad-2026Q1",
            priority_evaluation_date=dt.date(2026, 4, 1),
            priority_basis_version="v1",
            problem_priority_basis_status=PriorityBasisStatus.INSUFFICIENT,
            problem_priority_action=ProblemPriorityAction.REVIEW_NOW,
        )
    assert "not_assessable" in str(blad.value)


def test_niewystarczajaca_podstawa_z_not_assessable_przechodzi() -> None:
    rekord = PriorityRecord(
        finding_id="FND-x",
        priority_context_id="przeglad-2026Q1",
        priority_evaluation_date=dt.date(2026, 4, 1),
        priority_basis_version="v1",
        problem_priority_basis_status=PriorityBasisStatus.INSUFFICIENT,
        problem_priority_action=ProblemPriorityAction.NOT_ASSESSABLE,
    )
    assert rekord.problem_priority_action is ProblemPriorityAction.NOT_ASSESSABLE


def test_priorytet_nie_jest_polem_wyniku() -> None:
    """PRI-01 rozdz. 3: zmiana kontekstu tworzy nową ewaluację, nie nadpisuje śladu.

    Gdyby priorytet był kolumną w FINDINGS, każda ponowna ocena kasowałaby poprzednią.
    """
    assert "problem_priority_action" not in FindingRecord.model_fields
    assert "priority_context_id" in PriorityRecord.model_fields


# --- pola kontekstu chwili zapisu ----------------------------------------------------


def test_wynik_niesie_pola_ochrony_wplywu() -> None:
    """Bez nich nie da się wstecz ustalić, które wyniki opisywały ten sam wpływ."""
    assert "impact_group_id" in FindingRecord.model_fields
    assert "impact_accounting_role" in FindingRecord.model_fields


def test_dowod_niesie_grupe_wspolnego_zrodla() -> None:
    """Wspólne pochodzenie jest faktem o momencie zapisu; po fakcie nie do odtworzenia."""
    assert "evidence_source_group_id" in EvidenceRecord.model_fields


# --- wersja algorytmu tożsamości -----------------------------------------------------


def test_rekord_niesie_wersje_algorytmu_tozsamosci() -> None:
    """Bez tego nie dałoby się odróżnić rekordu policzonego starym algorytmem
    od uszkodzonego."""
    assert zbuduj_wynik().identity_algorithm_version == IDENTITY_ALGORITHM_VERSION
    for klasa in (FindingRecord, ClaimRecord, EvidenceRecord, ClaimEvidenceLink):
        assert "identity_algorithm_version" in klasa.model_fields, klasa.__name__


def test_rozne_wersje_algorytmu_daja_rozne_identyfikatory() -> None:
    """Wersja algorytmu wchodzi do krotki tożsamości, więc ta sama treść policzona
    inną wersją daje inny skrót — i stary rekord nie miesza się z nowym."""
    a = FindingRecord.identity_of(
        test_id="NOOP-01", scope=ZAKRES, period=OKRES, identity_algorithm_version="1"
    )
    b = FindingRecord.identity_of(
        test_id="NOOP-01", scope=ZAKRES, period=OKRES, identity_algorithm_version="99"
    )
    assert a != b
    assert canonical_form(a) != canonical_form(b)


def test_nieznana_wersja_algorytmu_ma_wlasny_wyjatek() -> None:
    """Rekord zapisany nowszym wydaniem systemu NIE jest uszkodzony.

    Mylenie tych dwóch przypadków kazałoby uznać poprawne dane za uszkodzone.
    """
    with pytest.raises(UnknownIdentityAlgorithm) as blad:
        compute_id("FND", {"a": 1}, algorithm_version="99")
    assert "nie jest uszkodzony" in str(blad.value)


def test_wersja_kontraktu_nie_wywoluje_masowego_odrzucania() -> None:
    """Stary rekord przelicza się ze SWOJĄ wersją kontraktu i dalej się zgadza.

    identity_of bierze self.contract_version, a nie stałą z modułu — to celowa ochrona.
    """
    stary = zbuduj_wynik(contract_version="ZOP-TECH-01/v0.0")
    odczytany = FindingRecord(**stary.model_dump())
    assert odczytany.finding_id == stary.finding_id


def test_zmiana_tresci_po_zapisie_jest_wykrywana() -> None:
    """To jest to, przed czym chroni sprawdzenie tożsamości przy odczycie."""
    dane = zbuduj_wynik().model_dump()
    dane["test_id"] = "FIN-01"  # ręczna poprawka w magazynie
    with pytest.raises(ValidationError) as blad:
        FindingRecord(**dane)
    assert "tożsamości" in str(blad.value)
