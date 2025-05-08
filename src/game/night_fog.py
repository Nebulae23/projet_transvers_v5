#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Night Fog System for Nightfall Defenders
Implements a fog that approaches the city at night and serves as a spawn medium for monsters
"""

from panda3d.core import NodePath, Fog, Vec3, Vec4, Point3
import math
import random
import os

class NightFog:
    """Manages the night fog that approaches the city during night time"""
    
    def __init__(self, game):
        """
        Initialize the night fog system
        
        Args:
            game: The main game instance
        """
        self.game = game
        
        # Fog properties
        self.active = False
        self.intensity = 0.0  # 0.0 to 1.0 scale
        self.damage_enabled = True
        self.spawn_enabled = True
        
        # Movement properties
        self.speed = 1.0  # Base movement speed
        self.edge_distance = 100.0  # Distance from map center to edge where fog starts
        self.city_distance = 10.0  # Distance from center where city is considered protected
        
        # Fog tendrils - lists of fog sources that move toward city
        self.tendrils = []
        self.max_tendrils = 5
        
        # Visibility effects
        self.max_visibility_reduction = 0.7  # Maximum reduction (70%)
        
        # Spawn properties
        self.spawn_chance = 0.05  # Base chance per tendril per second
        self.spawn_distance_factor = 0.8  # Closer to city = more spawns
        
        # Damage properties
        self.damage_interval = 5.0  # Seconds between damage ticks
        self.damage_timer = 0.0
        self.base_damage = 5  # Base damage per tick to city sections
        
        # Visual properties
        self.fog_color = Vec4(0.1, 0.1, 0.2, 1.0)  # Base fog color
        self.setup_visual_effects()
        
        # Difficulty scaling
        self.difficulty_speed_multiplier = 1.0
        self.difficulty_damage_multiplier = 1.0
        self.difficulty_spawn_multiplier = 1.0
        
        # City reference for damage calculations
        self.city_center = Vec3(0, 0, 0)
        if hasattr(self.game, 'city_manager') and hasattr(self.game.city_manager, 'city_center'):
            self.city_center = self.game.city_manager.city_center
    
    def setup_visual_effects(self):
        """Set up the visual effects for the night fog"""
        # Create a main node for all fog effects
        self.fog_root = self.game.render.attachNewNode("night_fog_root")
        
        # Try to set up shader-based volumetric fog if supported
        try:
            # Set up shader for volumetric fog if available
            shader_path = "src/assets/shaders/fog_volume.glsl"
            if os.path.exists(shader_path):
                from panda3d.core import Shader
                self.fog_shader = Shader.load(Shader.SL_Cg, 
                                          vertex=shader_path,
                                          fragment=shader_path)
                print("Loaded volumetric fog shader")
            else:
                print("Volumetric fog shader not found, using standard fog")
                self.fog_shader = None
        except Exception as e:
            print(f"Could not set up volumetric fog shader: {e}")
            self.fog_shader = None
        
        # Set up standard fog as fallback
        self.standard_fog = Fog("night_fog")
        self.standard_fog.setColor(self.fog_color)
        self.standard_fog.setExpDensity(0.0)  # Start with no fog
    
    def update(self, dt):
        """
        Update the night fog
        
        Args:
            dt: Delta time in seconds
        """
        # Only process if active
        if not self.active:
            return
        
        # Update fog intensity based on time of day
        self._update_fog_intensity()
        
        # Apply current difficulty settings from adaptive difficulty system if available
        self._apply_adaptive_difficulty()
        
        # Update fog tendrils
        self._update_tendrils(dt)
        
        # Handle enemy spawning in fog
        if self.spawn_enabled:
            self._process_enemy_spawning(dt)
        
        # Handle city damage from fog
        if self.damage_enabled:
            self._process_city_damage(dt)
        
        # Update visual effects
        self._update_visual_effects()
    
    def _update_fog_intensity(self):
        """Update fog intensity based on time of day"""
        # Get current time of day
        if hasattr(self.game, 'day_night_cycle'):
            time_of_day = self.game.day_night_cycle.time_of_day
            current_time = self.game.day_night_cycle.current_time
            
            # Import TimeOfDay if available
            try:
                from game.day_night_cycle import TimeOfDay
                
                # Determine fog intensity based on time of day
                if time_of_day == TimeOfDay.NIGHT:
                    # Ramp up during night
                    night_progress = (current_time - 0.75) * 4  # 0 to 1 during night phase
                    self.intensity = min(0.7 + night_progress * 0.3, 1.0)
                elif time_of_day == TimeOfDay.MIDNIGHT:
                    # Full intensity at midnight
                    self.intensity = 1.0
                elif time_of_day == TimeOfDay.DAWN:
                    # Ramp down during dawn
                    dawn_progress = current_time * 4  # 0 to 1 during dawn phase
                    self.intensity = max(0.0, 1.0 - dawn_progress)
                else:
                    # No fog during day and dusk
                    self.intensity = 0.0
            except ImportError:
                # Fallback if TimeOfDay isn't available
                # Use simple day/night detection based on light levels
                if hasattr(self.game.day_night_cycle, 'directional_light'):
                    light_brightness = self.game.day_night_cycle.directional_light.getColor().length()
                    # Light below 0.5 brightness = night
                    self.intensity = max(0.0, 1.0 - light_brightness)
                else:
                    # Can't determine, use manual control
                    pass
        
        # Ensure fog is only active when intensity > 0
        self.active = self.intensity > 0.0
    
    def _apply_adaptive_difficulty(self):
        """Apply adaptive difficulty settings to fog parameters"""
        if hasattr(self.game, 'adaptive_difficulty_system'):
            # Get current difficulty factors
            factors = self.game.adaptive_difficulty_system.get_current_difficulty_factors()
            
            # Apply fog-specific factors
            self.difficulty_speed_multiplier = factors['fog_speed']
            self.difficulty_damage_multiplier = factors['enemy_damage'] # Use enemy damage for fog damage
            self.difficulty_spawn_multiplier = factors['enemy_spawn_rate']
            
            # Adjust fog density based on difficulty
            if hasattr(self, 'standard_fog'):
                # Use fog_density factor for visual density
                density_modifier = factors['fog_density']
                self.standard_fog.setExpDensity(0.005 * self.intensity * density_modifier)
            
            # Debug info
            if hasattr(self.game, 'debug_mode') and self.game.debug_mode:
                print(f"Applied adaptive difficulty to night fog:")
                print(f"  Speed: x{self.difficulty_speed_multiplier:.2f}")
                print(f"  Damage: x{self.difficulty_damage_multiplier:.2f}")
                print(f"  Spawn Rate: x{self.difficulty_spawn_multiplier:.2f}")
                print(f"  Density: x{factors['fog_density']:.2f}")
    
    def _update_tendrils(self, dt):
        """
        Update fog tendrils movement
        
        Args:
            dt: Delta time in seconds
        """
        # Spawn new tendrils if needed
        self._spawn_tendrils()
        
        # Update existing tendrils
        for i, tendril in enumerate(self.tendrils):
            # Calculate movement direction toward city center
            direction = self.city_center - tendril['position']
            distance = direction.length()
            
            if distance > 0.1:  # Avoid division by zero
                direction.normalize()
                
                # Movement speed depends on distance and base speed
                # Slower as it gets closer to city
                speed_factor = 0.5 + 0.5 * (distance / self.edge_distance)
                movement = direction * self.speed * speed_factor * self.difficulty_speed_multiplier * dt
                
                # Update position
                tendril['position'] += movement
                
                # Update visual node if it exists
                if 'node' in tendril and tendril['node']:
                    tendril['node'].setPos(tendril['position'])
            
            # Remove tendril if it reaches the city center
            if distance < self.city_distance:
                # Clean up visual node
                if 'node' in tendril and tendril['node']:
                    tendril['node'].removeNode()
                # Remove from list
                self.tendrils[i] = None
        
        # Clean up removed tendrils
        self.tendrils = [t for t in self.tendrils if t is not None]
    
    def _spawn_tendrils(self):
        """Spawn new fog tendrils from the map edges"""
        # Spawn tendrils only if intensity is high enough and we need more
        if self.intensity > 0.2 and len(self.tendrils) < self.max_tendrils:
            # Scale number of tendrils with intensity
            desired_tendrils = int(self.max_tendrils * self.intensity)
            
            # Spawn new tendrils up to the desired count
            while len(self.tendrils) < desired_tendrils:
                # Random angle around the city
                angle = random.uniform(0, math.pi * 2)
                
                # Position at the edge
                pos_x = self.city_center.x + math.cos(angle) * self.edge_distance
                pos_y = self.city_center.y + math.sin(angle) * self.edge_distance
                position = Vec3(pos_x, pos_y, 0)
                
                # Create visual representation
                node = self._create_tendril_visual(position)
                
                # Add to list
                self.tendrils.append({
                    'position': position,
                    'direction': Vec3(-math.cos(angle), -math.sin(angle), 0),
                    'node': node,
                    'spawn_timer': random.uniform(1.0, 3.0)  # Random timer for first spawn
                })
    
    def _create_tendril_visual(self, position):
        """
        Create visual representation of a fog tendril
        
        Args:
            position: Position of the tendril
        
        Returns:
            NodePath: The node representing the tendril
        """
        # Create a visual representation using particles or models
        try:
            # Simple placeholder using a sphere
            from panda3d.core import Geom, GeomNode
            
            # You would typically use particles for fog, but for now use a simple model
            node = self.game.loader.loadModel("models/box")
            if node:
                # Scale and position
                node.setScale(5, 5, 2)  # Wide, flat fog tendril
                node.setPos(position)
                node.setColor(self.fog_color)
                
                # Apply transparency
                node.setTransparency(1)
                node.setAlphaScale(0.3)  # Semi-transparent
                
                # Attach to fog root
                node.reparentTo(self.fog_root)
                
                # Apply shader if available
                if self.fog_shader:
                    node.setShader(self.fog_shader)
                    node.setShaderInput("fogDensity", self.intensity)
                
                return node
        except Exception as e:
            print(f"Could not create tendril visual: {e}")
        
        return None
    
    def _process_enemy_spawning(self, dt):
        """
        Process enemy spawning from fog tendrils
        
        Args:
            dt: Delta time in seconds
        """
        # Only spawn if we have an entity manager
        if not hasattr(self.game, 'entity_manager'):
            return
        
        # Process each tendril
        for tendril in self.tendrils:
            # Update spawn timer
            tendril['spawn_timer'] -= dt
            
            # Check if it's time to spawn
            if tendril['spawn_timer'] <= 0:
                # Calculate base spawn chance adjusted by difficulty
                spawn_roll = random.random()
                
                # Calculate distance-based spawn chance modifier
                # Closer to city = higher chance
                distance = (tendril['position'] - self.city_center).length()
                distance_factor = 1.0 - (distance / self.edge_distance) * self.spawn_distance_factor
                
                # Final spawn chance
                final_chance = self.spawn_chance * self.intensity * distance_factor * self.difficulty_spawn_multiplier
                
                # Attempt to spawn
                if spawn_roll < final_chance:
                    # Spawn an enemy at the tendril position
                    self.game.entity_manager.spawn_enemy_at_position(tendril['position'])
                
                # Reset timer with some randomness
                tendril['spawn_timer'] = random.uniform(0.5, 2.0)
    
    def _process_city_damage(self, dt):
        """
        Process damage to unprotected city sections
        
        Args:
            dt: Delta time in seconds
        """
        # Only process if we have a city manager
        if not hasattr(self.game, 'city_manager'):
            return
        
        # Update damage timer
        self.damage_timer -= dt
        
        # Check if it's time to apply damage
        if self.damage_timer <= 0:
            # Reset timer
            self.damage_timer = self.damage_interval
            
            # Calculate total damage based on fog intensity and difficulty
            total_damage = self.base_damage * self.intensity * self.difficulty_damage_multiplier
            
            # Apply damage to city sections
            # This depends on your city system implementation
            if hasattr(self.game.city_manager, 'apply_fog_damage'):
                self.game.city_manager.apply_fog_damage(total_damage)
            elif hasattr(self.game.city_manager, 'damage_city'):
                self.game.city_manager.damage_city(total_damage)
    
    def _update_visual_effects(self):
        """Update visual effects based on current fog state"""
        # Update standard fog density
        if self.standard_fog:
            # Scale density with intensity
            self.standard_fog.setExpDensity(0.005 * self.intensity)
            
            # Only apply fog if active
            if self.active and self.intensity > 0.01:
                self.game.render.setFog(self.standard_fog)
            else:
                self.game.render.clearFog()
        
        # Update shader parameters if using volumetric fog
        if self.fog_shader:
            # Update all tendril visuals
            for tendril in self.tendrils:
                if 'node' in tendril and tendril['node']:
                    tendril['node'].setShaderInput("fogDensity", self.intensity)
    
    def get_visibility_factor(self, position):
        """
        Get the visibility factor at a position (1.0 = full visibility, 0.0 = no visibility)
        
        Args:
            position: Position to check
            
        Returns:
            float: Visibility factor (0.0 to 1.0)
        """
        if not self.active:
            return 1.0
        
        # Base visibility reduction from overall fog intensity
        visibility = 1.0 - (self.intensity * 0.3)
        
        # Calculate additional reduction based on proximity to tendrils
        for tendril in self.tendrils:
            distance = (position - tendril['position']).length()
            
            # Tendril effect radius
            radius = 15.0
            
            if distance < radius:
                # Closer to tendril = less visibility
                tendril_factor = distance / radius
                local_visibility = tendril_factor
                
                # Take minimum visibility between current and this tendril
                visibility = min(visibility, local_visibility)
        
        # Ensure visibility stays within bounds
        return max(1.0 - self.max_visibility_reduction, visibility)
    
    def is_in_fog(self, position):
        """
        Check if a position is inside fog
        
        Args:
            position: Position to check
            
        Returns:
            bool: True if in fog, False otherwise
        """
        if not self.active:
            return False
        
        # Consider a position "in fog" if visibility is below threshold
        visibility = self.get_visibility_factor(position)
        return visibility < 0.7
    
    def set_difficulty(self, difficulty_level):
        """
        Set the fog system difficulty level manually (used for testing)
        
        Args:
            difficulty_level: Difficulty level (0.0 = easiest, 1.0 = normal, 2.0+ = harder)
        """
        # Scale different aspects based on difficulty
        self.difficulty_speed_multiplier = 0.7 + (difficulty_level * 0.3)  # 0.7x to 1.3x speed
        self.difficulty_damage_multiplier = 0.5 + (difficulty_level * 0.5)  # 0.5x to 1.5x damage
        self.difficulty_spawn_multiplier = 0.5 + (difficulty_level * 0.5)  # 0.5x to 1.5x spawns
        
        # Adjust maximum tendrils based on difficulty
        self.max_tendrils = 3 + int(difficulty_level * 2)  # 3 to 7 tendrils
        
        # Debug info
        if hasattr(self.game, 'debug_mode') and self.game.debug_mode:
            print(f"Manually set night fog difficulty to {difficulty_level:.1f}:")
            print(f"  Speed: x{self.difficulty_speed_multiplier:.2f}")
            print(f"  Damage: x{self.difficulty_damage_multiplier:.2f}")
            print(f"  Spawn Rate: x{self.difficulty_spawn_multiplier:.2f}")
            print(f"  Max Tendrils: {self.max_tendrils}")
    
    def toggle(self):
        """Toggle night fog on/off"""
        self.active = not self.active
        
        # Update visual effects based on new state
        if self.active:
            # Force intensity to be visible
            self.intensity = 0.7 if self.intensity < 0.1 else self.intensity
            print("Night fog activated")
        else:
            # Keep intensity value but disable fog
            print("Night fog deactivated")
            
        # Update visual effects
        self._update_visual_effects()
    
    def set_intensity(self, intensity):
        """
        Set fog intensity directly (mainly for debugging)
        
        Args:
            intensity: Fog intensity (0.0 to 1.0)
        """
        self.intensity = max(0.0, min(1.0, intensity))
        self.active = self.intensity > 0.0
        
        # Update visuals immediately
        self._update_visual_effects() 