@echo off
setlocal EnableExtensions EnableDelayedExpansion

set "APP_URL=http://localhost:8000/"
set "SERVICE_NAME=SistemaGestaoAgro"
set "SCRIPT_DIR=%~dp0"
set "LOG_DIR=C:\SistemaGestaoAgro\logs"
set "RUN_WAITRESS_BAT=%SCRIPT_DIR%run_waitress.bat"
set "HAS_WARNING=0"

sc query "%SERVICE_NAME%" >nul 2>&1
if errorlevel 1 (
    echo Aviso: o servico %SERVICE_NAME% nao foi encontrado.
    echo A instalacao provavelmente falhou antes do registro do servico.
    echo Verifique %LOG_DIR%\install.log.
    set "HAS_WARNING=1"
    goto start_direct_waitress
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
        echo Tentando iniciar a aplicacao diretamente com run_waitress.bat...
        set "HAS_WARNING=1"
        goto start_direct_waitress
    )
)

goto open_browser

:service_ready
echo Servico %SERVICE_NAME% iniciado com sucesso.
goto open_browser

:start_direct_waitress
if not exist "%RUN_WAITRESS_BAT%" (
    echo ERRO: nao encontrei %RUN_WAITRESS_BAT%.
    echo Se continuar falhando, verifique %LOG_DIR%\service.err.log.
    goto open_browser
)

echo Iniciando Waitress diretamente em janela minimizada...
start "SistemaGestaoAgro Waitress" /min "%ComSpec%" /c ""%RUN_WAITRESS_BAT%""

for /L %%I in (1,1,15) do (
    powershell -NoProfile -Command "$c=New-Object Net.Sockets.TcpClient; try { $c.Connect('127.0.0.1',8000); $c.Close(); exit 0 } catch { exit 1 }" >nul 2>&1
    if not errorlevel 1 goto direct_ready
    timeout /t 2 /nobreak >nul
)

echo Aviso: nao foi possivel confirmar resposta na porta 8000.
echo Verifique %LOG_DIR%\service.err.log ou execute manualmente: %RUN_WAITRESS_BAT%
goto open_browser

:direct_ready
echo Aplicacao iniciada diretamente em http://localhost:8000/.
set "HAS_WARNING=0"

:open_browser
start "" "%APP_URL%"
if "%HAS_WARNING%"=="1" (
    echo.
    echo O navegador foi aberto, mas o servico precisa estar em execucao para o sistema responder.
    echo Como alternativa, confirme se a janela minimizada do Waitress esta aberta.
    pause
)
endlocal
