# Sprawdza odczyt XLSX i CSV oraz raport importu wobec ZOP-TECH-01 v0.1 pkt 5.1,
# kryteriów odbioru 8.1 i 8.4 oraz zasad 3 i 4 z CLAUDE.md.
"""Testy importu.

Sprawdzają trzy rzeczy naraz: że plik da się wczytać bez ingerencji w kod, że odrzucony
wiersz nie znika po cichu i że ślad prowadzi od identyfikatora wiersza do konkretnego
wiersza w pliku klienta.
"""

import datetime as dt
from pathlib import Path

import pandas as pd
import pytest

from xray.ingest import load_table

ZBIOR = "firma-syntetyczna"

POPRAWNE = {
    "date": ["2026-01-01", "2026-02-01", "2026-03-01"],
    "unit": ["Dział A", "Dział A", "Dział B"],
    "category": ["wynagrodzenia", "materiały", "wynagrodzenia"],
    "amount": ["125400.50", "8200", "99000"],
}


@pytest.fixture
def csv_poprawny(tmp_path: Path) -> Path:
    sciezka = tmp_path / "koszty.csv"
    pd.DataFrame(POPRAWNE).to_csv(sciezka, index=False, encoding="utf-8")
    return sciezka


@pytest.fixture
def xlsx_poprawny(tmp_path: Path) -> Path:
    sciezka = tmp_path / "koszty.xlsx"
    pd.DataFrame(
        {
            "date": [dt.date(2026, 1, 1), dt.date(2026, 2, 1), dt.date(2026, 3, 1)],
            "unit": ["Dział A", "Dział A", "Dział B"],
            "category": ["wynagrodzenia", "materiały", "wynagrodzenia"],
            "amount": [125400.50, 8200.0, 99000.0],
        }
    ).to_excel(sciezka, index=False)
    return sciezka


# --- odczyt obu formatów -------------------------------------------------------------


def test_csv_wczytuje_sie_bez_ingerencji_w_kod(csv_poprawny: Path) -> None:
    """Kryterium odbioru 8.1."""
    wynik = load_table(csv_poprawny, "COST", dataset_id=ZBIOR)
    assert wynik.report.records_accepted == 3
    assert wynik.report.records_rejected == 0
    assert list(wynik.frame.columns) == ["date", "unit", "category", "amount"]


def test_xlsx_wczytuje_sie_bez_ingerencji_w_kod(xlsx_poprawny: Path) -> None:
    wynik = load_table(xlsx_poprawny, "COST", dataset_id=ZBIOR)
    assert wynik.report.records_accepted == 3
    assert wynik.frame["amount"].tolist() == [125400.50, 8200.0, 99000.0]


def test_oba_formaty_daja_te_same_dane(csv_poprawny: Path, xlsx_poprawny: Path) -> None:
    """Ta sama treść w dwóch formatach ma dać ten sam wynik w kontrakcie."""
    z_csv = load_table(csv_poprawny, "COST", dataset_id=ZBIOR).frame.reset_index(drop=True)
    z_xlsx = load_table(xlsx_poprawny, "COST", dataset_id=ZBIOR).frame.reset_index(drop=True)
    pd.testing.assert_frame_equal(z_csv, z_xlsx)


def test_nieobslugiwane_rozszerzenie_daje_czytelny_blad(tmp_path: Path) -> None:
    plik = tmp_path / "dane.json"
    plik.write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError) as blad:
        load_table(plik, "COST", dataset_id=ZBIOR)
    assert "XLSX" in str(blad.value)


# --- numer seryjny daty z arkusza ----------------------------------------------------


def test_numer_seryjny_z_xlsx_jest_przeliczany(tmp_path: Path) -> None:
    """Konwersja należy do ingest/, bo tylko tu wiadomo, że wartość przyszła z arkusza."""
    sciezka = tmp_path / "serial.xlsx"
    pd.DataFrame(
        {
            "date": [46023],  # 2026-01-01 w systemie 1900
            "unit": ["Dział A"],
            "category": ["wynagrodzenia"],
            "amount": [100.0],
        }
    ).to_excel(sciezka, index=False)
    wynik = load_table(sciezka, "COST", dataset_id=ZBIOR)
    assert wynik.report.records_accepted == 1
    assert wynik.frame["date"].iloc[0] == dt.date(2026, 1, 1)


