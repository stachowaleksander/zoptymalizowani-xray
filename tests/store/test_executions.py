# Sprawdza rozdzielenie run_id od proweniencji wykonania (wpis DT-21) oraz zakres odcisku
# kodu i środowiska (wpis DT-22).
"""Testy wykonań przebiegu.

Pierwsza część sprawdza invariant wprost, wiersz po wierszu z tabeli w
``xray.store.executions``. Odciski są tam zadeklarowane jawnie: test ma kontrolować, czy dwa
wykonania mają ten sam odcisk, a nie zależeć od tego, co akurat zawiera środowisko.

Druga część sprawdza, jak odcisk powstaje w bieżącym środowisku.
"""

import datetime as dt
import sqlite3
from pathlib import Path

import pytest

from xray.ingest import load_table
from xray.model import FindingRecord, LogicalStatus, PeriodRef, ScopeRef
from xray.store import (
    ConflictingRun,
    ExecutionRef,
    FindingStore,
    FingerprintStatus,
    RunRef,
    connect,
)
from xray.store.executions import (
    code_manifest,
    compute_fingerprint,
    git_description,
    runtime_distributions,
)

ZBIOR = "klient-testowy"
ZAKRES = ScopeRef(scope_label="cała firma")
OKRES = PeriodRef(period_start=dt.date(2026, 1, 1), period_end=dt.date(2026, 1, 31))


def wykonanie(odcisk: str | None) -> ExecutionRef:
    """Wykonanie z odciskiem zadeklarowanym w teście; ``None`` = odcisk nieznany."""
    return ExecutionRef(
        execution_fingerprint=odcisk,
        fingerprint_status=(
            FingerprintStatus.KNOWN if odcisk is not None else FingerprintStatus.UNKNOWN
        ),
        fingerprint_basis={"opis": "odcisk zadeklarowany w teście"},
        code_provenance={"git_status": "unavailable", "reason": "test jednostkowy"},
    )


def wynik(metric_value: float = 1.0) -> FindingRecord:
    return FindingRecord.create(
        test_id="NOOP-01",
        scope=ZAKRES,
        period=OKRES,
        status=LogicalStatus.NO_ADVERSE_SIGNAL,
        finding="Liczba wierszy.",
        metric_value=metric_value,
    )


@pytest.fixture
def przebieg(tmp_path: Path) -> RunRef:
    sciezka = tmp_path / "koszty.csv"
    sciezka.write_text(
        "date,unit,category,amount\n2026-01-01,Dział A,wynagrodzenia,100\n", encoding="utf-8"
    )
    raport = load_table(sciezka, "COST", dataset_id=ZBIOR).report
    return RunRef.create(dataset_id=ZBIOR, reports=[raport])


@pytest.fixture
def magazyn() -> FindingStore:
    return FindingStore(connect(":memory:"))


# --- invariant: ten sam run_id -----------------------------------------------------------


def test_ten_sam_odcisk_i_ta_sama_tresc_to_brak_operacji(
    magazyn: FindingStore, przebieg: RunRef
) -> None:
    assert magazyn.save_run(przebieg, (wynik(),), wykonanie("FPR-a")) is True
    assert magazyn.save_run(przebieg, (wynik(),), wykonanie("FPR-a")) is False
    assert len(magazyn.executions(przebieg.run_id)) == 1
    assert len(magazyn.history(wynik().finding_id)) == 1


def test_ten_sam_odcisk_i_inna_tresc_to_sprzecznosc(
    magazyn: FindingStore, przebieg: RunRef
) -> None:
    """Ten sam przebieg, kod i środowisko, inny wynik: przepływ nie jest deterministyczny."""
    magazyn.save_run(przebieg, (wynik(1.0),), wykonanie("FPR-a"))
    with pytest.raises(ConflictingRun) as blad:
        magazyn.save_run(przebieg, (wynik(2.0),), wykonanie("FPR-a"))
    assert "FPR-a" in str(blad.value)
    # Transakcja: sprzeczne wykonanie nie zostawia śladu częściowego.
    assert len(magazyn.executions(przebieg.run_id)) == 1
    assert [r.metric_value for _, _, r in magazyn.history(wynik().finding_id)] == [1.0]


def test_sprzecznosc_rozstrzyga_schemat_a_nie_warunek_w_kodzie(przebieg: RunRef) -> None:
    """Ograniczenie działa także z pominięciem FindingStore: invariant jest w strukturze."""
    polaczenie = connect(":memory:")
    FindingStore(polaczenie).save_run(przebieg, (wynik(1.0),), wykonanie("FPR-a"))
    with pytest.raises(sqlite3.IntegrityError) as blad:
        polaczenie.execute(
            "INSERT INTO executions (execution_id, run_id, execution_fingerprint, "
            "fingerprint_status, result_digest, fingerprint_basis, code_provenance, "
            "input_provenance) VALUES ('EXE-obejscie', ?, 'FPR-a', 'known', 'RSET-inny', "
            "'{}', '{}', '{}')",
            (przebieg.run_id,),
        )
    assert blad.value.sqlite_errorname == "SQLITE_CONSTRAINT_UNIQUE"


