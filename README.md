<p align="center">
  <img src="https://img.shields.io/badge/python-3.7+-blue?logo=python" alt="Python 3.7+">
  <img src="https://img.shields.io/badge/platform-windows%20%7C%20linux%20%7C%20raspberry%20pi-lightgrey" alt="Platform">
  <img src="https://img.shields.io/github/actions/workflow/status/emantey21/SwiftBell/test.yml?branch=main&label=tests" alt="Tests">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green" alt="License"></a>
</p>

<h1 align="center">SwiftBell</h1>

<p align="center">
  Automated school bell and announcement system with text-to-speech, siren alerts, web dashboard, and timetable scheduling.
</p>

---

## Features

- **Timetable scheduling** — Reads schedules from JSON or CSV; supports daily and day-specific events
- **Text-to-speech announcements** — Cross-platform TTS (SAPI5 on Windows, espeak on Linux)
- **Multi-audio playback** — Plays bells, sirens, and music files via pygame
- **Web dashboard** — FastAPI web UI to manage the system from any browser
- **Desktop UI** — PyQt5 graphical interface with live status, controls, and log
- **Emergency override** — Instant evacuation alert with siren + voice
- **Auto-reload** — Detects timetable file changes every 5 minutes
- **Event dedup** — Each event fires once per day; resets at midnight
- **Logging** — All activity recorded to `SwiftBell.log`
- **Cross-platform** — Windows, Linux, Raspberry Pi
- **Docker support** — Run with a single `docker compose up`

## Quick start

### Windows

```batch
git clone https://github.com/emantey21/SwiftBell.git
cd SwiftBell
pip install -r requirements.txt
python main.py test
python main.py start
```

Or double-click `INSTALL.bat`.

### Linux / Raspberry Pi

```bash
sudo apt-get install espeak espeak-data alsa-utils
git clone https://github.com/emantey21/SwiftBell.git
cd SwiftBell
pip install -r requirements.txt
python3 main.py test
python3 main.py start
```

Or run `bash install.sh`.

### Docker

```bash
docker compose up -d
# Web dashboard at http://localhost:8000
```

### Commands

| Command | Action |
|---------|--------|
| `python main.py start` | Run the scheduler (CLI) |
| `python main.py ui` | Launch the desktop UI |
| `python main.py test` | Test audio playback and TTS |
| `python main.py emergency` | Trigger immediate evacuation |
| `python main.py status` | Show system status and upcoming events |
| `python -m uvicorn web.main:app` | Launch web dashboard (localhost:8000) |

Press `e` + Enter for emergency evacuation (CLI mode). Press Ctrl+C to stop.

## Web Dashboard

Start the web UI:

```bash
pip install -r requirements.txt
uvicorn web.main:app --host 0.0.0.0 --port 8000
```

Open `http://localhost:8000` in your browser.

**Endpoints:**

| Method | Path | Action |
|--------|------|--------|
| GET | `/` | Dashboard UI |
| GET | `/api/status` | JSON status |
| POST | `/api/start` | Start scheduler |
| POST | `/api/stop` | Stop scheduler |
| POST | `/api/emergency` | Trigger evacuation |
| POST | `/api/reload` | Reload timetable |

## Testing

```bash
pip install pytest httpx
pytest -v
```

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
    "message": "Good morning students and staff.",
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

Place audio files in `sounds/`.

## Architecture

```
main.py                  CLI entrypoint
├── config.py            Default settings + config.json overlay
├── timetable_manager.py Reads & validates timetable files
├── scheduler.py         Time-based event dispatcher (1-min tolerance)
├── audio_manager.py     Audio playback (pygame) + TTS (pyttsx3 / espeak)
├── ui.py                PyQt5 desktop UI
├── web/main.py          FastAPI web dashboard
└── tests/               pytest test suite (21 tests)
```

## Deployment

### Docker

```bash
docker compose up -d
```

### Raspberry Pi (auto-start on boot)

```bash
sudo apt-get install python3-pip python3-dev espeak espeak-data
pip install -r requirements.txt
```

Add to `/etc/rc.local`:

```bash
cd /home/pi/SwiftBell && python3 main.py start &
```

### Windows (Task Scheduler / Startup)

**Startup folder:** Press `Win + R`, `shell:startup`, create `SwiftBell.bat`:

```batch
@echo off
cd /d "C:\path\to\SwiftBell"
python main.py start
```

**Task Scheduler:** Create task → trigger "At startup" → action: `python main.py start`.

## Troubleshooting

| Symptom | Likely fix |
|---------|------------|
| No audio output | Check speakers; run `python main.py test` |
| TTS not working (Windows) | `pip install pyttsx3` (uses built-in SAPI5 voices) |
| TTS not working (Linux) | `sudo apt-get install espeak espeak-data` |
| Timetable not loading | Verify JSON/CSV format and HH:MM time strings |
| Sound files not playing | Check paths in `timetable.json`; use WAV for best compat |
| Missing voices | Run `python find_voice.py` (Windows only) |

## Support

[![GitHub Sponsors](https://img.shields.io/badge/GitHub%20Sponsors-support-%23ea4aaa?logo=github)](https://github.com/sponsors/emantey21)

If SwiftBell is useful to you, consider supporting its development.

## License

MIT
