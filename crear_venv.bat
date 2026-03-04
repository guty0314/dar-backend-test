@echo off
for /f "delims=" %%i in ('python --version') do set VERSION=%%i
echo Creando entorno virtual usando %VERSION%...
python -m venv venv
echo Creado entorno virtual con exito. Ejecutando entorno virtual...
call venv\Scripts\activate
echo Instalando librerias...
pip install -r requirements.txt
echo FINALIZADO
pause
