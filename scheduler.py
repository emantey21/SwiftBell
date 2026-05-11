# scheduler.py

"""
Scheduler management for timed events
"""

import logging
import os
from datetime import datetime, time as time_obj
from typing import List, Dict, Any

class SchedulerManager:
    """Manages scheduled events and triggers"""
    
    def __init__(self, config, audio_manager, timetable_manager):
        self.config = config
        self.audio_manager = audio_manager
        self.timetable_manager = timetable_manager
        self.logger = logging.getLogger(__name__)
        
        # Track executed events to avoid duplicates
        self.executed_today = set()
        self.current_date = datetime.now().date()
        
    def load_schedule(self, events: List[Dict[str, Any]]):
        """Load schedule from timetable events"""
        self.logger.info(f"Loading {len(events)} scheduled events")
        
        # Reset daily tracking if date changed
        today = datetime.now().date()
        if today != self.current_date:
            self.executed_today.clear()
            self.current_date = today
            
    def check_schedule(self):
        """Check if any scheduled events should be triggered now"""
        current_time = datetime.now().time()
        today_name = datetime.now().strftime("%A").lower()  # e.g., "monday"
        events = self.timetable_manager.get_events()
        
        for event in events:
            # Check if event is for today
            event_day = event.get("day", "everyday").lower()
            if event_day not in ("everyday", today_name):
                continue  # skip events for other days

            # Parse time
            event_time = self._parse_time(event['time'])
            event_key = f"{event['day']}_{event['time']}_{event['event']}"
            
            # Check if this event should be triggered now
            if (self._is_time_to_trigger(current_time, event_time) and 
                event_key not in self.executed_today):
                
                self._trigger_event(event)
                self.executed_today.add(event_key)
                
    def _parse_time(self, time_str: str) -> time_obj:
        """Parse time string in HH:MM format"""
        try:
            hour, minute = map(int, time_str.split(':'))
            return time_obj(hour, minute)
        except ValueError:
            self.logger.error(f"Invalid time format: {time_str}")
            raise
            
    def _is_time_to_trigger(self, current_time: time_obj, event_time: time_obj) -> bool:
        """Check if current time matches event time (within 1 minute tolerance)"""
        current_minutes = current_time.hour * 60 + current_time.minute
        event_minutes = event_time.hour * 60 + event_time.minute
        
        return abs(current_minutes - event_minutes) <= 1
        
    def _trigger_event(self, event: Dict[str, Any]):
        """Trigger a scheduled event"""
        self.logger.info(f"Triggering event: {event['event']} at {event['time']} ({event.get('day','everyday')})")
        
        event_type = event.get('type', 'announcement').lower()
        
        if event_type == 'siren':
            sound_file = event.get('sound_file', self.config.get('default_siren'))
            if sound_file:
                self.audio_manager.play_siren(sound_file)
            else:
                self.logger.warning("No sound file specified for siren event")
                
        elif event_type == 'music':
            music_file = event.get('sound_file', self.config.get('default_music'))
            if music_file:
                self.audio_manager.play_music(music_file)
            else:
                self.logger.warning("No music file specified for music event")
                
        elif event_type == 'announcement':
            message = event.get('message', f"{event['event']} - {event['time']}")
            self.audio_manager.speak(message)
            
        elif event_type == 'siren_and_announcement':
            sound_file = event.get('sound_file', self.config.get('default_siren'))
            message = event.get('message', f"{event['event']} - {event['time']}")
            if sound_file and message:
                self.audio_manager.play_siren_then_speak(sound_file, message, repeat_count=1)
            else:
                self.logger.warning("Missing sound file or message for siren+announcement event")
                
        elif event_type == 'bell':
            bell_sound = event.get('sound_file', self.config.get('default_bell', 'sounds/bell.wav'))
            if bell_sound and os.path.exists(bell_sound):
                self.audio_manager.play_siren(bell_sound)
            else:
                self.logger.warning(f"Bell sound file not found: {bell_sound}")
                
        elif event_type == 'bell_and_announcement':
            bell_sound = event.get('sound_file', self.config.get('default_bell', 'sounds/bell.wav'))
            message = event.get('message', f"{event['event']} - {event['time']}")
            if bell_sound and message:
                self.audio_manager.play_siren_then_speak(bell_sound, message, repeat_count=1)
            else:
                self.logger.warning("Missing bell sound or message for bell+announcement event")
                
        else:
            self.logger.warning(f"Unknown event type: {event_type}")
            
    def get_next_events(self, count: int = 5) -> List[Dict[str, Any]]:
        """Get the next scheduled events for today"""
        current_time = datetime.now().time()
        today_name = datetime.now().strftime("%A").lower()
        events = self.timetable_manager.get_events()
        
        # Filter only today's future events
        future_events = []
        for event in events:
            event_day = event.get("day", "everyday").lower()
            if event_day not in ("everyday", today_name):
                continue
            
            event_time = self._parse_time(event['time'])
            if event_time > current_time:
                future_events.append(event)
                
        # Sort by time
        future_events.sort(key=lambda x: self._parse_time(x['time']))
        return future_events[:count]