def test_inny_odcisk_i_inna_tresc_to_dwa_wykonania(
    magazyn: FindingStore, przebieg: RunRef
) -> None:
    assert magazyn.save_run(przebieg, (wynik(1.0),), wykonanie("FPR-a")) is True
    assert magazyn.save_run(przebieg, (wynik(2.0),), wykonanie("FPR-b")) is True
    assert len(magazyn.executions(przebieg.run_id)) == 2


def test_inny_odcisk_i_ta_sama_tresc_to_dwa_wykonania(
    magazyn: FindingStore, przebieg: RunRef
) -> None:
    assert magazyn.save_run(przebieg, (wynik(1.0),), wykonanie("FPR-a")) is True
    assert magazyn.save_run(przebieg, (wynik(1.0),), wykonanie("FPR-b")) is True
    assert len(magazyn.executions(przebieg.run_id)) == 2


def test_historia_pokazuje_wszystkie_wykonania(
    magazyn: FindingStore, przebieg: RunRef
) -> None:
    magazyn.save_run(przebieg, (wynik(1.0),), wykonanie("FPR-a"))
    magazyn.save_run(przebieg, (wynik(1.0),), wykonanie("FPR-b"))
    magazyn.save_run(przebieg, (wynik(2.0),), wykonanie("FPR-c"))

    historia = magazyn.history(wynik().finding_id)
    assert len(historia) == 3
    assert {run_id for run_id, _, _ in historia} == {przebieg.run_id}
    assert len({execution_id for _, execution_id, _ in historia}) == 3
    assert [r.metric_value for _, _, r in historia] == [1.0, 1.0, 2.0]
    assert [
        w.execution.execution_fingerprint for w in magazyn.executions(przebieg.run_id)
    ] == ["FPR-a", "FPR-b", "FPR-c"]


# --- odcisk nieznany (D5) ---------------------------------------------------------------


def test_nieznany_odcisk_nie_zglasza_sprzecznosci_i_mowi_to_wprost(
    magazyn: FindingStore, przebieg: RunRef
) -> None:
    """Wykonania o nieznanym odcisku współistnieją. Kontrola determinizmu jest dla nich
    wyłączona — i każdy rekord to mówi, zamiast udawać, że odcisk jest znany."""
    assert magazyn.save_run(przebieg, (wynik(1.0),), wykonanie(None)) is True
    assert magazyn.save_run(przebieg, (wynik(2.0),), wykonanie(None)) is True
    zapisane = magazyn.executions(przebieg.run_id)
    assert [w.execution.fingerprint_status for w in zapisane] == [
        FingerprintStatus.UNKNOWN,
        FingerprintStatus.UNKNOWN,
    ]
    assert all(w.execution.execution_fingerprint is None for w in zapisane)


def test_nieznany_odcisk_z_ta_sama_trescia_to_brak_operacji(
    magazyn: FindingStore, przebieg: RunRef
) -> None:
    assert magazyn.save_run(przebieg, (wynik(),), wykonanie(None)) is True
    assert magazyn.save_run(przebieg, (wynik(),), wykonanie(None)) is False


def test_status_odcisku_nie_rozjezdza_sie_z_odciskiem() -> None:
    """Odcisku nie zmyślamy i nie ukrywamy; podstawa jest wymagana."""
    with pytest.raises(ValueError):
        ExecutionRef(
            execution_fingerprint="FPR-a",
            fingerprint_status=FingerprintStatus.UNKNOWN,
            fingerprint_basis={"opis": "x"},
            code_provenance={},
        )
    with pytest.raises(ValueError):
        ExecutionRef(
            execution_fingerprint=None,
            fingerprint_status=FingerprintStatus.KNOWN,
            fingerprint_basis={"opis": "x"},
            code_provenance={},
        )
    with pytest.raises(ValueError):
        ExecutionRef(
            execution_fingerprint="FPR-a",
            fingerprint_status=FingerprintStatus.KNOWN,
            fingerprint_basis={},
            code_provenance={},
        )


# --- czas i odczyt ------------------------------------------------------------------------


