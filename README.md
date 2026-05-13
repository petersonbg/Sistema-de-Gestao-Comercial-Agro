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

## Configuração para rede local interna

O uso inicial recomendado é manter o sistema rodando em um computador da empresa, chamado aqui de **computador servidor**, e permitir que outros computadores e celulares da mesma rede acessem pelo navegador.

> Esta seção cobre somente acesso na rede local da empresa. Não configure acesso remoto externo pela internet nesta etapa.

### 1. Descobrir o IP local do computador servidor

No **Windows**, abra o Prompt de Comando ou PowerShell no computador servidor e execute:

```powershell
ipconfig
```

Procure pelo adaptador de rede em uso, normalmente **Adaptador Ethernet** ou **Adaptador de Rede sem Fio Wi-Fi**, e anote o valor de **Endereço IPv4**. Exemplo:

```text
Endereço IPv4 . . . . . . . . . . . . . . : 192.168.0.10
```

No **Linux**, execute:

```bash
hostname -I
```

ou:

```bash
ip addr
```

Use o IP da interface conectada à rede interna, por exemplo `192.168.0.10`.

### 2. Configurar ALLOWED_HOSTS no `.env`

Para o Django aceitar conexões feitas por outros dispositivos da rede, inclua o IP local do servidor em `ALLOWED_HOSTS` no arquivo `.env`:

```env
ALLOWED_HOSTS=127.0.0.1,localhost,192.168.0.10
```

Substitua `192.168.0.10` pelo IP local real do computador servidor. Se a empresa usar um nome de máquina na rede, ele também pode ser incluído:

```env
ALLOWED_HOSTS=127.0.0.1,localhost,192.168.0.10,servidor-agro
```

### 3. Rodar o Django acessível na rede local

No computador servidor, com o ambiente virtual ativo e dentro da pasta do projeto, execute:

```bash
python manage.py runserver 0.0.0.0:8000
```

O endereço `0.0.0.0` faz o servidor escutar em todas as interfaces de rede do computador, permitindo acesso de outros dispositivos da mesma rede.

### 4. Acessar de outro computador ou celular

Em outro computador, notebook, tablet ou celular conectado à mesma rede Wi-Fi/cabeada, abra o navegador e acesse:

```text
http://IP_DO_SERVIDOR:8000/
```

Exemplo:

```text
http://192.168.0.10:8000/
```

Se aparecer erro de host não permitido, revise o `ALLOWED_HOSTS` no `.env` e reinicie o servidor Django.

### 5. Cuidados com firewall do Windows

No Windows, o firewall pode bloquear conexões na porta `8000`. Se outros dispositivos não conseguirem acessar:

1. Abra **Segurança do Windows**.
2. Acesse **Firewall e proteção de rede**.
3. Clique em **Permitir um aplicativo pelo firewall** ou crie uma **Regra de Entrada**.
4. Permita o Python/Django ou libere a porta TCP `8000` somente para redes privadas.
5. Evite liberar a porta para redes públicas.

Também verifique se a rede atual do Windows está marcada como **Rede privada**, e não como **Rede pública**, para facilitar o acesso interno controlado.

### 6. Cuidados com antivírus e firewalls de terceiros

Antivírus, suítes de segurança e firewalls de terceiros podem bloquear o Python, o PostgreSQL ou a porta `8000`. Caso o acesso falhe mesmo com `ALLOWED_HOSTS` correto:

- crie exceção para o executável do Python usado no ambiente virtual;
- crie exceção para a porta TCP `8000` na rede privada;
- confirme que o PostgreSQL local continua acessível pelo sistema;
- evite desativar completamente o antivírus/firewall como solução permanente.

### 7. Recomendações operacionais para o servidor local

