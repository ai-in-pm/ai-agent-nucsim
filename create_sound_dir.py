import os
import wave
import struct

# Create sounds directory
sounds_dir = 'sounds'
if not os.path.exists(sounds_dir):
    os.makedirs(sounds_dir)

def create_simple_wav(filename, frequency=440, duration=0.1, volume=0.5):
    # Audio parameters
    sample_rate = 44100
    num_samples = int(sample_rate * duration)
    
    # Create WAV file
    with wave.open(os.path.join(sounds_dir, filename), 'w') as wav_file:
        # Set parameters
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 2 bytes per sample
        wav_file.setframerate(sample_rate)
        
        # Generate simple sine wave
        for i in range(num_samples):
            value = int(32767.0 * volume * (i / num_samples))  # Simple fade out
            data = struct.pack('<h', value)
            wav_file.writeframes(data)

# Create sound effects
create_simple_wav('click.wav', frequency=880, duration=0.05)
create_simple_wav('hover.wav', frequency=440, duration=0.1)
create_simple_wav('connect.wav', frequency=660, duration=0.15)
create_simple_wav('alert.wav', frequency=220, duration=0.2)

print("Sound files created successfully")
