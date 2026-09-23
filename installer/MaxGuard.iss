#define AppName "MaxGuard"
#define AppVersion "1.0.0"
#define AppPublisher "MaxGuard"
#define AppExeName "MaxGuard.exe"

[Setup]
AppId={{B4D7E9C0-7D2A-4C71-9E11-5A7B7E1C1010}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
DefaultDirName={autopf}\MaxGuard
DefaultGroupName=MaxGuard
OutputDir=output
OutputBaseFilename=MaxGuard-1.0-Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
UninstallDisplayIcon={app}\{#AppExeName}

[Files]
Source: "..\dist\MaxGuard\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs ignoreversion

[Icons]
Name: "{group}\MaxGuard"; Filename: "{app}\{#AppExeName}"
Name: "{autodesktop}\MaxGuard"; Filename: "{app}\{#AppExeName}"

[Run]
Filename: "{app}\{#AppExeName}"; Description: "Launch MaxGuard"; Flags: nowait postinstall skipifsilent
