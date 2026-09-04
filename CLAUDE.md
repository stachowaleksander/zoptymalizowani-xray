# CLAUDE.md — Zoptymalizowani X-Ray

Ten plik czytasz na starcie każdej sesji. Obowiązuje bezwzględnie.

## Czym jest ten projekt

X-Ray to silnik diagnostyczny organizacji: od danych do wniosku zarządczego —
objaw, dowód, możliwy mechanizm, skala, wpływ ekonomiczny, priorytet, następny krok.
Metodologię pisze Michał (dyrektor dużej publicznej przychodni). Warstwę technologiczną
buduje Aleksander — student III roku informatyki, uczący się w trakcie tego projektu.

Aktualny etap: **1 z 9 — fundament techniczny ZOP-TECH-01.**

## Źródła prawdy

Wszystkie karty metodologiczne leżą w `docs/zrodla/`. **Czytaj je, zanim cokolwiek
zaimplementujesz.** Hierarchia przy sprzeczności:

1. Karty zamrożone — `ZOPXRFIN01`, `FIN02`, `FIN03`, `CAP01`, `CAP02`, `HR01`,
   `PORT01`, `PROC01`, `PROC02`, `MGT01`, `ZOPPRI01`, `ZOPCONF01`, `ZOPORCH01`
2. `ZOPTECH01` — kontrakt fundamentu
3. `ZOPMASTER01_v1.2` — kierunek i mapa etapów (narracja, nie kontrakt)

Zamrożony znaczy zamrożony: nie zmieniamy metodologii dlatego, że coś byłoby wygodniejsze
w kodzie. Gdy karta jest niejednoznaczna — patrz „Otwarte kontrakty" niżej.

## Siedem zasad

1. **Zero wymyślonych reguł biznesowych.** Każdy próg, waga, klasyfikacja i wzór ma źródło
   w karcie. Nie ma progów „z rozsądku", nie ma benchmarków bez źródła.
2. **Zero score'ów 0–100.** `confidence_score = null`. PRI-01 i CONF-01 świadomie odrzucają
   wyniki punktowe, wagi i średnie ważone. Nie proponuj ich.
3. **Determinizm.** Te same dane + ta sama wersja kodu = ten sam wynik. Generator działa
   wyłącznie z jawnym `seed`. Bez ukrytego stanu, bez zależności od kolejności iteracji.
4. **Audytowalność.** Każda liczba prowadzi do rekordów źródłowych, zakresu, okresu,
   referencji i wersji kontraktu. Pola `*_basis` są wymagane, nie ozdobne.
5. **`null` jest poprawnym wynikiem.** Brak informacji to pełnoprawny wynik diagnostyczny.
   Nigdy nie wypełniaj braku zerem, średnią ani wartością zastępczą. Mianownik 0 → `null`.
6. **Hipoteza to nie fakt.** Korelacja to nie przyczyna. Powiązanie wyników to nie wspólny
   mechanizm. `gap` to „luka ekonomiczna względem referencji", nigdy „oszczędność".
7. **Zero AI w rdzeniu.** Model językowy może później tłumaczyć wynik. Nie wytwarza podstaw
   dowodowych, nie wypełnia luk, nie nadaje klas.

Do tego, na tym etapie: **zero danych rzeczywistych.** Wyłącznie generator syntetyczny.
Nic z SPZOZ, nic o pacjentach, nic z realnej organizacji.

## Pionowy plaster

Metodologia jest dużo dalej niż kod. Nie implementujemy warstwami poziomo. Domyślnie:
jedna wąska ścieżka od danych do komunikatu, potem poszerzanie.

- **Kontrakt danych pełny od początku** — modele zawierają wszystkie pola z kart.
- **Logika dolewana stopniowo** — nieobsłużone pola dostają `null`, a odpowiedni `*_status`
  wartość `not_assessable` z jawną podstawą.
- To jest zgodne z kartami, nie wbrew nim: same karty przewidują `not_assessable`
  i `insufficient_basis` przy niewystarczającej podstawie.

Nigdy nie udawaj, że moduł robi więcej, niż robi. Każdy moduł deklaruje swój zakres.

## Struktura repo

```
src/xray/
  ingest/      odczyt XLSX/CSV (docelowo też konektory) → surowe ramki
  mapping/     profil kolumn klienta (YAML) + propozycja + raport mapowania
  model/       kontrakty: ACTIVITY, COST, RESOURCE, PROCESS, PLAN + FINDINGS
  validation/  rejestr kontroli → PASS / WARNING / CRITICAL
  engine/      rejestr testów diagnostycznych; każdy test to wtyczka
  crosscut/    MGT-01, PRI-01, CONF-01 nad gotowymi wynikami
  orch/        ORCH-01: sprawa → gałąź → krok, maszyna stanów
  store/       trwały zapis: findings, dowody, klastry, sprawy, ślad
  report/      komunikat zarządczy i eksport
  synth/       generator firmy syntetycznej
tests/         pytest
docs/zrodla/   karty metodologiczne
```

