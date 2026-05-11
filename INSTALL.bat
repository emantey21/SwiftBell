@echo off
echo Installing SwiftBell...
echo.

echo Step 1: Installing Python libraries...
pip install -r requirements.txt

echo.
echo Step 2: Testing installation...
python main.py test

echo.
echo Installation complete!
echo.
echo To start the system, run: python main.py start
echo To customize schedule, edit: timetable.json
echo.
pause