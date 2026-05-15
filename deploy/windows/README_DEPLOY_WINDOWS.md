# Implantação no Windows — Sistema de Gestão Comercial Agro

Esta pasta contém a estrutura para instalar a aplicação Django existente neste repositório em um computador Windows da empresa, com o mínimo possível de comandos manuais.

A implantação usa:

- Django com templates tradicionais;
- Waitress como servidor WSGI local;
- PostgreSQL como banco de dados;
- NSSM para registrar a aplicação como serviço do Windows;
- Inno Setup, opcionalmente, para gerar um instalador `.exe`.

> Não use PyInstaller como solução principal. A aplicação deve rodar como código Python em ambiente virtual, servida pelo Waitress e gerenciada pelo NSSM.

## Estrutura criada no servidor

O `install.bat` cria a seguinte estrutura:

```text
C:\SistemaGestaoAgro\
├── app\       # código da aplicação Django
├── venv\      # ambiente virtual Python
├── logs\      # logs stdout/stderr do serviço NSSM
├── backups\   # destino sugerido para backups locais
└── media\     # arquivos enviados/gerados em tempo de execução
```

O serviço do Windows se chama:

```text
SistemaGestaoAgro
```

O comando executado pelo serviço é equivalente a:

```bat
waitress-serve --listen=0.0.0.0:8000 sistema_gestao.wsgi:application
```

## Pré-requisitos

