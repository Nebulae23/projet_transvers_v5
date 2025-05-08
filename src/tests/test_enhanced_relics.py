#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Enhanced Relic System Test for Nightfall Defenders
Demonstrates the enhanced relic system with night chest rewards and drawbacks
"""

import os
import sys
import math
import random

# Add src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.abspath(os.path.join(current_dir, '..'))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from direct.showbase.ShowBase import ShowBase
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import (
    DirectButton, DirectLabel, DirectScrolledFrame, 
    DirectFrame, DGG
)
from panda3d.core import TextNode, Vec3, Vec4, NodePath, AmbientLight, DirectionalLight

# Import the relic system
from game.relic_system import RelicSystem, RelicRarity

class DummyPlayer:
    """Dummy player class for testing the relic system"""
    
    def __init__(self):
        """Initialize a dummy player for testing"""
        self.health = 100
        self.max_health = 100
        self.damage_multiplier = 1.0
        self.speed_multiplier = 1.0
        self.cooldown_multiplier = 1.0
        self.stamina_cost_multiplier = 1.0
        self.max_stamina_multiplier = 1.0
        self.life_steal = 0.0
        self.damage_reduction = 0.0
        self.inventory = {"monster_essence": 50}

class DummyGame:
    """Dummy game class for testing the relic system"""
    
    def __init__(self):
        """Initialize a dummy game for testing"""
        self.player = DummyPlayer()
        self.time_of_day = "night"
        self.game_time = 0.0
        self.messages = []
    
    def show_message(self, text, duration=2.0):
        """Show a message to the player"""
        self.messages.append(text)
        print(f"MESSAGE: {text}")

class EnhancedRelicTest(ShowBase):
    """Test application for the enhanced relic system"""
    
    def __init__(self):
        ShowBase.__init__(self)
        
        # Set window title
        self.window_props = self.win.getProperties()
        self.window_props.setTitle("Nightfall Defenders - Enhanced Relic System Test")
        self.win.requestProperties(self.window_props)
        
        # Create a dummy game with player
        self.game = DummyGame()
        
        # Create the relic system
        self.relic_system = RelicSystem(self.game)
        
        # Create UI
        self.create_ui()
        
        # Create relic display
        self.create_relic_display()
        
        # Add chest display
        self.create_chest_display()
        
        # Set up a task to update the display
        self.taskMgr.add(self.update, "update_task")
    
    def create_ui(self):
        """Create the user interface"""
        # Title
        self.title = OnscreenText(
            text="Enhanced Relic System Test",
            pos=(0, 0.9),
            scale=0.06,
            fg=(1, 1, 1, 1),
            shadow=(0, 0, 0, 0.5),
            align=TextNode.ACenter
        )
        
        # Instructions
        self.instructions = OnscreenText(
            text="Complete nights to earn relic chests with varying quality\n"
                 "Add relics to see how they affect the player stats\n"
                 "Some relics have significant drawbacks!",
            pos=(0, 0.8),
            scale=0.04,
            fg=(1, 0.9, 0.8, 1),
            align=TextNode.ACenter
        )
        
        # Night survival buttons
        self.night_buttons_frame = DirectFrame(
            frameColor=(0.2, 0.2, 0.2, 0.7),
            frameSize=(-0.4, 0.4, -0.15, 0.15),
            pos=(-0.5, 0, 0.5)
        )
        
        night_label = DirectLabel(
            text="Night Survival",
            scale=0.05,
            pos=(0, 0, 0.1),
            text_fg=(1, 1, 1, 1),
            frameColor=(0, 0, 0, 0),
            parent=self.night_buttons_frame
        )
        
        complete_night_button = DirectButton(
            text="Complete Night (Easy)",
            scale=0.04,
            pos=(0, 0, 0.03),
            command=self.complete_night,
            extraArgs=[1.0],
            frameColor=(0.3, 0.5, 0.3, 0.8),
            parent=self.night_buttons_frame
        )
        
        complete_hard_night_button = DirectButton(
            text="Complete Night (Hard)",
            scale=0.04,
            pos=(0, 0, -0.03),
            command=self.complete_night,
            extraArgs=[2.0],
            frameColor=(0.5, 0.3, 0.3, 0.8),
            parent=self.night_buttons_frame
        )
        
        open_chest_button = DirectButton(
            text="Open Reward Chest",
            scale=0.04,
            pos=(0, 0, -0.09),
            command=self.open_chest,
            frameColor=(0.3, 0.3, 0.6, 0.8),
            parent=self.night_buttons_frame
        )
        
        # Player stats frame
        self.stats_frame = DirectFrame(
            frameColor=(0.2, 0.2, 0.2, 0.7),
            frameSize=(-0.4, 0.4, -0.25, 0.15),
            pos=(0.5, 0, 0.5)
        )
        
        stats_label = DirectLabel(
            text="Player Stats",
            scale=0.05,
            pos=(0, 0, 0.1),
            text_fg=(1, 1, 1, 1),
            frameColor=(0, 0, 0, 0),
            parent=self.stats_frame
        )
        
        # Add stats labels
        self.health_label = DirectLabel(
            text="Health: 100/100",
            scale=0.04,
            pos=(-0.3, 0, 0.03),
            text_align=TextNode.ALeft,
            text_fg=(1, 1, 1, 1),
            frameColor=(0, 0, 0, 0),
            parent=self.stats_frame
        )
        
        self.damage_label = DirectLabel(
            text="Damage Multiplier: 1.0x",
            scale=0.04,
            pos=(-0.3, 0, -0.03),
            text_align=TextNode.ALeft,
            text_fg=(1, 1, 1, 1),
            frameColor=(0, 0, 0, 0),
            parent=self.stats_frame
        )
        
        self.speed_label = DirectLabel(
            text="Speed Multiplier: 1.0x",
            scale=0.04,
            pos=(-0.3, 0, -0.09),
            text_align=TextNode.ALeft,
            text_fg=(1, 1, 1, 1),
            frameColor=(0, 0, 0, 0),
            parent=self.stats_frame
        )
        
        self.cooldown_label = DirectLabel(
            text="Cooldown Multiplier: 1.0x",
            scale=0.04,
            pos=(-0.3, 0, -0.15),
            text_align=TextNode.ALeft,
            text_fg=(1, 1, 1, 1),
            frameColor=(0, 0, 0, 0),
            parent=self.stats_frame
        )
        
        # Day/Night toggle
        self.time_toggle_frame = DirectFrame(
            frameColor=(0.2, 0.2, 0.2, 0.7),
            frameSize=(-0.3, 0.3, -0.08, 0.08),
            pos=(0, 0, 0.3)
        )
        
        time_label = DirectLabel(
            text="Time of Day",
            scale=0.05,
            pos=(0, 0, 0.03),
            text_fg=(1, 1, 1, 1),
            frameColor=(0, 0, 0, 0),
            parent=self.time_toggle_frame
        )
        
        day_button = DirectButton(
            text="Set to Day",
            scale=0.04,
            pos=(-0.15, 0, -0.03),
            command=self.set_time_of_day,
            extraArgs=["day"],
            frameColor=(0.5, 0.5, 0.2, 0.8),
            parent=self.time_toggle_frame
        )
        
        night_button = DirectButton(
            text="Set to Night",
            scale=0.04,
            pos=(0.15, 0, -0.03),
            command=self.set_time_of_day,
            extraArgs=["night"],
            frameColor=(0.2, 0.2, 0.5, 0.8),
            parent=self.time_toggle_frame
        )
    
    def create_relic_display(self):
        """Create the display for active and available relics"""
        # Active relics frame
        self.active_relics_frame = DirectFrame(
            frameColor=(0.2, 0.2, 0.3, 0.7),
            frameSize=(-0.45, 0.45, -0.3, 0.3),
            pos=(-0.5, 0, -0.3)
        )
        
        active_label = DirectLabel(
            text="Active Relics",
            scale=0.05,
            pos=(0, 0, 0.25),
            text_fg=(1, 1, 1, 1),
            frameColor=(0, 0, 0, 0),
            parent=self.active_relics_frame
        )
        
        # Create a scrolled frame for active relics
        self.active_relics_scroll = DirectScrolledFrame(
            frameSize=(-0.4, 0.4, -0.2, 0.2),
            canvasSize=(-0.35, 0.35, -0.5, 0.5),  # Will be adjusted based on content
            scrollBarWidth=0.04,
            verticalScroll_relief=DGG.FLAT,
            frameColor=(0.25, 0.25, 0.3, 0.9),
            parent=self.active_relics_frame
        )
        
        # Inventory relics frame
        self.inventory_relics_frame = DirectFrame(
            frameColor=(0.2, 0.3, 0.2, 0.7),
            frameSize=(-0.45, 0.45, -0.3, 0.3),
            pos=(0.5, 0, -0.3)
        )
        
        inventory_label = DirectLabel(
            text="Relic Inventory",
            scale=0.05,
            pos=(0, 0, 0.25),
            text_fg=(1, 1, 1, 1),
            frameColor=(0, 0, 0, 0),
            parent=self.inventory_relics_frame
        )
        
        # Create a scrolled frame for inventory relics
        self.inventory_relics_scroll = DirectScrolledFrame(
            frameSize=(-0.4, 0.4, -0.2, 0.2),
            canvasSize=(-0.35, 0.35, -0.5, 0.5),  # Will be adjusted based on content
            scrollBarWidth=0.04,
            verticalScroll_relief=DGG.FLAT,
            frameColor=(0.25, 0.3, 0.25, 0.9),
            parent=self.inventory_relics_frame
        )
        
        # Update the displays
        self.update_relic_displays()
    
    def create_chest_display(self):
        """Create the display for chest rewards"""
        self.chest_frame = DirectFrame(
            frameColor=(0.3, 0.25, 0.2, 0.7),
            frameSize=(-0.3, 0.3, -0.2, 0.2),
            pos=(0, 0, 0),
            state=DGG.NORMAL
        )
        
        self.chest_label = DirectLabel(
            text="Reward Chest (Not Available)",
            scale=0.05,
            pos=(0, 0, 0.15),
            text_fg=(1, 1, 1, 1),
            frameColor=(0, 0, 0, 0),
            parent=self.chest_frame
        )
        
        self.chest_quality_label = DirectLabel(
            text="Quality: None",
            scale=0.04,
            pos=(0, 0, 0.08),
            text_fg=(1, 1, 1, 1),
            frameColor=(0, 0, 0, 0),
            parent=self.chest_frame
        )
        
        self.chest_contents = DirectLabel(
            text="Contents: None",
            scale=0.04,
            pos=(0, 0, 0),
            text_fg=(1, 1, 1, 1),
            frameColor=(0, 0, 0, 0),
            parent=self.chest_frame
        )
        
        # Initially hide the chest
        self.chest_frame.hide()
    
    def update_relic_displays(self):
        """Update the active and inventory relic displays"""
        # Clear existing display items
        for child in self.active_relics_scroll.getCanvas().getChildren():
            child.removeNode()
            
        for child in self.inventory_relics_scroll.getCanvas().getChildren():
            child.removeNode()
        
        # Add active relics
        y_pos = 0.45
        for relic_id, relic in self.relic_system.active_relics.items():
            relic_frame = self.create_relic_item(relic_id, relic, y_pos, True)
            relic_frame.reparentTo(self.active_relics_scroll.getCanvas())
            y_pos -= 0.12
        
        # Reset canvas size for active relics
        if y_pos < -0.5:
            self.active_relics_scroll["canvasSize"] = (-0.35, 0.35, y_pos, 0.5)
        else:
            self.active_relics_scroll["canvasSize"] = (-0.35, 0.35, -0.5, 0.5)
        
        # Add inventory relics
        y_pos = 0.45
        for relic_id, relic in self.relic_system.relic_inventory.items():
            relic_frame = self.create_relic_item(relic_id, relic, y_pos, False)
            relic_frame.reparentTo(self.inventory_relics_scroll.getCanvas())
            y_pos -= 0.12
        
        # Reset canvas size for inventory relics
        if y_pos < -0.5:
            self.inventory_relics_scroll["canvasSize"] = (-0.35, 0.35, y_pos, 0.5)
        else:
            self.inventory_relics_scroll["canvasSize"] = (-0.35, 0.35, -0.5, 0.5)
    
    def create_relic_item(self, relic_id, relic, y_pos, is_active):
        """Create a UI element for a relic"""
        color_by_rarity = {
            RelicRarity.COMMON: (0.5, 0.5, 0.5, 0.8),      # Gray
            RelicRarity.UNCOMMON: (0.3, 0.7, 0.3, 0.8),    # Green
            RelicRarity.RARE: (0.3, 0.3, 0.8, 0.8),        # Blue
            RelicRarity.EPIC: (0.7, 0.3, 0.7, 0.8),        # Purple
            RelicRarity.LEGENDARY: (0.8, 0.7, 0.2, 0.8),   # Gold
            RelicRarity.MYTHICAL: (1.0, 0.4, 0.4, 0.8)     # Red
        }
        
        relic_color = color_by_rarity.get(relic["rarity"], (0.5, 0.5, 0.5, 0.8))
        
        frame = DirectFrame(
            frameColor=relic_color,
            frameSize=(-0.33, 0.33, -0.05, 0.05),
            pos=(0, 0, y_pos)
        )
        
        # Relic name
        relic_name = DirectLabel(
            text=relic["name"],
            scale=0.04,
            pos=(-0.3, 0, 0.02),
            text_align=TextNode.ALeft,
            text_fg=(1, 1, 1, 1),
            frameColor=(0, 0, 0, 0),
            parent=frame
        )
        
        # Relic rarity
        relic_rarity = DirectLabel(
            text=f"({relic['rarity']})",
            scale=0.03,
            pos=(-0.3, 0, -0.02),
            text_align=TextNode.ALeft,
            text_fg=(0.8, 0.8, 0.8, 1),
            frameColor=(0, 0, 0, 0),
            parent=frame
        )
        
        # Action button
        if is_active:
            button = DirectButton(
                text="Remove",
                scale=0.03,
                pos=(0.25, 0, 0),
                command=self.remove_relic,
                extraArgs=[relic_id],
                frameColor=(0.7, 0.3, 0.3, 0.8),
                parent=frame
            )
        else:
            button = DirectButton(
                text="Equip",
                scale=0.03,
                pos=(0.25, 0, 0),
                command=self.add_relic,
                extraArgs=[relic_id],
                frameColor=(0.3, 0.7, 0.3, 0.8),
                parent=frame
            )
        
        return frame
    
    def update_chest_display(self):
        """Update the chest reward display"""
        if self.relic_system.chest_reward_ready:
            self.chest_frame.show()
            
            # Update labels
            self.chest_label["text"] = "Reward Chest (Available)"
            self.chest_quality_label["text"] = f"Quality: {self.relic_system.chest_quality}"
            
            # Format contents
            if self.relic_system.chest_rewards:
                content_text = "Contents:\n"
                for relic_id in self.relic_system.chest_rewards:
                    relic = self.relic_system.available_relics[relic_id]
                    content_text += f"• {relic['name']} ({relic['rarity']})\n"
                self.chest_contents["text"] = content_text
            else:
                self.chest_contents["text"] = "Contents: Empty"
            
            # Set color based on quality
            quality_colors = {
                RelicRarity.COMMON: (0.5, 0.5, 0.5, 0.8),      # Gray
                RelicRarity.UNCOMMON: (0.3, 0.7, 0.3, 0.8),    # Green
                RelicRarity.RARE: (0.3, 0.3, 0.8, 0.8),        # Blue
                RelicRarity.EPIC: (0.7, 0.3, 0.7, 0.8),        # Purple
                RelicRarity.LEGENDARY: (0.8, 0.7, 0.2, 0.8),   # Gold
                RelicRarity.MYTHICAL: (1.0, 0.4, 0.4, 0.8)     # Red
            }
            self.chest_frame["frameColor"] = quality_colors.get(
                self.relic_system.chest_quality, (0.3, 0.25, 0.2, 0.7)
            )
        else:
            self.chest_frame.hide()
    
    def update_player_stats(self):
        """Update the player stats display"""
        player = self.game.player
        
        self.health_label["text"] = f"Health: {player.health}/{player.max_health}"
        self.damage_label["text"] = f"Damage Multiplier: {player.damage_multiplier:.2f}x"
        self.speed_label["text"] = f"Speed Multiplier: {player.speed_multiplier:.2f}x"
        self.cooldown_label["text"] = f"Cooldown Multiplier: {player.cooldown_multiplier:.2f}x"
    
    def complete_night(self, difficulty=1.0):
        """Simulate completing a night"""
        self.relic_system.night_completed(success=True, difficulty_level=difficulty)
        self.update_chest_display()
    
    def open_chest(self):
        """Open the reward chest"""
        if self.relic_system.chest_reward_ready:
            rewards = self.relic_system.open_chest()
            print(f"Opened chest! Received {len(rewards)} relics.")
            self.update_chest_display()
            self.update_relic_displays()
    
    def add_relic(self, relic_id):
        """Add a relic to the player's active relics"""
        success = self.relic_system.add_relic(relic_id)
        if success:
            self.update_relic_displays()
            self.update_player_stats()
    
    def remove_relic(self, relic_id):
        """Remove a relic from the player's active relics"""
        if relic_id in self.relic_system.active_relics:
            # Add back to inventory
            self.relic_system.relic_inventory[relic_id] = self.relic_system.active_relics[relic_id].copy()
            
            # Remove active relic
            self.relic_system.remove_relic(relic_id)
            
            self.update_relic_displays()
            self.update_player_stats()
    
    def set_time_of_day(self, time):
        """Set the time of day (day/night)"""
        self.game.time_of_day = time
        
        # Update title color to indicate time of day
        if time == "day":
            self.title["fg"] = (1, 0.9, 0.6, 1)  # Yellowish for day
        else:
            self.title["fg"] = (0.6, 0.7, 1, 1)  # Blueish for night
    
    def update(self, task):
        """Update the display"""
        dt = globalClock.getDt()
        self.game.game_time += dt
        
        # Update relic system
        self.relic_system.update(dt)
        
        # Update player stats
        self.update_player_stats()
        
        return task.cont

def main():
    app = EnhancedRelicTest()
    app.run()

if __name__ == "__main__":
    main() 