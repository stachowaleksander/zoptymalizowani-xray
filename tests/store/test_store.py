# Sprawdza magazyn wyników: tożsamość przebiegu, idempotentność i odczyt przez
# sprawdzenie tożsamości rekordu.
"""Testy warstwy zapisu.

Najważniejsze są trzy: rekord odczytany jest identyczny z zapisanym, ręczna zmiana
w bazie jest wykrywana, a ten sam plik dwa razy nie tworzy duplikatu.

Wykonanie jest tu jedno i stałe: badamy przebieg i odczyt. Invariant wykonań — ten sam albo
inny odcisk — sprawdza ``tests/store/test_executions.py``.
"""

import datetime as dt
from pathlib import Path

import pandas as pd
import pytest

from xray.ingest import load_table
from xray.mapping import MappingProfile
from xray.model import FindingRecord, LogicalStatus, PeriodRef, ScopeRef
from xray.store import (
    ConflictingRun,
    ExecutionRef,
    FindingStore,
    FingerprintStatus,
    ProjectionMismatch,
    RunRef,
    connect,
)

ZBIOR = "klient-testowy"
KOSZTY = (
    "date,unit,category,amount\n"
    "2026-01-01,Dział A,wynagrodzenia,100\n"
    "2026-02-01,Dział A,wynagrodzenia,200\n"
)
ZAKRES = ScopeRef(scope_label="cała firma")
OKRES = PeriodRef(period_start=dt.date(2026, 1, 1), period_end=dt.date(2026, 2, 28))

WYKONANIE = ExecutionRef(
    execution_fingerprint="FPR-testowy",
    fingerprint_status=FingerprintStatus.KNOWN,
    fingerprint_basis={"opis": "odcisk zadeklarowany w teście: ten sam kod i środowisko"},
    code_provenance={"git_status": "unavailable", "reason": "test jednostkowy"},
)


def zapisz_plik(katalog: Path, tresc: str = KOSZTY, nazwa: str = "koszty.csv") -> Path:
    sciezka = katalog / nazwa
    sciezka.write_text(tresc, encoding="utf-8")
    return sciezka


def zbuduj_wynik(**pola) -> FindingRecord:
    domyslne = {
        "test_id": "NOOP-01",
        "scope": ZAKRES,
        "period": OKRES,
        "status": LogicalStatus.NO_ADVERSE_SIGNAL,
        "finding": "Brak sygnału niekorzystnego.",
        "metric_value": 2.0,
    }
    return FindingRecord.create(**{**domyslne, **pola})


def zbuduj_przebieg(katalog: Path, tresc: str = KOSZTY, nazwa: str = "koszty.csv"):
    raport = load_table(zapisz_plik(katalog, tresc, nazwa), "COST", dataset_id=ZBIOR).report
    return RunRef.create(dataset_id=ZBIOR, reports=[raport])


# --- zapisz → odczytaj -----------------------------------------------------------------


def test_rekord_odczytany_jest_identyczny_z_zapisanym(tmp_path: Path) -> None:
    """Odczyt idzie przez model_validate_json, więc przechodzi przez _check_identity."""
    store = FindingStore(connect(":memory:"))
    run = zbuduj_przebieg(tmp_path)
    wynik = zbuduj_wynik()
    assert store.save_run(run, (wynik,), WYKONANIE) is True
    assert store.load_run(run.run_id) == (wynik,)


def test_zapis_przetrwa_zamkniecie_bazy(tmp_path: Path) -> None:
    """SQLite jako magazyn kanoniczny, a nie bufor w pamięci."""
    plik_bazy = tmp_path / "xray.db"
    run = zbuduj_przebieg(tmp_path)
    wynik = zbuduj_wynik()
    polaczenie = connect(plik_bazy)
    FindingStore(polaczenie).save_run(run, (wynik,), WYKONANIE)
    polaczenie.close()
    assert FindingStore(connect(plik_bazy)).load_run(run.run_id) == (wynik,)


# --- ręczna zmiana w bazie -------------------------------------------------------------