1. Windows 10/11 ou Windows Server.
2. Conta de usuário com permissão de **Administrador**.
3. Python 3.11 ou superior.
4. PostgreSQL instalado e em execução.
5. NSSM instalado ou `nssm.exe` copiado para `deploy\windows\`.
6. Acesso à internet para `pip install -r requirements.txt`, ou repositório interno de pacotes Python configurado.
7. Código do projeto disponível no computador servidor, via Git, arquivo ZIP ou instalador gerado pelo Inno Setup.

## Instalação do Python

1. Baixe o Python em <https://www.python.org/downloads/windows/>.
2. Execute o instalador.
3. Marque a opção **Add python.exe to PATH**.
4. Finalize a instalação.
5. Abra um novo Prompt de Comando e valide:

   ```bat
   python --version
   pip --version
   ```

Se o comando `python` não for reconhecido, reinstale marcando a opção de PATH ou ajuste as variáveis de ambiente do Windows.

## Instalação e configuração do PostgreSQL

1. Baixe o PostgreSQL em <https://www.postgresql.org/download/windows/>.
2. Instale mantendo a porta padrão `5432`, salvo política diferente da empresa.
3. Anote usuário e senha administrativos.
4. Crie o banco da aplicação pelo pgAdmin ou pelo `psql`:

   ```sql
   CREATE DATABASE sistema_gestao;
   ```

5. Confirme que o serviço do PostgreSQL está iniciado no Windows.
6. Depois da instalação da aplicação, revise o arquivo:

   ```text
   C:\SistemaGestaoAgro\app\.env
   ```

   Ajuste as variáveis conforme o banco local:

   ```env
   POSTGRES_DB=sistema_gestao
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=SUA_SENHA_LOCAL
   POSTGRES_HOST=localhost
   POSTGRES_PORT=5432
   ```

## Instalação do NSSM

O `install.bat` tenta localizar o NSSM no `PATH` ou em `deploy\windows\nssm.exe`. Se não encontrar, ele tenta baixar automaticamente o NSSM usando `deploy\windows\get_nssm.ps1` e copia o executável correto para a pasta dos scripts.

Se o download automático falhar por bloqueio de internet, proxy, antivírus ou política da empresa, faça manualmente:

1. Baixe o NSSM em <https://nssm.cc/download>.
2. Extraia o arquivo ZIP.
3. Copie o `nssm.exe` compatível com a arquitetura do Windows para uma das opções abaixo:
   - uma pasta presente no `PATH` do Windows; ou
   - `C:\SistemaGestaoAgro\app\deploy\windows\nssm.exe`, ao lado do `install.bat`.
4. Valide no Prompt de Comando:

   ```bat
   C:\SistemaGestaoAgro\app\deploy\windows\nssm.exe version
   ```

## Instalação manual com install.bat

1. Copie ou clone o projeto no computador servidor.
2. Abra o Prompt de Comando ou PowerShell como **Administrador**.
3. Entre na pasta raiz do projeto.
4. Execute:

   ```bat
   deploy\windows\install.bat
   ```

O script irá:

- criar `C:\SistemaGestaoAgro`, se não existir;
- criar as subpastas `app`, `logs`, `backups` e `media`;
- copiar o projeto para `C:\SistemaGestaoAgro\app`, quando necessário;
- criar o ambiente virtual em `C:\SistemaGestaoAgro\venv`;
- instalar as dependências do `requirements.txt`;
- criar `C:\SistemaGestaoAgro\app\.env` a partir de `.env.example`, caso ainda não exista;
- executar `python manage.py migrate`;
- executar `python manage.py collectstatic --noinput`;
- registrar a aplicação como serviço do Windows via NSSM;
- configurar o serviço para usar `waitress-serve` na porta `8000`;
- gravar logs em `C:\SistemaGestaoAgro\logs`;
- iniciar o serviço `SistemaGestaoAgro`.

> Se o `.env` for criado pela primeira vez e as credenciais do PostgreSQL ainda estiverem incorretas, ajuste o arquivo e execute o `install.bat` novamente como administrador.

## Controle do serviço

Execute os scripts abaixo como administrador:

```bat
deploy\windows\start_service.bat
deploy\windows\stop_service.bat
deploy\windows\restart_service.bat
```

Também é possível abrir `services.msc` e procurar por **SistemaGestaoAgro**.

## Desinstalação

Execute como administrador:

```bat
deploy\windows\uninstall.bat
```

O `uninstall.bat` apenas:

- para o serviço `SistemaGestaoAgro`;
- remove o serviço com NSSM.

Ele **não apaga** banco PostgreSQL, backups, logs, `media` nem a pasta `C:\SistemaGestaoAgro`, para evitar perda acidental de dados.

## Acesso local

No próprio servidor, abra o navegador em:

```text
http://localhost:8000/
```

ou:

```text
http://127.0.0.1:8000/
```

## Acesso pela rede local

1. No servidor, descubra o IP local:

   ```bat
   ipconfig
   ```

2. Edite `C:\SistemaGestaoAgro\app\.env` e inclua o IP em `ALLOWED_HOSTS`:

   ```env
   ALLOWED_HOSTS=127.0.0.1,localhost,192.168.0.10
   ```

3. Reinicie o serviço:

   ```bat
   deploy\windows\restart_service.bat
   ```

4. Em outro computador da mesma rede, acesse:

   ```text
   http://192.168.0.10:8000/
   ```

Não exponha a porta `8000` diretamente para a internet sem um planejamento específico de segurança, HTTPS, domínio e regras de firewall.

## Firewall do Windows

Para liberar acesso na rede local:

1. Abra **Segurança do Windows**.
2. Acesse **Firewall e proteção de rede**.
3. Clique em **Configurações avançadas**.
4. Crie uma **Regra de Entrada** para a porta TCP `8000`.
5. Permita somente em redes privadas ou no perfil de rede usado pela empresa.
6. Evite liberar a porta para redes públicas.

Também confirme que a rede atual está marcada como **Rede privada**.

## Backup

O diretório `C:\SistemaGestaoAgro\backups` é criado para armazenar backups locais.

Recomendações:

1. Use `pg_dump` para backup do PostgreSQL.
2. Faça cópia da pasta `C:\SistemaGestaoAgro\media`.
3. Agende a rotina no **Agendador de Tarefas** do Windows.
4. Copie backups para mídia externa ou armazenamento seguro.
5. Teste a restauração periodicamente.

Se desejar usar o script PowerShell existente no projeto, ajuste as variáveis e execute como administrador:

```powershell
powershell -ExecutionPolicy Bypass -File C:\SistemaGestaoAgro\app\scripts\backup_windows.ps1
```

## Logs

Os logs do serviço ficam em:

```text
C:\SistemaGestaoAgro\logs\service.out.log
C:\SistemaGestaoAgro\logs\service.err.log
```

Consulte esses arquivos quando o serviço não iniciar ou quando o sistema retornar erro.

## Problemas comuns



### `[SC] EnumQueryServicesStatus:OpenService FALHA 1060`

Esse erro significa que o Windows não encontrou um serviço chamado `SistemaGestaoAgro`. Normalmente isso acontece quando a instalação falhou antes da etapa de registro no NSSM, por exemplo por falta de Python, NSSM, dependências Python ou conexão com PostgreSQL durante o `migrate`.

Para corrigir:

1. Abra o Prompt de Comando como Administrador.
2. Execute novamente o instalador manualmente para ver a saída completa:

   ```bat
   C:\SistemaGestaoAgro\app\deploy\windows\install.bat
   ```

3. Consulte o log da instalação:

   ```text
   C:\SistemaGestaoAgro\logs\install.log
   ```

4. Corrija o primeiro erro indicado no log. Os casos mais comuns são:
   - `nssm` não encontrado: coloque `nssm.exe` em `C:\SistemaGestaoAgro\app\deploy\windows\nssm.exe` ou no `PATH`;
   - PostgreSQL parado ou credenciais incorretas no `.env`;
   - `waitress-serve.exe` ausente por falha no `pip install -r requirements.txt`;
   - Python não instalado no `PATH`.

5. Depois rode novamente:

   ```bat
   C:\SistemaGestaoAgro\app\deploy\windows\install.bat
   ```

6. Valide se o serviço foi criado:

   ```bat
   sc query SistemaGestaoAgro
   ```

### Atalho da área de trabalho não abre nada

O atalho da área de trabalho executa `open_system.bat`, que abre `http://localhost:8000/` no navegador padrão e avisa se o serviço não estiver em execução.

Se nada aparecer:

1. Abra o Prompt de Comando como Administrador.
2. Verifique se o serviço existe e está rodando:

   ```bat
   sc query SistemaGestaoAgro
   ```

