# Zoptymalizowani X-Ray — fundament technologiczny

X-Ray to silnik diagnostyczny organizacji: od danych do wniosku zarządczego — objaw,
dowód, możliwy mechanizm, skala, wpływ ekonomiczny, priorytet, następny krok.

To repozytorium zawiera **warstwę danych i szkielet silnika**, realizowane wg zadania
ZOP-TECH-01: wspólny model danych, mapowanie kolumn klienta, import, kontrole jakości,
strukturę wynikową FINDINGS, trwały zapis i generator danych syntetycznych.

Metodologię pisze Michał. Warstwę technologiczną buduje Aleksander.

---

## Od czego zacząć czytanie

Kolejność nie jest dowolna. Notatka techniczna czytana **przed** kartą jest zbiorem
arbitralnych decyzji; przeczytana po niej — zapisem, dlaczego kod wygląda tak, a nie
inaczej.

| Nr | Dokument | Po co |
| --- | --- | --- |
| 1 | `CLAUDE.md` | zasady obowiązujące bezwzględnie, szwy architektury, sposób pracy |
| 2 | `docs/zrodla/ZOPTECH01_…md` | zadanie: zakres, pięć tabel, osiem kontroli, kryteria odbioru |
| 3 | `docs/schemat-architektury.md` | mapa komponentów i przepływu danych |
| 4 | `docs/notatka-techniczna.md` | decyzje technologiczne wraz z odrzuconymi wariantami |
| 5 | `docs/otwarte-kontrakty.md` | niejednoznaczności kart: otwarte i rozstrzygnięte |

Pozostałe karty w `docs/zrodla/` (FIN, CAP, HR, PORT, PROC, MGT, PRI, CONF, ORCH) opisują
testy diagnostyczne, które **jeszcze nie są zaimplementowane**. Czyta się je, gdy przychodzi
czas na konkretny test — nie zawczasu.

---

## Siedem zasad

Nie są ozdobą deklaracji. Wyjaśniają rzeczy, które w kodzie wyglądają na niedokończone.

**1. Zero wymyślonych reguł biznesowych.** Każdy próg, waga, klasyfikacja i wzór ma
źródło w karcie metodologicznej. Nie ma progów „z rozsądku", nie ma benchmarków bez źródła.
Gdy karta czegoś nie rozstrzyga, trafia to do `docs/otwarte-kontrakty.md`, a w kodzie
zostaje komentarz `# ASSUMPTION:` — nie domysł udający regułę.

**2. Zero score'ów 0–100.** `confidence_score` jest zawsze `null`, a jego typ dopuszcza
wyłącznie `None`. To **nie jest niedokończony kod**: ZOP-CONF-01 pkt 2.2 zawiera dosłowny
zakaz — „CONF-01 nie tworzy wyniku 0–100, wag, średniej ważonej, arbitralnych progów ani
katalogu HIGH/MEDIUM/LOW". Pewność niesie klasa jakościowa, nie liczba.

**3. Determinizm.** Te same dane plus ta sama wersja kodu równa się ten sam wynik. Bez
ukrytego stanu, bez zależności od kolejności iteracji, bez czasu w tożsamości. Generator
działa wyłącznie z jawnym `seed`, identyfikatory rekordów są wyliczane, nie losowane.

**4. Audytowalność.** Każda liczba prowadzi do rekordów źródłowych, zakresu, okresu
i wersji kontraktu. Każda kontrola zwraca `basis` — podstawę, na jakiej powiedziała to,
co powiedziała. Liczba bez podstawy nie jest dowodem.

**5. `null` jest poprawnym wynikiem.** Brak informacji to pełnoprawny wynik diagnostyczny.
Nigdy nie wypełniamy braku zerem, średnią ani wartością zastępczą. Zero **nie jest**
brakiem: koszt kategorii mógł realnie wynieść 0 zł.

**6. Hipoteza to nie fakt.** Korelacja to nie przyczyna, a powiązanie wyników to nie
wspólny mechanizm. `gap` znaczy „luka ekonomiczna względem referencji", nigdy
„oszczędność". Kontrola wykrywająca podobne nazwy jednostek stawia **hipotezę tożsamości**
i tak ją nazywa.

**7. Zero AI w rdzeniu.** Model językowy może później tłumaczyć wynik. Nie wytwarza podstaw
dowodowych, nie wypełnia luk, nie nadaje klas.

Na tym etapie obowiązuje dodatkowo: **zero danych rzeczywistych**. Wyłącznie generator
syntetyczny. Nic z SPZOZ, nic o pacjentach, nic z realnej organizacji.

---

## Czego ten fundament świadomie nie robi

Bez tej listy łatwo założyć, że reszta już istnieje.

- **Nie ma żadnego testu diagnostycznego.** `NOOP-01` jest **atrapą**: liczy wiersze
  w ACTIVITY i zapisuje jeden wynik bez treści metodologicznej. Istnieje po to, żeby
  dowieść, że rejestr, kontrakt FINDINGS, zapis i ślad działają razem. Nie wolno rozwijać
  go w kierunku diagnostyki — pierwszym prawdziwym testem będzie FIN-01, na własnej karcie.
