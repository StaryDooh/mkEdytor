# mkEdytor – problemy do rozwiązania

Wynik przeglądu wersji 1.0.2.1 (`mkEdytor.py`, `Budowanie_EXE.bat`, `Budowanie_instalatora.iss`, `wersja.txt`, `Licencja.txt`).
Przegląd: 2026-11-11.

> **Stan w wersji 2.0.0.0:** dokumenty zapisywane są wyłącznie w formacie `.mked` (JSON z treścią HTML Qt),
> zapis do .txt i .html usunięty, dodany eksport do HTML, starsze pliki .html/.txt można zaimportować
> (oryginał nie jest nadpisywany). mkEdytor jest domyślnym programem dla `.mked`; skojarzenia z .txt/.html
> z wersji 1.x są usuwane przez instalator. Wersję w instalatorze odczytuje się z `mkEdytor.exe`.
> W pkt 10 dodano już automatyczne dopisywanie rozszerzenia przy eksporcie (ODT działa bez rozszerzenia);
> sprawdzanie sukcesu eksportu PDF rozwiązane w wersji 2.0.5.0.
>
> **Stan w wersji 2.0.2.0:** wszystkie błędy poważne (pkt 1–5) są rozwiązane.

Legenda: 🔴 poważne · 🟠 błędy logiczne / usterki · 🟡 interfejs dla klas 1–3 · 🔵 nadmiarowy kod · ⚙️ budowanie i instalator · ⚖️ licencja

---

## 🔴 Błędy poważne

### [x] 1. Skojarzenia plików nie działają – program ignoruje `sys.argv`
Instalator rejestruje polecenie `"mkEdytor.exe" "%1"` dla plików .txt i .html, ale `__main__` w ogóle nie czyta argumentów. Dwuklik na pliku otwiera **pusty** edytor.

**Poprawka:** wydzielić z `otworz_plik` metodę `wczytaj_plik(sciezka)` i dopisać:
```python
okno = NowoczesnyEdytor()
if len(sys.argv) > 1 and os.path.isfile(sys.argv[1]):
    okno.wczytaj_plik(sys.argv[1])
okno.showMaximized()
```

### [x] 2. Okno wyboru koloru startuje z kolorem białym (linia 337)
`QColorDialog.getColor()` bez argumentów ma domyślnie kolor `Qt.white`. Dziecko kliknie „OK” bez wyboru i dalej pisze niewidocznym białym tekstem na białym tle. Okno nie ma też rodzica.

**Poprawka:**
```python
kolor = QColorDialog.getColor(self.edytor.textColor(), self, "Wybierz kolor tekstu")
```

### [x] 3. Formatowanie znika bez ostrzeżenia przy zapisie do .txt
Scenariusz: dziecko otwiera `notatka.txt` dwuklikiem, pogrubia, koloruje, wciska Ctrl+S. Plik zapisuje się jako czysty tekst, gwiazdka w tytule znika, a po ponownym otwarciu formatowania nie ma. To samo przy wybraniu filtra „Zwykły tekst” w „Zapisz jako”.

**Poprawka:** przy zapisie do .txt sprawdzać, czy dokument ma formatowanie, i wtedy proponować zapis jako .html.

### [x] 4. Otwarcie i zapis „prawdziwego” pliku HTML go niszczy
Program rejestruje się dla wszystkich plików `.html`. `QTextEdit` obsługuje tylko podzbiór HTML: wyrzuca skrypty, CSS, `<div>`, formularze i przepisuje całą strukturę. Strona zrobiona przez ucznia na innych zajęciach zostanie po zapisie nieodwracalnie przerobiona.

**Poprawka:** zrezygnować ze skojarzenia `.html` albo ostrzegać przy zapisie pliku, który nie powstał w mkEdytorze (np. brak `<meta name="qrichtext">` w źródle).

### [x] 5. Niezgodna wersja
W kodzie `WERSJA = "1.0.2.0"`, w `wersja.txt` i `.iss` – `1.0.2.1`. Tytuł okna pokazuje złą wersję.

