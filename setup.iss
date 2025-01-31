[Setup]
AppName=Odin
AppVersion=1.0
DefaultDirName={autopf}\OdinIstaller
OutputDir=dist
OutputBaseFilename=OdinIstaller
Compression=lzma
SolidCompression=yes
PrivilegesRequired=admin
SetupIconFile=logo.ico
WizardStyle=modern
DisableProgramGroupPage=yes
DisableReadyPage=yes


[Files]
Source: "dist\Odin.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\index.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "logo.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "img\*"; DestDir: "{app}\img"; Flags: ignoreversion recursesubdirs
Source: "areas.json"; DestDir: "{app}"; Flags: ignoreversion
Source: "crear_hc\*"; DestDir: "{app}\crear_hc"; Flags: ignoreversion recursesubdirs
Source: "version.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "index.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "analizar_exel.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "reglas.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "error_log.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "__version__.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\Gesi-Educativo\AppData\Local\Programs\Python\Python312\Lib\site-packages\customtkinter\*"; DestDir: "{app}\customtkinter"; Flags: ignoreversion recursesubdirs


[Icons]
Name: "{autoprograms}\Odin"; Filename: "{app}\Odin.exe"
Name: "{userdesktop}\Odin"; Filename: "{app}\Odin.exe"; IconFilename: "{app}\logo.ico" 

[Run]
Filename: "{app}\Odin.exe"; Description: "{cm:LaunchProgram,TuAplicacion}"; Flags: nowait postinstall skipifsilent



