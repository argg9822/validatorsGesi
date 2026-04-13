; ═══════════════════════════════════════════════════════════════════════════════
;  ValidatorsGesi  –  Inno Setup Script
;  Genera el instalador .exe que distribuyes a los usuarios.
;
;  REQUISITOS PREVIOS (correr antes de compilar este .iss):
;    1. pip install pyinstaller
;    2. pyinstaller --onefile --windowed --icon=img\logo.ico Odin.py
;       (esto genera dist\Odin.exe)
;    3. Abre este .iss con Inno Setup Compiler y pulsa Compile.
;
;  IMPORTANTE: ajusta MyAppVersion cada vez que publiques una versión nueva.
;  Ese número debe coincidir con __version__.py del repositorio.
; ═══════════════════════════════════════════════════════════════════════════════

#define MyAppName        "Validador GesiApp"
#define MyAppVersion     "1.0.1"
#define MyAppPublisher   "Gabriel Monhabell - Aramis Garcia"
#define MyAppURL         "https://github.com/Monhabell/validatorsGesi"
#define MyAppExeName     "Odin.exe"
#define MySourceDir      "dist"

; ── Sección principal ─────────────────────────────────────────────────────────
[Setup]
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

; Directorio de instalación
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes

; Ícono del instalador y del desinstalador
SetupIconFile=img\logo.ico
UninstallDisplayIcon={app}\{#MyAppExeName}

; Compresión máxima
Compression=lzma2/ultra64
SolidCompression=yes
CompressionThreads=auto

; Arquitectura
ArchitecturesInstallIn64BitMode=x64compatible

; El instalador requiere privilegios de administrador para escribir en Archivos de programa
PrivilegesRequired=admin

; Archivo de salida
OutputDir=output_installer
OutputBaseFilename=ValidatorGesiApp_Setup_v{#MyAppVersion}

; Mostrar licencia (opcional – comenta si no tienes archivo de licencia)
; LicenseFile=LICENSE.txt

; Wizard moderno
WizardStyle=modern


; ── Idioma ────────────────────────────────────────────────────────────────────
[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"


; ── Archivos a instalar ───────────────────────────────────────────────────────
[Files]
; ── Ejecutable principal (generado por PyInstaller) ──────────────────────────
Source: "{#MySourceDir}\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

; ── Carpetas de código fuente Python (para que el auto-updater pueda reemplazarlas) ──
; El ejecutable Odin.exe descarga .py actualizados de GitHub y los escribe aquí.
; Por eso instalamos también los .py — la app los importa en runtime.
Source: "index.py";            DestDir: "{app}"; Flags: ignoreversion
Source: "__version__.py";      DestDir: "{app}"; Flags: ignoreversion
Source: "version.txt";         DestDir: "{app}"; Flags: ignoreversion

; Carpeta de validadores (módulos Python)
Source: "validadores\*";       DestDir: "{app}\validadores"; \
    Flags: ignoreversion recursesubdirs createallsubdirs

; Imágenes e íconos
Source: "img\*";               DestDir: "{app}\img"; \
    Flags: ignoreversion recursesubdirs createallsubdirs

; Dependencias Python necesarias en tiempo de ejecución
; (requests, colorama, Pillow, customtkinter — ya están embebidas en el .exe
;  gracias a PyInstaller, pero las listamos aquí por si se usa el modo script)


; ── Accesos directos ──────────────────────────────────────────────────────────
[Icons]
; Menú Inicio
Name: "{group}\{#MyAppName}";       Filename: "{app}\{#MyAppExeName}"; \
    IconFilename: "{app}\img\logo.ico"
Name: "{group}\Desinstalar {#MyAppName}"; \
    Filename: "{uninstallexe}"

; Acceso directo en el Escritorio (el usuario puede elegir no crearlo)
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; \
    IconFilename: "{app}\img\logo.ico"; \
    Tasks: desktopicon


; ── Tareas opcionales ─────────────────────────────────────────────────────────
[Tasks]
Name: "desktopicon"; \
    Description: "Crear acceso directo en el &Escritorio"; \
    GroupDescription: "Iconos adicionales:"


; ── Ejecutar al finalizar la instalación ──────────────────────────────────────
[Run]
Filename: "{app}\{#MyAppExeName}"; \
    Description: "Iniciar {#MyAppName}"; \
    Flags: nowait postinstall skipifsilent


; ── Código Pascal: verifica que exista version.txt al instalar ───────────────
[Code]
procedure CurStepChanged(CurStep: TSetupStep);
var
  VersionFile: string;
  VersionContent: string;
begin
  if CurStep = ssPostInstall then
  begin
    VersionFile := ExpandConstant('{app}\version.txt');
    if not FileExists(VersionFile) then
    begin
      VersionContent := '{#MyAppVersion}';
      SaveStringToFile(VersionFile, VersionContent, False);
    end;
  end;
end;
