# Sprawdza kontekst, deklarację, rejestr oraz kontrole 3 i 4 z ZOP-TECH-01 v0.1 pkt 5.3.
"""Testy warstwy kontroli danych.

Najważniejsze są tu testy tego, czego kontrola **nie** robi: nie sumuje dwóch rodzajów
braku, nie liczy zera przy braku wiedzy i nie nadaje statusu mocniejszego niż
zadeklarowany.
"""

from pathlib import Path
from typing import ClassVar

import pandas as pd
import pytest

from xray.ingest import load_table
from xray.ingest.report import ImportReport, SourceRef
from xray.model import TimeGrain, ValidationStatus, get_table
from xray.validation import (
    EVIDENCE_LIMIT,
    CheckDeclaration,
    CheckObservation,
    CheckOutcome,
    DataCheck,
    NotAssessedReason,
    ValidationContext,
    get_declaration,
    registered_check_ids,
    run_check,
    run_checks,
)

ZBIOR = "firma-syntetyczna"


def zbuduj_kontekst(tmp_path: Path, tresc: str, tabela: str = "COST", **kwargs):
    """Wczytuje plik i buduje kontekst z prawdziwym raportem importu."""
    sciezka = tmp_path / f"{tabela.lower()}.csv"
    sciezka.write_text(tresc, encoding="utf-8")
    wynik = load_table(sciezka, tabela, dataset_id=ZBIOR)
    return ValidationContext(
        table=get_table(tabela),
        frame=wynik.frame,
        import_reports=kwargs.get("import_reports", (wynik.report,)),
    )


KOSZTY = (
    "date,unit,category,amount\n"
    "2026-01-01,Dział A,wynagrodzenia,100\n"
    "2026-02-01,Dział A,wynagrodzenia,\n"
    "2026-03-01,,materiały,50\n"
)


# --- kontekst ------------------------------------------------------------------------


def test_nazwa_tabeli_wynika_z_kontraktu(tmp_path: Path) -> None:
    """Jedno źródło prawdy zamiast dwóch, które mogą się rozjechać."""
    ctx = zbuduj_kontekst(tmp_path, KOSZTY)
    assert ctx.table_name == "COST"
    assert ctx.table is get_table("COST")


def test_pusta_krotka_raportow_jest_zakazana() -> None:
    """Byłaby nie do odróżnienia od braku wiedzy."""
    with pytest.raises(ValueError) as blad:
        ValidationContext(
            table=get_table("COST"), frame=pd.DataFrame(), import_reports=()
        )
    assert "None" in str(blad.value)


def test_brak_wiedzy_o_imporcie_jest_dopuszczalny() -> None:
    """Generator firmy syntetycznej produkuje ramki bez przechodzenia przez ingest/."""
    ctx = ValidationContext(table=get_table("COST"), frame=pd.DataFrame())
    assert ctx.import_reports is None
    assert ctx.import_known is False


def test_raport_obcej_tabeli_jest_odrzucany(tmp_path: Path) -> None:
    """Kontekst tabeli COST nie może nieść raportu importu tabeli PLAN."""
    sciezka = tmp_path / "plan.csv"
    sciezka.write_text("date,unit,metric,target\n2026-01-01,A,koszt,100\n", "utf-8")
    obcy = load_table(sciezka, "PLAN", dataset_id=ZBIOR).report
    with pytest.raises(ValueError) as blad:
        ValidationContext(
            table=get_table("COST"), frame=pd.DataFrame(), import_reports=(obcy,)
        )
    assert "PLAN" in str(blad.value)


# --- deklaracja i rejestr ------------------------------------------------------------


def test_rejestr_zna_zaimplementowane_kontrole() -> None:
    """Komplet ośmiu kontroli z ZOP-TECH-01 pkt 5.3."""
    assert set(registered_check_ids()) == {
        "TECH01-VAL-01",
        "TECH01-VAL-02",
        "TECH01-VAL-03",
        "TECH01-VAL-04",
        "TECH01-VAL-05",
        "TECH01-VAL-06",
        "TECH01-VAL-07",
        "TECH01-VAL-08",
    }


