# find_voice.py
from config import Config
from audio_manager import AudioManager

def test_voices():
    config = Config()
    audio = AudioManager(config)
    
    print("=== AVAILABLE VOICES ===")
    voices = audio.list_available_voices()
    
    # Find English female voices
    english_female_voices = [v for v in voices if v['language'] == 'English' and v['gender'] == 'female']
    english_male_voices = [v for v in voices if v['language'] == 'English' and v['gender'] == 'male']
    
    print("\n=== ENGLISH FEMALE VOICES ===")
    for voice in english_female_voices:
        print(f"Name: {voice['name']}")
        print(f"ID: {voice['id']}")
        print("---")
    
    print("\n=== ENGLISH MALE VOICES ===")
    for voice in english_male_voices:
        print(f"Name: {voice['name']}")
        print(f"ID: {voice['id']}")
        print("---")
    
    # Test with first English female voice if available
    if english_female_voices:
        female_voice_id = english_female_voices[0]['id']
        print(f"\nTesting with English female voice: {english_female_voices[0]['name']}")
        
        # You can set this voice ID directly in your config.json:
        print(f"\nAdd this to your config.json:")
        print(f'{{"tts_voice": "{female_voice_id}"}}')
        
        # Test the voice
        audio.tts_engine.setProperty('voice', female_voice_id)
        audio.speak("This is a test of the English female voice.")
    else:
        print("No English female voices found.")

if __name__ == "__main__":
    test_voices()