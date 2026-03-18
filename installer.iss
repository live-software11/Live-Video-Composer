; Live Video Composer Inno Setup Script
; Genera installer Windows professionale
; Richiede Inno Setup: https://jrsoftware.org/isinfo.php

#define MyAppName "Live Video Composer"
#define MyAppVersion "1.4.1"
#define MyAppPublisher "Live Software"
#define MyAppURL "https://github.com/live-software11"
#define MyAppExeName "Live_Video_Composer.exe"

[Setup]
; Identificatore unico applicazione
AppId={{A8B7C6D5-E4F3-2A1B-0C9D-8E7F6A5B4C3D}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
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
; Requisiti
MinVersion=10.0
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
; Aspetto moderno
WizardStyle=modern
; Permessi
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

[Languages]
Name: "italian"; MessagesFile: "compiler:Languages\Italian.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
; Copia tutti i file dalla cartella dist/Live_Video_Composer
Source: "dist\Live_Video_Composer\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; Documentazione
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"
