; ═══════════════════════════════════════════════════════════════════════════════
;  ValidatorsGesi – Inno Setup Script (Optimizado para Auto-Update)
; ═══════════════════════════════════════════════════════════════════════════════

#define MyAppName        "Odin"
#define MyAppVersion     "1.0.1"
#define MyAppPublisher   "Gabriel Monhabell - Aramis Garcia"
#define MyAppURL         "https://github.com/argg9822/validatorsGesi"
#define MyAppExeName     "Odin.exe"
#define MyUpdaterExe     "Updater.exe"
#define MySourceDir      "dist"

[Setup]
; ID único del programa (puedes generar uno nuevo o mantener este)
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}

; --- INSTALACIÓN POR USUARIO (Local AppData) ---
; Esto permite que el actualizador reemplace archivos sin pedir permisos de admin.
DefaultDirName={userappdata}\{#MyAppName}
PrivilegesRequired=lowest
; -----------------------------------------------

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
; --- EJECUTABLES PRINCIPALES (Desde carpeta dist) ---
Source: "{#MySourceDir}\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#MySourceDir}\{#MyUpdaterExe}"; DestDir: "{app}"; Flags: ignoreversion

; --- ARCHIVOS DE CONTROL DE VERSIÓN ---
; Necesarios para que el Updater compare con GitHub
Source: "version.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "__version__.py"; DestDir: "{app}"; Flags: ignoreversion

; --- CONFIGURACIONES JSON ---
Source: "areas.json"; DestDir: "{app}"; Flags: ignoreversion
Source: "bases.json"; DestDir: "{app}"; Flags: ignoreversion

; --- CARPETAS DE RECURSOS ---
; Nota: Se incluyen como respaldo aunque PyInstaller ya las lleve dentro
Source: "crear_hc\*";     DestDir: "{app}\crear_hc"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "validadores\*";  DestDir: "{app}\validadores"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "img\*";          DestDir: "{app}\img"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; Acceso directo en el menú inicio
Name: "{userprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\img\logo.ico"
; Acceso directo en el escritorio
Name: "{userdesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\img\logo.ico"; Tasks: desktopicon

[Run]
; Ejecutar el programa al finalizar la instalación
Filename: "{app}\{#MyAppExeName}"; Description: "Iniciar {#MyAppName}"; Flags: nowait postinstall skipifsilent

[Code]
// Procedimiento para asegurar que el archivo de versión local esté sincronizado
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Al instalar, creamos/sobreescribimos el version.txt con la versión del Setup
    SaveStringToFile(ExpandConstant('{app}\version.txt'), '{#MyAppVersion}', False);
  end;
end;

// Función para cerrar Odin antes de desinstalar o actualizar
function InitializeUninstall(): Boolean;
var
  ErrorCode: Integer;
begin
  ShellExec('open', 'taskkill.exe', '/f /im {#MyAppExeName}', '', SW_HIDE, ewWaitUntilTerminated, ErrorCode);
  Result := True;
end;