$ErrorActionPreference = 'Stop'

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ToolsDir = 'C:\SistemaGestaoAgro\tools'
$ZipPath = Join-Path $ToolsDir 'nssm.zip'
$ExtractDir = Join-Path $ToolsDir 'nssm'
$TargetPath = Join-Path $ScriptDir 'nssm.exe'
$NssmUrl = 'https://nssm.cc/release/nssm-2.24.zip'

New-Item -ItemType Directory -Force -Path $ToolsDir | Out-Null

Write-Host "Baixando NSSM de $NssmUrl ..."
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
Invoke-WebRequest -Uri $NssmUrl -OutFile $ZipPath -UseBasicParsing

if (Test-Path $ExtractDir) {
    Remove-Item $ExtractDir -Recurse -Force
}
New-Item -ItemType Directory -Force -Path $ExtractDir | Out-Null

Write-Host "Extraindo NSSM..."
Expand-Archive -Path $ZipPath -DestinationPath $ExtractDir -Force

$ArchFolder = if ([Environment]::Is64BitOperatingSystem) { 'win64' } else { 'win32' }
$SourcePath = Get-ChildItem -Path $ExtractDir -Recurse -Filter 'nssm.exe' |
    Where-Object { $_.FullName -like "*\$ArchFolder\nssm.exe" } |
    Select-Object -First 1

if (-not $SourcePath) {
    throw "nssm.exe nao foi encontrado no ZIP baixado."
}

Copy-Item -Path $SourcePath.FullName -Destination $TargetPath -Force
Write-Host "NSSM preparado em $TargetPath"
