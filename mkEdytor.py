import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTextEdit, QToolBar,
                             QComboBox, QSpinBox, QColorDialog, QFileDialog,
                             QMessageBox)
from PyQt6.QtGui import (QFont, QAction, QFontDatabase, QTextListFormat,
                         QKeySequence, QIcon, QTextDocumentWriter, QPdfWriter,
                         QPageSize, QDesktopServices, QTextCharFormat)
from PyQt6.QtCore import Qt, QUrl, QStandardPaths
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog


# --- FUNKCJA DO OBSŁUGI ŚCIEŻEK W PLIKU .EXE ---
def sciezka_zasobu(wzgledna_sciezka):
    try:
        baza = sys._MEIPASS
    except Exception:
        baza = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(baza, wzgledna_sciezka)


class NowoczesnyEdytor(QMainWindow):

    # Wersja jako stała klasy
    WERSJA = "1.0.2.0"

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"mkEdytor v{self.WERSJA} - Nowy dokument")
        self.resize(1000, 700)

        self.setWindowIcon(QIcon(sciezka_zasobu("ikona.ico")))

        self.pulpit = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DesktopLocation)
        self.ostatni_katalog = self.pulpit

        self.aktualny_plik = None

        # Flaga śledzenia niezapisanych zmian
        self.zmodyfikowany = False

        self.edytor = QTextEdit()
        domyslna_czcionka = QFont("Arial", 18)
        self.edytor.setFont(domyslna_czcionka)
        self.edytor.setStyleSheet("QTextEdit { padding: 20px; border: none; }")
        self.setCentralWidget(self.edytor)

        self.stworz_menu()
        self.stworz_pasek_narzedzi()

        self.edytor.textChanged.connect(self.utrzymaj_formatowanie)
        self.edytor.textChanged.connect(self._oznacz_jako_zmodyfikowany)
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

    def _oznacz_jako_zmodyfikowany(self):
        if not self.zmodyfikowany:
            self.zmodyfikowany = True
            self._aktualizuj_tytul()

    def _aktualizuj_tytul(self):
        if self.aktualny_plik:
            nazwa = self.aktualny_plik
        else:
            nazwa = "Nowy dokument"
        prefiks = "* " if self.zmodyfikowany else ""
        self.setWindowTitle(f"{prefiks}mkEdytor v{self.WERSJA} - {nazwa}")
        
    def _czy_html(self, sciezka):
        return os.path.splitext(sciezka)[1].lower() in ('.html', '.htm')

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
        akcja_zapisz_jako.setShortcut(QKeySequence.StandardKey.SaveAs)
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

        akcja_eksport_pdf = QAction("Wyeksportuj do PDF", self)
        akcja_eksport_pdf.triggered.connect(self.eksportuj_pdf)
        menu_plik.addAction(akcja_eksport_pdf)

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
        self.lista_czcionek.setCurrentText("Arial")
        self.lista_czcionek.currentTextChanged.connect(self.zmien_czcionke)
        pasek.addWidget(self.lista_czcionek)

        self.rozmiar_czcionki = QSpinBox()
        self.rozmiar_czcionki.setRange(8, 72)
        self.rozmiar_czcionki.setValue(18)
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
        kolor = QColorDialog.getColor()
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
        self.utrzymaj_formatowanie()
        self.aktualny_plik = None
        self.zmodyfikowany = False
        self._aktualizuj_tytul()

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
            "Pliki z formatowaniem (*.html);;Zwykły tekst (*.txt);;Wszystkie pliki (*.*)"
        )
        if sciezka:
            self.ostatni_katalog = os.path.dirname(sciezka)
            zawartosc = self._czytaj_plik(sciezka)
            if zawartosc is None:
                return 
            if self._czy_html(sciezka):
                self.edytor.setHtml(zawartosc)
            else:
                self.edytor.setPlainText(zawartosc)
            self.aktualny_plik = sciezka
            self.zmodyfikowany = False
            self._aktualizuj_tytul()

    def _czytaj_plik(self, sciezka):
        # Lista popularnych kodowań (od najczęstszych po regionalne)
        kodowania = ["utf-8-sig", "utf-8", "windows-1250", "iso-8859-2", "cp1252"]

        for kodowanie in kodowania:
            try:
                with open(sciezka, "r", encoding=kodowanie) as plik:
                    zawartosc = plik.read()
                    
                    # Ostrzegamy użytkownika, jeśli użyto kodowania innego niż warianty UTF-8
                    if kodowanie not in ["utf-8", "utf-8-sig"]:
                        QMessageBox.information(
                            self, "Informacja o kodowaniu",
                            f"Plik został pomyślnie wczytany z użyciem kodowania: {kodowanie}.\n\n"
                            "Podczas ewentualnego zapisu z poziomu programu, plik zostanie zachowany jako standardowy UTF-8."
                        )
                    return zawartosc
            except UnicodeDecodeError:
                continue
            except Exception as e:
                QMessageBox.critical(self, "Błąd", f"Nie udało się otworzyć pliku:\n{e}")
                return None

        # Awaryjne wczytywanie, jeśli żadne znane kodowanie z listy nie podołało (podmieniamy nieznane znaki)
        try:
            with open(sciezka, "r", encoding="utf-8", errors="replace") as plik:
                zawartosc = plik.read()
            QMessageBox.warning(
                self, "Ostrzeżenie kodowania",
                "Plik zawiera znaki niemożliwe do prawidłowego zdekodowania przez program.\n"
                "Nieznane znaki zostały zastąpione znakiem '?'."
            )
            return zawartosc
        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Nie udało się otworzyć pliku:\n{e}")
            return None

    def zapisz_plik(self):
        if self.aktualny_plik:
            self.zapisz_na_dysk(self.aktualny_plik)
        else:
            self.zapisz_jako()

    def zapisz_jako(self):
        sciezka, _ = QFileDialog.getSaveFileName(
            self, "Zapisz jako", self.ostatni_katalog,
            "Plik z formatowaniem (*.html);;Zwykły tekst (*.txt)"
        )
        if sciezka:
            self.ostatni_katalog = os.path.dirname(sciezka)
            self.aktualny_plik = sciezka
            self.zapisz_na_dysk(sciezka)

    def zapisz_na_dysk(self, sciezka):
        try:
            tresc = self.edytor.toHtml() if self._czy_html(sciezka) else self.edytor.toPlainText()
            tmp = sciezka + ".tmp"
            
            with open(tmp, 'w', encoding='utf-8') as f:
                f.write(tresc)
                f.flush()
                os.fsync(f.fileno())
                
            os.replace(tmp, sciezka)
            self.zmodyfikowany = False
            self._aktualizuj_tytul()
            return True
        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Nie udało się zapisać pliku:\n{e}")
            return False

    def drukuj_plik(self):
        drukarka = QPrinter(QPrinter.PrinterMode.HighResolution)
        okno_druku = QPrintDialog(drukarka, self)
        if okno_druku.exec():
            self.edytor.document().print(drukarka)

    def eksportuj_odt(self):
        sciezka, _ = QFileDialog.getSaveFileName(
            self, "Eksportuj do ODT", self.ostatni_katalog,
            "Plik LibreOffice Writer (*.odt)"
        )
        if sciezka:
            try:
                writer = QTextDocumentWriter(sciezka)
                if writer.write(self.edytor.document()):
                    QMessageBox.information(self, "Sukces", "Pomyślnie wyeksportowano plik ODT.")
                else:
                    QMessageBox.critical(
                        self, "Błąd eksportu",
                        "Nie udało się zapisać pliku ODT.\n"
                        "Sprawdź, czy masz uprawnienia do zapisu w wybranej lokalizacji."
                    )
            except Exception as e:
                QMessageBox.critical(self, "Błąd", f"Błąd eksportu ODT:\n{e}")

    def eksportuj_pdf(self):
        sciezka, _ = QFileDialog.getSaveFileName(
            self, "Eksportuj do PDF", self.ostatni_katalog,
            "Pliki PDF (*.pdf)"
        )
        if sciezka:
            try:
                pdf_writer = QPdfWriter(sciezka)
                pdf_writer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
                self.edytor.document().print(pdf_writer)
                QMessageBox.information(self, "Sukces", "Pomyślnie wyeksportowano plik PDF.")
            except Exception as e:
                QMessageBox.critical(self, "Błąd", f"Błąd eksportu PDF:\n{e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    okno = NowoczesnyEdytor()
    okno.showMaximized()
    sys.exit(app.exec())