#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Enemy Psychological System for Nightfall Defenders
Implements psychological states and responses to player power
"""

import math
import random

class PsychologicalState:
    """Enumerates the possible psychological states of enemies"""
    NORMAL = "normal"
    HESITANT = "hesitant"
    FEARFUL = "fearful"
    TERRIFIED = "terrified"
    SUBSERVIENT = "subservient"
    EMPOWERED = "empowered"  # New state for fog-empowered enemies

class PsychologyTraits:
    """Defines psychological traits that affect enemy behavior and responses"""
    
    def __init__(self, 
                 bravery=1.0, 
                 aggression=1.0, 
                 intelligence=1.0, 
                 pack_mentality=1.0, 
                 dominance=1.0):
        """
        Initialize psychological traits
        
        Args:
            bravery (float): Resistance to fear (0.5-1.5)
                - Higher values increase thresholds for negative psychological states
                - Lower values make the enemy more easily frightened
            
            aggression (float): Tendency toward offensive action (0.5-1.5)
                - Higher values increase attack frequency and damage
                - Lower values lead to more defensive behavior
            
            intelligence (float): Tactical decision-making capability (0.5-1.5)
                - Higher values enable more complex strategies
                - Lower values lead to more predictable behavior
            
            pack_mentality (float): Influence from and on nearby allies (0.5-1.5)
                - Higher values make the enemy more affected by group psychology
                - Lower values make the enemy more independent
            
            dominance (float): Leadership and influence over others (0.5-1.5)
                - Higher values allow enemies to rally others
                - Lower values make them more likely to follow others
        """
        # Ensure traits are within valid range
        self.bravery = max(0.5, min(1.5, bravery))
        self.aggression = max(0.5, min(1.5, aggression))
        self.intelligence = max(0.5, min(1.5, intelligence))
        self.pack_mentality = max(0.5, min(1.5, pack_mentality))
        self.dominance = max(0.5, min(1.5, dominance))
        
        # Derived attributes
        self.is_alpha = dominance >= 1.3  # Alpha enemies have high dominance
        
    def get_state_threshold_modifier(self):
        """
        Calculate modification to psychological state thresholds
        
        Returns:
            float: Multiplier for state transition thresholds
        """
        # Brave enemies have higher thresholds (harder to frighten)
        return self.bravery
    
    def get_attack_modifier(self):
        """
        Calculate modification to attack behavior
        
        Returns:
            float: Multiplier for attack frequency and damage
        """
        return self.aggression
    
    def get_pack_influence(self):
        """
        Calculate how much influence the entity has on pack psychology
        
        Returns:
            float: Influence factor for emotional contagion
        """
        # Combines dominance and pack mentality
        return self.dominance * self.pack_mentality
    
    def get_intelligence_factor(self):
        """
        Calculate intelligence factor for decision making
        
        Returns:
            float: Intelligence factor for decision making
        """
        return self.intelligence

class EnemyPsychology:
    """Manages enemy psychological state and responses to player power"""
    
    def __init__(self, enemy, initial_state=PsychologicalState.NORMAL):
        """
        Initialize the psychological system
        
        Args:
            enemy: The enemy entity this system belongs to
            initial_state: The initial psychological state
        """
        self.enemy = enemy
        self.state = initial_state
        self.confidence = 1.0  # 0.0 to 1.0 scale (fully terrified to fully confident)
        
        # Add psychological traits (default to neutral values)
        self.traits = PsychologyTraits()
        
        # Apply trait-based modifiers to thresholds
        threshold_modifier = self.traits.get_state_threshold_modifier()
        
        # Thresholds for state transitions (overridable by enemy types)
        self.hesitant_threshold = 1.2 * threshold_modifier
        self.fearful_threshold = 1.5 * threshold_modifier
        self.terrified_threshold = 2.0 * threshold_modifier
        self.subservient_threshold = 3.0 * threshold_modifier
        
        # Memory system for tracking player encounters
        self.memory = {
            'player_encounters': 0,       # Number of times engaged with player
            'damage_taken': 0,            # Total damage taken from player
            'allies_lost': 0,             # Allies defeated in presence
            'last_encounter_outcome': None, # 'escaped', 'damaged', 'unharmed'
            'encounter_timestamps': [],    # Times of encounters for recency
            'grudge_factor': 0.0,         # Animosity towards player (0.0-1.0)
        }
        
        # Pack mentality tracking
        self.nearby_allies = []           # List of nearby allied enemies
        self.nearby_ally_count = 0        # Count of nearby allies
        self.pack_strength_bonus = 0.0    # Confidence bonus from pack
        self.alpha_nearby = False         # Whether an alpha enemy is nearby
        
        # Delayed reaction system
        self.pending_state_change = None  # Target state for delayed change
        self.state_change_delay = 0.0     # Delay before state change occurs
        self.reaction_timer = 0.0         # Timer for current reaction
        
        # Behavioral modifiers
        self.attack_chance_modifier = 1.0
        self.speed_modifier = 1.0
        self.damage_modifier = 1.0
        
        # Chance for subservience instead of terror (varies by enemy type)
        self.subservience_chance = 0.1  # 10% chance
        
        # Psychological inertia (resistance to rapid state changes)
        self.inertia = 0.8  # Higher values mean slower state changes
        
        # Visual indicators
        self.indicator_color = (1, 0, 0, 1)  # Default red
        self.indicator_node = None  # Node for visual indicator
        self.indicator_animation = None  # Animation effect for indicator
        self.indicator_emoji = None  # Emoji/icon representing state
        self.indicator_size = 1.0  # Size modifier for indicator
        self.indicator_pulse_speed = 1.0  # Animation speed for pulsing
        
        # Night fog effect
        self.in_fog = False
        self.fog_empowerment = 0.0
        
        # Update behavior modifiers based on initial state
        self._update_behavior_modifiers()
        
        # Set up visual indicators
        self._setup_visual_indicator()
    
    def _setup_visual_indicator(self):
        """Create visual indicator for psychological state"""
        if not hasattr(self.enemy, 'render_node') or not self.enemy.render_node:
            return
            
        # Clean up existing indicator if present
        if self.indicator_node:
            self.indicator_node.removeNode()
            
        try:
            from panda3d.core import NodePath, TextNode, TransparencyAttrib
            from direct.gui.OnscreenText import OnscreenText
            
            # Create parent node for indicator
            self.indicator_node = NodePath("psych_indicator")
            self.indicator_node.reparentTo(self.enemy.render_node)
            
            # Position above the enemy
            height = getattr(self.enemy, 'height', 1.0)
            self.indicator_node.setPos(0, 0, height * 1.2)
            
            # Look at camera
            if hasattr(self.enemy.game, 'camera'):
                self.indicator_node.lookAt(self.enemy.game.camera)
                
            # Create text node for emoji indicator
            self.indicator_emoji = TextNode("emoji_indicator")
            self.indicator_emoji.setText(self._get_state_emoji())
            self.indicator_emoji.setAlign(TextNode.ACenter)
            self.indicator_emoji.setTextColor(*self.indicator_color)
            
            # Create node path for emoji
            emoji_np = self.indicator_node.attachNewNode(self.indicator_emoji)
            emoji_np.setScale(0.5)
            emoji_np.setTransparency(TransparencyAttrib.MAlpha)
            
            # Create background circle
            from direct.gui.DirectGui import DirectFrame
            bg_frame = DirectFrame(
                frameColor=(0.1, 0.1, 0.1, 0.7),
                frameSize=(-0.2, 0.2, -0.2, 0.2),
                parent=self.indicator_node,
                pos=(0, 0, 0),
                scale=0.5
            )
            
            # Set initial state
            self._update_visual_indicator()
            
        except ImportError as e:
            print(f"Warning: Could not create psychological state indicator: {e}")
    
    def _get_state_emoji(self):
        """Get emoji representing current psychological state"""
        if self.state == PsychologicalState.NORMAL:
            return "😐"  # Neutral face
        elif self.state == PsychologicalState.HESITANT:
            return "😟"  # Worried face
        elif self.state == PsychologicalState.FEARFUL:
            return "😨"  # Fearful face
        elif self.state == PsychologicalState.TERRIFIED:
            return "😱"  # Screaming in fear
        elif self.state == PsychologicalState.SUBSERVIENT:
            return "🙇"  # Bowing in submission
        elif self.state == PsychologicalState.EMPOWERED:
            return "😈"  # Smiling devil (empowered by fog)
        else:
            return "❓"  # Question mark for unknown state
    
    def _update_visual_indicator(self):
        """Update the visual indicator based on current psychological state"""
        # Update color based on state
        if self.state == PsychologicalState.NORMAL:
            self.indicator_color = (0.7, 0.7, 0.7, 1.0)  # Gray for normal
            self.indicator_size = 1.0
            self.indicator_pulse_speed = 0.5
        elif self.state == PsychologicalState.HESITANT:
            self.indicator_color = (1.0, 0.8, 0.2, 1.0)  # Yellow for hesitant
            self.indicator_size = 1.1
            self.indicator_pulse_speed = 1.0
        elif self.state == PsychologicalState.FEARFUL:
            self.indicator_color = (1.0, 0.5, 0.0, 1.0)  # Orange for fearful
            self.indicator_size = 1.3
            self.indicator_pulse_speed = 1.5
        elif self.state == PsychologicalState.TERRIFIED:
            self.indicator_color = (1.0, 0.0, 0.0, 1.0)  # Red for terrified
            self.indicator_size = 1.5
            self.indicator_pulse_speed = 2.0
        elif self.state == PsychologicalState.SUBSERVIENT:
            self.indicator_color = (0.5, 0.5, 1.0, 1.0)  # Blue for subservient
            self.indicator_size = 1.2
            self.indicator_pulse_speed = 0.7
        elif self.state == PsychologicalState.EMPOWERED:
            self.indicator_color = (0.7, 0.0, 1.0, 1.0)  # Purple for fog-empowered
            self.indicator_size = 1.4
            self.indicator_pulse_speed = 1.5
        
        # Update the visual indicator if it exists
        if not self.indicator_emoji:
            return
            
        # Update emoji
        self.indicator_emoji.setText(self._get_state_emoji())
        self.indicator_emoji.setTextColor(*self.indicator_color)
        
        # Update size
        if self.indicator_node:
            self.indicator_node.setScale(self.indicator_size)
            
            # Ensure indicator always faces camera
            if hasattr(self.enemy.game, 'camera'):
                self.indicator_node.lookAt(self.enemy.game.camera)
            
            # Create pulse animation if not already created
            if not self.indicator_animation:
                # Use Panda3D sequence if available
                try:
                    from direct.interval.LerpInterval import LerpScaleInterval
                    from direct.interval.MetaInterval import Sequence
                    
                    # Create pulsing effect
                    scale_up = LerpScaleInterval(
                        self.indicator_node,
                        duration=0.5 / self.indicator_pulse_speed,
                        scale=self.indicator_size * 1.2,
                        startScale=self.indicator_size
                    )
                    
                    scale_down = LerpScaleInterval(
                        self.indicator_node,
                        duration=0.5 / self.indicator_pulse_speed,
                        scale=self.indicator_size,
                        startScale=self.indicator_size * 1.2
                    )
                    
                    self.indicator_animation = Sequence(scale_up, scale_down)
                    self.indicator_animation.loop()
                    
                except ImportError:
                    pass
            
            # Make visible or invisible based on state
            if self.state == PsychologicalState.NORMAL:
                self.indicator_node.hide()
            else:
                self.indicator_node.show()
    
    def update_indicator_animation(self, dt):
        """Update animation for the psychological indicator"""
        if not self.indicator_node:
            return
            
        # If using custom animation instead of Panda3D sequences
        if self.indicator_animation is None:
            # Simple pulse animation
            pulse_factor = 1.0 + 0.2 * math.sin(self.enemy.game.game_time * self.indicator_pulse_speed * 2.0 * math.pi)
            self.indicator_node.setScale(self.indicator_size * pulse_factor)
            
            # Ensure indicator always faces camera
            if hasattr(self.enemy.game, 'camera'):
                self.indicator_node.lookAt(self.enemy.game.camera)

    def calculate_player_power_ratio(self):
        """
        Calculate the ratio between player power and enemy power
        
        Returns:
            float: Player power / enemy power ratio
        """
        player = self.enemy.game.player
        if not player:
            return 1.0
        
        # Basic measure of player power from level, health, and weapon damage
        player_level = getattr(player, 'level', 1)
        player_health_ratio = getattr(player, 'health', 100) / getattr(player, 'max_health', 100)
        
        # Get player's current weapon damage
        projectile_type = getattr(player, 'projectile_type', 'straight')
        projectile_types = getattr(player, 'projectile_types', {})
        weapon_damage = 10  # Default value
        if projectile_type in projectile_types:
            weapon_damage = projectile_types[projectile_type].get('damage', 10)
        
        # City defense bonus if player is near city
        city_defense_bonus = 0
        if hasattr(self.enemy.game, 'city_manager'):
            city_manager = self.enemy.game.city_manager
            
            # Check if player is inside city boundaries
            player_pos = getattr(player, 'position', None)
            if player_pos and hasattr(city_manager, 'is_inside_city'):
                if city_manager.is_inside_city(player_pos):
                    city_defense_bonus = city_manager.defense / 100.0
        
        # Calculate player power
        player_power = player_level * (1.0 + weapon_damage / 10.0) * (0.5 + player_health_ratio / 2.0)
        player_power *= (1.0 + city_defense_bonus)
        
        # Increase player power based on memory/grudge factor
        memory_modifier = 1.0 + (self.memory['grudge_factor'] * 0.5)
        player_power *= memory_modifier
        
        # Reduce player power based on fog visibility at player's position
        if hasattr(self.enemy.game, 'night_fog'):
            player_pos = getattr(player, 'position', None)
            if player_pos:
                # Get visibility factor (1.0 = full visibility, 0.3 = minimum visibility)
                visibility = self.enemy.game.night_fog.get_visibility_factor(player_pos)
                # Reduce power by up to 50% in dense fog
                player_power *= (0.5 + visibility * 0.5)
        
        # Enemy power based on health ratio and base damage
        enemy_health_ratio = self.enemy.health / self.enemy.max_health
        enemy_power = self.enemy.damage * (0.5 + enemy_health_ratio / 2.0)
        
        # Apply fog empowerment to enemy power
        enemy_power *= (1.0 + self.fog_empowerment)
        
        # Apply pack strength bonus to enemy power
        enemy_power *= (1.0 + self.pack_strength_bonus)
        
        # Desperation factor - enemies get stronger when at critical health
        if enemy_health_ratio < 0.25:
            desperation_boost = (0.25 - enemy_health_ratio) * 2.0  # Up to 50% boost at 1 HP
            enemy_power *= (1.0 + desperation_boost)
        
        # Avoid division by zero
        if enemy_power <= 0:
            enemy_power = 0.1
            
        return player_power / enemy_power
    
    def calculate_pack_strength(self):
        """
        Calculate strength bonus from nearby allies
        
        Returns:
            float: Pack strength bonus multiplier
        """
        # Clear previous pack data
        self.nearby_allies = []
        self.nearby_ally_count = 0
        self.alpha_nearby = False
        
        # Get all enemies from entity manager
        if not hasattr(self.enemy.game, 'entity_manager'):
            return 0.0
            
        allies = self.enemy.game.entity_manager.enemies
        
        # Filter out self and defeated enemies
        allies = [ally for ally in allies if ally != self.enemy and ally.health > 0]
        
        # Check distance to each ally
        pack_range = 12.0  # Units within which pack mentality applies
        for ally in allies:
            if not hasattr(ally, 'position') or not hasattr(self.enemy, 'position'):
                continue
                
            distance = (ally.position - self.enemy.position).length()
            
            if distance <= pack_range:
                self.nearby_allies.append(ally)
                self.nearby_ally_count += 1
                
                # Check if this is an alpha
                if hasattr(ally, 'psychology') and hasattr(ally.psychology, 'traits'):
                    if ally.psychology.traits.is_alpha:
                        self.alpha_nearby = True
        
        # No allies means no pack bonus
        if self.nearby_ally_count == 0:
            return 0.0
            
        # Calculate base pack bonus based on number of allies
        base_bonus = min(0.5, self.nearby_ally_count * 0.1)  # Cap at 50%
        
        # Apply pack mentality trait
        trait_modifier = self.traits.pack_mentality
        
        # Alpha bonus
        alpha_bonus = 0.2 if self.alpha_nearby else 0.0
        
        # Calculate total pack strength bonus
        pack_bonus = base_bonus * trait_modifier + alpha_bonus
        
        return pack_bonus
    
    def record_player_encounter(self, encounter_type='spotted', damage_taken=0):
        """
        Record an encounter with the player
        
        Args:
            encounter_type (str): Type of encounter ('spotted', 'damaged', 'escaped')
            damage_taken (float): Amount of damage taken in this encounter
        """
        # Increment encounter counter
        self.memory['player_encounters'] += 1
        
        # Record damage if any
        if damage_taken > 0:
            self.memory['damage_taken'] += damage_taken
            self.memory['last_encounter_outcome'] = 'damaged'
            
            # Increase grudge based on damage
            grudge_increment = min(0.1, damage_taken / self.enemy.max_health)
            self.memory['grudge_factor'] = min(1.0, self.memory['grudge_factor'] + grudge_increment)
        elif encounter_type == 'escaped':
            self.memory['last_encounter_outcome'] = 'escaped'
            # Slightly reduce grudge when escaping successfully
            self.memory['grudge_factor'] = max(0.0, self.memory['grudge_factor'] - 0.05)
        else:
            self.memory['last_encounter_outcome'] = 'unharmed'
            
        # Record timestamp (game time)
        if hasattr(self.enemy.game, 'day_night_cycle'):
            current_time = self.enemy.game.day_night_cycle.current_time
            self.memory['encounter_timestamps'].append(current_time)
            
            # Keep only the last 5 encounters
            if len(self.memory['encounter_timestamps']) > 5:
                self.memory['encounter_timestamps'] = self.memory['encounter_timestamps'][-5:]
    
    def record_ally_defeated(self):
        """Record when an ally is defeated in presence of this enemy"""
        self.memory['allies_lost'] += 1
        
        # Increase grudge when witnessing allies fall
        self.memory['grudge_factor'] = min(1.0, self.memory['grudge_factor'] + 0.15)
        
        # This is a traumatic event that might cause immediate fear
        if random.random() < 0.3:  # 30% chance
            self.confidence = max(0.0, self.confidence - 0.3)
    
    def update(self, dt):
        """
        Update psychological state based on player power and proximity
        
        Args:
            dt: Delta time in seconds
        """
        # Check if enemy is in fog
        self._check_fog_state()
        
        # Calculate pack strength from nearby allies
        self.pack_strength_bonus = self.calculate_pack_strength()
        
        # Calculate player-to-enemy power ratio
        power_ratio = self.calculate_player_power_ratio()
        
        # Calculate proximity factor - closer player has stronger psychological effect
        proximity_factor = 1.0
        player = self.enemy.game.player
        if player and hasattr(player, 'position') and hasattr(self.enemy, 'position'):
            distance = (player.position - self.enemy.position).length()
            detection_range = getattr(self.enemy, 'detection_range', 10.0)
            
            # Normalize distance: 0 (at detection range) to 1 (very close)
            if distance < detection_range:
                proximity_factor = 1.0 - (distance / detection_range)
                
                # Record encounter if close enough - but only occasionally to avoid spam
                if proximity_factor > 0.7 and random.random() < 0.05:
                    self.record_player_encounter(encounter_type='spotted')
            else:
                proximity_factor = 0.0
                
            # Reduce proximity factor in fog based on visibility
            if hasattr(self.enemy.game, 'night_fog') and self.enemy.game.night_fog.active:
                # Get visibility factor at player position
                visibility = self.enemy.game.night_fog.get_visibility_factor(player.position)
                # Scale proximity factor by visibility
                proximity_factor *= visibility
        
        # Special case: if enemy is empowered by fog, prioritize that state
        if self.fog_empowerment > 0.5:
            self.state = PsychologicalState.EMPOWERED
            self.confidence = 1.0
            self._update_behavior_modifiers()
            self._update_visual_indicator()
            return
        
        # Determine target state based on power ratio
        target_state = PsychologicalState.NORMAL
        target_confidence = 1.0
        
        if power_ratio >= self.subservient_threshold and random.random() < self.subservience_chance:
            # Small chance to become subservient instead of terrified
            target_state = PsychologicalState.SUBSERVIENT
            target_confidence = 0.0
        elif power_ratio >= self.terrified_threshold:
            target_state = PsychologicalState.TERRIFIED
            target_confidence = 0.0
        elif power_ratio >= self.fearful_threshold:
            target_state = PsychologicalState.FEARFUL
            target_confidence = 0.25
        elif power_ratio >= self.hesitant_threshold:
            target_state = PsychologicalState.HESITANT
            target_confidence = 0.5
        else:
            target_state = PsychologicalState.NORMAL
            target_confidence = 1.0
        
        # Process delayed reactions
        if self.pending_state_change:
            self.reaction_timer += dt
            if self.reaction_timer >= self.state_change_delay:
                # Time to change state
                self.state = self.pending_state_change
                target_confidence = 0.0 if self.state == PsychologicalState.TERRIFIED or self.state == PsychologicalState.SUBSERVIENT else \
                                   0.25 if self.state == PsychologicalState.FEARFUL else \
                                   0.5 if self.state == PsychologicalState.HESITANT else 1.0
                
                self.pending_state_change = None
                self.reaction_timer = 0.0
        else:
            # Consider setting up a delayed reaction for significant state changes
            # More intelligent enemies have slower reactions (they think more)
            intelligence_factor = self.traits.get_intelligence_factor()
            
            # Only delay significant negative transitions (normal->fearful, hesitant->terrified, etc.)
            current_severity = self._get_state_severity(self.state)
            target_severity = self._get_state_severity(target_state)
            
            if target_severity - current_severity >= 2:  # Significant worsening
                # Set up delayed reaction
                self.pending_state_change = target_state
                # Delay based on intelligence (0.5-2.0 seconds)
                self.state_change_delay = 0.5 + (intelligence_factor * 1.0)
                self.reaction_timer = 0.0
                
                # For now, transition to an intermediate state
                if current_severity == 0:  # Normal
                    intermediate_state = PsychologicalState.HESITANT
                    intermediate_confidence = 0.5
                else:  # Already hesitant or worse
                    intermediate_state = PsychologicalState.FEARFUL
                    intermediate_confidence = 0.25
                    
                target_state = intermediate_state
                target_confidence = intermediate_confidence
        
        # Emotional contagion from nearby allies
        if self.nearby_ally_count > 0:
            contagion_strength = 0.05 * dt  # Base contagion strength per second
            
            # Find the most influential ally (highest dominance)
            most_influential = None
            max_influence = 0
            
            for ally in self.nearby_allies:
                if hasattr(ally, 'psychology'):
                    influence = ally.psychology.traits.get_pack_influence() if hasattr(ally.psychology, 'traits') else 1.0
                    if influence > max_influence:
                        max_influence = influence
                        most_influential = ally
            
            if most_influential and hasattr(most_influential, 'psychology'):
                # More dominant allies have stronger influence
                contagion_strength *= max_influence
                
                # Apply emotional contagion
                ally_confidence = most_influential.psychology.confidence
                confidence_diff = ally_confidence - self.confidence
                
                # Only be influenced if the difference is significant and in the direction of the pack
                if abs(confidence_diff) > 0.2:
                    # Scale by own pack mentality trait
                    adjustment = confidence_diff * contagion_strength * self.traits.pack_mentality
                    self.confidence = max(0.0, min(1.0, self.confidence + adjustment))
        
        # Apply proximity-based confidence adjustment
        if self.pending_state_change is None:  # Don't adjust if already in delayed reaction
            confidence_change = (target_confidence - self.confidence) * proximity_factor * (1.0 - self.inertia) * dt
            self.confidence = max(0.0, min(1.0, self.confidence + confidence_change))
        
        # Update state if confidence crosses thresholds and not in delayed reaction
        if self.pending_state_change is None:
            if self.confidence < 0.1 and target_state == PsychologicalState.SUBSERVIENT:
                self.state = PsychologicalState.SUBSERVIENT
            elif self.confidence < 0.2:
                self.state = PsychologicalState.TERRIFIED
            elif self.confidence < 0.4:
                self.state = PsychologicalState.FEARFUL
            elif self.confidence < 0.7:
                self.state = PsychologicalState.HESITANT
            else:
                self.state = PsychologicalState.NORMAL
                
        # Override state if in fog with sufficient empowerment
        if self.fog_empowerment > 0.5:
            self.state = PsychologicalState.EMPOWERED
            self.confidence = 1.0
        
        # Update behavior modifiers based on new state
        self._update_behavior_modifiers()
        
        # Update visual indicator
        self._update_visual_indicator()

    def _check_fog_state(self):
        """Check if the enemy is in fog and update fog empowerment"""
        # Reset fog state
        previous_in_fog = self.in_fog
        self.in_fog = False
        
        # Check if game has night fog system
        if hasattr(self.enemy.game, 'night_fog') and self.enemy.game.night_fog.active:
            night_fog = self.enemy.game.night_fog
            
            # Check if enemy is in fog
            if hasattr(self.enemy, 'position'):
                self.in_fog = night_fog.is_in_fog(self.enemy.position)
                
                # Update fog empowerment (gradually increase when in fog, decrease when not)
                if self.in_fog:
                    # Increase empowerment while in fog, up to a maximum
                    self.fog_empowerment = min(1.0, self.fog_empowerment + 0.1)
                    
                    # Apply visual effect for fog-empowered enemy
                    if hasattr(self.enemy, 'model') and self.fog_empowerment > 0.5:
                        try:
                            # Add blue fog aura
                            self.enemy.model.setColorScale(0.7, 0.7, 1.2, 1.0)
                        except:
                            pass
                else:
                    # Decrease empowerment when not in fog
                    self.fog_empowerment = max(0.0, self.fog_empowerment - 0.05)
                    
                    # Remove visual effect if no longer empowered
                    if hasattr(self.enemy, 'model') and self.fog_empowerment < 0.5:
                        try:
                            self.enemy.model.clearColorScale()
                        except:
                            pass
        else:
            # No fog system or inactive, reset empowerment
            self.fog_empowerment = 0.0
    
    def _update_behavior_modifiers(self):
        """Update behavior modifiers based on current psychological state"""
        # Reset modifiers
        self.attack_chance_modifier = 1.0
        self.speed_modifier = 1.0
        self.damage_modifier = 1.0
        
        # Apply state-based modifiers
        if self.state == PsychologicalState.NORMAL:
            # Normal state - standard behavior
            pass
        elif self.state == PsychologicalState.HESITANT:
            # Hesitant - reduced attack chance, slightly increased speed (cautious)
            self.attack_chance_modifier = 0.7
            self.speed_modifier = 1.1
        elif self.state == PsychologicalState.FEARFUL:
            # Fearful - greatly reduced attack chance, increased speed (evasive)
            self.attack_chance_modifier = 0.4
            self.speed_modifier = 1.3
            self.damage_modifier = 0.8
        elif self.state == PsychologicalState.TERRIFIED:
            # Terrified - no attacks, maximum speed (fleeing)
            self.attack_chance_modifier = 0.0
            self.speed_modifier = 1.5
            self.damage_modifier = 0.5
        elif self.state == PsychologicalState.SUBSERVIENT:
            # Subservient - no attack chance against player, normal otherwise
            self.attack_chance_modifier = 0.0  # Will be ignored when targeting other enemies
            self.speed_modifier = 1.0
            self.damage_modifier = 0.8
        elif self.state == PsychologicalState.EMPOWERED:
            # Empowered by fog - increased damage and attack chance
            self.attack_chance_modifier = 1.3
            self.speed_modifier = 1.1
            self.damage_modifier = 1.5
        
        # Apply personality trait modifiers
        if hasattr(self, 'traits'):
            # Aggression affects attack chance and damage
            aggression_factor = self.traits.aggression
            self.attack_chance_modifier *= aggression_factor
            self.damage_modifier *= aggression_factor
            
            # Add desperation bonus for low health
            if hasattr(self.enemy, 'health') and hasattr(self.enemy, 'max_health'):
                health_ratio = self.enemy.health / self.enemy.max_health
                if health_ratio < 0.25:
                    # Become more desperate (aggressive) at low health
                    desperation_bonus = (0.25 - health_ratio) * 2.0  # Up to +50% at 1 HP
                    self.attack_chance_modifier *= (1.0 + desperation_bonus)
                    self.damage_modifier *= (1.0 + desperation_bonus)
            
            # Pack mentality provides bonuses when in groups
            if self.nearby_ally_count > 0:
                # Bonus increases with number of allies up to a cap
                pack_bonus = min(0.5, self.nearby_ally_count * 0.1)  # Cap at +50%
                
                # Alpha enemies provide extra courage
                if self.alpha_nearby:
                    pack_bonus += 0.2
                    
                # Scale by pack mentality trait
                pack_bonus *= self.traits.pack_mentality
                
                # Apply pack bonus to attack chance
                self.attack_chance_modifier *= (1.0 + pack_bonus)
                
            # Add grudge factor impact - enemies with grudges hit harder
            if hasattr(self, 'memory') and 'grudge_factor' in self.memory:
                grudge_factor = self.memory['grudge_factor']
                if grudge_factor > 0.2:  # Only significant grudges matter
                    self.damage_modifier *= (1.0 + (grudge_factor * 0.3))  # Up to +30% damage
    
    def should_attack_player(self):
        """
        Determine if the enemy should attack the player based on psychological state
        
        Returns:
            bool: True if the enemy should attack, False otherwise
        """
        # Terrified enemies never attack
        if self.state == PsychologicalState.TERRIFIED:
            return False
        
        # Subservient enemies never attack player
        if self.state == PsychologicalState.SUBSERVIENT:
            return False
            
        # Check attack chance based on state and modifiers
        base_chance = 1.0  # Base 100% chance to attack when in range
        
        # Apply psychological modifier
        modified_chance = base_chance * self.attack_chance_modifier
        
        # Randomize based on modified chance
        return random.random() < modified_chance
    
    def get_effective_speed(self):
        """
        Get the effective movement speed based on psychological state
        
        Returns:
            float: Speed multiplier
        """
        return self.speed_modifier
    
    def get_effective_damage(self):
        """
        Get the effective damage multiplier based on psychological state
        
        Returns:
            float: Damage multiplier
        """
        return self.damage_modifier
    
    def get_state_description(self):
        """
        Get a human-readable description of the current psychological state
        
        Returns:
            str: Description of the state
        """
        base_desc = str(self.state).capitalize()
        
        # Add pack information if relevant
        if self.nearby_ally_count > 0:
            base_desc += f" (Pack: {self.nearby_ally_count})"
            
        # Add alpha information
        if hasattr(self, 'traits') and self.traits.is_alpha:
            base_desc = "Alpha " + base_desc
            
        # Add pending state change if any
        if self.pending_state_change:
            base_desc += f" → {self.pending_state_change.capitalize()}"
            
        # Add grudge information for debugging
        if hasattr(self, 'memory') and self.memory['grudge_factor'] > 0.3:
            base_desc += " [Grudge]"
            
        return base_desc
        
    def make_tactical_decision(self, available_actions):
        """
        Make a tactical decision based on psychological state and intelligence
        
        Args:
            available_actions (list): List of possible actions the enemy can take
            
        Returns:
            str: The chosen action
        """
        # Default to first available action if list is empty
        if not available_actions:
            return None
            
        # Base decision on psychological state
        if self.state == PsychologicalState.NORMAL:
            # Normal state - balanced decision making
            # Higher intelligence means better tactical choices
            if hasattr(self, 'traits') and self.traits.intelligence > 1.2:
                # Smart enemies pick the best tactical option
                # This would involve evaluating each action's effectiveness
                # For now, just a placeholder
                return random.choice(available_actions)
            else:
                # Average intelligence - slightly randomized choice
                return random.choice(available_actions)
                
        elif self.state == PsychologicalState.HESITANT:
            # Prefer defensive actions
            defensive_actions = [a for a in available_actions if 'defend' in a or 'retreat' in a or 'ranged' in a]
            if defensive_actions:
                return random.choice(defensive_actions)
            else:
                return random.choice(available_actions)
                
        elif self.state == PsychologicalState.FEARFUL:
            # Strongly prefer evasive actions
            evasive_actions = [a for a in available_actions if 'flee' in a or 'evade' in a or 'distance' in a]
            if evasive_actions:
                return random.choice(evasive_actions)
            else:
                # Fall back to defensive actions
                defensive_actions = [a for a in available_actions if 'defend' in a or 'retreat' in a]
                if defensive_actions:
                    return random.choice(defensive_actions)
                else:
                    return random.choice(available_actions)
                    
        elif self.state == PsychologicalState.TERRIFIED:
            # Always choose to flee if possible
            flee_actions = [a for a in available_actions if 'flee' in a]
            if flee_actions:
                return flee_actions[0]  # Take first flee action
            else:
                # If can't flee, take most defensive action
                return random.choice(available_actions)
                
        elif self.state == PsychologicalState.SUBSERVIENT:
            # Choose actions that help the player
            helpful_actions = [a for a in available_actions if 'assist' in a or 'follow' in a]
            if helpful_actions:
                return random.choice(helpful_actions)
            else:
                return random.choice(available_actions)
                
        elif self.state == PsychologicalState.EMPOWERED:
            # Prefer aggressive actions
            aggressive_actions = [a for a in available_actions if 'attack' in a or 'charge' in a or 'aggressive' in a]
            if aggressive_actions:
                return random.choice(aggressive_actions)
            else:
                return random.choice(available_actions)
                
        # Default fallback
        return random.choice(available_actions)
    
    def rally_nearby_allies(self):
        """
        Attempt to rally nearby allies, boosting their confidence
        Only alpha enemies or those with high dominance can rally effectively
        
        Returns:
            bool: True if rally was successful, False otherwise
        """
        # Check if this enemy can rally others
        if not hasattr(self, 'traits') or self.traits.dominance < 1.2:
            return False
            
        # Can only rally from normal or hesitant state
        if self.state not in [PsychologicalState.NORMAL, PsychologicalState.HESITANT]:
            return False
            
        # Need allies to rally
        if not self.nearby_allies:
            return False
            
        # Rally effectiveness based on dominance
        rally_strength = 0.3 * self.traits.dominance
        
        # Apply rally effect to nearby allies
        rallied_count = 0
        for ally in self.nearby_allies:
            if hasattr(ally, 'psychology'):
                # Boost confidence based on rally strength
                old_confidence = ally.psychology.confidence
                new_confidence = min(1.0, old_confidence + rally_strength)
                ally.psychology.confidence = new_confidence
                
                # Count successful rallies
                if new_confidence > old_confidence + 0.1:  # Significant boost
                    rallied_count += 1
                    
                    # Visual effect for rally (if applicable)
                    if hasattr(ally, 'root'):
                        # Could add a visual rally effect here
                        pass
        
        return rallied_count > 0

    def _get_state_severity(self, state):
        """
        Get numerical severity of a psychological state
        
        Args:
            state: The psychological state to evaluate
            
        Returns:
            int: Severity level (0-4), higher means more severe negative state
        """
        if state == PsychologicalState.NORMAL:
            return 0
        elif state == PsychologicalState.HESITANT:
            return 1
        elif state == PsychologicalState.FEARFUL:
            return 2
        elif state == PsychologicalState.TERRIFIED:
            return 3
        elif state == PsychologicalState.SUBSERVIENT:
            return 4
        else:  # Empowered or others
            return 0 