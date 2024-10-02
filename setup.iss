[Setup]
; Información básica del instalador
AppName=Odin
AppVersion=1.0
DefaultDirName={pf}\Odin
DefaultGroupName=Odin
OutputBaseFilename=OdinInstaller
OutputDir=D:\Perfil\Documentos\Odin
Compression=lzma
SolidCompression=yes
SetupIconFile=D:\Perfil\Documentos\validatorsGesi\img\logo.ico

[Files]
; Archivos que se incluirán en el instalador
; Asegúrate de que la ruta de 'Source' es la correcta según la estructura generada por cx_Freeze
Source: "build\exe.win-amd64-3.12\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Tasks]
; Opciones adicionales durante la instalación
Name: "desktopicon"; Description: "Crear un acceso directo en el escritorio"; GroupDescription: "Tareas adicionales:"

[Icons]
; Accesos directos en el menú de inicio
Name: "{group}\Odin"; Filename: "{app}\Odin.exe"; IconFilename: "{app}\img\logo.ico"
; Acceso directo en el escritorio (solo si se selecciona la tarea 'desktopicon')
Name: "{userdesktop}\Odin"; Filename: "{app}\Odin.exe"; Tasks: desktopicon; IconFilename: "{app}\img\logo.ico"

[Run]
; Ejecutar la aplicación después de la instalación
Filename: "{app}\Odin.exe"; Description: "Ejecutar Odin"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Borrar archivos al desinstalar
Type: filesandordirs; Name: "{app}"
