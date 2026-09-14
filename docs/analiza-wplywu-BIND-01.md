# Analiza wpływu ZOP-XR-FOUNDATION-BIND-01 v1.0 na fundament X-Ray

Dokument analityczny. **Nie zmienia kodu, nie jest otwartym kontraktem i nie proponuje
rozstrzygnięć.** BIND-01 ma status `FOUNDATION_BIND_ACTIVE = false` (BIND l.7, 353, 402)
i `CONTROLLING_RELEASE_FOR_IMPLEMENTATION = false` (l.406). Analiza opisuje, co się stanie
z obecnym kodem, **gdy** kontrakt zostanie zwolniony.

Stan na 2026-09-13, gałąź `main`, commit `be593ca`.

## Konwencje

- `BIND l.N` — numer linii w `docs/zrodla/ZOP-XR-FOUNDATION-BIND-01_v1.0.md`.
- `plik:N` albo `plik:N–M` — numer linii w repozytorium, liczony w chwili pisania.
- `notatka l.N` — `docs/notatka-techniczna.md`; `OK l.N` — `docs/otwarte-kontrakty.md`.
- `CAP01 l.N`, `FIN01 l.N` itd. — linia w pliku karty w `docs/zrodla/`.
- `N-xx` — niejednoznaczność z sekcji 8.

## Metoda i granice sprawdzenia

**Przeczytane w całości:** BIND-01 (408 linii); każdy plik `src/xray/**/*.py`;
wszystkie 21 plików `tests/**/*.py`; `docs/notatka-techniczna.md` (DT-01…DT-20);
`docs/otwarte-kontrakty.md`; `docs/schemat-architektury.md`; karta ZOP-XR-CAP-01;
ZOP-TECH-01 v0.1; `profiles/firma-syntetyczna.yaml`.

**Przeczytane fragmentami (wskazane przy użyciu):** FIN-01, FIN-02, FIN-03, HR-01, PORT-01,
PROC-01, PROC-02, CAP-02, MGT-01 (grep + wybrane zakresy linii), PRI-01 (grep
`validation_required`).

**Nie przeczytane:** ZOP-MASTER-01 v1.2, ZOP-CONF-01, ZOP-ORCH-01 w całości.

**Uruchomione (nic z `src/` i `tests/` nie zmieniono):**

1. `pytest --collect-only` z `PYTHONDONTWRITEBYTECODE=1` i `-p no:cacheprovider` —
   zebrane **381** testów, **żaden nie został uruchomiony**, bez ostrzeżeń zbierania.
2. Sześć sprawdzeń empirycznych w katalogu tymczasowym sesji (poza repozytorium):
   - `canonical_form({"x": date(2026,1,1)}) == canonical_form({"x": "2026-01-01"})` → **True**,
   - `canonical_form({"u": ("A","B")}) == canonical_form({"u": ("B","A")})` → **False**,
   - „ą" złożone (U+0105) i rozłożone (a + U+0328) dają **różne** postacie kanoniczne,
   - CSV z pustą linią między rekordami: drugi rekord leży w fizycznej linii 4,
     `Rejection.file_row = 3`,
   - CSV z polem wieloliniowym w cudzysłowie: drugi rekord zaczyna się w linii 4,
     `file_row = 3`,
   - XLSX wczytany bez wskazania arkusza: `SourceRef.source_sheet = None`.
3. `git status` przed i po: jedyny nieśledzony plik to sam BIND-01
   (`?? docs/zrodla/ZOP-XR-FOUNDATION-BIND-01_v1.0.md`) — **dokument nie jest zacommitowany**.
4. `find` po `*.db`, `*.sqlite`, `*.sqlite3` poza `.venv` — brak plików (magazyn trwały
   nie istnieje; demonstracja używa `:memory:`, `src/xray/demo/run.py:95`).

**Nie sprawdzone:** zachowanie `pd.read_excel` przy pustych wierszach wewnątrz arkusza;
treść „Decision 08" i „pytań Aleksandra z 09.09.2026", na które powołuje się BIND l.29 —
w repozytorium ich nie ma (grep po `docs/`).

---

## 0. Streszczenie dla planowania

- Najcięższe skutki mają **rozdz. 9 (record_id + strukturalność wszystkich pól
  bazowych)** i **rozdz. 4–5 (tożsamość zakresu, referencji, wyniku)**. Oba trafiają
  w dwa szwy z CLAUDE.md: kontrakt danych i FINDINGS.
- **Obalone:** DT-19, DT-18, DT-14 (dla tożsamości regulowanych przez BIND), DT-03
  w części, DT-20 w większości. **Do poprawki:** DT-02, DT-06, DT-08, DT-09, DT-10,
  DT-11, DT-12, DT-13. Sekcja C: **B-06** — obalone „Odczytanie kryterium
  strukturalnego" i gałąź PASS; B-02 i B-04 do poprawki.
- **Testy:** 14 pewnych upadków, 57 zależnych od kształtu implementacji — łącznie
  **71 z 381 (18,6%)**. Z ryzykiem kaskadowym (błąd zbierania całego pliku) do
  **123 (32,3%)**. Żaden istniejący test nie pokrywa scenariuszy BIND T01–T15.
