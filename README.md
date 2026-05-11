<p align="center">
  <img src="https://img.shields.io/badge/python-3.7+-blue?logo=python" alt="Python 3.7+">
  <img src="https://img.shields.io/badge/platform-windows%20%7C%20linux%20%7C%20raspberry%20pi-lightgrey" alt="Platform">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="License">
</p>

<h1 align="center">SwiftBell</h1>

<p align="center">
  Automated school bell and announcement system with text-to-speech, siren alerts, and timetable scheduling.
</p>

---

## Features

- **Timetable scheduling** — Reads schedules from JSON or CSV; supports daily and day-specific events
- **Text-to-speech announcements** — Cross-platform TTS (SAPI5 on Windows, espeak on Linux)
- **Multi-audio playback** — Plays bells, sirens, and music files via pygame
- **Emergency override** — Instant evacuation alert with siren + voice, interruptible from keyboard
- **Desktop UI** — PyQt5 graphical interface with live status, controls, and log
- **Auto-reload** — Detects timetable file changes every 5 minutes without restart
- **Event dedup** — Each event fires once per day; resets at midnight
- **Logging** — All activity recorded to `SwiftBell.log`
- **Cross-platform** — Windows, Linux, Raspberry Pi

## Quick start

### Windows

```batch
:: 1. Install Python from https://python.org (add to PATH)
:: 2. Clone and install
git clone https://github.com/emantey21/SwiftBell.git
cd SwiftBell
pip install pyttsx3 pygame PyQt5

:: 3. Run
python main.py test
python main.py start
```

Or double-click `INSTALL.bat` to auto-install and test.

### Linux / Raspberry Pi

```bash
# 1. System dependencies
sudo apt-get install espeak espeak-data alsa-utils

# 2. Clone and install
git clone https://github.com/emantey21/SwiftBell.git
cd SwiftBell
pip install pyttsx3 pygame PyQt5

# 3. Run
python3 main.py test
python3 main.py start
```

Or run `bash install.sh` to auto-install and test.

### Desktop UI (both platforms)

```bash
python main.py ui
```

Press `e` + Enter for emergency evacuation (CLI mode). Press Ctrl+C to stop.

### Commands

| Command | Action |
|---------|--------|
| `python main.py start` | Run the scheduler (default) |
| `python main.py ui` | Launch the desktop UI |
| `python main.py test` | Test audio playback and TTS |
| `python main.py emergency` | Trigger immediate evacuation |
| `python main.py status` | Show system status and upcoming events |
| `python main.py help` | Print usage info |

## Configuration

### Timetable

Edit `timetable.json` (or `timetable.csv` — auto-detected by extension):

```json
[
  {
    "day": "Monday",
    "time": "08:00",
    "event": "Opening Bell",
    "type": "siren_and_announcement",
    "message": "Good morning students and staff. The school day is starting.",
    "sound_file": "sounds/opening_bell.mp3"
  }
]
```

### Event types

| Type | Behavior |
|------|----------|
| `announcement` | TTS only |
| `siren` | Play sound file |
| `music` | Play music file |
| `bell` | Play bell sound |
| `siren_and_announcement` | Sound then TTS |
| `bell_and_announcement` | Bell then TTS |

### Config file

`config.json` holds TTS overrides. Full defaults are in `config.py`.

```json
{
  "tts_voice": "female",
  "tts_rate": 120,
  "tts_volume": 1.0
}
```

Place audio files in `sounds/`.

## Architecture

```
main.py                  CLI entrypoint, coordinates all components
├── config.py            Default settings + config.json overlay
├── timetable_manager.py Reads & validates timetable.json / timetable.csv
├── scheduler.py         Time-based event dispatcher (1-min tolerance)
└── audio_manager.py     Audio playback (pygame) + TTS (pyttsx3 / espeak)
```

- **Event dedup**: each event runs once per day; `executed_today` resets at midnight
- **Timetable poll**: checks file mtime every 5 minutes (`timetable_check_interval`)
- **Emergency**: interrupts current audio, plays siren + evacuation message 3x

## Deployment

### Raspberry Pi (auto-start on boot)

```bash
sudo apt-get install python3-pip python3-dev espeak espeak-data
pip install pyttsx3 pygame PyQt5
```

Add to `/etc/rc.local`:

```bash
cd /home/pi/SwiftBell && python3 main.py start &
```

### Windows (Task Scheduler / Startup)

**Option A — Startup folder** (simplest):

1. Press `Win + R`, type `shell:startup`, press Enter
2. Create `SwiftBell.bat` in that folder with:

```batch
@echo off
cd /d "C:\path\to\SwiftBell"
python main.py start
```

**Option B — Task Scheduler** (runs on boot even before login):

1. Open Task Scheduler → Create Basic Task
2. Trigger: "When the computer starts"
3. Action: Start a program → browse to `python.exe`, argument: `main.py start`, start in: your SwiftBell folder

## Troubleshooting

| Symptom | Likely fix |
|---------|------------|
| No audio output | Check speakers; run `python main.py test` |
| TTS not working (Windows) | `pip install pyttsx3` — uses SAPI5 voices built into Windows |
| TTS not working (Linux) | `sudo apt-get install espeak espeak-data` |
| Timetable not loading | Verify JSON/CSV format and HH:MM time strings |
| Sound files not playing | Check paths in `timetable.json`; use WAV for best compat |
| Missing voices | Run `python find_voice.py` (Windows only) |

## Support

If SwiftBell is useful to you, consider supporting its development:

[![GitHub Sponsors](https://img.shields.io/badge/GitHub%20Sponsors-support-%23ea4aaa?logo=github)](https://github.com/sponsors/emantey21)

- **GitHub Sponsors** — monthly or one-time sponsorship (button on repo)
- **PayPal** — coming soon
- **Mobile Money (Momo)** — coming soon

Every bit helps with hosting, testing hardware, and development time.

## Project status

Active. Built for educational institutions needing a reliable, offline bell and announcement system.

## License

MIT
