ZOPTYMALIZOWANI

# ZOP-MASTER-01

Dokument przewodni projektu Zoptymalizowani

Cel, pierwszy produkt, role, architektura i plan dojścia do działającego X-Ray

> **STATUS AKTYWNY MASTER PROJEKTU – prowadzi kierunek prac, ale nie zastępuje zamrożonych kart metodologicznych FIN-01, CAP-01 i HR-01.**

| Pole | Wartość |
| --- | --- |
| Identyfikator | ZOP-MASTER-01 |
| Wersja / data | v1.0 / 2 września 2026 |
| Odbiorcy | Michał i Aleksander |
| Pierwszy produkt | Zoptymalizowani X-Ray – diagnostyka zarządcza organizacji |
| Stan prac | fundament technologiczny w realizacji; 3 testy Core 10 zamrożone metodologicznie |
| Zasada aktualizacji | Master aktualizujemy po istotnym kamieniu milowym lub decyzji zmieniającej kierunek projektu |

> **SENS MASTERU Ten dokument ma sprawić, żebyśmy obaj w każdej chwili potrafili odpowiedzieć na trzy pytania: co budujemy, dlaczego to budujemy i co jest następnym krokiem.**

## 1. Po co istnieje ten dokument

ZOP-MASTER-01 jest wspólnym przewodnikiem projektu. Nie ma zastępować szczegółowych kart testów ani instrukcji technicznych. Ma utrzymywać spójność pomiędzy pomysłem biznesowym, metodologią zarządczą i kodem, który powstaje po stronie technologicznej.

1.1. Dla Michała  Master ma być mapą decyzji: jaki problem rynkowy rozwiązujemy, jakie zasady są już zamrożone, które elementy metodologii trzeba jeszcze zbudować i kiedy produkt będzie wystarczająco dojrzały, aby pokazać go klientowi.

1.2. Dla Aleksandra  Master ma wyjaśniać sens kodu. Każdy moduł techniczny ma mieć miejsce w większej całości: dane są porządkowane po to, aby testy mogły wygenerować wiarygodne FINDINGS, a FINDINGS mają prowadzić do decyzji zarządczej, nie do kolejnego wykresu.

1.3. Dla projektu  Master rozdziela elementy zamrożone, robocze i otwarte. Dzięki temu nie przebudowujemy raz uzgodnionych fundamentów przy każdym nowym pomyśle.

## 2. Co właściwie budujemy

Zoptymalizowani mają być połączeniem wiedzy zarządczej i technologii. Nie zaczynamy od pytania „jaką aplikację możemy stworzyć?”. Zaczynamy od pytania „jaką decyzję zarządzający powinien móc podjąć szybciej i lepiej dzięki danym?”.

> **CEL NADRZĘDNY Zbudować powtarzalny system, który z niejednorodnych danych organizacji potrafi przejść do wiarygodnej diagnozy: co się dzieje, gdzie, od kiedy, jak duża jest skala, co może być przyczyną i co należy sprawdzić dalej.**

### 2.1. Problem, który chcemy rozwiązać

W wielu organizacjach dane istnieją, ale informacja zarządcza jest rozproszona. Zarząd otrzymuje zestawienia kosztów, sprzedaży, czasu pracy lub aktywności, jednak nadal nie ma szybkiej odpowiedzi na pytanie, co naprawdę zmienia wynik i gdzie rozpocząć działanie.

Naszą odpowiedzią nie ma być kolejny panel z kilkudziesięcioma wskaźnikami. System powinien uporządkować dane, wykryć odchylenie, sprawdzić jego trwałość i porównywalność, oszacować skalę oraz skierować diagnozę do kolejnego właściwego testu.

### 2.2. Co klient ma ostatecznie kupować

| Klient nie kupuje przede wszystkim | Klient kupuje |
| --- | --- |
| aplikacji | zrozumienie, co wymaga uwagi |
| wykresów | dowód i skalę zjawiska |
| samego AI | kontrolowaną diagnozę opartą na danych |
| godzin konsultanta | powtarzalny proces dojścia od danych do decyzji |
| obietnicy oszczędności | informację, gdzie istnieje luka i co trzeba zweryfikować przed decyzją |

