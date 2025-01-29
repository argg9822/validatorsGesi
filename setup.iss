[Setup]
AppName=Odin2
AppVersion=1.0
DefaultDirName={autopf}\Odin2
OutputDir=dist
OutputBaseFilename=Odin2
Compression=lzma
SolidCompression=yes
PrivilegesRequired=admin
SetupIconFile=logo.ico
WizardStyle=modern

[Files]
Source: "dist\Odin.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "logo.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "img\*"; DestDir: "{app}\img"; Flags: ignoreversion recursesubdirs
Source: "areas.json"; DestDir: "{app}"; Flags: ignoreversion
Source: "bases.json"; DestDir: "{app}"; Flags: ignoreversion
Source: "crear_hc\*"; DestDir: "{app}\crear_hc"; Flags: ignoreversion recursesubdirs
Source: "validadores\*"; DestDir: "{app}\validadores"; Flags: ignoreversion recursesubdirs
Source: "version.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "index.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "error_log.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "__version__.py"; DestDir: "{app}"; Flags: ignoreversion


[Icons]
Name: "{autoprograms}\Odin"; Filename: "{app}\Odin.exe"

[Run]
Filename: "{app}\Odin.exe"; Description: "{cm:LaunchProgram,TuAplicacion}"; Flags: nowait postinstall skipifsilent


[Code]
function InitializeSetup(): Boolean;
begin
  Result := True;
end;