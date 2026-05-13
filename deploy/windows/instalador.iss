#define MyAppName "Sistema Gestao Agro"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Sistema Gestao Agro"
#define MyAppURL "http://localhost:8000"
#define MyAppDir "C:\SistemaGestaoAgro"

[Setup]
AppId={{5B1C2A4A-5F5A-4D8E-B4F4-2B2F3A8A7A10}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={#MyAppDir}
DisableDirPage=yes
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=no
OutputDir=.
OutputBaseFilename=SistemaGestaoAgroSetup
Compression=lzma
SolidCompression=yes
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64
UninstallDisplayName={#MyAppName}

[Dirs]
Name: "{app}\app"
Name: "{app}\logs"
Name: "{app}\backups"
Name: "{app}\media"

[Files]
Source: "..\..\*"; DestDir: "{app}\app"; Flags: recursesubdirs createallsubdirs ignoreversion; Excludes: ".git\*,.venv\*,venv\*,env\*,__pycache__\*,backups\*,media\*,staticfiles\*,deploy\windows\Output\*,*.pyc,*.pyo,db.sqlite3"

[Icons]
Name: "{commondesktop}\Sistema Gestao Agro"; Filename: "{#MyAppURL}"
Name: "{group}\Sistema Gestao Agro"; Filename: "{#MyAppURL}"
Name: "{group}\Iniciar servico"; Filename: "{app}\app\deploy\windows\start_service.bat"; WorkingDir: "{app}\app\deploy\windows"
Name: "{group}\Parar servico"; Filename: "{app}\app\deploy\windows\stop_service.bat"; WorkingDir: "{app}\app\deploy\windows"
Name: "{group}\Reiniciar servico"; Filename: "{app}\app\deploy\windows\restart_service.bat"; WorkingDir: "{app}\app\deploy\windows"
Name: "{group}\Desinstalar Sistema Gestao Agro"; Filename: "{uninstallexe}"

[Run]
Filename: "{app}\app\deploy\windows\install.bat"; WorkingDir: "{app}\app"; Flags: runhidden waituntilterminated; StatusMsg: "Instalando e configurando o servico Sistema Gestao Agro..."
Filename: "{#MyAppURL}"; Description: "Abrir Sistema Gestao Agro"; Flags: postinstall shellexec skipifsilent nowait

[UninstallRun]
Filename: "{app}\app\deploy\windows\uninstall.bat"; WorkingDir: "{app}\app"; Flags: runhidden waituntilterminated

[UninstallDelete]
Type: files; Name: "{commondesktop}\Sistema Gestao Agro.lnk"

[Code]
function InitializeSetup(): Boolean;
begin
  Result := True;
end;
