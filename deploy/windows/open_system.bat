@echo off
setlocal EnableExtensions EnableDelayedExpansion

set "APP_URL=http://localhost:8000/"
set "SERVICE_NAME=SistemaGestaoAgro"
set "SCRIPT_DIR=%~dp0"
set "LOG_DIR=C:\SistemaGestaoAgro\logs"
set "HAS_WARNING=0"

sc query "%SERVICE_NAME%" >nul 2>&1
if errorlevel 1 (
    echo Aviso: o servico %SERVICE_NAME% nao foi encontrado.
    echo A instalacao provavelmente falhou antes do registro do servico.
    echo Verifique %LOG_DIR%\install.log.
    set "HAS_WARNING=1"
) else (
    sc query "%SERVICE_NAME%" | find /I "RUNNING" >nul 2>&1
    if errorlevel 1 (
        echo Aviso: o servico %SERVICE_NAME% nao esta em execucao.
        echo Tentando iniciar o servico automaticamente...
        powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process -FilePath '%SCRIPT_DIR%start_service.bat' -Verb RunAs -Wait"

        for /L %%I in (1,1,15) do (
            sc query "%SERVICE_NAME%" | find /I "RUNNING" >nul 2>&1
            if not errorlevel 1 goto service_ready
            timeout /t 2 /nobreak >nul
        )

        echo Aviso: nao foi possivel confirmar o servico em execucao.
        echo Se a janela de permissao do Windows apareceu, confirme e tente novamente.
        echo Se continuar falhando, verifique %LOG_DIR%\service.err.log.
        echo Voce tambem pode testar manualmente: %SCRIPT_DIR%run_waitress.bat
        set "HAS_WARNING=1"
    )
)

goto open_browser

:service_ready
echo Servico %SERVICE_NAME% iniciado com sucesso.

:open_browser
start "" "%APP_URL%"
if "%HAS_WARNING%"=="1" (
    echo.
    echo O navegador foi aberto, mas o servico precisa estar em execucao para o sistema responder.
    pause
)
endlocal
