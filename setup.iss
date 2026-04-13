; ═══════════════════════════════════════════════════════════════════════════════
;  ValidatorsGesi – Inno Setup Script (Optimizado para Auto-Update)
; ═══════════════════════════════════════════════════════════════════════════════

#define MyAppName        "Odin"
#define MyAppVersion     "1.0.1"
#define MyAppPublisher   "Gabriel Monhabell - Aramis Garcia"
#define MyAppURL         "https://github.com/argg9822/validatorsGesi"
#define MyAppExeName     "Odin.exe"
#define MySourceDir      "dist"

[Setup]
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}

; --- CAMBIO CLAVE: Instalación por usuario para permitir Auto-Update ---
DefaultDirName={userappdata}\{#MyAppName}
PrivilegesRequired=lowest
; -----------------------------------------------------------------------

DefaultGroupName={#MyAppName}
AllowNoIcons=yes
SetupIconFile=img\logo.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
Compression=lzma2/ultra64
SolidCompression=yes
OutputDir=output_installer
OutputBaseFilename=ValidatorGesiApp_Setup_v{#MyAppVersion}
WizardStyle=modern

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "Crear acceso directo en el &Escritorio"; GroupDescription: "Iconos adicionales:"

[Files]
; Ejecutable principal
Source: "{#MySourceDir}\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

; Archivos base necesarios para el Updater y ejecución
Source: "index.py";         DestDir: "{app}"; Flags: ignoreversion
Source: "__version__.py";   DestDir: "{app}"; Flags: ignoreversion
Source: "version.txt";       DestDir: "{app}"; Flags: ignoreversion

; Carpeta de crear_hc (La que mencionaste que daba problemas)
Source: "crear_hc\*";        DestDir: "{app}\crear_hc"; Flags: ignoreversion recursesubdirs createallsubdirs

; Carpeta de validadores
Source: "validadores\*";     DestDir: "{app}\validadores"; Flags: ignoreversion recursesubdirs createallsubdirs

; Imágenes
Source: "img\*";             DestDir: "{app}\img"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{userprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\img\logo.ico"
Name: "{userdesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\img\logo.ico"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Iniciar {#MyAppName}"; Flags: nowait postinstall skipifsilent

[Code]
// Forzamos que version.txt siempre tenga la versión instalada inicialmente
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    SaveStringToFile(ExpandConstant('{app}\version.txt'), '{#MyAppVersion}', False);
  end;
end;