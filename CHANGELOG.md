# Changelog (Historia zmian)

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