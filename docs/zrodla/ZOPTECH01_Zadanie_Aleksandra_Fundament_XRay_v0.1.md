ZOPTYMALIZOWANI

# ZADANIE TECHNICZNE 01

Fundament technologiczny systemu X-Ray

Pierwsze zadanie dla Aleksandra

> ****

| Kod dokumentu | ZOP-TECH-01 |
| --- | --- |
| Wersja | v0.1 |
| Adresat | Aleksander |
| Obszar | Technologia, dane, przygotowanie wersji pilotażowej X-Ray |
| Termin roboczy | około 7 dni spokojnej pracy |
| Status | zadanie założycielskie - bez budowy pełnej aplikacji |

## 1. Cel dokumentu

Niniejszy dokument definiuje pierwsze zadanie technologiczne w projekcie Zoptymalizowani. Jego celem nie jest zbudowanie gotowej aplikacji, lecz przygotowanie uporządkowanego fundamentu, na którym będzie można bezpiecznie rozwijać system X-Ray - narzędzie do diagnostyki zarządczej organizacji.

Efektem pracy ma być niewielki, zrozumiały i możliwy do rozbudowy szkielet rozwiązania: model danych, mechanizm przyjmowania i sprawdzania plików, struktura zapisu wyników oraz generator danych testowych. Na tym etapie ważniejsza od wyglądu jest poprawność konstrukcji.

> **Zasada nadrzędna: najpierw porządkujemy dane i logikę obliczeń. Interfejs użytkownika, sztuczna inteligencja i automatyczne rekomendacje powstaną dopiero wtedy, gdy fundament będzie stabilny.**

## 2. Kontekst i uzasadnienie

Zoptymalizowani mają docelowo pomagać właścicielom i osobom zarządzającym odpowiadać na pytania, które w wielu organizacjach pozostają bez szybkiej odpowiedzi: co naprawdę wpływa na wynik, gdzie powstają straty, które zasoby są niewykorzystane, gdzie tworzą się wąskie gardła i które działanie powinno mieć najwyższy priorytet.

Pierwszym planowanym produktem jest X-Ray - ustandaryzowana diagnostyka organizacji. Nie ma ona być kolejnym raportem z dużą liczbą wykresów. Ma prowadzić od danych do wniosku zarządczego: objaw, dowód, możliwa przyczyna, skala, wpływ ekonomiczny, priorytet oraz dalszy krok.

Żeby taki system mógł powstać, trzeba najpierw zbudować wspólny język danych. Każdy przyszły klient będzie miał inne pliki, inne nazwy kolumn i inne systemy. Pierwsze zadanie technologiczne ma więc odpowiedzieć na pytanie, czy potrafimy sprowadzić różne dane do prostego, spójnego modelu i wiarygodnie ocenić ich jakość.

## 3. Miejsce zadania w architekturze X-Ray

| 1 | WARSTWA DANYCH | Import, sprawdzenie, normalizacja i zapis danych. |
| --- | --- | --- |
| 2 | SILNIK DIAGNOSTYCZNY | Obliczenia, testy, odchylenia, trendy, ocena wpływu i priorytetu. |
| 3 | INTERPRETACJA | Opis wyników, hipotezy przyczyn i pytania weryfikacyjne. |
| 4 | WSPARCIE DECYZJI | Priorytety działań, ścieżki diagnostyczne i rekomendowane następne kroki. |
| 5 | PREZENTACJA | Czytelny widok dla właściciela lub zarządu. |

Zadanie ZOP-TECH-01 dotyczy wyłącznie warstwy 1 oraz przygotowania technicznego do warstwy 2. Nie obejmuje jeszcze automatycznej interpretacji, sztucznej inteligencji ani pełnego interfejsu użytkownika.

## 4. Zasady wykonania

4.1. Prostota. Rozwiązanie ma być możliwe do zrozumienia i utrzymania przez jedną osobę. Nie budujemy infrastruktury na skalę, której jeszcze nie potrzebujemy.

