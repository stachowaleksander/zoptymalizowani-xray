# Sprawdza generator firmy syntetycznej — ZOP-TECH-01 v0.1 pkt 5.5 i kryterium 8.6.
"""Testy generatora.

Najmocniejszy strażnik jest jeden: **wszystkie osiem kontroli na wszystkich pięciu
tabelach daje PASS albo not_applicable**. WARNING kontroli 6 znaczyłby niespójne nazwy,
CRITICAL kontroli 4 — zły klucz, WARNING kontroli 8 — lukę w szeregu.

Pozostałe testy powtarzają część tego, co i tak wyłapią kontrole. Trzymamy je mimo to:
kontrola powie „WARNING w kontroli 6", a test powie „generator produkuje dwa warianty
nazwy jednostki". Pierwsze wymaga śledztwa, drugie wskazuje przyczynę.
"""

import datetime as dt
from hashlib import blake2b
from pathlib import Path

import pandas as pd
import pytest

from xray.ingest import load_table
from xray.mapping import MappingProfile, apply_profile
from xray.model import TABLES, get_table
from xray.model.enums import ValidationStatus
from xray.model.tables.base import text_key_fields
from xray.synth import generate
from xray.synth.generator import (
    AVAILABLE_HOURS,
    DEFAULT_MONTHS,
    DEFAULT_RESOURCES_PER_UNIT,
    DEFAULT_UNITS,
)
from xray.synth.names import HEADERS, RECONCILED_CATEGORY
from xray.validation import ValidationContext, run_checks
from xray.validation.checks.inconsistent_names import comparison_key

ZIARNO = 20260907
PROFIL = "profiles/firma-syntetyczna.yaml"
ZBIOR = "firma-syntetyczna"

# Mała skala tam, gdzie własność nie zależy od rozmiaru — testy mają być szybkie.
MALA = {"months": 4, "units": 3, "resources_per_unit": 2, "cases_per_unit_month": 3}


@pytest.fixture(scope="module")
def zbior(tmp_path_factory) -> dict:
    """Jeden pełny zbiór w domyślnej skali, użyty przez kilka testów."""
    katalog = tmp_path_factory.mktemp("firma")
    return {"dane": generate(katalog, seed=ZIARNO), "katalog": katalog}


def wczytaj(plik: Path, tabela: str):
    """Przeprowadza plik przez profil, import i kontrole — tak jak dane klienta."""
    profil = MappingProfile.load(PROFIL)
    naglowki = (
        pd.read_excel(plik, nrows=0) if plik.suffix == ".xlsx" else pd.read_csv(plik, nrows=0)
    )
    raport_mapowania = apply_profile(profil, tabela, list(naglowki.columns))
    wynik = load_table(
        plik, tabela, dataset_id=ZBIOR, column_map=raport_mapowania.column_map
    )
    kontekst = ValidationContext(
        table=get_table(tabela),
        frame=wynik.frame,
        import_reports=(wynik.report,),
        mapping_reports=(raport_mapowania,),
    )
    return wynik, kontekst


# --- strażnik główny ------------------------------------------------------------------


def test_wszystkie_kontrole_przechodza_na_kazdej_tabeli(zbior) -> None:
    """Kryterium z pkt 5.5.4: zmienność wolno, problem nie.

    Sygnał którejkolwiek kontroli byłby błędem generatora, nie danych.
    """
    for tabela, plik in zbior["dane"].files.items():
        wynik, kontekst = wczytaj(plik, tabela)
        assert wynik.report.records_rejected == 0, tabela
        for kontrola in run_checks(kontekst):
            assert kontrola.status in (ValidationStatus.PASS, None), (
                tabela,
                kontrola.check_id,
                kontrola.basis,
            )
            if kontrola.status is None:
                assert kontrola.not_assessed_reason is not None


# --- determinizm ----------------------------------------------------------------------


def _wczytaj_surowo(sciezka: Path) -> pd.DataFrame:
    """Czyta plik bez przechodzenia przez kontrakt — do porównania samej struktury."""
    if sciezka.suffix == ".xlsx":
        return pd.read_excel(sciezka)
    return pd.read_csv(sciezka)


