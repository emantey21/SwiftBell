import os
import pytest
from timetable_manager import TimetableManager


class TestTimetableManager:
    def test_load_json(self, config, timetable_json):
        config.set("timetable_file", timetable_json)
        tm = TimetableManager(config)
        tm.load_timetable()
        events = tm.get_events()
        assert len(events) == 3
        assert events[0]["event"] == "Opening Bell"
        assert events[1]["event"] == "Lunch Break"
        assert events[2]["event"] == "Closing Bell"

    def test_load_csv(self, config, timetable_csv):
        config.set("timetable_file", timetable_csv)
        tm = TimetableManager(config)
        tm.load_timetable()
        events = tm.get_events()
        assert len(events) == 3
        assert events[0]["event"] == "Opening Bell"
        assert events[1]["event"] == "Lunch Break"

    def test_file_not_found(self, config):
        config.set("timetable_file", "nonexistent.json")
        tm = TimetableManager(config)
        with pytest.raises(FileNotFoundError):
            tm.load_timetable()

    def test_has_timetable_changed(self, config, timetable_json):
        config.set("timetable_file", timetable_json)
        tm = TimetableManager(config)
        tm.load_timetable()
        assert not tm.has_timetable_changed()
        import time
        time.sleep(0.01)
        os.utime(timetable_json, None)
        assert tm.has_timetable_changed()

    def test_invalid_time_format(self, config, tmp_path):
        path = tmp_path / "bad.json"
        path.write_text(
            '[{"time": "invalid", "event": "Test", "day": "everyday"}]',
            encoding="utf-8",
        )
        config.set("timetable_file", str(path))
        tm = TimetableManager(config)
        tm.load_timetable()
        assert len(tm.get_events()) == 0

    def test_invalid_day_defaults_to_everyday(self, config, tmp_path):
        path = tmp_path / "bad_day.json"
        path.write_text(
            '[{"day": "Funday", "time": "10:00", "event": "Test", "type": "announcement"}]',
            encoding="utf-8",
        )
        config.set("timetable_file", str(path))
        tm = TimetableManager(config)
        tm.load_timetable()
        assert tm.get_events()[0]["day"] == "everyday"

    def test_add_event(self, config, timetable_json):
        config.set("timetable_file", timetable_json)
        tm = TimetableManager(config)
        tm.load_timetable()
        new_event = {
            "day": "Tuesday",
            "time": "09:00",
            "event": "Test Event",
            "type": "announcement",
        }
        tm.add_event(new_event)
        assert len(tm.get_events()) == 4

    def test_get_events_for_time_range(self, config, timetable_json):
        config.set("timetable_file", timetable_json)
        tm = TimetableManager(config)
        tm.load_timetable()
        events = tm.get_events_for_time_range("07:00", "09:00")
        assert len(events) == 1
        assert events[0]["event"] == "Opening Bell"
