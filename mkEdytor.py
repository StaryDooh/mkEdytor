import sys
import os
import json
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTextEdit, QToolBar,
                             QComboBox, QSpinBox, QColorDialog, QFileDialog,
                             QMessageBox)
from PyQt6.QtGui import (QFont, QAction, QFontDatabase, QTextListFormat,
                         QKeySequence, QIcon, QTextDocumentWriter, QPdfWriter,
                         QPageSize, QDesktopServices, QTextCharFormat,
                         QTextBlockFormat)
from PyQt6.QtCore import Qt, QUrl, QStandardPaths, QSettings, QTimer
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog


# --- FUNKCJA DO OBSŁUGI ŚCIEŻEK W PLIKU .EXE ---
def sciezka_zasobu(wzgledna_sciezka):
    try:
        baza = sys._MEIPASS
    except Exception:
        baza = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(baza, wzgledna_sciezka)


# --- FORMAT DOKUMENTU mkEdytora (.mked) ---
# Plik .mked to tekst UTF-8 w formacie JSON:
#   {"format": "mkEdytor", "wersja_formatu": 1, "program": "...", "tresc": "<html Qt>"}
# Pole "wersja_formatu" pozwoli w przyszłości rozbudować format (np. o obrazki)
# bez utraty zgodności ze starszymi dokumentami.
ROZSZERZENIE = ".mked"
FORMAT_ID = "mkEdytor"
FORMAT_WERSJA = 1
PROGID = "mkEdytor.dokument"   # identyfikator typu pliku w rejestrze (taki sam jak w instalatorze)


# --- SKOJARZENIE PLIKÓW .mked Z PROGRAMEM (tylko Windows) ---
def obsluga_skojarzen():
    """Skojarzenia ustawiamy tylko w zbudowanym .exe na Windows.
    Przy uruchamianiu z Pythona skojarzyłoby to pliki z python.exe."""
    return sys.platform == "win32" and getattr(sys, "frozen", False)


def _program_dla_rozszerzenia(rozszerzenie):
    """Zwraca ścieżkę programu, którym Windows faktycznie otworzy plik
    (uwzględnia też wybór użytkownika z okna „Otwórz za pomocą”)."""
    import ctypes
    from ctypes import wintypes
    ASSOCF_INIT_IGNOREUNKNOWN = 0x400
    ASSOCSTR_EXECUTABLE = 2
    funkcja = ctypes.windll.shlwapi.AssocQueryStringW
    funkcja.argtypes = [wintypes.DWORD, ctypes.c_int, wintypes.LPCWSTR, wintypes.LPCWSTR,
                        wintypes.LPWSTR, ctypes.POINTER(wintypes.DWORD)]
    funkcja.restype = ctypes.c_long
    rozmiar = wintypes.DWORD(1024)
    bufor = ctypes.create_unicode_buffer(rozmiar.value)
    wynik = funkcja(ASSOCF_INIT_IGNOREUNKNOWN, ASSOCSTR_EXECUTABLE, rozszerzenie,
                    None, bufor, ctypes.byref(rozmiar))
    return bufor.value if wynik == 0 else None


def czy_mked_skojarzony():
    program = _program_dla_rozszerzenia(ROZSZERZENIE)
    if not program:
        return False
    try:
        return os.path.samefile(program, sys.executable)
    except OSError:
        return (os.path.normcase(os.path.abspath(program))
                == os.path.normcase(os.path.abspath(sys.executable)))


def _usun_klucz_rekurencyjnie(korzen, sciezka):
    import winreg
    try:
        with winreg.OpenKey(korzen, sciezka, 0, winreg.KEY_READ) as klucz:
            podklucze = []
            i = 0
            while True:
                try:
                    podklucze.append(winreg.EnumKey(klucz, i))
                    i += 1
                except OSError:
                    break
        for podklucz in podklucze:
            _usun_klucz_rekurencyjnie(korzen, sciezka + "\\" + podklucz)
        winreg.DeleteKey(korzen, sciezka)
    except FileNotFoundError:
        pass


def skojarz_mked_dla_uzytkownika():
    """Rejestruje .mked dla bieżącego użytkownika (HKCU) – nie wymaga uprawnień
    administratora. Usuwa też wcześniejszy wybór innego programu dla .mked."""
    import winreg
    import ctypes
    exe = sys.executable
    klasy = r"Software\Classes"
    wpisy = [
        (rf"{klasy}\{PROGID}", "", "Dokument mkEdytor"),
        (rf"{klasy}\{PROGID}\DefaultIcon", "", f'"{exe}",0'),
        (rf"{klasy}\{PROGID}\shell\open\command", "", f'"{exe}" "%1"'),
        (rf"{klasy}\{ROZSZERZENIE}", "", PROGID),
        (rf"{klasy}\{ROZSZERZENIE}\OpenWithProgids", PROGID, ""),
    ]
    for sciezka, nazwa, wartosc in wpisy:
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, sciezka) as klucz:
            winreg.SetValueEx(klucz, nazwa, 0, winreg.REG_SZ, wartosc)

    # Wybór z okna „Otwórz za pomocą → Zawsze” (UserChoice) ma pierwszeństwo
    # przed rejestracją – .mked to nasze rozszerzenie, więc go kasujemy.
    _usun_klucz_rekurencyjnie(
        winreg.HKEY_CURRENT_USER,
        r"Software\Microsoft\Windows\CurrentVersion\Explorer\FileExts" + "\\" + ROZSZERZENIE)

    SHCNE_ASSOCCHANGED = 0x08000000
    ctypes.windll.shell32.SHChangeNotify(SHCNE_ASSOCCHANGED, 0, None, None)


