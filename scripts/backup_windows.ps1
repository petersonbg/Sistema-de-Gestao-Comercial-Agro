<#
Backup local simples do Sistema de Gestão Comercial Agro para Windows PowerShell.
Configure as variáveis abaixo ou sobrescreva-as com variáveis de ambiente antes de executar.
Não coloque senhas reais neste arquivo. Use a variável de ambiente PGPASSWORD apenas no computador local
ou configure o arquivo pgpass do PostgreSQL.
#>

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$DefaultAppDir = Resolve-Path (Join-Path $ScriptDir "..")

$AppDir = if ($env:APP_DIR) { $env:APP_DIR } else { $DefaultAppDir.Path }
$BackupDir = if ($env:BACKUP_DIR) { $env:BACKUP_DIR } else { Join-Path $AppDir "backups" }
$PostgresDb = if ($env:POSTGRES_DB) { $env:POSTGRES_DB } else { "sistema_gestao" }
$PostgresUser = if ($env:POSTGRES_USER) { $env:POSTGRES_USER } else { "postgres" }
$PostgresHost = if ($env:POSTGRES_HOST) { $env:POSTGRES_HOST } else { "localhost" }
$PostgresPort = if ($env:POSTGRES_PORT) { $env:POSTGRES_PORT } else { "5432" }
$MediaDir = if ($env:MEDIA_DIR) { $env:MEDIA_DIR } else { Join-Path $AppDir "media" }
$PdfDir = if ($env:PDF_DIR) { $env:PDF_DIR } else { "" }

$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$WorkDir = Join-Path $BackupDir "backup_$Timestamp"
$Archive = Join-Path $BackupDir "sistema_gestao_backup_$Timestamp.zip"

New-Item -ItemType Directory -Force -Path $WorkDir | Out-Null

$PgDump = Get-Command pg_dump -ErrorAction SilentlyContinue
if (-not $PgDump) {
    throw "pg_dump não encontrado. Instale as ferramentas cliente do PostgreSQL ou adicione o diretório bin do PostgreSQL ao PATH."
}

Write-Host "Gerando backup do banco PostgreSQL..."
& $PgDump.Source `
    --host=$PostgresHost `
    --port=$PostgresPort `
    --username=$PostgresUser `
    --format=custom `
    --file=(Join-Path $WorkDir "${PostgresDb}_$Timestamp.dump") `
    $PostgresDb

if (Test-Path $MediaDir) {
    Write-Host "Copiando pasta media..."
    Copy-Item -Path $MediaDir -Destination (Join-Path $WorkDir "media") -Recurse -Force
} else {
    Write-Host "Aviso: pasta media não encontrada em $MediaDir; etapa ignorada."
}

if ($PdfDir) {
    if (Test-Path $PdfDir) {
        Write-Host "Copiando pasta de PDFs..."
        Copy-Item -Path $PdfDir -Destination (Join-Path $WorkDir "pdfs") -Recurse -Force
    } else {
        Write-Host "Aviso: PDF_DIR foi informado, mas não existe: $PdfDir; etapa ignorada."
    }
}

Write-Host "Compactando backup..."
if (Test-Path $Archive) { Remove-Item $Archive -Force }
Compress-Archive -Path (Join-Path $WorkDir "*") -DestinationPath $Archive -Force
Remove-Item $WorkDir -Recurse -Force

Write-Host "Backup concluído: $Archive"
