#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Utility to generate simple test sound files for Nightfall Defenders
These are placeholder sounds for testing the audio system
"""

import os
import numpy as np
from scipy.io import wavfile

# Define the output directory
OUTPUT_DIR = os.path.join("src", "assets", "sounds")
SAMPLE_RATE = 44100  # 44.1 kHz

def ensure_directories():
    """Ensure all required directories exist"""
    for category in ["sfx", "music", "ambient", "ui", "voice"]:
        dir_path = os.path.join(OUTPUT_DIR, category)
        os.makedirs(dir_path, exist_ok=True)
        print(f"Ensured directory exists: {dir_path}")

def generate_tone(freq, duration, volume=0.5, fade=0.1):
    """
    Generate a simple tone
    
    Args:
        freq: Frequency in Hz
        duration: Duration in seconds
        volume: Volume (0.0 to 1.0)
        fade: Fade in/out duration in seconds
        
    Returns:
        Numpy array of audio samples
    """
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    tone = np.sin(freq * 2 * np.pi * t) * volume
    
    # Apply fade in/out
    fade_samples = int(SAMPLE_RATE * fade)
    if fade_samples > 0:
        fade_in = np.linspace(0, 1, fade_samples)
        fade_out = np.linspace(1, 0, fade_samples)
        
        # Apply fade in
        tone[:fade_samples] *= fade_in
        
        # Apply fade out
        tone[-fade_samples:] *= fade_out
    
    return tone

def generate_noise(duration, volume=0.3, fade=0.1):
    """Generate white noise"""
    noise = np.random.uniform(-1, 1, int(SAMPLE_RATE * duration)) * volume
    
    # Apply fade in/out
    fade_samples = int(SAMPLE_RATE * fade)
    if fade_samples > 0:
        fade_in = np.linspace(0, 1, fade_samples)
        fade_out = np.linspace(1, 0, fade_samples)
        
        # Apply fade in
        noise[:fade_samples] *= fade_in
        
        # Apply fade out
        noise[-fade_samples:] *= fade_out
    
    return noise

def save_wav(samples, filename):
    """Save audio samples to WAV file"""
    # Convert to 16-bit PCM
    samples = (samples * 32767).astype(np.int16)
    
    # Save to file
    wavfile.write(filename, SAMPLE_RATE, samples)
    print(f"Saved: {filename}")

def generate_combat_sounds():
    """Generate placeholder combat sound effects"""
    sfx_dir = os.path.join(OUTPUT_DIR, "sfx")
    
    # Generate weapon swing sounds
    for i in range(1, 4):
        # Whoosh sound - mix of frequencies
        duration = 0.3
        samples = generate_tone(300, duration, 0.3, 0.05)
        samples += generate_tone(600, duration, 0.2, 0.05)
        save_wav(samples, os.path.join(sfx_dir, f"weapon_swing_{i}.wav"))
    
    # Generate weapon hit sounds
    for i in range(1, 4):
        # Impact sound - noise with low tone
        duration = 0.2
        samples = generate_noise(duration, 0.5, 0.01)
        samples += generate_tone(120, duration, 0.7, 0.01)
        save_wav(samples, os.path.join(sfx_dir, f"weapon_hit_{i}.wav"))
    
    # Generate weapon block sounds
    for i in range(1, 3):
        # Metallic block - high frequency with noise
        duration = 0.3
        samples = generate_noise(duration, 0.3, 0.05)
        samples += generate_tone(800, duration, 0.6, 0.05)
        save_wav(samples, os.path.join(sfx_dir, f"weapon_block_{i}.wav"))

def generate_ambient_sounds():
    """Generate placeholder ambient sounds"""
    ambient_dir = os.path.join(OUTPUT_DIR, "ambient")
    
    # Wind sounds - different intensities
    wind_types = ["light", "medium", "strong", "eerie"]
    for wind_type in wind_types:
        duration = 5.0  # 5 seconds, will be looped
        
        # Base noise
        volume = 0.2 if wind_type == "light" else 0.4 if wind_type == "medium" else 0.6
        samples = generate_noise(duration, volume, 0.5)
        
        # For eerie wind, add some tones
        if wind_type == "eerie":
            # Add some eerie high tones
            samples += generate_tone(700, duration, 0.1, 0.5)
            samples += generate_tone(1200, duration, 0.05, 0.5)
        
        save_wav(samples, os.path.join(ambient_dir, f"ambient_wind_{wind_type}.wav"))
    
    # Cricket sounds
    cricket_types = ["light", "", "heavy"]
    for cricket_type in cricket_types:
        duration = 5.0
        
        # Create cricket chirps - series of short tones
        samples = np.zeros(int(SAMPLE_RATE * duration))
        
        # Number of chirps depends on intensity
        chirp_count = 10 if cricket_type == "light" else 20 if cricket_type == "" else 40
        
        for _ in range(chirp_count):
            # Random time for chirp
            start_time = np.random.uniform(0, duration - 0.1)
            start_sample = int(start_time * SAMPLE_RATE)
            
            # Create a short chirp
            chirp_duration = 0.05
            chirp_samples = int(chirp_duration * SAMPLE_RATE)
            chirp = generate_tone(4000, chirp_duration, 0.3, 0.01)
            
            # Add to main samples
            end_sample = min(start_sample + chirp_samples, len(samples))
            samples[start_sample:end_sample] += chirp[:end_sample-start_sample]
        
        type_suffix = f"_{cricket_type}" if cricket_type else ""
        save_wav(samples, os.path.join(ambient_dir, f"ambient_crickets{type_suffix}.wav"))

def generate_ui_sounds():
    """Generate placeholder UI sounds"""
    ui_dir = os.path.join(OUTPUT_DIR, "ui")
    
    # UI click sound
    click_samples = generate_tone(1000, 0.1, 0.4, 0.02)
    save_wav(click_samples, os.path.join(ui_dir, "ui_click.wav"))
    
    # UI hover sound
    hover_samples = generate_tone(700, 0.05, 0.2, 0.01)
    save_wav(hover_samples, os.path.join(ui_dir, "ui_hover.wav"))
    
    # UI toggle sound - need to make sure both samples are the same length
    duration = 0.15
    toggle_samples = generate_tone(900, duration, 0.3, 0.03)
    # Add a higher tone that starts midway
    second_tone = generate_tone(1200, duration, 0.3, 0.02)
    toggle_samples += second_tone
    save_wav(toggle_samples, os.path.join(ui_dir, "ui_toggle.wav"))

def generate_music_samples():
    """Generate very basic music samples"""
    music_dir = os.path.join(OUTPUT_DIR, "music")
    
    # Extremely simple music patterns
    patterns = {
        "exploration": [(300, 0.5), (400, 0.5), (350, 0.5), (500, 0.5)],
        "combat": [(200, 0.25), (200, 0.25), (300, 0.5), (200, 0.25), (200, 0.25), (350, 0.5)],
        "menu": [(600, 1.0), (500, 1.0), (400, 1.0), (500, 1.0)]
    }
    
    for name, pattern in patterns.items():
        # Create a longer sequence by repeating the pattern
        duration = sum(note[1] for note in pattern) * 4
        samples = np.zeros(int(SAMPLE_RATE * duration))
        
        time_idx = 0
        for _ in range(4):  # Repeat pattern 4 times
            for freq, note_duration in pattern:
                note_samples = int(note_duration * SAMPLE_RATE)
                end_idx = min(time_idx + note_samples, len(samples))
                
                # Create note with envelope
                note = generate_tone(freq, note_duration, 0.5, min(0.05, note_duration / 4))
                samples[time_idx:end_idx] += note[:end_idx - time_idx]
                
                time_idx += note_samples
        
        save_wav(samples, os.path.join(music_dir, f"{name}.wav"))

def main():
    """Main function to generate all test sounds"""
    print("Generating test sound files for Nightfall Defenders...")
    
    # Ensure directories exist
    ensure_directories()
    
    # Generate sounds for each category
    generate_combat_sounds()
    generate_ambient_sounds()
    generate_ui_sounds()
    generate_music_samples()
    
    print("Sound generation complete!")

if __name__ == "__main__":
    main() 