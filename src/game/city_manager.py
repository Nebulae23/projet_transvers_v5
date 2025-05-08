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
        
        # City sections and walls for fog damage
        self.sections = []
        self.walls = []
        self.fog_protection = 0.0  # 0.0 to 1.0 scale (0 = no protection, 1 = full protection)
        self.fog_damage_timer = 0.0
        
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
                
                # Add to city sections
                self.sections.append({
                    'position': Vec3(x1, y1, 0),
                    'angle': angle1,
                    'health': 100,
                    'max_health': 100,
                    'marker': marker,
                    'protected': False,
                    'wall': None
                })
        
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
        
        # Update fog damage timer
        self._update_fog_protection(dt)
        
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
        """Level up the city and improve its stats"""
        self.city_level += 1
        self.city_exp -= self.exp_to_next_level
        self.exp_to_next_level = int(self.exp_to_next_level * 1.5)  # Increase XP needed for next level
        
        # Improve city stats
        self.defense += 5
        self.detection_range += 2
        self.max_defenders += 1
        self.food_production += 1
        self.healing_rate += 0.5
        
        # Update visuals
        self._update_city_visuals()
        
        print(f"City leveled up to level {self.city_level}!")
        
    def _update_city_visuals(self):
        """Update city visuals based on current level"""
        # For now, just scale the city boundary markers based on level
        scale_factor = 1.0 + (self.city_level - 1) * 0.1
        
        for child in self.boundary_marker.getChildren():
            child.setScale(0.5 * scale_factor, 0.5 * scale_factor, 1.5 * scale_factor)
        
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
            position: The position to check
            
        Returns:
            bool: True if position is inside city, False otherwise
        """
        # Simple distance check for now
        distance = (position - self.city_center).length()
        return distance < self.city_radius
        
    def set_city_center(self, position):
        """
        Set the city center position
        
        Args:
            position: The new city center position
        """
        self.city_center = Vec3(position)
        if self.boundary_marker:
            self.boundary_marker.setPos(self.city_center)
            
        print(f"City center set to {self.city_center}")
        
    def add_defender(self):
        """
        Add a defender to the city
        
        Returns:
            bool: True if defender added successfully, False otherwise
        """
        if self.current_defenders < self.max_defenders:
            self.current_defenders += 1
            print(f"Defender added. Current defenders: {self.current_defenders}/{self.max_defenders}")
            return True
        else:
            print(f"Cannot add defender. Already at maximum ({self.max_defenders}).")
            return False
        
    def remove_defender(self):
        """
        Remove a defender from the city
        
        Returns:
            bool: True if defender removed successfully, False otherwise
        """
        if self.current_defenders > 0:
            self.current_defenders -= 1
            print(f"Defender removed. Current defenders: {self.current_defenders}/{self.max_defenders}")
            return True
        else:
            print("Cannot remove defender. No defenders left.")
            return False
        
    def get_city_stats(self):
        """
        Get city statistics
        
        Returns:
            dict: Dictionary of city stats
        """
        return {
            'level': self.city_level,
            'exp': self.city_exp,
            'exp_to_next_level': self.exp_to_next_level,
            'defense': self.defense,
            'detection_range': self.detection_range,
            'max_defenders': self.max_defenders,
            'current_defenders': self.current_defenders,
            'food_production': self.food_production,
            'food_storage': int(self.food_storage),
            'healing_rate': self.healing_rate,
            'fog_protection': int(self.fog_protection * 100)
        }
        
    def calculate_defense_bonus(self):
        """
        Calculate defense bonus for player when in the city
        
        Returns:
            float: Defense bonus multiplier (1.0 = no bonus, >1.0 = bonus)
        """
        base_bonus = 1.0 + (self.defense / 100.0)  # Each defense point gives 1% bonus
        return base_bonus
        
    def _update_fog_protection(self, dt):
        """
        Update fog protection status and handle damage
        
        Args:
            dt: Delta time in seconds
        """
        # Update protection level based on walls and other defenses
        total_sections = len(self.sections)
        protected_sections = sum(1 for section in self.sections if section['protected'])
        
        if total_sections > 0:
            self.fog_protection = protected_sections / total_sections
        else:
            self.fog_protection = 0.0
            
        # Update visual indicators for protection
        for section in self.sections:
            if section['protected']:
                # Add blue glow or indicator
                section['marker'].setColor(0.2, 0.4, 0.8, 1.0)
            else:
                # Normal color
                section['marker'].setColor(0.6, 0.6, 0.6, 1.0)
        
    def apply_fog_damage(self, damage):
        """
        Apply damage from fog to unprotected city sections
        
        Args:
            damage: Base damage amount
            
        Returns:
            float: Actual damage applied
        """
        # Only apply damage if there's fog
        if not hasattr(self.game, 'night_fog') or not self.game.night_fog.active:
            return 0.0
            
        # Reduce damage based on fog protection
        actual_damage = damage * (1.0 - self.fog_protection)
        
        # Apply damage to unprotected sections
        for section in self.sections:
            if not section['protected']:
                section['health'] -= actual_damage
                
                # Clamp health
                section['health'] = max(0, section['health'])
                
                # Visual indicator of damage
                damage_factor = section['health'] / section['max_health']
                if damage_factor < 0.3:
                    # Severely damaged
                    section['marker'].setColor(0.8, 0.2, 0.2, 1.0)
                elif damage_factor < 0.7:
                    # Moderately damaged
                    section['marker'].setColor(0.8, 0.6, 0.2, 1.0)
                
        # Show message if significant damage
        if actual_damage > 5:
            self.show_fog_damage_warning(actual_damage)
            
        return actual_damage
        
    def show_fog_damage_warning(self, damage):
        """
        Show a warning about fog damage
        
        Args:
            damage: Damage amount
        """
        if hasattr(self.game, 'show_message'):
            self.game.show_message(f"Night fog damaging city! ({int(damage)} damage)")
        else:
            print(f"City taking {int(damage)} damage from night fog!")
        
    def add_wall(self, position, angle):
        """
        Add a wall to protect a city section
        
        Args:
            position: Position to place wall
            angle: Wall orientation angle
            
        Returns:
            bool: True if wall added successfully
        """
        # Find the nearest section
        nearest_section = None
        nearest_distance = float('inf')
        
        for section in self.sections:
            distance = (section['position'] - position).length()
            if distance < nearest_distance:
                nearest_distance = distance
                nearest_section = section
                
        # If section is close enough, add wall
        if nearest_section and nearest_distance < 5.0:
            if nearest_section['wall'] is None:
                # Create wall
                wall = self.game.loader.loadModel("models/box")
                wall.setScale(4, 0.5, 2)
                wall.setH(math.degrees(angle))
                wall.setPos(position)
                wall.setColor(0.4, 0.4, 0.6, 1.0)
                wall.reparentTo(self.game.render)
                
                # Mark section as protected
                nearest_section['protected'] = True
                nearest_section['wall'] = wall
                
                # Add to walls list
                self.walls.append(wall)
                
                # Update fog protection
                self._update_fog_protection(0)
                
                return True
                
        return False
        
    def repair_section(self, position):
        """
        Repair a damaged city section
        
        Args:
            position: Position near the section to repair
            
        Returns:
            bool: True if repair successful
        """
        # Find the nearest section
        nearest_section = None
        nearest_distance = float('inf')
        
        for section in self.sections:
            distance = (section['position'] - position).length()
            if distance < nearest_distance:
                nearest_distance = distance
                nearest_section = section
                
        # If section is close enough and damaged, repair it
        if nearest_section and nearest_distance < 5.0:
            if nearest_section['health'] < nearest_section['max_health']:
                # Repair to full health
                nearest_section['health'] = nearest_section['max_health']
                
                # Reset color
                if nearest_section['protected']:
                    nearest_section['marker'].setColor(0.2, 0.4, 0.8, 1.0)
                else:
                    nearest_section['marker'].setColor(0.6, 0.6, 0.6, 1.0)
                
                return True
                
        return False 