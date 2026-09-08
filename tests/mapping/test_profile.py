# Sprawdza profil mapowania i raport z jego zastosowania — ZOP-TECH-01 v0.1 pkt 10.3,
# rozstrzygnięcia B-04, B-06, DT-05, DT-10 i DT-13.
"""Testy warstwy mapowania.

Najważniejsze są tu testy rozróżnień: cztery różne rzeczy, które łatwo zlać w jedną,
i skrót profilu, który musi widzieć zmianę znaczenia, a nie zmianę zapisu.
"""

from pathlib import Path

import pytest

from xray.mapping import MappingProfile, ProfileError, apply_profile

POPRAWNY = """
profile_id: klient-testowy
profile_version: 1
dataset_id: klient-testowy
organization_timezone: Europe/Warsaw
columns:
  COST:
    date: Miesiac
    unit: Komorka
    category: Rodzaj_kosztu
    amount: Kwota
  RESOURCE:
    date: Miesiac
    unit: Komorka
    resource: Zasob
    available: Godziny_dostepne
    used: Godziny_wykorzystane
    cost: Koszt_zasobu
plan_metrics: []
"""

KOLUMNY_COST = ["Miesiac", "Komorka", "Rodzaj_kosztu", "Kwota"]


def zapisz(tmp_path: Path, tresc: str, nazwa: str = "p.yaml") -> Path:
    sciezka = tmp_path / nazwa
    sciezka.write_text(tresc, encoding="utf-8")
    return sciezka


# --- wczytanie ------------------------------------------------------------------------


def test_profil_sie_wczytuje(tmp_path: Path) -> None:
    profil = MappingProfile.load(zapisz(tmp_path, POPRAWNY))
    assert profil.dataset_id == "klient-testowy"
    assert profil.organization_timezone == "Europe/Warsaw"
    assert profil.column_map("COST")["amount"] == "Kwota"


def test_profil_firmy_syntetycznej_jest_poprawny() -> None:
    """Profil w repozytorium ma się wczytywać, a nie tylko wyglądać poprawnie."""
    profil = MappingProfile.load("profiles/firma-syntetyczna.yaml")
    assert profil.dataset_id == "firma-syntetyczna"
    assert set(profil.columns) == {"ACTIVITY", "COST", "RESOURCE", "PROCESS", "PLAN"}
    assert profil.plan_metrics == ()


def test_duplikat_klucza_jest_odrzucany(tmp_path: Path) -> None:
    """PyYAML wziąłby po cichu ostatni wpis, a jedno przypisanie zniknęłoby bez śladu."""
    zly = POPRAWNY.replace(
        "    unit: Komorka\n    category",
        "    unit: Komorka\n    unit: Inna\n    category",
        1,
    )
    with pytest.raises(ProfileError) as blad:
        MappingProfile.load(zapisz(tmp_path, zly, "dup.yaml"))
    assert "powtarza się" in str(blad.value)


def test_ten_sam_klucz_w_roznych_tabelach_jest_poprawny(tmp_path: Path) -> None:
    """`unit` występuje w mapie każdej tabeli — powtórzenie liczy się w obrębie jednej."""
    profil = MappingProfile.load(zapisz(tmp_path, POPRAWNY))
    assert profil.column_map("COST")["unit"] == "Komorka"
    assert profil.column_map("RESOURCE")["unit"] == "Komorka"


def test_nieznane_pole_kontraktu_jest_bledem_profilu(tmp_path: Path) -> None:
    """Nie pozycja raportu — inaczej kontrola 1 zgłosiłaby CRITICAL przeciwko danym
    klienta za naszą literówkę, a klient poszedłby szukać kolumny, której nie ma mieć."""
    zly = POPRAWNY.replace(
        "    date: Miesiac\n    unit: Komorka",
        "    dat: Miesiac\n    unit: Komorka",
        1,
    )
    with pytest.raises(ProfileError) as blad:
        MappingProfile.load(zapisz(tmp_path, zly, "zle.yaml"))
    assert "dat" in str(blad.value)


def test_nieznana_tabela_jest_bledem_profilu(tmp_path: Path) -> None:
    zly = POPRAWNY.replace("  COST:", "  KOSZTY:", 1)
    with pytest.raises(ProfileError) as blad:
        MappingProfile.load(zapisz(tmp_path, zly, "tab.yaml"))
    assert "KOSZTY" in str(blad.value)


def test_puste_przypisanie_jest_bledem(tmp_path: Path) -> None:
    """Brak przypisania wyraża się pominięciem klucza, nie pustą wartością."""
    zly = POPRAWNY.replace("    amount: Kwota", "    amount: ''", 1)
    with pytest.raises(ProfileError):
        MappingProfile.load(zapisz(tmp_path, zly, "puste.yaml"))