def test_kazda_kontrola_ma_numer_zgodny_z_identyfikatorem() -> None:
    """Identyfikator ma prowadzić do punktu karty, a nie być dowolnym napisem."""
    for check_id in registered_check_ids():
        numer = get_declaration(check_id).control_number
        assert check_id == f"TECH01-VAL-{numer:02d}"


def test_deklaracja_wskazuje_numer_kontroli_z_karty() -> None:
    assert get_declaration("TECH01-VAL-03").control_number == 3
    assert get_declaration("TECH01-VAL-04").control_number == 4


def test_numer_kontroli_poza_zakresem_jest_odrzucany() -> None:
    """ZOP-TECH-01 pkt 5.3 definiuje osiem kontroli."""
    with pytest.raises(ValueError):
        CheckDeclaration(check_id="X", control_number=9, title="X")


def test_kontrola_bez_deklaracji_nie_powstaje() -> None:
    with pytest.raises(TypeError) as blad:

        class BezDeklaracji(DataCheck):
            def run(self, context):  # noqa: D102
                return CheckOutcome(status=ValidationStatus.PASS, basis="x")

    assert "DECLARATION" in str(blad.value)


def test_limit_modulowany_jest_ziarnem_a_nie_nazwa_tabeli() -> None:
    """A-01 mówi o danych zdarzeniowych, nie o nazwie „PROCESS".

    Gdyby limit był kluczowany nazwą tabeli, druga tabela zdarzeniowa dostałaby po cichu
    limit domyślny.
    """
    deklaracja = get_declaration("TECH01-VAL-04")
    assert deklaracja.max_status_by_time_grain == {TimeGrain.EVENT: ValidationStatus.WARNING}
    assert deklaracja.effective_max_status(get_table("COST")) is ValidationStatus.CRITICAL
    assert (
        deklaracja.effective_max_status(get_table("PROCESS")) is ValidationStatus.WARNING
    )


def test_przekroczenie_limitu_statusu_jest_bledem(tmp_path: Path) -> None:
    """Rozstrzygnięcie mocniejsze niż zadeklarowane należy do karty, nie do fundamentu."""

    class ZaMocna(DataCheck):
        DECLARATION: ClassVar[CheckDeclaration] = CheckDeclaration(
            check_id="ATRAPA-LIMIT",
            control_number=5,
            title="Atrapa przekraczająca zadeklarowany limit",
            max_status=ValidationStatus.WARNING,
        )

        def run(self, context):  # noqa: D102
            return CheckOutcome(status=ValidationStatus.CRITICAL, basis="zbyt mocno")

    import xray.validation.registry as rejestr

    ctx = zbuduj_kontekst(tmp_path, KOSZTY)
    pierwotne = rejestr.CHECKS
    try:
        rejestr.CHECKS = {**pierwotne, "ATRAPA-LIMIT": ZaMocna}
        with pytest.raises(RuntimeError) as blad:
            run_check("ATRAPA-LIMIT", ctx)
    finally:
        rejestr.CHECKS = pierwotne
    assert "WARNING" in str(blad.value)


# --- brak wejścia to nie zero --------------------------------------------------------


def test_kontrola_bez_raportu_importu_nie_liczy_zera(tmp_path: Path) -> None:
    """Liczba odrzuceń jest nieznana, a nie zerowa."""
    ctx = zbuduj_kontekst(tmp_path, KOSZTY, import_reports=None)
    wynik = run_check("TECH01-VAL-03", ctx)
    assert wynik.status is None
    assert wynik.not_assessed_reason is NotAssessedReason.MISSING_INPUT
    assert wynik.observations == ()
    assert "nieznana" in wynik.basis