## 3. Pierwszy produkt: Zoptymalizowani X-Ray

Pierwszym rzeczywistym produktem ma być X-Ray – ustandaryzowana diagnostyka zarządcza organizacji. W pierwszej fazie będzie to usługa wsparta własnym silnikiem analitycznym, a nie samodzielny program sprzedawany klientowi bez udziału człowieka.

> **CZTERY PYTANIA X-RAY Co się dzieje? → Gdzie i od kiedy? → Jaka jest skala i wpływ? → Co trzeba sprawdzić lub zrobić w pierwszej kolejności?**

### 3.1. Minimalny przebieg X-Ray

| Etap | Co się dzieje | Rezultat |
| --- | --- | --- |
| 1. Przyjęcie danych | pliki XLSX/CSV są mapowane do wspólnego modelu | spójny zestaw wejściowy |
| 2. Kontrola jakości | system wykrywa braki, duplikaty, niespójności i ograniczenia | raport walidacji |
| 3. Testy diagnostyczne | uruchamiane są reguły FIN/CAP/HR/PORT/PROC itd. | ustrukturyzowane FINDINGS |
| 4. Sieć diagnostyczna | test wskazuje hipotezy i właściwe next_tests | ścieżka dalszego sprawdzenia |
| 5. Priorytet i pewność | wspólne mechanizmy PRI i CONF oceniają istotność oraz jakość podstawy | kolejność działania + poziom pewności |
| 6. Raport zarządczy | wynik jest tłumaczony na język decyzji | krótka lista najważniejszych wniosków i dalszych kroków |

### 3.2. Czego X-Ray na początku nie ma robić

3.2.1. Nie zastępuje zarządu  System ma zwiększać jakość informacji i kierować uwagę, nie podejmować samodzielnie decyzji organizacyjnych.

3.2.2. Nie udaje pewności  Jeżeli dane nie pozwalają na wiarygodny wniosek, wynik ma pozostać częściowy, zablokowany albo wymagający walidacji.

3.2.3. Nie obiecuje automatycznych oszczędności  Luka ekonomiczna lub koszt niewykorzystanej zdolności nie są tym samym co kwota możliwa do wycięcia z budżetu.

3.2.4. Nie zaczyna od AI  Najpierw mają działać deterministyczne obliczenia, walidacja i logika testów. AI dołączymy dopiero do stabilnego rdzenia.

## 4. Zasady konstrukcyjne całego systemu

| Zasada | Treść | Konsekwencja |
| --- | --- | --- |
| 01 | Najpierw dane, potem wniosek | Nie wnioskujemy przed walidacją. Brak danych nie jest zastępowany zgadywaniem. |
| 02 | Hipoteza nie jest przyczyną | Test może wskazać możliwy mechanizm, ale przyczyna wymaga dalszego dowodu. |
| 03 | Koszt nie oznacza oszczędności | Luki ekonomiczne wymagają dekompozycji i weryfikacji wykonalności. |
| 04 | Porównujemy tylko porównywalne | Jednostki, okresy, produkty, zasoby i efekty muszą mieć zgodną definicję. |
| 05 | Nie ustawiamy arbitralnych benchmarków | Pierwszeństwo ma historia organizacji, plan i porównywalne jednostki wewnętrzne. |
| 06 | Każdy wynik ma ślad | Źródło danych, sposób przeliczenia, korekta i ograniczenie muszą być odtwarzalne. |
| 07 | Testy tworzą sieć | Wynik jednego testu wskazuje, który kolejny test może zweryfikować hipotezę. |
| 08 | Technologia służy decyzji | Nie budujemy funkcji dlatego, że są efektowne; budujemy je, gdy poprawiają diagnozę lub powtarzalność. |

## 5. Architektura X-Ray