def test_profil_nie_wykonuje_obiektow_z_pliku(tmp_path: Path) -> None:
    """Plik przychodzi od klienta; loader czyta wyłącznie typy proste."""
    zly = POPRAWNY + "\nzlosliwe: !!python/object/apply:os.system ['echo x']\n"
    with pytest.raises(ProfileError):
        MappingProfile.load(zapisz(tmp_path, zly, "exec.yaml"))


# --- cztery rozróżnienia w raporcie ---------------------------------------------------


def test_zmapowane_i_niezmapowane(tmp_path: Path) -> None:
    profil = MappingProfile.load(zapisz(tmp_path, POPRAWNY))
    raport = apply_profile(profil, "COST", [*KOLUMNY_COST, "Kod_MPK"])
    assert raport.mapped == (
        ("date", "Miesiac"),
        ("unit", "Komorka"),
        ("category", "Rodzaj_kosztu"),
        ("amount", "Kwota"),
    )
    assert raport.unmapped_columns == ("Kod_MPK",)


def test_pole_bez_przypisania_a_kolumna_ktorej_nie_ma(tmp_path: Path) -> None:
    """Dwie różne rozmowy z klientem, więc dwie różne pozycje raportu."""
    bez_kosztu = POPRAWNY.replace("    cost: Koszt_zasobu\n", "")
    profil = MappingProfile.load(zapisz(tmp_path, bez_kosztu, "bez.yaml"))
    raport = apply_profile(
        profil,
        "RESOURCE",
        ["Miesiac", "Komorka", "Zasob", "Godziny_dostepne"],
    )
    assert raport.fields_without_mapping == ("cost",)
    assert raport.declared_missing_columns == (("used", "Godziny_wykorzystane"),)
    assert set(raport.materialized_empty) == {"used", "cost"}


def test_brak_kolumny_klucza_jest_odnotowany_osobno(tmp_path: Path) -> None:
    """Wpis B-06: element NATURAL_KEY to inna sprawa niż pole spoza klucza."""
    profil = MappingProfile.load(zapisz(tmp_path, POPRAWNY))
    raport = apply_profile(profil, "COST", ["Miesiac", "Rodzaj_kosztu", "Kwota"])
    assert raport.missing_key_fields == ("unit",)
    assert "unit" not in raport.materialized_empty


def test_kolumna_zasilajaca_dwa_pola_jest_odnotowana(tmp_path: Path) -> None:
    """Decyzja D-C: dopuszczone, ale ciche dopuszczenie ukrywałoby pomyłkę w profilu."""
    dzielona = POPRAWNY.replace("    resource: Zasob", "    resource: Komorka", 1)
    profil = MappingProfile.load(zapisz(tmp_path, dzielona, "dziel.yaml"))
    raport = apply_profile(
        profil,
        "RESOURCE",
        ["Miesiac", "Komorka", "Godziny_dostepne", "Godziny_wykorzystane", "Koszt_zasobu"],
    )
    assert raport.shared_source_columns == (("Komorka", ("unit", "resource")),)


# --- ogłoszenie stanu plan_metrics ----------------------------------------------------


def test_pusta_plan_metrics_jest_ogloszona_a_nie_wywnioskowana(tmp_path: Path) -> None:
    """Ta sama racja, dla której „zmaterializowana jako pusta" jest oddzielona
    od „była, ale pusta": czytający ma zobaczyć zdanie, nie nieobecność."""
    profil = MappingProfile.load(zapisz(tmp_path, POPRAWNY))
    raport = apply_profile(profil, "COST", KOLUMNY_COST)
    assert raport.plan_budget_available is False
    assert "plan_budget" in raport.plan_budget_note()
    assert "B-04" in raport.plan_budget_note()


def test_zadeklarowana_miara_zmienia_ogloszenie(tmp_path: Path) -> None:
    z_miara = POPRAWNY.replace(
        "plan_metrics: []",
        "plan_metrics:\n"
        "  - plan_metric: koszt_calkowity\n"
        "    target_measure: FIN-01/koszt\n"
        "    definition_match_basis: obie miary liczą koszt pracodawcy w tym samym zakresie\n"
        "    declared_by: Aleksander\n"
        "    declared_at: 2026-09-07\n",
    )
    profil = MappingProfile.load(zapisz(tmp_path, z_miara, "miara.yaml"))
    raport = apply_profile(profil, "COST", KOLUMNY_COST)
    assert raport.plan_budget_available is True
    assert raport.plan_metrics_declared == 1


# --- skrót znaczącej treści -----------------------------------------------------------


