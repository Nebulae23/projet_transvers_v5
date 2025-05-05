# src/engine/audio/music_system.py
from typing import Dict, Optional
import pyfmodex as fmod
import numpy as np
from dataclasses import dataclass

@dataclass
class MusicLayer:
    track: fmod.Sound
    channel: Optional[fmod.Channel] = None
    volume: float = 1.0
    
class MusicSystem:
    def __init__(self, fmod_system):
        self.system = fmod_system
        self.current_track: Optional[str] = None
        self.layers: Dict[str, Dict[str, MusicLayer]] = {}
        self.crossfade_time = 2.0  # seconds
        
    def load_music_track(self, track_id: str, file_path: str, 
                        layers: Optional[Dict[str, str]] = None):
        if layers:
            self.layers[track_id] = {}
            for layer_name, layer_path in layers.items():
                sound = self.system.create_sound(
                    layer_path,
                    mode=fmod.MODE_LOOP_NORMAL | fmod.MODE_CREATESTREAM
                )
                self.layers[track_id][layer_name] = MusicLayer(sound)
        else:
            # Single track loading
            sound = self.system.create_sound(
                file_path,
                mode=fmod.MODE_LOOP_NORMAL | fmod.MODE_CREATESTREAM
            )
            self.layers[track_id] = {"main": MusicLayer(sound)}
            
    def play_track(self, track_id: str):
        if track_id not in self.layers:
            return
            
        if self.current_track:
            self._crossfade_to(track_id)
        else:
            self._start_track(track_id)
            
        self.current_track = track_id
        
    def _start_track(self, track_id: str):
        for layer_name, layer in self.layers[track_id].items():
            channel = self.system.play_sound(layer.track)
            channel.volume = layer.volume
            self.layers[track_id][layer_name].channel = channel
            
    def _crossfade_to(self, new_track_id: str):
        old_layers = self.layers[self.current_track]
        new_layers = self.layers[new_track_id]
        
        # Start new track
        self._start_track(new_track_id)
        
        # Fade out old track
        for layer in old_layers.values():
            if layer.channel:
                layer.channel.fade_volume(0, self.crossfade_time * 1000)
                
        # Fade in new track
        for layer in new_layers.values():
            if layer.channel:
                layer.channel.volume = 0
                layer.channel.fade_volume(layer.volume, self.crossfade_time * 1000)
                
    def set_layer_volume(self, track_id: str, layer_name: str, volume: float):
        if track_id in self.layers and layer_name in self.layers[track_id]:
            layer = self.layers[track_id][layer_name]
            layer.volume = volume
            if layer.channel:
                layer.channel.volume = volume
                
    def update(self):
        self.system.update()