System rozwijamy warstwowo. Rozdzielenie jest celowe: liczba najpierw musi zostać prawidłowo policzona, dopiero potem można ją interpretować i prezentować.

| Warstwa | Rola | Stan obecny |
| --- | --- | --- |
| 1. DANE | import, mapowanie, walidacja, normalizacja i zapis | w realizacji w ZOP-TECH-01 |
| 2. SILNIK DIAGNOSTYCZNY | reguły testów, obliczenia, trendy, dekompozycja i FINDINGS | 3 testy zamrożone metodologicznie |
| 3. PRIORYTET I PEWNOŚĆ | wspólna ocena znaczenia oraz jakości podstawy dowodowej | ZOP-PRI-01 i ZOP-CONF-01 do opracowania |
| 4. INTERPRETACJA | opis wyników, hipotezy, pytania weryfikacyjne | projektowana po ustabilizowaniu rdzenia |
| 5. WSPARCIE DECYZJI | kolejność działań i ścieżki diagnostyczne | docelowa funkcja X-Ray |
| 6. PREZENTACJA | czytelny raport / panel dla zarządzającego | po walidacji silnika na firmie syntetycznej |

> **ZASADA TECHNOLOGICZNA Silnik obliczeniowy ma być deterministyczny i testowalny. AI może później pomagać tłumaczyć wynik, zadawać pytania i redagować komunikat, ale nie może wymyślać wartości, których nie wyliczył silnik.**

## 6. Wspólny model danych

Na obecnym etapie świadomie utrzymujemy model prosty. Pięć podstawowych tabel ma pozwolić opisać działalność, koszty, zasoby, proces i plan w większości organizacji usługowych oraz w wielu organizacjach produkcyjnych.

| Tabela | Znaczenie | Minimalne pola |
| --- | --- | --- |
| ACTIVITY | aktywność, produkt, wolumen i przychód | date, unit, product, volume, revenue |
| COST | koszty według jednostki i kategorii | date, unit, category, amount |
| RESOURCE | zasoby, dostępność, wykorzystanie i koszt | date, unit, resource, available, used, cost |
| PROCESS | przebieg przypadku przez etapy | case_id, stage, start, end, unit |
| PLAN | wartości docelowe i plan | date, unit, metric, target |

Karty testów mogą dodawać pola pomocnicze, ale nie powinny bez potrzeby rozbijać wspólnego modelu. Przykładowo CAP-01 wprowadził jawne available_source i effective_available, a HR-01 labor_input_basis i comparable_effect. Takie rozszerzenia mają precyzować znaczenie danych, nie tworzyć nowego silosu dla każdego testu.

## 7. Biblioteka Core 10

Core 10 jest pierwszym rdzeniem diagnostycznym X-Ray. Ma objąć pieniądze, zasoby, pracę, proces i portfel, a na końcu jakość informacji zarządczej. Statusy poniżej pokazują stan na 2 września 2026.

| Kod | Test | Status |
| --- | --- | --- |
| FIN-01 | Dynamika kosztów względem przychodów | ZAMROŻONY v1.0 |
| FIN-02 | Erozja rentowności | DO OPRACOWANIA |
| FIN-03 | Koszt jednostkowy | DO OPRACOWANIA |
| CAP-01 | Wykorzystanie zasobu | ZAMROŻONY v1.0 |
| CAP-02 | Przeciążenie zasobu | DO OPRACOWANIA |
| PROC-01 | Czas procesu | DO OPRACOWANIA |
| PROC-02 | Wąskie gardło | DO OPRACOWANIA |
| PORT-01 | Rentowność portfela | NASTĘPNY TEST |
| HR-01 | Koszt pracy względem efektu | ZAMROŻONY v1.0 |
| MGT-01 | Jakość informacji zarządczej | DO OPRACOWANIA |

## 8. Pierwszy trójkąt diagnostyczny już istnieje

FIN-01, CAP-01 i HR-01 tworzą pierwszy spójny zestaw, który zaczyna odróżniać zjawiska często wrzucane przez organizacje do jednego worka jako „za wysokie koszty”.

