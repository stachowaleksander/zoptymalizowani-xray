# Sprawdza bramkę gotowości testu — rozstrzygnięcie B-06, wiersz „rejestr testów".
"""Testy egzekwowania ``required_by_test`` wobec rzeczywistych raportów importu.

Teza, której pilnują: **test nie może udawać wyniku**. Do 2026-09-08 deklaracja była
sprawdzana wyłącznie wobec kontraktu danych, czyli zawsze prawdziwie, niezależnie od
tego, co przyszło w pliku.

Raporty importu powstają tu przez ``load_table`` na prawdziwych plikach, a nie ręcznie:
sprawdzamy egzekwowanie wobec **rzeczywistych** raportów, tak jak mówi rozstrzygnięcie.
"""

import datetime as dt
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import pytest

from xray.engine import (
    DiagnosticTest,
    DiagnosticTestDeclaration,
    ReadinessReason,
    check_readiness,
    run_test,
)
from xray.ingest import load_table
from xray.model import FindingRecord, LogicalStatus, PeriodRef, ScopeRef
from xray.store import FindingStore, RunRef, connect

ZBIOR = "firma-syntetyczna"
ZAKRES = ScopeRef(scope_label="cała firma")
OKRES = PeriodRef(
    period_start=dt.date(2026, 1, 1),
    period_end=dt.date(2026, 1, 1),
)

PELNY = "date,unit,product,volume,revenue\n2026-01-01,Dział A,porada,10,1000\n"
BEZ_REVENUE = "date,unit,product,volume\n2026-01-01,Dział A,porada,10\n"
BEZ_UNIT = "date,product,volume,revenue\n2026-01-01,porada,10,1000\n"


def wczytaj(tmp_path: Path, tresc: str, nazwa: str = "activity.csv"):
    """Zwraca wynik importu ACTIVITY przy mapowaniu tożsamościowym."""
    sciezka = tmp_path / nazwa
    sciezka.write_text(tresc, encoding="utf-8")
    return load_table(sciezka, "ACTIVITY", dataset_id=ZBIOR)


class RequiresRevenue(DiagnosticTest):
    """Atrapa deklarująca pole **spoza klucza naturalnego**.

    NOOP-01 wymaga wyłącznie pól klucza, więc na nim nie da się pokazać rzeczy
    najważniejszej: że kontrola 1 mówi PASS, a test i tak odmawia. To są odpowiedzi na
    dwa różne pytania — „czy tabela jest strukturalnie w porządku" i „czy ja mogę wydać
    swoje twierdzenie".
    """

    DECLARATION = DiagnosticTestDeclaration(
        test_id="TESTOWY-REVENUE",
        required_tables=("ACTIVITY",),
        required_by_test={"ACTIVITY": ("revenue",)},
    )

    def run(
        self,
        data: Mapping[str, Any],
        *,
        scope: ScopeRef,
        period: PeriodRef,
    ) -> tuple[FindingRecord, ...]:
        return (
            FindingRecord.create(
                test_id=self.DECLARATION.test_id,
                scope=scope,
                period=period,
                status=LogicalStatus.NO_ADVERSE_SIGNAL,
                finding="policzone",
                metric_value=float(len(data["ACTIVITY"])),
            ),
        )


def uruchom(wynik) -> tuple[FindingRecord, ...]:
    """Uruchamia atrapę przez bramkę na jednym wyniku importu."""
    return RequiresRevenue().execute(
        {"ACTIVITY": wynik.frame},
        import_reports={"ACTIVITY": (wynik.report,)},
        scope=ZAKRES,
        period=OKRES,
    )


# --- brak pola wymaganego przez test --------------------------------------------------


def test_brak_pola_spoza_klucza_blokuje_test(tmp_path: Path) -> None:
    """Kontrola 1 ogłasza PASS, a test i tak nie wydaje wyniku. Sprzeczności nie ma."""
    wyniki = uruchom(wczytaj(tmp_path, BEZ_REVENUE))
    assert len(wyniki) == 1
    assert wyniki[0].status is LogicalStatus.TEST_BLOCKED
    assert wyniki[0].metric_value is None
    assert "revenue" in wyniki[0].finding


def test_komplet_kolumn_daje_normalny_wynik(tmp_path: Path) -> None:
    wyniki = uruchom(wczytaj(tmp_path, PELNY))
    assert wyniki[0].status is LogicalStatus.NO_ADVERSE_SIGNAL
    assert wyniki[0].metric_value == 1.0


