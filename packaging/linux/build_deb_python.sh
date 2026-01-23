#!/bin/bash
# Build .deb package for Transcripter (Python version)
# Installs Python package with system GTK - more reliable than PyInstaller

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
DIST_DIR="$PROJECT_ROOT/dist"
VERSION="1.0.0"
PACKAGE_NAME="deor-transcripter"
ARCH="all"  # Python is architecture-independent

echo "========================================"
echo "Building Transcripter .deb (Python)"
echo "========================================"
echo ""

# Create package directory structure
DEB_DIR="$DIST_DIR/${PACKAGE_NAME}_${VERSION}_${ARCH}"
rm -rf "$DEB_DIR"
mkdir -p "$DEB_DIR/DEBIAN"
mkdir -p "$DEB_DIR/opt/transcripter"
mkdir -p "$DEB_DIR/usr/share/applications"
mkdir -p "$DEB_DIR/usr/share/icons/hicolor/512x512/apps"
mkdir -p "$DEB_DIR/usr/share/icons/hicolor/256x256/apps"
mkdir -p "$DEB_DIR/usr/share/icons/hicolor/128x128/apps"
mkdir -p "$DEB_DIR/usr/share/icons/hicolor/64x64/apps"
mkdir -p "$DEB_DIR/usr/share/icons/hicolor/48x48/apps"
mkdir -p "$DEB_DIR/usr/bin"

# Copy Python package
cp -r "$PROJECT_ROOT/transcripter" "$DEB_DIR/opt/transcripter/"
cp -r "$PROJECT_ROOT/config" "$DEB_DIR/opt/transcripter/"
cp "$PROJECT_ROOT/requirements.txt" "$DEB_DIR/opt/transcripter/"

# Create launcher script
cat > "$DEB_DIR/usr/bin/transcripter" << 'LAUNCHER'
#!/bin/bash
# Transcripter launcher
cd /opt/transcripter
exec ./venv/bin/python -m transcripter "$@"
LAUNCHER
chmod 755 "$DEB_DIR/usr/bin/transcripter"

# Create toggle script for system shortcut
cat > "$DEB_DIR/usr/bin/transcripter-toggle" << 'TOGGLE'
#!/bin/bash
# Toggle Transcripter recording via USR1 signal

# Try multiple patterns to find the process
PID=""

# Pattern 1: Find by module name
PID=$(pgrep -f "python.*transcripter" 2>/dev/null | head -1)

# Pattern 2: Find by script path
if [ -z "$PID" ]; then
    PID=$(pgrep -f "/opt/transcripter" 2>/dev/null | head -1)
fi

# Pattern 3: Find by process name containing transcripter
if [ -z "$PID" ]; then
    PID=$(ps aux | grep -i "[t]ranscripter" | grep -v "transcripter-toggle" | awk '{print $2}' | head -1)
fi

if [ -n "$PID" ]; then
    echo "Sending USR1 signal to PID $PID"
    kill -USR1 "$PID"
else
    echo "Transcripter not running, starting..."
    /usr/bin/transcripter &
fi
TOGGLE
chmod 755 "$DEB_DIR/usr/bin/transcripter-toggle"

# Copy icons
ASSETS_DIR="$PROJECT_ROOT/packaging/assets"
cp "$ASSETS_DIR/transcripter.png" "$DEB_DIR/usr/share/icons/hicolor/512x512/apps/transcripter.png"
cp "$ASSETS_DIR/transcripter_256.png" "$DEB_DIR/usr/share/icons/hicolor/256x256/apps/transcripter.png"
cp "$ASSETS_DIR/transcripter_128.png" "$DEB_DIR/usr/share/icons/hicolor/128x128/apps/transcripter.png"
cp "$ASSETS_DIR/transcripter_64.png" "$DEB_DIR/usr/share/icons/hicolor/64x64/apps/transcripter.png"
cp "$ASSETS_DIR/transcripter_48.png" "$DEB_DIR/usr/share/icons/hicolor/48x48/apps/transcripter.png"

# Create .desktop file
cat > "$DEB_DIR/usr/share/applications/transcripter.desktop" << 'EOF'
[Desktop Entry]
Name=Deor Transcripter
Comment=Transcreva audio para texto com IA
GenericName=Audio Transcription
Exec=transcripter
Icon=transcripter
Type=Application
Categories=AudioVideo;Audio;Utility;
Keywords=transcription;audio;speech;voice;whisper;deor;
StartupNotify=true
Terminal=false
EOF

# Create control file
cat > "$DEB_DIR/DEBIAN/control" << EOF
Package: $PACKAGE_NAME
Version: $VERSION
Section: utils
Priority: optional
Architecture: $ARCH
Depends: python3 (>= 3.9), python3-pip, python3-venv, python3-gi, gir1.2-gtk-3.0, gir1.2-appindicator3-0.1, libnotify4, libportaudio2, libsndfile1
Maintainer: Klaus Deor <klaus@deor.dev>
Description: Audio transcription tool with AI
 Transcripter converts speech to text using multiple AI providers
 including Groq, OpenAI, AssemblyAI, Deepgram, and Google Cloud.
 .
 Features:
  - Global hotkey (Ctrl+Alt+R) to start/stop recording
  - Automatic clipboard copy of transcribed text
  - Multiple transcription providers
  - System tray integration with native GTK
Homepage: https://github.com/klaus-deor/Deor-Transcripter
Bugs: https://github.com/klaus-deor/Deor-Transcripter/issues
EOF

# Create postinst script
cat > "$DEB_DIR/DEBIAN/postinst" << 'EOF'
#!/bin/bash
set -e

echo "Creating virtual environment..."
cd /opt/transcripter
python3 -m venv venv --system-site-packages

echo "Installing Python dependencies..."
./venv/bin/pip install -q -r requirements.txt

# Update icon cache
if command -v gtk-update-icon-cache &> /dev/null; then
    gtk-update-icon-cache -f -t /usr/share/icons/hicolor || true
fi

# Update desktop database
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database /usr/share/applications || true
fi

echo ""
echo "============================================"
echo "  Deor Transcripter instalado com sucesso!"
echo "============================================"
echo ""
echo "  Abra pelo menu de aplicativos ou execute:"
echo "  $ transcripter"
echo ""
echo "  Primeira vez? Configure sua API key em Settings"
echo "  Recomendado: Groq (gratis) - https://console.groq.com"
echo ""
EOF
chmod 755 "$DEB_DIR/DEBIAN/postinst"

# Create postrm script
cat > "$DEB_DIR/DEBIAN/postrm" << 'EOF'
#!/bin/bash
set -e

# Update icon cache
if command -v gtk-update-icon-cache &> /dev/null; then
    gtk-update-icon-cache -f -t /usr/share/icons/hicolor || true
fi

# Update desktop database
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database /usr/share/applications || true
fi
EOF
chmod 755 "$DEB_DIR/DEBIAN/postrm"

# Build the .deb package
echo "Building .deb package..."
mkdir -p "$DIST_DIR"
DEB_OUTPUT="$DIST_DIR/${PACKAGE_NAME}_${VERSION}_${ARCH}.deb"
dpkg-deb --build "$DEB_DIR" "$DEB_OUTPUT"

# Clean up
rm -rf "$DEB_DIR"

echo ""
echo "========================================"
echo ".deb Package built successfully!"
echo "========================================"
echo ""
echo "Output: $DEB_OUTPUT"
echo ""
echo "To install:"
echo "  sudo dpkg -i $DEB_OUTPUT"
echo ""