4.2. Modułowość. Import, sprawdzanie danych, obliczenia i zapis wyników powinny być rozdzielone tak, aby można je było rozwijać niezależnie.

4.3. Powtarzalność. Ten sam kod powinien móc przyjąć kolejny zestaw danych bez przepisywania całego rozwiązania.

4.4. Jawność obliczeń. Każda liczba używana później w diagnozie powinna mieć możliwe do prześledzenia źródło i sposób wyliczenia.

4.5. Brak danych rzeczywistych. W tym etapie pracujemy wyłącznie na danych syntetycznych lub technicznych danych testowych. Nie wykorzystujemy danych SPZOZ, danych pacjentów ani poufnych danych jakiejkolwiek rzeczywistej organizacji.

4.6. Brak sztucznej inteligencji na tym etapie. Najpierw ma działać matematyka, walidacja i przepływ danych. Modele językowe i inne mechanizmy AI będą dołączane do stabilnego rdzenia, a nie odwrotnie.

## 5. Zakres zadania

### 5.1. Propozycja architektury technologicznej

Aleksander powinien zaproponować możliwie prostą architekturę wersji pilotażowej. Preferowanym środowiskiem jest Python, ale dobór bibliotek, sposobu przechowywania danych i organizacji kodu pozostaje po jego stronie.

Propozycja powinna obejmować import plików XLSX i CSV, walidację, normalizację, obliczenia, zapis wyników oraz możliwość późniejszego dołączenia warstwy prezentacyjnej i sztucznej inteligencji. Każda ważniejsza decyzja techniczna powinna mieć krótkie uzasadnienie: dlaczego to rozwiązanie jest odpowiednie na obecnym etapie.

### 5.2. Szkielet wspólnego modelu danych

Należy przygotować pięć podstawowych struktur danych. Nazwy techniczne pozostają na razie w języku angielskim, ponieważ będą używane w kodzie. Nie oznacza to przyjęcia angielskiego nazewnictwa w komunikacji z klientem.

| Tabela techniczna | Znaczenie | Minimalny zakres pól |
| --- | --- | --- |
| ACTIVITY | Aktywność i przychód | date, unit, product, volume, revenue |
| COST | Koszty | date, unit, category, amount |
| RESOURCE | Zasoby i ich wykorzystanie | date, unit, resource, available, used, cost |
| PROCESS | Przebieg procesu | case_id, stage, start, end, unit |
| PLAN | Plan i wartości docelowe | date, unit, metric, target |

### 5.3. Walidator danych wejściowych

System ma przed wykonaniem jakichkolwiek analiz sprawdzić, czy dane nadają się do użycia. Walidator powinien co najmniej rozpoznawać poniższe problemy.

| Lp. | Kontrola | Przykład wyniku |
| --- | --- | --- |
| 1 | Brak wymaganej kolumny | np. brak pola date, unit lub amount. |
| 2 | Nieprawidłowy format danych | np. tekst w polu liczbowym albo niespójny format daty. |
| 3 | Brakujące wartości | wykaz pól i liczba braków. |
| 4 | Duplikaty | powtarzające się rekordy wymagające wyjaśnienia. |
| 5 | Wartości podejrzane | np. ujemny przychód lub koszt, jeśli nie został oznaczony jako korekta. |
| 6 | Niespójne nazwy jednostek | np. Dział A, dział A i DZIAL_A jako trzy różne wartości. |
| 7 | Nielogiczne wykorzystanie zasobu | np. used większe od available. |
| 8 | Zakres czasowy | informacja, ile miesięcy obejmuje zbiór i czy są w nim luki. |

### 5.4. Struktura zapisu wyników FINDINGS

Należy przygotować jedną strukturę wynikową, do której w przyszłości będą zapisywane rezultaty wszystkich testów diagnostycznych. Na tym etapie nie trzeba jeszcze wdrażać logiki FIN-01 ani pozostałych testów.

