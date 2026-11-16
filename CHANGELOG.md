# Changelog (Historia zmian)

## [2.0.2.0]

### Zmieniono
- Instalator odczytuje numer wersji bezpośrednio z pliku `wersja.txt` (wcześniej z gotowego `mkEdytor.exe`). Numer wersji ustawia się w dwóch miejscach: w `wersja.txt` i w stałej `WERSJA` w `mkEdytor.py`. Jeśli numeru nie da się odczytać, kompilacja instalatora zatrzymuje się z komunikatem błędu.

### Poprawiono
- Okno wyboru koloru otwierało się z zaznaczonym kolorem białym – kliknięcie „OK” bez wyboru sprawiało, że dalszy tekst był niewidoczny na białym tle. Teraz okno startuje z bieżącym kolorem tekstu, ma polski tytuł „Wybierz kolor tekstu” i jest powiązane z oknem programu.

## [2.0.1.1]

### Zmieniono
- Nowy, niezapisany dokument nazywa się teraz „Bez nazwy” – w tytule okna (zamiast „Nowy dokument”) oraz jako proponowana nazwa pliku przy zapisie i eksporcie (zamiast „dokument”), np. `Bez nazwy.mked`.

## [2.0.1.0]

### Dodano
- **Sprawdzanie skojarzenia przy starcie:** jeśli pliki `.mked` nie otwierają się w mkEdytorze (np. wcześniej wybrano inny program w oknie „Otwórz za pomocą”), program proponuje naprawę: *Tak* / *Nie teraz* / *Nie pytaj więcej*. Skojarzenie zapisywane jest dla bieżącego użytkownika i nie wymaga uprawnień administratora. To samo można zrobić ręcznie: *Plik → Otwieraj pliki .mked w mkEdytorze*.
- Instalator rejestruje mkEdytor na liście „Otwórz za pomocą” oraz w Ustawieniach Windows → *Aplikacje domyślne*, usuwa wcześniejszy wybór innego programu dla `.mked`, a deinstalator sprząta skojarzenie zapisane przez program.

### Zmieniono
- Sprzątanie skojarzeń z `.txt` i `.html` po wersjach 1.x przeniesiono do sekcji `[Code]` instalatora – w sekcji `[Registry]` pozostały wyłącznie wpisy dla `.mked`.
- Ikona plików `.mked` jest pobierana bezpośrednio z `mkEdytor.exe`.

### Poprawiono
- Pliki `.mked` nie otwierały się w mkEdytorze, jeśli wcześniej wybrano dla nich inny program („Otwórz za pomocą → Zawsze”).

## [2.0.0.0]

> **Wersja przełomowa:** dokumenty są zapisywane w nowym, własnym formacie `.mked`. Pliki z wersji 1.x (`.html`, `.txt`) można zaimportować.

### Dodano
- **Własny format dokumentów `.mked`:** plik tekstowy UTF-8 w formacie JSON, zawierający treść z pełnym formatowaniem oraz numer wersji formatu (przygotowanie pod przyszłe rozszerzenia).
- **Eksport do HTML:** nowe polecenie *Plik → Wyeksportuj do HTML (strona internetowa)*. Eksport nie zmienia otwartego dokumentu.
- **Import starszych plików:** pliki `.html`, `.htm` i `.txt` otwierają się jako import (w tytule okna „(zaimportowany)”). Oryginał nie jest nadpisywany – *Zapisz* proponuje zapis jako nowy dokument `.mked` o tej samej nazwie.
- **Otwieranie dwuklikiem:** program odczytuje ścieżkę pliku przekazaną przez system, a instalator rejestruje mkEdytor jako domyślny program dla plików `.mked` (z ikoną programu).
- Czytelne komunikaty przy próbie otwarcia uszkodzonego pliku lub dokumentu utworzonego w nowszej wersji programu.

### Zmieniono
- Usunięto możliwość zapisu do `.txt` i `.html` – *Zapisz* / *Zapisz jako* zapisują wyłącznie `.mked` (eliminuje to ciche gubienie formatowania przy zapisie do zwykłego tekstu).
- Instalator usuwa skojarzenia z plikami `.txt` i `.html` pozostawione przez wersje 1.x.
- Tytuł okna pokazuje samą nazwę pliku zamiast pełnej ścieżki.
- Okna zapisu i eksportu proponują nazwę pliku na podstawie bieżącego dokumentu i automatycznie dopisują brakujące rozszerzenie (`.mked`, `.odt`, `.html`, `.pdf`).
- Numer wersji w instalatorze jest odczytywany automatycznie z pliku `mkEdytor.exe`.

### Poprawiono
- Program pokazywał w tytule okna nieaktualny numer wersji (1.0.2.0 zamiast 1.0.2.1).
- Dwuklik na skojarzonym pliku otwierał pusty edytor zamiast wskazanego dokumentu.
- Po nieudanym zapisie nie pozostaje już plik tymczasowy `.tmp`.
- Po nieudanym *Zapisz jako* program nie przypisuje już dokumentu do pliku, który nie został zapisany.
- Eksport do ODT nie działał, gdy nazwa pliku nie miała rozszerzenia.
- Instalator: usunięto podwójne kopiowanie `mkEdytor.exe` i zbędną flagę zadania „Ikona na pulpicie”.

## [1.0.2.1]

### Zmieniono
- Zmieniono ikonę na bardziej nowoczesną.

## [1.0.2.0]

### Zmieniono
- Podbito wersję aplikacji do **1.0.2.0**, oznaczając stabilizację kodu po usunięciu krytycznych błędów związanych z formatowaniem tekstu oraz obsługą operacji na plikach.

