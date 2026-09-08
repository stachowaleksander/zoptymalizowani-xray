# Realizuje ZOP-TECH-01 v0.1 pkt 5.5 — nazewnictwo firmy syntetycznej.
"""Kanoniczny słownik nazw i nagłówków.

## Jedno źródło nazw dla całego generatora

Kontrola 6 pracuje **w obrębie tabeli**, więc „Dział A" w COST i „Dzial A" w RESOURCE
nie uruchomiłyby jej — a dane byłyby niespójne przy pierwszym łączeniu tabel i nikt by
tego nie zobaczył. Dlatego nazwy nie są składane w miejscu użycia.

## Nagłówki są tutaj, a nie czytane z profilu

Wyprowadzenie nagłówków z ``profiles/firma-syntetyczna.yaml`` sprawiłoby, że zawsze by
pasowały — i zamieniłoby szew mapowania w tautologię, dokładnie jak mapowanie
tożsamościowe. Gwarancją, której chcemy, nie jest „zawsze pasują", tylko **„rozjazd jest
głośny"**: nagłówki i profil pisane osobno mogą się rozjechać, a wtedy kontrola 1 zapali
to widocznie na firmie syntetycznej.

Nagłówki są celowo „klienckie" — polskie, bez diakrytyki, jak w eksporcie z systemu.
Żaden nie równa się nazwie pola kontraktu; gdyby się równał, mapowanie w tym miejscu
przestałoby czegokolwiek dowodzić.
"""

UNITS: tuple[str, ...] = (
    "Dział A",
    "Dział B",
    "Dział C",
    "Dział D",
    "Dział E",
)
"""Jednostki organizacyjne. Te same we wszystkich pięciu tabelach."""

PRODUCTS: tuple[str, ...] = (
    "Konsultacja",
    "Badanie",
    "Zabieg",
    "Pakiet roczny",
)

COST_CATEGORIES: tuple[str, ...] = (
    "Wynagrodzenia",
    "Materiały",
    "Usługi obce",
    "Amortyzacja",
)

RECONCILED_CATEGORY = "Wynagrodzenia"
"""Kategoria kosztowa uzgadniana z sumą kosztów zasobów jednostki w miesiącu.

Bez tego powiązania suma ``RESOURCE.cost`` nie zgadzałaby się z żadną kategorią COST,
a ZOP-XR-MGT-01 — karta od uzgodnień — znalazłaby ``unreconciled`` **z konstrukcji
generatora**. To byłby zaszyty problem wg kryterium z pkt 5.5.4, choćby nikt go świadomie
nie zaszywał.
"""

PLAN_METRICS: tuple[str, ...] = (
    "Koszt calkowity",
    "Przychod calkowity",
    "Liczba wykonan",
)
"""Nazwy wskaźników planu — tekst z danych klienta, bez normalizacji.

Profil nie deklaruje dla nich zgodności definicji (``plan_metrics: []``), więc PLAN nie
może posłużyć jako ``reference_type = plan_budget``. Rozstrzygnięcie B-04.
"""

STAGES: tuple[str, ...] = (
    "Rejestracja",
    "Realizacja",
    "Rozliczenie",
    "Zamknięcie",
)
"""Etapy procesu **w kolejności następstwa**.

Kolejność nie jest ozdobą: etap zaczyna się nie wcześniej, niż kończy się poprzedni.
Żadna z ośmiu kontroli nie sprawdza następstwa etapów (klucz to ``case_id + stage``),
więc odwrócona kolejność byłaby dziś niewidoczna, a ZOP-XR-PROC-01 znalazłaby ją jako
pierwszą rzecz.
"""


def resource_name(unit: str, index: int) -> str:
    """Nazwa zasobu. Zawiera jednostkę, więc zasoby nie mylą się między działami."""
    return f"{unit} / stanowisko {index:02d}"


HEADERS: dict[str, dict[str, str]] = {
    "ACTIVITY": {
        "date": "Miesiac",
        "unit": "Komorka",
        "product": "Usluga",
        "volume": "Liczba_wykonan",
        "revenue": "Przychod_netto",
    },
    "COST": {
        "date": "Miesiac",
        "unit": "Komorka",
        "category": "Rodzaj_kosztu",
        "amount": "Kwota",
    },
    "RESOURCE": {
        "date": "Miesiac",
        "unit": "Komorka",
        "resource": "Zasob",
        "available": "Godziny_dostepne",
        "used": "Godziny_wykorzystane",
        "cost": "Koszt_zasobu",
    },
    "PROCESS": {
        "case_id": "Nr_sprawy",
        "stage": "Etap",
        "start": "Poczatek",
        "end": "Koniec",
        "unit": "Komorka",
    },
    "PLAN": {
        "date": "Miesiac",
        "unit": "Komorka",
        "metric": "Wskaznik",
        "target": "Wartosc_planu",
    },
}
"""Pole kontraktu → nagłówek w pliku. Ten sam kierunek co profil mapowania."""

EXTRA_COLUMNS: dict[str, tuple[str, ...]] = {
    "RESOURCE": ("Kod_MPK",),
}
"""Kolumny, dla których kontrakt nie ma miejsca.

Bez nich element „kolumny niezmapowane" raportu mapowania nie zostałby przećwiczony.
Kosztują zero: żadna z ośmiu kontroli ich nie widzi, PASS zostaje PASS.
"""