| Pole | Znaczenie |
| --- | --- |
| test_id | kod testu, np. FIN-01 |
| scope | zakres analizy, np. cała firma, jednostka, produkt |
| period | okres, którego dotyczy wynik |
| status | STANDARD / MEDIUM / HIGH / CRITICAL |
| finding | krótki opis wykrytego zjawiska |
| metric_value | wartość badanego wskaźnika |
| reference_value | wartość odniesienia |
| gap | odchylenie |
| impact_low / impact_high | przedział szacowanego wpływu ekonomicznego |
| confidence_score | techniczna ocena pewności 0-1 |
| confidence_class | klasa pewności A / B / C |
| next_tests | kolejne testy sugerowane przez ścieżkę diagnostyczną |
| validation_required | informacja, czy wniosek wymaga ręcznej weryfikacji |

### 5.5. Generator danych syntetycznych

Należy przygotować prosty generator fikcyjnej firmy, który pozwoli testować import, walidację i późniejsze obliczenia bez sięgania do danych rzeczywistych.

5.5.1. Skala. około 100 pracowników lub zasobów, 5 jednostek organizacyjnych i kilka produktów lub usług.

5.5.2. Horyzont. 24 miesiące danych, aby możliwe było późniejsze badanie trendów i porównań rok do roku.

5.5.3. Zakres. dane powinny zasilać wszystkie pięć tabel podstawowych.

5.5.4. Etap pierwszy. na razie nie trzeba celowo zaszywać problemów biznesowych. Wystarczy realistyczna struktura danych.

5.5.5. Etap kolejny. po zatwierdzeniu pierwszych testów diagnostycznych powstanie osobna wersja zbioru z celowo wprowadzonymi odchyleniami.

### 5.6. Dokumentacja techniczna

Kod powinien być przekazany razem z krótką dokumentacją, pozwalającą odtworzyć środowisko i uruchomić rozwiązanie bez wiedzy autora. Dokumentacja ma być praktyczna, nie akademicka.

## 6. Czego świadomie nie robimy

6.1. Nie budujemy pełnej aplikacji webowej ani mobilnej.

6.2. Nie projektujemy jeszcze wyglądu panelu zarządczego.

6.3. Nie wdrażamy modeli językowych, chatbotów ani automatycznych rekomendacji AI.

6.4. Nie integrujemy się jeszcze z ERP, CRM, systemami księgowymi ani zewnętrznymi interfejsami API.

6.5. Nie korzystamy z danych rzeczywistych klientów, SPZOZ ani jakichkolwiek danych pacjentów.

6.6. Nie próbujemy od razu rozwiązywać problemu skalowania na setki klientów.

6.7. Nie zamykamy technologii na przyszłość. Wersja pilotażowa ma być prosta, ale nie jednorazowa.

## 7. Produkty do przekazania

| Lp. | Produkt | Minimalna zawartość | Forma |
| --- | --- | --- | --- |
| 1 | Kod wersji pilotażowej | import, walidacja, model danych, zapis wyników | repozytorium / pliki |
| 2 | README | instrukcja uruchomienia i opis struktury | plik tekstowy |
| 3 | Schemat architektury | prosty diagram komponentów i przepływu danych | 1 strona |
| 4 | Notatka techniczna | najważniejsze decyzje technologiczne wraz z uzasadnieniem | 1-2 strony |
| 5 | Zbiór syntetyczny | fikcyjna firma 24 miesiące | CSV/XLSX lub generator |
| 6 | Krótka demonstracja | uruchomienie importu, walidacji i zapisu wyniku | 10-20 minut |

## 8. Kryteria odbioru

8.1. Rozwiązanie przyjmuje przykładowe pliki XLSX i CSV bez ręcznej ingerencji w kod przy każdym uruchomieniu.

8.2. Dane są mapowane do pięciu uzgodnionych struktur i można sprawdzić ich zakres czasowy.

8.3. Walidator wykrywa co najmniej osiem kategorii błędów opisanych w rozdziale 5.3.

