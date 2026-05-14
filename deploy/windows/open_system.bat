@echo off
setlocal EnableExtensions

set "APP_URL=http://localhost:8000/"
set "SERVICE_NAME=SistemaGestaoAgro"

sc query "%SERVICE_NAME%" >nul 2>&1
if errorlevel 1 (
    echo Aviso: o servico %SERVICE_NAME% nao foi encontrado.
    echo Execute o instalador novamente como Administrador ou verifique a instalacao.
) else (
    sc query "%SERVICE_NAME%" | find /I "RUNNING" >nul 2>&1
    if errorlevel 1 (
        echo Aviso: o servico %SERVICE_NAME% nao esta em execucao.
        echo Tente iniciar pelo menu Iniciar ou execute start_service.bat como Administrador.
    )
)

start "" "%APP_URL%"
endlocal
