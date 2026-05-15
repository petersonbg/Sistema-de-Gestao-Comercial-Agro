@echo off
setlocal EnableExtensions
set "SERVICE_NAME=SistemaGestaoAgro"
set "NSSM_EXE=nssm"
if exist "%~dp0nssm.exe" set "NSSM_EXE=%~dp0nssm.exe"
"%NSSM_EXE%" restart %SERVICE_NAME%
endlocal
