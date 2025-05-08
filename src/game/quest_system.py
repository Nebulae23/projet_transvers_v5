#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Quest System for Nightfall Defenders
Manages quests, objectives, and quest progression
"""

from enum import Enum
import random
import time

class QuestType(Enum):
    """Enumeration of different quest types"""
    MAIN = "main"
    SIDE = "side"
    DAILY = "daily"
    WORLD_EVENT = "world_event"

class QuestStatus(Enum):
    """Enumeration of quest status states"""
    UNAVAILABLE = "unavailable"
    AVAILABLE = "available"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"

class ObjectiveType(Enum):
    """Enumeration of objective types"""
    KILL = "kill"
    COLLECT = "collect"
    INTERACT = "interact"
    DISCOVER = "discover"
    ESCORT = "escort"
    DEFEND = "defend"
    CRAFT = "craft"
    DELIVER = "deliver"

class QuestObjective:
    """Represents a single objective in a quest"""
    
    def __init__(self, objective_id, description, objective_type, target_id=None, amount=1):
        """
        Initialize a quest objective
        
        Args:
            objective_id (str): Unique identifier for this objective
            description (str): Description of the objective
            objective_type (ObjectiveType): Type of objective
            target_id (str): Target entity ID (enemy type, item, location, etc.)
            amount (int): Amount required (kills, items, etc.)
        """
        self.objective_id = objective_id
        self.description = description
        self.objective_type = objective_type
        self.target_id = target_id
        self.amount = amount
        
        # Progress tracking
        self.current_progress = 0
        self.completed = False
    
    def update_progress(self, amount=1):
        """
        Update the progress on this objective
        
        Args:
            amount (int): Amount to increase progress by
            
        Returns:
            bool: True if objective was completed with this update
        """
        was_completed = self.completed
        self.current_progress += amount
        
        if self.current_progress >= self.amount and not was_completed:
            self.completed = True
            return True
            
        return False
    
    def get_progress_percent(self):
        """Get the progress as a percentage"""
        if self.amount == 0:
            return 100.0
            
        return min(100.0, (self.current_progress / self.amount) * 100.0)
    
    def get_progress_text(self):
        """Get the progress as a formatted string"""
        return f"{self.current_progress}/{self.amount}"

class Quest:
    """Represents a quest with objectives and rewards"""
    
    def __init__(self, quest_id, name, quest_type, description, level_requirement=1):
        """
        Initialize a quest
        
        Args:
            quest_id (str): Unique identifier for this quest
            name (str): Display name of the quest
            quest_type (QuestType): Type of quest (main, side, etc.)
            description (str): Description of the quest
            level_requirement (int): Minimum player level required
        """
        self.quest_id = quest_id
        self.name = name
        self.quest_type = quest_type
        self.description = description
        self.level_requirement = level_requirement
        
        # Objectives and rewards
        self.objectives = []
        self.rewards = {
            "experience": 0,
            "gold": 0,
            "items": {},
            "reputation": 0
        }
        
        # State information
        self.status = QuestStatus.UNAVAILABLE
        self.giver_npc_id = None
        self.turn_in_npc_id = None
        self.complete_npc_id = None
        
        # Time tracking
        self.start_time = None
        self.completion_time = None
        self.fail_time = None
        self.expiration_time = None  # For time-limited quests
        
        # Requirements and unlocks
        self.required_quests = []  # Quests that must be completed first
        self.unlocks_quests = []  # Quests unlocked by completing this one
        
        # Optional content
        self.dialogue = {
            "offer": "Would you help me with this task?",
            "accept": "Thank you for your help!",
            "decline": "Perhaps another time then.",
            "progress": "How's your progress going?",
            "complete": "Excellent work! Here's your reward."
        }
    
    def add_objective(self, objective):
        """
        Add an objective to this quest
        
        Args:
            objective (QuestObjective): The objective to add
        """
        self.objectives.append(objective)
    
    def add_reward(self, reward_type, value):
        """
        Add a reward to this quest
        
        Args:
            reward_type (str): Type of reward (experience, gold, item, etc.)
            value: Value of the reward
        """
        if reward_type == "item":
            if isinstance(value, tuple) and len(value) == 2:
                item_id, amount = value
                if item_id in self.rewards["items"]:
                    self.rewards["items"][item_id] += amount
                else:
                    self.rewards["items"][item_id] = amount
        else:
            if reward_type in self.rewards:
                self.rewards[reward_type] += value
    
    def activate(self):
        """Activate this quest (player accepted it)"""
        self.status = QuestStatus.ACTIVE
        self.start_time = time.time()
    
    def complete(self):
        """Complete this quest"""
        self.status = QuestStatus.COMPLETED
        self.completion_time = time.time()
    
    def fail(self):
        """Fail this quest"""
        self.status = QuestStatus.FAILED
        self.fail_time = time.time()
    
    def make_available(self):
        """Make this quest available to the player"""
        self.status = QuestStatus.AVAILABLE
    
    def is_complete(self):
        """Check if all objectives are completed"""
        if not self.objectives:
            return False
            
        return all(obj.completed for obj in self.objectives)
    
    def is_ready_to_complete(self):
        """Check if the quest is ready to be turned in"""
        return self.status == QuestStatus.ACTIVE and self.is_complete()
    
    def update_objective_progress(self, objective_type, target_id, amount=1):
        """
        Update progress on objectives of the specified type/target
        
        Args:
            objective_type (ObjectiveType): Type of objective
            target_id (str): Target entity ID
            amount (int): Amount to increase progress by
            
        Returns:
            bool: True if any objectives were updated
        """
        if self.status != QuestStatus.ACTIVE:
            return False
            
        updated = False
        for objective in self.objectives:
            if objective.objective_type == objective_type and objective.target_id == target_id:
                if objective.update_progress(amount):
                    updated = True
        
        return updated
    
    def get_progress_text(self):
        """Get overall progress text"""
        total_objectives = len(self.objectives)
        completed_objectives = sum(1 for obj in self.objectives if obj.completed)
        
        return f"{completed_objectives}/{total_objectives}"
    
    def get_progress_percent(self):
        """Get overall progress percentage"""
        if not self.objectives:
            return 0.0
            
        total = len(self.objectives)
        completed = sum(1 for obj in self.objectives if obj.completed)
        partial_progress = sum(obj.get_progress_percent() / 100.0 for obj in self.objectives if not obj.completed)
        
        return (completed / total + partial_progress / total) * 100.0

class QuestManager:
    """Manages all quests and quest progression"""
    
    def __init__(self, game):
        """
        Initialize the quest manager
        
        Args:
            game: The main game instance
        """
        self.game = game
        self.quests = {}  # All quests by ID
        self.player_quests = {}  # Player's quests by ID
        self.completed_quests = set()  # IDs of completed quests
        self.failed_quests = set()  # IDs of failed quests
    
    def create_quest(self, quest_id, name, quest_type, description, level_requirement=1):
        """
        Create a new quest
        
        Args:
            quest_id (str): Unique identifier
            name (str): Display name
            quest_type (QuestType): Type of quest
            description (str): Description
            level_requirement (int): Minimum player level
            
        Returns:
            Quest: The created quest
        """
        quest = Quest(quest_id, name, quest_type, description, level_requirement)
        self.quests[quest_id] = quest
        return quest
    
    def update(self, dt):
        """
        Update quests (check for time-based conditions, etc.)
        
        Args:
            dt: Time delta
        """
        current_time = time.time()
        
        # Check for expired quests
        for quest_id, quest in self.player_quests.items():
            if quest.status == QuestStatus.ACTIVE and quest.expiration_time:
                if current_time > quest.expiration_time:
                    self.fail_quest(quest_id)
                    if hasattr(self.game, 'message_system') and self.game.message_system:
                        self.game.message_system.show_message(
                            f"Quest failed: {quest.name} (Time expired)",
                            duration=5.0,
                            message_type="quest_failed"
                        )
    
    def accept_quest(self, quest_id):
        """
        Player accepts a quest
        
        Args:
            quest_id (str): Quest ID
            
        Returns:
            bool: True if quest was accepted
        """
        if quest_id not in self.quests:
            return False
            
        quest = self.quests[quest_id]
        
        # Check if already active or completed
        if quest_id in self.player_quests or quest_id in self.completed_quests:
            return False
            
        # Check requirements
        if not self._check_quest_requirements(quest_id):
            return False
            
        # Activate the quest
        quest.activate()
        self.player_quests[quest_id] = quest
        
        # Notify via message system if available
        if hasattr(self.game, 'message_system') and self.game.message_system:
            self.game.message_system.show_message(
                f"Quest accepted: {quest.name}",
                duration=3.0,
                message_type="quest_accepted"
            )
            
        return True
    
    def complete_quest(self, quest_id):
        """
        Complete a quest and give rewards
        
        Args:
            quest_id (str): Quest ID
            
        Returns:
            bool: True if quest was completed
        """
        if quest_id not in self.player_quests:
            return False
            
        quest = self.player_quests[quest_id]
        
        # Check if all objectives are complete
        if not quest.is_complete():
            return False
            
        # Mark as completed
        quest.complete()
        self.completed_quests.add(quest_id)
        del self.player_quests[quest_id]
        
        # Give rewards
        self._give_quest_rewards(quest)
        
        # Check for quests that this unlocks
        self._check_quest_unlocks(quest_id)
        
        # Notify via message system if available
        if hasattr(self.game, 'message_system') and self.game.message_system:
            self.game.message_system.show_message(
                f"Quest completed: {quest.name}",
                duration=3.0,
                message_type="quest_completed"
            )
            
        return True
    
    def fail_quest(self, quest_id):
        """
        Fail a quest
        
        Args:
            quest_id (str): Quest ID
            
        Returns:
            bool: True if quest was failed
        """
        if quest_id not in self.player_quests:
            return False
            
        quest = self.player_quests[quest_id]
        quest.fail()
        self.failed_quests.add(quest_id)
        del self.player_quests[quest_id]
        
        return True
    
    def abandon_quest(self, quest_id):
        """
        Abandon a quest (remove from active quests)
        
        Args:
            quest_id (str): Quest ID
            
        Returns:
            bool: True if quest was abandoned
        """
        if quest_id not in self.player_quests:
            return False
            
        del self.player_quests[quest_id]
        return True
    
    def _check_quest_requirements(self, quest_id):
        """
        Check if a quest's requirements are met
        
        Args:
            quest_id (str): Quest ID
            
        Returns:
            bool: True if requirements are met
        """
        quest = self.quests[quest_id]
        
        # Check player level
        if self.game.player.level < quest.level_requirement:
            return False
            
        # Check required quests
        for req_quest_id in quest.required_quests:
            if req_quest_id not in self.completed_quests:
                return False
                
        return True
    
    def _check_quest_unlocks(self, completed_quest_id):
        """
        Check for quests unlocked by completing a quest
        
        Args:
            completed_quest_id (str): ID of the completed quest
        """
        for quest_id, quest in self.quests.items():
            if completed_quest_id in quest.required_quests:
                if self._check_quest_requirements(quest_id):
                    quest.make_available()
    
    def _give_quest_rewards(self, quest):
        """
        Give the rewards for a completed quest
        
        Args:
            quest (Quest): The completed quest
        """
        # Experience
        if quest.rewards["experience"] > 0:
            self.game.player.add_experience(quest.rewards["experience"])
            
        # Gold
        if quest.rewards["gold"] > 0:
            if hasattr(self.game.player, 'gold'):
                self.game.player.gold += quest.rewards["gold"]
                
        # Items
        for item_id, amount in quest.rewards["items"].items():
            if hasattr(self.game.player, 'inventory'):
                if item_id in self.game.player.inventory:
                    self.game.player.inventory[item_id] += amount
                else:
                    self.game.player.inventory[item_id] = amount
    
    def on_kill(self, enemy_type, amount=1):
        """
        Register enemy kill for quest tracking
        
        Args:
            enemy_type (str): Type of enemy killed
            amount (int): Number killed
        """
        updated_quests = []
        
        for quest_id, quest in self.player_quests.items():
            if quest.update_objective_progress(ObjectiveType.KILL, enemy_type, amount):
                updated_quests.append(quest)
                
        return updated_quests
    
    def on_collect(self, item_id, amount=1):
        """
        Register item collection for quest tracking
        
        Args:
            item_id (str): ID of collected item
            amount (int): Amount collected
        """
        updated_quests = []
        
        for quest_id, quest in self.player_quests.items():
            if quest.update_objective_progress(ObjectiveType.COLLECT, item_id, amount):
                updated_quests.append(quest)
                
        return updated_quests
    
    def on_interact(self, object_id):
        """
        Register interaction for quest tracking
        
        Args:
            object_id (str): ID of interacted object
        """
        updated_quests = []
        
        for quest_id, quest in self.player_quests.items():
            if quest.update_objective_progress(ObjectiveType.INTERACT, object_id, 1):
                updated_quests.append(quest)
                
        return updated_quests
    
    def on_poi_discovered(self, poi):
        """
        Register POI discovery for quest tracking
        
        Args:
            poi: The discovered POI
        """
        updated_quests = []
        
        for quest_id, quest in self.player_quests.items():
            if quest.update_objective_progress(ObjectiveType.DISCOVER, poi.poi_id, 1):
                updated_quests.append(quest)
                
        return updated_quests
    
    def on_craft(self, item_id, amount=1):
        """
        Register crafting for quest tracking
        
        Args:
            item_id (str): ID of crafted item
            amount (int): Amount crafted
        """
        updated_quests = []
        
        for quest_id, quest in self.player_quests.items():
            if quest.update_objective_progress(ObjectiveType.CRAFT, item_id, amount):
                updated_quests.append(quest)
                
        return updated_quests
    
    def get_active_quests(self):
        """Get all active quests"""
        return list(self.player_quests.values())
    
    def get_available_quests(self):
        """Get all available quests"""
        return [quest for quest_id, quest in self.quests.items() 
                if quest.status == QuestStatus.AVAILABLE 
                and quest_id not in self.player_quests 
                and quest_id not in self.completed_quests 
                and self._check_quest_requirements(quest_id)]
    
    def get_available_quests_from_npc(self, npc_id, player=None):
        """
        Get available quests from a specific NPC
        
        Args:
            npc_id (str): NPC ID
            player: Player entity (for level checks)
            
        Returns:
            list: Available quests from this NPC
        """
        available_quests = []
        
        for quest_id, quest in self.quests.items():
            if quest.giver_npc_id == npc_id and quest.status == QuestStatus.AVAILABLE:
                if quest_id not in self.player_quests and quest_id not in self.completed_quests:
                    if player and player.level < quest.level_requirement:
                        continue
                        
                    if not all(req_id in self.completed_quests for req_id in quest.required_quests):
                        continue
                        
                    available_quests.append(quest)
                    
        return available_quests
    
    def get_active_quests_from_npc(self, npc_id, player=None):
        """
        Get active quests from a specific NPC
        
        Args:
            npc_id (str): NPC ID
            player: Player entity (unused, for API consistency)
            
        Returns:
            list: Active quests from this NPC
        """
        active_quests = []
        
        for quest_id, quest in self.player_quests.items():
            if quest.turn_in_npc_id == npc_id or quest.giver_npc_id == npc_id:
                active_quests.append(quest)
                
        return active_quests
    
    def get_completed_quests_from_npc(self, npc_id, player=None):
        """
        Get completed quests waiting to be turned in to a specific NPC
        
        Args:
            npc_id (str): NPC ID
            player: Player entity (unused, for API consistency)
            
        Returns:
            list: Completed quests for this NPC
        """
        completed_quests = []
        
        for quest_id, quest in self.player_quests.items():
            if quest.turn_in_npc_id == npc_id and quest.is_ready_to_complete():
                completed_quests.append(quest)
                
        return completed_quests
    
    def save_data(self):
        """
        Create a serializable data representation of quest state
        
        Returns:
            dict: Serializable quest data
        """
        data = {
            "player_quests": {},
            "completed_quests": list(self.completed_quests),
            "failed_quests": list(self.failed_quests)
        }
        
        # Save active quests
        for quest_id, quest in self.player_quests.items():
            quest_data = {
                "id": quest.quest_id,
                "status": quest.status.value,
                "start_time": quest.start_time,
                "objectives": []
            }
            
            # Save objective progress
            for obj in quest.objectives:
                obj_data = {
                    "id": obj.objective_id,
                    "progress": obj.current_progress,
                    "completed": obj.completed
                }
                quest_data["objectives"].append(obj_data)
                
            data["player_quests"][quest_id] = quest_data
            
        return data
    
    def load_data(self, data):
        """
        Load quest state from serialized data
        
        Args:
            data: Serialized quest data
        """
        # Clear current state
        self.player_quests = {}
        self.completed_quests = set()
        self.failed_quests = set()
        
        # Load completed and failed quests
        if "completed_quests" in data:
            self.completed_quests = set(data["completed_quests"])
            
        if "failed_quests" in data:
            self.failed_quests = set(data["failed_quests"])
            
        # Load active quests
        if "player_quests" in data:
            for quest_id, quest_data in data["player_quests"].items():
                if quest_id in self.quests:
                    quest = self.quests[quest_id]
                    
                    # Set quest state
                    quest.status = QuestStatus(quest_data["status"])
                    quest.start_time = quest_data["start_time"]
                    
                    # Set objective progress
                    for obj_data in quest_data["objectives"]:
                        for obj in quest.objectives:
                            if obj.objective_id == obj_data["id"]:
                                obj.current_progress = obj_data["progress"]
                                obj.completed = obj_data["completed"]
                                
                    # Add to player quests
                    self.player_quests[quest_id] = quest 