def test_bramka_nie_zastepuje_wymaganych_walidacji(tmp_path: Path) -> None:
    """Granica bramki, znaleziona przez ten test — i celowo tu zapisana.

    ACTIVITY bez kolumny ``unit`` jest tabelą rozbitą strukturalnie: kontrola 1 daje
    CRITICAL, a wszystkie wiersze są odrzucane, bo nie da się ich przypisać do zakresu.
    Mimo to atrapa wymagająca **wyłącznie** ``revenue`` przechodzi bramkę i liczy na
    pustej ramce.

    To **nie jest** wada bramki: odpowiada ona na jedno pytanie — czy pole
    z ``required_by_test`` miało kolumnę. Egzekwowanie CRITICAL wymaganych kontroli to
    osobny mechanizm (``required_validations``), którego rozstrzygnięcie B-06 nie
    dotyczy i którego jeszcze nie ma. Wpis DT-20 nazywa tę lukę.

    Test, który realnie potrzebuje klucza, wpisuje go w ``required_by_test`` — tak robi
    NOOP-01 i dlatego na tych samych danych odmawia (niżej).
    """
    wyniki = uruchom(wczytaj(tmp_path, BEZ_UNIT))
    assert wyniki[0].status is LogicalStatus.NO_ADVERSE_SIGNAL
    assert wyniki[0].metric_value == 0.0


def test_bramka_patrzy_na_kolumny_a_nie_na_wypelnienie(tmp_path: Path) -> None:
    """Kolumna pusta w stu procentach przechodzi — to sprawa kontroli 3, nie bramki."""
    puste = "date,unit,product,volume,revenue\n2026-01-01,Dział A,porada,10,\n"
    gotowosc = RequiresRevenue.readiness(
        {"ACTIVITY": wczytaj(tmp_path, puste).frame},
        import_reports={"ACTIVITY": (wczytaj(tmp_path, puste).report,)},
    )
    assert gotowosc.ready is True


def test_pole_z_jednego_z_dwoch_plikow_wystarczy(tmp_path: Path) -> None:
    """Tabela zasilona z dwóch plików ma pole, gdy przyniósł je choć jeden."""
    z_polem = wczytaj(tmp_path, PELNY, "a.csv")
    bez_pola = wczytaj(tmp_path, BEZ_REVENUE, "b.csv")
    gotowosc = RequiresRevenue.readiness(
        {"ACTIVITY": z_polem.frame},
        import_reports={"ACTIVITY": (z_polem.report, bez_pola.report)},
    )
    assert gotowosc.ready is True


# --- trzy stany wiedzy, nie dwa -------------------------------------------------------


def test_brak_wiedzy_o_imporcie_nie_daje_wyniku(tmp_path: Path) -> None:
    """„Nie wiem" nie jest podstawą do wydania wyniku — ta sama reguła co w kontroli 1."""
    wyniki = RequiresRevenue().execute(
        {"ACTIVITY": wczytaj(tmp_path, PELNY).frame},
        import_reports={},
        scope=ZAKRES,
        period=OKRES,
    )
    assert wyniki[0].status is LogicalStatus.TEST_BLOCKED
    assert "brak raportu importu" in wyniki[0].validation_notes[0]


def test_brak_wiedzy_ma_inny_powod_niz_brak_kolumny(tmp_path: Path) -> None:
    """Odmowa mówi, **dlaczego** odmawia; inaczej klient dostałby złą instrukcję."""
    nieznane = RequiresRevenue.readiness(
        {"ACTIVITY": wczytaj(tmp_path, PELNY).frame}, import_reports={"ACTIVITY": None}
    )
    brak = RequiresRevenue.readiness(
        {"ACTIVITY": wczytaj(tmp_path, BEZ_REVENUE).frame},
        import_reports={"ACTIVITY": (wczytaj(tmp_path, BEZ_REVENUE).report,)},
    )
    assert nieznane.missing[0].reason is ReadinessReason.UNKNOWN_IMPORT
    assert brak.missing[0].reason is ReadinessReason.MISSING_COLUMN


def test_pusta_krotka_raportow_jest_zakazana(tmp_path: Path) -> None:
    """Ta sama racja co w ValidationContext: nie do odróżnienia od braku wiedzy."""
    with pytest.raises(ValueError):
        RequiresRevenue.readiness(
            {"ACTIVITY": wczytaj(tmp_path, PELNY).frame}, import_reports={"ACTIVITY": ()}
        )


def test_brak_calej_tabeli_ma_wlasny_powod() -> None:
    gotowosc = RequiresRevenue.readiness({}, import_reports={})
    assert [m.reason for m in gotowosc.missing] == [ReadinessReason.MISSING_TABLE]
    assert "nie została podana" in gotowosc.basis()


# --- bramki nie da się ominąć ---------------------------------------------------------


def test_nadpisanie_execute_jest_odrzucane() -> None:
    """Bramka, którą wolno nadpisać, jest konwencją, a nie mechanizmem."""
    with pytest.raises(TypeError) as blad:

        class Obchodzi(DiagnosticTest):
            DECLARATION = DiagnosticTestDeclaration(
                test_id="TESTOWY-OBEJSCIE", required_tables=("ACTIVITY",)
            )

            def run(self, data, *, scope, period):  # pragma: no cover - nie dojdzie
                return ()

            def execute(self, data, *, import_reports, scope, period):
                return ()

    assert "execute" in str(blad.value)


