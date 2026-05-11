# audio_manager.py

"""
Cross-platform audio management for sounds and text-to-speech
Windows → pyttsx3 (SAPI5 voices)
Linux   → espeak subprocess (direct, for male/female voices)
"""

import logging
import threading
import time
import os
import platform
import subprocess

# Use pygame for audio playback
try:
    import pygame
    pygame.mixer.init()
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    print("Warning: pygame not available. Install with: pip install pygame")

# Try TTS library (used only for Windows)
try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False
    print("Warning: pyttsx3 not available. Install with: pip install pyttsx3")


class AudioManager:
    """Manages audio: sounds + cross-platform TTS"""

    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)

        self.system = platform.system().lower()
        self.tts_engine = None

        # Audio playback state
        self.current_audio_thread = None
        self.stop_audio_flag = threading.Event()
        self.is_sequential_playback = False

        # Initialize TTS
        self._init_tts()

    def _init_tts(self):
        """Initialize TTS engine depending on OS"""
        try:
            if self.system == "windows" and PYTTSX3_AVAILABLE:
                # Windows → pyttsx3 (SAPI5)
                self.tts_engine = pyttsx3.init()
                self._configure_tts()
                self.logger.info("Windows TTS (SAPI5) initialized")

            elif self.system == "linux":
                # Force subprocess espeak on Linux
                self.tts_engine = None
                self.logger.info("Linux TTS will use subprocess espeak")

        except Exception as e:
            self.logger.error(f"Failed to initialize TTS: {e}")
            self.tts_engine = None

    def _configure_tts(self):
        """Configure pyttsx3 TTS (voice, rate, volume) on Windows"""
        if not self.tts_engine:
            return

        # Set rate
        rate = self.config.get("tts_rate", 200)
        self.tts_engine.setProperty("rate", rate)
        self.logger.info(f"Set speech rate: {rate}")

        # Set volume
        volume = self.config.get("tts_volume", 1.0)
        self.tts_engine.setProperty("volume", volume)
        self.logger.info(f"Set volume: {volume}")

        # Try to match voice preference
        voice_pref = self.config.get("tts_voice", "female").lower()
        voices = self.tts_engine.getProperty("voices")

        chosen = None
        for voice in voices:
            vname = voice.name.lower()
            vid = voice.id.lower()
            if "english" in vname or "en" in vid:
                if voice_pref == "female" and "female" in vname:
                    chosen = voice
                    break
                if voice_pref == "male" and "male" in vname:
                    chosen = voice
                    break

        # Fallbacks
        if not chosen:
            for voice in voices:
                if "english" in voice.name.lower() or "en" in voice.id.lower():
                    chosen = voice
                    break
        if not chosen and voices:
            chosen = voices[0]

        if chosen:
            self.tts_engine.setProperty("voice", chosen.id)
            self.logger.info(f"Set {voice_pref} voice: {chosen.name}")

    def speak(self, message: str, priority: bool = False, skip_check: bool = False):
        """Speak a message using TTS"""
        if priority:
            self.stop_all()

        def _speak():
            try:
                self.logger.info(f"Speaking: {message}")
                if self.system == "windows" and self.tts_engine:
                    self.tts_engine.say(message)
                    self.tts_engine.runAndWait()
                elif self.system == "linux":
                    # Linux → subprocess espeak with gender selection
                    voice_pref = self.config.get("tts_voice", "female").lower()
                    if voice_pref == "female":
                        subprocess.run(["espeak", "-v", "en+f2", message])
                    else:
                        subprocess.run(["espeak", "-v", "en+m1", message])
                else:
                    self.logger.error("No TTS engine available")
            except Exception as e:
                self.logger.error(f"TTS error: {e}")

        if (
            not priority
            and not skip_check
            and self.current_audio_thread
            and self.current_audio_thread.is_alive()
        ):
            self.logger.info("Audio already playing, skipping announcement")
            return

        self.current_audio_thread = threading.Thread(target=_speak, daemon=True)
        self.current_audio_thread.start()

    def play_siren(self, file_path: str, repeat_count: int = 1):
        """Play siren sound file"""
        self._play_audio_file(file_path, "siren", repeat_count)

    def play_music(self, file_path: str, repeat_count: int = 1):
        """Play music file"""
        self._play_audio_file(file_path, "music", repeat_count)

    def play_siren_then_speak(self, file_path: str, message: str, repeat_count: int = 1):
        """Play siren sound (repeat_count times), then speak the given message"""
        def _sequence():
            try:
                # Step 1: Play siren(s)
                if os.path.exists(file_path) and PYGAME_AVAILABLE:
                    for _ in range(max(1, repeat_count)):
                        self.logger.info(f"Playing siren: {file_path}")
                        pygame.mixer.music.load(file_path)
                        pygame.mixer.music.play()
                        while pygame.mixer.music.get_busy():
                            if self.stop_audio_flag.is_set():
                                pygame.mixer.music.stop()
                                return
                            time.sleep(0.1)
                else:
                    self.logger.warning("Siren file not found or pygame unavailable, skipping siren")

                # Step 2: Speak
                self.speak(message, priority=True, skip_check=True)

            except Exception as e:
                self.logger.error(f"Error in play_siren_then_speak: {e}")

        self.stop_all()
        self.stop_audio_flag.clear()
        self.current_audio_thread = threading.Thread(target=_sequence, daemon=True)
        self.current_audio_thread.start()

    def play_music_then_speak(self, file_path: str, message: str, repeat_count: int = 1):
        """Play music file (repeat_count times), then speak the given message"""
        def _sequence():
            try:
                # Step 1: Play music
                if os.path.exists(file_path) and PYGAME_AVAILABLE:
                    for _ in range(max(1, repeat_count)):
                        self.logger.info(f"Playing music: {file_path}")
                        pygame.mixer.music.load(file_path)
                        pygame.mixer.music.play()
                        while pygame.mixer.music.get_busy():
                            if self.stop_audio_flag.is_set():
                                pygame.mixer.music.stop()
                                return
                            time.sleep(0.1)
                else:
                    self.logger.warning("Music file not found or pygame unavailable, skipping music")

                # Step 2: Speak
                self.speak(message, priority=True, skip_check=True)

            except Exception as e:
                self.logger.error(f"Error in play_music_then_speak: {e}")

        self.stop_all()
        self.stop_audio_flag.clear()
        self.current_audio_thread = threading.Thread(target=_sequence, daemon=True)
        self.current_audio_thread.start()

    def _play_audio_file(self, file_path: str, audio_type: str, repeat_count: int = 1):
        """Play audio file with pygame"""
        if not os.path.exists(file_path):
            self.logger.error(f"Audio file not found: {file_path}")
            return

        def _play():
            try:
                for _ in range(max(1, repeat_count)):
                    self.logger.info(f"Playing {audio_type}: {file_path}")
                    if PYGAME_AVAILABLE:
                        pygame.mixer.music.load(file_path)
                        pygame.mixer.music.play()
                        while pygame.mixer.music.get_busy():
                            if self.stop_audio_flag.is_set():
                                pygame.mixer.music.stop()
                                return
                            time.sleep(0.1)
                    else:
                        self.logger.error("pygame not available")
                        return
            except Exception as e:
                self.logger.error(f"Error playing {audio_type}: {e}")

        self.stop_all()
        self.stop_audio_flag.clear()
        self.current_audio_thread = threading.Thread(target=_play, daemon=True)
        self.current_audio_thread.start()

    def stop_all(self):
        """Stop all audio"""
        self.stop_audio_flag.set()
        if PYGAME_AVAILABLE:
            try:
                pygame.mixer.music.stop()
            except:
                pass
        if self.tts_engine:
            try:
                self.tts_engine.stop()
            except:
                pass
        self.logger.info("All audio stopped")

    def test_audio(self):
        """Test TTS and sound"""
        self.logger.info("Testing audio...")
        test_message = "Audio test. This is a test of the announcement system."
        self.speak(test_message)