def test_reczna_zmiana_tresci_w_bazie_jest_odrzucana(tmp_path: Path) -> None:
    """To jest moment, w którym sprawdzenie tożsamości przy odczycie zaczyna coś robić."""
    polaczenie = connect(":memory:")
    store = FindingStore(polaczenie)
    run = zbuduj_przebieg(tmp_path)
    wynik = zbuduj_wynik()
    store.save_run(run, (wynik,), WYKONANIE)

    podmieniony = wynik.model_copy(update={"test_id": "FIN-01"}).model_dump_json()
    polaczenie.execute(
        "UPDATE findings SET payload = ? WHERE finding_id = ?",
        (podmieniony, wynik.finding_id),
    )
    polaczenie.commit()

    with pytest.raises(ValueError) as blad:
        store.load_run(run.run_id)
    assert "tożsamości" in str(blad.value)


def test_reczna_zmiana_kolumny_indeksu_jest_wykrywana(tmp_path: Path) -> None:
    """Indeks, który po cichu kłamie, jest gorszy od braku indeksu.

    Zapytanie o status = 'WARNING' zwróciłoby zły zbiór i nikt by się nie dowiedział.
    """
    polaczenie = connect(":memory:")
    store = FindingStore(polaczenie)
    run = zbuduj_przebieg(tmp_path)
    wynik = zbuduj_wynik()
    store.save_run(run, (wynik,), WYKONANIE)

    polaczenie.execute(
        "UPDATE findings SET status = 'CRITICAL' WHERE finding_id = ?",
        (wynik.finding_id,),
    )
    polaczenie.commit()

    with pytest.raises(ProjectionMismatch) as blad:
        store.load_run(run.run_id)
    assert "status" in str(blad.value)


# --- idempotentność --------------------------------------------------------------------


def test_ten_sam_plik_dwa_razy_daje_ten_sam_przebieg(tmp_path: Path) -> None:
    a = tmp_path / "a"
    b = tmp_path / "b"
    a.mkdir()
    b.mkdir()
    assert zbuduj_przebieg(a).run_id == zbuduj_przebieg(b).run_id


def test_powtorny_zapis_nie_tworzy_duplikatu(tmp_path: Path) -> None:
    """Bez tego testu idempotentność byłaby deklaracją."""
    store = FindingStore(connect(":memory:"))
    run = zbuduj_przebieg(tmp_path)
    wynik = zbuduj_wynik()
    assert store.save_run(run, (wynik,), WYKONANIE) is True
    assert store.save_run(run, (wynik,), WYKONANIE) is False
    assert len(store.load_run(run.run_id)) == 1
    assert store.runs() == (run.run_id,)


def test_ten_sam_przebieg_z_inna_trescia_jest_sprzecznoscia(tmp_path: Path) -> None:
    """Ten sam skrót wejścia i ten sam odcisk z innym wynikiem: przepływ nie jest
    deterministyczny."""
    store = FindingStore(connect(":memory:"))
    run = zbuduj_przebieg(tmp_path)
    store.save_run(run, (zbuduj_wynik(metric_value=2.0),), WYKONANIE)
    with pytest.raises(ConflictingRun) as blad:
        store.save_run(run, (zbuduj_wynik(metric_value=99.0),), WYKONANIE)
    assert "deterministyczny" in str(blad.value)


# --- tożsamość przebiegu ---------------------------------------------------------------


def test_poprawione_dane_daja_nowy_przebieg(tmp_path: Path) -> None:
    """Poprawka niezmieniająca liczby wierszy — najczęstszy przypadek."""
    a = tmp_path / "a"
    b = tmp_path / "b"
    a.mkdir()
    b.mkdir()
    poprawione = KOSZTY.replace("200", "250")
    assert zbuduj_przebieg(a).run_id != zbuduj_przebieg(b, poprawione).run_id


def test_zmiana_formatu_pliku_nie_tworzy_nowego_przebiegu(tmp_path: Path) -> None:
    """Zmiana formatu zapisu nie jest zmianą danych."""
    dane = pd.DataFrame(
        {
            "date": [dt.date(2026, 1, 1), dt.date(2026, 2, 1)],
            "unit": ["Dział A", "Dział A"],
            "category": ["wynagrodzenia", "wynagrodzenia"],
            "amount": [100.0, 200.0],
        }
    )
    csv = tmp_path / "koszty.csv"
    xlsx = tmp_path / "koszty.xlsx"
    dane.to_csv(csv, index=False, encoding="utf-8")
    dane.to_excel(xlsx, index=False)
    z_csv = load_table(csv, "COST", dataset_id=ZBIOR).report
    z_xlsx = load_table(xlsx, "COST", dataset_id=ZBIOR).report
    assert z_csv.content_digest == z_xlsx.content_digest
    assert (
        RunRef.create(dataset_id=ZBIOR, reports=[z_csv]).run_id
        == RunRef.create(dataset_id=ZBIOR, reports=[z_xlsx]).run_id
    )


