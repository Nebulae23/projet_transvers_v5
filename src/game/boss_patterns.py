#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Boss Attack Pattern System for Nightfall Defenders
Implements complex attack patterns and phase transitions for bosses
"""

from enum import Enum
import random
import math
from panda3d.core import Vec3

class PatternType(Enum):
    """Types of attack patterns"""
    PROJECTILE_BURST = "projectile_burst"
    CHARGE = "charge"
    SUMMON_MINIONS = "summon_minions"
    GROUND_SLAM = "ground_slam"
    LASER_SWEEP = "laser_sweep"
    TELEPORT_STRIKE = "teleport_strike"
    AOE_EXPLOSION = "aoe_explosion"

class PatternDifficulty(Enum):
    """Difficulty levels for patterns"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXTREME = "extreme"

class BossPhase(Enum):
    """Boss fight phases"""
    INTRO = "intro"
    PHASE_1 = "phase_1"
    PHASE_2 = "phase_2"
    PHASE_3 = "phase_3"
    FINAL = "final"
    ENRAGE = "enrage"

class AttackPattern:
    """Base class for boss attack patterns"""
    
    def __init__(self, pattern_id, name, pattern_type, difficulty=PatternDifficulty.MEDIUM):
        """
        Initialize an attack pattern
        
        Args:
            pattern_id (str): Unique identifier
            name (str): Display name of the pattern
            pattern_type (PatternType): Type of pattern
            difficulty (PatternDifficulty): Difficulty level
        """
        self.pattern_id = pattern_id
        self.name = name
        self.pattern_type = pattern_type
        self.difficulty = difficulty
        
        # Pattern properties
        self.cooldown = 5.0  # Base cooldown in seconds
        self.duration = 2.0  # Duration of the attack
        self.damage = 10     # Base damage
        self.range = 10.0    # Range of the attack
        
        # State
        self.is_executing = False
        self.timer = 0.0
        self.current_cooldown = 0.0
        
        # Visual and sound effects
        self.telegraph_effect = None
        self.execute_effect = None
        self.sound_effect = None
        
        # Arena effects
        self.arena_effect = None
    
    def start(self, boss):
        """
        Start executing this pattern
        
        Args:
            boss: The boss executing the pattern
        """
        self.is_executing = True
        self.timer = 0.0
        
        # Play telegraph effect
        if self.telegraph_effect and hasattr(boss, 'spawn_effect'):
            boss.spawn_effect(self.telegraph_effect, 
                              duration=self.duration * 0.5,
                              position=boss.position)
        
        # Start cooldown
        self.current_cooldown = self.cooldown
    
    def update(self, dt, boss, player_position):
        """
        Update pattern execution
        
        Args:
            dt: Time delta
            boss: The boss executing the pattern
            player_position: Position of the player
            
        Returns:
            bool: True if pattern completed execution
        """
        if not self.is_executing:
            # Update cooldown
            if self.current_cooldown > 0:
                self.current_cooldown -= dt
            return False
            
        # Update timer
        self.timer += dt
        
        # Check if pattern is complete
        if self.timer >= self.duration:
            self.end(boss)
            return True
            
        # Execute pattern behavior
        self._execute_behavior(dt, boss, player_position)
        
        return False
    
    def end(self, boss):
        """
        End pattern execution
        
        Args:
            boss: The boss executing the pattern
        """
        self.is_executing = False
        self.timer = 0.0
    
    def _execute_behavior(self, dt, boss, player_position):
        """
        Execute the pattern's behavior (override in subclasses)
        
        Args:
            dt: Time delta
            boss: The boss executing the pattern
            player_position: Position of the player
        """
        pass
    
    def is_ready(self):
        """Check if pattern is ready to execute"""
        return self.current_cooldown <= 0 and not self.is_executing
    
    def is_in_range(self, boss_position, player_position):
        """
        Check if player is in range for this pattern
        
        Args:
            boss_position: Boss position
            player_position: Player position
            
        Returns:
            bool: True if in range
        """
        distance = (boss_position - player_position).length()
        return distance <= self.range

