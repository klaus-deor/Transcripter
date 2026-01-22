#!/bin/bash
# Script to stop Transcripter running in background

PID_FILE="$HOME/.config/transcripter/transcripter.pid"

if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")

    if ps -p $PID > /dev/null 2>&1; then
        echo "Stopping Transcripter (PID: $PID)..."
        kill $PID
        rm "$PID_FILE"
        echo "Transcripter stopped!"
    else
        echo "Transcripter is not running (stale PID file)"
        rm "$PID_FILE"
    fi
else
    # Try to kill by process name
    if pkill -f "python.*transcripter.main"; then
        echo "Transcripter stopped!"
    else
        echo "Transcripter is not running"
    fi
fi
