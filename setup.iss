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
PrivilegesRequired=admin ; Requiere privilegios de administrador para instalar en "Archivos de programa"

[Files]
; Archivos que se incluirán en el instalador
; Asegúrate de que la ruta de 'Source' es correcta
Source: "build\exe.win-amd64-3.12\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Tasks]
; Opciones adicionales durante la instalación
Name: "desktopicon"; Description: "Crear un acceso directo en el escritorio"; GroupDescription: "Tareas adicionales:"
Name: "startmenuicon"; Description: "Agregar un acceso directo al menú Inicio"; GroupDescription: "Tareas adicionales:"

[Icons]
; Accesos directos en el menú Inicio y escritorio
Name: "{group}\Odin"; Filename: "{app}\Odin.exe"; IconFilename: "{app}\img\logo.ico"
Name: "{userdesktop}\Odin"; Filename: "{app}\Odin.exe"; Tasks: desktopicon; IconFilename: "{app}\img\logo.ico"
Name: "{commonprograms}\Odin"; Filename: "{app}\Odin.exe"; Tasks: startmenuicon; IconFilename: "{app}\img\logo.ico"

[Run]
; Ejecutar la aplicación después de la instalación
Filename: "{app}\Odin.exe"; Description: "Ejecutar Odin ahora"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Borrar todos los archivos y directorios al desinstalar
Type: filesandordirs; Name: "{app}"