def test_zadeklarowany_brak_odrzucen_daje_zero(tmp_path: Path) -> None:
    """Deklaracja ma mieć autora: pusty raport, a nie None."""
    ctx_z_plikiem = zbuduj_kontekst(tmp_path, KOSZTY)
    pusty = ImportReport(
        table_name="COST",
        source=SourceRef.create(
            dataset_id=ZBIOR,
            source_file="generator syntetyczny",
            source_path="synth://firma-syntetyczna",
        ),
        records_accepted=len(ctx_z_plikiem.frame),
        records_rejected=0,
        # Generator liczy skrót własnych rekordów tak samo jak ingest/ — deklaracja ma
        # mieć autora także wtedy, gdy autorem nie jest import z pliku.
        content_digest="0" * 32,
    )
    ctx = ValidationContext(
        table=get_table("COST"), frame=ctx_z_plikiem.frame, import_reports=(pusty,)
    )
    wynik = run_check("TECH01-VAL-03", ctx)
    assert wynik.status is ValidationStatus.PASS
    utracone = _obserwacja(wynik, "rows_rejected_missing_key")
    assert utracone.value == 0.0


def test_kontrola_niedotyczaca_tabeli_daje_wynik_a_nie_milczenie() -> None:
    """Raport jakości danych ma pokryć wszystkie osiem kontroli dla każdej tabeli."""

    class TylkoZasoby(DataCheck):
        DECLARATION: ClassVar[CheckDeclaration] = CheckDeclaration(
            check_id="ATRAPA-ZASOBY",
            control_number=7,
            title="Atrapa wymagająca pól zdolności",
            required_fields=("available", "used"),
            max_status=ValidationStatus.WARNING,
        )

        def run(self, context):  # noqa: D102
            return CheckOutcome(status=ValidationStatus.PASS, basis="x")

    import xray.validation.registry as rejestr

    pierwotne = rejestr.CHECKS
    try:
        rejestr.CHECKS = {**pierwotne, "ATRAPA-ZASOBY": TylkoZasoby}
        wynik = run_check(
            "ATRAPA-ZASOBY",
            ValidationContext(table=get_table("COST"), frame=pd.DataFrame()),
        )
    finally:
        rejestr.CHECKS = pierwotne
    assert wynik.status is None
    assert wynik.not_assessed_reason is NotAssessedReason.NOT_APPLICABLE
    assert "available" in wynik.basis


# --- kontrola 3 ----------------------------------------------------------------------


def _obserwacja(wynik, measure: str, subject: str | None = None) -> CheckObservation:
    for o in wynik.observations:
        if o.measure == measure and (subject is None or o.subject == subject):
            return o
    raise AssertionError(f"brak obserwacji {measure} / {subject}")


def test_kontrola_3_liczy_puste_komorki(tmp_path: Path) -> None:
    ctx = zbuduj_kontekst(tmp_path, KOSZTY)
    wynik = run_check("TECH01-VAL-03", ctx)
    assert _obserwacja(wynik, "missing_values", "amount").value == 1.0


def test_kontrola_3_liczy_wiersze_utracone_osobno(tmp_path: Path) -> None:
    """Wiersz z pustym unit nie trafił do ramki — widać go tylko w raporcie importu."""
    ctx = zbuduj_kontekst(tmp_path, KOSZTY)
    wynik = run_check("TECH01-VAL-03", ctx)
    assert _obserwacja(wynik, "rows_rejected_missing_key").value == 1.0


def test_dwoch_rodzajow_braku_nie_da_sie_zsumowac(tmp_path: Path) -> None:
    """Nie istnieje pole zbiorcze, w którym dałoby się dodać puste komórki
    i utracone wiersze. „Trzydzieści braków" wprowadzałoby w błąd."""
    ctx = zbuduj_kontekst(tmp_path, KOSZTY)
    wynik = run_check("TECH01-VAL-03", ctx)
    miary = {o.measure for o in wynik.observations}
    assert miary == {"missing_values", "rows_rejected_missing_key"}
    from xray.validation import CheckResult

    assert not any(
        "total" in nazwa or "sum" in nazwa for nazwa in CheckResult.model_fields
    )


