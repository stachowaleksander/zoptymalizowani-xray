# Sprawdza zamknięte słowniki z ZOP-TECH-01 pkt 5.3/5.4, ZOP-CONF-01 pkt 2.2
# oraz statusy logiczne kart Core 10.
"""Testy słowników wartości.

Te testy nie sprawdzają logiki — pilnują, żeby katalog wartości nie rozjechał się
z kartą po cichu. Jeżeli ktoś dopisze wartość „z rozsądku", test to pokaże.
"""

from xray.model.enums import ConfidenceClass, LogicalStatus, TimeGrain, ValidationStatus


def test_validation_status_ma_dokladnie_trzy_wartosci() -> None:
    """FIN-01 rozdz. 3: każda kontrola zwraca PASS, WARNING albo CRITICAL."""
    assert {s.value for s in ValidationStatus} == {"PASS", "WARNING", "CRITICAL"}


def test_logical_status_zawiera_wspolny_katalog_osmiu_wartosci() -> None:
    """Wspólny katalog wg PROC-02 pkt 16.1, PORT-01 13.1, PROC-01 12.1, FIN-03 rozdz. 14."""
    wspolny = {
        "NO_ADVERSE_SIGNAL",
        "ADVERSE_SIGNAL",
        "INCIDENT",
        "DETERIORATING",
        "STABLE",
        "IMPROVING",
        "TEST_PARTIAL",
        "TEST_BLOCKED",
    }
    assert wspolny <= {s.value for s in LogicalStatus}


def test_logical_status_zawiera_short_term_deviation() -> None:
    """FIN-01 pkt 12.2 i CAP-01 rozdz. 7 używają wartości spoza wspólnego katalogu."""
    assert LogicalStatus.SHORT_TERM_DEVIATION.value == "SHORT_TERM_DEVIATION"


def test_logical_status_nie_zawiera_slownika_priorytetu() -> None:
    """STANDARD/MEDIUM/HIGH/CRITICAL to nie jest status logiczny.

    ZOP-TECH-01 pkt 5.4 przypisuje ten słownik polu ``status``, ale ZOP-PRI-01 v1.0
    go nie zawiera, a FIN-01 pkt 12.2 nazywa statusy diagnostycznymi, „nie wynikiem
    globalnej priorytetyzacji". Patrz docs/otwarte-kontrakty.md wpis B-02.
    """
    wartosci = {s.value for s in LogicalStatus}
    assert wartosci.isdisjoint({"STANDARD", "MEDIUM", "HIGH", "CRITICAL"})


def test_logical_status_nie_zawiera_volatile_ani_seasonal() -> None:
    """CAP-01 ma wiersz „VOLATILE / SEASONAL" o niejasnej liczbie wartości.

    Świadomie nie zgadujemy — wpis B-02. Test pilnuje, żeby nikt nie dopisał ich
    bez rozstrzygnięcia karty.
    """
    wartosci = {s.value for s in LogicalStatus}
    assert wartosci.isdisjoint({"VOLATILE", "SEASONAL", "VOLATILE / SEASONAL"})


def test_confidence_class_ma_katalog_z_conf_01() -> None:
    """CONF-01 pkt 2.2 „Wspólny katalog klas" — pięć wartości, bez A/B/C."""
    assert {c.value for c in ConfidenceClass} == {
        "well_supported",
        "supported_with_limitations",
        "partially_supported",
        "weakly_supported",
        "not_assessable",
    }


def test_confidence_class_nie_zawiera_a_b_c() -> None:
    """ZOP-TECH-01 pkt 5.4 mówi „A / B / C"; CONF-01 takich wartości nie zna (wpis B-03)."""
    assert {c.value for c in ConfidenceClass}.isdisjoint({"A", "B", "C"})


def test_time_grain_rozroznia_okres_od_zdarzenia() -> None:
    """Cztery tabele są okresowe, PROCESS jest zdarzeniowa — wpis A-01."""
    assert {g.value for g in TimeGrain} == {"period", "event"}