def skrot_pliku(sciezka: Path) -> str:
    return blake2b(sciezka.read_bytes(), digest_size=16).hexdigest()


def test_ten_sam_seed_daje_identyczne_pliki(tmp_path: Path) -> None:
    """Porównujemy skróty **zawartości plików**, nie ramek.

    Porównanie w pamięci przeszłoby także wtedy, gdyby zapis wprowadzał zależność
    od kolejności.
    """
    a = generate(tmp_path / "a", seed=ZIARNO, **MALA)
    b = generate(tmp_path / "b", seed=ZIARNO, **MALA)
    for tabela in a.files:
        assert skrot_pliku(a.files[tabela]) == skrot_pliku(b.files[tabela]), tabela


def test_inny_seed_daje_inne_dane_o_tej_samej_strukturze(tmp_path: Path) -> None:
    """Niezmienniczość, nie loteria — jedno dodatkowe ziarno wystarcza."""
    a = generate(tmp_path / "a", seed=ZIARNO, **MALA)
    b = generate(tmp_path / "b", seed=ZIARNO + 1, **MALA)
    for tabela in a.files:
        assert skrot_pliku(a.files[tabela]) != skrot_pliku(b.files[tabela]), tabela
        ramka_a = _wczytaj_surowo(a.files[tabela])
        ramka_b = _wczytaj_surowo(b.files[tabela])
        assert list(ramka_a.columns) == list(ramka_b.columns), tabela
        assert len(ramka_a) == len(ramka_b), tabela


# --- twarde ograniczenia konstrukcji --------------------------------------------------


def test_wykorzystanie_nie_przekracza_dostepnosci(zbior) -> None:
    """Nadgodziny są w rzeczywistości prawdą, ale tutaj byłyby sygnałem kontroli 7."""
    wynik, _ = wczytaj(zbior["dane"].files["RESOURCE"], "RESOURCE")
    ramka = wynik.frame
    assert (ramka["used"] <= ramka["available"]).all()
    assert (ramka["available"] == AVAILABLE_HOURS).all()


def test_brak_kwot_ujemnych(zbior) -> None:
    """Wartość ujemna byłaby sygnałem kontroli 5 (wpis B-01)."""
    for tabela, kolumny in (
        ("COST", ["amount"]),
        ("ACTIVITY", ["volume", "revenue"]),
        ("RESOURCE", ["available", "used", "cost"]),
        ("PLAN", ["target"]),
    ):
        wynik, _ = wczytaj(zbior["dane"].files[tabela], tabela)
        for kolumna in kolumny:
            assert (wynik.frame[kolumna] >= 0).all(), (tabela, kolumna)


def test_nazwy_nie_sprowadzaja_sie_do_wspolnego_klucza(zbior) -> None:
    """Dwa warianty jednej nazwy zapaliłyby kontrolę 6 — tu wskazujemy przyczynę."""
    for tabela, plik in zbior["dane"].files.items():
        wynik, _ = wczytaj(plik, tabela)
        for pole in text_key_fields(TABLES[tabela]):
            wartosci = sorted(set(wynik.frame[pole].dropna().astype(str)))
            klucze = {comparison_key(w) for w in wartosci}
            assert len(klucze) == len(wartosci), (tabela, pole)


def test_szereg_okresowy_jest_ciagly(zbior) -> None:
    """24 kolejne miesiące bez luk w każdej tabeli okresowej."""
    for tabela in ("ACTIVITY", "COST", "RESOURCE", "PLAN"):
        wynik, _ = wczytaj(zbior["dane"].files[tabela], tabela)
        miesiace = sorted({d.replace(day=1) for d in wynik.frame["date"]})
        assert len(miesiace) == DEFAULT_MONTHS, tabela
        okresy = pd.PeriodIndex(pd.to_datetime(pd.Series(miesiace)), freq="M")
        assert list(okresy) == list(pd.period_range(okresy.min(), okresy.max(), freq="M"))


# --- PROCESS: następstwo etapów i granica miesiąca ------------------------------------