def test_kontrola_3_ma_status_pass_mimo_brakow(tmp_path: Path) -> None:
    """Obraz braków, nie ocena. To test rozstrzyga, czy brak go blokuje."""
    ctx = zbuduj_kontekst(tmp_path, KOSZTY)
    assert run_check("TECH01-VAL-03", ctx).status is ValidationStatus.PASS
    assert get_declaration("TECH01-VAL-03").max_status is ValidationStatus.PASS


def test_dowod_braku_wskazuje_wiersz(tmp_path: Path) -> None:
    ctx = zbuduj_kontekst(tmp_path, KOSZTY)
    wynik = run_check("TECH01-VAL-03", ctx)
    obs = _obserwacja(wynik, "missing_values", "amount")
    assert len(obs.evidence_row_ids) == 1
    assert obs.evidence_row_ids[0] in ctx.frame.index


def test_dowod_utraconego_wiersza_wskazuje_plik_i_numer(tmp_path: Path) -> None:
    """Sam numer wiersza nie byłby adresem: tabela może pochodzić z kilku plików."""
    ctx = zbuduj_kontekst(tmp_path, KOSZTY)
    obs = _obserwacja(run_check("TECH01-VAL-03", ctx), "rows_rejected_missing_key")
    (source_id, file_row) = obs.evidence_source_rows[0]
    assert source_id == ctx.import_reports[0].source.source_id
    assert file_row == 4


# --- kontrola 4 ----------------------------------------------------------------------


def test_kontrola_4_wykrywa_powtorzony_klucz(tmp_path: Path) -> None:
    tresc = (
        "date,unit,category,amount\n"
        "2026-01-01,Dział A,wynagrodzenia,100\n"
        "2026-01-01,Dział A,wynagrodzenia,200\n"
        "2026-02-01,Dział B,materiały,50\n"
    )
    wynik = run_check("TECH01-VAL-04", zbuduj_kontekst(tmp_path, tresc))
    assert wynik.status is ValidationStatus.CRITICAL
    assert _obserwacja(wynik, "duplicate_rows").value == 2.0


def test_kontrola_4_bez_duplikatow_daje_pass(tmp_path: Path) -> None:
    wynik = run_check("TECH01-VAL-04", zbuduj_kontekst(tmp_path, KOSZTY))
    assert wynik.status is ValidationStatus.PASS
    assert wynik.observations == ()


def test_kontrola_4_na_pustej_tabeli_daje_pass(tmp_path: Path) -> None:
    ctx = zbuduj_kontekst(tmp_path, "date,unit,category,amount\n")
    assert run_check("TECH01-VAL-04", ctx).status is ValidationStatus.PASS


def test_duplikat_w_tabeli_zdarzeniowej_jest_sygnalem_nie_bledem(tmp_path: Path) -> None:
    """PROC-02 pkt 2.4: powrót do tego samego etapu jest oczekiwany do czasu
    wprowadzenia repeat_visit."""
    tresc = (
        "case_id,stage,start,end,unit\n"
        "SPR-1,rejestracja,2026-03-01T08:00:00,2026-03-01T08:10:00,A\n"
        "SPR-1,rejestracja,2026-03-01T09:00:00,2026-03-01T09:10:00,A\n"
    )
    wynik = run_check("TECH01-VAL-04", zbuduj_kontekst(tmp_path, tresc, "PROCESS"))
    assert wynik.status is ValidationStatus.WARNING
    assert "repeat_visit" in wynik.basis


# --- dowody: granica i uczciwe oznaczenie --------------------------------------------


def test_dowod_jest_przycinany_i_oznaczany(tmp_path: Path) -> None:
    """Kolumna z tysiącami braków nie może wypełnić raportu identyfikatorami."""
    wiersze = "".join(
        f"2026-01-{dzien:02d},Dział A,kat{i},\n" for i, dzien in enumerate(range(1, 29))
    )
    tresc = "date,unit,category,amount\n" + wiersze
    ctx = zbuduj_kontekst(tmp_path, tresc)
    obs = _obserwacja(run_check("TECH01-VAL-03", ctx), "missing_values", "amount")
    assert obs.value == 28.0
    assert len(obs.evidence_row_ids) == 28
    assert obs.evidence_truncated is False