class ProjectileBurstPattern(AttackPattern):
    """Pattern that fires a burst of projectiles"""
    
    def __init__(self, pattern_id, name, difficulty=PatternDifficulty.MEDIUM):
        """Initialize a projectile burst pattern"""
        super().__init__(pattern_id, name, PatternType.PROJECTILE_BURST, difficulty)
        
        # Pattern-specific properties
        self.projectile_count = 8
        self.projectile_speed = 8.0
        self.arc_degrees = 360.0  # Full circle by default
        self.projectile_type = "boss_projectile"
        self.current_wave = 0
        self.waves = 1
        self.wave_delay = 0.5
        self.wave_timer = 0.0
        
    def _execute_behavior(self, dt, boss, player_position):
        """Execute the projectile burst pattern"""
        # Check if it's time for a new wave
        self.wave_timer += dt
        if self.wave_timer >= self.wave_delay or self.current_wave == 0:
            self.wave_timer = 0.0
            
            if self.current_wave < self.waves:
                # Fire a wave of projectiles
                self._fire_projectile_wave(boss, player_position)
                self.current_wave += 1
    
    def _fire_projectile_wave(self, boss, player_position):
        """Fire a wave of projectiles"""
        # Calculate direction to player
        direction = player_position - boss.position
        direction.normalize()
        
        # Calculate base angle
        base_angle = math.atan2(direction.y, direction.x)
        
        # Create projectiles in an arc
        angle_step = math.radians(self.arc_degrees) / self.projectile_count
        start_angle = base_angle - math.radians(self.arc_degrees) / 2
        
        for i in range(self.projectile_count):
            angle = start_angle + angle_step * i
            proj_dir = Vec3(math.cos(angle), math.sin(angle), 0)
            
            # Spawn the projectile through the boss's projectile system
            if hasattr(boss, 'fire_projectile'):
                boss.fire_projectile(
                    projectile_type=self.projectile_type,
                    direction=proj_dir,
                    speed=self.projectile_speed,
                    damage=self.damage
                )
    
    def end(self, boss):
        """End the pattern execution"""
        super().end(boss)
        self.current_wave = 0
        self.wave_timer = 0.0

class ChargePattern(AttackPattern):
    """Pattern where the boss charges at the player"""
    
    def __init__(self, pattern_id, name, difficulty=PatternDifficulty.MEDIUM):
        """Initialize a charge pattern"""
        super().__init__(pattern_id, name, PatternType.CHARGE, difficulty)
        
        # Pattern-specific properties
        self.charge_speed = 15.0
        self.charge_distance = 20.0
        self.pre_charge_delay = 0.5
        self.post_charge_delay = 0.5
        self.charge_direction = None
        self.charge_start_pos = None
        self.charge_target_pos = None
        self.charge_state = "pre"  # pre, charge, post
    
    def start(self, boss):
        """Start the charge pattern"""
        super().start(boss)
        self.charge_state = "pre"
        self.charge_start_pos = Vec3(boss.position)
    
    def _execute_behavior(self, dt, boss, player_position):
        """Execute the charge pattern"""
        if self.charge_state == "pre":
            # Pre-charge telegraph
            if self.timer >= self.pre_charge_delay:
                # Calculate charge direction
                self.charge_direction = player_position - boss.position
                self.charge_direction.normalize()
                
                # Calculate target position
                self.charge_target_pos = boss.position + self.charge_direction * self.charge_distance
                
                # Start charge
                self.charge_state = "charge"
                
                # Play effect if available
                if self.execute_effect and hasattr(boss, 'spawn_effect'):
                    boss.spawn_effect(self.execute_effect, duration=1.0, position=boss.position)
        
        elif self.charge_state == "charge":
            # Move boss along charge path
            boss.position += self.charge_direction * self.charge_speed * dt
            
            # Check if charge is complete
            distance_traveled = (boss.position - self.charge_start_pos).length()
            if distance_traveled >= self.charge_distance:
                boss.position = self.charge_target_pos
                self.charge_state = "post"
        
        elif self.charge_state == "post":
            # Post-charge recovery period
            if self.timer >= self.duration - self.post_charge_delay:
                # Pattern will end when timer exceeds duration
                pass

