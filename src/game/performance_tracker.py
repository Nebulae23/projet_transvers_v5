#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Performance Tracker for Nightfall Defenders
Monitors and analyzes player performance metrics for adaptive difficulty adjustments
"""

import time
import math
import collections

class PerformanceTracker:
    """Tracks and analyzes player performance for adaptive difficulty adjustments"""
    
    def __init__(self, game):
        """
        Initialize the performance tracker
        
        Args:
            game: The main game instance
        """
        self.game = game
        
        # Reference to the adaptive difficulty system
        self.adaptive_difficulty_system = None
        if hasattr(game, 'adaptive_difficulty_system'):
            self.adaptive_difficulty_system = game.adaptive_difficulty_system
        
        # Session metrics
        self.session_start_time = time.time()
        self.last_update_time = time.time()
        
        # Short-term and long-term metrics windows
        self.short_term_window = 300  # 5 minutes
        self.long_term_window = 1800  # 30 minutes
        
        # Base metrics structure
        self.base_metrics = {
            # Combat metrics
            'damage_dealt': 0,
            'damage_taken': 0,
            'enemies_killed': 0,
            'deaths': 0,
            'close_calls': 0,
            'damage_dealt_per_minute': 0,
            'damage_taken_per_minute': 0,
            'kills_per_minute': 0,
            
            # Resource metrics
            'resources_collected': {},
            'resources_per_minute': {},
            
            # City metrics
            'city_damage_taken': 0,
            'city_attacks': 0,
            'city_sections_lost': 0,
            
            # Boss metrics
            'boss_encounters': 0,
            'boss_victories': 0,
            'boss_time_to_kill': [],
            
            # Night survival
            'nights_survived': 0,
            'night_survival_health': [],
            
            # Timestamps for trend analysis
            'timestamp': time.time()
        }
        
        # Initialize tracking collections
        # Recent window of time-stamped events
        self.recent_events = {
            'damage_dealt': collections.deque(maxlen=100),
            'damage_taken': collections.deque(maxlen=100),
            'enemies_killed': collections.deque(maxlen=100),
            'deaths': collections.deque(maxlen=10),
            'resources_collected': collections.deque(maxlen=100),
            'city_damage': collections.deque(maxlen=50),
            'boss_encounters': collections.deque(maxlen=10)
        }
        
        # Performance metrics history
        self.short_term_metrics = dict(self.base_metrics)
        self.long_term_metrics = dict(self.base_metrics)
        self.metrics_history = collections.deque(maxlen=24)  # Keep a day's worth of hourly metrics
        
        # Last serialized metrics
        self.last_metrics_record = {}
    
    def update(self, dt):
        """
        Update performance metrics
        
        Args:
            dt: Delta time in seconds
        """
        current_time = time.time()
        
        # Update rate-based metrics (every minute)
        if current_time - self.last_update_time >= 60:
            self._update_derived_metrics()
            self.last_update_time = current_time
            
        # Periodically record metrics history (hourly)
        elapsed_session_time = current_time - self.session_start_time
        if len(self.metrics_history) == 0 or elapsed_session_time >= len(self.metrics_history) * 3600:
            self._record_metrics_history()
    
    def record_combat_event(self, event_type, value=1, source=None):
        """
        Record a combat event
        
        Args:
            event_type (str): Type of combat event
            value (float): Value associated with the event
            source (str): Source of the event (enemy type, weapon, etc.)
        """
        # Ensure combat metrics exist
        if 'combat' not in self.metrics:
            self.metrics['combat'] = {
                'damage_dealt': 0,
                'damage_taken': 0,
                'kills': 0,
                'deaths': 0,
                'time_to_kill': [],
                'accuracy': [],
                'enemy_types_killed': {},
                'enemy_types_spawned': {}
            }
        
        # Update metrics based on event type
        if event_type == 'damage_dealt':
            self.metrics['combat']['damage_dealt'] += value
            
        elif event_type == 'damage_taken':
            self.metrics['combat']['damage_taken'] += value
            
        elif event_type == 'kill':
            self.metrics['combat']['kills'] += 1
            
            # Track enemy type
            if source:
                if source not in self.metrics['combat']['enemy_types_killed']:
                    self.metrics['combat']['enemy_types_killed'][source] = 0
                self.metrics['combat']['enemy_types_killed'][source] += 1
                
            # Track time to kill if provided
            if isinstance(value, (int, float)) and value > 0:
                self.metrics['combat']['time_to_kill'].append(value)
                
        elif event_type == 'enemy_spawned':
            # Track enemy type spawned
            if source:
                if source not in self.metrics['combat']['enemy_types_spawned']:
                    self.metrics['combat']['enemy_types_spawned'][source] = 0
                self.metrics['combat']['enemy_types_spawned'][source] += 1
                
        elif event_type == 'death':
            self.metrics['combat']['deaths'] += 1
            
        elif event_type == 'accuracy':
            # Record shot accuracy (0-1)
            if 0 <= value <= 1:
                self.metrics['combat']['accuracy'].append(value)
        
        # Schedule metrics update
        self._schedule_metrics_update()
    
    def record_resource_event(self, resource_type, amount, source=None):
        """
        Record a resource gathering event
        
        Args:
            resource_type (str): Type of resource
            amount (int): Amount gathered
            source (str): Source of the resource (node, enemy drop, etc.)
        """
        # Ensure resource metrics exist
        if 'resources' not in self.metrics:
            self.metrics['resources'] = {
                'gathered': {},
                'spent': {},
                'sources': {}
            }
        
        # Track resource gathering
        if resource_type not in self.metrics['resources']['gathered']:
            self.metrics['resources']['gathered'][resource_type] = 0
        self.metrics['resources']['gathered'][resource_type] += amount
        
        # Track source
        if source:
            if source not in self.metrics['resources']['sources']:
                self.metrics['resources']['sources'][source] = {}
            if resource_type not in self.metrics['resources']['sources'][source]:
                self.metrics['resources']['sources'][source][resource_type] = 0
            self.metrics['resources']['sources'][source][resource_type] += amount
        
        # Schedule metrics update
        self._schedule_metrics_update()
    
    def record_city_event(self, event_type, value=1, source=None):
        """
        Record a city-related event
        
        Args:
            event_type (str): Type of city event
            value (float): Value associated with the event
            source (str): Source of the event
        """
        # Ensure city metrics exist
        if 'city' not in self.metrics:
            self.metrics['city'] = {
                'damage_taken': 0,
                'buildings_constructed': 0,
                'buildings_lost': 0,
                'resources_spent': 0,
                'defense_events': 0,
                'defense_success_rate': []
            }
        
        # Update metrics based on event type
        if event_type == 'damage':
            self.metrics['city']['damage_taken'] += value
            
        elif event_type == 'building_constructed':
            self.metrics['city']['buildings_constructed'] += 1
            
        elif event_type == 'building_lost':
            self.metrics['city']['buildings_lost'] += 1
            
        elif event_type == 'resources_spent':
            self.metrics['city']['resources_spent'] += value
            
        elif event_type == 'defense_event':
            self.metrics['city']['defense_events'] += 1
            
        elif event_type == 'defense_success':
            # Record defense success (0-1)
            if 0 <= value <= 1:
                self.metrics['city']['defense_success_rate'].append(value)
        
        # Schedule metrics update
        self._schedule_metrics_update()
    
    def record_boss_event(self, event_type, boss_type=None, defeat_time=None):
        """
        Record a boss-related event
        
        Args:
            event_type (str): Type of boss event (encounter, victory, defeat)
            boss_type (str): Type of boss
            defeat_time (float): Time taken to defeat the boss (in seconds)
        """
        # Ensure boss metrics exist
        if 'bosses' not in self.metrics:
            self.metrics['bosses'] = {
                'encounters': 0,
                'victories': 0,
                'defeats': 0,
                'average_time': None,
                'times': [],
                'boss_types': {}
            }
        
        # Update metrics based on event type
        if event_type == 'encounter':
            self.metrics['bosses']['encounters'] += 1
            
            # Track boss type
            if boss_type:
                if boss_type not in self.metrics['bosses']['boss_types']:
                    self.metrics['bosses']['boss_types'][boss_type] = {
                        'encounters': 0,
                        'victories': 0,
                        'defeats': 0
                    }
                self.metrics['bosses']['boss_types'][boss_type]['encounters'] += 1
                
        elif event_type == 'victory':
            self.metrics['bosses']['victories'] += 1
            
            # Track boss type
            if boss_type:
                if boss_type not in self.metrics['bosses']['boss_types']:
                    self.metrics['bosses']['boss_types'][boss_type] = {
                        'encounters': 0,
                        'victories': 0,
                        'defeats': 0
                    }
                self.metrics['bosses']['boss_types'][boss_type]['victories'] += 1
            
            # Track defeat time
            if defeat_time is not None:
                self.metrics['bosses']['times'].append(defeat_time)
                # Update average time
                self.metrics['bosses']['average_time'] = sum(self.metrics['bosses']['times']) / len(self.metrics['bosses']['times'])
                
        elif event_type == 'defeat':
            self.metrics['bosses']['defeats'] += 1
            
            # Track boss type
            if boss_type:
                if boss_type not in self.metrics['bosses']['boss_types']:
                    self.metrics['bosses']['boss_types'][boss_type] = {
                        'encounters': 0,
                        'victories': 0,
                        'defeats': 0
                    }
                self.metrics['bosses']['boss_types'][boss_type]['defeats'] += 1
        
        # Schedule metrics update
        self._schedule_metrics_update()
    
    def record_survival_event(self, event_type, value=None):
        """
        Record a survival-related event
        
        Args:
            event_type (str): Type of survival event
            value: Value associated with the event
        """
        # Ensure survival metrics exist
        if 'survival' not in self.metrics:
            self.metrics['survival'] = {
                'playtime': 0,
                'deaths': 0,
                'night_cycles_survived': 0,
                'damage_avoided': 0,
                'near_death_events': 0
            }
        
        # Update metrics based on event type
        if event_type == 'playtime':
            self.metrics['survival']['playtime'] += value
            
        elif event_type == 'death':
            self.metrics['survival']['deaths'] += 1
            
        elif event_type == 'night_survived':
            self.metrics['survival']['night_cycles_survived'] += 1
            
        elif event_type == 'damage_avoided':
            self.metrics['survival']['damage_avoided'] += value
            
        elif event_type == 'near_death':
            self.metrics['survival']['near_death_events'] += 1
        
        # Schedule metrics update
        self._schedule_metrics_update()
    
    def get_combat_efficiency_score(self):
        """
        Calculate a score for combat efficiency
        
        Returns:
            float: Combat efficiency score (0.0-1.0)
        """
        # Ensure combat metrics exist
        if 'combat' not in self.metrics:
            return 0.5  # Default middle value
        
        combat = self.metrics['combat']
        
        # Calculate damage efficiency
        damage_ratio = 1.0
        if combat['damage_taken'] > 0:
            damage_ratio = combat['damage_dealt'] / max(1, combat['damage_taken'])
            # Cap the ratio to avoid extreme values
            damage_ratio = min(damage_ratio, 5.0) / 5.0
        
        # Calculate kill efficiency
        kill_ratio = 1.0
        if combat['deaths'] > 0:
            kill_ratio = combat['kills'] / max(1, combat['deaths'])
            # Cap the ratio to avoid extreme values
            kill_ratio = min(kill_ratio, 10.0) / 10.0
        
        # Calculate average time to kill if available
        ttk_efficiency = 0.5  # Default middle value
        if len(combat['time_to_kill']) > 0:
            avg_ttk = sum(combat['time_to_kill']) / len(combat['time_to_kill'])
            # Lower time is better (5s is excellent, 20s is poor)
            ttk_efficiency = 1.0 - min(max((avg_ttk - 5) / 15, 0), 1)
        
        # Calculate accuracy if available
        accuracy = 0.5  # Default middle value
        if len(combat['accuracy']) > 0:
            accuracy = sum(combat['accuracy']) / len(combat['accuracy'])
        
        # Weight the components
        weighted_score = (
            damage_ratio * 0.3 +
            kill_ratio * 0.3 +
            ttk_efficiency * 0.2 +
            accuracy * 0.2
        )
        
        return weighted_score
    
    def get_resource_efficiency_score(self):
        """
        Calculate a score for resource gathering efficiency
        
        Returns:
            float: Resource efficiency score (0.0-1.0)
        """
        # Ensure resource metrics exist
        if 'resources' not in self.metrics:
            return 0.5  # Default middle value
        
        resources = self.metrics['resources']
        
        # If no resources gathered yet, return default
        if not resources['gathered'] or sum(resources['gathered'].values()) == 0:
            return 0.5
        
        # Calculate total resources gathered
        total_gathered = sum(resources['gathered'].values())
        
        # Calculate gathering rate based on playtime if available
        gathering_rate = 0.5  # Default middle value
        if 'survival' in self.metrics and self.metrics['survival']['playtime'] > 0:
            playtime_minutes = self.metrics['survival']['playtime'] / 60
            # Resources per minute
            rate = total_gathered / max(playtime_minutes, 1)
            # Rate of 5 resources/min is decent, 10 is excellent
            gathering_rate = min(rate / 10, 1.0)
        
        # Calculate diversity of resources (better to gather different types)
        diversity = len(resources['gathered']) / 5  # Assuming 5 resource types
        
        # Calculate utilization if spending data is available
        utilization = 0.5  # Default middle value
        if 'spent' in resources and resources['spent']:
            total_spent = sum(resources['spent'].values())
            utilization = min(total_spent / max(total_gathered, 1), 1.0)
        
        # Weight the components
        weighted_score = (
            gathering_rate * 0.5 +
            diversity * 0.3 +
            utilization * 0.2
        )
        
        return weighted_score
    
    def get_city_defense_score(self):
        """
        Calculate a score for city defense success
        
        Returns:
            float: City defense score (0.0-1.0)
        """
        # Ensure city metrics exist
        if 'city' not in self.metrics:
            return 0.5  # Default middle value
        
        city = self.metrics['city']
        
        # Calculate building preservation ratio
        building_ratio = 1.0
        if city['buildings_constructed'] > 0:
            buildings_preserved = city['buildings_constructed'] - city['buildings_lost']
            building_ratio = max(0, buildings_preserved) / max(1, city['buildings_constructed'])
        
        # Calculate defense success rate if available
        defense_rate = 0.5  # Default middle value
        if len(city['defense_success_rate']) > 0:
            defense_rate = sum(city['defense_success_rate']) / len(city['defense_success_rate'])
        
        # Calculate damage resilience (lower damage is better)
        damage_factor = 0.5  # Default middle value
        if 'combat' in self.metrics and self.metrics['combat']['damage_dealt'] > 0:
            # Calculate ratio of city damage to combat damage
            ratio = city['damage_taken'] / max(1, self.metrics['combat']['damage_dealt'])
            # Lower ratio is better (0.1 is excellent, 0.5+ is poor)
            damage_factor = 1.0 - min(ratio, 1.0)
        
        # Weight the components
        weighted_score = (
            building_ratio * 0.4 +
            defense_rate * 0.3 +
            damage_factor * 0.3
        )
        
        return weighted_score
    
    def get_boss_performance_score(self):
        """
        Calculate a score for boss encounter performance
        
        Returns:
            float: Boss performance score (0.0-1.0)
        """
        # Ensure boss metrics exist
        if 'bosses' not in self.metrics or self.metrics['bosses']['encounters'] == 0:
            return 0.5  # Default middle value
        
        bosses = self.metrics['bosses']
        
        # Calculate victory rate
        victory_rate = bosses['victories'] / max(1, bosses['encounters'])
        
        # Calculate time efficiency if we have timing data
        time_efficiency = 0.5  # Default middle value
        if bosses['average_time'] is not None:
            # Lower time is better (120s is excellent, 300s+ is poor)
            time_efficiency = 1.0 - min(max((bosses['average_time'] - 120) / 180, 0), 1)
        
        # Weight the components (victory rate is more important)
        weighted_score = (
            victory_rate * 0.7 +
            time_efficiency * 0.3
        )
        
        return weighted_score
    
    def get_survival_score(self):
        """
        Calculate a score for survival performance
        
        Returns:
            float: Survival score (0.0-1.0)
        """
        # Ensure survival metrics exist
        if 'survival' not in self.metrics:
            return 0.5  # Default middle value
        
        survival = self.metrics['survival']
        
        # Calculate night survival rate if we have night cycle data
        night_survival = 0.5  # Default middle value
        if survival['night_cycles_survived'] > 0:
            # Better if more nights survived
            night_survival = min(survival['night_cycles_survived'] / 5, 1.0)
        
        # Calculate death avoidance
        death_avoidance = 1.0
        if survival['near_death_events'] > 0:
            # Calculate ratio of avoided deaths to near-death events
            avoided = survival['near_death_events'] - survival['deaths']
            death_avoidance = max(0, avoided) / max(1, survival['near_death_events'])
        
        # Calculate damage avoidance if available
        avoidance_rate = 0.5  # Default middle value
        if 'combat' in self.metrics and self.metrics['combat']['damage_taken'] > 0:
            # Calculate ratio of avoided damage to taken damage
            ratio = survival['damage_avoided'] / max(1, self.metrics['combat']['damage_taken'])
            # Higher ratio is better
            avoidance_rate = min(ratio, 2.0) / 2.0
        
        # Weight the components
        weighted_score = (
            night_survival * 0.4 +
            death_avoidance * 0.4 +
            avoidance_rate * 0.2
        )
        
        return weighted_score
    
    def get_overall_performance_score(self):
        """
        Calculate an overall performance score combining all metrics
        
        Returns:
            float: Overall performance score (0.0-1.0)
        """
        # Get individual scores
        combat_score = self.get_combat_efficiency_score()
        resource_score = self.get_resource_efficiency_score()
        city_score = self.get_city_defense_score()
        boss_score = self.get_boss_performance_score()
        survival_score = self.get_survival_score()
        
        # Weight the components
        weighted_score = (
            combat_score * 0.3 +
            resource_score * 0.15 +
            city_score * 0.2 +
            boss_score * 0.2 +
            survival_score * 0.15
        )
        
        # Log the scores if in debug mode
        if hasattr(self.game, 'debug_mode') and self.game.debug_mode:
            print(f"Performance Scores:")
            print(f"  Combat: {combat_score:.2f}")
            print(f"  Resource: {resource_score:.2f}")
            print(f"  City: {city_score:.2f}")
            print(f"  Boss: {boss_score:.2f}")
            print(f"  Survival: {survival_score:.2f}")
            print(f"  Overall: {weighted_score:.2f}")
        
        return weighted_score
    
    def _update_derived_metrics(self):
        """Update rate-based and derived metrics"""
        current_time = time.time()
        
        # Calculate time windows
        short_term_elapsed = min(current_time - self.session_start_time, self.short_term_window)
        long_term_elapsed = min(current_time - self.session_start_time, self.long_term_window)
        
        if short_term_elapsed > 0:
            # Short-term metrics (per minute rates)
            minutes_short = short_term_elapsed / 60.0
            
            self.short_term_metrics['damage_dealt_per_minute'] = self.short_term_metrics['damage_dealt'] / minutes_short
            self.short_term_metrics['damage_taken_per_minute'] = self.short_term_metrics['damage_taken'] / minutes_short
            self.short_term_metrics['kills_per_minute'] = self.short_term_metrics['enemies_killed'] / minutes_short
            
            # Resource rates
            for resource_type, amount in self.short_term_metrics['resources_collected'].items():
                self.short_term_metrics['resources_per_minute'][resource_type] = amount / minutes_short
        
        if long_term_elapsed > 0:
            # Long-term metrics (per minute rates)
            minutes_long = long_term_elapsed / 60.0
            
            self.long_term_metrics['damage_dealt_per_minute'] = self.long_term_metrics['damage_dealt'] / minutes_long
            self.long_term_metrics['damage_taken_per_minute'] = self.long_term_metrics['damage_taken'] / minutes_long
            self.long_term_metrics['kills_per_minute'] = self.long_term_metrics['enemies_killed'] / minutes_long
            
            # Resource rates
            for resource_type, amount in self.long_term_metrics['resources_collected'].items():
                self.long_term_metrics['resources_per_minute'][resource_type] = amount / minutes_long
    
    def _record_metrics_history(self):
        """Record current metrics for historical tracking"""
        # Create a snapshot of current metrics
        snapshot = {
            'timestamp': time.time(),
            'elapsed_time': time.time() - self.session_start_time,
            'short_term': dict(self.short_term_metrics),
            'long_term': dict(self.long_term_metrics)
        }
        
        # Add to history
        self.metrics_history.append(snapshot)
        self.last_metrics_record = snapshot
    
    def get_performance_snapshot(self):
        """
        Get a snapshot of current performance metrics
        
        Returns:
            dict: Dictionary of current performance metrics
        """
        return {
            'short_term': dict(self.short_term_metrics),
            'long_term': dict(self.long_term_metrics),
            'session_time': time.time() - self.session_start_time
        }
    
    def calculate_combat_efficiency(self):
        """
        Calculate combat efficiency rating
        
        Returns:
            float: Combat efficiency rating (-1.0 to 1.0)
        """
        # Use short-term metrics for recent performance
        damage_dealt = self.short_term_metrics['damage_dealt']
        damage_taken = self.short_term_metrics['damage_taken']
        kills = self.short_term_metrics['enemies_killed']
        deaths = self.short_term_metrics['deaths']
        
        # Calculate damage efficiency (damage dealt vs taken)
        damage_ratio = 0.5  # Default neutral value
        if damage_dealt + damage_taken > 0:
            damage_ratio = damage_dealt / (damage_dealt + damage_taken)
        
        # Calculate kill/death ratio
        kd_ratio = 1.0  # Default neutral value
        if deaths > 0:
            kd_ratio = kills / deaths
        elif kills > 0:
            kd_ratio = 2.0  # No deaths is excellent
            
        # Normalize KD ratio to 0-1 range
        normalized_kd = min(1.0, kd_ratio / 4.0)  # Cap at 4:1 KD ratio
        
        # Combine factors (weighted)
        combined_rating = (damage_ratio * 0.7) + (normalized_kd * 0.3)
        
        # Scale to -1 to 1 range
        return (combined_rating * 2) - 1
    
    def calculate_resource_efficiency(self):
        """
        Calculate resource gathering efficiency
        
        Returns:
            float: Resource efficiency rating (-1.0 to 1.0)
        """
        # Get resource rates for short-term period
        resource_rates = self.short_term_metrics['resources_per_minute']
        
        if not resource_rates:
            return 0.0  # Neutral if no resources gathered
            
        # Get a combined rate across all resources
        total_resources_per_minute = sum(resource_rates.values())
        
        # Base efficiency assumes approximately 5 resources per minute is average
        baseline_rate = 5.0
        efficiency = total_resources_per_minute / baseline_rate
        
        # Normalize to -1 to 1 range (cap at 3x baseline)
        normalized = min(2.0, efficiency) / 2.0
        
        return normalized * 2 - 1
    
    def calculate_overall_performance(self):
        """
        Calculate overall player performance rating
        
        Returns:
            float: Performance rating (-1.0 to 1.0)
        """
        # Get component ratings
        combat_rating = self.calculate_combat_efficiency()
        resource_rating = self.calculate_resource_efficiency()
        
        # Survival factor based on deaths
        recent_deaths = self.short_term_metrics['deaths']
        survival_rating = 0.0
        if recent_deaths == 0:
            survival_rating = 1.0
        elif recent_deaths == 1:
            survival_rating = 0.0
        else:
            survival_rating = -1.0
        
        # Boss performance (if any)
        boss_rating = 0.0
        if self.short_term_metrics['boss_encounters'] > 0:
            victory_rate = self.short_term_metrics['boss_victories'] / self.short_term_metrics['boss_encounters']
            boss_rating = (victory_rate * 2) - 1
        
        # Weight the components based on their importance to difficulty
        weights = {
            'combat': 0.5,
            'resource': 0.2,
            'survival': 0.2,
            'boss': 0.1
        }
        
        overall_rating = (
            combat_rating * weights['combat'] +
            resource_rating * weights['resource'] +
            survival_rating * weights['survival'] +
            boss_rating * weights['boss']
        )
        
        return max(-1.0, min(1.0, overall_rating)) 