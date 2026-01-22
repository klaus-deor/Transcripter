#!/bin/bash
# =============================================================================
# Transcripter - macOS Installation Script
# =============================================================================

set -e

echo "========================================"
echo "  Transcripter - macOS Installer"
echo "========================================"
echo ""

# Check for Python 3.8+
echo "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed."
    echo "Please install Python 3.8+ from https://www.python.org/downloads/"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
    echo "Error: Python 3.8+ is required. Found Python $PYTHON_VERSION"
    exit 1
fi

echo "Python $PYTHON_VERSION detected."

# Check for Homebrew (optional, for portaudio)
echo ""
echo "Checking for Homebrew..."
if command -v brew &> /dev/null; then
    echo "Homebrew detected. Installing portaudio..."
    brew install portaudio 2>/dev/null || echo "portaudio already installed or installation skipped"
else
    echo "Homebrew not found. You may need to install portaudio manually."
    echo "Install Homebrew from https://brew.sh and run: brew install portaudio"
fi

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

# Install Transcripter
echo ""
echo "Installing Transcripter..."
pip install -e .

echo ""
echo "========================================"
echo "  Installation Complete!"
echo "========================================"
echo ""
echo "To run Transcripter:"
echo ""
echo "  1. Activate the virtual environment:"
echo "     source venv/bin/activate"
echo ""
echo "  2. Run the application:"
echo "     transcripter-cross"
echo ""
echo "  3. Configure your Groq API key in Settings"
echo "     Get your API key at: https://console.groq.com/"
echo ""
echo "Default hotkey: Ctrl+Option+R (toggle recording)"
echo ""
echo "Note: On macOS, you may need to grant accessibility"
echo "permissions for global hotkeys to work."
echo ""
