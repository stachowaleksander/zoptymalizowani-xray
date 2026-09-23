# C-T13 — część wykazana i decyzja STOP R1-S16 (karta V12-R1 §16 i §16.1).
"""Granica między tożsamością fizyczną a tożsamością wyniku.

## Dlaczego ten plik nie zamyka C-T13

Scenariusz C-T13 „PHYSICAL RESERIALIZATION WITH RECORD EXCLUSION" ma w karcie §16 expected
z wbudowanym wyjściem awaryjnym: „physical IDs may differ; result_identity unchanged;
**if new orphan machinery required => STOP R1-S16**".

Rozstrzygnięcie zapadło **czytaniem, przed implementacją**, zgodnie z §16.1. Ustalenie:
scenariusza nie da się wykazać w całości na istniejącym conformant behavior, bo wymaga
podmiotu, którego w kodzie nie ma — **fizycznej tożsamości rekordu**. Nie ma
``record_id`` ani ``source_row_id``; jedyna tożsamość fizyczna w kodzie to ``source_id``
na poziomie **pliku** (``ingest/report.py``). Wyłączenie rekordu, po którym reimport
osierociłby podmiot, nie ma się do czego przypiąć.

Zbudowanie tej domeny znaczyłoby wprowadzenie nowego rodzaju tożsamości, którego żadna
runda V12-R1–R7 nie przypisuje do R1: v1.2 §17 traktuje „Physical record/source-row
identity" jako **zachowywaną z v1.1 bez zmian** (a u nas jej nie ma), a V12-R6 obejmuje
obserwowalność osieroceń, nie wydawanie identyfikatorów rekordów. To jest dokładnie
przesłanka **STOP R1-S16**: „Domknięcie R1 wymaga implementacji V12-R2/R3/R4/R5/R6 albo
innej przyszłej rundy".

Dlatego nie implementujemy niczego i nie udajemy, że wektor przeszedł. Poniżej zostaje
wyłącznie ta część, którą **da się** wykazać bez żadnej nowej maszynerii — i jest ona
wykazana uczciwie, jako część, nie jako całość.
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

ZBIOR = "klient-testowy"
KOSZTY = (
    "date,unit,category,amount\n"
    "2026-01-01,Dział A,wynagrodzenia,100\n"
)

PYTANIE = ResultIdentityV2(
    test_id="FIN-01",
    test_contract_version="ZOP-XR-FIN-01 v1.0",
    scope_id=scope_id(ScopeDefinition(population=["Dział A"])),
    analysis_period=CanonicalPeriod(
        start_inclusive=dt.date(2026, 1, 1), end_exclusive=dt.date(2026, 2, 1)
    ),
    calculation_component_ref=ComponentRef(
        ComponentType.EXECUTION_COMPONENT, "FIN01-EC-DYNAMICS"
    ),
)


def test_ct13_czesc_tozsamosc_fizyczna_nie_dotyka_tozsamosci_wyniku(tmp_path: Path):
    """C-T13, część wykazana: inny plik, ta sama treść → inna tożsamość fizyczna,
    nietknięta tożsamość wyniku.

    Invariant z v1.2 §7.2: ``PHYSICAL_RECORD_ID_AFFECTS_RESULT_IDENTITY = false``,
    ``PHYSICAL_SOURCE_BYTES_AFFECT_RESULT_IDENTITY = false``,
    ``PHYSICAL_RESERIALIZATION_ALONE_AFFECTS_RESULT_IDENTITY = false``.

    **Czego ten test nie pokazuje:** wyłączenia rekordu ani jego osierocenia po reimporcie.
    Powód w docstringu modułu — STOP R1-S16.
    """
    pierwszy = tmp_path / "koszty.csv"
    drugi = tmp_path / "koszty-po-reimporcie.csv"
    for sciezka in (pierwszy, drugi):
        sciezka.write_text(KOSZTY, encoding="utf-8")

    a = load_table(pierwszy, "COST", dataset_id=ZBIOR).report
    b = load_table(drugi, "COST", dataset_id=ZBIOR).report

    # tożsamość fizyczna źródła się zmienia…
    assert a.source.source_id != b.source.source_id
    # …treść semantyczna nie…
    assert a.content_digest == b.content_digest
    # …a tożsamość pytania diagnostycznego nie ma z tym nic wspólnego
    assert result_identity(PYTANIE) == result_identity(PYTANIE)
    assert "source" not in str(PYTANIE.payload())


def test_ct13_brak_domeny_tozsamosci_rekordu_fizycznego():
    """Dowód do STOP R1-S16: podmiotu scenariusza nie ma w kodzie.

    Gdyby ``record_id`` albo ``source_row_id`` istniały, C-T13 dałoby się wykazać w całości
    i ten test by padł — a wtedy trzeba by wrócić do decyzji, nie do implementacji.
    """
    import xray.ingest.report as raport
    import xray.model.findings.finding as wynik

    pola_zrodla = set(raport.SourceRef.model_fields)
    assert "record_id" not in pola_zrodla
    assert "source_row_id" not in pola_zrodla
    assert not [p for p in wynik.FindingRecord.model_fields if "record_id" in p]
