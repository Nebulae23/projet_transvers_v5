# src/engine/audio/spatial_audio.py
from typing import Dict, Tuple, Optional
import numpy as np

class SpatialAudioSource:
    def __init__(self, source_id: str, position: Tuple[float, float, float]):
        self.source_id = source_id
        self.position = list(position)
        self.velocity = [0.0, 0.0, 0.0]
        self.active = True

class SpatialAudioSystem:
    def __init__(self, audio_engine):
        self.audio_engine = audio_engine
        self.sources: Dict[str, SpatialAudioSource] = {}
        self.max_distance = 50.0
        self.reference_distance = 5.0
        
    def create_source(self, source_id: str, position: Tuple[float, float, float]) -> Optional[str]:
        if source_id in self.sources:
            return None
            
        # Create OpenAL source
        al_source = self.audio_engine.create_source(source_id)
        if not al_source:
            return None
            
        # Set spatial audio properties
        self.audio_engine.al_source_f(al_source, AL_MAX_DISTANCE, self.max_distance)
        self.audio_engine.al_source_f(al_source, AL_REFERENCE_DISTANCE, self.reference_distance)
        self.audio_engine.al_source_f(al_source, AL_ROLLOFF_FACTOR, 1.0)
        
        # Create and store source
        source = SpatialAudioSource(source_id, position)
        self.sources[source_id] = source
        return source_id
        
    def update_source_position(self, source_id: str, position: Tuple[float, float, float],
                             velocity: Tuple[float, float, float] = (0.0, 0.0, 0.0)):
        if source_id in self.sources:
            source = self.sources[source_id]
            source.position = list(position)
            source.velocity = list(velocity)
            
            # Update OpenAL source position and velocity
            self.audio_engine.al_source_3f(
                self.audio_engine.sources[source_id],
                AL_POSITION,
                *position
            )
            self.audio_engine.al_source_3f(
                self.audio_engine.sources[source_id],
                AL_VELOCITY,
                *velocity
            )
            
    def play_sound_at_position(self, sound_id: str, position: Tuple[float, float, float]):
        source_id = f"spatial_{sound_id}_{len(self.sources)}"
        source_id = self.create_source(source_id, position)
        if source_id:
            self.audio_engine.play_sound(sound_id, source_id)
            
    def update(self, dt: float):
        # Update all spatial audio sources
        inactive_sources = []
        for source_id, source in self.sources.items():
            if not source.active:
                inactive_sources.append(source_id)
                
        # Cleanup inactive sources
        for source_id in inactive_sources:
            del self.sources[source_id]