def test_nadpisanie_readiness_jest_odrzucane() -> None:
    with pytest.raises(TypeError) as blad:

        class Klamie(DiagnosticTest):
            DECLARATION = DiagnosticTestDeclaration(
                test_id="TESTOWY-KLAMIE", required_tables=("ACTIVITY",)
            )

            def run(self, data, *, scope, period):  # pragma: no cover - nie dojdzie
                return ()

            @classmethod
            def readiness(cls, data, *, import_reports):
                return None

    assert "readiness" in str(blad.value)


def test_rejestr_prowadzi_przez_bramke(tmp_path: Path) -> None:
    """NOOP-01 wymaga wyłącznie pól klucza, więc na komplecie kolumn liczy normalnie."""
    wynik = wczytaj(tmp_path, PELNY)
    wyniki = run_test(
        "NOOP-01",
        {"ACTIVITY": wynik.frame},
        import_reports={"ACTIVITY": (wynik.report,)},
        scope=ZAKRES,
        period=OKRES,
    )
    assert wyniki[0].status is LogicalStatus.NO_ADVERSE_SIGNAL

    bez_klucza = wczytaj(tmp_path, BEZ_UNIT, "bez.csv")
    zablokowane = run_test(
        "NOOP-01",
        {"ACTIVITY": bez_klucza.frame},
        import_reports={"ACTIVITY": (bez_klucza.report,)},
        scope=ZAKRES,
        period=OKRES,
    )
    assert zablokowane[0].status is LogicalStatus.TEST_BLOCKED
    assert check_readiness(
        "NOOP-01", {"ACTIVITY": bez_klucza.frame},
        import_reports={"ACTIVITY": (bez_klucza.report,)},
    ).ready is False


# --- odmowa jest wynikiem, nie śmieciem -----------------------------------------------


def test_odmowa_i_wynik_maja_ten_sam_finding_id(tmp_path: Path) -> None:
    """Pierwszy realny użytkownik klucza złożonego z pary (DT-11).

    Tożsamość wyniku to test_id + scope + period + contract_version, więc uzupełnienie
    brakującej kolumny nie tworzy nowego wyniku — tworzy nową **wersję** tego samego.
    """
    odmowa = uruchom(wczytaj(tmp_path, BEZ_REVENUE))[0]
    policzone = uruchom(wczytaj(tmp_path, PELNY, "pelny.csv"))[0]
    assert odmowa.finding_id == policzone.finding_id
    assert odmowa.status is not policzone.status


def test_historia_pokazuje_odmowe_i_uzupelnienie(tmp_path: Path) -> None:
    """Ślad ma mówić, że w przebiegu 1 nie było czym liczyć."""
    from xray.store import ExecutionRef

    bez = wczytaj(tmp_path, BEZ_REVENUE)
    pelny = wczytaj(tmp_path, PELNY, "pelny.csv")
    magazyn = FindingStore(connect(":memory:"))
    wykonanie = ExecutionRef.capture()

    pierwszy = RunRef.create(dataset_id=ZBIOR, reports=[bez.report])
    drugi = RunRef.create(dataset_id=ZBIOR, reports=[pelny.report])
    magazyn.save_run(pierwszy, uruchom(bez), wykonanie)
    magazyn.save_run(drugi, uruchom(pelny), wykonanie)

    historia = magazyn.history(uruchom(bez)[0].finding_id)
    assert len(historia) == 2
    assert {r.status for _, _, r in historia} == {
        LogicalStatus.TEST_BLOCKED,
        LogicalStatus.NO_ADVERSE_SIGNAL,
    }


def test_dwie_odmowy_daja_ten_sam_rekord(tmp_path: Path) -> None:
    """Zasada 3: odmowa jest wyliczana, nie improwizowana."""
    a = uruchom(wczytaj(tmp_path, BEZ_REVENUE, "a.csv"))[0]
    b = uruchom(wczytaj(tmp_path, BEZ_REVENUE, "b.csv"))[0]
    assert a == b


def test_odmowa_niesie_podstawe_i_flage_walidacji(tmp_path: Path) -> None:
    """Ślad, że wynik wymaga uzupełnienia danych, musi dać się odpytać, nie tylko odczytać."""
    odmowa = uruchom(wczytaj(tmp_path, BEZ_REVENUE))[0]
    assert odmowa.validation_required is True
    assert odmowa.validation_notes == (
        "tabela ACTIVITY nie miała kolumny dla pola revenue",
    )
    assert odmowa.confidence_score is None
    assert odmowa.next_tests == ()


def test_bramka_nigdy_nie_zwraca_test_partial(tmp_path: Path) -> None:
    """TEST_PARTIAL jest nieosiągalny do czasu zbudowania required_by_claim (DT-18).

    ``required_by_test`` jest deklaracją na poziomie całego testu, więc brak takiego
    pola znaczy, że test nie wyda żadnego twierdzenia. Bramka nie zgaduje wartości,
    której nie potrafi wywieść.
    """
    warianty = (BEZ_REVENUE, BEZ_UNIT, "date,unit,product\n2026-01-01,Dział A,porada\n")
    for tresc in warianty:
        wyniki = uruchom(wczytaj(tmp_path, tresc))
        assert wyniki[0].status is not LogicalStatus.TEST_PARTIAL, tresc
