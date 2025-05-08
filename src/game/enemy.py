#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Enemy entity module for Nightfall Defenders
"""

from panda3d.core import NodePath, Vec3, Point3
import math
import random
from game.enemy_healthbar import EnemyHealthBar
from game.resource_drop import ResourceDrop
from game.enemy_psychology import EnemyPsychology, PsychologicalState

class Enemy:
    """Base class for all enemies in the game"""
    
    def __init__(self, game, position=Vec3(0, 0, 0)):
        """Initialize the enemy entity"""
        self.game = game
        
        # Create the enemy node
        self.root = NodePath("Enemy")
        self.root.reparentTo(game.render)
        
        # Enemy state
        self.position = Vec3(position)
        self.velocity = Vec3(0, 0, 0)
        self.facing_angle = 0  # In degrees
        
        # Set initial position
        self.root.setPos(self.position)
        
        # Base enemy stats (override in subclasses)
        self.base_max_health = 50
        self.base_speed = 3.0  # Units per second
        self.base_damage = 10  # Damage dealt on contact
        
        # Actual stats after difficulty adjustment
        self.max_health = self.base_max_health
        self.health = self.max_health
        self.speed = self.base_speed
        self.damage = self.base_damage
        
        # Apply difficulty adjustment if available
        self.apply_difficulty_adjustment()
        
        # Other stats
        self.attack_range = 1.5  # Units
        self.detection_range = 10.0  # Units
        self.collision_radius = 0.5
        
        # AI state
        self.current_state = "idle"  # idle, patrol, chase, attack, flee
        self.target = None
        self.patrol_points = []
        self.current_patrol_index = 0
        self.state_time = 0  # Time in current state
        
        # Create psychological traits with default values
        # Will be customized by specific enemy types
        self.psychology_traits = {
            'bravery': 1.0,
            'aggression': 1.0,
            'intelligence': 1.0,
            'pack_mentality': 1.0,
            'dominance': 1.0
        }
        
        # Initialize psychological system with traits
        from game.enemy_psychology import PsychologyTraits, EnemyPsychology
        traits = PsychologyTraits(
            bravery=self.psychology_traits['bravery'],
            aggression=self.psychology_traits['aggression'],
            intelligence=self.psychology_traits['intelligence'],
            pack_mentality=self.psychology_traits['pack_mentality'],
            dominance=self.psychology_traits['dominance']
        )
        
        self.psychology = EnemyPsychology(self)
        self.psychology.traits = traits
        
        # Action cooldowns
        self.attack_cooldown = 0
        self.rally_cooldown = 0  # New cooldown for rally ability
        
        # Available actions for tactical decision making
        self.available_actions = [
            'attack_direct',      # Direct attack at close range
            'attack_ranged',      # Ranged attack if applicable
            'maintain_distance',  # Keep at medium range
            'retreat',            # Move away to max attack range
            'defend',             # Prioritize defense over attack
            'flee',               # Run away from player
            'follow',             # Follow player (for subservient)
            'assist'              # Help player (for subservient)
        ]
        
        # Load the enemy model
        self.setup_model()
        
        # Debug visualization
        self.debug_node = self.root.attachNewNode("EnemyDebug")
        self.draw_debug_visualization()
        
        # Add a health bar
        self.health_bar = EnemyHealthBar(game, self)
        
        # Resource drop parameters
        self.drop_chance = 0.7  # 70% chance to drop resources
        self.possible_drops = ["wood", "stone", "crystal", "herb"]
        self.drop_amounts = {
            "wood": (1, 3),
            "stone": (1, 2),
            "crystal": (1, 1),
            "herb": (1, 2)
        }
        
        # Experience value
        self.experience_value = 10
        
        # Track targeted enemies (for subservient enemies)
        self.enemy_target = None
        
        # Rally effect (for alpha enemies)
        self.rally_active = False
        self.rally_duration = 0
    
    def apply_difficulty_adjustment(self):
        """Apply difficulty adjustment to enemy stats"""
        if hasattr(self.game, 'adaptive_difficulty_system'):
            # Get difficulty factors
            factors = self.game.adaptive_difficulty_system.get_current_difficulty_factors()
            
            # Apply health multiplier
            self.max_health = int(self.base_max_health * factors['enemy_health'])
            self.health = self.max_health
            
            # Apply damage multiplier
            self.damage = self.base_damage * factors['enemy_damage']
            
            # Apply speed multiplier (affected by aggression factor)
            # Higher aggression makes enemies move faster
            self.speed = self.base_speed * (1.0 + (factors['enemy_aggression'] - 1.0) * 0.5)
    
    def get_effective_aggression(self):
        """Get the effective aggression level with difficulty adjustment"""
        base_aggression = self.psychology.traits.aggression
        
        # Apply difficulty adjustment if available
        if hasattr(self.game, 'adaptive_difficulty_system'):
            factors = self.game.adaptive_difficulty_system.get_current_difficulty_factors()
            return base_aggression * factors['enemy_aggression']
        
        return base_aggression
    
    def setup_model(self):
        """Set up the enemy model"""
        # For now, just use a box as placeholder
        try:
            self.model = self.game.loader.loadModel("models/box")
            self.model.setScale(0.5, 0.5, 1.0)  # Enemy dimensions
            self.model.reparentTo(self.root)
            
            # Color the box for visibility
            self.model.setColor(0.8, 0.2, 0.2, 1)  # Red color for enemy
            
            # For alpha enemies, make them larger
            if hasattr(self, 'psychology') and hasattr(self.psychology, 'traits') and \
               hasattr(self.psychology.traits, 'is_alpha') and self.psychology.traits.is_alpha:
                self.model.setScale(0.7, 0.7, 1.4)  # 40% larger
                
        except Exception as e:
            print(f"Error loading enemy model: {e}")
            # Fallback to a simple marker
            from panda3d.core import PointLight
            plight = PointLight("EnemyMarker")
            plight.setColor((1, 0, 0, 1))
            plnp = self.root.attachNewNode(plight)
            plnp.setPos(0, 0, 1)
    
    def draw_debug_visualization(self):
        """Draw debug visualization for the enemy"""
        # Clear any existing debug visualization
        self.debug_node.removeNode()
        self.debug_node = self.root.attachNewNode("EnemyDebug")
        
        # Only draw debug visuals if debug mode is enabled
        if hasattr(self.game, 'debug_mode') and self.game.debug_mode:
            from panda3d.core import LineSegs
            
            # Draw facing direction indicator
            segs = LineSegs()
            segs.setColor(1, 0, 0, 1)  # Red
            segs.moveTo(0, 0, 0.1)  # Slightly above ground
            segs.drawTo(0, 1.0, 0.1)  # Forward direction
            self.debug_node.attachNewNode(segs.create())
            
            # Draw collision radius
            segs = LineSegs()
            segs.setColor(1, 0.5, 0.5, 1)  # Light red
            segments = 16
            for i in range(segments + 1):
                angle = i * 360 / segments
                x = self.collision_radius * math.sin(math.radians(angle))
                y = self.collision_radius * math.cos(math.radians(angle))
                if i == 0:
                    segs.moveTo(x, y, 0.05)  # Slightly above ground
                else:
                    segs.drawTo(x, y, 0.05)
            self.debug_node.attachNewNode(segs.create())
            
            # Draw detection range
            segs = LineSegs()
            segs.setColor(0.8, 0.8, 0.2, 0.5)  # Yellow, semi-transparent
            segments = 32
            for i in range(segments + 1):
                angle = i * 360 / segments
                x = self.detection_range * math.sin(math.radians(angle))
                y = self.detection_range * math.cos(math.radians(angle))
                if i == 0:
                    segs.moveTo(x, y, 0.05)  # Slightly above ground
                else:
                    segs.drawTo(x, y, 0.05)
            self.debug_node.attachNewNode(segs.create())
            
            # Draw attack range
            segs = LineSegs()
            segs.setColor(1, 0, 0, 0.5)  # Red, semi-transparent
            segments = 32
            for i in range(segments + 1):
                angle = i * 360 / segments
                x = self.attack_range * math.sin(math.radians(angle))
                y = self.attack_range * math.cos(math.radians(angle))
                if i == 0:
                    segs.moveTo(x, y, 0.05)  # Slightly above ground
                else:
                    segs.drawTo(x, y, 0.05)
            self.debug_node.attachNewNode(segs.create())
            
            # Draw psychological state indicator
            segs = LineSegs()
            segs.setColor(*self.psychology.indicator_color)  # Color based on psychological state
            segs.moveTo(0, 0, 1.2)
            segs.drawTo(0, 0, 1.5)
            
            # Add state label
            from panda3d.core import TextNode
            text = TextNode('state_text')
            text.setText(self.psychology.get_state_description())
            text.setAlign(TextNode.ACenter)
            text.setTextColor(*self.psychology.indicator_color)
            text_np = self.debug_node.attachNewNode(text)
            text_np.setScale(0.5)
            text_np.setPos(0, 0, 1.6)
            text_np.setBillboardPointEye()
            
            self.debug_node.attachNewNode(segs.create())
    
    def update(self, dt):
        """Update enemy behavior"""
        # Update the position of the node
        self.root.setPos(self.position)
        
        # Update the rotation of the node
        self.root.setH(-self.facing_angle)
        
        # Update cooldowns
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt
            
        if self.rally_cooldown > 0:
            self.rally_cooldown -= dt
            
        # Update rally effect duration
        if self.rally_active:
            self.rally_duration -= dt
            if self.rally_duration <= 0:
                self.rally_active = False
        
        # Update psychological system
        self.psychology.update(dt)
        
        # Update based on state
        if self.psychology.state == PsychologicalState.SUBSERVIENT:
            self.update_subservient_state(dt)
        else:
            if self.current_state == "idle":
                self.update_idle_state(dt)
            elif self.current_state == "patrol":
                self.update_patrol_state(dt)
            elif self.current_state == "chase":
                self.update_chase_state(dt)
            elif self.current_state == "attack":
                self.update_attack_state(dt)
            elif self.current_state == "flee":
                self.update_flee_state(dt)
            elif self.current_state == "chase_building":
                self.update_chase_building_state(dt)
            elif self.current_state == "attack_building":
                self.update_attack_building_state(dt)
            
            # Check for state transitions
            self.check_state_transitions()
        
        # Apply movement velocity to position
        self.apply_movement(dt)
        
        # Update health bar
        if hasattr(self.health_bar, 'update'):
            if hasattr(self.health_bar.update, '__code__') and self.health_bar.update.__code__.co_argcount > 1:
                self.health_bar.update(dt)
            else:
                self.health_bar.update()
        
        # Update the state time
        self.state_time += dt
    
    def update_subservient_state(self, dt):
        """Update behavior when in subservient state"""
        # Look for nearby enemies to attack
        nearby_enemies = self.find_nearby_enemies()
        
        if nearby_enemies and not self.enemy_target:
            # Target the closest enemy
            self.enemy_target = min(nearby_enemies, key=lambda e: (e.position - self.position).length())
        
        if self.enemy_target:
            # Check if enemy target is still valid
            if self.enemy_target in nearby_enemies:
                # Move toward enemy target
                direction = self.enemy_target.position - self.position
                distance = direction.length()
                
                if distance < self.attack_range:
                    # Close enough to attack the enemy
                    self.attack_enemy(self.enemy_target)
                else:
                    # Move toward the enemy
                    direction.normalize()
                    
                    # Use psychological speed modifier
                    self.velocity = direction * self.psychology.get_effective_speed()
                    
                    # Set facing direction
                    self.facing_angle = -math.degrees(math.atan2(direction.x, direction.y))
            else:
                # Target is no longer valid
                self.enemy_target = None
        else:
            # Follow the player at a distance if no enemy targets
            if self.game.player:
                player_pos = self.game.player.position
                direction = player_pos - self.position
                distance = direction.length()
                
                if distance > 5.0:  # Stay within 5 units of player
                    # Move toward player
                    direction.normalize()
                    self.velocity = direction * self.psychology.get_effective_speed() * 0.5  # Move at half speed
                    self.facing_angle = -math.degrees(math.atan2(direction.x, direction.y))
                else:
                    # Stay in place
                    self.velocity = Vec3(0, 0, 0)
    
    def find_nearby_enemies(self):
        """Find nearby enemy entities that are not subservient to the player"""
        nearby_enemies = []
        
        if hasattr(self.game, 'entity_manager'):
            for enemy in self.game.entity_manager.enemies:
                if enemy != self and hasattr(enemy, 'psychology'):
                    # Only target enemies that are not subservient
                    if enemy.psychology.state != PsychologicalState.SUBSERVIENT:
                        distance = (enemy.position - self.position).length()
                        if distance < self.detection_range:
                            nearby_enemies.append(enemy)
        
        return nearby_enemies
    
    def attack_enemy(self, enemy):
        """Attack another enemy (when subservient)"""
        if self.attack_cooldown <= 0:
            # Deal damage to the enemy
            if hasattr(enemy, 'take_damage'):
                damage = self.psychology.get_effective_damage()
                enemy.take_damage(damage)
                
            # Set attack cooldown
            self.attack_cooldown = 1.0  # 1 second between attacks
    
    def update_idle_state(self, dt):
        """Update behavior in idle state"""
        # In idle, occasionally look around or transition to patrol
        if self.state_time > 3.0:  # Idle for 3 seconds
            # 30% chance to look around, 70% chance to patrol
            if random.random() < 0.3:
                # Look in a random direction
                self.facing_angle = random.uniform(0, 360)
                self.state_time = 0  # Reset state timer
            else:
                self.set_state("patrol")
                
                # Generate some patrol points if none exist
                if not self.patrol_points:
                    self.generate_patrol_points()
    
    def update_patrol_state(self, dt):
        """Update behavior in patrol state"""
        # Check if we should flee based on psychological state
        if self.psychology.state in [PsychologicalState.FEARFUL, PsychologicalState.TERRIFIED]:
            self.set_state("flee")
            return
            
        if not self.patrol_points:
            self.set_state("idle")
            return
        
        # Move towards the current patrol point
        target_point = self.patrol_points[self.current_patrol_index]
        direction = target_point - self.position
        distance = direction.length()
        
        # If we've reached the current patrol point, move to the next one
        if distance < 0.5:
            self.current_patrol_index = (self.current_patrol_index + 1) % len(self.patrol_points)
            self.state_time = 0  # Reset state timer
        else:
            # Move towards the patrol point with psychological speed
            direction.normalize()
            self.velocity = direction * self.psychology.get_effective_speed()
            
            # Set facing direction
            self.facing_angle = -math.degrees(math.atan2(direction.x, direction.y))
    
    def update_chase_state(self, dt):
        """Update behavior when in chase state"""
        player = self.game.player
        if not player:
            self.set_state("idle")
            return
            
        # Get direction to player
        direction = player.position - self.position
        distance = direction.length()
        
        # Determine tactical behavior based on psychological state
        chosen_action = self.psychology.make_tactical_decision(self.available_actions)
        
        if chosen_action == 'attack_direct':
            # Approach directly for attack
            if distance < self.attack_range:
                # Within attack range, stop and attack
                self.velocity = Vec3(0, 0, 0)
                self.set_state("attack")
            else:
                # Move toward player
                direction.normalize()
                self.velocity = direction * self.speed * self.psychology.get_effective_speed()
                
        elif chosen_action == 'attack_ranged':
            # Keep distance and use ranged attacks if available
            ideal_distance = self.attack_range * 0.8
            
            if distance < ideal_distance * 0.7:
                # Too close, back up
                direction.normalize()
                self.velocity = -direction * self.speed * self.psychology.get_effective_speed()
            elif distance > ideal_distance * 1.3:
                # Too far, move closer
                direction.normalize()
                self.velocity = direction * self.speed * self.psychology.get_effective_speed()
            else:
                # Good distance for ranged attack
                self.velocity = Vec3(0, 0, 0)
                self.set_state("attack")
                
        elif chosen_action == 'maintain_distance':
            # Try to maintain a medium distance
            ideal_distance = self.attack_range * 1.5
            
            if abs(distance - ideal_distance) < 0.5:
                # At good distance, circle the player
                perpendicular = Vec3(-direction.y, direction.x, 0)
                perpendicular.normalize()
                circle_dir = perpendicular if random.random() < 0.5 else -perpendicular
                self.velocity = circle_dir * self.speed * self.psychology.get_effective_speed() * 0.7
            elif distance < ideal_distance:
                # Too close, back up
                direction.normalize()
                self.velocity = -direction * self.speed * self.psychology.get_effective_speed()
            else:
                # Too far, move closer
                direction.normalize()
                self.velocity = direction * self.speed * self.psychology.get_effective_speed()
                
        elif chosen_action == 'retreat':
            # Move to maximum effective range
            ideal_distance = self.attack_range * 0.9
            
            if distance < ideal_distance:
                # Too close, back up
                direction.normalize()
                self.velocity = -direction * self.speed * self.psychology.get_effective_speed()
            else:
                # At good distance, stop
                self.velocity = Vec3(0, 0, 0)
                
        elif chosen_action == 'defend':
            # Take defensive posture, minimal movement
            if distance < self.attack_range * 0.7:
                # Too close, back up slowly
                direction.normalize()
                self.velocity = -direction * self.speed * self.psychology.get_effective_speed() * 0.5
            else:
                # Hold position
                self.velocity = Vec3(0, 0, 0)
                
        elif chosen_action == 'flee':
            # Get away from player as quickly as possible
            if distance < self.detection_range * 1.5:
                # Still too close, flee
                direction.normalize()
                self.velocity = -direction * self.speed * self.psychology.get_effective_speed() * 1.5
                self.set_state("flee")
            else:
                # Far enough, transition to idle
                self.set_state("idle")
                
        elif chosen_action in ['follow', 'assist']:
            # These are for subservient state, shouldn't reach here
            # Just move toward player
            direction.normalize()
            self.velocity = direction * self.speed * self.psychology.get_effective_speed()
        
        # Set facing direction toward player for appropriate actions
        if chosen_action not in ['flee', 'retreat']:
            # Calculate angle to face player
            if direction.length() > 0:
                self.facing_angle = math.degrees(math.atan2(-direction.x, direction.y))
    
    def update_attack_state(self, dt):
        """Update behavior in attack state"""
        # Check if we should flee based on psychological state
        if not self.psychology.should_attack_player():
            self.set_state("flee")
            return
            
        if not self.target or not hasattr(self.target, 'position'):
            self.set_state("idle")
            return
            
        # Face the target
        direction = self.target.position - self.position
        self.facing_angle = -math.degrees(math.atan2(direction.x, direction.y))
        
        # Check distance to target
        distance = direction.length()
        
        # If out of range, go back to chase
        if distance > self.attack_range:
            self.set_state("chase")
            return
            
        # Stop moving while attacking
        self.velocity = Vec3(0, 0, 0)
        
        # Attack if cooled down
        if self.attack_cooldown <= 0:
            self.perform_attack()
    
    def update_flee_state(self, dt):
        """Enhanced flee behavior for nimble enemies"""
        player = self.game.player
        if not player:
            self.set_state("idle")
            return
        
        # Get direction away from player
        direction = self.position - player.position
        distance = direction.length()
        
        if distance > self.detection_range * 1.5:
            # Far enough away, transition to patrol
            self.set_state("patrol")
            return
            
        # Move away from player with erratic movement
        if direction.length() > 0:
            direction.normalize()
            
            # Add randomization to direction for erratic movement
            if random.random() < 0.2:  # 20% chance per update
                random_angle = random.uniform(-90, 90)  # -90 to 90 degrees
                rad_angle = math.radians(random_angle)
                cos_angle = math.cos(rad_angle)
                sin_angle = math.sin(rad_angle)
                
                # Rotate direction
                new_x = direction.x * cos_angle - direction.y * sin_angle
                new_y = direction.x * sin_angle + direction.y * cos_angle
                direction = Vec3(new_x, new_y, 0)
                direction.normalize()
            
            # Set velocity away from player with enhanced speed when fleeing
            speed_boost = 1.3  # 30% faster when fleeing
            self.velocity = direction * self.speed * self.psychology.get_effective_speed() * speed_boost
            
            # Face away from player
            self.facing_angle = math.degrees(math.atan2(-direction.x, direction.y))
    
    def check_immediate_threat(self):
        """Check for immediate threats like the player"""
        if not hasattr(self.game, 'player') or not self.game.player:
            return False
            
        # Calculate distance to player
        distance = (self.game.player.position - self.position).length()
        
        # Adjust detection range based on time of day
        effective_detection_range = self.detection_range
        
        # If day/night cycle is active, reduce detection range at night
        if hasattr(self.game, 'day_night_cycle'):
            # Get the base visibility from the day/night cycle
            visibility_factor = self.game.day_night_cycle.get_visibility_distance() / 100.0
            
            # Apply visibility modifier to detection range
            effective_detection_range *= visibility_factor
            
            # Minimum detection range
            effective_detection_range = max(3.0, effective_detection_range)
        
        # Return true if player is within detection range
        return distance < effective_detection_range
    
    def check_for_buildings(self):
        """
        Check for buildings in range that can be targeted
        
        Returns:
            tuple: (building, distance) if found, None otherwise
        """
        # Skip if city manager isn't available
        if not hasattr(self.game, 'city_manager'):
            return None
            
        closest_building = None
        closest_distance = float('inf')
        
        # Check all buildings
        for building_id, building in self.game.city_manager.buildings.items():
            # Don't target destroyed buildings
            if building.state == "destroyed":
                continue
                
            # Get building position in world coordinates
            building_pos = Vec3(*self.game.city_manager.grid_to_world(building.position))
            
            # Calculate distance
            distance = (building_pos - self.position).length()
            
            # Check if within range and closer than current closest
            if distance < self.detection_range and distance < closest_distance:
                closest_building = building
                closest_distance = distance
                
        if closest_building:
            return (closest_building, closest_distance)
        
        return None
    
    def check_state_transitions(self):
        """Check for state transitions based on circumstances and psychological state"""
        # Skip if in subservient state (handled separately)
        if self.psychology.state == PsychologicalState.SUBSERVIENT:
            return
            
        # Check for player in detection range - with day/night visibility modifier
        player_detected = self.check_immediate_threat()
        
        # Check for buildings (if this enemy targets buildings)
        building_target = None
        if hasattr(self, 'targets_buildings') and self.targets_buildings:
            building_result = self.check_for_buildings()
            if building_result:
                building_target, building_distance = building_result
        
        # State transitions vary based on psychological state
        if player_detected:
            if self.psychology.state == PsychologicalState.NORMAL:
                # Normal enemies chase the player
                if self.current_state not in ["chase", "attack"]:
                    # If this enemy prioritizes buildings and one is in range, target it instead
                    if building_target and hasattr(self, 'building_priority') and self.building_priority > 0.5:
                        self.target = building_target
                        self.set_state("chase_building")
                    else:
                        self.set_state("chase")
            elif self.psychology.state == PsychologicalState.HESITANT:
                # Hesitant enemies sometimes chase, sometimes flee
                if self.current_state not in ["chase", "attack", "flee", "chase_building", "attack_building"]:
                    if random.random() < 0.7:  # 70% chance to chase
                        # If this enemy prioritizes buildings and one is in range, target it instead
                        if building_target and hasattr(self, 'building_priority') and self.building_priority > 0.5:
                            self.target = building_target
                            self.set_state("chase_building")
                        else:
                            self.set_state("chase")
                    else:
                        self.set_state("flee")
            elif self.psychology.state in [PsychologicalState.FEARFUL, PsychologicalState.TERRIFIED]:
                # Fearful/terrified enemies always flee
                if self.current_state != "flee":
                    self.set_state("flee")
        # Only check for buildings if player isn't detected or if this is a building-focused enemy
        elif building_target and hasattr(self, 'targets_buildings') and self.targets_buildings:
            # Target the building
            self.target = building_target
            if self.current_state not in ["chase_building", "attack_building"]:
                self.set_state("chase_building")
        elif self.current_state == "chase" and not player_detected:
            # If we lose track of the player, go back to idle/patrol
            self.set_state("idle")
            
        # Allow fleeing enemies to stop fleeing after some time has passed
        if self.current_state == "flee" and self.state_time > 10.0:  # After 10 seconds of fleeing
            if random.random() < 0.1:  # 10% chance per update
                self.set_state("idle")
    
    def apply_movement(self, dt):
        """Apply movement velocity to position with collision detection"""
        # Simple movement without collision for now
        self.position += self.velocity * dt
        
        # In a real implementation, we would check for collisions here
        # and adjust the position accordingly
    
    def set_state(self, new_state):
        """Set a new AI state"""
        self.current_state = new_state
        self.state_time = 0
        
        # Update target for chase/attack/flee states
        if new_state in ["chase", "attack", "flee"]:
            self.target = self.game.player
        # Building targeting states keep their existing target
    
    def generate_patrol_points(self):
        """Generate random patrol points around the current position"""
        self.patrol_points = []
        
        # Create 3-5 patrol points
        num_points = random.randint(3, 5)
        for i in range(num_points):
            # Random point within a reasonable distance
            radius = random.uniform(5, 15)
            angle = random.uniform(0, 2 * math.pi)
            
            x = self.position.x + radius * math.cos(angle)
            y = self.position.y + radius * math.sin(angle)
            z = 0  # Assuming flat terrain for now
            
            self.patrol_points.append(Vec3(x, y, z))
    
    def perform_attack(self):
        """Perform an attack on the player"""
        if not self.game.player:
            return
            
        # Calculate damage with psychological modifiers
        damage = self.damage * self.psychology.get_damage_modifier()
        
        if self.rally_active:
            # Rallied enemies do more damage
            damage *= 1.2
            
        # Apply damage to player
        distance = (self.game.player.position - self.position).length()
        if distance < self.attack_range:
            self.game.player.take_damage(damage)
            
            # Record damage in difficulty system if available
            if hasattr(self.game, 'adaptive_difficulty_system'):
                self.game.adaptive_difficulty_system.record_combat_event('damage_taken', damage)
            
            # Reset attack cooldown
            self.attack_cooldown = 1.0
            
            # If player is killed, record in difficulty system
            if self.game.player.health <= 0 and hasattr(self.game, 'adaptive_difficulty_system'):
                self.game.adaptive_difficulty_system.record_combat_event('player_death')
    
    def take_damage(self, amount):
        """Take damage from an attack"""
        # Apply the damage
        self.health -= amount
        
        # Update health bar
        if hasattr(self, 'health_bar'):
            self.health_bar.update_health(self.health / self.max_health)
        
        # Call psychology reaction
        if self.health > 0:
            self.psychology.react_to_damage(amount)
            self.react_to_damage()
        else:
            # Enemy died
            self.die()
            
            # Record enemy death in performance tracker if available
            if hasattr(self.game, 'performance_tracker'):
                self.game.performance_tracker.record_combat_event('enemy_killed')
            
            # Record enemy death in difficulty system if available
            if hasattr(self.game, 'adaptive_difficulty_system'):
                self.game.adaptive_difficulty_system.record_combat_event('enemy_killed')
    
    def react_to_damage(self):
        """React to being damaged"""
        # If confidence is low, might flee when taking damage
        if self.psychology.confidence < 0.5 and random.random() < 0.7:
            self.set_state("flee")
        else:
            # Otherwise, switch to chase or attack
            if not self.target:
                # Try to find who damaged us
                if hasattr(self.game, 'player'):
                    self.target = self.game.player
            
            if self.target:
                distance = (self.target.position - self.position).length()
                if distance < self.attack_range:
                    self.set_state("attack")
                else:
                    self.set_state("chase")
    
    def die(self):
        """Handle enemy death"""
        # Drop resources
        self.drop_resources()
        
        # Drop experience
        self.drop_experience()
        
        # Remove from entity manager
        if hasattr(self.game, 'entity_manager'):
            self.game.entity_manager.remove_entity(self)
        
        # Remove health bar
        if hasattr(self, 'health_bar'):
            self.health_bar.remove()
        
        # Remove model
        if hasattr(self, 'root'):
            self.root.removeNode()
            
        print(f"{self.__class__.__name__} defeated!")
    
    def drop_resources(self):
        """Drop resources when killed"""
        if random.random() < self.drop_chance:
            # Determine how many types of resources to drop
            num_types = random.randint(1, min(2, len(self.possible_drops)))
            
            # Randomly select resource types
            drop_types = random.sample(self.possible_drops, num_types)
            
            # Apply difficulty adjustment to drop amounts if available
            drop_multiplier = 1.0
            if hasattr(self.game, 'adaptive_difficulty_system'):
                factors = self.game.adaptive_difficulty_system.get_current_difficulty_factors()
                drop_multiplier = factors['resource_drop']
            
            # Drop each selected resource type
            for resource_type in drop_types:
                # Get the base amount range
                min_amount, max_amount = self.drop_amounts.get(resource_type, (1, 1))
                
                # Calculate drop amount with multiplier
                # Higher resource_drop means more resources
                amount = random.randint(min_amount, max_amount)
                if drop_multiplier > 1.0:
                    # Add chance for extra resources when multiplier is high
                    extra_chance = drop_multiplier - 1.0  # e.g., 1.3 gives 30% chance
                    if random.random() < extra_chance:
                        amount += 1
                
                # Create the resource drop
                if hasattr(self.game, 'entity_manager'):
                    self.game.entity_manager.create_resource_drop(
                        resource_type, amount, self.position)
                    
                    # Record resource drop in performance tracker if available
                    if hasattr(self.game, 'performance_tracker'):
                        self.game.performance_tracker.record_resource_event(
                            resource_type, amount, source="enemy_drop")
    
    def drop_experience(self):
        """Drop experience points upon death"""
        # Add some randomization to experience (±20%)
        variance = self.experience_value * 0.2
        exp_amount = round(self.experience_value + random.uniform(-variance, variance))
        exp_amount = max(1, exp_amount)  # Ensure at least 1 XP
        
        # Create the experience drop
        if hasattr(self.game, 'entity_manager'):
            self.game.entity_manager.create_resource_drop(
                self.position,
                "experience",
                exp_amount
            )
        else:
            drop = ResourceDrop(
                self.game,
                self.position,
                "experience",
                exp_amount
            )
            # Add to game entities list if it exists
            if hasattr(self.game, 'entities'):
                self.game.entities.append(drop)
    
    @property
    def confidence(self):
        """Property for backwards compatibility"""
        return self.psychology.confidence
        
    @confidence.setter
    def confidence(self, value):
        """Setter for backwards compatibility"""
        self.psychology.confidence = value

    def ally_died(self, ally):
        """
        React to an ally dying nearby
        
        Args:
            ally: The ally that died
        """
        if hasattr(self, 'psychology'):
            self.psychology.record_ally_defeated()
            
        # Visual or audio effect could be added here
        
        # Potentially change state based on psychological impact
        if self.psychology.confidence < 0.3:
            self.set_state("flee")


class BasicEnemy(Enemy):
    """Basic melee enemy"""
    
    def __init__(self, game, position=Vec3(0, 0, 0)):
        """Initialize basic enemy"""
        # Set psychological traits before parent init
        self.psychology_traits = {
            'bravery': random.uniform(0.9, 1.1),
            'aggression': random.uniform(0.9, 1.1),
            'intelligence': random.uniform(0.8, 1.0),
            'pack_mentality': random.uniform(1.0, 1.2),
            'dominance': random.uniform(0.8, 1.0)
        }
        
        super().__init__(game, position)
        
        # Override stats
        self.max_health = 50
        self.health = 50
        self.speed = 3.0
        self.damage = 10
        self.attack_range = 1.5
        self.detection_range = 10.0
        
        # Set model color
        if hasattr(self, 'model'):
            self.model.setColor(0.8, 0.2, 0.2, 1)  # Red


class RangedEnemy(Enemy):
    """Ranged attack enemy"""
    
    def __init__(self, game, position=Vec3(0, 0, 0)):
        """Initialize ranged enemy"""
        # Set psychological traits before parent init
        self.psychology_traits = {
            'bravery': random.uniform(0.7, 0.9),
            'aggression': random.uniform(0.8, 1.0),
            'intelligence': random.uniform(1.0, 1.2),
            'pack_mentality': random.uniform(0.8, 1.0),
            'dominance': random.uniform(0.8, 1.0)
        }
        
        super().__init__(game, position)
        
        # Override stats
        self.max_health = 40
        self.health = 40
        self.speed = 2.5
        self.damage = 15
        self.attack_range = 8.0  # Longer attack range
        self.detection_range = 12.0
        
        # Set model color
        if hasattr(self, 'model'):
            self.model.setColor(0.2, 0.2, 0.8, 1)  # Blue
    
    def perform_attack(self):
        """Perform ranged attack"""
        if not self.game.player:
            return False
            
        # Only attack if we should based on psychological state
        if not self.psychology.should_attack_player():
            return False
            
        # Create and launch projectile
        from game.projectile import Projectile
        
        # Calculate direction to player
        direction = self.game.player.position - self.position
        direction.normalize()
        
        # Apply psychological damage modifier
        damage = self.damage * self.psychology.get_effective_damage()
        
        # Create projectile
        projectile = Projectile(
            self.game,
            self.position + Vec3(0, 0, 0.5),  # Slight height offset
            direction,
            damage,
            10.0,  # Speed
            "enemy",
            "straight"
        )
        
        # Add to entity manager
        self.game.entity_manager.projectiles.append(projectile)
        
        # Reset attack cooldown
        self.attack_cooldown = 2.0
        
        return True


class AlphaEnemy(BasicEnemy):
    """Alpha leader enemy with pack mentality enhancements"""
    
    def __init__(self, game, position=Vec3(0, 0, 0)):
        """Initialize alpha enemy"""
        # Set psychological traits before parent init - high dominance makes it an alpha
        self.psychology_traits = {
            'bravery': random.uniform(1.2, 1.4),
            'aggression': random.uniform(1.1, 1.3),
            'intelligence': random.uniform(1.1, 1.3),
            'pack_mentality': random.uniform(1.2, 1.4),
            'dominance': random.uniform(1.3, 1.5)  # High dominance makes it an alpha
        }
        
        super().__init__(game, position)
        
        # Override stats - stronger than basic enemies
        self.max_health = 80
        self.health = 80
        self.speed = 3.2
        self.damage = 15
        self.attack_range = 1.8
        self.detection_range = 12.0
        
        # Set model color and scale
        if hasattr(self, 'model'):
            self.model.setColor(0.9, 0.4, 0.1, 1)  # Orange
            self.model.setScale(0.7, 0.7, 1.4)  # Larger than regular enemies
            
        # Experience value is higher
        self.experience_value = 25
        
        # Resource drops are better
        self.drop_chance = 0.9
        self.drop_amounts = {
            "wood": (2, 4),
            "stone": (2, 3),
            "crystal": (1, 2),
            "herb": (2, 3)
        }


class NimbleEnemy(Enemy):
    """Fast, evasive enemy that uses intelligence to avoid direct combat"""
    
    def __init__(self, game, position=Vec3(0, 0, 0)):
        """Initialize nimble enemy"""
        # Set psychological traits before parent init
        self.psychology_traits = {
            'bravery': random.uniform(0.8, 1.0),
            'aggression': random.uniform(0.7, 0.9),
            'intelligence': random.uniform(1.3, 1.5),  # Very intelligent
            'pack_mentality': random.uniform(0.6, 0.8),  # Less pack-oriented
            'dominance': random.uniform(0.7, 0.9)
        }
        
        super().__init__(game, position)
        
        # Override stats - faster but weaker
        self.base_max_health = 35
        self.base_speed = 4.5  # Much faster
        self.base_damage = 8
        
        # Apply difficulty adjustment
        self.apply_difficulty_adjustment()
        
        self.attack_range = 1.2
        self.detection_range = 14.0  # Good awareness
        
        # Set model color
        if hasattr(self, 'model'):
            self.model.setColor(0.2, 0.8, 0.2, 1)  # Green
            self.model.setScale(0.4, 0.4, 0.9)  # Smaller, lankier
    
    def update_flee_state(self, dt):
        """Enhanced flee behavior for nimble enemies"""
        player = self.game.player
        if not player:
            self.set_state("idle")
            return
        
        # Get direction away from player
        direction = self.position - player.position
        distance = direction.length()
        
        if distance > self.detection_range * 1.5:
            # Far enough away, transition to patrol
            self.set_state("patrol")
            return
            
        # Move away from player with erratic movement
        if direction.length() > 0:
            direction.normalize()
            
            # Add randomization to direction for erratic movement
            if random.random() < 0.2:  # 20% chance per update
                random_angle = random.uniform(-90, 90)  # -90 to 90 degrees
                rad_angle = math.radians(random_angle)
                cos_angle = math.cos(rad_angle)
                sin_angle = math.sin(rad_angle)
                
                # Rotate direction
                new_x = direction.x * cos_angle - direction.y * sin_angle
                new_y = direction.x * sin_angle + direction.y * cos_angle
                direction = Vec3(new_x, new_y, 0)
                direction.normalize()
            
            # Set velocity away from player with enhanced speed when fleeing
            speed_boost = 1.3  # 30% faster when fleeing
            self.velocity = direction * self.speed * self.psychology.get_effective_speed() * speed_boost
            
            # Face away from player
            self.facing_angle = math.degrees(math.atan2(-direction.x, direction.y))


class BruteEnemy(Enemy):
    """Heavy, tough enemy with high aggression but lower intelligence"""
    
    def __init__(self, game, position=Vec3(0, 0, 0)):
        """Initialize brute enemy"""
        # Set psychological traits before parent init
        self.psychology_traits = {
            'bravery': random.uniform(1.2, 1.4),  # Very brave
            'aggression': random.uniform(1.3, 1.5),  # Highly aggressive
            'intelligence': random.uniform(0.5, 0.7),  # Lower intelligence
            'pack_mentality': random.uniform(0.7, 0.9),  # Less pack-oriented
            'dominance': random.uniform(1.1, 1.3)  # Fairly dominant
        }
        
        super().__init__(game, position)
        
        # Override stats - slower but much stronger
        self.max_health = 120
        self.health = 120
        self.speed = 2.0  # Slower
        self.damage = 25  # High damage
        self.attack_range = 2.0  # Longer reach
        self.detection_range = 8.0  # Less awareness
        
        # Set model color and scale
        if hasattr(self, 'model'):
            self.model.setColor(0.6, 0.1, 0.1, 1)  # Dark red
            self.model.setScale(0.9, 0.9, 1.8)  # Much larger
            
        # Experience value is higher
        self.experience_value = 20
        
        # Resource drops are better
        self.drop_chance = 0.8
        self.drop_amounts = {
            "wood": (3, 5),
            "stone": (3, 4),
            "crystal": (1, 2),
            "herb": (1, 2)
        }
    
    def perform_attack(self):
        """Stronger but slower attack"""
        if not self.game.player:
            return False
            
        # Only attack if we should based on psychological state
        if not self.psychology.should_attack_player():
            return False
            
        # Apply psychological damage modifier
        damage = self.damage * self.psychology.get_effective_damage()
        
        # Apply damage to player
        if hasattr(self.game.player, 'take_damage'):
            self.game.player.take_damage(damage)
            
            # Visual feedback
            if hasattr(self.game, 'camera_controller'):
                shake_amount = min(0.5, damage / 20.0)  # Cap at 0.5
                self.game.camera_controller.shake(shake_amount, 0.3)
        
        # Reset attack cooldown - longer for brutes
        self.attack_cooldown = 3.0
        
        return True


# Factory function to create different enemy types
def create_enemy(game, enemy_type, position=Vec3(0, 0, 0)):
    """
    Factory function to create enemies of different types
    
    Args:
        game: Game instance
        enemy_type: Type of enemy to create ("basic", "ranged", "alpha", "nimble", "brute", or "raider")
        position: Initial position for the enemy
        
    Returns:
        Enemy: The created enemy instance
    """
    if enemy_type == "basic":
        return BasicEnemy(game, position)
    elif enemy_type == "ranged":
        return RangedEnemy(game, position)
    elif enemy_type == "alpha":
        return AlphaEnemy(game, position)
    elif enemy_type == "nimble":
        return NimbleEnemy(game, position)
    elif enemy_type == "brute":
        return BruteEnemy(game, position)
    elif enemy_type == "raider":
        return BuildingRaider(game, position)
    else:
        # Default to basic enemy
        print(f"Unknown enemy type '{enemy_type}', defaulting to basic enemy")
        return BasicEnemy(game, position)

# Add a new class for building raiders that specialize in attacking buildings
class BuildingRaider(Enemy):
    """Enemy that prioritizes attacking buildings over the player"""
    
    def __init__(self, game, position=Vec3(0, 0, 0)):
        """Initialize the building raider enemy"""
        super().__init__(game, position)
        
        # Set the enemy's name
        self.name = "Building Raider"
        
        # Mark this enemy type as targeting buildings
        self.targets_buildings = True
        
        # Higher priority for buildings (1.0 = always target buildings if available)
        self.building_priority = 0.9
        
        # Custom stats for building raiders
        self.base_max_health = 60
        self.base_speed = 3.5
        self.base_damage = 15  # More damage to buildings
        
        # Apply difficulty adjustment
        self.apply_difficulty_adjustment()
        
        # Set the health to max
        self.health = self.max_health
        
        # Special building damage bonus
        self.building_damage_multiplier = 1.5  # 50% more damage to buildings
        
        # Update model color to distinguish from other enemies
        if hasattr(self, 'model'):
            self.model.setColor(0.8, 0.4, 0.1, 1)  # Orange-brown for raiders
    
    def attack_building(self):
        """Raiders do extra damage to buildings"""
        if not self.target or not hasattr(self.game, 'city_manager'):
            return
            
        # Calculate damage with psychological modifiers and building bonus
        damage = self.damage * self.psychology.get_damage_modifier() * self.building_damage_multiplier
        
        if self.rally_active:
            # Rallied enemies do more damage
            damage *= 1.2
            
        # Apply damage to building
        self.game.city_manager.damage_building(self.target, damage, self)
        
        # Reset attack cooldown
        self.attack_cooldown = 1.2  # Faster attacks on buildings than normal enemies
        
        # Create attack animation/effect if available
        if hasattr(self.game, 'effect_manager'):
            building_pos = Vec3(*self.game.city_manager.grid_to_world(self.target.position))
            self.game.effect_manager.create_effect("building_attack", self.position, building_pos) 