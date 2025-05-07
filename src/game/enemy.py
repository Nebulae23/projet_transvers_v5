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
        
        # Enemy stats (override in subclasses)
        self.max_health = 50
        self.health = 50
        self.speed = 3.0  # Units per second
        self.damage = 10  # Damage dealt on contact
        self.attack_range = 1.5  # Units
        self.detection_range = 10.0  # Units
        self.collision_radius = 0.5
        
        # AI state
        self.current_state = "idle"  # idle, patrol, chase, attack, flee
        self.target = None
        self.patrol_points = []
        self.current_patrol_index = 0
        self.state_time = 0  # Time in current state
        
        # Initialize psychological system
        self.psychology = EnemyPsychology(self)
        
        # Action cooldowns
        self.attack_cooldown = 0
        
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
    
    def setup_model(self):
        """Set up the enemy model"""
        # For now, just use a box as placeholder
        try:
            self.model = self.game.loader.loadModel("models/box")
            self.model.setScale(0.5, 0.5, 1.0)  # Enemy dimensions
            self.model.reparentTo(self.root)
            
            # Color the box for visibility
            self.model.setColor(0.8, 0.2, 0.2, 1)  # Red color for enemy
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
        """Update the enemy state"""
        # Update psychological state
        self.psychology.update(dt)
        
        # Update state timer
        self.state_time += dt
        
        # Update cooldowns
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt
        
        # Check if in subservient state
        if self.psychology.state == PsychologicalState.SUBSERVIENT:
            self.update_subservient_state(dt)
        else:
            # Update AI based on current state with psychological influence
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
        
        # Check for state transitions (with psychological influence)
        self.check_state_transitions()
        
        # Apply movement
        self.apply_movement(dt)
        
        # Update the model position
        self.root.setPos(self.position)
        self.root.setH(self.facing_angle)
        
        # Update debug visualization if needed
        if hasattr(self.game, 'debug_mode') and self.game.debug_mode:
            self.draw_debug_visualization()
        
        # Update the health bar
        if hasattr(self, 'health_bar'):
            self.health_bar.update(dt)
    
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
        """Update behavior in chase state"""
        # Check if we should flee based on psychological state
        if self.psychology.state in [PsychologicalState.FEARFUL, PsychologicalState.TERRIFIED]:
            self.set_state("flee")
            return
            
        if not self.target or not hasattr(self.target, 'position'):
            self.set_state("idle")
            return
            
        # Move towards the target
        direction = self.target.position - self.position
        distance = direction.length()
        
        # If we're in range to attack, transition to attack state
        if distance < self.attack_range and self.psychology.should_attack_player():
            self.set_state("attack")
        else:
            # Move towards the target with psychological speed
            direction.normalize()
            self.velocity = direction * self.psychology.get_effective_speed()
            
            # If hesitant, occasionally pause
            if self.psychology.state == PsychologicalState.HESITANT and random.random() < 0.1:
                self.velocity = Vec3(0, 0, 0)
                
            # Set facing direction
            self.facing_angle = -math.degrees(math.atan2(direction.x, direction.y))
    
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
        """Update behavior in flee state"""
        # If confidence is restored, stop fleeing
        if self.psychology.state in [PsychologicalState.NORMAL, PsychologicalState.HESITANT]:
            self.set_state("idle")
            return
            
        if not self.target or not hasattr(self.target, 'position'):
            self.set_state("idle")
            return
            
        # Move away from the target
        direction = self.position - self.target.position
        distance = direction.length()
        
        # If we're far enough away, go back to idle
        if distance > self.detection_range * 1.5:
            self.set_state("idle")
            return
            
        # Move away from the target
        direction.normalize()
        
        # Use psychological speed for fleeing (terrified enemies flee faster)
        self.velocity = direction * self.psychology.get_effective_speed()
        
        # Set facing direction (looking back at target while fleeing)
        self.facing_angle = -math.degrees(math.atan2(-direction.x, -direction.y))
    
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
    
    def check_state_transitions(self):
        """Check for state transitions based on circumstances and psychological state"""
        # Skip if in subservient state (handled separately)
        if self.psychology.state == PsychologicalState.SUBSERVIENT:
            return
            
        # Check for player in detection range - with day/night visibility modifier
        player_detected = self.check_immediate_threat()
        
        # State transitions vary based on psychological state
        if player_detected:
            if self.psychology.state == PsychologicalState.NORMAL:
                # Normal enemies chase the player
                if self.current_state not in ["chase", "attack"]:
                    self.set_state("chase")
            elif self.psychology.state == PsychologicalState.HESITANT:
                # Hesitant enemies sometimes chase, sometimes flee
                if self.current_state not in ["chase", "attack", "flee"]:
                    if random.random() < 0.7:  # 70% chance to chase
                        self.set_state("chase")
                    else:
                        self.set_state("flee")
            elif self.psychology.state in [PsychologicalState.FEARFUL, PsychologicalState.TERRIFIED]:
                # Fearful/terrified enemies always flee
                if self.current_state != "flee":
                    self.set_state("flee")
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
        """Perform an attack action"""
        if not self.target:
            return
            
        # Deal damage to the target
        if hasattr(self.target, 'take_damage'):
            # Apply psychological damage modifier
            damage = self.psychology.get_effective_damage()
            self.target.take_damage(damage)
            
        # Reset cooldown
        self.attack_cooldown = 1.0  # 1 second between attacks
    
    def take_damage(self, amount):
        """Take damage from an attack"""
        self.health -= amount
        
        # Update the health bar
        if hasattr(self, 'health_bar'):
            self.health_bar.set_health_ratio(self.health / self.max_health)
            
        # Check for death
        if self.health <= 0:
            self.die()
        else:
            # Potentially update psychological state based on damage
            # Getting hit reduces confidence
            current_confidence = self.psychology.confidence
            damage_ratio = amount / self.max_health
            confidence_reduction = damage_ratio * 0.5  # Reduce confidence by up to 50% of damage ratio
            self.psychology.confidence = max(0.0, current_confidence - confidence_reduction)
            
            # React to being damaged
            self.react_to_damage()
    
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
        """Drop resources upon death"""
        # Choose a random resource type to drop
        resource_type = random.choice(self.possible_drops)
        
        # Determine amount based on enemy type
        min_amount, max_amount = self.drop_amounts.get(resource_type, (1, 1))
        amount = random.randint(min_amount, max_amount)
        
        # Create the resource drop
        if hasattr(self.game, 'entity_manager'):
            self.game.entity_manager.create_resource_drop(
                self.position,
                resource_type,
                amount
            )
        else:
            drop = ResourceDrop(
                self.game,
                self.position,
                resource_type,
                amount
            )
            # Add to game entities list if it exists
            if hasattr(self.game, 'entities'):
                self.game.entities.append(drop)
    
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


