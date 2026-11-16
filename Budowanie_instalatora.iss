; Numer wersji jest odczytywany z pliku wersja.txt (ten sam plik PyInstaller wbudowuje w mkEdytor.exe).
; Numer wersji zmieniasz w dwóch miejscach: w wersja.txt oraz w stałej WERSJA w mkEdytor.py.

#define PlikWersji AddBackslash(SourcePath) + "wersja.txt"
#define Znacznik "u'FileVersion', u'"
#define MyAppVersion ""
#define UchwytPliku 0
#define Reszta ""

#if !FileExists(PlikWersji)
  #error Nie znaleziono pliku wersja.txt obok skryptu .iss
#endif

; Szuka linii: StringStruct(u'FileVersion', u'X.X.X.X') i wycina z niej numer wersji.
; UWAGA: #define wewnątrz #sub tworzy zmienną LOKALNĄ – dlatego zmienne globalne
; (Reszta, MyAppVersion) zmieniamy przypisaniem w #expr.
#sub SzukajWersji
  #define Linia FileRead(UchwytPliku)
  #if Len(MyAppVersion) == 0
    #if Pos(Znacznik, Linia) > 0
      #expr Reszta = Copy(Linia, Pos(Znacznik, Linia) + Len(Znacznik), 100)
      #expr MyAppVersion = Copy(Reszta, 1, Pos("'", Reszta) - 1)
    #endif
  #endif
#endsub

#expr UchwytPliku = FileOpen(PlikWersji)
#if UchwytPliku == 0
  #error Nie mozna otworzyc pliku wersja.txt
#endif
#for {0; !FileEof(UchwytPliku); 0} SzukajWersji
#expr FileClose(UchwytPliku)

#if Len(MyAppVersion) == 0
  #error Nie znaleziono numeru wersji (FileVersion) w pliku wersja.txt
#endif
#pragma message "Wersja mkEdytora (z wersja.txt): " + MyAppVersion


