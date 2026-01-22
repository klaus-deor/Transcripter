@echo off
REM =============================================================================
REM Transcripter - Windows Installation Script
REM =============================================================================

echo ========================================
echo   Transcripter - Windows Installer
echo ========================================
echo.

REM Check for Python
echo Checking Python version...
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH.
    echo Please install Python 3.8+ from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

python -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"
if errorlevel 1 (
    echo Error: Python 3.8+ is required.
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"') do set PYTHON_VERSION=%%i
echo Python %PYTHON_VERSION% detected.

REM Create virtual environment
echo.
echo Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo.
echo Upgrading pip...
pip install --upgrade pip

REM Install dependencies
echo.
echo Installing dependencies...
pip install -r requirements.txt

REM Install optional Windows dependencies
echo.
echo Installing optional Windows dependencies...
pip install win10toast

REM Install Transcripter
echo.
echo Installing Transcripter...
pip install -e .

echo.
echo ========================================
echo   Installation Complete!
echo ========================================
echo.
echo To run Transcripter:
echo.
echo   1. Activate the virtual environment:
echo      venv\Scripts\activate.bat
echo.
echo   2. Run the application:
echo      transcripter-cross
echo.
echo   3. Configure your Groq API key in Settings
echo      Get your API key at: https://console.groq.com/
echo.
echo Default hotkey: Ctrl+Alt+R (toggle recording)
echo.
pause
