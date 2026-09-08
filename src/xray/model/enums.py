# Implementuje ZOP-TECH-01 v0.1 pkt 5.3 (statusy walidacji) i pkt 5.4 (pola FINDINGS)
# oraz zamknięte katalogi ZOP-CONF-01 v1.0 pkt 2.2 i statusy logiczne kart Core 10.
"""Zamknięte słowniki wartości używane w całym X-Ray.

Każda wartość ma źródło w karcie. Nie dopisujemy tu wartości „z rozsądku" — jeżeli
karta czegoś nie definiuje, trafia to do ``docs/otwarte-kontrakty.md``, a nie do enumu.

Dlaczego ``StrEnum``: wartość jest jednocześnie napisem, więc zapis do SQLite, Parquet
i JSON nie wymaga konwersji, a porównanie ``status == "NO_ADVERSE_SIGNAL"`` w teście
działa wprost. To wygoda techniczna, nie decyzja metodologiczna.
"""

from enum import StrEnum


class TimeGrain(StrEnum):
    """Ziarno czasowe tabeli — opis techniczny, nie kategoria z karty.

    Cztery tabele bazowe niosą agregaty okresowe i mają ``date`` jako etykietę okresu.
    PROCESS niesie zdarzenia i ma czas rzeczywisty w ``start`` / ``end``. To rozróżnienie
    decyduje o sposobie wykonania kontroli 8 (zakres czasowy) z ZOP-TECH-01 pkt 5.3.

    Patrz: docs/otwarte-kontrakty.md, wpis A-01 (etykieta okresu dla PROCESS).
    """

    PERIOD = "period"
    EVENT = "event"


class ValidationStatus(StrEnum):
    """Wynik pojedynczej kontroli danych.

    Źródło: ZOP-TECH-01 pkt 5.3 oraz zgodnie ZOP-XR-FIN-01 v1.0 rozdz. 3 i
    ZOP-XR-CAP-01 v1.0 rozdz. 4 — „każda kontrola zwraca PASS, WARNING albo CRITICAL".

    Walidator sam niczego nie blokuje: ogłasza status. To test deklaruje, które kontrole
    są dla niego wymagane i co oznacza ich CRITICAL (TEST_BLOCKED / TEST_PARTIAL).
    """

    PASS = "PASS"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class LogicalStatus(StrEnum):
    """Status logiczny wyniku diagnostycznego — pole ``status`` w FINDINGS.

    Źródło wspólnego katalogu: ZOP-XR-PROC-02 v1.0 pkt 16.1 („zachowuje wspólny
    katalog"), identycznie ZOP-XR-PORT-01 pkt 13.1, ZOP-XR-PROC-01 pkt 12.1,
    ZOP-XR-FIN-03 rozdz. 14, ZOP-XR-CAP-02 rozdz. 21, ZOP-XR-MGT-01 rozdz. 16.
    ``SHORT_TERM_DEVIATION`` pochodzi z ZOP-XR-FIN-01 pkt 12.2 i ZOP-XR-CAP-01 rozdz. 7.

    To NIE jest priorytet. FIN-01 pkt 12.2: „to statusy diagnostyczne, nie wynik
    globalnej priorytetyzacji". CAP-02 rozdz. 21: „CRITICAL pozostaje wyłącznie wynikiem
    walidacji danych". Priorytet nadaje ZOP-PRI-01 we własnych polach.

    # DECYZJA (Michał, 2026-09-05), wpis B-02: słownik STANDARD / MEDIUM / HIGH /
    # CRITICAL z ZOP-TECH-01 pkt 5.4 jest zapisem historycznym i został WYCOFANY.
    # Nie implementujemy go jako priorytetu — ani jako wartości tego pola, ani jako
    # osobnego pola. ``status`` niesie status logiczny; priorytet mieszka wyłącznie
    # w kontraktach ZOP-PRI-01.
    # DECYZJA (Michał, 2026-09-05), wpis B-02: ``VOLATILE`` i ``SEASONAL``
    # z ZOP-XR-CAP-01 rozdz. 7 pozostają poza enumem do czasu implementacji CAP-01.
    # Karta zapisuje je w jednym wierszu „VOLATILE / SEASONAL" i nie wynika z niej,
    # czy to jedna wartość, czy dwie — nie zgadujemy.
    """

    NO_ADVERSE_SIGNAL = "NO_ADVERSE_SIGNAL"
    ADVERSE_SIGNAL = "ADVERSE_SIGNAL"
    INCIDENT = "INCIDENT"
    SHORT_TERM_DEVIATION = "SHORT_TERM_DEVIATION"
    DETERIORATING = "DETERIORATING"
    STABLE = "STABLE"
    IMPROVING = "IMPROVING"
    TEST_PARTIAL = "TEST_PARTIAL"
    TEST_BLOCKED = "TEST_BLOCKED"


