#!/bin/bash

# Detect the operating system
OS=$(uname -s)

# Set the Python script to be scheduled
SCRIPT_PATH="$(pwd)/utils/backup_scheduler.py"

# Function to schedule the backup on Linux using cron
schedule_linux() {
    # Check if cron is installed
    if ! command -v crontab &> /dev/null
    then
        echo "cron is not installed. Please install it first."
        exit 1
    fi

    # Add a cron job to run the script every minute (or adjust as needed)
    (crontab -l 2>/dev/null; echo "* * * * * python3 $SCRIPT_PATH") | crontab -

    echo "Backup scheduler has been set up with cron on Linux."
}

# Function to schedule the backup on macOS using launchd
schedule_macos() {
    PLIST_NAME="com.user.backup_scheduler.plist"
    PLIST_PATH="$HOME/Library/LaunchAgents/$PLIST_NAME"

    # Create a launchd plist file
    cat <<EOF > $PLIST_PATH
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>$PLIST_NAME</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>$SCRIPT_PATH</string>
    </array>
    <key>StartInterval</key>
    <integer>86400</integer> <!-- Run every 60 seconds -->
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
EOF

    # Load the plist into launchd
    launchctl load $PLIST_PATH

    echo "Backup scheduler has been set up with launchd on macOS."
}

# Function to schedule the backup on Windows (manual instructions)
schedule_windows() {
    echo "To schedule the backup on Windows, please follow these steps:"
    echo "1. Open Task Scheduler."
    echo "2. Create a new task."
    echo "3. Set the trigger to the desired frequency."
    echo "4. Set the action to run 'python' with the script path: $SCRIPT_PATH"
    echo "5. Save and enable the task."
}

# OS-specific scheduling
case "$OS" in
    Linux*)
        schedule_linux
        ;;
    Darwin*)
        schedule_macos
        ;;
    CYGWIN*|MINGW*|MSYS*|MINGW32*|MINGW64*)
        schedule_windows
        ;;
    *)
        echo "Unsupported operating system: $OS"
        exit 1
        ;;
esac
