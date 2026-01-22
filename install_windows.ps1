# =============================================================================
# Transcripter - Windows Installation Script (PowerShell)
# =============================================================================

Write-Host "========================================"
Write-Host "  Transcripter - Windows Installer"
Write-Host "========================================"
Write-Host ""

# Check for Python
Write-Host "Checking Python version..."
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Python not found"
    }
} catch {
    Write-Host "Error: Python is not installed or not in PATH." -ForegroundColor Red
    Write-Host "Please install Python 3.8+ from https://www.python.org/downloads/"
    Write-Host "Make sure to check 'Add Python to PATH' during installation."
    Read-Host "Press Enter to exit"
    exit 1
}

# Check Python version
$versionCheck = python -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Python 3.8+ is required." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

$pyVersion = python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
Write-Host "Python $pyVersion detected." -ForegroundColor Green

# Create virtual environment
Write-Host ""
Write-Host "Creating virtual environment..."
python -m venv venv

# Activate virtual environment
Write-Host "Activating virtual environment..."
& .\venv\Scripts\Activate.ps1

# Upgrade pip
Write-Host ""
Write-Host "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
Write-Host ""
Write-Host "Installing dependencies..."
pip install -r requirements.txt

# Install optional Windows dependencies
Write-Host ""
Write-Host "Installing optional Windows dependencies..."
pip install win10toast

# Install Transcripter
Write-Host ""
Write-Host "Installing Transcripter..."
pip install -e .

Write-Host ""
Write-Host "========================================"
Write-Host "  Installation Complete!" -ForegroundColor Green
Write-Host "========================================"
Write-Host ""
Write-Host "To run Transcripter:"
Write-Host ""
Write-Host "  1. Activate the virtual environment:"
Write-Host "     .\venv\Scripts\Activate.ps1" -ForegroundColor Cyan
Write-Host ""
Write-Host "  2. Run the application:"
Write-Host "     transcripter-cross" -ForegroundColor Cyan
Write-Host ""
Write-Host "  3. Configure your Groq API key in Settings"
Write-Host "     Get your API key at: https://console.groq.com/"
Write-Host ""
Write-Host "Default hotkey: Ctrl+Alt+R (toggle recording)"
Write-Host ""
Read-Host "Press Enter to exit"
