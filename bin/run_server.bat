@echo off
REM Flask 서버 실행 스크립트 (Windows)
REM US Market Alpha Platform Web Server

cd /d "%~dp0\.."

echo 🚀 Starting Flask server...
echo 📁 Working directory: %CD%

REM Python 가상환경 활성화 (있는 경우)
if exist "venv\Scripts\activate.bat" (
    echo 🔧 Activating virtual environment...
    call venv\Scripts\activate.bat
) else if exist ".venv\Scripts\activate.bat" (
    echo 🔧 Activating virtual environment...
    call .venv\Scripts\activate.bat
)

REM 서버 실행
python web\app.py

pause