| Test | Pytanie | Co potrafi rozróżnić |
| --- | --- | --- |
| FIN-01 | Co dzieje się z relacją kosztów i przychodów? | czy ekonomika pogarsza się, gdzie powstaje luka i które kategorie odpowiadają za zmianę |
| CAP-01 | Co dzieje się z wykorzystaniem kupionej zdolności? | niewykorzystanie od przeciążenia, problemu popytu, planowej rezerwy lub błędu danych |
| HR-01 | Czy koszt pracy pozostaje w relacji do mierzalnego efektu? | wzrost ceny pracy od spadku produktywności i od niewykorzystania zdolności |

> **PRZYKŁAD LOGIKI Koszt pracy rośnie. FIN-01 pokazuje pogorszenie ekonomiki. HR-01 sprawdza, czy rośnie cena pracy, czy spada produktywność. CAP-01 sprawdza, czy kupiona zdolność jest wykorzystywana. Dopiero kombinacja wyników pozwala sensownie postawić hipotezę.**

### 8.1. Co to zmienia dla Olka

Implementacja nie polega na napisaniu trzech niezależnych skryptów. Każdy test powinien działać w tym samym szkielecie: wspólny import, walidacja, referencja, status wykonania, FINDINGS, validation_required i next_tests. Nowy test ma być modułem dołączanym do silnika, nie nową aplikacją.

### 8.2. Co to zmienia dla Michała

Kolejne doświadczenia zarządcze trzeba przekładać na reguły możliwe do zapisania, przetestowania i zakwestionowania. Wartość nie polega na tym, że „Michał wie z doświadczenia”, lecz na tym, że wiedza zostaje rozbita na warunki wejścia, obliczenia, granice interpretacji, hipotezy i scenariusze regresyjne.

## 9. Role i odpowiedzialność

> **MODEL WSPÓŁPRACY Michał odpowiada przede wszystkim za sens zarządczy i metodologię. Aleksander odpowiada przede wszystkim za architekturę technologiczną i implementację. Decyzje na styku obu światów podejmujemy wspólnie.**

| Obszar | Michał | Aleksander |
| --- | --- | --- |
| Problem klienta | definiuje pytanie zarządcze i wartość dla klienta | ocenia, jak przełożyć je na dane i funkcje systemu |
| Metodologia | projektuje testy, granice interpretacji, hipotezy i kryteria odbioru | sprawdza implementowalność, zgłasza niejednoznaczności i testuje przypadki brzegowe |
| Dane | definiuje znaczenie biznesowe i warunki porównywalności | projektuje mapowanie, walidację, kontrakt danych i obsługę błędów |
| Kod | nie narzuca szczegółowego stacku | odpowiada za architekturę, jakość kodu, testy automatyczne i dokumentację |
| Produkt | pilnuje, żeby wynik prowadził do decyzji | pilnuje, żeby produkt był powtarzalny, modułowy i możliwy do rozwijania |
| Odbiór | sprawdza poprawność merytoryczną | demonstruje działanie, testy i ograniczenia |
| Rozwój | buduje kolejne karty i logikę sieci testów | dokłada moduły do wspólnego silnika zamiast budować osobne rozwiązania |

### 9.1. Rola Aleksandra nie jest rolą wykonawcy

Olek ma mieć przestrzeń do podejmowania decyzji technicznych. ZOP-TECH-01 celowo zostawia mu wybór sposobu przechowywania danych, organizacji kodu, bibliotek i konstrukcji modułów. Oczekujemy nie tylko napisania kodu, ale również uzasadnienia architektury i sygnalizowania, gdy metodologia pozostawia niejednoznaczność implementacyjną.

### 9.2. Rola Michała nie jest rolą programisty

Michał nie powinien projektować technologii na poziomie bibliotek i klas. Jego zadaniem jest dostarczyć jednoznaczne znaczenie biznesowe, zdefiniować granice wniosku i pilnować, żeby system nie zamieniał korelacji w przyczynę ani wskaźnika w decyzję kadrową czy kosztową.