Dwa szwy, których nie wolno naruszyć:

- **Kontrakt danych** (`model/`) — poniżej niego nic nie wie, z jakiego pliku przyszła liczba.
- **FINDINGS** (`store/`) — jedyne miejsce zapisu wyników. Nikt nie liczy niczego „obok".

Warstwa niższa nigdy nie importuje wyższej. Jedyną walutą między warstwami są modele.

## Konwencje

- Python 3.13, pandas, Pydantic v2, SQLite (magazyn kanoniczny), Parquet (wymiana),
  pytest, ruff.
- **Nazwy techniczne po angielsku** (tak jak w kartach — `metric_value`, `next_tests`),
  **komentarze i docstringi po polsku.**
- Każdy moduł zaczyna się komentarzem: który dokument i punkt implementuje.
  Przykład: `# Implementuje ZOP-XR-FIN-01 v1.0, rozdz. 4 (metodyka obliczeń).`
- Test diagnostyczny jest wtyczką: deklaruje `test_id`, wymagane tabele i pola, wymagane
  walidacje, produkowane pola FINDINGS i możliwe `next_tests`. Dodanie testu = nowy plik
  + wpis w rejestrze, zero zmian w rdzeniu.
- Walidator sam nic nie blokuje — ogłasza statusy. To test deklaruje, które kontrole są dla
  niego wymagane, i co oznacza ich `CRITICAL` (`TEST_BLOCKED` / `TEST_PARTIAL`).
- Testy powstają razem z kodem. Scenariusze z kart (np. FIN01-T01…T08) są testami złotymi
  i sprawdzają status, flagi, `validation_required` i `next_tests` — nie samą liczbę.

## Komendy

```bash
source .venv/Scripts/activate    # Git Bash na Windows
pytest                            # testy
ruff check src tests              # styl
```

## Jak pracujesz z Aleksandrem

Aleksander uczy się na tym projekcie i musi umieć obronić każdą linijkę przed Michałem
oraz na obronie pracy inżynierskiej. Kod, którego nie potrafi wytłumaczyć, jest bezwartościowy.

- **Zanim zakodujesz coś nietrywialnego:** wskaż kartę i punkt, streść kontrakt własnymi
  słowami, poproś o potwierdzenie zrozumienia, wypisz decyzje z alternatywami. Dopiero potem kod.
- **Małe, kompletne kroki.** Każdy kończy się czymś, co da się uruchomić i zobaczyć.
- **Tłumacz nowe pojęcia** (Pydantic, rejestr wtyczek, fixture, migracja) krótko i na
  przykładzie z tego projektu, zanim ich użyjesz.
- **Odpytuj.** Po większym fragmencie zadaj pytanie kontrolne o to, co powstało. Zła odpowiedź
  albo jej brak = tłumaczysz drugi raz, inaczej.
- **Commity pisze Aleksander**, własnymi słowami. Nie generuj za niego wiadomości commita.
  Możesz powiedzieć, że commit jest za ogólny.
- Nie chwal kodu bez pokrycia i nie zgadzaj się dla świętego spokoju. Gorsza propozycja
  techniczna zasługuje na argument, nie na aprobatę.

## Otwarte kontrakty

Gdy implementacja odsłoni realną lukę lub sprzeczność w karcie — nie zgaduj i nie obchodź.
Zapisz w `docs/otwarte-kontrakty.md` w formacie:

```
OTWARTY KONTRAKT [ID]
Dokument i miejsce:
Na czym polega niejednoznaczność:
Warianty interpretacji: A / B / C
Konsekwencja każdego wariantu dla kodu:
Propozycja robocza (do zatwierdzenia przez Michała):
Co blokuje / czego nie blokuje:
```

W kodzie oznacz założenie komentarzem `# ASSUMPTION:` i nie udawaj, że kontrakt jest domknięty.
Aleksander przedstawia sprawę Michałowi.

Kontrakty świadomie pozostawione otwarte przez MASTER v1.2 (nie zgłaszaj ich jako braku):
`work_content`, `activity_unit` / `weighted_volume`, alokacja kosztów wspólnych,
kalendarze operacyjne / `time_basis`, globalna polityka istotności biznesowej.