- Configure um **IP fixo local** para o computador servidor, preferencialmente por reserva DHCP no roteador. Isso evita que o endereço mude e que os atalhos dos usuários parem de funcionar.
- Use um **no-break** no computador servidor e no roteador/switch principal para reduzir risco de desligamento inesperado e corrupção de dados.
- Faça **backup diário** do banco PostgreSQL e da pasta `media/` usando a rotina descrita em [Rotina recomendada de backup](#rotina-recomendada-de-backup).
- Mantenha o computador servidor ligado durante o expediente e evite reinicializações sem avisar os usuários.
- Não exponha a porta `8000` diretamente para a internet. Acesso remoto externo deve ser planejado separadamente, com HTTPS, domínio, autenticação adequada e regras de segurança.

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

O CRUD de clientes, fornecedores, categorias, marcas e produtos usa busca, paginação, detalhes, cadastro, edição e inativação lógica, sempre restringindo dados à empresa vinculada ao usuário logado. O módulo de estoque registra entradas conforme o controle do produto e atualiza o saldo com movimentação vinculada. O módulo de venda balcão finaliza vendas em transação atômica, aplica descontos e baixa estoque por controle simples, lote FEFO ou unidade serial. Vendas finalizadas podem ser canceladas por administradores, com motivo obrigatório, devolução integral ao estoque e movimentações de cancelamento.

## Models iniciais

A base inclui models iniciais para:

- empresas e usuários personalizados por empresa;
- clientes e fornecedores;
- categorias, marcas e cadastro único de produtos;
- controle de estoque simples, por lote/validade e por unidade identificada;
- vendas, itens de venda, orçamentos e itens de orçamento.

O cadastro de produtos usa `tipo_controle_estoque` para separar produtos comuns, produtos com lote e validade, e unidades identificadas como triciclos, máquinas ou veículos.

## Rotina recomendada de backup

O sistema foi pensado para rodar inicialmente em um computador comum da empresa. Nesse cenário, mantenha uma rotina simples e verificável de backup local, copiando o arquivo gerado para um HD externo, pendrive ou serviço de armazenamento seguro ao final do dia.

### O que é incluído no backup

Os scripts em `scripts/` geram um arquivo compactado com data e hora no nome contendo:

- dump do banco PostgreSQL em formato customizado (`pg_dump --format=custom`);
- pasta `media/`, quando existir;
- pasta de PDFs, caso você configure a variável `PDF_DIR` para uma pasta específica.

> Atualmente os PDFs de recibos e orçamentos são gerados para abertura no navegador e não ficam salvos em uma pasta fixa. Se futuramente forem salvos em disco, defina `PDF_DIR` apontando para essa pasta antes de executar o backup.

### Variáveis configuráveis

Os scripts não incluem senhas reais. Configure senha via mecanismos locais do PostgreSQL, como `PGPASSWORD` apenas no ambiente do usuário que executará o backup, ou arquivo `pgpass`/`.pgpass` protegido.

Variáveis aceitas pelos scripts:

| Variável | Descrição | Padrão |
| --- | --- | --- |
| `APP_DIR` | Pasta raiz do projeto | pasta acima de `scripts/` |
| `BACKUP_DIR` | Pasta onde os backups serão criados | `APP_DIR/backups` |
| `POSTGRES_DB` | Nome do banco PostgreSQL | `sistema_gestao` |
| `POSTGRES_USER` | Usuário do PostgreSQL | `postgres` |
| `POSTGRES_HOST` | Host do PostgreSQL | `localhost` |
| `POSTGRES_PORT` | Porta do PostgreSQL | `5432` |
| `MEDIA_DIR` | Pasta de arquivos enviados pela aplicação | `APP_DIR/media` |
| `PDF_DIR` | Pasta opcional de PDFs salvos em disco | vazio |

A pasta `backups/` é ignorada pelo Git e deve ser copiada para um local externo conforme a política da empresa.

### Executar backup no Linux

No terminal, a partir da raiz do projeto:

```bash
chmod +x scripts/backup_linux.sh
POSTGRES_DB=sistema_gestao POSTGRES_USER=postgres ./scripts/backup_linux.sh
```

Exemplo informando senha apenas no ambiente local da execução:

```bash
PGPASSWORD='SUA_SENHA_LOCAL' ./scripts/backup_linux.sh
```

### Agendar backup no Linux com cron

1. Abra o agendador do usuário que executa o sistema:

   ```bash
   crontab -e
   ```

2. Adicione uma linha para executar todos os dias às 18h30:

   ```cron
   30 18 * * * cd /caminho/para/Sistema-de-Gestao-Comercial-Agro && /caminho/para/Sistema-de-Gestao-Comercial-Agro/scripts/backup_linux.sh >> /caminho/para/Sistema-de-Gestao-Comercial-Agro/backups/backup.log 2>&1
   ```

3. Salve o arquivo e confirme no dia seguinte se o `.tar.gz` foi gerado em `backups/`.

### Executar backup no Windows

No PowerShell, a partir da raiz do projeto:

```powershell
$env:POSTGRES_DB = "sistema_gestao"
$env:POSTGRES_USER = "postgres"
.\scripts\backup_windows.ps1
```

Se o `pg_dump` não estiver no `PATH`, adicione temporariamente o diretório `bin` do PostgreSQL antes da execução, ajustando a versão instalada:

```powershell
$env:Path += ";C:\Program Files\PostgreSQL\16\bin"
.\scripts\backup_windows.ps1
```

Exemplo informando senha apenas no ambiente local da execução:

```powershell
$env:PGPASSWORD = "SUA_SENHA_LOCAL"
.\scripts\backup_windows.ps1
Remove-Item Env:\PGPASSWORD
```

### Agendar backup no Windows pelo Agendador de Tarefas

1. Abra **Agendador de Tarefas** no Windows.
2. Clique em **Criar Tarefa Básica...**.
3. Nomeie como `Backup Sistema Gestão Agro`.
4. Escolha o gatilho **Diariamente** e defina um horário fora do expediente, por exemplo 18h30.
5. Em **Ação**, selecione **Iniciar um programa**.
6. Em **Programa/script**, informe:

   ```text
   powershell.exe
   ```

7. Em **Adicionar argumentos**, informe, ajustando o caminho do projeto:

   ```text
   -ExecutionPolicy Bypass -File "C:\caminho\para\Sistema-de-Gestao-Comercial-Agro\scripts\backup_windows.ps1"
   ```

8. Em **Iniciar em**, informe a pasta raiz do projeto:

   ```text
   C:\caminho\para\Sistema-de-Gestao-Comercial-Agro
   ```

9. Conclua e execute a tarefa manualmente uma vez para validar.
10. Verifique se o arquivo `.zip` foi criado em `backups/`.

### Boas práticas simples

- Teste a restauração periodicamente em outro computador ou banco de homologação.
- Mantenha pelo menos uma cópia fora do computador principal.
- Evite salvar senhas dentro dos scripts ou do repositório.
- Monitore o espaço em disco da pasta `backups/`.
- Apague backups antigos somente depois de confirmar que existem cópias externas válidas.

## Próximas etapas sugeridas

- Definir models de empresas, clientes, fornecedores e produtos;
- Implementar cadastro de produtos por categorias e unidades de medida;
- Criar regras de movimentação de estoque;
- Implementar orçamentos e vendas;
- Adicionar financeiro básico;
- Criar relatórios comerciais e gerenciais;
- Refinar permissões por perfil de usuário.
