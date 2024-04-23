[Setup]
AppName=Validador GesiApp
AppVersion=1.0
DefaultDirName={pf}\ValidadorGesiApp
DefaultGroupName=ValidadorGesiApp
UninstallDisplayIcon={app}\index.exe
Compression=lzma2
SolidCompression=yes

[Files]
Source: "ruta\a\tu\aplicacion\*"; DestDir: "{app}"

[Icons]
Name: "{group}\Gesiapp"; Filename: "{app}\index.exe"
