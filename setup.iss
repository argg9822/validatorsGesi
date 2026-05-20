; ═══════════════════════════════════════════════════════════════════════
;  Odin - Instalador Profesional (Nuitka Standalone)
; ═══════════════════════════════════════════════════════════════════════

#define MyAppName        "Odin"
#define MyAppVersion     "1.0.1"
#define MyAppPublisher   "Gabriel Monhabell - Aramis Garcia"
#define MyAppURL         "https://github.com/argg9822/validatorsGesi"
#define MyAppExeName     "Odin.exe"

; Carpeta generada por Nuitka
#define MySourceDir      "build\Odin.dist"

[Setup]

AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}

AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}

AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

; Instala en AppData
DefaultDirName={userappdata}\{#MyAppName}

DefaultGroupName={#MyAppName}

AllowNoIcons=yes

; SIN ADMIN
PrivilegesRequired=lowest

; Compatibilidad
ArchitecturesInstallIn64BitMode=x64compatible

; Salida instalador
OutputDir=output_installer
OutputBaseFilename=Odin_Setup_v{#MyAppVersion}

; Compresión
Compression=lzma2/ultra64
SolidCompression=yes

WizardStyle=modern

; Icono instalador
SetupIconFile=logo.ico

; Icono desinstalador
UninstallDisplayIcon={app}\{#MyAppExeName}

; Mejoras
DisableProgramGroupPage=yes
CloseApplications=yes
CloseApplicationsFilter=Odin.exe
RestartApplications=no

; ═══════════════════════════════════════════════════════════════════════
; Idioma
; ═══════════════════════════════════════════════════════════════════════

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

; ═══════════════════════════════════════════════════════════════════════
; Tareas
; ═══════════════════════════════════════════════════════════════════════

[Tasks]

Name: "desktopicon"; \
Description: "Crear acceso directo en el escritorio"; \
GroupDescription: "Opciones adicionales:"

; ═══════════════════════════════════════════════════════════════════════
; Archivos
; ═══════════════════════════════════════════════════════════════════════

[Files]

; Copiar TODO Nuitka
Source: "{#MySourceDir}\*"; \
DestDir: "{app}"; \
Flags: ignoreversion recursesubdirs createallsubdirs

; ═══════════════════════════════════════════════════════════════════════
; Accesos directos
; ═══════════════════════════════════════════════════════════════════════

[Icons]

Name: "{group}\{#MyAppName}"; \
Filename: "{app}\{#MyAppExeName}"; \
WorkingDir: "{app}"; \
IconFilename: "{app}\{#MyAppExeName}"

Name: "{autodesktop}\{#MyAppName}"; \
Filename: "{app}\{#MyAppExeName}"; \
WorkingDir: "{app}"; \
IconFilename: "{app}\{#MyAppExeName}"; \
Tasks: desktopicon

; ═══════════════════════════════════════════════════════════════════════
; Ejecutar al finalizar
; ═══════════════════════════════════════════════════════════════════════

[Run]

Filename: "{app}\{#MyAppExeName}"; \
Description: "Iniciar {#MyAppName}"; \
Flags: nowait postinstall skipifsilent

; ═══════════════════════════════════════════════════════════════════════
; Registro
; ═══════════════════════════════════════════════════════════════════════

[Registry]

Root: HKCU; \
Subkey: "Software\{#MyAppName}"; \
ValueType: string; \
ValueName: "InstallPath"; \
ValueData: "{app}"; \
Flags: uninsdeletekey

; ═══════════════════════════════════════════════════════════════════════
; Código personalizado
; ═══════════════════════════════════════════════════════════════════════

[Code]

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin

    SaveStringToFile(
      ExpandConstant('{app}\version.txt'),
      '{#MyAppVersion}',
      False
    );

    SaveStringToFile(
      ExpandConstant('{app}\__version__.py'),
      '__version__ = "{#MyAppVersion}"',
      False
    );

  end;
end;

function InitializeUninstall(): Boolean;
var
  ResultCode: Integer;
begin

  ShellExec(
    'open',
    'taskkill.exe',
    '/F /T /IM {#MyAppExeName}',
    '',
    SW_HIDE,
    ewWaitUntilTerminated,
    ResultCode
  );

  Result := True;
end;