def test_czas_nie_wchodzi_do_identyfikatora_wykonania() -> None:
    wczesniej = wykonanie("FPR-a").model_copy(update={"executed_at": dt.datetime(2026, 1, 1)})
    pozniej = wykonanie("FPR-a").model_copy(update={"executed_at": dt.datetime(2026, 9, 14)})
    assert wczesniej.execution_id("RUN-x", "RSET-y") == pozniej.execution_id("RUN-x", "RSET-y")


def test_load_run_nie_wybiera_wykonania_przy_wielu(
    magazyn: FindingStore, przebieg: RunRef
) -> None:
    """Wybór jednego z kilku wykonań byłby zgadywaniem."""
    magazyn.save_run(przebieg, (wynik(1.0),), wykonanie("FPR-a"))
    magazyn.save_run(przebieg, (wynik(2.0),), wykonanie("FPR-b"))
    with pytest.raises(ValueError) as blad:
        magazyn.load_run(przebieg.run_id)
    assert "zgadywaniem" in str(blad.value)
    drugie = magazyn.executions(przebieg.run_id)[1]
    assert magazyn.load_execution(drugie.execution_id) == (wynik(2.0),)


def test_wykonanie_odczytane_zachowuje_podstawe_i_czas(
    magazyn: FindingStore, przebieg: RunRef
) -> None:
    zapisane = wykonanie("FPR-a").model_copy(
        update={"executed_at": dt.datetime(2026, 9, 14, 10, 30)}
    )
    magazyn.save_run(przebieg, (wynik(),), zapisane)
    assert magazyn.executions(przebieg.run_id)[0].execution == zapisane


# --- jak powstaje odcisk ------------------------------------------------------------------


def test_odcisk_nie_zalezy_od_czasu_ani_od_ponownego_liczenia() -> None:
    """Pułapka z DT-21: gdyby do odcisku wszedł czas, człon „ten sam odcisk" nigdy by się
    nie ziścił, a kontrola determinizmu cicho przestałaby działać."""
    a = ExecutionRef.capture(executed_at=dt.datetime(2026, 1, 1))
    b = ExecutionRef.capture(executed_at=dt.datetime(2026, 9, 14))
    assert a.fingerprint_status is FingerprintStatus.KNOWN
    assert a.execution_fingerprint == b.execution_fingerprint
    assert compute_fingerprint()[0] == a.execution_fingerprint


def _pakiet(katalog: Path, pliki: dict[str, bytes]) -> Path:
    for wzgledna, tresc in pliki.items():
        sciezka = katalog / wzgledna
        sciezka.parent.mkdir(parents=True, exist_ok=True)
        sciezka.write_bytes(tresc)
    return katalog


def test_manifest_kodu_nie_zalezy_od_polozenia_katalogu(tmp_path: Path) -> None:
    """D4a: ścieżka bezwzględna zmieniałaby odcisk po sklonowaniu repozytorium gdzie indziej."""
    pliki = {"__init__.py": b"", "store/runs.py": b"x = 1\n"}
    a = _pakiet(tmp_path / "klon_a" / "xray", pliki)
    b = _pakiet(tmp_path / "gdzies" / "indziej" / "xray", pliki)
    assert code_manifest(a) == code_manifest(b)
    assert [s for s, _ in code_manifest(a)] == ["__init__.py", "store/runs.py"]


def test_manifest_kodu_bierze_wylacznie_pliki_py_spoza_pycache(tmp_path: Path) -> None:
    """D4b."""
    katalog = _pakiet(
        tmp_path / "xray",
        {
            "m.py": b"a = 1\n",
            "__pycache__/m.cpython-313.pyc": b"\x00",
            "__pycache__/stary.py": b"b = 2\n",
            "notatki.txt": b"tekst",
        },
    )
    assert [s for s, _ in code_manifest(katalog)] == ["m.py"]


def test_konce_linii_nie_sa_normalizowane(tmp_path: Path) -> None:
    """DT-22: kod tożsamości nie normalizuje końców linii — inne bajty to inny kod.

    LF w drzewie roboczym zapewnia ``.gitattributes`` (``*.py text eol=lf``), a nie ta
    funkcja: normalizacja tutaj byłaby drugą definicją „tego samego kodu".
    """
    unix = code_manifest(_pakiet(tmp_path / "a", {"m.py": b"a = 1\n"}))
    windows = code_manifest(_pakiet(tmp_path / "b", {"m.py": b"a = 1\r\n"}))
    assert unix != windows


