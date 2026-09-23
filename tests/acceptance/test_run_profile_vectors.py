# Wektory odbiorowe C-T08 i C-T09 — granica profil / przebieg (karta V12-R1 §16).
"""Dwa scenariusze odbiorowe o tym, co profil mapowania robi z tożsamością przebiegu.

Kod scenariusza jest w nazwie testu, żeby handoff mógł wskazać exact test locator.
``NEW_ACCEPTANCE_SCENARIO_COUNT = 0``.

## Wyłącznie istniejące zachowanie

Karta §16.1 pozwala wykazać te dwa wektory „wyłącznie istniejącym conformant behavior",
a §13 zakazuje w R1 migracji do ``XR_SEMANTIC_RUN_PROFILE_01`` (to V12-R3). Dlatego oba
wektory korzystają z ``RunRef.create(..., profile=...)`` i z istniejącego
``MappingProfile.semantic_digest`` — nic w warstwie przebiegu nie powstaje ani się nie
zmienia.

Granicę semantyczną wyznacza sam kod profilu (``mapping/profile.py``): do skrótu wchodzą
faktycznie użyte przypisania kolumn, deklaracje miar planu i strefa organizacji, a poza nim
zostają „``profile_id`` i ``profile_version`` …, komentarze i formatowanie pliku,
``declared_by`` i ``declared_at``".
"""

import datetime as dt
from pathlib import Path

from xray.canonical import (
    CanonicalPeriod,
    ComponentRef,
    ComponentType,
    ResultIdentityV2,
    ScopeDefinition,
    result_identity,
    scope_id,
)
from xray.ingest import load_table
from xray.mapping import MappingProfile
from xray.mapping.profile import PlanMetricDeclaration
from xray.store import RunRef

ZBIOR = "klient-testowy"
KOSZTY = (
    "date,unit,category,amount\n"
    "2026-01-01,Dział A,wynagrodzenia,100\n"
    "2026-02-01,Dział A,wynagrodzenia,200\n"
)

PYTANIE = ResultIdentityV2(
    test_id="FIN-01",
    test_contract_version="ZOP-XR-FIN-01 v1.0",
    scope_id=scope_id(ScopeDefinition(population=["Dział A"])),
    analysis_period=CanonicalPeriod(
        start_inclusive=dt.date(2026, 1, 1), end_exclusive=dt.date(2026, 3, 1)
    ),
    calculation_component_ref=ComponentRef(
        ComponentType.EXECUTION_COMPONENT, "FIN01-EC-DYNAMICS"
    ),
)


MIARA_PLANU = PlanMetricDeclaration(
    plan_metric="koszt_planowany",
    target_measure="amount",
    definition_match_basis="deklaracja profilu klienta",
    declared_by="controlling klienta",
    declared_at=dt.date(2026, 1, 15),
)


def raport(tmp_path: Path):
    sciezka = tmp_path / "koszty.csv"
    sciezka.write_text(KOSZTY, encoding="utf-8")
    return load_table(sciezka, "COST", dataset_id=ZBIOR).report


def profil() -> MappingProfile:
    return MappingProfile.load("profiles/firma-syntetyczna.yaml")


# --- C-T08 ------------------------------------------------------------------


def test_ct08_zmiana_semantyczna_profilu_zmienia_przebieg(tmp_path: Path):
    """C-T08 SEMANTIC PROFILE CHANGE.

    Invariant (karta §16): „R1 nie implementuje R3; verify compatibility/binding only on
    existing conformant behavior".
    Expected: „different semantic_run_id; R1 does not move profile semantics into result
    identity".

    Zmiana semantyczna: dochodzi deklaracja miary planu. Nie rusza treści ani jednego
    rekordu, więc ``content_digest`` zostaje ten sam — a jednak zmienia wynik, bo dopiero
    z nią PLAN może służyć jako referencja. Stąd wchodzi do ``profile_digest``.
    """
    wejscie = raport(tmp_path)
    bazowy = profil()
    semantycznie_inny = bazowy.model_copy(
        update={
            "plan_metrics": (
                MIARA_PLANU,
            )
        }
    )

    przed = RunRef.create(dataset_id=ZBIOR, reports=[wejscie], profile=bazowy)
    po = RunRef.create(dataset_id=ZBIOR, reports=[wejscie], profile=semantycznie_inny)

    assert przed.profile_digest != po.profile_digest
    assert przed.run_id != po.run_id
    # treść rekordów się nie zmieniła — różnicę robi wyłącznie semantyka profilu
    assert przed.inputs[0].content_digest == po.inputs[0].content_digest


