#!/bin/bash
echo "Installing SwiftBell..."
echo

echo "Step 1: Installing system dependencies (Linux/Raspberry Pi)..."
if command -v apt-get &> /dev/null; then
    sudo apt-get update
    sudo apt-get install -y python3-pip python3-dev espeak espeak-data alsa-utils
fi

echo
echo "Step 2: Installing Python libraries..."
pip3 install pyttsx3 pygame

echo
echo "Step 3: Testing installation..."
python3 main.py test

echo
echo "Installation complete!"
echo
echo "To start the system, run: python3 main.py start"
echo "To customize schedule, edit: timetable.json"
echo