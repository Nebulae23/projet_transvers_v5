# src/engine/audio/sound_manager.py
from typing import Dict, Optional
from .audio_engine import AudioEngine
from .music_system import MusicSystem
from .spatial_audio import SpatialAudioSystem
from .environment_audio import EnvironmentAudioSystem
from .combat_audio import CombatAudioSystem
from .ui_audio import UIAudioSystem

class SoundManager:
    def __init__(self):
        self.audio_engine = AudioEngine()
        self.music_system = MusicSystem(self.audio_engine.fmod_system)
        self.spatial_audio = SpatialAudioSystem(self.audio_engine)
        self.environment_audio = EnvironmentAudioSystem(self.audio_engine)
        self.combat_audio = CombatAudioSystem(self.audio_engine)
        self.ui_audio = UIAudioSystem(self.audio_engine)
        
        self._load_default_sounds()
        
    def _load_default_sounds(self):
        # Load music tracks
        self.music_system.load_music_track(
            "town_peaceful",
            "assets/audio/music/town_peaceful.ogg",
            {
                "ambient": "assets/audio/music/town_ambient.ogg",
                "activity": "assets/audio/music/town_activity.ogg"
            }
        )
        
        self.music_system.load_music_track(
            "combat",
            "assets/audio/music/combat.ogg",
            {
                "base": "assets/audio/music/combat_base.ogg",
                "intense": "assets/audio/music/combat_intense.ogg",
                "victory": "assets/audio/music/combat_victory.ogg"
            }
        )
        
        # Load environment sounds
        self.environment_audio.load_sounds()
        
        # Load combat sounds
        self.combat_audio.load_sounds()
        
        # Load UI sounds
        self.ui_audio.load_sounds()
        
    def update(self, dt: float, player_position, player_velocity, player_orientation):
        # Update listener position
        self.audio_engine.update_listener(
            player_position,
            player_velocity,
            player_orientation
        )
        
        # Update subsystems
        self.music_system.update()
        self.spatial_audio.update(dt)
        self.environment_audio.update(dt)
        self.combat_audio.update(dt)
        
    def play_music(self, track_id: str):
        self.music_system.play_track(track_id)
        
    def play_environment_sound(self, sound_id: str, position=None):
        self.environment_audio.play_sound(sound_id, position)
        
    def play_combat_sound(self, sound_id: str, position=None):
        self.combat_audio.play_sound(sound_id, position)
        
    def play_ui_sound(self, sound_id: str):
        self.ui_audio.play_sound(sound_id)
        
    def cleanup(self):
        self.audio_engine.cleanup()