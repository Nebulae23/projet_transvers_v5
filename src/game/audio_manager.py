#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Audio Manager for Nightfall Defenders
Implements sound effects, music, and 3D positional audio
"""

import os
import json
import random
from typing import Dict, List, Optional, Tuple
from panda3d.core import AudioSound, AudioManager as P3DAudioManager
from panda3d.core import Point3, Vec3

class SoundCategory:
    """Enum for sound categories for volume control"""
    MUSIC = "music"
    SFX = "sfx"
    AMBIENT = "ambient"
    UI = "ui"
    VOICE = "voice"

class AudioManager:
    """Manages all game audio including sfx, music, and ambient sounds"""
    
    def __init__(self, game):
        """
        Initialize the audio manager
        
        Args:
            game: The main game instance
        """
        self.game = game
        
        # Initialize Panda3D audio system
        self.audio_manager = P3DAudioManager.createAudioManager()
        if not self.audio_manager.isValid():
            print("Warning: Audio system initialization failed. Game will run without sound.")
            self.audio_enabled = False
        else:
            self.audio_enabled = True
            
        # Sound asset cache
        self.sound_cache = {}
        
        # Active sounds (currently playing)
        self.active_sounds = {}
        
        # Music system
        self.current_music = None
        self.next_music = None
        self.music_crossfade_time = 2.0  # in seconds
        self.music_crossfade_timer = 0.0
        self.is_crossfading = False
        
        # Volume settings for each category
        self.volume_settings = {
            SoundCategory.MUSIC: 0.8,
            SoundCategory.SFX: 1.0,
            SoundCategory.AMBIENT: 0.7,
            SoundCategory.UI: 0.9,
            SoundCategory.VOICE: 1.0
        }
        
        # 3D audio settings
        self.audio_3d_settings = {
            "footstep_min_distance": 5.0,
            "footstep_max_distance": 30.0,
            "ambient_min_distance": 20.0,
            "ambient_max_distance": 100.0,
            "default_min_distance": 10.0,
            "default_max_distance": 50.0
        }
        
        # Sound pools for frequently used sounds to avoid constant loading
        self.sound_pools = {}
        
        # Sound cooldown system to prevent sound spamming
        self.sound_cooldowns = {}
        
        # List of ambient loops currently active
        self.ambient_loops = {}
        
        # Time-of-day specific ambient sounds
        self.time_ambient_sounds = {
            "dawn": ["ambient_birds_morning", "ambient_wind_light"],
            "day": ["ambient_birds_day", "ambient_wind_medium"],
            "dusk": ["ambient_crickets_light", "ambient_wind_medium"],
            "night": ["ambient_crickets", "ambient_wolf_howl", "ambient_wind_strong"],
            "midnight": ["ambient_crickets_heavy", "ambient_owl", "ambient_wind_eerie"]
        }
        
        # Load configuration
        self.load_config()
        
        # Create asset directory if it doesn't exist
        sound_dir = os.path.join("src", "assets", "sounds")
        os.makedirs(sound_dir, exist_ok=True)
        
        # Create subdirectories if they don't exist
        for subdir in ["music", "sfx", "ambient", "ui", "voice"]:
            os.makedirs(os.path.join(sound_dir, subdir), exist_ok=True)
    
    def load_config(self):
        """Load audio configuration from file"""
        # Try to load configuration from the config file
        config_path = os.path.join("src", "assets", "configs", "audio_config.json")
        
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                
                # Apply volume settings
                if "volume_settings" in config:
                    for category, volume in config["volume_settings"].items():
                        category_attr = getattr(SoundCategory, category.upper(), None)
                        if category_attr:
                            self.volume_settings[category_attr] = volume
                
                # Apply crossfade time
                if "crossfade_time" in config:
                    self.music_crossfade_time = config["crossfade_time"]
                    
                # Apply ambient sounds configuration
                if "ambient_sounds" in config:
                    self.time_ambient_sounds = config["ambient_sounds"]
                    
                # Apply 3D audio settings - these will be used in play_sound
                if "3d_audio" in config:
                    self.audio_3d_settings = config["3d_audio"]
                
                print(f"Audio configuration loaded from {config_path}")
            except Exception as e:
                print(f"Error loading audio config: {e}")
                print("Using default audio settings")
        else:
            print(f"Audio config file not found at {config_path}")
            print("Using default audio settings")
    
    def load_sound(self, sound_path: str, positional: bool = False) -> Optional[AudioSound]:
        """
        Load a sound file
        
        Args:
            sound_path: Path to the sound file
            positional: Whether this sound should be 3D positional
            
        Returns:
            AudioSound object or None if loading fails
        """
        if not self.audio_enabled:
            return None
            
        # Check cache first
        cache_key = f"{sound_path}_{positional}"
        if cache_key in self.sound_cache:
            return self.sound_cache[cache_key]
            
        # Make sure the path exists
        if not os.path.exists(sound_path):
            # Try relative to assets
            asset_path = os.path.join("src", "assets", "sounds", sound_path)
            if os.path.exists(asset_path):
                sound_path = asset_path
            else:
                print(f"Warning: Sound file not found: {sound_path}")
                return None
        
        try:
            # Load the sound
            if positional:
                sound = self.audio_manager.makeSoundWithListener(sound_path)
            else:
                sound = self.audio_manager.getSound(sound_path)
                
            if sound:
                self.sound_cache[cache_key] = sound
                return sound
            else:
                print(f"Warning: Failed to load sound: {sound_path}")
                return None
        except Exception as e:
            print(f"Error loading sound {sound_path}: {e}")
            return None
    
    def play_sound(self, sound_name: str, volume: float = 1.0, loop: bool = False, 
                  position: Tuple[float, float, float] = None, category: str = SoundCategory.SFX) -> Optional[str]:
        """
        Play a sound effect
        
        Args:
            sound_name: Name or path of the sound file
            volume: Volume multiplier (0.0 to 1.0)
            loop: Whether to loop the sound
            position: 3D position for the sound (x, y, z) or None for non-positional
            category: Sound category for volume control
            
        Returns:
            Sound ID for controlling the sound later, or None if failed
        """
        if not self.audio_enabled:
            return None
            
        # Check cooldown for this sound
        if sound_name in self.sound_cooldowns and self.sound_cooldowns[sound_name] > 0:
            return None
            
        # Apply category volume
        if category in self.volume_settings:
            volume *= self.volume_settings[category]
        
        # Determine if positional
        positional = position is not None
        
        # Find the sound path
        if not sound_name.endswith((".wav", ".ogg", ".mp3")):
            # Add appropriate extension based on category
            if category == SoundCategory.MUSIC:
                sound_path = f"music/{sound_name}.ogg"
            elif category == SoundCategory.AMBIENT:
                sound_path = f"ambient/{sound_name}.ogg"
            elif category == SoundCategory.UI:
                sound_path = f"ui/{sound_name}.wav"
            elif category == SoundCategory.VOICE:
                sound_path = f"voice/{sound_name}.ogg"
            else:  # SFX
                sound_path = f"sfx/{sound_name}.wav"
        else:
            sound_path = sound_name
        
        # Try to get from sound pool first
        pool_key = f"{sound_path}_{positional}"
        sound = None
        
        if pool_key in self.sound_pools:
            # Look for an available sound in the pool
            for pooled_sound in self.sound_pools[pool_key]:
                if not pooled_sound.status() == AudioSound.PLAYING:
                    sound = pooled_sound
                    break
        
        # If not found in pool, load it
        if sound is None:
            sound = self.load_sound(sound_path, positional)
            
            if sound is None:
                return None
                
            # Add to pool if it doesn't exist yet
            if pool_key not in self.sound_pools:
                self.sound_pools[pool_key] = []
            self.sound_pools[pool_key].append(sound)
        
        # Generate a unique ID for this sound instance
        sound_id = f"{sound_name}_{id(sound)}_{len(self.active_sounds)}"
        
        # Configure the sound
        sound.setVolume(volume)
        sound.setLoop(loop)
        
        # Set position if 3D
        if positional and position:
            sound.set3dAttributes(position[0], position[1], position[2], 0, 0, 0)
            
            # Set attenuation based on effect type
            if "footstep" in sound_name:
                sound.set3dMinDistance(self.audio_3d_settings["footstep_min_distance"])
                sound.set3dMaxDistance(self.audio_3d_settings["footstep_max_distance"])
            elif "ambient" in sound_name:
                sound.set3dMinDistance(self.audio_3d_settings["ambient_min_distance"])
                sound.set3dMaxDistance(self.audio_3d_settings["ambient_max_distance"])
            else:
                sound.set3dMinDistance(self.audio_3d_settings["default_min_distance"])
                sound.set3dMaxDistance(self.audio_3d_settings["default_max_distance"])
        
        # Play the sound
        sound.play()
        
        # Store in active sounds
        self.active_sounds[sound_id] = {
            "sound": sound,
            "category": category,
            "positional": positional,
            "base_volume": volume
        }
        
        # Set cooldown for sound to prevent spamming (mainly for SFX)
        if category == SoundCategory.SFX and not loop:
            self.sound_cooldowns[sound_name] = 0.05  # 50ms cooldown
        
        return sound_id
    
    def stop_sound(self, sound_id: str):
        """
        Stop a playing sound
        
        Args:
            sound_id: ID of the sound to stop
        """
        if not self.audio_enabled or sound_id not in self.active_sounds:
            return
            
        sound_data = self.active_sounds[sound_id]
        sound_data["sound"].stop()
        del self.active_sounds[sound_id]
    
    def play_music(self, music_name: str, crossfade: bool = True):
        """
        Play music track with optional crossfade
        
        Args:
            music_name: Name of the music file
            crossfade: Whether to crossfade from current track
        """
        if not self.audio_enabled:
            return
            
        # If already playing this music, do nothing
        if self.current_music and music_name in self.current_music:
            return
            
        volume = self.volume_settings[SoundCategory.MUSIC]
        
        if crossfade and self.current_music is not None:
            # Set up crossfade
            self.next_music = self.play_sound(music_name, 0.0, True, None, SoundCategory.MUSIC)
            self.is_crossfading = True
            self.music_crossfade_timer = 0.0
        else:
            # Stop current music if any
            if self.current_music is not None:
                self.stop_sound(self.current_music)
                
            # Start new music immediately
            self.current_music = self.play_sound(music_name, volume, True, None, SoundCategory.MUSIC)
    
    def update_ambient_sounds(self):
        """Update ambient sounds based on time of day and player location"""
        if not self.audio_enabled:
            return
            
        # Get current time of day
        time_of_day = "day"  # Default
        if hasattr(self.game, 'day_night_cycle'):
            # Check which method is available
            if hasattr(self.game.day_night_cycle, 'get_time_of_day_name'):
                time_of_day = self.game.day_night_cycle.get_time_of_day_name().lower()
            elif hasattr(self.game.day_night_cycle, 'getTimeOfDayName'):
                time_of_day = self.game.day_night_cycle.getTimeOfDayName().lower()
            elif hasattr(self.game.day_night_cycle, 'time_of_day_name'):
                time_of_day = self.game.day_night_cycle.time_of_day_name.lower()
            else:
                # Determine name based on numeric value if methods aren't available
                numeric_time = 0.5  # Default to midday
                
                if hasattr(self.game.day_night_cycle, 'get_time_of_day'):
                    numeric_time = self.game.day_night_cycle.get_time_of_day()
                elif hasattr(self.game.day_night_cycle, 'getTimeOfDay'):
                    numeric_time = self.game.day_night_cycle.getTimeOfDay()
                elif hasattr(self.game.day_night_cycle, 'time_of_day'):
                    numeric_time = self.game.day_night_cycle.time_of_day
                
                # Map numeric time to time of day name
                if numeric_time < 0.25:
                    time_of_day = "night"
                elif numeric_time < 0.4:
                    time_of_day = "dawn"
                elif numeric_time < 0.75:
                    time_of_day = "day"
                elif numeric_time < 0.9:
                    time_of_day = "dusk"
                else:
                    time_of_day = "night"
        
        # Check if we have ambient sounds for this time
        if time_of_day in self.time_ambient_sounds:
            # Get ambient sounds for this time
            ambient_list = self.time_ambient_sounds[time_of_day]
            
            # Stop any ambient sounds that shouldn't be playing
            for sound_id, sound_data in list(self.ambient_loops.items()):
                if sound_data["sound_name"] not in ambient_list:
                    self.stop_sound(sound_id)
                    del self.ambient_loops[sound_id]
            
            # Start any missing ambient sounds
            for ambient_sound in ambient_list:
                # Check if already playing
                already_playing = False
                for sound_data in self.ambient_loops.values():
                    if sound_data["sound_name"] == ambient_sound:
                        already_playing = True
                        break
                
                if not already_playing:
                    # Start this ambient sound
                    sound_id = self.play_sound(ambient_sound, 0.7, True, None, SoundCategory.AMBIENT)
                    if sound_id:
                        self.ambient_loops[sound_id] = {
                            "sound_name": ambient_sound,
                            "time_of_day": time_of_day
                        }
    
    def play_combat_sound(self, combat_type: str, intensity: float = 1.0, position: Tuple[float, float, float] = None):
        """
        Play an appropriate combat sound
        
        Args:
            combat_type: Type of combat sound (attack, hit, swing, etc.)
            intensity: Intensity of the action (0.0 to 1.0)
            position: 3D position for the sound or None
        """
        if not self.audio_enabled:
            return
            
        sound_options = []
        
        if combat_type == "swing":
            sound_options = ["weapon_swing_1", "weapon_swing_2", "weapon_swing_3"]
        elif combat_type == "hit":
            sound_options = ["weapon_hit_1", "weapon_hit_2", "weapon_hit_3"]
        elif combat_type == "block":
            sound_options = ["weapon_block_1", "weapon_block_2"]
        elif combat_type == "arrow":
            sound_options = ["arrow_shoot_1", "arrow_shoot_2"]
        elif combat_type == "magic":
            sound_options = ["magic_cast_1", "magic_cast_2", "magic_cast_3"]
        elif combat_type == "monster":
            sound_options = ["monster_attack_1", "monster_attack_2"]
        
        if sound_options:
            # Pick a random sound from the options
            sound_name = random.choice(sound_options)
            
            # Scale volume based on intensity
            volume = 0.6 + (intensity * 0.4)
            
            # Play the sound
            self.play_sound(sound_name, volume, False, position, SoundCategory.SFX)
    
    def update(self, dt: float):
        """
        Update the audio system
        
        Args:
            dt: Delta time in seconds
        """
        if not self.audio_enabled:
            return
            
        # Update 3D listener position to match the camera
        if hasattr(self.game, 'camera'):
            cam_pos = self.game.camera.getPos()
            cam_direction = self.game.camera.getQuat().getForward()
            
            # Try different method names and handle errors gracefully
            try:
                # Try different method names for setting 3D listener position
                if hasattr(self.audio_manager, 'set3dListenerAttributes'):
                    self.audio_manager.set3dListenerAttributes(
                        cam_pos.x, cam_pos.y, cam_pos.z,  # Position
                        cam_direction.x, cam_direction.y, cam_direction.z,  # Direction (forward vector)
                        0, 1, 0  # Up vector
                    )
                elif hasattr(self.audio_manager, 'setListenerAttributes'):
                    self.audio_manager.setListenerAttributes(
                        cam_pos.x, cam_pos.y, cam_pos.z,  # Position
                        cam_direction.x, cam_direction.y, cam_direction.z,  # Direction (forward vector)
                        0, 1, 0  # Up vector
                    )
                elif hasattr(self.audio_manager, 'setListenerPosition'):
                    # Just update position if that's all we can do
                    self.audio_manager.setListenerPosition(cam_pos.x, cam_pos.y, cam_pos.z)
                
                # Silently continue if 3D positioning isn't available
            except Exception as e:
                # Silently continue if the operation fails - 3D audio may not be fully implemented
                pass
        
        # Handle music crossfading
        if self.is_crossfading and self.next_music is not None:
            self.music_crossfade_timer += dt
            progress = min(1.0, self.music_crossfade_timer / self.music_crossfade_time)
            
            # Fade out current music
            if self.current_music in self.active_sounds:
                current_vol = (1.0 - progress) * self.volume_settings[SoundCategory.MUSIC]
                self.active_sounds[self.current_music]["sound"].setVolume(current_vol)
            
            # Fade in next music
            if self.next_music in self.active_sounds:
                next_vol = progress * self.volume_settings[SoundCategory.MUSIC]
                self.active_sounds[self.next_music]["sound"].setVolume(next_vol)
            
            # If crossfade complete
            if progress >= 1.0:
                # Stop old music
                if self.current_music in self.active_sounds:
                    self.stop_sound(self.current_music)
                
                # Set new music as current
                self.current_music = self.next_music
                self.next_music = None
                self.is_crossfading = False
        
        # Update ambient sounds
        self.update_ambient_sounds()
        
        # Clean up stopped sounds
        for sound_id in list(self.active_sounds.keys()):
            sound_data = self.active_sounds[sound_id]
            if sound_data["sound"].status() != AudioSound.PLAYING:
                del self.active_sounds[sound_id]
        
        # Decrease sound cooldowns
        for sound_name in list(self.sound_cooldowns.keys()):
            self.sound_cooldowns[sound_name] -= dt
            if self.sound_cooldowns[sound_name] <= 0:
                del self.sound_cooldowns[sound_name]
    
    def set_volume(self, category: str, volume: float):
        """
        Set volume for a category of sounds
        
        Args:
            category: Sound category to adjust
            volume: New volume (0.0 to 1.0)
        """
        if category not in self.volume_settings:
            return
            
        # Clamp volume to valid range
        volume = max(0.0, min(1.0, volume))
        
        # Store the new volume
        self.volume_settings[category] = volume
        
        # Update all playing sounds in this category
        for sound_id, sound_data in self.active_sounds.items():
            if sound_data["category"] == category:
                actual_volume = volume * sound_data["base_volume"]
                sound_data["sound"].setVolume(actual_volume)
    
    def cleanup(self):
        """Clean up audio resources"""
        if not self.audio_enabled:
            return
            
        # Stop all sounds
        for sound_id in list(self.active_sounds.keys()):
            self.active_sounds[sound_id]["sound"].stop()
        
        # Clear all sound pools
        for sound_list in self.sound_pools.values():
            for sound in sound_list:
                sound.stop()
        
        self.active_sounds.clear()
        self.sound_pools.clear()
        self.sound_cache.clear()
        
        # Shutdown audio manager
        self.audio_manager.shutdown() 