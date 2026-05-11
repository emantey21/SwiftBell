import json
import pytest
from config import Config

SAMPLE_EVENTS = [
    {
        "day": "Monday",
        "time": "08:00",
        "event": "Opening Bell",
        "type": "siren_and_announcement",
        "message": "Good morning.",
        "sound_file": "sounds/opening_bell.mp3",
    },
    {
        "day": "Monday",
        "time": "12:30",
        "event": "Lunch Break",
        "type": "announcement",
        "message": "Lunch time.",
        "sound_file": "",
    },
    {
        "day": "everyday",
        "time": "15:00",
        "event": "Closing Bell",
        "type": "siren",
        "message": "",
        "sound_file": "sounds/closing_bell.mp3",
    },
]


@pytest.fixture
def config():
    return Config(config_file="")


@pytest.fixture
def sample_events():
    return [dict(e) for e in SAMPLE_EVENTS]


@pytest.fixture
def timetable_json(tmp_path):
    path = tmp_path / "timetable.json"
    path.write_text(json.dumps(SAMPLE_EVENTS), encoding="utf-8")
    return str(path)


@pytest.fixture
def timetable_csv(tmp_path):
    path = tmp_path / "timetable.csv"
    path.write_text(
        "day,time,event,type,message,sound_file\n"
        "Monday,08:00,Opening Bell,siren_and_announcement,Good morning.,sounds/opening_bell.mp3\n"
        "Monday,12:30,Lunch Break,announcement,Lunch time.,\n"
        "everyday,15:00,Closing Bell,siren,,sounds/closing_bell.mp3\n",
        encoding="utf-8",
    )
    return str(path)