## [1.0.1.11]

### Poprawiono
- **Krytyczny błąd formatowania:** Usunięto błąd polegający na "spłaszczaniu" (nadpisywaniu) formatowania przy zmianie czcionki, rozmiaru lub koloru zaznaczonego tekstu. Wcześniej zmiana np. koloru w bloku zawierającym pogrubienie i pochylenie kopiowała styl pierwszego znaku na całe zaznaczenie. Teraz modyfikowana jest wyłącznie wybrana właściwość (dzięki `QTextCharFormat` i `mergeCurrentCharFormat`).
- Usunięto błąd nadpisywania globalnej domyślnej czcionki dokumentu przy modyfikacji formatu zaczynającego się od pozycji zerowej kursora.

## [1.0.1.10]

### Zmieniono
- Całkowicie uniezależniono aplikację od zewnętrznych bibliotek (usunięto `chardet`), co rozwiązuje problemy z importem i analizą statyczną (np. w VS Code) oraz ułatwia kompilację do pliku `.exe`.
### Dodano
- Własny, wbudowany mechanizm wykrywania kodowania plików przy otwieraniu. Obsługa najpopularniejszych standardów: `utf-8-sig`, `utf-8`, `windows-1250`, `iso-8859-2`, `cp1252`.
- Dodano okna dialogowe informujące użytkownika o wczytaniu pliku w formacie innym niż UTF-8 oraz o ewentualnym zastąpieniu nierozpoznanych znaków na znak `?` w przypadku całkowitej awarii dekodowania.

## [1.0.1.x] - *(Aktualizacje z przedziału 1.0.1.5 - 1.0.1.9)*

### Dodano
- **Bezpieczny zapis (Safe Save):** Zapisywanie plików odbywa się teraz z wykorzystaniem pliku tymczasowego (`.tmp`). Chroni to dane użytkownika przed uszkodzeniem w przypadku nagłej awarii (np. braku prądu) w momencie zapisu.
- Pełne spolszczenie własnych okien dialogowych (wymuszono polskie przyciski "Zapisz", "Nie zapisuj", "Anuluj" w QMessageBox niezależnie od języka systemu operacyjnego).
- Dodano dynamiczne oznaczanie pliku jako zmodyfikowany (pojawienie się `*` w tytule okna) od razu po wprowadzeniu jakiejkolwiek zmiany (śledzenie poprzez sygnał `textChanged`).
### Poprawiono
- Dopracowano obsługę zdarzenia zamknięcia okna (`closeEvent`), aby aplikacja prawidłowo wstrzymywała zamknięcie, jeśli proces zapisu zostanie anulowany lub wystąpi błąd.

## [1.0.1.3]

### Dodano
* **Drukowanie:** Nowa opcja "Drukuj" (Ctrl+P) w menu `Plik`, pozwalająca na bezpośrednie drukowanie dokumentów z zachowaniem ich pełnego formatowania.
* **Ponawianie akcji:** Dodano opcję "Ponów" (Ctrl+Y) w menu `Edytuj`, uzupełniającą system cofania zmian.
* **Rozbudowane menu "Odwiedź":** Zamiast pojedynczego przycisku, menu teraz rozwija się, oferując szybki dostęp do przydatnych linków:
  * *Pobierz najnowszą wersję* (przekierowanie do wydań na GitHubie).
  * *Zgłoś błąd* (przekierowanie do zakładki Issues na GitHubie).
  * *Zrelaksuj się* (przekierowanie na kanał StaryDooh na YouTube).

## [1.0.1.2]

### Naprawiono
* **Znikający tekst:** Usunięto krytyczny błąd polegający na znikaniu pierwszej linii tekstu podczas próby zmiany jej formatowania (czcionki, rozmiaru lub koloru).
* **Konflikty formatowania:** Zoptymalizowano mechanizm nakładania stylów. Zmiany formatu są teraz zamykane w pojedynczych blokach edycyjnych (`QTextCursor.beginEditBlock()`), co stabilizuje renderowanie tekstu i zapobiega konfliktom między stylem akapitu a stylem pojedynczych znaków.
* **Punkty i listy:** Poprawiono logikę skalowania punktorów w listach. Znaki wypunktowania bezbłędnie dziedziczą teraz rozmiar i kolor czcionki tekstu głównego.

## [1.0.1.1]

### Dodano (Pierwsze stabilne wydanie)
* **Interfejs użytkownika:** Intuicyjny, graficzny interfejs (GUI) stworzony w bibliotece PyQt6, dostosowany do potrzeb edukacyjnych (duże ikony, czytelny układ).
* **Formatowanie tekstu:** * Zmiana kroju pisma (odczyt czcionek systemowych).
  * Zmiana rozmiaru tekstu (od 8 do 72 pkt).
  * Paleta kolorów (zmiana koloru tekstu).
  * Style: **Pogrubienie**, *Pochylenie*, U̲nderline (Podkreślenie).
* **Akapity i listy:**
  * Wyrównywanie: do lewej, do środka, do prawej, justowanie.
  * Inteligentne wstawianie list punktowanych i numerowanych.
* **Zarządzanie plikami:**
  * Tworzenie, otwieranie i zapisywanie plików ze wsparciem dla formatów `.txt` (zwykły tekst) oraz `.html` (tekst sformatowany).
  * Eksport dokumentów do standardu `.odt` (LibreOffice / OpenOffice).
  * Generowanie plików `.pdf` do bezpośredniego wydruku lub wysyłki.
* **Optymalizacje:** Utrzymywanie ustalonego formatowania nawet po wyczyszczeniu okna edytora.