@echo off
setlocal EnableExtensions EnableDelayedExpansion

set "SERVICE_NAME=SistemaGestaoAgro"
set "INSTALL_ROOT=C:\SistemaGestaoAgro"
set "APP_DIR=%INSTALL_ROOT%\app"
set "LOG_DIR=%INSTALL_ROOT%\logs"
set "BACKUP_DIR=%INSTALL_ROOT%\backups"
set "MEDIA_DIR=%INSTALL_ROOT%\media"
set "VENV_DIR=%INSTALL_ROOT%\venv"
set "PYTHON_EXE=python"
set "NSSM_EXE=nssm"
set "PORT=8000"
set "LISTEN=0.0.0.0:%PORT%"
set "SCRIPT_DIR=%~dp0"
set "SOURCE_DIR=%SCRIPT_DIR%..\.."

net session >nul 2>&1
if errorlevel 1 (
    echo ERRO: execute este instalador como Administrador.
    echo Clique com o botao direito em install.bat e escolha "Executar como administrador".
    exit /b 1
)

for %%D in ("%INSTALL_ROOT%" "%APP_DIR%" "%LOG_DIR%" "%BACKUP_DIR%" "%MEDIA_DIR%") do (
    if not exist "%%~D" mkdir "%%~D"
)

if /I not "%CD%"=="%APP_DIR%" (
    if not exist "%APP_DIR%\manage.py" (
        echo Copiando arquivos da aplicacao para %APP_DIR%...
        robocopy "%SOURCE_DIR%" "%APP_DIR%" /E /XD .git .venv venv env __pycache__ backups media staticfiles deploy\windows\Output /XF *.pyc *.pyo >nul
        if errorlevel 8 (
            echo ERRO: falha ao copiar arquivos da aplicacao para %APP_DIR%.
            exit /b 1
        )
    ) else (
        echo Arquivos da aplicacao ja existem em %APP_DIR%.
    )
)

cd /d "%APP_DIR%"

if not exist "%APP_DIR%\media" (
    mklink /J "%APP_DIR%\media" "%MEDIA_DIR%" >nul 2>&1
)

where %PYTHON_EXE% >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python nao encontrado no PATH. Instale Python 3.11+ e marque "Add python.exe to PATH".
    exit /b 1
)

if not exist "%VENV_DIR%\Scripts\python.exe" (
    echo Criando ambiente virtual em %VENV_DIR%...
    %PYTHON_EXE% -m venv "%VENV_DIR%"
    if errorlevel 1 exit /b 1
) else (
    echo Ambiente virtual ja existe em %VENV_DIR%.
)

set "VENV_PY=%VENV_DIR%\Scripts\python.exe"
set "VENV_PIP=%VENV_DIR%\Scripts\pip.exe"
set "WAITRESS_EXE=%VENV_DIR%\Scripts\waitress-serve.exe"

echo Atualizando pip e instalando dependencias...
"%VENV_PY%" -m pip install --upgrade pip
if errorlevel 1 exit /b 1
"%VENV_PIP%" install -r "%APP_DIR%\requirements.txt"
if errorlevel 1 exit /b 1

if not exist "%WAITRESS_EXE%" (
    echo ERRO: waitress-serve.exe nao foi encontrado em %WAITRESS_EXE%.
    echo Confirme se waitress esta listado no requirements.txt e se a instalacao das dependencias concluiu sem erros.
    exit /b 1
)

if not exist "%APP_DIR%\.env" (
    echo Criando arquivo .env a partir de .env.example...
    copy "%APP_DIR%\.env.example" "%APP_DIR%\.env" >nul
    echo ATENCAO: revise %APP_DIR%\.env e configure SECRET_KEY, ALLOWED_HOSTS e PostgreSQL antes do uso em producao.
) else (
    echo Arquivo .env ja existe; mantendo configuracao atual.
)

echo Executando migracoes do banco de dados...
"%VENV_PY%" "%APP_DIR%\manage.py" migrate
if errorlevel 1 exit /b 1

echo Coletando arquivos estaticos...
"%VENV_PY%" "%APP_DIR%\manage.py" collectstatic --noinput
if errorlevel 1 exit /b 1

where %NSSM_EXE% >nul 2>&1
if errorlevel 1 (
    if exist "%SCRIPT_DIR%nssm.exe" (
        set "NSSM_EXE=%SCRIPT_DIR%nssm.exe"
    ) else (
        echo ERRO: NSSM nao encontrado no PATH nem em %SCRIPT_DIR%nssm.exe.
        echo Baixe o NSSM em https://nssm.cc/ e coloque nssm.exe no PATH ou nesta pasta.
        exit /b 1
    )
)

"%NSSM_EXE%" status %SERVICE_NAME% >nul 2>&1
if not errorlevel 1 (
    echo Servico %SERVICE_NAME% ja existe. Parando para atualizar configuracao...
    "%NSSM_EXE%" stop %SERVICE_NAME% >nul 2>&1
) else (
    echo Registrando servico %SERVICE_NAME%...
    "%NSSM_EXE%" install %SERVICE_NAME% "%WAITRESS_EXE%"
    if errorlevel 1 exit /b 1
)

"%NSSM_EXE%" set %SERVICE_NAME% AppDirectory "%APP_DIR%"
"%NSSM_EXE%" set %SERVICE_NAME% AppParameters --listen=%LISTEN% sistema_gestao.wsgi:application
"%NSSM_EXE%" set %SERVICE_NAME% DisplayName "Sistema Gestao Agro"
"%NSSM_EXE%" set %SERVICE_NAME% Description "Sistema de Gestao Comercial Agro - Django com Waitress"
"%NSSM_EXE%" set %SERVICE_NAME% Start SERVICE_AUTO_START
"%NSSM_EXE%" set %SERVICE_NAME% AppStdout "%LOG_DIR%\service.out.log"
"%NSSM_EXE%" set %SERVICE_NAME% AppStderr "%LOG_DIR%\service.err.log"
"%NSSM_EXE%" set %SERVICE_NAME% AppRotateFiles 1
"%NSSM_EXE%" set %SERVICE_NAME% AppRotateOnline 1
"%NSSM_EXE%" set %SERVICE_NAME% AppRotateBytes 10485760

if not exist "%LOG_DIR%\service.out.log" type nul > "%LOG_DIR%\service.out.log"
if not exist "%LOG_DIR%\service.err.log" type nul > "%LOG_DIR%\service.err.log"

echo Iniciando servico %SERVICE_NAME%...
"%NSSM_EXE%" start %SERVICE_NAME%
if errorlevel 1 exit /b 1

echo.
echo Instalacao concluida.
echo Aplicacao: %APP_DIR%
echo Logs: %LOG_DIR%
echo Backups: %BACKUP_DIR%
echo Media: %MEDIA_DIR%
echo Acesse no servidor: http://localhost:%PORT%/
echo Acesse na rede: http://IP_DO_SERVIDOR:%PORT%/
endlocal