- **Nie ma priorytetyzacji, oceny pewności ani orkiestracji.** Kontrakty ZOP-PRI-01,
  ZOP-CONF-01 i ZOP-ORCH-01 są w strukturze danych obecne, ale żaden kod ich nie wypełnia.
  Wszystkie pola pewności i priorytetu pozostają `null`.
- **Nie ma danych rzeczywistych** i nie będzie na tym etapie. Katalogi `data/`
  i `dane_klienta/` są w `.gitignore`.
- **Nie ma sztucznej inteligencji.** Żadnego modelu językowego, chatbota ani automatycznych
  rekomendacji — patrz zasada 7.
- **Nie ma interfejsu użytkownika ani panelu zarządczego.** Powstaną, gdy fundament będzie
  stabilny, a nie wcześniej.
- **Nie ma integracji z ERP, CRM ani systemami księgowymi.** Wejściem są pliki XLSX i CSV.
- **Zbiór syntetyczny nie zawiera zaszytych problemów.** Ma zmienność (sezonowość,
  jednostki różnej wielkości), ale nie ma problemów biznesowych — te przyjdą osobną wersją
  zbioru, po zatwierdzeniu pierwszych testów. Zapisane ograniczenia zbioru: wpis DT-17
  w notatce technicznej.

---

## Uruchomienie

```
python -m venv .venv
source .venv/Scripts/activate     # Git Bash na Windows
pip install -r requirements.txt
pip install -e .
```

Ostatni krok instaluje pakiet `xray` w trybie edytowalnym: zmiany w `src/` działają od
razu, a `import xray` działa w testach, skryptach i demonstracji bez ustawiania
`PYTHONPATH`.

### Zobaczyć całość w działaniu

```
python -m xray.demo
```

Demonstracja **generuje** firmę syntetyczną w katalogu tymczasowym, po czym przeprowadza
ją przez pełny łańcuch:

```
generator → pięć plików (CSV + XLSX)
  → profil mapowania   → raport mapowania
  → ingest             → ramki w kontrakcie + raporty importu
  → osiem kontroli     → statusy z podstawą
  → NOOP-01            → rekord FINDINGS
  → magazyn SQLite     → zapis i odczyt przez sprawdzenie tożsamości
```

Dane **powstają w trakcie**, a nie leżą w repozytorium — dzięki temu demonstracja
uruchamia się na każdej maszynie. Ziarno jest jawne, więc każde uruchomienie daje ten sam
wynik.

### Sprawdzenie

```
pytest                     # testy
ruff check src tests       # styl
```

---

## Struktura

```
src/xray/
  ingest/      odczyt XLSX i CSV → ramka w kontrakcie + raport importu
  mapping/     profil kolumn klienta (YAML) + raport mapowania
  model/       kontrakt danych: pięć tabel bazowych + FINDINGS
    tables/    ACTIVITY, COST, RESOURCE, PROCESS, PLAN
    findings/  wynik, twierdzenie, dowód, priorytet, tożsamość
  validation/  rejestr ośmiu kontroli jakości danych
    checks/    po jednym pliku na kontrolę
  engine/      rejestr testów diagnostycznych (wtyczki)
  store/       trwały zapis: przebiegi i wyniki (SQLite)
  synth/       generator firmy syntetycznej
  demo/        przebieg pokazowy
  crosscut/    MGT-01, PRI-01, CONF-01 nad gotowymi wynikami (puste)
  orch/        ORCH-01: sprawa → gałąź → krok (puste)
  report/      komunikat zarządczy i eksport (puste)

profiles/      profile mapowania (firma syntetyczna; profile klientów poza repozytorium)
docs/          karty źródłowe, notatka techniczna, otwarte kontrakty
tests/         pytest, układ odpowiadający src/
```

**Dwa szwy, których nie wolno naruszyć:**

- **kontrakt danych** (`model/`) — poniżej niego nic nie wie, z jakiego pliku przyszła
  liczba; pochodzenie rekordu żyje w raporcie importu **obok** kontraktu, nie w jego polach,
- **FINDINGS** (`store/`) — jedyne miejsce zapisu wyników; nikt nie liczy niczego „obok".

Warstwa niższa nigdy nie importuje wyższej. Jedyną walutą między warstwami są modele.

---

## Jak dołożyć kontrolę jakości danych

Architektura twierdzi, że to nowy plik plus wpis w rejestrze i zero zmian w rdzeniu.
Przepis czyni to twierdzenie sprawdzalnym.

1. **Nowy plik** w `src/xray/validation/checks/`.
2. **Klasa dziedzicząca po `DataCheck`** z polem `DECLARATION: ClassVar[CheckDeclaration]`.
   Bez deklaracji klasa nie da się utworzyć — sprawdzenie jest przy imporcie.
