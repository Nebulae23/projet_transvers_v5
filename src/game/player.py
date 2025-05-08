#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Player entity module for Nightfall Defenders
"""

from panda3d.core import NodePath, Vec3, KeyboardButton, MouseButton
from direct.actor.Actor import Actor
import math
import random

# Import the new systems
from game.ability_system import AbilityManager
from game.character_class import ClassType
from game.skill_tree import SkillTree
import game.skill_definitions

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
        self.direction = Vec3(0, 1, 0)  # Forward direction vector
        
        # Player stats
        self.max_health = 100
        self.health = 100
        self.max_stamina = 100
        self.stamina = 100
        self.max_mana = 100  # New resource for abilities
        self.mana = 100
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
        
        # Projectile settings - kept for backward compatibility
        self.projectile_type = "straight"  # Default projectile type
        self.setup_projectile_types()
        
        # New ability system
        self.ability_manager = AbilityManager(self)
        self.current_ability_slot = 0
        
        # Character class system
        self.character_class = None  # Will be set when class is chosen
        self.damage_multiplier = 1.0
        self.spell_damage_multiplier = 1.0
        self.healing_multiplier = 1.0
        self.dodge_chance = 0.0
        
        # Skill tree
        self.skill_tree = SkillTree()
        self.skill_tree.create_from_template(game.skill_definitions.create_skill_tree_template())
        self.skill_points = 0
        
        # Passives
        self.passives = {}
        
        # Fusion and Harmonization flags
        self.can_create_fusions = False
        self.can_harmonize_abilities = False
        
        # Load the player model
        self.setup_model()
        
        # Set up collision detection
        self.setup_collision()
        
        # Debug visualization
        self.debug_node = self.root.attachNewNode("PlayerDebug")
        self.draw_debug_visualization()
        
        # Setup key listeners for ability switching
        self.setup_ability_keys()
        
        # Inventory
        self.inventory = {
            "wood": 0,
            "stone": 0,
            "crystal": 0,
            "herb": 0,
            "monster_essence": 0  # New resource for skill tree
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
        
        # Update ability manager
        self.ability_manager.update(dt)
        
        # Update visibility based on time of day
        self._update_visibility()
        
        # Apply movement
        self.apply_movement(dt)
        
        # Update the model position
        self.root.setPos(self.position)
        self.root.setH(self.facing_angle)
        
        # Update effects display
        if hasattr(self, 'effects_display'):
            self.effects_display.update(dt)
        
        # Update debug visualization if needed
        if hasattr(self.game, 'debug_mode') and self.game.debug_mode:
            self.draw_debug_visualization()
        
        # Regenerate mana
        self.regenerate_mana(dt)
    
    def regenerate_mana(self, dt):
        """Regenerate mana over time"""
        # Base mana regen rate
        mana_regen_rate = 2.0  # Mana per second
        
        # Apply modifiers from passives
        if "mana_regen_multiplier" in self.get_passive_effects():
            mana_regen_multiplier = self.get_passive_effects()["mana_regen_multiplier"]
            mana_regen_rate *= mana_regen_multiplier
        
        # Apply regen
        self.mana = min(self.max_mana, self.mana + mana_regen_rate * dt)
    
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
            
            # Update the facing angle based on movement direction
            # Only if the player is actually moving
            self.facing_angle = math.degrees(math.atan2(-input_vector.x, input_vector.y))
            
            # Update the direction vector
            self.direction = Vec3(
                -math.sin(math.radians(self.facing_angle)),
                math.cos(math.radians(self.facing_angle)),
                0
            )
        
        # Apply input to velocity
        speed_to_use = self.speed
        if self.is_dodging:
            speed_to_use = self.dodge_speed
            
        # Apply speed modifiers from passives
        if "speed_multiplier" in self.get_passive_effects():
            speed_to_use *= self.get_passive_effects()["speed_multiplier"]
            
        self.velocity = input_vector * speed_to_use
    
    def process_action_input(self, dt):
        """Process action input from the player"""
        # Cooldown updates are handled in update_cooldowns
        pass
    
    def primary_attack(self):
        """Handle primary attack (use current ability)"""
        self.ability_manager.use_ability(self.current_ability_slot)
    
    def secondary_attack(self):
        """Handle secondary attack (change to next ability)"""
        # Cycle through active abilities
        if len(self.ability_manager.active_abilities) > 0:
            self.current_ability_slot = (self.current_ability_slot + 1) % len(self.ability_manager.active_abilities)
            self.show_current_ability()
    
    def dodge(self):
        """Perform a dodge action"""
        if self.dodge_cooldown <= 0:
            self.start_dodge()
    
    def interact(self):
        """Interact with nearby objects"""
        if not self.is_interacting:
            self.interact_with_world()
    
    def update_cooldowns(self, dt):
        """Update all cooldowns"""
        # Dodge cooldown
        if self.dodge_cooldown > 0:
            self.dodge_cooldown -= dt
        
        # Attack cooldown (for backward compatibility)
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt
    
    def apply_movement(self, dt):
        """Apply movement based on velocity"""
        # Move the player
        self.position += self.velocity * dt
        
        # TODO: Add collision detection and response
    
    def setup_projectile_types(self):
        """Setup different projectile types and their properties (for backward compatibility)"""
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
    
    def setup_ability_keys(self):
        """Setup key listeners for ability selection"""
        self.game.accept("1", self.set_ability_slot, [0])
        self.game.accept("2", self.set_ability_slot, [1])
        self.game.accept("3", self.set_ability_slot, [2])
        self.game.accept("4", self.set_ability_slot, [3])
        
        # Show initial ability
        self.show_current_ability()
    
    def set_ability_slot(self, slot):
        """Set the current ability slot"""
        if slot >= 0 and slot < len(self.ability_manager.active_abilities):
            self.current_ability_slot = slot
            self.show_current_ability()
    
    def show_current_ability(self):
        """Show the current abilities in the UI"""
        # Make sure the player has a class
        if not self.character_class:
            print("No class selected yet.")
            return
            
        # Get ability info from ability manager
        if hasattr(self, 'ability_manager'):
            primary = getattr(self, 'current_primary_ability', "None")
            secondary = getattr(self, 'current_secondary_ability', "None")
            
            # Update the display if UI elements exist
            if hasattr(self.game, 'ability_box'):
                self.game.ability_box.update_value(0, primary)
                self.game.ability_box.update_value(1, secondary)
                
            print(f"Current abilities: Primary - {primary}, Secondary - {secondary}")
            
            # Show a notification if notification system exists
            if hasattr(self.game, 'notification_system'):
                self.game.notification_system.add_notification(
                    f"Selected {self.character_class.value} class",
                    duration=3.0,
                    type="success"
                )
    
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
                        
                        print(f"Gathered {amount} {resource_type}")
                        found_interaction = True
            
            # End interaction after a delay
            self.game.taskMgr.doMethodLater(0.5, self.end_interaction, "EndInteraction")
            
            # Return whether we found something to interact with
            return found_interaction
        
        return False
    
    def end_interaction(self, task):
        """End the interaction state"""
        self.is_interacting = False
        return task.done
    
    def take_damage(self, amount, source=None):
        """
        Take damage from an attack
        
        Args:
            amount (int): Amount of damage to take
            source: Source of the damage
            
        Returns:
            int: Actual damage taken
        """
        # Check for dodge
        if self.dodge_chance > 0 and random.random() < self.dodge_chance:
            print("Player dodged the attack!")
            return 0
        
        # Apply damage reduction
        damage_reduction = self.damage_reduction
        
        # Add passive damage reduction if available
        if "damage_reduction" in self.get_passive_effects():
            damage_reduction += self.get_passive_effects()["damage_reduction"]
        
        # Calculate actual damage
        actual_damage = int(amount * (1.0 - damage_reduction))
        actual_damage = max(1, actual_damage)  # Always take at least 1 damage
        
        # Apply damage
        self.health = max(0, self.health - actual_damage)
        
        print(f"Player took {actual_damage} damage! Health: {self.health}/{self.max_health}")
        
        # Check if dead
        if self.health <= 0:
            self.die()
        
        return actual_damage
    
    def heal(self, amount):
        """
        Heal the player
        
        Args:
            amount (int): Amount to heal
            
        Returns:
            int: Actual amount healed
        """
        # Apply healing modifier
        if hasattr(self, 'healing_multiplier'):
            amount = int(amount * self.healing_multiplier)
        
        # Calculate actual healing
        old_health = self.health
        self.health = min(self.max_health, self.health + amount)
        actual_heal = self.health - old_health
        
        if actual_heal > 0:
            print(f"Player healed for {actual_heal}! Health: {self.health}/{self.max_health}")
        
        return actual_heal
    
    def die(self):
        """Handle player death"""
        print("Player has died!")
        
        # Trigger resurrection if available
        if hasattr(self.game, 'trigger_resurrection'):
            self.game.trigger_resurrection()
        else:
            # Default death behavior - respawn at starting position
            self.health = self.max_health
            self.position = Vec3(0, 0, 0)
    
    def add_experience(self, amount):
        """
        Add experience points to the player
        
        Args:
            amount (int): Amount of experience to add
            
        Returns:
            bool: True if player leveled up
        """
        self.experience += amount
        print(f"Gained {amount} experience! Total: {self.experience}")
        
        # Check for level up
        if self.experience >= self.experience_to_next_level:
            self.level_up()
            return True
            
        return False
    
    def level_up(self):
        """Handle player level up"""
        self.level += 1
        
        # Calculate experience needed for next level
        # Using a simple formula: base_xp * (level_factor ^ current_level)
        base_xp = 100
        level_factor = 1.5
        self.experience_to_next_level = int(base_xp * (level_factor ** self.level))
        
        print(f"Level up! You are now level {self.level}")
        print(f"Next level at {self.experience_to_next_level} experience")
        
        # Increase stats
        self.max_health += 10
        self.health = self.max_health
        
        self.max_stamina += 5
        self.stamina = self.max_stamina
        
        self.max_mana += 8
        self.mana = self.max_mana
        
        # Grant skill point
        self.skill_points += 1
        print(f"You have gained a skill point! (Total: {self.skill_points})")
        
        # Apply class-specific level up effects
        if self.character_class and hasattr(self.game, 'class_manager'):
            class_manager = self.game.class_manager
            class_obj = class_manager.get_class(ClassType(self.character_class))
            if class_obj:
                class_obj.on_level_up(self, self.level)
                
        # Increase projectile damage (for backward compatibility)
        for projectile_type in self.projectile_types.values():
            projectile_type["damage"] += 2
    
    def set_class(self, class_type):
        """
        Set the player's character class
        
        Args:
            class_type (ClassType): The class to set
            
        Returns:
            bool: True if the class was set successfully
        """
        if hasattr(self.game, 'class_manager'):
            success = self.game.class_manager.apply_class(self, class_type)
            
            if success:
                print(f"Character class set to {class_type.value}")
                
                # Apply skill tree root node unlock based on class
                class_obj = self.game.class_manager.get_class(class_type)
                if class_obj:
                    root_node_id = f"{class_type.value}_root"
                    root_node = self.skill_tree.nodes.get(root_node_id)
                    if root_node:
                        root_node.is_unlocked = True
                        
                        # Make root node's children visible
                        for child in root_node.children:
                            child.is_visible = True
                
                return True
        
        return False
    
    def add_passive(self, passive_id, passive_data):
        """
        Add a passive effect to the player
        
        Args:
            passive_id (str): ID of the passive
            passive_data (dict): Data for the passive
            
        Returns:
            bool: True if added successfully
        """
        self.passives[passive_id] = passive_data
        return True
    
    def get_passive_effects(self):
        """
        Get combined effects from all passives
        
        Returns:
            dict: Combined effects
        """
        effects = {}
        
        # Combine all passive effects
        for passive_id, passive_data in self.passives.items():
            if "effects" in passive_data:
                for effect_key, effect_value in passive_data["effects"].items():
                    if effect_key in effects:
                        # For multipliers, compound them
                        if "multiplier" in effect_key:
                            effects[effect_key] *= effect_value
                        # For flat values, add them
                        else:
                            effects[effect_key] += effect_value
                    else:
                        effects[effect_key] = effect_value
        
        return effects
    
    def unlock_ability(self, ability_id):
        """
        Unlock a new ability
        
        Args:
            ability_id (str): ID of the ability to unlock
            
        Returns:
            bool: True if unlocked successfully
        """
        from game.ability_factory import create_ability
        
        # Create the ability
        ability = create_ability(ability_id)
        if not ability:
            return False
        
        # Add to ability manager
        self.ability_manager.add_ability(ability)
        return self.ability_manager.unlock_ability(ability_id)
    
    def modify_ability(self, ability_id, modifiers):
        """
        Apply modifiers to an ability
        
        Args:
            ability_id (str): ID of the ability to modify
            modifiers (dict): Modifiers to apply
            
        Returns:
            bool: True if modified successfully
        """
        return self.ability_manager.modify_ability(ability_id, modifiers)
    
    def set_specialization(self, spec_path):
        """
        Set specialization for an ability
        
        Args:
            spec_path (str): Specialization path identifier
            
        Returns:
            bool: True if specialization was set
        """
        # In a real implementation, this would determine which ability to specialize
        # For now, just specialize the first active ability if available
        if len(self.ability_manager.active_abilities) > 0:
            ability_id = self.ability_manager.active_abilities[0]
            
            # Convert string path to enum
            from game.ability_system import SpecializationPath
            try:
                path = SpecializationPath(spec_path)
                return self.ability_manager.specialize_ability(ability_id, path)
            except:
                print(f"Invalid specialization path: {spec_path}")
                return False
        
        return False
    
    def unlock_fusion_type(self, fusion_type):
        """
        Unlock a fusion type
        
        Args:
            fusion_type (str): Type of fusion to unlock
            
        Returns:
            bool: True if unlocked successfully
        """
        # Mark player as having fusion abilities
        self.can_create_fusions = True
        
        # Log the fusion type unlock
        print(f"Unlocked fusion type: {fusion_type}")
        
        # Set the specific fusion type flag on the player
        # This is checked in AbilityManager.create_fusion
        setattr(self, f"can_use_{fusion_type}_fusion", True)
        
        # Display a notification if UI is available
        if hasattr(self.game, 'ui_manager') and hasattr(self.game.ui_manager, 'show_notification'):
            self.game.ui_manager.show_notification(f"New Fusion Type Unlocked: {fusion_type.capitalize()}")
            
        return True
    
    def get_experience_percent(self):
        """
        Get the percentage of experience to next level
        
        Returns:
            float: Percentage (0.0 to 1.0)
        """
        if self.experience_to_next_level <= 0:
            return 1.0
        return min(1.0, self.experience / self.experience_to_next_level)
    
    def open_fusion_ui(self):
        """Open the ability fusion UI"""
        # Check if fusion is unlocked
        if not getattr(self, 'can_create_fusions', False):
            # Show notification if UI manager exists
            if hasattr(self.game, 'ui_manager') and hasattr(self.game.ui_manager, 'show_notification'):
                self.game.ui_manager.show_notification("Fusion is not yet unlocked.")
            return False
        
        # Check if fusion UI already exists
        if not hasattr(self.game, 'fusion_ui'):
            # Create fusion UI
            from game.fusion_ui import FusionUI
            self.game.fusion_ui = FusionUI(self.game)
        
        # Show fusion UI
        self.game.fusion_ui.show(self)
        return True
    
    def get_inventory_string(self):
        """
        Get a string representation of the inventory
        
        Returns:
            str: Inventory string
        """
        items = []
        for item, count in self.inventory.items():
            if count > 0:
                items.append(f"{item}: {count}")
        
        if not items:
            return "Inventory: Empty"
        
        return "Inventory: " + ", ".join(items)
    
    def _update_visibility(self):
        """Update visibility based on time of day"""
        # This would normally be used to adjust player visibility
        # based on lighting conditions, day/night cycle, etc.
        pass

    def get_position(self):
        """
        Get the player's current position
        
        Returns:
            Vec3 position
        """
        if hasattr(self, 'node_path'):
            return self.node_path.getPos()
        return Vec3(0, 0, 0)

    def perform_primary_attack(self):
        """Perform the player's primary attack"""
        if hasattr(self, 'primary_attack'):
            self.primary_attack()
            
            # Apply physics impulse if game has physics manager
            if hasattr(self.game, 'physics_manager'):
                # Example: apply recoil force opposite to facing direction
                facing_dir = self.get_facing_direction()
                recoil_force = facing_dir * -50.0  # Adjust strength as needed
                self.game.physics_manager.apply_force("player", recoil_force)

    def perform_secondary_attack(self):
        """Perform the player's secondary attack"""
        if hasattr(self, 'secondary_attack'):
            self.secondary_attack()
            
            # Apply physics effect if game has physics manager
            if hasattr(self.game, 'physics_manager'):
                # Example: for a magical attack, create wind effect
                self.game.physics_manager.set_wind(
                    self.get_facing_direction(),  # Wind direction matches player facing
                    2.0,  # Wind strength
                    0.4   # Turbulence
                )

    def get_facing_direction(self):
        """
        Get the player's facing direction
        
        Returns:
            Vec3 normalized direction vector
        """
        # Simple implementation assuming player faces where they move
        if hasattr(self, 'movement_dir') and self.movement_dir.length_squared() > 0.001:
            return self.movement_dir.normalized()
        
        # Default facing direction if no movement
        return Vec3(1, 0, 0)

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

    def _update_visibility(self):
        """Update player's visibility based on time of day"""
        # Default visibility range
        self.visibility_range = 100.0
        
        # Check if day/night cycle is active
        if hasattr(self.game, 'day_night_cycle'):
            # Get visibility modifier from day/night cycle
            self.visibility_range = self.game.day_night_cycle.get_visibility_distance()
            
            # Apply any player visibility bonuses/relics
            if hasattr(self, 'visibility_bonus'):
                self.visibility_range += self.visibility_bonus
            
            # Update vision-related game elements
            if hasattr(self.game, 'fog') and hasattr(self.game.fog, 'setLinearRange'):
                # If the game has fog with configurable range, update it
                self.game.fog.setLinearRange(0, self.visibility_range)

    def unlock_harmonization_type(self, harmonization_type):
        """
        Unlock a harmonization type
        
        Args:
            harmonization_type (str): Type of harmonization to unlock
            
        Returns:
            bool: True if unlocked successfully
        """
        # Mark player as having harmonization abilities
        self.can_harmonize_abilities = True
        
        # Log the harmonization type unlock
        print(f"Unlocked harmonization type: {harmonization_type}")
        
        # Set the specific harmonization type flag on the player
        # This is checked in AbilityManager.harmonize_ability
        setattr(self, f"can_use_{harmonization_type}_harmonization", True)
        
        # Display a notification if UI is available
        if hasattr(self.game, 'ui_manager') and hasattr(self.game.ui_manager, 'show_notification'):
            self.game.ui_manager.show_notification(f"New Harmonization Type Unlocked: {harmonization_type.capitalize()}")
            
        return True
        
    def open_harmonization_ui(self):
        """Open the ability harmonization UI"""
        # Check if harmonization is unlocked
        if not getattr(self, 'can_harmonize_abilities', False):
            # Show notification if UI manager exists
            if hasattr(self.game, 'ui_manager') and hasattr(self.game.ui_manager, 'show_notification'):
                self.game.ui_manager.show_notification("Harmonization is not yet unlocked.")
            return False
        
        # Check if harmonization UI already exists
        if not hasattr(self.game, 'harmonization_ui'):
            # Create harmonization UI
            from game.harmonization_ui import HarmonizationUI
            self.game.harmonization_ui = HarmonizationUI(self.game)
        
        # Show harmonization UI
        self.game.harmonization_ui.show(self)
        return True
        
    def harmonize_ability(self, ability_id):
        """
        Harmonize an ability
        
        Args:
            ability_id (str): ID of the ability to harmonize
            
        Returns:
            str or None: ID of the harmonized ability or None if harmonization failed
        """
        if not hasattr(self, 'ability_manager'):
            return None
            
        # Check if player has any harmonization resources
        harmonization_resource = "harmonization_essence"
        if self.inventory.get(harmonization_resource, 0) <= 0:
            # Show notification if UI manager exists
            if hasattr(self.game, 'ui_manager') and hasattr(self.game.ui_manager, 'show_notification'):
                self.game.ui_manager.show_notification(f"You need {harmonization_resource} to harmonize an ability.")
            return None
            
        # Try to harmonize the ability
        harmonized_ability_id = self.ability_manager.harmonize_ability(ability_id)
        
        if harmonized_ability_id:
            # Consume the harmonization resource
            self.inventory[harmonization_resource] = self.inventory.get(harmonization_resource, 0) - 1
            
            # Show notification if UI manager exists
            if hasattr(self.game, 'ui_manager') and hasattr(self.game.ui_manager, 'show_notification'):
                harmonized_ability = self.ability_manager.get_ability(harmonized_ability_id)
                self.game.ui_manager.show_notification(f"Successfully harmonized into {harmonized_ability.name}!")
                
        return harmonized_ability_id 