class GroundSlamPattern(AttackPattern):
    """Pattern where the boss slams the ground creating a shockwave"""
    
    def __init__(self, pattern_id, name, difficulty=PatternDifficulty.MEDIUM):
        """Initialize a ground slam pattern"""
        super().__init__(pattern_id, name, PatternType.GROUND_SLAM, difficulty)
        
        # Pattern-specific properties
        self.slam_radius = 8.0
        self.shockwave_speed = 5.0
        self.shockwave_distance = 15.0
        self.current_radius = 0.0
        self.telegraph_duration = 1.0
        self.slam_state = "telegraph"  # telegraph, slam, shockwave
        
    def _execute_behavior(self, dt, boss, player_position):
        """Execute the ground slam pattern"""
        if self.slam_state == "telegraph":
            # Telegraph the slam
            if self.timer >= self.telegraph_duration:
                self.slam_state = "slam"
                
                # Play effect if available
                if self.execute_effect and hasattr(boss, 'spawn_effect'):
                    boss.spawn_effect(self.execute_effect, duration=0.5, position=boss.position)
                    
                # Apply damage to player if in initial radius
                distance_to_player = (player_position - boss.position).length()
                if distance_to_player <= self.slam_radius * 0.5:
                    if hasattr(boss.game, 'player') and hasattr(boss.game.player, 'take_damage'):
                        boss.game.player.take_damage(self.damage * 1.5, boss)
        
        elif self.slam_state == "slam":
            # Shockwave expansion phase
            self.slam_state = "shockwave"
            self.current_radius = self.slam_radius * 0.5
            
        elif self.slam_state == "shockwave":
            # Expand the shockwave
            self.current_radius += self.shockwave_speed * dt
            
            # Check for player collision with shockwave
            distance_to_player = (player_position - boss.position).length()
            if abs(distance_to_player - self.current_radius) < 1.0:  # Player is near the shockwave edge
                if hasattr(boss.game, 'player') and hasattr(boss.game.player, 'take_damage'):
                    boss.game.player.take_damage(self.damage, boss)
            
            # End when shockwave reaches max distance
            if self.current_radius >= self.shockwave_distance:
                # Pattern will end when timer exceeds duration
                pass

class PatternSequence:
    """Sequence of attack patterns for a specific boss phase"""
    
    def __init__(self, phase, difficulty_scale=1.0):
        """
        Initialize a pattern sequence
        
        Args:
            phase (BossPhase): Boss phase this sequence is for
            difficulty_scale (float): Scaling factor for pattern difficulty
        """
        self.phase = phase
        self.difficulty_scale = difficulty_scale
        self.patterns = []
        self.weights = []
        self.current_pattern = None
        self.pattern_index = -1
        self.sequential = False  # If True, execute patterns in order
        
    def add_pattern(self, pattern, weight=1.0):
        """
        Add a pattern to this sequence
        
        Args:
            pattern (AttackPattern): Pattern to add
            weight (float): Selection weight for random selection
        """
        self.patterns.append(pattern)
        self.weights.append(weight)
        
        # Scale pattern properties based on difficulty
        pattern.damage *= self.difficulty_scale
        pattern.cooldown /= max(0.5, self.difficulty_scale)  # Faster cooldowns at higher difficulty
    
    def select_next_pattern(self, boss, player_position):
        """
        Select the next pattern to execute
        
        Args:
            boss: The boss executing patterns
            player_position: Position of the player
            
        Returns:
            AttackPattern or None: The selected pattern
        """
        if not self.patterns:
            return None
            
        if self.sequential:
            # Select next pattern in sequence
            self.pattern_index = (self.pattern_index + 1) % len(self.patterns)
            self.current_pattern = self.patterns[self.pattern_index]
        else:
            # Filter patterns that are ready and in range
            eligible_patterns = []
            eligible_weights = []
            
            for i, pattern in enumerate(self.patterns):
                if pattern.is_ready() and pattern.is_in_range(boss.position, player_position):
                    eligible_patterns.append(pattern)
                    eligible_weights.append(self.weights[i])
            
            if not eligible_patterns:
                return None
                
            # Select random pattern based on weights
            total_weight = sum(eligible_weights)
            if total_weight <= 0:
                return None
                
            # Normalize weights
            normalized_weights = [w / total_weight for w in eligible_weights]
            
            # Select pattern
            rand_val = random.random()
            cumulative = 0
            
            for i, weight in enumerate(normalized_weights):
                cumulative += weight
                if rand_val <= cumulative:
                    self.current_pattern = eligible_patterns[i]
                    break
            
        return self.current_pattern
    
    def start_pattern(self, boss):
        """
        Start the current pattern
        
        Args:
            boss: The boss executing the pattern
            
        Returns:
            bool: True if pattern was started
        """
        if self.current_pattern:
            self.current_pattern.start(boss)
            return True
        return False
    
    def update(self, dt, boss, player_position):
        """
        Update the current pattern
        
        Args:
            dt: Time delta
            boss: The boss executing the pattern
            player_position: Position of the player
            
        Returns:
            bool: True if pattern completed execution
        """
        if self.current_pattern and self.current_pattern.is_executing:
            return self.current_pattern.update(dt, boss, player_position)
        return False
    
    def is_executing(self):
        """Check if a pattern is currently executing"""
        return self.current_pattern and self.current_pattern.is_executing

