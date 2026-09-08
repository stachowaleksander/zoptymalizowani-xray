# Sprawdza produkt 6 z ZOP-TECH-01 v0.1 rozdz. 7 — pełny przebieg na firmie syntetycznej.
"""Testy demonstracji.

Każda warstwa była testowana osobno; tu sprawdzamy, że łańcuch **spina się w całość**:
generator → mapowanie → import → osiem kontroli → NOOP-01 → magazyn → odczyt.

Testy pilnują też trzech decyzji, które nie są kosmetyczne: demonstracja generuje dane
zamiast je czytać, przebieg obejmuje pięć tabel, a raport mapowania trafia na ekran.
"""

from pathlib import Path

from xray.demo import opisz, run_demo
from xray.demo.run import DATASET_ID, DEMO_SEED
from xray.model import LogicalStatus, table_names
from xray.model.enums import ValidationStatus
from xray.store.runs import RUN_IDENTITY_VERSION
from xray.validation import registered_check_ids

# Mała skala: własności sprawdzane niżej nie zależą od rozmiaru zbioru.
MALA = {"months": 4, "units": 3, "resources_per_unit": 2, "cases_per_unit_month": 3}


def test_przeplyw_spina_sie_na_pieciu_tabelach(tmp_path: Path) -> None:
    """Kryterium odbioru 8.5: działająca struktura FINDINGS, nie sama definicja."""
    wynik = run_demo(tmp_path, **MALA)
    assert {t.table_name for t in wynik.tables} == set(table_names())
    assert all(t.load.report.records_rejected == 0 for t in wynik.tables)
    assert wynik.written is True
    assert wynik.stored == wynik.findings


def test_demo_generuje_dane_zamiast_je_czytac(tmp_path: Path) -> None:
    """Czytanie z data/ dałoby demonstrację, która u kogoś innego nie ruszy."""
    wynik = run_demo(tmp_path, **MALA)
    for plik in wynik.dataset.files.values():
        assert plik.exists()
        assert plik.is_relative_to(tmp_path)
    assert wynik.dataset.seed == DEMO_SEED


def test_dane_przechodza_przez_ingest(tmp_path: Path) -> None:
    """Kryterium 8.1: pliki wczytywane bez ingerencji w kod przy każdym uruchomieniu."""
    wynik = run_demo(tmp_path, **MALA)
    assert wynik.dataset.files["COST"].suffix == ".xlsx"
    assert wynik.dataset.files["ACTIVITY"].suffix == ".csv"
    for tabela in wynik.tables:
        assert tabela.load.report.source.dataset_id == DATASET_ID
        assert tabela.load.report.content_digest


def test_wszystkie_kontrole_przechodza(tmp_path: Path) -> None:
    """Sygnał którejkolwiek kontroli byłby błędem generatora, nie danych (pkt 5.5.4)."""
    wynik = run_demo(tmp_path, **MALA)
    for tabela in wynik.tables:
        assert len(tabela.checks) == len(registered_check_ids()), tabela.table_name
        for kontrola in tabela.checks:
            assert kontrola.status in (ValidationStatus.PASS, None), (
                tabela.table_name,
                kontrola.check_id,
                kontrola.basis,
            )


# --- jeden przebieg na pięciu tabelach ------------------------------------------------


def test_przebieg_obejmuje_wszystkie_piec_tabel(tmp_path: Path) -> None:
    """Pierwsze miejsce, gdzie profile_digest i wersja przebiegu działają end-to-end."""
    wynik = run_demo(tmp_path, **MALA)
    assert len(wynik.run.inputs) == len(table_names())
    assert {w.table_name for w in wynik.run.inputs} == set(table_names())


def test_profil_wchodzi_do_tozsamosci_przebiegu(tmp_path: Path) -> None:
    wynik = run_demo(tmp_path, **MALA)
    assert wynik.run.profile_digest is not None
    assert wynik.run.profile_digest.startswith("PRF-")


def test_wersja_tozsamosci_jest_per_rodzaj_rekordu(tmp_path: Path) -> None:
    """Reguła z DT-14, sprawdzona na prawdziwym przebiegu, nie tylko jednostkowo."""
    wynik = run_demo(tmp_path, **MALA)
    assert wynik.run.identity_algorithm_version == RUN_IDENTITY_VERSION == "2"
    assert wynik.findings[0].identity_algorithm_version == "1"


# --- raport mapowania na ekranie ------------------------------------------------------


def test_ogloszenie_o_planie_trafia_na_ekran(tmp_path: Path) -> None:
    """Ogłoszenie, którego się nie drukuje, nie jest ogłoszeniem.

    Ta sama racja, dla której time_basis_used zostaje w wyniku kontroli 8.
    """
    tekst = opisz(run_demo(tmp_path, **MALA))
    assert "plan_budget" in tekst
    assert "B-04" in tekst


def test_kolumna_spoza_kontraktu_widoczna_w_opisie(tmp_path: Path) -> None:
    wynik = run_demo(tmp_path, **MALA)
    assert wynik.table("RESOURCE").mapping.unmapped_columns == ("Kod_MPK",)
    assert "Kod_MPK" in opisz(wynik)


def test_opis_wymienia_kazda_tabele_i_kazda_kontrole(tmp_path: Path) -> None:
    tekst = opisz(run_demo(tmp_path, **MALA))
    for tabela in table_names():
        assert tabela in tekst
    assert "1:PASS" in tekst
    assert "run_id" in tekst and "finding_id" in tekst and "profile_digest" in tekst


def test_rozroznienie_z_a01_widoczne_w_opisie(tmp_path: Path) -> None:
    """Różnica miesięcy startów i końców ma być na ekranie, a nie tylko w teście."""
    tekst = opisz(run_demo(tmp_path, **MALA))
    assert "months_with_stage_starts" in tekst
    assert "months_with_stage_ends" in tekst
    assert "time_basis_used" in tekst


# --- wynik diagnostyczny --------------------------------------------------------------


def test_noop01_nie_niesie_tresci_metodologicznej(tmp_path: Path) -> None:
    finding = run_demo(tmp_path, **MALA).findings[0]
    assert finding.status is LogicalStatus.NO_ADVERSE_SIGNAL
    assert finding.next_tests == ()
    assert finding.gap is None
    assert finding.reference is None
    assert finding.confidence_score is None
    assert finding.confidence_class is None


def test_dwa_przebiegi_daja_ten_sam_wynik(tmp_path: Path) -> None:
    """Zasada 3, na dwóch niezależnych katalogach."""
    pierwszy = tmp_path / "a"
    drugi = tmp_path / "b"
    pierwszy.mkdir()
    drugi.mkdir()
    a = run_demo(pierwszy, **MALA)
    b = run_demo(drugi, **MALA)
    assert a.run.run_id == b.run.run_id
    assert a.findings == b.findings
    assert a.run.profile_digest == b.run.profile_digest
