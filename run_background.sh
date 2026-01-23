#!/bin/bash
# Script to run Transcripter in background, detached from terminal

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Activate virtual environment
source "$SCRIPT_DIR/venv/bin/activate"

# Run transcripter in background, redirecting output to a log file
LOG_FILE="$HOME/.config/transcripter/transcripter.log"
mkdir -p "$HOME/.config/transcripter"

# Kill any existing instance
pkill -f "python.*transcripter.main" 2>/dev/null

# Start in background with nohup (continues after terminal closes)
nohup python -m transcripter.main > "$LOG_FILE" 2>&1 &

# Get the PID
PID=$!

# Save PID to file for later stopping
echo $PID > "$HOME/.config/transcripter/transcripter.pid"

echo "Transcripter started in background!"
echo "PID: $PID"
echo "Log file: $LOG_FILE"
echo ""
echo "To stop: ./stop_transcripter.sh"
echo "Or: kill $PID"
