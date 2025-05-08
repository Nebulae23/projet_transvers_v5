#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test script for the Secondary Abilities system
"""

import os
import sys

# Add the src directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import time
import random
from direct.showbase.ShowBase import ShowBase
from panda3d.core import loadPrcFileData, WindowProperties, TextNode, CardMaker
from panda3d.core import AmbientLight, DirectionalLight, Vec3, Vec4, Fog, LPoint3f

from game.character_class import ClassType, ClassManager
from game.secondary_abilities import SecondaryAbilityManager, AbilityUnlockType
from game.ability_factory import create_ability

# Configure Panda3D
loadPrcFileData("", """
    window-title Nightfall Defenders - Secondary Abilities Test
    sync-video #t
    show-frame-rate-meter #t
    fullscreen #f
    win-size 1280 720
""")

class TestPlayer:
    """Test player class for demonstration purposes"""
    
    def __init__(self, class_type=None):
        """Initialize a test player"""
        self.max_health = 100
        self.health = 100
        self.max_stamina = 100
        self.stamina = 100
        self.speed = 5.0
        self.damage_multiplier = 1.0
        self.passives = {}
        self.primary_ability = None
        self.class_type = class_type
        
        # Create secondary ability manager
        self.secondary_abilities = SecondaryAbilityManager(self)
        
    def add_passive(self, passive_id, passive_data):
        """Add a passive effect to the player"""
        self.passives[passive_id] = passive_data
        print(f"Added passive: {passive_data['name']} - {passive_data['description']}")
        
    def set_primary_ability(self, ability):
        """Set the primary ability"""
        self.primary_ability = ability
        print(f"Set primary ability: {ability.name} - {ability.description}")
        
    def use_primary_ability(self, target_pos=Vec3(0, 10, 0)):
        """Use the primary ability"""
        if self.primary_ability:
            print(f"Using primary ability: {self.primary_ability.name}")
            self.primary_ability.use(self, None, target_pos)
            return True
        return False
        
    def use_secondary_ability(self, slot, target_pos=Vec3(0, 10, 0)):
        """Use a secondary ability"""
        return self.secondary_abilities.use_ability(slot, None, target_pos)
        
class SecondaryAbilitiesTestApp(ShowBase):
    """Test application for secondary abilities"""
    
    def __init__(self):
        """Initialize the test application"""
        super().__init__()
        
        # Set up scene
        self.setup_scene()
        
        # Set up class manager
        self.class_manager = ClassManager()
        
        # Create UI
        self.create_ui()
        
        # Create test player
        self.player = TestPlayer()
        
        # Available classes
        self.available_classes = [
            ClassType.WARRIOR,
            ClassType.MAGE,
            ClassType.CLERIC,
            ClassType.RANGER,
            ClassType.ALCHEMIST,
            ClassType.SUMMONER
        ]
        
        # Start with warrior
        self.current_class_idx = 0
        self.apply_class(self.available_classes[self.current_class_idx])
        
        # For demonstration, unlock some secondary abilities
        self.unlock_demonstration_abilities()
        
        # Set up keyboard controls
        self.accept("escape", self.quit_app)
        self.accept("arrow_right", self.next_class)
        self.accept("arrow_left", self.prev_class)
        self.accept("space", self.player.use_primary_ability)
        self.accept("1", lambda: self.player.use_secondary_ability(0))
        self.accept("2", lambda: self.player.use_secondary_ability(1))
        self.accept("3", lambda: self.player.use_secondary_ability(2))
        self.accept("u", self.unlock_random_ability)
        self.accept("e", self.equip_random_ability)
        
        # Add task to update abilities
        self.taskMgr.add(self.update_abilities, "UpdateAbilities")
        
    def setup_scene(self):
        """Set up the 3D scene"""
        # Set up camera
        self.cam.setPos(0, -15, 5)
        self.cam.lookAt(0, 0, 0)
        
        # Create a ground plane
        cm = CardMaker("ground")
        cm.setFrame(-20, 20, -20, 20)
        ground = self.render.attachNewNode(cm.generate())
        ground.setP(-90)
        ground.setZ(-0.01)
        ground.setColor(0.2, 0.2, 0.2, 1)
        
        # Add lights
        alight = AmbientLight("alight")
        alight.setColor(Vec4(0.3, 0.3, 0.3, 1.0))
        alnp = self.render.attachNewNode(alight)
        self.render.setLight(alnp)
        
        dlight = DirectionalLight("dlight")
        dlight.setColor(Vec4(0.8, 0.8, 0.8, 1.0))
        dlnp = self.render.attachNewNode(dlight)
        dlnp.setHpr(0, -60, 0)
        self.render.setLight(dlnp)
        
    def create_ui(self):
        """Create user interface elements"""
        # Class title
        self.class_title = OnscreenText(
            text="",
            pos=(0, 0.8),
            scale=0.08,
            fg=(1, 1, 1, 1),
            shadow=(0, 0, 0, 0.5),
            parent=self.aspect2d
        )
        
        # Instructions
        instructions = (
            "Arrow Keys: Change Class\n"
            "Space: Use Primary Ability\n"
            "1-3: Use Secondary Abilities\n"
            "U: Unlock Random Ability\n"
            "E: Equip Random Ability\n"
            "ESC: Quit"
        )
        
        self.instructions = OnscreenText(
            text=instructions,
            pos=(-1.3, 0.9),
            scale=0.04,
            fg=(1, 1, 1, 1),
            align=TextNode.ALeft,
            parent=self.aspect2d
        )
        
        # Primary ability
        self.primary_ability_text = OnscreenText(
            text="",
            pos=(-1.3, 0.5),
            scale=0.045,
            fg=(1, 0.9, 0.5, 1),
            align=TextNode.ALeft,
            parent=self.aspect2d
        )
        
        # Secondary abilities
        self.secondary_abilities_title = OnscreenText(
            text="Secondary Abilities:",
            pos=(-1.3, 0.3),
            scale=0.045,
            fg=(0.4, 0.8, 1, 1),
            align=TextNode.ALeft,
            parent=self.aspect2d
        )
        
        self.secondary_ability_labels = []
        for i in range(3):
            label = OnscreenText(
                text=f"{i+1}: None",
                pos=(-1.3, 0.2 - (i * 0.1)),
                scale=0.04,
                fg=(0.5, 0.8, 1, 1),
                align=TextNode.ALeft,
                parent=self.aspect2d
            )
            self.secondary_ability_labels.append(label)
            
        # Unlocked abilities list
        self.unlocked_abilities_title = OnscreenText(
            text="Unlocked Abilities:",
            pos=(1.3, 0.9),
            scale=0.045,
            fg=(0.7, 1, 0.7, 1),
            align=TextNode.ARight,
            parent=self.aspect2d
        )
        
        self.unlocked_abilities_text = OnscreenText(
            text="None",
            pos=(1.3, 0.8),
            scale=0.035,
            fg=(0.7, 1, 0.7, 1),
            align=TextNode.ARight,
            wordwrap=20,
            parent=self.aspect2d
        )
        
    def apply_class(self, class_type):
        """Apply a class to the test player"""
        # Get class from manager
        self.player = TestPlayer(class_type)
        character_class = self.class_manager.get_class(class_type)
        
        if character_class:
            # Apply class bonuses
            character_class.apply_class_bonuses(self.player)
            
            # Get the primary ability
            abilities = character_class.get_starting_abilities()
            if abilities:
                self.player.set_primary_ability(abilities[0])
                
            # Update UI
            self.class_title.setText(character_class.name)
            
            # Update ability displays
            self.update_ability_displays()
            
            print(f"\nClass Applied: {character_class.name}")
            
            # For demonstration, unlock some abilities for the class
            self.unlock_demonstration_abilities()
            
    def unlock_demonstration_abilities(self):
        """Unlock demonstration abilities for the current class"""
        # Get available abilities for this class
        class_type = self.player.class_type.value if self.player.class_type else "warrior"
        available_abilities = self.player.secondary_abilities.get_available_abilities_by_class(class_type)
        
        # Unlock 2 random abilities
        if available_abilities:
            for _ in range(min(2, len(available_abilities))):
                ability_id = random.choice(available_abilities)
                self.player.secondary_abilities.unlock_ability(ability_id)
                available_abilities.remove(ability_id)
                
            # Equip one ability to the first slot
            unlocked = self.player.secondary_abilities.get_unlocked_abilities()
            if unlocked:
                self.player.secondary_abilities.equip_ability(
                    self.player.secondary_abilities.unlocked_abilities[0], 0
                )
                
        # Update UI
        self.update_ability_displays()
        
    def update_ability_displays(self):
        """Update all ability displays"""
        # Update primary ability display
        if self.player.primary_ability:
            self.primary_ability_text.setText(
                f"Primary: {self.player.primary_ability.name} - {self.player.primary_ability.description}"
            )
        else:
            self.primary_ability_text.setText("Primary: None")
            
        # Update secondary abilities display
        equipped = self.player.secondary_abilities.get_equipped_abilities()
        for i, ability in enumerate(equipped):
            if i < len(self.secondary_ability_labels):
                if ability:
                    self.secondary_ability_labels[i].setText(
                        f"{i+1}: {ability.name} - {ability.description}"
                    )
                else:
                    self.secondary_ability_labels[i].setText(f"{i+1}: None")
                    
        # Update unlocked abilities display
        unlocked = self.player.secondary_abilities.get_unlocked_abilities()
        if unlocked:
            text = ""
            for ability in unlocked:
                text += f"• {ability.name}\n"
            self.unlocked_abilities_text.setText(text)
        else:
            self.unlocked_abilities_text.setText("None")
            
    def unlock_random_ability(self):
        """Unlock a random ability for the current class"""
        # Get available abilities for this class
        class_type = self.player.class_type.value if self.player.class_type else "warrior"
        available_abilities = self.player.secondary_abilities.get_available_abilities_by_class(class_type)
        
        # Remove already unlocked abilities
        for ability_id in self.player.secondary_abilities.unlocked_abilities:
            if ability_id in available_abilities:
                available_abilities.remove(ability_id)
                
        if available_abilities:
            ability_id = random.choice(available_abilities)
            if self.player.secondary_abilities.unlock_ability(ability_id):
                print(f"Unlocked new ability: {ability_id}")
            
        # Update UI
        self.update_ability_displays()
        
    def equip_random_ability(self):
        """Equip a random unlocked ability to a random slot"""
        unlocked = self.player.secondary_abilities.unlocked_abilities
        if not unlocked:
            print("No abilities to equip")
            return
            
        ability_id = random.choice(unlocked)
        slot = random.randint(0, self.player.secondary_abilities.max_slots - 1)
        
        if self.player.secondary_abilities.equip_ability(ability_id, slot):
            ability = create_ability(ability_id)
            print(f"Equipped {ability.name} to slot {slot+1}")
            
        # Update UI
        self.update_ability_displays()
        
    def update_abilities(self, task):
        """Update abilities"""
        dt = globalClock.getDt()
        self.player.secondary_abilities.update(dt)
        return task.cont
        
    def next_class(self):
        """Switch to the next class"""
        self.current_class_idx = (self.current_class_idx + 1) % len(self.available_classes)
        self.apply_class(self.available_classes[self.current_class_idx])
        
    def prev_class(self):
        """Switch to the previous class"""
        self.current_class_idx = (self.current_class_idx - 1) % len(self.available_classes)
        self.apply_class(self.available_classes[self.current_class_idx])
        
    def quit_app(self):
        """Exit the application"""
        self.userExit()
        
def main():
    """Main function"""
    app = SecondaryAbilitiesTestApp()
    app.run()
    
if __name__ == "__main__":
    main() 