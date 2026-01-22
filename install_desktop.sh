#!/bin/bash
# Script to install Transcripter desktop integration

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
DESKTOP_FILE="$SCRIPT_DIR/transcripter.desktop"
DESKTOP_FILE_INSTALLED="$HOME/.local/share/applications/transcripter.desktop"
AUTOSTART_FILE="$HOME/.config/autostart/transcripter.desktop"

echo "Installing Transcripter desktop integration..."
echo ""

# Create directories if they don't exist
mkdir -p "$HOME/.local/share/applications"
mkdir -p "$HOME/.config/autostart"

# Copy desktop file to applications
echo "Installing application launcher..."
cp "$DESKTOP_FILE" "$DESKTOP_FILE_INSTALLED"
chmod +x "$DESKTOP_FILE_INSTALLED"

# Update desktop database
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database "$HOME/.local/share/applications"
fi

echo "\u2713 Application launcher installed"
echo ""

# Ask if user wants autostart
read -p "Do you want Transcripter to start automatically on login? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    cp "$DESKTOP_FILE" "$AUTOSTART_FILE"
    chmod +x "$AUTOSTART_FILE"
    echo "\u2713 Autostart enabled"
else
    # Remove autostart if it exists
    if [ -f "$AUTOSTART_FILE" ]; then
        rm "$AUTOSTART_FILE"
    fi
    echo "\u2713 Autostart disabled"
fi

echo ""
echo "==================================="
echo "Desktop integration installed!"
echo "==================================="
echo ""
echo "You can now:"
echo "1. Find 'Transcripter' in your application menu"
echo "2. Run it without keeping the terminal open"
echo ""
echo "To enable/disable autostart later:"
echo "  Enable:  cp transcripter.desktop ~/.config/autostart/"
echo "  Disable: rm ~/.config/autostart/transcripter.desktop"
echo ""
echo "To uninstall:"
echo "  rm ~/.local/share/applications/transcripter.desktop"
echo "  rm ~/.config/autostart/transcripter.desktop"
echo ""
