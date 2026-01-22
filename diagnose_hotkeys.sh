#!/bin/bash
# Script to diagnose hotkey problems

echo "=========================================="
echo "Transcripter Hotkey Diagnostics"
echo "=========================================="
echo ""

# Check if running
echo "1. Checking if Transcripter is running..."
if pgrep -f "transcripter.main" > /dev/null; then
    echo "   \u2713 Transcripter is running"
    PID=$(pgrep -f "transcripter.main")
    echo "   PID: $PID"
else
    echo "   \u2717 Transcripter is NOT running"
    echo "   Start it first with: ./run_background.sh"
    exit 1
fi
echo ""

# Check display server
echo "2. Checking display server..."
if [ "$XDG_SESSION_TYPE" = "wayland" ]; then
    echo "   \u26a0 WARNING: You are using Wayland"
    echo "   Wayland has restrictions on global hotkeys for security"
    echo "   Recommendation: Use X11 instead, or use keyboard shortcuts from DE"
    WAYLAND=true
elif [ "$XDG_SESSION_TYPE" = "x11" ]; then
    echo "   \u2713 You are using X11 (good for hotkeys)"
    WAYLAND=false
else
    echo "   ? Unknown display server: $XDG_SESSION_TYPE"
    WAYLAND=unknown
fi
echo ""

# Check desktop environment
echo "3. Checking desktop environment..."
echo "   Desktop: $XDG_CURRENT_DESKTOP"
echo "   Session: $DESKTOP_SESSION"
echo ""

# Check logs
echo "4. Checking logs for errors..."
LOG_FILE="$HOME/.config/transcripter/transcripter.log"
if [ -f "$LOG_FILE" ]; then
    echo "   Log file: $LOG_FILE"
    echo ""
    echo "   Last 20 lines:"
    echo "   ----------------------------------------"
    tail -n 20 "$LOG_FILE" | sed 's/^/   /'
    echo "   ----------------------------------------"
    echo ""

    # Check for specific errors
    if grep -i "error.*hotkey\|error.*keyboard\|permission denied" "$LOG_FILE" > /dev/null; then
        echo "   \u26a0 Found hotkey-related errors in log!"
        echo ""
        echo "   Errors found:"
        grep -i "error.*hotkey\|error.*keyboard\|permission denied" "$LOG_FILE" | tail -n 5 | sed 's/^/   /'
    else
        echo "   \u2713 No obvious hotkey errors in log"
    fi
else
    echo "   \u2717 Log file not found"
    echo "   Run with: ./run_background.sh"
fi
echo ""

# Check Python packages
echo "5. Checking Python packages..."
source venv/bin/activate 2>/dev/null
if python3 -c "import pynput" 2>/dev/null; then
    echo "   \u2713 pynput is installed"
else
    echo "   \u2717 pynput is NOT installed"
    echo "   Install with: pip install pynput"
fi

if python3 -c "import keyboard" 2>/dev/null; then
    echo "   \u2713 keyboard is installed"
else
    echo "   \u2717 keyboard is NOT installed (optional)"
fi
echo ""

# Test pynput
echo "6. Testing pynput hotkey capture..."
echo "   Creating test script..."

cat > /tmp/test_pynput.py << 'EOF'
import sys
from pynput import keyboard

print("Testing pynput...")
print("Press Ctrl+C to exit")
print("")

pressed_keys = set()

def on_press(key):
    pressed_keys.add(key)
    try:
        print(f"Key pressed: {key.char}")
    except AttributeError:
        print(f"Special key pressed: {key}")

def on_release(key):
    if key in pressed_keys:
        pressed_keys.remove(key)
    if key == keyboard.Key.esc:
        return False

try:
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        print("Listener started. Press ESC to stop.")
        listener.join()
    print("\nTest completed successfully!")
    sys.exit(0)
except Exception as e:
    print(f"\nERROR: {e}")
    print("\nPynput cannot capture keys on this system!")
    sys.exit(1)
EOF

echo "   Run this test manually:"
echo "   source venv/bin/activate && python /tmp/test_pynput.py"
echo ""

# Check user groups
echo "7. Checking user groups..."
if groups | grep -q input; then
    echo "   \u2713 User is in 'input' group"
else
    echo "   \u26a0 User is NOT in 'input' group"
    echo "   This may be needed for keyboard access"
    echo "   Add with: sudo usermod -a -G input $USER"
fi
echo ""

# Recommendations
echo "=========================================="
echo "RECOMMENDATIONS:"
echo "=========================================="
echo ""

if [ "$WAYLAND" = true ]; then
    echo "\u26a0 WAYLAND DETECTED - This is likely the problem!"
    echo ""
    echo "Wayland blocks global hotkeys for security reasons."
    echo ""
    echo "SOLUTIONS:"
    echo ""
    echo "Option 1: Switch to X11 (Recommended)"
    echo "  - Log out"
    echo "  - On login screen, click the gear icon"
    echo "  - Select 'Ubuntu on Xorg' or similar"
    echo "  - Log in"
    echo ""
    echo "Option 2: Use desktop environment shortcuts"
    echo "  - Open your DE's keyboard settings"
    echo "  - Add a custom shortcut"
    echo "  - Command: $HOME/Documentos/Saas/Transcripter/toggle_recording.sh"
    echo "  - Assign your desired hotkey"
    echo ""
elif [ "$WAYLAND" = false ]; then
    echo "\u2713 You are using X11, which is good for hotkeys"
    echo ""
    echo "If hotkeys still don't work:"
    echo ""
    echo "1. Check the logs:"
    echo "   tail -f ~/.config/transcripter/transcripter.log"
    echo ""
    echo "2. Test pynput manually:"
    echo "   source venv/bin/activate"
    echo "   python /tmp/test_pynput.py"
    echo ""
    echo "3. Try running with sudo (testing only):"
    echo "   sudo venv/bin/python -m transcripter.main"
    echo ""
    echo "4. Check if another app is blocking the hotkey"
    echo ""
fi

echo "=========================================="
echo ""