def test_czas_wykonania_nie_wchodzi_do_zadnej_tozsamosci(tmp_path: Path) -> None:
    """executed_at jest polem audytowym poza tożsamością przebiegu i wykonania.

    Gdyby wchodził, każde wykonanie byłoby „nowe", a kontrola determinizmu cicho
    przestałaby działać.
    """
    store = FindingStore(connect(":memory:"))
    run = zbuduj_przebieg(tmp_path)
    wczesniej = WYKONANIE.model_copy(update={"executed_at": dt.datetime(2026, 1, 1)})
    pozniej = WYKONANIE.model_copy(update={"executed_at": dt.datetime(2026, 9, 6)})
    assert store.save_run(run, (zbuduj_wynik(),), wczesniej) is True
    assert store.save_run(run, (zbuduj_wynik(),), pozniej) is False
    assert "executed_at" not in RunRef.model_fields


def test_kolejnosc_raportow_nie_zmienia_tozsamosci(tmp_path: Path) -> None:
    """Kolejność wywołań importu nie jest cechą danych."""
    koszty = load_table(zapisz_plik(tmp_path), "COST", dataset_id=ZBIOR).report
    plan = tmp_path / "plan.csv"
    plan.write_text("date,unit,metric,target\n2026-01-01,A,koszt,250\n", encoding="utf-8")
    plan_raport = load_table(plan, "PLAN", dataset_id=ZBIOR).report
    assert (
        RunRef.create(dataset_id=ZBIOR, reports=[koszty, plan_raport]).run_id
        == RunRef.create(dataset_id=ZBIOR, reports=[plan_raport, koszty]).run_id
    )


def test_przebieg_bez_raportow_jest_odrzucany() -> None:
    """Nie dałoby się powiedzieć, na jakich danych powstał wynik."""
    with pytest.raises(ValueError):
        RunRef.create(dataset_id=ZBIOR, reports=[])


def test_raport_z_obcego_zbioru_jest_odrzucany(tmp_path: Path) -> None:
    raport = load_table(zapisz_plik(tmp_path), "COST", dataset_id="inny-klient").report
    with pytest.raises(ValueError) as blad:
        RunRef.create(dataset_id=ZBIOR, reports=[raport])
    assert "inny-klient" in str(blad.value)


def test_podstawa_identyfikatora_jest_odczytywalna(tmp_path: Path) -> None:
    """Skrót sam w sobie jest ślepym zaułkiem — zapisujemy, z czego powstał."""
    run = zbuduj_przebieg(tmp_path)
    assert "content_digest" in run.input_digest
    assert run.dataset_id in run.input_digest
    assert run.inputs[0].table_name == "COST"
    assert run.inputs[0].records_accepted == 2


# --- historia wyniku -------------------------------------------------------------------


def test_historia_wyniku_przez_kolejne_przebiegi(tmp_path: Path) -> None:
    """Główny zysk z tego, że wynik nie jest kluczowany samym finding_id.

    Po finding_id widać, jak zmieniała się ta sama odpowiedź na to samo pytanie.
    """
    a = tmp_path / "a"
    b = tmp_path / "b"
    a.mkdir()
    b.mkdir()
    store = FindingStore(connect(":memory:"))

    pierwszy = zbuduj_przebieg(a)
    drugi = zbuduj_przebieg(b, KOSZTY.replace("200", "250"))
    assert pierwszy.run_id != drugi.run_id

    store.save_run(pierwszy, (zbuduj_wynik(metric_value=2.0),), WYKONANIE)
    store.save_run(
        drugi, (zbuduj_wynik(metric_value=2.0, finding="Po poprawce."),), WYKONANIE
    )

    finding_id = zbuduj_wynik().finding_id
    historia = store.history(finding_id)
    assert len(historia) == 2
    assert {run_id for run_id, _, _ in historia} == {pierwszy.run_id, drugi.run_id}
    assert [rekord.finding for _, _, rekord in historia] == [
        "Brak sygnału niekorzystnego.",
        "Po poprawce.",
    ]


