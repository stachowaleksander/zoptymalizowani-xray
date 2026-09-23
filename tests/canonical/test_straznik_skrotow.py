# Strażnik: dodanie profilu XR_IDENTITY_CANONICAL_JSON_V1 nie rusza istniejących skrótów.
"""Wartości przypięte na sztywno, policzone przed dodaniem nowego profilu.

Karta V12-R1 §1 ustala ``HISTORICAL_IDENTITY_REWRITE = false``, a BIND-01 v1.1 §7 mówi, że
profil „nie zastępuje generatorów syntetycznych, content digestów, profile_digest ani
innych skrótów niezwiązanych z poniższymi identity". Ten plik zamienia oba zdania
w test: gdyby ktoś kiedyś „przy okazji ujednolicił" ``canonical_form``, padnie tutaj,
a nie dopiero przy porównaniu dwóch wygenerowanych firm.

Wartości pochodzą z uruchomienia na commicie 155e360 (baseline V12-R1), przed utworzeniem
pakietu ``xray.canonical``.
"""

import datetime as dt

from xray.canonical import digest
from xray.model.findings.identity import canonical_form, compute_id
from xray.synth.values import scaled, symmetric_noise, unit_interval


def test_canonical_form_zachowuje_postac():
    assert canonical_form({"b": 1, "a": "x"}) == '{"a":"x","b":1}'


def test_canonical_form_nadal_splaszcza_date_do_lancucha():
    """To nie jest usterka do naprawienia w tym pakiecie — to jest powód, dla którego
    nowy profil powstał **obok**. Stary zapis niesie istniejące tożsamości i musi zostać
    taki, jaki jest; rozróżnienie daty od tekstu ma nowy profil (patrz test niżej)."""
    assert canonical_form({"data": dt.date(2026, 9, 1), "tekst": "2026-09-01"}) == (
        '{"data":"2026-09-01","tekst":"2026-09-01"}'
    )


def test_nowy_profil_rozroznia_to_czego_stary_nie_rozroznia():
    assert digest(dt.date(2026, 9, 1)) != digest("2026-09-01")


def test_compute_id_zachowuje_wartosc():
    assert compute_id("FND", {"test_id": "NOOP-01", "n": 1}) == (
        "FND-56d82380808b176ad40f891f5deae734"
    )


def test_wartosci_generatora_zachowuja_sie():
    """Generator liczy wartości z ``canonical_form``: zmiana kanonizacji zmieniłaby dane
    przy tym samym ziarnie, czyli złamała powtarzalność z wpisu DT-23."""
    assert unit_interval(7, "COST", 3, "amount") == 0.1789404381152043
    assert unit_interval(7, "PLAN", 0, "metric") == 0.8139281964092584
    assert symmetric_noise(7, 0.25, "COST", 3) == 0.09096600331167443
    assert scaled(7, 1000.0, 0.1, "RESOURCE", 2) == 1011.7516934739185