class BossPatternSystem:
    """Manages attack patterns and phases for a boss"""
    
    def __init__(self, boss):
        """
        Initialize the pattern system
        
        Args:
            boss: The boss this system is for
        """
        self.boss = boss
        self.sequences = {}  # Phase -> PatternSequence mapping
        self.current_phase = BossPhase.INTRO
        self.phase_health_thresholds = {
            BossPhase.PHASE_1: 0.75,  # 75% health
            BossPhase.PHASE_2: 0.50,  # 50% health
            BossPhase.PHASE_3: 0.25,  # 25% health
            BossPhase.FINAL: 0.10,    # 10% health
            BossPhase.ENRAGE: 0.05    # 5% health (optional enrage phase)
        }
        
        # Transition effects
        self.transition_effects = {}
        
        # Pattern selection cooldown
        self.pattern_selection_cooldown = 0.0
        self.min_time_between_patterns = 1.0  # Minimum time between patterns
        
    def add_sequence(self, phase, sequence):
        """
        Add a pattern sequence for a phase
        
        Args:
            phase (BossPhase): The boss phase
            sequence (PatternSequence): Pattern sequence for this phase
        """
        self.sequences[phase] = sequence
    
    def add_transition_effect(self, from_phase, to_phase, effect_data):
        """
        Add a transition effect between phases
        
        Args:
            from_phase (BossPhase): Starting phase
            to_phase (BossPhase): Ending phase
            effect_data: Effect data (visual effect, sound, etc.)
        """
        self.transition_effects[(from_phase, to_phase)] = effect_data
    
    def update(self, dt, player_position):
        """
        Update the pattern system
        
        Args:
            dt: Time delta
            player_position: Position of the player
        """
        # Check for phase transitions based on boss health
        self._check_phase_transition()
        
        # Update pattern cooldowns
        if self.pattern_selection_cooldown > 0:
            self.pattern_selection_cooldown -= dt
        
        # Get current sequence
        sequence = self.sequences.get(self.current_phase)
        if not sequence:
            return
            
        # Update current pattern
        if sequence.is_executing():
            pattern_completed = sequence.update(dt, self.boss, player_position)
            
            if pattern_completed:
                # Pattern finished executing
                self.pattern_selection_cooldown = self.min_time_between_patterns
        elif self.pattern_selection_cooldown <= 0:
            # Select and start a new pattern
            pattern = sequence.select_next_pattern(self.boss, player_position)
            if pattern:
                sequence.start_pattern(self.boss)
    
    def _check_phase_transition(self):
        """Check for phase transitions based on boss health"""
        # Calculate current health percentage
        health_percent = self.boss.health / self.boss.max_health
        
        # Check each phase threshold
        for phase, threshold in self.phase_health_thresholds.items():
            if health_percent <= threshold and phase.value > self.current_phase.value:
                # Transition to new phase
                self._transition_to_phase(phase)
                break
    
    def _transition_to_phase(self, new_phase):
        """
        Transition to a new boss phase
        
        Args:
            new_phase (BossPhase): Phase to transition to
        """
        # Get transition effect if available
        effect_data = self.transition_effects.get((self.current_phase, new_phase))
        
        # Play transition effect
        if effect_data and hasattr(self.boss, 'play_transition_effect'):
            self.boss.play_transition_effect(effect_data)
            
        # Set new phase
        old_phase = self.current_phase
        self.current_phase = new_phase
        
        # Notify boss of phase change
        if hasattr(self.boss, 'on_phase_change'):
            self.boss.on_phase_change(old_phase, new_phase)
    
    def get_current_phase(self):
        """Get the current boss phase"""
        return self.current_phase

# Factory function to create common patterns
def create_pattern(pattern_type, pattern_id, name, difficulty=PatternDifficulty.MEDIUM):
    """
    Create a pattern of the specified type
    
    Args:
        pattern_type (PatternType): Type of pattern to create
        pattern_id (str): Pattern ID
        name (str): Pattern name
        difficulty (PatternDifficulty): Pattern difficulty
        
    Returns:
        AttackPattern: The created pattern
    """
    if pattern_type == PatternType.PROJECTILE_BURST:
        return ProjectileBurstPattern(pattern_id, name, difficulty)
    elif pattern_type == PatternType.CHARGE:
        return ChargePattern(pattern_id, name, difficulty)
    elif pattern_type == PatternType.GROUND_SLAM:
        return GroundSlamPattern(pattern_id, name, difficulty)
    else:
        # Create a basic pattern for other types
        return AttackPattern(pattern_id, name, pattern_type, difficulty) 