def test_ten_sam_wynik_w_dwoch_przebiegach_nie_jest_duplikatem(tmp_path: Path) -> None:
    """Ten sam finding_id może wystąpić w wielu przebiegach."""
    a = tmp_path / "a"
    b = tmp_path / "b"
    a.mkdir()
    b.mkdir()
    store = FindingStore(connect(":memory:"))
    store.save_run(zbuduj_przebieg(a), (zbuduj_wynik(),), WYKONANIE)
    store.save_run(
        zbuduj_przebieg(b, KOSZTY.replace("200", "250")), (zbuduj_wynik(),), WYKONANIE
    )
    assert len(store.history(zbuduj_wynik().finding_id)) == 2


def test_pochodzenie_jest_zapisane_mimo_ze_nie_wchodzi_do_tozsamosci(
    tmp_path: Path,
) -> None:
    """source_id nie wpływa na wynik, więc jest poza skrótem — ale audyt go potrzebuje."""
    run = zbuduj_przebieg(tmp_path)
    assert run.inputs[0].source_id not in run.input_digest
    assert run.inputs[0].source_id in run.provenance


def test_inna_liczba_odrzucen_daje_inny_przebieg(tmp_path: Path) -> None:
    """Odrzucenia czyta kontrola 2 i 3, więc wpływają na obraz jakości danych."""
    a = tmp_path / "a"
    b = tmp_path / "b"
    a.mkdir()
    b.mkdir()
    z_odrzuceniem = KOSZTY + "2026-03-01,,materiały,50\n"
    assert zbuduj_przebieg(a).run_id != zbuduj_przebieg(b, z_odrzuceniem).run_id


# --- wersja tożsamości należy do kształtu krotki (DT-14) -----------------------------


def test_wersja_przebiegu_i_wyniku_sa_niezalezne() -> None:
    """Reguła z DT-14 bez testu byłaby regułą, którą ktoś złamie przy pierwszym pośpiechu.

    Krotka RunRef zmieniała się dwa razy (profile_digest, potem zestawienie odrzuceń),
    więc wersja przebiegu jest dziś "3". Krotka FindingRecord się nie zmieniła, więc jej
    wersja ZOSTAJE "1" — jedna wspólna stała unieważniałaby weryfikację rekordów, których
    zmiana w ogóle nie dotyczyła.
    """
    from xray.model.findings.identity import IDENTITY_ALGORITHM_VERSION
    from xray.store.runs import RUN_IDENTITY_VERSION

    assert RUN_IDENTITY_VERSION == "3"
    assert IDENTITY_ALGORITHM_VERSION == "1"
    assert RUN_IDENTITY_VERSION != IDENTITY_ALGORITHM_VERSION

    wynik = zbuduj_wynik()
    assert wynik.identity_algorithm_version == "1"


def test_przebieg_deklaruje_wersje_ktora_go_policzyla(tmp_path: Path) -> None:
    """Dodanie pola i podniesienie wersji weszły jedną zmianą.

    W dwóch podejściach powstałyby rekordy deklarujące starą wersję, a policzone nową
    krotką — i nic nie odróżniłoby ich później od uszkodzonych.
    """
    from xray.store.runs import RUN_IDENTITY_VERSION

    run = zbuduj_przebieg(tmp_path)
    assert run.identity_algorithm_version == RUN_IDENTITY_VERSION
    assert "profile_digest" in run.input_digest


# --- skrót profilu w tożsamości przebiegu --------------------------------------------


def test_profil_zmienia_tozsamosc_przebiegu(tmp_path: Path) -> None:
    """Sedno DT-13: plan_metrics nie rusza content_digest, więc bez profile_digest
    ten sam run_id niósłby inną treść."""
    raport = load_table(zapisz_plik(tmp_path), "COST", dataset_id=ZBIOR).report
    profil = MappingProfile.load("profiles/firma-syntetyczna.yaml")
    inny = profil.model_copy(update={"organization_timezone": "Europe/Berlin"})
    bez = RunRef.create(dataset_id=ZBIOR, reports=[raport])
    z_profilem = RunRef.create(dataset_id=ZBIOR, reports=[raport], profile=profil)
    inny_profil = RunRef.create(dataset_id=ZBIOR, reports=[raport], profile=inny)
    assert bez.run_id != z_profilem.run_id
    assert z_profilem.run_id != inny_profil.run_id


def test_przebieg_bez_profilu_jest_dopuszczalny(tmp_path: Path) -> None:
    """Brak profilu to zadeklarowany brak, nie awaria — mapowanie tożsamościowe."""
    run = zbuduj_przebieg(tmp_path)
    assert run.profile_digest is None
