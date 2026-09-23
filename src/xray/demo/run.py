# Realizuje produkt 6 z ZOP-TECH-01 v0.1 rozdz. 7 oraz kryteria odbioru 8.1–8.6.
"""Przebieg demonstracyjny na firmie syntetycznej.

Pełny łańcuch, od profilu do odczytu z magazynu:

```
generator → pięć plików (CSV + XLSX)
  → profil mapowania      → raport mapowania
  → ingest.load_table     → ramka w kontrakcie + raport importu
  → ValidationContext     → osiem kontroli
  → NOOP-01               → FindingRecord
  → RunRef + ExecutionRef → przebieg (dane) i wykonanie (kod, środowisko)
  → FindingStore          → zapis i odczyt
```

## Trzy decyzje, które nie są kosmetyczne

**Demonstracja generuje, nie czyta.** Dane powstają w katalogu tymczasowym z jawnym
ziarnem. Czytanie z ``data/`` dałoby demonstrację, która u kogoś innego nie ruszy —
``data/`` jest w ``.gitignore``, więc plików tam nie ma.

**Jeden przebieg na pięciu tabelach.** ``RunRef`` powstaje z pięciu raportów importu
i profilu, więc ``profile_digest`` i bieżąca wersja tożsamości przebiegu są tu przećwiczone
end-to-end, a nie tylko w testach jednostkowych.

**Raport mapowania trafia na ekran**, w szczególności ``plan_budget_note()``. Ogłoszenie,
którego się nie drukuje, nie jest ogłoszeniem — ta sama racja, dla której
``time_basis_used`` zostaje w wyniku kontroli 8.

Uruchomienie: ``python -m xray.demo``.
"""

import datetime as dt
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

from xray.engine import check_readiness, get_declaration, run_test
from xray.engine.base import TestReadiness
from xray.ingest import LoadResult, load_table
from xray.mapping import MappingProfile, MappingReport, apply_profile
from xray.model import FindingRecord, PeriodRef, ScopeRef, get_table, table_names
from xray.store import ExecutionRef, FindingStore, RunRef, SaveOutcome, connect
from xray.synth import GeneratedDataset, generate
from xray.validation import CheckResult, ValidationContext, run_checks

DATASET_ID = "firma-syntetyczna"
"""Zbiór danych demonstracji. Zadeklarowany, nie wyprowadzony ze ścieżki (wpis DT-10)."""

PROFILE_PATH = Path("profiles/firma-syntetyczna.yaml")

DEMO_SEED = 20260907
"""Ziarno generatora. Jawne w kodzie — bez niego przebieg nie byłby odtwarzalny."""


@dataclass(frozen=True, slots=True)
class TableRun:
    """Co się wydarzyło z jedną tabelą."""

    table_name: str
    mapping: MappingReport
    load: LoadResult
    checks: tuple[CheckResult, ...]


@dataclass(frozen=True, slots=True)
class DemoResult:
    """Wynik całego przebiegu."""

    dataset: GeneratedDataset
    profile: MappingProfile
    tables: tuple[TableRun, ...]
    findings: tuple[FindingRecord, ...]
    readiness: TestReadiness
    run: RunRef
    execution: ExecutionRef
    stored: tuple[FindingRecord, ...]
    written: SaveOutcome
    store: FindingStore = field(repr=False)

    def table(self, name: str) -> TableRun:
        """Wynik dla jednej tabeli."""
        return next(t for t in self.tables if t.table_name == name)


def _naglowki(sciezka: Path) -> list[str]:
    """Same nagłówki pliku — profil zestawia się z tym, co w pliku faktycznie jest."""
    if sciezka.suffix == ".xlsx":
        return list(pd.read_excel(sciezka, nrows=0).columns)
    return list(pd.read_csv(sciezka, nrows=0).columns)


