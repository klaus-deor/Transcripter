#!/bin/bash
# Script to toggle recording - can be called from desktop environment shortcuts

# Find the Transcripter process
PID=$(pgrep -f "transcripter.main" | head -1)

if [ -z "$PID" ]; then
    notify-send "Transcripter" "Transcripter is not running!" -i dialog-error
    exit 1
fi

# Send USR1 signal to toggle recording
kill -USR1 $PID

# Optional: show notification
# notify-send "Transcripter" "Recording toggled" -i audio-input-microphone
