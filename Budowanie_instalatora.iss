#define MyAppVersion "1.0.2.0"


[Setup]
; --- BARDZO WAŻNE: Wygeneruj swój własny AppId! ---
; W Inno Setup kliknij u góry: Tools -> Generate GUID (lub Shift+Ctrl+G)
; i podmień poniższy ciąg znaków (zostaw tylko pierwszą klamrę na początku).
AppId={{6DCABD0D-3D80-4A72-8AAE-CB3B0F2A0189}

AppName=mkEdytor
AppVersion={#MyAppVersion}
AppPublisher=Krzysztof Markowski

; Domyślny folder instalacji (Program Files)
DefaultDirName={autopf}\mkEdytor
DefaultGroupName=mkEdytor
PrivilegesRequired=admin

; Plik licencji, który przygotowaliśmy
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
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: checkablealone

[Files]
; Główny plik wykonywalny pobierany z podkatalogu dist/mkEdytor
Source: "dist\mkEdytor\mkEdytor.exe"; DestDir: "{app}"; Flags: ignoreversion

; Kopiuje całą resztę z folderu dist/mkEdytor (w tym folder _internal ze wszystkimi plikami)
Source: "dist\mkEdytor\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; Dodatkowe pliki leżące obok skryptu .iss
Source: "Licencja.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "ikona.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Tworzenie skrótów w Menu Start i na Pulpicie
Name: "{autoprograms}\mkEdytor"; Filename: "{app}\mkEdytor.exe"; IconFilename: "{app}\ikona.ico"
Name: "{autodesktop}\mkEdytor"; Filename: "{app}\mkEdytor.exe"; IconFilename: "{app}\ikona.ico"; Tasks: desktopicon

[Registry]
; --- Skojarzenie plików .txt z programem mkEdytor ---
Root: HKA; Subkey: "Software\Classes\.txt\OpenWithProgids"; ValueType: string; ValueName: "mkEdytor.txt"; ValueData: ""; Flags: uninsdeletevalue
Root: HKA; Subkey: "Software\Classes\mkEdytor.txt"; ValueType: string; ValueName: ""; ValueData: "Plik tekstowy mkEdytor"; Flags: uninsdeletekey
Root: HKA; Subkey: "Software\Classes\mkEdytor.txt\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\ikona.ico,0"
Root: HKA; Subkey: "Software\Classes\mkEdytor.txt\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\mkEdytor.exe"" ""%1"""

; --- Skojarzenie plików .html z programem mkEdytor ---
Root: HKA; Subkey: "Software\Classes\.html\OpenWithProgids"; ValueType: string; ValueName: "mkEdytor.html"; ValueData: ""; Flags: uninsdeletevalue
Root: HKA; Subkey: "Software\Classes\mkEdytor.html"; ValueType: string; ValueName: ""; ValueData: "Dokument HTML mkEdytor"; Flags: uninsdeletekey
Root: HKA; Subkey: "Software\Classes\mkEdytor.html\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\ikona.ico,0"
Root: HKA; Subkey: "Software\Classes\mkEdytor.html\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\mkEdytor.exe"" ""%1"""