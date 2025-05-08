#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Boss entity module for Nightfall Defenders
Extends the Enemy class with boss-specific behavior and component system
"""

from panda3d.core import NodePath, Vec3, TextNode
import math
import random
from game.enemy import Enemy
from game.enemy_psychology import PsychologicalState

# Possible boss phases
class BossPhase:
    """Enum for boss phases"""
    INTRO = "intro"
    PHASE1 = "phase1"
    PHASE2 = "phase2"
    PHASE3 = "phase3"
    ENRAGED = "enraged"
    VULNERABLE = "vulnerable"
    TRANSITION = "transition"
    DEFEATED = "defeated"

class Boss(Enemy):
    """Base class for all boss entities in the game"""
    
    def __init__(self, game, position=Vec3(0, 0, 0), boss_type="forest_guardian"):
        """
        Initialize the boss entity
        
        Args:
            game: Game instance
            position: Initial spawn position
            boss_type: Type of boss to create
        """
        # Initialize parent Enemy class
        super().__init__(game, position)
        
        # Boss-specific properties
        self.boss_type = boss_type
        self.name = self._get_name_from_type()
        self.title = self._get_title_from_type()
        self.description = self._get_description_from_type()
        
        # Enhanced stats for boss
        self.base_max_health = 500
        self.base_health = 500
        self.base_damage = 30
        self.max_health = self.base_max_health
        self.health = self.base_health
        self.damage = self.base_damage
        self.attack_range = 3.0
        self.detection_range = 25.0
        self.collision_radius = 1.5
        self.experience_value = 200
        
        # Apply difficulty adjustment if available
        self.apply_difficulty_adjustment()
        
        # Phase handling
        self.phases = [BossPhase.INTRO, BossPhase.PHASE1, BossPhase.PHASE2, BossPhase.PHASE3]
        self.current_phase = BossPhase.INTRO
        self.phase_health_thresholds = {
            BossPhase.PHASE1: 1.0,  # 100% health
            BossPhase.PHASE2: 0.7,  # 70% health
            BossPhase.PHASE3: 0.3,  # 30% health
            BossPhase.ENRAGED: 0.1  # 10% health
        }
        self.phase_transition_time = 0.0
        self.in_transition = False
        
        # Components system
        self.components = []
        
        # Special abilities
        self.abilities = {}
        self.current_ability = None
        self.ability_cooldowns = {}
        
        # Visual effects
        self.effect_nodes = {}
        
        # Encounter tracking
        self.encounter_started = False
        self.encounter_duration = 0.0
        self.defeated = False
        self.despawn_timer = 0.0
        
        # Rewards
        self.guaranteed_drops = []
        self.special_relic_chance = 0.5
        
        # Boss UI
        self.setup_boss_ui()
        
        # Override psychological thresholds to make bosses more resistant
        self.psychology.hesitant_threshold = 2.0
        self.psychology.fearful_threshold = 3.0
        self.psychology.terrified_threshold = 4.0
        self.psychology.subservient_threshold = 5.0
        
        # Bosses are less likely to become subservient
        self.psychology.subservience_chance = 0.01
        
        # Bosses are more resistant to psychological state changes
        self.psychology.inertia = 0.95
        
        # Initialize based on boss type
        self._initialize_boss_type()
    
    def _get_name_from_type(self):
        """Get the boss name based on type"""
        names = {
            "forest_guardian": "Thicket Sovereign",
            "ancient_construct": "Forgotten Automaton",
            "void_amalgamation": "Umbral Devourer",
            "default": "Unknown Entity"
        }
        return names.get(self.boss_type, names["default"])
    
    def _get_title_from_type(self):
        """Get the boss title based on type"""
        titles = {
            "forest_guardian": "Guardian of the Ancient Grove",
            "ancient_construct": "Relic of a Forgotten Age",
            "void_amalgamation": "Horror from the Abyss",
            "default": "Mysterious Creature"
        }
        return titles.get(self.boss_type, titles["default"])
    
    def _get_description_from_type(self):
        """Get the boss description based on type"""
        descriptions = {
            "forest_guardian": "A massive sentient plant creature that protects the ancient forests. Uses vines and toxic spores to attack.",
            "ancient_construct": "A mechanical monstrosity built by a long-dead civilization. Attacks with precision and devastating energy weapons.",
            "void_amalgamation": "A chaotic entity formed from the darkness itself. Unpredictable and capable of warping reality around it.",
            "default": "A mysterious entity with unknown origins and abilities."
        }
        return descriptions.get(self.boss_type, descriptions["default"])
    
    def _initialize_boss_type(self):
        """Initialize the boss based on its type"""
        # Placeholder - will be implemented in boss_factory.py
        pass
    
    def setup_model(self):
        """Set up the boss model with enhanced size and appearance"""
        try:
            # For now, use a larger box as placeholder
            self.model = self.game.loader.loadModel("models/box")
            self.model.setScale(2.0, 2.0, 3.0)  # Boss is larger than regular enemies
            self.model.reparentTo(self.root)
            
            # Color based on boss type
            colors = {
                "forest_guardian": (0.2, 0.8, 0.2, 1),  # Green
                "ancient_construct": (0.7, 0.7, 0.9, 1),  # Metallic blue
                "void_amalgamation": (0.3, 0.1, 0.3, 1),  # Dark purple
                "default": (0.9, 0.3, 0.3, 1)  # Red
            }
            self.model.setColor(colors.get(self.boss_type, colors["default"]))
            
            # Add crown to indicate boss status
            crown = self.game.loader.loadModel("models/box")
            crown.setScale(0.5, 0.5, 0.5)
            crown.setPos(0, 0, 1.5)
            crown.setColor(0.9, 0.8, 0.0, 1)  # Gold color
            crown.reparentTo(self.model)
            
        except Exception as e:
            print(f"Error loading boss model: {e}")
            # Fallback to a simple marker
            from panda3d.core import PointLight
            plight = PointLight("BossMarker")
            plight.setColor((1, 0, 0, 1))
            plnp = self.root.attachNewNode(plight)
            plnp.setPos(0, 0, 2)
    
    def setup_boss_ui(self):
        """Set up boss-specific UI elements"""
        # Full health bar at the top of the screen will be implemented in boss_ui.py
        # For now, create a special label for the boss
        from panda3d.core import TextNode
        self.name_label = TextNode('boss_name')
        self.name_label.setText(f"{self.name}")
        self.name_label.setAlign(TextNode.ACenter)
        self.name_label.setTextColor(1, 0.8, 0, 1)  # Gold color
        
        self.name_label_np = self.game.render.attachNewNode(self.name_label)
        self.name_label_np.setScale(2.0)
        self.name_label_np.setPos(0, 0, 5)  # Above the boss
        self.name_label_np.setBillboardPointEye()
    
    def add_component(self, component):
        """
        Add a component to the boss
        
        Args:
            component: The component to add
        """
        self.components.append(component)
    
    def get_component(self, component_type):
        """
        Get a component of the specified type
        
        Args:
            component_type: The type of component to get
            
        Returns:
            The first component of the specified type, or None if not found
        """
        for component in self.components:
            if isinstance(component, component_type):
                return component
        return None
    
    def update(self, dt):
        """Update the boss entity"""
        # Update base enemy functionality
        super().update(dt)
        
        # Update encounter tracking
        if self.encounter_started and not self.defeated:
            self.encounter_duration += dt
        
        # Check if we should transition to a new phase based on health
        self._check_phase_transitions()
        
        # Skip further updates if in transition
        if self.in_transition:
            self._update_transition(dt)
            return
        
        # Skip further updates if defeated
        if self.defeated:
            self._update_defeated(dt)
            return
        
        # Update all components
        for component in self.components:
            component.update(dt)
        
        # Update ability cooldowns
        for ability_name, cooldown in list(self.ability_cooldowns.items()):
            if cooldown > 0:
                self.ability_cooldowns[ability_name] -= dt
        
        # Update boss position
        self.root.setPos(self.position)
        
        # Update boss UI elements
        self._update_ui()
    
    def _check_phase_transitions(self):
        """Check and handle phase transitions based on health percentage"""
        if self.in_transition or self.defeated:
            return
            
        # Calculate current health percentage
        health_percent = self.health / self.max_health
        
        # Check if we should transition to a new phase
        for phase, threshold in self.phase_health_thresholds.items():
            if health_percent <= threshold and phase != self.current_phase:
                # Only transition if the new phase comes after the current one
                if self.phases.index(phase) > self.phases.index(self.current_phase):
                    self._begin_phase_transition(phase)
                    break
    
    def _begin_phase_transition(self, new_phase):
        """
        Begin transition to a new phase
        
        Args:
            new_phase: The phase to transition to
        """
        self.in_transition = True
        self.phase_transition_time = 0.0
        
        # Notify components about phase change
        for component in self.components:
            component.on_phase_change(new_phase)
        
        # Play transition effects
        self._play_phase_transition_effects(new_phase)
        
        print(f"Boss {self.name} entering {new_phase} phase!")
    
    def _update_transition(self, dt):
        """
        Update during phase transition
        
        Args:
            dt: Delta time in seconds
        """
        # Update transition timer
        self.phase_transition_time += dt
        
        # End transition after a set time
        if self.phase_transition_time >= 3.0:  # 3 second transition
            self.in_transition = False
            next_phase_index = self.phases.index(self.current_phase) + 1
            if next_phase_index < len(self.phases):
                self.current_phase = self.phases[next_phase_index]
            else:
                self.current_phase = BossPhase.ENRAGED
    
    def _update_defeated(self, dt):
        """
        Update after boss is defeated
        
        Args:
            dt: Delta time in seconds
        """
        # Update despawn timer
        self.despawn_timer += dt
        
        # Despawn after a set time
        if self.despawn_timer >= 5.0:  # 5 seconds after defeat
            self._despawn()
    
    def _play_phase_transition_effects(self, new_phase):
        """
        Play effects for phase transition
        
        Args:
            new_phase: The phase transitioning to
        """
        # Visual effects would go here - placeholder for now
        pass
    
    def _update_ui(self):
        """Update boss UI elements"""
        if self.name_label_np:
            # Position name label above boss
            self.name_label_np.setPos(self.position + Vec3(0, 0, 5))
            
            # Update label text with phase info
            if self.current_phase == BossPhase.INTRO:
                phase_text = "Awakening"
            elif self.current_phase == BossPhase.PHASE1:
                phase_text = "Phase I"
            elif self.current_phase == BossPhase.PHASE2:
                phase_text = "Phase II"
            elif self.current_phase == BossPhase.PHASE3:
                phase_text = "Phase III"
            elif self.current_phase == BossPhase.ENRAGED:
                phase_text = "ENRAGED"
            elif self.current_phase == BossPhase.VULNERABLE:
                phase_text = "VULNERABLE"
            else:
                phase_text = ""
                
            if phase_text:
                self.name_label.setText(f"{self.name}\n{phase_text}")
    
    def use_ability(self, ability_name):
        """
        Use a boss ability
        
        Args:
            ability_name: Name of the ability to use
            
        Returns:
            bool: True if ability was used, False if on cooldown or not found
        """
        # Check if ability exists and is not on cooldown
        if ability_name in self.abilities and self.ability_cooldowns.get(ability_name, 0) <= 0:
            ability = self.abilities[ability_name]
            
            # Set current ability
            self.current_ability = ability_name
            
            # Apply cooldown
            self.ability_cooldowns[ability_name] = ability.get("cooldown", 5.0)
            
            # Notify components
            for component in self.components:
                component.on_ability_use(ability_name)
            
            print(f"Boss {self.name} used ability: {ability_name}")
            return True
            
        return False
    
    def take_damage(self, amount, source=None):
        """
        Boss takes damage with special effects and phase transitions
        
        Args:
            amount: Amount of damage to take
            source: Source of the damage (player, ability, etc.)
        """
        # Record the damage in the performance tracker if available
        if hasattr(self.game, 'performance_tracker'):
            self.game.performance_tracker.record_combat_event('damage_dealt', amount)
        
        # Apply the damage
        self.health -= amount
        self.health = max(0, self.health)
        health_percent = self.health / self.max_health
        
        # Update health bar
        if hasattr(self, 'health_bar'):
            self.health_bar.update_health(health_percent)
        
        # Check for phase transitions
        if not self.in_transition and self.current_phase != BossPhase.DEFEATED:
            self._check_phase_transitions()
        
        # Check if defeated
        if self.health <= 0 and self.current_phase != BossPhase.DEFEATED:
            self._begin_phase_transition(BossPhase.DEFEATED)
            
            # Record boss defeat in the performance tracker and adaptive difficulty system
            if hasattr(self.game, 'performance_tracker'):
                defeat_time = self.encounter_duration
                self.game.performance_tracker.record_boss_event('victory', self.boss_type, defeat_time)
                
            if hasattr(self.game, 'adaptive_difficulty_system'):
                defeat_time = self.encounter_duration
                self.game.adaptive_difficulty_system.record_boss_event('defeat', defeat_time)
                
        # Trigger visual feedback
        if amount > 0:
            # Flash effect for damage feedback
            if hasattr(self, 'model'):
                original_color = self.model.getColor()
                self.model.setColor(1, 1, 1, 1)  # Flash white
                
                # Reset color after a short delay
                from direct.task.Task import Task
                
                def reset_color(task):
                    if hasattr(self, 'model'):
                        self.model.setColor(original_color)
                    return Task.done
                
                self.game.taskMgr.doMethodLater(0.1, reset_color, f"{self.name}_reset_color")
    
    def _on_defeated(self):
        """Handle boss defeat"""
        self.defeated = True
        self.current_phase = BossPhase.DEFEATED
        self.despawn_timer = 0.0
        
        # Stop movement and attacks
        self.velocity = Vec3(0, 0, 0)
        
        # Notify components
        for component in self.components:
            component.on_phase_change(BossPhase.DEFEATED)
        
        # Drop rewards
        self._drop_boss_rewards()
        
        # Trigger victory effects and notifications
        self._play_victory_effects()
        
        print(f"Boss {self.name} has been defeated!")
        
        # In a full implementation, this would notify the boss_manager
    
    def _drop_boss_rewards(self):
        """Drop boss-specific rewards"""
        # Standard resource drops with higher amounts
        self.drop_resources()
        
        # Experience drop
        self.drop_experience()
        
        # Guaranteed special drops
        for drop_info in self.guaranteed_drops:
            resource_type = drop_info.get("type", "crystal")
            amount = drop_info.get("amount", 5)
            
            # Create the drop at a random position near the boss
            offset = Vec3(
                random.uniform(-1.0, 1.0),
                random.uniform(-1.0, 1.0),
                0
            )
            drop_pos = self.position + offset
            
            # Create the resource drop
            self.game.entity_manager.create_resource_drop(drop_pos, resource_type, amount)
        
        # Chance for special relic
        if random.random() < self.special_relic_chance:
            # In a full implementation, this would create a special relic drop
            # through the relic system
            print(f"Boss {self.name} dropped a special relic!")
    
    def _play_victory_effects(self):
        """Play victory effects after boss defeat"""
        # Visual effects would go here - placeholder for now
        pass
    
    def _despawn(self):
        """Despawn the boss entity"""
        # Cleanup UI elements
        if self.name_label_np:
            self.name_label_np.removeNode()
        
        # Cleanup components
        for component in self.components:
            component.cleanup()
        
        # Remove from game
        if self.game.entity_manager:
            self.game.entity_manager.remove_entity(self)
    
    def cleanup(self):
        """Clean up boss resources"""
        for component in self.components:
            component.cleanup()
        
        if self.name_label_np:
            self.name_label_np.removeNode()
        
        # Call parent cleanup
        super().cleanup()
    
    def apply_difficulty_adjustment(self):
        """Apply difficulty adjustment to boss stats based on adaptive difficulty system"""
        if hasattr(self.game, 'adaptive_difficulty_system'):
            # Get difficulty factors
            factors = self.game.adaptive_difficulty_system.get_current_difficulty_factors()
            
            # Apply boss-specific difficulty multiplier for health
            # Bosses are more significantly affected by the boss_difficulty factor
            boss_health_multiplier = factors['enemy_health'] * factors['boss_difficulty']
            self.max_health = int(self.base_max_health * boss_health_multiplier)
            self.health = self.max_health
            
            # Apply damage multiplier (affected by both enemy_damage and boss_difficulty)
            boss_damage_multiplier = factors['enemy_damage'] * (0.7 + (0.3 * factors['boss_difficulty']))
            self.damage = self.base_damage * boss_damage_multiplier
            
            # Apply other adjustments (phases, abilities, etc.)
            # Harder difficulty means faster phase transitions
            phase_speed_modifier = 1.0 + (factors['boss_difficulty'] - 1.0) * 0.5
            
            # Adjust ability cooldowns based on difficulty (harder = faster abilities)
            for ability_name in self.ability_cooldowns:
                base_cooldown = self.ability_cooldowns[ability_name]
                if isinstance(base_cooldown, (int, float)):
                    # Harder difficulty = shorter cooldowns (more frequent attacks)
                    cooldown_modifier = 1.0 / (0.8 + (0.2 * factors['boss_difficulty']))
                    self.ability_cooldowns[ability_name] = base_cooldown * cooldown_modifier
            
            # Print debug info if debug mode is enabled
            if hasattr(self.game, 'debug_mode') and self.game.debug_mode:
                print(f"Applied difficulty adjustment to boss {self.name}:")
                print(f"  Health: {self.max_health} (x{boss_health_multiplier:.2f})")
                print(f"  Damage: {self.damage} (x{boss_damage_multiplier:.2f})")
                print(f"  Phase Speed: x{phase_speed_modifier:.2f}") 