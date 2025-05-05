# src/engine/audio/ui_audio.py
from typing import Dict
import random

class UIAudioSystem:
    def __init__(self, audio_engine):
        self.audio_engine = audio_engine
        self.ui_sounds: Dict[str, str] = {}
        
    def load_sounds(self):
        # Menu sounds
        menu_sounds = {
            "button_hover": "hover",
            "button_click": "click",
            "menu_open": "open",
            "menu_close": "close",
            "scroll": "scroll",
            "error": "error"
        }
        
        # Notification sounds
        notification_sounds = {
            "quest_complete": "complete",
            "quest_update": "update",
            "item_pickup": "pickup",
            "level_up": "level_up",
            "achievement": "achieve"
        }
        
        # Load all UI sounds
        for sound_type, sounds in [("menu", menu_sounds), ("notification", notification_sounds)]:
            for sound_id, filename in sounds.items():
                full_id = f"ui_{sound_type}_{sound_id}"
                self.audio_engine.load_sound(
                    full_id,
                    f"assets/audio/ui/{sound_type}/{filename}.ogg"
                )
                self.ui_sounds[sound_id] = full_id
                
    def play_sound(self, sound_id: str):
        if sound_id not in self.ui_sounds:
            return
            
        # Create a new source for the UI sound
        source_id = f"ui_{sound_id}_{random.randint(0, 1000)}"
        self.audio_engine.create_source(source_id)
        
        # Play the sound (non-spatial)
        self.audio_engine.play_sound(self.ui_sounds[sound_id], source_id)
        
    def play_notification(self, notification_type: str, importance: str = "normal"):
        # Adjust volume based on notification importance
        volume = {
            "low": 0.7,
            "normal": 1.0,
            "high": 1.3
        }.get(importance, 1.0)
        
        sound_id = f"ui_notification_{notification_type}"
        source_id = f"notification_{random.randint(0, 1000)}"
        
        self.audio_engine.create_source(source_id)
        al_source = self.audio_engine.sources[source_id]
        self.audio_engine.al_source_f(al_source, AL_GAIN, volume)
        
        self.audio_engine.play_sound(sound_id, source_id)