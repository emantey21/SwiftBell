# AGENTS.md — SwiftBell

## Project overview
Python-only: bell/announcement scheduler, TTS, audio playback.

## Commands

| Command | Notes |
|---------|-------|
| `python main.py start` | Main entry point; also `test`, `emergency`, `status`, `help`, `ui` |
| `pip install pyttsx3 pygame PyQt5` | No `requirements.txt` exists |

## Architecture

- **`main.py`** — CLI entrypoint, coordinates `Config` → `TimetableManager` → `SchedulerManager` → `AudioManager`
- **`audio_manager.py`** — pygame for WAV/MP3 playback; pyttsx3 (Windows) or subprocess `espeak` (Linux) for TTS
- **`timetable_manager.py`** — Reads `timetable.json` (primary) or `timetable.csv` (auto-detected by extension)
- **`config.py`** — Python class with defaults, overlaid by `config.json` at runtime
- **`find_voice.py`** — Utility to enumerate TTS voices (Windows pyttsx3 only)
- **`sounds/`** — Audio files; system logs to `SwiftBell.log`

## Setup quirks

- **Linux audio**: requires `espeak`, `espeak-data`, `alsa-utils` (apt packages)
- **Missing requirements.txt**: `pip install pyttsx3 pygame` is the real install command
- **Timetable auto-reload**: polls `timetable.json` mtime every 5 min (configurable via `timetable_check_interval`)
- **Event dedup**: each event runs once per day (`executed_today` set resets at midnight)

## Event types (in timetable)
`siren`, `music`, `announcement`, `siren_and_announcement`, `bell`, `bell_and_announcement`

## Key constraints
- Do NOT create a `requirements.txt` unless asked — current convention is ad-hoc `pip install`
- `config.json` only holds TTS overrides — full defaults are in `config.py`
- No test framework, no CI, no pre-commit hooks