- **Trzy pytania z sekcji 6:** wszystkie trzy są realne.
- **CAP01-T10:** karta mówi o **nullu w polu** („cost null"). Słowo „kolumna" nie pada
  w żadnej karcie Core 10. Gałąź PASS kontroli 1 nie miała pokrycia w karcie.
- **Sekcja 8:** 25 nowych niejednoznaczności. BIND deklaruje ich zero (l.351, 379,
  388–389).

---

## 1. Sekcja po sekcji

### A — Module contract (BIND l.50–79)

**Dziś w kodzie.**

- Kod nie zna pojęcia modułu. `DiagnosticTestDeclaration`
  (`src/xray/engine/base.py:56–159`) ma `test_id`, `required_tables`, `required_by_test`,
  `required_validations`, `produced_fields`, `possible_next_tests`. Nie ma `module_id`,
  `module_name`, `module_requirements`, `module_execution_status`, `module_result_status`.
- Status testu wynika z bramki gotowości kolumn: `execute` albo woła `run`, albo zwraca
  jeden `FindingRecord` ze statusem `TEST_BLOCKED` (`engine/base.py:345–362`, `364–396`).
  `TEST_PARTIAL` jest świadomie nieosiągalny (`engine/base.py:373–378`; notatka l.527–529).
- Katalog `LogicalStatus` (`src/xray/model/enums.py:45–76`) zawiera `TEST_PARTIAL`
  i `TEST_BLOCKED`, nie zawiera `TEST_NOT_APPLICABLE` ani `TEST_COMPLETE`.
- Rekordu technicznego wykonania nie ma: magazyn ma tylko tabele `runs` i `findings`
  (`src/xray/store/schema.py:33–60`).
- `test_contract_version` nie istnieje. `CONTRACT_VERSION = "ZOP-TECH-01/v0.1"`
  (`src/xray/model/findings/identity.py:34`, `finding.py:71`) to wersja **kontraktu
  FINDINGS**, a nie wersja karty.
- `run()` zwraca krotkę wyników bez przypisania do modułu (`engine/base.py:398–414`,
  `engine/noop01.py:51–82`).

**Co kontrakt nakazuje.** Cztery statusy modułu (l.60); `module_result_status = null` do
`MODULE_EXECUTED` (l.61); status testu wyznaczany deterministycznie z tabeli l.69–77;
zamknięty katalog `test_execution_status` = {`TEST_NOT_APPLICABLE`, `TEST_BLOCKED`,
`TEST_PARTIAL`, `TEST_COMPLETE`} (l.79); `TEST_NOT_APPLICABLE` wyłącznie przy rozstrzygniętej
applicability i zerze modułów stosowalnych; dla niego obowiązkowy rekord techniczny
z polami minimum (l.79); zakaz statusu terminalnego, gdy moduł zostaje w `MODULE_READY`
(l.65, 77).

**Kolizja.**

1. Status testu wynika dziś z obecności kolumn, a ma wynikać ze statusów modułów.
2. Kod nie ma stanu „wykonanie niedokończone" (l.76–77) — bramka zawsze kończy się
   wynikiem terminalnym.
3. Brak tabeli daje dziś `ReadinessReason.MISSING_TABLE` → `TEST_BLOCKED`
   (`engine/base.py:165–166`, `297–303`). Kontrakt odróżnia „nie dotyczy" od „zablokowany",
   a kod nie ma jak wyrazić applicability (N-22).
4. `TEST_COMPLETE` nie istnieje; relacja `test_execution_status` do pola `status` jest
   nieokreślona (N-09).

**Pliki do tknięcia.** `engine/base.py`, `engine/registry.py`, `engine/noop01.py`,
`model/enums.py`, `model/findings/finding.py`, `store/schema.py`, `store/findings.py`,
`demo/run.py`, `tests/engine/test_readiness.py`, `tests/engine/test_noop01.py`,
`tests/demo/test_demo.py`.

### B — Validation dependency contract (BIND l.81–91)

**Dziś w kodzie.**

- `required_validations: tuple[str, ...]` (`engine/base.py:101–107`) — deklaracja bez
  egzekucji. Nic nie łączy wyników `run_checks` z wykonaniem testu. Luka jest opisana
  w DT-20 (notatka l.629–640) i **utrwalona testem jako zachowanie oczekiwane**:
  `test_bramka_nie_zastepuje_wymaganych_walidacji` (`tests/engine/test_readiness.py:111–129`).
- NOOP-01 deklaruje `required_validations=()` (`engine/noop01.py:42–44`).
- `CheckResult` (`src/xray/validation/results.py:263–287`) to wynik kontroli dla tabeli;
  nie ma `validation_dependency_scope` ani `affected_module_ids`.
- Zarejestrowane są wyłącznie kontrole fundamentu `TECH01-VAL-01…08`
  (`validation/registry.py:40–49`). Kontroli z kart (`CAP01-VAL-xx`, `FIN01-VAL-xx`) nie ma.

**Co kontrakt nakazuje.** Dla każdej wymaganej walidacji: `validation_dependency_scope`
MODULE albo GLOBAL_TEST, `affected_module_ids` (niepuste dla MODULE, puste dla GLOBAL_TEST),
skutek CRITICAL + MODULE → moduły `MODULE_BLOCKED`, CRITICAL + GLOBAL_TEST → `TEST_BLOCKED`
(l.85–89). Brak automatycznej reguły „CRITICAL blokuje cały test" (l.91).

**Kolizja.** DT-20 odkłada domknięcie tej luki „do rozstrzygnięcia metodologicznego
(TEST_BLOCKED czy TEST_PARTIAL)" (notatka l.638–640). BIND B to rozstrzyga (l.89). Kod
nie ma ani miejsca na zależność, ani identyfikatorów modułów, na które zależność mogłaby
wskazywać.

**Pliki.** `engine/base.py`, `validation/results.py` (odczyt statusu po `validation_id`),
`tests/engine/test_readiness.py`.

### C — Scope identity contract (BIND l.93–122)

**Dziś w kodzie.**

- `ScopeRef` (`src/xray/model/findings/refs.py:25–49`): `scope_label` (35), `units`
  jako krotka uporządkowana (38), `filters: tuple[tuple[str, str], ...]` — pary pole–wartość
  bez operatora, wartość zawsze tekstowa, kolejność celowo istotna (41–46),
  `aggregation_level: str | None` (48). Brak `constraints`, `contract_scope_extensions`,
  `scope_definition_hash`, `scope_id`.
- Tożsamość wyniku bierze `scope.model_dump()` w całości, **z etykietą**
  (`finding.py:194`). To samo w `ClaimRecord` (`claim.py:134`) i `EvidenceRecord`
  (`evidence.py:113–115`).
- Kanonizacja (`identity.py:95–128`): `sort_keys=True`, separatory bez spacji, UTF-8
  z `ensure_ascii=False` — zgodne z 4.1 pkt 2. Niezgodne:
  - brak normalizacji NFC (4.1 pkt 1) — potwierdzone empirycznie,
  - listy i krotki zawsze w kolejności zapisu (`identity.py:108–109`), bez rozróżnienia
    zbiór/sekwencja (4.1 pkt 4) — potwierdzone empirycznie,
  - daty zamieniane na napis ISO (`identity.py:104–105`), więc data i identyczny napis
    dają tę samą postać kanoniczną — potwierdzone empirycznie; sprzeczne z 4.1 pkt 5
    („liczba, data, tekst i null nie są zamienne").
- Skrót: blake2b, 16 bajtów (`identity.py:79`, `131–136`), prefiks `FND-`
  (`finding.py:44`). Kontrakt: SHA-256 lowercase hex, prefiks `SCOPE-` (l.103–104).
- Ta sama `canonical_form` zasila także skrót treści importu (`ingest/reader.py:304`),
  skrót profilu (`mapping/profile.py:179`), `run_id` (`store/runs.py:220`) i **wartości
  generatora** (`synth/values.py:41`). Zmiana reguł kanonizacji przesuwa wszystkie te
  wartości naraz.

**Co kontrakt nakazuje.** `scope_definition` z filtrami jako predykatami
field/operator/value, populacją, poziomem agregacji, ograniczeniami i rozszerzeniami
z karty; etykieta wykluczona z tożsamości; `scope_id = "SCOPE-" + SHA-256`; same semantics
→ same `scope_id` (l.120).

**Kolizja.** Ta sama semantyka z inną etykietą daje dziś inny `finding_id`, a kontrakt
wymaga tego samego `scope_id` (l.118, 120). Kolejność filtrów i jednostek zmienia dziś
tożsamość. Brak operatora uniemożliwia zapis IN, RANGE, LT itd. Scenariusz T03 (l.333)
dziś **przechodzi przypadkiem** — różne filtry wchodzą do skrótu — ale odwrotny kierunek
(ta sama semantyka, różna etykieta) nie jest spełniony.

**Pliki.** `model/findings/identity.py`, `refs.py`, `finding.py`, `claim.py`,
`evidence.py`, `priority.py`, `store/schema.py` (`identity_canonical`, 100–108),
`demo/run.py:145`, `tests/model/test_findings.py:40`, `tests/engine/test_noop01.py:26`,
`tests/engine/test_readiness.py:31`, `tests/store/test_store.py:32`.

### D/E — Reference semantic identity / provenance (BIND l.126–144)

**Dziś w kodzie.**

- `ReferenceRef` (`refs.py:70–103`): `reference_type`, `reference_period` (PeriodRef),
  `reference_scope` (ScopeRef), `reference_value`, `reference_quality` (tekst),
  `reference_source` (tekst). Brak `reference_source_logical_id`,
  `reference_semantic_extensions`, `reference_id`, `reference_applicable` i wszystkich pól
  provenance (`reference_source_artifact_id`, `reference_source_SHA256`,
  `reference_source_location_or_member_path`, `reference_extracted_at_utc`,
  `reference_input_binding`).
- Brak referencji to `reference=None` w wyniku (`finding.py:103–108`); referencja
  niewyznaczona to `reference_value=None` (`refs.py:91–92`). Kod nie odróżnia
  „nie dotyczy" (`reference_applicable=false`) od „dotyczy, ale brak".
- `ReferenceType` (`enums.py:163–176`) to jedna lista wg FIN-01 6.1, z wartością
  `plan_budget` (173). CAP-01 i HR-01 używają `plan` (CAP01 l.203, HR01 l.202).
- Import nie liczy SHA-256 bajtów pliku w ogóle (grep `sha256` po `src/`: brak trafień).

**Co kontrakt nakazuje.** Bezwzględne rozdzielenie tożsamości semantycznej od provenance
(l.144); `reference_id = "REF-" + SHA256(canonical JSON {5 pól})` (l.135);
`reference_type` jako „exact value z source contract" (l.130); T14: inna kopia fizyczna →
ten sam `reference_id`, nowy rekord wykonania (l.344).

**Kolizja.** `reference_source` jako tekst miesza semantykę z pochodzeniem. Jeden enum
nie przeniesie `plan` z CAP-01/HR-01 w „exact value" (N-17). Bez skrótu bajtów nie ma
`reference_source_SHA256`.

**Pliki.** `refs.py`, `enums.py`, `finding.py` (walidator `_check_reference_consistency`,
262–285, opiera się na `reference is None`), `ingest/reader.py`, `ingest/report.py`,
`mapping/report.py:99–123` (pisownia `plan_budget`), `tests/model/test_findings.py:129–140`.

### D/E — Result identity contract (BIND l.146–166)

**Dziś w kodzie.** `finding_id = "FND-" + blake2b-128(canonical {test_id, scope,
period, contract_version, identity_algorithm_version})` (`finding.py:181–198`).

| Element | Kod | Kontrakt (l.150–156) |
| --- | --- | --- |
| `test_id` | jest | wymagany |
| wersja | `contract_version` = wersja kontraktu FINDINGS | `test_contract_version` = wersja karty |
| `module_id` | brak | wymagany albo canonical null |
| zakres | cały `ScopeRef`, z `scope_label` | `scope_id` |
| okres | cały `PeriodRef`, z `period_label` (`refs.py:66`) | `analysis_period` „w kanonicznej reprezentacji właściwej dla karty" |
| referencja | brak | `reference_id` albo canonical null |
| `identity_algorithm_version` | w krotce (`finding.py:197`) | spoza zamkniętej listy |
| funkcja i prefiks | blake2b-128, `FND-` | SHA-256, `RESULT-` |

**Kolizja.**

1. T04 (l.334): dwie referencje przy tym samym okresie analizy dają dwa `result_identity`.
   Dziś dają ten sam `finding_id`. Dwa takie wyniki w jednym przebiegu naruszyłyby klucz
   główny `(finding_id, run_id)` (`store/schema.py:58`), a `save_run` przy porównaniu
   skleiłby je w słowniku po `finding_id` (`store/findings.py:66–67`).
2. „Powtórne obliczenie tworzy nowy immutable result record" (l.166) wobec obecnej
   idempotencji: ten sam `run_id` z tą samą treścią → brak operacji
   (`store/findings.py:65–69`). Czy to kolizja, zależy od N-11.

**Pliki.** `finding.py`, `identity.py`, `store/schema.py`, `store/findings.py`,
`engine/base.py` (`_blocked`), `engine/noop01.py`, `demo/run.py`, testy findings/store/
readiness/noop01/demo.

### F — Version compatibility contract (BIND l.168–184)

**Dziś w kodzie.** Nic. Istniejące „wersje": `CONTRACT_VERSION` (`identity.py:34`),
`IDENTITY_ALGORITHM_VERSION` (`identity.py:42`), `RUN_IDENTITY_VERSION`
(`store/runs.py:60`), `claim_version` (`claim.py:80`). Żadna nie jest wersją karty.

**Co kontrakt nakazuje.** Deklaracja `comparison_compatibility` z podstawą
i ograniczeniami, powstająca wraz z release nowej wersji karty (l.172–176); zakaz
automatycznego porównania przy INCOMPATIBLE (l.178).

**Kolizja.** Brak — wszystkie karty zamrożone są w v1.0, więc nie ma czego porównywać.
Test `test_inna_wersja_kontraktu_daje_inny_identyfikator`
(`tests/model/test_findings.py:70–75`) dotyczy wersji kontraktu FINDINGS, nie karty.

**Pliki.** Nowy model w `model/findings/`, `store/`. Brak konsumenta dziś (N-23).

### G — Dataset currency contract (BIND l.186–196)

**Dziś w kodzie.** Pola waluty nie ma nigdzie (grep `currency|walut` po `src/`, `tests/`,
`profiles/`: jedno trafienie, `src/xray/mapping/__init__.py:145`). `MappingProfile`
(`mapping/profile.py:83–96`) ma `extra="forbid"`, więc wpis `dataset_currency:`
w YAML dziś kończy się `ProfileError`. `semantic_digest` (`profile.py:179–199`) buduje
skrót z **jawnej listy** kluczy: `applied_columns`, `plan_metrics`,
`organization_timezone`.

**Co kontrakt nakazuje.** Jedna jawna waluta profilu (ISO, wielkie litery); trzy statusy
zgodności; `monetary_modules_execution_allowed` tylko przy `SINGLE_CURRENCY_CONFIRMED`;
zero FX (l.190–196).

**Kolizja.** Docstring `mapping/__init__.py:144–146` twierdzi, że „deklaracja waluty
zostanie pokryta automatycznie" przez skrót profilu. Wobec `profile.py:179–199` to
nieprawda — nowe pole nie trafi do skrótu bez zmiany kodu (zapisane w załączniku, Z-1).
Bramkowanie „modułów pieniężnych" wymaga kontraktu A i listy modułów pieniężnych, której
karty nie podają (N-20).

**Pliki.** `mapping/profile.py`, `profiles/firma-syntetyczna.yaml`, `mapping/report.py`,
`store/runs.py` (przez `profile_digest`), `engine/base.py`, `tests/mapping/test_profile.py`.

### H — Validation message contract (BIND l.198–214)

**Dziś w kodzie.** `CheckResult{check_id, control_number, table_name, status, basis,
observations, not_assessed_reason}` (`validation/results.py:263–287`);
`CheckObservation{subject, measure, value, text_value, basis, evidence_row_ids,
evidence_source_rows, evidence_truncated}` (`results.py:84–123`). Brak `validation_code`,
`technical_verification_suggestion` jako pola, `affected_scope_id`. Dowód wiersza to
`evidence_row_ids` (row_id, nie record_id) albo `evidence_source_rows` —
pary `(source_id, file_row)` dla odrzuceń (`results.py:107–116`).

ZOP-TECH-01 kryterium 8.4 wymaga „proponowanego sposobu dalszej weryfikacji" (ZOPTECH01
l.168). Dziś taka treść, jeżeli jest, żyje wyłącznie w prozie `basis`.

**Co kontrakt nakazuje.** Kod, dokładny status ze źródła, podstawa, opcjonalna **wyłącznie
techniczna** sugestia, wskazanie rekordów lub zakresu; zakaz interpretacji biznesowej
(l.202–214).

**Kolizja i miejsca do oceny.**

- Podstawa kontroli 7: „nieudokumentowana kieruje do CAP-02" (`checks/resource_usage.py:111–116`);
  obserwacja powołuje się na „ZOP-XR-CAP-01 rozdz. 5" (75–78).
- Podstawa kontroli 5: „wartość ujemna bywa poprawnym zapisem korekty"
  (`checks/suspicious_values.py:94–97`).
- Czy wskazanie testu diagnostycznego i uwaga o możliwej korekcie mieszczą się w „ścieżce
  technicznej" — lista przykładów dopuszczalnych (l.208) tego nie obejmuje (N-16).
  Test utrwalający obecność „CAP-01" w podstawie: `tests/validation/test_validation.py:548`.
- `validation_severity` ma być „exact source-defined" (l.203), a TECH-01 5.3 nie
  definiuje statusów dla swoich ośmiu kontroli (N-15).

**Pliki.** `validation/results.py`, `validation/registry.py:90–99`, wszystkie
`validation/checks/*.py`, `tests/validation/*`.

### I — 9.1 techniczne `record_id` (BIND l.218–236)

**Dziś w kodzie.**

- `row_id = f"{table_name}:{source.source_id}:{file_row:06d}"` (`ingest/reader.py:153–163`),
  żyje jako indeks ramki (`reader.py:311`) — zgodnie z l.230, że to metadane, a nie pole
  biznesowe.
- `source_id = "SRC-" + blake2b(canonical {dataset_id, source_file (nazwa), source_sheet,
  header_row, identity_algorithm_version})` (`ingest/report.py:84–94`). **Skrótu bajtów
  pliku nie ma.**
- `file_row = header_row + 1 + pozycja` (`reader.py:275`), gdzie `pozycja` to indeks
  z `iterrows` po ramce pandas; `header_row` zaszyte na 1 (`reader.py:221`).

**Co kontrakt nakazuje.**
`record_id = "REC-" + SHA256(canonical UTF-8 JSON {source_artifact_SHA256,
source_object_or_sheet_id, source_row_ordinal})` (l.234); niepusty, unikalny w datasecie,
deterministyczny (l.220–226); fizyczny ordinal niezależny od sortowania (l.236).

**Kolizja.**

1. **Składniki.** Dziś: nazwa pliku i `dataset_id`. Kontrakt: skrót bajtów, bez nazwy, bez
   `dataset_id`. Skutki:
   - identyczne bajty pod dwiema nazwami → dziś rozłączne identyfikatory, wg kontraktu
     identyczne, o ile `source_object_or_sheet_id` dla CSV nie niesie nazwy (N-07),
   - ten sam plik w dwóch zbiorach → dziś rozłączne (DT-10), wg kontraktu identyczne
     (`dataset_id` nie wchodzi, unikalność wymagana tylko w obrębie datasetu, l.224).
2. **Fizyczny ordinal.** Potwierdzone empirycznie: przy pustej linii i przy polu
   wieloliniowym `file_row` różni się od numeru fizycznej linii. `pd.read_csv` pomija puste
   linie i skleja rekord wieloliniowy (`reader.py:175`). `file_row = 3` odpowiada numerowi
   **rekordu** liczonemu z nagłówkiem, a nie numerowi **linii**. Co liczy kontrakt — N-07.
3. **Arkusz.** XLSX bez wskazanego arkusza ma `source_sheet = None` (`reader.py:172`,
   `220`) — potwierdzone empirycznie; nieodróżnialne od CSV.
4. **Import manifest** (l.236) nie istnieje w kodzie ani w żadnym dokumencie (grep).
5. **Wiersze odrzucone** nie mają identyfikatora (`report.py:138–161`; `results.py:110–116`)
   — N-06.

**Pliki.** `ingest/reader.py`, `ingest/report.py`, `validation/context.py:42–47`,
`validation/results.py`, każda kontrola czytająca indeks ramki, `store/runs.py`
(provenance), `tests/ingest/test_load_table.py`.

### I — 9.2 finalna macierz tabel bazowych (BIND l.238–264)

**Dziś w kodzie.**

- Pola klucza są wymagane i niepuste już w modelu: `KeyText` (`model/tables/base.py:212–213`,
  walidator 114–129) i `PeriodDate` bez `None` (221–222). Pola spoza klucza są nullowalne
  (`NumericValue` 235, `OptionalKeyText` 215–219, `EventTimestamp` 224–228).
- Brak kolumny spoza klucza → materializacja `None` (`ingest/reader.py:243–247`, `283`),
  raport `materialized_empty` (`ingest/report.py:250–265`). Brak kolumny klucza →
  `missing_key_columns` (`report.py:235–248`); wiersze odpadają, bo `KeyText` dostaje `None`.
- Kontrola 1: brak kolumny klucza → CRITICAL, brak innej kolumny → PASS z obserwacją
  (`validation/checks/missing_columns.py:129–162`).
- Bramka: pole z `required_by_test` bez kolumny → `TEST_BLOCKED` (`engine/base.py:326–339`).

**Co kontrakt nakazuje.** Każde pole bazowe z ZOP-TECH-01 jest kolumną wymaganą,
`fields_optional = NONE` dla wszystkich pięciu tabel (l.240–246);
`COLUMN_MISSING → STRUCTURAL_SCHEMA_FAILURE` (l.250);
`COLUMN_PRESENT_VALUE_NULL → MISSING_VALUE → VALUE_LEVEL_VALIDATION_ISSUE` (l.252);
null dopuszczalny dla **wszystkich** pól na etapie ingestion z obowiązkową walidacją (l.248);
zakaz cichej akceptacji nulla, imputacji i substytucji (l.254–258); PROCESS bez klucza
`case_id + stage` (l.264).

**Kolizja.**

1. `KeyText`/`PeriodDate` odrzucają pustą wartość w polach, które kontrakt każe przyjąć
   i zwalidować (l.248).
2. Materializacja zamienia brak kolumny na wartości `None` w ramce; rozróżnienie żyje
   tylko w raporcie importu. Sprzeczne co najmniej z „missing column ≠ null" (l.46);
   czy mechanizm może przetrwać z innym statusem — N-01.
3. Kontrola 1 ogłasza PASS przy brakującej kolumnie — sprzeczne z l.250.
4. Kryterium „strukturalnie wymagany = element NATURAL_KEY" (OK l.556–571; DT-19)
   sprzeczne z l.46, 240–246, 323.
5. `ProcessRecord.NATURAL_KEY = ("case_id", "stage")` (`model/tables/process.py:74`) —
   sprzeczne wprost z l.264. Docstring `process.py:104–106` twierdzi, że „karty PROC-01
   pkt 2.3 i PROC-02 pkt 2.3 wskazują jako klucz case_id i stage". **To nie ma pokrycia:**
   pkt 2.3 obu kart (PROC01 l.75–84, PROC02 l.67–76) wymienia wyłącznie pola bazowe i nie
   używa słowa „klucz". To samo powtarza `tests/model/test_process.py:45`.
6. Źródła pozostałych kluczy: ACTIVITY i COST — klucz karty FIN-01 (FIN01 l.60), nie
   ZOP-TECH-01; RESOURCE — klucz CAP-01 3.1 bez `capacity_unit` (CAP01 l.78,
   `resource.py:34–36`); PLAN `date + unit + metric` (`plan.py:27`, `31`) — **bez
   żadnego cytowanego źródła**.

**Pliki.** `model/tables/base.py`, `activity.py`, `cost.py`, `resource.py`, `process.py`,
`plan.py`, `ingest/reader.py`, `ingest/report.py`, `mapping/report.py`,
`mapping/__init__.py`, `validation/checks/missing_columns.py`, `missing_values.py`,
`duplicates.py`, `inconsistent_names.py`, `engine/base.py`, `engine/noop01.py`,
`synth/generator.py` (uzasadnienia), `demo/run.py:218–219`; testy — sekcja 3.

### J — Exclusion record contract (BIND l.266–290)

**Dziś w kodzie.** Nic. `FindingRecord` (`finding.py:47–177`) nie ma nawet
`exclusion_flags`, choć FIN-01 i CAP-01 wymieniają je w FINDINGS (FIN01 l.333,
CAP01 l.335).

**Co kontrakt nakazuje.** Rekord wyłączenia z namespace, typem i tożsamością podmiotu,
dwiema tożsamościami (`EXCL-`, `EXAPP-`) i ochroną przed podwójnym efektem w obrębie
jednej kalkulacji (l.270–290).

**Kolizja.** Z istniejącym kodem — żadna (nie ma czego łamać). Zależności:
`record_id` (9.1), `scope_id` (C), `result_identity` (5.2), kanoniczny okres (pytanie 6b).

**Pliki.** Nowy moduł w `model/findings/`, nowa tabela w `store/`, powiązanie
w `finding.py`.

### K — validation_required / PRI-01 binding (BIND l.292–312)

**Dziś w kodzie.**

- `FindingRecord.validation_required: bool = False` (`finding.py:126–127`), rekord
  niezmienny (`frozen=True`, 56).
- `PriorityRecord.validation_priority_action` to osobne pole (`priority.py:84`) —
  architektura zgodna z K.
- `validation_priority_basis` świadomie pominięte jako pole opisowe (`priority.py:25–29`),
  a K wymienia je jako pole (l.298).
- Bramka ustawia `validation_required=True` z komentarzem: „routing należy do PRI-01
  i to on może flagę zdjąć" (`engine/base.py:386–394`). DT-20: „PRI-01 może ją świadomie
  odwrócić" (notatka l.621–623).

**Co kontrakt nakazuje.** `PRI_01_may_clear_source_validation_required = false` (l.306);
właściciel `validation_required`: „source engine / frozen karta" (l.296). PRI-01 sam
zastrzega: „Rozszerzenia PRI-01 nie zmieniają ich semantyki" (ZOPPRI01 l.309).

**Kolizja.** Komentarz w kodzie i DT-20 dopuszczają to, czego K zakazuje. Czy silnik
bez podstawy w karcie może w ogóle ustawić flagę — N-14.

**Pliki.** `engine/base.py`, `model/findings/priority.py`, `docs/notatka-techniczna.md`
(DT-20), `tests/engine/test_readiness.py:302–310`.

---

## 2. Co zostaje obalone

### 2.1. Rejestr DT-01…DT-20

| DT | Werdykt | Podstawa w BIND | Dlaczego |
| --- | --- | --- | --- |
| DT-01 | bez zmian | — | G nie dotyczy typu liczbowego |
| DT-02 | drobna poprawka | l.206, 234 | komunikat „wskazujący wiersz" ma wskazywać `record_id` |
| DT-03 | **obalony w części** | l.248, 252 | szczegóły niżej |
| DT-04 | bez zmian | — | — |
| DT-05 | bez zmian | — | BIND nie mówi o strefie czasowej |
| DT-06 | do ponownej oceny | l.254–258 | N-25: czy `""` → `null` to cicha substytucja |
| DT-07 | bez zmian | — | kod ma istniejącą niezgodność z DT-07 (Z-7) |
| DT-08 | do poprawki | l.248 | wiersz „`date` … nie dotyczy — pole klucza" (notatka l.188) przestaje być prawdą |
| DT-09 | do poprawki | l.103, 135, 156, 234, 279, 282 | „pole wchodzi do krotki tożsamości" (notatka l.236–237) jest sprzeczne z zamkniętymi listami elementów tożsamości BIND; dla `RunRef`, `SourceRef`, `ClaimRecord`, `EvidenceRecord` BIND milczy (N-08) |
| DT-10 | do poprawki | l.224, 234 | ochrona „dwóch klientów z `koszty.csv`" (notatka l.271–275) dla tożsamości wiersza znika, bo `record_id` nie zawiera `dataset_id`; `source_id` nie jest regulowany |
| DT-11 | **do poprawki** (zasada zostaje) | l.150–166, 184, 308 | szczegóły niżej |
| DT-12 | **do poprawki** | l.138, 144, 234, 344 | szczegóły niżej |
| DT-13 | do rozszerzenia | l.190 | `dataset_currency` musi wejść do skrótu profilu, a skrót ma jawną listę kluczy (Z-1) |
| DT-14 | **obalony dla tożsamości BIND** | l.103, 135, 156, 234, 279, 282 | szczegóły niżej |
| DT-15 | bez zmian | — | — |
| DT-16 | bez zmian | — | ma zastosowanie przy migracji testów (fałszywe przejścia, sekcja 3) |
| DT-17 | bez zmian merytorycznie | l.228 | ograniczenie 1 generatora uzasadnia się kluczem (`generator.py:20–21`) |
| DT-18 | **obalony / zastąpiony** | l.50–79 | granulację per twierdzenie zastępuje kontrakt modułu; `TEST_PARTIAL` staje się osiągalny (l.74); przesłanka z CAP01-T10 była nadinterpretacją (sekcja 7) |
| DT-19 | **obalony** | l.46, 240–246, 250, 323, 338 | szczegóły niżej |
| DT-20 | **obalony w większości** | l.58, 69–79, 86–91, 250, 306 | szczegóły niżej |

### 2.2. DT-03 — granica odrzucania w modelu

**Treść DT-03:** model odrzuca „wartość nieprzetłumaczalną na zadeklarowany typ oraz pusty
element klucza naturalnego" (notatka l.58–60). Kod: `base.py:13–16` (reguła warstwy),
`114–129` (`_require_non_blank`), `212–213` (`KeyText`), `221–222` (`PeriodDate` bez `None`).

**Co obala BIND.** l.248: dla **wszystkich** pól bazowych null jest dopuszczalny na etapie
ingestion z obowiązkową walidacją. l.252: kolumna obecna z wartością null →
`MISSING_VALUE` → problem **poziomu wartości**, czyli rekord istnieje. Część „pusty element
klucza naturalnego" jest więc obalona.

**Co zostaje.** Część „wartość nieprzetłumaczalna na typ" — BIND o niej milczy. Otwarte
zostaje, czy taki wiersz dostaje `record_id` (N-06).

**Uwaga.** Uzasadnienie DT-03 — „model, który sam odrzuca rekord, odbiera decyzję
walidatorowi" (notatka l.71–73) — BIND wzmacnia. Pusty element klucza był według
kryterium samego DT-03 „faktem diagnostycznym o danych", a mimo to trafił do odrzucanych.

### 2.3. DT-11 — wynik kluczowany parą `(finding_id, run_id)`

**Zostaje:**

- zakaz nadpisywania i historia wyniku (BIND l.166, 184: `historical_result_mutation = false`,
  l.308),
- to, że dane wejściowe nie wchodzą do tożsamości wyniku (notatka l.292–293) — lista
  z l.150–156 nie zawiera skrótu wejścia, a T14 (l.344) przewiduje nowy rekord wykonania
  przy tej samej tożsamości.

**Wymaga poprawki:**

1. Skład `finding_id` zmienia się w `result_identity` — tabela w sekcji 1 D/E.
2. Klucz magazynu: BIND nie definiuje ani przebiegu, ani identyfikatora rekordu wyniku.
   Para może przetrwać jako klucz rekordu, ale obecna idempotencja („ten sam `run_id`
   z identyczną treścią to brak operacji", notatka l.310–312) stoi wobec „powtórne
   obliczenie tworzy nowy immutable result record" (l.166) — N-11.
3. T04: dziś dwa warianty referencji w jednym przebiegu naruszyłyby klucz główny
   (`schema.py:58`) — sekcja 1 D/E.
4. „Pierwszy realny użytkownik klucza z pary" z DT-20 — odmowa i policzony wynik mają ten
   sam `finding_id` (notatka l.609–614) — utrzyma się tylko wtedy, gdy `reference_id`
   i `module_id` są znane przed wykonaniem (N-12).

### 2.4. DT-12 — skrót treści liczony z rekordów, nie z bajtów

**Zostaje:** skrót treści niezależny od formatu jako składnik `run_id`. BIND nie reguluje
`run_id`.

**Wymaga poprawki:**

1. BIND wymaga SHA-256 **dokładnych bajtów** (l.138 dla referencji, l.234 dla `record_id`).
   Zdanie „skrót zawartości jest faktem o tym, co wczytano" (notatka l.324–325) przestaje
   być jedynym faktem — potrzebne są oba skróty, a import dziś nie liczy żadnego z bajtów.
2. Pułapka z DT-12 (notatka l.332–335) — `row_id` niesie nazwę pliku, więc nie może wejść
   do skrótu treści — powtarza się z `record_id`, który niesie skrót artefaktu.
3. „Przeformatowanie pliku bez zmiany wartości nie tworzy nowego przebiegu, a zapis pozostaje
   idempotentny" (notatka l.329–330) koliduje na dwa sposoby:
   - T14 (l.344): nowe dokładne bajty → nowy niezmienny rekord wykonania z nowym SHA,
   - ten sam `run_id` dla CSV i XLSX przy **różnych** `record_id`. Jeżeli `record_id`
     trafi do treści wyniku — przez `affected_record_ids` (l.206) albo
     `exclusion_subject_id` (l.273) — `save_run` podniesie `ConflictingRun` z komunikatem
     „przepływ nie jest deterministyczny" (`store/findings.py:65–74`). To dokładnie ten
     błąd, przed którym DT-13 ostrzega (notatka l.372).

Test: `test_zmiana_formatu_pliku_nie_tworzy_nowego_przebiegu`
(`tests/store/test_store.py:172–192`).

### 2.5. DT-14 — wersja per kształt krotki

**Treść reguły:** „wersja należy do kształtu krotki danego rodzaju rekordu, nie do systemu"
(notatka l.406–409); rejestr `_ALGORITHMS` (`identity.py:139–145`).

**Co obala BIND.** Dla `SCOPE-`, `REF-`, `RESULT-`, `REC-`, `EXCL-`, `EXAPP-` kontrakt
ustala listę elementów, funkcję skrótu, prefiks i kanoniczny JSON. **Żadna z tych list nie
ma elementu wersji** (l.103, 135, 156, 234, 279, 282). Zmiana kształtu którejś z nich nie
jest więc lokalnym podniesieniem wersji rodzaju rekordu, tylko zmianą kontraktu. Czy
wymaga deklaracji z F — N-23.

**Co zostaje.** Reguła DT-14 nadal dotyczy `RunRef` (`store/runs.py:60`) i `SourceRef`,
których BIND nie reguluje (N-08).

**Fakt pomocniczy.** „Magazyn jest pusty" (notatka l.403) — potwierdzone: brak plików bazy
w repozytorium; demonstracja działa w `:memory:`.

Testy: `test_wersja_przebiegu_i_wyniku_sa_niezalezne` (`tests/store/test_store.py:306–321`),
`test_wersja_tozsamosci_jest_per_rodzaj_rekordu` (`tests/demo/test_demo.py:81–85`).

### 2.6. DT-19 — kontrola 1 ogłasza stan

**Treść:** dwa stany — brak elementu `NATURAL_KEY` → CRITICAL, brak dowolnego innego pola
→ PASS z obserwacją (notatka l.539–544).

**Co obala BIND:** każde pole bazowe jest kolumną wymaganą (l.46, 240–246, 323), brak
kolumny to `STRUCTURAL_SCHEMA_FAILURE` (l.250), a T08 podaje wprost przykład pola spoza
klucza: „COST bez kolumny amount" (l.338). Obalone są:

- gałąź PASS,
- argument „PASS nie jest fałszywym przejściem" (notatka l.553–556),
- kryterium gałęzi CRITICAL (element klucza),
- przeniesienie odpowiedzialności na bramkę gotowości (notatka l.557–568).

**Co zostaje:** zdanie „walidator ogłasza stan danych, ale nie przejmuje metodologicznej
odpowiedzialności testu" jest zgodne z H (l.212–214).

**Fakt pomocniczy:** ZOP-TECH-01 5.3 podaje jako przykład braku wymaganej kolumny
„brak pola date, unit **lub amount**" (ZOPTECH01 l.86), a `amount` nie należy do klucza.
DT-19 i B-06 odeszły od tej litery; BIND do niej wraca.

### 2.7. DT-20 — bramka gotowości

| Element DT-20 | Stan po BIND |
| --- | --- |
| bramka sprawdza, czy pole z `required_by_test` miało kolumnę (notatka l.591–594) | dla pól bazowych bez przedmiotu — brak kolumny jest porażką strukturalną wcześniej (l.250) |
| odmowa jako jeden `TEST_BLOCKED` (notatka l.603–607) | status wyznaczany z modułów (l.69–79) |
| `validation_required=True`, „PRI-01 może świadomie odwrócić" (notatka l.616–623) | sprzeczne z l.306 |
| „Granica bramki: kolumny, nie wypełnienie" (notatka l.625–627) | wypełnienie wchodzi do modułu: `required_value_missing → record_not_creditable_for_that_calculation` (l.260) |
| luka `required_validations` wymaga rozstrzygnięcia metodologicznego (notatka l.635–640) | rozstrzygnięte przez B (l.86–91) |
| odmowa i wynik mają ten sam `finding_id` (notatka l.609–614) | zależy od N-12 |
| ochrona metody szablonowej przed nadpisaniem (notatka l.586–589) | nietknięte — BIND o tym milczy |

### 2.8. Sekcja C `docs/otwarte-kontrakty.md`

| Wpis | Werdykt | Uzasadnienie |
| --- | --- | --- |
| A-01 | bez zmian | BIND nie dotyka `time_basis`. Styk: `analysis_period` dla testów PROC (pytanie 6b) wymaga podstawy przypisania, której A-01 zakazuje wybierać |
| B-01 | bez zmian | zgodne z H: „uznanie pozycji za korektę księgową" to interpretacja niedopuszczalna (l.210) |
| B-02 | do poprawki | katalog `test_execution_status` z `TEST_NOT_APPLICABLE` i `TEST_COMPLETE` (l.79); enum ma 9 wartości (`enums.py:68–76`); relacja do `status` — N-09 |
| B-03 | bez zmian | K rozdziela pewność od kompletności wykonania (l.300, 310) |
| B-04 | do poprawki w pisowni | decyzja posługuje się `reference_type = plan_budget` (OK l.361–363; `mapping/report.py:99–123`), czyli pisownią FIN-01; CAP-01 i HR-01 mają `plan` — N-17 |
| B-05 | bez zmian | BIND nie mówi o dowodach |
| **B-06** | **obalone w części** | poniżej |

**B-06 — szczegółowo.**

1. **Przesłanka.** „ZOP-XR-CAP-01 pkt 4.1 stwierdza wprost: brak cost … czyli klient bez
   kolumny `cost` ma być obsługiwalny" (OK l.446–449) oraz „Brak kolumny `cost` oznacza
   dziś odrzucenie każdego wiersza RESOURCE — dokładnie to, czego CAP-01 zakazuje"
   (OK l.458–459). Karta nie mówi o kolumnie i niczego takiego nie zakazuje — sekcja 7.
2. **Rozstrzygnięcie Michała — trzy stany** (OK l.507–527):
   - stan 1 `required_structurally` — BIND rozszerza z elementu klucza na **wszystkie**
     pola bazowe,
   - stan 2 `required_by_test` / `required_by_claim` — przenosi się na poziom wartości
     i modułów (l.58, 260),
   - stan 3 „pole legalnie opcjonalne" — dla pól bazowych nie istnieje
     (`fields_optional = NONE`, l.242–246); zostaje dla rozszerzeń kart (l.262).
3. **„Odczytanie kryterium strukturalnego"** — „strukturalnie wymagany = element klucza
   naturalnego i nic ponadto" (OK l.556–571), zapisane jawnie „do ewentualnego
   zaprotestowania" — **obalone wprost** przez l.46, 240–246, 323 i T08.
4. **Mechanizm materializacji pustej kolumny** (OK l.478–484) koliduje z „missing column
   ≠ null" (l.46); czy może przetrwać z innym statusem — N-01.
5. **Skutki dla kodu** (OK l.531–534, 550): wiersz „kontrola 1" — obalony; wiersz „rejestr
   testów egzekwuje `required_by_test`" — zastąpiony przez `module_requirements` (l.58);
   akapit „Czego bramka nie zamyka" (OK l.544–549) — rozstrzygnięty przez B.
6. **Odroczenie `required_by_claim`** (OK l.573–582) — zastąpione kontraktem modułu.

Reguła pliku mówi, że „wpisu rozstrzygniętego nie otwiera się ponownie bez nowego faktu"
(OK l.15). BIND jest takim faktem, ale do chwili release nie obowiązuje.

---

## 3. Które testy padną

Prognoza, **nie wynik uruchomienia**. Stan wyjściowy wg zlecenia: 381 zielonych (tego nie
sprawdzałem — zebrałem 381, nie uruchomiłem).

**Kategorie:**

- **A — pewny upadek.** Asercja stoi w sprzeczności z zachowaniem, które BIND nakazuje
  literą. Padnie przy każdej zgodnej implementacji.
- **B — upadek przy prawdopodobnej implementacji.** Asercja wiąże artefakt, który BIND
  zastępuje (format identyfikatora, podział klucz/nie-klucz, skład tożsamości), albo zależy
  od nierozstrzygniętego skutku z sekcji 8. Test może przejść, jeśli stary artefakt zostanie
  zachowany obok nowego.
- **K — ryzyko kaskadowe.** Plik importuje albo buduje na poziomie modułu obiekt, którego
  kształt się zmieni; wtedy pada **zbieranie całego pliku**.

### 3.1. Kategoria A — 14 testów

| # | Plik | Test | Powód |
| --- | --- | --- | --- |
| 1 | `tests/model/test_activity.py:40–43` | `test_pusty_produkt_jest_odrzucany` | pusty `product` ma przejść z walidacją (l.248) |
| 2 | `tests/model/test_cost.py:123–126` | `test_pusta_jednostka_jest_odrzucana` | l.248 |
| 3 | `tests/model/test_cost.py:129–131` | `test_jednostka_z_samych_spacji_jest_odrzucana` | l.248 (niezależnie od N-25) |
| 4 | `tests/model/test_resource.py:63–66` | `test_pusta_nazwa_zasobu_jest_odrzucana` | l.248 |
| 5 | `tests/model/test_process.py:44–46` | `test_klucz_naturalny_to_case_id_i_stage` | l.264 wprost |
| 6 | `tests/model/test_process.py:85–88` | `test_pusty_identyfikator_przypadku_jest_odrzucany` | l.248 |
| 7 | `tests/model/test_plan.py:35–38` | `test_pusta_nazwa_wskaznika_jest_odrzucana` | l.248 |
| 8 | `tests/model/test_registry.py:36–41` | `test_klucz_naturalny_jest_podzbiorem_pol[PROCESS]` | asercja niepustego klucza PROCESS; l.228, 264 |
| 9 | `tests/ingest/test_load_table.py:114–132` | `test_odrzucony_wiersz_trafia_do_raportu_z_numerem_z_pliku` | wiersz z pustym `unit` ma zostać przyjęty (l.248, 252) |
| 10 | `tests/validation/test_missing_columns.py:74–83` | `test_brak_pola_spoza_klucza_daje_pass_z_obserwacja` | brak kolumny `cost` to nie PASS (l.250) |
| 11 | `tests/validation/test_missing_columns.py:86–91` | `test_pass_przy_braku_pola_nie_jest_falszywym_przejsciem` | asercja na treści gałęzi PASS („nie orzeka o jego ciężarze", `missing_columns.py:153–155`) |
| 12 | `tests/validation/test_missing_columns.py:135–147` | `test_kontrola_dziala_bez_profilu` | PASS przy braku kolumny `cost` (l.250) |
| 13 | `tests/validation/test_validation.py:264–268` | `test_kontrola_3_liczy_wiersze_utracone_osobno` | wiersz z pustym `unit` nie będzie odrzucony, więc licznik = 0 (l.248) |
| 14 | `tests/validation/test_validation.py:300–306` | `test_dowod_utraconego_wiersza_wskazuje_plik_i_numer` | j.w.; `evidence_source_rows[0]` nie istnieje |

### 3.2. Kategoria B — 57 testów

| Plik | Test (linie) | Powód / zależność |
| --- | --- | --- |
| `tests/model/test_base.py` | `test_tabela_bez_metadanych_nie_powstaje` (17–25) | asercja `"NATURAL_KEY" in komunikat`; l.228 |
| | `test_klucz_naturalny_wskazujacy_nieistniejace_pole_nie_powstaje` (39–50) | walidacja NATURAL_KEY; l.228 |
| `tests/model/test_cost.py` | `test_metadane_tabeli_sa_dostepne_bez_tworzenia_rekordu` (38–43) | `NATURAL_KEY == ("date","unit","category")` |
| | `test_klucz_naturalny_pokrywa_sie_z_polami_modelu` (46–48) | j.w. |
| `tests/model/test_registry.py` | `test_klucz_naturalny_jest_podzbiorem_pol[ACTIVITY]`, `[COST]`, `[PLAN]`, `[RESOURCE]` (36–41) | klucz przestaje być tożsamością (l.228, 240–246); przetrwa tylko przy zachowaniu NATURAL_KEY do innych celów (N-04) |
| `tests/model/test_findings.py` | `test_inna_wersja_kontraktu_daje_inny_identyfikator` (70–75) | `contract_version` ≠ `test_contract_version` (l.151) |
| | `test_krotka_tozsamosci_jest_odczytywalna` (83–89) | j.w. |
| | `test_luka_z_referencja_przechodzi` (129–140) | kształt `ReferenceRef` (l.128–142) |
| | `test_rekord_niesie_wersje_algorytmu_tozsamosci` (322–327) | wersja poza zamkniętą listą elementów (l.156) |
| | `test_rozne_wersje_algorytmu_daja_rozne_identyfikatory` (330–340) | j.w.; przejdzie tylko przy zachowaniu starego `finding_id` obok `result_identity` |
| | `test_nieznana_wersja_algorytmu_ma_wlasny_wyjatek` (343–350) | rejestr `_ALGORITHMS` wobec stałej funkcji SHA-256 |
| | `test_wersja_kontraktu_nie_wywoluje_masowego_odrzucania` (353–360) | j.w. |
| `tests/ingest/test_load_table.py` | `test_identyfikator_wiersza_jest_indeksem_ramki_a_nie_polem` (163–170) | nazwa indeksu `row_id`; N-05 |
| | `test_identyfikator_prowadzi_do_numeru_wiersza_w_pliku` (173–179) | prefiks `COST:` wobec `REC-` (l.234) |
| | `test_rozne_pliki_daja_rozne_identyfikatory` (211–217) | identyczne bajty → identyczny `record_id`, o ile obiekt CSV nie niesie nazwy (N-07) |
| | `test_raport_niesie_zakres_wierszy_i_identyfikatorow` (220–223) | `row_id_range` |
| | `test_ten_sam_plik_w_dwoch_zbiorach_daje_rozlaczne_identyfikatory` (415–422) | `dataset_id` nie wchodzi do `record_id` (l.234); przejdzie tylko przy zachowaniu `row_id` jako indeksu |
| | `test_zrodlo_niesie_wersje_algorytmu_tozsamosci` (452–454) | DT-09 |
| `tests/mapping/test_profile.py` | `test_pole_bez_przypisania_a_kolumna_ktorej_nie_ma` (131–142) | `materialized_empty` (N-01) |
| | `test_brak_kolumny_klucza_jest_odnotowany_osobno` (145–150) | rozróżnienie klucz/nie-klucz znika (l.240–246) |
| `tests/mapping/test_zgodnosc_z_importem.py` | `test_zapowiedz_i_zapis_zgadzaja_sie_takze_przy_brakujacej_kolumnie` (102–121) | `materialized_empty`, `missing_key_columns` |
| `tests/validation/test_missing_columns.py` | `test_brak_elementu_klucza_daje_critical` (94–102) | miara `missing_key_column` |
| | `test_brak_klucza_wygrywa_nad_brakiem_pola_spoza` (105–111) | zbiór miar {`missing_key_column`, `materialized_empty_column`} |
| | `test_kontrola_1_nigdy_nie_zwraca_warning` (120–129) | przesłanka B-06 obalona; wynik zależy od N-01 |
| | `test_raport_mapowania_wzbogaca_podstawe` (150–167) | treść podstawy gałęzi PASS |
| `tests/validation/test_validation.py` | `test_limit_modulowany_jest_ziarnem_a_nie_nazwa_tabeli` (138–149) | kontrola 4 dla PROCESS bez klucza (N-04) |
| | `test_zadeklarowany_brak_odrzucen_daje_zero` (192–214) | miara `rows_rejected_missing_key` traci źródło |
| | `test_dwoch_rodzajow_braku_nie_da_sie_zsumowac` (271–282) | j.w. |
| | `test_kontrola_4_wykrywa_powtorzony_klucz` (312–321) | co porównuje kontrola 4 (N-04) |
| | `test_duplikat_w_tabeli_zdarzeniowej_jest_sygnalem_nie_bledem` (335–345) | PROCESS bez klucza (l.264, N-04) |
| | `test_kontrola_2_wskazuje_plik_i_wiersz` (484–488) | adresowanie `(source_id, file_row)` wobec `affected_record_ids` (l.206, N-06) |
| `tests/validation/test_comparison_pairs.py` | `test_kontekst_rozpoznaje_wspolne_zrodlo` (37–51) | plik RESOURCE bez kolumny `cost` → `STRUCTURAL_SCHEMA_FAILURE`; skutek dla importu nieznany (N-01) |
| | `test_rozne_kolumny_nie_dziela_zrodla` (54–68) | j.w. |
| | `test_wspolna_kolumna_uniewaznia_cala_kontrole_7` (89–108) | j.w. |
| | `test_rozne_kolumny_pozwalaja_kontroli_7_dzialac` (111–125) | j.w. |
| | `test_wspolne_zrodlo_nie_psuje_kontroli_6` (202–223) | j.w. |
| `tests/validation/test_names_and_time.py` | `test_kontrola_6_obejmuje_case_id` (123–132) | kontrola 6 wybiera pola przez `text_key_fields`; `case_id` wypada z klucza (l.264, N-04) |
| `tests/engine/test_readiness.py` | `test_brak_pola_spoza_klucza_blokuje_test` (96–102) | plik bez kolumny `revenue` (N-01); status z modułów (l.69–79) |
| | `test_bramka_nie_zastepuje_wymaganych_walidacji` (111–129) | utrwala lukę, którą zamyka B; plik bez `unit` (N-01) |
| | `test_pole_z_jednego_z_dwoch_plikow_wystarczy` (142–150) | N-21 |
| | `test_brak_wiedzy_ma_inny_powod_niz_brak_kolumny` (168–178) | `ReadinessReason.MISSING_COLUMN` traci sens (l.250) |
| | `test_rejestr_prowadzi_przez_bramke` (234–258) | plik bez `unit` (N-01) |
| | `test_odmowa_i_wynik_maja_ten_sam_finding_id` (264–273) | N-12 |
| | `test_historia_pokazuje_odmowe_i_uzupelnienie` (276–292) | N-11, N-12 |
| | `test_dwie_odmowy_daja_ten_sam_rekord` (295–299) | plik bez kolumny `revenue` (N-01) |
| | `test_odmowa_niesie_podstawe_i_flage_walidacji` (302–310) | `validation_required` ustawiane przez silnik (l.296, 306, N-14) |
| | `test_bramka_nigdy_nie_zwraca_test_partial` (313–323) | przesłanka DT-18 obalona; asercja może przejść przypadkiem |
| `tests/engine/test_noop01.py` | `test_wtyczka_z_deklaracja_powstaje` (115–124) | deklaracja bez modułów (l.54–61) |
| | `test_noop01_niesie_krotke_tozsamosci_i_wersje_kontraktu` (180–190) | `contract_version` (l.151, N-08) |
| `tests/store/test_store.py` | `test_powtorny_zapis_nie_tworzy_duplikatu` (138–146) | N-11 |
| | `test_zmiana_formatu_pliku_nie_tworzy_nowego_przebiegu` (172–192) | sekcja 2.4 |
| | `test_wersja_przebiegu_i_wyniku_sa_niezalezne` (306–321) | sekcja 2.5 |
| `tests/synth/test_generator.py` | `test_nazwy_nie_sprowadzaja_sie_do_wspolnego_klucza` (153–160) | `text_key_fields` (N-04) |
| `tests/demo/test_demo.py` | `test_wersja_tozsamosci_jest_per_rodzaj_rekordu` (81–85) | sekcja 2.5 |

### 3.3. Kategoria K — ryzyko kaskadowe

| Plik | Mechanizm | Testów w pliku | Już policzone w A+B | Dodatkowo zagrożone |
| --- | --- | --- | --- | --- |
| `tests/model/test_findings.py` | `ZAKRES = ScopeRef(scope_label=…, units=…, aggregation_level=…)` na poziomie modułu (l.40) | 31 | 7 | 24 |
| `tests/synth/test_generator.py` | `from xray.model.tables.base import text_key_fields` (l.24) | 19 | 1 | 18 |
| `tests/engine/test_readiness.py` | klasa `RequiresRevenue` z `DiagnosticTestDeclaration` na poziomie modułu (l.49–62) | 17 | 10 | 7 |
| `tests/model/test_base.py` | `from xray.model.tables.base import KeyText` (l.14) | 5 | 2 | 3 |
| **razem** | | | | **52** |

**Dodatkowe ryzyko, niepoliczone.** Jeżeli `record_id` stanie się **polem modelu**
(N-05), konstruowanie rekordu bez niego podniesie `ValidationError`. Wtedy testy
oczekujące `pytest.raises(ValidationError)` w `test_activity.py`, `test_cost.py`,
`test_resource.py`, `test_process.py`, `test_plan.py` **przejdą z niewłaściwego powodu**
— to figura z DT-16. Testy oczekujące poprawnego rekordu (np.
`test_rekord_minimalny_przechodzi` w każdym z tych plików) padną.

### 3.4. Skala

| Plik | Zebrane | A | B | K (dodatkowo) |
| --- | --- | --- | --- | --- |
| `tests/demo/test_demo.py` | 13 | 0 | 1 | 0 |
| `tests/engine/test_noop01.py` | 18 | 0 | 2 | 0 |
| `tests/engine/test_readiness.py` | 17 | 0 | 10 | 7 |
| `tests/ingest/test_load_table.py` | 35 | 1 | 6 | 0 |
| `tests/mapping/test_profile.py` | 20 | 0 | 2 | 0 |
| `tests/mapping/test_zgodnosc_z_importem.py` | 11 | 0 | 1 | 0 |
| `tests/model/test_activity.py` | 5 | 1 | 0 | 0 |
| `tests/model/test_base.py` | 5 | 0 | 2 | 3 |
| `tests/model/test_cost.py` | 18 | 2 | 2 | 0 |
| `tests/model/test_enums.py` | 8 | 0 | 0 | 0 |
| `tests/model/test_findings.py` | 31 | 0 | 7 | 24 |
| `tests/model/test_plan.py` | 4 | 1 | 0 | 0 |
| `tests/model/test_process.py` | 18 | 2 | 0 | 0 |
| `tests/model/test_registry.py` | 25 | 1 | 4 | 0 |
| `tests/model/test_resource.py` | 5 | 1 | 0 | 0 |
| `tests/store/test_store.py` | 22 | 0 | 3 | 0 |
| `tests/synth/test_generator.py` | 19 | 0 | 1 | 18 |
| `tests/validation/test_comparison_pairs.py` | 19 | 0 | 5 | 0 |
| `tests/validation/test_missing_columns.py` | 14 | 3 | 4 | 0 |
| `tests/validation/test_names_and_time.py` | 26 | 0 | 1 | 0 |
| `tests/validation/test_validation.py` | 48 | 2 | 6 | 0 |
| **Razem** | **381** | **14** | **57** | **52** |

- A: **14 / 381 = 3,7%**
- A + B: **71 / 381 = 18,6%**
- A + B + K: **123 / 381 = 32,3%**

**Czego brakuje zamiast tego, co padnie.** Żaden istniejący test nie sprawdza scenariuszy
akceptacyjnych BIND T01–T15 (l.329–345). Wszystkie piętnaście to nowe testy złote.

---

## 4. Klucz naturalny — każde miejsce, które na nim stoi

BIND: `inferred_natural_key_allowed = false` (l.228); tożsamość rekordu = `record_id`
dla wszystkich pięciu tabel (l.240–246); brak globalnego klucza PROCESS `case_id + stage`
ani `case_id + stage + start` (l.264). Kolumna „Co się stanie" opisuje **skutek tekstu
BIND**, nie projekt zmiany.

| # | Miejsce | Jak opiera się na kluczu | Co się stanie |
| --- | --- | --- | --- |
| 1 | `src/xray/model/tables/base.py:46–51` | `NATURAL_KEY` na liście wymuszonych metadanych tabeli | wymuszenie deklaracji traci podstawę jako tożsamość rekordu |
| 2 | `base.py:267–273` | docstring: „Pola, których komplet jednoznacznie wskazuje rekord" — definicja klucza jako tożsamości | sprzeczne z l.228, 240–246 |
| 3 | `base.py:299–304`, `313–314` | klucz musi być podzbiorem pól i **nie może być pusty** | zakaz pustego klucza uniemożliwia zapis PROCESS bez klucza (l.264) |
| 4 | `base.py:84–94` | `text_key_fields()` — pola tekstowe klucza; konsumenci: kontrola 6 (`checks/inconsistent_names.py:108`), `tests/synth/test_generator.py:24, 157` | zbiór pól kontroli 6 przestaje mieć źródło (N-04) |
| 5 | `base.py:114–129`, `212–213`, `221–222` | `KeyText` i `PeriodDate` nie przyjmują pustej wartości — ta sama reguła DT-03, zapisana typem | sprzeczne z l.248 |
| 6 | `model/tables/activity.py:25–30`, `cost.py:21–27`, `resource.py:34–40`, `plan.py:27–31` | deklaracje kluczy tabel okresowych | przestają być tożsamością; PLAN nie ma cytowanego źródła klucza |
| 7 | `model/tables/process.py:66–74` | `NATURAL_KEY = ("case_id", "stage")`, z niepokrytym cytatem PROC-01/02 pkt 2.3 (104–106) | sprzeczne wprost z l.264 |
| 8 | `process.py:101–122` | `unit` nullowalne, bo „nie należy do klucza naturalnego PROCESS" | uzasadnienie znika; wynik (null dopuszczalny) zgodny z l.248, ale teraz dla wszystkich pól |
| 9 | `src/xray/ingest/reader.py:240–253`, `283` | podział pól bez kolumny: spoza klucza → materializacja `None`; z klucza → `missing_key_columns` | podział nie ma odpowiednika; każda brakująca kolumna → `STRUCTURAL_SCHEMA_FAILURE` (l.250); los materializacji — N-01 |
| 10 | `reader.py:132–135` | komentarz: „Pola `date` należą w czterech tabelach do klucza naturalnego, więc i tak nie mogą być puste" — założenie typu kolumny | `date` może być null (l.248); DT-08 do poprawki |
| 11 | `reader.py:350–352`; `ingest/report.py:118–123` | kod `blank_key` → `RejectionCategory.MISSING_VALUE`, opisany jako „rekord w kontrakcie nie istnieje" | pusta wartość to problem poziomu wartości, a rekord istnieje (l.252) |
| 12 | `ingest/report.py:235–248`, `250–265`, `267–282` | `missing_key_columns`, `materialized_empty` (z DECYZJĄ B-06), `fields_without_column` jako unia obu | rozróżnienie traci podstawę; unia nadal odpowiada zbiorowi COLUMN_MISSING |
| 13 | `src/xray/mapping/report.py:61–73`, `156–162`; `mapping/__init__.py:44–47`, `94–99` | `materialized_empty` i `missing_key_fields` w raporcie mapowania; nieaktualne `# ASSUMPTION` (Z-5) | j.w. |
| 14 | `src/xray/validation/base.py:130–131`, `193–194` | `requires_natural_key` — warunek stosowalności kontroli 1, 3, 4, 6 (`missing_columns.py:75`, `missing_values.py:52`, `duplicates.py:42`, `inconsistent_names.py:102`) | warunek bez przedmiotu, gdy klucza nie ma (PROCESS) |
| 15 | **kontrola 1** — `checks/missing_columns.py:82–170` | CRITICAL wyłącznie za element klucza (129–142), PASS za resztę (144–162) | obie gałęzie tracą kryterium; PASS sprzeczny z l.250 |
| 16 | **kontrola 3** — `checks/missing_values.py:60`, `68–84`, `89–109` | dopisek „pole należy do klucza, pusta wartość oznaczałaby błąd bramki" (78–81); miara `rows_rejected_missing_key` z `subject` = klucz | puste pola klucza trafią do ramki, więc dopisek jest nieprawdziwy; miara traci źródło |
| 17 | **kontrola 4** — `checks/duplicates.py:36–47`, `51`, `65–66`, `96–110` | duplikat = powtórzona wartość klucza; tabela zdarzeniowa ograniczona do WARNING; porównanie przez `astype(str)` | dla PROCESS brak klucza (l.264); dla tabel okresowych klucz przestaje być tożsamością; co porównywać — N-04. **Nie sprawdzone empirycznie:** `astype(str)` zamienia `None` na napis `"None"`, więc po dopuszczeniu nulli dwa wiersze z pustym `unit` wyglądałyby na tę samą wartość klucza |
| 18 | **kontrola 6** — `checks/inconsistent_names.py:24–31`, `108` | pola badane = `text_key_fields`, w tym `case_id` i `stage` | przy obecnym mechanizmie `case_id`/`stage` wypadną; TECH-01 mówi o „nazwach jednostek" (ZOPTECH01 l.91) — N-04 |
| 19 | **bramka gotowości** — `engine/base.py:81`, `305–339` | tabela stanów: „wymagane strukturalnie = element `NATURAL_KEY`"; bramka czyta `fields_without_column` | brak kolumny jest już porażką strukturalną; `ReadinessReason.MISSING_COLUMN` (168–169) zmienia sens |
| 20 | `engine/noop01.py:41` | `required_by_test = {"ACTIVITY": ("date","unit","product")}` — dokładnie pola klucza; testy opierają na tym rozróżnienie (`tests/engine/test_readiness.py:52–53`, `235`) | rozróżnienie „NOOP-01 wymaga tylko klucza, atrapa pola spoza" traci znaczenie |
| 21 | **generator** — `synth/generator.py:18–21` | ograniczenie 1: „wiersz okresowy to agregat miesiąca — inaczej kontrola 4 zapaliłaby duplikaty na kluczu `date + unit + product`" | dane pozostają poprawne, uzasadnienie opiera się na kluczu |
| 22 | `synth/generator.py:271–274`; `synth/names.py:72–77` | uzasadnienie następstwa etapów: „klucz to `case_id + stage`" | sprzeczne z l.264 jako opis kontraktu |
| 23 | `synth/generator.py:287–333` | generuje unikalne pary `(case_id, stage)`; strażnik `tests/synth/test_generator.py:73–89` wymaga PASS kontroli 4 | generator nie importuje `NATURAL_KEY`; strażnik zależy od nowej definicji kontroli 4 |
| 24 | `demo/run.py:218–219` | drukuje `materialized_empty` | N-01 |
| 25 | `store/schema.py`, `store/findings.py`, `store/runs.py` | **nie opierają się** na kluczu (sprawdzone) | bez zmian z tego powodu |
| 26 | dokumentacja | DT-03 (notatka l.58–60), DT-08 (l.188), DT-19 (l.539–544), DT-20 (l.591–594); `schemat-architektury.md:167`, `171`, `229–232`; OK l.462–471, 556–571 | do aktualizacji po release |
| 27 | testy | sekcja 3 (A: 1–8, 13–14; B: `test_base`, `test_cost`, `test_registry`, `test_profile`, `test_zgodnosc`, `test_missing_columns`, `test_validation`, `test_names_and_time`, `test_generator`) | sekcja 3 |

---

## 5. Kolejność implementacji

Porządek wynika z zależności danych. Przy każdym kroku podano, **co musi istnieć wcześniej**
i **które pytania z sekcji 6 i 8 blokują** jego rozpoczęcie.

| Krok | Zakres | Wymaga | Zablokowany przez |
| --- | --- | --- | --- |
| **K0** | Controlling release | — | l.406; N-24 (brak źródeł decyzji w repozytorium) |
| **K1** | Kanonizacja i funkcja skrótu: SHA-256 hex, NFC, rozróżnienie zbiór/sekwencja, zachowanie typu (`identity.py`) | K0 | 6a |
| **K2** | Surowe fakty o źródle w imporcie: SHA-256 bajtów artefaktu, identyfikator obiektu/arkusza, fizyczny ordinal, manifest → `record_id` (`ingest/`) | K1 | N-05, N-06, N-07 |
| **K3** | Kontrakt strukturalny tabel: null dopuszczalny we wszystkich polach bazowych, koniec podziału klucz/nie-klucz, reprezentacja COLUMN_MISSING (`model/tables/`, `ingest/`) | K2 — bez `record_id` po odejściu od `NATURAL_KEY` wiersz w ramce i dowód w kontrolach nie mają tożsamości | N-01, N-02, N-03, N-21, N-25 |
| **K4** | Warstwa walidacji: kontrole 1, 3, 4, 6 i kontrakt komunikatu H (`validation/`) | K3; `affected_record_ids` wymaga K2; `affected_scope_id` wymaga K5 | N-04, N-15, N-16 |
| **K5** | Tożsamość zakresu (`refs.py`, `claim.py`, `evidence.py`, `priority.py`) | K1 (niezależne od K2–K4, można równolegle) | N-18 |
| **K6** | Kanoniczna reprezentacja okresu | K0 | **6b w całości** |
| **K7** | Tożsamość i provenance referencji | K1, K5, K6; SHA źródła wymaga K2 | 6a, N-17 |
| **K8** | Moduł, zależności walidacji, `test_execution_status` (`engine/`) | K4 — moduł czeka na wyniki walidacji z identyfikatorami | N-09, N-10, N-14, N-22 |
| **K9** | Tożsamość wyniku (`finding.py`) | K1, K5, K6, K7 (`reference_id`), K8 (`module_id`, `test_contract_version`) | N-08, N-12 |
| **K10** | Magazyn: niezmienne rekordy wyników, rekord techniczny wykonania, provenance wykonania (`store/`) | K2, K8, K9 | N-11, N-13 |
| **K11** | `validation_required` wobec PRI-01 | K8 — obecna bramka znika | N-14 |
| **K12** | Waluta: pole i skrót profilu (niezależne; może wejść wcześnie) oraz bramkowanie modułów pieniężnych (wymaga K8) | K0 / K8 | N-20 |
| **K13** | Wyłączenia | K2 (`record_id` jako podmiot), K5, K6, K9 (`EXAPP`) | 6c, N-19 |
| **K14** | Zgodność wersji | K9 (`test_contract_version`) | N-23; dziś brak konsumenta |

**Równolegle z każdym krokiem:** aktualizacja DT i sekcji C oraz nowe testy złote
przypisane do kroków:

| Scenariusz BIND | Krok |
| --- | --- |
| T08, T09 | K3 |
| T03 | K5 |
| T04, T14 | K7, K9, K10 |
| T12 | K9, K10 |
| T01, T02, T13 | K8 |
| T10 | K11 |
| T07 | K12 |
| T11, T15 | K13 |
| T05, T06 | K14 |

**Uwaga o NOOP-01 i demonstracji.** `demo/run.py` przechodzi przez K2, K3, K4, K8 i K9
naraz (`run.py:111–163`), a `tests/demo/test_demo.py` sprawdza cały łańcuch. Demonstracja
będzie czerwona od K2 do K9 włącznie, chyba że kroki zostaną pocięte inaczej.

---

## 6. Weryfikacja trzech otwartych pytań

### 6a. Czy kanonizacja z 4.1 obowiązuje także dla `reference_id`, `result_identity`, `record_id`, `exclusion_id`, `exclusion_application_key`?

**Werdykt: pytanie jest realne.** BIND tego nie rozstrzyga.

**Fakty z dokumentu:**

| Formuła | Linia | Zapis |
| --- | --- | --- |
| `scope_definition_hash` | l.103 | „SHA-256 **lowercase hex** z canonical **UTF-8** JSON scope_definition" |
| rozdział 4.1 | l.106 | tytuł: „Kanoniczna serializacja **scope**" |
| `reference_id` | l.135 | „SHA256(canonical JSON {…})" — bez UTF-8, bez formatu wyjścia, bez odesłania |
| `result_identity` | l.156 | „SHA-256(canonical JSON powyższych elementów)" — j.w. |
| `record_id` | l.234 | „SHA256(canonical UTF-8 JSON {…})" — bez formatu wyjścia, bez odesłania |
| `exclusion_id` | l.279 | „SHA256(canonical JSON {…})" — j.w. |
| `exclusion_application_key` | l.282 | „SHA256(canonical JSON {…})" — j.w. |

Dodatkowo:

- Reguły 4.1 mają różny zasięg w samym brzmieniu. Pkt 3 (predykaty filtrów) i pkt 6
  (`scope_label`) mówią wyłącznie o scope. Pkt 1, 2, 4, 5 są sformułowane ogólnie.
- W pliku markdown punkty 1–6 rozdziału 4.1 są zapisane jako nagłówki drugiego poziomu
  `## 1.` … `## 6.` (l.108–118), czyli na tym samym poziomie co rozdziały dokumentu
  (`## 1. ROLA…`, l.13). Strukturalnie wychodzą poza 4.1. Wygląda to na artefakt konwersji,
  ale z samego pliku nie da się ustalić ich zasięgu.
- „Lowercase hex" pada tylko przy `scope_definition_hash`. Postać wyjścia pozostałych
  „SHA256(…)" (hex? wielkość liter? bajty?) nie jest określona.

**Konsekwencja dla kodu.** Dziś jedna funkcja `canonical_form` (`identity.py:117–128`)
obsługuje wszystkie tożsamości, skrót profilu, `run_id`, skrót treści importu
(`reader.py:304`) i wartości generatora (`synth/values.py:41`).

- Jeżeli 4.1 obowiązuje wszędzie — NFC i zachowanie typu zmienią także `record_id`
  (np. nazwa arkusza z diakrytykiem zapisana w NFD) i wartości syntetyczne.
- Jeżeli obowiązuje tylko dla scope — potrzebne są dwie kanonizacje, a te same dane
  (np. `reference_scope_id` obok `reference_period`) zostaną zserializowane dwiema regułami
  w obrębie jednej formuły.
- Format wyjścia SHA dla `REF-`, `RESULT-`, `REC-`, `EXCL-`, `EXAPP-` jest dziś do
  zgadnięcia.

### 6b. Czy BIND definiuje kanoniczną postać `analysis_period`?

**Werdykt: pytanie jest realne.** BIND nie definiuje; karty nie definiują.

**Fakty:**

- `analysis_period`: „Wymagany, w kanonicznej reprezentacji właściwej dla karty" (l.154).
- `reference_period`: „kanoniczny okres/data referencji" (l.131) — bez formatu.
- `period` wyłączenia: „Kanoniczny okres obowiązywania wyłączenia" (l.275) — bez formatu
  i bez odesłania do karty.
- Rekord techniczny `TEST_NOT_APPLICABLE` wymaga `analysis_period` (l.79).
- 4.1 pkt 5 mówi tylko, że data i tekst nie są zamienne (l.116).
- Karty opisują `period` w FINDINGS opisowo, nie kanonicznie: FIN-01 „current + reference"
  (FIN01 l.305), CAP-01 „current + reference + horyzont" (CAP01 l.297), PROC-01
  „current + reference + horyzont / time_bucket" (PROC01 l.450), PROC-02
  „current + reference + time_bucket" (PROC02 l.482), PORT-01 i HR-01
  „current + reference + horyzont" (PORT01 l.354, HR01 l.350).
- Grep po `docs/zrodla/` za `analysis_period`, `kanoniczn`, `canonical`: poza BIND-01
  trafia wyłącznie `canonical_field_name` w MGT-01 — inne pojęcie.
- NOOP-01 nie implementuje żadnej karty (`engine/noop01.py:1–3`).

**Dodatkowa niespójność struktury.** Karty łączą w jednym polu `period` okres bieżący,
referencyjny i horyzont. BIND rozdziela `analysis_period` (element `result_identity`)
i `reference_period` (element `reference_id`). Gdzie trafia **horyzont** (1M/3M/6M/12M
w CAP-01 rozdz. 7, CAP01 l.169–173) — do `analysis_period`, `module_id` czy
`scope_definition` — nie wynika z żadnego dokumentu. Dla testów PROC `analysis_period`
wymaga przypisania zdarzeń do okresu, a tego A-01 zakazuje bez kontraktu `time_basis`
(OK l.103–124).

**Konsekwencja dla kodu.** `PeriodRef` (`refs.py:52–67`) ma granice i `period_label`,
a etykieta wchodzi dziś do tożsamości (`finding.py:195`). Bez definicji nie da się
zbudować `result_identity` dla NOOP-01 ani dla żadnego testu Core 10 w sposób, który
Aleksander obroni jako „z kontraktu". Nie da się też spełnić T04 (l.334), który zależy od
rozróżnienia dwóch `reference_period`.

### 6c. `record_id` z bajtów artefaktu wobec T14 dla referencji — czy asymetria jest zamierzona?

**Werdykt: asymetria jest realna w tekście. Zamiar nie jest wyrażony.**

**Fakty:**

- `record_id` zawiera `source_artifact_SHA256` (l.234). Te same dane w CSV i XLSX, a nawet
  ten sam CSV z innymi końcami linii, dają różne `record_id`.
- BIND świadomie nadaje `record_id` charakter fizyczny: „Nie oznacza business entity
  identity ani analytical grain" (l.230).
- `exclusion_subject_id` może być `record_id` (l.273); `exclusion_id` zawiera
  `exclusion_subject_id` (l.279), a `exclusion_application_key` również (l.282).
- Dla referencji BIND wymaga tożsamości **logicznej**: „Nie wolno zastępować
  reference_source_logical_id … physical SHA" (l.144); T14: inna kopia fizyczna lub
  poprawione bajty bez zmiany logicznego źródła → ten sam `reference_id` (l.344).
- Dla wyłączeń agregatowych BIND wymaga podmiotu logicznego (`SCOPE` + `scope_id`, l.290).
  Asymetria dotyczy więc wyłącznie podmiotu typu `RECORD`.
- `same_exclusion_can_be_linked_cross_test = true` (l.286) mówi o powiązaniu **między
  testami**, nie **między importami**. Samokontrola `A03_EXCLUSION_SUBJECT_IDENTITY =
  RESOLVED` (l.387) nie wspomina ponownego importu.

**Konsekwencja dla kodu.**

1. Wyłączenie zapisane na `record_id` jest przypięte do dokładnego artefaktu. Ponowny
   import tej samej treści w innym formacie da nowe `record_id`, więc istniejące
   `exclusion_id` i `exclusion_application_key` przestaną trafiać w rekordy.
2. Połączenie z DT-12: ten sam `run_id` przy różnych `record_id`. Jeżeli identyfikatory
   rekordów trafią do treści wyniku, `save_run` podniesie `ConflictingRun`
   (`store/findings.py:65–74`) — sekcja 2.4.
3. Obecny `row_id` ma dokładnie przeciwną własność: nie zależy od bajtów, zależy od nazwy
   pliku i `dataset_id` (`reader.py:153–163`; `report.py:84–94`).

---

## 7. Weryfikacja faktu z karty: CAP01-T10

**Pytanie:** czy karta mówi o braku kolumny `cost`, czy o nullu w istniejącej kolumnie.

**Fakty z `docs/zrodla/ZOPXRCAP01_v1.0_Karta_metodologiczna_testu_wykorzystania_zasobu.md`:**

| Linia | Miejsce | Brzmienie |
| --- | --- | --- |
| l.383 | CAP01-T10, kolumna „Scenariusz" | „Brak cost" |
| l.383 | kolumna „Dane" | „available i used poprawne; **cost null**" |
| l.383 | kolumna „Obliczenia" | „U, UC, UCR, UG i luka fizyczna; ekonomika null" |
| l.383 | kolumna „Status" | „wg trendu; nie TEST_BLOCKED" |
| l.383 | kolumna „Flagi / walidacja" | „WARNING; validation wg polityki" |
| l.383 | kolumna „FINDINGS" | „economic_gap=null; jawne ograniczenie" |
| l.110 | 4.1 Reguły wykonania | „brak cost \| miary fizyczne działają; economic_gap = null" |
| l.95 | CAP01-VAL-10 | „cost i podstawa kosztowa **dostępne** dla ekonomiki \| WARNING; ekonomika null albo wskaźnik brutto" |
| l.64 | rozdz. 3 | RESOURCE — pola bazowe: „date, unit, resource, available, used, **cost**" |
| l.70 | 3.1 | „Rozszerzenia nie zmieniają bazowej struktury ZOP-TECH-01" |

**Słowo „kolumna" / „column"** nie występuje w karcie CAP-01. Nie występuje też w żadnej
innej karcie Core 10 ani w PRI-01, CONF-01, ORCH-01, MASTER. Grep bez rozróżniania
wielkości liter po `docs/zrodla/` trafia wyłącznie w BIND-01 i ZOP-TECH-01.

**Ustalenie.**

- Jedyny opis **danych wejściowych** scenariusza T10 brzmi „cost null". To wartość null.
- „Brak cost" w nazwie scenariusza i w 4.1 nie mówi, czego brakuje. W karcie nie ma zdania,
  które opisywałoby nieobecność kolumny.
- Karta wymienia `cost` jako pole bazowe RESOURCE (l.64) i zastrzega nienaruszalność
  struktury bazowej (l.70).
- ZOP-TECH-01 5.3 podaje jako przykład braku wymaganej kolumny pole spoza klucza:
  „brak pola date, unit lub amount" (ZOPTECH01 l.86).
- T10 jest zgodny z BIND T09 (l.339): „amount istnieje; wartość null → MISSING_VALUE;
  nie COLUMN_MISSING; dalszy status wg source validation".

**Gdzie w naszych dokumentach i kodzie „null" stał się „brakiem kolumny":**

- DT-18 cytuje T10 **dosłownie z „`cost` null"** (notatka l.513–515). Wniosek o bramce
  (notatka l.520–525) dotyczy jednak braku kolumny, bo bramka sprawdza kolumny, a nie
  wypełnienie (`engine/base.py:290–292`).
- B-06: „czyli klient bez kolumny `cost` ma być obsługiwalny" (OK l.446–449);
  „Brak kolumny `cost` oznacza dziś odrzucenie każdego wiersza RESOURCE — dokładnie to,
  czego CAP-01 zakazuje" (OK l.458–459).
- `engine/base.py:94–98`: „brak `cost` daje miary fizyczne".
- `model/tables/resource.py:66–67`: „Brak kosztu nie unieruchamia tabeli".

**Odpowiedź.** Karta mówi o **nullu w istniejącym polu**. Gałąź PASS kontroli 1 opierała się
na założeniu, że karta dopuszcza brak kolumny — tego założenia karta nie wspiera. BIND 9.2
nie cofa więc niczego, co stoi w CAP-01; cofa nasze odczytanie.

**Dwa zastrzeżenia, żeby nie przesadzić w drugą stronę:**

1. B-06 zawiera nie tylko nasz odczyt karty, ale też **rozstrzygnięcie Michała** — trzy
   stany (OK l.507–527). To jest decyzja, a nie cytat, i BIND ją zmienia (sekcja 2.8).
   W samym rozstrzygnięciu pada „brak pola" bez rozróżnienia kolumny i wartości
   (OK l.514–518), więc niejednoznaczność nie była wyłącznie nasza.
2. „Odczytanie kryterium strukturalnego" (OK l.556–571) było zapisane jawnie „do
   ewentualnego zaprotestowania". BIND 9.2 działa jak ten protest.

---

## 8. Nowe niejednoznaczności

Bez propozycji rozwiązań. BIND deklaruje `CONTRACT_IMPLEMENTATION_AMBIGUITY_COUNT = 0`
(l.351), `implementation_ambiguity_count = 0` (l.379) i `OPEN_IMPLEMENTATION_AMBIGUITIES = 0`
(l.388). Poniżej 25 pozycji spoza listy pytań 6a–6c.

**N-01. Skutek `STRUCTURAL_SCHEMA_FAILURE`.**
Miejsce: l.250 wobec l.86–89 i tabeli l.71–77.
Niejednoznaczność: nie jest przypisany do `validation_severity` (PASS/WARNING/CRITICAL),
do zakresu MODULE/GLOBAL_TEST ani do tego, czy tabela zostaje zaimportowana i czy powstaje
ramka.
Konsekwencja: materializacja w `ingest/reader.py:243–283`, status kontroli 1, bramka
w `engine/base.py`, 11 testów z sekcji 3.2 opartych na plikach bez kolumny.

**N-02. Karty z kontrolą „istnieje X" o zasięgu modułowym.**
Miejsce: CAP01-VAL-01 „istnieje available | CRITICAL dla U, UC i luk" (CAP01 l.86),
CAP01-VAL-02 (l.87), PROC01-VAL-01 (PROC01 l.192), PROC02-VAL-01 (PROC02 l.132); wobec
BIND l.250. Klauzula „bardziej szczegółowy frozen contract ma pierwszeństwo" jest w l.91
i l.144, ale nie w 9.2.
Niejednoznaczność: czy „istnieje" w kartach znaczy kolumnę czy wartość; jeśli kolumnę —
czy brak kolumny `available` blokuje tabelę strukturalnie, czy tylko moduły U/UC.
Konsekwencja: zakres blokady w kontraktach A/B dla CAP i PROC.

**N-03. „Null jest dopuszczalny wyłącznie na etapie ingestion".**
Miejsce: l.248; wobec l.260 („required_value_missing → record_not_creditable_for_that_calculation").
Niejednoznaczność: dosłownie poza etapem ingestion null jest niedopuszczalny, a l.260
zakłada rekord z nullem obecny w kalkulacji.
Konsekwencja: typy modelu i ramki (DT-08, `reader.py:124–150`), kontrole 3 i 8.

**N-04. Kontrole 4 i 6 bez klucza naturalnego.**
Miejsce: l.228, 264; ZOP-TECH-01 5.3 kontrola 4 „powtarzające się rekordy wymagające
wyjaśnienia" i kontrola 6 „niespójne nazwy jednostek" (ZOPTECH01 l.89, 91).
Niejednoznaczność: co jest powtórzonym rekordem i które pola są „nazwami jednostek"; czy
`inferred_natural_key_allowed = false` dotyczy tylko tożsamości rekordu, czy też klucza
wykrywania duplikatów na poziomie fundamentu (karty mają własne klucze: FIN01 l.60,
CAP01 l.78).
Konsekwencja: `checks/duplicates.py`, `checks/inconsistent_names.py`, `text_key_fields`,
strażnik generatora.

**N-05. `record_id` — pole modelu czy metadane.**
Miejsce: „technicznym metadata field, a nie nowym polem biznesowym bazowej tabeli" (l.230)
wobec tabeli l.240, w której `record_id` stoi obok pól.
Konsekwencja: `extra="forbid"` w `TableRecord` (`base.py:254–262`), każda konstrukcja
rekordu w testach (ryzyko fałszywych przejść, sekcja 3.3), skład skrótu treści
(`reader.py:301–304`).

**N-06. `record_id` dla wierszy odrzuconych za format.**
Miejsce: `record_id_required = true` (l.220); `affected_record_ids` (l.206).
Niejednoznaczność: czy wiersz nieprzetłumaczalny na typ jest „rekordem", który musi mieć
identyfikator.
Konsekwencja: `Rejection` (`report.py:138–161`), `evidence_source_rows`
(`results.py:110–116`), kontrola 2.

**N-07. Składniki `record_id` dla CSV i XLSX.**
Miejsce: l.234–236.
Niejednoznaczność:
- czym jest `source_object_or_sheet_id` dla CSV;
- czym jest „import manifest" — pojęcie nie jest zdefiniowane w żadnym dokumencie;
- czy „fizyczny ordinal rekordu" dla CSV liczy linie czy rekordy (pusta linia, pole
  wieloliniowe — rozjazd potwierdzony empirycznie);
- czy numer wiersza arkusza obejmuje nagłówek;
- jak identyfikować domyślny arkusz, gdy import nie podaje nazwy;
- czy `source_artifact_SHA256` dla XLSX to skrót całego pliku.
Konsekwencja: `reader.py:166–180`, `216–222`, `275`; test `test_rozne_pliki_daja_rozne_identyfikatory`.

**N-08. Wersja w tożsamości wyniku i zasięg BIND wobec innych tożsamości.**
Miejsce: l.55, 151, 150–156.
Niejednoznaczność:
- format `test_contract_version` i jego wartość dla testu bez karty (NOOP-01);
- czy wersja kontraktu FINDINGS albo wersja samego BIND wpływa na `result_identity`
  (zamknięta lista jej nie zawiera);
- czy tożsamości `ClaimRecord`, `EvidenceRecord`, `ClaimEvidenceLink`, `SourceRef`, `RunRef`
  mają przejść na SHA-256 i kanonizację BIND — BIND o nich milczy.
Konsekwencja: `identity.py:34`, `finding.py:71`, `claim.py`, `evidence.py`,
`ingest/report.py`, `store/runs.py`.

**N-09. `test_execution_status` a pole `status`.**
Miejsce: l.79; wobec kart, które trzymają `TEST_PARTIAL`/`TEST_BLOCKED` w katalogu statusu
logicznego (CAP01 l.186) i wpisu B-02.
Niejednoznaczność: czy to osobne pole; jaki `status` niesie wynik `TEST_COMPLETE`; jaki jest
status testu, gdy moduły mają różne `module_result_status`.
Konsekwencja: `finding.py:88`, `enums.py:45–76`.

**N-10. Kto definiuje listę modułów i `module_id`.**
Miejsce: l.56–58, 152.
Fakty: FIN-02 wylicza moduły nazwami (FIN02 l.518–529); CAP-01, FIN-01, FIN-03, HR-01,
PORT-01 mówią o „modułach zależnych" bez wyliczenia (CAP01 l.82, 106; FIN01 l.71;
FIN03 l.189; HR01 l.100; PORT01 l.125). BIND zakazuje dopisywania semantyki testu (l.58).
Niejednoznaczność: skąd biorą się `module_id` dla kart, które modułów nie wyliczają; kiedy
wynik jest „nie-modułowy" (l.152), skoro status testu wynika z modułów (l.40).
Konsekwencja: deklaracja wtyczki, `result_identity`.

**N-11. Powtórne obliczenie a idempotencja.**
Miejsce: l.166 („Powtórne obliczenie tworzy nowy immutable result record").
Niejednoznaczność: czy identyczne wejście i identyczny kod mają dać nowy rekord, czy brak
operacji; jaki jest identyfikator **rekordu** wyniku — BIND definiuje tylko semantyczny
`result_identity`.
Konsekwencja: klucz główny `(finding_id, run_id)` (`schema.py:58`), `save_run`
(`store/findings.py:55–99`).

**N-12. `reference_applicable` — własność definicji wyniku czy wynik wykonania.**
Miejsce: l.142, 155.
Niejednoznaczność: jeżeli ustala się ją w wykonaniu, rekord `TEST_BLOCKED` (referencja nie
wyznaczona) i policzony wynik tej samej semantyki dostaną różne `result_identity`, a historia
opisana w DT-20 (notatka l.609–614) się rozpada.
Konsekwencja: `_blocked` (`engine/base.py:364–396`), `FindingStore.history`.

**N-13. Rekord wykonania, rekord wyniku, rekord techniczny.**
Miejsce: l.79, 144, 166, 344.
Niejednoznaczność: struktura i wzajemna relacja trzech rodzajów rekordu nie są określone;
czy wyniki `TEST_BLOCKED`, `TEST_PARTIAL`, `TEST_COMPLETE` też mają rekord techniczny.
Konsekwencja: `store/`.

**N-14. Czy silnik może ustawić `validation_required` bez podstawy w karcie.**
Miejsce: l.296 („source engine / frozen karta").
Konsekwencja: `engine/base.py:394` — bramka ustawia flagę z decyzji technicznej, a nie
z karty.

**N-15. „Exact source-defined severity" dla kontroli fundamentu.**
Miejsce: l.88, 202–203.
Fakty: ZOP-TECH-01 5.3 nie definiuje statusów dla ośmiu kontroli (ZOPTECH01 l.84–93);
sufity `max_status` to decyzje fundamentu (`schemat-architektury.md:165–174`). Katalog
`validation_code` nie jest nigdzie zdefiniowany.
Konsekwencja: deklaracje w `validation/checks/*.py`.

**N-16. Granica `technical_verification_suggestion`.**
Miejsce: l.208–214.
Niejednoznaczność: czy wskazanie testu diagnostycznego („kieruje do CAP-02") albo uwaga
„bywa poprawnym zapisem korekty" jest ścieżką techniczną, czy interpretacją biznesową.
Konsekwencja: `checks/resource_usage.py:111–116`, `checks/suspicious_values.py:94–97`.

**N-17. `reference_type` jako „exact value" przy różnych pisowniach tej samej referencji.**
Miejsce: l.130; FIN01 l.173 (`plan_budget`), CAP01 l.203 (`plan`), HR01 l.202 (`plan`).
Niejednoznaczność: czy ten sam plan użyty przez FIN-01 i CAP-01 to dwie różne referencje
semantyczne, bo różni je `reference_type`.
Konsekwencja: `enums.py:163–176`, B-04, `mapping/report.py:99–123`.

**N-18. Równoważność zapisów scope.**
Miejsce: l.98–101, 112, 120.
Niejednoznaczność:
- czy populacja wyrażona jako `population` i jako filtr `unit IN [...]` to ta sama semantyka
  (inaczej dwa zapisy dadzą dwa `scope_id` wbrew l.120);
- czy katalog operatorów jest zamknięty („np.", l.112);
- jak reprezentować datę w wartości predykatu;
- `aggregation_level` jako „zestaw wymiarów" (l.100) wobec pojedynczego poziomu.
Konsekwencja: `refs.py:25–49`.

**N-19. `source` w `exclusion_id` — logiczne czy fizyczne.**
Miejsce: l.276, 279.
Niejednoznaczność: czy poprawione bajty dowodu tworzą nowe `exclusion_id`; odpowiednika
reguły z 5.1 dla wyłączeń nie ma.
Konsekwencja: tożsamość `EXCL-`.

**N-20. Waluta bez pola i bez listy modułów pieniężnych.**
Miejsce: l.190–196; `fields_optional = NONE` (l.242–246).
Niejednoznaczność: tabele bazowe nie mają pola waluty, a pole bazowe nie może zostać
dodane jako opcjonalne; czym jest „source metadata" wskazujące kilka walut (l.194); które
moduły są „monetary" — karty tego nie oznaczają.
Konsekwencja: `mapping/profile.py`, `engine/`.

**N-21. Tabela zasilona z kilku artefaktów, z których jeden nie ma kolumny.**
Miejsce: l.250.
Niejednoznaczność: czy porażka strukturalna dotyczy artefaktu czy całej tabeli.
Konsekwencja: reguła „wystarczy jeden plik" (`engine/base.py:326–330`), krotka raportów
w `ValidationContext` (`context.py:49–67`), `test_pole_z_jednego_z_dwoch_plikow_wystarczy`.

**N-22. Brak tabeli opcjonalnej: `TEST_NOT_APPLICABLE` czy `TEST_BLOCKED`.**
Miejsce: l.79 (zakaz obchodzenia brakujących danych), l.260 („Optional table … nie oznacza
optional fields"); PLAN opcjonalna w CAP-01 (CAP01 l.66).
Niejednoznaczność: czy moduł zależny od nieobecnej tabeli opcjonalnej jest
`MODULE_NOT_APPLICABLE`, czy `MODULE_BLOCKED`.
Konsekwencja: `ReadinessReason.MISSING_TABLE` (`engine/base.py:165–166`).

**N-23. Forma i zasięg deklaracji zgodności wersji.**
Miejsce: l.176.
Niejednoznaczność: gdzie i w jakiej postaci powstaje deklaracja (żadna karta v1.0 jej nie
ma); czy zmiana formuł tożsamości w nowej wersji BIND wymaga deklaracji z F.
Konsekwencja: brak konsumenta dziś; krok K14.

**N-24. Źródła decyzji nieobecne w repozytorium.**
Miejsce: l.29 („pytania Aleksandra z 09.09.2026", „finalna Decision 08"), l.323, 381.
Fakty: grep po `docs/` — brak; sam BIND-01 jest nieśledzony w git.
Konsekwencja: nie da się zweryfikować, czy 9.1–9.2 wiernie oddają Decision 08, ani obronić
tego śladu przy obronie kodu.

**N-25. Kanonizacja pustego napisu wobec zakazu cichego nulla.**
Miejsce: l.254–258 (`silent_null_acceptance = false`, `default_value_substitution = false`);
4.1 pkt 1 zakazuje „trim" tylko przy scope.
Niejednoznaczność: czy zamiana `""` i `"   "` na null (DT-06; `base.py:167–183`) jest cichą
akceptacją nulla albo substytucją, skoro rozszerza się na wszystkie pola bazowe.
Konsekwencja: `OptionalKeyText`, typ pól dotychczas kluczowych, kontrola 6 (spacje jako dowód).

---

## Załącznik — błędy i niespójności znalezione przy okazji (nie poprawione)

| # | Miejsce | Opis |
| --- | --- | --- |
| Z-1 | `src/xray/mapping/__init__.py:144–146` | twierdzi, że „deklaracja waluty, reguła korekt — zostanie pokryta automatycznie" przez skrót profilu; `profile.py:179–199` buduje skrót z jawnej listy kluczy, więc nowe pole nie zostanie pokryte |
| Z-2 | `src/xray/model/tables/process.py:104–106`; `tests/model/test_process.py:45` | cytat „karty PROC-01 pkt 2.3 i PROC-02 pkt 2.3 wskazują jako klucz `case_id` i `stage`" nie ma pokrycia w kartach (PROC01 l.75–84, PROC02 l.67–76) |
| Z-3 | `src/xray/ingest/report.py:147–152` | `Rejection.file_row` obiecuje „numer, który klient znajdzie w swoim arkuszu"; dla CSV z pustą linią albo polem wieloliniowym numer jest mniejszy od fizycznego (potwierdzone empirycznie) |
| Z-4 | `src/xray/ingest/reader.py:172`, `220` | XLSX wczytany bez nazwy arkusza zapisuje `source_sheet = None` — nieodróżnialnie od CSV; ślad nie mówi, który arkusz przeczytano (potwierdzone empirycznie) |
| Z-5 | `src/xray/mapping/report.py:71–72`; `src/xray/mapping/__init__.py:96–99` | nieaktualne `# ASSUMPTION` z propozycją „pole spoza klucza → WARNING", odrzuconą 2026-09-08; reguła z OK l.20–23 każe po rozstrzygnięciu zmienić komentarz na `# DECYZJA` |
| Z-6 | `src/xray/ingest/__init__.py:48–49`; `src/xray/validation/checks/missing_values.py:19–21`; `docs/schemat-architektury.md:9`, `227–232` | nieaktualne: „brak wymaganej kolumny to kontrola 1 (CRITICAL)" przypisane do `mapping/`; „362 testy"; B-06 „czeka na decyzję Michała" z propozycją WARNING |
| Z-7 | `src/xray/engine/base.py:202`; eksport `engine/__init__.py:14`, `36` | publiczna klasa `TestReadiness` zaczyna się od `Test`, wbrew zasadzie DT-07 (notatka l.154–175); dziś żaden moduł testowy jej nie importuje, więc pytest jej nie zbiera (zbieranie bez ostrzeżeń) |
| Z-8 | `docs/otwarte-kontrakty.md:531–550` | tabela „Skutki dla kodu" w B-06 jest rozerwana: wiersz „\| deklaracja testu \| …" (l.550) stoi po akapitach l.536–549 |
| Z-9 | `src/xray/model/findings/identity.py:146–151` | docstring rejestru: „Dziś jest jedna wersja, więc rozgałęzienia faktycznie nie ma", a rejestr ma wersje `"1"` i `"2"` (139–145) |
