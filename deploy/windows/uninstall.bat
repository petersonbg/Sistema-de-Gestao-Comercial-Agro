@echo off
setlocal EnableExtensions

set "SERVICE_NAME=SistemaGestaoAgro"
set "INSTALL_ROOT=C:\SistemaGestaoAgro"
set "NSSM_EXE=nssm"
set "SCRIPT_DIR=%~dp0"

net session >nul 2>&1
if errorlevel 1 (
    echo ERRO: execute este desinstalador como Administrador.
    exit /b 1
)

where %NSSM_EXE% >nul 2>&1
if errorlevel 1 (
    if exist "%SCRIPT_DIR%nssm.exe" (
        set "NSSM_EXE=%SCRIPT_DIR%nssm.exe"
    ) else (
        echo ERRO: NSSM nao encontrado no PATH nem em %SCRIPT_DIR%nssm.exe.
        echo O banco de dados, backups, media e arquivos da aplicacao nao foram alterados.
        exit /b 1
    )
)

"%NSSM_EXE%" status %SERVICE_NAME% >nul 2>&1
if errorlevel 1 (
    echo Servico %SERVICE_NAME% nao encontrado.
    echo Nada foi removido.
    exit /b 0
)

echo Parando servico %SERVICE_NAME%...
"%NSSM_EXE%" stop %SERVICE_NAME% >nul 2>&1

echo Removendo servico %SERVICE_NAME%...
"%NSSM_EXE%" remove %SERVICE_NAME% confirm
if errorlevel 1 exit /b 1

echo Servico removido.
echo Nenhum dado importante foi apagado.
echo Mantidos: banco PostgreSQL, %INSTALL_ROOT%, backups, media, logs e arquivos da aplicacao.
endlocal
