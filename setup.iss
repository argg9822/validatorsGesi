[Setup]
AppName=Gesi App
AppVersion=1.0
OutputDir=output
DefaultDirName={pf}\Gesi App

[Files]
Source: "build\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs

[Icons]
Name: "{group}\Gesi App"; Filename: "{app}\splash.exe"

[Run]
Filename: "{app}\splash.exe"; Parameters: "/install"; WorkingDir: "{app}"