#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
NPC System for Nightfall Defenders
Manages NPCs, their behaviors, and interactions with the player
"""

from enum import Enum
import random
from panda3d.core import Vec3, NodePath, TextNode

class NPCType(Enum):
    """Enumeration of different NPC types"""
    MERCHANT = "merchant"
    QUEST_GIVER = "quest_giver"
    TRAINER = "trainer"
    CRAFTSMAN = "craftsman"
    GUARD = "guard"
    VILLAGER = "villager"

class DialogueType(Enum):
    """Enumeration of dialogue types"""
    GREETING = "greeting"
    QUEST_OFFER = "quest_offer"
    QUEST_PROGRESS = "quest_progress"
    QUEST_COMPLETE = "quest_complete"
    MERCHANT_DIALOGUE = "merchant_dialogue"
    TRAINING_DIALOGUE = "training_dialogue"
    CRAFTING_DIALOGUE = "crafting_dialogue"
    LORE = "lore"
    HINT = "hint"

class NPC:
    """Base class for all NPCs"""
    
    def __init__(self, npc_id, name, npc_type, position, model_path=None):
        """
        Initialize an NPC
        
        Args:
            npc_id (str): Unique identifier
            name (str): Display name
            npc_type (NPCType): Type of NPC
            position (Vec3): World position
            model_path (str): Path to model file
        """
        self.npc_id = npc_id
        self.name = name
        self.npc_type = npc_type
        self.position = position
        self.model_path = model_path or "models/character"
        
        # Visual components
        self.node_path = None
        self.name_display = None
        
        # Dialogue and quests
        self.dialogues = {
            DialogueType.GREETING: [f"Hello, traveler. I am {name}."]
        }
        self.current_dialogue = None
        self.associated_quests = []
        
        # Behaviors
        self.schedule = {}  # Time of day -> behavior
        self.current_behavior = "idle"
        self.interaction_range = 3.0
        
        # Merchant inventory (if applicable)
        self.inventory = {}
        self.services = {}
        
    def create_world_representation(self, render):
        """
        Create the visual representation of this NPC in the world
        
        Args:
            render: The render node to attach to
        """
        # Create a node for this NPC
        self.node_path = NodePath(f"NPC_{self.npc_id}")
        self.node_path.reparentTo(render)
        self.node_path.setPos(self.position)
        
        # Try to load the model
        try:
            model = render.getParent().loader.loadModel(self.model_path)
            model.reparentTo(self.node_path)
            
            # Apply NPC type-specific coloring
            if self.npc_type == NPCType.MERCHANT:
                model.setColor(0.8, 0.7, 0.2, 1)  # Gold-ish
            elif self.npc_type == NPCType.QUEST_GIVER:
                model.setColor(0.8, 0.2, 0.8, 1)  # Purple-ish
            elif self.npc_type == NPCType.TRAINER:
                model.setColor(0.2, 0.6, 0.8, 1)  # Blue-ish
            else:
                model.setColor(0.7, 0.7, 0.7, 1)  # Gray
        except Exception as e:
            print(f"Error loading model for NPC {self.name}: {e}")
            # Use a default box if model loading fails
            from panda3d.core import CardMaker
            cm = CardMaker("npc_marker")
            cm.setFrame(-0.5, 0.5, 0, 2)
            marker = self.node_path.attachNewNode(cm.generate())
            
            # Color based on NPC type
            if self.npc_type == NPCType.MERCHANT:
                marker.setColor(0.8, 0.7, 0.2, 1)  # Gold-ish
            elif self.npc_type == NPCType.QUEST_GIVER:
                marker.setColor(0.8, 0.2, 0.8, 1)  # Purple-ish
            elif self.npc_type == NPCType.TRAINER:
                marker.setColor(0.2, 0.6, 0.8, 1)  # Blue-ish
            else:
                marker.setColor(0.7, 0.7, 0.7, 1)  # Gray
                
            marker.setBillboardPointEye()
        
        # Create floating name
        self._create_name_display()
        
        # Add interaction indicator
        self._create_interaction_indicator()
        
        return self.node_path
    
    def _create_name_display(self):
        """Create a floating name display above the NPC"""
        if self.node_path:
            # Text node to display the name
            text_node = TextNode(f"NPC_text_{self.npc_id}")
            text_node.setText(self.name)
            text_node.setAlign(TextNode.ACenter)
            
            # Color based on NPC type
            if self.npc_type == NPCType.MERCHANT:
                text_node.setTextColor(0.9, 0.8, 0.3, 1)  # Gold
            elif self.npc_type == NPCType.QUEST_GIVER:
                text_node.setTextColor(0.9, 0.3, 0.9, 1)  # Purple
            elif self.npc_type == NPCType.TRAINER:
                text_node.setTextColor(0.3, 0.7, 0.9, 1)  # Blue
            else:
                text_node.setTextColor(0.9, 0.9, 0.9, 1)  # White
                
            text_node.setShadow(0.05, 0.05)
            text_node.setShadowColor(0, 0, 0, 1)
            
            # Create a node path for the text
            text_np = self.node_path.attachNewNode(text_node)
            text_np.setScale(0.5)
            text_np.setPos(0, 0, 2.2)  # Position above the NPC
            text_np.setBillboardPointEye()  # Make it always face the camera
            
            # Store the text node path
            self.name_display = text_np
    
    def _create_interaction_indicator(self):
        """Create an indicator that the NPC can be interacted with"""
        if self.node_path:
            from panda3d.core import CardMaker
            cm = CardMaker("interaction_indicator")
            cm.setFrame(-0.3, 0.3, -0.3, 0.3)
            
            indicator = self.node_path.attachNewNode(cm.generate())
            indicator.setColor(1, 1, 0, 0.7)  # Yellow, semi-transparent
            indicator.setPos(0, 0, 2.5)  # Above the name
            indicator.setBillboardPointEye()
            
            # By default, hide it until player is in range
            indicator.hide()
            
            # Store the indicator
            self.interaction_indicator = indicator
    
    def update(self, dt, player_position):
        """
        Update the NPC
        
        Args:
            dt: Time delta
            player_position: Current player position
        """
        # Update behavior based on schedule
        self._update_behavior()
        
        # Handle the current behavior
        self._handle_behavior(dt)
        
        # Check if player is in interaction range
        distance = (self.position - player_position).length()
        in_range = distance <= self.interaction_range
        
        # Show/hide interaction indicator
        if hasattr(self, 'interaction_indicator'):
            if in_range:
                self.interaction_indicator.show()
            else:
                self.interaction_indicator.hide()
    
    def _update_behavior(self):
        """Update behavior based on time of day and schedule"""
        # This would be implemented with proper scheduling based on game time
        pass
    
    def _handle_behavior(self, dt):
        """Handle the current behavior"""
        if self.current_behavior == "idle":
            # Just stand in place
            pass
        elif self.current_behavior == "patrol":
            # Move along patrol path
            pass
        elif self.current_behavior == "work":
            # Perform work animations
            pass
        elif self.current_behavior == "sleep":
            # Sleep animation
            pass
    
    def interact(self, player):
        """
        Handle player interaction with this NPC
        
        Args:
            player: The player entity
            
        Returns:
            dict: Interaction result with dialogue, options, etc.
        """
        # Different behavior based on NPC type
        if self.npc_type == NPCType.MERCHANT:
            return self._merchant_interaction(player)
        elif self.npc_type == NPCType.QUEST_GIVER:
            return self._quest_interaction(player)
        elif self.npc_type == NPCType.TRAINER:
            return self._trainer_interaction(player)
        else:
            return self._generic_interaction(player)
    
    def _merchant_interaction(self, player):
        """Handle merchant-specific interaction"""
        # Get appropriate dialogue
        dialogue = random.choice(self.dialogues.get(DialogueType.MERCHANT_DIALOGUE, 
                                                  ["Welcome to my shop, traveler. Take a look at my wares."]))
        
        # Return interaction data
        return {
            "dialogue": dialogue,
            "options": [
                {"text": "Buy Items", "action": "open_shop"},
                {"text": "Sell Items", "action": "open_sell"},
                {"text": "Goodbye", "action": "close_dialogue"}
            ],
            "npc": self,
            "type": "merchant"
        }
    
    def _quest_interaction(self, player):
        """Handle quest-specific interaction"""
        # Check for available or in-progress quests
        quest_system = getattr(player.game, 'quest_system', None)
        if not quest_system:
            return self._generic_interaction(player)
            
        # Find quests from this NPC
        available_quests = quest_system.get_available_quests_from_npc(self.npc_id, player)
        active_quests = quest_system.get_active_quests_from_npc(self.npc_id, player)
        completed_quests = quest_system.get_completed_quests_from_npc(self.npc_id, player)
        
        options = []
        dialogue = ""
        
        if completed_quests:
            # Handle completed quest dialogue and rewards
            dialogue = random.choice(self.dialogues.get(DialogueType.QUEST_COMPLETE, 
                                                      ["Excellent work! Here's your reward."]))
            for quest in completed_quests:
                options.append({
                    "text": f"Complete: {quest.name}", 
                    "action": "complete_quest", 
                    "quest_id": quest.quest_id
                })
        elif active_quests:
            # Check progress on active quests
            dialogue = random.choice(self.dialogues.get(DialogueType.QUEST_PROGRESS, 
                                                      ["How's your progress on that task I gave you?"]))
            for quest in active_quests:
                progress_text = "In Progress"
                if quest.is_ready_to_complete():
                    progress_text = "Ready to Complete"
                    
                options.append({
                    "text": f"{quest.name} ({progress_text})", 
                    "action": "show_quest_details", 
                    "quest_id": quest.quest_id
                })
        elif available_quests:
            # Offer new quests
            dialogue = random.choice(self.dialogues.get(DialogueType.QUEST_OFFER, 
                                                      ["I could use some help with something. Are you interested?"]))
            for quest in available_quests:
                options.append({
                    "text": f"Accept: {quest.name}", 
                    "action": "accept_quest", 
                    "quest_id": quest.quest_id
                })
        else:
            # Generic dialogue if no quests
            dialogue = random.choice(self.dialogues.get(DialogueType.GREETING, 
                                                      [f"Hello, {player.name}. I have no tasks for you at the moment."]))
                
        # Always add a goodbye option
        options.append({"text": "Goodbye", "action": "close_dialogue"})
        
        return {
            "dialogue": dialogue,
            "options": options,
            "npc": self,
            "type": "quest_giver"
        }
    
    def _trainer_interaction(self, player):
        """Handle trainer-specific interaction"""
        # Get appropriate dialogue
        dialogue = random.choice(self.dialogues.get(DialogueType.TRAINING_DIALOGUE, 
                                                  ["I can train you in various skills. What would you like to learn?"]))
        
        # Build options based on available training
        options = []
        for skill_id, training in self.services.items():
            cost = training.get('cost', 0)
            options.append({
                "text": f"Train {training.get('name', skill_id)} ({cost} gold)", 
                "action": "train_skill", 
                "skill_id": skill_id,
                "cost": cost
            })
            
        # Add goodbye option
        options.append({"text": "Goodbye", "action": "close_dialogue"})
        
        return {
            "dialogue": dialogue,
            "options": options,
            "npc": self,
            "type": "trainer"
        }
    
    def _generic_interaction(self, player):
        """Handle generic NPC interaction"""
        # Get an appropriate greeting
        dialogue = random.choice(self.dialogues.get(DialogueType.GREETING, 
                                                  [f"Hello, traveler. I am {self.name}."]))
        
        # Basic options
        options = [
            {"text": "Ask about the area", "action": "ask_lore"},
            {"text": "Goodbye", "action": "close_dialogue"}
        ]
        
        return {
            "dialogue": dialogue,
            "options": options,
            "npc": self,
            "type": "generic"
        }
    
    def add_dialogue(self, dialogue_type, text):
        """Add a dialogue option for this NPC"""
        if dialogue_type not in self.dialogues:
            self.dialogues[dialogue_type] = []
            
        self.dialogues[dialogue_type].append(text)
    
    def add_lore_dialogue(self, text):
        """Add lore dialogue"""
        self.add_dialogue(DialogueType.LORE, text)
    
    def add_greeting(self, text):
        """Add greeting dialogue"""
        self.add_dialogue(DialogueType.GREETING, text)
    
    def add_merchant_item(self, item_id, price, quantity=1):
        """Add an item to merchant inventory"""
        if item_id not in self.inventory:
            self.inventory[item_id] = {"price": price, "quantity": quantity}
        else:
            self.inventory[item_id]["quantity"] += quantity
    
    def add_training_service(self, skill_id, name, description, cost):
        """Add a training service"""
        self.services[skill_id] = {
            "name": name,
            "description": description, 
            "cost": cost
        }
        
    def save_data(self):
        """Create a serializable representation of the NPC"""
        data = {
            "id": self.npc_id,
            "name": self.name,
            "type": self.npc_type.value,
            "position": [self.position.x, self.position.y, self.position.z],
            "model_path": self.model_path,
            "dialogues": {k.value: v for k, v in self.dialogues.items()},
            "associated_quests": self.associated_quests,
            "schedule": self.schedule,
            "inventory": self.inventory,
            "services": self.services
        }
        return data
    
    @classmethod
    def from_data(cls, data):
        """Create an NPC from serialized data"""
        position = Vec3(data["position"][0], data["position"][1], data["position"][2])
        npc = cls(
            data["id"],
            data["name"],
            NPCType(data["type"]),
            position,
            data["model_path"]
        )
        
        # Load dialogues
        for dialogue_type, texts in data["dialogues"].items():
            npc.dialogues[DialogueType(dialogue_type)] = texts
        
        # Load other data
        npc.associated_quests = data["associated_quests"]
        npc.schedule = data["schedule"]
        npc.inventory = data["inventory"]
        npc.services = data["services"]
        
        return npc


class NPCManager:
    """Manages all NPCs in the game world"""
    
    def __init__(self, game):
        """Initialize the NPC manager"""
        self.game = game
        self.npcs = {}
    
    def create_npc(self, npc_id, name, npc_type, position, model_path=None):
        """Create a new NPC"""
        npc = NPC(npc_id, name, npc_type, position, model_path)
        self.npcs[npc_id] = npc
        return npc
    
    def update(self, dt, player_position):
        """Update all NPCs"""
        for npc_id, npc in self.npcs.items():
            npc.update(dt, player_position)
    
    def get_npc_at_position(self, position, interaction_range=3.0):
        """Get an NPC at the given position within interaction range"""
        for npc_id, npc in self.npcs.items():
            if (npc.position - position).length() <= interaction_range:
                return npc
        return None
    
    def get_nearest_npc(self, position, max_distance=float('inf')):
        """Get the nearest NPC to the given position"""
        nearest_npc = None
        nearest_distance = max_distance
        
        for npc_id, npc in self.npcs.items():
            distance = (npc.position - position).length()
            if distance < nearest_distance:
                nearest_npc = npc
                nearest_distance = distance
        
        return nearest_npc
    
    def save_data(self):
        """Create serializable data for all NPCs"""
        data = {
            "npcs": {}
        }
        
        for npc_id, npc in self.npcs.items():
            data["npcs"][npc_id] = npc.save_data()
            
        return data
    
    def load_data(self, data):
        """Load NPCs from serialized data"""
        if "npcs" not in data:
            return
            
        # Clear existing NPCs
        self.npcs = {}
        
        # Load NPCs
        for npc_id, npc_data in data["npcs"].items():
            npc = NPC.from_data(npc_data)
            self.npcs[npc_id] = npc 