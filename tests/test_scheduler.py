from datetime import datetime, time
from scheduler import SchedulerManager


class FakeConfig:
    def get(self, key, default=None):
        return default


class FakeAudioManager:
    def __init__(self):
        self.played = []
        self.spoken = []

    def play_siren(self, path):
        self.played.append(("siren", path))

    def play_music(self, path):
        self.played.append(("music", path))

    def speak(self, msg):
        self.spoken.append(msg)

    def play_siren_then_speak(self, path, msg, repeat_count=1):
        self.played.append(("siren_then_speak", path, repeat_count))
        self.spoken.append(msg)

    def stop_all(self):
        pass


class FakeTimetableManager:
    def __init__(self, events):
        self._events = events

    def get_events(self):
        return self._events


class TestSchedulerManager:
    def test_load_schedule(self, sample_events):
        scheduler = SchedulerManager(FakeConfig(), FakeAudioManager(), FakeTimetableManager(sample_events))
        scheduler.load_schedule(sample_events)
        assert scheduler.current_date == datetime.now().date()

    def test_parse_time(self, sample_events):
        scheduler = SchedulerManager(FakeConfig(), FakeAudioManager(), FakeTimetableManager(sample_events))
        parsed = scheduler._parse_time("08:30")
        assert parsed == time(8, 30)

    def test_is_time_to_trigger_exact_match(self, sample_events):
        scheduler = SchedulerManager(FakeConfig(), FakeAudioManager(), FakeTimetableManager(sample_events))
        assert scheduler._is_time_to_trigger(time(10, 0), time(10, 0))

    def test_is_time_to_trigger_within_tolerance(self, sample_events):
        scheduler = SchedulerManager(FakeConfig(), FakeAudioManager(), FakeTimetableManager(sample_events))
        assert scheduler._is_time_to_trigger(time(10, 0), time(10, 1))
        assert scheduler._is_time_to_trigger(time(10, 1), time(10, 0))

    def test_is_time_to_trigger_outside_tolerance(self, sample_events):
        scheduler = SchedulerManager(FakeConfig(), FakeAudioManager(), FakeTimetableManager(sample_events))
        assert not scheduler._is_time_to_trigger(time(10, 0), time(10, 3))
        assert not scheduler._is_time_to_trigger(time(10, 5), time(10, 0))

    def test_event_dedup(self, sample_events):
        audio = FakeAudioManager()
        scheduler = SchedulerManager(FakeConfig(), audio, FakeTimetableManager(sample_events))
        scheduler.load_schedule(sample_events)

        event = sample_events[0]
        event_key = f"{event['day']}_{event['time']}_{event['event']}"
        assert event_key not in scheduler.executed_today
        scheduler.executed_today.add(event_key)
        assert event_key in scheduler.executed_today

    def test_get_next_events_returns_sorted(self, sample_events):
        audio = FakeAudioManager()
        scheduler = SchedulerManager(FakeConfig(), audio, FakeTimetableManager(sample_events))
        scheduler.load_schedule(sample_events)
        next_events = scheduler.get_next_events(2)
        assert len(next_events) <= 2
        if len(next_events) > 1:
            t1 = scheduler._parse_time(next_events[0]["time"])
            t2 = scheduler._parse_time(next_events[1]["time"])
            assert t1 <= t2