class ConfidenceClass(StrEnum):
    """Klasa pewności twierdzenia diagnostycznego.

    Źródło: ZOP-CONF-01 v1.0 pkt 2.2 „Wspólny katalog klas".

    Katalog jest jakościowy i nie jest skalą punktową — CONF-01 pkt 2.2 zawiera zakaz:
    „confidence_score = null. CONF-01 nie tworzy wyniku 0–100, wag, średniej ważonej,
    arbitralnych progów ani katalogu HIGH/MEDIUM/LOW". Kolejność członków poniżej jest
    kolejnością zapisu w karcie i NIE oznacza porządku, po którym wolno sortować,
    uśredniać ani agregować.

    # DECYZJA (Michał, 2026-09-05), wpis B-03: klas „A / B / C" z ZOP-TECH-01 pkt 5.4
    # NIE implementujemy — to zapis nieaktualny. Obowiązuje katalog z CONF-01 pkt 2.2.
    # Rozdzielenie pewności na miarę, wynik i mechanizm zostaje zgodnie z CONF-01
    # pkt 2.1: klasy per poziom mieszkają w ClaimRecord.
    """

    WELL_SUPPORTED = "well_supported"
    SUPPORTED_WITH_LIMITATIONS = "supported_with_limitations"
    PARTIALLY_SUPPORTED = "partially_supported"
    WEAKLY_SUPPORTED = "weakly_supported"
    NOT_ASSESSABLE = "not_assessable"


# --- katalogi ZOP-CONF-01 v1.0 ------------------------------------------------------


class ClaimType(StrEnum):
    """Poziom twierdzenia diagnostycznego. Źródło: ZOP-CONF-01 v1.0 rozdz. 3.

    Trzy poziomy są niezależne. CONF-01 pkt 2.1 podaje przykład rozdzielenia:
    miara ``well_supported``, wynik ``well_supported``, mechanizm ``weakly_supported``.
    """

    METRIC_CLAIM = "metric_claim"
    FINDING_CLAIM = "finding_claim"
    MECHANISM_CLAIM = "mechanism_claim"


class ConfidenceSourceLevel(StrEnum):
    """Poziom, z którego pochodzi klasa pewności. Źródło: ZOP-CONF-01 rozdz. 3, tabela
    ``claim_type`` → ``confidence_class_source_level``.

    CONF-01 QCONF01-183: „Klasa nie jest kopiowana automatycznie między poziomami".
    Pole istnieje po to, żeby przy każdej przekazanej klasie było wiadomo, czego dotyczy.
    """

    METRIC_CONFIDENCE = "metric_confidence"
    FINDING_CONFIDENCE = "finding_confidence"
    MECHANISM_CONFIDENCE = "mechanism_confidence"


class EvidenceRole(StrEnum):
    """Rola dowodu wobec twierdzenia. Źródło: ZOP-CONF-01 v1.0 pkt 4.1.

    Role nie są skalą i nie sumują się w głosy. ``supporting_evidence`` nie zastępuje
    braku ``primary_evidence``, a ``contradictory_evidence`` pozostaje widoczny także
    przy wysokiej klasie pewności.

    CONF-01 pkt 4.1: „Brak dowodu wspierającego nie jest dowodem przeciwnym".
    """

    PRIMARY_EVIDENCE = "primary_evidence"
    SUPPORTING_EVIDENCE = "supporting_evidence"
    CONTEXTUAL_EVIDENCE = "contextual_evidence"
    CONTRADICTORY_EVIDENCE = "contradictory_evidence"
    VALIDATION_EVIDENCE = "validation_evidence"


class EvidenceIndependenceStatus(StrEnum):
    """Niezależność pochodzenia dowodów. Źródło: ZOP-PRI-01 v1.0 pkt 5.2.

    CONF-01 rozdz. 9: „Dwa źródła nie oznaczają automatycznie well_supported".
    """

    DOCUMENTED_INDEPENDENT = "documented_independent"
    PARTLY_SHARED = "partly_shared"
    SHARED_SOURCE = "shared_source"
    UNKNOWN = "unknown"


