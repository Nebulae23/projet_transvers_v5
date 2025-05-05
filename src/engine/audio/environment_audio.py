# src/engine/audio/environment_audio.py
from typing import Dict, Optional, Tuple
import random

class EnvironmentSound:
    def __init__(self, sound_id: str, min_interval: float, max_interval: float):
        self.sound_id = sound_id
        self.min_interval = min_interval
        self.max_interval = max_interval
        self.timer = random.uniform(min_interval, max_interval)
        
class WeatherSound:
    def __init__(self, sound_id: str, intensity: float = 1.0):
        self.sound_id = sound_id
        self.intensity = intensity
        self.active = False

class EnvironmentAudioSystem:
    def __init__(self, audio_engine):
        self.audio_engine = audio_engine
        self.ambient_sounds: Dict[str, EnvironmentSound] = {}
        self.weather_sounds: Dict[str, WeatherSound] = {}
        
    def load_sounds(self):
        # Load ambient sounds
        ambient_sounds = {
            "birds": (15.0, 30.0),
            "crickets": (10.0, 20.0),
            "wind_light": (20.0, 40.0),
            "wind_strong": (15.0, 25.0),
            "water_stream": (25.0, 45.0),
        }
        
        for sound_id, (min_int, max_int) in ambient_sounds.items():
            self.audio_engine.load_sound(
                f"ambient_{sound_id}",
                f"assets/audio/environment/{sound_id}.ogg"
            )
            self.ambient_sounds[sound_id] = EnvironmentSound(
                f"ambient_{sound_id}",
                min_int,
                max_int
            )
            
        # Load weather sounds
        weather_sounds = [
            "rain_light",
            "rain_heavy",
            "thunder_distant",
            "thunder_close",
            "wind_gust"
        ]
        
        for sound_id in weather_sounds:
            self.audio_engine.load_sound(
                f"weather_{sound_id}",
                f"assets/audio/weather/{sound_id}.ogg"
            )
            self.weather_sounds[sound_id] = WeatherSound(f"weather_{sound_id}")
            
    def update(self, dt: float):
        # Update ambient sounds
        for sound in self.ambient_sounds.values():
            sound.timer -= dt
            if sound.timer <= 0:
                self.play_sound(sound.sound_id)
                sound.timer = random.uniform(sound.min_interval, sound.max_interval)
                
        # Update weather sounds
        for sound in self.weather_sounds.values():
            if sound.active:
                # Continuously play weather sounds with varying intensity
                source_id = f"weather_{sound.sound_id}"
                if source_id in self.audio_engine.sources:
                    self.audio_engine.al_source_f(
                        self.audio_engine.sources[source_id],
                        AL_GAIN,
                        sound.intensity
                    )
                    
    def play_sound(self, sound_id: str, position: Optional[Tuple[float, float, float]] = None):
        if position:
            self.audio_engine.spatial_audio.play_sound_at_position(sound_id, position)
        else:
            source_id = f"env_{sound_id}_{random.randint(0, 1000)}"
            self.audio_engine.create_source(source_id)
            self.audio_engine.play_sound(sound_id, source_id)
            
    def set_weather(self, weather_type: str, intensity: float):
        # Update weather sound states
        if weather_type == "rain":
            self.weather_sounds["rain_light"].active = intensity < 0.5
            self.weather_sounds["rain_heavy"].active = intensity >= 0.5
            self.weather_sounds["thunder_distant"].active = intensity > 0.3
            self.weather_sounds["thunder_close"].active = intensity > 0.7
        elif weather_type == "wind":
            self.weather_sounds["wind_gust"].active = True
            self.weather_sounds["wind_gust"].intensity = intensity