**Poprawka:** trzymać numer w jednym miejscu (np. `wersja.py`), z którego czyta program, a pozostałe pliki generować skryptem.

**Rozwiązanie (2.0.2.0):** numer wersji jest w `mkEdytor.py` (stała `WERSJA`) i w `wersja.txt`; instalator odczytuje go z `wersja.txt`. Rozwiązanie przyjęte jako docelowe.

---

## 🟠 Błędy logiczne i drobniejsze usterki

### [x] 6. Skrót „Zapisz jako” nie działa na Windows
`QKeySequence.StandardKey.SaveAs` jest na Windows **puste** (Ctrl+Shift+S istnieje tylko w KDE/GNOME/macOS).

**Poprawka:** `akcja_zapisz_jako.setShortcut(QKeySequence("Ctrl+Shift+S"))`

### [x] 7. Część listy kodowań to martwy kod (linie 421–454)
- `utf-8` po `utf-8-sig` jest zbędne – `utf-8-sig` czyta też UTF-8 bez BOM.
- `iso-8859-2` przypisuje znak **każdemu** bajtowi, więc dekodowanie nigdy się nie wywali. `cp1252` i awaryjny blok `errors="replace"` nigdy się nie wykonają.
- Skutek uboczny: plik binarny (.docx, .exe przez „Wszystkie pliki”) otworzy się jako sieczka znaków z komunikatem o „pomyślnym wczytaniu”.

**Poprawka:** lista `["utf-8-sig", "windows-1250"]` + fallback; odrzucać pliki zawierające bajty `\x00` oraz bardzo duże pliki (zamrożą program).

### [x] 8. Pozostaje plik `.tmp` po nieudanym zapisie
Jeśli `os.replace` się nie powiedzie (plik tylko do odczytu, zablokowany – częste na szkolnych dyskach sieciowych), `praca.html.tmp` zostaje w katalogu.

**Poprawka:** w `except` próbować `os.remove(tmp)`.

### [x] 9. `zapisz_jako` zmienia ścieżkę przed zapisem
`self.aktualny_plik = sciezka` jest ustawiane przed `zapisz_na_dysk`. Po nieudanym zapisie program „myśli”, że dokument należy do nieistniejącego pliku.

**Poprawka:** ustawiać ścieżkę dopiero po sukcesie; `zapisz_plik` i `zapisz_jako` powinny zwracać `bool`.

### [x] 10. Eksport PDF zawsze pokazuje „Sukces”
`QPdfWriter` nie rzuca wyjątków, więc `try/except` niczego nie łapie. Gdy PDF jest otwarty w przeglądarce PDF, zapis się nie uda, a komunikat i tak pokaże sukces.

**Poprawka:**
- po eksporcie sprawdzać, czy plik istnieje i ma niezerowy rozmiar,
- w ODT ustawić format jawnie: `writer.setFormat(b"odf")`,
- w obu eksportach dopisywać brakujące rozszerzenie.

### [x] 11. „Nowy” nie zeruje formatowania
`clear()` + `utrzymaj_formatowanie()` przywraca tylko krój i rozmiar. Kolor, pogrubienie i wyrównanie przechodzą z poprzedniego dokumentu.

**Poprawka:** `self.edytor.setCurrentCharFormat(QTextCharFormat())` + wyrównanie do lewej.

### [x] 12. Flaga zmian nie uwzględnia cofania
Po wpisaniu czegoś i cofnięciu Ctrl+Z do stanu pierwotnego program dalej pyta o zapis.

**Poprawka:** użyć wbudowanego mechanizmu Qt – `document().isModified()`, `setModified(False)`, sygnał `modificationChanged` → `setWindowModified` (znacznik `[*]` w tytule). Można wtedy usunąć własną flagę `zmodyfikowany` i `_oznacz_jako_zmodyfikowany`.

### [x] 13. Tytuł pokazuje pełną ścieżkę
Np. `C:\Users\uczen12\OneDrive\Pulpit\...`.