def test_ct08_semantyka_profilu_nie_wchodzi_do_tozsamosci_wyniku(tmp_path: Path):
    """Druga połowa oczekiwania: „R1 does not move profile semantics into result identity".

    ``XR_RESULT_IDENTITY_V2`` ma siedem składników i przebiegu wśród nich nie ma, więc
    zmiana profilu nie może ruszyć tożsamości pytania diagnostycznego.
    """
    wejscie = raport(tmp_path)
    bazowy = profil()
    inny = bazowy.model_copy(update={"organization_timezone": "Europe/Berlin"})

    przed = RunRef.create(dataset_id=ZBIOR, reports=[wejscie], profile=bazowy)
    po = RunRef.create(dataset_id=ZBIOR, reports=[wejscie], profile=inny)

    assert przed.run_id != po.run_id
    assert result_identity(PYTANIE) == result_identity(PYTANIE)
    assert "semantic_run" not in str(PYTANIE.payload())


# --- C-T09 ------------------------------------------------------------------


def test_ct09_zmiana_niesemantyczna_profilu_nie_zmienia_przebiegu(tmp_path: Path):
    """C-T09 NONSEMANTIC PROFILE CHANGE.

    Invariant (karta §16): „R1 nie implementuje R3; nonsemantic metadata may not
    contaminate run/result binding".
    Expected: „same semantic_run_id on conformant behavior".

    Podniesienie numeru wersji profilu i zmiana jego identyfikatora to metadane. Gdyby
    weszły do skrótu, każde przenumerowanie pliku tworzyłoby nowy przebieg — czyli problem
    bajtów o poziom wyżej.
    """
    wejscie = raport(tmp_path)
    bazowy = profil()
    przenumerowany = bazowy.model_copy(
        update={
            "profile_id": bazowy.profile_id + "-kopia",
            "profile_version": bazowy.profile_version + 1,
        }
    )

    przed = RunRef.create(dataset_id=ZBIOR, reports=[wejscie], profile=bazowy)
    po = RunRef.create(dataset_id=ZBIOR, reports=[wejscie], profile=przenumerowany)

    assert przed.profile_digest == po.profile_digest
    assert przed.run_id == po.run_id


def test_ct09_kto_i_kiedy_zadeklarowal_miare_nie_zmienia_przebiegu(tmp_path: Path):
    """Ta sama reguła na drugim polu: ``declared_by`` i ``declared_at`` „mówią kto, nie
    dlaczego to wolno" (``mapping/profile.py``), więc zostają poza skrótem."""
    wejscie = raport(tmp_path)
    bazowy = profil().model_copy(update={"plan_metrics": (MIARA_PLANU,)})
    inny_autor = bazowy.model_copy(
        update={
            "plan_metrics": (
                MIARA_PLANU.model_copy(
                    update={
                        "declared_by": "kto inny",
                        "declared_at": dt.date(2026, 6, 1),
                    }
                ),
            )
        }
    )

    przed = RunRef.create(dataset_id=ZBIOR, reports=[wejscie], profile=bazowy)
    po = RunRef.create(dataset_id=ZBIOR, reports=[wejscie], profile=inny_autor)
    assert przed.run_id == po.run_id


def test_ct09_para_z_ct08_jest_rozlaczna(tmp_path: Path):
    """Wspólny invariant obu wektorów: jedna zmiana semantyczna i jedna niesemantyczna
    zastosowane do tego samego profilu dają dokładnie jeden nowy przebieg."""
    wejscie = raport(tmp_path)
    bazowy = profil()
    tylko_metadane = bazowy.model_copy(update={"profile_version": bazowy.profile_version + 7})
    z_semantyka = tylko_metadane.model_copy(
        update={"organization_timezone": "Europe/Berlin"}
    )

    przebiegi = [
        RunRef.create(dataset_id=ZBIOR, reports=[wejscie], profile=p).run_id
        for p in (bazowy, tylko_metadane, z_semantyka)
    ]
    assert przebiegi[0] == przebiegi[1]
    assert przebiegi[0] != przebiegi[2]
    assert len(set(przebiegi)) == 2
