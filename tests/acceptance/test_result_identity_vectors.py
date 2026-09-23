# Wektory odbiorowe C-T01–C-T07 dla XR_RESULT_IDENTITY_V2 (karta V12-R1 §16).
"""Scenariusze odbiorowe rundy V12-R1 dotyczące tożsamości wyniku.

Każdy test nosi kod scenariusza w nazwie, żeby handoff mógł wskazać **exact test locator**
bez przeszukiwania testów technicznych (karta §16: „Każdy scenario ma otrzymać
w handoffie: exact test/fixture locator, executed command, wynik, expected result").
``NEW_ACCEPTANCE_SCENARIO_COUNT = 0`` — nie tworzymy tu nowych scenariuszy, tylko wykazujemy
te już związane kartą.

## Skąd bierze się „ten sam semantic_run_id" w C-T05, C-T06 i C-T07

Wyłącznie z **istniejącego zachowania**, zgodnie z §16.1 karty: „W R1 wolno użyć wyłącznie
istniejącego conformant behavior do sprawdzenia invariantów R1". Przebieg liczymy dzisiejszym
``RunRef`` (``RUN_IDENTITY_VERSION = "3"``) i tylko porównujemy. Nie budujemy niczego
w warstwie przebiegu, nie migrujemy do ``XR_SEMANTIC_RUN_PROFILE_01`` (to V12-R3) i nie
tworzymy żadnego rekordu — pytanie o pole ``semantic_run_id`` na ``CalculationResultRecord``
pozostaje otwarte (STOP R1-S16 / A).

To, co te trzy wektory faktycznie wykazują, to **rozdział warstw**: ten sam import danych
daje ten sam identyfikator przebiegu, a zmiana testu, zakresu albo okresu zmienia wyłącznie
tożsamość wyniku. Zgodne z v1.2 §10.3: „Test, test_contract_version, scope_id,
analysis_period i reference_id nie należą do semantic data run; tworzą
XR_RESULT_IDENTITY_V2".
"""

import datetime as dt

from xray.canonical import (
    CanonicalPeriod,
    ComponentRef,
    ComponentType,
    ResultIdentityV2,
    ScopeDefinition,
    ScopeOperator,
    ScopePredicate,
    canonical_text,
    component_ref_payload,
    result_identity,
    scope_id,
)
from xray.ingest.report import ImportReport, Rejection, RejectionCategory, SourceRef
from xray.store import RunRef

ZBIOR = "klient-testowy"
SKROT_PUSTEGO_STRUMIENIA = "cae66941d9efbd404e4d88758ea67670"

MARZEC = CanonicalPeriod(start_inclusive=dt.date(2026, 3, 1), end_exclusive=dt.date(2026, 4, 1))
KWIECIEN = CanonicalPeriod(start_inclusive=dt.date(2026, 4, 1), end_exclusive=dt.date(2026, 5, 1))

# Zakresy budowane kanonicznym predykatem z v1.0 §4.1 (wpis B-09, sekcja C).
DZIAL_A = ScopeDefinition(
    filters=[ScopePredicate("jednostka", ScopeOperator.EQ, "A")],
    aggregation_level="UNIT",
    scope_label="Dział A",
)
DZIAL_B = ScopeDefinition(
    filters=[ScopePredicate("jednostka", ScopeOperator.EQ, "B")],
    aggregation_level="UNIT",
    scope_label="Dział B",
)
ZAKRES_A = scope_id(DZIAL_A)
ZAKRES_B = scope_id(DZIAL_B)

FIN01 = "ZOP-XR-FIN-01 v1.0"
CAP01 = "ZOP-XR-CAP-01 v1.0"


def pytanie(**zmiany) -> ResultIdentityV2:
    pola = {
        "test_id": "FIN-01",
        "test_contract_version": FIN01,
        "scope_id": ZAKRES_A,
        "analysis_period": MARZEC,
        "calculation_component_ref": ComponentRef(
            ComponentType.EXECUTION_COMPONENT, "FIN01-EC-DYNAMICS"
        ),
    }
    return ResultIdentityV2(**(pola | zmiany))