class NowoczesnyEdytor(QMainWindow):

    # Wersja jako stała klasy
    WERSJA = "2.0.7.0"
    NAZWA_DOMYSLNA = "Bez nazwy"   # nazwa nowego, niezapisanego dokumentu
    CZCIONKA_DOMYSLNA = "Arial"    # krój i rozmiar tekstu w nowym dokumencie
    ROZMIAR_DOMYSLNY = 18

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"mkEdytor v{self.WERSJA} - {self.NAZWA_DOMYSLNA}")
        self.resize(1000, 700)

        self.setWindowIcon(QIcon(sciezka_zasobu("ikona.ico")))

        self.pulpit = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DesktopLocation)
        self.ostatni_katalog = self.pulpit

        self.aktualny_plik = None      # ścieżka do pliku .mked (lub None)
        self.nazwa_importu = None      # nazwa zaimportowanego pliku .html/.txt (lub None)

        self.edytor = QTextEdit()
        domyslna_czcionka = QFont(self.CZCIONKA_DOMYSLNA, self.ROZMIAR_DOMYSLNY)
        self.edytor.setFont(domyslna_czcionka)
        self.edytor.setStyleSheet("QTextEdit { padding: 20px; border: none; }")
        self.setCentralWidget(self.edytor)

        self.stworz_menu()
        self.stworz_pasek_narzedzi()

        self.edytor.textChanged.connect(self.utrzymaj_formatowanie)
        # Niezapisane zmiany śledzi sam dokument Qt – cofnięcie (Ctrl+Z) do stanu
        # z ostatniego zapisu z powrotem oznacza dokument jako niezmieniony.
        self.edytor.document().modificationChanged.connect(self._aktualizuj_tytul)
        self.edytor.cursorPositionChanged.connect(self.aktualizuj_stan_narzedzi)
        self.edytor.currentCharFormatChanged.connect(self.aktualizuj_stan_narzedzi)

    # --- Wymuszenie polskich przycisków w oknie dialogowym ---
    def _zapytaj_o_zapis(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("Niezapisane zmiany")
        msg.setText("Dokument ma niezapisane zmiany.\nCzy chcesz go zapisać?")
        msg.setIcon(QMessageBox.Icon.Question)
        
        btn_zapisz = msg.addButton("Zapisz", QMessageBox.ButtonRole.AcceptRole)
        btn_odrzuc = msg.addButton("Nie zapisuj", QMessageBox.ButtonRole.DestructiveRole)
        btn_anuluj = msg.addButton("Anuluj", QMessageBox.ButtonRole.RejectRole)
        
        msg.exec()
        
        if msg.clickedButton() == btn_zapisz:
            return "ZAPISZ"
        elif msg.clickedButton() == btn_odrzuc:
            return "ODRZUC"
        else:
            return "ANULUJ"

    @property
    def zmodyfikowany(self):
        """Czy dokument ma niezapisane zmiany (stan prowadzony przez QTextDocument)."""
        return self.edytor.document().isModified()

    def _oznacz_jako_zapisany(self):
        """Bieżący stan dokumentu staje się punktem odniesienia dla „niezapisanych zmian”."""
        self.edytor.document().setModified(False)
        self._aktualizuj_tytul()

    def _aktualizuj_tytul(self, *_):
        if self.aktualny_plik:
            nazwa = os.path.basename(self.aktualny_plik)
        elif self.nazwa_importu:
            nazwa = f"{self.nazwa_importu} (zaimportowany)"
        else:
            nazwa = self.NAZWA_DOMYSLNA
        prefiks = "* " if self.zmodyfikowany else ""
        self.setWindowTitle(f"{prefiks}mkEdytor v{self.WERSJA} - {nazwa}")

    @staticmethod
    def _z_rozszerzeniem(sciezka, rozszerzenie, dozwolone=None):
        """Dopisuje rozszerzenie, jeśli użytkownik go nie podał."""
        dozwolone = dozwolone or (rozszerzenie,)
        if os.path.splitext(sciezka)[1].lower() not in dozwolone:
            sciezka += rozszerzenie
        return sciezka

    def _domyslna_sciezka(self, rozszerzenie):
        """Proponowana nazwa pliku w oknach zapisu i eksportu."""
        if self.aktualny_plik:
            nazwa = os.path.basename(self.aktualny_plik)
        elif self.nazwa_importu:
            nazwa = self.nazwa_importu
        else:
            nazwa = self.NAZWA_DOMYSLNA
        nazwa = os.path.splitext(nazwa)[0] + rozszerzenie
        return os.path.join(self.ostatni_katalog, nazwa)

    def closeEvent(self, event):
        if self.zmodyfikowany:
            odpowiedz = self._zapytaj_o_zapis()
            if odpowiedz == "ZAPISZ":
                self.zapisz_plik()
                # Jeśli zapis się nie powiódł, nie zamykaj
                if self.zmodyfikowany:
                    event.ignore()
                    return
            elif odpowiedz == "ANULUJ":
                event.ignore()
                return
        event.accept()

    def stworz_menu(self):
        pasek_menu = self.menuBar()

        # --- MENU PLIK ---
        menu_plik = pasek_menu.addMenu("Plik")
        akcja_nowy = QAction("Nowy", self)
        akcja_nowy.setShortcut(QKeySequence.StandardKey.New)
        akcja_nowy.triggered.connect(self.nowy_plik)
        menu_plik.addAction(akcja_nowy)

        akcja_otworz = QAction("Otwórz...", self)
        akcja_otworz.setShortcut(QKeySequence.StandardKey.Open)
        akcja_otworz.triggered.connect(self.otworz_plik)
        menu_plik.addAction(akcja_otworz)

        akcja_zapisz = QAction("Zapisz", self)
        akcja_zapisz.setShortcut(QKeySequence.StandardKey.Save)
        akcja_zapisz.triggered.connect(self.zapisz_plik)
        menu_plik.addAction(akcja_zapisz)

        akcja_zapisz_jako = QAction("Zapisz jako...", self)
        # StandardKey.SaveAs jest na Windows puste – skrót ustawiamy jawnie
        akcja_zapisz_jako.setShortcut(QKeySequence("Ctrl+Shift+S"))
        akcja_zapisz_jako.triggered.connect(self.zapisz_jako)
        menu_plik.addAction(akcja_zapisz_jako)

        menu_plik.addSeparator()

        akcja_drukuj = QAction("Drukuj", self)
        akcja_drukuj.setShortcut(QKeySequence.StandardKey.Print)
        akcja_drukuj.triggered.connect(self.drukuj_plik)
        menu_plik.addAction(akcja_drukuj)

        menu_plik.addSeparator()

        akcja_eksport_odt = QAction("Wyeksportuj do .odt (LibreOffice Writer)", self)
        akcja_eksport_odt.triggered.connect(self.eksportuj_odt)
        menu_plik.addAction(akcja_eksport_odt)

        akcja_eksport_html = QAction("Wyeksportuj do HTML (strona internetowa)", self)
        akcja_eksport_html.triggered.connect(self.eksportuj_html)
        menu_plik.addAction(akcja_eksport_html)

        akcja_eksport_pdf = QAction("Wyeksportuj do PDF", self)
        akcja_eksport_pdf.triggered.connect(self.eksportuj_pdf)
        menu_plik.addAction(akcja_eksport_pdf)

        menu_plik.addSeparator()

        akcja_skojarz = QAction(f"Otwieraj pliki {ROZSZERZENIE} w mkEdytorze", self)
        akcja_skojarz.triggered.connect(lambda: self.sprawdz_skojarzenie(na_zadanie=True))
        akcja_skojarz.setEnabled(obsluga_skojarzen())
        menu_plik.addAction(akcja_skojarz)

        # --- MENU EDYTUJ ---
        menu_edytuj = pasek_menu.addMenu("Edytuj")
        akcja_cofnij = QAction("Cofnij", self)
        akcja_cofnij.setShortcut(QKeySequence.StandardKey.Undo)
        akcja_cofnij.triggered.connect(self.edytor.undo)
        menu_edytuj.addAction(akcja_cofnij)

        akcja_ponow = QAction("Ponów", self)
        akcja_ponow.setShortcut(QKeySequence.StandardKey.Redo)
        akcja_ponow.triggered.connect(self.edytor.redo)
        menu_edytuj.addAction(akcja_ponow)

        menu_edytuj.addSeparator()

        akcja_wytnij_menu = QAction("Wytnij", self)
        akcja_wytnij_menu.setShortcut(QKeySequence.StandardKey.Cut)
        akcja_wytnij_menu.triggered.connect(self.edytor.cut)
        menu_edytuj.addAction(akcja_wytnij_menu)

        akcja_kopiuj_menu = QAction("Kopiuj", self)
        akcja_kopiuj_menu.setShortcut(QKeySequence.StandardKey.Copy)
        akcja_kopiuj_menu.triggered.connect(self.edytor.copy)
        menu_edytuj.addAction(akcja_kopiuj_menu)

        akcja_wklej_menu = QAction("Wklej", self)
        akcja_wklej_menu.setShortcut(QKeySequence.StandardKey.Paste)
        akcja_wklej_menu.triggered.connect(self.edytor.paste)
        menu_edytuj.addAction(akcja_wklej_menu)

        # --- MENU ODWIEDŹ ---
        menu_odwiedz = pasek_menu.addMenu("Odwiedź")

        akcja_pobierz = QAction("Pobierz najnowszą wersję", self)
        akcja_pobierz.triggered.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com/StaryDooh/mkEdytor/releases/")))
        menu_odwiedz.addAction(akcja_pobierz)

        akcja_zglos = QAction("Zgłoś błąd", self)
        akcja_zglos.triggered.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com/StaryDooh/mkEdytor/issues/")))
        menu_odwiedz.addAction(akcja_zglos)

        akcja_relaks = QAction("Zrelaksuj się", self)
        akcja_relaks.triggered.connect(lambda: QDesktopServices.openUrl(QUrl("https://www.youtube.com/@StaryDooh")))
        menu_odwiedz.addAction(akcja_relaks)

    def stworz_pasek_narzedzi(self):
        pasek = QToolBar("Pasek Narzędzi")
        pasek.setMovable(False)
        pasek.setStyleSheet("QToolBar { spacing: 5px; padding: 5px; } QToolButton { font-size: 18px; padding: 4px; }")
        self.addToolBar(pasek)

        akcja_cofnij_tb = QAction("↩", self)
        akcja_cofnij_tb.setToolTip("Cofnij (Ctrl+Z)")
        akcja_cofnij_tb.triggered.connect(self.edytor.undo)
        pasek.addAction(akcja_cofnij_tb)

        akcja_ponow_tb = QAction("↪", self)
        akcja_ponow_tb.setToolTip("Ponów (Ctrl+Y)")
        akcja_ponow_tb.triggered.connect(self.edytor.redo)
        pasek.addAction(akcja_ponow_tb)

        pasek.addSeparator()

        akcja_wytnij = QAction("✂️", self)
        akcja_wytnij.setToolTip("Wytnij (Ctrl+X)")
        akcja_wytnij.triggered.connect(self.edytor.cut)
        pasek.addAction(akcja_wytnij)

        akcja_kopiuj = QAction("📄", self)
        akcja_kopiuj.setToolTip("Kopiuj (Ctrl+C)")
        akcja_kopiuj.triggered.connect(self.edytor.copy)
        pasek.addAction(akcja_kopiuj)

        akcja_wklej = QAction("📋", self)
        akcja_wklej.setToolTip("Wklej (Ctrl+V)")
        akcja_wklej.triggered.connect(self.edytor.paste)
        pasek.addAction(akcja_wklej)

        pasek.addSeparator()

        self.lista_czcionek = QComboBox()
        self.lista_czcionek.addItems(QFontDatabase.families())
        self.lista_czcionek.setCurrentText(self.CZCIONKA_DOMYSLNA)
        self.lista_czcionek.currentTextChanged.connect(self.zmien_czcionke)
        pasek.addWidget(self.lista_czcionek)

        self.rozmiar_czcionki = QSpinBox()
        self.rozmiar_czcionki.setRange(8, 72)
        self.rozmiar_czcionki.setValue(self.ROZMIAR_DOMYSLNY)
        self.rozmiar_czcionki.valueChanged.connect(self.zmien_rozmiar)
        pasek.addWidget(self.rozmiar_czcionki)

        akcja_kolor = QAction("🎨", self)
        akcja_kolor.setToolTip("Zmień kolor tekstu")
        akcja_kolor.triggered.connect(self.wybierz_kolor)
        pasek.addAction(akcja_kolor)

        pasek.addSeparator()

        self.akcja_pogrubienie = QAction("𝐁", self)
        self.akcja_pogrubienie.setToolTip("Pogrubienie")
        self.akcja_pogrubienie.setCheckable(True)
        self.akcja_pogrubienie.triggered.connect(
            lambda ch: self.edytor.setFontWeight(QFont.Weight.Bold if ch else QFont.Weight.Normal))
        pasek.addAction(self.akcja_pogrubienie)

        self.akcja_pochylenie = QAction("𝐼", self)
        self.akcja_pochylenie.setToolTip("Pochylenie")
        self.akcja_pochylenie.setCheckable(True)
        self.akcja_pochylenie.triggered.connect(self.edytor.setFontItalic)
        pasek.addAction(self.akcja_pochylenie)

        self.akcja_podkreslenie = QAction("U̲", self)
        self.akcja_podkreslenie.setToolTip("Podkreślenie")
        self.akcja_podkreslenie.setCheckable(True)
        self.akcja_podkreslenie.triggered.connect(self.edytor.setFontUnderline)
        pasek.addAction(self.akcja_podkreslenie)

        pasek.addSeparator()

        akcja_lewo = self._akcja_z_ikona("lewo.png", "⬅", "Wyrównaj do lewej")
        akcja_lewo.triggered.connect(lambda: self.edytor.setAlignment(Qt.AlignmentFlag.AlignLeft))
        pasek.addAction(akcja_lewo)

        akcja_srodek = self._akcja_z_ikona("srodek.png", "↔", "Wyrównaj do środka")
        akcja_srodek.triggered.connect(lambda: self.edytor.setAlignment(Qt.AlignmentFlag.AlignCenter))
        pasek.addAction(akcja_srodek)

        akcja_prawo = self._akcja_z_ikona("prawo.png", "➡", "Wyrównaj do prawej")
        akcja_prawo.triggered.connect(lambda: self.edytor.setAlignment(Qt.AlignmentFlag.AlignRight))
        pasek.addAction(akcja_prawo)

        akcja_justuj = self._akcja_z_ikona("justuj.png", "≡", "Wyjustuj")
        akcja_justuj.triggered.connect(lambda: self.edytor.setAlignment(Qt.AlignmentFlag.AlignJustify))
        pasek.addAction(akcja_justuj)

        pasek.addSeparator()

        akcja_punktory = self._akcja_z_ikona("l_punktowana.png", "•≡", "Lista punktowana")
        akcja_punktory.triggered.connect(self.wstaw_liste_punktowana)
        pasek.addAction(akcja_punktory)

        akcja_numerowana = self._akcja_z_ikona("l_numerowana.png", "1≡", "Lista numerowana")
        akcja_numerowana.triggered.connect(self.wstaw_liste_numerowana)
        pasek.addAction(akcja_numerowana)

    def _akcja_z_ikona(self, nazwa_pliku, tekst_fallback, tooltip):
        sciezka = sciezka_zasobu(nazwa_pliku)
        if os.path.exists(sciezka):
            akcja = QAction(QIcon(sciezka), "", self)
        else:
            akcja = QAction(tekst_fallback, self)
        akcja.setToolTip(tooltip)
        return akcja

    def aktualizuj_stan_narzedzi(self):
        czcionka = self.edytor.currentFont()
        self.akcja_pogrubienie.setChecked(czcionka.bold())
        self.akcja_pochylenie.setChecked(czcionka.italic())
        self.akcja_podkreslenie.setChecked(czcionka.underline())

        self.lista_czcionek.blockSignals(True)
        self.rozmiar_czcionki.blockSignals(True)
        self.lista_czcionek.setCurrentText(czcionka.family())
        rozmiar = czcionka.pointSize()
        if rozmiar > 0:
            self.rozmiar_czcionki.setValue(rozmiar)
        self.lista_czcionek.blockSignals(False)
        self.rozmiar_czcionki.blockSignals(False)

    def utrzymaj_formatowanie(self):
        if self.edytor.document().isEmpty() and not self.edytor.textCursor().currentList():
            self.edytor.blockSignals(True)
            self.edytor.setFontFamily(self.lista_czcionek.currentText())
            self.edytor.setFontPointSize(self.rozmiar_czcionki.value())
            self.edytor.blockSignals(False)

    def zmien_czcionke(self, nazwa):
        fmt = QTextCharFormat()
        fmt.setFontFamily(nazwa)
        self.edytor.mergeCurrentCharFormat(fmt)
        self.edytor.setFocus()

    def zmien_rozmiar(self, wartosc):
        fmt = QTextCharFormat()
        fmt.setFontPointSize(float(wartosc))
        self.edytor.mergeCurrentCharFormat(fmt)
        self.edytor.setFocus()

    def wybierz_kolor(self):
        # Start z bieżącym kolorem tekstu (domyślnie byłby biały – niewidoczny na białym tle)
        kolor = QColorDialog.getColor(self.edytor.textColor(), self, "Wybierz kolor tekstu")
        if kolor.isValid():
            fmt = QTextCharFormat()
            fmt.setForeground(kolor)
            self.edytor.mergeCurrentCharFormat(fmt)
        self.edytor.setFocus()

    def wstaw_liste_punktowana(self):
        kursor = self.edytor.textCursor()
        obecna_lista = kursor.currentList()
        if obecna_lista:
            if obecna_lista.format().style() == QTextListFormat.Style.ListDisc:
                format_bloku = kursor.blockFormat()
                format_bloku.setObjectIndex(-1)
                kursor.setBlockFormat(format_bloku)
            else:
                nowy_format = obecna_lista.format()
                nowy_format.setStyle(QTextListFormat.Style.ListDisc)
                obecna_lista.setFormat(nowy_format)
        else:
            kursor.createList(QTextListFormat.Style.ListDisc)
        self.edytor.setFocus()

    def wstaw_liste_numerowana(self):
        kursor = self.edytor.textCursor()
        obecna_lista = kursor.currentList()
        if obecna_lista:
            if obecna_lista.format().style() == QTextListFormat.Style.ListDecimal:
                format_bloku = kursor.blockFormat()
                format_bloku.setObjectIndex(-1)
                kursor.setBlockFormat(format_bloku)
            else:
                nowy_format = obecna_lista.format()
                nowy_format.setStyle(QTextListFormat.Style.ListDecimal)
                obecna_lista.setFormat(nowy_format)
        else:
            kursor.createList(QTextListFormat.Style.ListDecimal)
        self.edytor.setFocus()

    def nowy_plik(self):
        if self.zmodyfikowany:
            odpowiedz = self._zapytaj_o_zapis()
            if odpowiedz == "ZAPISZ":
                self.zapisz_plik()
                if self.zmodyfikowany:
                    return
            elif odpowiedz == "ANULUJ":
                return

        self.edytor.clear()
        self._przywroc_domyslne_formatowanie()
        self.aktualny_plik = None
        self.nazwa_importu = None
        self._oznacz_jako_zapisany()

    def _przywroc_domyslne_formatowanie(self):
        """Nowy dokument zaczyna się od ustawień startowych: Arial 18, czarny,
        bez pogrubienia/pochylenia/podkreślenia, wyrównanie do lewej, bez listy."""
        # Pasek narzędzi – bez sygnałów, żeby nie formatować pustego dokumentu dwa razy
        self.lista_czcionek.blockSignals(True)
        self.rozmiar_czcionki.blockSignals(True)
        self.lista_czcionek.setCurrentText(self.CZCIONKA_DOMYSLNA)
        self.rozmiar_czcionki.setValue(self.ROZMIAR_DOMYSLNY)
        self.lista_czcionek.blockSignals(False)
        self.rozmiar_czcionki.blockSignals(False)

        kursor = self.edytor.textCursor()
        kursor.setBlockFormat(QTextBlockFormat())   # akapit: do lewej, bez wcięć i listy
        kursor.setBlockCharFormat(QTextCharFormat())
        self.edytor.setTextCursor(kursor)
        self.edytor.setCurrentCharFormat(QTextCharFormat())  # znaki: domyślne
        self.edytor.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.utrzymaj_formatowanie()                 # krój i rozmiar z paska

        # Te zmiany nie powinny dać się „cofnąć” w nowym dokumencie
        self.edytor.document().clearUndoRedoStacks()
        self.aktualizuj_stan_narzedzi()

    def otworz_plik(self):
        if self.zmodyfikowany:
            odpowiedz = self._zapytaj_o_zapis()
            if odpowiedz == "ZAPISZ":
                self.zapisz_plik()
                if self.zmodyfikowany:
                    return
            elif odpowiedz == "ANULUJ":
                return

        sciezka, _ = QFileDialog.getOpenFileName(
            self, "Otwórz plik", self.ostatni_katalog,
            f"Dokument mkEdytor (*{ROZSZERZENIE});;"
            "Starsze dokumenty – import (*.html *.htm *.txt);;"
            "Wszystkie pliki (*.*)"
        )
        if sciezka:
            self.wczytaj_plik(sciezka)

    def wczytaj_plik(self, sciezka):
        """Otwiera dokument .mked albo importuje starszy plik .html / .txt.

        Używane przez menu „Otwórz” oraz przy uruchomieniu z argumentem
        (dwuklik na pliku .mked w Eksploratorze Windows).
        """
        sciezka = os.path.abspath(sciezka)
        self.ostatni_katalog = os.path.dirname(sciezka)
        rozszerzenie = os.path.splitext(sciezka)[1].lower()

        if rozszerzenie == ROZSZERZENIE:
            html = self._czytaj_mked(sciezka)
            if html is None:
                return False
            self.edytor.setHtml(html)
            self.aktualny_plik = sciezka
            self.nazwa_importu = None
        else:
            # Import: plik źródłowy nie zostanie nadpisany –
            # „Zapisz” zaproponuje zapis jako nowy dokument .mked.
            zawartosc = self._czytaj_plik(sciezka)
            if zawartosc is None:
                return False
            if rozszerzenie in (".html", ".htm"):
                self.edytor.setHtml(zawartosc)
            else:
                self.edytor.setPlainText(zawartosc)
            self.aktualny_plik = None
            self.nazwa_importu = os.path.basename(sciezka)

        self._oznacz_jako_zapisany()
        return True

    def _czytaj_mked(self, sciezka):
        """Zwraca treść HTML dokumentu .mked albo None przy błędzie."""
        try:
            with open(sciezka, "r", encoding="utf-8-sig") as plik:
                surowe = plik.read()
            if not surowe.strip():
                return ""  # pusty plik = pusty dokument
            dane = json.loads(surowe)
        except (OSError, ValueError) as e:
            QMessageBox.critical(
                self, "Błąd",
                "Nie udało się otworzyć dokumentu.\n"
                "Plik może być uszkodzony albo nie jest dokumentem mkEdytora.\n\n"
                f"Szczegóły: {e}"
            )
            return None

        if (not isinstance(dane, dict) or dane.get("format") != FORMAT_ID
                or not isinstance(dane.get("tresc"), str)):
            QMessageBox.critical(
                self, "Błąd",
                "Ten plik nie jest dokumentem mkEdytora albo jest uszkodzony."
            )
            return None

        wersja_formatu = dane.get("wersja_formatu", 1)
        if isinstance(wersja_formatu, int) and wersja_formatu > FORMAT_WERSJA:
            QMessageBox.warning(
                self, "Nowsza wersja dokumentu",
                "Ten dokument został utworzony w nowszej wersji mkEdytora.\n"
                "Część formatowania może się nie wyświetlić.\n\n"
                "Pobierz najnowszą wersję programu z menu „Odwiedź”."
            )
        return dane["tresc"]

    # Maksymalny rozmiar importowanego pliku .txt/.html (większe zamroziłyby edytor)
    MAKS_ROZMIAR_IMPORTU = 10 * 1024 * 1024  # 10 MB

    def _czytaj_plik(self, sciezka):
        """Wczytuje starszy plik .txt / .html do importu.

        Rozpoznawane kodowania:
        - UTF-16 (z BOM) – „Unicode” z Notatnika,
        - UTF-8 (z BOM i bez),
        - Windows-1250 – starsze polskie pliki z Windows.
        Windows-1250 ma 5 nieprzypisanych bajtów, więc bardzo rzadko może się nie udać –
        wtedy nieznane znaki są zastępowane znakiem „�” i pojawia się ostrzeżenie.
        """
        try:
            if os.path.getsize(sciezka) > self.MAKS_ROZMIAR_IMPORTU:
                QMessageBox.critical(
                    self, "Plik jest za duży",
                    "Ten plik jest za duży, żeby otworzyć go w mkEdytorze (ponad 10 MB).")
                return None
            with open(sciezka, "rb") as plik:
                dane = plik.read()
        except OSError as e:
            QMessageBox.critical(self, "Błąd", f"Nie udało się otworzyć pliku:\n{e}")
            return None

        # UTF-16 trzeba rozpoznać przed sprawdzaniem bajtów zerowych (zawiera ich mnóstwo)
        if dane.startswith((b"\xff\xfe", b"\xfe\xff")):
            try:
                return dane.decode("utf-16")
            except UnicodeDecodeError:
                pass

        # Bajty zerowe nie występują w plikach tekstowych – to np. .docx, .exe, obrazek
        if b"\x00" in dane:
            QMessageBox.critical(
                self, "To nie jest plik tekstowy",
                "Tego pliku nie da się otworzyć w mkEdytorze.\n"
                "Można otwierać dokumenty mkEdytora (.mked) oraz pliki tekstowe (.txt, .html).")
            return None

        try:
            return dane.decode("utf-8-sig")
        except UnicodeDecodeError:
            pass

        try:
            return dane.decode("windows-1250")
        except UnicodeDecodeError:
            QMessageBox.warning(
                self, "Ostrzeżenie kodowania",
                "Niektórych znaków w tym pliku nie udało się odczytać.\n"
                "Zostały zastąpione znakiem „�”.")
            return dane.decode("windows-1250", errors="replace")

    def zapisz_plik(self):
        if self.aktualny_plik:
            return self.zapisz_na_dysk(self.aktualny_plik)
        return self.zapisz_jako()

    def zapisz_jako(self):
        sciezka, _ = QFileDialog.getSaveFileName(
            self, "Zapisz jako", self._domyslna_sciezka(ROZSZERZENIE),
            f"Dokument mkEdytor (*{ROZSZERZENIE})"
        )
        if not sciezka:
            return False
        sciezka = self._z_rozszerzeniem(sciezka, ROZSZERZENIE)
        self.ostatni_katalog = os.path.dirname(sciezka)
        # Ścieżkę zapamiętujemy dopiero po udanym zapisie
        if self.zapisz_na_dysk(sciezka):
            self.aktualny_plik = sciezka
            self.nazwa_importu = None
            self._aktualizuj_tytul()
            return True
        return False

    def zapisz_na_dysk(self, sciezka):
        dane = {
            "format": FORMAT_ID,
            "wersja_formatu": FORMAT_WERSJA,
            "program": f"mkEdytor {self.WERSJA}",
            "tresc": self.edytor.toHtml(),
        }
        tresc = json.dumps(dane, ensure_ascii=False, indent=1)
        if self._zapisz_atomowo(sciezka, tresc):
            self._oznacz_jako_zapisany()
            return True
        return False

    def _zapisz_atomowo(self, sciezka, tresc):
        """Zapis przez plik tymczasowy – przerwany zapis nie niszczy oryginału."""
        tmp = sciezka + ".tmp"
        try:
            with open(tmp, "w", encoding="utf-8") as f:
                f.write(tresc)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp, sciezka)
            return True
        except OSError as e:
            try:
                if os.path.exists(tmp):
                    os.remove(tmp)
            except OSError:
                pass
            QMessageBox.critical(self, "Błąd", f"Nie udało się zapisać pliku:\n{e}")
            return False

    def drukuj_plik(self):
        drukarka = QPrinter(QPrinter.PrinterMode.HighResolution)
        okno_druku = QPrintDialog(drukarka, self)
        if okno_druku.exec():
            self.edytor.document().print(drukarka)

    def _eksportuj(self, sciezka, zapisz, nazwa_formatu):
        """Wspólna obsługa eksportu (ODT, PDF).

        Eksport trafia najpierw do pliku tymczasowego. Dopiero gdy ten plik istnieje
        i nie jest pusty, zastępuje plik docelowy. Dzięki temu:
        - komunikat „Sukces” pojawia się tylko po faktycznym zapisie,
        - błąd wychodzi na jaw także wtedy, gdy stary plik o tej nazwie istnieje,
          ale jest zablokowany (np. otwarty w przeglądarce PDF).
        """
        tmp = sciezka + ".tmp"
        try:
            udalo_sie = zapisz(tmp)
            if udalo_sie and os.path.isfile(tmp) and os.path.getsize(tmp) > 0:
                os.replace(tmp, sciezka)
                QMessageBox.information(self, "Sukces", f"Pomyślnie wyeksportowano plik {nazwa_formatu}.")
                return True
        except Exception:
            pass

        try:
            if os.path.exists(tmp):
                os.remove(tmp)
        except OSError:
            pass
        QMessageBox.critical(
            self, "Błąd eksportu",
            f"Nie udało się zapisać pliku {nazwa_formatu}.\n\n"
            "Jeśli ten plik jest otwarty w innym programie, zamknij go i spróbuj ponownie.\n"
            "Sprawdź też, czy masz uprawnienia do zapisu w wybranym folderze."
        )
        return False

    def eksportuj_odt(self):
        sciezka, _ = QFileDialog.getSaveFileName(
            self, "Eksportuj do ODT", self._domyslna_sciezka(".odt"),
            "Plik LibreOffice Writer (*.odt)"
        )
        if not sciezka:
            return
        sciezka = self._z_rozszerzeniem(sciezka, ".odt")

        def zapisz(plik):
            writer = QTextDocumentWriter(plik)
            writer.setFormat(b"odf")  # format jawnie – nie zależy od rozszerzenia pliku
            wynik = writer.write(self.edytor.document())
            del writer  # zamknięcie pliku przed sprawdzeniem rozmiaru
            return wynik

        self._eksportuj(sciezka, zapisz, "ODT")

    def eksportuj_pdf(self):
        sciezka, _ = QFileDialog.getSaveFileName(
            self, "Eksportuj do PDF", self._domyslna_sciezka(".pdf"),
            "Pliki PDF (*.pdf)"
        )
        if not sciezka:
            return
        sciezka = self._z_rozszerzeniem(sciezka, ".pdf")

        def zapisz(plik):
            pdf_writer = QPdfWriter(plik)
            pdf_writer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
            self.edytor.document().print(pdf_writer)
            del pdf_writer  # zamknięcie pliku przed sprawdzeniem rozmiaru
            return True  # QPdfWriter nie zgłasza błędów – o sukcesie decyduje rozmiar pliku

        self._eksportuj(sciezka, zapisz, "PDF")

    def sprawdz_skojarzenie(self, na_zadanie=False):
        """Sprawdza, czy pliki .mked otwierają się w mkEdytorze, i proponuje naprawę.

        na_zadanie=False – automatycznie przy starcie (można wyłączyć „Nie pytaj więcej”),
        na_zadanie=True  – z menu Plik.
        """
        if not obsluga_skojarzen():
            return
        ustawienia = QSettings("Krzysztof Markowski", "mkEdytor")
        if not na_zadanie and ustawienia.value("nie_pytaj_o_skojarzenie", False, type=bool):
            return

        try:
            skojarzony = czy_mked_skojarzony()
        except Exception:
            return  # nie przeszkadzamy dziecku, jeśli nie da się tego sprawdzić

        if skojarzony:
            if na_zadanie:
                QMessageBox.information(
                    self, "Pliki mkEdytora",
                    f"Wszystko w porządku – pliki {ROZSZERZENIE} otwierają się w mkEdytorze.")
            return

        if not na_zadanie:
            msg = QMessageBox(self)
            msg.setWindowTitle("Pliki mkEdytora")
            msg.setIcon(QMessageBox.Icon.Question)
            msg.setText(
                f"Dokumenty mkEdytora (pliki {ROZSZERZENIE}) nie otwierają się teraz w mkEdytorze.\n\n"
                "Czy ustawić, żeby otwierały się w mkEdytorze po dwukrotnym kliknięciu?")
            btn_tak = msg.addButton("Tak", QMessageBox.ButtonRole.AcceptRole)
            msg.addButton("Nie teraz", QMessageBox.ButtonRole.RejectRole)
            btn_nigdy = msg.addButton("Nie pytaj więcej", QMessageBox.ButtonRole.DestructiveRole)
            msg.exec()
            if msg.clickedButton() == btn_nigdy:
                ustawienia.setValue("nie_pytaj_o_skojarzenie", True)
                return
            if msg.clickedButton() != btn_tak:
                return

        try:
            skojarz_mked_dla_uzytkownika()
        except OSError as e:
            QMessageBox.critical(self, "Błąd", f"Nie udało się ustawić skojarzenia plików:\n{e}")
            return

        if czy_mked_skojarzony():
            ustawienia.setValue("nie_pytaj_o_skojarzenie", False)
            QMessageBox.information(
                self, "Gotowe",
                f"Gotowe! Pliki {ROZSZERZENIE} będą się teraz otwierać w mkEdytorze.")
        else:
            msg = QMessageBox(self)
            msg.setWindowTitle("Potrzebna pomoc")
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setText(
                f"Windows nie pozwolił automatycznie ustawić mkEdytora dla plików {ROZSZERZENIE}.\n\n"
                "Otwórz ustawienia „Aplikacje domyślne”, wpisz w wyszukiwaniu "
                f"„{ROZSZERZENIE}” i wybierz mkEdytor.")
            btn_ustawienia = msg.addButton("Otwórz ustawienia", QMessageBox.ButtonRole.AcceptRole)
            msg.addButton("Zamknij", QMessageBox.ButtonRole.RejectRole)
            msg.exec()
            if msg.clickedButton() == btn_ustawienia:
                QDesktopServices.openUrl(QUrl("ms-settings:defaultapps"))

    def eksportuj_html(self):
        sciezka, _ = QFileDialog.getSaveFileName(
            self, "Eksportuj do HTML", self._domyslna_sciezka(".html"),
            "Strona internetowa (*.html *.htm)"
        )
        if sciezka:
            sciezka = self._z_rozszerzeniem(sciezka, ".html", (".html", ".htm"))
            # Eksport nie zmienia bieżącego dokumentu ani stanu „niezapisany”
            if self._zapisz_atomowo(sciezka, self.edytor.toHtml()):
                QMessageBox.information(self, "Sukces", "Pomyślnie wyeksportowano plik HTML.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    okno = NowoczesnyEdytor()
    # Dwuklik na pliku .mked w Eksploratorze: Windows przekazuje ścieżkę jako argument
    if len(sys.argv) > 1 and os.path.isfile(sys.argv[1]):
        okno.wczytaj_plik(sys.argv[1])
    okno.showMaximized()
    # Sprawdzenie skojarzenia .mked dopiero po pokazaniu okna
    QTimer.singleShot(500, okno.sprawdz_skojarzenie)
    sys.exit(app.exec())