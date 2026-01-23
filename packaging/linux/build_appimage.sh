#!/bin/bash
# Build AppImage for Transcripter
# Requires: appimagetool

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
DIST_DIR="$PROJECT_ROOT/dist"
APPDIR="$DIST_DIR/Transcripter.AppDir"
VERSION="1.0.0"

echo "========================================"
echo "Building Transcripter AppImage"
echo "========================================"
echo ""

# Check if PyInstaller build exists
if [ ! -f "$DIST_DIR/Transcripter" ]; then
    echo "Error: PyInstaller build not found at $DIST_DIR/Transcripter"
    echo "Run 'python scripts/build.py' first"
    exit 1
fi

# Check for appimagetool
APPIMAGETOOL=""
if command -v appimagetool &> /dev/null; then
    APPIMAGETOOL="appimagetool"
elif [ -f "$HOME/appimagetool-x86_64.AppImage" ]; then
    APPIMAGETOOL="$HOME/appimagetool-x86_64.AppImage"
elif [ -f "/tmp/appimagetool-x86_64.AppImage" ]; then
    APPIMAGETOOL="/tmp/appimagetool-x86_64.AppImage"
else
    echo "appimagetool not found. Downloading..."
    wget -q -O /tmp/appimagetool-x86_64.AppImage \
        "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage"
    chmod +x /tmp/appimagetool-x86_64.AppImage
    APPIMAGETOOL="/tmp/appimagetool-x86_64.AppImage"
fi

echo "Using appimagetool: $APPIMAGETOOL"

# Clean previous AppDir
rm -rf "$APPDIR"
mkdir -p "$APPDIR/usr/bin"
mkdir -p "$APPDIR/usr/share/applications"
mkdir -p "$APPDIR/usr/share/icons/hicolor/512x512/apps"
mkdir -p "$APPDIR/usr/share/icons/hicolor/256x256/apps"
mkdir -p "$APPDIR/usr/share/icons/hicolor/128x128/apps"
mkdir -p "$APPDIR/usr/share/icons/hicolor/64x64/apps"

# Copy executable
cp "$DIST_DIR/Transcripter" "$APPDIR/usr/bin/"

# Copy desktop file
cp "$SCRIPT_DIR/transcripter.desktop" "$APPDIR/"
cp "$SCRIPT_DIR/transcripter.desktop" "$APPDIR/usr/share/applications/"

# Copy icons
ASSETS_DIR="$PROJECT_ROOT/packaging/assets"
cp "$ASSETS_DIR/transcripter.png" "$APPDIR/transcripter.png"
cp "$ASSETS_DIR/transcripter.png" "$APPDIR/usr/share/icons/hicolor/512x512/apps/transcripter.png"
cp "$ASSETS_DIR/transcripter_256.png" "$APPDIR/usr/share/icons/hicolor/256x256/apps/transcripter.png"
cp "$ASSETS_DIR/transcripter_128.png" "$APPDIR/usr/share/icons/hicolor/128x128/apps/transcripter.png"
cp "$ASSETS_DIR/transcripter_64.png" "$APPDIR/usr/share/icons/hicolor/64x64/apps/transcripter.png"

# Create AppRun script
cat > "$APPDIR/AppRun" << 'EOF'
#!/bin/bash
SELF=$(readlink -f "$0")
HERE=${SELF%/*}
export PATH="${HERE}/usr/bin:${PATH}"
export LD_LIBRARY_PATH="${HERE}/usr/lib:${LD_LIBRARY_PATH}"
exec "${HERE}/usr/bin/Transcripter" "$@"
EOF
chmod +x "$APPDIR/AppRun"

# Determine architecture
ARCH=$(uname -m)

# Build AppImage
echo ""
echo "Building AppImage..."
APPIMAGE_NAME="Transcripter-${VERSION}-${ARCH}.AppImage"
ARCH="$ARCH" "$APPIMAGETOOL" "$APPDIR" "$DIST_DIR/$APPIMAGE_NAME"

# Clean up AppDir
rm -rf "$APPDIR"

echo ""
echo "========================================"
echo "AppImage built successfully!"
echo "========================================"
echo ""
echo "Output: $DIST_DIR/$APPIMAGE_NAME"
echo ""
echo "To run:"
echo "  chmod +x $DIST_DIR/$APPIMAGE_NAME"
echo "  $DIST_DIR/$APPIMAGE_NAME"