def test_liczba_w_kolumnie_daty_w_csv_jest_odrzucana(tmp_path: Path) -> None:
    """W pliku CSV liczba nie jest numerem seryjnym, więc model ma prawo ją odrzucić."""
    sciezka = tmp_path / "serial.csv"
    sciezka.write_text(
        "date,unit,category,amount\n46023,Dział A,wynagrodzenia,100\n", encoding="utf-8"
    )
    wynik = load_table(sciezka, "COST", dataset_id=ZBIOR)
    assert wynik.report.records_rejected == 1
    assert "date" in wynik.report.rejections[0].fields


# --- odrzucenia: wiersz nie znika po cichu -------------------------------------------


def test_odrzucony_wiersz_trafia_do_raportu_z_numerem_z_pliku(tmp_path: Path) -> None:
    """Kryterium odbioru 8.4: komunikat wskazuje problem i jego miejsce.

    Numer ma być tym, który klient znajdzie w swoim arkuszu — czyli licząc nagłówek.
    """
    sciezka = tmp_path / "koszty.csv"
    sciezka.write_text(
        "date,unit,category,amount\n"
        "2026-01-01,Dział A,wynagrodzenia,100\n"
        "2026-02-01,,materiały,200\n"  # pusta jednostka — element klucza naturalnego
        "2026-03-01,Dział B,wynagrodzenia,300\n",
        encoding="utf-8",
    )
    wynik = load_table(sciezka, "COST", dataset_id=ZBIOR)
    assert wynik.report.records_accepted == 2
    assert wynik.report.records_rejected == 1
    odrzucenie = wynik.report.rejections[0]
    assert odrzucenie.file_row == 3
    assert "unit" in odrzucenie.fields


def test_odrzucenie_nie_przerywa_importu(tmp_path: Path) -> None:
    """Odrzucenie jest informacją o jakości danych, a nie awarią importu."""
    sciezka = tmp_path / "koszty.csv"
    sciezka.write_text(
        "date,unit,category,amount\n"
        "2026-01-01,Dział A,wynagrodzenia,sto\n"
        "2026-02-01,Dział A,materiały,200\n",
        encoding="utf-8",
    )
    wynik = load_table(sciezka, "COST", dataset_id=ZBIOR)
    assert wynik.report.records_accepted == 1
    assert wynik.report.records_rejected == 1
    assert wynik.report.rows_read == 2


def test_komunikat_odrzucenia_nazywa_pole_i_problem(tmp_path: Path) -> None:
    sciezka = tmp_path / "koszty.csv"
    sciezka.write_text(
        "date,unit,category,amount\n2026-01-01,Dział A,wynagrodzenia,sto\n",
        encoding="utf-8",
    )
    wynik = load_table(sciezka, "COST", dataset_id=ZBIOR)
    assert "amount" in wynik.report.rejections[0].reason


# --- ślad pochodzenia ----------------------------------------------------------------


def test_identyfikator_wiersza_jest_indeksem_ramki_a_nie_polem(
    csv_poprawny: Path,
) -> None:
    """Kontrakt danych nie może wiedzieć, z jakiego pliku przyszła liczba."""
    wynik = load_table(csv_poprawny, "COST", dataset_id=ZBIOR)
    assert wynik.frame.index.name == "row_id"
    assert "row_id" not in wynik.frame.columns
    assert "source_file" not in wynik.frame.columns


def test_identyfikator_prowadzi_do_numeru_wiersza_w_pliku(csv_poprawny: Path) -> None:
    """Ślad: liczba → identyfikator wiersza → raport → wiersz w pliku klienta."""
    wynik = load_table(csv_poprawny, "COST", dataset_id=ZBIOR)
    pierwszy = wynik.frame.index[0]
    assert pierwszy.startswith("COST:")
    assert pierwszy.endswith("000002")  # wiersz 1 to nagłówek
    assert wynik.report.source.source_file == "koszty.csv"


def test_identyfikatory_sa_deterministyczne(tmp_path: Path) -> None:
    """Zasada 3: te same dane wczytane tym samym kodem dają te same identyfikatory."""
    sciezka = tmp_path / "koszty.csv"
    pd.DataFrame(POPRAWNE).to_csv(sciezka, index=False, encoding="utf-8")
    pierwszy = load_table(sciezka, "COST", dataset_id=ZBIOR)
    drugi = load_table(sciezka, "COST", dataset_id=ZBIOR)
    assert list(pierwszy.frame.index) == list(drugi.frame.index)


