@echo off

set APP_HOME=%cd%
echo =============================
echo ADBFileExplorer: %APP_HOME%

set PYTHONUNBUFFERED=1
call %APP_HOME%\.venv\Scripts\activate.bat
python %APP_HOME%\src\main.py

@echo on