def test_etap_konczy_sie_nie_wczesniej_niz_zaczyna(zbior) -> None:
    """Żadna z ośmiu kontroli tego nie sprawdza, więc musi być testem."""
    wynik, _ = wczytaj(zbior["dane"].files["PROCESS"], "PROCESS")
    assert (wynik.frame["end"] >= wynik.frame["start"]).all()


def test_etapy_nastepuja_po_sobie_w_kolejnosci(zbior) -> None:
    """Odwrócona kolejność etapów byłaby dziś niewidoczna — klucz to case_id + stage —
    a ZOP-XR-PROC-01 znalazłaby ją jako pierwszą rzecz."""
    from xray.synth.names import STAGES

    wynik, _ = wczytaj(zbior["dane"].files["PROCESS"], "PROCESS")
    ramka = wynik.frame.copy()
    ramka["kolejnosc"] = ramka["stage"].map({e: i for i, e in enumerate(STAGES)})
    for _, sprawa in ramka.groupby("case_id", sort=True):
        uporzadkowana = sprawa.sort_values("kolejnosc")
        starty = list(uporzadkowana["start"])
        konce = list(uporzadkowana["end"])
        assert starty == sorted(starty)
        for poprzedni_koniec, kolejny_start in zip(konce, starty[1:], strict=False):
            assert kolejny_start >= poprzedni_koniec


def test_kazdy_miesiac_ma_sprawe_przekraczajaca_granice(zbior) -> None:
    """Gwarancja konstrukcji, nie ziarna.

    Własność probabilistyczna zanikłaby po cichu przy zmianie parametrów; wtedy
    rozróżnienie z A-01 przestałoby być ćwiczone, a test wyglądałby na chwiejny.
    """
    wynik, _ = wczytaj(zbior["dane"].files["PROCESS"], "PROCESS")
    ramka = wynik.frame
    po_sprawie = ramka.groupby("case_id", sort=True).agg(
        poczatek=("start", "min"), koniec=("end", "max")
    )
    przekraczajace = po_sprawie[
        po_sprawie["poczatek"].dt.to_period("M") != po_sprawie["koniec"].dt.to_period("M")
    ]
    miesiace_startu = sorted(set(przekraczajace["poczatek"].dt.to_period("M")))
    wszystkie_miesiace = sorted(set(po_sprawie["poczatek"].dt.to_period("M")))
    assert miesiace_startu == wszystkie_miesiace


def test_miesiace_startow_i_koncow_roznia_sie(zbior) -> None:
    """To jest rozróżnienie z A-01, i ma być widoczne na prawdziwych danych.

    Starty obejmują 24 miesiące, końce 25 — bo sprawa z ostatniego miesiąca przelewa się
    poza horyzont. To obserwacja, nie sygnał: kontrola 8 dla tabeli zdarzeniowej ma sufit
    PASS.
    """
    _, kontekst = wczytaj(zbior["dane"].files["PROCESS"], "PROCESS")
    wynik = next(k for k in run_checks(kontekst) if k.check_id == "TECH01-VAL-08")
    miary = {o.measure: o.value for o in wynik.observations}
    assert miary["months_with_stage_starts"] == float(DEFAULT_MONTHS)
    assert miary["months_with_stage_ends"] == float(DEFAULT_MONTHS + 1)
    assert wynik.status is ValidationStatus.PASS


# --- uzgodnienie RESOURCE ↔ COST ------------------------------------------------------


def test_kategoria_kosztowa_uzgadnia_sie_z_suma_zasobow(zbior) -> None:
    """Brak uzgodnienia byłby zaszytym problemem: MGT-01 znalazłaby unreconciled.

    Porównanie **dokładne**, bez tolerancji — kwoty są pełnymi złotymi, a liczby całkowite
    do 2^53 sumują się w float64 bez straty. Tolerancja uzgodnienia jest pytaniem
    metodologicznym do MGT-01 (wpis DT-01) i nie wolno jej tu wyprzedzić.
    """
    koszty, _ = wczytaj(zbior["dane"].files["COST"], "COST")
    zasoby, _ = wczytaj(zbior["dane"].files["RESOURCE"], "RESOURCE")

    suma_zasobow = zasoby.frame.groupby(["date", "unit"], sort=True)["cost"].sum()
    kategoria = koszty.frame[koszty.frame["category"] == RECONCILED_CATEGORY]
    zadeklarowane = kategoria.set_index(["date", "unit"])["amount"].sort_index()

    assert len(zadeklarowane) == len(suma_zasobow)
    assert (zadeklarowane == suma_zasobow.sort_index()).all()


