# mkEdytor ✍️

**mkEdytor** to prosty w obsłudze edytor tekstu, stworzony z myślą o dzieciach klas 1-3 oraz celach edukacyjnych. Program jest idealnym narzędziem dla uczniów stawiających pierwsze kroki w nauce pisania i formatowania dokumentów na komputerze.
Pobierz: [Releases](https://github.com/StaryDooh/mkEdytor/releases/)

## ✨ Najważniejsze funkcje

* **Przyjazny interfejs:** Duże, intuicyjne ikony i przejrzysty układ menu.
* **Pełne formatowanie:**
    * Wybór czcionki i płynna zmiana rozmiaru tekstu.
    * Zmiana koloru czcionki (🎨).
    * Style tekstu: pogrubienie, pochylenie i podkreślenie.
* **Listy i akapity:**
    * Obsługa list punktowanych i numerowanych (z poprawionym formatowaniem znaków wypunktowania).
    * Wyrównywanie tekstu: do lewej, do prawej, środkowanie oraz justowanie.
* **Własny format dokumentów `.mked`:** Praca jest zapisywana razem z całym formatowaniem w pliku `.mked`. Dzięki temu dziecko nie straci przypadkiem kolorów i pogrubień, wybierając zły format zapisu.
* **Eksport dokumentów** (menu *Plik*):
    * `.odt` (standard LibreOffice / OpenOffice)
    * `.html` (strona internetowa)
    * `.pdf` (dokument gotowy do wydruku)
* **Import starszych plików:** Pliki `.html` i `.txt` (np. zapisane w wersjach 1.x) można otworzyć poleceniem *Plik → Otwórz*. Oryginał nie jest nadpisywany – po zapisaniu powstaje nowy dokument `.mked`.
* **Integracja z systemem:** mkEdytor jest domyślnym programem dla plików `.mked` – wystarczy dwukrotnie kliknąć dokument, aby go otworzyć. Jeśli pliki `.mked` otwierają się w innym programie, mkEdytor przy starcie zaproponuje naprawę (można to też zrobić w menu *Plik → Otwieraj pliki .mked w mkEdytorze*).

## 🚀 Instalacja i uruchomienie

Program jest udostępniany w formie wygodnego instalatora dla systemu Windows.

1. Przejdź do zakładki [Releases](https://github.com/StaryDooh/mkEdytor/releases/) w tym repozytorium.
2. Pobierz najnowszy plik `Setup_mkEdytor_vX.X.X.X.exe`.
3. Uruchom instalator i postępuj zgodnie z instrukcjami na ekranie (może być wymagane uruchomienie z uprawnieniami administratora).
4. Po instalacji skrót do programu pojawi się w Menu Start (oraz na pulpicie, jeśli zaznaczysz tę opcję).

**Aktualizacja z wersji 1.x:** wystarczy zainstalować nową wersję na starą. Instalator usuwa skojarzenia mkEdytora z plikami `.txt` i `.html` – będą się one znowu otwierać w programach domyślnych systemu (np. Notatniku i przeglądarce).

**Dla nauczycieli - instalacja nienadzorowana**

* Instalacja:

```
Setup_mkEdytor_vX.X.X.X.exe /VERYSILENT /SUPPRESSMSGBOXES /NORESTART
```

* Deinstalacja:

```
"C:\Program Files (x86)\mkEdytor\unins000.exe" /VERYSILENT /SUPPRESSMSGBOXES
```

## 📄 Format pliku `.mked`

Dokument `.mked` to zwykły plik tekstowy UTF-8 w formacie JSON:

```json
{
 "format": "mkEdytor",
 "wersja_formatu": 1,
 "program": "mkEdytor 2.0.7.0",
 "tresc": "<!DOCTYPE HTML ...>"
}
```

Pole `tresc` zawiera dokument w postaci HTML (Qt Rich Text). Pole `wersja_formatu` pozwala rozwijać format w przyszłych wersjach programu bez utraty zgodności ze starszymi dokumentami.

## 💻 Wymagania systemowe

* **System operacyjny:** Windows 10 lub Windows 11 (64-bit).
* **Miejsce na dysku:** ok. 50 MB.

## 📜 Licencja i warunki użytkowania

Program **mkEdytor** jest udostępniany jako oprogramowanie darmowe (**Freeware**) wyłącznie do użytku edukacyjnego i niekomercyjnego.

**Ważne:** Przed instalacją i rozpoczęciem korzystania z oprogramowania, każdy użytkownik ma obowiązek zapoznać się z pełną treścią dokumentu **LICENSE** (EULA) dołączonego do programu i dostępnego w tym repozytorium. Instalacja programu oznacza akceptację wszystkich warunków licencyjnych.


## 👤 Autor
**Krzysztof Markowski**
Jeśli masz pytania lub chcesz zgłosić błąd, możesz skontaktować się ze mną poprzez https://github.com/StaryDooh/mkEdytor/issues/ (duży zielony przycisk "New issue" lub "Otwórz zgłoszenie").

---
*Program dostarczany w stanie "takim, w jakim jest" (as is).*

_______________________
Krzysztof Markowski
https://www.youtube.com/@StaryDooh
