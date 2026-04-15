; Live Video Composer Inno Setup Script
; Genera installer Windows professionale
; Richiede Inno Setup: https://jrsoftware.org/isinfo.php

#define MyAppName "Live Video Composer"
#define MyAppVersion "1.5.0"
#define MyAppPublisher "Live Software"
#define MyAppURL "https://www.liveworksapp.com"
#define MyAppExeName "Live_Video_Composer.exe"

[Setup]
; Identificatore unico applicazione (NON modificare: usato per upgrade in-place)
AppId={{A8B7C6D5-E4F3-2A1B-0C9D-8E7F6A5B4C3D}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
; Output installer
OutputDir=release
OutputBaseFilename=Live_Video_Composer_Setup
; Compressione
Compression=lzma2/ultra64
SolidCompression=yes
; Icona setup e uninstall
SetupIconFile=icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
; Grafiche wizard (stile broadcast, dark)
WizardImageFile=installer-wizard.bmp
WizardSmallImageFile=installer-wizard-small.bmp
; Requisiti
MinVersion=10.0
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
; Aspetto moderno
WizardStyle=modern
; Permessi
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
; Upgrade: chiudi app se in esecuzione, consenti downgrade
CloseApplications=force
CloseApplicationsFilter=*.exe
RestartApplications=no

[Languages]
; Lingua ufficiale: Inglese (i18n-installer.mdc)
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "italian"; MessagesFile: "compiler:Languages\Italian.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Copia tutti i file dalla cartella dist/Live_Video_Composer
Source: "dist\Live_Video_Composer\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; Documentazione
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallRun]
; Deattiva la licenza Live Works prima della rimozione (best-effort, timeout 30s)
Filename: "{app}\{#MyAppExeName}"; Parameters: "--deactivate"; RunOnceId: "DeactivateLicense"; Flags: waituntilterminated; StatusMsg: "Deactivating license..."

[UninstallDelete]
Type: filesandordirs; Name: "{app}"

[Code]
function PrepareToInstall(var NeedsRestart: Boolean): String;
var
  ResultCode: Integer;
begin
  Result := '';
  { Kill running instance before upgrade }
  Exec('taskkill', '/F /IM {#MyAppExeName} /T', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
end;
