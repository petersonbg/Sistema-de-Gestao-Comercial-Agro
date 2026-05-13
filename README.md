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
- `/clientes/` — CRUD de clientes da empresa do usuário;
- `/fornecedores/` — CRUD de fornecedores da empresa do usuário;
- `/produtos/` — CRUD de produtos da empresa do usuário;
- `/produtos/categorias/` — CRUD de categorias de produtos;
- `/produtos/marcas/` — CRUD de marcas de produtos;
- `/estoque/entradas/nova/` — entrada de estoque por controle simples, lote ou serial;
- `/vendas/balcao/` — venda simples estilo balcão com baixa automática de estoque;
- `/admin/` — administração padrão do Django.



## Autenticação e perfis

O projeto usa a autenticação tradicional do Django com tela de login personalizada em Bootstrap, confirmação de logout e redirecionamento automático para o dashboard após login.

Perfis iniciais:

- **Administrador**: acesso completo aos módulos e configurações administrativas.
- **Vendedor**: acesso aos módulos comerciais de clientes, produtos, vendas e orçamentos, sem acesso às configurações administrativas sensíveis.

O dashboard exibe indicadores simples de clientes, produtos ativos, estoque baixo, vendas do dia e orçamentos abertos.

O CRUD de clientes, fornecedores, categorias, marcas e produtos usa busca, paginação, detalhes, cadastro, edição e inativação lógica, sempre restringindo dados à empresa vinculada ao usuário logado. O módulo de estoque registra entradas conforme o controle do produto e atualiza o saldo com movimentação vinculada. O módulo de venda balcão finaliza vendas em transação atômica, aplica descontos e baixa estoque por controle simples, lote FEFO ou unidade serial.

## Models iniciais

A base inclui models iniciais para:

- empresas e usuários personalizados por empresa;
- clientes e fornecedores;
- categorias, marcas e cadastro único de produtos;
- controle de estoque simples, por lote/validade e por unidade identificada;
- vendas, itens de venda, orçamentos e itens de orçamento.

O cadastro de produtos usa `tipo_controle_estoque` para separar produtos comuns, produtos com lote e validade, e unidades identificadas como triciclos, máquinas ou veículos.

## Próximas etapas sugeridas

- Definir models de empresas, clientes, fornecedores e produtos;
- Implementar cadastro de produtos por categorias e unidades de medida;
- Criar regras de movimentação de estoque;
- Implementar orçamentos e vendas;
- Adicionar financeiro básico;
- Criar relatórios comerciais e gerenciais;
- Refinar permissões por perfil de usuário.
