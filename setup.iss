[Setup]
AppName=Odin
AppVersion=1.0
DefaultDirName={autopf}\Odin
DefaultGroupName=Odin
OutputDir=dist
OutputBaseFilename=OdinInstaller
Compression=lzma
SolidCompression=yes
PrivilegesRequired=admin
SetupIconFile=logo.ico
WizardStyle=modern
DisableProgramGroupPage=yes
LicenseFile=license.txt

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[CustomMessages]
spanish.LicenseAccepted=Acepto los términos de la licencia
spanish.LicenseNotAccepted=No acepto los términos

[WelcomePage]
WelcomeLabel1=Bienvenido al instalador de Odin
WelcomeLabel2=Este asistente instalará Odin en su computadora.%n%nSe recomienda cerrar otras aplicaciones antes de continuar.

[Files]
Source: "dist\Odin.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\index.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "logo.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "img\*"; DestDir: "{app}\img"; Flags: ignoreversion recursesubdirs
Source: "areas.json"; DestDir: "{app}"; Flags: ignoreversion
Source: "crear_hc\*"; DestDir: "{app}\crear_hc"; Flags: ignoreversion recursesubdirs
Source: "crc_princ\*"; DestDir: "{app}\crc_princ"; Flags: ignoreversion recursesubdirs
Source: "version.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "error_log.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "__version__.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\Gesi-Educativo\AppData\Local\Programs\Python\Python312\Lib\site-packages\customtkinter\*"; DestDir: "{app}\customtkinter"; Flags: ignoreversion recursesubdirs

[Icons]
Name: "{autoprograms}\Odin"; Filename: "{app}\Odin.exe"; IconFilename: "{app}\logo.ico"
Name: "{userdesktop}\Odin"; Filename: "{app}\Odin.exe"; IconFilename: "{app}\logo.ico"

[Run]
Filename: "{app}\Odin.exe"; Description: "Abrir Odin ahora"; Flags: nowait postinstall skipifsilent

[Code]
procedure InitializeWizard();
begin
  // Personalizar colores del wizard
  WizardForm.Color := clWhite;
  WizardForm.MainPanel.Color := clWhite;
  
  // Personalizar fuentes
  WizardForm.WelcomeLabel1.Font.Style := [fsBold];
  WizardForm.WelcomeLabel1.Font.Size := 12;
  WizardForm.WelcomeLabel2.Font.Size := 10;
  WizardForm.WelcomeLabel2.Font.Color := clGray;
  
  WizardForm.LicenseMemo.Font.Name := 'Arial';
  WizardForm.LicenseMemo.Font.Size := 9;
  
  // Textos de licencia en español
  WizardForm.LicenseAcceptedRadio.Caption := ExpandConstant('{cm:LicenseAccepted}');
  WizardForm.LicenseNotAcceptedRadio.Caption := ExpandConstant('{cm:LicenseNotAccepted}');
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
  
  // Validar aceptación de licencia
  if CurPageID = wpLicense then
  begin
    if not WizardForm.LicenseAcceptedRadio.Checked then
    begin
      MsgBox('Debe aceptar los términos de la licencia para continuar.', mbError, MB_OK);
      Result := False;
    end;
  end;
end;