; ═══════════════════════════════════════════════════════════════════════════════
;  ValidatorsGesi – Inno Setup Script (Optimizado para Auto-Update Externo)
; ═══════════════════════════════════════════════════════════════════════════════

#define MyAppName        "Odin"
#define MyAppVersion     "1.0.1"
#define MyAppPublisher   "Gabriel Monhabell - Aramis Garcia"
#define MyAppURL         "https://github.com/argg9822/validatorsGesi"
#define MyAppExeName     "Odin.exe"
#define MyUpdaterExe     "Updater.exe"
#define MySourceDir      "dist"

[Setup]
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}

; Instalación en Local AppData para evitar pedir permisos de Admin al actualizar
DefaultDirName={userappdata}\{#MyAppName}
PrivilegesRequired=lowest

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
; 1. EJECUTABLES (Los "Shells" que no cambian)
Source: "{#MySourceDir}\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#MySourceDir}\{#MyUpdaterExe}"; DestDir: "{app}"; Flags: ignoreversion

; 2. LÓGICA DINÁMICA (Lo que el Updater reemplazará)
Source: "index.py";       DestDir: "{app}"; Flags: ignoreversion
Source: "Updater.py";     DestDir: "{app}"; Flags: ignoreversion
Source: "version.txt";    DestDir: "{app}"; Flags: ignoreversion
Source: "__version__.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "areas.json";     DestDir: "{app}"; Flags: ignoreversion
Source: "bases.json";     DestDir: "{app}"; Flags: ignoreversion

; 3. CARPETAS DE RECURSOS Y COMPONENTES
Source: "crear_hc\*";     DestDir: "{app}\crear_hc"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "crc_princ\*";    DestDir: "{app}\crc_princ"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "validadores\*";  DestDir: "{app}\validadores"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "img\*";          DestDir: "{app}\img"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "validatorweb\*"; DestDir: "{app}\validatorweb"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{userprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\img\logo.ico"
Name: "{userdesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\img\logo.ico"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Iniciar {#MyAppName}"; Flags: nowait postinstall skipifsilent

[Code]
// Sincronizar versión al instalar
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    SaveStringToFile(ExpandConstant('{app}\version.txt'), '{#MyAppVersion}', False);
  end;
end;

// Cerrar Odin antes de desinstalar
function InitializeUninstall(): Boolean;
var
  ErrorCode: Integer;
begin
  ShellExec('open', 'taskkill.exe', '/f /im {#MyAppExeName}', '', SW_HIDE, ewWaitUntilTerminated, ErrorCode);
  Result := True;
end;