def przebieg() -> RunRef:
    """Jeden i ten sam import — budowany z jawnego raportu, tak jak w testach przebiegu."""
    raport = ImportReport(
        table_name="COST",
        source=SourceRef.create(
            dataset_id=ZBIOR, source_file="koszty.csv", source_path="koszty.csv"
        ),
        records_accepted=0,
        records_rejected=1,
        content_digest=SKROT_PUSTEGO_STRUMIENIA,
        rejections=(
            Rejection(
                file_row=2,
                reason="unit: pole wymagane",
                category=RejectionCategory.MISSING_VALUE,
                fields=("unit",),
            ),
        ),
        timestamps_converted=0,
        ambiguous_local_times=(),
    )
    return RunRef.create(dataset_id=ZBIOR, reports=[raport])


# --- C-T01 ------------------------------------------------------------------


def test_ct01_inny_execution_component_daje_inna_tozsamosc_wyniku():
    """C-T01 DIFFERENT EXECUTION COMPONENT.

    Invariant: „calculation_component_ref component_id jest częścią result identity".
    Expected: different result_identity; same semantic_run_id.
    """
    dynamika = pytanie()
    trend = pytanie(
        calculation_component_ref=ComponentRef(
            ComponentType.EXECUTION_COMPONENT, "FIN01-EC-TREND"
        )
    )
    assert result_identity(dynamika) != result_identity(trend)
    assert przebieg().run_id == przebieg().run_id


# --- C-T02 ------------------------------------------------------------------


def test_ct02_ten_sam_modul_i_reszta_identyczna_daje_te_sama_tozsamosc():
    """C-T02 SAME FORMAL MODULE.

    Invariant: „identyczny MODULE ref i pozostałe ingredients".
    Expected: same result_identity.
    """
    modul = ComponentRef(ComponentType.MODULE, "FIN02-M-CM1_AMOUNT")
    jeden = pytanie(
        test_id="FIN-02",
        test_contract_version="ZOP-XR-FIN-02 v1.0",
        calculation_component_ref=modul,
    )
    drugi = pytanie(
        test_id="FIN-02",
        test_contract_version="ZOP-XR-FIN-02 v1.0",
        calculation_component_ref=ComponentRef(ComponentType.MODULE, "FIN02-M-CM1_AMOUNT"),
    )
    assert result_identity(jeden) == result_identity(drugi)


# --- C-T03 ------------------------------------------------------------------


def test_ct03_ten_sam_id_inny_typ_komponentu_daje_rozne_tozsamosci():
    """C-T03 MODULE VS EXECUTION_COMPONENT SAME ID.

    Invariant: „component_type jest identity-significant".
    Expected: different result_identity.

    Rejestr §6.1 nie przypisuje żadnemu testowi obu typów naraz, więc wektor buduje się na
    samej strukturze referencji — to jest własność kanonizacji, nie rejestru.
    """
    jako_modul = pytanie(calculation_component_ref=ComponentRef(ComponentType.MODULE, "X"))
    jako_komponent = pytanie(
        calculation_component_ref=ComponentRef(ComponentType.EXECUTION_COMPONENT, "X")
    )
    assert result_identity(jako_modul) != result_identity(jako_komponent)


# --- C-T04 ------------------------------------------------------------------


def test_ct04_canonical_null_jest_stabilny_i_rozny_od_kazdego_komponentu():
    """C-T04 NON-MODULAR TEST — **zdolność wykazana, przesłanka bez podmiotu**.

    Invariant: „true non-modular => calculation_component_ref canonical null; no fabricated
    component". Expected: „stable result_identity without fabricated component".

    Wykazujemy zdolność: canonical null ma stabilną postać, daje powtarzalną tożsamość
    i różni się od każdej referencji komponentu — czyli test niemodularny **dostałby**
    poprawną tożsamość bez fabrykowania komponentu.

    Samej przesłanki na zamrożonym źródle nie ma. v1.2 §8 klasyfikuje wszystkie dziesięć
    testów Core 10 jako ``SOURCE_DEFINED_INDEPENDENT_OUTPUTS_BINDABLE`` albo
    ``FORMAL_MODULES_EXPLICIT``, każdy z niepustą listą komponentów i kolumną „TEST_PARTIAL
    reachable? = YES". Żaden nie jest non-modular. Do handoffu scenariusz idzie jako
    **NOT_APPLICABLE z podstawą v1.2 §8**, a nie jako PASS. Atrapa NOOP-01 nie jest
    zamrożonym źródłem i nie wolno jej tu użyć jako podmiotu.
    """
    bez_komponentu = pytanie(calculation_component_ref=None)
    powtorzony = pytanie(calculation_component_ref=None)
    assert canonical_text(component_ref_payload(None)) == "null"
    assert result_identity(bez_komponentu) == result_identity(powtorzony)
    assert result_identity(bez_komponentu) != result_identity(pytanie())