3. **W deklaracji**: `check_id`, `control_number` (1–8 wg pkt 5.3), `title`, co kontrola
   wymaga (`requires_import_report`, `required_fields`, `requires_natural_key`,
   `requires_time_fields`) oraz `max_status` — **sufit**, jaki wolno jej nadać samodzielnie.
   Sufit to granica, nie stały wynik: kontrola 1 deklaruje CRITICAL, ale sięga po niego
   wyłącznie przy braku elementu klucza naturalnego — każdy inny brak ogłasza jako PASS
   z obserwacją, bo o ciężarze braku wie test, a nie walidator (rozstrzygnięcie B-06).
   Jeżeli ograniczenie zależy od ziarna czasowego tabeli, użyj `max_status_by_time_grain`;
   jeżeli sygnałem kontroli jest **różnica między dwoma polami**, zadeklaruj
   `comparison_pairs`.
4. **Metoda `run(context) -> CheckOutcome`.** Wejściem jest `ValidationContext` — stan
   wiedzy o tabeli (ramka, raporty importu, raporty mapowania, klasa kontraktu), a nie
   sama ramka. Zwracasz status, `basis` i obserwacje; `check_id` i nazwy tabeli nie
   przepisujesz — składa je rejestr.
5. **Jedna linia** w `_CHECK_CLASSES` w `src/xray/validation/registry.py`.
6. **Testy** w `tests/validation/`.

Rejestr bierze na siebie: stosowalność do tabeli, dostępność wejścia, egzekwowanie sufitu
statusu i unieważnianie wyniku, gdy zadeklarowana para pól pochodzi z jednej kolumny
klienta. Kontrola nie powtarza tych warunków.

## Jak dołożyć test diagnostyczny

1. **Nowy plik** w `src/xray/engine/`.
2. **Klasa dziedzicząca po `DiagnosticTest`** z polem
   `DECLARATION: ClassVar[DiagnosticTestDeclaration]`.
3. **W deklaracji**: `test_id`, `required_tables`, `required_by_test` (pola, bez których
   **ten test** nie może wydać wyniku), `required_validations` (które kontrole muszą być
   wykonane), `produced_fields` (co test wypełnia w FINDINGS) i `possible_next_tests`.
   Nazwa `required_by_test` niesie, **czyim** wymaganiem jest pole: strukturalnie wymagany
   jest wyłącznie element klucza naturalnego, a reszta jest wymaganiem konkretnego testu.
   Deklaracja jest sprawdzana wobec kontraktu danych przy imporcie: test odwołujący się do
   nieistniejącej tabeli albo pola nie da się zarejestrować. Do `required_by_test` wpisuj
   wyłącznie pole, bez którego test nie wyda **żadnego** twierdzenia — pole potrzebne
   części twierdzeń zostaje poza deklaracją, dopóki nie ma `required_by_claim` (DT-18).
4. **Metoda `run(data, scope, period) -> tuple[FindingRecord, ...]`.** Rekordy buduj przez
   `FindingRecord.create` — identyfikator jest wtedy wyliczany z krotki tożsamości i rekord
   sam potwierdza swoją spójność. Test **nie zapisuje** wyników; zwraca je. `run` dostaje
   ramki, a nie metadane: obecność kolumn sprawdziła bramka piętro wyżej.
5. **Jedna linia** w `_TEST_CLASSES` w `src/xray/engine/registry.py`.
6. **Testy złote** ze scenariuszy karty (np. FIN01-T01…T08) w `tests/engine/`.
   Sprawdzają status, flagi, `validation_required` i `next_tests` — nie samą liczbę.

Rejestr jest **jawną krotką, nie dekoratorem**: rejestracja przez dekorator zależałaby od
kolejności importów, czyli od ukrytego stanu, co łamie zasadę 3.

Testu **nie uruchamia się przez `run`**, tylko przez `engine.run_test(...)` albo
`test.execute(...)`. `execute` jest metodą szablonową: sprawdza `required_by_test` wobec
rzeczywistych raportów importu i albo woła `run`, albo zwraca **jeden** wynik ze statusem
`TEST_BLOCKED`. Wtyczka nie może tego ominąć — nadpisanie `execute` lub `readiness` kończy
się `TypeError` przy tworzeniu klasy. Brak wiedzy o imporcie też daje odmowę: bramka
zamyka się w stronę bezpieczną. Szczegóły i granice: wpis DT-20.

---

## Konwencje

- Python 3.13, pandas, Pydantic v2, SQLite (magazyn kanoniczny), PyYAML, pytest, ruff.
- **Nazwy techniczne po angielsku** (jak w kartach: `metric_value`, `next_tests`),
  **komentarze i docstringi po polsku.**
- Każdy moduł zaczyna się komentarzem, który dokument i punkt implementuje.
- Testy powstają razem z kodem.
- Nazwa publiczna nie może zaczynać się od `test` — koliduje z regułami zbierania pytest
  i daje fałszywie przechodzące testy (wpis DT-07).