def test_zaden_plik_odcisku_nie_ma_konca_linii_crlf() -> None:
    """Strażnik: pliki, z których liczony jest odcisk, nie zawierają ``\\r\\n``.

    ``.gitattributes`` (``*.py text eol=lf``) gwarantuje treść **przy checkoucie**, a nie
    przy zapisie z narzędzia. Odcisk czyta bajty z dysku, więc CRLF zapisany po checkoucie
    — przez edytor, formatter albo skrypt — zmienia odcisk, a git tego nie pokaże: porównuje
    treść po normalizacji do LF. Sprawdzone 2026-09-14: ``git diff`` jest pusty od razu,
    a po pierwszym ``git add`` także ``git status`` jest czysty, choć na dysku zostaje CRLF
    (``git ls-files --eol``: ``i/lf w/crlf``). Ten sam commit dawałby wtedy dwa odciski,
    czyli dwa legalne wykonania zamiast kontroli determinizmu (wpis DT-22).

    Lista plików pochodzi z ``code_files`` — tej samej funkcji, z której ``code_manifest``
    liczy odcisk. Druga, równoległa lista mogłaby się z nim rozjechać.
    """
    from xray.store.executions import code_files, package_dir

    pliki = code_files(package_dir())
    assert pliki, "nie znaleziono plików kodu pakietu"
    z_crlf = sorted(
        wzgledna for wzgledna, sciezka in pliki.items() if b"\r\n" in sciezka.read_bytes()
    )
    assert z_crlf == [], f"pliki z CRLF zmieniają odcisk wykonania: {z_crlf}"


def test_katalog_bez_kodu_nie_daje_znanego_manifestu(tmp_path: Path) -> None:
    (tmp_path / "pusty").mkdir()
    assert code_manifest(tmp_path / "pusty") is None
    assert code_manifest(tmp_path / "nie_istnieje") is None


def test_do_odcisku_wchodzi_tylko_domkniecie_zaleznosci_runtime() -> None:
    """D4c: ``pip install ruff`` nie może zmieniać odcisku.

    Im więcej wchodzi do odcisku, tym słabsza kontrola sprzeczności — dwa różne wyniki
    z tych samych danych stałyby się dwoma legalnymi wykonaniami.
    """
    _, podstawa = compute_fingerprint()
    runtime = {nazwa for nazwa, _ in podstawa["runtime_distributions"]}
    pozostale = {nazwa for nazwa, _ in podstawa["other_distributions"]}
    assert {"pandas", "pydantic", "pydantic-core", "pyyaml", "packaging"} <= runtime
    assert {"pytest", "ruff"}.isdisjoint(runtime)
    assert {"pytest", "ruff"} <= pozostale
    assert podstawa["runtime_requirements_source"] == "pyproject.toml"


def test_do_odcisku_wchodzi_domkniecie_przechodnie_z_wersjami_z_instalacji() -> None:
    """Z-4: zależności pośrednie zmieniają wynik tak samo jak deklarowane wprost.

    numpy i python-dateutil (pod pandas), six (pod python-dateutil), et-xmlfile (pod
    openpyxl), pydantic-core (pod pydantic) — i tzdata, bo według jego reguł ingest
    przelicza znaczniki czasu (DT-05). Nazwy zakresu pochodzą z pyproject.toml, wersje
    z faktycznie zainstalowanego środowiska.
    """
    import importlib.metadata as md

    _, podstawa = compute_fingerprint()
    wersje = dict(podstawa["runtime_distributions"])
    for nazwa in ("numpy", "python-dateutil", "six", "et-xmlfile", "pydantic-core", "tzdata"):
        assert wersje.get(nazwa) == md.version(nazwa), nazwa


def test_zaleznosci_dodatkow_nie_wchodza_do_domkniecia() -> None:
    """pandas deklaruje hypothesis wyłącznie dla dodatku „test"."""
    wersje, brakujace = runtime_distributions(["pandas"])
    nazwy = {nazwa for nazwa, _ in wersje}
    assert {"pandas", "numpy"} <= nazwy
    assert "hypothesis" not in nazwy
    assert "hypothesis" not in brakujace


def test_niezainstalowane_wymaganie_jest_nazwane_a_nie_pominiete() -> None:
    _, brakujace = runtime_distributions(["pakiet-ktorego-nie-ma==1.0"])
    assert brakujace == ("pakiet-ktorego-nie-ma",)


def test_podstawa_odcisku_nie_niesie_sciezek_bezwzglednych() -> None:
    _, podstawa = compute_fingerprint()
    sciezki = [s for s, _ in podstawa["code_files"]]
    assert "store/executions.py" in sciezki
    assert not any(":" in s or s.startswith("/") for s in sciezki)


def test_git_niedostepny_jest_opisany_a_nie_zmyslony(tmp_path: Path) -> None:
    assert git_description(None)["git_status"] == "unavailable"
    opis = git_description(tmp_path)  # katalog poza repozytorium
    assert opis["git_status"] == "unavailable"
    assert "head_commit" not in opis
