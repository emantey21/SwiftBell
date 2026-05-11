"""
Timetable management for reading and parsing schedule files
"""

import json
import csv
import os
import logging
from typing import List, Dict, Any
from datetime import datetime


class TimetableManager:
    """Manages timetable loading and parsing from JSON/CSV files"""

    VALID_DAYS = [
        "monday", "tuesday", "wednesday", "thursday",
        "friday", "saturday", "sunday", "everyday"
    ]

    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)

        self.timetable_file = config.get("timetable_file", "timetable.json")
        self.events: List[Dict[str, Any]] = []
        self.file_modified_time = 0

    def load_timetable(self):
        """Load timetable from configured file"""
        if not os.path.exists(self.timetable_file):
            self.logger.error(f"Timetable file not found: {self.timetable_file}")
            raise FileNotFoundError(f"Timetable file not found: {self.timetable_file}")

        try:
            # Determine file type and load accordingly
            if self.timetable_file.endswith(".json"):
                self._load_json_timetable()
            elif self.timetable_file.endswith(".csv"):
                self._load_csv_timetable()
            else:
                raise ValueError(f"Unsupported file type: {self.timetable_file}")

            # Update file modification time
            self.file_modified_time = os.path.getmtime(self.timetable_file)

            self.logger.info(f"Loaded {len(self.events)} events from timetable")

        except Exception as e:
            self.logger.error(f"Failed to load timetable: {e}")
            raise

    def _load_json_timetable(self):
        """Load timetable from JSON file"""
        with open(self.timetable_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Handle different JSON structures
        if isinstance(data, list):
            self.events = data
        elif isinstance(data, dict) and "events" in data:
            self.events = data["events"]
        else:
            raise ValueError("Invalid JSON structure. Expected list or object with 'events' key")

        # Validate events
        self._validate_events()

    def _load_csv_timetable(self):
        """Load timetable from CSV file"""
        self.events = []

        with open(self.timetable_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for row in reader:
                # Convert CSV row to event format
                event = {
                    "day": row.get("day", "everyday").strip().lower(),
                    "time": row.get("time", "").strip(),
                    "event": row.get("event", "").strip(),
                    "message": row.get("message", "").strip(),
                    "type": row.get("type", "announcement").strip().lower(),
                    "sound_file": row.get("sound_file", "").strip(),
                }

                # Skip empty rows
                if event["time"] and event["event"]:
                    self.events.append(event)

        # Validate events
        self._validate_events()

    def _validate_events(self):
        """Validate event data"""
        valid_events = []

        for i, event in enumerate(self.events):
            try:
                # Check required fields
                if not event.get("time") or not event.get("event"):
                    self.logger.warning(f"Event {i} missing required fields, skipping")
                    continue

                # Validate day
                day = event.get("day", "everyday").strip().lower()
                if day not in self.VALID_DAYS:
                    self.logger.warning(f"Invalid day in event {i}: {day}, defaulting to 'everyday'")
                    day = "everyday"
                event["day"] = day

                # Validate time format
                time_str = event["time"]
                if ":" not in time_str:
                    self.logger.warning(f"Invalid time format in event {i}: {time_str}")
                    continue

                try:
                    hour, minute = map(int, time_str.split(":"))
                    if not (0 <= hour <= 23 and 0 <= minute <= 59):
                        raise ValueError("Time out of range")
                except ValueError:
                    self.logger.warning(f"Invalid time in event {i}: {time_str}")
                    continue

                # Set default values for optional fields
                event.setdefault("type", "announcement")
                event.setdefault("message", f"{event['event']} at {event['time']}")
                event.setdefault("sound_file", "")

                valid_events.append(event)

            except Exception as e:
                self.logger.error(f"Error validating event {i}: {e}")

        self.events = valid_events
        self.logger.info(f"Validated {len(self.events)} events")

    def get_events(self) -> List[Dict[str, Any]]:
        """Get all loaded events"""
        return self.events.copy()

    def has_timetable_changed(self) -> bool:
        """Check if timetable file has been modified since last load"""
        if not os.path.exists(self.timetable_file):
            return False

        current_mtime = os.path.getmtime(self.timetable_file)
        return current_mtime > self.file_modified_time

    def get_events_for_time_range(self, start_time: str, end_time: str) -> List[Dict[str, Any]]:
        """Get events within specified time range for the current day"""
        try:
            today = datetime.now().strftime("%A").lower()  # e.g. "monday"

            start_hour, start_minute = map(int, start_time.split(":"))
            end_hour, end_minute = map(int, end_time.split(":"))

            start_minutes = start_hour * 60 + start_minute
            end_minutes = end_hour * 60 + end_minute

            filtered_events = []
            for event in self.events:
                if event["day"] not in ("everyday", today):
                    continue

                event_hour, event_minute = map(int, event["time"].split(":"))
                event_minutes = event_hour * 60 + event_minute

                if start_minutes <= event_minutes <= end_minutes:
                    filtered_events.append(event)

            return filtered_events

        except Exception as e:
            self.logger.error(f"Error filtering events by time range: {e}")
            return []

    def add_event(self, event: Dict[str, Any]):
        """Add a new event to the timetable"""
        # Validate the new event
        temp_events = self.events + [event]
        original_events = self.events
        self.events = temp_events

        try:
            self._validate_events()
            self.logger.info(f"Added new event: {event['event']} at {event['time']}")
        except Exception as e:
            self.events = original_events
            self.logger.error(f"Failed to add event: {e}")
            raise

    def save_timetable(self):
        """Save current timetable back to file"""
        try:
            if self.timetable_file.endswith(".json"):
                with open(self.timetable_file, "w", encoding="utf-8") as f:
                    json.dump(self.events, f, indent=2, ensure_ascii=False)
            elif self.timetable_file.endswith(".csv"):
                with open(self.timetable_file, "w", newline="", encoding="utf-8") as f:
                    if self.events:
                        fieldnames = self.events[0].keys()
                        writer = csv.DictWriter(f, fieldnames=fieldnames)
                        writer.writeheader()
                        writer.writerows(self.events)

            self.file_modified_time = os.path.getmtime(self.timetable_file)
            self.logger.info("Timetable saved successfully")

        except Exception as e:
            self.logger.error(f"Failed to save timetable: {e}")
            raise
