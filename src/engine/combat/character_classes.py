# src/engine/combat/character_classes.py
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import numpy as np
from .ability_system import AbilityType, Ability
from .combat_fx import CombatEffects

class CharacterClass(Enum):
    SPELLBLADE = "spellblade"
    SHADOWMAGE = "shadowmage"
    BEASTMASTER = "beastmaster"
    TIMEMAGE = "timemage"

@dataclass
class ClassStats:
    health: float
    mana: float
    strength: float
    intelligence: float
    agility: float
    defense: float
    
@dataclass
class ClassVisuals:
    main_color: tuple
    accent_color: tuple
    weapon_effect: str
    idle_particles: str
    combat_aura: str
    
class CharacterClassManager:
    def __init__(self):
        self.fx_system = CombatEffects()
        self.classes: Dict[CharacterClass, Tuple[ClassStats, ClassVisuals]] = {
            CharacterClass.SPELLBLADE: (
                ClassStats(120, 100, 14, 12, 10, 8),
                ClassVisuals(
                    (0.2, 0.6, 1.0), (1.0, 0.8, 0.2),
                    "blade_energy", "arcane_sparkles", "blade_aura"
                )
            ),
            CharacterClass.SHADOWMAGE: (
                ClassStats(90, 130, 8, 16, 12, 6),
                ClassVisuals(
                    (0.3, 0.0, 0.4), (0.8, 0.0, 1.0),
                    "shadow_tendrils", "dark_wisps", "shadow_shroud"
                )
            ),
            CharacterClass.BEASTMASTER: (
                ClassStats(110, 80, 12, 8, 14, 10),
                ClassVisuals(
                    (0.0, 0.6, 0.3), (0.8, 0.4, 0.0),
                    "beast_claw", "nature_leaves", "primal_aura"
                )
            ),
            CharacterClass.TIMEMAGE: (
                ClassStats(100, 120, 6, 15, 8, 7),
                ClassVisuals(
                    (0.8, 0.8, 1.0), (0.4, 0.8, 0.8),
                    "time_ripple", "clock_particles", "temporal_distortion"
                )
            )
        }
        
class Character:
    def __init__(self, char_class: CharacterClass, level: int = 1):
        self.class_type = char_class
        self.level = level
        self.manager = CharacterClassManager()
        
        # Get class configuration
        stats, visuals = self.manager.classes[char_class]
        
        # Initialize stats
        self.stats = ClassStats(
            health=stats.health * level,
            mana=stats.mana * level,
            strength=stats.strength * (1 + 0.1 * level),
            intelligence=stats.intelligence * (1 + 0.1 * level),
            agility=stats.agility * (1 + 0.1 * level),
            defense=stats.defense * (1 + 0.1 * level)
        )
        
        # Initialize visual effects
        self.visuals = visuals
        self.current_effects = []
        self._setup_visual_effects()
        
        # Initialize abilities
        self.abilities = self._setup_abilities()
        
    def _setup_visual_effects(self):
        # Set up HD-2D visual effects for the character
        self.current_effects = [
            self.manager.fx_system.create_effect(
                self.visuals.idle_particles,
                self.visuals.main_color
            ),
            self.manager.fx_system.create_effect(
                self.visuals.combat_aura,
                self.visuals.accent_color,
                intensity=0.5
            )
        ]
        
        # Setup weapon trail effect
        self.weapon_trail = self.manager.fx_system.create_effect(
            self.visuals.weapon_effect,
            self.visuals.main_color
        )
        
    def _setup_abilities(self) -> Dict[str, Ability]:
        if self.class_type == CharacterClass.SPELLBLADE:
            return {
                "arcane_slash": Ability("Arcane Slash", 25, 3.0, AbilityType.PHYSICAL,
                                     fx_type="blade_energy_wave"),
                "spell_burst": Ability("Spell Burst", 40, 8.0, AbilityType.MAGICAL,
                                    fx_type="arcane_explosion"),
                "blade_dance": Ability("Blade Dance", 35, 10.0, AbilityType.PHYSICAL,
                                    fx_type="dancing_blades"),
                "energy_shield": Ability("Energy Shield", 0, 15.0, AbilityType.BUFF,
                                      fx_type="energy_barrier")
            }
        elif self.class_type == CharacterClass.SHADOWMAGE:
            return {
                "shadow_bolt": Ability("Shadow Bolt", 30, 2.0, AbilityType.MAGICAL,
                                    fx_type="shadow_projectile"),
                "void_rupture": Ability("Void Rupture", 45, 10.0, AbilityType.MAGICAL,
                                     fx_type="void_explosion"),
                "dark_embrace": Ability("Dark Embrace", 0, 12.0, AbilityType.BUFF,
                                     fx_type="shadow_shield"),
                "nightmare": Ability("Nightmare", 35, 15.0, AbilityType.MAGICAL,
                                  fx_type="nightmare_field")
            }
        elif self.class_type == CharacterClass.BEASTMASTER:
            return {
                "primal_strike": Ability("Primal Strike", 28, 3.0, AbilityType.PHYSICAL,
                                      fx_type="beast_slash"),
                "summon_companion": Ability("Summon Companion", 0, 20.0, AbilityType.SUMMON,
                                        fx_type="beast_summon"),
                "nature_fury": Ability("Nature's Fury", 40, 12.0, AbilityType.HYBRID,
                                    fx_type="nature_storm"),
                "wild_instinct": Ability("Wild Instinct", 0, 15.0, AbilityType.BUFF,
                                      fx_type="primal_power")
            }
        elif self.class_type == CharacterClass.TIMEMAGE:
            return {
                "temporal_bolt": Ability("Temporal Bolt", 25, 2.0, AbilityType.MAGICAL,
                                     fx_type="time_projectile"),
                "chronosphere": Ability("Chronosphere", 35, 10.0, AbilityType.MAGICAL,
                                    fx_type="time_bubble"),
                "time_dilation": Ability("Time Dilation", 0, 15.0, AbilityType.BUFF,
                                      fx_type="time_slow"),
                "paradox_blast": Ability("Paradox Blast", 50, 20.0, AbilityType.MAGICAL,
                                      fx_type="temporal_explosion")
            }