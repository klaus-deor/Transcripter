@echo off
REM ============================================
REM Transcripter - Windows Build Script
REM Cria o executavel .exe automaticamente
REM ============================================

echo.
echo ========================================
echo    TRANSCRIPTER - Build para Windows
echo ========================================
echo.

REM Verificar se Python esta instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado!
    echo.
    echo Por favor, instale Python 3.10+ de:
    echo https://www.python.org/downloads/
    echo.
    echo Marque "Add Python to PATH" durante a instalacao!
    echo.
    pause
    exit /b 1
)

echo [OK] Python encontrado
python --version

REM Criar ambiente virtual se nao existir
if not exist "venv" (
    echo.
    echo [1/4] Criando ambiente virtual...
    python -m venv venv
)

REM Ativar ambiente virtual
echo.
echo [2/4] Ativando ambiente virtual...
call venv\Scripts\activate.bat

REM Instalar dependencias
echo.
echo [3/4] Instalando dependencias (pode demorar alguns minutos)...
pip install --upgrade pip >nul
pip install -r requirements.txt
pip install pyinstaller pillow pywin32

REM Gerar icones se necessario
if not exist "packaging\assets\transcripter.png" (
    echo.
    echo Gerando icones...
    python scripts\generate_icons.py
)

REM Compilar executavel
echo.
echo [4/4] Compilando executavel...
echo.
python scripts\build.py --clean

echo.
echo ========================================
echo    BUILD CONCLUIDO!
echo ========================================
echo.
echo Executavel criado em:
echo    dist\Transcripter.exe
echo.
echo Para criar instalador NSIS (opcional):
echo    1. Instale NSIS: https://nsis.sourceforge.io/
echo    2. Abra packaging\windows\installer.nsi no NSIS
echo    3. Compile o instalador
echo.
pause
