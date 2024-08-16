[Setup]
; Información básica del instalador
AppName=Validador gesiapp
AppVersion=1.0
DefaultDirName={pf}\Validador_Gesiapp
DefaultGroupName=Validador_Gesiapp
OutputBaseFilename=ValidadorGesiInstaller
OutputDir=D:\Perfil\Documentos\validatorsGesi
Compression=lzma
SolidCompression=yes
SetupIconFile=D:\Perfil\Documentos\validatorsGesi\img\logo.ico

[Files]
; Archivos que se incluirán en el instalador
Source: "build\exe.win-amd64-3.12\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "install_dependencies.bat"; DestDir: "{tmp}"; Flags: deleteafterinstall

[Tasks]
; Opciones adicionales durante la instalación
Name: "desktopicon"; Description: "Crear un acceso directo en el escritorio"; GroupDescription: "Tareas adicionales:"

[Icons]
; Accesos directos en el menú de inicio
Name: "{group}\Validador_Gesiapp"; Filename: "{app}\Validador_gesi.exe"; IconFilename: "{app}\img\logo.ico"
; Acceso directo en el escritorio (solo si se selecciona la tarea 'desktopicon')
Name: "{userdesktop}\Validador_Gesiapp"; Filename: "{app}\Validador_gesi.exe"; Tasks: desktopicon; IconFilename: "{app}\img\logo.ico"

[Run]
; Ejecutar la aplicación después de la instalación
Filename: "{app}\Validador_gesi.exe"; Description: "Ejecutar Validador_Gesiapp"; Flags: nowait postinstall skipifsilent
; Ejecutar el script de instalación de dependencias
Filename: "{tmp}\install_dependencies.bat"; Parameters: ""; Flags: runhidden

[UninstallDelete]
; Borrar archivos al desinstalar
Type: filesandordirs; Name: "{app}"
