#!/bin/bash
# Build .deb package for Transcripter
# Creates a proper Debian package that installs like any other app

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
DIST_DIR="$PROJECT_ROOT/dist"
VERSION="1.0.0"
PACKAGE_NAME="transcripter"
ARCH="amd64"

echo "========================================"
echo "Building Transcripter .deb Package"
echo "========================================"
echo ""

# Check if PyInstaller build exists
if [ ! -f "$DIST_DIR/Transcripter" ]; then
    echo "Error: PyInstaller build not found at $DIST_DIR/Transcripter"
    echo "Run 'python scripts/build.py' first"
    exit 1
fi

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

# Copy executable
cp "$DIST_DIR/Transcripter" "$DEB_DIR/opt/transcripter/"
chmod 755 "$DEB_DIR/opt/transcripter/Transcripter"

# Create symlink in /usr/bin
ln -s /opt/transcripter/Transcripter "$DEB_DIR/usr/bin/transcripter"

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
Name=Transcripter
Comment=Transcreva audio para texto com IA
GenericName=Audio Transcription
Exec=/opt/transcripter/Transcripter
Icon=transcripter
Type=Application
Categories=AudioVideo;Audio;Utility;
Keywords=transcription;audio;speech;voice;whisper;
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
Depends: libgtk-3-0, libayatana-appindicator3-1 | libappindicator3-1, libnotify4
Maintainer: Klaus Deor <klaus@deor.dev>
Description: Audio transcription tool with AI
 Transcripter converts speech to text using multiple AI providers
 including Groq, OpenAI, AssemblyAI, Deepgram, and Google Cloud.
 .
 Features:
  - Global hotkey (Ctrl+Alt+R) to start/stop recording
  - Automatic clipboard copy of transcribed text
  - Multiple transcription providers
  - System tray integration
Homepage: https://github.com/klaus-deor/Transcripter
EOF

# Create postinst script (runs after installation)
cat > "$DEB_DIR/DEBIAN/postinst" << 'EOF'
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

echo ""
echo "============================================"
echo "  Transcripter instalado com sucesso!"
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

# Create postrm script (runs after removal)
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
dpkg-deb --build "$DEB_DIR"

# Rename to standard format
mv "$DEB_DIR.deb" "$DIST_DIR/transcripter_${VERSION}_${ARCH}.deb"

# Clean up
rm -rf "$DEB_DIR"

echo ""
echo "========================================"
echo ".deb Package built successfully!"
echo "========================================"
echo ""
echo "Output: $DIST_DIR/transcripter_${VERSION}_${ARCH}.deb"
echo ""
echo "To install:"
echo "  sudo dpkg -i $DIST_DIR/transcripter_${VERSION}_${ARCH}.deb"
echo ""
echo "Or just double-click the .deb file!"
echo ""
