#!/bin/bash
# Create DMG installer for Transcripter on macOS
# Requires: create-dmg (brew install create-dmg)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
DIST_DIR="$PROJECT_ROOT/dist"
APP_PATH="$DIST_DIR/Transcripter.app"
VERSION="1.0.0"
DMG_NAME="Transcripter-${VERSION}"

echo "========================================"
echo "Creating Transcripter DMG"
echo "========================================"
echo ""

# Check if app exists
if [ ! -d "$APP_PATH" ]; then
    echo "Error: App bundle not found at $APP_PATH"
    echo "Run 'python scripts/build.py' first"
    exit 1
fi

# Check for create-dmg
if ! command -v create-dmg &> /dev/null; then
    echo "create-dmg not found. Installing via Homebrew..."
    brew install create-dmg
fi

# Remove old DMG if exists
rm -f "$DIST_DIR/$DMG_NAME.dmg"

# Create DMG
echo "Creating DMG..."
create-dmg \
    --volname "$DMG_NAME" \
    --volicon "$SCRIPT_DIR/transcripter.icns" \
    --window-pos 200 120 \
    --window-size 600 400 \
    --icon-size 100 \
    --icon "Transcripter.app" 175 190 \
    --hide-extension "Transcripter.app" \
    --app-drop-link 425 190 \
    --no-internet-enable \
    "$DIST_DIR/$DMG_NAME.dmg" \
    "$APP_PATH"

echo ""
echo "========================================"
echo "DMG created successfully!"
echo "========================================"
echo ""
echo "Output: $DIST_DIR/$DMG_NAME.dmg"
echo ""

# Optional: Code signing instructions
echo "To code sign the app (requires Apple Developer account):"
echo "  codesign --deep --force --verify --verbose \\"
echo "    --sign \"Developer ID Application: Your Name\" \\"
echo "    --options runtime \\"
echo "    --entitlements $SCRIPT_DIR/entitlements.plist \\"
echo "    \"$APP_PATH\""
echo ""
echo "To notarize (required for Gatekeeper on macOS 10.15+):"
echo "  xcrun notarytool submit \"$DIST_DIR/$DMG_NAME.dmg\" \\"
echo "    --apple-id \"your@email.com\" \\"
echo "    --team-id \"TEAMID\" \\"
echo "    --password \"app-specific-password\" \\"
echo "    --wait"
