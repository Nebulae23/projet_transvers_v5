# src/engine/audio/combat_audio.py
from typing import Dict, Optional, Tuple
import random

class CombatSound:
    def __init__(self, base_sound_id: str, variations: int = 1):
        self.base_sound_id = base_sound_id
        self.variations = variations
        self.last_variation = -1

class CombatAudioSystem:
    def __init__(self, audio_engine):
        self.audio_engine = audio_engine
        self.combat_sounds: Dict[str, CombatSound] = {}
        self.active_sounds: Dict[str, float] = {}  # sound_id: cooldown
        
    def load_sounds(self):
        # Melee combat sounds
        melee_sounds = {
            "sword_swing": 3,
            "sword_hit": 4,
            "sword_block": 2,
            "sword_parry": 2,
            "impact_flesh": 3,
            "impact_metal": 3
        }
        
        # Magic combat sounds
        magic_sounds = {
            "spell_cast": 4,
            "spell_impact": 3,
            "magic_charge": 2,
            "magic_release": 2,
            "element_fire": 3,
            "element_ice": 2,
            "element_lightning": 2
        }
        
        # Load all combat sounds with variations
        for sound_type, sounds in [("melee", melee_sounds), ("magic", magic_sounds)]:
            for sound_id, variations in sounds.items():
                full_id = f"{sound_type}_{sound_id}"
                
                # Load each variation
                for i in range(variations):
                    self.audio_engine.load_sound(
                        f"{full_id}_{i}",
                        f"assets/audio/combat/{sound_type}/{sound_id}_{i}.ogg"
                    )
                    
                self.combat_sounds[full_id] = CombatSound(full_id, variations)
                
    def play_sound(self, sound_id: str, position: Optional[Tuple[float, float, float]] = None):
        if sound_id not in self.combat_sounds:
            return
            
        combat_sound = self.combat_sounds[sound_id]
        
        # Select variation avoiding recent ones
        variation = random.randint(0, combat_sound.variations - 1)
        while variation == combat_sound.last_variation and combat_sound.variations > 1:
            variation = random.randint(0, combat_sound.variations - 1)
        combat_sound.last_variation = variation
        
        # Construct final sound ID with variation
        final_sound_id = f"{combat_sound.base_sound_id}_{variation}"
        
        # Play the sound
        if position:
            self.audio_engine.spatial_audio.play_sound_at_position(final_sound_id, position)
        else:
            source_id = f"combat_{final_sound_id}_{random.randint(0, 1000)}"
            self.audio_engine.create_source(source_id)
            self.audio_engine.play_sound(final_sound_id, source_id)
            
    def play_combo_sound(self, combo_type: str, combo_count: int, position: Optional[Tuple[float, float, float]] = None):
        # Play increasingly intense sounds for combos
        base_sound = "melee_sword_swing" if combo_type == "melee" else "magic_spell_cast"
        
        # Adjust volume and pitch based on combo count
        source_id = f"combo_{combo_type}_{random.randint(0, 1000)}"
        self.audio_engine.create_source(source_id)
        
        # Increase intensity with combo count
        volume = min(1.0 + (combo_count * 0.1), 2.0)
        pitch = min(1.0 + (combo_count * 0.05), 1.5)
        
        al_source = self.audio_engine.sources[source_id]
        self.audio_engine.al_source_f(al_source, AL_GAIN, volume)
        self.audio_engine.al_source_f(al_source, AL_PITCH, pitch)
        
        if position:
            self.audio_engine.spatial_audio.update_source_position(source_id, position)
            
        self.play_sound(base_sound, position)
        
    def update(self, dt: float):
        # Update cooldowns for active sounds
        finished_sounds = []
        for sound_id, cooldown in self.active_sounds.items():
            self.active_sounds[sound_id] -= dt
            if self.active_sounds[sound_id] <= 0:
                finished_sounds.append(sound_id)
                
        # Remove finished sounds
        for sound_id in finished_sounds:
            del self.active_sounds[sound_id]