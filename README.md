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
- **Auto-reload** — Detects timetable file changes every 5 minutes without restart
- **Event dedup** — Each event fires once per day; resets at midnight
- **Logging** — All activity recorded to `SwiftBell.log`
- **Cross-platform** — Windows, Linux, Raspberry Pi

## Quick start

### Prerequisites

- Python 3.7+
- **Linux / Raspberry Pi**: `sudo apt-get install espeak espeak-data alsa-utils`

### Install & run

```bash
git clone https://github.com/emantey21/SwiftBell.git
cd SwiftBell

pip install pyttsx3 pygame

# Test audio
python main.py test

# Start the system
python main.py start
```

Press `e` + Enter for emergency evacuation. Press Ctrl+C to stop.

### Commands

| Command | Action |
|---------|--------|
| `python main.py start` | Run the scheduler (default) |
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
pip install pyttsx3 pygame
```

Add to `/etc/rc.local`:

```bash
cd /home/pi/SwiftBell && python3 main.py start &
```

### Windows (task scheduler)

Create a batch file or use Windows Task Scheduler to run:

```batch
cd /d "C:\path\to\SwiftBell"
python main.py start
```

## Troubleshooting

| Symptom | Likely fix |
|---------|------------|
| No audio output | Check speakers; run `python main.py test` |
| TTS not working | `pip install pyttsx3`; Linux: `sudo apt-get install espeak` |
| Timetable not loading | Verify JSON/CSV format and HH:MM time strings |
| Sound files not playing | Check paths in `timetable.json`; use WAV for best compat |
| Missing voices | Run `python find_voice.py` (Windows only) |

## Project status

Active. Built for educational institutions needing a reliable, offline bell and announcement system.

## License

MIT
