#!/usr/bin/env bash
set -euo pipefail

# Backup local simples do Sistema de Gestão Comercial Agro para Linux.
# Configure as variáveis abaixo ou sobrescreva-as no ambiente antes de executar.
# Não coloque senhas reais neste arquivo. Use ~/.pgpass ou exporte PGPASSWORD apenas no ambiente local.

APP_DIR="${APP_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
BACKUP_DIR="${BACKUP_DIR:-$APP_DIR/backups}"
POSTGRES_DB="${POSTGRES_DB:-sistema_gestao}"
POSTGRES_USER="${POSTGRES_USER:-postgres}"
POSTGRES_HOST="${POSTGRES_HOST:-localhost}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"
MEDIA_DIR="${MEDIA_DIR:-$APP_DIR/media}"
PDF_DIR="${PDF_DIR:-}"

TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
WORK_DIR="$BACKUP_DIR/backup_$TIMESTAMP"
ARCHIVE="$BACKUP_DIR/sistema_gestao_backup_$TIMESTAMP.tar.gz"

mkdir -p "$WORK_DIR"

if ! command -v pg_dump >/dev/null 2>&1; then
  echo "Erro: pg_dump não encontrado. Instale as ferramentas cliente do PostgreSQL." >&2
  exit 1
fi

echo "Gerando backup do banco PostgreSQL..."
pg_dump \
  --host="$POSTGRES_HOST" \
  --port="$POSTGRES_PORT" \
  --username="$POSTGRES_USER" \
  --format=custom \
  --file="$WORK_DIR/${POSTGRES_DB}_$TIMESTAMP.dump" \
  "$POSTGRES_DB"

if [ -d "$MEDIA_DIR" ]; then
  echo "Copiando pasta media..."
  mkdir -p "$WORK_DIR/media"
  cp -a "$MEDIA_DIR/." "$WORK_DIR/media/"
else
  echo "Aviso: pasta media não encontrada em $MEDIA_DIR; etapa ignorada."
fi

if [ -n "$PDF_DIR" ]; then
  if [ -d "$PDF_DIR" ]; then
    echo "Copiando pasta de PDFs..."
    mkdir -p "$WORK_DIR/pdfs"
    cp -a "$PDF_DIR/." "$WORK_DIR/pdfs/"
  else
    echo "Aviso: PDF_DIR foi informado, mas não existe: $PDF_DIR; etapa ignorada."
  fi
fi

echo "Compactando backup..."
tar -czf "$ARCHIVE" -C "$BACKUP_DIR" "backup_$TIMESTAMP"
rm -rf "$WORK_DIR"

echo "Backup concluído: $ARCHIVE"