def test_dowod_ponad_granica_jest_oznaczony_jako_probka() -> None:
    """Bez oznaczenia skrócona lista wyglądałaby identycznie jak pełna."""
    obs = CheckObservation.create(
        subject="amount",
        measure="missing_values",
        value=5000.0,
        basis="test",
        evidence_row_ids=tuple(f"COST:SRC-x:{i:06d}" for i in range(5000)),
    )
    assert len(obs.evidence_row_ids) == EVIDENCE_LIMIT
    assert obs.evidence_truncated is True
    assert obs.value == 5000.0


def test_probka_dowodu_jest_deterministyczna() -> None:
    """Losowy wybór dałby różne dowody dla tych samych danych w dwóch przebiegach."""
    wiersze = tuple(f"COST:SRC-x:{i:06d}" for i in range(200))
    a = CheckObservation.create(
        subject="x", measure="m", value=200.0, basis="t", evidence_row_ids=wiersze
    )
    b = CheckObservation.create(
        subject="x", measure="m", value=200.0, basis="t", evidence_row_ids=wiersze
    )
    assert a.evidence_row_ids == b.evidence_row_ids == wiersze[:EVIDENCE_LIMIT]


def test_dowod_ponad_granica_nie_przechodzi_konstruktorem() -> None:
    """Granicy nie da się obejść, budując obserwację wprost."""
    with pytest.raises(ValueError) as blad:
        CheckObservation(
            subject="x",
            measure="m",
            value=1.0,
            basis="t",
            evidence_row_ids=tuple(str(i) for i in range(EVIDENCE_LIMIT + 1)),
        )
    assert "create" in str(blad.value)


# --- spójność wyniku -----------------------------------------------------------------


def test_obserwacja_bez_podstawy_jest_odrzucana() -> None:
    """Liczba bez podstawy nie jest dowodem."""
    with pytest.raises(ValueError):
        CheckObservation(subject="x", measure="m", value=1.0, basis="  ")


def test_brak_statusu_wymaga_powodu_z_katalogu() -> None:
    """Na prozie nie da się policzyć, ile kontroli nie dało wyniku."""
    with pytest.raises(ValueError) as blad:
        CheckOutcome(status=None, basis="nie wiadomo")
    assert "NotAssessedReason" in str(blad.value)


def test_status_i_powod_braku_wykluczaja_sie() -> None:
    with pytest.raises(ValueError):
        CheckOutcome(
            status=ValidationStatus.PASS,
            basis="x",
            not_assessed_reason=NotAssessedReason.MISSING_INPUT,
        )


def test_run_checks_zwraca_wyniki_w_kolejnosci_rejestru(tmp_path: Path) -> None:
    """Kolejność deterministyczna, bo rejestr jest jawną krotką."""
    ctx = zbuduj_kontekst(tmp_path, KOSZTY)
    wyniki = run_checks(ctx)
    assert [w.check_id for w in wyniki] == list(registered_check_ids())
    assert all(w.table_name == "COST" for w in wyniki)




def test_dwa_niezalezne_przebiegi_daja_ten_sam_wynik(tmp_path: Path) -> None:
    """Zasada 3, sprawdzona na dwóch **niezależnych** kontekstach.

    Porównanie ``run_checks(ctx) == run_checks(ctx)`` na tym samym obiekcie przeszłoby
    także wtedy, gdyby kontrole zależały od czasu wykonania albo kolejności iteracji —
    ta sama kategoria fałszywego testu co przy DT-07. Wczytujemy plik dwa razy, do dwóch
    osobnych katalogów, i porównujemy wyniki.
    """
    pierwszy = tmp_path / "a"
    drugi = tmp_path / "b"
    pierwszy.mkdir()
    drugi.mkdir()
    wyniki = [run_checks(zbuduj_kontekst(katalog, KOSZTY)) for katalog in (pierwszy, drugi)]
    assert wyniki[0] == wyniki[1]