[Setup]
; Stały identyfikator programu – NIE ZMIENIAĆ (inaczej aktualizacje przestaną działać)
AppId={{6DCABD0D-3D80-4A72-8AAE-CB3B0F2A0189}

AppName=mkEdytor
AppVersion={#MyAppVersion}
AppPublisher=Krzysztof Markowski

; Domyślny folder instalacji (Program Files)
DefaultDirName={autopf}\mkEdytor
DefaultGroupName=mkEdytor
PrivilegesRequired=admin

; Plik licencji
LicenseFile=Licencja.txt

; Ikony instalatora i deinstalatora
SetupIconFile=ikona.ico
UninstallDisplayIcon={app}\ikona.ico

; Gdzie ma się zapisać gotowy instalator i jak ma się nazywać
OutputDir=.\GitHub
OutputBaseFilename=Setup_mkEdytor_v{#MyAppVersion}

; Najlepsza kompresja, żeby plik ważył jak najmniej
Compression=lzma
SolidCompression=yes

; Ułatwia aktualizację (próbuje zamknąć mkEdytor, jeśli jest włączony)
CloseApplications=yes

; Informuje system Windows, że instalator zmienia skojarzenia plików
ChangesAssociations=yes

[Languages]
Name: "pl"; MessagesFile: "compiler:Languages\Polish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
; Cała zawartość folderu dist\mkEdytor (mkEdytor.exe + folder _internal)
Source: "dist\mkEdytor\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; Dodatkowe pliki leżące obok skryptu .iss
Source: "Licencja.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "ikona.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Tworzenie skrótów w Menu Start i na Pulpicie
Name: "{autoprograms}\mkEdytor"; Filename: "{app}\mkEdytor.exe"; IconFilename: "{app}\ikona.ico"
Name: "{autodesktop}\mkEdytor"; Filename: "{app}\mkEdytor.exe"; IconFilename: "{app}\ikona.ico"; Tasks: desktopicon

[Registry]
; --- mkEdytor jako domyślny program dla plików .mked ---
; Typ pliku (ProgID): nazwa, ikona i polecenie otwierania
Root: HKA; Subkey: "Software\Classes\mkEdytor.dokument"; ValueType: string; ValueName: ""; ValueData: "Dokument mkEdytor"; Flags: uninsdeletekey
Root: HKA; Subkey: "Software\Classes\mkEdytor.dokument\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: """{app}\mkEdytor.exe"",0"
Root: HKA; Subkey: "Software\Classes\mkEdytor.dokument\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\mkEdytor.exe"" ""%1"""

; Rozszerzenie .mked wskazuje na typ pliku mkEdytor.dokument
Root: HKA; Subkey: "Software\Classes\.mked"; ValueType: string; ValueName: ""; ValueData: "mkEdytor.dokument"; Flags: uninsdeletevalue uninsdeletekeyifempty
Root: HKA; Subkey: "Software\Classes\.mked\OpenWithProgids"; ValueType: string; ValueName: "mkEdytor.dokument"; ValueData: ""; Flags: uninsdeletevalue uninsdeletekeyifempty

; Program na liście „Otwórz za pomocą”
Root: HKA; Subkey: "Software\Classes\Applications\mkEdytor.exe"; ValueType: string; ValueName: "FriendlyAppName"; ValueData: "mkEdytor"; Flags: uninsdeletekey
Root: HKA; Subkey: "Software\Classes\Applications\mkEdytor.exe\SupportedTypes"; ValueType: string; ValueName: ".mked"; ValueData: ""
Root: HKA; Subkey: "Software\Classes\Applications\mkEdytor.exe\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\mkEdytor.exe"" ""%1"""

; Program na liście „Aplikacje domyślne” w Ustawieniach Windows (64-bitowy widok rejestru)
Root: HKLM64; Subkey: "Software\mkEdytor\Capabilities"; ValueType: string; ValueName: "ApplicationName"; ValueData: "mkEdytor"; Flags: uninsdeletekey; Check: IsWin64
Root: HKLM64; Subkey: "Software\mkEdytor\Capabilities"; ValueType: string; ValueName: "ApplicationDescription"; ValueData: "Prosty edytor tekstu dla dzieci"; Check: IsWin64
Root: HKLM64; Subkey: "Software\mkEdytor\Capabilities\FileAssociations"; ValueType: string; ValueName: ".mked"; ValueData: "mkEdytor.dokument"; Check: IsWin64
Root: HKLM64; Subkey: "Software\RegisteredApplications"; ValueType: string; ValueName: "mkEdytor"; ValueData: "Software\mkEdytor\Capabilities"; Flags: uninsdeletevalue; Check: IsWin64

[Code]
const
  KLUCZ_WYBORU = 'Software\Microsoft\Windows\CurrentVersion\Explorer\FileExts\.mked';

{ Sprzątanie po wersjach 1.x, które kojarzyły mkEdytor z plikami .txt i .html }
procedure UsunSkojarzeniaZWersji1;
begin
  RegDeleteValue(HKLM, 'Software\Classes\.txt\OpenWithProgids', 'mkEdytor.txt');
  RegDeleteValue(HKLM, 'Software\Classes\.html\OpenWithProgids', 'mkEdytor.html');
  RegDeleteKeyIncludingSubkeys(HKLM, 'Software\Classes\mkEdytor.txt');
  RegDeleteKeyIncludingSubkeys(HKLM, 'Software\Classes\mkEdytor.html');
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    UsunSkojarzeniaZWersji1;
    { Wcześniejszy wybór „Otwórz za pomocą → Zawsze” dla .mked ma pierwszeństwo
      przed rejestracją programu – usuwamy go (dotyczy użytkownika uruchamiającego instalator). }
    RegDeleteKeyIncludingSubkeys(HKCU, KLUCZ_WYBORU);
  end;
end;

{ Przy deinstalacji usuwamy też skojarzenie zapisane przez sam program
  (opcja „Otwieraj pliki .mked w mkEdytorze”) dla bieżącego użytkownika. }
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  Wartosc: String;
begin
  if CurUninstallStep = usPostUninstall then
  begin
    RegDeleteKeyIncludingSubkeys(HKCU, 'Software\Classes\mkEdytor.dokument');
    if RegQueryStringValue(HKCU, 'Software\Classes\.mked', '', Wartosc) and (Wartosc = 'mkEdytor.dokument') then
      RegDeleteKeyIncludingSubkeys(HKCU, 'Software\Classes\.mked');
    RegDeleteKeyIncludingSubkeys(HKCU, KLUCZ_WYBORU);
  end;
end;
