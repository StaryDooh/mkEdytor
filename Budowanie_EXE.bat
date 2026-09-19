echo [1/2] Kasowanie poprzednich exe

if exist build rd /s /q build
if exist dist rd /s /q dist

echo [1/2] Stare pliki usuniete.
echo [2/2] Rozpoczynam prace PyInstallera...

python -m PyInstaller --noconsole --icon="ikona.ico" --version-file="wersja.txt" --add-data "ikona.ico;." --add-data "lewo.png;." --add-data "srodek.png;." --add-data "prawo.png;." --add-data "justuj.png;." --add-data "l_punktowana.png;." --add-data "l_numerowana.png;." mkEdytor.py

PAUSE