8.4. Komunikaty walidatora są zrozumiałe: wskazują problem, jego miejsce i proponowany sposób dalszej weryfikacji.

8.5. Istnieje działająca struktura FINDINGS gotowa do przyjmowania wyników przyszłych testów.

8.6. Generator danych tworzy powtarzalny, spójny zestaw syntetyczny dla fikcyjnej firmy.

8.7. Kod jest podzielony na logiczne części i opisany w sposób pozwalający go dalej rozwijać.

8.8. Nie ma zależności od danych rzeczywistej organizacji ani elementów wymagających dostępu do środowiska SPZOZ.

## 9. Zalecana kolejność pracy

1. Najpierw zaprojektuj schemat rozwiązania na jednej stronie. Nie koduj, dopóki nie wiesz, które elementy mają być od siebie niezależne.

2. Zbuduj pięć struktur danych i kilka ręcznych rekordów testowych.

3. Zaimplementuj import oraz mapowanie danych.

4. Dodaj walidację i raport jakości danych.

5. Dodaj strukturę FINDINGS.

6. Zbuduj generator firmy syntetycznej.

7. Przetestuj całość od początku do końca.

8. Dopiero na końcu uporządkuj dokumentację i przygotuj krótką demonstrację.

## 10. Pytania, na które Aleksander ma odpowiedzieć sam

W zadaniu celowo pozostawiamy część decyzji technicznych otwartych. Chcemy ocenić nie tylko wykonanie kodu, ale również sposób myślenia o produkcie i architekturze.

10.1. Jakiego sposobu przechowywania danych użyć w pierwszej wersji i dlaczego?

10.2. Jak rozdzielić warstwę importu, walidacji, obliczeń i zapisu wyników?

10.3. Jak zaprojektować mapowanie różnych nazw kolumn klienta do wspólnego modelu?

10.4. Które błędy danych powinny zatrzymywać analizę, a które tylko generować ostrzeżenie?

10.5. Jak zapewnić możliwość łatwego dodawania kolejnych testów diagnostycznych bez przebudowy całego kodu?

10.6. Jakie testy automatyczne warto napisać już na tym etapie?

## 11. Co nastąpi po odbiorze

Po zatwierdzeniu ZOP-TECH-01 Aleksander otrzyma pierwszą pełną kartę testu diagnostycznego FIN-01 - dynamika kosztów względem przychodów. Jego zadaniem będzie zaimplementowanie tego testu na przygotowanym fundamencie.

Następnie do biblioteki będą dokładane kolejne testy podstawowe, w szczególności CAP-01 - wykorzystanie zasobu, HR-01 - koszt pracy względem efektu, PORT-01 - rentowność portfela oraz PROC-02 - wąskie gardło procesu.

Pierwszym istotnym kamieniem milowym będzie moment, w którym system na specjalnie przygotowanej fikcyjnej firmie samodzielnie wykryje celowo zaszyte problemy i zapisze je w jednolitej strukturze wyników. Dopiero po osiągnięciu tego etapu zasadne będzie projektowanie pełniejszego panelu zarządczego i warstwy AI.

## 12. Sens tego zadania

> **Nie chodzi o to, aby napisać dużo kodu. Chodzi o zbudowanie pierwszego fragmentu systemu, w którym wiedza o zarządzaniu może zostać zapisana w sposób powtarzalny, testowalny i możliwy do automatyzacji.**

Jeżeli ten fundament będzie dobry, dalsza praca będzie polegała na dokładaniu kolejnych reguł diagnostycznych i uczeniu systemu sposobu patrzenia na organizację. W ten sposób doświadczenie zarządcze może stopniowo zostać przełożone na produkt technologiczny, który nie tylko pokazuje dane, ale pomaga zrozumieć, gdzie naprawdę znajduje się problem.

> **Oczekiwany rezultat po około 7 dniach: działający, prosty i dobrze udokumentowany fundament X-Ray, gotowy do przyjęcia pierwszego testu FIN-01.**