def run_demo(
    katalog: Path,
    *,
    baza: str | Path = ":memory:",
    seed: int = DEMO_SEED,
    **skala: int,
) -> DemoResult:
    """Wykonuje pełny przebieg i zwraca wszystko, co po drodze powstało."""
    dane = generate(katalog / "dane", seed=seed, **skala)
    profil = MappingProfile.load(PROFILE_PATH)

    przebiegi: list[TableRun] = []
    for nazwa in table_names():
        plik = dane.files[nazwa]

        # 1. Mapowanie: profil zestawiony z kolumnami, które w pliku faktycznie są.
        raport_mapowania = apply_profile(profil, nazwa, _naglowki(plik))

        # 2. Import: plik → ramka w kontrakcie + raport pochodzenia i skrót treści.
        wynik = load_table(
            plik,
            nazwa,
            dataset_id=DATASET_ID,
            column_map=raport_mapowania.column_map,
            organization_timezone=profil.organization_timezone,
        )

        # 3. Kontrole: stan wiedzy o tabeli, nie sama ramka.
        kontekst = ValidationContext(
            table=get_table(nazwa),
            frame=wynik.frame,
            import_reports=(wynik.report,),
            mapping_reports=(raport_mapowania,),
        )
        przebiegi.append(
            TableRun(
                table_name=nazwa,
                mapping=raport_mapowania,
                load=wynik,
                checks=run_checks(kontekst),
            )
        )

    tabele = tuple(przebiegi)
    activity = next(t for t in tabele if t.table_name == "ACTIVITY").load.frame

    # 4. Test diagnostyczny. NOOP-01 nie niesie treści metodologicznej.
    #
    # Przez run_test, nie przez get_test(...)().run(...): to drugie omijało bramkę
    # gotowości, więc test wykonałby się także wtedy, gdyby ACTIVITY przyszło bez
    # kolumny dla pola z required_by_test (rozstrzygnięcie B-06).
    daty = sorted(activity["date"])
    okres = PeriodRef(period_start=daty[0], period_end=daty[-1])
    wiedza_o_imporcie = {t.table_name: (t.load.report,) for t in tabele}
    zakres = ScopeRef(scope_label="cała firma")
    gotowosc = check_readiness("NOOP-01", {"ACTIVITY": activity}, import_reports=wiedza_o_imporcie)
    wyniki = run_test(
        "NOOP-01",
        {"ACTIVITY": activity},
        import_reports=wiedza_o_imporcie,
        scope=zakres,
        period=okres,
    )

    # 5. Przebieg — na jakich danych — i wykonanie — jakim kodem i w jakim środowisku.
    #    Czas trafia wyłącznie do wykonania, jako pole audytowe poza odciskiem (DT-21).
    przebieg = RunRef.create(
        dataset_id=DATASET_ID,
        reports=[t.load.report for t in tabele],
        profile=profil,
    )
    wykonanie = ExecutionRef.capture(executed_at=dt.datetime.now())
    magazyn = FindingStore(connect(baza))
    zapis = magazyn.save_run(przebieg, wyniki, wykonanie)

    # 6. Odczyt: rekord sam potwierdza swoją tożsamość.
    return DemoResult(
        dataset=dane,
        profile=profil,
        tables=tabele,
        findings=wyniki,
        readiness=gotowosc,
        run=przebieg,
        execution=wykonanie,
        stored=magazyn.load_run(przebieg.run_id),
        written=zapis,
        store=magazyn,
    )


