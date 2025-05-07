#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
City Manager for Nightfall Defenders
Manages overall city state and coordinates building placement
"""

from panda3d.core import Vec3, NodePath
import math

class CityManager:
    """Manages the city state, resources, and defenses"""
    
    def __init__(self, game):
        """
        Initialize the city manager
        
        Args:
            game: The main game instance
        """
        self.game = game
        
        # City center position
        self.city_center = Vec3(0, 0, 0)
        
        # City radius
        self.city_radius = 50.0
        
        # City stats
        self.defense = 0
        self.detection_range = 20  # Base detection range
        self.max_defenders = 0
        self.current_defenders = 0
        self.food_production = 0
        self.food_storage = 0
        self.food_consumption = 0
        self.healing_rate = 0
        
        # City level
        self.city_level = 1
        self.city_exp = 0
        self.exp_to_next_level = 100
        
        # Attack state
        self.under_attack = False
        self.last_attack_time = 0
        self.attack_warning_cooldown = 0
        
        # Visual representation of city boundaries
        self.boundary_marker = None
        
        # Initialize city representation
        self._initialize_city_visuals()
        
    def _initialize_city_visuals(self):
        """Initialize visual representations of the city"""
        # Create a simple visual boundary for the city
        self.boundary_marker = NodePath("city_boundary")
        self.boundary_marker.reparentTo(self.game.render)
        self.boundary_marker.setPos(self.city_center)
        
        # Create a simple circular boundary
        segments = 20
        for i in range(segments):
            angle1 = 2.0 * math.pi * i / segments
            angle2 = 2.0 * math.pi * (i + 1) / segments
            
            x1 = math.sin(angle1) * self.city_radius
            y1 = math.cos(angle1) * self.city_radius
            
            x2 = math.sin(angle2) * self.city_radius
            y2 = math.cos(angle2) * self.city_radius
            
            # Create line segment for boundary
            # In a full implementation, this would create a visual line segment
            # Here we'll just place marker posts at intervals
            if i % 4 == 0:
                marker = self.game.loader.loadModel("models/box")  # Placeholder
                marker.setScale(0.5, 0.5, 1.5)
                marker.setPos(x1, y1, 0)
                marker.reparentTo(self.boundary_marker)
        
    def update(self, dt):
        """
        Update city status
        
        Args:
            dt: Delta time in seconds
        """
        # Update food production and consumption
        self._update_food(dt)
        
        # Update defenders
        self._update_defenders(dt)
        
        # Check for enemy attacks
        self._check_for_attacks(dt)
        
        # Apply healing from infirmary
        self._apply_healing(dt)
        
        # Check for city level ups
        self._check_level_up()
        
    def _update_food(self, dt):
        """
        Update food production and consumption
        
        Args:
            dt: Delta time in seconds
        """
        # Food production (every 10 game seconds = 1 food unit)
        production_rate = self.food_production / 10.0 * dt
        self.food_storage += production_rate
        
        # Food consumption by defenders (every 15 game seconds per defender)
        if self.current_defenders > 0:
            consumption_rate = self.current_defenders / 15.0 * dt
            self.food_storage -= consumption_rate
            
            # Ensure food doesn't go negative
            if self.food_storage < 0:
                self.food_storage = 0
                # Defenders might leave if no food, but not implementing that now
        
    def _update_defenders(self, dt):
        """
        Update defenders status
        
        Args:
            dt: Delta time in seconds
        """
        # Defenders return to full health over time if not under attack
        if not self.under_attack and self.food_storage > 0:
            # Defenders recover health (not implemented in detail here)
            pass
        
    def _check_for_attacks(self, dt):
        """
        Check for enemy attacks
        
        Args:
            dt: Delta time in seconds
        """
        # Update attack warning cooldown
        if self.attack_warning_cooldown > 0:
            self.attack_warning_cooldown -= dt
        
        # In a real implementation, this would scan for approaching enemies
        # For now, this is a placeholder
        
        # Early warning from watchtowers based on detection range
        enemies_nearby = self._detect_nearby_enemies()
        if enemies_nearby and self.attack_warning_cooldown <= 0:
            self.show_attack_warning()
            self.attack_warning_cooldown = 30  # 30 seconds cooldown between warnings
        
    def _detect_nearby_enemies(self):
        """
        Detect enemies within detection range
        
        Returns:
            bool: True if enemies detected, False otherwise
        """
        # This is a placeholder for the actual detection logic
        # In a real implementation, scan all enemies and check distance to city
        
        for entity in self.game.entity_manager.entities.values():
            if hasattr(entity, 'enemy') and entity.enemy:
                distance = (entity.position - self.city_center).length()
                if distance < self.detection_range:
                    return True
                    
        return False
        
    def show_attack_warning(self):
        """Show a warning that enemies are approaching the city"""
        # In a full implementation, this would show an on-screen alert
        print("WARNING: Enemies approaching the city!")
        
        # Could also play a sound effect or flash a visual indicator
        
    def _apply_healing(self, dt):
        """
        Apply healing to player and defenders
        
        Args:
            dt: Delta time in seconds
        """
        if self.healing_rate > 0:
            # Heal player when near city center
            player_distance = (self.game.player.position - self.city_center).length()
            if player_distance < self.city_radius:
                # Apply healing based on healing_rate
                healing_amount = self.healing_rate * dt
                self.game.player.heal(healing_amount)
                
    def _check_level_up(self):
        """Check and process city level ups"""
        if self.city_exp >= self.exp_to_next_level:
            self.level_up()
            
    def level_up(self):
        """Level up the city"""
        self.city_level += 1
        self.city_exp -= self.exp_to_next_level
        
        # Increase city stats with level
        self.city_radius += 5.0
        self.detection_range += 5
        
        # Increase experience required for next level
        self.exp_to_next_level = int(self.exp_to_next_level * 1.5)
        
        # Update city visuals to reflect new size
        self._update_city_visuals()
        
        # Show level up message
        print(f"City leveled up to level {self.city_level}!")
        
    def _update_city_visuals(self):
        """Update city visuals based on current size and level"""
        # Remove old boundary
        if self.boundary_marker:
            self.boundary_marker.removeNode()
            
        # Create new boundary with updated radius
        self._initialize_city_visuals()
        
    def add_city_exp(self, amount):
        """
        Add experience to the city
        
        Args:
            amount: Amount of experience to add
        """
        self.city_exp += amount
        self._check_level_up()
        
    def is_inside_city(self, position):
        """
        Check if a position is inside the city boundaries
        
        Args:
            position: The position to check (Vec3)
            
        Returns:
            bool: True if inside city, False otherwise
        """
        distance = (position - self.city_center).length()
        return distance <= self.city_radius
        
    def set_city_center(self, position):
        """
        Set city center position
        
        Args:
            position: The new city center position (Vec3)
        """
        self.city_center = position
        self._update_city_visuals()
        
    def add_defender(self):
        """
        Add a defender to the city
        
        Returns:
            bool: True if defender added, False if max reached
        """
        if self.current_defenders < self.max_defenders:
            self.current_defenders += 1
            return True
        return False
        
    def remove_defender(self):
        """
        Remove a defender from the city
        
        Returns:
            bool: True if defender removed, False if none to remove
        """
        if self.current_defenders > 0:
            self.current_defenders -= 1
            return True
        return False
        
    def get_city_stats(self):
        """
        Get current city stats
        
        Returns:
            dict: Dictionary of city stats
        """
        return {
            "level": self.city_level,
            "exp": self.city_exp,
            "exp_to_next": self.exp_to_next_level,
            "defense": self.defense,
            "detection_range": self.detection_range,
            "max_defenders": self.max_defenders,
            "current_defenders": self.current_defenders,
            "food_production": self.food_production,
            "food_storage": int(self.food_storage),
            "healing_rate": self.healing_rate
        }
        
    def calculate_defense_bonus(self):
        """
        Calculate defense bonus for player
        
        Returns:
            float: Defense bonus percentage
        """
        # Base defense is 0%, increases with city level and buildings
        return self.defense / 100.0  # Convert to percentage 