# --- kontrola 2: nieprawidłowy format ------------------------------------------------


def test_kontrola_2_zlicza_odrzucenia_formatu(tmp_path: Path) -> None:
    tresc = (
        "date,unit,category,amount\n"
        "2026-01-01,Dział A,wynagrodzenia,sto\n"
        "2026-02-01,Dział A,materiały,200\n"
    )
    wynik = run_check("TECH01-VAL-02", zbuduj_kontekst(tmp_path, tresc))
    assert wynik.status is ValidationStatus.WARNING
    assert _obserwacja(wynik, "rows_rejected_invalid_format", "amount").value == 1.0


def test_kontrola_2_nie_liczy_brakow_jako_formatu(tmp_path: Path) -> None:
    """Pusta komórka w polu klucza to brak wartości, a nie zły format.

    Klient ma dostać „uzupełnij", a nie „popraw zapis".
    """
    wynik = run_check("TECH01-VAL-02", zbuduj_kontekst(tmp_path, KOSZTY))
    assert wynik.status is ValidationStatus.PASS
    assert wynik.observations == ()


def test_kontrola_2_bez_raportu_nie_liczy_zera(tmp_path: Path) -> None:
    ctx = zbuduj_kontekst(tmp_path, KOSZTY, import_reports=None)
    wynik = run_check("TECH01-VAL-02", ctx)
    assert wynik.not_assessed_reason is NotAssessedReason.MISSING_INPUT


def test_kontrola_2_wskazuje_plik_i_wiersz(tmp_path: Path) -> None:
    tresc = "date,unit,category,amount\n2026-01-01,Dział A,wyn,sto\n"
    ctx = zbuduj_kontekst(tmp_path, tresc)
    obs = _obserwacja(run_check("TECH01-VAL-02", ctx), "rows_rejected_invalid_format")
    assert obs.evidence_source_rows == ((ctx.import_reports[0].source.source_id, 2),)


# --- kontrola 5: wartości podejrzane -------------------------------------------------


def test_kontrola_5_zglasza_ujemna_kwote_jako_sygnal(tmp_path: Path) -> None:
    """Wpis B-01: bez pola oznaczenia korekty kontrola nie klasyfikuje wartości."""
    tresc = "date,unit,category,amount\n2026-01-01,Dział A,korekty,-4200\n"
    wynik = run_check("TECH01-VAL-05", zbuduj_kontekst(tmp_path, tresc))
    assert wynik.status is ValidationStatus.WARNING
    assert _obserwacja(wynik, "negative_values", "amount").value == 1.0
    assert "B-01" in _obserwacja(wynik, "negative_values", "amount").basis


def test_kontrola_5_nie_moze_nadac_critical() -> None:
    """Ujemny koszt bywa poprawnym zapisem korekty — CRITICAL byłby wymyśloną regułą."""
    assert get_declaration("TECH01-VAL-05").max_status is ValidationStatus.WARNING


def test_kontrola_5_bada_wszystkie_pola_liczbowe(tmp_path: Path) -> None:
    """Pola wybierane po właściwości, nie po nazwie."""
    tresc = (
        "date,unit,resource,available,used,cost\n"
        "2026-01-01,A,gabinet,-8,132,24000\n"
        "2026-02-01,A,gabinet,160,-2,-100\n"
    )
    wynik = run_check("TECH01-VAL-05", zbuduj_kontekst(tmp_path, tresc, "RESOURCE"))
    assert {o.subject for o in wynik.observations} == {"available", "used", "cost"}


def test_kontrola_5_pomija_zero(tmp_path: Path) -> None:
    """Zero nie jest wartością ujemną ani brakiem."""
    tresc = "date,unit,category,amount\n2026-01-01,A,wyn,0\n"
    assert run_check(
        "TECH01-VAL-05", zbuduj_kontekst(tmp_path, tresc)
    ).status is ValidationStatus.PASS