3. Tente iniciar o serviço manualmente:

   ```bat
   C:\SistemaGestaoAgro\app\deploy\windows\start_service.bat
   ```

4. Abra o endereço diretamente no navegador:

   ```text
   http://localhost:8000/
   ```

5. Se o navegador mostrar erro de conexão, consulte os logs em `C:\SistemaGestaoAgro\logs\service.err.log` e `C:\SistemaGestaoAgro\logs\service.out.log`.

### `python` não encontrado

Reinstale o Python marcando **Add python.exe to PATH** ou ajuste o `PATH` do sistema.

### `nssm` não encontrado

O instalador tenta baixar o NSSM automaticamente com `get_nssm.ps1`. Se aparecer `NSSM nao encontrado` ou `nao foi possivel baixar/preparar o NSSM automaticamente`, há duas opções:

1. Execute novamente o instalador com internet liberada para `https://nssm.cc/`; ou
2. Baixe manualmente o NSSM, extraia o ZIP e copie o executável para:

   ```text
   C:\SistemaGestaoAgro\app\deploy\windows\nssm.exe
   ```

Depois rode novamente como Administrador:

```bat
C:\SistemaGestaoAgro\app\deploy\windows\install.bat
```


### Serviço fica `SERVICE_PAUSED` ou não inicia após o NSSM

Se o log mostrar `Unexpected status SERVICE_PAUSED in response to START control`, o serviço foi criado, mas o processo do Django/Waitress não permaneceu em execução. O instalador agora configura o NSSM para chamar o Python do ambiente virtual com `python -m waitress`, aguarda o serviço entrar em `RUNNING` e imprime as últimas linhas de `service.err.log` e `service.out.log` quando houver falha.

Para diagnosticar manualmente no Windows:

```bat
cd /d C:\SistemaGestaoAgro\app
C:\SistemaGestaoAgro\venv\Scripts\python.exe -m waitress --listen=0.0.0.0:8000 sistema_gestao.wsgi:application
```

Se o comando manual falhar, corrija o erro exibido no console. Causas comuns:

- porta `8000` já em uso por outro processo;
- erro no `.env`;
- banco PostgreSQL inacessível no momento em que o serviço inicia;
- dependência Python ausente ou quebrada;
- erro de importação ao carregar `sistema_gestao.wsgi`.

Também verifique:

```bat
type C:\SistemaGestaoAgro\logs\service.err.log
type C:\SistemaGestaoAgro\logs\service.out.log
netstat -ano | findstr :8000
```

### `waitress-serve.exe` não encontrado

Confirme que `waitress` está em `requirements.txt` e execute novamente:

```bat
C:\SistemaGestaoAgro\venv\Scripts\pip.exe install -r C:\SistemaGestaoAgro\app\requirements.txt
```

### Erro ao conectar no PostgreSQL

Se o log mostrar `connection refused`, `porta 5432`, `Is the server running on that host`, `codec can't decode byte` ou a mensagem `PostgreSQL nao esta acessivel`, a instalação parou antes de registrar o serviço porque o instalador não conseguiu acessar o banco.

Verifique:

- se o PostgreSQL está instalado;
- se o serviço do PostgreSQL está iniciado no Windows;
- se o banco `sistema_gestao` foi criado;
- se usuário e senha em `C:\SistemaGestaoAgro\app\.env` estão corretos;
- se `POSTGRES_HOST=localhost` e `POSTGRES_PORT=5432` correspondem à instalação local;
- se firewall/antivírus não estão bloqueando conexões locais;
- se mensagens com `codec can't decode byte` aparecem, trate como erro de conexão/autenticação do PostgreSQL em Windows localizado e confira principalmente serviço, porta, banco, usuário e senha.

Comandos úteis no Windows:

```bat
sc query postgresql-x64-16
netstat -ano | findstr :5432
```

O nome exato do serviço pode variar conforme a versão instalada do PostgreSQL, por exemplo `postgresql-x64-15`, `postgresql-x64-16` ou `postgresql-x64-17`.

Depois de iniciar/corrigir o PostgreSQL, rode novamente como Administrador:

```bat
C:\SistemaGestaoAgro\app\deploy\windows\install.bat
```

### Erro `DisallowedHost`

Inclua `localhost`, `127.0.0.1`, o IP do servidor ou o nome da máquina em `ALLOWED_HOSTS` no `.env` e reinicie o serviço.

### Arquivos estáticos não carregam

Execute:

```bat
C:\SistemaGestaoAgro\venv\Scripts\python.exe C:\SistemaGestaoAgro\app\manage.py collectstatic --noinput
```

Depois reinicie o serviço.

### Serviço não inicia

1. Veja `C:\SistemaGestaoAgro\logs\service.err.log`.
2. Confirme as variáveis do `.env`.
3. Rode manualmente para ver o erro:

   ```bat
   cd /d C:\SistemaGestaoAgro\app
   C:\SistemaGestaoAgro\venv\Scripts\waitress-serve.exe --listen=0.0.0.0:8000 sistema_gestao.wsgi:application
   ```
