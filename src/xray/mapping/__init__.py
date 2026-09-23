# Implementuje ZOP-TECH-01 v0.1 pkt 5.3 kontrola 1 oraz pkt 10.3 (mapowanie kolumn),
# a także rozstrzygnięcie B-04 (jawne mapowanie miar planu).
"""Mapowanie danych klienta na wspólny model.

Profil i jego zastosowanie są zaimplementowane w ``profile.py`` i ``report.py``.
Poniżej kontrakt, według którego obie części powstały.

Rozróżniamy dwie rzeczy, które łatwo zlać w jedną: **profil** jest wejściem
(deklaracją klienta, plik YAML), **raport mapowania** jest wyjściem (opisem tego, co
z tej deklaracji wyszło na konkretnych plikach).

---

# CZĘŚĆ I — PROFIL MAPOWANIA (wejście)

Jeden profil = jeden klient = jeden zbiór danych. Sześć elementów; przy każdym punkt,
z którego wynika.

**1. `dataset_id`** — ZOP-TECH-01 pkt 5.1, wpis DT-10.

Wartość **zadeklarowana**, a nie wyprowadzana ze ścieżki katalogu ani z nazwy pliku —
wyprowadzana byłaby zgadywana. Bez niej dwóch klientów przysyłających plik o nazwie
``koszty.csv`` dostałoby ten sam ``source_id``, a więc te same identyfikatory wierszy
dla tych samych numerów; w magazynie obejmującym więcej niż jeden zbiór ślad wskazywałby
nie ten plik.

**2. `organization_timezone`** — wpis DT-05.

Strefa, w której ``ingest/`` przelicza znaczniki czasu ze strefą na czas lokalny
organizacji. Model odmawia przyjęcia znacznika ze strefą, bo dwa nieporównywalne typy
w jednej kolumnie rozsypałyby kontrolę 8; konwersję robi warstwa, która zna kontekst
pliku. Strefa jest **zadeklarowana w profilu**, a nie zaszyta w kodzie, więc jest
udokumentowana i audytowalna.

**3. `columns`** — ZOP-TECH-01 pkt 10.3, kryterium odbioru 8.1.

Przypisanie **pole kontraktu → kolumna klienta**, osobno dla każdej tabeli. To jedyna
treść, jaką profil ma o kolumnach.

Kierunek nie jest kwestią gustu. Przy zapisie ``pole: kolumna`` niewyrażalne staje się
przypisanie **dwóch kolumn do jednego pola** — przypadek zakazany decyzją D-B. Naturalne
pozostaje **jedna kolumna do dwóch pól** (D-C), bywające uprawnionym.

Profil **nie deklaruje, które pola są wymagane**. Ta wiedza jest już w kontrakcie
danych (``TableRecord.model_fields``, ``NATURAL_KEY``) i jest maszynowo odczytywalna.
Gdyby lista wymaganych leżała w profilu, klient mógłby ją skrócić i import przeszedłby
bez pola wymaganego przez kartę — reguła metodologiczna wpełzłaby do danych wejściowych.

**4. `plan_metrics`** — rozstrzygnięcie B-04 (Michał, 2026-09-05).

Żadnego automatycznego dopasowania PLAN do miary testu; fundament **wymaga** jawnego
mapowania i zgodności definicji.

| Element deklaracji | Znaczenie |
| --- | --- |
| ``plan_metric`` | wartość ``PLAN.metric`` z danych klienta, bez normalizacji |
| ``target_measure`` | miara testu, której ta wartość odpowiada |
| ``definition_match_basis`` | na czym polega zgodność definicji obu miar |
| ``declared_by`` / ``declared_at`` | kto i kiedy zadeklarował zgodność |

``definition_match_basis`` nie jest ozdobą: ZOP-XR-FIN-01 rozdz. 6 dopuszcza plan jako
źródło referencji wyłącznie pod warunkiem „zgodna definicja miary", a bez zapisanej
podstawy tego warunku nie da się sprawdzić ani odtworzyć.

**Brak deklaracji nie jest błędem importu.** PLAN wczytuje się normalnie, rekordy
przechodzą kontrakt, kontrole danych działają. Skutek jest węższy: dla miary bez
deklaracji PLAN **nie może posłużyć jako** ``reference_type = plan_budget``.

**5. `profile_id` i `profile_version`** — zasada 4 (audytowalność).

Który profil i w jakiej wersji wyprodukował mapowanie. Bez tego nie da się odtworzyć,
skąd wzięło się przypisanie kolumn w konkretnym przebiegu.

**6. Nic więcej** — zasada 1.

Żadnych progów, wag, klasyfikacji ani list pól wymaganych. Profil mapuje **nagłówki
kolumn**, nie wartości i nie reguły.

---

# CZĘŚĆ II — RAPORT MAPOWANIA (wyjście)

**1. Kolumny zmapowane** — kolumna klienta i pole kontraktu, na które trafiła.

**2. Kolumny niezmapowane** — kolumny obecne w pliku, dla których nie ma miejsca
w kontrakcie. To pozycja w raporcie, **nie awaria**.

Lista niezmapowanych jest przyszłym miejscem podpięcia rozszerzeń z kart. Karty Core 10
definiują dziesiątki pól opcjonalnych (``capacity_unit`` z CAP-01, ``labor_input``
z HR-01, ``portfolio_item`` z PORT-01, ``queue_time`` z PROC-01), które dziś nie mają
odpowiednika w kontrakcie. Kolumna dziś niezmapowana jutro może być polem rozszerzenia —
dlatego raportujemy ją, zamiast pomijać.

**3. Pola kontraktu bez przypisanej kolumny** — kontrola 1 z pkt 5.3.

# ASSUMPTION: kryterium „kolumna wymagana" nie jest rozstrzygnięte — patrz
# docs/otwarte-kontrakty.md, wpis B-06. Propozycja robocza: element NATURAL_KEY →
# CRITICAL, pole spoza klucza → WARNING. Kierunek wynika z hierarchii kart (ZOP-XR-CAP-01
# pkt 4.1 jest zamrożona i dopuszcza brak `cost`), ale samo kryterium czeka na Michała.

**4. Kolumny zmaterializowane jako puste** — konsekwencja punktu 3.

Brakująca kolumna spoza klucza jest materializowana jako w całości pusta. ``None``
oznacza tu **nieobecność kolumny**, a nie wartość zastępczą wstawioną w miejsce danych —
zasada 5 nie jest naruszona, ale rozróżnienie musi być **widoczne w raporcie**, a nie
domyślane z liczby braków. Bez tego wpisu „100% braków w polu ``cost``" wyglądałoby
identycznie jak „kolumna była, ale pusta", a to dwie różne rozmowy z klientem.

**5. Kolumny użyte więcej niż raz** — konsekwencja decyzji D-C.

Jedna kolumna klienta może zasilać więcej niż jedno pole kontraktu; bywa to uprawnione
(plik, w którym nazwa zasobu jest zarazem nazwą jednostki), a zakaz wymagałby reguły,
której z kontraktu nie da się wywieść. Ciche dopuszczenie ukrywałoby jednak częstą pomyłkę
w profilu, więc **odnotowujemy fakt**.

To nie wystarczy. Jedna kolumna przypisana jednocześnie do ``available`` i ``used``
sprawia, że kontrola 7 nigdy nie może zgłosić sygnału i wypisuje PASS przy każdym
przebiegu — czyli jest **fałszywie przechodzącą kontrolą**, tą samą klasą błędu co
w DT-07, tylko wpuszczoną przez konfigurację zamiast przez kod. Dlatego: gdy pola czytane
przez kontrolę pochodzą z jednej kolumny klienta, kontrola ogłasza ``not_assessable``
z podstawą, a **nie** PASS.

---

# CZĘŚĆ III — PROFIL A TOŻSAMOŚĆ PRZEBIEGU

**Znacząca treść profilu wchodzi do ``run_id``.**

Wcześniejszy zapis mówił, że profil jest pokryty przez ``content_digest``, bo zmiana
mapowania zmienia treść rekordów. Dla przypisań kolumn i strefy czasowej to prawda.
Dla ``plan_metrics`` **nie**: dodanie deklaracji miary planu nie zmienia treści żadnego
rekordu, więc nie zmienia skrótu treści, więc nie zmienia ``run_id`` — a zmienia wynik,
bo dopiero z nią PLAN może służyć jako ``reference_type = plan_budget``.

Skutek błędnego zapisu byłby taki: ten sam ``finding_id``, ten sam ``run_id``, inna treść
→ para wykonań, którą warstwa porównania sklasyfikuje jako ``NONDETERMINISM_CONFLICT``.
A przepływ jest deterministyczny. Diagnoza byłaby fałszywa — i po rundzie V12-R1 **trafiłaby
do magazynu**, bo sprzeczności już nie odrzucamy, tylko zapisujemy i oceniamy.

Do tożsamości przebiegu wchodzi więc **znacząca treść profilu**: faktycznie użyte
przypisania kolumn, ``plan_metrics``, ``organization_timezone``. Nie wchodzą: bajty pliku,
komentarze, formatowanie ani przypisania do kolumn, których w plikach nie było — ta sama
racja co w DT-12 (skrót z treści, nie z zapisu).

Zakres jest szerszy, niż wymaga sam kontrprzykład, i celowo: następny element
interpretacyjny profilu — deklaracja waluty, reguła korekt — zostanie pokryty
automatycznie, zamiast powtórzyć ten sam błąd.

---

# CZEGO MAPOWANIE NIE ROBI

Nie normalizuje wartości. ``PLAN.metric`` przechodzi taki, jaki przyszedł; nazwy
jednostek nie są przycinane ani ujednolicane — to dowód dla kontroli 6 z pkt 5.3.

Nie sumuje ani nie wybiera. **Dwie kolumny klienta na jedno pole kontraktu są zakazane**:
zsumowanie ``koszt_netto`` i ``koszt_brutto`` w ``amount`` byłoby regułą biznesową ukrytą
w konfiguracji, a takiego rozstrzygnięcia nie robi żadna karta (zasada 1). Klient, który
potrzebuje sumy, liczy ją przed przekazaniem pliku — wtedy decyzja jest jego i jest
widoczna.

Nie wiąże plików z tabelami. Ścieżka pliku pozostaje argumentem ``ingest.load_table``,
a profil jest profilem **kolumn**, nie konfiguracją uruchomienia.

Model danych nigdy nie ogląda niezmapowanej kolumny: to ``mapping/`` decyduje, co gdzie
trafia, zanim rekord dojdzie do bramki kontraktu w ``ingest/``.
"""

from xray.mapping.profile import MappingProfile, PlanMetricDeclaration, ProfileError
from xray.mapping.report import MappingReport, apply_profile

__all__ = [
    "MappingProfile",
    "MappingReport",
    "PlanMetricDeclaration",
    "ProfileError",
    "apply_profile",
]