def wczytaj(tmp_path: Path, tresc: str, nazwa: str) -> MappingProfile:
    return MappingProfile.load(zapisz(tmp_path, tresc, nazwa))


def test_skrot_ignoruje_komentarze_i_formatowanie(tmp_path: Path) -> None:
    """Ta sama racja co w DT-12: skrót z treści, nie z zapisu."""
    inaczej = "# komentarz bez znaczenia\n" + POPRAWNY.replace(
        "profile_version: 1", "profile_version: 7"
    )
    a = wczytaj(tmp_path, POPRAWNY, "a.yaml")
    b = wczytaj(tmp_path, inaczej, "b.yaml")
    uzyte = {"COST": (("date", "Miesiac"), ("amount", "Kwota"))}
    assert a.semantic_digest(uzyte) == b.semantic_digest(uzyte)


def test_zmiana_strefy_zmienia_skrot(tmp_path: Path) -> None:
    inna = POPRAWNY.replace("Europe/Warsaw", "Europe/Berlin")
    a = wczytaj(tmp_path, POPRAWNY, "a.yaml")
    b = wczytaj(tmp_path, inna, "c.yaml")
    uzyte = {"COST": (("date", "Miesiac"),)}
    assert a.semantic_digest(uzyte) != b.semantic_digest(uzyte)


def test_dodanie_deklaracji_miary_zmienia_skrot(tmp_path: Path) -> None:
    """Sedno DT-13: plan_metrics nie zmienia treści rekordów, więc bez skrótu profilu
    byłaby niewidoczna dla tożsamości przebiegu."""
    z_miara = POPRAWNY.replace(
        "plan_metrics: []",
        "plan_metrics:\n"
        "  - plan_metric: koszt_calkowity\n"
        "    target_measure: FIN-01/koszt\n"
        "    definition_match_basis: zgodne ujęcie\n"
        "    declared_by: Aleksander\n"
        "    declared_at: 2026-09-07\n",
    )
    a = wczytaj(tmp_path, POPRAWNY, "a.yaml")
    b = wczytaj(tmp_path, z_miara, "m.yaml")
    uzyte = {"COST": (("date", "Miesiac"),)}
    assert a.semantic_digest(uzyte) != b.semantic_digest(uzyte)


def test_zmiana_podstawy_zgodnosci_zmienia_skrot(tmp_path: Path) -> None:
    """Wpis DT-13: definition_match_basis to osąd, nie wyprowadzenie."""
    szablon = POPRAWNY.replace(
        "plan_metrics: []",
        "plan_metrics:\n"
        "  - plan_metric: koszt_calkowity\n"
        "    target_measure: FIN-01/koszt\n"
        "    definition_match_basis: PODSTAWA\n"
        "    declared_by: Aleksander\n"
        "    declared_at: 2026-09-07\n",
    )
    a = wczytaj(tmp_path, szablon.replace("PODSTAWA", "obie miary liczą to samo"), "x.yaml")
    b = wczytaj(
        tmp_path,
        szablon.replace("PODSTAWA", "miary różnią się ujęciem VAT, przyjęto przybliżenie"),
        "y.yaml",
    )
    uzyte = {"COST": (("date", "Miesiac"),)}
    assert a.semantic_digest(uzyte) != b.semantic_digest(uzyte)


def test_zmiana_autora_deklaracji_nie_zmienia_skrotu(tmp_path: Path) -> None:
    """declared_by i declared_at mówią kto, nie dlaczego to wolno."""
    szablon = POPRAWNY.replace(
        "plan_metrics: []",
        "plan_metrics:\n"
        "  - plan_metric: koszt_calkowity\n"
        "    target_measure: FIN-01/koszt\n"
        "    definition_match_basis: zgodne ujęcie\n"
        "    declared_by: AUTOR\n"
        "    declared_at: 2026-09-07\n",
    )
    a = wczytaj(tmp_path, szablon.replace("AUTOR", "Aleksander"), "p1.yaml")
    b = wczytaj(tmp_path, szablon.replace("AUTOR", "Michał"), "p2.yaml")
    uzyte = {"COST": (("date", "Miesiac"),)}
    assert a.semantic_digest(uzyte) == b.semantic_digest(uzyte)


def test_przypisanie_do_nieuzytej_kolumny_nie_zmienia_skrotu(tmp_path: Path) -> None:
    """Liczy się to, co się wydarzyło — jak przy source_id."""
    profil = wczytaj(tmp_path, POPRAWNY, "a.yaml")
    uzyte = {"COST": (("date", "Miesiac"), ("unit", "Komorka"))}
    assert profil.semantic_digest(uzyte) == profil.semantic_digest(dict(uzyte))
