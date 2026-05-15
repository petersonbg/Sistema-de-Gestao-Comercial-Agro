@echo off
setlocal EnableExtensions

set "APP_DIR=C:\SistemaGestaoAgro\app"
set "VENV_PY=C:\SistemaGestaoAgro\venv\Scripts\python.exe"
set "WAITRESS_LISTEN=0.0.0.0:8000"
set "DJANGO_WSGI=sistema_gestao.wsgi:application"

cd /d "%APP_DIR%"
"%VENV_PY%" -m waitress --listen=%WAITRESS_LISTEN% %DJANGO_WSGI%
endlocal