# --- C-T05 ------------------------------------------------------------------


def test_ct05_ten_sam_zbior_danych_dwa_testy():
    """C-T05 SAME DATA / DIFFERENT TEST.

    Invariant: „test_id poza semantic data run; w result identity".
    Expected: same semantic_run_id; different result_identity.
    """
    fin = pytanie()
    cap = pytanie(
        test_id="CAP-01",
        test_contract_version=CAP01,
        calculation_component_ref=ComponentRef(
            ComponentType.EXECUTION_COMPONENT, "CAP01-EC-PHYSICAL_UTILIZATION"
        ),
    )
    assert przebieg().run_id == przebieg().run_id
    assert result_identity(fin) != result_identity(cap)


# --- C-T06 ------------------------------------------------------------------


def test_ct06_ten_sam_zbior_danych_dwa_zakresy():
    """C-T06 SAME DATA / DIFFERENT SCOPE.

    Invariant: „scope_id poza data run; w result identity".
    Expected: same semantic_run_id; different result_identity.

    Zakresy różnią się **wartością predykatu** `jednostka EQ A` wobec `jednostka EQ B`,
    czyli na strukturze z v1.0 §4.1, a nie samą populacją.
    """
    assert przebieg().run_id == przebieg().run_id
    assert result_identity(pytanie(scope_id=ZAKRES_A)) != result_identity(
        pytanie(scope_id=ZAKRES_B)
    )


def test_ct06_ta_sama_semantyka_zakresu_daje_te_sama_tozsamosc_wyniku():
    """Druga połowa tej samej własności: `different_label + same_semantics → same_scope_id`
    (v1.0 §4.1 pkt 6) ma przenosić się na `result_identity`.

    Ten sam predykat wymieniony w innej kolejności i pod inną etykietą — jedno pytanie.
    """
    inaczej_opisany = ScopeDefinition(
        filters=[ScopePredicate("jednostka", ScopeOperator.EQ, "A")],
        aggregation_level="UNIT",
        scope_label="oddział przy Kwiatowej",
    )
    assert scope_id(inaczej_opisany) == ZAKRES_A
    assert result_identity(pytanie(scope_id=scope_id(inaczej_opisany))) == result_identity(
        pytanie(scope_id=ZAKRES_A)
    )


# --- C-T07 ------------------------------------------------------------------


def test_ct07_ten_sam_zbior_danych_dwa_okresy():
    """C-T07 SAME DATA / DIFFERENT PERIOD.

    Invariant: „analysis_period poza data run; w result identity".
    Expected: same semantic_run_id; different result_identity.
    """
    assert przebieg().run_id == przebieg().run_id
    assert result_identity(pytanie(analysis_period=MARZEC)) != result_identity(
        pytanie(analysis_period=KWIECIEN)
    )


# --- wspólny invariant trzech ostatnich -------------------------------------


def test_zmiana_pytania_nie_rusza_identyfikatora_przebiegu():
    """v1.2 §10.3: pytanie diagnostyczne nie należy do semantic data run.

    Jeden import, trzy różne pytania — identyfikator przebiegu ani drgnie.
    """
    run_id = przebieg().run_id
    tozsamosci = {
        result_identity(pytanie()),
        result_identity(pytanie(scope_id=ZAKRES_B)),
        result_identity(pytanie(analysis_period=KWIECIEN)),
    }
    assert len(tozsamosci) == 3
    assert przebieg().run_id == run_id