**Poprawka:** `os.path.basename(self.aktualny_plik)`.

---

## 🟡 Interfejs a wiek 6–9 lat

### [x] 14. Okna Qt są po angielsku
Menu kontekstowe edytora: „Undo / Redo / Cut / Copy / Paste / Select All”. Okno kolorów: „Basic colors”, „Custom colors”. Własny `_zapytaj_o_zapis` obchodzi problem tylko w jednym miejscu.

**Poprawka (globalnie):**
```python
from PyQt6.QtCore import QTranslator, QLibraryInfo, QLocale
tlumacz = QTranslator()
if tlumacz.load(QLocale(QLocale.Language.Polish), "qtbase", "_",
                QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)):
    app.installTranslator(tlumacz)
```
Po zbudowaniu sprawdzić, czy w `_internal\PyQt6\Qt6\translations` jest `qtbase_pl.qm`. Wtedy wystarczy zwykły `QMessageBox.question`.

### [x] 15. Brak skrótów Ctrl+B / Ctrl+I / Ctrl+U
`QTextEdit` sam ich nie obsługuje. W programie do nauki edytora to spory brak – dzieci spotkają te skróty w Wordzie i Writerze. Dopisać skróty także w podpowiedziach przycisków.

### [ ] 16. Ikony z Unicode mogą się nie wyświetlić
`𝐁` (U+1D401) i `𝐼` (U+1D43C) to znaki matematyczne spoza podstawowego zakresu; emoji ✂️📄📋🎨 zależą od czcionki Segoe UI Emoji. Na starszych komputerach może być „kwadracik”. Zastąpić ikonami PNG (jak wyrównanie i listy). 📄 jako „Kopiuj” jest mylące.

### [ ] 17. Lista czcionek ma kilkaset pozycji
`QFontDatabase.families()` zwraca też Wingdings, Webdings, Symbol – tekst zamienia się w obrazki i dziecko nie wie, co się stało.

**Poprawka:** krótka, ręcznie wybrana lista (Arial, Comic Sans MS, Times New Roman, Verdana…) albo `QFontComboBox` z podglądem.

### [ ] 18. Menu „Zrelaksuj się” otwiera YouTube
Jedno kliknięcie wyprowadza dziecko z lekcji na YouTube (polecane filmy, reklamy, komentarze). W wielu szkołach YouTube jest blokowany lub wymaga nadzoru. „Zgłoś błąd” wymaga konta GitHub, którego dzieci nie mają.

**Poprawka:** ukryć menu „Odwiedź” przełącznikiem w pliku konfiguracyjnym albo zastąpić oknem „O programie”. Takie okno i tak jest potrzebne – licencja zabrania usuwania informacji o prawach autorskich, a program nigdzie ich nie pokazuje.

### [ ] 19. Brak autozapisu
Komputery w pracowni bywają wyłączane z listwy na koniec lekcji.

**Poprawka:** `QTimer` co minutę zapisuje kopię do `%LOCALAPPDATA%\mkEdytor\autozapis.html`; przy starcie propozycja odzyskania.

### [ ] 20. Drobiazgi
- [ ] Spinbox po każdej zmianie oddaje fokus edytorowi – strzałką klawiatury zmiana tylko o 1.
- [ ] Rozmiar > 72 pt z wklejonego tekstu pokazywany jako 72.
- [ ] Brak „Zakończ” w menu Plik i „Zaznacz wszystko” w Edytuj.
- [ ] Filtr otwierania nie obejmuje `*.htm`, choć kod go obsługuje.
- [ ] Wklejanie z przeglądarki przenosi cały „śmietnik” formatowania – można uprościć, nadpisując `insertFromMimeData`.

---

## 🔵 Nadmiarowy kod i jakość