def opisz(wynik: DemoResult) -> str:
    """Buduje czytelny opis przebiegu."""
    linie = [
        "=" * 78,
        "X-RAY — demonstracja przebiegu na firmie syntetycznej",
        "ZOP-TECH-01, produkt 6 z rozdz. 7",
        "=" * 78,
        "",
        "1. GENEROWANIE ZBIORU SYNTETYCZNEGO",
        f"   ziarno          : {wynik.dataset.seed}",
        f"   miesięcy        : {wynik.dataset.months}",
        f"   jednostek       : {len(wynik.dataset.units)}",
        f"   zasobów         : {len(wynik.dataset.units) * wynik.dataset.resources_per_unit}",
        f"   katalog         : {wynik.dataset.directory}",
    ]
    for nazwa in table_names():
        plik = wynik.dataset.files[nazwa]
        linie.append(f"   {nazwa:<9} → {plik.name}")

    linie += [
        "",
        "2. PROFIL I MAPOWANIE",
        f"   profil          : {wynik.profile.profile_id} v{wynik.profile.profile_version}",
        f"   strefa          : {wynik.profile.organization_timezone}",
        "",
        f"   {wynik.tables[0].mapping.plan_budget_note()}",
        "",
    ]
    for tabela in wynik.tables:
        m = tabela.mapping
        linie.append(f"   {tabela.table_name:<9} zmapowanych pól: {len(m.mapped)}")
        if m.unmapped_columns:
            opis = ", ".join(m.unmapped_columns)
            linie.append(f"       kolumny bez miejsca w kontrakcie: {opis}")
        if m.fields_without_mapping:
            linie.append(f"       pola bez przypisania: {', '.join(m.fields_without_mapping)}")
        if m.declared_missing_columns:
            opis = ", ".join(f"{p} → {k}" for p, k in m.declared_missing_columns)
            linie.append(f"       przypisania do nieistniejących kolumn: {opis}")
        if m.materialized_empty:
            linie.append(f"       zmaterializowane jako puste: {', '.join(m.materialized_empty)}")
        if m.shared_source_columns:
            opis = ", ".join(f"{k} → {', '.join(p)}" for k, p in m.shared_source_columns)
            linie.append(f"       kolumny zasilające kilka pól: {opis}")

    linie += ["", "3. IMPORT"]
    for tabela in wynik.tables:
        r = tabela.load.report
        linie.append(
            f"   {tabela.table_name:<9} przyjęto {r.records_accepted:>5}, "
            f"odrzucono {r.records_rejected:>3}   skrót treści: {r.content_digest}"
        )
        linie.append(
            f"       strefa: {r.organization_timezone or '— (nie zadeklarowano)'}, "
            f"przeliczono znaczników: {r.timestamps_converted}, "
            f"godzin niejednoznacznych: {r.ambiguous_local_time_count}"
        )
        for odrzucenie in r.rejections[:3]:
            linie.append(
                f"       ! wiersz {odrzucenie.file_row} ({odrzucenie.category.value}): "
                f"{odrzucenie.reason[:60]}"
            )

    linie += ["", "4. KONTROLE DANYCH (osiem kontroli z pkt 5.3)"]
    for tabela in wynik.tables:
        statusy = []
        for kontrola in tabela.checks:
            numer = kontrola.control_number
            if kontrola.status is not None:
                statusy.append(f"{numer}:{kontrola.status.value}")
            else:
                statusy.append(f"{numer}:{kontrola.not_assessed_reason.value}")
        linie.append(f"   {tabela.table_name:<9} {'  '.join(statusy)}")

    zdarzeniowa = wynik.table("PROCESS")
    czas = next(k for k in zdarzeniowa.checks if k.check_id == "TECH01-VAL-08")
    linie += ["", "   PROCESS — rozróżnienie z rozstrzygnięcia A-01:"]
    for obserwacja in czas.observations:
        if obserwacja.measure in (
            "months_with_stage_starts",
            "months_with_stage_ends",
            "time_basis_used",
        ):
            wartosc = "—" if obserwacja.is_unknown else obserwacja.value
            linie.append(f"       {obserwacja.measure:<26} = {wartosc}")

    deklaracja = get_declaration("NOOP-01")
    wymagane = ", ".join(
        f"{tabela}.{pole}" for tabela, pola in deklaracja.required_by_test.items() for pole in pola
    )
    linie += [
        "",
        "5. TEST DIAGNOSTYCZNY",
        f"   required_by_test: {wymagane}",
        f"   bramka gotowości: {'gotowy' if wynik.readiness.ready else 'ODMOWA'} "
        f"— {wynik.readiness.basis()}",
    ]
    for finding in wynik.findings:
        linie += [
            f"   test            : {finding.test_id}",
            f"   status          : {finding.status.value}",
            f"   metric_value    : {finding.metric_value}",
            f"   okres           : {finding.period.period_start} — {finding.period.period_end}",
            f"   next_tests      : {finding.next_tests or '(brak)'}",
            f"   pewność         : score={finding.confidence_score} "
            f"class={finding.confidence_class}",
            f"   finding_id      : {finding.finding_id}",
        ]

    wykonanie = wynik.execution
    git = wykonanie.code_provenance
    opis_gita = git.get("git_status", "—")
    if "head_commit" in git:
        opis_gita += f" (HEAD {git['head_commit'][:12]})"
    linie += [
        "",
        "6. ZAPIS I ODCZYT",
        f"   run_id          : {wynik.run.run_id}",
        f"   profile_digest  : {wynik.run.profile_digest}",
        f"   wersja tożsam.  : przebieg {wynik.run.identity_algorithm_version}, "
        f"wynik {wynik.findings[0].identity_algorithm_version}",
        f"   wejść przebiegu : {len(wynik.run.inputs)}",
        f"   odcisk wykonania: {wykonanie.execution_fingerprint or '— (nieznany)'}",
        f"   status odcisku  : {wykonanie.fingerprint_status.value}",
        f"   git (opis)      : {opis_gita}",
        f"   próba wykonania : {wynik.written.execution_attempt_id}",
        f"   opis wykonania  : "
        f"{'nowy' if wynik.written.execution_described_now else 'już zapisany'}"
        f", wyników: {wynik.written.findings_written}",
        f"   odczytano       : {len(wynik.stored)} rekordów",
        f"   identyczne      : {'tak' if wynik.stored == wynik.findings else 'NIE'}",
        "",
        "=" * 78,
    ]
    return "\n".join(linie)


def main() -> None:
    """Uruchamia demonstrację w katalogu tymczasowym.

    Wyjście przestawiamy na UTF-8: domyślne kodowanie konsoli Windows (cp1250) nie zna
    znaków, których używa opis, i przerywa wypisywanie wyjątkiem. Demonstracja ma się
    uruchomić u odbiorcy, a nie tylko u autora — ``errors="replace"`` gwarantuje, że
    nieobsłużony znak zamieni się w znak zastępczy, a nie w przerwany przebieg.
    """
    import sys
    import tempfile

    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8", errors="replace")

    with tempfile.TemporaryDirectory() as katalog:
        print(opisz(run_demo(Path(katalog))))
