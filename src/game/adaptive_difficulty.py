#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Adaptive Difficulty System for Nightfall Defenders
Dynamically adjusts game difficulty based on player performance
"""

import math
import random
import time
from enum import Enum

class DifficultyPreset(Enum):
    """Enumeration of difficulty presets"""
    EASY = 1
    NORMAL = 2
    HARD = 3
    CUSTOM = 4

class AdaptiveDifficultySystem:
    """
    Manages dynamic difficulty adjustments based on player performance
    """
    
    def __init__(self, game, initial_difficulty=DifficultyPreset.NORMAL):
        """
        Initialize the adaptive difficulty system
        
        Args:
            game: The main game instance
            initial_difficulty: Initial difficulty preset
        """
        self.game = game
        self.difficulty_preset = initial_difficulty
        
        # Current difficulty multipliers
        self.enemy_health_multiplier = 1.0
        self.enemy_damage_multiplier = 1.0
        self.enemy_spawn_rate_multiplier = 1.0
        self.enemy_aggression_multiplier = 1.0
        self.resource_drop_multiplier = 1.0
        self.fog_speed_multiplier = 1.0
        self.fog_density_multiplier = 1.0
        self.boss_difficulty_multiplier = 1.0
        
        # Performance metrics
        self.performance_metrics = {
            # Combat metrics
            'player_damage_dealt': 0,
            'player_damage_taken': 0,
            'enemy_kills': 0,
            'deaths': 0,
            'close_calls': 0,  # Near-death experiences
            
            # Resource metrics
            'resources_collected': {},  # Dict of resource type to amount
            'resources_spent': {},
            
            # City metrics
            'city_attacks': 0,
            'city_damage_taken': 0,
            'city_sections_lost': 0,
            
            # Boss metrics
            'boss_encounters': 0,
            'boss_defeats': 0,
            'boss_time_to_kill': [],  # List of times to kill bosses
            
            # Night survival metrics
            'nights_survived': 0,
            'night_survival_health': [],  # Health percentage at end of night
        }
        
        # Performance trends
        self.recent_performance_rating = 0.0  # -1.0 to 1.0 (struggling to excelling)
        self.performance_history = []  # List of historical performance ratings
        self.adjustment_history = []  # List of adjustment events
        
        # Configuration
        self.adjustment_frequency = 300  # Seconds between major adjustments
        self.adjustment_strength = 0.1  # Maximum adjustment per cycle
        self.last_adjustment_time = time.time()
        
        # Anti-frustration features
        self.consecutive_deaths = 0
        self.frustration_threshold = 3
        
        # Apply initial difficulty settings
        self._apply_difficulty_preset(initial_difficulty)
        
        # Debug mode
        self.debug_mode = False
        
    def _apply_difficulty_preset(self, preset):
        """
        Apply a difficulty preset to set initial values
        
        Args:
            preset: DifficultyPreset enum value
        """
        if preset == DifficultyPreset.EASY:
            self.enemy_health_multiplier = 0.8
            self.enemy_damage_multiplier = 0.7
            self.enemy_spawn_rate_multiplier = 0.8
            self.enemy_aggression_multiplier = 0.7
            self.resource_drop_multiplier = 1.3
            self.fog_speed_multiplier = 0.7
            self.fog_density_multiplier = 0.8
            self.boss_difficulty_multiplier = 0.8
            
        elif preset == DifficultyPreset.NORMAL:
            self.enemy_health_multiplier = 1.0
            self.enemy_damage_multiplier = 1.0
            self.enemy_spawn_rate_multiplier = 1.0
            self.enemy_aggression_multiplier = 1.0
            self.resource_drop_multiplier = 1.0
            self.fog_speed_multiplier = 1.0
            self.fog_density_multiplier = 1.0
            self.boss_difficulty_multiplier = 1.0
            
        elif preset == DifficultyPreset.HARD:
            self.enemy_health_multiplier = 1.3
            self.enemy_damage_multiplier = 1.2
            self.enemy_spawn_rate_multiplier = 1.2
            self.enemy_aggression_multiplier = 1.3
            self.resource_drop_multiplier = 0.8
            self.fog_speed_multiplier = 1.3
            self.fog_density_multiplier = 1.2
            self.boss_difficulty_multiplier = 1.3
            
        # Custom preset doesn't change anything, keeps current values
        
        # Log the change
        self.difficulty_preset = preset
        self._log_adjustment(f"Applied {preset.name} difficulty preset")
    
    def update(self, dt):
        """
        Update the adaptive difficulty system
        
        Args:
            dt: Delta time in seconds
        """
        # Check if it's time for periodic adjustment
        current_time = time.time()
        if current_time - self.last_adjustment_time >= self.adjustment_frequency:
            self._evaluate_and_adjust_difficulty()
            self.last_adjustment_time = current_time
            
        # Check for anti-frustration triggers
        self._check_anti_frustration_triggers()
        
        # Update debug visualizations if enabled
        if self.debug_mode:
            self._update_debug_display()
    
    def record_combat_event(self, event_type, amount=1):
        """
        Record a combat-related event
        
        Args:
            event_type: Type of event ('damage_dealt', 'damage_taken', 'enemy_killed', 'player_death', 'close_call')
            amount: Amount to add (default 1)
        """
        if event_type == 'damage_dealt':
            self.performance_metrics['player_damage_dealt'] += amount
        elif event_type == 'damage_taken':
            self.performance_metrics['player_damage_taken'] += amount
        elif event_type == 'enemy_killed':
            self.performance_metrics['enemy_kills'] += amount
        elif event_type == 'player_death':
            self.performance_metrics['deaths'] += amount
            self.consecutive_deaths += 1
            self._consider_anti_frustration_adjustment()
        elif event_type == 'close_call':
            self.performance_metrics['close_calls'] += amount
            
        # Update real-time performance rating
        self._update_performance_rating()
    
    def record_resource_event(self, event_type, resource_type, amount):
        """
        Record a resource-related event
        
        Args:
            event_type: Type of event ('collected', 'spent')
            resource_type: Type of resource
            amount: Amount collected or spent
        """
        if event_type == 'collected':
            if resource_type not in self.performance_metrics['resources_collected']:
                self.performance_metrics['resources_collected'][resource_type] = 0
            self.performance_metrics['resources_collected'][resource_type] += amount
        elif event_type == 'spent':
            if resource_type not in self.performance_metrics['resources_spent']:
                self.performance_metrics['resources_spent'][resource_type] = 0
            self.performance_metrics['resources_spent'][resource_type] += amount
    
    def record_city_event(self, event_type, amount=1):
        """
        Record a city-related event
        
        Args:
            event_type: Type of event ('attack', 'damage', 'section_lost')
            amount: Amount to add (default 1)
        """
        if event_type == 'attack':
            self.performance_metrics['city_attacks'] += amount
        elif event_type == 'damage':
            self.performance_metrics['city_damage_taken'] += amount
        elif event_type == 'section_lost':
            self.performance_metrics['city_sections_lost'] += amount
    
    def record_boss_event(self, event_type, defeat_time=None):
        """
        Record a boss-related event for difficulty adjustment
        
        Args:
            event_type (str): Type of boss event ('encounter', 'defeat', 'death')
            defeat_time (float): Time taken to defeat the boss (in seconds)
        """
        # Update boss performance metrics
        if event_type == 'encounter':
            self.performance_metrics['boss_encounters'] += 1
            
        elif event_type == 'defeat':
            self.performance_metrics['boss_defeats'] += 1
            
            # Record defeat time
            if defeat_time is not None:
                self.performance_metrics['boss_time_to_kill'].append(defeat_time)
                # Keep only the last few defeat times
                if len(self.performance_metrics['boss_time_to_kill']) > 5:
                    self.performance_metrics['boss_time_to_kill'] = self.performance_metrics['boss_time_to_kill'][-5:]
                    
                # Calculate average defeat time
                self.average_boss_defeat_time = sum(self.performance_metrics['boss_time_to_kill']) / len(self.performance_metrics['boss_time_to_kill'])
                
                # Log if in debug mode
                if hasattr(self.game, 'debug_mode') and self.game.debug_mode:
                    print(f"Boss defeated in {defeat_time:.1f} seconds (avg: {self.average_boss_defeat_time:.1f}s)")
                    
                # Adjust boss difficulty based on performance
                self._adjust_difficulty_for_boss_performance(defeat_time)
                
        elif event_type == 'death':
            # Player died during boss fight
            self._adjust_difficulty_for_boss_death()
            
        # Update performance rating
        self._update_performance_rating()
    
    def record_night_survived(self, health_percentage):
        """
        Record a night survived
        
        Args:
            health_percentage: Player health percentage at end of night
        """
        self.performance_metrics['nights_survived'] += 1
        self.performance_metrics['night_survival_health'].append(health_percentage)
        
        # Keep only the last 5 night survival health percentages
        if len(self.performance_metrics['night_survival_health']) > 5:
            self.performance_metrics['night_survival_health'] = self.performance_metrics['night_survival_health'][-5:]
        
        # Reset consecutive deaths counter
        self.consecutive_deaths = 0
    
    def _update_performance_rating(self):
        """Update the real-time performance rating based on metrics"""
        # Calculate combat performance
        combat_total = self.performance_metrics['player_damage_dealt'] + self.performance_metrics['player_damage_taken']
        if combat_total > 0:
            combat_ratio = self.performance_metrics['player_damage_dealt'] / combat_total
        else:
            combat_ratio = 0.5  # Neutral if no combat
            
        # Calculate survival rating
        survival_score = 0
        if self.performance_metrics['deaths'] > 0:
            survival_score = -0.5  # Penalty for any deaths
        else:
            # Bonus for surviving with high health
            recent_health = self.performance_metrics['night_survival_health'][-3:] if self.performance_metrics['night_survival_health'] else []
            if recent_health:
                avg_health = sum(recent_health) / len(recent_health)
                survival_score = (avg_health / 100.0) * 0.5  # Up to 0.5 bonus
        
        # Calculate boss performance
        boss_score = 0
        if self.performance_metrics['boss_encounters'] > 0:
            boss_win_rate = self.performance_metrics['boss_defeats'] / self.performance_metrics['boss_encounters']
            boss_score = (boss_win_rate - 0.5) * 0.5  # -0.25 to 0.25
        
        # Combine scores into overall rating (-1.0 to 1.0)
        combat_weight = 0.5
        survival_weight = 0.3
        boss_weight = 0.2
        
        self.recent_performance_rating = (
            combat_ratio * combat_weight +
            survival_score * survival_weight +
            boss_score * boss_weight
        ) * 2 - 1  # Scale from 0-1 to -1-1
        
        # Add to history
        self.performance_history.append(self.recent_performance_rating)
        if len(self.performance_history) > 10:
            self.performance_history = self.performance_history[-10:]
    
    def _evaluate_and_adjust_difficulty(self):
        """Evaluate performance and make difficulty adjustments"""
        # Skip adjustment if using fixed preset and not custom
        if self.difficulty_preset != DifficultyPreset.CUSTOM:
            return
            
        # Calculate average performance over recent history
        if not self.performance_history:
            return
            
        avg_performance = sum(self.performance_history) / len(self.performance_history)
        
        # Determine adjustment direction and strength
        adjustment = -avg_performance * self.adjustment_strength
        
        # Apply adjustments to difficulty parameters
        self._adjust_enemy_parameters(adjustment)
        self._adjust_resource_parameters(adjustment)
        self._adjust_environment_parameters(adjustment)
        
        # Log the adjustment
        self._log_adjustment(f"Regular adjustment: {adjustment:.2f} based on performance {avg_performance:.2f}")
    
    def _adjust_enemy_parameters(self, adjustment):
        """
        Adjust enemy-related difficulty parameters
        
        Args:
            adjustment: Amount to adjust (positive = harder, negative = easier)
        """
        # Apply adjustments with limits
        self.enemy_health_multiplier = max(0.6, min(1.5, self.enemy_health_multiplier * (1 + adjustment)))
        self.enemy_damage_multiplier = max(0.6, min(1.5, self.enemy_damage_multiplier * (1 + adjustment)))
        self.enemy_spawn_rate_multiplier = max(0.7, min(1.4, self.enemy_spawn_rate_multiplier * (1 + adjustment)))
        self.enemy_aggression_multiplier = max(0.7, min(1.4, self.enemy_aggression_multiplier * (1 + adjustment)))
        self.boss_difficulty_multiplier = max(0.7, min(1.5, self.boss_difficulty_multiplier * (1 + adjustment)))
    
    def _adjust_resource_parameters(self, adjustment):
        """
        Adjust resource-related difficulty parameters
        
        Args:
            adjustment: Amount to adjust (positive = harder, negative = easier)
        """
        # For resources, negative adjustment means more resources (easier)
        self.resource_drop_multiplier = max(0.7, min(1.4, self.resource_drop_multiplier * (1 - adjustment)))
    
    def _adjust_environment_parameters(self, adjustment):
        """
        Adjust environment-related difficulty parameters
        
        Args:
            adjustment: Amount to adjust (positive = harder, negative = easier)
        """
        self.fog_speed_multiplier = max(0.7, min(1.5, self.fog_speed_multiplier * (1 + adjustment)))
        self.fog_density_multiplier = max(0.7, min(1.5, self.fog_density_multiplier * (1 + adjustment)))
    
    def _consider_anti_frustration_adjustment(self):
        """Consider making the game easier if player is frustrated"""
        if self.consecutive_deaths >= self.frustration_threshold:
            # Apply significant easing of difficulty
            anti_frustration_adjustment = -0.2  # Significant reduction in difficulty
            
            self._adjust_enemy_parameters(anti_frustration_adjustment)
            self._adjust_resource_parameters(anti_frustration_adjustment)
            self._adjust_environment_parameters(anti_frustration_adjustment)
            
            # Log the adjustment
            self._log_adjustment(f"Anti-frustration adjustment: {anti_frustration_adjustment:.2f} after {self.consecutive_deaths} consecutive deaths")
            
            # Reset counter but not to zero - continue monitoring
            self.consecutive_deaths = self.frustration_threshold - 1
    
    def _check_anti_frustration_triggers(self):
        """Check for other triggers that might indicate player frustration"""
        # Check for rapid health loss without death
        # This would typically be implemented by monitoring health changes over time
        
        # Check for repeated failure at the same challenge
        # Would require tracking specific challenges and attempts
        
        # These would be more sophisticated in a full implementation
        pass
    
    def _log_adjustment(self, message):
        """
        Log a difficulty adjustment event
        
        Args:
            message: Description of the adjustment
        """
        timestamp = time.time()
        self.adjustment_history.append({
            'timestamp': timestamp,
            'message': message,
            'enemy_health': self.enemy_health_multiplier,
            'enemy_damage': self.enemy_damage_multiplier,
            'enemy_spawn_rate': self.enemy_spawn_rate_multiplier,
            'enemy_aggression': self.enemy_aggression_multiplier,
            'resource_drop': self.resource_drop_multiplier,
            'fog_speed': self.fog_speed_multiplier,
            'fog_density': self.fog_density_multiplier,
            'boss_difficulty': self.boss_difficulty_multiplier
        })
        
        # Keep adjustment history to a reasonable size
        if len(self.adjustment_history) > 50:
            self.adjustment_history = self.adjustment_history[-50:]
            
        # Print debug message if debug mode is enabled
        game_debug = hasattr(self.game, 'debug_mode') and self.game.debug_mode
        self_debug = hasattr(self, 'debug_mode') and self.debug_mode
        
        if game_debug or self_debug:
            print(f"[DIFFICULTY] {message}")
    
    def _update_debug_display(self):
        """Update debug display with current difficulty information"""
        # This would create or update on-screen text showing current difficulty settings
        # In a full implementation, this might use the game's UI system
        if hasattr(self.game, 'debug_overlay'):
            difficulty_info = (
                f"Difficulty: {self.difficulty_preset.name}\n"
                f"Performance: {self.recent_performance_rating:.2f}\n"
                f"Enemy HP: {self.enemy_health_multiplier:.2f}x\n"
                f"Enemy DMG: {self.enemy_damage_multiplier:.2f}x\n"
                f"Spawn Rate: {self.enemy_spawn_rate_multiplier:.2f}x\n"
                f"Fog Speed: {self.fog_speed_multiplier:.2f}x"
            )
            # Update debug text - implementation would depend on the game's UI system
            pass
    
    def set_difficulty_preset(self, preset):
        """
        Set the game difficulty to a preset value
        
        Args:
            preset: DifficultyPreset enum value
        """
        self._apply_difficulty_preset(preset)
        
        # Reset performance metrics for a fresh start
        self._reset_performance_metrics()
    
    def set_custom_difficulty(self, settings):
        """
        Set custom difficulty parameters
        
        Args:
            settings: Dictionary of difficulty settings to apply
        """
        # Apply any provided settings
        if 'enemy_health' in settings:
            self.enemy_health_multiplier = settings['enemy_health']
        if 'enemy_damage' in settings:
            self.enemy_damage_multiplier = settings['enemy_damage']
        if 'enemy_spawn_rate' in settings:
            self.enemy_spawn_rate_multiplier = settings['enemy_spawn_rate']
        if 'enemy_aggression' in settings:
            self.enemy_aggression_multiplier = settings['enemy_aggression']
        if 'resource_drop' in settings:
            self.resource_drop_multiplier = settings['resource_drop']
        if 'fog_speed' in settings:
            self.fog_speed_multiplier = settings['fog_speed']
        if 'fog_density' in settings:
            self.fog_density_multiplier = settings['fog_density']
        if 'boss_difficulty' in settings:
            self.boss_difficulty_multiplier = settings['boss_difficulty']
        
        # Set to custom preset
        self.difficulty_preset = DifficultyPreset.CUSTOM
        
        # Log the change
        self._log_adjustment("Applied custom difficulty settings")
    
    def _reset_performance_metrics(self):
        """Reset performance metrics to defaults"""
        self.performance_metrics = {
            'player_damage_dealt': 0,
            'player_damage_taken': 0,
            'enemy_kills': 0,
            'deaths': 0,
            'close_calls': 0,
            'resources_collected': {},
            'resources_spent': {},
            'city_attacks': 0,
            'city_damage_taken': 0,
            'city_sections_lost': 0,
            'boss_encounters': 0,
            'boss_defeats': 0,
            'boss_time_to_kill': [],
            'nights_survived': 0,
            'night_survival_health': [],
        }
        
        self.recent_performance_rating = 0.0
        self.performance_history = []
        self.consecutive_deaths = 0
    
    def get_current_difficulty_factors(self):
        """
        Get the current difficulty factors
        
        Returns:
            dict: Dictionary of current difficulty factors
        """
        return {
            'enemy_health': self.enemy_health_multiplier,
            'enemy_damage': self.enemy_damage_multiplier,
            'enemy_spawn_rate': self.enemy_spawn_rate_multiplier,
            'enemy_aggression': self.enemy_aggression_multiplier,
            'resource_drop': self.resource_drop_multiplier,
            'fog_speed': self.fog_speed_multiplier,
            'fog_density': self.fog_density_multiplier,
            'boss_difficulty': self.boss_difficulty_multiplier
        }
    
    def get_difficulty_stats(self):
        """
        Get statistics about difficulty adjustments
        
        Returns:
            dict: Statistics about difficulty adjustments
        """
        recent_adjustments = self.adjustment_history[-5:] if self.adjustment_history else []
        
        return {
            'preset': self.difficulty_preset.name,
            'performance_rating': self.recent_performance_rating,
            'recent_adjustments': recent_adjustments,
            'factors': self.get_current_difficulty_factors()
        }
    
    def enable_debug_mode(self, enabled=True):
        """
        Enable or disable debug mode
        
        Args:
            enabled: Whether debug mode should be enabled
        """
        self.debug_mode = enabled
    
    def _adjust_difficulty_for_boss_performance(self, defeat_time):
        """
        Adjust difficulty based on boss defeat time
        
        Args:
            defeat_time (float): Time taken to defeat the boss
        """
        # Define thresholds for boss defeat time (in seconds)
        very_fast = 120  # 2 minutes
        fast = 180       # 3 minutes
        average = 240    # 4 minutes
        slow = 300       # 5 minutes
        
        # Adjust boss difficulty factor based on defeat time
        if defeat_time <= very_fast:
            # Very fast defeat - significantly increase difficulty
            adjustment = 0.15
            log_msg = "Very fast boss defeat - increasing boss difficulty"
        elif defeat_time <= fast:
            # Fast defeat - increase difficulty
            adjustment = 0.1
            log_msg = "Fast boss defeat - slightly increasing boss difficulty"
        elif defeat_time <= average:
            # Average defeat time - maintain difficulty
            adjustment = 0.0
            log_msg = "Average boss defeat time - maintaining boss difficulty"
        elif defeat_time <= slow:
            # Slow defeat - decrease difficulty slightly
            adjustment = -0.05
            log_msg = "Slow boss defeat - slightly decreasing boss difficulty"
        else:
            # Very slow defeat - decrease difficulty
            adjustment = -0.1
            log_msg = "Very slow boss defeat - decreasing boss difficulty"
        
        # Apply adjustment to boss difficulty factor
        self.boss_difficulty_multiplier = max(min(self.boss_difficulty_multiplier + adjustment, 2.0), 0.5)
        
        # Enforce min/max bounds
        self.boss_difficulty_multiplier = max(min(self.boss_difficulty_multiplier, 2.0), 0.5)
            
        # Apply smaller adjustment to other combat factors
        combat_adjustment = adjustment * 0.5
        self.enemy_health_multiplier += combat_adjustment
        self.enemy_damage_multiplier += combat_adjustment
        
        # Enforce min/max bounds for other factors
        self.enemy_health_multiplier = max(min(self.enemy_health_multiplier, 1.5), 0.6)
        self.enemy_damage_multiplier = max(min(self.enemy_damage_multiplier, 1.5), 0.6)
        
        # Log adjustment if in debug mode
        if hasattr(self.game, 'debug_mode') and self.game.debug_mode:
            print(f"{log_msg}")
            print(f"  Boss difficulty factor: {self.boss_difficulty_multiplier:.2f}")
            print(f"  Enemy health factor: {self.enemy_health_multiplier:.2f}")
            print(f"  Enemy damage factor: {self.enemy_damage_multiplier:.2f}")
    
    def _adjust_difficulty_for_boss_death(self):
        """Adjust difficulty when player dies during boss fight"""
        # Reduce boss difficulty
        self.boss_difficulty_multiplier -= 0.1
        
        # Also reduce enemy damage and health slightly
        self.enemy_damage_multiplier -= 0.05
        self.enemy_health_multiplier -= 0.05
        
        # Enforce min/max bounds
        self.enemy_health_multiplier = max(min(self.enemy_health_multiplier, 1.5), 0.6)
        self.enemy_damage_multiplier = max(min(self.enemy_damage_multiplier, 1.5), 0.6)
        
        # Log adjustment if in debug mode
        if hasattr(self.game, 'debug_mode') and self.game.debug_mode:
            print("Player died during boss fight - reducing boss difficulty")
            print(f"  Boss difficulty factor: {self.boss_difficulty_multiplier:.2f}")
            print(f"  Enemy damage factor: {self.enemy_damage_multiplier:.2f}")
            print(f"  Enemy health factor: {self.enemy_health_multiplier:.2f}") 