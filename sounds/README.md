# Sound Files Directory

This directory should contain your audio files for SwiftBell.

## Required Sound Files (configure paths in config.py):

- `morning_bell.wav` - Bell sound for school day start
- `class_bell.wav` - Standard class transition bell
- `break_bell.wav` - Break time bell
- `lunch_bell.wav` - Lunch time bell  
- `dismissal_bell.wav` - End of day bell
- `evacuation.wav` - Emergency evacuation siren
- `test_beep.wav` - Test sound for audio system check

## File Format Requirements:

- **Supported formats**: WAV, MP3, OGG
- **Recommended**: WAV files for best compatibility
- **Bit rate**: 16-bit or 24-bit
- **Sample rate**: 44.1kHz or 48kHz
- **Duration**: Keep under 30 seconds for efficiency

## Where to Get Sound Files:

1. **Free Sources**:
   - Freesound.org (CC licensed sounds)
   - Zapsplat.com (free with registration)
   - YouTube Audio Library
   
2. **Create Your Own**:
   - Record using Audacity (free audio editor)
   - Use online tone generators for simple bells
   
3. **Commercial Sources**:
   - AudioJungle
   - Pond5

## File Naming Convention:

Use descriptive names that match your timetable configuration:
- `morning_bell.wav`
- `period_change_bell.wav`
- `emergency_evacuation_siren.wav`

## Volume Levels:

Ensure all sound files have consistent volume levels. You can normalize them using:
- Audacity (Effect > Normalize)
- Online audio tools
- Command line tools like FFmpeg

## Testing:

Use the system's test command to verify all sounds work:
```bash
python main.py test
```