def test_kwoty_sa_pelnymi_zlotymi(zbior) -> None:
    """Warunek, bez którego uzgodnienie wymagałoby tolerancji."""
    koszty, _ = wczytaj(zbior["dane"].files["COST"], "COST")
    assert (koszty.frame["amount"] % 1 == 0).all()


# --- plan bez kierunku ----------------------------------------------------------------


def test_plan_wypada_raz_nad_raz_pod_wykonaniem(zbior) -> None:
    """Plan powstający niezależnie od wykonania byłby systematycznie po jednej stronie —
    luka planistyczna zaszyta w danych, którą FIN-01 znalazłby w pierwszym uruchomieniu."""
    plan, _ = wczytaj(zbior["dane"].files["PLAN"], "PLAN")
    koszty, _ = wczytaj(zbior["dane"].files["COST"], "COST")

    wykonanie = koszty.frame.groupby(["date", "unit"], sort=True)["amount"].sum()
    cel = (
        plan.frame[plan.frame["metric"] == "Koszt calkowity"]
        .set_index(["date", "unit"])["target"]
        .sort_index()
    )
    roznica = cel - wykonanie.sort_index()
    assert (roznica > 0).any(), "plan nigdy nie jest powyżej wykonania"
    assert (roznica < 0).any(), "plan nigdy nie jest poniżej wykonania"


# --- nagłówki i formaty ---------------------------------------------------------------


def test_zaden_naglowek_nie_jest_nazwa_pola_kontraktu() -> None:
    """Gdyby był, mapowanie w tym miejscu przestałoby czegokolwiek dowodzić."""
    for tabela, mapa in HEADERS.items():
        pola = set(TABLES[tabela].model_fields)
        for pole, naglowek in mapa.items():
            assert naglowek not in pola, (tabela, pole, naglowek)


def test_data_z_xlsx_wraca_jako_data(zbior) -> None:
    """Ścieżka numeru seryjnego arkusza — tam siedział błąd z klasyfikacją typu pola."""
    assert zbior["dane"].files["COST"].suffix == ".xlsx"
    wynik, _ = wczytaj(zbior["dane"].files["COST"], "COST")
    assert isinstance(wynik.frame["date"].iloc[0], dt.date)
    assert not isinstance(wynik.frame["date"].iloc[0], dt.datetime)


def test_kolumna_spoza_kontraktu_jest_zglaszana(zbior) -> None:
    """Bez niej element „kolumny niezmapowane" raportu mapowania nie byłby ćwiczony."""
    wynik, _ = wczytaj(zbior["dane"].files["RESOURCE"], "RESOURCE")
    assert wynik.report.dropped_columns == ("Kod_MPK",)


# --- skala z karty --------------------------------------------------------------------


def test_domyslna_skala_odpowiada_karcie(zbior) -> None:
    """Pkt 5.5.1–5.5.2: około 100 zasobów, 5 jednostek, 24 miesiące, wszystkie tabele."""
    dane = zbior["dane"]
    assert dane.months == 24
    assert len(dane.units) == DEFAULT_UNITS == 5
    assert DEFAULT_RESOURCES_PER_UNIT * DEFAULT_UNITS == 100
    assert set(dane.files) == set(TABLES)


def test_generator_odmawia_wiecej_jednostek_niz_zna(tmp_path: Path) -> None:
    """Nazwy pochodzą z kanonicznego słownika i nie są dogenerowywane."""
    with pytest.raises(ValueError) as blad:
        parametry = {k: v for k, v in MALA.items() if k != "units"}
        generate(tmp_path, seed=ZIARNO, units=99, **parametry)
    assert "słownik" in str(blad.value)