def test_identyfikator_nie_zalezy_od_katalogu(tmp_path: Path) -> None:
    """Ten sam plik z innego katalogu jest tym samym źródłem.

    Ścieżka bezwzględna zależy od maszyny, więc nie może wchodzić do tożsamości —
    inaczej ten sam import na dwóch komputerach dałby różne identyfikatory.
    """
    a = tmp_path / "a"
    b = tmp_path / "b"
    a.mkdir()
    b.mkdir()
    for katalog in (a, b):
        pd.DataFrame(POPRAWNE).to_csv(
            katalog / "koszty.csv", index=False, encoding="utf-8"
        )
    assert (
        load_table(a / "koszty.csv", "COST", dataset_id=ZBIOR).report.source.source_id
        == load_table(b / "koszty.csv", "COST", dataset_id=ZBIOR).report.source.source_id
    )


def test_rozne_pliki_daja_rozne_identyfikatory(tmp_path: Path) -> None:
    """Dwa pliki zasilające tę samą tabelę nie mogą skleić identyfikatorów."""
    for nazwa in ("koszty_2025.csv", "koszty_2026.csv"):
        pd.DataFrame(POPRAWNE).to_csv(tmp_path / nazwa, index=False, encoding="utf-8")
    a = load_table(tmp_path / "koszty_2025.csv", "COST", dataset_id=ZBIOR)
    b = load_table(tmp_path / "koszty_2026.csv", "COST", dataset_id=ZBIOR)
    assert set(a.frame.index).isdisjoint(set(b.frame.index))


def test_raport_niesie_zakres_wierszy_i_identyfikatorow(csv_poprawny: Path) -> None:
    wynik = load_table(csv_poprawny, "COST", dataset_id=ZBIOR)
    assert wynik.report.source_row_range == (2, 4)
    assert wynik.report.row_id_range == (wynik.frame.index[0], wynik.frame.index[-1])


def test_czas_importu_nie_wchodzi_do_identyfikatorow(csv_poprawny: Path) -> None:
    """Gdyby wchodził, dwa przebiegi dałyby różne wyniki (zasada 3)."""
    assert load_table(csv_poprawny, "COST", dataset_id=ZBIOR).report.imported_at is None


# --- kolumny spoza kontraktu ---------------------------------------------------------


def test_kolumna_spoza_kontraktu_jest_pomijana_i_zapisana(tmp_path: Path) -> None:
    """Kolumna niezmapowana to pozycja w raporcie, nie awaria."""
    sciezka = tmp_path / "koszty.csv"
    sciezka.write_text(
        "date,unit,category,amount,uwagi\n2026-01-01,Dział A,wynagrodzenia,100,korekta\n",
        encoding="utf-8",
    )
    wynik = load_table(sciezka, "COST", dataset_id=ZBIOR)
    assert wynik.report.records_accepted == 1
    assert wynik.report.dropped_columns == ("uwagi",)
    assert "uwagi" not in wynik.frame.columns


def test_mapa_kolumn_tlumaczy_nazwy_klienta(tmp_path: Path) -> None:
    """Docelowo mapę dostarcza mapping/."""
    sciezka = tmp_path / "koszty.csv"
    sciezka.write_text(
        "Miesiac,Komorka,Rodzaj,Kwota\n2026-01-01,Dział A,wynagrodzenia,100\n",
        encoding="utf-8",
    )
    wynik = load_table(
        sciezka,
        "COST", dataset_id=ZBIOR,
        column_map={
            "date": "Miesiac",
            "unit": "Komorka",
            "category": "Rodzaj",
            "amount": "Kwota",
        },
    )
    assert wynik.report.records_accepted == 1
    assert wynik.frame["unit"].iloc[0] == "Dział A"


# --- braki i przypadki brzegowe ------------------------------------------------------


def test_pusta_komorka_staje_sie_brakiem_a_nie_zerem(tmp_path: Path) -> None:
    """Zasada 5 i wpis DT-06: braku nie wypełniamy zerem."""
    sciezka = tmp_path / "koszty.csv"
    sciezka.write_text(
        "date,unit,category,amount\n2026-01-01,Dział A,wynagrodzenia,\n", encoding="utf-8"
    )
    wynik = load_table(sciezka, "COST", dataset_id=ZBIOR)
    assert wynik.report.records_accepted == 1
    assert pd.isna(wynik.frame["amount"].iloc[0])
    assert wynik.frame["amount"].iloc[0] != 0.0


def test_zero_zostaje_zerem(tmp_path: Path) -> None:
    """Koszt kategorii mógł realnie wynieść 0 zł — to nie jest brak."""
    sciezka = tmp_path / "koszty.csv"
    sciezka.write_text(
        "date,unit,category,amount\n2026-01-01,Dział A,wynagrodzenia,0\n", encoding="utf-8"
    )
    wynik = load_table(sciezka, "COST", dataset_id=ZBIOR)
    assert wynik.frame["amount"].iloc[0] == 0.0


