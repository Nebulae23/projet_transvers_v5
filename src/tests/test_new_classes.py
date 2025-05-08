#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test script for the enhanced character class system
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
from game.ability_factory import create_ability

# Configure Panda3D
loadPrcFileData("", """
    window-title Nightfall Defenders - Character Class Test
    sync-video #t
    show-frame-rate-meter #t
    fullscreen #f
    win-size 1280 720
""")

class ClassTestPlayer:
    """Test player class for demonstration purposes"""
    
    def __init__(self, class_type=None):
        """Initialize a test player"""
        self.max_health = 100
        self.health = 100
        self.max_stamina = 100
        self.stamina = 100
        self.speed = 5.0
        self.damage_multiplier = 1.0
        self.crit_chance_bonus = 0.0
        self.crit_damage_multiplier = 1.5
        self.passives = {}
        self.abilities = []
        self.class_type = class_type
        
    def add_passive(self, passive_id, passive_data):
        """Add a passive effect to the player"""
        self.passives[passive_id] = passive_data
        print(f"Added passive: {passive_data['name']} - {passive_data['description']}")
        
    def add_ability(self, ability):
        """Add an ability to the player"""
        self.abilities.append(ability)
        print(f"Added ability: {ability.name} - {ability.description}")
        
    def use_ability(self, ability_idx, target_pos=Vec3(0, 10, 0)):
        """Simulate using an ability"""
        if 0 <= ability_idx < len(self.abilities):
            ability = self.abilities[ability_idx]
            print(f"Using ability: {ability.name}")
            ability.use(self, None, target_pos)
            return True
        return False
        
class ClassTestApp(ShowBase):
    """Test application for character classes"""
    
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
        self.player = ClassTestPlayer()
        
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
        
        # Set up keyboard controls
        self.accept("escape", self.quit_app)
        self.accept("arrow_right", self.next_class)
        self.accept("arrow_left", self.prev_class)
        self.accept("1", lambda: self.player.use_ability(0))
        self.accept("2", lambda: self.player.use_ability(1))
        self.accept("3", lambda: self.player.use_ability(2))
        self.accept("4", lambda: self.player.use_ability(3))
        
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
        
        # Add placeholder for ability visualization
        self.ability_effects = self.render.attachNewNode("ability_effects")
        
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
        
        # Class description
        self.class_desc = OnscreenText(
            text="",
            pos=(0, 0.7),
            scale=0.04,
            fg=(0.8, 0.8, 1, 1),
            parent=self.aspect2d,
            align=TextNode.ACenter,
            wordwrap=30
        )
        
        # Instructions
        instructions = (
            "Arrow Keys: Change Class\n"
            "1-4: Use Abilities\n"
            "ESC: Quit"
        )
        
        self.instructions = OnscreenText(
            text=instructions,
            pos=(-1.1, 0.9),
            scale=0.04,
            fg=(1, 1, 1, 1),
            align=TextNode.ALeft,
            parent=self.aspect2d
        )
        
        # Abilities info
        self.ability_labels = []
        for i in range(4):
            label = OnscreenText(
                text="",
                pos=(-1.1, 0.7 - (i * 0.08)),
                scale=0.04,
                fg=(1, 0.8, 0.2, 1),
                align=TextNode.ALeft,
                parent=self.aspect2d
            )
            self.ability_labels.append(label)
            
        # Stats info
        self.stats_text = OnscreenText(
            text="",
            pos=(1.1, 0.9),
            scale=0.04,
            fg=(0.2, 1, 0.2, 1),
            align=TextNode.ARight,
            parent=self.aspect2d
        )
        
        # Passives info
        self.passives_text = OnscreenText(
            text="",
            pos=(1.1, 0.6),
            scale=0.035,
            fg=(0.2, 0.8, 1, 1),
            align=TextNode.ARight,
            wordwrap=20,
            parent=self.aspect2d
        )
        
    def apply_class(self, class_type):
        """Apply a class to the test player"""
        # Get class from manager
        self.player = ClassTestPlayer(class_type)
        character_class = self.class_manager.get_class(class_type)
        
        if character_class:
            # Apply class bonuses
            character_class.apply_class_bonuses(self.player)
            
            # Add abilities
            abilities = character_class.get_starting_abilities()
            for ability in abilities:
                self.player.add_ability(ability)
                
            # Update UI
            self.class_title.setText(character_class.name)
            self.class_desc.setText(character_class.description)
            
            # Update abilities display
            self.update_abilities_display()
            
            # Update stats display
            self.update_stats_display()
            
            # Update passives display
            self.update_passives_display()
            
            print(f"\nClass Applied: {character_class.name}")
            print(f"Description: {character_class.description}")
            print(f"Health: {self.player.health}/{self.player.max_health}")
            print(f"Stamina: {self.player.stamina}/{self.player.max_stamina}")
            print(f"Speed: {self.player.speed}")
            print(f"Damage Multiplier: {self.player.damage_multiplier}")
            print(f"Abilities: {len(self.player.abilities)}")
            
    def update_abilities_display(self):
        """Update the ability labels"""
        # Clear all labels
        for label in self.ability_labels:
            label.setText("")
            
        # Set text for available abilities
        for i, ability in enumerate(self.player.abilities):
            if i < len(self.ability_labels):
                self.ability_labels[i].setText(f"{i+1}: {ability.name} - {ability.description}")
                
    def update_stats_display(self):
        """Update the stats display"""
        stats_text = (
            f"Health: {self.player.health}/{self.player.max_health}\n"
            f"Stamina: {self.player.stamina}/{self.player.max_stamina}\n"
            f"Speed: {self.player.speed:.1f}\n"
            f"Damage Multiplier: {self.player.damage_multiplier:.2f}\n"
        )
        
        if hasattr(self.player, 'crit_chance_bonus') and self.player.crit_chance_bonus > 0:
            stats_text += f"Crit Chance: {self.player.crit_chance_bonus*100:.1f}%\n"
            
        if hasattr(self.player, 'max_summons'):
            stats_text += f"Max Summons: {self.player.max_summons}\n"
            
        self.stats_text.setText(stats_text)
        
    def update_passives_display(self):
        """Update the passives display"""
        if not self.player.passives:
            self.passives_text.setText("No passive abilities")
            return
            
        passives_text = "Passives:\n"
        for passive_id, passive_data in self.player.passives.items():
            passives_text += f"• {passive_data['name']}: {passive_data['description']}\n"
            
        self.passives_text.setText(passives_text)
        
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
    app = ClassTestApp()
    app.run()
    
if __name__ == "__main__":
    main() 