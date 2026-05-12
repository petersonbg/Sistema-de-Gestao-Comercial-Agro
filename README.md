# Sistema de Gestão Comercial Agro

Projeto Django base para um sistema de gestão comercial agropecuário, pensado para uso inicial em um computador comum da empresa como servidor local e acesso por navegador na rede interna.

A aplicação atenderá uma empresa que comercializa:

- adubos e fertilizantes;
- peças mecânicas de reposição;
- triciclos agrícolas;
- ferramentas, acessórios e produtos diversos.

> Esta etapa cria somente a base limpa do projeto. Models completos, CRUDs, relatórios, regras de estoque, vendas e financeiro serão implementados em fases futuras.

## Tecnologias

- Python;
- Django;
- PostgreSQL;
- Templates tradicionais do Django;
- Bootstrap;
- JavaScript simples apenas quando necessário.

## Estrutura inicial

```text
sistema_gestao/      # Configurações principais do projeto Django
core/                # Dashboard e views centrais
empresas/            # Dados da empresa e filiais
usuarios/            # Organização futura de usuários e permissões
clientes/            # Cadastro de clientes
fornecedores/        # Cadastro de fornecedores
produtos/            # Cadastro de produtos
estoque/             # Controle de estoque
vendas/              # Vendas e pedidos
orcamentos/          # Orçamentos comerciais
relatorios/          # Relatórios gerenciais
financeiro/          # Contas, recebimentos e pagamentos
templates/           # Templates globais Django
static/css/          # Estilos customizados
static/js/           # JavaScript simples
```

## Pré-requisitos

- Python 3.11 ou superior recomendado;
- PostgreSQL instalado e em execução;
- Git, para versionamento do projeto.

## Instalação

1. Clone o repositório e entre na pasta do projeto.

2. Crie e ative um ambiente virtual:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

   No Windows PowerShell:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Instale as dependências:

   ```bash
   pip install -r requirements.txt
   ```

4. Crie o arquivo `.env` com base no exemplo:

   ```bash
   cp .env.example .env
   ```

5. Ajuste as variáveis do PostgreSQL no `.env`:

   ```env
   POSTGRES_DB=sistema_gestao
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=postgres
   POSTGRES_HOST=localhost
   POSTGRES_PORT=5432
   ```

6. Crie o banco no PostgreSQL, se ainda não existir:

   ```sql
   CREATE DATABASE sistema_gestao;
   ```

7. Execute as migrações iniciais do Django:

   ```bash
   python manage.py migrate
   ```

8. Crie um usuário administrador:

   ```bash
   python manage.py createsuperuser
   ```

9. Rode o servidor local:

   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```

10. Acesse no navegador:

    - No próprio servidor: <http://127.0.0.1:8000/>
    - Em outro computador da mesma rede: `http://IP_DO_SERVIDOR:8000/`

## Configuração para rede interna

Para acessar de outros computadores da rede, inclua o IP ou nome do servidor em `ALLOWED_HOSTS` no arquivo `.env`:

```env
ALLOWED_HOSTS=127.0.0.1,localhost,192.168.0.10
```

Se futuramente houver acesso remoto com domínio e HTTPS, também configure `CSRF_TRUSTED_ORIGINS`:

```env
CSRF_TRUSTED_ORIGINS=https://seudominio.com.br
```

## Rotas iniciais

- `/` — dashboard protegido por login;
- `/login/` — tela de login;
- `/logout/` — saída do sistema;
- `/admin/` — administração padrão do Django.

## Próximas etapas sugeridas

- Definir models de empresas, clientes, fornecedores e produtos;
- Implementar cadastro de produtos por categorias e unidades de medida;
- Criar regras de movimentação de estoque;
- Implementar orçamentos e vendas;
- Adicionar financeiro básico;
- Criar relatórios comerciais e gerenciais;
- Refinar permissões por perfil de usuário.
