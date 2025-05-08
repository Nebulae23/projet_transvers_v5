#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Sound Generator for Nightfall Defenders
Generates placeholders for sound effects and ambiance
"""

import os
import wave
import array
import math
import random
import struct
import numpy as np
from enum import Enum
import time

class SoundType(Enum):
    """Types of sounds that can be generated"""
    UI = "ui"
    AMBIENT = "ambient"
    SFX = "sfx"
    MUSIC = "music"
    VOICE = "voice"

class SoundGenerator:
    """Generator for sound effects and ambient sounds"""
    
    def __init__(self, output_dir):
        """
        Initialize the sound generator
        
        Args:
            output_dir (str): Directory to save generated sounds
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Create subdirectories for different sound types
        self.sound_dirs = {
            SoundType.UI: os.path.join(output_dir, "ui"),
            SoundType.AMBIENT: os.path.join(output_dir, "ambient"),
            SoundType.SFX: os.path.join(output_dir, "sfx"),
            SoundType.MUSIC: os.path.join(output_dir, "music"),
            SoundType.VOICE: os.path.join(output_dir, "voice")
        }
        
        for directory in self.sound_dirs.values():
            os.makedirs(directory, exist_ok=True)
    
    def generate_with_cache(self, asset_id, params=None, seed=None):
        """
        Generate a sound asset with caching
        
        Args:
            asset_id (str): Identifier for the sound
            params (dict): Parameters for generation
            seed (int): Random seed for deterministic generation
            
        Returns:
            tuple: (sound data, sample rate)
        """
        if params is None:
            params = {}
            
        # Set random seed if provided
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
        
        # Determine sound type from asset_id
        sound_type = params.get("sound_type", None)
        if sound_type is None:
            if asset_id.startswith("ui_"):
                sound_type = SoundType.UI
            elif asset_id.startswith("ambient_"):
                sound_type = SoundType.AMBIENT
            elif asset_id.startswith("sfx_"):
                sound_type = SoundType.SFX
            elif asset_id.startswith("music_"):
                sound_type = SoundType.MUSIC
            elif asset_id.startswith("voice_"):
                sound_type = SoundType.VOICE
            else:
                # Default to SFX
                sound_type = SoundType.SFX
        
        # Generate sound based on type and ID
        if asset_id == "ui_notification_info" or asset_id.endswith("ui_notification_info.wav"):
            return self.generate_notification_sound(True, params)
        elif asset_id == "ui_notification_error" or asset_id.endswith("ui_notification_error.wav"):
            return self.generate_notification_sound(False, params)
        elif asset_id == "ambient_birds_morning" or asset_id.endswith("ambient_birds_morning.ogg"):
            return self.generate_ambient_sound("birds", params)
        elif asset_id == "ambient_wind_light" or asset_id.endswith("ambient_wind_light.ogg"):
            return self.generate_ambient_sound("wind", params)
        else:
            # Generate a default sound
            return self.generate_default_sound(sound_type, params)
    
    def generate_notification_sound(self, is_success, params=None):
        """
        Generate a notification sound
        
        Args:
            is_success (bool): Whether this is a success or error notification
            params (dict): Parameters for generation
            
        Returns:
            tuple: (sound data, sample rate)
        """
        if params is None:
            params = {}
            
        # Sound parameters
        sample_rate = params.get("sample_rate", 44100)
        duration = params.get("duration", 0.5 if is_success else 0.7)
        
        # Generate different tones based on success/error
        if is_success:
            # Success sound: rising tone
            frequencies = [440, 660]
            durations = [0.2, 0.3]
        else:
            # Error sound: falling tone
            frequencies = [440, 330, 220]
            durations = [0.2, 0.2, 0.3]
            
        # Generate sound data
        sound_data = []
        current_time = 0
        
        for freq, dur in zip(frequencies, durations):
            # Calculate number of samples for this tone
            num_samples = int(dur * sample_rate)
            
            # Generate tone
            for i in range(num_samples):
                t = current_time + i / sample_rate
                # Sine wave with fade in/out
                envelope = min(1.0, i / (0.1 * sample_rate)) * min(1.0, (num_samples - i) / (0.1 * sample_rate))
                value = int(32767 * envelope * math.sin(2 * math.pi * freq * t))
                sound_data.append(value)
                
            current_time += dur
            
        # Convert to bytes
        byte_data = struct.pack('<' + 'h' * len(sound_data), *sound_data)
        
        return byte_data, sample_rate
    
    def generate_ambient_sound(self, ambient_type, params=None):
        """
        Generate an ambient sound
        
        Args:
            ambient_type (str): Type of ambient sound to generate
            params (dict): Parameters for generation
            
        Returns:
            tuple: (sound data, sample rate)
        """
        if params is None:
            params = {}
            
        # Sound parameters
        sample_rate = params.get("sample_rate", 44100)
        duration = params.get("duration", 10.0)  # 10 seconds of ambient sound
        
        # Number of samples
        num_samples = int(duration * sample_rate)
        sound_data = np.zeros(num_samples, dtype=np.int16)
        
        if ambient_type == "birds":
            # Simulate bird chirps
            num_chirps = random.randint(20, 40)
            
            for _ in range(num_chirps):
                # Random timing for chirp
                chirp_start = random.randint(0, num_samples - int(0.3 * sample_rate))
                chirp_length = random.randint(int(0.1 * sample_rate), int(0.3 * sample_rate))
                chirp_freq = random.uniform(2000, 4000)
                
                # Create chirp
                for i in range(chirp_length):
                    t = i / sample_rate
                    # Chirp envelope
                    envelope = math.sin(math.pi * i / chirp_length)
                    # Add some frequency variation
                    freq_variation = chirp_freq * (1 + 0.1 * math.sin(2 * math.pi * 10 * t))
                    value = int(8000 * envelope * math.sin(2 * math.pi * freq_variation * t))
                    
                    if chirp_start + i < num_samples:
                        sound_data[chirp_start + i] += value
                        
        elif ambient_type == "wind":
            # Simulate wind using filtered noise
            noise = np.random.normal(0, 1, num_samples)
            
            # Apply low-pass filter for wind effect
            for i in range(1, num_samples):
                noise[i] = 0.95 * noise[i-1] + 0.05 * noise[i]
                
            # Scale and convert to int16
            sound_data = (noise * 8000).astype(np.int16)
        
        # Convert to bytes
        byte_data = sound_data.tobytes()
        
        return byte_data, sample_rate
    
    def generate_default_sound(self, sound_type, params=None):
        """
        Generate a default sound when specific type is not recognized
        
        Args:
            sound_type (SoundType): Type of sound to generate
            params (dict): Parameters for generation
            
        Returns:
            tuple: (sound data, sample rate)
        """
        if params is None:
            params = {}
            
        # Sound parameters
        sample_rate = params.get("sample_rate", 44100)
        duration = params.get("duration", 1.0)
        
        # Number of samples
        num_samples = int(duration * sample_rate)
        
        if sound_type == SoundType.UI:
            # Simple beep
            frequency = 440
            sound_data = []
            
            for i in range(num_samples):
                t = i / sample_rate
                # Sine wave with quick fade in/out
                envelope = min(1.0, i / (0.05 * sample_rate)) * min(1.0, (num_samples - i) / (0.05 * sample_rate))
                value = int(16000 * envelope * math.sin(2 * math.pi * frequency * t))
                sound_data.append(value)
                
        elif sound_type == SoundType.SFX:
            # White noise with envelope
            sound_data = []
            
            for i in range(num_samples):
                # Envelope: fade in/out
                envelope = min(1.0, i / (0.1 * sample_rate)) * min(1.0, (num_samples - i) / (0.1 * sample_rate))
                value = int(16000 * envelope * (random.random() * 2 - 1))
                sound_data.append(value)
                
        elif sound_type == SoundType.AMBIENT:
            # Low filtered noise
            sound_data = []
            last_value = 0
            
            for i in range(num_samples):
                # Low-pass filter for ambient sound
                new_value = 0.95 * last_value + 0.05 * (random.random() * 2 - 1)
                value = int(8000 * new_value)
                sound_data.append(value)
                last_value = new_value
                
        elif sound_type == SoundType.MUSIC:
            # Simple sine wave melody
            notes = [261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88]  # C4 to B4
            note_duration = 0.25  # quarter note
            sound_data = []
            
            for i in range(int(duration / note_duration)):
                frequency = random.choice(notes)
                for j in range(int(note_duration * sample_rate)):
                    t = j / sample_rate
                    # Sine wave with quick fade in/out
                    envelope = min(1.0, j / (0.05 * sample_rate)) * min(1.0, (int(note_duration * sample_rate) - j) / (0.05 * sample_rate))
                    value = int(16000 * envelope * math.sin(2 * math.pi * frequency * t))
                    sound_data.append(value)
                    
        else:  # VOICE or default
            # Just use a soft sine wave
            frequency = 150
            sound_data = []
            
            for i in range(num_samples):
                t = i / sample_rate
                # Sine wave with envelope
                envelope = min(1.0, i / (0.1 * sample_rate)) * min(1.0, (num_samples - i) / (0.1 * sample_rate))
                value = int(8000 * envelope * math.sin(2 * math.pi * frequency * t))
                sound_data.append(value)
        
        # Convert to bytes
        byte_data = struct.pack('<' + 'h' * len(sound_data), *sound_data)
        
        return byte_data, sample_rate
    
    def save_asset(self, asset_data, output_path):
        """
        Save the generated sound asset to disk
        
        Args:
            asset_data (tuple): (sound data, sample rate)
            output_path (str): Path to save the asset to
        """
        sound_data, sample_rate = asset_data
        
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Check file extension
            if output_path.lower().endswith('.wav'):
                self._save_wav(sound_data, sample_rate, output_path)
            elif output_path.lower().endswith('.ogg'):
                self._save_ogg(sound_data, sample_rate, output_path)
            else:
                # Default to WAV
                output_path = output_path + '.wav'
                self._save_wav(sound_data, sample_rate, output_path)
                
            print(f"Saved sound asset to {output_path}")
        except Exception as e:
            print(f"Error saving sound asset: {e}")
    
    def _save_wav(self, sound_data, sample_rate, output_path):
        """Save sound data in WAV format"""
        with wave.open(output_path, 'w') as wavfile:
            wavfile.setnchannels(1)  # Mono
            wavfile.setsampwidth(2)  # 2 bytes (16 bits)
            wavfile.setframerate(sample_rate)
            wavfile.writeframes(sound_data)
    
    def _save_ogg(self, sound_data, sample_rate, output_path):
        """Save sound data in OGG format"""
        try:
            # Convert WAV to OGG using pydub or another library
            # Since pydub might not be available, we'll create a temporary WAV file and try to convert it
            temp_wav = output_path.replace('.ogg', '.temp.wav')
            self._save_wav(sound_data, sample_rate, temp_wav)
            
            try:
                # Try to use pydub if available
                from pydub import AudioSegment
                AudioSegment.from_wav(temp_wav).export(output_path, format="ogg")
            except ImportError:
                # Fallback to subprocess if pydub is not available
                import subprocess
                try:
                    subprocess.check_call(['ffmpeg', '-i', temp_wav, '-c:a', 'libvorbis', '-q:a', '4', output_path])
                except:
                    print(f"Warning: Could not convert to OGG format. Keeping WAV file.")
                    # Rename temp file to .ogg
                    os.rename(temp_wav, output_path)
            
            # Clean up temp file if it still exists
            if os.path.exists(temp_wav):
                os.remove(temp_wav)
                
        except Exception as e:
            print(f"Error converting to OGG: {e}")
            # Fall back to WAV if conversion fails
            output_path = output_path.replace('.ogg', '.wav')
            self._save_wav(sound_data, sample_rate, output_path)
    
    def save_metadata(self, asset_id, metadata):
        """
        Save metadata for the generated asset
        
        Args:
            asset_id (str): Identifier for the asset
            metadata (dict): Metadata to save
        """
        # Create metadata directory if it doesn't exist
        metadata_dir = os.path.join(self.output_dir, "metadata")
        os.makedirs(metadata_dir, exist_ok=True)
        
        # Save metadata to JSON file
        import json
        metadata_path = os.path.join(metadata_dir, f"{asset_id}.json")
        
        try:
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
        except Exception as e:
            print(f"Error saving metadata: {e}")

def main():
    """Main entry point for testing"""
    import sys
    output_dir = sys.argv[1] if len(sys.argv) > 1 else "./output"
    
    generator = SoundGenerator(output_dir)
    
    # Generate and save some example sounds
    print("Generating notification sounds...")
    info_sound, rate = generator.generate_notification_sound(True)
    error_sound, rate = generator.generate_notification_sound(False)
    
    generator._save_wav(info_sound, rate, os.path.join(output_dir, "ui/ui_notification_info.wav"))
    generator._save_wav(error_sound, rate, os.path.join(output_dir, "ui/ui_notification_error.wav"))
    
    print("Generating ambient sounds...")
    birds_sound, rate = generator.generate_ambient_sound("birds")
    wind_sound, rate = generator.generate_ambient_sound("wind")
    
    generator._save_wav(birds_sound, rate, os.path.join(output_dir, "ambient/ambient_birds_morning.wav"))
    generator._save_wav(wind_sound, rate, os.path.join(output_dir, "ambient/ambient_wind_light.wav"))
    
    print("Sound generation complete!")

if __name__ == "__main__":
    main() 