## 10. Co Olek robi teraz

Pierwszym aktywnym zadaniem technologicznym pozostaje ZOP-TECH-01. Jego rezultat ma stworzyć fundament, na który bez przebudowy będzie można nakładać FIN-01, CAP-01, HR-01 i kolejne karty.

| Produkt techniczny | Co ma powstać | Po co |
| --- | --- | --- |
| Architektura pilotażowa | prosty schemat komponentów i decyzji technologicznych | żeby dalszy kod miał strukturę |
| Model danych | pięć bazowych tabel oraz rozszerzenia bez łamania kontraktu | żeby testy pracowały na wspólnym języku danych |
| Import i mapowanie | XLSX/CSV do modelu wewnętrznego | żeby kolejny klient nie wymagał przepisywania całego kodu |
| Walidator | błędy krytyczne, ostrzeżenia, braki i duplikaty | żeby system nie liczył wiarygodnie wyglądających bzdur |
| FINDINGS | jedna wspólna struktura zapisu wyników | żeby wszystkie testy mogły być porównywane i orkiestrujące |
| Generator danych syntetycznych | fikcyjna firma 24M, 5 jednostek, ok. 100 zasobów | żeby testować system bez danych rzeczywistych |
| Testy + dokumentacja | powtarzalne uruchomienie i opis środowiska | żeby system można było rozwijać, a nie tylko „mieć na laptopie” |

### 10.1. Co następuje bezpośrednio po ZOP-TECH-01

10.1.1. Implementacja FIN-01  Pierwszy test ma zostać przełożony z karty metodologicznej na działający moduł i przejść swoje scenariusze regresyjne.

10.1.2. Implementacja CAP-01  Drugi moduł sprawdza, czy wspólny szkielet rzeczywiście obsługuje inną rodzinę danych i logikę capacity.

10.1.3. Implementacja HR-01  Trzeci moduł sprawdza, czy potrafimy połączyć koszt, nakład, efekt oraz sygnały z CAP-01 bez fałszywej atrybucji.

## 11. Plan rozwoju: od metodologii do pierwszego klienta

| Etap | Cel | Produkt / bramka | Status |
| --- | --- | --- | --- |
| ETAP 0 | Fundament technologiczny | ZOP-TECH-01 | w realizacji |
| ETAP 1 | Rdzeń metodologiczny Core 10 | FIN/CAP/HR + kolejne testy | 3/10 zamrożone |
| ETAP 2 | Implementacja testów | moduły działające w jednym silniku | po odbiorze TECH-01 |
| ETAP 3 | Wspólne mechanizmy | ZOP-PRI-01, ZOP-CONF-01, reguły next_tests | do opracowania |
| ETAP 4 | Firma syntetyczna z problemami | kontrolowany zestaw danych z zaszytymi odchyleniami | kamień milowy M1 |
| ETAP 5 | Automatyczny raport X-Ray | FINDINGS → krótka synteza zarządcza | po przejściu M1 |
| ETAP 6 | Pilotaż na realnej organizacji | dane kontraktowe, nie SPZOZ, bez danych wrażliwych | po walidacji syntetycznej |
| ETAP 7 | Pierwszy płacący klient | X-Ray jako usługa wsparta własnym silnikiem | cel biznesowy |
| ETAP 8 | Powtarzalność i produkt | standaryzacja wejścia, raportu, procesu i czasu realizacji | po kilku realizacjach |
| ETAP 9 | CONTROL / inteligencja ciągła | monitoring i późniejsza warstwa AI | dopiero po potwierdzeniu rynku |

### 11.1. Najważniejszy pierwszy kamień milowy – M1

> **M1 X-Ray analizuje sztuczną organizację i poprawnie wykrywa celowo zaszyte problemy, zapisując wyniki do wspólnej struktury FINDINGS. System musi również poprawnie nie alarmować tam, gdzie odchylenie jest pozorne albo dane nie są porównywalne.**

