#main.py
#!/usr/bin/env python3
"""
SwiftBell
Main application entry point
"""

import sys
import time
import logging
import threading
from datetime import datetime

from scheduler import SchedulerManager
from audio_manager import AudioManager
from timetable_manager import TimetableManager
from config import Config
from ui import main as ui_main

class SchoolAnnouncementSystem:
    """Main system class that coordinates all components"""
    
    def __init__(self):
        self.setup_logging()
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing SwiftBell...")
        
        # Initialize components
        self.config = Config()
        self.audio_manager = AudioManager(self.config)
        self.timetable_manager = TimetableManager(self.config)
        self.scheduler = SchedulerManager(self.config, self.audio_manager, self.timetable_manager)
        
        # System state
        self.running = False
        self.emergency_active = False
        
        # Setup signal handlers for graceful shutdown (if available)
        try:
            import signal
            signal.signal(signal.SIGINT, self.signal_handler)
            signal.signal(signal.SIGTERM, self.signal_handler)
            self.logger.info("Signal handlers configured for graceful shutdown")
        except ImportError:
            self.logger.warning("Signal module not available - use Ctrl+C to stop")
        except Exception as e:
            self.logger.warning(f"Could not setup signal handlers: {e}")
        
    def setup_logging(self):
        """Configure logging for the application"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('SwiftBell.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        self.logger.info(f"Received signal {signum}. Shutting down gracefully...")
        self.stop()
        sys.exit(0)
    
    def start(self):
        """Start the announcement system"""
        try:
            self.logger.info("Starting SwiftBell...")
            
            # Load initial timetable
            self.timetable_manager.load_timetable()
            
            # Initialize scheduler with current timetable
            self.scheduler.load_schedule(self.timetable_manager.get_events())
            
            self.running = True
            self.logger.info("System started successfully!")
            
            # Start the main loop
            self.main_loop()
            
        except Exception as e:
            self.logger.error(f"Failed to start system: {e}")
            raise
    
    def stop(self):
        """Stop the announcement system"""
        self.logger.info("Stopping SwiftBell...")
        self.running = False
        self.audio_manager.stop_all()
    
    def emergency_evacuation(self):
        """Trigger emergency evacuation procedure"""
        self.logger.warning("EMERGENCY EVACUATION TRIGGERED!")
        self.emergency_active = True
        
        # Get emergency configuration
        siren_file = self.config.get('evacuation_siren', 'sounds/evacuation.wav')
        evacuation_message = self.config.get('emergency_message', 
                                           "EMERGENCY! Please evacuate the building immediately. Follow your emergency procedures.")
        
        # Use sequential playback: siren first, then voice announcement
        self.audio_manager.play_siren_then_speak(siren_file, evacuation_message, repeat_count=3)
        
        # Reset emergency flag after a reasonable time (approximate duration)
        # Siren duration + (3 announcements * ~5 seconds each) + pauses
        emergency_duration = 10 + (3 * 5) + 2  # ~27 seconds total
        threading.Timer(emergency_duration, self._reset_emergency_flag).start()
    
    def _reset_emergency_flag(self):
        """Reset the emergency flag after evacuation procedure completes"""
        self.emergency_active = False
        self.logger.info("Emergency evacuation procedure completed")
    
    def reload_timetable(self):
        """Reload timetable from file"""
        try:
            self.logger.info("Reloading timetable...")
            self.timetable_manager.load_timetable()
            self.scheduler.load_schedule(self.timetable_manager.get_events())
            self.logger.info("Timetable reloaded successfully!")
        except Exception as e:
            self.logger.error(f"Failed to reload timetable: {e}")
    
    def main_loop(self):
        """Main system loop"""
        last_timetable_check = time.time()
        timetable_check_interval = self.config.get('timetable_check_interval', 300)  # 5 minutes
        
        while self.running:
            try:
                # Check for scheduled events
                self.scheduler.check_schedule()
                
                # Periodically check if timetable file has been modified
                current_time = time.time()
                if current_time - last_timetable_check > timetable_check_interval:
                    if self.timetable_manager.has_timetable_changed():
                        self.reload_timetable()
                    last_timetable_check = current_time
                
                # Small delay to prevent excessive CPU usage
                time.sleep(1)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                self.logger.error(f"Error in main loop: {e}")
                time.sleep(5)  # Wait before continuing
    
    def status(self):
        """Get system status"""
        status = {
            'running': self.running,
            'emergency_active': self.emergency_active,
            'current_time': datetime.now().strftime('%H:%M:%S'),
            'next_events': self.scheduler.get_next_events(5)
        }
        return status


def print_usage():
    """Print usage instructions"""
    print("""
SwiftBell - School Bell & Announcement System

FIRST TIME SETUP:
    1. Install Python 3.9+ from python.org
    2. Run: pip install -r requirements.txt
    3. Edit timetable.json with your schedule
    4. Add sound files to sounds/ folder (optional)

Usage:
    python main.py [command]

Commands:
    start       - Start SwiftBell (default)
    ui          - Launch desktop UI
    emergency   - Trigger emergency evacuation
    status      - Show system status
    test        - Test audio systems
    help        - Show this help message

Configuration:
    Edit config.py to customize settings
    Edit timetable.json to modify the school schedule
    
Quick Test:
    python main.py test    # Test if everything works
    
Emergency: Press 'e' + Enter while system is running, or run: python main.py emergency
    """)


def main():
    """Main entry point"""
    command = sys.argv[1] if len(sys.argv) > 1 else 'start'
    
    if command == 'help':
        print_usage()
        return
    
    # Initialize the system
    system = SchoolAnnouncementSystem()
    
    if command == 'start':
        # Setup emergency key listener in a separate thread
        def emergency_listener():
            while system.running:
                try:
                    user_input = input().strip().lower()
                    if user_input in ['e', 'emergency', 'evacuate']:
                        system.emergency_evacuation()
                except (EOFError, KeyboardInterrupt):
                    break
        
        # Start emergency listener thread
        emergency_thread = threading.Thread(target=emergency_listener, daemon=True)
        emergency_thread.start()
        
        print("SwiftBell starting...")
        print("Press 'e' + Enter for emergency evacuation")
        print("Press Ctrl+C to stop the system")
        
        system.start()
        
    elif command == 'emergency':
        print("Triggering emergency evacuation...")
        system.emergency_evacuation()
        
    elif command == 'status':
        status = system.status()
        print("System Status:")
        for key, value in status.items():
            print(f"  {key}: {value}")
            
    elif command == 'ui':
        ui_main()

    elif command == 'test':
        print("Testing audio systems...")
        system.audio_manager.speak("Audio test. This is a test of the announcement system.")
        
    else:
        print(f"Unknown command: {command}")
        print_usage()


if __name__ == "__main__":
    main()