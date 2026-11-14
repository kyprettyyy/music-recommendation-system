@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    python -m venv .venv
    if errorlevel 1 goto fail
)
".venv\Scripts\python.exe" -m pip install -r requirements-core.txt
if errorlevel 1 goto fail
if not exist "recommend\db.sqlite3" set INIT_DEMO=1
".venv\Scripts\python.exe" recommend\manage.py migrate
if errorlevel 1 goto fail
if defined INIT_DEMO (
    ".venv\Scripts\python.exe" recommend\manage.py seed_demo
    if errorlevel 1 goto fail
)
".venv\Scripts\python.exe" recommend\manage.py build_features --demo
if errorlevel 1 goto fail
echo Open http://127.0.0.1:8000/ after the server starts.
".venv\Scripts\python.exe" recommend\manage.py runserver
goto :eof
:fail
echo Setup failed. See the error above and README.md. Python 3.11 is recommended.
pause