M1 jest ważniejszy niż wygląd aplikacji. Jeżeli silnik nie przechodzi tego egzaminu, nie ma sensu projektować efektownego panelu, integracji ani warstwy AI.

## 12. Jak ma wyglądać pierwsza wersja sprzedażowa X-Ray

Pierwsza sprzedażowa wersja X-Ray nie musi być jeszcze samoobsługowym systemem. Wystarczy, że proces jest powtarzalny, wynik wiarygodny, a przygotowanie kolejnej analizy wymaga znacznie mniej pracy ręcznej niż klasyczny projekt konsultingowy.

| Element | Wersja pierwsza | Kierunek docelowy |
| --- | --- | --- |
| Dostarczenie danych | ustalony pakiet XLSX/CSV | mapowanie wielu źródeł i integracje |
| Walidacja | automatyczna + kontrola człowieka | automatyczna kontrola jakości i alerty |
| Testy | Core 10 i ścieżki next_tests | szersza biblioteka branżowa |
| Priorytet | wspólny ZOP-PRI-01 | dynamiczny ranking problemów |
| Pewność | wspólny ZOP-CONF-01 | ciągła ocena jakości dowodu |
| Raport | zwięzły dokument zarządczy | panel + raport + rozmowa z systemem |
| Interpretacja | Michał + reguły systemu | warstwa AI oparta na deterministycznych wynikach |
| Sprzedaż | usługa diagnostyczna | produkt abonamentowy / SaaS |

### 12.1. Co musi otrzymać zarządzający

12.1.1. Najważniejsze problemy  Nie lista wszystkiego, co system policzył, lecz ograniczona liczba zjawisk wymagających uwagi.

12.1.2. Dowód  Każdy wniosek musi mieć wartość, referencję, okres, zakres i możliwość odtworzenia.

12.1.3. Skalę  W miarę możliwości fizyczną i ekonomiczną, ale bez fałszywego utożsamiania luki z oszczędnością.

12.1.4. Pewność  Zarządzający powinien wiedzieć, czy widzi mocny wniosek, umiarkowany sygnał czy hipotezę wymagającą danych.

12.1.5. Następny krok  Wynik ma mówić, co warto sprawdzić dalej i które testy mogą rozstrzygnąć hipotezę.

## 13. Kierunek biznesowy

Na początku świadomie nie budujemy firmy opartej na sprzedaży samego oprogramowania. Najpierw musimy udowodnić, że metodologia rozwiązuje rzeczywisty problem i że klienci chcą płacić za wynik diagnostyczny.

> **KIERUNEK Usługa → powtarzalny produkt → stały system zarządzania → dopiero później pełna warstwa SaaS/AI.**

| Poziom | Co sprzedajemy | Rola technologii | Status |
| --- | --- | --- | --- |
| X-RAY | jednorazową lub okresową diagnozę organizacji | automatyzuje dane, testy i raportowanie | pierwszy produkt |
| CONTROL | ciągły monitoring wskaźników, odchyleń i działań | utrzymuje historię i alerty | kierunek po walidacji X-Ray |
| INTELLIGENCE / AI | rozmowę z warstwą decyzyjną organizacji | interpretuje stabilne wyniki i pomaga eksplorować przyczyny | dalszy etap |

Robocza hipoteza komercyjna zakłada, że pierwszy klient powinien zapłacić za realną diagnozę, nie za „pilotaż technologiczny”. Cena, dokładny czas realizacji i segment pierwszych klientów pozostają do walidacji rynkowej po przejściu M1.

## 14. Granice bezpieczeństwa i danych

14.1. Brak danych SPZOZ  Projekt Zoptymalizowani rozwijamy bez wykorzystywania danych SPZOZ jako materiału testowego lub przewagi komercyjnej.

14.2. Brak danych pacjentów  Na etapie budowy nie wykorzystujemy danych pacjentów ani danych wrażliwych. Do testów służą dane syntetyczne i techniczne.

14.3. Minimalizacja danych  X-Ray powinien potrzebować danych o działalności, kosztach, zasobach i procesie tylko w takim zakresie, w jakim są konieczne do diagnozy.

