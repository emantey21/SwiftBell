#config.py
"""
Configuration settings for SwiftBell
"""

import json
import os

class Config:
    """Configuration management"""
    
    def __init__(self, config_file: str = "config.json"):
        # File paths
        self.settings = {
            # Timetable settings
            # Can be either timetable.json or timetable.csv (detected automatically)
            'timetable_file': 'timetable.json',
            'timetable_check_interval': 300,  # Check every 5 minutes
            
            # Audio settings
            'tts_rate': 200,  # Words per minute (increased from 180)
            'tts_volume': 1.0,  # Volume level (0.0 to 1.0) - MAX VOLUME
            'tts_voice': 'female',  # Voice type: 'male' or 'female'
            
            # Default sound files
            'default_siren': 'sounds/school_bell.mp3',
            'default_music': 'sounds/closing_bell.mp3',
            'evacuation_siren': 'sounds/evacuation.wav',
            'test_sound_file': 'sounds/school_bell.mp3',
            
            # Emergency settings
            'emergency_message': (
                "EMERGENCY ALERT! This is not a drill. "
                "Please evacuate the building immediately using your nearest exit. "
                "Follow your emergency procedures and proceed to the designated assembly area. "
                "Do not use elevators. Walk, do not run. "
                "Listen for further instructions from school staff."
            ),
            
            # System settings
            'enable_logging': True,
            'log_level': 'INFO',
            'audio_buffer_size': 1024,
            
            # School-specific settings
            'school_name': 'Your School Name',
            'timezone': 'local',
            
            # Advanced features
            'enable_web_interface': False,
            'web_port': 8080,
            'enable_remote_control': False,
        }
        
        # Load from config file if it exists
        self._config_file = config_file
        self.load_from_file(config_file)
    
    def get(self, key: str, default=None):
        """Get configuration value"""
        return self.settings.get(key, default)
    
    def set(self, key: str, value):
        """Set configuration value"""
        self.settings[key] = value
    
    def update(self, new_settings: dict):
        """Update multiple configuration values"""
        self.settings.update(new_settings)
    
    def get_all(self):
        """Get all configuration settings"""
        return self.settings.copy()
    
    def load_from_file(self, config_file: str):
        """Load configuration from JSON file"""
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    file_config = json.load(f)
                    self.settings.update(file_config)
                print(f"Configuration loaded from {config_file}")
            except Exception as e:
                print(f"Failed to load config file {config_file}: {e}")
        else:
            print(f"Config file {config_file} not found, using defaults")
    
    def save_to_file(self, config_file: str):
        """Save configuration to JSON file"""
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
            print(f"Configuration saved to {config_file}")
        except Exception as e:
            print(f"Failed to save config file {config_file}: {e}")
