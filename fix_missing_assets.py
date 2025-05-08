#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Nightfall Defenders - Fix Missing Assets Script
Generates the specific missing assets identified in the game
"""

import os
import sys
import time
import random
import shutil

def main():
    """Generate specific missing assets"""
    print("=" * 60)
    print("Nightfall Defenders - Fix Missing Assets")
    print("=" * 60)
    
    start_time = time.time()
    
    # Ensure necessary directories exist
    base_dir = os.path.dirname(os.path.abspath(__file__))
    ui_dir = os.path.join(base_dir, "src", "assets", "generated", "ui")
    sounds_dir = os.path.join(base_dir, "src", "assets", "sounds")
    sfx_dir = os.path.join(sounds_dir, "sfx")
    ambient_dir = os.path.join(sounds_dir, "ambient")
    models_dir = os.path.join(base_dir, "src", "assets", "generated", "models")
    
    os.makedirs(ui_dir, exist_ok=True)
    os.makedirs(sfx_dir, exist_ok=True)
    os.makedirs(ambient_dir, exist_ok=True)
    os.makedirs(models_dir, exist_ok=True)
    
    # Set random seed for reproducibility
    random.seed(42)
    
    # 1. Generate main menu background
    print("Generating main menu background...")
    try:
        from src.tools.asset_generator.ui_generator import UIGenerator
        ui_generator = UIGenerator(ui_dir)
        main_menu_bg = ui_generator.generate_main_menu_background()
        main_menu_bg.save(os.path.join(ui_dir, "main_menu_bg.png"))
        print("Main menu background generated successfully!")
    except Exception as e:
        print(f"Error generating main menu background: {e}")
    
    # 2. Generate notification sounds
    print("Generating notification sounds...")
    try:
        from src.tools.asset_generator.sound_generator import SoundGenerator
        sound_generator = SoundGenerator(sounds_dir)
        
        # Generate UI notification sounds
        info_sound, rate = sound_generator.generate_notification_sound(True)
        error_sound, rate = sound_generator.generate_notification_sound(False)
        
        sound_generator._save_wav(info_sound, rate, os.path.join(sfx_dir, "ui_notification_info.wav"))
        sound_generator._save_wav(error_sound, rate, os.path.join(sfx_dir, "ui_notification_error.wav"))
        
        # Generate ambient sounds as WAV instead of OGG
        birds_sound, rate = sound_generator.generate_ambient_sound("birds")
        wind_sound, rate = sound_generator.generate_ambient_sound("wind")
        
        sound_generator._save_wav(birds_sound, rate, os.path.join(ambient_dir, "ambient_birds_morning.wav"))
        sound_generator._save_wav(wind_sound, rate, os.path.join(ambient_dir, "ambient_wind_light.wav"))
        
        print("Sound assets generated successfully!")
    except Exception as e:
        print(f"Error generating sound assets: {e}")
    
    # 3. Generate plane model
    print("Generating plane model...")
    try:
        from src.tools.asset_generator.model_generator import ModelGenerator
        model_generator = ModelGenerator(models_dir)
        model_generator.generate_plane_model()
        
        # Also copy the plane model to the panda3d models directory
        target_model_dir = os.path.join(base_dir, "models")
        os.makedirs(target_model_dir, exist_ok=True)
        
        # Copy plane.egg to models/plane.egg
        source_path = os.path.join(models_dir, "plane.egg")
        target_path = os.path.join(target_model_dir, "plane.egg")
        
        if os.path.exists(source_path):
            shutil.copy2(source_path, target_path)
            print(f"Copied plane model to {target_path}")
            
        print("Plane model generated successfully!")
    except Exception as e:
        print(f"Error generating plane model: {e}")
    
    # Create basic sound files if they weren't created by the generator
    if not os.path.exists(os.path.join(sfx_dir, "ui_notification_info.wav")):
        print("Creating fallback notification info sound...")
        try:
            # Create a very basic WAV file
            import wave
            import struct
            import math
            
            with wave.open(os.path.join(sfx_dir, "ui_notification_info.wav"), 'w') as wav_file:
                # Set parameters
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(44100)  # 44.1kHz
                
                # Generate a simple beep
                data = []
                for i in range(22050):  # 0.5 seconds
                    value = int(32767 * 0.5 * math.sin(2 * math.pi * 440 * i / 44100))
                    data.append(struct.pack('<h', value))
                
                wav_file.writeframes(b''.join(data))
        except Exception as e:
            print(f"Error creating fallback sound: {e}")
    
    # Calculate duration
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"Missing assets fixed in {duration:.2f} seconds!")
    print("You can now run the game with: python run_game.py")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 