14.4. Ślad obliczeń  Każda korekta, mapowanie i transformacja powinny być możliwe do prześledzenia.

14.5. Człowiek pozostaje odpowiedzialny  System może rekomendować test i kolejny krok, ale decyzje kadrowe, inwestycyjne i organizacyjne wymagają oceny zarządzającego.

## 15. Co pozostaje otwarte

| Element | Temat | Po co | Status |
| --- | --- | --- | --- |
| ZOP-PRI-01 | wspólny mechanizm priorytetu | ma przeliczać istotność FINDINGS na spójny status / kolejność działania | DO OPRACOWANIA |
| ZOP-CONF-01 | wspólny mechanizm pewności | ma oceniać jakość danych, referencji, porównywalności i ograniczeń | DO OPRACOWANIA |
| Orkiestracja | reguły next_tests | kiedy test tylko rekomenduje, a kiedy system uruchamia kolejny moduł | DO OPRACOWANIA |
| Porównywalny efekt | standard wag i wersjonowania weighted_volume | wspólny kontrakt dla HR/PORT/PROC | DO UJEDNOLICENIA |
| Podstawa kosztowa | jednolity sposób opisu zakresu kosztu | ważne dla FIN, CAP i HR | DO UJEDNOLICENIA |
| Warstwa raportowa | standard komunikatu zarządczego | jedna architektura raportu dla wszystkich testów | PO M1 |
| Segment klienta | pierwszy rynek i profil organizacji | hipoteza organizacji usługowych pozostaje do walidacji | ROBOCZE |

## 16. Najbliższa kolejność prac

16.1. Olek kończy ZOP-TECH-01  Nie czekamy z technologią na pełne Core 10. Fundament danych, walidacji i FINDINGS jest potrzebny już teraz.

16.2. Michał buduje PORT-01  Po zamrożeniu pierwszego trójkąta przechodzimy do rentowności portfela, bo portfel będzie jednym z kluczowych wyjaśnień zmian w FIN, CAP i HR.

16.3. Po odbiorze TECH-01 zaczyna się implementacja FIN-01  Pierwszy test wdrożeniowy ma sprawdzić, czy karta metodologiczna jest wystarczająco jednoznaczna dla kodu.

16.4. Kolejno implementujemy CAP-01 i HR-01  To da pierwszy działający zestaw testów wzajemnie się uzupełniających.

16.5. Rozwijamy pozostałe Core 10  PORT, FIN-02/03, CAP-02, PROC-01/02, MGT-01.

16.6. Projektujemy PRI i CONF  Dopiero gdy mamy kilka rzeczywistych testów, budujemy wspólny scoring na podstawie ich prawdziwych potrzeb.

16.7. Budujemy Synthetic Company v1.0 z zaszytymi problemami  To jest pierwszy pełny egzamin X-Ray i bramka przed pilotażem z klientem.

## 17. Jak pracujemy z dokumentacją

Dokumentacja nie jest celem samym w sobie. Jest sposobem na zamianę doświadczenia i decyzji w powtarzalną specyfikację, którą można wdrożyć, przetestować i poprawić bez utraty sensu biznesowego.

| Typ dokumentu | Rola | Zasada |
| --- | --- | --- |
| ZOP-MASTER-01 | kierunek projektu, role, plan, status i decyzje przekrojowe | aktualizowany po kamieniach milowych |
| ZOP-TECH-XX | zadania i standardy technologiczne | nie zmienia metodologii testów |
| ZOP-XR-XX-XX | karty metodologiczne testów | po zamrożeniu nie zmieniamy bez realnego błędu ujawnionego w implementacji |
| ZOP-PRI-01 / ZOP-CONF-01 | wspólne mechanizmy całego silnika | projektowane raz dla wszystkich testów |
| Pakiety korekcyjne | kontrolowana zmiana jednej karty | bez ponownego otwierania całego projektu |

### 17.1. Hierarchia dokumentów