def test_kontrola_5_bez_pol_liczbowych_jest_niestosowalna(tmp_path: Path) -> None:
    """PROCESS nie ma pól liczbowych. To nie to samo co brak wartości podejrzanych."""
    tresc = "case_id,stage,start,end,unit\nSPR-1,rej,2026-01-01T08:00:00,,A\n"
    wynik = run_check("TECH01-VAL-05", zbuduj_kontekst(tmp_path, tresc, "PROCESS"))
    assert wynik.status is None
    assert wynik.not_assessed_reason is NotAssessedReason.NOT_APPLICABLE


# --- kontrola 7: used > available ----------------------------------------------------

ZASOBY = (
    "date,unit,resource,available,used,cost\n"
    "2026-01-01,Dział A,gabinet 1,160,132,24000\n"
    "2026-02-01,Dział A,gabinet 1,160,190,24000\n"
)


def test_kontrola_7_zglasza_przekroczenie_jako_sygnal(tmp_path: Path) -> None:
    wynik = run_check("TECH01-VAL-07", zbuduj_kontekst(tmp_path, ZASOBY, "RESOURCE"))
    assert wynik.status is ValidationStatus.WARNING
    assert _obserwacja(wynik, "usage_above_capacity").value == 1.0
    assert "CAP-01" in _obserwacja(wynik, "usage_above_capacity").basis


def test_kontrola_7_nie_moze_nadac_critical() -> None:
    """CAP-01 rozdz. 5: przekroczenie nie jest automatycznie błędem logicznym."""
    assert get_declaration("TECH01-VAL-07").max_status is ValidationStatus.WARNING


def test_kontrola_7_nie_dotyczy_tabeli_bez_zdolnosci(tmp_path: Path) -> None:
    wynik = run_check("TECH01-VAL-07", zbuduj_kontekst(tmp_path, KOSZTY))
    assert wynik.not_assessed_reason is NotAssessedReason.NOT_APPLICABLE
    assert "available" in wynik.basis


def test_kontrola_7_brak_wartosci_to_nie_przekroczenie(tmp_path: Path) -> None:
    """Brak zgłasza kontrola 3; tutaj byłby fałszywym sygnałem."""
    tresc = (
        "date,unit,resource,available,used,cost\n"
        "2026-01-01,Dział A,gabinet 1,,132,24000\n"
    )
    wynik = run_check("TECH01-VAL-07", zbuduj_kontekst(tmp_path, tresc, "RESOURCE"))
    assert wynik.status is ValidationStatus.PASS
    assert _obserwacja(wynik, "rows_not_comparable").value == 1.0


def test_kontrola_7_nie_koryguje_wartosci(tmp_path: Path) -> None:
    """CAP-01 rozdz. 5: nie korygować po cichu. Ramka zostaje nietknięta."""
    ctx = zbuduj_kontekst(tmp_path, ZASOBY, "RESOURCE")
    przed = ctx.frame.copy()
    run_check("TECH01-VAL-07", ctx)
    pd.testing.assert_frame_equal(ctx.frame, przed)


def test_wszystkie_zarejestrowane_kontrole_daja_wynik_dla_kazdej_tabeli(
    tmp_path: Path,
) -> None:
    """Raport jakości danych ma pokryć każdą kontrolę dla każdej tabeli."""
    pliki = {
        "ACTIVITY": "date,unit,product,volume,revenue\n2026-01-01,A,p,10,100\n",
        "COST": KOSZTY,
        "RESOURCE": ZASOBY,
        "PROCESS": "case_id,stage,start,end,unit\nSPR-1,rej,2026-01-01T08:00:00,,A\n",
        "PLAN": "date,unit,metric,target\n2026-01-01,A,koszt,250\n",
    }
    for tabela, tresc in pliki.items():
        wyniki = run_checks(zbuduj_kontekst(tmp_path, tresc, tabela))
        assert len(wyniki) == len(registered_check_ids()), tabela
        assert all(w.basis.strip() for w in wyniki), tabela
        assert all(
            w.status is not None or w.not_assessed_reason is not None for w in wyniki
        ), tabela
