# src/engine/world/quest.py
from typing import Dict, List, Tuple, Optional
from enum import Enum
from dataclasses import dataclass
import uuid

class QuestType(Enum):
    MAIN = "main"
    SIDE = "side"
    WORLD = "world"

class ObjectiveType(Enum):
    KILL = "kill"
    COLLECT = "collect"
    TALK = "talk"
    EXPLORE = "explore"
    DEFEND = "defend"

@dataclass
class QuestReward:
    experience: int
    gold: int
    items: List[Tuple[str, int]]  # (item_id, quantity)

@dataclass
class QuestObjective:
    type: ObjectiveType
    target: str
    required: int
    current: int = 0
    completed: bool = False

class Quest:
    def __init__(self, quest_id: str, title: str, description: str, quest_type: QuestType):
        self.quest_id = quest_id
        self.title = title
        self.description = description
        self.type = quest_type
        self.objectives: List[QuestObjective] = []
        self.reward: Optional[QuestReward] = None
        self.prerequisites: List[str] = []  # List of required quest IDs
        self.completed = False
        self.active = False
        
    def add_objective(self, type: ObjectiveType, target: str, required: int):
        self.objectives.append(QuestObjective(type, target, required))
        
    def set_reward(self, experience: int, gold: int, items: List[Tuple[str, int]]):
        self.reward = QuestReward(experience, gold, items)
        
    def update_objective(self, objective_type: ObjectiveType, target: str, progress: int) -> bool:
        """Update objective progress and check completion"""
        updated = False
        for objective in self.objectives:
            if objective.type == objective_type and objective.target == target:
                objective.current = min(objective.current + progress, objective.required)
                objective.completed = objective.current >= objective.required
                updated = True
                
        self.completed = all(obj.completed for obj in self.objectives)
        return updated

class QuestManager:
    def __init__(self):
        self.quests: Dict[str, Quest] = {}
        self.active_quests: Dict[str, Quest] = {}
        
    def create_quest(self, title: str, description: str, quest_type: QuestType) -> Quest:
        quest_id = str(uuid.uuid4())
        quest = Quest(quest_id, title, description, quest_type)
        self.quests[quest_id] = quest
        return quest
        
    def activate_quest(self, quest_id: str) -> bool:
        if quest_id in self.quests and self._can_activate_quest(quest_id):
            quest = self.quests[quest_id]
            quest.active = True
            self.active_quests[quest_id] = quest
            return True
        return False
        
    def _can_activate_quest(self, quest_id: str) -> bool:
        quest = self.quests[quest_id]
        return all(
            prereq_id in self.quests and self.quests[prereq_id].completed
            for prereq_id in quest.prerequisites
        )
        
    def update_quest_progress(self, objective_type: ObjectiveType, target: str, progress: int):
        """Update progress for all active quests with matching objective"""
        for quest in self.active_quests.values():
            if quest.update_objective(objective_type, target, progress):
                self._check_quest_completion(quest)
                
    def _check_quest_completion(self, quest: Quest):
        if quest.completed:
            # Handle quest completion
            if quest.quest_id in self.active_quests:
                del self.active_quests[quest.quest_id]