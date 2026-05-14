"""Valida a conexão PostgreSQL antes de executar as migrações no Windows."""
from __future__ import annotations

import os
import socket
import sys
from pathlib import Path

import psycopg2
from dotenv import dotenv_values


DEFAULT_ENV_PATH = r"C:\SistemaGestaoAgro\app\.env"
DEFAULT_INSTALLER = r"C:\SistemaGestaoAgro\app\deploy\windows\install.bat"


def describe_exception(exc: BaseException) -> str:
    """Converte exceções do PostgreSQL em texto seguro para consoles Windows."""
    if isinstance(exc, UnicodeDecodeError):
        return (
            "Mensagem do PostgreSQL/libpq veio em uma codificacao diferente de UTF-8 "
            f"({exc.encoding}, bytes {exc.start}-{exc.end}). Isso normalmente indica erro "
            "de conexao, autenticacao, porta ou banco inexistente. Confira os itens abaixo."
        )

    try:
        return str(exc)
    except UnicodeError:
        return repr(exc)


def main() -> int:
    env_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".env")
    values = dotenv_values(env_path)

    db_name = values.get("POSTGRES_DB") or "sistema_gestao"
    db_user = values.get("POSTGRES_USER") or "postgres"
    db_password = values.get("POSTGRES_PASSWORD") or "postgres"
    db_host = values.get("POSTGRES_HOST") or "localhost"
    db_port = values.get("POSTGRES_PORT") or "5432"

    os.environ.setdefault("PGCLIENTENCODING", "UTF8")

    print(f"Verificando PostgreSQL em {db_host}:{db_port}, banco '{db_name}', usuario '{db_user}'...")

    try:
        with socket.create_connection((db_host, int(db_port)), timeout=5):
            pass
    except Exception as exc:
        print("ERRO: nao foi possivel abrir conexao TCP com o PostgreSQL.")
        print(f"Detalhe: {describe_exception(exc)}")
        print("")
        print("Verifique se o servico do PostgreSQL esta iniciado e se a porta esta correta.")
        print("Comandos uteis no Prompt de Comando:")
        print("  sc query postgresql-x64-16")
        print("  netstat -ano | findstr :5432")
        return 1

    try:
        connection = psycopg2.connect(
            dbname=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port,
            connect_timeout=5,
        )
    except Exception as exc:
        print("ERRO: nao foi possivel autenticar/conectar ao PostgreSQL com as configuracoes do .env.")
        print(f"Detalhe: {describe_exception(exc)}")
        print("")
        print("Verifique no Windows:")
        print("1. Se o PostgreSQL esta instalado e o servico esta iniciado.")
        print("2. Se a porta configurada esta correta, normalmente 5432.")
        print("3. Se o banco de dados existe, por exemplo: CREATE DATABASE sistema_gestao;")
        print(f"4. Se POSTGRES_USER e POSTGRES_PASSWORD em {DEFAULT_ENV_PATH} estao corretos.")
        print(f"5. Depois de corrigir, execute novamente {DEFAULT_INSTALLER} como Administrador.")
        return 1

    connection.close()
    print("Conexao com PostgreSQL validada com sucesso.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
