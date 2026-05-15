@echo off
setlocal EnableExtensions

set "APP_URL=http://localhost:8000/"
set "SERVICE_NAME=SistemaGestaoAgro"
set "HAS_WARNING=0"

sc query "%SERVICE_NAME%" >nul 2>&1
if errorlevel 1 (
    echo Aviso: o servico %SERVICE_NAME% nao foi encontrado.
    echo A instalacao provavelmente falhou antes do registro do servico.
    echo Verifique C:\SistemaGestaoAgro\logs\install.log.
    set "HAS_WARNING=1"
) else (
    sc query "%SERVICE_NAME%" | find /I "RUNNING" >nul 2>&1
    if errorlevel 1 (
        echo Aviso: o servico %SERVICE_NAME% nao esta em execucao.
        echo Tente iniciar pelo menu Iniciar ou execute start_service.bat como Administrador.
        echo Se falhar, verifique C:\SistemaGestaoAgro\logs\service.err.log.
        set "HAS_WARNING=1"
    )
)

start "" "%APP_URL%"
if "%HAS_WARNING%"=="1" (
    echo.
    echo O navegador foi aberto, mas o servico precisa ser corrigido para o sistema responder.
    pause
)
endlocal