class BasicEnemy(Enemy):
    """Simple melee enemy that chases the player"""
    
    def __init__(self, game, position=Vec3(0, 0, 0)):
        super().__init__(game, position)
        
        # Override base stats
        self.max_health = 40
        self.health = 40
        self.speed = 3.5
        self.damage = 8
        self.detection_range = 12.0
        self.attack_range = 1.2
        
        # Override model appearance
        if hasattr(self, 'model') and not self.model.isEmpty():
            self.model.setColor(0.7, 0.2, 0.2, 1)  # Darker red
        
        # Modify drop chances for basic enemy
        self.drop_chance = 0.6
        self.experience_value = 8


class RangedEnemy(Enemy):
    """Ranged enemy that attacks from a distance"""
    
    def __init__(self, game, position=Vec3(0, 0, 0)):
        super().__init__(game, position)
        
        # Override base stats
        self.max_health = 30
        self.health = 30
        self.speed = 2.8
        self.damage = 12
        self.detection_range = 15.0
        self.attack_range = 8.0  # Much larger attack range
        
        # Override model appearance
        if hasattr(self, 'model') and not self.model.isEmpty():
            self.model.setColor(0.2, 0.2, 0.7, 1)  # Blue color
        
        # Modify drop chances for ranged enemy
        self.drop_chance = 0.75
        self.experience_value = 12
        
        # Ranged enemies have better chance of dropping crystals
        self.possible_drops = ["wood", "stone", "crystal", "crystal", "herb"]
    
    def perform_attack(self):
        """Perform a ranged attack by firing a projectile"""
        self.attack_cooldown = 1.5  # Longer cooldown for ranged attacks
        
        if not self.target or not hasattr(self.target, 'position'):
            return
        
        print(f"Ranged enemy firing projectile!")
        
        # Calculate direction to target
        direction = self.target.position - self.position
        direction.normalize()
        
        # Spawn a projectile
        try:
            from game.projectile import StraightProjectile
            
            # Create projectile slightly in front of the enemy
            spawn_pos = self.position + direction * 0.7
            spawn_pos.z += 0.5  # Raise projectile to mid-body level
            
            projectile = StraightProjectile(
                self.game,
                spawn_pos,
                direction,
                owner=self
            )
            
            # Add to game projectiles list if it exists
            if hasattr(self.game, 'projectiles'):
                self.game.projectiles.append(projectile)
            
            # Or add to entities list
            elif hasattr(self.game, 'entities'):
                self.game.entities.append(projectile)
        except ImportError:
            # Fallback if projectile module is not available
            if hasattr(self.target, 'take_damage'):
                # Direct damage with damage falloff based on distance
                distance = (self.target.position - self.position).length()
                damage_factor = 1.0 - (distance / self.attack_range) * 0.5
                actual_damage = max(1, int(self.damage * damage_factor))
                self.target.take_damage(actual_damage) 