def test_plik_bez_wierszy_danych_daje_pusta_ramke_z_kolumnami(tmp_path: Path) -> None:
    """validation/ i engine/ nie mają rozróżniać „brak danych" od „inna struktura"."""
    sciezka = tmp_path / "koszty.csv"
    sciezka.write_text("date,unit,category,amount\n", encoding="utf-8")
    wynik = load_table(sciezka, "COST", dataset_id=ZBIOR)
    assert wynik.report.records_accepted == 0
    assert wynik.report.source_row_range is None
    assert wynik.report.row_id_range is None
    assert list(wynik.frame.columns) == ["date", "unit", "category", "amount"]


def test_ujemna_kwota_przechodzi_import(tmp_path: Path) -> None:
    """Wpis B-01: ujemny koszt to sygnał dla validation/, nie odrzucenie."""
    sciezka = tmp_path / "koszty.csv"
    sciezka.write_text(
        "date,unit,category,amount\n2026-01-01,Dział A,korekty,-4200\n", encoding="utf-8"
    )
    wynik = load_table(sciezka, "COST", dataset_id=ZBIOR)
    assert wynik.report.records_accepted == 1
    assert wynik.frame["amount"].iloc[0] == -4200.0


# --- pozostałe tabele ----------------------------------------------------------------


def test_process_wczytuje_znaczniki_czasu(tmp_path: Path) -> None:
    sciezka = tmp_path / "proces.csv"
    sciezka.write_text(
        "case_id,stage,start,end,unit\n"
        "SPR-1,rejestracja,2026-03-01T08:30:00,2026-03-01T08:52:00,Dział A\n"
        "SPR-2,rejestracja,2026-03-01T09:00:00,,\n",
        encoding="utf-8",
    )
    wynik = load_table(sciezka, "PROCESS", dataset_id=ZBIOR)
    assert wynik.report.records_accepted == 2
    # Brak w ramce sprawdzamy przez pd.isna — patrz wpis DT-08.
    assert pd.isna(wynik.frame["end"].iloc[1])
    assert pd.isna(wynik.frame["unit"].iloc[1])


def test_znacznik_ze_strefa_jest_odrzucany_z_wskazaniem_pola(tmp_path: Path) -> None:
    """Wpis DT-05: przeliczenie na czas lokalny organizacji wymaga profilu mapowania."""
    sciezka = tmp_path / "proces.csv"
    sciezka.write_text(
        "case_id,stage,start,end,unit\n"
        "SPR-1,rejestracja,2026-03-01T08:30:00+01:00,,Dział A\n",
        encoding="utf-8",
    )
    wynik = load_table(sciezka, "PROCESS", dataset_id=ZBIOR)
    assert wynik.report.records_rejected == 1
    assert "start" in wynik.report.rejections[0].fields


def test_wszystkie_piec_tabel_da_sie_wczytac(tmp_path: Path) -> None:
    """Kryterium odbioru 8.2: dane mapowane do pięciu uzgodnionych struktur."""
    pliki = {
        "ACTIVITY": "date,unit,product,volume,revenue\n2026-01-01,A,p,10,100\n",
        "COST": "date,unit,category,amount\n2026-01-01,A,wynagrodzenia,100\n",
        "RESOURCE": "date,unit,resource,available,used,cost\n2026-01-01,A,gabinet,160,132,24000\n",
        "PROCESS": "case_id,stage,start,end,unit\nSPR-1,rejestracja,2026-01-01T08:00:00,,A\n",
        "PLAN": "date,unit,metric,target\n2026-01-01,A,koszt_calkowity,250000\n",
    }
    for tabela, tresc in pliki.items():
        sciezka = tmp_path / f"{tabela.lower()}.csv"
        sciezka.write_text(tresc, encoding="utf-8")
        wynik = load_table(sciezka, tabela, dataset_id=ZBIOR)
        assert wynik.report.records_accepted == 1, tabela
        assert wynik.report.records_rejected == 0, tabela


# --- typy kolumn ramki (wpis DT-08) --------------------------------------------------