> **HIERARCHIA Master prowadzi kierunek projektu, ale nie nadpisuje zamrożonej matematyki kart testów. Karta testu prowadzi implementację danego testu. Zadanie techniczne prowadzi architekturę i kod, ale nie zmienia znaczenia biznesowego testu.**

## 18. Kiedy uznamy, że pierwszy produkt naprawdę istnieje

Nie wtedy, gdy mamy stronę internetową. Nie wtedy, gdy mamy logo. Nie wtedy, gdy potrafimy pokazać kilka wykresów.

> **DEFINITION OF PRODUCT Pierwszy X-Ray istnieje wtedy, gdy nieznany wcześniej zestaw danych może przejść przez walidację, wspólny model i zestaw testów, a system wykrywa zaszyte problemy, nie generuje fałszywych alarmów w scenariuszach ochronnych i tworzy FINDINGS wystarczające do przygotowania krótkiego raportu zarządczego.**

Dopiero po spełnieniu tej definicji zaczynamy traktować stronę, panel, integracje i AI jako elementy zwiększające skalę produktu, a nie substytut jego logiki.

## 19. Jedna strona dla Olka: po co to robimy

> **OLKU Nie budujesz programu do liczenia wskaźników. Budujesz silnik, który ma nauczyć się powtarzalnego sposobu patrzenia na organizację.**

Na wejściu klient ma nieuporządkowane dane. Twoim pierwszym zadaniem jest sprawić, żeby system wiedział, czy tym danym można zaufać i jak je zapisać w jednym modelu. Następnie dokładamy testy. Każdy test ma precyzyjnie policzyć zjawisko, wskazać ograniczenia, zapisać FINDING i powiedzieć, co warto sprawdzić dalej.

Nie oczekuję, że będziesz programował moje pomysły linijka po linijce. Chcę, żebyś współtworzył architekturę: widział niejednoznaczności, proponował prostsze rozwiązania, pisał testy i pilnował, żeby kolejny moduł nie wymagał przebudowy całego systemu.

Jeżeli metodologiczna karta jest niejednoznaczna, nie zgaduj. Zgłoś to. Jeżeli da się zrobić prostszą architekturę niż zaproponowaliśmy, pokaż ją i uzasadnij. Jeżeli test przechodzi na pięknych danych, ale rozpada się na błędach, to nie jest gotowy.

Najważniejszy pierwszy cel nie brzmi „zrobić aplikację”. Brzmi: stworzyć system, który na fikcyjnej firmie sam wykryje problemy, które celowo zaszyjemy, i jednocześnie nie oskarży organizacji o problem tam, gdzie danych albo podstawy porównania nie ma.

> **TWOJA ROLA Architekt technologii i przyszłego produktu. Kod jest narzędziem. Celem jest wiarygodna, powtarzalna diagnoza.**

## 20. Stan projektu na dzień 2 września 2026

| Element | Status |
| --- | --- |
| ZOP-MASTER-01 | v1.0 – aktywny dokument przewodni |
| ZOP-TECH-01 | zadanie przekazane Aleksandrowi – fundament technologiczny w realizacji |
| FIN-01 | v1.0 – zamrożony, gotowy do implementacji |
| CAP-01 | v1.0 – zamrożony, gotowy do implementacji |
| HR-01 | v1.0 – zamrożony, gotowy do implementacji |
| PORT-01 | następny test metodologiczny |
| ZOP-PRI-01 | do opracowania po zbudowaniu większej części rdzenia |
| ZOP-CONF-01 | do opracowania po zbudowaniu większej części rdzenia |
| Synthetic Company v1.0 | po implementacji pierwszego zestawu testów |
| Pierwszy klient | po przejściu bramki M1 i przygotowaniu powtarzalnego raportu X-Ray |

> **NAJBLIŻSZY KROK Olek kończy fundament technologiczny. My przechodzimy do PORT-01. Po odbiorze ZOP-TECH-01 zaczyna się implementacja zamrożonych kart FIN-01 → CAP-01 → HR-01.**