# --- katalogi wartości odniesienia (ZOP-XR-FIN-01 v1.0 pkt 6.1) ---------------------


class ReferenceType(StrEnum):
    """Rodzaj wartości odniesienia. Źródło: ZOP-XR-FIN-01 v1.0 pkt 6.1.

    Kolejność członków odpowiada kolejności źródeł z FIN-01 rozdz. 6 (od historii
    własnej organizacji do benchmarku zewnętrznego). Kolejność opisuje preferencję
    metodologiczną karty, a NIE jest skalą, po której wolno sortować ani agregować.
    """

    OWN_HISTORY = "own_history"
    COMPARABLE_PERIOD = "comparable_period"
    PLAN_BUDGET = "plan_budget"
    INTERNAL_PEER = "internal_peer"
    BEST_OWN_PERIOD = "best_own_period"
    EXTERNAL_BENCHMARK = "external_benchmark"


# --- katalogi ZOP-PRI-01 v1.0 -------------------------------------------------------


class ProblemPriorityAction(StrEnum):
    """Kolejność uwagi zarządczej wobec problemu. Źródło: ZOP-PRI-01 v1.0 rozdz. 8.

    Katalog zamknięty. PRI-01 pkt 8.1: „Katalog nie wprowadza progów kwotowych,
    procentowych ani wag". Pierwsze cztery działania wymagają
    ``problem_priority_basis_status = sufficient``; ``insufficient`` prowadzi do
    ``not_assessable``.
    """

    REVIEW_NOW = "review_now"
    REVIEW_NEXT = "review_next"
    PLAN_REVIEW = "plan_review"
    OBSERVE = "observe"
    NOT_ASSESSABLE = "not_assessable"


class ValidationPriorityAction(StrEnum):
    """Pilność uzupełnienia lub weryfikacji informacji. Źródło: ZOP-PRI-01 rozdz. 8.

    PRI-01 pkt 8.2: „Kwalifikacja nie zależy od progu liczbowego ani od przyszłego
    Confidence Score".
    """

    VALIDATE_NOW = "validate_now"
    VALIDATE_NEXT = "validate_next"
    VALIDATE_WHEN_NEEDED = "validate_when_needed"
    NO_ADDITIONAL_VALIDATION = "no_additional_validation"
    NOT_ASSESSABLE = "not_assessable"


class ManagementAttentionRoute(StrEnum):
    """Trasa dalszego postępowania. Źródło: ZOP-PRI-01 v1.0 rozdz. 8.

    PRI-01 pkt 3.4: trasa „nie ma liniowego porządku" i nie służy do obliczania
    stabilności priorytetu. To nie jest ranking.
    """

    REVIEW_NOW = "review_now"
    VALIDATE_FIRST = "validate_first"
    REVIEW_AND_VALIDATE_IN_PARALLEL = "review_and_validate_in_parallel"
    REVIEW_NEXT = "review_next"
    PLAN = "plan"
    OBSERVE = "observe"
    INSUFFICIENT_BASIS = "insufficient_basis"


class PriorityBasisStatus(StrEnum):
    """Wystarczalność podstawy kwalifikacji priorytetu. Źródło: ZOP-PRI-01 pkt 8.1."""

    SUFFICIENT = "sufficient"
    INSUFFICIENT = "insufficient"


class ImpactAccountingRole(StrEnum):
    """Rola wyniku w rozliczeniu wpływu ekonomicznego. Źródło: ZOP-PRI-01 v1.0 rozdz. 5.

    Katalog zamknięty (PRI01-VAL-37, QPRI01-061). Chroni przed policzeniem tej samej
    złotówki wielokrotnie — PRI-01 rozdz. 5: „Jeżeli trzy testy opisują ten sam zakres
    i mechanizm ekonomiczny, jedna wartość może być primary_impact, a pozostałe są
    supporting_evidence albo non_additive_context. PRI-01 nie sumuje trzech wartości".

    Tylko poprawnie wskazany ``primary_impact`` może wejść do podstawy ekonomicznej.
    """

    PRIMARY_IMPACT = "primary_impact"
    SUPPORTING_EVIDENCE = "supporting_evidence"
    NON_ADDITIVE_CONTEXT = "non_additive_context"
    UNRESOLVED_OVERLAP = "unresolved_overlap"