- [x] Blok „zapytaj → zapisz → sprawdź” powtórzony 3 razy (`closeEvent`, `nowy_plik`, `otworz_plik`) – wydzielić do `_czy_mozna_porzucic() -> bool`.
- [ ] `wstaw_liste_punktowana` i `wstaw_liste_numerowana` są identyczne poza stylem – jedna metoda `_przelacz_liste(styl)`; do zdejmowania listy standardowe `lista.remove(blok)` zamiast `setObjectIndex(-1)`.
- [ ] Cofnij/ponów/wytnij/kopiuj/wklej mają osobne `QAction` w menu i na pasku – jedna akcja w obu miejscach (od razu ze skrótem i podpowiedzią); wyłączać je sygnałami `undoAvailable` / `copyAvailable`.
- [ ] `self.resize(1000, 700)` nic nie daje przy `showMaximized()`.
- [ ] `except Exception` w `sciezka_zasobu` → `except AttributeError`.

---

## ⚙️ Budowanie i instalator

- [x] **`.iss`, linie 48 i 51:** `mkEdytor.exe` kopiowany dwa razy (wzorzec `dist\mkEdytor\*` już go obejmuje) – usunąć linię 48.
- [x] **`Flags: checkablealone`** dotyczy zadań z podzadaniami – tu nic nie robi; usunąć lub zamienić na `unchecked`.
- [ ] **Architektura:** dodać `ArchitecturesInstallIn64BitMode=x64compatible` i `ArchitecturesAllowed=x64compatible`. Bez tego 64-bitowy program trafi do `Program Files (x86)`, a na 32-bitowym Windows instalacja się uda, ale program nie uruchomi.
- [ ] **Licencja w instalatorze:** Inno Setup poprawnie czyta polskie znaki w `.txt` tylko przy UTF-8 **z BOM** (lub ANSI) – sprawdzić ekran licencji.
- [x] **Komentarz „BARDZO WAŻNE: Wygeneruj swój własny AppId”** – pozostałość szablonu; usunąć, żeby nikt nie zmienił GUID (zepsułoby aktualizacje).
- [ ] **`.bat`:** dodać `@echo off`, `cd /d "%~dp0"` i przerwanie przy błędzie PyInstallera (`if errorlevel 1 ...`).
- [ ] Niepodpisany `.exe` z PyInstallera często wywołuje alarmy antywirusów i SmartScreen – opisać w README dla nauczycieli.

---

## ⚖️ Licencja (do konsultacji z prawnikiem)

- [ ] **PyQt6 jest na licencji GPL v3** (lub komercyjnej). Program z nim rozpowszechniany musi mieć licencję zgodną z GPL – zakaz modyfikacji i tworzenia programów pochodnych jest z tym sprzeczny. Opcje: wydać mkEdytor na GPL v3 albo przejść na **PySide6** (LGPL, API niemal identyczne). Nawet wtedy biblioteki Qt (LGPL) wymagają dołączenia ich licencji i nie pozwalają zakazać inżynierii wstecznej w zakresie potrzebnym do ich podmiany.
- [ ] Prawo autorskie (art. 75 ust. 2 pkt 3 w zw. z art. 76) dopuszcza dekompilację w celu interoperacyjności – umowa nie może tego wyłączyć.
- [ ] Art. 473 § 2 KC unieważnia wyłączenie odpowiedzialności za szkodę wyrządzoną umyślnie – sformułowanie „jakiekolwiek szkody” jest za szerokie.
- [ ] Dzieci nie mogą skutecznie zawrzeć umowy – w praktyce licencję akceptuje szkoła lub rodzic; warto to napisać wprost.

---

## Kolejność prac

1. [x] Obsługa `sys.argv` (pkt 1)
2. [x] Kolor startowy w oknie kolorów (pkt 2)
3. [x] ~~Ostrzeżenie przed~~ (zbędne – brak zapisu do .txt) utratą formatowania przy zapisie do .txt (pkt 3)
4. [x] Polskie tłumaczenia Qt (pkt 14)
5. [x] Skrót Ctrl+Shift+S (pkt 6)
6. [x] Jeden numer wersji (pkt 5)
7. [ ] Decyzja licencyjna: PyQt6 na GPL albo PySide6
