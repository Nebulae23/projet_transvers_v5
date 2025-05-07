#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Player entity module for Nightfall Defenders
"""

from panda3d.core import NodePath, Vec3, KeyboardButton, MouseButton
from direct.actor.Actor import Actor
import math

class Player:
    """Player entity with movement, combat, and inventory systems"""
    
    def __init__(self, game):
        """Initialize the player entity"""
        self.game = game
        
        # Create the player node
        self.root = NodePath("Player")
        self.root.reparentTo(game.render)
        
        # Player state
        self.position = Vec3(0, 0, 0)
        self.velocity = Vec3(0, 0, 0)
        self.facing_angle = 0  # In degrees
        
        # Player stats
        self.max_health = 100
        self.health = 100
        self.max_stamina = 100
        self.stamina = 100
        self.speed = 5.0  # Units per second
        self.dodge_speed = 12.0  # Dodge boost
        
        # Experience and level system
        self.level = 1
        self.experience = 0
        self.experience_to_next_level = 100  # Base XP needed for level 2
        
        # Action states
        self.is_attacking = False
        self.is_dodging = False
        self.is_interacting = False
        
        # Cooldowns (in seconds)
        self.dodge_cooldown = 0
        self.attack_cooldown = 0
        
        # Projectile settings
        self.projectile_type = "straight"  # Default projectile type
        self.setup_projectile_types()
        
        # Load the player model
        self.setup_model()
        
        # Set up collision detection
        self.setup_collision()
        
        # Debug visualization
        self.debug_node = self.root.attachNewNode("PlayerDebug")
        self.draw_debug_visualization()
        
        # Setup key listeners for projectile switching
        self.setup_projectile_keys()
        
        # Inventory
        self.inventory = {
            "wood": 0,
            "stone": 0,
            "crystal": 0,
            "herb": 0
        }
        
        # Relic system properties
        self.damage_reduction = 0.0
        self.last_damage_dealt = 0
        
        # Movement input state
        self.movement_keys = [False, False, False, False]  # W, S, A, D
    
    def setup_model(self):
        """Set up the player model"""
        # For now, just use a box as placeholder
        # In the future, this would load a proper character model
        try:
            self.model = self.game.loader.loadModel("models/box")
            self.model.setScale(0.5, 0.5, 1.0)  # Character dimensions
            self.model.reparentTo(self.root)
            
            # Color the box for visibility
            self.model.setColor(0.2, 0.4, 0.8, 1)  # Blue color
        except Exception as e:
            print(f"Error loading player model: {e}")
            # Fallback to a simple marker
            from panda3d.core import PointLight
            plight = PointLight("PlayerMarker")
            plight.setColor((1, 0, 0, 1))
            plnp = self.root.attachNewNode(plight)
            plnp.setPos(0, 0, 1)
    
    def setup_collision(self):
        """Set up collision detection for the player"""
        # This would normally set up proper collision geometry
        # For now, we'll just use a simple representation
        self.collision_radius = 0.5
    
    def draw_debug_visualization(self):
        """Draw debug visualization for the player"""
        # Clear any existing debug visualization
        self.debug_node.removeNode()
        self.debug_node = self.root.attachNewNode("PlayerDebug")
        
        # Only draw debug visuals if debug mode is enabled
        if hasattr(self.game, 'debug_mode') and self.game.debug_mode:
            # Draw facing direction indicator
            from panda3d.core import LineSegs
            segs = LineSegs()
            segs.setColor(1, 0, 0, 1)  # Red
            segs.moveTo(0, 0, 0.1)  # Slightly above ground
            segs.drawTo(0, 1.5, 0.1)  # Forward direction
            self.debug_node.attachNewNode(segs.create())
            
            # Draw collision radius
            segs = LineSegs()
            segs.setColor(0, 1, 0, 1)  # Green
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
    
    def update(self, dt):
        """Update the player state"""
        # Handle input for movement
        self.process_movement_input(dt)
        
        # Handle input for actions
        self.process_action_input(dt)
        
        # Update cooldowns
        self.update_cooldowns(dt)
        
        # Apply movement
        self.apply_movement(dt)
        
        # Update the model position
        self.root.setPos(self.position)
        self.root.setH(self.facing_angle)
        
        # Update debug visualization if needed
        if hasattr(self.game, 'debug_mode') and self.game.debug_mode:
            self.draw_debug_visualization()
    
    def set_moving(self, is_pressed, direction):
        """
        Set the movement state for a specific direction
        
        Args:
            is_pressed (bool): Whether the key is pressed
            direction (int): Direction index (0=forward, 1=backward, 2=left, 3=right)
        """
        if direction >= 0 and direction < 4:
            self.movement_keys[direction] = is_pressed
    
    def process_movement_input(self, dt):
        """Process movement input from the player"""
        # Create movement vector from key state
        move_x = 0
        move_y = 0
        
        # Apply movement based on active keys
        if self.movement_keys[0]:  # W - forward
            move_y += 1
        if self.movement_keys[1]:  # S - backward
            move_y -= 1
        if self.movement_keys[2]:  # A - left
            move_x -= 1
        if self.movement_keys[3]:  # D - right
            move_x += 1
            
        # Convert to 3D vector (we're in a 3D space, but moving on XY plane)
        input_vector = Vec3(move_x, move_y, 0)
        
        # Normalize if not zero
        if input_vector.length() > 0:
            input_vector.normalize()
            
            # Set facing direction based on movement (optional)
            if input_vector.length() > 0:
                # Calculate angle in degrees using math module
                self.facing_angle = -math.degrees(math.atan2(input_vector[0], input_vector[1]))
        
        # Apply movement speed
        current_speed = self.dodge_speed if self.is_dodging else self.speed
        self.velocity = input_vector * current_speed
    
    def process_action_input(self, dt):
        """Process action inputs from the player"""
        # This method is kept for compatibility, but actual actions
        # are now triggered directly by key bindings

        # Update is_interacting flag based on interaction cooldown
        if hasattr(self, 'interaction_cooldown') and self.interaction_cooldown > 0:
            self.interaction_cooldown -= dt
            if self.interaction_cooldown <= 0:
                self.is_interacting = False
    
    def primary_attack(self):
        """Handle primary attack action"""
        if not self.is_attacking and self.attack_cooldown <= 0:
            self.start_attack()
    
    def secondary_attack(self):
        """Handle secondary attack (change projectile type)"""
        # Cycle through projectile types
        current_types = list(self.projectile_types.keys())
        current_index = current_types.index(self.projectile_type)
        next_index = (current_index + 1) % len(current_types)
        self.set_projectile_type(current_types[next_index])
    
    def dodge(self):
        """Handle dodge action"""
        if not self.is_dodging and self.dodge_cooldown <= 0:
            self.start_dodge()
    
    def interact(self):
        """Handle interact action"""
        if not self.is_interacting:
            self.interact_with_world()
    
    def update_cooldowns(self, dt):
        """Update action cooldowns"""
        if self.dodge_cooldown > 0:
            self.dodge_cooldown -= dt
        
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt
            
        # End dodge state if cooldown is finished
        if self.is_dodging and self.dodge_cooldown <= 0.8:  # Dodge lasts for 0.2s
            self.is_dodging = False
    
    def apply_movement(self, dt):
        """Apply movement velocity to position with collision detection"""
        # Simple movement without collision for now
        self.position += self.velocity * dt
        
        # In a real implementation, we would check for collisions here
        # and adjust the position accordingly
    
    def setup_projectile_types(self):
        """Setup different projectile types and their properties"""
        self.projectile_types = {
            "straight": {
                "name": "Straight Shot",
                "cooldown": 0.5,
                "color": (0.2, 0.8, 1),
                "damage": 10
            },
            "arcing": {
                "name": "Arcing Shot",
                "cooldown": 1.0,
                "color": (1, 0.4, 0.1),
                "damage": 12
            },
            "spiral": {
                "name": "Spiral Shot",
                "cooldown": 1.5,
                "color": (0.2, 1, 0.2),
                "damage": 14
            },
            "homing": {
                "name": "Homing Shot",
                "cooldown": 2.0,
                "color": (0.8, 0.1, 0.8),
                "damage": 16
            }
        }
        
    def setup_projectile_keys(self):
        """Setup key listeners for projectile type switching"""
        self.game.accept("1", self.set_projectile_type, ["straight"])
        self.game.accept("2", self.set_projectile_type, ["arcing"])
        self.game.accept("3", self.set_projectile_type, ["spiral"])
        self.game.accept("4", self.set_projectile_type, ["homing"])
        
        # Show initial projectile type
        self.show_projectile_type()
        
    def set_projectile_type(self, projectile_type):
        """Change the current projectile type"""
        if projectile_type in self.projectile_types:
            self.projectile_type = projectile_type
            self.show_projectile_type()
            
            # Update the weapon text in the main game if it exists
            if hasattr(self.game, 'weapon_text'):
                projectile_info = self.projectile_types[projectile_type]
                key_number = {"straight": "1", "arcing": "2", "spiral": "3", "homing": "4"}
                self.game.weapon_text.setText(f"Current Weapon: {projectile_info['name']} ({key_number.get(projectile_type, '')})")
    
    def show_projectile_type(self):
        """Display the current projectile type to the player"""
        if self.projectile_type in self.projectile_types:
            projectile_info = self.projectile_types[self.projectile_type]
            print(f"Switched to {projectile_info['name']} projectile")
            
            # Change the player's color to match the projectile type
            if hasattr(self, 'model') and not self.model.isEmpty():
                self.model.setColor(*projectile_info['color'], 1)
    
    def start_attack(self):
        """Start an attack action"""
        self.is_attacking = True
        
        # Set cooldown based on projectile type
        self.attack_cooldown = self.projectile_types[self.projectile_type]["cooldown"]
        
        # Get direction based on player facing
        direction = Vec3(
            -math.sin(math.radians(self.facing_angle)),
            math.cos(math.radians(self.facing_angle)),
            0
        )
        
        # Alternatively, if we have a mouse position, shoot toward mouse
        if self.game.mouseWatcherNode.hasMouse():
            try:
                # Get 2D mouse position
                mouse_pos = self.game.mouseWatcherNode.getMouse()
                
                # Convert to 3D position using the ground plane
                ground_pos = self.game.calculate_ground_point_at_mouse(mouse_pos)
                
                if ground_pos:
                    # Calculate direction from player to ground position
                    direction = ground_pos - self.position
                    direction.z = 0  # Keep projectile flat on XY plane
                    if direction.length() > 0:
                        direction.normalize()
            except Exception as e:
                print(f"Error calculating mouse direction: {e}")
        
        # Create the projectile
        if hasattr(self.game, 'entity_manager'):
            # Get projectile parameters
            projectile_params = self.projectile_types[self.projectile_type].copy()
            
            # Damage modification from relics
            if hasattr(self, 'damage_multiplier') and self.damage_multiplier != 1.0:
                projectile_params["damage"] *= self.damage_multiplier
            
            # Calculate starting position (slightly in front of player)
            start_pos = self.position + direction * 0.7
            start_pos.z = 0.5  # Adjust height
            
            # Create projectile through entity manager
            projectile_type = self.projectile_type
            damage = projectile_params.get("damage", 10)
            
            self.game.entity_manager.create_projectile(
                projectile_type, 
                start_pos, 
                direction, 
                owner=self, 
                damage=damage
            )
            
            # Reset last damage dealt
            self.last_damage_dealt = 0
            
            print(f"Player attacks with {projectile_type}!")
        
        # End the attack state after a delay
        self.game.taskMgr.doMethodLater(0.1, self.end_attack, "EndAttack")
    
    def end_attack(self, task):
        """End the attack state"""
        self.is_attacking = False
        return task.done
    
    def start_dodge(self):
        """Start a dodge action"""
        self.is_dodging = True
        self.dodge_cooldown = 1.0  # 1 second cooldown
        
        # Apply a quick boost in the current movement direction
        # The actual boost is applied in process_movement_input
        print("Player dodged!")
    
    def interact_with_world(self):
        """Interact with nearby objects in the world"""
        self.is_interacting = True
        
        # Find nearby interactable objects
        if hasattr(self.game, 'entity_manager'):
            # Get all nearby interactables within interaction radius
            interaction_radius = 2.0
            found_interaction = False
            
            # Check for nearby interactables first
            if hasattr(self.game.entity_manager, 'get_nearby_interactables'):
                nearby_interactables = self.game.entity_manager.get_nearby_interactables(
                    self.position, interaction_radius
                )
                
                if nearby_interactables:
                    # Find the closest interactable
                    closest_interactable = min(
                        nearby_interactables, 
                        key=lambda obj: (obj.position - self.position).length()
                    )
                    
                    # Interact with it if it has an interact method
                    if hasattr(closest_interactable, 'interact'):
                        closest_interactable.interact(self)
                        found_interaction = True
            
            # If no interactable found, try resource nodes
            if not found_interaction:
                nearby_entities = self.game.entity_manager.get_nearby_entities(
                    self.position, interaction_radius
                )
                
                # Find the closest resource node
                resource_nodes = [
                    entity for entity in nearby_entities 
                    if hasattr(entity, 'resource_type') and entity != self
                ]
                
                if resource_nodes:
                    closest_node = min(
                        resource_nodes, 
                        key=lambda node: (node.position - self.position).length()
                    )
                    
                    # Gather from the resource node
                    resources = closest_node.gather(self)
                    
                    if resources:
                        # Add to inventory
                        resource_type = resources["type"]
                        amount = resources["amount"]
                        self.inventory[resource_type] = self.inventory.get(resource_type, 0) + amount
                        
                        # Track resource collection stats
                        if hasattr(self.game.entity_manager, 'add_resource_collection'):
                            self.game.entity_manager.add_resource_collection(resource_type, amount)
                        
                        # Show a message about what was gathered
                        if hasattr(self.game, 'show_message'):
                            self.game.show_message(f"Gathered {amount} {resource_type}")
                        else:
                            print(f"Player gathered {amount} {resource_type}! Inventory: {self.get_inventory_string()}")
                    else:
                        if hasattr(self.game, 'show_message'):
                            self.game.show_message("Resource depleted")
                        else:
                            print("Resource node is depleted!")
                else:
                    print("Player interacting with world - nothing nearby")
        else:
            print("Player interacting with world")
        
        # End interaction state after a small delay
        self.game.taskMgr.doMethodLater(0.1, self.end_interaction, "EndInteract")
    
    def end_interaction(self, task):
        """End the interaction state"""
        self.is_interacting = False
        return task.done
    
    def take_damage(self, amount):
        """Apply damage to the player"""
        # Apply damage reduction from relics
        if hasattr(self, 'damage_reduction') and self.damage_reduction > 0:
            reduced_amount = amount * (1 - self.damage_reduction)
            amount = reduced_amount
            
        self.health -= amount
        if self.health < 0:
            self.health = 0
            self.die()
        
        print(f"Player took {amount} damage! Health: {self.health}/{self.max_health}")
    
    def heal(self, amount):
        """Heal the player"""
        self.health += amount
        if self.health > self.max_health:
            self.health = self.max_health
        
        print(f"Player healed {amount}! Health: {self.health}/{self.max_health}")
    
    def die(self):
        """Handle player death"""
        print("Player died!")
        # This would normally trigger death animation, game over screen, etc.
        
        # For now, just reset the player's position and health
        self.position = Vec3(0, 0, 0)
        self.health = self.max_health
    
    def add_experience(self, amount):
        """
        Add experience points to the player
        
        Args:
            amount (int): Amount of experience to add
        
        Returns:
            bool: True if the player leveled up
        """
        self.experience += amount
        
        # Check for level up
        if self.experience >= self.experience_to_next_level:
            self.level_up()
            return True
        
        return False
    
    def level_up(self):
        """Handle player level up"""
        self.level += 1
        
        # Carry over excess experience
        excess_xp = self.experience - self.experience_to_next_level
        
        # Calculate new experience requirement (increases with each level)
        self.experience_to_next_level = int(self.experience_to_next_level * 1.5)
        
        # Reset experience but keep the excess
        self.experience = excess_xp
        
        # Improve player stats
        old_max_health = self.max_health
        old_max_stamina = self.max_stamina
        
        # Increase stats
        self.max_health += 10
        self.max_stamina += 5
        
        # Heal player on level up
        self.health += (self.max_health - old_max_health)
        self.stamina += (self.max_stamina - old_max_stamina)
        
        # Increase attack damage
        for projectile_type in self.projectile_types.values():
            projectile_type["damage"] += 2
        
        # Display level up message
        print(f"Level Up! You are now level {self.level}!")
        
        # Show visual feedback if the game has a UI manager
        if hasattr(self.game, 'ui_manager') and hasattr(self.game.ui_manager, 'show_level_up'):
            self.game.ui_manager.show_level_up(self.level)
    
    def get_experience_percent(self):
        """Get the percentage of experience to next level"""
        if self.experience_to_next_level <= 0:
            return 100.0
        return (self.experience / self.experience_to_next_level) * 100.0
    
    def get_inventory_string(self):
        """Get a formatted string of the player's inventory"""
        inv_str = ""
        for resource, amount in self.inventory.items():
            if amount > 0:
                inv_str += f"{resource}: {amount}, "
        
        if inv_str:
            inv_str = inv_str[:-2]  # Remove trailing comma and space
        else:
            inv_str = "empty"
        
        return inv_str 