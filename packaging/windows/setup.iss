#ifndef AppVersion
  #define AppVersion "0.1.0"
#endif

[Setup]
AppId={{AF797CF0-94F4-4C2D-A7F5-D42BE8284B8A}
AppName=몰입 퀘스트
AppVersion={#AppVersion}
AppPublisher=몰입 퀘스트
DefaultDirName={localappdata}\Programs\MolipQuest
DefaultGroupName=몰입 퀘스트
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0
OutputDir=..\..\target\installers
OutputBaseFilename=molip-quest-windows-x64-setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\molip-quest.exe
SetupIconFile=..\..\assets\icon\icon.ico

[Files]
Source: "..\..\target\release\molip-quest.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\requirements-learning.txt"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\몰입 퀘스트"; Filename: "{app}\molip-quest.exe"
Name: "{group}\몰입 퀘스트 제거"; Filename: "{uninstallexe}"

[Run]
Filename: "{app}\molip-quest.exe"; Description: "몰입 퀘스트 실행"; Flags: nowait postinstall skipifsilent