def test_typ_kolumny_nie_zalezy_od_zawartosci_pliku(tmp_path: Path) -> None:
    """Ta sama tabela ma dać te same typy kolumn niezależnie od próbki danych.

    Bez tego kolumna `end` z samymi brakami byłaby obiektowa, a z jednym znacznikiem —
    czasowa, i sposób sprawdzania braku zależałby od zawartości pliku klienta.
    """
    z_danymi = tmp_path / "a.csv"
    z_danymi.write_text(
        "case_id,stage,start,end,unit\n"
        "SPR-1,rejestracja,2026-03-01T08:30:00,2026-03-01T08:52:00,Dział A\n",
        encoding="utf-8",
    )
    same_braki = tmp_path / "b.csv"
    same_braki.write_text(
        "case_id,stage,start,end,unit\nSPR-1,rejestracja,,,\n", encoding="utf-8"
    )
    a = load_table(z_danymi, "PROCESS", dataset_id=ZBIOR).frame
    b = load_table(same_braki, "PROCESS", dataset_id=ZBIOR).frame
    assert a.dtypes.to_dict() == b.dtypes.to_dict()


def test_pusta_ramka_ma_te_same_typy_co_wypelniona(tmp_path: Path) -> None:
    pusty = tmp_path / "pusty.csv"
    pusty.write_text("date,unit,category,amount\n", encoding="utf-8")
    pelny = tmp_path / "pelny.csv"
    pd.DataFrame(POPRAWNE).to_csv(pelny, index=False, encoding="utf-8")
    assert (
        load_table(pusty, "COST", dataset_id=ZBIOR).frame.dtypes.to_dict()
        == load_table(pelny, "COST", dataset_id=ZBIOR).frame.dtypes.to_dict()
    )


def test_kolumna_liczbowa_jest_zmiennoprzecinkowa(csv_poprawny: Path) -> None:
    """DT-01: kwoty jako float64, natywnie dla pandas i Parquet."""
    assert load_table(csv_poprawny, "COST", dataset_id=ZBIOR).frame["amount"].dtype == "float64"


# --- dataset_id: rozróżnianie zbiorów danych -----------------------------------------


def test_ten_sam_plik_w_dwoch_zbiorach_daje_rozne_zrodla(tmp_path: Path) -> None:
    """Dwóch klientów przysyła koszty.csv — ślad nie może wskazywać nie tego pliku."""
    sciezka = tmp_path / "koszty.csv"
    pd.DataFrame(POPRAWNE).to_csv(sciezka, index=False, encoding="utf-8")
    a = load_table(sciezka, "COST", dataset_id="klient-a")
    b = load_table(sciezka, "COST", dataset_id="klient-b")
    assert a.report.source.source_id != b.report.source.source_id


def test_ten_sam_plik_w_dwoch_zbiorach_daje_rozlaczne_identyfikatory(
    tmp_path: Path,
) -> None:
    sciezka = tmp_path / "koszty.csv"
    pd.DataFrame(POPRAWNE).to_csv(sciezka, index=False, encoding="utf-8")
    a = load_table(sciezka, "COST", dataset_id="klient-a")
    b = load_table(sciezka, "COST", dataset_id="klient-b")
    assert set(a.frame.index).isdisjoint(set(b.frame.index))


def test_ten_sam_plik_w_tym_samym_zbiorze_daje_identyczne_identyfikatory(
    tmp_path: Path,
) -> None:
    sciezka = tmp_path / "koszty.csv"
    pd.DataFrame(POPRAWNE).to_csv(sciezka, index=False, encoding="utf-8")
    a = load_table(sciezka, "COST", dataset_id="klient-a")
    b = load_table(sciezka, "COST", dataset_id="klient-a")
    assert list(a.frame.index) == list(b.frame.index)


def test_dataset_id_jest_wymagany() -> None:
    """Zbiór ma być zadeklarowany, a nie wyprowadzony ze ścieżki albo nazwy pliku."""
    with pytest.raises(TypeError):
        load_table("koszty.csv", "COST")  # type: ignore[call-arg]


def test_pusty_dataset_id_jest_odrzucany(csv_poprawny: Path) -> None:
    with pytest.raises(ValueError) as blad:
        load_table(csv_poprawny, "COST", dataset_id="   ")
    assert "dataset_id" in str(blad.value)


def test_raport_niesie_zadeklarowany_zbior(csv_poprawny: Path) -> None:
    wynik = load_table(csv_poprawny, "COST", dataset_id="klient-a")
    assert wynik.report.source.dataset_id == "klient-a"


def test_zrodlo_niesie_wersje_algorytmu_tozsamosci(csv_poprawny: Path) -> None:
    wynik = load_table(csv_poprawny, "COST", dataset_id=ZBIOR)
    assert wynik.report.source.identity_algorithm_version
